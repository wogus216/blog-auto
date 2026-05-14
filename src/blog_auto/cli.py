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

app = typer.Typer(help="AI blog automation (Tistory + Naver + Blogger)")


Platform = Literal["tistory", "naver", "blogger"]
_ALL_PLATFORMS: list[Platform] = ["tistory", "naver", "blogger"]
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
    platform: str = typer.Option("tistory", help="tistory | naver | blogger | all"),
    context: str = typer.Option("", help="추가 컨텍스트/배경"),
    no_critic: bool = typer.Option(False, help="크리틱/리바이즈 단계 스킵 (빠름/저렴)"),
):
    """주제를 받아 파이프라인으로 초안 생성 (posts/_drafts/ 저장)."""
    targets: list[Platform] = _ALL_PLATFORMS if platform == "all" else [platform]  # type: ignore[list-item]
    for p in targets:
        print(f"[bold cyan]>>> generating for {p}[/]")
        post = generate(topic=topic, platform=p, context=context, use_critic=not no_critic)
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

    if mode == "schedule" and not at:
        raise typer.BadParameter("schedule 모드는 --at RFC3339 시간 필요. 예: --at 2026-05-06T08:00:00+09:00")

    req = PublishRequest(
        title=meta.get("title", "(제목 없음)"),
        body_md=body,
        tags=tags,
        category=meta.get("category", ""),
        mode=mode,  # type: ignore[arg-type]
        schedule_at=at or None,
        cta_url=meta.get("cta_url") or None,
        cta_text=meta.get("cta_text") or None,
    )

    platform_name = meta.get("platform", "tistory")
    if platform_name == "blogger":
        pub = BloggerPublisher()
    elif platform_name == "naver":
        pub = NaverPublisher()
    else:
        pub = TistoryPublisher()
    result = pub.publish(req)
    print(result)


if __name__ == "__main__":
    app()
