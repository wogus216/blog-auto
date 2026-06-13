---
title: LG 드럼세탁기 에러코드 총정리 — IE·OE·UE·LE 급수·배수·탈수 원인과 자가조치
platform: blogger
category: 생활·정보
tags: ['LG세탁기', 'LG드럼세탁기', '세탁기에러코드', 'IE', 'OE', 'UE', 'LE', '세탁기배수', 'LG전자서비스']
date: 2026-06-13
source: LG전자 고객지원 스스로해결(lge.co.kr) 드럼세탁기 에러표시 솔루션 + LG 세탁기 코드 다중 신뢰소스 교차확인
---

LG 드럼세탁기를 돌리다 갑자기 멈추면서 **IE·OE·UE·LE 같은 코드가 표시**되면 당황하기 쉽다. 하지만 LG 세탁기 에러코드는 **알파벳이 곧 원인의 약자**라, 뜻만 알면 대처가 쉽다. **IE는 급수(Inlet), OE는 배수(Outlet), UE는 탈수 불균형(Unbalance)** 이고, 이들 대부분은 수도·배수호스·세탁물 배치만 확인하면 **집에서 바로 해결**된다.

이 글은 **LG전자 고객지원(lge.co.kr) 스스로 해결** 안내와 공개 자료를 교차해, LG 드럼세탁기에서 자주 보이는 에러코드의 **의미·원인·자가조치·기사 호출 필요 여부**를 정리했다.

<div style="border-left:5px solid #2563eb;background:#eff6ff;padding:16px 20px;margin:20px 0;border-radius:8px;font-size:14px;"><b>📌 LG 세탁기 코드는 약자로 읽으면 쉽다</b><br><b>I</b>nlet(급수)→IE, <b>O</b>utlet(배수)→OE, <b>U</b>nbalance(불균형)→UE, <b>L</b>ock·모터 구속→LE, <b>d</b>oor(문)→dE. 급수·배수·탈수 계열은 대부분 자가조치로 풀리지만, <b>센서·모터·온도 계열(tE·PE·CE)은 전문 기사</b> 점검이 필요하다.</div>

{{broker:washer_header}}

## 코드를 찾기 전: 기본 점검 3단계

특정 코드를 보기 전에, 아래 기본 점검만으로 급수·배수·일시 오류의 상당수가 해결된다.

1. **전원 리셋** — 전원을 끄고 차단기/플러그를 1분간 분리했다 다시 연결한다. 순간정전(PF) 등 일시 오류가 초기화된다.
2. **수도·급수 확인** — 수도꼭지가 끝까지 열렸는지, 급수호스가 꺾이지 않았는지 본다(IE 대비).
3. **배수필터 청소** — 세탁기 하단 배수필터를 열어 이물질을 제거한다(OE 대비). 물이 남아 있을 수 있으니 수건을 받쳐 둔다.

:::stat LG 세탁기, 약자로 기억
IE·OE | 급수(In)·배수(Out)
UE | 탈수 불균형 = 펴기
LE | 세탁통 과부하 = 줄이기
:::

> 📌 위 점검 후에도 같은 코드가 다시 뜬다면, 아래 코드별 표를 보고 기사 호출 여부를 판단하면 된다.

