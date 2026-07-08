"""GSC 색인 리포트 — 살아있는 채널(티스토리·allrunabout) 보강판.

gsc_index_report.py 는 Blogger API로 URL을 모아 Blogger 3종만 검사한다.
이 스크립트는 GSC에 등록된 '모든' 속성의 28일 실적을 한 줄로 스캔하고,
살아있는 채널(sitemap 있는 티스토리·allrunabout)은 sitemap에서 최신 글
URL을 뽑아 URL 검사(색인 상태)까지 돌린다. 읽기 전용.
"""

from __future__ import annotations

import re
import sys
from datetime import date, timedelta
from urllib.parse import urlparse
import urllib.request

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 같은 폴더의 기존 스크립트에서 인증·유틸 재사용
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from gsc_index_report import gsc_credentials, pick_property, fmt_http_error, inspect_url  # noqa: E402

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# sitemap 기반 최신글 검사 대상 (살아있는 채널)
SITEMAP_TARGETS = {
    "sancho216(티스토리)": ("https://sancho216.tistory.com/", "https://sancho216.tistory.com/sitemap.xml"),
    "allrunabout": ("https://allrunabout.com/", "https://allrunabout.com/sitemap.xml"),
    "onestepstock(티스토리)": ("https://onestepstock.tistory.com/", "https://onestepstock.tistory.com/sitemap.xml"),
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "replace")


def locs(xml: str) -> list[str]:
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)


def newest_post_urls(sitemap_url: str, home: str, n: int) -> list[str]:
    """sitemap(및 sitemap index)에서 실제 글 URL만 골라 최신 n개."""
    xml = fetch(sitemap_url)
    all_locs = locs(xml)
    # sitemap index면 하위 sitemap을 펼침
    subs = [u for u in all_locs if u.endswith(".xml")]
    if subs:
        for s in subs[:5]:
            try:
                all_locs += locs(fetch(s))
            except Exception:
                pass
    host = urlparse(home).hostname or ""
    posts = []
    for u in all_locs:
        if u.endswith(".xml"):
            continue
        p = urlparse(u)
        if p.hostname != host:
            continue
        path = p.path.strip("/")
        if not path or path.startswith("category") or path in ("tag", "guestbook", "notice"):
            continue
        posts.append(u)
    # 티스토리: 숫자 path 클수록 최신 → 숫자 desc. 그 외: sitemap 뒤쪽이 최신인 경우가 많아 역순.
    def sort_key(u: str):
        m = re.search(r"/(\d+)/?$", u)
        return (1, int(m.group(1))) if m else (0, 0)
    if any(sort_key(u)[0] for u in posts):
        posts.sort(key=sort_key, reverse=True)
    else:
        posts = list(reversed(posts))
    # 중복 제거(순서 유지)
    seen, out = set(), []
    for u in posts:
        if u not in seen:
            seen.add(u); out.append(u)
    return out[:n]


def main() -> int:
    inspect_n = 10
    print("GSC 인증 중...")
    creds = gsc_credentials()
    sc = build("searchconsole", "v1", credentials=creds)

    sites = sc.sites().list().execute().get("siteEntry", [])
    props = [s["siteUrl"] for s in sites]

    end = date.today() - timedelta(days=2)
    start = end - timedelta(days=28)

    # 1) 전체 속성 28일 실적 한눈에
    print(f"\n{'='*72}\n전체 GSC 속성 28일 실적 ({start}~{end})\n{'='*72}")
    scored = []
    for prop in props:
        try:
            r = sc.searchanalytics().query(
                siteUrl=prop,
                body={"startDate": start.isoformat(), "endDate": end.isoformat(),
                      "dimensions": [], "dataState": "all"},
            ).execute().get("rows", [])
            if r:
                row = r[0]
                scored.append((int(row["clicks"]), int(row["impressions"]), prop, row["position"]))
            else:
                scored.append((0, 0, prop, 0.0))
        except HttpError as e:
            print(f"  [{prop}] 실패: {fmt_http_error(e)}")
    for clicks, impr, prop, pos in sorted(scored, reverse=True):
        state = "🟢 LIVE" if clicks > 10 else ("🟡 미약" if impr > 5 else "🔴 사망")
        print(f"  {state}  클릭 {clicks:>5} · 노출 {impr:>7} · 평균순위 {pos:>4.1f}   {prop}")

    # 2) 살아있는 채널 — 최신글 색인 상태 + 노출 상위
    for name, (home, smap) in SITEMAP_TARGETS.items():
        prop = pick_property(home, props)
        print(f"\n{'='*72}\n[{name}]  {home}\n  매칭 속성: {prop}")
        if not prop:
            print("  ⚠ GSC 속성 매칭 실패"); continue

        # 노출 상위 페이지 (= 색인되어 실제 검색에 뜨는 글)
        try:
            pg = sc.searchanalytics().query(
                siteUrl=prop,
                body={"startDate": start.isoformat(), "endDate": end.isoformat(),
                      "dimensions": ["page"], "rowLimit": 10, "dataState": "all"},
            ).execute().get("rows", [])
            if pg:
                print(f"  ── 노출 상위 {len(pg)}개(색인+검색노출 중) ──")
                for r in pg:
                    u = r["keys"][0].replace(home, "/")
                    print(f"    노출{int(r['impressions']):>5} 클릭{int(r['clicks']):>4} 순위{r['position']:>5.1f}  {u[:52]}")
            else:
                print("  ── 노출 상위: 없음 ──")
        except HttpError as e:
            print(f"  [페이지별 실패] {fmt_http_error(e)}")

        # 최신글 색인 검사
        try:
            urls = newest_post_urls(smap, home, inspect_n)
        except Exception as e:
            print(f"  [sitemap 수집 실패] {e}"); urls = []
        print(f"  ── 최신 글 {len(urls)}개 색인 검사 ──")
        tally: dict[str, int] = {}
        for u in urls:
            try:
                r = inspect_url(sc, prop, u)
                cov = r.get("coverageState", "?")
                verdict = r.get("verdict", "?")
                last = (r.get("lastCrawlTime", "") or "")[:10] or "—"
                tally[cov] = tally.get(cov, 0) + 1
                flag = "✅" if verdict == "PASS" else "❌"
                print(f"    {flag} {u.replace(home, '/')[:48]:<48}  {cov} | 크롤 {last}")
            except HttpError as e:
                print(f"    [검사실패] {u}: {fmt_http_error(e)}")
        if tally:
            print("  ▶ 집계: " + " / ".join(f"{k}={v}" for k, v in sorted(tally.items())))

    return 0


if __name__ == "__main__":
    sys.exit(main())
