"""Schema.org JSON-LD 빌더.

LLM(ChatGPT/Claude/Perplexity) 과 검색엔진이 글을 '인용'할 때 가장 먼저
보는 신호가 구조화 데이터다. 같은 글이라도 JSON-LD 가 있으면 인용
가능성이 크게 올라간다.

설계 원칙
- 각 schema 는 plain dict 를 반환 (json.dumps 로 바로 직렬화 가능)
- 입력 dict 에 None / 빈 값이 들어오면 조용히 제거 (Schema.org validator 통과용)
- ResearchBundle 과 직접 연계되는 통합 빌더 1 개 (build_running_shoes_jsonld)
- 플랫폼별 주입은 호출부에서 결정 (티스토리/Blogger 는 <script>, 네이버는 텍스트 fallback)
"""

from __future__ import annotations

import json
from typing import Any

from blog_auto.pipeline.research import (
    FAQ,
    ApartmentSubscription,
    ResearchBundle,
    ShoeSpec,
    Source,
)

SCHEMA_CTX = "https://schema.org"


# ---- Low-level dict cleaner -------------------------------------------------


def _clean(d: dict[str, Any]) -> dict[str, Any]:
    """None / 빈 컬렉션 제거 후 반환. 중첩 dict 재귀."""
    out: dict[str, Any] = {}
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, dict):
            cleaned = _clean(v)
            if cleaned:
                out[k] = cleaned
        elif isinstance(v, list):
            cleaned_list = [
                _clean(i) if isinstance(i, dict) else i
                for i in v
                if i not in (None, "", [], {})
            ]
            if cleaned_list:
                out[k] = cleaned_list
        elif v == "" or v == []:
            continue
        else:
            out[k] = v
    return out


# ---- Schema builders --------------------------------------------------------


def article(
    *,
    headline: str,
    description: str,
    author: str,
    date_published: str,
    date_modified: str | None = None,
    image: str | None = None,
    url: str | None = None,
    publisher_name: str | None = None,
    publisher_logo: str | None = None,
) -> dict[str, Any]:
    return _clean(
        {
            "@context": SCHEMA_CTX,
            "@type": "Article",
            "headline": headline,
            "description": description,
            "author": {"@type": "Person", "name": author} if author else None,
            "datePublished": date_published,
            "dateModified": date_modified or date_published,
            "image": image,
            "url": url,
            "publisher": (
                {
                    "@type": "Organization",
                    "name": publisher_name,
                    "logo": (
                        {"@type": "ImageObject", "url": publisher_logo}
                        if publisher_logo
                        else None
                    ),
                }
                if publisher_name
                else None
            ),
        }
    )


def faq_page(faqs: list[FAQ]) -> dict[str, Any] | None:
    if not faqs:
        return None
    return _clean(
        {
            "@context": SCHEMA_CTX,
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": f.q,
                    "acceptedAnswer": {"@type": "Answer", "text": f.a},
                }
                for f in faqs
            ],
        }
    )


def shoe_to_product(shoe: ShoeSpec) -> dict[str, Any]:
    """ShoeSpec → schema.org Product."""
    additional_props = []
    if shoe.weight_g:
        additional_props.append(
            {"@type": "PropertyValue", "name": "무게", "value": f"{shoe.weight_g}g"}
        )
    if shoe.drop_mm is not None:
        additional_props.append(
            {"@type": "PropertyValue", "name": "드롭", "value": f"{shoe.drop_mm}mm"}
        )
    if shoe.stack_mm is not None:
        additional_props.append(
            {"@type": "PropertyValue", "name": "스택 높이", "value": f"{shoe.stack_mm}mm"}
        )
    if shoe.midsole:
        additional_props.append(
            {"@type": "PropertyValue", "name": "미드솔", "value": shoe.midsole}
        )

    return _clean(
        {
            "@type": "Product",
            "name": shoe.full_name,
            "brand": {"@type": "Brand", "name": shoe.brand},
            "category": shoe.category,
            "releaseDate": str(shoe.release_year) if shoe.release_year else None,
            "additionalProperty": additional_props,
            "offers": (
                {
                    "@type": "Offer",
                    "priceCurrency": "KRW",
                    "price": shoe.price_krw,
                    "availability": "https://schema.org/InStock",
                }
                if shoe.price_krw
                else None
            ),
        }
    )


