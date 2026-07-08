---
title: LG 천장형·시스템에어컨 에러코드! 빨간불 깜빡임 읽는 법 + CH07·CH237 (상가·사무실 자가진단)
platform: tistory
category: 에러해결
tags: ['LG시스템에어컨', '천장형에어컨', '에어컨에러코드', 'CH07', 'CH237', '에어컨빨간불', '시스템에어컨', '상가에어컨', 'LG전자서비스']
date: 2026-07-08
source: LG전자 고객지원 스스로해결(lge.co.kr) — 시스템에어컨 CH05/천장형 CH-07/LED램프 깜빡임/CH237·CH238(21년 이후) 솔루션 교차확인
---

상가나 사무실 천장에 달린 **LG 시스템에어컨(천장형)**이 갑자기 안 시원하거나 꺼졌는데 — 벽걸이처럼 **표시창에 'CH05' 같은 코드가 안 뜨고, 실내기 구석 램프만 빨갛게 깜빡거린 적** 있으시죠? 천장형·시스템 제품은 표시창이 없는 모델이 많아서, **에러코드를 'LED 램프 깜빡임 횟수'로 읽어야** 해요. 이걸 모르면 "그냥 불만 깜빡인다"며 무작정 기사부터 부르게 됩니다.

이 글은 **LG전자 고객지원(lge.co.kr)** 의 시스템에어컨·천장형 안내를 기준으로, ① **깜빡임으로 코드 읽는 법**부터 ② 천장형·멀티에서 유독 자주 뜨는 **CH07·CH237·CH238** 같은 코드까지, 상가·사무실에서 직접 확인하고 조치하는 순서로 정리했어요. (가정용 벽걸이·스탠드 CH 코드는 글 맨 아래 링크에 따로 정리해뒀습니다.)

<div style="border-left:5px solid #2563eb;background:#eff6ff;padding:16px 20px;margin:20px 0;border-radius:8px;font-size:14px;"><b>📌 천장형은 '코드'가 아니라 '깜빡임'으로 말해요</b><br>표시창이 없는 <b>4WAY·2WAY·1WAY 천장형</b>은 실내기 LED 램프의 <b>색깔과 깜빡임 횟수</b>로 에러를 알려줘요. 반면 <b>1대 실외기 + 여러 실내기</b>인 멀티/시스템에선 <b>CH07(운전모드 불일치)·CH237/238(실외기 통신)</b>처럼 벽걸이엔 잘 안 뜨는 코드가 나옵니다.</div>

{{broker:aircon_header}}

## 🔦 표시창이 없어요 — 천장형은 'LED 깜빡임'으로 코드를 읽어요

천장형 실내기는 표시창 대신 **바람 나오는 판(패널) 구석의 표시램프**로 에러를 알려줘요. 램프 개수·색상은 모델마다 다르지만, 원리는 **깜빡임 횟수 = 코드 숫자**예요. 자릿수(백·십·일)는 **깜빡이는 간격(속도)** 이나 **색깔**로 구분합니다.

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">램프 타입</th><th style="padding:9px;text-align:left;">자릿수 구분 방법</th><th style="padding:9px;text-align:left;">읽는 순서</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">1WAY<br>(빨간 램프)</td><td style="padding:8px;">간격으로 구분 — <b>백자리 2초 / 십자리 0.8초 / 일자리 0.3초</b> 간격 점멸</td><td style="padding:8px;">일 → 십 → 백</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">4WAY·2WAY<br>(초록·주황 램프)</td><td style="padding:8px;">색으로 구분 — <b>주황=백자리 / 초록=일자리</b>, 0.5초 주기로 번갈아 점멸</td><td style="padding:8px;">백(주황) → 십 → 일(초록)</td></tr></tbody></table>

예를 들어 빨간 램프가 **"3번 깜빡 → (잠깐 쉬고) → 2번 깜빡"** 을 반복하면 **CH23**(실외기 전원·전압 계열)이에요. 4WAY에서 주황 2번 → 초록 3번이면 **CH203** 식으로 백·십·일을 조합해 읽으면 됩니다.

:::stat 깜빡임 읽는 핵심
색깔 | 자릿수를 나눠요
간격 | 2초=백, 0.8초=십, 0.3초=일
촬영 | 폰으로 찍어 반복구간 확인
:::

