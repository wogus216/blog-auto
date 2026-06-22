"""Google Search Console 색인 리포트 (읽기 전용).

목적
  - 발행은 됐는데 구글 색인에 안 잡히는 문제를 '실측'한다.
  - URL 검사 API 로 신규 글별 색인 상태/거부·제외 사유를 뽑고,
  - 검색 분석 API 로 최근 28일 클릭·노출을 본다.

인증
  - 기존 Blogger OAuth 클라이언트(credentials/blogger_client_secrets.json)를 재사용.
  - 스코프는 webmasters.readonly (Blogger 토큰과 별개) → sessions/gsc_token.json 에 저장.
  - 최초 1회 브라우저 동의 필요(자동으로 브라우저가 열림). 이후 자동 갱신.
  - GCP 프로젝트에서 'Google Search Console API' 가 사용 설정돼 있어야 함.
    안 돼 있으면 403 과 함께 활성화 URL 이 출력된다.

사용
  uv run python scripts/gsc_index_report.py                # 3개 블로그 전체
  uv run python scripts/gsc_index_report.py --blog consistency
  uv run python scripts/gsc_index_report.py --inspect 15   # 블로그당 최근 15개 URL 검사
  uv run python scripts/gsc_index_report.py --days 28      # 검색분석 기간
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from blog_auto import config
from blog_auto.publishers.blogger import _get_credentials as blogger_creds

GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

BLOGS = {
    "consistency": (config.BLOGGER_BLOG_ID, "https://consistency.onestepblog.info/"),
    "stocks": (config.BLOGGER_STOCKS_BLOG_ID, "https://www.onestepblog.info/"),
    "money": (config.BLOGGER_MONEY_BLOG_ID, "https://money.onestepblog.info/"),
}


def gsc_credentials() -> Credentials:
    token_path = config.SESSIONS_DIR / "gsc_token.json"
    secrets = Path(config.BLOGGER_CLIENT_SECRETS)
    if not secrets.is_absolute():
        secrets = config.ROOT / secrets

    creds: Credentials | None = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), GSC_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("  [인증] 브라우저에서 Google 로그인·동의가 필요합니다 (webmasters.readonly)...")
            flow = InstalledAppFlow.from_client_secrets_file(str(secrets), GSC_SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def pick_property(home_url: str, props: list[str]) -> str | None:
    """GSC 등록 속성 중 이 블로그를 담는 속성 문자열을 고른다."""
    home_norm = home_url.rstrip("/")
    for p in props:  # 1) URL-prefix 정확 매칭
        if p.rstrip("/") == home_norm:
            return p
    host = urlparse(home_url).hostname or ""
    for p in props:  # 2) 도메인 속성(sc-domain:onestepblog.info)
        if p.startswith("sc-domain:"):
            dom = p.split(":", 1)[1]
            if host == dom or host.endswith("." + dom):
                return p
    return None


def recent_post_urls(blogger_svc, blog_id: str, n: int) -> list[str]:
    try:
        resp = (
            blogger_svc.posts()
            .list(blogId=blog_id, status="LIVE", maxResults=n, orderBy="PUBLISHED",
                  view="ADMIN", fetchBodies=False)
            .execute()
        )
        return [(it.get("published", "")[:10], it.get("title", "")[:38], it.get("url"))
                for it in resp.get("items", [])]
    except HttpError as e:
        print(f"  [Blogger URL 조회 실패] {e}")
        return []


def fmt_http_error(e: HttpError) -> str:
    try:
        data = e.error_details  # type: ignore[attr-defined]
    except Exception:
        data = None
    msg = getattr(e, "reason", None) or str(e)
    return f"{e.resp.status if e.resp else '?'} {msg} {data or ''}"


def inspect_url(sc, prop: str, url: str) -> dict:
    body = {"inspectionUrl": url, "siteUrl": prop, "languageCode": "ko"}
    res = sc.urlInspection().index().inspect(body=body).execute()
    return res.get("inspectionResult", {}).get("indexStatusResult", {})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--blog", choices=list(BLOGS), help="단일 블로그만")
    ap.add_argument("--inspect", type=int, default=12, help="블로그당 검사할 최근 URL 수")
    ap.add_argument("--days", type=int, default=28, help="검색분석 기간(일)")
    args = ap.parse_args()

    print("GSC 인증 중...")
    creds = gsc_credentials()
    sc = build("searchconsole", "v1", credentials=creds)
    bsvc = build("blogger", "v3", credentials=blogger_creds())

    # 등록 속성 목록
    try:
        sites = sc.sites().list().execute().get("siteEntry", [])
    except HttpError as e:
        print("\n[치명] Search Console API 호출 실패:")
        print("  " + fmt_http_error(e))
        print("\n→ GCP 프로젝트에서 'Google Search Console API' 를 사용 설정해야 합니다.")
        print("  https://console.cloud.google.com/apis/library/searchconsole.googleapis.com")
        return 1

    props = [s["siteUrl"] for s in sites]
    print(f"\n등록된 GSC 속성 {len(props)}개:")
    for s in sites:
        print(f"  · {s['siteUrl']}  (권한: {s.get('permissionLevel')})")

    end = date.today() - timedelta(days=2)  # GSC 데이터 지연 보정
    start = end - timedelta(days=args.days)

    targets = {args.blog: BLOGS[args.blog]} if args.blog else BLOGS
    for name, (blog_id, home) in targets.items():
        print("\n" + "=" * 72)
        print(f"[{name}]  {home}")
        prop = pick_property(home, props)
        if not prop:
            print(f"  ⚠ GSC에 이 도메인 속성이 없습니다. 등록 속성 중 매칭 실패.")
            continue
        print(f"  매칭 속성: {prop}")

        # 1) 검색 분석 — 총계
        try:
            tot = sc.searchanalytics().query(
                siteUrl=prop,
                body={"startDate": start.isoformat(), "endDate": end.isoformat(),
                      "dimensions": [], "dataState": "all"},
            ).execute()
            rows = tot.get("rows", [])
            if rows:
                r = rows[0]
                print(f"  최근 {args.days}일 검색({start}~{end}): "
                      f"클릭 {int(r['clicks'])} · 노출 {int(r['impressions'])} · "
                      f"CTR {r['ctr']*100:.2f}% · 평균순위 {r['position']:.1f}")
            else:
                print(f"  최근 {args.days}일 검색: 클릭/노출 데이터 0 (검색 유입 없음)")
        except HttpError as e:
            print(f"  [검색분석 실패] {fmt_http_error(e)}")

        # 2) 검색 분석 — 페이지별 상위 (신규 글이 노출되는지)
        try:
            pg = sc.searchanalytics().query(
                siteUrl=prop,
                body={"startDate": start.isoformat(), "endDate": end.isoformat(),
                      "dimensions": ["page"], "rowLimit": 5, "dataState": "all"},
            ).execute()
            prows = pg.get("rows", [])
            if prows:
                print(f"  노출 상위 페이지 {len(prows)}개:")
                for r in prows:
                    u = r["keys"][0].replace(home, "/")
                    print(f"    노출{int(r['impressions']):>4} 클릭{int(r['clicks']):>3}  {u[:54]}")
        except HttpError as e:
            print(f"  [페이지별 실패] {fmt_http_error(e)}")

        # 3) URL 검사 — 신규 글별 색인 상태
        urls = recent_post_urls(bsvc, blog_id, args.inspect)
        print(f"  --- URL 검사 (최근 {len(urls)}개) ---")
        tally: dict[str, int] = {}
        for pub, title, url in urls:
            if not url:
                continue
            try:
                r = inspect_url(sc, prop, url)
                verdict = r.get("verdict", "?")
                cov = r.get("coverageState", "?")
                last = (r.get("lastCrawlTime", "") or "")[:10] or "—"
                tally[cov] = tally.get(cov, 0) + 1
                flag = "✅" if verdict == "PASS" else "❌"
                print(f"    {flag} [{pub}] {title}")
                print(f"        색인상태: {cov}  | 마지막크롤: {last}")
            except HttpError as e:
                print(f"    [검사실패] {title}: {fmt_http_error(e)}")
        if tally:
            print(f"  ▶ 색인상태 집계: " +
                  " / ".join(f"{k}={v}" for k, v in sorted(tally.items())))

    return 0


if __name__ == "__main__":
    sys.exit(main())
