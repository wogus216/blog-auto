"""GEO 우선 파이프라인의 리서치 단계.

글을 쓰기 *전* 에 수집한 사실/수치/출처를 한 곳에 묶어 둔다.
generate() 에 주입되면:
  - 프롬프트 컨텍스트가 "실측 수치 + 출처" 기반으로 깊어진다
  - structured_data 빌더가 Schema.org JSON-LD 를 자동 생성한다
  - critic 이 "근거(grounding) 있는 글인지" 평가할 수 있다

Phase 0 (현재): JSON 파일 로드만 지원. 자동 fetch 는 Phase 2+ 에서 추가.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal

from blog_auto import config

RESEARCH_DIR = config.ROOT / "assets" / "research"

Domain = Literal[
    "running_shoes",
    "stocks",
    "baseball",
    "apartment_subscription",  # 부동산 청약 (money.onestepblog.info 등)
    "generic",
]


@dataclass(frozen=True)
class Source:
    """단일 출처. 인용 신뢰도의 단위."""

    title: str
    url: str
    accessed_at: str  # YYYY-MM-DD
    publisher: str = ""

    def to_citation(self) -> str:
        date_part = f" (확인 {self.accessed_at})" if self.accessed_at else ""
        return f"[{self.title}]({self.url}){date_part}"


@dataclass
class FAQ:
    q: str
    a: str
    source: Source | None = None


@dataclass
class ShoeSpec:
    """러닝화 1종의 실측/공식 스펙. ItemList/Product schema 의 원천."""

    brand: str
    model: str
    category: str  # "데일리 트레이닝" / "레이싱" / "회복주" 등
    weight_g: int | None = None
    drop_mm: float | None = None
    stack_mm: float | None = None
    price_krw: int | None = None
    release_year: int | None = None
    midsole: str = ""
    best_for: list[str] = field(default_factory=list)
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)
    source: Source | None = None

    @property
    def full_name(self) -> str:
        return f"{self.brand} {self.model}"

    def spec_summary(self) -> str:
        """프롬프트에 주입할 한 줄 요약."""
        bits = []
        if self.weight_g:
            bits.append(f"{self.weight_g}g")
        if self.drop_mm is not None:
            bits.append(f"드롭 {self.drop_mm}mm")
        if self.stack_mm is not None:
            bits.append(f"스택 {self.stack_mm}mm")
        if self.price_krw:
            bits.append(f"{self.price_krw:,}원")
        spec = " · ".join(bits) if bits else ""
        tail = f" [{self.category}]" if self.category else ""
        return f"{self.full_name}{tail}{' — ' + spec if spec else ''}"


@dataclass
class ApartmentSubscription:
    """청약 단지 1개의 공식 정보. '공식 자료 큐레이터' 포지셔닝의 핵심.

    YMYL niche 이므로 모든 필드는 공식 출처 (청약홈/LH/SH/지자체) 기준이어야 한다.
    """

    name: str  # 단지명 (예: "별내 퍼스트포레")
    location: str = ""  # 위치 (예: "경기도 남양주시 별내동")
    supply_type: str = ""  # 공급 유형 (공공분양/민간분양/신혼희망타운/특별공급/무순위)
    total_units: int | None = None
    available_units: int | None = None  # 잔여 (무순위/줍줍 등)
    sizes_m2: list[float] = field(default_factory=list)  # 면적 (m²) 후보
    price_min_krw: int | None = None
    price_max_krw: int | None = None
    application_start: str = ""  # ISO datetime (YYYY-MM-DD HH:MM)
    application_end: str = ""
    announcement_date: str = ""  # 당첨자 발표일
    contract_date: str = ""  # 계약일
    eligibility: list[str] = field(default_factory=list)  # 자격 요건 bullets
    application_url: str = ""  # 청약 신청 URL (청약홈/LH 등)
    official_notice_url: str = ""  # 공고문 PDF
    floor_plan_url: str = ""  # 평면도
    map_url: str = ""  # 배치도/지도
    source: Source | None = None  # 메인 출처 (필수 권장)

    @property
    def price_range_label(self) -> str:
        def _b(krw: int) -> str:
            return f"{krw/100_000_000:.2f}억"
        if self.price_min_krw and self.price_max_krw:
            if self.price_min_krw == self.price_max_krw:
                return f"약 {_b(self.price_min_krw)}"
            return f"{_b(self.price_min_krw)} ~ {_b(self.price_max_krw)}"
        if self.price_min_krw:
            return f"약 {_b(self.price_min_krw)}"
        return ""

    @property
    def schedule_label(self) -> str:
        if self.application_start and self.application_end:
            return f"{self.application_start} ~ {self.application_end}"
        return self.application_start or self.application_end

    def spec_summary(self) -> str:
        """프롬프트에 주입할 한 줄 요약."""
        bits = [self.name]
        if self.location:
            bits.append(self.location)
        if self.supply_type:
            bits.append(f"[{self.supply_type}]")
        if self.available_units and self.total_units:
            bits.append(f"잔여 {self.available_units}/{self.total_units}세대")
        elif self.total_units:
            bits.append(f"{self.total_units}세대")
        if self.price_range_label:
            bits.append(self.price_range_label)
        return " · ".join(bits)


@dataclass
class ResearchBundle:
    """글 1편을 위한 리서치 데이터 컨테이너.

    하나의 ResearchBundle = 하나의 글 = 하나의 JSON 파일.
    """

    domain: Domain
    topic: str
    last_updated: str
    shoes: list[ShoeSpec] = field(default_factory=list)
    apartments: list[ApartmentSubscription] = field(default_factory=list)
    faqs: list[FAQ] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    # ---- Loading ----------------------------------------------------------

    @classmethod
    def from_json(cls, path: Path | str) -> "ResearchBundle":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchBundle":
        def _src(d: dict[str, Any] | None) -> Source | None:
            if not d:
                return None
            return Source(
                title=d["title"],
                url=d["url"],
                accessed_at=d.get("accessed_at", ""),
                publisher=d.get("publisher", ""),
            )

        shoes = [
            ShoeSpec(
                brand=s["brand"],
                model=s["model"],
                category=s.get("category", ""),
                weight_g=s.get("weight_g"),
                drop_mm=s.get("drop_mm"),
                stack_mm=s.get("stack_mm"),
                price_krw=s.get("price_krw"),
                release_year=s.get("release_year"),
                midsole=s.get("midsole", ""),
                best_for=s.get("best_for", []),
                pros=s.get("pros", []),
                cons=s.get("cons", []),
                source=_src(s.get("source")),
            )
            for s in data.get("shoes", [])
        ]
        apartments = [
            ApartmentSubscription(
                name=a["name"],
                location=a.get("location", ""),
                supply_type=a.get("supply_type", ""),
                total_units=a.get("total_units"),
                available_units=a.get("available_units"),
                sizes_m2=a.get("sizes_m2", []),
                price_min_krw=a.get("price_min_krw"),
                price_max_krw=a.get("price_max_krw"),
                application_start=a.get("application_start", ""),
                application_end=a.get("application_end", ""),
                announcement_date=a.get("announcement_date", ""),
                contract_date=a.get("contract_date", ""),
                eligibility=a.get("eligibility", []),
                application_url=a.get("application_url", ""),
                official_notice_url=a.get("official_notice_url", ""),
                floor_plan_url=a.get("floor_plan_url", ""),
                map_url=a.get("map_url", ""),
                source=_src(a.get("source")),
            )
            for a in data.get("apartments", [])
        ]
        faqs = [
            FAQ(q=f["q"], a=f["a"], source=_src(f.get("source")))
            for f in data.get("faqs", [])
        ]
        sources = [_src(s) for s in data.get("sources", []) if s]
        return cls(
            domain=data.get("domain", "generic"),
            topic=data["topic"],
            last_updated=data.get("last_updated", date.today().isoformat()),
            shoes=shoes,
            apartments=apartments,
            faqs=faqs,
            sources=[s for s in sources if s is not None],
            extra=data.get("extra", {}),
        )

    @classmethod
    def load(cls, slug: str) -> "ResearchBundle":
        """assets/research/{slug}.json 로드."""
        return cls.from_json(RESEARCH_DIR / f"{slug}.json")

    # ---- Prompt injection -------------------------------------------------

    def as_prompt_context(self) -> str:
        """프롬프트에 그대로 붙일 수 있는 텍스트 블록.

        outline.j2 / draft.j2 의 {{ context }} 자리에 주입되는 것을 가정.
        '추측하지 말고 이 사실만 써라' 신호로 작동.
        """
        lines = [
            f"[리서치 데이터 — {self.last_updated} 기준]",
            f"주제: {self.topic}",
            "",
        ]

        if self.shoes:
            lines.append("## 수집된 러닝화 스펙 (이 수치만 사용, 임의 추측 금지)")
            for i, s in enumerate(self.shoes, 1):
                lines.append(f"{i}. {s.spec_summary()}")
                if s.midsole:
                    lines.append(f"   - 미드솔: {s.midsole}")
                if s.best_for:
                    lines.append(f"   - 추천 대상: {', '.join(s.best_for)}")
                if s.pros:
                    lines.append(f"   - 장점: {', '.join(s.pros)}")
                if s.cons:
                    lines.append(f"   - 단점: {', '.join(s.cons)}")
                if s.source:
                    lines.append(f"   - 출처: {s.source.to_citation()}")
            lines.append("")

        if self.apartments:
            lines.append("## 수집된 청약 단지 정보 (공식 자료 기반 — 임의 변경 금지)")
            for i, a in enumerate(self.apartments, 1):
                lines.append(f"{i}. {a.spec_summary()}")
                if a.schedule_label:
                    lines.append(f"   - 청약일정: {a.schedule_label}")
                if a.announcement_date:
                    lines.append(f"   - 당첨발표: {a.announcement_date}")
                if a.contract_date:
                    lines.append(f"   - 계약일: {a.contract_date}")
                if a.eligibility:
                    for e in a.eligibility:
                        lines.append(f"   - 자격: {e}")
                if a.application_url:
                    lines.append(f"   - 청약신청: {a.application_url}")
                if a.official_notice_url:
                    lines.append(f"   - 공고문(PDF): {a.official_notice_url}")
                if a.source:
                    lines.append(f"   - 출처: {a.source.to_citation()}")
            lines.append("")
            lines.append(
                "[YMYL 작성 원칙] 부동산 청약은 사용자 자산과 직결되는 정보다. "
                "위 공식 자료에 명시된 수치/일정/자격만 사용하고, 본인 의견("
                "'좋다', '추천') 은 피한다. 모든 단정 문장은 출처를 인라인으로 표기한다. "
                "글 말미에 면책 한 줄 ('정보 제공용이며 청약 신청은 본인 책임') 을 반드시 포함."
            )

        if self.faqs:
            lines.append("## 사용자 자주 묻는 질문 (FAQ 섹션에 반영)")
            for f in self.faqs:
                lines.append(f"- Q: {f.q}")
                lines.append(f"  A: {f.a}")
            lines.append("")

        if self.sources:
            lines.append("## 인용 가능한 출처 (글 말미에 '참고 자료'로 노출)")
            for s in self.sources:
                lines.append(f"- {s.to_citation()}")
            lines.append("")

        lines.append(
            "[작성 규칙] 위 데이터에 없는 수치/사실은 만들지 않는다. "
            "단정형 문장은 출처가 있을 때만 사용한다."
        )
        return "\n".join(lines)

    # ---- Convenience ------------------------------------------------------

    @property
    def has_data(self) -> bool:
        return bool(self.shoes or self.apartments or self.faqs or self.sources)

    def all_sources(self) -> list[Source]:
        """shoes/apartments/faqs 안에 박힌 source 까지 모두 수집해 dedupe."""
        seen: dict[str, Source] = {}
        for s in self.sources:
            seen.setdefault(s.url, s)
        for shoe in self.shoes:
            if shoe.source:
                seen.setdefault(shoe.source.url, shoe.source)
        for apt in self.apartments:
            if apt.source:
                seen.setdefault(apt.source.url, apt.source)
        for f in self.faqs:
            if f.source:
                seen.setdefault(f.source.url, f.source)
        return list(seen.values())
