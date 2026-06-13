---
title: 삼성 세탁기 에러코드 총정리 — 4C·5C·UE 급수·배수·탈수 원인과 자가조치 (드럼·통돌이)
platform: blogger
category: 생활·정보
tags: ['삼성세탁기', '세탁기에러코드', '4C', '5C', 'UE', '드럼세탁기', '세탁기급수', '세탁기배수', '삼성전자서비스']
date: 2026-06-13
source: 삼성전자서비스 공식(samsungsvc.co.kr) 4C/4E 점검코드 + 삼성 드럼세탁기 에러코드 다중 신뢰소스 교차확인
---

삼성 세탁기를 돌리는데 갑자기 멈추면서 **4C·5C·UE 같은 코드가 표시**되면 당황하기 쉽다. 하지만 가장 흔한 **4C(급수)·5C(배수)·UE(탈수 불균형)** 는 대부분 수도꼭지·배수필터·세탁물 배치만 확인하면 **집에서 바로 해결**되는 코드다. 모르고 서비스 기사를 부르면 출장비만 나갈 수 있다.

이 글은 **삼성전자서비스 공식 점검코드(samsungsvc.co.kr)** 와 공개 자료를 교차해, 삼성 세탁기에서 자주 보이는 에러코드의 **의미·원인·자가조치·기사 호출 필요 여부**를 정리했다. 드럼·통돌이(전자동) 모두 포함한다.

<div style="border-left:5px solid #2563eb;background:#eff6ff;padding:16px 20px;margin:20px 0;border-radius:8px;font-size:14px;"><b>📌 먼저 알아두세요</b><br>삼성 세탁기 코드는 <b>2015년 이전은 숫자+E(4E), 이후는 숫자+C(4C)</b> 로 표기만 다르고 의미는 같다(4E = 4C). 급수·배수·탈수 계열은 대부분 자가조치로 풀리지만, <b>누수(LC)·센서·통신·히터 계열은 전문 기사</b> 점검이 필요하다.</div>

{{broker:washer_header}}

## 코드를 찾기 전: 기본 점검 3단계

특정 코드를 보기 전에, 아래 기본 점검만으로 급수·배수·일시 오류의 상당수가 해결된다.

1. **전원 리셋** — 전원 버튼을 끄고 차단기/플러그를 1분간 분리했다 다시 연결한다. 일시적 통신·센서 오류가 초기화된다.
2. **수도·급수 확인** — 수도꼭지가 완전히 열려 있는지, 급수호스가 꺾이지 않았는지 본다(4C 대비).
3. **배수필터 청소** — 세탁기 하단 배수필터를 열어 이물질·동전·머리카락을 제거한다(5C 대비). 물이 남아 있을 수 있으니 수건을 받쳐 둔다.

:::stat 세탁기, 이것부터
4C·5C | 급수·배수 = 가장 흔함
UE | 탈수 시 세탁물 펴기
1분 | 전원 껐다 켜기
:::

> 📌 위 점검 후에도 같은 코드가 다시 뜬다면, 아래 코드별 표를 보고 기사 호출 여부를 판단하면 된다.

## 자주 뜨는 삼성 세탁기 에러코드 요약표

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">자가조치</th><th style="padding:9px;text-align:center;">기사필요</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">4C (4E)</td><td style="padding:8px;">급수 불량 — 물이 안 나오거나 적게 들어옴</td><td style="padding:8px;">수도꼭지 개방·급수호스 꺾임·급수필터 청소</td><td style="padding:8px;text-align:center;">대개 불필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">5C (5E)</td><td style="padding:8px;">배수 불량 — 정해진 시간 안에 배수 안 됨</td><td style="padding:8px;">배수필터·배수호스 막힘 청소</td><td style="padding:8px;text-align:center;">대개 불필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">UE (Ub)</td><td style="padding:8px;">탈수 불균형 — 세탁물 한쪽 쏠림·수평 불량</td><td style="padding:8px;">세탁물 양 조절·골고루 펴기·제품 수평 확인</td><td style="padding:8px;text-align:center;">불필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">dC (dE)</td><td style="padding:8px;">도어 열림·잠금 불량</td><td style="padding:8px;">도어를 완전히 닫고 재동작</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">3C (3E)</td><td style="padding:8px;">모터 과부하 — 세탁물 과다·무거움</td><td style="padding:8px;">세탁물 줄이고 재동작</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">Sud</td><td style="padding:8px;">거품 과다 (에러 아님) — 세제 과다 투입</td><td style="padding:8px;">거품 제거 동작 대기·세제량 줄이기</td><td style="padding:8px;text-align:center;">불필요</td></tr></tbody></table>

