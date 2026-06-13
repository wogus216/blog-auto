---
title: LG 에어컨 CH 에러코드 뜰 때! CH05·CH38 자가진단 총정리 (휘센 포함, 기사 부르기 전에)
platform: tistory
category: 에러해결
tags: ['LG에어컨', '에어컨에러코드', 'CH05', 'CH38', '휘센', '에어컨ch', '에어컨고장', 'LG전자서비스']
date: 2026-06-13
source: LG전자 고객지원 스스로해결(lge.co.kr) CH05/CH38 솔루션 + LG 에어컨 CH 코드 다중 신뢰소스 교차확인
---

여름에 LG 에어컨(휘센)을 켰는데 시원한 바람 대신 표시창에 **'CH05'·'CH38'** 같은 글자가 떴다면 — 너무 걱정 마세요. LG 에어컨의 **CH는 'Check(점검)'의 약자**라, 뒤 숫자가 어디가 문제인지 알려주는 신호예요. 그리고 제일 흔한 **CH05(통신)** 는 차단기 한 번 내렸다 올리면 풀리는 경우가 대부분입니다. 모르고 기사부터 부르면 출장비만 나가요.

이 글은 **LG전자 고객지원(lge.co.kr)** 기준으로, LG 에어컨에서 자주 뜨는 CH 코드를 **집에서 직접 확인하고 조치하는 법**으로 정리했어요. 벽걸이·스탠드·시스템(휘센) 다 포함합니다.

<div style="border-left:5px solid #2563eb;background:#eff6ff;padding:16px 20px;margin:20px 0;border-radius:8px;font-size:14px;"><b>📌 CH 코드, 약자로 읽으면 쉬워요</b><br>LG 에어컨의 <b>CH = Check(점검)</b>, 뒤 숫자가 이상 부위예요. 같은 통신 오류를 <b>E0</b>로 표시하는 모델도 있어요. 통신·센서 계열은 대부분 전원 리셋으로 풀리지만, <b>냉매·설치 코드(CH38·CH90·CH91)는 전문 기사</b>가 필요합니다.</div>

{{broker:aircon_header}}

## 🚨 코드 보기 전, 이것부터 (대부분 여기서 끝나요)

특정 코드를 찾기 전에, 통신·센서 일시 오류는 아래 기본 조치로 대부분 사라져요. LG는 전원 리셋 시 **5분 대기**를 권장합니다.

1. **전원(차단기) 리셋** — 차단기를 내리고 **약 5분 기다린 뒤** 다시 올려요. CH05·CH53 같은 통신 코드가 여기서 많이 풀립니다.
2. **실외기 주변 확인** — 실외기 좌우·뒤 공간을 확보하고(갤러리형은 창 개방), 통풍을 막는 물건을 치워요.
3. **필터 청소** — 실내기 필터를 분리해 세척·건조 후 다시 끼워요. 냉방 약화·결빙 예방에 좋아요.

:::stat CH 코드, 이것부터
CH05 | 가장 흔한 통신 장애
5분 | 차단기 내렸다 올리기
2계열 | 통신·센서 vs 압축기·냉매
:::

> 📌 위 조치 후에도 같은 CH 코드가 반복되면, 아래 표에서 통신·센서 계열인지 압축기·냉매 계열인지 확인하고 기사 호출을 판단하세요.

## 📋 LG 에어컨 자주 뜨는 CH 코드 한눈에

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">자가조치</th><th style="padding:9px;text-align:center;">기사필요</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH05</td><td style="padding:8px;">실내기↔실외기 통신 장애 (가장 흔함). E0로도 표시</td><td style="padding:8px;">차단기 5분 내렸다 올리기</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH01</td><td style="padding:8px;">실내 온도센서 이상 (단선·이탈)</td><td style="padding:8px;">차단기 리셋</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH10</td><td style="padding:8px;">실내 팬모터 회전 불량 (팬 막힘·고착)</td><td style="padding:8px;">차단기 리셋 + 팬 주변 이물질 확인</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH21</td><td style="padding:8px;">실외 인버터 압축기 DC 과전류 (전원 불안정·압축기)</td><td style="padding:8px;">차단기 리셋</td><td style="padding:8px;text-align:center;font-weight:700;color:#dc2626;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH38</td><td style="padding:8px;">냉매 부족·누설 감지 (가스 부족)</td><td style="padding:8px;color:#dc2626;font-weight:600;">기사 점검 필요(냉매 작업)</td><td style="padding:8px;text-align:center;font-weight:700;color:#dc2626;">○ 필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH90·CH91</td><td style="padding:8px;">설치·시운전 중 배관 연결 비정상 (F4 동반)</td><td style="padding:8px;color:#dc2626;font-weight:600;">설치 업체에 배관 점검 요청</td><td style="padding:8px;text-align:center;font-weight:700;color:#dc2626;">○ 필요</td></tr></tbody></table>

> 📌 **CH05**는 여름 첫 가동 때 제일 많이 떠요. 겨우내 꺼뒀던 실외기와 통신이 잠깐 어긋난 경우가 많아 차단기 리셋 한 번으로 끝나는 사례가 대부분이에요.

## 🔧 통신·센서 계열 — 대부분 리셋으로 해결