> 📌 **가장 편한 방법은 '핸드폰 촬영'이에요.** 램프가 빠르게 깜빡이면 눈으로 세기 어렵거든요. 실내기 램프를 10~20초 동영상으로 찍고 **반복되는 한 구간**만 천천히 돌려 보면 횟수가 정확히 보여요. 이 영상은 나중에 기사에게 보여주기에도 좋아요.

## 🚨 코드 확인 전, 이것부터 (대부분 여기서 끝나요)

깜빡임 코드를 읽었어도, 통신·센서 계열 일시 오류는 아래 기본 조치로 많이 사라져요. 시스템에어컨은 **실외기까지 전원이 함께 내려가야** 리셋이 제대로 됩니다.

1. **전원(차단기) 리셋** — 해당 계통 차단기를 내리고 **3~5분 기다린 뒤** 다시 올려요. 상가·사무실은 차단기 위치를 모르면 **건물 관리사무소**에 문의하세요.
2. **실외기 주변 확인** — 옥상·베란다 실외기 앞뒤 통풍구를 막은 물건(간판·박스·낙엽)을 치워요. 여름 폭염엔 실외기 과열로 보호정지가 잦아요.
3. **필터 청소** — 천장형은 흡입 그릴을 열어 필터를 분리·세척해요. 상가는 먼지가 빨리 껴서 냉방 약화·결빙의 흔한 원인이에요.

> 📌 위 조치 후에도 같은 코드가 반복되면, 아래 표에서 **통신·팬 계열**(리셋으로 해소)인지 **냉매·압축기 계열**(기사 점검)인지 구분해 판단하세요.

## 📋 천장형·시스템에어컨 자주 뜨는 코드 한눈에

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">자가조치</th><th style="padding:9px;text-align:center;">기사필요</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH05·CH53</td><td style="padding:8px;">실내기↔실외기 통신 이상 (E0로도 표시)</td><td style="padding:8px;">차단기 3~5분 리셋 / 통신선 접촉 확인</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH07</td><td style="padding:8px;">멀티 실내기끼리 냉·난방 모드가 서로 다름 (천장형 특유)</td><td style="padding:8px;">모든 실내기를 같은 모드로 통일</td><td style="padding:8px;text-align:center;">보통 자가해결</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH10</td><td style="padding:8px;">실내기 팬 구속 (E6) — 팬 막힘·이물질</td><td style="padding:8px;">전원 차단 후 팬 주변 이물질 제거</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH237·CH238</td><td style="padding:8px;">실내기↔실외기 연결·통신 이상 (실외기 전원 미공급 포함, 21년 이후 제품)</td><td style="padding:8px;">실외기 차단기·전원 확인 후 리셋</td><td style="padding:8px;text-align:center;font-weight:700;color:#dc2626;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH38</td><td style="padding:8px;">냉매 부족·누설 감지 (가스 부족)</td><td style="padding:8px;color:#dc2626;font-weight:600;">기사 점검 필요(냉매 작업)</td><td style="padding:8px;text-align:center;font-weight:700;color:#dc2626;">○ 필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH90·CH91</td><td style="padding:8px;">설치·시운전 중 배관 연결 비정상</td><td style="padding:8px;color:#dc2626;font-weight:600;">설치 업체에 배관 점검 요청</td><td style="padding:8px;text-align:center;font-weight:700;color:#dc2626;">○ 필요</td></tr></tbody></table>

> 📌 **천장형·시스템에서 제일 흔한 두 가지는 CH07과 CH237**이에요. CH07은 여러 방을 각자 리모컨으로 켜다 보니 모드가 엇갈린 경우라 **직접 해결**되고, CH237은 실외기 전원이 안 들어오면도 떠서 **차단기부터** 봐야 해요.

## 🔁 CH07 — 천장형·멀티 특유의 '운전모드 불일치'

CH07은 벽걸이 단독기엔 거의 안 뜨고, **1대 실외기에 여러 실내기가 물린 멀티/시스템**에서 나오는 대표 코드예요. LG 안내에 따르면 **실내기들이 냉방·난방으로 제각각 운전되면** 시스템이 충돌을 막으려 CH07을 띄우고 운전을 멈춥니다. (한 실외기는 같은 순간에 냉방 또는 난방 '하나'만 할 수 있기 때문이에요.)

