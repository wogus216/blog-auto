"""Naver Blog publisher (Playwright + SmartEditor ONE 기반).

셀렉터 정리:
  mainFrame    iframe[name="mainFrame"]
  제목         .se-title-text  (클릭 후 type)
  본문         .se-main-section (클릭 후 execCommand insertHTML)
  임시저장     button.save_btn__bzc5B
  발행열기     button.publish_btn__m9KHH
  카테고리     button.selectbox_button__jb1Dt → [role=menuitem]
  태그         input#tag-input (Enter로 추가)
  최종발행     button.confirm_btn__WEaBq
"""

from __future__ import annotations

import markdown as md_lib

from blog_auto import config
from blog_auto.publishers.base import BasePublisher, PublishRequest, PublishResult
from blog_auto.publishers.session import has_profile, open_context

_MD_EXTENSIONS = ["tables", "fenced_code", "nl2br"]
_WRITE_URL = f"https://blog.naver.com/{config.NAVER_BLOG_ID}?Redirect=Write"


class NaverPublisher(BasePublisher):
    platform = "naver"

    def publish(self, req: PublishRequest) -> PublishResult:
        if not has_profile("naver"):
            return PublishResult(url=None, ok=False, note="세션 없음. `cli login naver` 먼저 실행.")

        html_body = md_lib.markdown(req.body_md, extensions=_MD_EXTENSIONS)

        with open_context("naver") as ctx:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            # 네이티브 alert/confirm 자동 수락 (발행 시 native dialog 가능성)
            page.on("dialog", lambda d: d.accept())
            page.goto(_WRITE_URL, wait_until="networkidle")
            self.tiny_pause()

            if "nidlogin" in page.url or "nid.naver.com" in page.url:
                return PublishResult(url=None, ok=False, note=f"로그인 페이지로 리다이렉트됨 ({page.url}) — 재로그인 필요")

            mf = page.frame(name="mainFrame")
            if not mf:
                return PublishResult(url=None, ok=False, note="mainFrame 없음 — 재로그인 필요")

            # 진입 시 뜨는 confirm 팝업 처리 ("작성 중인 글이 있습니다 — 이어 쓰기/새로 쓰기?")
            # se-popup-dim이 클릭을 가로막으므로 반드시 닫아야 함
            # 팝업 dump 후 다양한 텍스트 후보 클릭
            try:
                popup_dump = mf.evaluate(
                    """() => Array.from(document.querySelectorAll('.se-popup button, .se-popup-alert button')).map(b => ({
                        text: (b.innerText||'').trim().slice(0, 30),
                        className: (b.className||'').toString().slice(0, 60)
                    }))"""
                )
                if popup_dump:
                    print(f"[DEBUG] 네이버 팝업 버튼: {popup_dump}")
            except Exception:
                pass

            popup_closed = False
            for sel in (
                ".se-popup-button-cancel",
                ".se-popup-alert-confirm button:has-text('취소')",
                ".se-popup-alert-confirm button:has-text('새로 작성')",
                ".se-popup-alert-confirm button:has-text('새로 쓰기')",
                ".se-popup-alert-confirm button:has-text('아니오')",
                ".se-popup-alert-confirm button:has-text('닫기')",
                ".se-popup-button:has-text('새로 작성')",
                ".se-popup-button:has-text('취소')",
                ".se-popup button.se-popup-button",
            ):
                try:
                    btn = mf.query_selector(sel)
                    if btn:
                        btn.click()
                        popup_closed = True
                        print(f"[DEBUG] 팝업 dismiss: {sel}")
                        self.tiny_pause()
                        break
                except Exception:
                    continue

            # popup dim이 사라질 때까지 대기 (최대 5초)
            try:
                mf.wait_for_selector(".se-popup-dim", state="hidden", timeout=5000)
            except Exception:
                # 그래도 안 사라지면 ESC 시도
                page.keyboard.press("Escape")
                self.tiny_pause()
                try:
                    mf.wait_for_selector(".se-popup-dim", state="hidden", timeout=3000)
                except Exception:
                    print("[DEBUG] 팝업 dim이 계속 남아있음")

            # 도움말 패널 닫기 (있으면)
            try:
                close_btn = mf.query_selector("[class*='help'] [class*='close'], [aria-label*='닫기']")
                if close_btn:
                    close_btn.click()
                    self.tiny_pause()
            except Exception:
                pass

            # 제목 입력
            mf.click(".se-section-documentTitle")
            self.tiny_pause()
            page.keyboard.type(req.title)
            self.tiny_pause()

            # 본문 입력 — execCommand가 동작 안 하는 케이스 대비
            # 네이버 스마트에디터 ONE은 mainFrame 내부에 또 다른 iframe이 있는 경우가 있음
            mf.click(".se-section-text")
            self.tiny_pause()

            # 모든 frame 순회 — 디버그 전체 출력
            all_frames = page.frames
            print(f"[DEBUG] 전체 frame 수: {len(all_frames)}")
            target_frame = None
            for f in all_frames:
                try:
                    info = f.evaluate(
                        """() => {
                            // contenteditable=true 외에도 본문일 가능성 있는 element 모두 찾기
                            const editables = Array.from(document.querySelectorAll(
                                '[contenteditable="true"], [contenteditable=""], [role="textbox"], .se-text, .se-component-content'
                            ));
                            return {
                                url: location.href.slice(0, 80),
                                bodyHTML: document.body ? document.body.innerHTML.slice(0, 200) : 'no body',
                                editableCount: editables.length,
                                editables: editables.slice(0, 8).map(el => ({
                                    tag: el.tagName,
                                    own: (el.className||'').toString().slice(0, 60),
                                    parent: el.parentElement ? (el.parentElement.className||'').toString().slice(0, 60) : '',
                                    contenteditable: el.getAttribute('contenteditable'),
                                    role: el.getAttribute('role'),
                                    len: (el.innerText||'').length
                                }))
                            };
                        }"""
                    )
                    print(f"[DEBUG] frame name='{f.name}' info: {info}")
                    # input_buffer 같은 IME buffer는 제외
                    if "input_buffer" in (f.name or ""):
                        continue
                    if info and info.get("editableCount", 0) > 0:
                        target_frame = f
                except Exception as e:
                    print(f"[DEBUG] frame '{f.name}' evaluate 실패: {e}")

            if not target_frame:
                target_frame = mf
            print(f"[DEBUG] 본문 주입 target frame: name='{target_frame.name}'")

            # 본문 영역에 ClipboardEvent paste 시뮬레이션 — 네이버 내부 상태와 동기화
            # 본문 컴포넌트(.se-component.se-text) 안의 입력 가능 영역 찾고 paste event dispatch
            inject_result = target_frame.evaluate(
                """(html) => {
                    // 1) 본문 컴포넌트 찾기
                    const bodyComp = document.querySelector('.se-component.se-text');
                    if (!bodyComp) return {ok: false, reason: 'no body component'};

                    // 2) 본문 안의 editable 영역 (contenteditable 또는 .se-text-paragraph)
                    const editable = bodyComp.querySelector('[contenteditable="true"]') ||
                                     bodyComp.querySelector('.se-text-paragraph') ||
                                     bodyComp.querySelector('.se-component-content');
                    if (!editable) return {ok: false, reason: 'no editable in body comp', bodyHTML: bodyComp.innerHTML.slice(0, 200)};

                    // 3) focus + ClipboardEvent paste 시뮬레이션
                    editable.focus();
                    // 선택 영역 설정
                    const range = document.createRange();
                    range.selectNodeContents(editable);
                    const sel = window.getSelection();
                    sel.removeAllRanges();
                    sel.addRange(range);

                    const dt = new DataTransfer();
                    dt.setData('text/html', html);
                    dt.setData('text/plain', html.replace(/<[^>]+>/g, ''));
                    const pasteEvent = new ClipboardEvent('paste', {
                        clipboardData: dt,
                        bubbles: true,
                        cancelable: true
                    });
                    editable.dispatchEvent(pasteEvent);

                    return {
                        ok: true,
                        len: editable.innerText.length,
                        className: (editable.className||'').toString().slice(0, 60)
                    };
                }""",
                html_body,
            )
            print(f"[DEBUG] paste 시뮬레이션 결과: {inject_result}")
            self.tiny_pause()
            self.tiny_pause()

            # paste가 실패하면 (len이 placeholder 길이 그대로면) fallback — keyboard로 직접 type
            # 네이버 에디터가 untrusted event를 무시하는 경우 trusted 키보드 입력만 통함
            paste_len = inject_result.get("len", 0) if inject_result else 0
            if paste_len < 100:  # placeholder 길이(21) 등 무의미한 값이면 실패로 간주
                print(f"[DEBUG] paste 결과 len={paste_len} → keyboard.type fallback 발동")
                # 본문 영역 클릭 후 plain text 타이핑
                try:
                    mf.click(".se-component.se-text .se-component-content")
                    self.tiny_pause()
                except Exception:
                    try:
                        mf.click(".se-section-text")
                        self.tiny_pause()
                    except Exception:
                        pass

                # markdown 원문을 plain text로 type — 포맷팅(#·>·**)은 plain text로 들어가니
                # 사용자가 발행 전 네이버 에디터에서 시각적으로 보정 필요
                # delay=2ms로 빠르게 (네이버 IME 처리 시간 고려)
                page.keyboard.type(req.body_md, delay=2)
                self.tiny_pause()
                print("[DEBUG] keyboard.type 완료")

            # 임시저장 모드
            if req.mode == "draft":
                mf.click("button.save_btn__bzc5B")
                self.tiny_pause()
                return PublishResult(url=None, ok=True, note="임시저장 완료")

            # 발행 패널 열기
            mf.click("button.publish_btn__m9KHH")
            # 패널이 layer_popup__i0QOY .is_show__TMSLq 로 뜰 때까지 대기
            try:
                mf.wait_for_selector(".layer_popup__i0QOY.is_show__TMSLq, button.confirm_btn__WEaBq", timeout=8000)
            except Exception:
                pass
            self.tiny_pause()

            # 카테고리 설정
            if req.category:
                mf.click("button.selectbox_button__jb1Dt")
                self.tiny_pause()
                cat_item = mf.query_selector(f"[role='menuitem'][data-value*='{req.category}'], [role='menuitem']:has-text('{req.category}')")
                if cat_item:
                    cat_item.click()
                    self.tiny_pause()
                else:
                    page.keyboard.press("Escape")

            # 태그 입력
            for tag in req.tags:
                mf.fill("input#tag-input", tag)
                page.keyboard.press("Enter")
                self.tiny_pause()

            # semi 모드: 발행 패널까지 자동, "발행" 버튼은 사용자가 직접 클릭
            if req.mode == "semi":
                print("\n" + "=" * 60)
                print("[naver semi] 발행 패널이 열렸습니다.")
                print("브라우저 창에서 우하단 '발행' 버튼을 직접 클릭하세요.")
                print("발행 완료(또는 취소) 후 이 터미널에서 Enter를 누르세요.")
                print("=" * 60)
                try:
                    input("Enter로 종료: ")
                except EOFError:
                    pass
                final_url = page.url
                ok = "PostView" in final_url
                note = "발행 완료 (semi 모드)" if ok else "발행 미완료 — semi 모드 종료"
                return PublishResult(url=final_url if ok else None, ok=ok, note=note)

            # 자동 발행 (publish 모드) — event.isTrusted 검증으로 현재 미동작
            try:
                mf.wait_for_selector("button.confirm_btn__WEaBq:not([disabled])", timeout=5000)
            except Exception:
                pass
            try:
                mf.click("button.confirm_btn__WEaBq", timeout=5000)
            except Exception:
                pass

            post_url: str | None = None
            note = "발행 완료 (URL 확인 불가)"
            try:
                page.wait_for_url("**/PostView*", timeout=15000)
                post_url = page.url
                note = "발행 완료"
            except Exception:
                page.wait_for_timeout(3000)
                post_url = page.url

        return PublishResult(url=post_url, ok=True, note=note)
