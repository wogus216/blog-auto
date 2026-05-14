"""Bing Images 검색 (HTTP + 정규식 파싱).

원래 Google Images 스크래핑을 노렸지만 헤드리스 Chromium은 봇 차단(/sorry/index)
때문에 사실상 막힘. 차선으로 Bing Images를 사용한다.

Bing은 검색 결과 HTML의 각 이미지 타일 `<a class="iusc" m='{...}'>` 에 JSON
메타데이터(murl=원본 이미지, purl=출처 페이지, t=타이틀)를 그대로 박아두므로
JS 렌더링/Playwright 없이 단일 HTTP 요청으로 깨끗하게 추출 가능.

함수/클래스 명은 호환성 위해 google_* 유지.
"""

from __future__ import annotations

import html as html_lib
import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from urllib.parse import urlparse

BING_ENDPOINT = "https://www.bing.com/images/search"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
TIMEOUT = 15


@dataclass
class GoogleImageResult:
    image_url: str
    source_page: str
    source_domain: str
    title: str = ""

    def attribution_md(self) -> str:
        return f"> 출처: [{self.source_domain}]({self.source_page})"


_TILE_RE = re.compile(r'<a[^>]+class="iusc"[^>]+m="([^"]+)"', re.IGNORECASE)


def _http_get(url: str) -> str | None:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def search_google_images(
    query: str,
    n: int = 3,
    *,
    safe: str = "strict",
    **_unused,
) -> list[GoogleImageResult]:
    """Bing Images 검색 상위 결과를 N장 반환. 실패 시 빈 리스트.

    safe: "strict" | "moderate" | "off"
    """
    if not query.strip():
        return []

    params = {
        "q": query.strip(),
        "form": "HDRSC2",
        "first": "1",
        "tsc": "ImageBasicHover",
        "safesearch": safe,
        "setlang": "ko",
    }
    url = BING_ENDPOINT + "?" + urllib.parse.urlencode(params)
    html_src = _http_get(url)
    if not html_src:
        return []

    results: list[GoogleImageResult] = []
    seen_pages: set[str] = set()

    for raw in _TILE_RE.findall(html_src):
        decoded = html_lib.unescape(raw)
        try:
            data = json.loads(decoded)
        except json.JSONDecodeError:
            continue

        image_url = (data.get("murl") or "").strip()
        page_url = (data.get("purl") or "").strip()
        title = (data.get("t") or "").strip()

        if not image_url or not page_url:
            continue
        if not page_url.startswith("http"):
            continue
        if page_url in seen_pages:
            continue

        domain = re.sub(r"^www\.", "", urlparse(page_url).netloc)
        if not domain:
            continue
        seen_pages.add(page_url)
        results.append(
            GoogleImageResult(
                image_url=image_url,
                source_page=page_url,
                source_domain=domain,
                title=title,
            )
        )
        if len(results) >= n:
            break

    return results


def insert_images_into_markdown(
    body_md: str,
    images: list[GoogleImageResult],
    alt_prefix: str = "",
) -> str:
    """본문 H2 섹션 사이에 이미지를 균등 분산 삽입.

    이미지 직후 라인에 `> 출처: [domain](url)` 인라인 어트리뷰션.
    """
    if not images:
        return body_md

    lines = body_md.splitlines()
    h2_indices = [i for i, ln in enumerate(lines) if ln.startswith("## ")]
    if not h2_indices:
        block = "\n".join(_image_block(img, alt_prefix, i) for i, img in enumerate(images))
        return block + "\n\n" + body_md

    n = len(images)
    if len(h2_indices) >= n:
        step = max(1, len(h2_indices) // (n + 1))
        target_idx = [h2_indices[min((k + 1) * step, len(h2_indices) - 1)] for k in range(n)]
    else:
        target_idx = h2_indices[:n]

    target_idx = sorted(set(target_idx), reverse=True)
    for k, idx in enumerate(target_idx):
        img = images[len(target_idx) - 1 - k]
        block = _image_block(img, alt_prefix, len(target_idx) - 1 - k)
        lines.insert(idx, block + "\n")

    return "\n".join(lines)


def _image_block(img: GoogleImageResult, alt_prefix: str, index: int) -> str:
    alt = (alt_prefix or "이미지").strip() + f" {index + 1}"
    return f"![{alt}]({img.image_url})\n\n{img.attribution_md()}\n"
