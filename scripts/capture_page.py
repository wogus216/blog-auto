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

  # 셀렉터 모를 때 — 페이지에서 가장 큰 제품컷 자동 추출 (레티나 2배·팝업 자동닫기 기본)
  uv run python scripts/capture_page.py \
    --url "<url>" --key shoe_y --broker "Nike" --topic "페가수스 41" --auto-product

기본 동작: device_scale_factor=2(선명), 쿠키/팝업 자동 닫기. 끄려면 --scale 1 / --no-dismiss.

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

# 쿠키/동의/뉴스레터 팝업 — 흔한 닫기·동의 버튼들. 있으면 클릭, 없으면 무시.
_DISMISS_SELECTORS = [
    "#onetrust-accept-btn-handler",
    "button#truste-consent-button",
    "[aria-label='Accept all']", "[aria-label='모두 수락']", "[aria-label='동의']",
    "button:has-text('모두 동의')", "button:has-text('전체 동의')",
    "button:has-text('동의합니다')", "button:has-text('확인')",
    "button:has-text('Accept all')", "button:has-text('Accept All')",
    "button:has-text('I Agree')", "button:has-text('Got it')",
    "[aria-label='Close']", "[aria-label='닫기']", "[aria-label='close']",
    "button.close", ".modal-close", ".popup-close",
]


def _git(args: list[str]) -> str:
    r = subprocess.run(["git", *args], cwd=ASSETS_DIR, capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 실패:\n{r.stderr}")
    return r.stdout.strip()


def _dismiss_popups(page) -> None:
    """쿠키 배너·팝업을 닫아 캡처를 깨끗하게. 실패는 조용히 무시."""
    for sel in _DISMISS_SELECTORS:
        try:
            loc = page.locator(sel).first
            if loc.count() and loc.is_visible(timeout=400):
                loc.click(timeout=800)
                page.wait_for_timeout(250)
        except Exception:
            pass


def _find_product_image(page):
    """페이지에서 가장 큰 의미있는 이미지(로고/아이콘 제외)에 표식을 달고 locator 반환."""
    # lazy-load 이미지 트리거: 페이지를 한 번 훑어 내렸다 올림
    try:
        page.evaluate(
            """async () => {
                const sleep = ms => new Promise(r => setTimeout(r, ms));
                const H = document.body.scrollHeight;
                for (let y = 0; y < H; y += window.innerHeight) {
                    window.scrollTo(0, y); await sleep(150);
                }
                window.scrollTo(0, 0); await sleep(300);
            }"""
        )
    except Exception:
        pass
    found = page.evaluate(
        """() => {
            const imgs = [...document.querySelectorAll('img')];
            let best = null, area = 0;
            for (const im of imgs) {
                const r = im.getBoundingClientRect();
                // 화면상 렌더 크기 (lazy 이미지도 레이아웃 차지하면 잡힘)
                if (r.width < 180 || r.height < 180) continue;   // 로고/아이콘/썸네일 제외
                // 원본 화질 우선, 없으면 렌더 면적
                const nat = (im.naturalWidth || 0) * (im.naturalHeight || 0);
                const a = nat || (r.width * r.height);
                if (a > area) { area = a; best = im; }
            }
            if (!best) return false;
            best.setAttribute('data-vizcap', '1');
            best.scrollIntoView({block: 'center'});
            return true;
        }"""
    )
    if not found:
        return None
    page.wait_for_timeout(600)
    return page.locator("[data-vizcap='1']").first


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--key", required=True, help="자산 키 ([a-z0-9_]+). 본문 토큰 {{broker:key}} 에 사용")
    ap.add_argument("--broker", required=True, help="출처 표기명 (예: 'Nike', 'Adidas 공식')")
    ap.add_argument("--topic", required=True, help="캡션/설명 (예: '페가수스 41 제품 페이지')")
    ap.add_argument("--selector", default="", help="이 CSS 요소만 캡처 (없으면 페이지)")
    ap.add_argument("--auto-product", action="store_true", help="페이지에서 가장 큰 제품 이미지를 자동 탐지해 그것만 캡처")
    ap.add_argument("--viewport-only", action="store_true", help="full_page 대신 보이는 영역만")
    ap.add_argument("--no-dismiss", action="store_true", help="쿠키/팝업 자동 닫기 비활성화")
    ap.add_argument("--scale", type=int, default=2, help="device scale factor (2=레티나 2배 선명도, 기본)")
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
            device_scale_factor=max(1, a.scale),  # 레티나 2배 → 선명도 ↑
        )
        page = ctx.new_page()
        try:
            if a.pre_visit:
                print(f"    pre-visit: {a.pre_visit}")
                page.goto(a.pre_visit, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)
            page.goto(a.url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(a.wait)
            if not a.no_dismiss:
                _dismiss_popups(page)
            if a.selector:
                el = page.locator(a.selector).first
                el.scroll_into_view_if_needed(timeout=8000)
                page.wait_for_timeout(600)
                el.screenshot(path=str(out))
            elif a.auto_product:
                el = _find_product_image(page)
                if el is not None:
                    el.screenshot(path=str(out))
                    print("    (auto-product: 최대 제품 이미지 캡처)")
                else:
                    print("    [WARN] 제품 이미지 자동 탐지 실패 → 뷰포트 캡처로 폴백")
                    page.screenshot(path=str(out), full_page=False)
            else:
                page.screenshot(path=str(out), full_page=not a.viewport_only)
            print(f"    saved: {out.relative_to(ROOT)}  (scale x{max(1, a.scale)})")
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
