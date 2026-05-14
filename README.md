# blog-auto

티스토리 + 네이버 블로그 자동화. Anthropic Claude로 글을 생성하고, Playwright로 발행한다.

## 셋업

```bash
uv venv && source .venv/bin/activate     # 또는 python -m venv .venv
uv pip install -e ".[dev]"                # 또는 pip install -e ".[dev]"
playwright install chromium
cp .env.example .env                      # 값 채우기
```

## 사용

```bash
# 1회: 수동 로그인 (각 블로그 1회씩. 2FA/캡차 이후 Enter)
blog-auto login both

# 초안 생성
blog-auto generate-post "SSR 깊게 보기" --platform both

# 확인 후 발행 (draft=임시저장, publish=게시)
blog-auto publish posts/_drafts/tistory__SSR_깊게_보기.md --mode draft
```

## 스타일 튜닝

- `style/voice.md` — 말투/페르소나
- `style/structure.md` — 글 구조
- `style/banned.md` — 금지 표현
- `style/examples/good_*.md` — few-shot 샘플 (2~3개 이상 권장)

내가 쓴 실제 글을 `style/examples/`에 넣을수록 톤이 안정된다.

## 주의

- `sessions/*.json` 에는 로그인 쿠키가 저장된다. git에 커밋 금지 (`.gitignore` 처리됨).
- 하루 2~3개 이상 자동 발행은 차단 위험 증가. 스케줄링 시 `MIN_DELAY_SECONDS` / `MAX_DELAY_SECONDS` 조정.
- publisher의 DOM 셀렉터는 플랫폼 UI 변경 시 업데이트 필요.