**LG전자 안내 기준 해결 순서**

1. 에어컨 **전원 차단기를 내리고 약 3분** 기다려요.
2. 차단기를 올린 뒤 **실내기를 한 대씩 순차로 켜면서**, 각 실내기의 **운전선택 버튼을 눌러 전부 '냉방'(또는 전부 '난방')으로 통일**해요.
3. 모든 실내기가 같은 모드가 되면 정상 가동됩니다.

> 📌 사무실처럼 방마다 리모컨이 따로 있으면, **한 명이 "지금부터 전부 냉방"** 하고 돌면서 맞추는 게 제일 빨라요. 차단기 위치를 모르면 관리사무소에 요청하세요.

{{broker:aircon_outdoor}}

## 📡 CH237·CH238 — 21년 이후 시스템 멀티 통신 오류

2021년 이후 출시된 시스템 멀티형에서 **실내기와 실외기의 연결·통신에 문제**가 있을 때 뜨는 코드예요. 핵심은 **실외기에 전원이 아예 안 들어와도 CH237/238이 뜬다**는 점이에요. 그래서 통신선을 의심하기 전에 **실외기 전원부터** 확인해야 해요.

- **실외기 차단기 확인** — 실외기 전용 차단기가 내려가 있진 않은지 봐요(정전·누전 트립 후 흔함).
- **전원 리셋** — 실내·실외 계통을 함께 3~5분 내렸다 올려요.
- **재발 시 점검** — 그래도 반복되면 통신선 접촉·실외기 기판 문제일 수 있어 서비스 점검이 필요해요. 시스템 멀티는 **실내기별 배관 차압** 이상에서도 보고돼요.

## 🌡️ 통신·팬·냉매 계열 — 계통별로 나눠 보기

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">계통</th><th style="padding:9px;text-align:left;">해당 코드</th><th style="padding:9px;text-align:left;">성격 / 대응</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">통신·센서</td><td style="padding:8px;">CH01·CH02·CH03·CH05·CH53·CH237·CH238</td><td style="padding:8px;">대개 <b>전원 리셋</b>으로 1차 해소, 재발 시 통신선·기판 점검</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">팬·구속</td><td style="padding:8px;">CH10(실내 E6)·CH67(실외 EF)</td><td style="padding:8px;">전원 차단 후 <b>팬 주변 이물질 제거</b>, 모터 불량 시 교체</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">모드·설정</td><td style="padding:8px;">CH07</td><td style="padding:8px;">멀티 <b>운전모드 통일</b>로 해결(위 참고)</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">압축기·전원</td><td style="padding:8px;">CH21·CH22·CH23</td><td style="padding:8px;">실외기 통풍 확인 + 리셋, 반복되면 기사</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">냉매·설치</td><td style="padding:8px;color:#dc2626;font-weight:600;">CH38·CH90·CH91</td><td style="padding:8px;color:#dc2626;font-weight:600;">자가조치 X — 냉매·배관 전문 작업</td></tr></tbody></table>

> ⚠️ **CH38(냉매 부족)·CH90/CH91(설치 배관)** 은 무리하게 계속 돌리면 압축기가 상할 수 있어요. 특히 **설치·이전 직후** CH90/CH91이면 시운전 배관 문제일 수 있으니 설치 업체에 재점검을 요청하세요.

> 📌 위 코드·간격 값은 **LG전자 고객지원 안내(작성 시점 2026년 7월) 기준**이며, 모델·연식(특히 21년 전후)과 램프 개수에 따라 표시·의미가 달라질 수 있어요. **CH150·CH237·CH238**처럼 세 자리 코드는 제품마다 정의가 달라, 모델명과 함께 확인하는 게 정확합니다.

## 🏢 상가·사무실이라면 — 'AS 주체'부터 확인하세요

가정용과 달리 상가·사무실 천장형은 **누가 수리비를 부담하는지**가 먼저예요. 무작정 사설 기사를 부르면 나중에 정산이 꼬여요.

