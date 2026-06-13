---
title: 삼성 냉장고 에러코드 총정리 — OF OF·22E·88 냉각·팬·전원 원인과 자가조치
platform: blogger
category: 생활·정보
tags: ['삼성냉장고', '냉장고에러코드', 'OFOF', '냉각안됨', '22E', '88', '냉장고팬', '데모모드', '삼성전자서비스']
date: 2026-06-13
source: 삼성전자서비스 공식(samsungsvc.co.kr) 냉장고 솔루션 + 삼성 냉장고 에러코드 다중 신뢰소스 교차확인
---

삼성 냉장고가 갑자기 **시원하지 않거나 표시창에 'OF OF'·22E·88 같은 코드**가 보이면 고장부터 의심하게 된다. 하지만 의외로 많은 경우가 **'OF OF'(냉각 꺼짐·전시 모드)** 처럼 버튼 조작 한 번으로 풀리는 상태이거나, 팬에 성에가 낀 일시적 문제다. 무턱대고 기사를 부르기 전에 코드의 의미부터 확인하면 출장비를 아낄 수 있다.

이 글은 **삼성전자서비스 공식 안내(samsungsvc.co.kr)** 와 공개 자료를 교차해, 삼성 냉장고에서 자주 보이는 에러코드의 **의미·원인·자가조치·기사 호출 필요 여부**를 정리했다.

<div style="border-left:5px solid #2563eb;background:#eff6ff;padding:16px 20px;margin:20px 0;border-radius:8px;font-size:14px;"><b>📌 가장 먼저 — 'OF OF'부터 확인</b><br>냉장고가 안 시원한데 <b>표시창에 'OF OF'(또는 OFF)</b> 가 보인다면 고장이 아니라 <b>냉각을 끈 전시(데모) 모드</b>일 가능성이 높다. 매장 진열용 기능이 실수로 켜진 경우가 많고, 버튼 조작으로 바로 해제된다(아래 참고). 그 외 팬·센서 코드는 전원 리셋과 해동으로 풀리는 경우가 많다.</div>

{{broker:fridge_header}}

## 냉장고가 안 시원할 때 — 'OF OF'(데모/냉각 꺼짐 모드)

삼성 냉장고에서 **"냉각이 안 된다"는 신고의 흔한 원인 중 하나가 'OF OF' 모드**다. 이는 매장 전시용으로 **냉각을 끄고 조명·디스플레이만 켜두는 기능**인데, 청소·정전·아이 장난 등으로 실수로 켜지는 경우가 있다.

- **해제 방법**: 제어판의 특정 버튼 두 개(모델별로 '냉장'+'냉동' 또는 '절전'+'동결' 등)를 **5~8초간 동시에 길게** 눌러 신호음이 나면 해제된다. 정확한 버튼 조합은 모델 설명서에 표기돼 있다.
- 해제 후에는 정상 냉각까지 몇 시간이 걸릴 수 있다.

:::stat 냉장고 안 시원할 때
OF OF | 데모모드 = 버튼으로 해제
22E·21E | 팬 결빙 = 해동 후 재시작
88 | 전원 = 1분 리셋
:::

> 📌 'OF OF'를 해제했는데도 냉각이 안 되거나, 표시가 다시 'OF OF'로 돌아간다면 그때는 서비스 점검이 필요하다.

## 자주 뜨는 삼성 냉장고 에러코드 요약표

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">자가조치</th><th style="padding:9px;text-align:center;">기사필요</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">OF OF</td><td style="padding:8px;">냉각 꺼짐·전시(데모) 모드 — 고장 아님</td><td style="padding:8px;">제어판 버튼 2개 5~8초 길게 눌러 해제</td><td style="padding:8px;text-align:center;">불필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">88 (88 88)</td><td style="padding:8px;">전원·전압 오류 — 정전·전압 변동·통신</td><td style="padding:8px;">차단기/플러그 1분 분리 후 재연결</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">22E (22C)</td><td style="padding:8px;">냉장실 팬 오류 — 성에·이물질로 팬 정지</td><td style="padding:8px;">플러그 빼고 문 열어 수 시간 해동 후 재시작</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">21E</td><td style="padding:8px;">냉동실 팬 오류 — 팬 결빙·문 열림</td><td style="padding:8px;">해동 후 재시작 + 문 완전히 닫기</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">40E (40C)</td><td style="padding:8px;">제빙실 팬 오류 (얼음 제조부)</td><td style="padding:8px;">해동 후 재시작</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">5E</td><td style="padding:8px;">냉장실 제상센서 오류</td><td style="padding:8px;color:#dc2626;font-weight:600;">전원 리셋 후 재발 시 점검</td><td style="padding:8px;text-align:center;font-weight:700;color:#dc2626;">○ 필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">14E</td><td style="padding:8px;">얼음 제조기 센서 오류</td><td style="padding:8px;color:#dc2626;font-weight:600;">재발 시 점검</td><td style="padding:8px;text-align:center;font-weight:700;color:#dc2626;">○ 필요</td></tr></tbody></table>

> 📌 삼성 냉장고도 **숫자+E(구형)와 숫자+C(신형)** 가 같은 의미로 병용된다(22E = 22C). 표기만 다를 뿐 원인은 같다.

