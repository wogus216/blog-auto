"""발행된 Blogger 글에 broker 이미지 1장을 본문 중간에 삽입 (일회성 보완).

publisher 가 update 를 지원하지 않아, 이미 발행된 글의 이미지 보강은 Blogger API
posts.patch 로 직접 처리한다. 변경 전 백업 + dry-run 기본.

사용:
  uv run python scripts/add_image_to_post.py \
    --blog-id 8176922996371770922 --path /2026/06/2026.html \
    --broker hogangnono_offer --anchor "입지 분석"            # dry-run
  ... --apply                                                  # 실제 patch
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from blog_auto import config  # noqa: E402
from blog_auto.publishers.blogger import _get_credentials  # noqa: E402
from googleapiclient.discovery import build  # noqa: E402

BACKUP_DIR = ROOT / "assets" / "backups" / "blogger"
ASSETS_JSON = ROOT / "assets" / "broker_assets.json"


def img_block(asset: dict) -> str:
    caption = f"{asset['broker']} {asset['topic']}"
    return (
        f'<div style="text-align:center;margin:28px 0;">'
        f'<img src="{asset["raw_url"]}" alt="{caption}" '
        f'style="max-width:100%;height:auto;border-radius:8px;'
        f'box-shadow:0 2px 10px rgba(0,0,0,.08);" />'
        f'<div style="font-size:13px;color:#888;margin-top:6px;">출처: '
        f'<a href="{asset["source_url"]}" target="_blank" rel="noopener">{caption}</a>'
        f'</div></div>'
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--blog-id", required=True)
    ap.add_argument("--path", required=True, help="글 URL 경로 (예: /2026/06/2026.html)")
    ap.add_argument("--broker", required=True, help="broker_assets.json 키")
    ap.add_argument("--anchor", required=True, help="이 텍스트를 포함한 h2 섹션 끝에 삽입")
    ap.add_argument("--apply", action="store_true", help="실제 patch (기본 dry-run)")
    args = ap.parse_args()

    assets = json.loads(ASSETS_JSON.read_text(encoding="utf-8"))
    if args.broker not in assets:
        print(f"[err] broker 키 없음: {args.broker}")
        return
    block = img_block(assets[args.broker])

    creds = _get_credentials()
    service = build("blogger", "v3", credentials=creds)
    post = service.posts().getByPath(blogId=args.blog_id, path=args.path).execute()
    pid = post["id"]
    content = post.get("content", "")
    title = post.get("title", "")
    print(f"글: {title}\n  post_id={pid}  현재 length={len(content)}")

    if args.broker.split("_")[0] in content and assets[args.broker]["raw_url"] in content:
        print("  ⚠️ 이미 해당 이미지가 본문에 있음. 중복 방지 위해 중단.")
        return

    # anchor 를 포함한 <h2> 찾고, 그 다음 <h2> 직전(섹션 끝)에 삽입
    m = re.search(rf'<h2\b[^>]*>[^<]*{re.escape(args.anchor)}[^<]*</h2>', content)
    if not m:
        print(f"  [err] anchor h2 못 찾음: '{args.anchor}'")
        return
    nxt = re.search(r'<h2\b', content[m.end():])
    insert_pos = m.end() + nxt.start() if nxt else len(content)
    new_content = content[:insert_pos] + "\n" + block + "\n" + content[insert_pos:]

    print(f"  삽입 위치: char {insert_pos} (anchor='{args.anchor}' 섹션 끝)")
    print(f"  추가 length=+{len(new_content) - len(content)}")
    ctx = content[insert_pos:insert_pos + 60].replace("\n", " ")
    print(f"  삽입 지점 직후 컨텍스트: ...{ctx}...")

    if not args.apply:
        print("\n[dry-run] --apply 를 붙이면 실제 patch. 백업 후 변경됨.")
        return

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"{pid}_{ts}.html"
    backup.write_text(content, encoding="utf-8")
    print(f"  💾 백업: {backup.relative_to(ROOT)}")

    service.posts().patch(
        blogId=args.blog_id, postId=pid, body={"content": new_content}
    ).execute()
    print("  ✅ patch 완료 (LIVE 반영)")


if __name__ == "__main__":
    main()
