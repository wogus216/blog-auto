"""데이터 시각화 카드 — 본문 토큰을 검증된 인포그래픽 HTML로 치환.

월드컵 일정 카드처럼 매번 손으로 짜던 inline HTML을, 짧은 펜스 토큰으로
대체한다. broker_assets 와 동일한 후처리 패턴(발행 직전 본문 치환)이라
실제 운영 워크플로(Claude 가 마크다운 직접 작성 → 발행)에 그대로 얹힌다.

토큰 형식 (markdown 친화 fenced div):

    :::schedule 한국 A조 조별리그 일정
    6/12(금) 11:00 | 체코 | 과달라하라
    6/19(금) 10:00 | 멕시코 | 과달라하라
    6/25(목) 10:00 | 남아공 | 몬테레이
    :::

지원 타입:
  schedule  날짜·시간 카드 그리드 (각 줄: 큰글씨 | 메인 | 보조)
  stat      KPI 하이라이트 박스   (각 줄: 숫자 | 라벨)
  compare   2~3열 비교 카드        (각 줄: 컬럼명 | 항목/항목/항목 | best?)
  rank      TOP 순위 리스트        (각 줄: 항목 | 값/설명)  순위 자동·메달색
  spec      라벨-값 스펙 카드      (각 줄: 라벨 | 값)

테마 (용도별 톤):
  vivid     선명한 그라디언트·생기 — 티스토리(러닝/야구)·consistency(스포츠)
  refined   채도 낮춘 딥톤·차분 고급 — money(부동산)·stocks(주식) 등 YMYL
  호출부(cli.py)에서 platform 보고 자동 선택. 기본은 vivid.

설계 원칙
- inline style 만 사용 (티스토리 TinyMCE·Blogger 모두 외부 CSS 불가).
- 반응형: grid auto-fit + minmax 로 모바일에서 자동 줄바꿈.
- 데이터는 HTML escape (사용자 텍스트에 <,>,& 들어가도 안 깨짐).
- ⚠️ HTML 출력이므로 네이버(SmartEditor)는 표 컴포넌트로 못 받는다.
  호출부에서 platform 분기 — 네이버는 strip_viz_cards()로 텍스트 폴백.
"""

from __future__ import annotations

import html as _html
import re

from blog_auto.utils.html_enhance import (
    GRAY_BORDER,
    PRIMARY,
    PRIMARY_DARK,
    TEXT,
)

# ── 테마: 용도별 톤 ───────────────────────────────────────────────────
# palette = 카드 배경 그라디언트(진한 색 → 흰 글씨) 로테이션
THEMES: dict[str, dict] = {
    "vivid": {  # 생기 — 티스토리(러닝/야구)·consistency(스포츠)
        "palette": [
            ("#dc2626", "#991b1b"),  # red
            ("#059669", "#065f46"),  # green
            ("#2563eb", "#1e40af"),  # blue
            ("#7c3aed", "#5b21b6"),  # purple
            ("#d97706", "#92400e"),  # amber
            ("#0891b2", "#155e75"),  # cyan
        ],
        "shadow": "0 2px 10px rgba(0,0,0,.08)",
        "shadow_soft": "0 2px 8px rgba(0,0,0,.06)",
        "radius": "12px",
        "accent": PRIMARY,        # compare 추천 헤더·테두리
        "accent_dark": PRIMARY_DARK,  # 제목바
        "badge": "#f59e0b",       # 추천 배지
    },
    "refined": {  # 차분 고급 — money(부동산)·stocks(주식) YMYL
        "palette": [
            ("#475569", "#334155"),  # slate
            ("#1e3a5f", "#16293f"),  # deep navy
            ("#0f766e", "#0c5d57"),  # deep teal
            ("#9f1239", "#7d0e2d"),  # burgundy
            ("#4338ca", "#372fa3"),  # indigo
            ("#92400e", "#78340f"),  # bronze
        ],
        "shadow": "0 1px 4px rgba(0,0,0,.06)",
        "shadow_soft": "0 1px 3px rgba(0,0,0,.05)",
        "radius": "10px",
        "accent": "#1e3a5f",      # 차분한 네이비 강조
        "accent_dark": "#16293f",
        "badge": "#b45309",       # 절제된 브론즈 배지
    },
}
DEFAULT_THEME = "vivid"

# platform → theme (cli.py 가 참조)
PLATFORM_THEME = {
    "tistory": "vivid",
    "blogger": "vivid",          # consistency(꾸준함이 재능) = 스포츠
    "blogger_stocks": "refined",
    "blogger_money": "refined",
    "naver": "vivid",            # 어차피 strip_viz_cards 텍스트 폴백 — 무관
}

_MEDAL = ["#f59e0b", "#9ca3af", "#b45309"]  # 금·은·동 (테마 공통)

# :::type 제목  ...본문...  ::: (한 블록)
_BLOCK_RE = re.compile(
    r"^:::[ \t]*(\w+)[ \t]*(.*?)[ \t]*\n(.*?)\n:::[ \t]*$",
    re.MULTILINE | re.DOTALL,
)


