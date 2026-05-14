"""세 플랫폼 공개 발행 테스트. platform 변수를 바꿔가며 실행."""
import sys

platform = sys.argv[1] if len(sys.argv) > 1 else "blogger"
mode = sys.argv[2] if len(sys.argv) > 2 else "publish"  # publish | draft | semi

from blog_auto.publishers.base import PublishRequest

req = PublishRequest(
    title="[자동화 테스트] 발행 확인용 글",
    body_md=(
        "## 자동화 테스트\n\n"
        "이 글은 블로그 자동화 파이프라인 발행 테스트용입니다.\n\n"
        "- 항목 1\n"
        "- 항목 2\n\n"
        "확인 후 삭제하세요."
    ),
    tags=["테스트", "자동화"],
    category="",
    mode=mode,  # type: ignore[arg-type]
)

if platform == "blogger":
    from blog_auto.publishers.blogger import BloggerPublisher
    pub = BloggerPublisher()
elif platform == "tistory":
    from blog_auto.publishers.tistory import TistoryPublisher
    pub = TistoryPublisher()
elif platform == "naver":
    from blog_auto.publishers.naver import NaverPublisher
    pub = NaverPublisher()
else:
    print(f"알 수 없는 플랫폼: {platform}")
    sys.exit(1)

print(f"[{platform}] 발행 중...")
result = pub.publish(req)
print("ok:", result.ok)
print("note:", result.note)
print("url:", result.url)
