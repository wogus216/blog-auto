"""Persistent browser profile per platform.

`launch_persistent_context`로 user_data_dir 통째를 보존해서
쿠키만 저장하던 storage_state 방식보다 세션 유지 기간이 길다
(보통 네이버/티스토리 모두 30일+).

첫 1회만 사람이 로그인하고, 2FA/캡차까지 통과한 뒤 엔터를 누르면
프로필 디렉토리(쿠키 + IndexedDB + localStorage 전체)가 그대로 남는다.
이후 publish는 같은 프로필을 그대로 띄워서 자동 로그인 시도 자체가 없다.

**세션 쿠키 영구화**: 티스토리 `__T_`/카카오 SSO 쿠키는 만료시간이 없는
'세션 쿠키'라 user_data_dir 방식이어도 컨텍스트 종료 시 Chromium이 버린다.
그래서 매번 카카오 재로그인이 떴다. 이를 막기 위해 컨텍스트를 닫기 전
현재 쿠키를 읽어 세션 쿠키에 30일 만료를 강제 부여하고 별도 JSON에 저장한 뒤,
다음 실행에서 `add_cookies`로 주입한다(로그인 상태일 때만 저장 → 빈 세션 보존).
"""

from __future__ import annotations

import json
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Literal

from playwright.sync_api import BrowserContext, sync_playwright

from blog_auto import config

Platform = Literal["tistory", "naver"]

# 30일 만료를 부여할 지평선(초)
_COOKIE_TTL = 60 * 60 * 24 * 30

# 이 쿠키가 하나라도 있어야 '로그인된 상태'로 보고 저장한다(빈/로그아웃 세션이
# 기존 저장본을 덮어쓰는 것을 방지). 티스토리=티스토리/카카오 인증, 네이버=NID.
_AUTH_COOKIE_HINTS: dict[str, tuple[str, ...]] = {
    "tistory": ("TSSESSION", "__T_", "__T_SECURE", "_kawlt", "_karmt", "_kahai"),
    "naver": ("NID_AUT", "NID_SES"),
}

# add_cookies가 허용하는 sameSite 값
_VALID_SAMESITE = {"Strict", "Lax", "None"}


def _cookies_file(platform: Platform) -> Path:
    return config.SESSIONS_DIR / f"{platform}-cookies.json"


def _persist_cookies(ctx: BrowserContext, platform: Platform) -> None:
    """컨텍스트 종료 전 호출. 세션 쿠키에 만료를 부여해 JSON으로 저장.

    로그인 인증 쿠키가 없으면(=로그아웃/실패 상태) 저장을 건너뛰어
    기존 정상 저장본을 보존한다.
    """
    try:
        cookies = ctx.cookies()
    except Exception:
        return
    if not cookies:
        return
    hints = _AUTH_COOKIE_HINTS.get(platform, ())
    names = {c.get("name") for c in cookies}
    if hints and not any(h in names for h in hints):
        return  # 로그인 안 된 상태 → 덮어쓰지 않음
    horizon = time.time() + _COOKIE_TTL
    for c in cookies:
        exp = c.get("expires")
        if exp is None or exp < 0:  # 세션 쿠키 → 만료 강제 부여
            c["expires"] = horizon
        ss = c.get("sameSite")
        if ss not in _VALID_SAMESITE:
            c["sameSite"] = "Lax"
    f = _cookies_file(platform)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(cookies, ensure_ascii=False), encoding="utf-8")


def _restore_cookies(ctx: BrowserContext, platform: Platform) -> None:
    """컨텍스트를 열자마자 호출. 저장해둔 쿠키(세션 쿠키 포함)를 주입."""
    f = _cookies_file(platform)
    if not f.exists():
        return
    try:
        cookies = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return
    cleaned = []
    for c in cookies:
        if not c.get("name") or "value" not in c:
            continue
        if c.get("sameSite") not in _VALID_SAMESITE:
            c["sameSite"] = "Lax"
        cleaned.append(c)
    if cleaned:
        try:
            ctx.add_cookies(cleaned)
        except Exception:
            pass  # 형식 불일치 등은 무시(프로필 쿠키로 fallback)


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
        _restore_cookies(ctx, platform)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(_login_url(platform))

        print(f"\n[{platform}] 브라우저에서 직접 로그인하세요.")
        print("2FA/캡차까지 모두 통과한 뒤, 이 터미널에서 Enter를 누르면 저장됩니다.")
        input("로그인 완료 후 Enter: ")

        _persist_cookies(ctx, platform)  # 세션 쿠키까지 만료 부여해 영구 저장
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
        _restore_cookies(ctx, platform)  # 저장된 세션 쿠키 주입 → 카카오 재로그인 회피
        try:
            yield ctx
        finally:
            _persist_cookies(ctx, platform)  # 발행 중 갱신된 세션 쿠키를 다시 영구화
            ctx.close()
