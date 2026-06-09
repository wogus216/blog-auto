"""단발 URL/요소 캡처 → blog-assets repo push → raw URL + 본문 토큰.

티스토리·블로그 글에 넣을 '브랜드 공식 제품컷' 같은 이미지를 즉석에서 확보한다.
capture_brokers.py(여러 페이지 일괄)의 단발 버전. 캡처 후 broker_assets.json 에
등록하므로, 본문에 `{{broker:<key>}}` 토큰만 넣으면 발행 시 이미지+출처로 자동 치환.

사용:
  # 페이지 전체(뷰포트) 캡처
  uv run python scripts/capture_page.py \
    --url "https://www.nike.com/kr/t/pegasus-41-..." --key shoe_pegasus41 \
    --broker "Nike" --topic "페가수스 41 공식 제품 페이지" --viewport-only

  # 특정 요소(제품 이미지)만 깔끔하게
  uv run python scripts/capture_page.py \
    --url "<url>" --key shoe_x --broker "Adidas" --topic "아디제로 보스턴 12" \
    --selector "img[data-testid='product-image']"

전제: assets/ 가 wogus216/blog-assets git repo 로 클론돼 있어야 함.
저작권: 제품 리뷰 목적 인용 + 출처표시 자동(_img_block). 상업 이미지는 맥락상 인용 범위 내로만.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
CAPTURES_DIR = ASSETS_DIR / "captures"
ASSETS_JSON = ASSETS_DIR / "broker_assets.json"
RAW_BASE = "https://raw.githubusercontent.com/wogus216/blog-assets/main/captures"

_DESKTOP_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
)


def _git(args: list[str]) -> str:
    r = subprocess.run(["git", *args], cwd=ASSETS_DIR, capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 실패:\n{r.stderr}")
    return r.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--key", required=True, help="자산 키 ([a-z0-9_]+). 본문 토큰 {{broker:key}} 에 사용")
    ap.add_argument("--broker", required=True, help="출처 표기명 (예: 'Nike', 'Adidas 공식')")
    ap.add_argument("--topic", required=True, help="캡션/설명 (예: '페가수스 41 제품 페이지')")
    ap.add_argument("--selector", default="", help="이 CSS 요소만 캡처 (없으면 페이지)")
    ap.add_argument("--viewport-only", action="store_true", help="full_page 대신 보이는 영역만")
    ap.add_argument("--wait", type=int, default=2800, help="goto 후 대기(ms)")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--pre-visit", default="", help="봇차단 회피: 먼저 방문할 메인 URL")
    ap.add_argument("--no-push", action="store_true", help="로컬 캡처만, git push 생략")
    a = ap.parse_args()

    if not re.fullmatch(r"[a-z0-9_]+", a.key):
        print(f"[ERR] --key 는 영소문자/숫자/_ 만: {a.key}", file=sys.stderr)
        return 1
    if not (ASSETS_DIR / ".git").exists():
        print(f"[ERR] {ASSETS_DIR} 가 git repo 아님. 'git clone .../blog-assets.git assets' 먼저.", file=sys.stderr)
        return 1
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
    out = CAPTURES_DIR / f"{a.key}.png"

    print(f">>> 캡처: {a.url}  (key={a.key}, selector={a.selector or '페이지'})")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": a.width, "height": a.height},
            user_agent=_DESKTOP_UA,
            locale="ko-KR",
        )
        page = ctx.new_page()
        try:
            if a.pre_visit:
                print(f"    pre-visit: {a.pre_visit}")
                page.goto(a.pre_visit, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)
            page.goto(a.url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(a.wait)
            if a.selector:
                el = page.locator(a.selector).first
                el.scroll_into_view_if_needed(timeout=8000)
                page.wait_for_timeout(600)
                el.screenshot(path=str(out))
            else:
                page.screenshot(path=str(out), full_page=not a.viewport_only)
            print(f"    saved: {out.relative_to(ROOT)}")
        except Exception as e:
            print(f"[ERR] 캡처 실패: {e}", file=sys.stderr)
            browser.close()
            return 1
        finally:
            browser.close()

    assets = json.loads(ASSETS_JSON.read_text(encoding="utf-8")) if ASSETS_JSON.exists() else {}
    assets[a.key] = {
        "raw_url": f"{RAW_BASE}/{a.key}.png",
        "source_url": a.url,
        "broker": a.broker,
        "topic": a.topic,
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }
    ASSETS_JSON.write_text(json.dumps(assets, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    raw = f"{RAW_BASE}/{a.key}.png"

    if not a.no_push:
        _git(["add", "captures", "broker_assets.json"])
        if _git(["status", "--porcelain"]):
            _git([
                "-c", "user.email=developer@saltmine.io", "-c", "user.name=wogus216",
                "commit", "-m", f"capture: {a.key} ({datetime.now(timezone.utc).date()})",
            ])
            _git(["push", "origin", "main"])
            print(">>> pushed → raw URL 활성화")
        else:
            print(">>> 변경 없음(이미 동일).")

    print(f"\nRAW_URL: {raw}")
    print(f"본문에 이 토큰 한 줄 넣으면 발행 시 이미지+출처 자동 삽입:\n  {{{{broker:{a.key}}}}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