> 📌 **4C·5C·UE**가 전체 세탁기 코드의 대부분을 차지한다. 급수(수도)·배수(필터)·탈수(세탁물 배치)만 점검해도 상당수가 해결된다.

## 급수·배수 계열 — 4C·5C (가장 흔함)

세탁기 코드 중 가장 자주 보이는 계열이다. 물이 들어오고 나가는 경로만 점검하면 된다.

{{broker:washer_drum}}

- **4C(급수)**: 수도꼭지가 끝까지 열렸는지, 급수호스가 꺾이거나 눌리지 않았는지 확인한다. 호스 연결부의 **급수필터(거름망)** 에 이물질이 끼면 물이 적게 들어와 4C가 뜨므로, 호스를 분리해 거름망을 칫솔로 청소한다. 겨울철에는 호스 동결도 원인이 된다.
- **5C(배수)**: 세탁기 하단의 **배수필터**를 열어 동전·머리카락·이물질을 제거한다. 배수호스가 꺾였거나 너무 높이 올라가 있어도 배수가 안 된다. 호스 끝이 바닥 배수구에 제대로 들어가 있는지 확인한다.

## 탈수·도어 계열 — UE·dC

- **UE(Ub) 탈수 불균형**: 이불·수건처럼 무거운 빨래가 한쪽으로 쏠리면 탈수 시 통이 심하게 흔들려 보호를 위해 멈춘다. 세탁물을 골고루 펴주고, 빨래 양이 너무 적거나 많지 않게 조절한다. 세탁기 **수평**이 안 맞아도 발생하니 다리 높이를 조정한다.
- **dC(도어)**: 도어가 완전히 닫히지 않았거나 잠금 센서 문제다. 문틈에 빨래가 끼지 않았는지 확인하고 '딸깍' 소리가 나게 닫는다.

## 기사 점검이 필요한 코드

아래 코드는 센서·회로·누수 등 내부 부품 관련으로, 자가조치로 풀리지 않으면 점검이 필요하다.

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">조치</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">LC (LE)</td><td style="padding:8px;">누수 감지 — 누수 또는 회로기판 이상</td><td style="padding:8px;color:#dc2626;font-weight:600;">급수 잠그고 서비스 점검</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">OC (OE)</td><td style="padding:8px;">과수위 — 물이 넘침</td><td style="padding:8px;color:#dc2626;font-weight:600;">급수밸브 잠금 후 서비스 신청</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">1C</td><td style="padding:8px;">수위센서 이상 — 물높이 감지 오류</td><td style="padding:8px;color:#dc2626;font-weight:600;">전원 리셋 후 재발 시 점검</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">8C</td><td style="padding:8px;">진동감지 센서↔PCB 통신 불량</td><td style="padding:8px;color:#dc2626;font-weight:600;">서비스 점검</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">AC (AE)</td><td style="padding:8px;">회로기판 간 통신 이상</td><td style="padding:8px;color:#dc2626;font-weight:600;">전원 리셋 후 재발 시 점검</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">HC (HE)</td><td style="padding:8px;">히터 이상 (세탁·건조 가열)</td><td style="padding:8px;color:#dc2626;font-weight:600;">서비스 점검</td></tr></tbody></table>

