from blog_auto.publishers.naver import NaverPublisher
from blog_auto.publishers.base import PublishRequest

req = PublishRequest(
    title="[테스트] 자동화 임시저장 확인",
    body_md="## 테스트\n\n자동화 파이프라인 테스트입니다.\n\n- 항목 1\n- 항목 2\n",
    tags=["테스트", "자동화"],
    category="",
    mode="draft",
)

pub = NaverPublisher()
result = pub.publish(req)
print("ok:", result.ok)
print("note:", result.note)
