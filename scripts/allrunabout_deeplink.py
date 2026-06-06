"""티스토리 러닝화 글의 allrunabout 메인 링크 → 주제별 딥링크 교체 (일회성).

각 글에 등장하는 경로 없는 allrunabout 링크(https://allrunabout.com,
https://www.allrunabout.com/)를 등장 순서대로 딥링크로 치환. 앵커 텍스트는 유지.
이미 경로가 붙은 딥링크는 건드리지 않는다.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "posts" / "_drafts"
BASE = "https://allrunabout.com"

# 글별 딥링크 (본문 CTA → 같이보면 글 순서대로)
MAP = {
    "tistory__2026_beginner_first_running_shoes_best5.md": [
        "/best/beginner", "/best/under-150k"],
    "tistory__adidas_running_pace_guide.md": [
        "/brands/adidas", "/best/nike-racing", "/best/new-balance-max-cushion",
        "/shoes/adidas-adios-pro-4"],
    "tistory__asics_novablast6_preview.md": [
        "/shoes/asics-novablast-5", "/best/beginner", "/best/daily-trainer",
        "/brands/asics/technology"],
    "tistory__asics_running_pace_guide.md": [
        "/brands/asics", "/best/asics-racing", "/shoes/asics-magic-speed-5",
        "/shoes/asics-gel-nimbus-28"],
    "tistory__garmin_run_korea_2026.md": [
        "/blog/2026-garmin-run-korea-half-marathon", "/best/half-marathon",
        "/best/marathon", "/best/10k"],
    "tistory__hoka_running_pace_guide.md": [
        "/brands/hoka", "/best/nike-racing", "/best/new-balance-max-cushion",
        "/best/asics-racing"],
    "tistory__newbalance_running_pace_guide.md": [
        "/brands/new-balance", "/best/nike-racing", "/best/adidas-daily-trainer",
        "/best/wide-toebox"],
    "tistory__nike_running_pace_guide.md": [
        "/brands/nike", "/best/new-balance-max-cushion", "/best/racing",
        "/best/marathon"],
    "tistory__puma_deviate_nitro_pure_2026.md": [
        "/shoes/puma-deviate-pure-nitro", "/blog/puma-deviate-pure-nitro-review"],
    "tistory__running_injury_prevention_top5.md": [
        "/best/plantar-fasciitis", "/best/knee-protection"],
    "tistory__seonsa_marathon_2026.md": [
        "/blog/2026-seonsa-marathon-gangdong", "/best/10k", "/best/marathon",
        "/best/beginner"],
    "tistory__나이키 페가수스 42 리뷰 데일리 트레이너의 안정 카.md": [
        "/shoes/nike-pegasus-42", "/blog/nike-pegasus-42-review"],
}

# 경로 없는 allrunabout 링크만 (뒤에 ) " ' 공백 < 가 오는 것)
PAT = re.compile(r"https://(?:www\.)?allrunabout\.com/?(?=[)\"'\s<])")


def main() -> None:
    total_ok = 0
    for fn, paths in MAP.items():
        p = D / fn
        if not p.exists():
            print(f"  ✗ 파일 없음: {fn}")
            continue
        text = p.read_text(encoding="utf-8")
        gen = iter(BASE + x for x in paths)
        used = [0]

        def repl(m):
            try:
                v = next(gen)
                used[0] += 1
                return v
            except StopIteration:
                return m.group(0)

        new, n_match = PAT.subn(repl, text)
        status = "✓" if used[0] == len(paths) else "⚠️"
        print(f"  {status} {fn[:46]:46s} 치환 {used[0]}/{len(paths)} (매칭 {n_match})")
        if used[0] != len(paths):
            print(f"      [주의] 매핑 수({len(paths)})와 실제 링크 수 불일치 — 확인 필요")
        p.write_text(new, encoding="utf-8")
        total_ok += used[0]
    print(f"\n총 {total_ok}개 링크 딥링크화 완료")


if __name__ == "__main__":
    main()
