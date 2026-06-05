"""AdSense 니치별 RPM 분해 측정.

기존 Blogger와 같은 OAuth 클라이언트(credentials/blogger_client_secrets.json)를
재사용하되, AdSense 읽기 권한은 별도 토큰(sessions/adsense_token.json)으로 분리해
Blogger 발행 토큰을 건드리지 않는다.

첫 실행 시 브라우저가 열리며 구글 로그인 + 'AdSense 보고서 보기' 동의가 필요하다
(읽기 전용 — 데이터 조회만, 광고/수익 변경 권한 없음).

사용법:
    uv run python scripts/adsense_rpm.py [일수]
    예) uv run python scripts/adsense_rpm.py 28      # 최근 28일
        uv run python scripts/adsense_rpm.py 90      # 최근 90일(기본 30)

사장님 도메인=니치 매핑이 내장돼 있어, 사이트별 RPM이 곧 니치별 RPM 분해다.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from blog_auto import config

SCOPES = ["https://www.googleapis.com/auth/adsense.readonly"]
TOKEN_PATH = config.SESSIONS_DIR / "adsense_token.json"
SECRETS_PATH = config.BLOGGER_CLIENT_SECRETS

# 도메인 → 니치 (AdSense는 니치를 모르지만 사장님은 도메인=니치가 거의 일치)
NICHE = {
    "money.onestepblog.info": "부동산 청약 (YMYL 고단가)",
    "www.onestepblog.info": "미국주식 (YMYL 고단가)",
    "consistency.onestepblog.info": "스포츠+주택 (혼합)",
    "sancho216.tistory.com": "러닝+야구+투자 (혼합, 저단가 예상)",
}


def get_creds() -> Credentials:
    creds: Credentials | None = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("\n>>> 브라우저가 열립니다. 구글 로그인 후 'AdSense 보고서 보기' 권한에 동의하세요.")
            print(">>> (읽기 전용 — 광고/수익을 변경하지 않습니다)\n")
            flow = InstalledAppFlow.from_client_secrets_file(str(SECRETS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
        print(f"[OK] AdSense 토큰 저장: {TOKEN_PATH}")
    return creds


def fmt(v: str, money: bool = False) -> str:
    try:
        f = float(v)
        return f"${f:,.2f}" if money else f"{f:,.0f}" if f >= 100 else f"{f:,.2f}"
    except (ValueError, TypeError):
        return str(v)


def main() -> None:
    # googleapiclient는 점(.) 포함 파라미터(startDate.year 등)를 못 받으므로
    # AdSense dateRange 프리셋을 사용한다. 7/30일·이번달·올해 지원.
    arg = (sys.argv[1] if len(sys.argv) > 1 else "30").lower()
    preset = {
        "7": "LAST_7_DAYS", "30": "LAST_30_DAYS",
        "mtd": "MONTH_TO_DATE", "ytd": "YEAR_TO_DATE",
        "today": "TODAY", "yesterday": "YESTERDAY",
    }
    date_range = preset.get(arg, "LAST_30_DAYS")

    creds = get_creds()
    svc = build("adsense", "v2", credentials=creds)

    accounts = svc.accounts().list().execute().get("accounts", [])
    if not accounts:
        print("AdSense 계정을 찾을 수 없습니다.")
        return
    account = accounts[0]["name"]  # accounts/pub-XXXXXXXXXX
    print(f"\n계정: {account}  |  기간: {date_range}\n")

    metrics = [
        "ESTIMATED_EARNINGS", "PAGE_VIEWS", "PAGE_VIEWS_RPM",
        "IMPRESSIONS", "IMPRESSIONS_RPM", "CLICKS", "PAGE_VIEWS_CTR",
    ]
    report = svc.accounts().reports().generate(
        account=account,
        dateRange=date_range,
        dimensions=["DOMAIN_NAME"],
        metrics=metrics,
        currencyCode="USD",
        orderBy=["-PAGE_VIEWS_RPM"],
    ).execute()

    headers = [h["name"] for h in report.get("headers", [])]
    rows = report.get("rows", [])
    if not rows:
        print("데이터가 없습니다 (기간 내 노출 없음 또는 사이트 미연결).")
        return

    def cell(row, name):
        try:
            return row["cells"][headers.index(name)]["value"]
        except (ValueError, IndexError, KeyError):
            return "-"

    print(f"{'도메인':<32} {'니치':<24} {'페이지RPM':>10} {'노출RPM':>9} {'PV':>8} {'수익':>9} {'CTR':>7}")
    print("-" * 104)
    for row in rows:
        dom = cell(row, "DOMAIN_NAME")
        niche = NICHE.get(dom, "기타")
        print(
            f"{dom:<32} {niche:<24} "
            f"{fmt(cell(row,'PAGE_VIEWS_RPM'), True):>10} "
            f"{fmt(cell(row,'IMPRESSIONS_RPM'), True):>9} "
            f"{fmt(cell(row,'PAGE_VIEWS')):>8} "
            f"{fmt(cell(row,'ESTIMATED_EARNINGS'), True):>9} "
            f"{cell(row,'PAGE_VIEWS_CTR')}"
        )

    totals = report.get("totals", {})
    if totals:
        print("-" * 104)
        t_rpm = cell(totals, "PAGE_VIEWS_RPM") if "cells" in totals else "-"
        t_earn = cell(totals, "ESTIMATED_EARNINGS") if "cells" in totals else "-"
        t_pv = cell(totals, "PAGE_VIEWS") if "cells" in totals else "-"
        print(f"{'합계/블렌디드':<57} {fmt(t_rpm, True):>10} {'':>9} {fmt(t_pv):>8} {fmt(t_earn, True):>9}")

    print("\n해석 팁: 페이지RPM 낮은 도메인이 블렌디드를 끌어내리는 범인. "
          "혼합 도메인(티스토리)은 URL 채널/페이지별로 더 쪼개면 정밀.")


if __name__ == "__main__":
    main()
