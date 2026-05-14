"""야구 가이드 v2 9팀 일괄 예약 발행 스크립트 (Blogger + Tistory 지원).

사용법:
  uv run python scripts/schedule_baseball_bloggers.py blogger        # 9팀 모두 blogger 예약
  uv run python scripts/schedule_baseball_bloggers.py blogger --dry  # 드라이런 (요청만 출력)
  uv run python scripts/schedule_baseball_bloggers.py tistory        # 티스토리 예약 (옵션)
  uv run python scripts/schedule_baseball_bloggers.py blogger --only hanwha,kia  # 일부만

각 대상 마크다운 파일 frontmatter의 `schedule_at` 시간으로 예약합니다.
프론트매터 형식:
  ---
  title: ...
  platform: blogger
  tags: [...]
  schedule_at: 2026-05-15T09:00:00+09:00
  cta_url: ...
  cta_text: ...
  ---
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from blog_auto.publishers.base import PublishRequest  # noqa: E402

DRAFTS_DIR = ROOT / "posts" / "_drafts"

# 9팀 발행 매핑 (팀키 → blogger 파일명)
TEAM_FILES_BLOGGER = {
    "hanwha": "blogger__2026_hanwha_eagles_guide_v2.md",
    "kia":    "blogger__2026_kia_tigers_guide_v3.md",
    "lg":     "blogger__2026_lg_twins_guide_v2.md",
    "ssg":    "blogger__2026_ssg_landers_guide_v2.md",
    "doosan": "blogger__2026_doosan_bears_guide_v2.md",
    "kt":     "blogger__2026_kt_wiz_guide_v2.md",
    "kiwoom": "blogger__2026_kiwoom_heroes_guide_v2.md",
    "samsung":"blogger__2026_samsung_lions_guide_v2.md",
    "lotte":  "blogger__2026_lotte_giants_sajik_guide_v2.md",
}

TEAM_FILES_TISTORY = {
    "hanwha": "2026_hanwha_eagles_guide_v2.md",
    "kia":    "2026_kia_tigers_guide_v3.md",
    "lg":     "2026_lg_twins_guide_v2.md",
    "ssg":    "2026_ssg_landers_guide_v2.md",
    "doosan": "2026_doosan_bears_guide_v2.md",
    "kt":     "2026_kt_wiz_guide_v2.md",
    "kiwoom": "2026_kiwoom_heroes_guide_v2.md",
    "samsung":"2026_samsung_lions_guide_v2.md",
    "lotte":  "2026_lotte_giants_sajik_guide_v2.md",
}


_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _parse_simple_yaml(text: str) -> dict:
    """간단한 frontmatter용 YAML 파서 (PyYAML 의존성 없이)."""
    out: dict = {}
    for line in text.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            items = [s.strip().strip("'\"") for s in inner.split(",") if s.strip()]
            out[key] = items
        elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            out[key] = val[1:-1]
        else:
            out[key] = val
    return out


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    meta = _parse_simple_yaml(m.group(1))
    body = m.group(2)
    return meta, body


def build_request(path: Path) -> PublishRequest:
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    schedule_at = meta.get("schedule_at")
    if not schedule_at:
        raise ValueError(f"{path.name}: frontmatter에 schedule_at 없음")

    return PublishRequest(
        title=meta.get("title", path.stem),
        body_md=body,
        tags=meta.get("tags", []) or [],
        category=meta.get("category", "") or "",
        mode="schedule",
        schedule_at=str(schedule_at),
        cta_url=meta.get("cta_url"),
        cta_text=meta.get("cta_text"),
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("platform", choices=["blogger", "tistory"])
    ap.add_argument("--dry", action="store_true", help="실제 발행하지 않고 요청만 출력")
    ap.add_argument("--only", default="", help="콤마로 구분된 팀키만 발행 (예: hanwha,kia)")
    args = ap.parse_args()

    files = TEAM_FILES_BLOGGER if args.platform == "blogger" else TEAM_FILES_TISTORY
    if args.only:
        only = {k.strip() for k in args.only.split(",")}
        files = {k: v for k, v in files.items() if k in only}
        if not files:
            print(f"[!] --only 매칭 없음: {args.only}")
            sys.exit(1)

    if args.platform == "blogger":
        from blog_auto.publishers.blogger import BloggerPublisher
        pub = BloggerPublisher()
    else:
        from blog_auto.publishers.tistory import TistoryPublisher
        pub = TistoryPublisher()

    print(f"\n[{args.platform}] 야구 가이드 예약 발행 시작 — 대상 {len(files)}개")
    print("=" * 70)

    results: list[tuple[str, bool, str]] = []
    for team, fname in files.items():
        path = DRAFTS_DIR / fname
        if not path.exists():
            print(f"[!] {team}: 파일 없음 ({path.name})")
            results.append((team, False, "파일 없음"))
            continue

        try:
            req = build_request(path)
        except Exception as e:
            print(f"[!] {team}: frontmatter 파싱 실패 — {e}")
            results.append((team, False, f"파싱 실패: {e}"))
            continue

        print(f"\n[{team}] {req.title[:60]}...")
        print(f"  → 예약 시간: {req.schedule_at}")
        print(f"  → 태그: {', '.join(req.tags[:5])}{'...' if len(req.tags) > 5 else ''}")

        if args.dry:
            results.append((team, True, "DRY (skip)"))
            continue

        result = pub.publish(req)
        status = "✓" if result.ok else "✗"
        print(f"  {status} {result.note}")
        if result.url:
            print(f"  URL: {result.url}")
        results.append((team, result.ok, result.note))

    print("\n" + "=" * 70)
    print("발행 결과 요약")
    print("=" * 70)
    for team, ok, note in results:
        mark = "✓" if ok else "✗"
        print(f"  {mark} {team:10s} {note}")

    ok_count = sum(1 for _, ok, _ in results if ok)
    print(f"\n총 {len(results)}개 중 {ok_count}개 성공")


if __name__ == "__main__":
    main()
