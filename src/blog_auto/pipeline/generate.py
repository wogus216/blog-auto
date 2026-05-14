"""AI generation pipeline: outline → draft → polish → multi-critic → revise."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from anthropic import Anthropic
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from blog_auto import config
from blog_auto.utils.google_images import (
    GoogleImageResult,
    insert_images_into_markdown,
    search_google_images,
)
from blog_auto.utils.images import (
    ImageResult,
    build_header_markdown,
    search_image,
)


Platform = Literal["tistory", "naver", "blogger"]


@dataclass
class CritiqueReport:
    aspect: str
    issues: list[dict]


@dataclass
class GeneratedPost:
    title: str
    body_md: str
    tags: list[str]
    category: str
    platform: Platform
    critique: list[CritiqueReport] = field(default_factory=list)
    image: ImageResult | None = None


def _load_style(platform: Platform | None = None) -> dict[str, str]:
    style = {
        "voice": (config.STYLE_DIR / "voice.md").read_text(encoding="utf-8"),
        "structure": (config.STYLE_DIR / "structure.md").read_text(encoding="utf-8"),
        "banned": (config.STYLE_DIR / "banned.md").read_text(encoding="utf-8"),
        "platform_context": "",
    }
    if platform:
        ctx_path = config.STYLE_DIR / f"{platform}_context.md"
        if ctx_path.exists():
            style["platform_context"] = ctx_path.read_text(encoding="utf-8")
    return style


def _load_examples(max_count: int = 3) -> list[str]:
    ex_dir = config.STYLE_DIR / "examples"
    if not ex_dir.exists():
        return []
    files = sorted(p for p in ex_dir.glob("good_*.md"))
    return [p.read_text(encoding="utf-8") for p in files[:max_count]]


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(config.PROMPTS_DIR),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )


def _call(client: Anthropic, prompt: str, max_tokens: int = 4096) -> str:
    resp = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in resp.content if block.type == "text").strip()


def _strip_json_fence(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s
        if s.endswith("```"):
            s = s.rsplit("```", 1)[0]
    return s.strip()


CRITIC_ASPECTS: list[dict[str, str]] = [
    {
        "aspect": "voice",
        "instruction": (
            "말투/톤/페르소나가 voice 지침과 일치하는지만 본다. "
            "문장 리듬, 존댓말/반말 일관성, 페르소나 벗어남을 짚어라. "
            "구조나 팩트는 무시."
        ),
        "ref_key": "voice",
    },
    {
        "aspect": "structure",
        "instruction": (
            "글의 구조가 structure 지침과 맞는지만 본다. "
            "훅이 약한지, 섹션 흐름이 끊기는지, 군더더기 섹션이 있는지. "
            "말투는 무시."
        ),
        "ref_key": "structure",
    },
    {
        "aspect": "banned",
        "instruction": (
            "금지 표현이 들어갔는지만 찾는다. "
            "banned.md에 적힌 패턴 또는 그와 유사한 AI 상투구를 모두 찾아라. "
            "다른 관점은 무시."
        ),
        "ref_key": "banned",
    },
]


def _run_critic(
    client: Anthropic,
    env: Environment,
    aspect_spec: dict[str, str],
    draft: str,
    style: dict[str, str],
) -> CritiqueReport:
    prompt = env.get_template("critic.j2").render(
        aspect=aspect_spec["aspect"],
        aspect_instruction=aspect_spec["instruction"],
        reference=style[aspect_spec["ref_key"]],
        draft=draft,
    )
    raw = _call(client, prompt, max_tokens=1500)
    try:
        issues = json.loads(_strip_json_fence(raw))
    except json.JSONDecodeError:
        issues = []
    return CritiqueReport(aspect=aspect_spec["aspect"], issues=issues)


def _run_multi_critic(
    client: Anthropic, env: Environment, draft: str, style: dict[str, str]
) -> list[CritiqueReport]:
    with ThreadPoolExecutor(max_workers=len(CRITIC_ASPECTS)) as pool:
        futures = [
            pool.submit(_run_critic, client, env, spec, draft, style)
            for spec in CRITIC_ASPECTS
        ]
        return [f.result() for f in futures]


def generate(
    topic: str,
    platform: Platform,
    context: str = "",
    *,
    use_critic: bool = True,
) -> GeneratedPost:
    style = _load_style(platform)
    examples = _load_examples()
    env = _env()
    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    merged_context = context
    if style["platform_context"]:
        merged_context = (
            f"[플랫폼 니치 지침]\n{style['platform_context']}\n\n"
            f"[주제 추가 컨텍스트]\n{context or '(없음)'}"
        )

    outline_prompt = env.get_template("outline.j2").render(
        topic=topic,
        platform=platform,
        context=merged_context,
        voice=style["voice"],
        structure=style["structure"],
    )
    outline = json.loads(_strip_json_fence(_call(client, outline_prompt, max_tokens=1500)))

    draft_prompt = env.get_template("draft.j2").render(
        outline=json.dumps(outline, ensure_ascii=False, indent=2),
        platform=platform,
        voice=style["voice"],
        structure=style["structure"],
        banned=style["banned"],
    )
    draft = _call(client, draft_prompt, max_tokens=4096)

    polish_prompt = env.get_template("polish.j2").render(
        draft=draft,
        platform=platform,
        voice=style["voice"],
        banned=style["banned"],
        examples=examples,
    )
    polished = _call(client, polish_prompt, max_tokens=4096)

    critique: list[CritiqueReport] = []
    final = polished

    if use_critic:
        critique = _run_multi_critic(client, env, polished, style)
        all_issues = [i for r in critique for i in r.issues]
        if all_issues:
            revise_prompt = env.get_template("revise.j2").render(
                draft=polished,
                voice=style["voice"],
                banned=style["banned"],
                feedback_json=json.dumps(all_issues, ensure_ascii=False, indent=2),
            )
            final = _call(client, revise_prompt, max_tokens=4096)

    image: ImageResult | None = None
    image_query = (outline.get("image_query") or "").strip()
    if image_query:
        image = search_image(image_query)
    if image:
        final = build_header_markdown(image, alt=outline["title"]) + final

    # Google CSE 본문 이미지 3장 삽입 (API 키 없으면 자동 스킵)
    image_queries = [q for q in (outline.get("image_queries") or []) if isinstance(q, str) and q.strip()][:3]
    if image_queries:
        body_images: list[GoogleImageResult] = []
        for q in image_queries:
            hits = search_google_images(q, n=1)
            if hits:
                body_images.append(hits[0])
        if body_images:
            final = insert_images_into_markdown(final, body_images, alt_prefix=outline.get("title", ""))

    return GeneratedPost(
        title=outline["title"],
        body_md=final,
        tags=outline.get("tags", []),
        category=outline.get("category", ""),
        platform=platform,
        critique=critique,
        image=image,
    )


def save_draft(post: GeneratedPost, out_dir: Path | None = None) -> Path:
    out_dir = out_dir or (config.POSTS_DIR / "_drafts")
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_title = "".join(c if c.isalnum() or c in "-_ " else "_" for c in post.title).strip()[:50]
    path = out_dir / f"{post.platform}__{safe_title}.md"
    fm_lines = [
        "---",
        f"title: {post.title}",
        f"platform: {post.platform}",
        f"category: {post.category}",
        f"tags: {post.tags}",
    ]
    if post.image:
        fm_lines += [
            f"image_url: {post.image.url}",
            f"image_creator: {post.image.creator}",
            f"image_license: {post.image.license_label}",
            f"image_source: {post.image.source_page}",
        ]
    fm_lines += ["---", "", ""]
    frontmatter = "\n".join(fm_lines)
    path.write_text(frontmatter + post.body_md, encoding="utf-8")

    if post.critique:
        report_path = path.with_suffix(".critique.json")
        report_path.write_text(
            json.dumps(
                [{"aspect": r.aspect, "issues": r.issues} for r in post.critique],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    return path
