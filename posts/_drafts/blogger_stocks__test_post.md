---
title: [테스트] 미국주식 블로그 발행 점검
platform: blogger_stocks
category: US Stocks / Macro & Fed
tags: ['테스트', '미국주식', 'NVDA', 'QQQ']
---

이 글은 새로 추가한 **Blogger Stocks** 채널(미국주식 전문)의 발행 라우팅을 점검하기 위한 테스트 포스트입니다.

## 점검 포인트

- `platform: blogger_stocks` frontmatter가 `BloggerPublisher(blog_id=BLOGGER_STOCKS_BLOG_ID)`로 올바르게 라우팅되는지
- 새 blog ID(`2799842341670074025`)로 draft가 들어가는지
- OAuth 토큰이 기존 Blogger와 공유되어 추가 인증 없이 발행되는지

## 다음 단계

확인되면 본 포스트는 Blogger 관리자에서 삭제하고,
실제 미국주식 콘텐츠(엔비디아 실적, FOMC 해설, QQQ 플로우 등)를 생성하기 시작합니다.

> 이 글은 정보 제공 목적이며, 투자 판단은 본인 책임입니다.
