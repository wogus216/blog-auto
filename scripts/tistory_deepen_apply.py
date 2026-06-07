"""단신 깊이 보강본 8개를 티스토리에 반영 (update_post).

post_id를 명시했으므로 RSS 매칭 없이 바로 update_post(setContent). URL·조회수 유지.
첫 글에서 카카오 로그인하면 세션 유지로 이후 자동.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from blog_auto.publishers.tistory import TistoryPublisher  # noqa: E402
from update_tistory_running import build_request  # noqa: E402

D = ROOT / "posts" / "_drafts"

JOBS = [
    ("836", "tistory__asics_novablast6_preview.md"),
    ("810", "tistory__나이키 페가수스 42 리뷰 데일리 트레이너의 안정 카.md"),
    ("839", "tistory__puma_deviate_nitro_pure_2026.md"),
    ("835", "tistory__seonsa_marathon_2026.md"),
    ("834", "tistory__garmin_run_korea_2026.md"),
    ("833", "tistory__hwaseong_dongtan2_c27_2026.md"),
    ("832", "tistory__dundun_jeonse_2026_seoul.md"),
    ("842", "tistory__ssg_12_losing_streak_2026.md"),
]


def main() -> None:
    only = os.environ.get("ONLY", "")
    pub = TistoryPublisher()
    ok = 0
    jobs = [(p, f) for p, f in JOBS if not only or p in only]
    for pid, fn in jobs:
        p = D / fn
        if not p.exists():
            print(f"  ✗ 파일 없음: {fn}")
            continue
        req = build_request(p)
        try:
            res = pub.update_post(pid, req)
            s = "✓" if res.ok else "✗"
            print(f"  {s} {pid} {fn[:42]} — {res.note}")
            ok += res.ok
        except Exception as e:
            print(f"  ✗ {pid} {fn[:42]} — 예외: {e}")
    print(f"\n반영 완료 {ok}/{len(JOBS)}")


if __name__ == "__main__":
    main()
