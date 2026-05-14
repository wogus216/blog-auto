"""Blogger 예약 글에 라벨(태그)을 patch로 추가.

5/14 작업 컨텍스트: SSG·두산·삼성·롯데 4팀이 원래 태그 조합으로 발행 실패.
태그 없이 발행은 성공했으므로, 이제 추가하는 게 목표.

전략: 전체 태그 한 번 시도 → 실패하면 binary search로 문제 태그 격리.

사용법:
  uv run python scripts/patch_blogger_labels.py --dry      # 매칭만 확인
  uv run python scripts/patch_blogger_labels.py             # 4팀 라벨 추가
  uv run python scripts/patch_blogger_labels.py --only ssg  # 1팀만
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from blog_auto import config  # noqa: E402
from blog_auto.publishers.blogger import _get_credentials  # noqa: E402
from googleapiclient.discovery import build  # noqa: E402
from googleapiclient.errors import HttpError  # noqa: E402

DRAFTS_DIR = ROOT / "posts" / "_drafts"

# 4팀: (팀키, blogger 파일명, 제목 매칭 키워드)
TEAM_MATCHES = [
    ("ssg",     "blogger__2026_ssg_landers_guide_v2.md",        ["SSG 랜더스", "SSG랜더스"]),
    ("doosan",  "blogger__2026_doosan_bears_guide_v2.md",       ["두산 베어스", "두산베어스"]),
    ("samsung", "blogger__2026_samsung_lions_guide_v2.md",      ["삼성 라이온즈", "삼성라이온즈"]),
    ("lotte",   "blogger__2026_lotte_giants_sajik_guide_v2.md", ["롯데 자이언츠", "롯데자이언츠"]),
]

# frontmatter 파서 (다른 스크립트와 공유)
_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _parse_simple_yaml(text: str) -> dict:
    out: dict = {}
    for line in text.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#") or ":" not in line:
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


def load_tags(fname: str) -> tuple[str, list[str]]:
    """frontmatter에서 title, tags 추출."""
    text = (DRAFTS_DIR / fname).read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    if not m:
        return "", []
    meta = _parse_simple_yaml(m.group(1))
    return str(meta.get("title", "")), list(meta.get("tags", []) or [])


def list_scheduled_posts(service) -> list[dict]:
    """SCHEDULED 상태의 글 목록 (페이지네이션 포함)."""
    posts: list[dict] = []
    page_token = None
    while True:
        kwargs = {
            "blogId": config.BLOGGER_BLOG_ID,
            "status": "SCHEDULED",
            "maxResults": 50,
            "fields": "items(id,title,published,labels,url),nextPageToken",
        }
        if page_token:
            kwargs["pageToken"] = page_token
        resp = service.posts().list(**kwargs).execute()
        posts.extend(resp.get("items", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return posts


def match_post(posts: list[dict], keywords: list[str]) -> dict | None:
    """제목 부분문자열 매칭으로 글 찾기."""
    for p in posts:
        title = p.get("title", "")
        for kw in keywords:
            if kw.lower() in title.lower():
                return p
    return None


def patch_labels(service, post_id: str, labels: list[str]) -> tuple[bool, str]:
    """라벨 patch 시도. (성공 여부, 메시지)."""
    try:
        service.posts().patch(
            blogId=config.BLOGGER_BLOG_ID,
            postId=post_id,
            body={"labels": labels},
        ).execute()
        return True, "OK"
    except HttpError as e:
        return False, str(e)[:300]


def binary_search_bad_labels(
    service, post_id: str, labels: list[str]
) -> tuple[list[str], list[str]]:
    """문제 태그 격리. (성공 적용된 라벨 리스트, 거부된 라벨 리스트) 반환.

    재귀 binary search: 라벨 절반씩 나눠서 시도.
    """
    if not labels:
        return [], []

    # 전체 시도
    ok, msg = patch_labels(service, post_id, labels)
    if ok:
        return labels, []

    if len(labels) == 1:
        # 단일 라벨 실패 → 이건 문제 라벨
        return [], labels

    # 절반으로 나눠 재귀
    mid = len(labels) // 2
    left = labels[:mid]
    right = labels[mid:]

    left_ok, left_bad = binary_search_bad_labels(service, post_id, left)
    # left 결과를 유지한 채로 right 추가 시도
    if left_ok:
        # 누적 시도: left_ok + right
        ok, _ = patch_labels(service, post_id, left_ok + right)
        if ok:
            return left_ok + right, left_bad
        # 누적 실패 → right만 단독 시도
    right_ok, right_bad = binary_search_bad_labels(service, post_id, right)

    # 최종 결합: left_ok + right_ok 가능한가 확인
    final = left_ok + right_ok
    if final:
        ok, _ = patch_labels(service, post_id, final)
        if ok:
            return final, left_bad + right_bad
        # 결합 실패 → 더 작은 단위로 축소 (간단히 left_ok만 유지)
        ok, _ = patch_labels(service, post_id, left_ok)
        if ok:
            return left_ok, left_bad + right_bad + right_ok
        return [], labels  # fallback

    return [], left_bad + right_bad


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="매칭만 확인")
    ap.add_argument("--only", default="", help="콤마로 구분된 팀키만")
    args = ap.parse_args()

    only_set = {k.strip() for k in args.only.split(",") if k.strip()} if args.only else set()
    targets = [t for t in TEAM_MATCHES if not only_set or t[0] in only_set]

    print(f"\n[1/3] Blogger SCHEDULED 글 목록 조회")
    creds = _get_credentials()
    service = build("blogger", "v3", credentials=creds)
    posts = list_scheduled_posts(service)
    print(f"  → SCHEDULED 글 {len(posts)}개")
    for p in posts:
        print(f"    - id={p['id']}  {p['title'][:60]}")

    print(f"\n[2/3] 4팀 매칭")
    print("-" * 70)
    matched: dict[str, dict] = {}
    for team, fname, kw in targets:
        m = match_post(posts, kw)
        if m:
            title, tags = load_tags(fname)
            matched[team] = {"post": m, "title": title, "tags": tags}
            print(f"  ✓ {team:8s} id={m['id']}  tags={len(tags)}개")
        else:
            print(f"  ✗ {team:8s} 매칭 실패")

    if args.dry:
        print("\n[DRY] 종료.")
        return

    print(f"\n[3/3] 라벨 patch (실패 시 binary search)")
    print("-" * 70)
    summary: list[tuple[str, int, int, list[str]]] = []
    for team, info in matched.items():
        post_id = info["post"]["id"]
        tags = info["tags"]
        if not tags:
            print(f"  [{team}] tags 없음 → 스킵")
            continue

        print(f"\n[{team}] 전체 {len(tags)}개 시도...")
        ok, msg = patch_labels(service, post_id, tags)
        if ok:
            print(f"  ✓ 전체 적용 성공")
            summary.append((team, len(tags), 0, []))
            continue

        print(f"  ✗ 전체 거부 → binary search 시작")
        applied, rejected = binary_search_bad_labels(service, post_id, tags)
        print(f"  → 적용: {len(applied)}개")
        print(f"  → 거부: {len(rejected)}개 ({', '.join(rejected) if rejected else '없음'})")
        summary.append((team, len(applied), len(rejected), rejected))

    print("\n" + "=" * 70)
    print("결과 요약")
    print("=" * 70)
    for team, ok_n, bad_n, bad in summary:
        print(f"  {team:8s} 적용 {ok_n:>2}개, 거부 {bad_n}개  {'(' + ', '.join(bad) + ')' if bad else ''}")


if __name__ == "__main__":
    main()
