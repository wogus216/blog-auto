"""티스토리 투자글 3개에 나스닥 급락글 퍼널 추가본 반영 (update_post)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from blog_auto.publishers.tistory import TistoryPublisher  # noqa: E402
from update_tistory_running import build_request  # noqa: E402

D = ROOT / "posts" / "_drafts"
JOBS = [
    ("840", "tistory__etf_500jo_my_take.md"),
    ("841", "tistory__sol_ai_semi_top2_my_take.md"),
    ("843", "tistory__monthly_dividend_etf_rush_my_take_2026.md"),
]


def main() -> None:
    pub = TistoryPublisher()
    ok = 0
    for pid, fn in JOBS:
        req = build_request(D / fn)
        try:
            res = pub.update_post(pid, req)
            s = "✓" if res.ok else "✗"
            print(f"  {s} {pid} {fn[:40]} — {res.note}")
            ok += res.ok
        except Exception as e:
            print(f"  ✗ {pid} {fn[:40]} — 예외: {e}")
    print(f"\n반영 완료 {ok}/{len(JOBS)}")


if __name__ == "__main__":
    main()
