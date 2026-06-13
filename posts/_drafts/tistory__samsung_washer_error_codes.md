---
title: 삼성 세탁기 에러코드! 4C·5C·UE 급수·배수·탈수 자가진단 (드럼·통돌이)
platform: tistory
category: 에러해결
tags: ['삼성세탁기', '세탁기에러코드', '4C', '5C', 'UE', '드럼세탁기', '세탁기배수', '삼성전자서비스']
date: 2026-06-13
source: 삼성전자서비스 공식(samsungsvc.co.kr) 4C/4E 점검코드 + 삼성 드럼세탁기 에러코드 다중 신뢰소스 교차확인
---

삼성 세탁기를 돌리는데 갑자기 멈추면서 **4C·5C·UE 코드**가 떴다면 — 너무 걱정 마세요. 가장 흔한 **4C(급수)·5C(배수)·UE(탈수 불균형)** 는 대부분 수도꼭지·배수필터·세탁물 배치만 확인하면 **집에서 바로 해결**돼요. 모르고 기사를 부르면 출장비만 나갈 수 있죠.

이 글은 **삼성전자서비스 공식 점검코드(samsungsvc.co.kr)** 기준으로, 삼성 세탁기에서 자주 뜨는 코드를 **집에서 직접 확인하는 법**으로 정리했어요. 드럼·통돌이(전자동) 다 포함합니다.

<div style="border-left:5px solid #2563eb;background:#eff6ff;padding:16px 20px;margin:20px 0;border-radius:8px;font-size:14px;"><b>📌 먼저 알아두세요</b><br>삼성 세탁기 코드는 <b>2015년 이전은 숫자+E(4E), 이후는 숫자+C(4C)</b> 로 표기만 다르고 의미는 같아요(4E = 4C). 급수·배수·탈수는 자가조치로 풀리지만, <b>누수(LC)·센서·통신·히터 계열은 전문 기사</b>가 필요해요.</div>

{{broker:washer_header}}

## 🚨 코드 보기 전, 기본 점검 3단계

특정 코드 보기 전에, 아래 기본 점검만으로 급수·배수·일시 오류 대부분이 풀려요.

1. **전원 리셋** — 전원 끄고 차단기/플러그를 1분 분리했다 다시 연결해요. 일시적 통신·센서 오류가 초기화돼요.
2. **수도·급수 확인** — 수도꼭지가 끝까지 열렸는지, 급수호스가 꺾이지 않았는지 봐요(4C 대비).
3. **배수필터 청소** — 세탁기 하단 배수필터를 열어 동전·머리카락·이물질을 제거해요(5C 대비). 물이 남아 있을 수 있으니 수건을 받쳐요.

:::stat 세탁기, 이것부터
4C·5C | 급수·배수 = 가장 흔함
UE | 탈수 시 세탁물 펴기
1분 | 전원 껐다 켜기
:::

> 📌 위 점검 후에도 같은 코드가 반복되면, 아래 표를 보고 기사 호출을 판단하세요.

## 📋 삼성 세탁기 자주 뜨는 에러코드 한눈에

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">자가조치</th><th style="padding:9px;text-align:center;">기사필요</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">4C (4E)</td><td style="padding:8px;">급수 불량 — 물이 안 나오거나 적게 들어옴</td><td style="padding:8px;">수도꼭지 개방·급수호스 꺾임·급수필터 청소</td><td style="padding:8px;text-align:center;">대개 불필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">5C (5E)</td><td style="padding:8px;">배수 불량 — 정해진 시간 안에 배수 안 됨</td><td style="padding:8px;">배수필터·배수호스 막힘 청소</td><td style="padding:8px;text-align:center;">대개 불필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">UE (Ub)</td><td style="padding:8px;">탈수 불균형 — 세탁물 한쪽 쏠림·수평 불량</td><td style="padding:8px;">세탁물 양 조절·골고루 펴기·수평 확인</td><td style="padding:8px;text-align:center;">불필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">dC (dE)</td><td style="padding:8px;">도어 열림·잠금 불량</td><td style="padding:8px;">도어를 완전히 닫고 재동작</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">3C (3E)</td><td style="padding:8px;">모터 과부하 — 세탁물 과다·무거움</td><td style="padding:8px;">세탁물 줄이고 재동작</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">Sud</td><td style="padding:8px;">거품 과다 (에러 아님) — 세제 과다 투입</td><td style="padding:8px;">거품 제거 동작 대기·세제량 줄이기</td><td style="padding:8px;text-align:center;">불필요</td></tr></tbody></table>

> 📌 **4C·5C·UE**가 세탁기 코드의 대부분이에요. 급수(수도)·배수(필터)·탈수(세탁물 배치)만 점검해도 상당수가 풀려요.

## 💧 급수·배수 — 4C·5C (가장 흔함)

{{broker:washer_drum}}

- **4C(급수)**: 수도꼭지가 끝까지 열렸는지, 급수호스가 꺾이거나 눌리지 않았는지 봐요. 호스 연결부의 **급수필터(거름망)** 에 이물질이 끼면 물이 적게 들어와 4C가 떠요. 호스를 분리해 거름망을 칫솔로 청소하세요. 겨울엔 호스 동결도 원인이에요.
- **5C(배수)**: 세탁기 하단 **배수필터**를 열어 동전·머리카락을 제거해요. 배수호스가 꺾였거나 너무 높이 올라가 있어도 안 빠져요. 호스 끝이 바닥 배수구에 제대로 들어가 있는지 확인하세요.

## 🌀 탈수·도어 — UE·dC