> ⚠️ **LC·OC**처럼 누수·과수위 코드가 뜨면 우선 **수도(급수밸브)를 잠가** 추가 누수를 막은 뒤 서비스를 신청하는 것이 안전하다.

## 해결이 안 될 때: 삼성전자서비스

자가조치로 풀리지 않거나 센서·누수 계열 코드가 반복된다면 공식 채널을 이용한다.

- **대표 전화**: **1588-3366** (운영시간은 변동될 수 있음)
- **출장 서비스 예약·AI 챗봇**: 삼성전자서비스(samsungsvc.co.kr)
- 접수 전 **제품 모델명**(도어 안쪽·뒷면 라벨)과 **표시된 코드**를 메모해두면 상담이 빨라진다.

## 자주 묻는 질문 (FAQ)

**Q. 4C가 떴는데 수도는 잘 나와요.**
A. 수도가 정상이라면 급수호스 연결부의 **급수필터(거름망)** 막힘일 가능성이 크다. 호스를 분리해 거름망을 칫솔로 청소하면 대부분 해결된다. 겨울철에는 호스 동결도 확인한다.

**Q. 5C(배수)는 어떻게 해결하나요?**
A. 세탁기 하단 배수필터를 열어 이물질을 제거하고, 배수호스가 꺾이거나 너무 높이 올라가 있지 않은지 확인한다. 필터 청소만으로 해결되는 경우가 많다.

**Q. UE(탈수)가 자꾸 떠요.**
A. 세탁물이 한쪽으로 쏠리면 탈수 시 보호를 위해 멈춘다. 빨래를 골고루 펴고 양을 조절하며, 세탁기 수평을 맞추면 개선된다. 이불 같은 큰 빨래는 단독으로 돌리는 것이 좋다.

**Q. 'Sud'는 고장인가요?**
A. 아니다. 거품이 너무 많을 때 뜨는 안내로, 세제를 줄이면 된다. 세탁기가 거품 제거 동작을 마치면 자동으로 사라진다.

**Q. 4E와 4C는 다른 코드인가요?**
A. 같다. 2015년 이전 모델은 4E, 이후 모델은 4C로 표기만 다를 뿐 의미(급수)는 동일하다.

## 정리: 4C·5C·UE는 물길과 빨래부터

삼성 세탁기 에러코드는 **급수(4C)·배수(5C)·탈수(UE)** 세 가지가 대부분이고, 모두 **수도꼭지·배수필터·세탁물 배치**만 점검하면 집에서 해결되는 경우가 많다. 다만 **누수(LC)·과수위(OC)·센서·히터** 계열은 무리하게 돌리지 말고 점검을 받는 것이 안전하다.

> ⚠️ 본 글의 코드·조치는 삼성전자서비스 공식 점검코드와 공개 자료를 교차한 것(작성 시점 2026년 6월)이며, 모델·연식에 따라 다를 수 있다. 정확한 진단은 제품 모델명·표시 코드를 [삼성전자서비스](https://www.samsungsvc.co.kr/) 또는 1588-3366으로 확인하기 바란다.

## 함께 보면 좋은 글

- [삼성 에어컨 에러코드 완벽 가이드 (E101·E461·100~400번대)](https://consistency.onestepblog.info/2026/06/e101e461-100200400.html)
- [LG 에어컨 CH 에러코드 완벽 가이드 (CH05·CH38)](https://consistency.onestepblog.info/2026/06/lg-ch-ch05ch38.html)
- [LG 드럼 세탁기 에러코드 총정리 (LE·IE·OE·UE·dE)](https://sancho216.tistory.com/entry/LG-드럼-세탁기-에러코드LE-IE-OE-UE-dE-dE1-dE2-tE-v5-u5-dHE-PE-FE-LOE-FF-uS1-Cd-CL-LCI-CF-Ed1-Ed2-Ed3-Ed4-Ed5-OPn-원인과-해결방법을-찾아보자)
