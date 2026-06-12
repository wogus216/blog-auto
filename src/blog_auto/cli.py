from __future__ import annotations

from typing import Literal

import typer
from rich import print

from blog_auto import config
from blog_auto.pipeline.generate import generate, save_draft
from blog_auto.publishers.blogger import BloggerPublisher
from blog_auto.publishers.naver import NaverPublisher
from blog_auto.publishers.session import save_session
from blog_auto.publishers.tistory import TistoryPublisher
from blog_auto.publishers.base import PublishRequest
from blog_auto.utils.broker_assets import inject_broker_assets
from blog_auto.utils.viz_cards import inject_viz_cards, strip_viz_cards, theme_for_platform

app = typer.Typer(help="AI blog automation (Tistory + Naver + Blogger + Blogger Stocks)")


Platform = Literal["tistory", "naver", "blogger", "blogger_stocks", "blogger_money"]
_ALL_PLATFORMS: list[Platform] = ["tistory", "naver", "blogger", "blogger_stocks", "blogger_money"]
_PLAYWRIGHT_PLATFORMS = {"tistory", "naver"}


@app.command()
def login(platform: str = typer.Argument(..., help="tistory | naver | both")):
    """브라우저를 열어 수동 로그인 후 세션 저장. (tistory/naver 전용)"""
    targets = ["tistory", "naver"] if platform == "both" else [platform]
    for t in targets:
        if t not in _PLAYWRIGHT_PLATFORMS:
            print(f"[yellow]{t} 는 OAuth2 인증 사용. generate-post 또는 publish 실행 시 자동 안내됩니다.[/]")
            continue
        save_session(t)  # type: ignore[arg-type]


@app.command()
def generate_post(
    topic: str = typer.Argument(..., help="글 주제"),
    platform: str = typer.Option("tistory", help="tistory | naver | blogger | blogger_stocks | all"),
    context: str = typer.Option("", help="추가 컨텍스트/배경"),
    no_critic: bool = typer.Option(False, help="크리틱/리바이즈 단계 스킵 (빠름/저렴)"),
    cpc: bool = typer.Option(False, "--cpc", help="CPC 고단가 모드 (style/cpc_strategy.md + 플랫폼 CPC 친화 주제풀 적용)"),
):
    """주제를 받아 파이프라인으로 초안 생성 (posts/_drafts/ 저장)."""
    targets: list[Platform] = _ALL_PLATFORMS if platform == "all" else [platform]  # type: ignore[list-item]
    for p in targets:
        mode_tag = " [CPC]" if cpc else ""
        print(f"[bold cyan]>>> generating for {p}{mode_tag}[/]")
        post = generate(topic=topic, platform=p, context=context, use_critic=not no_critic, cpc_mode=cpc)
        path = save_draft(post)
        print(f"  saved: {path}")
        if post.critique:
            total = sum(len(r.issues) for r in post.critique)
            print(f"  critique issues: {total} (report: {path.with_suffix('.critique.json').name})")


@app.command()
def publish(
    draft_path: str = typer.Argument(..., help="posts/_drafts/ 안의 .md 파일"),
    mode: str = typer.Option(config.PUBLISH_MODE, help="draft | publish | schedule"),
    at: str = typer.Option("", help="schedule 모드 전용. RFC3339 시간 (예: 2026-05-06T08:00:00+09:00)"),
):
    """초안 마크다운을 해당 플랫폼에 업로드."""
    from pathlib import Path
    import re

    text = Path(draft_path).read_text(encoding="utf-8")
    fm_match = re.match(r"^---\n(.*?)\n---\n\n(.*)$", text, re.DOTALL)
    if not fm_match:
        raise typer.BadParameter("frontmatter 없음. generate-post로 만든 파일을 넣어주세요.")
    fm_raw, body = fm_match.groups()
    meta: dict[str, str] = {}
    for line in fm_raw.splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()

    tags = [t.strip().strip("'\"") for t in meta.get("tags", "[]").strip("[]").split(",") if t.strip()]

    body = inject_broker_assets(body)
    platform_name = meta.get("platform", "tistory")
    # 데이터 시각화 카드 토큰 → HTML (네이버는 HTML 표 불가라 텍스트 폴백)
    # 테마는 플랫폼별 자동 선택: money·stocks=refined(차분), 티스토리·consistency=vivid(생기)
    body = (
        strip_viz_cards(body)
        if platform_name == "naver"
        else inject_viz_cards(body, theme=theme_for_platform(platform_name))
    )

    if mode == "schedule" and not at:
        raise typer.BadParameter("schedule 모드는 --at RFC3339 시간 필요. 예: --at 2026-05-06T08:00:00+09:00")

    title = meta.get("title", "(제목 없음)").strip().strip('"').strip("'")
    req = PublishRequest(
        title=title,
        body_md=body,
        tags=tags,
        category=meta.get("category", ""),
        mode=mode,  # type: ignore[arg-type]
        schedule_at=at or None,
        cta_url=meta.get("cta_url") or None,
        cta_text=meta.get("cta_text") or None,
    )

    if platform_name == "blogger":
        pub = BloggerPublisher()
    elif platform_name == "blogger_stocks":
        pub = BloggerPublisher(blog_id=config.BLOGGER_STOCKS_BLOG_ID, platform="blogger_stocks")
    elif platform_name == "blogger_money":
        pub = BloggerPublisher(blog_id=config.BLOGGER_MONEY_BLOG_ID, platform="blogger_money")
    elif platform_name == "naver":
        pub = NaverPublisher()
    else:
        pub = TistoryPublisher()
    result = pub.publish(req)
    print(result)


