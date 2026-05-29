"""마크다운 → HTML 변환 후 시각 강화 (티스토리 기본 에디터용 inline style 주입).

티스토리 기본 에디터(TinyMCE)는 inline style을 그대로 보존하므로
별도 CSS 파일 없이 단일 HTML 안에 모든 스타일을 박는다.
"""

from __future__ import annotations

import re

# ─── 컬러 토큰 ───────────────────────────────────────────────────────
PRIMARY = "#2563eb"      # 메인 블루
PRIMARY_DARK = "#1e40af"
ACCENT = "#f59e0b"       # 꿀팁 옐로우
WARN = "#dc2626"         # 주의 레드
SUCCESS = "#10b981"      # 체크 그린
GRAY_BG = "#f9fafb"
GRAY_BORDER = "#e5e7eb"
TEXT = "#374151"


def _slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[^\w가-힣\s-]", "", text).strip().lower()
    return re.sub(r"[\s-]+", "-", text)[:80]


def _enhance_tables(html: str) -> str:
    """표를 줄무늬 + 컬러 헤더 스타일로."""
    html = re.sub(
        r"<table>",
        f'<table style="width:100%;border-collapse:collapse;margin:24px 0;'
        f'font-size:14px;border:1px solid {GRAY_BORDER};border-radius:8px;'
        f'overflow:hidden;">',
        html,
    )
    html = re.sub(
        r"<thead>",
        f'<thead style="background:{PRIMARY};color:white;">',
        html,
    )
    html = re.sub(
        r"<th>",
        f'<th style="padding:14px 12px;text-align:left;'
        f'border-bottom:2px solid {PRIMARY_DARK};font-weight:600;">',
        html,
    )
    html = re.sub(
        r"<td>",
        f'<td style="padding:12px;border-bottom:1px solid {GRAY_BORDER};">',
        html,
    )
    return html


def _enhance_blockquotes(html: str) -> str:
    """인용구를 첫 이모지(💡⚠️📌)에 따라 컬러 박스로."""

    # 💡 꿀팁
    html = re.sub(
        r"<blockquote>\s*<p>💡\s*(.+?)</p>\s*</blockquote>",
        lambda m: (
            f'<div style="background:#fef3c7;border-left:5px solid {ACCENT};'
            f'padding:16px 20px;margin:20px 0;border-radius:8px;'
            f'box-shadow:0 1px 2px rgba(0,0,0,0.05);">'
            f'<strong style="color:#92400e;">💡 꿀팁</strong>'
            f'<div style="margin-top:6px;color:{TEXT};">{m.group(1)}</div>'
            f"</div>"
        ),
        html,
        flags=re.DOTALL,
    )

    # ⚠️ 주의
    html = re.sub(
        r"<blockquote>\s*<p>⚠️\s*(.+?)</p>\s*</blockquote>",
        lambda m: (
            f'<div style="background:#fee2e2;border-left:5px solid {WARN};'
            f'padding:16px 20px;margin:20px 0;border-radius:8px;'
            f'box-shadow:0 1px 2px rgba(0,0,0,0.05);">'
            f'<strong style="color:#991b1b;">⚠️ 주의</strong>'
            f'<div style="margin-top:6px;color:{TEXT};">{m.group(1)}</div>'
            f"</div>"
        ),
        html,
        flags=re.DOTALL,
    )

    # 일반 인용구 — 컬러 박스
    html = re.sub(
        r"<blockquote>",
        f'<blockquote style="background:#eff6ff;border-left:5px solid {PRIMARY};'
        f'padding:16px 20px;margin:20px 0;border-radius:8px;color:{TEXT};">',
        html,
    )

    return html


def _enhance_headings(html: str) -> str:
    """H2 underline + 색상, H3 좌측 컬러 바."""

    def h2_repl(m: re.Match) -> str:
        text = m.group(1)
        slug = _slugify(text)
        return (
            f'<h2 id="{slug}" style="border-bottom:3px solid {PRIMARY};'
            f"padding-bottom:10px;margin-top:48px;margin-bottom:20px;"
            f'color:{PRIMARY_DARK};font-size:24px;">{text}</h2>'
        )

    html = re.sub(r"<h2>(.+?)</h2>", h2_repl, html)

    html = re.sub(
        r"<h3>(.+?)</h3>",
        lambda m: (
            f'<h3 style="border-left:4px solid {PRIMARY};padding-left:12px;'
            f"margin-top:28px;margin-bottom:14px;"
            f'color:{TEXT};font-size:19px;">{m.group(1)}</h3>'
        ),
        html,
    )
    return html


