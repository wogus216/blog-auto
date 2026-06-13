---
title: LG 에어컨 CH 에러코드 완벽 가이드 — CH05·CH38부터 통신·압축기 코드까지 자가조치 총정리
platform: blogger
category: 생활·정보
tags: ['LG에어컨', '에어컨에러코드', 'CH05', 'CH38', '휘센', '에어컨고장', '자가수리', 'LG전자서비스', '에어컨CH']
date: 2026-06-13
status: draft
source: LG전자 고객지원 스스로해결(lge.co.kr) CH05/CH38/LED 솔루션 + 공식 에러코드 안내
---

LG 에어컨(휘센 포함)을 켰을 때 표시창에 **CH05·CH38** 같은 'CH + 숫자' 코드가 뜨면서 냉방이 멈추는 경우가 있다. LG 에어컨의 **CH 코드는 'Check'의 약자**로, 센서·통신·압축기·냉매 중 어디에 이상이 감지됐는지를 숫자로 알려주는 신호다. 다행히 가장 흔한 **CH05(통신 장애)** 같은 코드는 차단기를 내렸다 올리는 것만으로 풀리는 경우가 많다.

이 가이드는 **LG전자 고객지원(lge.co.kr) 공식 안내**를 기준으로, LG 에어컨 CH 에러코드를 **통신·센서 계열과 압축기·냉매 계열**로 나눠 정리한다. 각 코드의 의미·원인·자가조치·기사 호출 필요 여부를 한 번에 확인할 수 있게 구성했고, 벽걸이·스탠드·시스템(휘센) 에어컨을 모두 포함한다.

<div style="border-left:5px solid #2563eb;background:#eff6ff;padding:16px 20px;margin:20px 0;border-radius:8px;font-size:14px;"><b>📌 CH 코드를 읽기 전 알아둘 것</b><br>LG 에어컨의 <b>CH는 'Check(점검)'</b>를 뜻하며 뒤의 숫자가 이상 부위를 가리킨다. 일부 모델은 같은 통신 오류를 <b>E0</b>로도 표시한다. 통신·센서 계열은 대부분 전원 리셋으로 풀리지만, <b>냉매·압축기·설치 관련 코드(CH38·CH90·CH91 등)는 전문 기사</b> 점검이 필요하다.</div>

{{broker:aircon_header}}

## CH 코드를 찾기 전: 기본 리셋 3단계 (대부분 여기서 끝난다)

특정 코드를 검색하기 전에, 통신·센서의 일시 오류는 아래 기본 조치만으로 사라지는 경우가 많다. LG는 전원 리셋 시 **5분 대기**를 권장한다.

1. **전원(차단기) 리셋** — 분전반에서 '에어컨' 또는 '실외기' 차단기를 내리고 **약 5분 기다린 뒤** 다시 올린다. CH05·CH53 등 통신 계열 코드의 상당수가 이 단계에서 해소된다.
2. **실외기 주변 점검** — 실외기 좌우·뒤로 공간을 확보하고(갤러리형은 창을 연다), 통풍을 막는 장애물을 치운다.
3. **필터 청소** — 실내기 필터를 분리해 세척·건조 후 다시 끼운다. 냉방 약화·결빙 관련 코드 예방에 도움이 된다.

:::stat CH 코드, 이것부터
CH05 | 가장 흔한 통신 장애
5분 | 차단기 내렸다 올리기
2계열 | 통신·센서 vs 압축기·냉매
:::

> 📌 위 조치 후에도 같은 CH 코드가 다시 뜬다면, 아래 코드별 표에서 통신·센서 계열인지 압축기·냉매 계열인지 확인해 기사 호출 여부를 판단하면 된다.

## 자주 뜨는 LG 에어컨 CH 에러코드 요약표

