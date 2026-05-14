"""티스토리 9팀 야구 가이드 v1 → v2 일괄 수정 자동화.

이미 발행된 9팀 "야구 완벽가이드" 글을 v2 내용으로 일괄 업데이트한다.

사용법:
    uv run python scripts/update_tistory_baseball_v2.py --dry           # 매칭만 확인
    uv run python scripts/update_tistory_baseball_v2.py                  # 매칭 + 즉시 수정
    uv run python scripts/update_tistory_baseball_v2.py --only hanwha    # 1팀만

흐름:
1. 티스토리 관리 페이지(/manage/posts) 글 목록을 스크래핑해서 (제목, post_id) 추출
2. 9팀 매니페스트와 case-insensitive 부분문자열 매칭
3. (--dry가 아니면) 각 팀의 v2 마크다운을 읽어서 update_post(post_id, req) 호출
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from blog_auto import config  # noqa: E402
from blog_auto.publishers.base import PublishRequest  # noqa: E402
from blog_auto.publishers.session import open_context  # noqa: E402

DRAFTS_DIR = ROOT / "posts" / "_drafts"

# 9팀 매핑: (팀키, v2 파일명, 제목 매칭 키워드 후보)
TEAM_MATCHES: list[tuple[str, str, list[str]]] = [
    ("hanwha",  "2026_hanwha_eagles_guide_v2.md",      ["한화이글스", "한화"]),
    ("kia",     "2026_kia_tigers_guide_v3.md",         ["KIA 타이거즈", "기아 타이거즈", "KIA"]),
    ("lg",      "2026_lg_twins_guide_v2.md",           ["LG 트윈스", "LG트윈스"]),
    ("ssg",     "2026_ssg_landers_guide_v2.md",        ["SSG 랜더스", "SSG랜더스"]),
    ("doosan",  "2026_doosan_bears_guide_v2.md",       ["두산 베어스", "두산베어스"]),
    ("kt",      "2026_kt_wiz_guide_v2.md",             ["KT 위즈", "KT위즈", "kt wiz"]),
    ("kiwoom",  "2026_kiwoom_heroes_guide_v2.md",      ["키움 히어로즈", "키움히어로즈"]),
    ("samsung", "2026_samsung_lions_guide_v2.md",      ["삼성 라이온즈", "삼성라이온즈"]),
    ("lotte",   "2026_lotte_giants_sajik_guide_v2.md", ["롯데 자이언츠", "롯데자이언츠"]),
]

# 무관한 글 제외용 필터 (제목에 이 단어 중 하나라도 있어야 매칭 후보로 인정)
EXTRA_FILTER_KEYWORDS = ["완벽 가이드", "완벽가이드", "직관", "가이드"]


# ─────────────────────────────────────────────────────────────
# frontmatter 파서 (schedule_baseball_bloggers.py 와 동일)
# ─────────────────────────────────────────────────────────────
_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _parse_simple_yaml(text: str) -> dict:
    out: dict = {}
    for line in text.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            items = [s.strip().strip("'\"") for s in inner.split(",") if s.strip()]
            out[key] = items
        elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            out[key] = val[1:-1]
        else:
            out[key] = val
    return out


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    meta = _parse_simple_yaml(m.group(1))
    body = m.group(2)
    return meta, body


def build_request(path: Path) -> PublishRequest:
    """frontmatter + 본문을 PublishRequest로 변환. mode='publish' 강제."""
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    return PublishRequest(
        title=meta.get("title", path.stem),
        body_md=body,
        tags=meta.get("tags", []) or [],
        category=meta.get("category", "") or "",
        mode="publish",  # update_post는 publish만 지원
        schedule_at=None,
        cta_url=meta.get("cta_url"),
        cta_text=meta.get("cta_text"),
    )


# ─────────────────────────────────────────────────────────────
# 티스토리 관리 페이지 스크래핑
# ─────────────────────────────────────────────────────────────
def _handle_kakao_login(page) -> bool:
    """카카오 SSO 자동 처리. 로그인 OK면 True."""
    if "/auth/login" not in page.url:
        return True
    kakao_btn = page.query_selector(
        "a.link_kakao_id, a.btn_login.link_kakao_id, "
        "a[href*='kauth.kakao.com'], a[href*='kakao'][class*='login'], "
        "button:has-text('카카오'), a:has-text('카카오')"
    )
    if not kakao_btn:
        print(f"[!] 카카오 로그인 버튼 없음 ({page.url})")
        return False
    kakao_btn.click()
    page.wait_for_timeout(3000)
    if "accounts.kakao.com" in page.url:
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        simple = page.query_selector("a.wrap_profile")
        if simple:
            simple.click()
            page.wait_for_timeout(3000)
    return "/auth/login" not in page.url


def scrape_post_list(blog_name: str) -> list[dict]:
    """티스토리 관리 페이지에서 (title, post_id, href) 목록 추출.

    유연한 셀렉터 후보 순회 + JS evaluate dump 패턴 (publish 메서드 참고).
    첫 페이지만 우선 (9팀 글이 보통 최근 글이라 가정).
    """
    posts_url = f"https://{blog_name}.tistory.com/manage/posts"

    with open_context("tistory") as ctx:
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(posts_url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        if not _handle_kakao_login(page):
            return []
        if "/auth/login" in page.url or page.url != posts_url:
            # 로그인 후 리다이렉트 됐으면 한번 더
            page.goto(posts_url, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

        print(f"[INFO] 관리 페이지 URL: {page.url}")

        # ajax 로딩 대기
        page.wait_for_timeout(2500)

        # 수정 링크의 행에서 글 제목을 다양한 후보로 추출
        all_links = page.evaluate(
            """() => {
                const editAnchors = Array.from(document.querySelectorAll(
                    'a[href*="/manage/newpost/"], a[href*="/manage/post/"]'
                ));
                return editAnchors.map(a => {
                    const row = a.closest('tr, li, .post-item, .list_post, [role="row"]') || a.parentElement;
                    let title = '';
                    if (row) {
                        // 1순위: /entry/ 링크 (실제 글 제목 링크)
                        const entryLink = row.querySelector('a[href*="/entry/"]');
                        if (entryLink) title = (entryLink.innerText || entryLink.textContent || '').trim();
                        // 2순위: title-like 클래스
                        if (!title) {
                            const t = row.querySelector('[class*="title" i], [class*="subject" i], strong.name, .post-title');
                            if (t) title = (t.innerText || t.textContent || '').trim();
                        }
                        // 3순위: 같은 행에서 '수정'/'삭제' 제외한 가장 긴 텍스트 노드
                        if (!title) {
                            const cands = Array.from(row.querySelectorAll('a, span, strong, p, div'))
                                .map(el => (el.innerText || el.textContent || '').trim())
                                .filter(t => t && t.length > 5 && !/^(수정|삭제|공개|비공개|발행|예약|임시저장)$/.test(t))
                                .sort((a, b) => b.length - a.length);
                            if (cands.length) title = cands[0];
                        }
                    }
                    return { href: a.href, title: title.slice(0, 200) };
                });
            }"""
        )

        print(f"[INFO] 발견된 글 링크 후보: {len(all_links)}개")

        # 만약 위가 다 실패하면 entry 링크로부터 직접 추출 시도
        empty_titles = sum(1 for it in all_links if not it.get("title"))
        if empty_titles >= len(all_links) // 2:
            print(f"[INFO] {empty_titles}개 제목 비어있음 → entry 링크 fallback 시도")
            entry_links = page.evaluate(
                """() => Array.from(document.querySelectorAll('a[href*="/entry/"]')).map(a => {
                    const m = a.href.match(/\\/entry\\/(\\d+)/);
                    return {
                        href: a.href,
                        post_id: m ? m[1] : null,
                        title: ((a.innerText || a.textContent || '').trim()).slice(0, 200)
                    };
                }).filter(x => x.post_id && x.title.length > 3)"""
            )
            print(f"[INFO] entry 링크 fallback에서 {len(entry_links)}개 발견")
            # entry 링크에서 가져온 (post_id, title) 매핑
            entry_map = {e["post_id"]: e["title"] for e in entry_links}
            # all_links의 빈 title을 entry_map으로 보강
            id_re_tmp = re.compile(r"/manage/(?:newpost|post)/(\d+)")
            for it in all_links:
                if it.get("title"):
                    continue
                m = id_re_tmp.search(it.get("href", ""))
                if m and m.group(1) in entry_map:
                    it["title"] = entry_map[m.group(1)]

        # post_id 추출 + 중복 제거
        id_re = re.compile(r"/manage/(?:newpost|post)/(\d+)")
        seen: set[str] = set()
        results: list[dict] = []
        for it in all_links:
            href = it.get("href", "")
            title = it.get("title", "")
            m = id_re.search(href)
            if not m:
                continue
            pid = m.group(1)
            if pid in seen:
                continue
            seen.add(pid)
            results.append({"post_id": pid, "title": title, "href": href})

        if not results:
            # fallback dump
            dump = page.evaluate(
                """() => Array.from(document.querySelectorAll('a')).slice(0, 30).map(a => ({
                    href: a.href, text: (a.innerText || '').slice(0, 80)
                })).filter(x => x.href.includes('manage') || x.href.includes('entry'))"""
            )
            print(f"[DEBUG] fallback a-tag dump: {dump}")

        return results


# ─────────────────────────────────────────────────────────────
# 매칭 로직
# ─────────────────────────────────────────────────────────────
def match_posts(posts: list[dict]) -> dict[str, dict | None]:
    """팀키 → matched post (또는 None) 매핑.

    매칭 규칙:
    - 제목에 키워드 후보 중 하나라도 case-insensitive 부분문자열로 포함
    - 추가 필터: EXTRA_FILTER_KEYWORDS 중 하나라도 포함 (무관한 글 제외)
    - 첫 매칭 채택
    """
    matched: dict[str, dict | None] = {}
    for team, _fname, keywords in TEAM_MATCHES:
        found: dict | None = None
        for p in posts:
            title_lower = p["title"].lower()
            kw_hit = any(kw.lower() in title_lower for kw in keywords)
            if not kw_hit:
                continue
            filter_hit = any(f.lower() in title_lower for f in EXTRA_FILTER_KEYWORDS)
            if not filter_hit:
                continue
            found = p
            break
        matched[team] = found
    return matched


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="매칭까지만 하고 종료")
    ap.add_argument("--only", default="", help="콤마로 구분된 팀키만 (예: hanwha,kia)")
    args = ap.parse_args()

    blog = config.TISTORY_BLOG_NAME
    if not blog:
        print("[!] TISTORY_BLOG_NAME 환경변수가 비어 있습니다.")
        sys.exit(1)

    only_set: set[str] = set()
    if args.only:
        only_set = {k.strip() for k in args.only.split(",") if k.strip()}

    targets = [m for m in TEAM_MATCHES if not only_set or m[0] in only_set]
    if not targets:
        print(f"[!] --only 매칭 없음: {args.only}")
        sys.exit(1)

    print(f"\n티스토리 야구 가이드 v2 일괄 수정 — 대상 {len(targets)}팀")
    print("=" * 70)

    # 1) 글 목록 스크래핑
    print(f"\n[1/3] 관리 페이지 스크래핑 (blog={blog})")
    posts = scrape_post_list(blog)
    print(f"  → 후보 글 {len(posts)}개")

    # 후보 글 제목 dump (디버깅용)
    if posts:
        print("\n[DEBUG] 발견된 글 목록:")
        for i, p in enumerate(posts):
            print(f"  [{i+1:2d}] id={p['post_id']:>10}  title={p['title'][:80]!r}")

    # 2) 매칭
    print(f"\n[2/3] 9팀 매칭")
    print("-" * 70)
    all_matched = match_posts(posts)
    # only 필터 적용
    matched = {k: v for k, v in all_matched.items() if not only_set or k in only_set}

    for team, m in matched.items():
        if m:
            print(f"  ✓ {team:10s} post_id={m['post_id']:>10}  {m['title'][:50]}")
        else:
            print(f"  ✗ {team:10s} 매칭 실패")

    missing = [t for t, m in matched.items() if m is None]
    if missing:
        print(f"\n[!] 매칭 실패 팀: {', '.join(missing)}")

    if args.dry:
        print("\n[DRY] 매칭만 확인하고 종료.")
        return

    # 3) 일괄 수정
    print(f"\n[3/3] 일괄 수정 실행")
    print("-" * 70)

    from blog_auto.publishers.tistory import TistoryPublisher
    pub = TistoryPublisher()

    results: list[tuple[str, bool, str]] = []
    for team, _fname, _kw in TEAM_MATCHES:
        if only_set and team not in only_set:
            continue
        m = matched.get(team)
        if not m:
            results.append((team, False, "매칭 실패"))
            continue

        # 파일명 찾기
        fname = next((f for t, f, _ in TEAM_MATCHES if t == team), None)
        if not fname:
            results.append((team, False, "파일명 없음"))
            continue
        path = DRAFTS_DIR / fname
        if not path.exists():
            print(f"  ✗ {team}: 파일 없음 ({path.name})")
            results.append((team, False, "파일 없음"))
            continue

        try:
            req = build_request(path)
        except Exception as e:
            print(f"  ✗ {team}: frontmatter 파싱 실패 — {e}")
            results.append((team, False, f"파싱 실패: {e}"))
            continue

        print(f"\n[{team}] post_id={m['post_id']} → {req.title[:50]}")
        try:
            result = pub.update_post(m["post_id"], req)
            status = "✓" if result.ok else "✗"
            print(f"  {status} {result.note}")
            if result.url:
                print(f"  URL: {result.url}")
            results.append((team, result.ok, result.note))
        except Exception as e:
            print(f"  ✗ 수정 중 예외 — {e}")
            results.append((team, False, f"예외: {e}"))

    print("\n" + "=" * 70)
    print("수정 결과 요약")
    print("=" * 70)
    for team, ok, note in results:
        mark = "✓" if ok else "✗"
        print(f"  {mark} {team:10s} {note}")
    ok_count = sum(1 for _, ok, _ in results if ok)
    print(f"\n총 {len(results)}개 중 {ok_count}개 성공")


if __name__ == "__main__":
    main()