@app.command()
def update_naver(
    draft_path: str = typer.Argument(..., help="posts/_drafts/ 의 .md (replace=전체 글, append=추가할 내용만)"),
    log_no: str = typer.Option(..., "--log-no", help="네이버 글 logNo (URL 끝 숫자)"),
    content_mode: str = typer.Option("append", help="append(본문 끝 추가) | replace(전체 교체)"),
    update_title: bool = typer.Option(False, help="제목도 frontmatter title 로 교체"),
):
    """네이버 발행글 본문 수정. append=추가할 내용만 든 .md, replace=전체 글 .md."""
    from pathlib import Path
    import re

    text = Path(draft_path).read_text(encoding="utf-8")
    fm_match = re.match(r"^---\n(.*?)\n---\n\n(.*)$", text, re.DOTALL)
    if not fm_match:
        raise typer.BadParameter("frontmatter 없음. (--- ... --- 형식 필요)")
    fm_raw, body = fm_match.groups()
    meta: dict[str, str] = {}
    for line in fm_raw.splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()

    tags = [t.strip().strip("'\"") for t in meta.get("tags", "[]").strip("[]").split(",") if t.strip()]
    body = inject_broker_assets(body)
    body = strip_viz_cards(body)  # 네이버 — 카드는 텍스트 폴백
    title = meta.get("title", "").strip().strip('"').strip("'")

    if meta.get("platform") != "naver":
        print(f"[yellow]경고: platform={meta.get('platform')} (naver 아님). 그래도 진행합니다.[/]")

    req = PublishRequest(
        title=title, body_md=body, tags=tags, category=meta.get("category", ""), mode="publish"
    )
    result = NaverPublisher().update(
        req, log_no, content_mode=content_mode, update_title=update_title
    )
    print(result)


@app.command()
def update_tistory(
    draft_path: str = typer.Argument(..., help="posts/_drafts/ 의 .md (전체 글)"),
    post_id: str = typer.Option(..., "--post-id", help="티스토리 글 번호 (글 HTML의 entryId / RSS로 확인)"),
):
    """티스토리 발행글 본문 전체 수정(덮어쓰기 후 재발행). {{broker:키}} 토큰도 자동 치환."""
    from pathlib import Path
    import re

    text = Path(draft_path).read_text(encoding="utf-8")
    fm_match = re.match(r"^---\n(.*?)\n---\n\n(.*)$", text, re.DOTALL)
    if not fm_match:
        raise typer.BadParameter("frontmatter 없음. (--- ... --- 형식 필요)")
    fm_raw, body = fm_match.groups()
    meta: dict[str, str] = {}
    for line in fm_raw.splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()

    tags = [t.strip().strip("'\"") for t in meta.get("tags", "[]").strip("[]").split(",") if t.strip()]
    body = inject_broker_assets(body)
    body = inject_viz_cards(body, theme="vivid")  # 티스토리 — 카드 토큰 → HTML(생기 테마)
    title = meta.get("title", "").strip().strip('"').strip("'")

    if meta.get("platform") != "tistory":
        print(f"[yellow]경고: platform={meta.get('platform')} (tistory 아님). 그래도 진행합니다.[/]")

    req = PublishRequest(
        title=title, body_md=body, tags=tags, category=meta.get("category", ""),
        mode="publish", cta_url=meta.get("cta_url") or None, cta_text=meta.get("cta_text") or None,
    )
    result = TistoryPublisher().update_post(post_id, req)
    print(result)


if __name__ == "__main__":
    app()