## 팬 오류(22E·21E·40E) — 해동이 먼저

{{broker:fridge_inside}}

냉장고 팬 오류의 가장 흔한 원인은 **팬 날개에 성에가 끼어 회전이 막히는 것**이다. 문을 자주 여닫거나 문이 살짝 열려 있었거나, 뜨거운 음식을 바로 넣으면 내부에 습기가 차 성에가 생긴다.

1. 냉장고 **전원(플러그)을 뽑는다.**
2. **문을 열어둔 채 몇 시간**(가능하면 반나절) 두어 성에를 자연 해동시킨다. 바닥에 수건을 깔아 녹은 물을 받는다.
3. 내부 물기를 닦고 전원을 다시 연결한다.
4. 그래도 같은 코드가 반복되면 팬 모터·센서 문제일 수 있어 점검이 필요하다.

> ⚠️ 성에 해동 시 **드라이어·뜨거운 물로 무리하게 녹이지 않는다.** 부품 손상·변형의 원인이 된다. 자연 해동이 가장 안전하다.

## 전원 코드(88)와 시작 시 깜빡임

- **88 / 88 88**: 정전·전압 변동·순간 통신 오류로 표시된다. 차단기나 플러그를 **1분간 분리**했다 다시 연결하면 대부분 해소된다.
- **정전 후 모든 아이콘이 깜빡임**: 이는 고장이 아니라 **정상적인 시작(자가진단) 과정**이다. 잠시 기다리면 정상 표시로 돌아온다.

## 해결이 안 될 때: 삼성전자서비스

자가조치로 풀리지 않거나 센서 계열 코드가 반복된다면 공식 채널을 이용한다.

- **대표 전화**: **1588-3366** (운영시간은 변동될 수 있음)
- **출장 서비스 예약·AI 챗봇**: 삼성전자서비스(samsungsvc.co.kr)
- 접수 전 **제품 모델명**(냉장실 안쪽 벽면 라벨)과 **표시된 코드**를 메모해두면 상담이 빨라진다.

## 자주 묻는 질문 (FAQ)

**Q. 냉장고가 안 시원한데 'OF OF'가 떠 있어요.**
A. 'OF OF'는 고장이 아니라 냉각을 끈 **전시(데모) 모드**다. 제어판의 버튼 두 개를 5~8초간 길게 눌러 해제하면 된다. 정확한 버튼 조합은 모델 설명서를 확인하자. 해제 후 정상 온도까지는 몇 시간 걸린다.

**Q. 22E가 떴어요. 바로 기사를 불러야 하나요?**
A. 22E(냉장실 팬)는 성에로 팬이 멈춘 경우가 많다. 먼저 플러그를 뽑고 문을 열어 몇 시간 해동한 뒤 재시작해 본다. 그래도 반복되면 팬 모터·센서 점검이 필요하다.

**Q. 88은 무슨 뜻인가요?**
A. 전원·전압 관련 오류다. 차단기나 플러그를 1분간 분리했다 다시 연결하면 대부분 사라진다. 반복되면 전원 환경(멀티탭 등)을 점검한다.

**Q. 정전 후 숫자·아이콘이 다 깜빡여요.**
A. 정전 복구 시 나타나는 정상적인 시작 과정이다. 잠시 기다리면 정상 표시로 돌아온다. 계속된다면 전원 리셋을 시도한다.

**Q. 22E와 22C는 다른가요?**
A. 같다. 구형은 숫자+E(22E), 신형은 숫자+C(22C)로 표기만 다르고 의미(냉장실 팬)는 동일하다.

## 정리: 안 시원하면 'OF OF'부터, 팬 코드는 해동부터

삼성 냉장고가 안 시원할 때는 **먼저 'OF OF'(전시 모드)인지 확인**하고, 팬 오류(22E·21E·40E)는 **성에 해동 후 재시작**, 전원 코드(88)는 **1분 리셋**으로 대부분 해결된다. 다만 제상센서(5E)·제빙 센서(14E) 같은 센서 코드가 반복되면 무리하게 쓰지 말고 점검을 받는 것이 안전하다.

> ⚠️ 본 글의 코드·조치는 삼성전자서비스 공식 안내와 공개 자료를 교차한 것(작성 시점 2026년 6월)이며, 모델·연식에 따라 다를 수 있다. 정확한 진단은 제품 모델명·표시 코드를 [삼성전자서비스](https://www.samsungsvc.co.kr/) 또는 1588-3366으로 확인하기 바란다.

## 함께 보면 좋은 글

- [삼성 세탁기 에러코드 총정리 (4C·5C·UE)](https://consistency.onestepblog.info/2026/06/4c5cue.html)
- [삼성 에어컨 에러코드 완벽 가이드 (E101·E461)](https://consistency.onestepblog.info/2026/06/e101e461-100200400.html)
- [LG 냉장고 에러코드 총정리 (원인과 해결책)](https://sancho216.tistory.com/entry/LG-냉장고에러코드-유형1F-FF-rF-CF-CO-FS-r5-d5-H5-55-rt-lt-9F-dH-Od-CH-CL-ld-UC-5d-CI-95-dr-IL-AS-Ad-P5-OFF-원인-과-해결책을-알아보자)
