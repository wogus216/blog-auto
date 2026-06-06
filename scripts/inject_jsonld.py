"""마크다운 글에 Schema.org JSON-LD 와 참고자료 섹션을 자동 주입.

Claude(어시스턴트)가 마크다운을 직접 작성하는 워크플로우의 GEO 후처리 단계.
글 본문은 그대로 두고, 글 말미에 두 가지를 추가한다:

  1) `## 참고 자료` 섹션 — ResearchBundle 의 모든 출처를 마크다운 링크로
  2) `<script type="application/ld+json">` 블록 — Article + ItemList + FAQPage
     (running_shoes 도메인 기준. 네이버는 SmartEditor 가 script 제거하므로 스킵)

사용:
  uv run python scripts/inject_jsonld.py posts/_drafts/foo.md \\
    --research 2026_beginner_running_shoes_best5

옵션:
  --dry-run             변경사항만 보여주고 파일 안 건드림
  -o, --output PATH     다른 경로에 저장 (기본: in-place)
  --force               이미 JSON-LD 가 있어도 재주입
  --author NAME         JSON-LD author 이름 (기본: "러닝 큐레이터 (allrunabout.com)")
  --url URL             글의 canonical URL (있으면 Article.url 에 사용)
  --skip-sources        참고 자료 섹션 추가 안 함 (JSON-LD 만)
  --skip-jsonld         JSON-LD 추가 안 함 (참고 자료만)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from blog_auto.pipeline.research import ResearchBundle  # noqa: E402
from blog_auto.utils.structured_data import (  # noqa: E402
    article,
    build_real_estate_jsonld,
    build_running_shoes_jsonld,
    faq_page,
    inject_jsonld,
    sources_to_markdown,
)

DEFAULT_AUTHOR = "러닝 큐레이터 (allrunabout.com)"
JSONLD_PLATFORMS = {"tistory", "blogger", "blogger_stocks", "blogger_money"}
JSONLD_MARKER = '<script type="application/ld+json">'
SOURCES_HEADING = "## 참고 자료"
DISCLAIMER_HEADING = "## 면책 조항"

# YMYL 도메인에서 글 말미에 자동 삽입하는 면책 텍스트.
# Google Quality Rater Guide 의 "Need High E-E-A-T" 카테고리 대응.
DISCLAIMERS: dict[str, str] = {
    "apartment_subscription": (
        "본 글은 청약홈, LH, SH 등 공식 자료를 정리한 정보 제공용 콘텐츠입니다. "
        "자격·일정·분양가는 발행 시점 기준이며, 청약 신청은 본인 판단·본인 책임 하에 "
        "진행해야 합니다. 신청 전 반드시 [청약홈](https://www.applyhome.co.kr/) 또는 "
        "해당 시행사 공식 공고문에서 최종 내용을 확인하세요."
    ),
}


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """`--- ... ---\\n\\n<body>` 형식의 frontmatter 분리."""
    m = re.match(r"^---\n(.*?)\n---\n\n?(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm_raw, body = m.groups()
    meta: dict[str, str] = {}
    for line in fm_raw.splitlines():
        k, _, v = line.partition(":")
        if k.strip():
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


def _extract_description(body: str, fallback: str) -> str:
    """본문 첫 단락에서 한 줄짜리 description 뽑기."""
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("!") or s.startswith("<"):
            continue
        return s[:160]
    return fallback[:160]


def _build_jsonld_docs(
    bundle: ResearchBundle,
    *,
    headline: str,
    description: str,
    author: str,
    url: str | None,
) -> list[dict]:
    """도메인별 JSON-LD 묶음 생성."""
    if bundle.domain == "running_shoes":
        return build_running_shoes_jsonld(
            bundle,
            headline=headline,
            description=description,
            author=author,
            url=url,
        )

    if bundle.domain == "apartment_subscription":
        return build_real_estate_jsonld(
            bundle,
            headline=headline,
            description=description,
            author=author,
            url=url,
        )

    docs: list[dict] = [
        article(
            headline=headline,
            description=description,
            author=author,
            date_published=bundle.last_updated,
            url=url,
        )
    ]
    fp = faq_page(bundle.faqs)
    if fp:
        docs.append(fp)
    return docs


def _summarize_diff(orig: str, new: str) -> str:
    added = len(new) - len(orig)
    jsonld_count = new.count(JSONLD_MARKER) - orig.count(JSONLD_MARKER)
    sources_added = SOURCES_HEADING in new and SOURCES_HEADING not in orig
    return (
        f"  +{added:,} chars, "
        f"+{jsonld_count} JSON-LD blocks, "
        f"sources={'added' if sources_added else 'unchanged'}"
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("markdown_path", help="대상 마크다운 파일 (frontmatter 포함)")
    ap.add_argument(
        "--research", required=True, help="assets/research/<slug>.json 의 slug"
    )
    ap.add_argument("--dry-run", action="store_true", help="변경 미리보기만")
    ap.add_argument(
        "-o", "--output", default="", help="다른 경로에 저장 (기본: 입력 파일 in-place)"
    )
    ap.add_argument(
        "--force", action="store_true", help="기존 JSON-LD/참고자료 있어도 재주입"
    )
    ap.add_argument("--author", default=DEFAULT_AUTHOR, help="JSON-LD author 이름")
    ap.add_argument("--url", default="", help="글 canonical URL (Article.url)")
    ap.add_argument("--skip-sources", action="store_true", help="참고 자료 섹션 생략")
    ap.add_argument("--skip-jsonld", action="store_true", help="JSON-LD 블록 생략")
    ap.add_argument(
        "--skip-disclaimer",
        action="store_true",
        help="YMYL 도메인 면책 자동 삽입 생략",
    )
    args = ap.parse_args()

    md_path = Path(args.markdown_path).resolve()
    if not md_path.exists():
        print(f"✗ 파일 없음: {md_path}")
        return 1

    bundle = ResearchBundle.load(args.research)
    print(
        f"📦 research: {args.research}  "
        f"(domain={bundle.domain}, shoes={len(bundle.shoes)}, "
        f"faqs={len(bundle.faqs)}, sources={len(bundle.all_sources())})"
    )

    original = md_path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(original)
    platform = meta.get("platform", "tistory")
    title = meta.get("title") or bundle.topic

    # 중복 체크
    has_jsonld = JSONLD_MARKER in original
    has_sources = SOURCES_HEADING in original
    has_disclaimer = DISCLAIMER_HEADING in original
    if (has_jsonld or has_sources or has_disclaimer) and not args.force:
        print(
            f"⚠️  이미 주입돼 있음 (jsonld={has_jsonld}, sources={has_sources}, "
            f"disclaimer={has_disclaimer}). --force 로 덮어쓰기."
        )
        return 2

    new_md = original

    # 1) YMYL 면책 (도메인이 매핑된 경우만)
    disclaimer_text = DISCLAIMERS.get(bundle.domain, "")
    if disclaimer_text and not args.skip_disclaimer:
        new_md = (
            new_md.rstrip()
            + "\n\n"
            + f"{DISCLAIMER_HEADING}\n\n> {disclaimer_text}\n"
        )
        print(f"  + 면책 조항 (YMYL domain={bundle.domain})")

    # 2) 참고 자료 섹션
    if not args.skip_sources:
        srcs = bundle.all_sources()
        if srcs:
            new_md = new_md.rstrip() + "\n\n" + sources_to_markdown(srcs)
            print(f"  + 참고 자료 {len(srcs)} 개 추가")
        else:
            print("  - 참고 자료 없음 (bundle 에 sources 비어 있음)")

    # 3) JSON-LD 블록 (네이버 제외)
    jsonld_skipped_reason = ""
    if args.skip_jsonld:
        jsonld_skipped_reason = "--skip-jsonld"
    elif platform not in JSONLD_PLATFORMS:
        jsonld_skipped_reason = f"platform={platform} (SmartEditor 가 <script> 제거)"

    if jsonld_skipped_reason:
        print(f"  - JSON-LD 스킵: {jsonld_skipped_reason}")
    else:
        description = _extract_description(body, bundle.topic)
        docs = _build_jsonld_docs(
            bundle,
            headline=title,
            description=description,
            author=args.author,
            url=args.url or None,
        )
        new_md = inject_jsonld(new_md, docs, placement="end")
        print(f"  + JSON-LD {len(docs)} 블록 추가 ({[d['@type'] for d in docs]})")

    if new_md == original:
        print("변경 없음.")
        return 0

    print()
    print("DIFF SUMMARY:")
    print(_summarize_diff(original, new_md))

    if args.dry_run:
        print("\n[--dry-run] 파일 안 건드림.")
        return 0

    out_path = Path(args.output).resolve() if args.output else md_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(new_md, encoding="utf-8")
    print(f"\n✅ 저장: {out_path.relative_to(ROOT) if out_path.is_relative_to(ROOT) else out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