def item_list(
    name: str,
    items: list[dict[str, Any]],
    description: str | None = None,
) -> dict[str, Any] | None:
    if not items:
        return None
    return _clean(
        {
            "@context": SCHEMA_CTX,
            "@type": "ItemList",
            "name": name,
            "description": description,
            "numberOfItems": len(items),
            "itemListElement": [
                {"@type": "ListItem", "position": i, "item": item}
                for i, item in enumerate(items, 1)
            ],
        }
    )


def how_to(
    name: str,
    steps: list[dict[str, str]],
    description: str | None = None,
    total_time: str | None = None,
) -> dict[str, Any] | None:
    """steps: [{'name': '..', 'text': '..'}, ...]"""
    if not steps:
        return None
    return _clean(
        {
            "@context": SCHEMA_CTX,
            "@type": "HowTo",
            "name": name,
            "description": description,
            "totalTime": total_time,
            "step": [
                {
                    "@type": "HowToStep",
                    "position": i,
                    "name": s.get("name", ""),
                    "text": s["text"],
                }
                for i, s in enumerate(steps, 1)
            ],
        }
    )


def breadcrumb(items: list[tuple[str, str]]) -> dict[str, Any] | None:
    """items: [(name, url), ...]"""
    if not items:
        return None
    return _clean(
        {
            "@context": SCHEMA_CTX,
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i, "name": name, "item": url}
                for i, (name, url) in enumerate(items, 1)
            ],
        }
    )


def apartment_to_residence(apt: ApartmentSubscription) -> dict[str, Any]:
    """ApartmentSubscription → schema.org Residence (Apartment 의 상위 타입).

    부동산 청약 데이터의 LLM 인용 시그널. 가격 범위·일정·자격을 구조화.
    """
    additional_props: list[dict[str, Any]] = []
    if apt.supply_type:
        additional_props.append(
            {"@type": "PropertyValue", "name": "공급유형", "value": apt.supply_type}
        )
    if apt.total_units:
        additional_props.append(
            {"@type": "PropertyValue", "name": "총세대수", "value": apt.total_units}
        )
    if apt.available_units is not None:
        additional_props.append(
            {"@type": "PropertyValue", "name": "잔여세대수", "value": apt.available_units}
        )
    if apt.sizes_m2:
        additional_props.append(
            {
                "@type": "PropertyValue",
                "name": "공급면적",
                "value": ", ".join(f"{s}㎡" for s in apt.sizes_m2),
            }
        )
    if apt.eligibility:
        additional_props.append(
            {"@type": "PropertyValue", "name": "자격요건", "value": " / ".join(apt.eligibility)}
        )

    offers: dict[str, Any] | None = None
    if apt.price_min_krw:
        offers = {
            "@type": "Offer",
            "priceCurrency": "KRW",
            "price": apt.price_min_krw,
            "availabilityStarts": apt.application_start or None,
            "availabilityEnds": apt.application_end or None,
            "url": apt.application_url or None,
        }
        if apt.price_max_krw and apt.price_max_krw != apt.price_min_krw:
            offers["priceSpecification"] = {
                "@type": "PriceSpecification",
                "minPrice": apt.price_min_krw,
                "maxPrice": apt.price_max_krw,
                "priceCurrency": "KRW",
            }

    return _clean(
        {
            "@type": "Residence",
            "name": apt.name,
            "address": apt.location,
            "additionalProperty": additional_props,
            "offers": offers,
            "url": apt.application_url or apt.official_notice_url or None,
        }
    )


def review(
    *,
    item_reviewed: dict[str, Any],
    rating: float,
    best_rating: float = 5.0,
    author: str,
    review_body: str,
    date_published: str,
) -> dict[str, Any]:
    return _clean(
        {
            "@context": SCHEMA_CTX,
            "@type": "Review",
            "itemReviewed": item_reviewed,
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": rating,
                "bestRating": best_rating,
            },
            "author": {"@type": "Person", "name": author},
            "reviewBody": review_body,
            "datePublished": date_published,
        }
    )


