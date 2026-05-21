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

예약 발행 (schedule 모드):
  발행 패널에서 "현재"/"예약" 라디오 토글 → 예약 선택 → 날짜·시각 입력
  네이버 SmartEditor ONE은 라디오/탭 구조가 자주 바뀌므로 셀렉터 후보 여러 개 시도 +
  실패 시 패널 구조 dump로 추적 가능.
"""

from __future__ import annotations

import platform as _platform
from datetime import datetime

import markdown as md_lib

from blog_auto import config
from blog_auto.publishers.base import BasePublisher, PublishRequest, PublishResult
from blog_auto.publishers.session import has_profile, open_context

_MD_EXTENSIONS = ["tables", "fenced_code", "nl2br"]
_WRITE_URL = f"https://blog.naver.com/{config.NAVER_BLOG_ID}?Redirect=Write"
_PASTE_MODIFIER = "Meta" if _platform.system() == "Darwin" else "Control"


class NaverPublisher(BasePublisher):
    platform = "naver"

    def publish(self, req: PublishRequest) -> PublishResult:
        if not has_profile("naver"):
            return PublishResult(url=None, ok=False, note="세션 없음. `cli login naver` 먼저 실행.")
        if req.mode == "schedule" and not req.schedule_at:
            return PublishResult(url=None, ok=False, note="schedule 모드는 --at RFC3339 시간 필요.")

        html_body = md_lib.markdown(req.body_md, extensions=_MD_EXTENSIONS)

        with open_context("naver") as ctx:
            # navigator.clipboard.write() 를 prompt 없이 호출하기 위해 권한 사전 부여.
            # SmartEditor ONE 이 합성 ClipboardEvent(isTrusted=false)를 거부하므로
            # 클립보드에 HTML 을 올려 두고 trusted Cmd/Ctrl+V 로 붙이는 방식 사용.
            try:
                ctx.grant_permissions(
                    ["clipboard-read", "clipboard-write"],
                    origin="https://blog.naver.com",
                )
            except Exception as e:
                print(f"[DEBUG] clipboard 권한 부여 실패(무시 가능): {e}")

            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            # 네이티브 alert/confirm 자동 수락 (발행 시 native dialog 가능성)
            page.on("dialog", lambda d: d.accept())
            page.goto(_WRITE_URL, wait_until="networkidle")
            self.tiny_pause()

            if "nidlogin" in page.url or "nid.naver.com" in page.url:
                return PublishResult(url=None, ok=False, note=f"로그인 페이지로 리다이렉트됨 ({page.url}) — 재로그인 필요")

            mf = page.frame(name="mainFrame")
            if not mf:
                # 네이버가 iframe name을 제거한 경우 fallback: PostWrite URL 패턴 또는 두 번째 iframe
                page.wait_for_timeout(3000)
                for f in page.frames:
                    if f == page.main_frame:
                        continue
                    if "PostWrite" in f.url or "postWrite" in f.url.lower():
                        mf = f
                        break
                if not mf and len(page.frames) >= 2:
                    mf = page.frames[1]  # 첫 iframe = 글쓰기일 가능성
            if not mf:
                all_frames = [{"name": f.name, "url": f.url[:120]} for f in page.frames]
                print(f"[DEBUG] page.url={page.url}")
                print(f"[DEBUG] iframes={all_frames}")
                return PublishResult(url=None, ok=False, note=f"mainFrame 없음 — fallback도 실패 (url={page.url})")
            print(f"[DEBUG] iframe 진입: name='{mf.name}' url={mf.url[:120]}")

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

            # 본문 주입: navigator.clipboard.write() 로 HTML 을 클립보드에 올린 뒤
            # trusted Cmd/Ctrl+V 키 입력으로 붙여넣기. SmartEditor ONE 은 합성
            # ClipboardEvent(isTrusted=false)를 무시하므로 진짜 키 입력이 필요하다.
            focus_result = target_frame.evaluate(
                """() => {
                    const bodyComp = document.querySelector('.se-component.se-text');
                    if (!bodyComp) return {ok: false, reason: 'no body component'};
                    const editable = bodyComp.querySelector('[contenteditable="true"]') ||
                                     bodyComp.querySelector('.se-text-paragraph') ||
                                     bodyComp.querySelector('.se-component-content');
                    if (!editable) return {ok: false, reason: 'no editable in body comp'};
                    editable.focus();
                    const range = document.createRange();
                    range.selectNodeContents(editable);
                    const sel = window.getSelection();
                    sel.removeAllRanges();
                    sel.addRange(range);
                    return {ok: true, len: editable.innerText.length};
                }"""
            )
            print(f"[DEBUG] 본문 focus 결과: {focus_result}")
            if not focus_result or not focus_result.get("ok"):
                return PublishResult(
                    url=None,
                    ok=False,
                    note=f"본문 editable 영역 못 찾음: {focus_result}",
                )

            clip_result = page.evaluate(
                """async (html) => {
                    try {
                        const plain = html.replace(/<[^>]+>/g, '');
                        const item = new ClipboardItem({
                            'text/html': new Blob([html], {type: 'text/html'}),
                            'text/plain': new Blob([plain], {type: 'text/plain'})
                        });
                        await navigator.clipboard.write([item]);
                        return {ok: true};
                    } catch (e) {
                        return {ok: false, error: String(e)};
                    }
                }""",
                html_body,
            )
            print(f"[DEBUG] clipboard.write 결과: {clip_result}")
            if not clip_result or not clip_result.get("ok"):
                return PublishResult(
                    url=None,
                    ok=False,
                    note=(
                        f"navigator.clipboard.write 실패 → 발행 중단. "
                        f"권한/secure context 확인 필요: {clip_result}"
                    ),
                )

            # trusted paste (Cmd/Ctrl+V)
            page.keyboard.press(f"{_PASTE_MODIFIER}+V")
            self.tiny_pause()
            self.tiny_pause()

            # paste 후 본문 길이 검증
            paste_check = target_frame.evaluate(
                """() => {
                    const bodyComp = document.querySelector('.se-component.se-text');
                    if (!bodyComp) return {len: 0};
                    const editable = bodyComp.querySelector('[contenteditable="true"]') ||
                                     bodyComp.querySelector('.se-text-paragraph') ||
                                     bodyComp.querySelector('.se-component-content');
                    return {len: editable ? (editable.innerText||'').length : 0};
                }"""
            )
            paste_len = paste_check.get("len", 0) if paste_check else 0
            print(f"[DEBUG] paste 후 본문 길이: {paste_len}")
            if paste_len < 100:
                return PublishResult(
                    url=None,
                    ok=False,
                    note=(
                        f"clipboard paste 후 본문 길이 {paste_len} — 주입 실패. "
                        f"raw markdown fallback 으로 빠지지 않기 위해 발행 중단."
                    ),
                )

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

            # schedule 모드: 예약 옵션 토글 + 날짜·시각 입력
            if req.mode == "schedule":
                schedule_ok = self._apply_schedule(mf, page, req.schedule_at)
                if not schedule_ok:
                    return PublishResult(
                        url=None,
                        ok=False,
                        note=(
                            "예약 UI 자동화 실패. 위 디버그 출력으로 셀렉터 후보 확인 필요.\n"
                            "현재 발행 패널이 열려있으니 브라우저에서 직접 예약 처리 가능."
                        ),
                    )

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

    def _apply_schedule(self, mf, page, schedule_at: str) -> bool:
        """발행 패널에서 '예약' 옵션 선택 + 날짜·시각 입력.

        네이버 SmartEditor ONE은 라디오/탭 구조가 자주 바뀌므로
        여러 셀렉터 후보를 순차 시도하고, 실패 시 패널 dump로 디버깅 가능.
        """
        dt = datetime.fromisoformat(schedule_at)
        year, month, day = dt.year, dt.month, dt.day
        hour, minute = dt.hour, dt.minute
        print(f"[DEBUG] schedule target: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}")

        # 1) 발행 패널 내 모든 라디오/버튼 dump (디버그 + 셀렉터 발굴)
        try:
            panel_dump = mf.evaluate(
                """() => {
                    const panel = document.querySelector('.layer_popup__i0QOY, [class*="publish_panel"], [class*="layer_publish"]');
                    const scope = panel || document.body;
                    return {
                        radios: Array.from(scope.querySelectorAll('input[type="radio"]')).map(r => ({
                            id: r.id, name: r.name, value: r.value,
                            checked: r.checked,
                            labelText: (r.closest('label')?.innerText || '').trim().slice(0, 30),
                            className: (r.className||'').toString().slice(0, 60)
                        })),
                        buttons: Array.from(scope.querySelectorAll('button')).filter(b => /예약|현재|발행|등록/.test(b.innerText||'')).map(b => ({
                            id: b.id, text: (b.innerText||'').trim().slice(0, 20), className: (b.className||'').toString().slice(0, 80)
                        })),
                        dateInputs: Array.from(scope.querySelectorAll('input')).filter(i => /date|time|hour|minute|year|month|day/i.test(i.id+i.name+i.type+i.className)).map(i => ({
                            id: i.id, name: i.name, type: i.type, value: i.value,
                            className: (i.className||'').toString().slice(0, 60)
                        }))
                    };
                }"""
            )
            print(f"[DEBUG] 발행 패널 dump:")
            print(f"  radios: {panel_dump.get('radios', [])}")
            print(f"  buttons: {panel_dump.get('buttons', [])}")
            print(f"  dateInputs: {panel_dump.get('dateInputs', [])}")
        except Exception as e:
            print(f"[DEBUG] panel dump 실패: {e}")
            panel_dump = {}

        # 2) "예약" 라디오/버튼 클릭 시도 (셀렉터 후보 순회)
        reservation_clicked = False
        for sel in (
            "input[type='radio'][value='reserve']",
            "input[type='radio'][value='schedule']",
            "input[type='radio'][value='reservation']",
            "label:has(input[type='radio']):has-text('예약')",
            "label:has-text('예약')",
            "button:has-text('예약')",
            "[role='tab']:has-text('예약')",
            ".publish_radio__i_kw7 input[value='reserve']",
        ):
            try:
                el = mf.query_selector(sel)
                if el:
                    el.click()
                    reservation_clicked = True
                    print(f"[DEBUG] 예약 옵션 클릭 성공: {sel}")
                    self.tiny_pause()
                    break
            except Exception:
                continue

        if not reservation_clicked:
            print("[DEBUG] '예약' 옵션 클릭 실패 — 위 panel dump의 radios 항목 확인 필요")
            return False

        # 3) 날짜·시각 input에 값 채우기 (여러 패턴 시도)
        self.tiny_pause()
        date_set = False

        # 패턴 A: 단일 date input (YYYY-MM-DD)
        for sel in ("input[type='date']", "input[name*='date']", "input#publishDate"):
            try:
                el = mf.query_selector(sel)
                if el:
                    iso_date = f"{year:04d}-{month:02d}-{day:02d}"
                    el.fill(iso_date)
                    date_set = True
                    print(f"[DEBUG] date input fill: {sel}={iso_date}")
                    break
            except Exception:
                continue

        # 패턴 B: 분리된 year/month/day input
        if not date_set:
            year_ok = self._try_fill(mf, ("input[name='year']", "input#year", "input.year_input"), str(year))
            month_ok = self._try_fill(mf, ("input[name='month']", "input#month", "input.month_input"), f"{month:02d}")
            day_ok = self._try_fill(mf, ("input[name='day']", "input#day", "input.day_input"), f"{day:02d}")
            if year_ok or month_ok or day_ok:
                date_set = True
                print(f"[DEBUG] year/month/day fill: y={year_ok} m={month_ok} d={day_ok}")

        # 시각 입력 (시·분)
        hour_ok = self._try_fill(mf, ("input[name='hour']", "input#hour", "input.hour_input", "input[type='time']"), f"{hour:02d}")
        minute_ok = self._try_fill(mf, ("input[name='minute']", "input#minute", "input.minute_input"), f"{minute:02d}")
        print(f"[DEBUG] time fill: hour={hour_ok} minute={minute_ok}")

        # select 박스 패턴 (시간/분이 dropdown일 경우)
        if not hour_ok:
            try:
                mf.select_option("select[name='hour'], select#hour", value=f"{hour:02d}")
                hour_ok = True
                print(f"[DEBUG] hour select fallback: {hour:02d}")
            except Exception:
                pass
        if not minute_ok:
            try:
                mf.select_option("select[name='minute'], select#minute", value=f"{minute:02d}")
                minute_ok = True
                print(f"[DEBUG] minute select fallback: {minute:02d}")
            except Exception:
                pass

        if not (hour_ok or minute_ok):
            print("[DEBUG] 시각 입력 실패 — 위 panel dump의 dateInputs 항목 확인 필요")
            return False

        return True

    def _try_fill(self, mf, selectors, value: str) -> bool:
        for sel in selectors:
            try:
                el = mf.query_selector(sel)
                if el:
                    el.fill(value)
                    return True
            except Exception:
                continue
        return False