def _enhance_images(html: str) -> str:
    """`<img>`에 max-width:100% inline style 주입 — 티스토리 본문 폭(~750px) 오버플로 방지.
    이미 style 속성이 있으면 그 안에 prepend.
    """
    img_style = (
        "max-width:100%;height:auto;display:block;"
        "margin:24px auto;border-radius:8px;"
        "box-shadow:0 2px 8px rgba(0,0,0,0.08);"
    )

    def repl(m: re.Match[str]) -> str:
        tag = m.group(0)
        attrs = m.group(1)
        style_m = re.search(r'style="([^"]*)"', attrs)
        if style_m:
            existing = style_m.group(1).rstrip(";")
            new_style = f"{img_style}{existing};"
            attrs = attrs.replace(style_m.group(0), f'style="{new_style}"')
        else:
            attrs = attrs.rstrip() + f' style="{img_style}"'
        return f"<img{attrs}>"

    return re.sub(r"<img((?:\s+[^>]*?)?)\s*/?>", repl, html)


def _enhance_checklist(html: str) -> str:
    """- [ ] / - [x] 체크리스트를 카드 안에 묶음."""
    pattern = re.compile(
        r"(<ul>(?:\s*<li>\s*\[[x ]\].*?</li>)+\s*</ul>)",
        re.DOTALL,
    )

    def wrap(m: re.Match) -> str:
        block = m.group(1)
        # 체크박스 변환
        block = block.replace("[ ]", '<input type="checkbox" disabled style="margin-right:10px;transform:scale(1.2);">')
        block = block.replace("[x]", '<input type="checkbox" disabled checked style="margin-right:10px;transform:scale(1.2);">')
        # ul/li 스타일
        block = block.replace(
            "<ul>",
            f'<ul style="list-style:none;padding:0;margin:0;">',
        )
        block = re.sub(
            r"<li>",
            f'<li style="padding:10px 14px;background:white;'
            f"border:1px solid {GRAY_BORDER};border-radius:6px;"
            f'margin:6px 0;display:flex;align-items:center;">',
            block,
        )
        return (
            f'<div style="background:{GRAY_BG};border:1px solid {GRAY_BORDER};'
            f'padding:20px;border-radius:10px;margin:24px 0;">'
            f'<strong style="display:block;margin-bottom:12px;color:{PRIMARY_DARK};font-size:15px;">'
            f"✅ 체크리스트</strong>"
            f"{block}"
            f"</div>"
        )

    return pattern.sub(wrap, html)


def _build_toc(html: str) -> str:
    """H2가 3개 이상이면 글 상단 목차 박스."""
    h2s = re.findall(r'<h2 id="([^"]+)"[^>]*>(.+?)</h2>', html)
    if len(h2s) < 3:
        return ""
    items = "".join(
        f'<li style="margin:6px 0;">'
        f'<a href="#{slug}" style="color:{PRIMARY};text-decoration:none;'
        f'border-bottom:1px dotted {PRIMARY};">{text}</a></li>'
        for slug, text in h2s
    )
    return (
        f'<div style="background:{GRAY_BG};border:1px solid {GRAY_BORDER};'
        f'padding:20px 24px;border-radius:10px;margin:0 0 32px;">'
        f'<strong style="display:block;margin-bottom:10px;color:{PRIMARY_DARK};font-size:16px;">'
        f"📋 목차</strong>"
        f'<ul style="margin:0;padding-left:20px;">{items}</ul>'
        f"</div>"
    )


def _build_cta(text: str = "⚾️ NC다이노스 공식 예매 바로가기", url: str = "https://www.ncdinos.com/") -> str:
    return (
        f'<div style="margin:40px 0 20px;text-align:center;">'
        f'<a href="{url}" target="_blank" rel="noopener" '
        f'style="display:inline-block;background:linear-gradient(135deg,{PRIMARY},{PRIMARY_DARK});'
        f"color:white;padding:16px 36px;border-radius:10px;text-decoration:none;"
        f'font-weight:bold;font-size:16px;box-shadow:0 4px 12px rgba(37,99,235,0.3);">'
        f"{text}</a>"
        f"</div>"
    )


def enhance(html: str, *, cta_url: str | None = None, cta_text: str | None = None) -> str:
    """전체 enhance 파이프라인."""
    html = _enhance_tables(html)
    html = _enhance_blockquotes(html)
    html = _enhance_headings(html)
    html = _enhance_checklist(html)
    html = _enhance_images(html)

    toc = _build_toc(html)
    cta = _build_cta(cta_text or "🔗 자세한 정보 확인하기", cta_url) if cta_url else ""

    # 본문 wrapper (line-height + font)
    body = (
        f'<div style="line-height:1.75;font-size:16px;color:{TEXT};'
        f'font-family:-apple-system,BlinkMacSystemFont,\'Pretendard\',sans-serif;">'
        f"{toc}{html}{cta}"
        f"</div>"
    )
    return body
