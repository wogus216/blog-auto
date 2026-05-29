"""ResearchBundle JSON 빈 템플릿 생성기.

GEO 모드로 글 1편을 쓰기 전에 리서치 데이터 JSON 을 손으로 채워야 한다.
이 스크립트는 도메인별 스켈레톤을 만들어 TODO 마커만 채우면 되도록 한다.

사용:
  python scripts/scaffold_research.py 2026_winter_running_shoes
  python scripts/scaffold_research.py my_topic --domain generic

이후:
  1) assets/research/<slug>.json 의 TODO 를 채운다 (각 공식 페이지 가서 스펙 확인)
  2) uv run blog-auto generate-post "주제" --research <slug>
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH_DIR = ROOT / "assets" / "research"


def _today() -> str:
    return date.today().isoformat()


def _shoe_skeleton() -> dict:
    return {
        "brand": "TODO 브랜드명",
        "model": "TODO 모델명",
        "category": "TODO 카테고리 (예: 데일리 트레이닝 / 레이싱 / 회복주)",
        "weight_g": 0,
        "drop_mm": 0,
        "stack_mm": 0,
        "price_krw": 0,
        "release_year": int(_today()[:4]),
        "midsole": "TODO 미드솔 폼/플레이트 정보",
        "best_for": ["TODO 추천 대상 1", "TODO 추천 대상 2"],
        "pros": ["TODO 장점 1", "TODO 장점 2"],
        "cons": ["TODO 단점 1"],
        "source": {
            "title": "TODO 공식 페이지 제목",
            "url": "https://TODO",
            "accessed_at": _today(),
            "publisher": "TODO 퍼블리셔 (예: Nike Korea)",
        },
    }


def _source_skeleton(label: str = "TODO 권위 자료 제목") -> dict:
    return {
        "title": label,
        "url": "https://TODO",
        "accessed_at": _today(),
        "publisher": "",
    }


def _faq_skeleton() -> dict:
    return {
        "q": "TODO 사용자가 자주 묻는 질문",
        "a": "TODO 답변. 가능한 한 수치 1개 이상 포함하고, 출처가 있으면 source 필드에 명시.",
    }


def running_shoes_template(topic_hint: str) -> dict:
    return {
        "domain": "running_shoes",
        "topic": topic_hint or "TODO 글 주제 (예: 2026 입문자 러닝화 BEST 5)",
        "last_updated": _today(),
        "shoes": [_shoe_skeleton() for _ in range(5)],
        "faqs": [_faq_skeleton() for _ in range(3)],
        "sources": [
            _source_skeleton("TODO 외부 권위 자료 (예: Runner's World 비교 리뷰)"),
        ],
        "extra": {
            "_note": "TODO 항목을 모두 채운 뒤 발행 전에 한 번 더 공식 페이지에서 스펙·가격을 검증하세요.",
            "target_keyword": "TODO 메인 검색 키워드 (예: 입문자 러닝화 추천)",
            "secondary_keywords": ["TODO 보조 키워드 1", "TODO 보조 키워드 2"],
        },
    }


def _apartment_skeleton() -> dict:
    return {
        "name": "TODO 단지명 (예: 별내 퍼스트포레)",
        "location": "TODO 위치 (예: 경기도 남양주시 별내동)",
        "supply_type": "TODO 공급유형 (공공분양 / 민간분양 / 신혼희망타운 / 특별공급 / 무순위)",
        "total_units": 0,
        "available_units": 0,
        "sizes_m2": [],
        "price_min_krw": 0,
        "price_max_krw": 0,
        "application_start": "YYYY-MM-DD HH:MM",
        "application_end": "YYYY-MM-DD HH:MM",
        "announcement_date": "YYYY-MM-DD",
        "contract_date": "YYYY-MM-DD",
        "eligibility": [
            "TODO 자격 요건 1 (예: 수도권 거주 무주택 세대구성원)",
            "TODO 자격 요건 2",
        ],
        "application_url": "https://www.applyhome.co.kr/TODO",
        "official_notice_url": "https://TODO/공고문.pdf",
        "floor_plan_url": "https://TODO/평면도",
        "map_url": "https://TODO/배치도",
        "source": {
            "title": "TODO 공식 공고 페이지 제목",
            "url": "https://TODO",
            "accessed_at": _today(),
            "publisher": "청약홈 / LH / SH / 시행사 등",
        },
    }


def apartment_subscription_template(topic_hint: str) -> dict:
    return {
        "domain": "apartment_subscription",
        "topic": topic_hint or "TODO 글 주제 (예: 9월 5주차 잔여공급 청약 정리)",
        "last_updated": _today(),
        "apartments": [_apartment_skeleton()],
        "faqs": [
            {
                "q": "TODO 자주 묻는 질문 (예: 무순위와 줍줍 차이?)",
                "a": "TODO 답변. 가능한 한 공식 출처(청약홈/LH) 의 정의 인용.",
            }
        ],
        "sources": [
            {
                "title": "청약홈 메인",
                "url": "https://www.applyhome.co.kr/",
                "accessed_at": _today(),
                "publisher": "한국부동산원",
            },
        ],
        "extra": {
            "_note": "YMYL 콘텐츠입니다. 모든 수치/일정/자격은 공고문 기준이어야 하고, 발행 전에 공식 페이지에서 한 번 더 확인하세요.",
            "target_keyword": "TODO 메인 검색 키워드 (예: 별내 퍼스트포레 청약)",
            "secondary_keywords": ["TODO 단지명 + 분양가", "TODO 단지명 + 평면도"],
        },
    }


def generic_template(topic_hint: str) -> dict:
    return {
        "domain": "generic",
        "topic": topic_hint or "TODO 글 주제",
        "last_updated": _today(),
        "shoes": [],
        "faqs": [_faq_skeleton() for _ in range(3)],
        "sources": [
            _source_skeleton(),
            _source_skeleton(),
        ],
        "extra": {
            "_note": "TODO 항목을 모두 채운 뒤 발행하세요.",
            "target_keyword": "",
            "secondary_keywords": [],
        },
    }


TEMPLATES = {
    "running_shoes": running_shoes_template,
    "apartment_subscription": apartment_subscription_template,
    "generic": generic_template,
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug", help="파일명 (assets/research/<slug>.json 으로 저장)")
    ap.add_argument(
        "--domain",
        default="running_shoes",
        choices=sorted(TEMPLATES.keys()),
        help="도메인 선택 (기본: running_shoes)",
    )
    ap.add_argument(
        "--topic",
        default="",
        help="topic 필드 초기값 (생략 시 TODO 마커)",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="기존 파일 덮어쓰기 허용",
    )
    args = ap.parse_args()

    out = RESEARCH_DIR / f"{args.slug}.json"
    if out.exists() and not args.force:
        print(f"✗ 이미 존재: {out.relative_to(ROOT)}  (--force 로 덮어쓰기)")
        sys.exit(1)

    out.parent.mkdir(parents=True, exist_ok=True)
    payload = TEMPLATES[args.domain](args.topic)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"✅ Created: {out.relative_to(ROOT)}")
    print(f"   domain: {args.domain}")
    print()
    print("Next steps:")
    print(f"  1) 에디터로 {out.relative_to(ROOT)} 열어서 TODO 마커를 채우세요.")
    print( "     - 각 모델/항목의 공식 페이지 URL 과 'accessed_at' 날짜를 정확히 기록.")
    print( "     - 추측 금지. 모르는 값은 비워두고 발행 전에 확인.")
    print(f"  2) uv run blog-auto generate-post \"<글 주제>\" --research {args.slug}")


if __name__ == "__main__":
    main()