## 자주 뜨는 LG 드럼세탁기 에러코드 요약표

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">자가조치</th><th style="padding:9px;text-align:center;">기사필요</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">IE</td><td style="padding:8px;">급수 불량(Inlet) — 물이 안 들어옴. 수도·호스 문제</td><td style="padding:8px;">수도꼭지 개방·급수호스 꺾임·급수필터 청소</td><td style="padding:8px;text-align:center;">대개 불필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">OE</td><td style="padding:8px;">배수 불량(Outlet) — 물이 안 빠짐. 배수호스·필터, 겨울 동결</td><td style="padding:8px;">배수필터·호스 막힘 청소 / 동결 시 해동</td><td style="padding:8px;text-align:center;">대개 불필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">UE</td><td style="padding:8px;">탈수 불균형(Unbalance) — 세탁물 쏠림·수평 불량</td><td style="padding:8px;">세탁물 골고루 펴기·양 조절·수평 확인</td><td style="padding:8px;text-align:center;">불필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">LE</td><td style="padding:8px;">세탁통 회전 이상·모터 구속 — 세탁물 과다·연속 동작</td><td style="padding:8px;">세탁물 줄이고 잠시 후 재동작</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">FE</td><td style="padding:8px;">과다 급수 — 물이 과도하게 들어옴</td><td style="padding:8px;color:#dc2626;font-weight:600;">전원 끄고 재발 시 수위센서 점검</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">dE</td><td style="padding:8px;">도어 열림·잠금 불량(Door)</td><td style="padding:8px;">도어를 완전히 닫고 재동작</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CL</td><td style="padding:8px;">버튼(차일드) 잠금 — 고장 아님</td><td style="padding:8px;">잠금 버튼 3초 길게 눌러 해제</td><td style="padding:8px;text-align:center;">불필요</td></tr></tbody></table>

> 📌 **IE·OE·UE**가 LG 세탁기 코드의 대부분이다. 급수(수도)·배수(필터)·탈수(세탁물 배치)만 점검해도 상당수가 해결된다.

## 급수·배수 계열 — IE·OE (가장 흔함)

{{broker:washer_drum}}

- **IE(급수)**: 수도꼭지가 끝까지 열렸는지, 급수호스가 꺾이거나 눌리지 않았는지 확인한다. 호스 연결부의 **급수필터(거름망)** 가 막히면 물이 적게 들어와 IE가 뜨므로, 호스를 분리해 거름망을 칫솔로 청소한다.
- **OE(배수)**: 세탁기 하단 **배수필터**를 열어 동전·머리카락·이물질을 제거한다. 배수호스가 꺾였거나 너무 높이 올라가 있어도 배수가 안 된다. **겨울철에는 배수호스·펌프가 얼어 OE가 뜨는 경우**가 많은데, 이때는 따뜻한 환경에서 자연 해동하거나 미지근한 물로 호스를 녹인다(뜨거운 물 직접 부음 금지).

## 탈수·모터·도어 계열 — UE·LE·dE

- **UE(탈수 불균형)**: 이불·수건처럼 무거운 빨래가 한쪽으로 쏠리면 탈수 시 통이 흔들려 보호를 위해 멈춘다. 세탁물을 골고루 펴고 양을 조절하며, 세탁기 **수평**(다리 높이)을 맞춘다.
- **LE(세탁통 회전 이상)**: 세탁물이 너무 많거나 무거울 때, 또는 세탁기를 연속으로 돌릴 때 모터 보호로 발생한다. 세탁물을 줄이고 잠시 식힌 뒤 재동작한다. 반복되면 모터·벨트 점검이 필요하다.
- **dE(도어)**: 문이 완전히 닫히지 않았거나 잠금 센서 문제다. 문틈에 빨래가 끼지 않았는지 확인하고 '딸깍' 소리가 나게 닫는다.

## 기사 점검이 필요한 코드

아래는 센서·모터·온도 등 내부 부품 관련으로, 자가조치로 풀리지 않으면 점검이 필요하다.

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">조치</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">tE</td><td style="padding:8px;">온도센서 이상 (세탁·건조 가열부)</td><td style="padding:8px;color:#dc2626;font-weight:600;">전원 리셋 후 재발 시 점검</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">PE</td><td style="padding:8px;">수위센서 이상 — 물높이 감지 오류</td><td style="padding:8px;color:#dc2626;font-weight:600;">서비스 점검</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CE</td><td style="padding:8px;">모터 과전류 — 구동부 과부하</td><td style="padding:8px;color:#dc2626;font-weight:600;">세탁물 줄이고 재발 시 점검</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">PF</td><td style="padding:8px;">순간 정전 — 동작 중 전원 끊김</td><td style="padding:8px;">전원 다시 켜고 재시작 (반복 시 전원 점검)</td></tr></tbody></table>

