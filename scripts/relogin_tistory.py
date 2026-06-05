"""티스토리(카카오 SSO) 재로그인 헬퍼.

`blog-auto login tistory`는 마지막에 터미널 Enter 입력을 기다리는데, 카카오가
prompt=select_account로 ID/PW 재인증을 요구할 때가 있어 자동 발행이 막힌다.
이 스크립트는 headful 브라우저를 띄우고 '글쓰기 화면 도달'을 자동 감지해
세션을 저장한다. Enter 입력 불필요.

사용법:
    uv run python scripts/relogin_tistory.py
브라우저가 열리면 카카오 로그인을 끝까지 진행하세요.
  ⚠️ '로그인 상태 유지' 체크박스를 반드시 체크할 것.
글쓰기 화면이 뜨면 자동으로 저장되고 종료됩니다(최대 5분 대기).
"""
from blog_auto import config
from blog_auto.publishers.session import open_context

write_url = f"https://{config.TISTORY_BLOG_NAME}.tistory.com/manage/newpost/"

print("\n=== 티스토리 재로그인 ===")
print(f"대상: {config.TISTORY_BLOG_NAME}.tistory.com")
print(">>> 브라우저에서 카카오 로그인을 끝까지 진행하세요.")
print(">>> ⚠️ '로그인 상태 유지' 체크박스 반드시 체크!")
print(">>> 글쓰기 화면이 뜨면 자동 저장됩니다 (최대 5분 대기).\n")

with open_context("tistory", headless=False, slow_mo=0) as ctx:
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto(write_url, wait_until="domcontentloaded")
    try:
        page.wait_for_url("**/manage/newpost/**", timeout=300000)
        # 에디터까지 떴는지 한 번 더 확인
        try:
            page.wait_for_function(
                "() => typeof tinymce !== 'undefined' && tinymce.get('editor-tistory') !== null",
                timeout=20000,
            )
        except Exception:
            pass
        print("\n[OK] 글쓰기 화면 도달 — 세션이 저장되었습니다. 이제 발행 가능합니다.")
    except Exception:
        print(f"\n[FAIL] 시간 초과 또는 미도달. 현재 URL: {page.url}")
        print("       다시 실행해서 카카오 로그인을 끝까지(2FA 포함) 진행해 주세요.")
