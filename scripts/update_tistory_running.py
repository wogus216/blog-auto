"""티스토리 나이키/아디다스 러닝화 글 일괄 in-place 업데이트.

발행된 두 글(나이키 러닝화 2026 추천 / 아디다스 러닝화 2026 추천)을
draft 파일 최신 내용으로 update_post() 호출. URL/조회수 유지.

사용법:
    uv run python scripts/update_tistory_running.py --dry         # 매칭만 확인
    uv run python scripts/update_tistory_running.py               # 매칭 + 즉시 수정
    uv run python scripts/update_tistory_running.py --only nike   # nike만
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

POST_MATCHES: list[tuple[str, str, list[str]]] = [
    ("nike",   "tistory__nike_running_pace_guide.md",   ["나이키 러닝화", "나이키러닝화"]),
    ("adidas", "tistory__adidas_running_pace_guide.md", ["아디다스 러닝화", "아디다스러닝화"]),
]

EXTRA_FILTER_KEYWORDS = ["페이스", "추천", "가이드", "Sub3"]


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
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    return PublishRequest(
        title=meta.get("title", path.stem),
        body_md=body,
        tags=meta.get("tags", []) or [],
        category=meta.get("category", "") or "",
        mode="publish",
        schedule_at=None,
        cta_url=meta.get("cta_url"),
        cta_text=meta.get("cta_text"),
    )


def _handle_kakao_login(page) -> bool:
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
    posts_url = f"https://{blog_name}.tistory.com/manage/posts"

    with open_context("tistory") as ctx:
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(posts_url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        if not _handle_kakao_login(page):
            return []
        if "/auth/login" in page.url or page.url != posts_url:
            page.goto(posts_url, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

        print(f"[INFO] 관리 페이지 URL: {page.url}")
        page.wait_for_timeout(2500)

        all_links = page.evaluate(
            """() => {
                const editAnchors = Array.from(document.querySelectorAll(
                    'a[href*="/manage/newpost/"], a[href*="/manage/post/"]'
                ));
                return editAnchors.map(a => {
                    const row = a.closest('tr, li, .post-item, .list_post, [role="row"]') || a.parentElement;
                    let title = '';
                    if (row) {
                        const entryLink = row.querySelector('a[href*="/entry/"]');
                        if (entryLink) title = (entryLink.innerText || entryLink.textContent || '').trim();
                        if (!title) {
                            const t = row.querySelector('[class*="title" i], [class*="subject" i], strong.name, .post-title');
                            if (t) title = (t.innerText || t.textContent || '').trim();
                        }
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
            entry_map = {e["post_id"]: e["title"] for e in entry_links}
            id_re_tmp = re.compile(r"/manage/(?:newpost|post)/(\d+)")
            for it in all_links:
                if it.get("title"):
                    continue
                m = id_re_tmp.search(it.get("href", ""))
                if m and m.group(1) in entry_map:
                    it["title"] = entry_map[m.group(1)]

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

        return results


def match_posts(posts: list[dict]) -> dict[str, dict | None]:
    matched: dict[str, dict | None] = {}
    for key, _fname, keywords in POST_MATCHES:
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
        matched[key] = found
    return matched


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="매칭까지만 하고 종료")
    ap.add_argument("--only", default="", help="콤마로 구분된 키만 (예: nike,adidas)")
    args = ap.parse_args()

    blog = config.TISTORY_BLOG_NAME
    if not blog:
        print("[!] TISTORY_BLOG_NAME 환경변수가 비어 있습니다.")
        sys.exit(1)

    only_set: set[str] = set()
    if args.only:
        only_set = {k.strip() for k in args.only.split(",") if k.strip()}

    targets = [m for m in POST_MATCHES if not only_set or m[0] in only_set]
    if not targets:
        print(f"[!] --only 매칭 없음: {args.only}")
        sys.exit(1)

    print(f"\n티스토리 러닝화 글 in-place 수정 — 대상 {len(targets)}개")
    print("=" * 70)

    print(f"\n[1/3] 관리 페이지 스크래핑 (blog={blog})")
    posts = scrape_post_list(blog)
    print(f"  → 후보 글 {len(posts)}개")

    if posts:
        print("\n[DEBUG] 발견된 글 목록 (처음 30개):")
        for i, p in enumerate(posts[:30]):
            print(f"  [{i+1:2d}] id={p['post_id']:>10}  title={p['title'][:80]!r}")

    print(f"\n[2/3] 매칭")
    print("-" * 70)
    all_matched = match_posts(posts)
    matched = {k: v for k, v in all_matched.items() if not only_set or k in only_set}

    for key, m in matched.items():
        if m:
            print(f"  ✓ {key:8s} post_id={m['post_id']:>10}  {m['title'][:60]}")
        else:
            print(f"  ✗ {key:8s} 매칭 실패")

    missing = [t for t, m in matched.items() if m is None]
    if missing:
        print(f"\n[!] 매칭 실패: {', '.join(missing)}")

    if args.dry:
        print("\n[DRY] 매칭만 확인하고 종료.")
        return

    print(f"\n[3/3] 일괄 수정 실행")
    print("-" * 70)

    from blog_auto.publishers.tistory import TistoryPublisher
    pub = TistoryPublisher()

    results: list[tuple[str, bool, str]] = []
    for key, fname, _kw in POST_MATCHES:
        if only_set and key not in only_set:
            continue
        m = matched.get(key)
        if not m:
            results.append((key, False, "매칭 실패"))
            continue

        path = DRAFTS_DIR / fname
        if not path.exists():
            print(f"  ✗ {key}: 파일 없음 ({path.name})")
            results.append((key, False, "파일 없음"))
            continue

        try:
            req = build_request(path)
        except Exception as e:
            print(f"  ✗ {key}: frontmatter 파싱 실패 — {e}")
            results.append((key, False, f"파싱 실패: {e}"))
            continue

        print(f"\n[{key}] post_id={m['post_id']} → {req.title[:60]}")
        try:
            result = pub.update_post(m["post_id"], req)
            status = "✓" if result.ok else "✗"
            print(f"  {status} {result.note}")
            if result.url:
                print(f"  URL: {result.url}")
            results.append((key, result.ok, result.note or ""))
        except Exception as e:
            print(f"  ✗ {key}: update_post 예외 — {e}")
            results.append((key, False, str(e)))

    print("\n" + "=" * 70)
    print("결과 요약")
    print("-" * 70)
    for k, ok, note in results:
        mark = "✓" if ok else "✗"
        print(f"  {mark} {k:8s} {note[:80]}")


if __name__ == "__main__":
    main()
