"""AdSense 다차원 분해 추출 → JSON 저장 (scientist 분석용).

adsense_rpm.py와 같은 OAuth 토큰(sessions/adsense_token.json)을 재사용해
국가·기기·광고유닛·포맷·페이지·일별 등 여러 차원으로 리포트를 뽑아
하나의 JSON으로 저장한다.

사용법:
    uv run python scripts/adsense_breakdown.py [7|30|mtd|ytd]   (기본 30)
저장: /tmp/adsense_breakdown.json
"""
from __future__ import annotations

import json
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from blog_auto import config

SCOPES = ["https://www.googleapis.com/auth/adsense.readonly"]
TOKEN_PATH = config.SESSIONS_DIR / "adsense_token.json"
OUT_PATH = "/tmp/adsense_breakdown.json"

METRICS = [
    "ESTIMATED_EARNINGS", "PAGE_VIEWS", "PAGE_VIEWS_RPM",
    "IMPRESSIONS", "IMPRESSIONS_RPM", "CLICKS", "PAGE_VIEWS_CTR", "COST_PER_CLICK",
]

# 분해 차원 (라벨 → dimensions)
BREAKDOWNS = {
    "by_domain": ["DOMAIN_NAME"],
    "by_country": ["COUNTRY_NAME"],
    "by_platform": ["PLATFORM_TYPE_NAME"],
    "by_ad_unit": ["AD_UNIT_NAME"],
    "by_ad_format": ["AD_FORMAT_NAME"],
    "by_ad_size": ["AD_UNIT_SIZE_NAME"],
    "by_page": ["DOMAIN_NAME", "PAGE_URL"],
    "by_buyer": ["BUYER_NETWORK_NAME"],
    "by_date": ["DATE"],
    "country_x_domain": ["DOMAIN_NAME", "COUNTRY_NAME"],
    "platform_x_domain": ["DOMAIN_NAME", "PLATFORM_TYPE_NAME"],
}


def get_creds() -> Credentials:
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    return creds


def rows_to_dicts(report: dict) -> list[dict]:
    headers = [h["name"] for h in report.get("headers", [])]
    out = []
    for row in report.get("rows", []):
        vals = [c.get("value") for c in row["cells"]]
        out.append(dict(zip(headers, vals)))
    return out


def main() -> None:
    arg = (sys.argv[1] if len(sys.argv) > 1 else "30").lower()
    date_range = {
        "7": "LAST_7_DAYS", "30": "LAST_30_DAYS",
        "mtd": "MONTH_TO_DATE", "ytd": "YEAR_TO_DATE",
    }.get(arg, "LAST_30_DAYS")

    svc = build("adsense", "v2", credentials=get_creds())
    account = svc.accounts().list().execute()["accounts"][0]["name"]
    print(f"계정 {account} | 기간 {date_range} | 차원 {len(BREAKDOWNS)}개 추출 중...")

    result = {"account": account, "date_range": date_range, "metrics": METRICS, "breakdowns": {}}
    for label, dims in BREAKDOWNS.items():
        try:
            rep = svc.accounts().reports().generate(
                account=account,
                dateRange=date_range,
                dimensions=dims,
                metrics=METRICS,
                currencyCode="USD",
                orderBy=["-ESTIMATED_EARNINGS"],
                limit=100,
            ).execute()
            rows = rows_to_dicts(rep)
            result["breakdowns"][label] = {
                "dimensions": dims,
                "row_count": len(rows),
                "rows": rows,
                "totals": rows_to_dicts({"headers": rep.get("headers", []), "rows": [rep["totals"]]})[0]
                if rep.get("totals") else None,
            }
            print(f"  ✓ {label:<20} {len(rows)} rows")
        except Exception as e:
            result["breakdowns"][label] = {"error": str(e)}
            print(f"  ✗ {label:<20} ERROR: {str(e)[:80]}")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n저장 완료: {OUT_PATH}")


if __name__ == "__main__":
    main()
