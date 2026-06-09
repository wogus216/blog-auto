"""임의 이미지 URL → 다운로드 → blog-assets push → 출처표기 + `{{broker:<key>}}` 토큰.

구글 이미지 등에서 찾은 사진을 '출처를 남기며' 본문에 넣기 위한 도구.
구글 우클릭 워크플로: 이미지 우클릭 → '이미지 주소 복사' → --url 에, 그 페이지 → --source 에.

⚠️ 출처표시가 저작권을 면책하지 않습니다. 사용 판단·책임은 운영자에게 있습니다.
    가능하면 공식 출처(capture_page.py)·무료 라이선스(unsplash_fetch.py)를 우선하세요.

사용:
  uv run python scripts/fetch_image.py \
    --url "https://.../photo.jpg" --source "https://원본-페이지-주소" \
    --credit "출처 사이트/작성자명" --key img_run01 --topic "러닝 장면"
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
CAPTURES_DIR = ASSETS_DIR / "captures"
ASSETS_JSON = ASSETS_DIR / "broker_assets.json"
RAW_BASE = "https://raw.githubusercontent.com/wogus216/blog-assets/main/captures"

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
)


def _git(args: list[str]) -> str:
    r = subprocess.run(["git", *args], cwd=ASSETS_DIR, capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 실패:\n{r.stderr}")
    return r.stdout.strip()


def _ext_from_url(url: str) -> str:
    m = re.search(r"\.(png|jpe?g|webp|gif)(?:[?#]|$)", url, re.I)
    return ("jpg" if m and m.group(1).lower() == "jpeg" else (m.group(1).lower() if m else "jpg"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="이미지 직접 URL (우클릭 '이미지 주소 복사')")
    ap.add_argument("--source", required=True, help="이미지가 있던 원본 페이지 URL (출처 링크)")
    ap.add_argument("--credit", required=True, help="출처 표기명 (사이트/작성자, 예 '러닝월드')")
    ap.add_argument("--key", required=True, help="자산 키 ([a-z0-9_]+). 본문 토큰 {{broker:key}}")
    ap.add_argument("--topic", default="", help="캡션 보조 설명")
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()

    if not re.fullmatch(r"[a-z0-9_]+", a.key):
        print(f"[ERR] --key 는 영소문자/숫자/_ 만: {a.key}", file=sys.stderr)
        return 1
    if not (ASSETS_DIR / ".git").exists():
        print(f"[ERR] {ASSETS_DIR} 가 git repo 아님.", file=sys.stderr)
        return 1
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)

    ext = _ext_from_url(a.url)
    out = CAPTURES_DIR / f"{a.key}.{ext}"
    print(f">>> 다운로드: {a.url[:70]}...")
    try:
        req = urllib.request.Request(a.url, headers={"User-Agent": _UA, "Referer": a.source})
        with urllib.request.urlopen(req, timeout=30) as r, open(out, "wb") as f:
            f.write(r.read())
        if out.stat().st_size < 1024:
            print(f"[WARN] 파일이 너무 작음({out.stat().st_size}B) — 차단/오류 이미지일 수 있음")
        print(f"    saved: {out.relative_to(ROOT)} ({out.stat().st_size // 1024}KB)")
    except Exception as e:
        print(f"[ERR] 다운로드 실패: {e}", file=sys.stderr)
        return 1

    assets = json.loads(ASSETS_JSON.read_text(encoding="utf-8")) if ASSETS_JSON.exists() else {}
    assets[a.key] = {
        "raw_url": f"{RAW_BASE}/{a.key}.{ext}",
        "source_url": a.source,
        "broker": a.credit,
        "topic": a.topic,
        "source_label": "원본",
        "date_kind": "이미지",
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }
    ASSETS_JSON.write_text(json.dumps(assets, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✅ 등록: {a.key}  (출처: {a.credit})")

    if not a.no_push:
        _git(["add", "captures", "broker_assets.json"])
        if _git(["status", "--porcelain"]):
            _git([
                "-c", "user.email=developer@saltmine.io", "-c", "user.name=wogus216",
                "commit", "-m", f"image: {a.key} ({datetime.now(timezone.utc).date()})",
            ])
            _git(["push", "origin", "main"])
            print(">>> pushed → raw URL 활성화")

    print(f"\n본문에 이 토큰 한 줄이면 발행 시 이미지+출처 자동 삽입:\n  {{{{broker:{a.key}}}}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
