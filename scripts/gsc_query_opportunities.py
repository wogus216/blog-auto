"""GSC 쿼리별 실적으로 '글감 광맥'을 발굴한다 (읽기 전용).

이미 노출되는데 순위가 애매한 키워드 = 글 하나 더 쓰면 뜨는 확실한 글감.
sancho216 등 살아있는 채널에 대해 query dimension으로 28일 실적을 뽑아
기회/저CTR/챔피언으로 분류한다.

사용:
  uv run python scripts/gsc_query_opportunities.py [property] [--days 28] [--min-impr 30]
  property 생략 시 sancho216 티스토리. 홈 URL이나 sc-domain 문자열도 허용.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gsc_index_report import gsc_credentials, pick_property, fmt_http_error  # noqa: E402

DEFAULT_PROP = "https://sancho216.tistory.com/"


def query_rows(sc, prop: str, start: date, end: date) -> list[dict]:
    return sc.searchanalytics().query(
        siteUrl=prop,
        body={
            "startDate": start.isoformat(), "endDate": end.isoformat(),
            "dimensions": ["query"], "rowLimit": 1000, "dataState": "all",
        },
    ).execute().get("rows", [])


def show(title, rows, note=""):
    print(f"\n{'─'*74}\n{title}   {note}\n{'─'*74}")
    if not rows:
        print("  (없음)"); return
    print(f"  {'클릭':>4} {'노출':>6} {'CTR':>5} {'순위':>5}  키워드")
    for r in rows:
        c, i = int(r["clicks"]), int(r["impressions"])
        ctr, pos = r["ctr"] * 100, r["position"]
        kw = r["keys"][0]
        print(f"  {c:>4} {i:>6} {ctr:>4.1f}% {pos:>5.1f}  {kw}")


def main() -> int:
    args = [a for a in sys.argv[1:]]
    days = 28
    min_impr = 30
    prop_arg = None
    i = 0
    while i < len(args):
        if args[i] == "--days":
            days = int(args[i + 1]); i += 2
        elif args[i] == "--min-impr":
            min_impr = int(args[i + 1]); i += 2
        else:
            prop_arg = args[i]; i += 1

    creds = gsc_credentials()
    sc = build("searchconsole", "v1", credentials=creds)
    props = [s["siteUrl"] for s in sc.sites().list().execute().get("siteEntry", [])]

    target = prop_arg or DEFAULT_PROP
    prop = target if target in props else (pick_property(target, props) or target)

    end = date.today() - timedelta(days=2)
    start = end - timedelta(days=days)
    print(f"글감 발굴 — {prop}\n기간 {start}~{end} ({days}일) · 노출 최소 {min_impr}")

    try:
        rows = query_rows(sc, prop, start, end)
    except HttpError as e:
        print(f"실패: {fmt_http_error(e)}"); return 1

    rows = [r for r in rows if int(r["impressions"]) >= min_impr]
    tot_c = sum(int(r["clicks"]) for r in rows)
    tot_i = sum(int(r["impressions"]) for r in rows)
    print(f"쿼리 {len(rows)}개 (노출≥{min_impr}) · 클릭합 {tot_c} · 노출합 {tot_i}")

    # 🔥 기회: 노출 충분한데 순위 8~20 = 글 하나 더 쓰면 1페이지 상단 진입
    opp = sorted(
        [r for r in rows if 7.5 <= r["position"] <= 20.5],
        key=lambda r: int(r["impressions"]), reverse=True,
    )[:25]
    show("🔥 기회 키워드 (순위 8~20, 노출順) — 강화/신규글 최우선", opp,
         "→ 이 주제로 깊은 글 하나면 1페이지 상단")

    # 💧 저CTR: 상위 노출(순위≤8)인데 클릭 전환 낮음 = 제목/메타 개선
    low_ctr = sorted(
        [r for r in rows if r["position"] <= 8 and r["ctr"] < 0.03 and int(r["impressions"]) >= min_impr * 2],
        key=lambda r: int(r["impressions"]), reverse=True,
    )[:15]
    show("💧 저CTR (순위≤8·CTR<3%) — 제목/썸네일 개선 or 의도 재매칭", low_ctr)

    # 🏆 챔피언: 클릭 상위 = 엔티티 복제(같은 공식으로 인접 주제 확장)
    champ = sorted(rows, key=lambda r: int(r["clicks"]), reverse=True)[:15]
    show("🏆 챔피언 (클릭順) — 엔티티 복제로 인접 주제 확장", champ)

    return 0


if __name__ == "__main__":
    sys.exit(main())