가장 빈번한 코드만 먼저 추렸다. 전체 코드는 아래 계열별 표에서 이어진다.

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">자가조치</th><th style="padding:9px;text-align:center;">기사필요</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH05</td><td style="padding:8px;">실내기↔실외기 통신 장애 (가장 흔함). E0로도 표시. 실외기 전원·통신선 문제</td><td style="padding:8px;">차단기 5분 내렸다 올리기</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH01</td><td style="padding:8px;">실내 온도센서 이상 (단선·이탈)</td><td style="padding:8px;">차단기 리셋</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH10</td><td style="padding:8px;">실내 팬모터 회전 불량 (팬 막힘·고착)</td><td style="padding:8px;">차단기 리셋 + 팬 주변 이물질 확인</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH21</td><td style="padding:8px;">실외 인버터 압축기 DC 과전류. 전원 불안정·압축기 이상</td><td style="padding:8px;">차단기 리셋</td><td style="padding:8px;text-align:center;font-weight:700;color:#dc2626;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH38</td><td style="padding:8px;">냉매 부족·누설 감지. 가스 부족 또는 배관 누설</td><td style="padding:8px;color:#dc2626;font-weight:600;">기사 점검 필요(냉매 작업)</td><td style="padding:8px;text-align:center;font-weight:700;color:#dc2626;">○ 필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH90·CH91</td><td style="padding:8px;">설치·시운전 중 배관 연결 비정상 (F4 동반)</td><td style="padding:8px;color:#dc2626;font-weight:600;">설치 업체에 배관 점검 요청</td><td style="padding:8px;text-align:center;font-weight:700;color:#dc2626;">○ 필요</td></tr></tbody></table>

> 📌 **CH05**는 여름 첫 가동 때 가장 많이 뜨는 코드다. 겨우내 꺼뒀던 실외기와의 통신이 일시적으로 어긋난 경우가 많아, 차단기 리셋 한 번으로 끝나는 사례가 대부분이다.

## 통신·센서 계열 CH 코드 (대부분 리셋으로 해결)

실내기 센서, 리모컨·실내외 통신, 배수 등 **전원 리셋으로 1차 해소되는** 코드들이다.

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">자가조치</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH01</td><td style="padding:8px;">실내 온도센서 이상</td><td style="padding:8px;">차단기 리셋 / 재발 시 점검</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH02</td><td style="padding:8px;">실내 열교환기(배관) 입구 센서 이상</td><td style="padding:8px;">차단기 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH03</td><td style="padding:8px;">리모컨↔실내기 통신 불량</td><td style="padding:8px;">리모컨 배터리 교체 / 전원 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH04</td><td style="padding:8px;">배수(드레인) 펌프 이상 — 응축수 배출 불량</td><td style="padding:8px;">배수 호스 막힘 확인 / 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH05</td><td style="padding:8px;">실내기↔실외기 통신 장애 (E0 동일)</td><td style="padding:8px;">차단기 5분 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH06</td><td style="padding:8px;">실내 열교환기 출구 센서 이상</td><td style="padding:8px;">차단기 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH07</td><td style="padding:8px;">한 실외기의 실내기들이 냉·난방을 다르게 운전 (멀티)</td><td style="padding:8px;">모든 실내기를 같은 모드로 통일</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH10</td><td style="padding:8px;">실내 팬모터 회전 불량 (락·고착)</td><td style="padding:8px;">차단기 리셋 + 팬 이물질 확인</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH53</td><td style="padding:8px;">실내기↔실외기 신호선 통신 이상</td><td style="padding:8px;">차단기 리셋 / 통신선 접촉 확인</td></tr></tbody></table>

## 압축기·냉매 계열 CH 코드 (전문 점검 구간)

실외기 압축기, 냉매, 설치 배관 관련으로 **자가조치로 풀리지 않으면 기사 점검이 필요한** 코드들이다.

{{broker:aircon_outdoor}}

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">자가조치 / 비고</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH21</td><td style="padding:8px;">실외 인버터 압축기 DC 과전류 (IPM)</td><td style="padding:8px;">차단기 리셋 후 재발 시 기사</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH22</td><td style="padding:8px;">실외 CT 과전류 — 압축기 과부하</td><td style="padding:8px;color:#dc2626;font-weight:600;">실외기 통풍 확인 후 재발 시 기사</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH23</td><td style="padding:8px;">DC 링크 저전압 — 전원 불안정</td><td style="padding:8px;">차단기 리셋 / 전원 점검</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH26</td><td style="padding:8px;">압축기 위치센서·기동 이상</td><td style="padding:8px;color:#dc2626;font-weight:600;">재발 시 기사 필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH38</td><td style="padding:8px;">냉매 부족·누설 감지 (가스 부족)</td><td style="padding:8px;color:#dc2626;font-weight:600;">기사 점검 필요(냉매 작업)</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CH90·CH91</td><td style="padding:8px;">설치·시운전 중 배관 연결 비정상 (F4 동반)</td><td style="padding:8px;color:#dc2626;font-weight:600;">설치 업체에 배관 점검 요청</td></tr></tbody></table>

> ⚠️ **CH38·CH90·CH91**은 냉매·배관 작업이 필요한 코드다. 특히 **설치·이전 직후 CH90/CH91**이 뜬다면 시운전 단계의 배관 연결 문제일 가능성이 높으니, 무리하게 가동하지 말고 설치 업체나 서비스센터에 점검을 요청하는 편이 안전하다.

