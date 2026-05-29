"""Phase 0 GEO 파이프라인 데모.

generate() 를 건드리지 않고 신규 모듈들이 어떻게 동작하는지 보여준다:
  1) ResearchBundle 을 JSON 에서 로드
  2) as_prompt_context() — 프롬프트에 주입될 텍스트 미리보기
  3) build_running_shoes_jsonld() — Schema.org JSON-LD 묶음 생성
  4) inject_jsonld() — 마크다운 끝에 <script> 블록 추가
  5) sources_to_markdown() — 참고 자료 섹션 생성

실행:
  python scripts/geo_demo.py
또는:
  python scripts/geo_demo.py 2026_beginner_running_shoes_best5
"""

from __future__ import annotations

import sys
from pathlib import Path

# blog-auto/scripts/ 에서 직접 실행 가능하도록 src 경로 추가
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from blog_auto.pipeline.research import ResearchBundle  # noqa: E402
from blog_auto.utils.structured_data import (  # noqa: E402
    build_running_shoes_jsonld,
    inject_jsonld,
    sources_to_markdown,
)


def main(slug: str = "2026_beginner_running_shoes_best5") -> None:
    bundle = ResearchBundle.load(slug)

    print("=" * 70)
    print(f"📦 LOADED: {slug}")
    print(f"   domain={bundle.domain}, shoes={len(bundle.shoes)}, "
          f"faqs={len(bundle.faqs)}, sources={len(bundle.all_sources())}")
    print("=" * 70)

    # 1) 프롬프트에 들어갈 컨텍스트 미리보기 ----------------------------
    print("\n[1] PROMPT CONTEXT (outline.j2 / draft.j2 의 {{ context }} 에 주입될 텍스트)")
    print("-" * 70)
    print(bundle.as_prompt_context())

    # 2) JSON-LD 묶음 -----------------------------------------------------
    docs = build_running_shoes_jsonld(
        bundle,
        headline=bundle.topic,
        description="입문자가 가장 자주 찾는 데일리 트레이닝화 5종을 스펙·가격·장단점 기준으로 비교합니다.",
        author="러닝 큐레이터 (allrunabout.com)",
        url="https://allrunabout.com/posts/beginner-shoes-2026",
        publisher_name="All Run About",
    )
    print("\n[2] JSON-LD DOCS GENERATED:", [d["@type"] for d in docs])

    # 3) 마크다운에 주입 ---------------------------------------------------
    sample_md = (
        "---\n"
        f"title: {bundle.topic}\n"
        "platform: tistory\n"
        "---\n\n"
        "# 본문은 generate() 가 만들 자리입니다 (Phase 1 에서 통합).\n\n"
        "여기에 LLM 이 생성한 마크다운 글이 들어갑니다.\n"
    )

    with_sources = sample_md + "\n" + sources_to_markdown(bundle.all_sources())
    final_md = inject_jsonld(with_sources, docs, placement="end")

    out = ROOT / "posts" / "_drafts" / f"GEO_DEMO__{slug}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(final_md, encoding="utf-8")

    print(f"\n[3] WROTE DEMO POST → {out.relative_to(ROOT)}")
    print(f"    ({len(final_md):,} chars, JSON-LD 블록 {len(docs)} 개 포함)")
    print("\n끝. 다음 단계 (Phase 1) 에서 outline.j2 가 bundle.as_prompt_context() 를 받도록 통합합니다.")


if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else "2026_beginner_running_shoes_best5"
    main(slug)
