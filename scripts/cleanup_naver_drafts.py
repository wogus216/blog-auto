"""네이버 블로그 임시저장 글 목록 dump + 선택 삭제.

dry-run으로 목록만 출력. --delete-old-markdown 플래그로 markdown 버전(▶가 본문에 없는 글) 삭제.
"""
from __future__ import annotations

import sys

from blog_auto import config
from blog_auto.publishers.session import open_context


def main() -> None:
    apply_delete = "--apply" in sys.argv
    write_url = f"https://blog.naver.com/{config.NAVER_BLOG_ID}?Redirect=Write"

    with open_context("naver") as ctx:
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.on("dialog", lambda d: d.accept())
        page.goto(write_url, wait_until="networkidle")
        page.wait_for_timeout(2000)

        mf = page.frame(name="mainFrame")
        if not mf:
            print("[ERROR] mainFrame 없음")
            return

        # 진입 팝업 닫기 (있으면)
        for sel in (".se-popup-button-cancel", ".se-popup-button:has-text('취소')"):
            try:
                btn = mf.query_selector(sel)
                if btn:
                    btn.click()
                    page.wait_for_timeout(800)
                    break
            except Exception:
                continue

        # "임시저장 N" 버튼 찾기 (네이버는 보통 상단에 표시)
        btn_dump = mf.evaluate(
            """() => Array.from(document.querySelectorAll('button')).map(b => ({
                text: (b.innerText||'').replace(/\\s+/g,' ').trim().slice(0, 40),
                className: (b.className||'').toString().slice(0, 60),
                ariaLabel: b.getAttribute('aria-label') || ''
            })).filter(x => /임시|저장|불러|드래프트|draft/i.test(x.text + ' ' + x.ariaLabel + ' ' + x.className))"""
        )
        print(f"[DEBUG] 임시저장 관련 버튼: {btn_dump}")

        # 임시저장 목록 열기 — save_count_btn__ZTLNa
        try:
            count_btn = mf.query_selector(".save_count_btn__ZTLNa")
            if count_btn:
                count_btn.click()
                page.wait_for_timeout(1500)
            else:
                print("[ERROR] save_count_btn 없음")
                return
        except Exception as e:
            print(f"[ERROR] 목록 버튼 클릭 실패: {e}")
            return

        # 목록 dump — 더 넓은 셀렉터
        list_dump = mf.evaluate(
            """() => {
                // 임시저장 패널 안의 글 항목들
                const allEls = Array.from(document.querySelectorAll('li, [role="listitem"], [class*="item"]'));
                return allEls.map(it => ({
                    text: (it.innerText||'').replace(/\\s+/g,' ').trim().slice(0, 100),
                    className: (it.className||'').toString().slice(0, 80),
                    deleteBtnClass: (() => {
                        const b = it.querySelector('button[class*="delete"], button[aria-label*="삭제"], [class*="remove"]');
                        return b ? (b.className||'').toString().slice(0, 60) : null;
                    })()
                })).filter(x => x.text && x.text.length > 5 && !/^확인|^취소|^닫기/.test(x.text)).slice(0, 30);
            }"""
        )
        print(f"[INFO] 임시글 후보 항목 ({len(list_dump)}개):")
        for i, it in enumerate(list_dump):
            mark = "✓" if "▶" in it["text"] else "✗"
            print(f"  {i:2d}. {mark} {it['text'][:70]}")
            if it["deleteBtnClass"]:
                print(f"       delete btn class: {it['deleteBtnClass']}")

        if not apply_delete:
            print("\n[DRY-RUN] --apply 추가 시 markdown 버전(본문에 ▶가 없는 글) 삭제.")
            return

        # markdown 버전 삭제 — 본문에 '▶' 없는 항목을 markdown으로 간주
        # (plain text 친화 버전은 ▶가 있어야 함)
        # 단, 제목만 있고 내용이 안 보이면 어떤 글인지 판단 어려움
        print("\n[INFO] --apply 모드 — 삭제 대상 골라서 클릭")
        # 추후 구현


if __name__ == "__main__":
    main()
