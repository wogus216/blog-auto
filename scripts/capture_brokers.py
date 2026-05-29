"""증권사 안내 페이지를 Playwright로 캡처 → assets/ repo에 push → raw URL 매핑 저장.

사용:
  python scripts/capture_brokers.py            # 모든 페이지 캡처
  python scripts/capture_brokers.py toss_us_fee  # 특정 key만

전제:
  - 프로젝트 루트의 assets/ 폴더가 별도 git repo로 클론되어 있어야 함
    (wogus216/blog-assets)
  - data/broker_pages.json 에 캡처 대상 정의
  - 캡처는 공개 안내 페이지만 (로그인 X). 저작권/약관 주의.

결과:
  - assets/captures/{key}.png            (실제 이미지)
  - assets/broker_assets.json            (key → {raw_url, source_url, broker, topic, captured_at})
  - 자동 commit + push
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES_JSON = ROOT / "data" / "broker_pages.json"
ASSETS_DIR = ROOT / "assets"
CAPTURES_DIR = ASSETS_DIR / "captures"
ASSETS_JSON = ASSETS_DIR / "broker_assets.json"
RAW_BASE = "https://raw.githubusercontent.com/wogus216/blog-assets/main/captures"


def _git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ASSETS_DIR,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{result.stderr}")
    return result.stdout.strip()


def capture_page(page_def: dict, default_viewport: dict) -> Path | None:
    key = page_def["key"]
    url = page_def["url"]
    wait_ms = page_def.get("wait_ms", 2000)
    viewport = page_def.get("viewport", default_viewport)
    is_mobile = viewport.get("width", 1280) < 600
    user_agent = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.4 Mobile/15E148 Safari/604.1"
    ) if is_mobile else (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    )
    out_path = CAPTURES_DIR / f"{key}.png"

    pre_visit_url = page_def.get("pre_visit_url")  # 봇 차단 회피용: 메인 페이지 먼저 방문해 세션/쿠키 확보
    pre_visit_wait_ms = page_def.get("pre_visit_wait_ms", 2000)
    full_page = page_def.get("full_page", True)  # 긴 페이지는 False로 viewport만 캡처

    print(f"  [{key}] {url}  ({viewport['width']}x{viewport['height']}{', mobile' if is_mobile else ''})")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport=viewport,
            user_agent=user_agent,
            locale="ko-KR",
            is_mobile=is_mobile,
            has_touch=is_mobile,
        )
        page = ctx.new_page()
        try:
            if pre_visit_url:
                print(f"    pre-visit: {pre_visit_url}")
                page.goto(pre_visit_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(pre_visit_wait_ms)
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(wait_ms)
            page.screenshot(path=str(out_path), full_page=full_page)
            print(f"    saved: {out_path.relative_to(ROOT)}")
            return out_path
        except Exception as e:
            print(f"    [WARN] capture failed: {e}", file=sys.stderr)
            return None
        finally:
            browser.close()


def main() -> int:
    if not ASSETS_DIR.exists() or not (ASSETS_DIR / ".git").exists():
        print(
            f"[ERR] {ASSETS_DIR} 가 없거나 git repo 가 아닙니다.\n"
            f"      먼저 'git clone https://github.com/wogus216/blog-assets.git assets' 실행.",
            file=sys.stderr,
        )
        return 1

    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)

    pages = json.loads(PAGES_JSON.read_text(encoding="utf-8"))["pages"]
    only = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    if only:
        pages = [p for p in pages if p["key"] in only]
        if not pages:
            print(f"[ERR] 매칭되는 key 없음. 후보: {only}", file=sys.stderr)
            return 1

    print(f">>> capturing {len(pages)} page(s)")
    viewport = {"width": 1280, "height": 900}

    existing: dict = {}
    if ASSETS_JSON.exists():
        existing = json.loads(ASSETS_JSON.read_text(encoding="utf-8"))

    captured_any = False
    now_iso = datetime.now(timezone.utc).isoformat()
    for p in pages:
        out = capture_page(p, viewport)
        if not out:
            continue
        captured_any = True
        existing[p["key"]] = {
            "raw_url": f"{RAW_BASE}/{p['key']}.png",
            "source_url": p["url"],
            "broker": p["broker"],
            "topic": p["topic"],
            "captured_at": now_iso,
        }

    if not captured_any:
        print(">>> nothing captured, exit.")
        return 1

    ASSETS_JSON.write_text(
        json.dumps(existing, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f">>> wrote {ASSETS_JSON.relative_to(ROOT)}")

    # commit + push
    print(">>> git add/commit/push")
    _git(["add", "captures", "broker_assets.json"])
    status = _git(["status", "--porcelain"])
    if not status:
        print("    no changes to commit.")
        return 0

    keys_str = ", ".join(p["key"] for p in pages)
    _git([
        "-c", "user.email=developer@saltmine.io",
        "-c", "user.name=wogus216",
        "commit", "-m", f"capture: {keys_str} ({now_iso[:10]})",
    ])
    _git(["push", "origin", "main"])
    print(">>> done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