- **UE(Ub) 탈수 불균형**: 이불·수건처럼 무거운 빨래가 한쪽으로 쏠리면 탈수 시 통이 흔들려 보호로 멈춰요. 세탁물을 펴고 양을 조절하고, 세탁기 **수평**(다리 높이)을 맞춰요.
- **dC(도어)**: 문이 덜 닫혔거나 잠금 센서 문제예요. 문틈에 빨래가 끼지 않았는지 보고 '딸깍' 소리 나게 닫아요.

## 🔧 기사 점검이 필요한 코드

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">조치</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">LC (LE)</td><td style="padding:8px;">누수 감지 — 누수 또는 회로기판 이상</td><td style="padding:8px;color:#dc2626;font-weight:600;">급수 잠그고 서비스 점검</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">OC (OE)</td><td style="padding:8px;">과수위 — 물이 넘침</td><td style="padding:8px;color:#dc2626;font-weight:600;">급수밸브 잠금 후 서비스 신청</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">1C</td><td style="padding:8px;">수위센서 이상 — 물높이 감지 오류</td><td style="padding:8px;color:#dc2626;font-weight:600;">전원 리셋 후 재발 시 점검</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">8C</td><td style="padding:8px;">진동감지 센서↔PCB 통신 불량</td><td style="padding:8px;color:#dc2626;font-weight:600;">서비스 점검</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">AC (AE)</td><td style="padding:8px;">회로기판 간 통신 이상</td><td style="padding:8px;color:#dc2626;font-weight:600;">전원 리셋 후 재발 시 점검</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">HC (HE)</td><td style="padding:8px;">히터 이상 (세탁·건조 가열)</td><td style="padding:8px;color:#dc2626;font-weight:600;">서비스 점검</td></tr></tbody></table>

> ⚠️ **LC·OC**처럼 누수·과수위 코드가 뜨면 우선 **수도(급수밸브)를 잠가** 추가 누수를 막은 뒤 서비스를 신청하세요.

## ☎️ 삼성전자서비스 문의

자가조치로 안 되거나 센서·누수 코드가 반복되면 공식 채널을 이용하세요.

- **대표 전화**: **1588-3366** (운영시간 변동될 수 있음)
- **출장 예약·AI 챗봇**: samsungsvc.co.kr
- 문의 전 **모델명**(도어 안쪽·뒷면 라벨)과 **뜬 코드**를 메모해두면 빨라요.

## 🔍 [FAQ] 자주 묻는 질문

**Q. 4C가 떴는데 수도는 잘 나와요.**
A. 수도가 정상이면 급수호스 연결부의 **급수필터(거름망)** 막힘일 가능성이 커요. 호스를 분리해 거름망을 칫솔로 청소하면 대부분 풀려요. 겨울엔 호스 동결도 확인하세요.

**Q. 5C(배수)는 어떻게 해결해요?**
A. 세탁기 하단 배수필터를 열어 이물질을 제거하고, 배수호스가 꺾이거나 너무 높이 올라가 있지 않은지 확인해요. 필터 청소만으로 풀리는 경우가 많아요.

**Q. UE(탈수)가 자꾸 떠요.**
A. 세탁물이 한쪽으로 쏠리면 탈수 시 보호로 멈춰요. 빨래를 펴고 양을 조절하며, 수평을 맞추면 개선돼요. 이불 같은 큰 빨래는 단독으로 돌리는 게 좋아요.

**Q. 'Sud'는 고장인가요?**
A. 아니에요. 거품이 너무 많을 때 뜨는 안내라 세제를 줄이면 돼요. 거품 제거 동작이 끝나면 자동으로 사라져요.

**Q. 4E와 4C는 다른 코드예요?**
A. 같아요. 2015년 이전은 4E, 이후는 4C로 표기만 다르고 의미(급수)는 동일해요.

## 🏁 정리: 4C·5C·UE는 물길과 빨래부터

삼성 세탁기 에러코드는 **급수(4C)·배수(5C)·탈수(UE)** 세 가지가 대부분이고, 모두 **수도꼭지·배수필터·세탁물 배치**만 점검하면 집에서 풀리는 경우가 많아요. 다만 **누수(LC)·과수위(OC)·센서·히터** 계열은 무리하지 말고 점검받는 게 안전해요.

> ⚠️ 본 글의 코드·조치는 삼성전자서비스 공식 점검코드와 공개 자료 기준(작성 시점 2026년 6월)이며, 모델·연식에 따라 다를 수 있어요. 정확한 진단은 모델명·코드와 함께 [삼성전자서비스](https://www.samsungsvc.co.kr/) 또는 1588-3366으로 확인하세요.

## 🛒 [함께 보면 좋은 글]

- [삼성 에어컨 에러코드 총정리 (E101·E461)](https://sancho216.tistory.com/863)
- [LG 드럼 세탁기 에러코드 (LE·IE·OE·UE·dE)](https://sancho216.tistory.com/entry/LG-드럼-세탁기-에러코드LE-IE-OE-UE-dE-dE1-dE2-tE-v5-u5-dHE-PE-FE-LOE-FF-uS1-Cd-CL-LCI-CF-Ed1-Ed2-Ed3-Ed4-Ed5-OPn-원인과-해결방법을-찾아보자)
- [LG 냉장고 에러코드 총정리](https://sancho216.tistory.com/entry/LG-냉장고에러코드-유형1F-FF-rF-CF-CO-FS-r5-d5-H5-55-rt-lt-9F-dH-Od-CH-CL-ld-UC-5d-CI-95-dr-IL-AS-Ad-P5-OFF-원인-과-해결책을-알아보자)
