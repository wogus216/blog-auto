"""러닝화 12개 글의 딥링크 교체본을 티스토리에 반영 (update_post).

RSS 제목 ↔ post_id 매칭으로 발행 글 식별 → update_post(setContent)로 본문 갱신.
URL·조회수 유지. update_post는 setContent라 중복 발행 quirk 없음.

  DRY=1 uv run python scripts/tistory_running_deeplink_apply.py   # 매칭만 검증
  uv run python scripts/tistory_running_deeplink_apply.py          # 실제 반영
"""
from __future__ import annotations

import html
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from blog_auto.publishers.tistory import TistoryPublisher  # noqa: E402
from update_tistory_running import build_request  # noqa: E402

D = ROOT / "posts" / "_drafts"
RSS_URL = "https://sancho216.tistory.com/rss"
DRY = os.environ.get("DRY") == "1"

FILES = [
    "tistory__2026_beginner_first_running_shoes_best5.md",
    "tistory__adidas_running_pace_guide.md",
    "tistory__asics_novablast6_preview.md",
    "tistory__asics_running_pace_guide.md",
    "tistory__garmin_run_korea_2026.md",
    "tistory__hoka_running_pace_guide.md",
    "tistory__newbalance_running_pace_guide.md",
    "tistory__nike_running_pace_guide.md",
    "tistory__puma_deviate_nitro_pure_2026.md",
    "tistory__running_injury_prevention_top5.md",
    "tistory__seonsa_marathon_2026.md",
    "tistory__나이키 페가수스 42 리뷰 데일리 트레이너의 안정 카.md",
]


def norm(s: str) -> str:
    s = re.sub(r"<!\[CDATA\[|\]\]>", "", s)
    s = html.unescape(s)
    s = s.replace("&mdash;", "—").replace("&middot;", "·").replace("&amp;", "&")
    return re.sub(r"\s+", "", s).strip()


def load_rss_map() -> dict[str, str]:
    raw = urllib.request.urlopen(RSS_URL, timeout=20).read().decode("utf-8", "ignore")
    items = re.findall(r"<item>(.*?)</item>", raw, re.DOTALL)
    out: dict[str, str] = {}
    for it in items:
        t = re.search(r"<title>(.*?)</title>", it, re.DOTALL)
        l = re.search(r"sancho216\.tistory\.com/(\d+)", it)
        if t and l:
            out.setdefault(norm(t.group(1)), l.group(1))
    return out


def main() -> None:
    rss = load_rss_map()
    print(f"RSS 글 {len(rss)}개 로드\n")

    only = os.environ.get("ONLY", "")
    jobs = []
    for fn in FILES:
        if only and only not in fn:
            continue
        p = D / fn
        if not p.exists():
            print(f"  ✗ 파일 없음: {fn}")
            continue
        req = build_request(p)
        pid = rss.get(norm(req.title))
        mark = "✓" if pid else "✗ 매칭실패"
        print(f"  {mark} post_id={pid or '?':>4} | {fn[:44]}")
        if pid:
            jobs.append((pid, req, fn))

    print(f"\n매칭 {len(jobs)}/{len(FILES)}")
    if DRY:
        print("[DRY] 반영 안 함. DRY 빼고 실행하면 update_post.")
        return
    if len(jobs) < len(FILES):
        print("⚠️ 일부 매칭 실패 — 그래도 매칭된 것만 진행합니다.")

    pub = TistoryPublisher()
    ok = 0
    for pid, req, fn in jobs:
        try:
            res = pub.update_post(pid, req)
            s = "✓" if res.ok else "✗"
            print(f"  {s} {pid} {fn[:40]} — {res.note}")
            ok += res.ok
        except Exception as e:
            print(f"  ✗ {pid} {fn[:40]} — 예외: {e}")
    print(f"\n반영 완료 {ok}/{len(jobs)}")


if __name__ == "__main__":
    main()