# ---- High-level: ResearchBundle integration --------------------------------


def build_running_shoes_jsonld(
    bundle: ResearchBundle,
    *,
    headline: str,
    description: str,
    author: str,
    url: str | None = None,
    publisher_name: str | None = None,
) -> list[dict[str, Any]]:
    """러닝화 글 1편을 위한 JSON-LD 묶음.

    포함: Article + ItemList(Product[]) + FAQPage (있을 때만)
    """
    docs: list[dict[str, Any]] = []

    docs.append(
        article(
            headline=headline,
            description=description,
            author=author,
            date_published=bundle.last_updated,
            url=url,
            publisher_name=publisher_name,
        )
    )

    if bundle.shoes:
        product_items = [shoe_to_product(s) for s in bundle.shoes]
        lst = item_list(
            name=bundle.topic,
            items=product_items,
            description=description,
        )
        if lst:
            docs.append(lst)

    fp = faq_page(bundle.faqs)
    if fp:
        docs.append(fp)

    return docs


def build_real_estate_jsonld(
    bundle: ResearchBundle,
    *,
    headline: str,
    description: str,
    author: str,
    url: str | None = None,
    publisher_name: str | None = None,
) -> list[dict[str, Any]]:
    """부동산 청약 글 1편을 위한 JSON-LD 묶음.

    포함: Article + ItemList(Residence[]) + FAQPage (있을 때만)
    YMYL 콘텐츠의 E-E-A-T 시그널 강화용.
    """
    docs: list[dict[str, Any]] = []

    docs.append(
        article(
            headline=headline,
            description=description,
            author=author,
            date_published=bundle.last_updated,
            url=url,
            publisher_name=publisher_name,
        )
    )

    if bundle.apartments:
        items = [apartment_to_residence(a) for a in bundle.apartments]
        lst = item_list(name=bundle.topic, items=items, description=description)
        if lst:
            docs.append(lst)

    fp = faq_page(bundle.faqs)
    if fp:
        docs.append(fp)

    return docs


# ---- Serialization / injection ---------------------------------------------


def to_script_tag(jsonld: dict[str, Any] | list[dict[str, Any]]) -> str:
    """JSON-LD 1 개 또는 여러 개 → <script type="application/ld+json"> 블록."""
    payload = (
        [jsonld] if isinstance(jsonld, dict) else list(jsonld)
    )
    blocks = [
        f'<script type="application/ld+json">\n{json.dumps(d, ensure_ascii=False, indent=2)}\n</script>'
        for d in payload
        if d
    ]
    return "\n".join(blocks)


def inject_jsonld(
    markdown: str,
    jsonld: dict[str, Any] | list[dict[str, Any]],
    *,
    placement: str = "end",
) -> str:
    """마크다운에 JSON-LD 블록을 삽입.

    placement: 'end' (default, 글 말미) | 'start' (frontmatter 다음)
    """
    block = to_script_tag(jsonld)
    if not block:
        return markdown

    if placement == "start":
        # frontmatter (--- ... ---) 다음 위치 찾기
        if markdown.startswith("---"):
            end = markdown.find("\n---", 3)
            if end != -1:
                cut = end + len("\n---")
                return markdown[:cut] + "\n\n" + block + "\n" + markdown[cut:]
        return block + "\n\n" + markdown

    # default: end
    sep = "\n\n" if not markdown.endswith("\n") else "\n"
    return markdown + sep + block + "\n"


def sources_to_markdown(sources: list[Source], heading: str = "## 참고 자료") -> str:
    """ResearchBundle.all_sources() 결과를 글 말미용 마크다운으로 변환."""
    if not sources:
        return ""
    lines = [heading, ""]
    for s in sources:
        line = f"- {s.to_citation()}"
        if s.publisher:
            line += f" — {s.publisher}"
        lines.append(line)
    return "\n".join(lines) + "\n"
