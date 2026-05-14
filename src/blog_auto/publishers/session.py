"""Persistent browser profile per platform.

`launch_persistent_context`로 user_data_dir 통째를 보존해서
쿠키만 저장하던 storage_state 방식보다 세션 유지 기간이 길다
(보통 네이버/티스토리 모두 30일+).

첫 1회만 사람이 로그인하고, 2FA/캡차까지 통과한 뒤 엔터를 누르면
프로필 디렉토리(쿠키 + IndexedDB + localStorage 전체)가 그대로 남는다.
이후 publish는 같은 프로필을 그대로 띄워서 자동 로그인 시도 자체가 없다.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Literal

from playwright.sync_api import BrowserContext, sync_playwright

from blog_auto import config

Platform = Literal["tistory", "naver"]


def _login_url(platform: Platform) -> str:
    if platform == "tistory":
        name = config.TISTORY_BLOG_NAME or "www"
        return f"https://{name}.tistory.com/manage/"
    return "https://nid.naver.com/nidlogin.login"


def profile_dir(platform: Platform) -> Path:
    return config.SESSIONS_DIR / f"{platform}-profile"


def has_profile(platform: Platform) -> bool:
    p = profile_dir(platform)
    return p.exists() and any(p.iterdir())


def save_session(platform: Platform) -> Path:
    target = profile_dir(platform)
    target.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(target),
            headless=False,
            slow_mo=50,
            viewport={"width": 1280, "height": 900},
            locale="ko-KR",
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(_login_url(platform))

        print(f"\n[{platform}] 브라우저에서 직접 로그인하세요.")
        print("2FA/캡차까지 모두 통과한 뒤, 이 터미널에서 Enter를 누르면 저장됩니다.")
        input("로그인 완료 후 Enter: ")

        ctx.close()

    print(f"저장됨: {target}")
    return target


@contextmanager
def open_context(platform: Platform, *, headless: bool = False, slow_mo: int = 60) -> Iterator[BrowserContext]:
    """Publish 시 사용. 기존 프로필을 띄운 BrowserContext를 yield한다."""
    target = profile_dir(platform)
    if not has_profile(platform):
        raise RuntimeError(f"세션 프로필 없음: {target}. `cli login {platform}` 먼저 실행.")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(target),
            headless=headless,
            slow_mo=slow_mo,
            viewport={"width": 1280, "height": 900},
            locale="ko-KR",
        )
        try:
            yield ctx
        finally:
            ctx.close()
