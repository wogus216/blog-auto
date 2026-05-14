"""티스토리 임시저장 글 정리 — 특정 제목 prefix 매칭만 삭제.

Usage:
    uv run python scripts/cleanup_tistory_drafts.py "⚾ 2026 두산베어스"
"""
from __future__ import annotations

import sys

from blog_auto import config
from blog_auto.publishers.session import open_context


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: cleanup_tistory_drafts.py <title-prefix> [--apply]")
        sys.exit(1)
    title_prefix = sys.argv[1]
    apply_delete = "--apply" in sys.argv
    status = "draft"
    for i, a in enumerate(sys.argv):
        if a == "--status" and i + 1 < len(sys.argv):
            status = sys.argv[i + 1]
    blog = config.TISTORY_BLOG_NAME or "www"
    drafts_url = f"https://{blog}.tistory.com/manage/posts/?status={status}"

    with open_context("tistory") as ctx:
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(drafts_url, wait_until="domcontentloaded")
        page.wait_for_timeout(1500)

        # 카카오 SSO 자동 처리 (tistory.py 와 동일 로직)
        if "/auth/login" in page.url:
            kakao_btn = page.query_selector(
                "a.link_kakao_id, a.btn_login.link_kakao_id, "
                "a[href*='kauth.kakao.com'], a[href*='kakao'][class*='login'], "
                "button:has-text('카카오'), a:has-text('카카오')"
            )
            if kakao_btn:
                kakao_btn.click()
                page.wait_for_timeout(3000)
                if "accounts.kakao.com" in page.url:
                    page.wait_for_load_state("networkidle", timeout=10000)
                    simple = page.query_selector("a.wrap_profile")
                    if simple:
                        simple.click()
                        page.wait_for_timeout(3000)
            # 다시 drafts 페이지로
            page.goto(drafts_url, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
        print(f"[INFO] drafts 페이지 URL: {page.url}")

        # ajax 로딩 대기
        page.wait_for_timeout(3000)

        # 페이지 전체 텍스트에 두산베어스 있는지 확인
        body_has = page.evaluate("(prefix) => document.body.innerText.includes(prefix)", title_prefix)
        print(f"[INFO] body innerText에 '{title_prefix}' 포함: {body_has}")

        # 좀 더 넓은 셀렉터 dump
        wide = page.evaluate(
            """(prefix) => {
                const all = Array.from(document.querySelectorAll('*')).filter(el => {
                    const t = (el.innerText || '').trim();
                    return t.startsWith(prefix) || t.includes(prefix);
                }).slice(0, 5);
                return all.map(el => ({
                    tag: el.tagName,
                    className: (el.className||'').toString().slice(0, 80),
                    id: el.id,
                    snippet: (el.innerText||'').slice(0, 120),
                    parentTag: el.parentElement ? el.parentElement.tagName : '',
                    parentClass: el.parentElement ? (el.parentElement.className||'').toString().slice(0, 80) : ''
                }));
            }""",
            title_prefix,
        )
        print(f"[DEBUG] '{title_prefix}' 포함 element 후보(상위 5개): {wide}")

        # 페이지 내 모든 draft 항목 dump (link + nearby delete button)
        items = page.evaluate(
            """(prefix) => {
                const rows = Array.from(document.querySelectorAll('tr, li.list_post, .list-post, [data-id]'));
                return rows.map(r => {
                    const text = (r.innerText || '').trim();
                    const link = r.querySelector('a[href*="/manage/post/"], a[href*="/manage/newpost/"]');
                    return {
                        snippet: text.slice(0, 100),
                        href: link ? link.href : '',
                        match: text.startsWith(prefix) || text.includes(prefix)
                    };
                }).filter(x => x.match);
            }""",
            title_prefix,
        )
        print(f"[INFO] '{title_prefix}' 매칭 draft 후보 {len(items)}개:")
        for it in items:
            print(f"  - {it['snippet'][:60]}  → {it['href']}")

        if not items:
            print("[INFO] 정리 대상 없음. URL 또는 셀렉터를 직접 확인하세요.")
            print(f"        진입 URL: {drafts_url}")
            print(f"        현재 URL: {page.url}")
            # 디버그용 dump
            dump = page.evaluate(
                """() => Array.from(document.querySelectorAll('a[href*=\"/manage/post\"], a[href*=\"/manage/newpost\"]')).slice(0, 20).map(a => ({
                    href: a.href, text: (a.innerText || '').slice(0, 80)
                }))"""
            )
            print(f"        링크 dump(첫 20개): {dump}")
            return

        if not apply_delete:
            print(f"\n[DRY-RUN] {len(items)}개 매칭. 실제 삭제하려면 --apply 추가.")
            return

        # 각 글 편집 페이지로 가서 삭제 (티스토리 신 에디터: 글 옆 메뉴/삭제 버튼)
        # 더 안전한 방법: 목록 페이지에서 체크박스 + 일괄 삭제 — 셀렉터 확실치 않으므로 일단 하나씩.
        for it in items:
            try:
                page.goto(it["href"], wait_until="domcontentloaded")
                page.wait_for_timeout(1200)
                # 삭제 버튼 후보
                deleted = False
                for sel in (
                    "button:has-text('삭제')",
                    "a:has-text('삭제')",
                    "#delete-btn",
                    "button[id*='delete']",
                ):
                    try:
                        loc = page.locator(sel)
                        if loc.count() > 0 and loc.first.is_visible():
                            loc.first.click()
                            page.wait_for_timeout(500)
                            # 확인 다이얼로그
                            for confirm_sel in (
                                "button:has-text('확인')",
                                "button:has-text('네')",
                                "button.btn-confirm",
                                "button.confirm",
                            ):
                                try:
                                    cloc = page.locator(confirm_sel)
                                    if cloc.count() > 0 and cloc.first.is_visible():
                                        cloc.first.click()
                                        break
                                except Exception:
                                    pass
                            page.wait_for_timeout(1000)
                            deleted = True
                            print(f"  ✓ 삭제: {it['snippet'][:50]}")
                            break
                    except Exception:
                        continue
                if not deleted:
                    print(f"  ✗ 삭제 버튼 못 찾음: {it['href']}")
            except Exception as e:
                print(f"  ✗ 에러 {it['href']}: {e}")


if __name__ == "__main__":
    main()
