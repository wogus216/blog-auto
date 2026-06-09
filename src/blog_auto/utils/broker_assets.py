"""Broker capture 이미지/링크를 마크다운 본문에 삽입하는 헬퍼.

capture_brokers.py 가 만든 assets/broker_assets.json 을 읽어
마크다운 안의 다음 토큰을 자동 치환한다:

  {{broker:toss_us_fee}}            → 이미지 + 캡션 + 출처 링크 블록
  {{broker_link:toss_us_fee}}       → "[토스증권 해외주식 수수료 안내](https://...)"

토큰이 매칭되는 키가 없으면 경고 출력 후 토큰 그대로 둔다 (글 깨지지 않게).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from blog_auto import config

ASSETS_JSON = config.ROOT / "assets" / "broker_assets.json"

_IMG_RE = re.compile(r"\{\{broker:([a-z0-9_]+)\}\}")
_LINK_RE = re.compile(r"\{\{broker_link:([a-z0-9_]+)\}\}")


def _load() -> dict:
    if not ASSETS_JSON.exists():
        return {}
    return json.loads(ASSETS_JSON.read_text(encoding="utf-8"))


def _img_block(asset: dict) -> str:
    caption = f"{asset['broker']} {asset['topic']}".strip()
    date = asset["captured_at"][:10]
    label = asset.get("source_label", "공식 페이지")  # 무료스톡 등은 "on Unsplash" 같은 값
    date_kind = asset.get("date_kind", "캡처")        # 스톡 사진은 "사진", AI는 "생성"
    src = asset.get("source_url", "")
    if src:
        credit = f"*출처: [{asset['broker']} {label}]({src}) ({date_kind} {date})*"
    else:
        # AI 생성 이미지 등 출처 링크가 없는 경우 — 링크 없이 명시만
        credit = f"*{asset['broker']} ({date_kind} {date})*"
    return f"\n![{caption}]({asset['raw_url']})\n{credit}\n"


def _link(asset: dict) -> str:
    return f"[{asset['broker']} {asset['topic']}]({asset['source_url']})"


def inject_broker_assets(markdown: str) -> str:
    assets = _load()
    if not assets:
        return markdown

    def img_sub(m: re.Match[str]) -> str:
        key = m.group(1)
        if key not in assets:
            print(f"  [warn] broker asset key not found: {key}")
            return m.group(0)
        return _img_block(assets[key])

    def link_sub(m: re.Match[str]) -> str:
        key = m.group(1)
        if key not in assets:
            print(f"  [warn] broker asset key not found: {key}")
            return m.group(0)
        return _link(assets[key])

    md = _IMG_RE.sub(img_sub, markdown)
    md = _LINK_RE.sub(link_sub, md)
    return md