- **임차(세입자)** — 표준임대차 관행상 **시설물 노후·고장은 임대인**, 사용 부주의는 임차인 부담인 경우가 많아요. 큰 수리 전 **임대인·관리사무소에 먼저 통보**하세요.
- **설치 5~10년 이내** — 실외기·냉매 계열은 **부품 보증**이 남았을 수 있어요. 설치 업체 명함·시공 내역을 찾아보세요.
- **여러 대 동시 이상** — 한 실외기에 물린 실내기가 **동시에** 문제면 실외기·전원·통신 공통 원인일 가능성이 커요. 개별기가 아니라 **계통 단위**로 봐야 해요.

## ☎️ LG전자 서비스센터

자가조치로 안 되거나 냉매·압축기 코드가 반복되면 공식 채널을 이용하세요.

- **대표 전화**: **1544-7777** (운영시간 변동될 수 있음)
- **온라인 예약·스스로 해결**: LG전자 고객지원(lge.co.kr)
- 문의 전 **모델명**(실내기 그릴 안쪽·패널 라벨), **뜬 코드(또는 깜빡임 영상)**, **설치 시기**를 메모해두면 빨라요.

## 🔍 [FAQ] 자주 묻는 질문

**Q. 표시창이 없고 빨간불만 깜빡여요. 코드를 어떻게 아나요?**
A. 천장형은 램프 깜빡임이 코드예요. **빨간 램프는 간격(2초=백, 0.8초=십, 0.3초=일), 초록·주황은 색(주황=백, 초록=일)** 으로 자릿수를 나눠요. 폰으로 찍어 반복 구간을 세면 정확합니다.

**Q. 방마다 온도가 따로 노는데 CH07이 떴어요.**
A. 멀티라 실내기들이 냉방·난방 모드가 엇갈린 경우예요. 차단기 3분 리셋 후, 실내기를 하나씩 켜며 **전부 같은 모드(냉방이면 냉방)로 통일**하면 풀려요.

**Q. CH237인데 실외기 소리가 아예 안 나요.**
A. CH237/238은 **실외기 전원이 안 들어와도** 떠요. 실외기 전용 차단기가 내려갔는지부터 확인하고, 정상인데 반복되면 통신선·기판 점검을 받으세요.

**Q. 상가 세입자인데 수리비를 제가 다 내야 하나요?**
A. 노후·고장은 임대인 부담인 경우가 많아요. 수리 전 **관리사무소·임대인에게 먼저 알리고** 진행하는 게 분쟁을 줄여요.

## 🏁 정리: 깜빡임부터 읽고, CH07·CH237은 차단기부터

LG 천장형·시스템에어컨은 **표시창이 없으면 LED 깜빡임으로 코드를 읽는 것**이 출발점이에요. 그다음은 두 갈래 — **CH07(운전모드 불일치)** 은 실내기 모드를 통일하면 되고, **CH237/238(실외기 통신)** 은 실외기 전원·차단기부터 확인하면 됩니다. **CH38·CH90/91처럼 냉매·배관 코드는 무리하지 말고 점검**받는 게 안전해요.

> ⚠️ 본 글은 LG전자 고객지원 안내(작성 시점 2026년 7월) 기준이며, 모델·연식에 따라 다를 수 있어요. 정확한 진단은 모델명·코드(또는 깜빡임 영상)와 함께 [LG전자 고객지원](https://www.lge.co.kr/support) 또는 1544-7777로 확인하세요.

## 🛒 [함께 보면 좋은 글]

- [LG 에어컨 CH 에러코드 총정리 및 해결 방법 (벽걸이·스탠드)](https://sancho216.tistory.com/entry/LG-에어컨-CH-에러코드-총정리-및-해결-방법)
- [삼성 에어컨 CE 에러 전체 코드 및 원인·해결방법](https://sancho216.tistory.com/entry/삼성-에어컨-CE에러-전체-코드-및-원인-해결방법)
- [에어컨이 안 시원할 때 — 냉방 안 되는 원인 7가지 자가진단](https://sancho216.tistory.com/entry/에어컨이-안-시원할-때-—-냉방-안-되는-원인-7가지-자가진단-필터·실외기·냉매·전기세까지)
