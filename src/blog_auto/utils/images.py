"""Openverse 이미지 검색 (무인증, CC 라이선스).

본문 상단에 삽입할 대표 이미지를 검색해 가져온다. Openverse는 Wikimedia,
Flickr 등의 CC/PDM 콘텐츠를 모아 제공하므로 출처 표기만 하면 블로그에
안전하게 사용할 수 있다.

API 문서: https://api.openverse.org/v1/
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass

OPENVERSE_API = "https://api.openverse.org/v1/images/"
USER_AGENT = "blog-auto/0.1 (+https://github.com/wogus216)"
TIMEOUT = 10


@dataclass
class ImageResult:
    url: str
    thumbnail: str
    title: str
    creator: str
    creator_url: str
    license: str
    license_version: str
    source_page: str

    @property
    def license_label(self) -> str:
        v = f" {self.license_version}" if self.license_version else ""
        return f"{self.license.upper()}{v}"

    def attribution_md(self) -> str:
        creator_part = (
            f"[{self.creator}]({self.creator_url})" if self.creator_url else self.creator
        )
        creator_part = creator_part or "Unknown"
        return (
            f"*사진: {creator_part} · "
            f"[{self.license_label}]({self.source_page})*"
        )


def _http_get_json(url: str) -> dict | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def search_image(
    query: str,
    *,
    license_type: str = "commercial",
    page_size: int = 5,
) -> ImageResult | None:
    """Openverse에서 첫 번째로 적합한 이미지를 반환. 실패하면 None.

    license_type:
      - "commercial": 상업적 사용 가능 (CC0/BY/BY-SA/PDM 등)
      - "modification": 수정 가능
      - "commercial,modification": 둘 다
    """
    if not query.strip():
        return None
    params = {
        "q": query.strip(),
        "license_type": license_type,
        "page_size": str(page_size),
        "mature": "false",
    }
    url = OPENVERSE_API + "?" + urllib.parse.urlencode(params)
    data = _http_get_json(url)
    if not data:
        return None
    for item in data.get("results", []):
        img_url = item.get("url")
        if not img_url:
            continue
        return ImageResult(
            url=img_url,
            thumbnail=item.get("thumbnail") or img_url,
            title=item.get("title", "") or "",
            creator=item.get("creator", "") or "",
            creator_url=item.get("creator_url", "") or "",
            license=item.get("license", "") or "",
            license_version=item.get("license_version", "") or "",
            source_page=item.get("foreign_landing_url", "") or item.get("url", ""),
        )
    return None


def build_header_markdown(image: ImageResult, alt: str) -> str:
    """본문 맨 위에 들어갈 '이미지 + 출처' 마크다운 블록."""
    safe_alt = alt.replace("[", "(").replace("]", ")")
    return f"![{safe_alt}]({image.url})\n\n{image.attribution_md()}\n\n"
