"""기존 Blogger 글을 일괄 강화 (backfill).

money.onestepblog.info 등 Blogger 사이트의 이미 발행된 글에 다음을 자동 추가:

  1) 인-아티클 광고 (assets/ads/inarticle_blogger.html) — H2 분포 균등 분산
  2) ## 참고 자료 섹션 — 공식 출처 링크 (도메인별)
  3) ## 면책 조항 (--domain apartment_subscription) — YMYL 대응

이 스크립트는 마크다운을 거치지 않고 **Blogger API 로 HTML 본문 직접 수정**한다.
실제 적용은 --apply 가 있을 때만. 기본은 dry-run.

안전 장치
  - 기본 dry-run (--apply 없으면 변경 안 함)
  - 변경 전 HTML 을 assets/backups/blogger/{post_id}_{timestamp}.html 로 백업
  - 이미 광고/참고자료/면책이 있으면 skip (--force 로 추가 삽입)
  - --limit 으로 한 번에 처리할 글 수 제한 (기본 0 = 전체)
  - --post-id 로 1개만 처리 (검증용)

사용
  # 1) 1개 글로 동작 확인 (dry-run)
  uv run python scripts/backfill_blogger.py \\
    --blog-id $BLOGGER_STOCKS_BLOG_ID \\
    --domain apartment_subscription \\
    --post-id <single_post_id>

  # 2) 5개 글 실제 적용
  uv run python scripts/backfill_blogger.py \\
    --blog-id $BLOGGER_STOCKS_BLOG_ID \\
    --domain apartment_subscription \\
    --limit 5 --apply

  # 3) 전체 글 실제 적용 (위험, 검증 후만)
  uv run python scripts/backfill_blogger.py \\
    --blog-id $BLOGGER_STOCKS_BLOG_ID \\
    --domain apartment_subscription \\
    --apply
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from blog_auto import config  # noqa: E402
from blog_auto.publishers.blogger import _get_credentials  # noqa: E402

BACKUP_DIR = ROOT / "assets" / "backups" / "blogger"
ADS_DIR = ROOT / "assets" / "ads"
AD_MARKER = "adsbygoogle"
SOURCES_MARKER = "참고 자료"
DISCLAIMER_MARKER = "면책 조항"
TODO_TOKEN = "TODO_REPLACE_ME"

# 부동산 청약 도메인 공식 출처 (자주 인용)
SOURCES_BY_DOMAIN: dict[str, list[tuple[str, str]]] = {
    "apartment_subscription": [
        ("청약홈", "https://www.applyhome.co.kr/"),
        ("LH 청약플러스", "https://apply.lh.or.kr/"),
        ("SH 서울주택도시공사", "https://www.i-sh.co.kr/"),
        ("국토교통부 — 주택공급제도 안내", "https://www.molit.go.kr/"),
    ],
    "running_shoes": [],
    "generic": [],
}

DISCLAIMERS: dict[str, str] = {
    "apartment_subscription": (
        "본 글은 청약홈, LH, SH 등 공식 자료를 정리한 정보 제공용 콘텐츠입니다. "
        "자격·일정·분양가는 발행 시점 기준이며, 청약 신청은 본인 판단·본인 책임 하에 "
        "진행해야 합니다. 신청 전 반드시 "
        '<a href="https://www.applyhome.co.kr/" target="_blank" rel="noopener">청약홈</a> '
        "또는 해당 시행사 공식 공고문에서 최종 내용을 확인하세요."
    ),
}

# Blogger 본문 안 H2 매칭 (스타일/속성 있어도 OK)
_H2_RE = re.compile(r"<h2\b[^>]*>.*?</h2>", re.IGNORECASE | re.DOTALL)


# ---- HTML utilities --------------------------------------------------------


def _load_ad_html() -> tuple[str, bool]:
    path = ADS_DIR / "inarticle_blogger.html"
    if not path.exists():
        raise FileNotFoundError(f"광고 HTML 없음: {path}")
    html = path.read_text(encoding="utf-8").strip()
    return html, TODO_TOKEN in html


def _h2_spans(html: str) -> list[tuple[int, int]]:
    """본문 HTML 의 모든 <h2>...</h2> 의 (start, end) char 위치."""
    return [(m.start(), m.end()) for m in _H2_RE.finditer(html)]


def _decide_inarticle_count(h2_count: int) -> int:
    if h2_count < 3:
        return 0
    if h2_count <= 5:
        return 1
    if h2_count <= 8:
        return 2
    return 3


def _pick_h2_targets(h2_spans: list[tuple[int, int]], n_ads: int) -> list[int]:
    """광고 삽입 위치 (H2 start offset) 선택. 첫/마지막 H2 제외, 균등 분포."""
    if n_ads == 0 or len(h2_spans) < 3:
        return []
    candidates = h2_spans[1:-1]
    if n_ads >= len(candidates):
        return [s for s, _ in candidates]
    step = len(candidates) / n_ads
    picks = [candidates[int(step * k + step / 2)][0] for k in range(n_ads)]
    return sorted(set(picks))


def _insert_ads(html: str, ad_html: str, n_ads_override: int = -1) -> tuple[str, int]:
    """H2 직전에 광고 N개 삽입. (new_html, inserted_count) 반환."""
    spans = _h2_spans(html)
    n_ads = (
        n_ads_override if n_ads_override >= 0 else _decide_inarticle_count(len(spans))
    )
    positions = _pick_h2_targets(spans, n_ads)
    if not positions:
        return html, 0
    # 뒤에서부터 삽입 → 앞 offset 안 깨짐
    block = f"\n\n{ad_html}\n\n"
    for pos in reversed(positions):
        html = html[:pos] + block + html[pos:]
    return html, len(positions)


def _sources_block(domain: str) -> str:
    items = SOURCES_BY_DOMAIN.get(domain, [])
    if not items:
        return ""
    lis = "\n".join(
        f'  <li><a href="{u}" target="_blank" rel="noopener">{t}</a></li>'
        for t, u in items
    )
    return f"\n\n<h2>{SOURCES_MARKER}</h2>\n<ul>\n{lis}\n</ul>\n"


def _disclaimer_block(domain: str) -> str:
    text = DISCLAIMERS.get(domain, "")
    if not text:
        return ""
    return (
        f"\n\n<h2>{DISCLAIMER_MARKER}</h2>\n"
        f'<blockquote style="border-left:3px solid #aaa; padding-left:12px; color:#555;">'
        f"{text}</blockquote>\n"
    )


def _backup(post_id: str, html: str) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    p = BACKUP_DIR / f"{post_id}_{ts}.html"
    p.write_text(html, encoding="utf-8")
    return p


# ---- Per-post processing ---------------------------------------------------


def _process_post(
    post: dict,
    *,
    domain: str,
    ad_html: str,
    skip_ads: bool,
    skip_sources: bool,
    skip_disclaimer: bool,
    force: bool,
    n_ads_override: int,
) -> tuple[str, list[str], bool]:
    """단일 글 처리. (new_html, log_lines, changed) 반환."""
    html = post.get("content", "")
    title = post.get("title", "(제목 없음)")
    logs: list[str] = []

    has_ad = AD_MARKER in html
    has_sources = SOURCES_MARKER in html
    has_disclaimer = DISCLAIMER_MARKER in html
    h2_count = len(_h2_spans(html))

    logs.append(f"  · 제목: {title[:60]}")
    logs.append(
        f"  · 현재상태: H2={h2_count}, 광고={'O' if has_ad else 'X'}, "
        f"sources={'O' if has_sources else 'X'}, disclaimer={'O' if has_disclaimer else 'X'}"
    )

    new_html = html
    inserted_any = False

    # 1) 광고
    if not skip_ads and (not has_ad or force):
        new_html, n = _insert_ads(new_html, ad_html, n_ads_override=n_ads_override)
        if n > 0:
            logs.append(f"  + 인-아티클 광고 {n} 개")
            inserted_any = True
        else:
            logs.append("  - 광고 0 (H2 부족 또는 후보 없음)")
    elif has_ad:
        logs.append("  - 광고 skip (이미 있음, --force 로 추가)")

    # 2) 참고 자료
    if not skip_sources and (not has_sources or force):
        block = _sources_block(domain)
        if block:
            new_html = new_html.rstrip() + block
            logs.append(f"  + 참고 자료 {len(SOURCES_BY_DOMAIN[domain])} 개")
            inserted_any = True
        else:
            logs.append(f"  - 참고 자료 없음 (domain={domain} 매핑 비어 있음)")

    # 3) 면책
    if not skip_disclaimer and (not has_disclaimer or force):
        block = _disclaimer_block(domain)
        if block:
            new_html = new_html.rstrip() + block
            logs.append(f"  + 면책 조항 (domain={domain})")
            inserted_any = True

    return new_html, logs, inserted_any


# ---- Main ------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--blog-id",
        default=config.BLOGGER_STOCKS_BLOG_ID or config.BLOGGER_BLOG_ID,
        help="대상 Blogger ID (기본: BLOGGER_STOCKS_BLOG_ID, 없으면 BLOGGER_BLOG_ID)",
    )
    ap.add_argument(
        "--domain",
        default="apartment_subscription",
        choices=list(SOURCES_BY_DOMAIN.keys()),
        help="콘텐츠 도메인 (참고자료/면책 매핑)",
    )
    ap.add_argument("--apply", action="store_true", help="실제 patch 호출 (기본: dry-run)")
    ap.add_argument(
        "--limit", type=int, default=0, help="처리할 글 수 (기본 0 = 전체)"
    )
    ap.add_argument("--post-id", default="", help="특정 글 1개만 처리 (검증용)")
    ap.add_argument("--skip-ads", action="store_true")
    ap.add_argument("--skip-sources", action="store_true")
    ap.add_argument("--skip-disclaimer", action="store_true")
    ap.add_argument(
        "--inarticle-count",
        type=int,
        default=-1,
        help="인-아티클 광고 강제 개수 (기본: H2 분포 기반 자동)",
    )
    ap.add_argument("--force", action="store_true", help="이미 있는 섹션도 추가")
    ap.add_argument("--no-backup", action="store_true", help="변경 전 백업 안 함 (위험)")
    args = ap.parse_args()

    if not args.blog_id:
        print("✗ blog_id 미설정 (--blog-id 또는 .env BLOGGER_STOCKS_BLOG_ID)")
        return 1

    ad_html, has_todo = _load_ad_html()
    if has_todo and not args.skip_ads:
        print(
            "⚠️  광고 HTML 에 TODO_REPLACE_ME 가 있습니다. "
            "AdSense 에서 인-아티클 광고 단위 만들고 slot ID 채우세요 → "
            "assets/ads/inarticle_blogger.html"
        )
        print("   (--skip-ads 로 광고만 비활성화 가능)\n")

    try:
        creds = _get_credentials()
    except Exception as e:
        print(f"✗ Blogger 인증 실패: {e}")
        return 1

    from googleapiclient.discovery import build  # 의존성 이미 있음

    service = build("blogger", "v3", credentials=creds)

    # 단일 글 모드
    if args.post_id:
        post_ids = [args.post_id]
    else:
        # 글 목록 (페이지네이션)
        post_ids = []
        token: str | None = None
        while True:
            kwargs = {"blogId": args.blog_id, "maxResults": 100, "fetchBodies": False}
            if token:
                kwargs["pageToken"] = token
            resp = service.posts().list(**kwargs).execute()
            for item in resp.get("items", []):
                post_ids.append(item["id"])
            token = resp.get("nextPageToken")
            if not token:
                break
        if args.limit > 0:
            post_ids = post_ids[: args.limit]

    print(f"📋 처리 대상: {len(post_ids)} 개 글  (blog_id={args.blog_id}, domain={args.domain})")
    print(f"   mode: {'APPLY (실제 변경)' if args.apply else 'DRY-RUN (변경 안 함)'}")
    print()

    summary = {"processed": 0, "changed": 0, "skipped": 0, "errors": 0}

    for i, pid in enumerate(post_ids, 1):
        print(f"[{i}/{len(post_ids)}] post_id={pid}")
        try:
            post = service.posts().get(blogId=args.blog_id, postId=pid).execute()
        except Exception as e:
            print(f"  ✗ fetch 실패: {e}")
            summary["errors"] += 1
            continue

        try:
            new_html, logs, changed = _process_post(
                post,
                domain=args.domain,
                ad_html=ad_html,
                skip_ads=args.skip_ads,
                skip_sources=args.skip_sources,
                skip_disclaimer=args.skip_disclaimer,
                force=args.force,
                n_ads_override=args.inarticle_count,
            )
        except Exception as e:
            print(f"  ✗ 처리 실패: {e}")
            summary["errors"] += 1
            continue

        for line in logs:
            print(line)

        summary["processed"] += 1
        if not changed:
            print("  → 변경 없음")
            summary["skipped"] += 1
            continue

        summary["changed"] += 1
        added = len(new_html) - len(post.get("content", ""))
        print(f"  → DIFF: +{added:,} chars")

        if not args.apply:
            print("  [dry-run] patch 안 함")
            continue

        if not args.no_backup:
            backup_path = _backup(pid, post.get("content", ""))
            print(f"  💾 백업: {backup_path.relative_to(ROOT)}")

        try:
            service.posts().patch(
                blogId=args.blog_id, postId=pid, body={"content": new_html}
            ).execute()
            print("  ✅ patch 성공")
        except Exception as e:
            print(f"  ✗ patch 실패: {e}")
            summary["errors"] += 1

        # API rate limit 보호
        time.sleep(0.5)

    print()
    print("=" * 50)
    print(
        f"완료: processed={summary['processed']}, "
        f"changed={summary['changed']}, skipped={summary['skipped']}, "
        f"errors={summary['errors']}"
    )
    if not args.apply and summary["changed"] > 0:
        print("\n실제 적용하려면 --apply 추가하세요.")
    return 0 if summary["errors"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
