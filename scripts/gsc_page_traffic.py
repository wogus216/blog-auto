"""stdin URL 목록의 28일 클릭/노출 합계를 GSC 검색분석으로 조회.
사용: uv run python scripts/gsc_page_traffic.py <property> < urls.txt
"""
from __future__ import annotations
import sys
from datetime import date, timedelta
from pathlib import Path
from googleapiclient.discovery import build
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gsc_index_report import gsc_credentials  # noqa: E402

def main() -> int:
    prop = sys.argv[1]
    want = {l.strip() for l in sys.stdin if l.strip().startswith("http")}
    sc = build("searchconsole", "v1", credentials=gsc_credentials())
    end = date.today() - timedelta(days=2)
    start = end - timedelta(days=28)
    rows = sc.searchanalytics().query(siteUrl=prop, body={
        "startDate": start.isoformat(), "endDate": end.isoformat(),
        "dimensions": ["page"], "rowLimit": 1000, "dataState": "all",
    }).execute().get("rows", [])
    home = prop if prop.startswith("http") else ""
    tc = ti = 0
    hits = []
    for r in rows:
        pg = r["keys"][0]
        if pg in want:
            c, i = int(r["clicks"]), int(r["impressions"])
            tc += c; ti += i
            hits.append((c, i, r["position"], pg.replace(home, "/")))
    print(f"대상 {len(want)}개 중 검색노출된 글 {len(hits)}개 ({start}~{end}):")
    for c, i, pos, u in sorted(hits, reverse=True):
        print(f"  클릭{c:>4} 노출{i:>5} 순위{pos:>5.1f}  {u[:50]}")
    print(f"▶ 합계: 클릭 {tc} · 노출 {ti}")
    # 전체 대비 비중
    tot = sc.searchanalytics().query(siteUrl=prop, body={
        "startDate": start.isoformat(), "endDate": end.isoformat(),
        "dimensions": [], "dataState": "all",
    }).execute().get("rows", [])
    if tot:
        TC = int(tot[0]["clicks"])
        print(f"▶ 채널 전체 클릭 {TC} 중 이 글들 비중: {tc}/{TC} = {100*tc/max(TC,1):.1f}%")
    return 0

if __name__ == "__main__":
    sys.exit(main())
