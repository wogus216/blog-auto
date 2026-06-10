"""Tistory publisher (Playwright + TinyMCE JS API 기반).

셀렉터 정리:
  제목     #post-title-inp
  본문     tinymce.get('editor-tistory').setContent(html)  [JS API]
  카테고리  #category-btn → #category-list [aria-label="카테고리명"]
  태그     #tagText (Enter로 추가)
  임시저장  button.action (text: 임시저장)
  완료     #publish-layer-btn → 공개 발행: #publish-btn
"""

from __future__ import annotations

import markdown as md_lib

from blog_auto import config
from blog_auto.publishers.base import BasePublisher, PublishRequest, PublishResult
from blog_auto.publishers.session import has_profile, open_context
from blog_auto.utils.html_enhance import enhance as enhance_html

_MD_EXTENSIONS = ["tables", "fenced_code", "nl2br"]


class TistoryPublisher(BasePublisher):
    platform = "tistory"

    def publish(self, req: PublishRequest) -> PublishResult:
        if not has_profile("tistory"):
            return PublishResult(url=None, ok=False, note="세션 없음. `cli login tistory` 먼저 실행.")

        html_body = md_lib.markdown(req.body_md, extensions=_MD_EXTENSIONS)
        # 시각 강화: 표/인용/체크리스트 컬러 박스 + TOC + CTA
        html_body = enhance_html(
            html_body,
            cta_url=getattr(req, "cta_url", None),
            cta_text=getattr(req, "cta_text", None),
        )
        write_url = f"https://{config.TISTORY_BLOG_NAME}.tistory.com/manage/newpost/"

        with open_context("tistory") as ctx:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto(write_url, wait_until="domcontentloaded")

            # 티스토리 자체 세션 쿠키(__T_)는 세션 쿠키라 휘발 → 카카오 SSO로 재인증 트리거
            if "/auth/login" in page.url:
                kakao_btn = page.query_selector(
                    "a.link_kakao_id, a.btn_login.link_kakao_id, "
                    "a[href*='kauth.kakao.com'], a[href*='kakao'][class*='login'], "
                    "button:has-text('카카오'), a:has-text('카카오')"
                )
                if not kakao_btn:
                    return PublishResult(url=None, ok=False, note=f"카카오 로그인 버튼 없음 ({page.url}) — 재로그인 필요")
                kakao_btn.click()
                try:
                    page.wait_for_url("**/manage/newpost/**", timeout=8000)
                except Exception:
                    pass

                # 카카오 간편 로그인 화면 (계정 카드 클릭으로 자동 통과 시도)
                if "accounts.kakao.com" in page.url:
                    try:
                        page.wait_for_load_state("networkidle", timeout=10000)
                    except Exception:
                        pass
                    # 첫 번째 a.wrap_profile = 본인 계정. 있으면 클릭해 자동 통과.
                    simple = page.query_selector("a.wrap_profile")
                    if simple:
                        simple.click()
                        try:
                            page.wait_for_url("**/manage/newpost/**", timeout=15000)
                        except Exception:
                            pass

                # 자동 통과 실패(prompt=select_account로 ID/PW 재인증 요구 등) →
                # 열린 브라우저에서 사람이 직접 로그인할 때까지 대기. 카카오는 자동화
                # 세션을 신뢰하지 않아 매번 재인증을 요구할 수 있으므로 이 경로가 필요.
                if ("accounts.kakao.com" in page.url) or ("kauth.kakao.com" in page.url):
                    print(
                        "\n[티스토리] 카카오 로그인 화면입니다. **열린 브라우저 창에서 직접 로그인**하세요.\n"
                        "           ('로그인 상태 유지' 체크 권장) 글쓰기 화면이 뜨면 발행이 자동으로 이어집니다.\n"
                        "           최대 5분 대기합니다...\n"
                    )
                    try:
                        page.wait_for_url("**/manage/newpost/**", timeout=300000)
                    except Exception:
                        return PublishResult(url=None, ok=False, note=f"카카오 수동 로그인 시간 초과 ({page.url}) — 다시 시도하세요")
                self.tiny_pause()

            page.wait_for_function(
                "() => typeof tinymce !== 'undefined' && tinymce.get('editor-tistory') !== null",
                timeout=15000,
            )
            self.tiny_pause()

            # 임시저장 복원 다이얼로그 자동 dismiss — ESC만 사용 (다른 selector는 사이드 메뉴 잘못 클릭 위험)
            try:
                page.keyboard.press("Escape")
                self.tiny_pause()
                page.keyboard.press("Escape")
                self.tiny_pause()
            except Exception:
                pass

            # 제목
            page.fill("#post-title-inp", req.title)
            self.tiny_pause()

            # 본문 (TinyMCE JS API로 직접 주입)
            # setContent는 iframe view만 갱신 → triggerSave()로 hidden textarea에도 sync해야 발행 시 본문 살아남음
            page.evaluate(
                """html => {
                    const ed = tinymce.get('editor-tistory');
                    ed.setContent(html);
                    ed.save();
                    tinymce.triggerSave();
                }""",
                html_body,
            )
            self.tiny_pause()

            # 카테고리
            if req.category:
                page.evaluate("() => document.querySelector('#category-btn').click()")
                self.tiny_pause()
                # 정확 매칭 → 부분 매칭 fallback (하위 카테고리는 aria-label이 '- 운동'처럼 prefix 붙음)
                cat_el = (page.query_selector(f"#category-list [aria-label='{req.category}']")
                          or page.query_selector(f"#category-list [aria-label*='{req.category}']"))
                if cat_el:
                    cat_el.click()
                else:
                    print(f"[DEBUG] 카테고리 '{req.category}' 매칭 실패 — 미설정")
                    page.keyboard.press("Escape")
                self.tiny_pause()

            # 태그 — 셀렉터 후보 순회 (티스토리 UI 변경 대비)
            if req.tags:
                # 디버그 dump 먼저 실행
                dump = page.evaluate(
                    """() => Array.from(document.querySelectorAll('input,textarea')).map(el => {
                        const r = el.getBoundingClientRect();
                        return {
                            tag: el.tagName, id: el.id, name: el.name,
                            placeholder: el.placeholder, className: el.className, type: el.type,
                            visible: r.width > 0 && r.height > 0,
                            hidden: el.hidden, disabled: el.disabled,
                        };
                    }).filter(x =>
                        (x.id && x.id.toLowerCase().includes('tag')) ||
                        (x.name && x.name.toLowerCase().includes('tag')) ||
                        (x.placeholder && x.placeholder.includes('태그')) ||
                        (x.className && x.className.toLowerCase().includes('tag'))
                    )"""
                )
                print(f"[DEBUG] 태그 관련 input/textarea dump: {dump}")

                tag_selector: str | None = None
                for sel in ("#tagText", "#tag-input-editor", "input[name='tag']", "input[placeholder*='태그']"):
                    try:
                        loc = page.locator(sel)
                        if loc.count() > 0 and loc.first.is_visible():
                            tag_selector = sel
                            break
                    except Exception:
                        continue
                if not tag_selector:
                    print("[DEBUG] visible 태그 input 없음 — 태그 입력 건너뜀")
                else:
                    print(f"[DEBUG] 태그 셀렉터: {tag_selector}")
                    # Playwright fill/click이 actionability 검사로 실패 → JS evaluate로 직접 dispatch
                    for tag in req.tags:
                        # 합성 이벤트는 티스토리가 무시(isTrusted=false) → 실제 키 입력으로 태그 칩 생성
                        page.evaluate(
                            "(sel) => { const el = document.querySelector(sel); if (el) { el.focus(); el.value = ''; } }",
                            tag_selector,
                        )
                        page.keyboard.type(tag)
                        self.tiny_pause()
                        page.keyboard.press("Enter")
                        self.tiny_pause()

            post_url: str | None = None

            if req.mode == "draft":
                page.locator("a.action", has_text="임시저장").click()
                self.tiny_pause()
                return PublishResult(url=None, ok=True, note="임시저장 완료")

            # alert / dialog 자동 처리 + console 메시지 캡처
            page.on("dialog", lambda d: (print(f"[DEBUG] dialog type={d.type} msg={d.message[:200]}"), d.accept()))
            page.on("console", lambda m: print(f"[CONSOLE.{m.type}] {m.text[:200]}") if m.type in ("error", "warning") else None)

            # 완료 → 발행 패널
            page.click("#publish-layer-btn")
            self.tiny_pause()

            # 공개(#open20) 라디오 명시 체크 — 기본값이 비공개로 들어오는 케이스 방어
            if req.mode in ("publish", "schedule"):
                try:
                    page.locator("#open20").check(force=True)
                    self.tiny_pause()
                except Exception as e:
                    print(f"[DEBUG] #open20 체크 실패: {e}")

            if req.mode == "schedule":
                if not req.schedule_at:
                    return PublishResult(url=None, ok=False, note="schedule 모드에 schedule_at 없음")

                # 발행 패널의 visible input/label dump (디버그)
                panel_dump = page.evaluate(
                    """() => Array.from(document.querySelectorAll('input, label, button')).filter(el => {
                        const r = el.getBoundingClientRect();
                        return r.width > 0 && r.height > 0;
                    }).map(el => ({
                        tag: el.tagName, id: el.id, name: el.name, type: el.type || '',
                        forAttr: el.getAttribute && el.getAttribute('for'),
                        text: (el.innerText || el.value || '').slice(0, 40),
                        placeholder: el.placeholder || ''
                    }))"""
                )
                print(f"[DEBUG] publish panel elements: {panel_dump}")

                # 공개(#open20) 보장
                try:
                    page.locator("#open20").check(force=True)
                except Exception:
                    pass
                self.tiny_pause()

                # '예약' 버튼 클릭 (티스토리 신 에디터: 라디오가 아니라 button text='예약')
                reserve_clicked = False
                try:
                    btn = page.locator("button", has_text="예약").filter(has_not_text="예약 발행")
                    if btn.count() > 0:
                        btn.first.click()
                        reserve_clicked = True
                        print("[DEBUG] '예약' 버튼 클릭")
                except Exception as e:
                    print(f"[DEBUG] 예약 버튼 클릭 실패: {e}")

                if not reserve_clicked:
                    return PublishResult(url=None, ok=False, note="예약 버튼 못 찾음")
                self.tiny_pause()
                self.tiny_pause()

                # 예약 버튼 클릭 후 노출된 datetime input dump
                dt_dump = page.evaluate(
                    """() => Array.from(document.querySelectorAll('input')).filter(el => {
                        const r = el.getBoundingClientRect();
                        return r.width > 0 && r.height > 0;
                    }).map(el => ({
                        id: el.id, name: el.name, type: el.type,
                        placeholder: el.placeholder, value: el.value,
                        className: el.className
                    })).filter(x =>
                        x.type === 'datetime-local' || x.type === 'date' || x.type === 'time' ||
                        (x.id && /reserv|publish|date|time/i.test(x.id)) ||
                        (x.name && /reserv|publish|date|time/i.test(x.name)) ||
                        (x.className && /reserv|publish|date|time/i.test(x.className))
                    )"""
                )
                print(f"[DEBUG] datetime input 후보: {dt_dump}")

                # RFC3339 분해 — 티스토리는 시/분 number input + 날짜 select 분리
                from datetime import datetime
                dt = datetime.fromisoformat(req.schedule_at)

                # 광범위한 dump (input + select + button — calendar trigger 포함)
                all_dt_dump = page.evaluate(
                    """() => Array.from(document.querySelectorAll('input, select, button, [class*="cal"], [class*="picker"], [data-toggle], [aria-haspopup]')).filter(el => {
                        const r = el.getBoundingClientRect();
                        return r.width > 0 && r.height > 0;
                    }).map(el => ({
                        tag: el.tagName, id: el.id, name: el.name,
                        type: el.tagName === 'SELECT' ? 'select' : (el.type || ''),
                        value: el.value, className: el.className || '',
                        text: (el.innerText||'').trim().slice(0, 30)
                    })).filter(x =>
                        /date|publish|time|year|month|day|hour|minute|reserv|cal|picker/i.test(
                            (x.id||'') + ' ' + (x.name||'') + ' ' + (x.className||'')
                        )
                    )"""
                )
                print(f"[DEBUG] 모든 날짜/시간 후보: {all_dt_dump}")

                # 시/분은 dateHour/dateMinute number input — JS로 직접 dispatch
                def set_value(selector: str, value: str) -> bool:
                    try:
                        return bool(page.evaluate(
                            """({sel, val}) => {
                                const el = document.querySelector(sel);
                                if (!el) return false;
                                const setter = Object.getOwnPropertyDescriptor(
                                    el.tagName === 'SELECT' ? HTMLSelectElement.prototype : HTMLInputElement.prototype,
                                    'value'
                                ).set;
                                setter.call(el, val);
                                el.dispatchEvent(new Event('input', {bubbles: true}));
                                el.dispatchEvent(new Event('change', {bubbles: true}));
                                return true;
                            }""",
                            {"sel": selector, "val": value},
                        ))
                    except Exception as e:
                        print(f"[DEBUG] set_value 실패 {selector}={value}: {e}")
                        return False

                # 시/분
                hour_ok = set_value("#dateHour", str(dt.hour))
                minute_ok = set_value("#dateMinute", str(dt.minute))
                print(f"[DEBUG] hour={dt.hour} ok={hour_ok}, minute={dt.minute} ok={minute_ok}")

                # 날짜 — 후보 선택자 순회 + datetime-local 단일 입력 fallback
                year_ok = (
                    set_value("#dateYear", str(dt.year))
                    or set_value("select[name='dateYear']", str(dt.year))
                    or set_value("input[name='dateYear']", str(dt.year))
                    or set_value("select#year", str(dt.year))
                )
                month_ok = (
                    set_value("#dateMonth", str(dt.month))
                    or set_value("select[name='dateMonth']", str(dt.month))
                    or set_value("input[name='dateMonth']", str(dt.month))
                    or set_value("select#month", str(dt.month))
                )
                day_ok = (
                    set_value("#dateDay", str(dt.day))
                    or set_value("select[name='dateDay']", str(dt.day))
                    or set_value("input[name='dateDay']", str(dt.day))
                    or set_value("select#day", str(dt.day))
                )
                print(f"[DEBUG] year={dt.year} ok={year_ok}, month={dt.month} ok={month_ok}, day={dt.day} ok={day_ok}")

                # 단일 datetime-local input 또는 date input fallback
                if not (year_ok and month_ok and day_ok):
                    iso_date = f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}"
                    iso_datetime = f"{iso_date}T{dt.hour:02d}:{dt.minute:02d}"
                    date_fallback = (
                        set_value("input[type='datetime-local']", iso_datetime)
                        or set_value("input[type='date']", iso_date)
                        or set_value("input[name*='date']:not([name*='Hour']):not([name*='Minute'])", iso_date)
                    )
                    if date_fallback:
                        year_ok = month_ok = day_ok = True
                        print(f"[DEBUG] 날짜 fallback 성공: {iso_datetime}")

                # 신 UI: 날짜 input(dateYear/Month/Day)이 없고, 날짜는 button.btn_reserve
                # 텍스트('YYYY-MM-DD')로 표시됨. 변경은 캘린더 위젯 클릭이 필요하나,
                # target이 이미 표시된 예약일과 같으면(당일/기본값 예약) 날짜 변경 불필요 → 통과.
                if not (year_ok and month_ok and day_ok):
                    target_date = f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}"
                    try:
                        shown = page.evaluate(
                            "() => { const b = document.querySelector('button.btn_reserve');"
                            " return b ? b.textContent.trim() : null; }"
                        )
                    except Exception:
                        shown = None
                    print(f"[DEBUG] btn_reserve 표시일={shown}, target={target_date}")
                    if shown == target_date:
                        year_ok = month_ok = day_ok = True
                        print("[DEBUG] 예약일이 이미 target과 동일 — 날짜 변경 불필요, 통과")

                # 시간만 통과하고 날짜 미적용이면 잘못된 시각에 발행되므로 명시적 중단
                # (실제 사례: 5/22 11:25에 등록 시 5/23·24·25·26 예약이 모두 5/22 11:25에 발행됨)
                if not (hour_ok and minute_ok):
                    return PublishResult(url=None, ok=False, note=f"시간 입력 실패 — dump 확인 (target={dt.isoformat()})")
                if not (year_ok and month_ok and day_ok):
                    return PublishResult(
                        url=None,
                        ok=False,
                        note=(
                            f"날짜 셀렉터 미적용 — 시간만 적용되면 가장 가까운 시각으로 잘못 발행됨. "
                            f"발행 중단 (target={dt.isoformat()}). 위 'datetime input 후보' / '모든 날짜/시간 후보' "
                            f"dump 로 실제 Tistory 캘린더 UI 셀렉터 확인 후 코드 수정 필요."
                        ),
                    )
                self.tiny_pause()

                page.click("#publish-btn")
                try:
                    page.wait_for_url("**/manage/**", timeout=12000)
                except Exception:
                    pass
                return PublishResult(url=page.url, ok=True, note=f"예약 발행 완료 → {dt.strftime('%Y-%m-%d %H:%M')}")

            # 일반 공개 발행
            print(f"[DEBUG] publish-btn 클릭 전 URL: {page.url}")
            page.click("#publish-btn")
            page.wait_for_timeout(3000)
            print(f"[DEBUG] publish-btn 클릭 후 3초 URL: {page.url}")

            try:
                page.wait_for_url("**/entry/**", timeout=12000)
                post_url = page.url
                note = "발행 완료"
            except Exception:
                post_url = page.url
                note = f"발행 완료 (URL 확인 불가, current={page.url})"

        return PublishResult(url=post_url, ok=True, note=note)

    def update_post(self, post_id: str | int, req: PublishRequest) -> PublishResult:
        """기존 발행 글 수정 (publish와 별개로 분리해서 회귀 방지).

        티스토리 글 수정 URL: /manage/newpost/{post_id}
        - 임시저장 복원 다이얼로그 처리 후 기존 콘텐츠가 로드된 상태에서 시작.
        - 제목/본문/태그는 덮어쓰기, 카테고리는 req.category 있을 때만 변경.
        - mode='publish'만 지원 (수정 후 즉시 재발행).
        """
        if not has_profile("tistory"):
            return PublishResult(url=None, ok=False, note="세션 없음. `cli login tistory` 먼저 실행.")

        if req.mode != "publish":
            return PublishResult(url=None, ok=False, note=f"update_post는 mode='publish'만 지원 (요청={req.mode})")

        html_body = md_lib.markdown(req.body_md, extensions=_MD_EXTENSIONS)
        html_body = enhance_html(
            html_body,
            cta_url=getattr(req, "cta_url", None),
            cta_text=getattr(req, "cta_text", None),
        )
        edit_url = f"https://{config.TISTORY_BLOG_NAME}.tistory.com/manage/newpost/{post_id}"

        with open_context("tistory") as ctx:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto(edit_url, wait_until="domcontentloaded")

            # 카카오 SSO 재인증 (publish 메서드와 동일)
            if "/auth/login" in page.url:
                kakao_btn = page.query_selector(
                    "a.link_kakao_id, a.btn_login.link_kakao_id, "
                    "a[href*='kauth.kakao.com'], a[href*='kakao'][class*='login'], "
                    "button:has-text('카카오'), a:has-text('카카오')"
                )
                if not kakao_btn:
                    return PublishResult(url=None, ok=False, note=f"카카오 로그인 버튼 없음 ({page.url})")
                kakao_btn.click()
                try:
                    page.wait_for_url("**/manage/newpost/**", timeout=8000)
                except Exception:
                    pass
                if "accounts.kakao.com" in page.url:
                    try:
                        page.wait_for_load_state("networkidle", timeout=10000)
                    except Exception:
                        pass
                    simple = page.query_selector("a.wrap_profile")
                    if not simple:
                        return PublishResult(url=None, ok=False, note=f"간편 로그인 계정 없음 ({page.url})")
                    simple.click()
                    try:
                        page.wait_for_url("**/manage/newpost/**", timeout=15000)
                    except Exception:
                        return PublishResult(url=None, ok=False, note=f"카카오 SSO 실패 ({page.url})")
                self.tiny_pause()

            page.wait_for_function(
                "() => typeof tinymce !== 'undefined' && tinymce.get('editor-tistory') !== null",
                timeout=15000,
            )
            # 기존 콘텐츠 로드 + 임시저장 복원 다이얼로그가 한꺼번에 뜰 수 있어 좀 더 대기
            self.tiny_pause()
            self.tiny_pause()
            page.wait_for_timeout(1500)

            # 임시저장 복원 다이얼로그 자동 dismiss — ESC만 사용
            try:
                page.keyboard.press("Escape")
                self.tiny_pause()
                page.keyboard.press("Escape")
                self.tiny_pause()
            except Exception:
                pass

            # 제목 — 기존 값 지우고 새 값 입력
            page.fill("#post-title-inp", "")
            self.tiny_pause()
            page.fill("#post-title-inp", req.title)
            self.tiny_pause()

            # 본문 — setContent로 덮어쓰기 (TinyMCE는 setContent가 자동으로 기존 내용 대체)
            page.evaluate(
                """html => {
                    const ed = tinymce.get('editor-tistory');
                    ed.setContent(html);
                    ed.save();
                    tinymce.triggerSave();
                }""",
                html_body,
            )
            self.tiny_pause()

            # 카테고리 — req.category 있을 때만 변경
            if req.category:
                page.evaluate("() => document.querySelector('#category-btn').click()")
                self.tiny_pause()
                # 정확 매칭 → 부분 매칭 fallback (하위 카테고리는 aria-label이 '- 운동'처럼 prefix 붙음)
                cat_el = (page.query_selector(f"#category-list [aria-label='{req.category}']")
                          or page.query_selector(f"#category-list [aria-label*='{req.category}']"))
                if cat_el:
                    cat_el.click()
                else:
                    print(f"[DEBUG] 카테고리 '{req.category}' 매칭 실패 — 미설정")
                    page.keyboard.press("Escape")
                self.tiny_pause()

            # 태그 — 기존 태그가 있을 수 있으나, 일단 새 태그 추가 (덮어쓰기 안 함)
            # 정확한 덮어쓰기는 별도 UI 조작이 필요해서 안정성 우선으로 append만.
            if req.tags:
                tag_selector: str | None = None
                for sel in ("#tagText", "#tag-input-editor", "input[name='tag']", "input[placeholder*='태그']"):
                    try:
                        loc = page.locator(sel)
                        if loc.count() > 0 and loc.first.is_visible():
                            tag_selector = sel
                            break
                    except Exception:
                        continue
                if tag_selector:
                    print(f"[DEBUG] update 태그 셀렉터: {tag_selector}")
                    for tag in req.tags:
                        # 합성 이벤트는 티스토리가 무시(isTrusted=false) → 실제 키 입력으로 태그 칩 생성
                        page.evaluate(
                            "(sel) => { const el = document.querySelector(sel); if (el) { el.focus(); el.value = ''; } }",
                            tag_selector,
                        )
                        page.keyboard.type(tag)
                        self.tiny_pause()
                        page.keyboard.press("Enter")
                        self.tiny_pause()

            # dialog/console 핸들러
            page.on("dialog", lambda d: (print(f"[DEBUG] dialog type={d.type} msg={d.message[:200]}"), d.accept()))
            page.on("console", lambda m: print(f"[CONSOLE.{m.type}] {m.text[:200]}") if m.type in ("error", "warning") else None)

            # 완료 → 발행 패널
            page.click("#publish-layer-btn")
            self.tiny_pause()

            # 공개 라디오 보장 (수정 시 비공개로 바뀌는 케이스 방어)
            try:
                page.locator("#open20").check(force=True)
                self.tiny_pause()
            except Exception as e:
                print(f"[DEBUG] #open20 체크 실패: {e}")

            # 재발행
            print(f"[DEBUG] update publish-btn 클릭 전 URL: {page.url}")
            page.click("#publish-btn")
            page.wait_for_timeout(3000)
            print(f"[DEBUG] update publish-btn 클릭 후 3초 URL: {page.url}")

            post_url: str | None
            try:
                page.wait_for_url("**/entry/**", timeout=12000)
                post_url = page.url
                note = f"수정 완료 (post_id={post_id})"
            except Exception:
                post_url = page.url
                note = f"수정 완료 (post_id={post_id}, current={page.url})"

        return PublishResult(url=post_url, ok=True, note=note)
