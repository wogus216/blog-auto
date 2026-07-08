"""RSS 등에서 뽑은 실제 글 URL 목록의 색인 상태를 GSC로 검사한다.
사용: uv run python scripts/gsc_inspect_urls.py <property> < urls.txt
"""
from __future__ import annotations
import sys
from pathlib import Path
from googleapiclient.discovery import build
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gsc_index_report import gsc_credentials, inspect_url, fmt_http_error  # noqa: E402
from googleapiclient.errors import HttpError

def main() -> int:
    prop = sys.argv[1]
    urls = [l.strip() for l in sys.stdin if l.strip() and l.startswith("http")]
    sc = build("searchconsole", "v1", credentials=gsc_credentials())
    home = prop if prop.startswith("http") else ""
    tally: dict[str, int] = {}
    for u in urls:
        try:
            r = inspect_url(sc, prop, u)
            cov = r.get("coverageState", "?")
            verdict = r.get("verdict", "?")
            last = (r.get("lastCrawlTime", "") or "")[:10] or "—"
            robots = r.get("robotsTxtState", "")
            tally[cov] = tally.get(cov, 0) + 1
            flag = "✅" if verdict == "PASS" else "❌"
            short = u.replace(home, "/")
            short = short if len(short) < 46 else short[:44] + "…"
            print(f"{flag} {short:<46} {cov} | 크롤 {last}")
        except HttpError as e:
            print(f"[검사실패] {u}: {fmt_http_error(e)}")
    print("▶ 집계: " + " / ".join(f"{k}={v}" for k, v in sorted(tally.items())))
    return 0

if __name__ == "__main__":
    sys.exit(main())