def _esc(s: str) -> str:
    return _html.escape(s.strip())


def _rows(body: str) -> list[list[str]]:
    """블록 본문을 줄 → '|' 분할 필드 리스트로. 빈 줄/주석(#) 무시."""
    out: list[list[str]] = []
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.append([c.strip() for c in line.split("|")])
    return out


def _title_bar(title: str, th: dict) -> str:
    if not title:
        return ""
    return (
        f'<div style="font-weight:800;font-size:17px;color:{th["accent_dark"]};'
        f'margin:0 0 14px;padding-left:11px;border-left:5px solid {th["accent"]};">'
        f"{_esc(title)}</div>"
    )


def _wrap(title: str, inner: str, th: dict) -> str:
    """카드 묶음을 위아래 여백 + 제목바로 감싼다. 앞뒤 빈 줄로 광고 트리거 분리."""
    return f"\n<div style=\"margin:28px 0;\">{_title_bar(title, th)}{inner}</div>\n"


# ── 카드 타입별 렌더러 ────────────────────────────────────────────────


def _card_schedule(title: str, rows: list[list[str]], th: dict) -> str:
    pal, rad, sh = th["palette"], th["radius"], th["shadow"]
    cells = []
    for i, r in enumerate(rows):
        big = _esc(r[0]) if r else ""
        main = _esc(r[1]) if len(r) > 1 else ""
        sub = _esc(r[2]) if len(r) > 2 else ""
        c1, c2 = pal[i % len(pal)]
        sub_html = (
            f'<div style="font-size:11px;opacity:.85;margin-top:3px;">{sub}</div>'
            if sub
            else ""
        )
        cells.append(
            f'<div style="background:linear-gradient(135deg,{c1},{c2});color:#fff;'
            f"padding:18px 14px;border-radius:{rad};text-align:center;box-shadow:{sh};\">"
            f'<div style="font-size:18px;font-weight:800;line-height:1.15;">{big}</div>'
            f'<div style="font-size:13px;font-weight:600;margin-top:7px;">{main}</div>'
            f"{sub_html}</div>"
        )
    grid = (
        '<div style="display:grid;grid-template-columns:'
        'repeat(auto-fit,minmax(140px,1fr));gap:12px;">' + "".join(cells) + "</div>"
    )
    return _wrap(title, grid, th)


def _card_stat(title: str, rows: list[list[str]], th: dict) -> str:
    pal, rad, sh = th["palette"], th["radius"], th["shadow"]
    cells = []
    for i, r in enumerate(rows):
        num = _esc(r[0]) if r else ""
        label = _esc(r[1]) if len(r) > 1 else ""
        c1, c2 = pal[i % len(pal)]
        cells.append(
            f'<div style="background:linear-gradient(135deg,{c1},{c2});color:#fff;'
            f"padding:20px 16px;border-radius:{rad};text-align:center;box-shadow:{sh};\">"
            f'<div style="font-size:26px;font-weight:800;line-height:1;">{num}</div>'
            f'<div style="font-size:12px;opacity:.92;margin-top:8px;">{label}</div>'
            f"</div>"
        )
    grid = (
        '<div style="display:grid;grid-template-columns:'
        'repeat(auto-fit,minmax(120px,1fr));gap:12px;">' + "".join(cells) + "</div>"
    )
    return _wrap(title, grid, th)


def _card_compare(title: str, rows: list[list[str]], th: dict) -> str:
    rad, sh = th["radius"], th["shadow_soft"]
    accent, badge_c = th["accent"], th["badge"]
    cols = []
    for r in rows:
        name = _esc(r[0]) if r else ""
        items_raw = r[1] if len(r) > 1 else ""
        flag = r[2].lower() if len(r) > 2 else ""
        best = flag in ("best", "추천", "1", "y", "★")
        items = [x.strip() for x in re.split(r"[/;]", items_raw) if x.strip()]
        li = "".join(
            f'<li style="padding:7px 0;border-bottom:1px solid {GRAY_BORDER};'
            f'font-size:14px;color:{TEXT};">{_esc(x)}</li>'
            for x in items
        )
        head_bg = accent if best else "#475569"
        badge = (
            f'<span style="background:{badge_c};color:#fff;font-size:11px;font-weight:700;'
            'padding:2px 8px;border-radius:999px;margin-left:8px;">추천</span>'
            if best
            else ""
        )
        border = f"2px solid {accent}" if best else f"1px solid {GRAY_BORDER}"
        cols.append(
            f'<div style="border:{border};border-radius:{rad};overflow:hidden;'
            f'box-shadow:{sh};background:#fff;">'
            f'<div style="background:{head_bg};color:#fff;padding:13px 16px;'
            f'font-weight:700;font-size:15px;">{name}{badge}</div>'
            f'<ul style="list-style:none;margin:0;padding:6px 16px 14px;">{li}</ul>'
            f"</div>"
        )
    grid = (
        '<div style="display:grid;grid-template-columns:'
        'repeat(auto-fit,minmax(200px,1fr));gap:14px;align-items:start;">'
        + "".join(cols)
        + "</div>"
    )
    return _wrap(title, grid, th)


