"""Replicate Flux 로 AI 이미지 생성 → blog-assets push → `{{broker:<key>}}` 토큰.

블로그 헤더·분위기·개념 일러스트를 텍스트 프롬프트로 생성. 저작권 0(생성물).
역할 분담: 실제 제품컷=capture_page.py / 실사 분위기=unsplash_fetch.py / 일러스트·개념=이것.

사용:
  uv run python scripts/replicate_generate.py \
    --prompt "minimalist flat illustration of a runner at sunrise, soft gradient" \
    --key run_hero --topic "러닝 일러스트" [--aspect-ratio 16:9]

전제: .env 에 REPLICATE_API_TOKEN. 비용: flux-schnell 장당 약 $0.003.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from blog_auto import config  # noqa: E402

ASSETS_DIR = ROOT / "assets"
CAPTURES_DIR = ASSETS_DIR / "captures"
ASSETS_JSON = ASSETS_DIR / "broker_assets.json"
RAW_BASE = "https://raw.githubusercontent.com/wogus216/blog-assets/main/captures"
DEFAULT_MODEL = "black-forest-labs/flux-schnell"


def _git(args: list[str]) -> str:
    r = subprocess.run(["git", *args], cwd=ASSETS_DIR, capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 실패:\n{r.stderr}")
    return r.stdout.strip()


def _req(url: str, *, method: str = "GET", body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    headers = {
        "Authorization": f"Bearer {config.REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
        "Prefer": "wait",
    }
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True, help="이미지 생성 프롬프트(영어 권장)")
    ap.add_argument("--key", required=True, help="자산 키 ([a-z0-9_]+). 본문 토큰 {{broker:key}}")
    ap.add_argument("--topic", default="", help="캡션 보조 설명")
    ap.add_argument("--aspect-ratio", default="16:9",
                    help="1:1 | 16:9 | 4:3 | 3:2 | 9:16 등 (flux-schnell)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()

    if not config.REPLICATE_API_TOKEN:
        print("[ERR] .env 에 REPLICATE_API_TOKEN 이 없습니다.", file=sys.stderr)
        return 1
    if not re.fullmatch(r"[a-z0-9_]+", a.key):
        print(f"[ERR] --key 는 영소문자/숫자/_ 만: {a.key}", file=sys.stderr)
        return 1
    if not (ASSETS_DIR / ".git").exists():
        print(f"[ERR] {ASSETS_DIR} 가 git repo 아님.", file=sys.stderr)
        return 1
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)

    api = f"https://api.replicate.com/v1/models/{a.model}/predictions"
    print(f">>> 생성: \"{a.prompt[:60]}...\"  (model={a.model}, {a.aspect_ratio})")
    try:
        resp = _req(api, method="POST", body={
            "input": {
                "prompt": a.prompt,
                "aspect_ratio": a.aspect_ratio,
                "output_format": "png",
                "num_outputs": 1,
            }
        })
    except Exception as e:
        print(f"[ERR] Replicate 요청 실패: {e}", file=sys.stderr)
        return 1

    # Prefer: wait 로 보통 즉시 succeeded. 아니면 polling.
    output = resp.get("output")
    status = resp.get("status")
    if status != "succeeded" or not output:
        get_url = (resp.get("urls") or {}).get("get")
        for _ in range(30):
            if not get_url:
                break
            time.sleep(2)
            resp = _req(get_url)
            status = resp.get("status")
            if status == "succeeded":
                output = resp.get("output")
                break
            if status in ("failed", "canceled"):
                print(f"[ERR] 생성 실패: status={status}, {resp.get('error')}", file=sys.stderr)
                return 1
    if not output:
        print(f"[ERR] output 없음 (status={status})", file=sys.stderr)
        return 1

    img_url = output[0] if isinstance(output, list) else output
    out_png = CAPTURES_DIR / f"{a.key}.png"
    try:
        urllib.request.urlretrieve(img_url, out_png)
        print(f"    saved: {out_png.relative_to(ROOT)}")
    except Exception as e:
        print(f"[ERR] 이미지 다운로드 실패: {e}", file=sys.stderr)
        return 1

    assets = json.loads(ASSETS_JSON.read_text(encoding="utf-8")) if ASSETS_JSON.exists() else {}
    assets[a.key] = {
        "raw_url": f"{RAW_BASE}/{a.key}.png",
        "source_url": "",  # AI 생성 — 출처 링크 없음 (broker_assets._img_block 가 '생성' 표기)
        "broker": "AI 생성 이미지(Flux)",
        "topic": a.topic,
        "date_kind": "생성",
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }
    ASSETS_JSON.write_text(json.dumps(assets, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✅ 등록: {a.key}")

    if not a.no_push:
        _git(["add", "captures", "broker_assets.json"])
        if _git(["status", "--porcelain"]):
            _git([
                "-c", "user.email=developer@saltmine.io", "-c", "user.name=wogus216",
                "commit", "-m", f"ai-image: {a.key} ({datetime.now(timezone.utc).date()})",
            ])
            _git(["push", "origin", "main"])
            print(">>> pushed → raw URL 활성화")

    print(f"\n본문에 이 토큰 한 줄이면 발행 시 이미지 자동 삽입:\n  {{{{broker:{a.key}}}}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