> 📌 위 외에 **CH150·CH237·CH238** 등 제품·연식에 따라 다른 코드가 보일 수 있다. 이런 코드는 모델별로 의미가 달라, 제품 모델명과 함께 LG전자 서비스센터에 확인하는 것이 정확하다.

## LED 램프만 깜빡일 때

디스플레이가 없는 일부 모델은 코드 대신 **운전·타이머 같은 LED 램프 깜빡임**으로 이상을 알린다. 이 경우 우선 차단기를 내리고 5분 뒤 올려본 다음, 같은 깜빡임이 반복되면 제품 모델명과 함께 LG전자 서비스센터에서 깜빡임 패턴의 의미를 확인하는 것이 정확하다.

## 해결이 안 될 때: LG전자 서비스센터

자가조치로 풀리지 않거나 압축기·냉매 계열 코드가 반복된다면 공식 채널을 이용한다.

- **대표 전화**: **1544-7777** (운영시간은 변동될 수 있음)
- **온라인 예약·스스로 해결**: LG전자 고객지원(lge.co.kr)
- 접수 전 **제품 모델명**(실내기 옆면·아래 라벨)과 **표시된 CH 코드**를 메모해두면 상담이 빨라진다.

## 자주 묻는 질문 (FAQ)

**Q. CH05가 떴는데 차단기를 내려도 계속 떠요.**
A. 차단기를 5분 이상 내렸다 올렸는데도 CH05가 반복된다면, 실내기·실외기 사이 통신선 접촉 불량이나 실외기 전원 문제일 수 있다. 이 경우 서비스 점검을 받는 것이 좋다.

**Q. CH38은 직접 고칠 수 있나요?**
A. CH38은 냉매 부족·누설 감지 코드다. 냉매 충전·누설 점검은 전문 장비가 필요해 일반 사용자가 직접 처리하기 어렵다. 무리하게 계속 가동하면 압축기 손상으로 이어질 수 있으니 기사 점검을 권한다.

**Q. 'CH'는 무슨 뜻인가요?**
A. CH는 **Check(점검)**의 약자로, 뒤의 숫자가 이상이 감지된 부위(센서·통신·압축기 등)를 가리킨다. 고장 코드를 빠르게 좁히기 위한 LG 에어컨의 표시 방식이다.

**Q. 설치하자마자 CH90/CH91이 떴어요.**
A. 설치·시운전 단계에서 배관 연결이 정상적으로 끝나지 않으면 뜨는 코드다. 사용자 조치보다 설치 업체에 배관 상태 재점검을 요청하는 것이 맞다.

**Q. 코드는 없고 LED만 깜빡여요.**
A. 디스플레이가 없는 모델은 LED 깜빡임으로 상태를 알린다. 차단기를 5분 리셋해보고, 반복되면 모델명과 함께 LG전자 서비스센터에서 깜빡임 패턴을 확인하면 된다.

## 정리: CH05는 리셋부터, 냉매·설치 코드는 점검

LG 에어컨 CH 에러코드는 **통신·센서 계열(CH01~CH10, CH53)**과 **압축기·냉매 계열(CH21~CH38, CH90/91)**로 나눠 보면 대응이 쉽다. 통신·센서 계열은 **차단기 5분 리셋**으로 대부분 해결되고, **CH38·CH90·CH91처럼 냉매·배관 관련 코드는 무리하게 가동하지 말고 점검**을 받는 것이 기기 수명과 안전에 좋다.

> ⚠️ 본 글의 코드·조치는 LG전자 고객지원 공식 안내(작성 시점 2026년 6월)를 기준으로 정리했다. 모델·연식에 따라 코드 의미가 다를 수 있으므로, 정확한 진단은 제품 모델명과 함께 [LG전자 고객지원](https://www.lge.co.kr/support) 또는 1544-7777로 확인하기 바란다. 냉매·전기 작업은 반드시 전문 기사에게 맡겨야 한다.

## 함께 보면 좋은 글

- [삼성 에어컨 에러코드 완벽 가이드 (E101·E461·100~400번대)](https://consistency.onestepblog.info/2026/06/e101e461-100200400.html)
- [캐리어 에어컨 에러코드·깜빡임 자가진단 (EC·E1·E5)](https://consistency.onestepblog.info/2026/06/ece1e5.html)
- [위니아(딤채) 에어컨 에러코드 (E1·E3·E4)](https://consistency.onestepblog.info/2026/06/e1e3e4.html)