def _card_rank(title: str, rows: list[list[str]], th: dict) -> str:
    rad, sh, accent_dark = th["radius"], th["shadow_soft"], th["accent_dark"]
    items = []
    for i, r in enumerate(rows):
        name = _esc(r[0]) if r else ""
        val = _esc(r[1]) if len(r) > 1 else ""
        rank = i + 1
        badge_bg = _MEDAL[i] if i < 3 else "#cbd5e1"
        badge_fg = "#fff" if i < 3 else "#475569"
        val_html = (
            f'<span style="margin-left:auto;font-weight:700;color:{accent_dark};'
            f'font-size:14px;">{val}</span>'
            if val
            else ""
        )
        items.append(
            f'<div style="display:flex;align-items:center;gap:12px;padding:12px 16px;'
            f"background:#fff;border:1px solid {GRAY_BORDER};border-radius:{rad};"
            f'margin:8px 0;box-shadow:{sh};">'
            f'<span style="flex:0 0 28px;height:28px;line-height:28px;text-align:center;'
            f"background:{badge_bg};color:{badge_fg};border-radius:50%;font-weight:800;"
            f'font-size:14px;">{rank}</span>'
            f'<span style="font-weight:600;font-size:15px;color:{TEXT};">{name}</span>'
            f"{val_html}</div>"
        )
    return _wrap(title, "".join(items), th)


def _card_spec(title: str, rows: list[list[str]], th: dict) -> str:
    rad, sh, accent_dark = th["radius"], th["shadow_soft"], th["accent_dark"]
    lines = []
    for i, r in enumerate(rows):
        label = _esc(r[0]) if r else ""
        val = _esc(r[1]) if len(r) > 1 else ""
        bg = "#f9fafb" if i % 2 == 0 else "#fff"
        lines.append(
            f'<div style="display:flex;padding:11px 16px;background:{bg};'
            f'border-bottom:1px solid {GRAY_BORDER};">'
            f'<span style="flex:0 0 40%;font-weight:600;color:{accent_dark};'
            f'font-size:14px;">{label}</span>'
            f'<span style="flex:1;color:{TEXT};font-size:14px;">{val}</span></div>'
        )
    box = (
        f'<div style="border:1px solid {GRAY_BORDER};border-radius:{rad};'
        f'overflow:hidden;box-shadow:{sh};">' + "".join(lines) + "</div>"
    )
    return _wrap(title, box, th)


_RENDERERS = {
    "schedule": _card_schedule,
    "stat": _card_stat,
    "compare": _card_compare,
    "rank": _card_rank,
    "spec": _card_spec,
}


def inject_viz_cards(markdown: str, theme: str = DEFAULT_THEME) -> str:
    """본문의 :::type ... ::: 카드 토큰을 인포그래픽 HTML로 치환.

    theme: 'vivid'(생기) | 'refined'(차분 고급). 알 수 없으면 vivid.
    알 수 없는 타입은 원문 그대로 둔다(글 안 깨지게).
    """
    th = THEMES.get(theme, THEMES[DEFAULT_THEME])

    def sub(m: re.Match[str]) -> str:
        kind = m.group(1).lower()
        title = m.group(2)
        body = m.group(3)
        renderer = _RENDERERS.get(kind)
        if renderer is None:
            return m.group(0)  # 카드 타입 아님 (다른 :::블록일 수 있음) — 그대로
        rows = _rows(body)
        if not rows:
            print(f"  [warn] viz card '{kind}' 본문 비어있음 — 토큰 제거")
            return ""
        return renderer(title, rows, th)

    return _BLOCK_RE.sub(sub, markdown)


def theme_for_platform(platform: str) -> str:
    """platform 문자열 → 테마 이름. 모르면 기본(vivid)."""
    return PLATFORM_THEME.get(platform, DEFAULT_THEME)


def strip_viz_cards(markdown: str) -> str:
    """네이버 등 HTML 카드 불가 플랫폼용 — 카드를 plain 텍스트로 풀어쓴다.

    제목은 소제목 줄로, 각 행은 '· a — b — c' 불릿으로. 표 컴포넌트 의존 없음.
    """

    def sub(m: re.Match[str]) -> str:
        kind = m.group(1).lower()
        if kind not in _RENDERERS:
            return m.group(0)
        title = m.group(2).strip()
        rows = _rows(m.group(3))
        lines = []
        if title:
            lines.append(f"▶ {title}")
        for i, r in enumerate(rows):
            # compare 의 3번째 필드(best/추천 플래그)는 텍스트 폴백에서 제외
            cells = r[:2] if kind == "compare" else r
            fields = [c for c in cells if c]
            if kind == "rank":
                lines.append(f"{i + 1}. " + " — ".join(fields))
            else:
                lines.append("· " + " — ".join(fields))
        return "\n" + "\n".join(lines) + "\n"

    return _BLOCK_RE.sub(sub, markdown)
