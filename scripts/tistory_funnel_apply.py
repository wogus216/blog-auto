"""티스토리 퍼널 강화 일괄 반영 (일회성).

발행글 2개는 update_post(조회수·URL 유지), 미발행 3개는 publish.
TistoryPublisher 1개 인스턴스로 순차 처리 → 첫 글에서 카카오 로그인하면
세션 유지로 나머지는 자동 통과(카카오가 재인증 요구하면 그 글에서 다시 로그인).

실행:
  uv run python scripts/tistory_funnel_apply.py
브라우저 창이 뜨면 카카오 로그인(‘로그인 상태 유지’ 체크 권장).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from blog_auto.publishers.tistory import TistoryPublisher  # noqa: E402
from update_tistory_running import build_request  # noqa: E402

DRAFTS = ROOT / "posts" / "_drafts"

# (action, 파일명, post_id)
JOBS = [
    ("update", "tistory__dundun_jeonse_2026_seoul.md", "832"),
    ("update", "tistory__hwaseong_dongtan2_c27_2026.md", "833"),
    ("publish", "tistory__etf_500jo_my_take.md", None),
    ("publish", "tistory__sol_ai_semi_top2_my_take.md", None),
    ("publish", "tistory__ssg_12_losing_streak_2026.md", None),
]


def main() -> None:
    pub = TistoryPublisher()
    results = []
    for action, fname, pid in JOBS:
        path = DRAFTS / fname
        if not path.exists():
            print(f"  ✗ {fname}: 파일 없음")
            results.append((fname, False, "파일 없음", None))
            continue
        req = build_request(path)
        print(f"\n[{action}] {fname}  ({req.title[:50]})")
        try:
            if action == "update":
                res = pub.update_post(pid, req)
            else:
                res = pub.publish(req)
            mark = "✓" if res.ok else "✗"
            print(f"  {mark} {res.note}  {res.url or ''}")
            results.append((fname, res.ok, res.note or "", res.url))
        except Exception as e:
            print(f"  ✗ 예외: {e}")
            results.append((fname, False, str(e), None))

    print("\n" + "=" * 72)
    print("결과 요약 (frontmatter 갱신용 — 발행 URL 확인)")
    print("-" * 72)
    for fname, ok, note, url in results:
        mark = "✓" if ok else "✗"
        print(f"  {mark} {fname}")
        if url:
            print(f"      url: {url}")


if __name__ == "__main__":
    main()