실내기 센서, 리모컨·실내외 통신, 배수 등 **전원 리셋으로 1차 해소되는** 코드예요.

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">자가조치</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH01</td><td style="padding:8px;">실내 온도센서 이상</td><td style="padding:8px;">차단기 리셋 / 재발 시 점검</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH02</td><td style="padding:8px;">실내 열교환기(배관) 입구 센서 이상</td><td style="padding:8px;">차단기 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH03</td><td style="padding:8px;">리모컨↔실내기 통신 불량</td><td style="padding:8px;">리모컨 배터리 교체 / 전원 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH05</td><td style="padding:8px;">실내기↔실외기 통신 장애 (E0 동일)</td><td style="padding:8px;">차단기 5분 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH07</td><td style="padding:8px;">실내기들이 냉·난방을 다르게 운전 (멀티)</td><td style="padding:8px;">모든 실내기를 같은 모드로 통일</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH10</td><td style="padding:8px;">실내 팬모터 회전 불량 (락·고착)</td><td style="padding:8px;">차단기 리셋 + 팬 이물질 확인</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH53</td><td style="padding:8px;">실내기↔실외기 신호선 통신 이상</td><td style="padding:8px;">차단기 리셋 / 통신선 접촉 확인</td></tr></tbody></table>

## ⚙️ 압축기·냉매 계열 — 반복되면 점검

실외기 압축기·냉매·설치 배관 관련이라 **자가조치로 안 풀리면 기사 점검**이 필요해요.

{{broker:aircon_outdoor}}

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">자가조치 / 비고</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH21</td><td style="padding:8px;">실외 인버터 압축기 DC 과전류 (IPM)</td><td style="padding:8px;">차단기 리셋 후 재발 시 기사</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH22</td><td style="padding:8px;">실외 CT 과전류 — 압축기 과부하</td><td style="padding:8px;color:#dc2626;font-weight:600;">실외기 통풍 확인 후 재발 시 기사</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH23</td><td style="padding:8px;">DC 링크 저전압 — 전원 불안정</td><td style="padding:8px;">차단기 리셋 / 전원 점검</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH38</td><td style="padding:8px;">냉매 부족·누설 감지</td><td style="padding:8px;color:#dc2626;font-weight:600;">기사 점검 필요(냉매 작업)</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH90·CH91</td><td style="padding:8px;">설치·시운전 배관 연결 비정상 (F4)</td><td style="padding:8px;color:#dc2626;font-weight:600;">설치 업체 배관 점검</td></tr></tbody></table>

> ⚠️ **CH38·CH90·CH91**은 냉매·배관 작업이 필요해요. 특히 **설치·이전 직후 CH90/CH91**이면 시운전 배관 문제일 수 있으니, 무리하게 돌리지 말고 설치 업체나 서비스센터에 점검을 요청하세요.

> 📌 이 외에 **CH150·CH237·CH238** 같은 코드는 제품·연식마다 의미가 달라요. 모델명과 함께 LG전자 서비스센터에 확인하는 게 정확합니다.

## ☎️ LG전자 서비스센터

자가조치로 안 되거나 압축기·냉매 코드가 반복되면 공식 채널을 이용하세요.

- **대표 전화**: **1544-7777** (운영시간 변동될 수 있음)
- **온라인 예약·스스로 해결**: LG전자 고객지원(lge.co.kr)
- 문의 전 **모델명**(실내기 옆면·아래 라벨)과 **뜬 CH 코드**를 메모해두면 빨라요.

## 🔍 [FAQ] 자주 묻는 질문

**Q. CH05가 떴는데 차단기를 내려도 계속 떠요.**
A. 차단기를 5분 이상 내렸다 올렸는데도 반복되면, 실내외 통신선 접촉 불량이나 실외기 전원 문제일 수 있어요. 이 경우 서비스 점검을 받는 게 좋아요.

**Q. CH38은 직접 고칠 수 있나요?**
A. CH38은 냉매 부족·누설이라 전문 장비가 필요해요. 무리하게 계속 돌리면 압축기가 상할 수 있으니 점검을 권해요.

**Q. 'CH'가 무슨 뜻이에요?**
A. Check(점검)의 약자예요. 뒤 숫자가 이상 부위(센서·통신·압축기)를 가리켜요.

**Q. 설치하자마자 CH90/CH91이 떴어요.**
A. 설치·시운전 단계 배관 연결 문제예요. 사용자 조치보다 설치 업체에 배관 재점검을 요청하는 게 맞아요.

## 🏁 정리: CH05는 리셋부터, 냉매·설치는 점검

LG 에어컨 CH 코드는 **통신·센서 계열(CH01~CH10, CH53)** 과 **압축기·냉매 계열(CH21~CH38, CH90/91)** 로 나눠 보면 쉬워요. 통신·센서는 **차단기 5분 리셋**으로 대부분 해결되고, **CH38·CH90·CH91처럼 냉매·배관 코드는 무리하지 말고 점검**받는 게 안전해요.

> ⚠️ 본 글의 코드·조치는 LG전자 고객지원 안내(작성 시점 2026년 6월) 기준이며, 모델·연식에 따라 다를 수 있어요. 정확한 진단은 모델명·코드와 함께 [LG전자 고객지원](https://www.lge.co.kr/support) 또는 1544-7777로 확인하세요.

## 🛒 [함께 보면 좋은 글]

- [삼성 에어컨 에러코드 총정리 (E101·E461)](https://sancho216.tistory.com/863)
- [LG 냉장고 에러코드 총정리](https://sancho216.tistory.com/entry/LG-냉장고에러코드-유형1F-FF-rF-CF-CO-FS-r5-d5-H5-55-rt-lt-9F-dH-Od-CH-CL-ld-UC-5d-CI-95-dr-IL-AS-Ad-P5-OFF-원인-과-해결책을-알아보자)
- [LG 드럼 세탁기 에러코드 (LE·IE·OE·UE·dE)](https://sancho216.tistory.com/entry/LG-드럼-세탁기-에러코드LE-IE-OE-UE-dE-dE1-dE2-tE-v5-u5-dHE-PE-FE-LOE-FF-uS1-Cd-CL-LCI-CF-Ed1-Ed2-Ed3-Ed4-Ed5-OPn-원인과-해결방법을-찾아보자)
