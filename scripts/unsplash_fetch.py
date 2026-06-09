"""Unsplash 무료 스톡 이미지를 글에 넣기 — capture_page.py 의 스톡 버전.

검색 → 선택 이미지를 broker_assets.json 에 등록 → 본문에 `{{broker:<key>}}` 토큰 한 줄.
Unsplash 이미지는 images.unsplash.com hotlink 라 blog-assets 업로드 불필요(Unsplash 권장 방식).
출처표시("Photo by 작가 on Unsplash")는 발행 시 inject_broker_assets 가 자동 렌더.

사용:
  uv run python scripts/unsplash_fetch.py --query "marathon running" --key run_header \
    --topic "마라톤" [--orientation landscape] [--index 0]

  # 같은 쿼리에서 다른 컷이 필요하면 --index 1, 2 ...
  uv run python scripts/unsplash_fetch.py --query "running track" --key run_track --index 2

전제: .env 에 UNSPLASH_ACCESS_KEY. (https://unsplash.com/oauth/applications)
저작권: Unsplash 라이선스(상업적 무료). 작가+Unsplash 출처표시는 자동 삽입됨.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from blog_auto import config  # noqa: E402

ASSETS_DIR = ROOT / "assets"
ASSETS_JSON = ASSETS_DIR / "broker_assets.json"
API = "https://api.unsplash.com"
UTM = "utm_source=blog_auto&utm_medium=referral"  # Unsplash API 가이드라인: referral 표기


def _git(args: list[str]) -> str:
    r = subprocess.run(["git", *args], cwd=ASSETS_DIR, capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 실패:\n{r.stderr}")
    return r.stdout.strip()


def _get(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Client-ID {config.UNSPLASH_ACCESS_KEY}",
            "Accept-Version": "v1",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True, help="검색어 (영어가 결과 풍부)")
    ap.add_argument("--key", required=True, help="자산 키 ([a-z0-9_]+). 본문 토큰 {{broker:key}}")
    ap.add_argument("--topic", default="", help="캡션 보조 설명 (예: '마라톤 풀코스')")
    ap.add_argument("--orientation", default="landscape",
                    choices=["landscape", "portrait", "squarish"])
    ap.add_argument("--index", type=int, default=0, help="검색결과 중 몇 번째(0-base)")
    ap.add_argument("--per-page", type=int, default=10)
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()

    if not config.UNSPLASH_ACCESS_KEY:
        print("[ERR] .env 에 UNSPLASH_ACCESS_KEY 가 없습니다.", file=sys.stderr)
        return 1
    if not re.fullmatch(r"[a-z0-9_]+", a.key):
        print(f"[ERR] --key 는 영소문자/숫자/_ 만: {a.key}", file=sys.stderr)
        return 1

    q = urllib.parse.quote(a.query)
    try:
        data = _get(f"{API}/search/photos?query={q}&per_page={a.per_page}&orientation={a.orientation}")
    except Exception as e:
        print(f"[ERR] Unsplash 검색 실패: {e}", file=sys.stderr)
        return 1

    results = data.get("results", [])
    if not results:
        print(f"[ERR] 검색 결과 없음: '{a.query}'", file=sys.stderr)
        return 1
    idx = a.index if a.index < len(results) else 0
    if idx != a.index:
        print(f"[WARN] index {a.index} 범위초과 → {idx} 사용")
    photo = results[idx]

    # Unsplash 가이드라인: 사용 시 download_location 을 1회 호출(다운로드 집계)
    try:
        dl = photo.get("links", {}).get("download_location")
        if dl:
            _get(dl)
    except Exception:
        pass

    artist = photo["user"]["name"]
    raw = photo["urls"]["regular"]
    src = f"{photo['links']['html']}?{UTM}"

    assets = json.loads(ASSETS_JSON.read_text(encoding="utf-8")) if ASSETS_JSON.exists() else {}
    assets[a.key] = {
        "raw_url": raw,
        "source_url": src,
        "broker": f"Photo by {artist}",
        "topic": a.topic,
        "source_label": "on Unsplash",
        "date_kind": "사진",
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }
    ASSETS_JSON.write_text(json.dumps(assets, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✅ 등록: {a.key}  (Photo by {artist}, 검색 {data.get('total', 0)}장 중 #{idx})")
    print(f"   {raw[:78]}...")

    if not a.no_push and (ASSETS_DIR / ".git").exists():
        _git(["add", "broker_assets.json"])
        if _git(["status", "--porcelain"]):
            _git([
                "-c", "user.email=developer@saltmine.io", "-c", "user.name=wogus216",
                "commit", "-m", f"unsplash: {a.key} ({datetime.now(timezone.utc).date()})",
            ])
            _git(["push", "origin", "main"])
            print(">>> broker_assets.json pushed")

    print(f"\n본문에 이 토큰 한 줄이면 발행 시 이미지+출처 자동 삽입:\n  {{{{broker:{a.key}}}}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
