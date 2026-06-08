"""원클릭 파이프라인 — 토픽 한 줄 → 생성→광고→GEO→(발행)까지.

Claude Code(대화) 없이 글 생성+발행을 자동화한다. 글 생성은 generate-post
(Anthropic API, .env의 ANTHROPIC_API_KEY 사용) → 이후 후처리·발행은 기존 스크립트.

흐름:
  1) generate()        토픽→초안(outline→draft→비평→수정), posts/_drafts/ 저장
  2) platform 보정     generate가 모르는 플랫폼(blogger_money 등)은 frontmatter 강제
  3) inject_ads        인-아티클+멀티플렉스 광고 분산 (--no-ads 로 생략)
  4) inject_jsonld     --research <slug> 있으면 JSON-LD/참고자료/면책 (없으면 스킵)
  5) publish           --publish 일 때만 발행 (기본은 draft 저장까지)

사용:
  # 초안까지(안전, 기본) — 검토 후 따로 발행
  uv run python scripts/oneclick_pipeline.py "주제" --platform blogger_stocks --context "핵심 사실들"
  # 발행까지 한 방에
  uv run python scripts/oneclick_pipeline.py "주제" --platform blogger --publish
  # research JSON까지 엮어 GEO 강화 + 발행
  uv run python scripts/oneclick_pipeline.py "주제" --platform blogger_money --research my_slug --publish

옵션:
  --platform   tistory|naver|blogger|blogger_stocks|blogger_money|all
  --context    추가 배경/핵심 사실(이게 충실할수록 품질↑)
  --research   assets/research/<slug>.json 슬러그 (JSON-LD·면책 주입)
  --publish    발행까지(기본: draft 저장만)
  --cpc        CPC 고단가 모드
  --no-critic  비평·수정 단계 생략(빠름/저렴, 품질↓)
  --no-ads     광고 주입 생략
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from blog_auto.pipeline.generate import generate, save_draft  # noqa: E402

# generate.py가 정식 지원하는 플랫폼(Literal). 그 외(blogger_money)는 사후 보정.
GEN_PLATFORMS = {"tistory", "naver", "blogger", "blogger_stocks"}


def run(*cmd: str) -> bool:
    print("   $ " + " ".join(str(c) for c in cmd))
    return subprocess.run(cmd, cwd=str(ROOT)).returncode == 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("topic", help="글 주제")
    ap.add_argument("--platform", default="blogger_stocks")
    ap.add_argument("--context", default="")
    ap.add_argument("--research", default="")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--cpc", action="store_true")
    ap.add_argument("--no-critic", action="store_true")
    ap.add_argument("--no-ads", action="store_true")
    a = ap.parse_args()

    # generate에 넘길 플랫폼: 미지원(blogger_money 등)은 blogger로 생성 후 보정
    gen_platform = a.platform if a.platform in GEN_PLATFORMS else "blogger"

    print(f"[1/5] 글 생성 (요청 platform={a.platform}, 생성기준={gen_platform})...")
    post = generate(
        topic=a.topic, platform=gen_platform, context=a.context,
        use_critic=not a.no_critic, cpc_mode=a.cpc,
    )
    path = save_draft(post)
    print(f"   ✅ 초안: {path}")
    if post.critique:
        n = sum(len(r.issues) for r in post.critique)
        print(f"   비평 이슈 {n}건 (검토 권장)")

    # [2/5] platform 보정 — 요청 플랫폼이 생성기준과 다르면 frontmatter 강제 교체
    if a.platform != gen_platform:
        text = path.read_text(encoding="utf-8")
        text2 = re.sub(r"^platform:.*$", f"platform: {a.platform}",
                       text, count=1, flags=re.M)
        path.write_text(text2, encoding="utf-8")
        print(f"[2/5] platform 보정: {gen_platform} → {a.platform}")
    else:
        print(f"[2/5] platform 보정 불필요 ({a.platform})")

    # [3/5] 광고
    if a.no_ads:
        print("[3/5] 광고 스킵(--no-ads)")
    else:
        print("[3/5] 광고 분산...")
        run("uv", "run", "python", "scripts/inject_ads.py", str(path), "--multiplex")

    # [4/5] GEO/참고자료/면책
    if a.research:
        rjson = ROOT / "assets" / "research" / f"{a.research}.json"
        if not rjson.exists():
            print(f"[4/5] ⚠️ research 파일 없음: {rjson} → JSON-LD 스킵")
        else:
            print(f"[4/5] GEO·참고자료·면책 (research={a.research})...")
            run("uv", "run", "python", "scripts/inject_jsonld.py", str(path),
                "--research", a.research)
    else:
        print("[4/5] research 미지정 → JSON-LD 스킵 (정형글은 --research 권장)")

    # [5/5] 발행
    if a.publish:
        print(f"[5/5] 발행 (platform={a.platform})...")
        ok = run("uv", "run", "blog-auto", "publish", str(path), "--mode", "publish")
        print("   ✅ 발행 요청 완료" if ok else "   ✗ 발행 실패(로그 확인)")
        if a.platform == "tistory":
            print("   ※ 티스토리는 브라우저에서 카카오 로그인 필요할 수 있음")
    else:
        print("[5/5] draft 저장까지 완료. 검토 후 발행:")
        print(f"   uv run blog-auto publish {path} --mode publish")

    print(f"\n파이프라인 종료 → {path}")
    print("⚠️ YMYL(투자·부동산)·시의성 글은 발행 전 사실·면책 검토 권장.")


if __name__ == "__main__":
    main()