> ⚠️ **FE(과다 급수)** 가 반복되면 수위센서·급수밸브 문제일 수 있다. 물이 계속 차오르면 우선 **수도(급수밸브)를 잠그고** 서비스를 신청한다.

## 해결이 안 될 때: LG전자 서비스센터

자가조치로 풀리지 않거나 센서·모터 계열 코드가 반복된다면 공식 채널을 이용한다.

- **대표 전화**: **1544-7777** (운영시간은 변동될 수 있음)
- **온라인 예약·스스로 해결**: LG전자 고객지원(lge.co.kr)
- 접수 전 **제품 모델명**(도어 안쪽·뒷면 라벨)과 **표시된 코드**를 메모해두면 상담이 빨라진다.

## 자주 묻는 질문 (FAQ)

**Q. IE가 떴는데 수도는 잘 나와요.**
A. 수도가 정상이라면 급수호스 연결부의 **급수필터(거름망)** 막힘일 가능성이 크다. 호스를 분리해 거름망을 칫솔로 청소하면 대부분 해결된다.

**Q. OE(배수)는 어떻게 해결하나요?**
A. 하단 배수필터를 열어 이물질을 제거하고, 배수호스가 꺾이거나 너무 높지 않은지 확인한다. 겨울철 동결이라면 자연 해동하거나 미지근한 물로 호스를 녹인다(뜨거운 물 직접 붓기 금지).

**Q. LE는 고장인가요?**
A. 세탁물이 많거나 연속 사용으로 모터가 보호 정지한 경우가 많다. 세탁물을 줄이고 잠시 식힌 뒤 다시 돌려본다. 반복되면 모터·벨트 점검이 필요하다.

**Q. 'CL'은 뭔가요?**
A. 고장이 아니라 **버튼(차일드) 잠금**이 켜진 상태다. 잠금 버튼을 3초간 길게 누르면 해제된다.

**Q. dE(도어)가 자꾸 떠요.**
A. 문이 완전히 닫혔는지, 문틈에 빨래가 끼지 않았는지 확인한다. '딸깍' 소리가 나게 닫아야 잠금이 인식된다. 반복되면 도어 잠금장치 점검이 필요하다.

## 정리: IE·OE·UE는 물길과 빨래부터

LG 드럼세탁기 에러코드는 **급수(IE)·배수(OE)·탈수(UE)** 세 가지가 대부분이고, 알파벳 약자만 알면 대처가 쉽다. 모두 **수도꼭지·배수필터·세탁물 배치**만 점검하면 집에서 해결되는 경우가 많다. 다만 **센서·모터·온도(tE·PE·CE)** 계열은 무리하게 돌리지 말고 점검을 받는 것이 안전하다.

> ⚠️ 본 글의 코드·조치는 LG전자 고객지원 안내와 공개 자료를 교차한 것(작성 시점 2026년 6월)이며, 모델·연식에 따라 다를 수 있다. 정확한 진단은 제품 모델명·표시 코드를 [LG전자 고객지원](https://www.lge.co.kr/support) 또는 1544-7777로 확인하기 바란다.

## 함께 보면 좋은 글

- [삼성 세탁기 에러코드 총정리 (4C·5C·UE)](https://consistency.onestepblog.info/2026/06/4c5cue.html)
- [LG 에어컨 CH 에러코드 완벽 가이드 (CH05·CH38)](https://consistency.onestepblog.info/2026/06/lg-ch-ch05ch38.html)
- [LG 드럼 세탁기 에러코드 (LE·IE·OE·UE·dE)](https://sancho216.tistory.com/entry/LG-드럼-세탁기-에러코드LE-IE-OE-UE-dE-dE1-dE2-tE-v5-u5-dHE-PE-FE-LOE-FF-uS1-Cd-CL-LCI-CF-Ed1-Ed2-Ed3-Ed4-Ed5-OPn-원인과-해결방법을-찾아보자)
