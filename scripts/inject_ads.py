"""마크다운 본문 H2 사이에 인-아티클 광고를 자동 분산 삽입.

진단 결과 (2026-05-25) 본문 중간 광고 분산이 거의 0 → CTR 0.75%.
이 스크립트는 H2 분포를 분석해 광고를 균등하게 박는다. 같은 글이라도
광고 노출 회수가 늘어 CTR 1.5~2배 기대.

사용 흐름
  Claude(어시스턴트) 가 마크다운 작성
    ↓
  uv run python scripts/inject_ads.py posts/_drafts/foo.md
    ↓
  (선택) uv run python scripts/inject_jsonld.py posts/_drafts/foo.md --research <slug>
    ↓
  uv run blog-auto publish posts/_drafts/foo.md

광고 개수 결정 규칙 (H2 = `## ` 시작 라인 개수)
  H2 < 3:   0개 (너무 짧은 글은 광고 강제 안 함)
  H2 3~5:   1개
  H2 6~8:   2개
  H2 9+:    3개
  단 첫 H2 직전과 마지막 H2 직전은 후보에서 제외 (도입부/마무리 어색)

플랫폼 분기
  tistory             → assets/ads/inarticle_tistory.html
  blogger / blogger_stocks → assets/ads/inarticle_blogger.html
  naver               → 광고 삽입 안 함 (SmartEditor 가 <script>/<ins> 제거)

옵션
  --multiplex         글 끝 (참고자료/JSON-LD 직전) 에 멀티플렉스 광고 추가
  --no-inarticle      인-아티클 광고 비활성화 (멀티플렉스만)
  --inarticle-count N 자동 결정 대신 강제 개수
  --auto-ads          자동광고 병행(밀도제어) 모드. 테마 head 자동광고가 본문을
                      알아서 채우므로 수동 인-아티클을 1개로 cap → AdSense 과밀/
                      정책 위반 방지. 하단 멀티플렉스는 그대로 유지.
                      (--inarticle-count 를 명시하면 그 값을 우선)
  --dry-run           변경사항 미리보기
  -o, --output PATH   다른 경로에 저장
  --force             기존에 광고 코드 있어도 추가 삽입
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADS_DIR = ROOT / "assets" / "ads"

# 플랫폼 → 광고 HTML 파일 prefix
PLATFORM_AD_FILE = {
    "tistory": "tistory",
    "blogger": "blogger",
    "blogger_stocks": "blogger",
    "blogger_money": "blogger",  # money.onestepblog.info — blogger 광고 HTML 공용 (ca-pub 동일)
}
NO_AD_PLATFORMS = {"naver"}  # SmartEditor 가 script/ins 제거
AD_MARKER = "adsbygoogle"
SOURCES_HEADING = "## 참고 자료"
DISCLAIMER_HEADING = "## 면책 조항"
JSONLD_MARKER = '<script type="application/ld+json">'
TODO_TOKEN = "TODO_REPLACE_ME"


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str, str]:
    """`--- ... ---\\n\\n<body>` 분리. (meta, fm_block, body) 반환."""
    m = re.match(r"^(---\n.*?\n---\n\n?)(.*)$", text, re.DOTALL)
    if not m:
        return {}, "", text
    fm_block, body = m.groups()
    meta: dict[str, str] = {}
    for line in fm_block.strip("-\n").splitlines():
        k, _, v = line.partition(":")
        if k.strip():
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, fm_block, body


def _h2_line_indices(lines: list[str]) -> list[int]:
    """본문 라인 중 `## ` 으로 시작하는 (단 `### ` 는 제외) 인덱스."""
    out: list[int] = []
    for i, line in enumerate(lines):
        s = line.lstrip()
        if s.startswith("## ") and not s.startswith("### "):
            out.append(i)
    return out


def _decide_inarticle_count(h2_count: int) -> int:
    if h2_count < 3:
        return 0
    if h2_count <= 5:
        return 1
    if h2_count <= 8:
        return 2
    return 3


def _pick_insertion_positions(h2_indices: list[int], n_ads: int) -> list[int]:
    """첫/마지막 H2 직전은 피하고 중간 H2 직전에 균등 분포."""
    if n_ads == 0:
        return []
    candidates = h2_indices[1:-1] if len(h2_indices) >= 3 else []
    if not candidates:
        return []
    if n_ads >= len(candidates):
        return list(candidates)
    step = len(candidates) / n_ads
    picks = [candidates[int(step * k + step / 2)] for k in range(n_ads)]
    return sorted(set(picks))


def _load_ad_html(ad_type: str, platform: str) -> tuple[str, bool]:
    """(html, has_todo) 반환. ad_type: 'inarticle' | 'multiplex'."""
    if platform not in PLATFORM_AD_FILE:
        raise ValueError(f"광고 미지원 플랫폼: {platform}")
    fname = f"{ad_type}_{PLATFORM_AD_FILE[platform]}.html"
    path = ADS_DIR / fname
    if not path.exists():
        raise FileNotFoundError(f"광고 HTML 파일 없음: {path}")
    html = path.read_text(encoding="utf-8").strip()
    return html, TODO_TOKEN in html


def _find_tail_insert_line(lines: list[str]) -> int:
    """멀티플렉스 삽입 위치 = 면책/참고자료/JSON-LD 직전, 없으면 글 끝."""
    for i, line in enumerate(lines):
        s = line.lstrip()
        if (
            s.startswith(DISCLAIMER_HEADING)
            or s.startswith(SOURCES_HEADING)
            or JSONLD_MARKER in line
        ):
            return i
    return len(lines)


def _ad_block(html: str) -> str:
    """광고 HTML 을 마크다운 라인으로 변환 (위/아래 빈 줄 포함)."""
    return "\n" + html + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("markdown_path", help="대상 마크다운 (frontmatter 포함)")
    ap.add_argument("--multiplex", action="store_true", help="글 끝 멀티플렉스 광고 추가")
    ap.add_argument("--no-inarticle", action="store_true", help="인-아티클 광고 비활성화")
    ap.add_argument(
        "--inarticle-count",
        type=int,
        default=-1,
        help="인-아티클 광고 개수 강제 (기본: H2 개수로 자동 결정)",
    )
    ap.add_argument(
        "--auto-ads",
        action="store_true",
        help="자동광고 병행(밀도제어): 수동 인-아티클을 1개로 cap. 과밀/정책 위반 방지.",
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-o", "--output", default="")
    ap.add_argument("--force", action="store_true", help="기존 광고 있어도 추가 삽입")
    args = ap.parse_args()

    md_path = Path(args.markdown_path).resolve()
    if not md_path.exists():
        print(f"✗ 파일 없음: {md_path}")
        return 1

    original = md_path.read_text(encoding="utf-8")
    meta, fm_block, body = _parse_frontmatter(original)
    platform = meta.get("platform", "tistory")

    if platform in NO_AD_PLATFORMS:
        print(f"⚠️  platform={platform} 은 광고 미지원 (SmartEditor 제약). 종료.")
        return 0
    if platform not in PLATFORM_AD_FILE:
        print(f"✗ 알 수 없는 platform: {platform}")
        return 1

    # 중복 체크
    already_has_ad = AD_MARKER in body
    if already_has_ad and not args.force:
        print(f"⚠️  본문에 이미 광고 코드 있음 ({AD_MARKER}). --force 로 추가 삽입.")
        return 2

    lines = body.split("\n")
    h2_idx = _h2_line_indices(lines)
    print(f"📄 {md_path.name}  platform={platform}  H2 개수={len(h2_idx)}")

    inserted_log: list[str] = []

    # 1) 인-아티클 광고
    if not args.no_inarticle:
        if args.inarticle_count >= 0:
            n_ads = args.inarticle_count
        else:
            n_ads = _decide_inarticle_count(len(h2_idx))
            # 자동광고 병행 시: 테마 head 자동광고가 본문을 채우므로
            # 수동 인-아티클은 1개로 cap (과밀/정책 위반 방지, 밀도제어).
            if args.auto_ads and n_ads > 1:
                print(
                    f"  ⓘ --auto-ads 밀도제어: 인-아티클 {n_ads} → 1 개로 cap "
                    f"(자동광고가 나머지 위치를 채움)"
                )
                n_ads = 1
        positions = _pick_insertion_positions(h2_idx, n_ads)
        if positions:
            html, has_todo = _load_ad_html("inarticle", platform)
            if has_todo:
                print(
                    f"  ⚠️  inarticle 광고 슬롯 ID 미설정 (TODO_REPLACE_ME). "
                    f"AdSense 에서 발급받아 assets/ads/inarticle_{PLATFORM_AD_FILE[platform]}.html 채우세요."
                )
            block = _ad_block(html)
            # 뒤에서부터 삽입 (앞 인덱스 안 깨짐)
            for pos in reversed(positions):
                lines.insert(pos, block)
            inserted_log.append(f"인-아티클 {len(positions)} 개 (H2 인덱스 {positions})")
        else:
            print(f"  - 인-아티클 광고 0 개 (H2={len(h2_idx)} 개로는 자동 분산 불가)")

    # 2) 멀티플렉스 광고
    if args.multiplex:
        html, has_todo = _load_ad_html("multiplex", platform)
        if has_todo:
            print(
                f"  ⚠️  multiplex 광고 슬롯 ID 미설정. "
                f"assets/ads/multiplex_{PLATFORM_AD_FILE[platform]}.html 채우세요."
            )
        tail_pos = _find_tail_insert_line(lines)
        lines.insert(tail_pos, _ad_block(html))
        inserted_log.append(
            f"멀티플렉스 1 개 (line {tail_pos}, {'참고자료/JSON-LD 직전' if tail_pos < len(lines) - 1 else '글 끝'})"
        )

    if not inserted_log:
        print("변경 없음.")
        return 0

    new_body = "\n".join(lines)
    new_text = fm_block + new_body if fm_block else new_body

    print("\nINSERTED:")
    for log in inserted_log:
        print(f"  + {log}")
    added = len(new_text) - len(original)
    print(f"\nDIFF: +{added:,} chars")

    if args.dry_run:
        print("\n[--dry-run] 파일 안 건드림.")
        return 0

    out_path = Path(args.output).resolve() if args.output else md_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(new_text, encoding="utf-8")
    rel = out_path.relative_to(ROOT) if out_path.is_relative_to(ROOT) else out_path
    print(f"\n✅ 저장: {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
