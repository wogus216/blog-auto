"""티스토리 글 삭제 (중복 구버전 정리, 일회성).

안전장치:
- ACTION=scan (기본): 글 관리 목록의 체크박스/삭제버튼 구조만 dump (삭제 안 함)
- ACTION=delete: TARGET_IDS 글만 체크 → 삭제. confirm 다이얼로그 자동 수락.
- 삭제 전 각 대상 글의 제목을 출력해 오삭제 방지.

실행:
  ACTION=scan   uv run python scripts/tistory_delete_posts.py
  ACTION=delete uv run python scripts/tistory_delete_posts.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from blog_auto import config  # noqa: E402
from blog_auto.publishers.session import open_context  # noqa: E402
from update_tistory_running import _handle_kakao_login  # noqa: E402

BLOG = config.TISTORY_BLOG_NAME
TARGET_IDS = ["837", "838"]
ACTION = os.environ.get("ACTION", "scan")


def main() -> None:
    manage_url = f"https://{BLOG}.tistory.com/manage/posts/"
    with open_context("tistory") as ctx:
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(manage_url, wait_until="domcontentloaded")

        if "/auth/login" in page.url:
            print("[로그인 필요] 브라우저에서 카카오 로그인하세요. 최대 5분 대기...")
            ok = _handle_kakao_login(page)
            if not ok:
                print("[!] 로그인 실패")
                return
            try:
                page.wait_for_url("**/manage/**", timeout=300000)
            except Exception:
                pass
        page.wait_for_timeout(3000)
        page.goto(manage_url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        # 삭제 링크(a.btn_post) ↔ 글 post_id 매핑.
        # 각 글 행에서 제목 링크 href(/숫자 또는 /manage/post/숫자)로 post_id 추출.
        rows = page.evaluate(
            """() => Array.from(document.querySelectorAll('a.btn_post')).map((a, i) => {
                const row = a.closest('tr,li,div');
                let pid = '';
                if (row) {
                    for (const link of row.querySelectorAll("a[href]")) {
                        const m = link.getAttribute('href').match(/\\/(?:manage\\/post\\/)?(\\d{2,})(?:$|\\?|\\/)/);
                        if (m) { pid = m[1]; break; }
                    }
                }
                return { idx:i, del_href:a.getAttribute('href'),
                         del_onclick:a.getAttribute('onclick'),
                         post_id:pid, title:(row?.innerText||'').trim().slice(0,30) };
            })"""
        )
        print(f"=== 삭제링크 ↔ 글 매핑 {len(rows)}개 ===")
        for r in rows:
            mark = " ← 삭제대상" if r["post_id"] in TARGET_IDS else ""
            print(f"  [{r['idx']}] post_id={r['post_id']!r} | {r['title']}{mark}")
            if r["post_id"] in TARGET_IDS:
                print(f"        href={r['del_href']!r} onclick={r['del_onclick']!r}")

        # 삭제 대상 = post_id 매칭 + 삭제 링크(href='#')
        del_targets = sorted({r["post_id"] for r in rows
                              if r["post_id"] in TARGET_IDS and r["del_href"] == "#"})
        print(f"\n삭제 링크(href=#) 확인된 대상: {del_targets}")

        if ACTION != "delete":
            print("[scan 모드] 삭제 안 함. ACTION=delete 로 실제 삭제.")
            return

        # 네이티브 confirm 자동 수락 (커스텀 모달은 아래에서 별도 처리)
        page.on("dialog", lambda d: d.accept())

        for pid in del_targets:
            page.goto(manage_url, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            # 해당 글 행의 삭제 링크(href='#') 인덱스 찾기
            idx = page.evaluate(
                """(pid) => {
                    const links = Array.from(document.querySelectorAll('a.btn_post'));
                    for (let i=0;i<links.length;i++){
                        const a=links[i];
                        if (a.getAttribute('href')!=='#') continue;
                        const row=a.closest('tr,li,div'); if(!row) continue;
                        for (const l of row.querySelectorAll("a[href]")){
                            const m=l.getAttribute('href').match(/\\/(?:manage\\/post\\/)?(\\d{2,})/);
                            if (m && m[1]===pid) return i;
                        }
                    }
                    return -1;
                }""", pid
            )
            if idx < 0:
                print(f"  ✗ {pid}: 삭제 링크 못 찾음 — 스킵")
                continue
            print(f"  → {pid} 삭제 링크 클릭 (idx={idx}, JS click)")
            # 삭제 링크는 행 호버 시에만 visible → JS로 직접 click 이벤트 발생
            page.evaluate("(i) => document.querySelectorAll('a.btn_post')[i].click()", idx)
            page.wait_for_timeout(1500)
            # 커스텀 확인 모달 처리 (티스토리는 레이어 팝업일 수 있음)
            for sel in ("button.btn_ok", "a.btn_ok", ".layer_post button:has-text('확인')",
                        "button:has-text('삭제')", "button:has-text('확인')", "a:has-text('확인')"):
                btn = page.query_selector(sel)
                if btn and btn.is_visible():
                    btn.click()
                    print(f"    확인 모달 클릭: {sel}")
                    break
            page.wait_for_timeout(3000)
            # 검증: 글이 실제로 사라졌는지
            still = page.evaluate(
                """(pid) => !!Array.from(document.querySelectorAll("a[href]")).find(l =>
                    (l.getAttribute('href')||'').match(new RegExp('/manage/post/'+pid+'(\\\\?|$)')))""", pid
            )
            print(f"  {'✗ 아직 남아있음' if still else '✅ 삭제 확인됨'}: {pid}")


if __name__ == "__main__":
    main()
