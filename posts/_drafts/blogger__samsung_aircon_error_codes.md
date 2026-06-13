---
title: 삼성 에어컨 에러코드 완벽 가이드 — E101·E461 자가진단부터 100·200·400번대 전체 코드표까지
platform: blogger
category: 생활·정보
tags: ['삼성에어컨', '에어컨에러코드', 'E101', 'E461', 'E422', '무풍에어컨', '에어컨고장', '자가수리', '삼성전자서비스']
date: 2026-06-13
status: draft
source: 삼성전자서비스 공식 솔루션(samsungsvc.co.kr) 100·200·400번대 점검코드 + E101/E461 공식 솔루션
---

한여름 에어컨을 켜자마자 디스플레이에 **E101·E461** 같은 코드가 뜨고 냉방이 멈추는 일은 생각보다 흔하다. 다행히 삼성 에어컨 에러코드의 상당수는 통신·센서의 일시적 오류라, **차단기를 1분간 내렸다 올리는 것만으로 풀리는 경우**가 많다. 문제는 어떤 코드가 셀프 조치로 끝나고 어떤 코드가 전문 기사를 불러야 하는지 구분하기 어렵다는 점이다.

이 가이드는 **삼성전자서비스 공식 점검코드(samsungsvc.co.kr)** 를 기준으로, 삼성 에어컨 에러코드를 **100·200·400번대와 구형 코드**로 나눠 정리한다. 각 코드의 의미·원인·자가조치·기사 호출 필요 여부를 한 번에 확인할 수 있게 구성했고, 무풍·벽걸이·스탠드·시스템 에어컨을 모두 포함한다.

<div style="border-left:5px solid #2563eb;background:#eff6ff;padding:16px 20px;margin:20px 0;border-radius:8px;font-size:14px;"><b>📌 코드를 읽기 전 알아둘 것</b><br>삼성 에어컨은 <b>E(Error)와 C(Check)를 같은 의미로 병용</b>한다(예: E101 = C101). 2014년 이전 구형은 <b>한 자리(E1)</b>, 이후 인버터·무풍 모델은 <b>세 자리(E101)</b> 체계다. 아래 내용은 공식 점검코드 기준이지만, <b>냉매·전기 작업이 필요한 코드는 반드시 전문 기사</b>에게 맡겨야 한다.</div>

{{broker:aircon_header}}

## 코드를 찾기 전: 기본 리셋 3단계 (대부분 여기서 끝난다)

특정 코드를 검색하기 전에, 통신·센서의 일시 오류는 아래 기본 조치만으로 사라지는 경우가 많다. 순서대로 시도해 보자.

1. **전원(차단기) 리셋** — 분전반(두꺼비집)에서 '에어컨' 또는 '실외기' 차단기를 내리고 **1분 이상 기다린 뒤** 다시 올린다. E101·E201·E154·E121 등 통신·센서 계열 코드의 상당수가 이 단계에서 해소된다.
2. **스마트 리셋(2017년 이후 모델)** — 실내기를 향해 리모컨의 **[확인] + [바람세기 ▽]** 를 동시에 4초 이상 누른다.
3. **실외기·필터 점검** — 실외기 좌우·뒤로 15cm 이상 공간을 확보하고(갤러리형은 창을 연다), 실내기 필터를 분리해 청소한다.

:::stat 코드 찾기 전, 이것부터
70% | 통신·센서 코드 자가해결
1분 | 차단기 내렸다 올리기
3단계 | 기사 부르기 전 기본 조치
:::

> 📌 위 3단계 후에도 같은 코드가 다시 뜬다면, 그때 아래 코드별 표를 보고 기사 호출 여부를 판단하면 된다.

## 자주 뜨는 삼성 에어컨 에러코드 요약표

가장 빈번한 코드만 먼저 추렸다. 전체 번대별 코드는 아래 섹션에서 이어진다.

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">자가조치</th><th style="padding:9px;text-align:center;">기사필요</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E101</td><td style="padding:8px;">실내기↔실외기 통신 불량 (가장 흔함). 실외기 전원 차단·케이블 접촉 불량</td><td style="padding:8px;">차단기 1분 내렸다 올리기 → 스마트 리셋</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E121</td><td style="padding:8px;">실내 온도센서(ROOM) 단선·이탈</td><td style="padding:8px;">전원코드 분리 후 재연결 / 차단기 리셋</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E154</td><td style="padding:8px;">실내기 팬모터(크로스팬) 이상. 회전 불량·이물질 간섭</td><td style="padding:8px;">차단기 리셋 + 팬 주변 이물질 확인</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E201</td><td style="padding:8px;">실외기에 설정된 실내기 대수와 실제 연결 대수 불일치 (멀티형)</td><td style="padding:8px;">차단기 내렸다 올려 초기화</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E221</td><td style="padding:8px;">실외기 외부 온도센서 이상</td><td style="padding:8px;">실외기/실내기 전원 재연결 또는 차단기 리셋</td><td style="padding:8px;text-align:center;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E422</td><td style="padding:8px;">고압배관 서비스밸브 막힘·냉매 흐름 이상. 밸브 잠김·냉매 누설·부족</td><td style="padding:8px;">전원 1분 차단 후 재연결(초기화)</td><td style="padding:8px;text-align:center;font-weight:700;color:#dc2626;">○ 필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E461</td><td style="padding:8px;">실외기 압축기 과부하·과전류로 자동 정지. 인버터 컴프 기동 실패</td><td style="padding:8px;">차단기 1분 리셋 → 스마트 리셋</td><td style="padding:8px;text-align:center;font-weight:700;color:#dc2626;">재발 시 ○</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CF</td><td style="padding:8px;">필터 청소 알림 (에러 아님, 정기 알림)</td><td style="padding:8px;">필터 분리·세척 후 전원 리셋</td><td style="padding:8px;text-align:center;">불필요</td></tr></tbody></table>

> 📌 **E101**은 여름 첫 가동 때 가장 많이 뜨는 코드다. 겨우내 꺼뒀던 실외기와의 통신이 일시적으로 어긋난 경우가 많아, 차단기 리셋 한 번으로 끝나는 사례가 대부분이다.

## 100번대: 실내기 통신·센서 코드

100번대는 주로 **실내기 쪽 통신·센서·팬모터** 관련이다. 대부분 전원 리셋으로 1차 해소된다.

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">자가조치</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E101</td><td style="padding:8px;">실내기↔실외기 통신 불량</td><td style="padding:8px;">차단기 1분 리셋 / 스마트 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E102·E103</td><td style="padding:8px;">실내기 표시부와 메인 회로 통신 불가</td><td style="padding:8px;">전원코드 분리 10초 후 재연결</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E116</td><td style="padding:8px;">냉매 누설 감지 센서 불작동</td><td style="padding:8px;">전원 재연결 / 차단기 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E121</td><td style="padding:8px;">실내 온도센서 단선·합선·이탈</td><td style="padding:8px;">전원 재연결 / 차단기 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E122·E123</td><td style="padding:8px;">실내기 열교환기 입·출구 온도센서 이상</td><td style="padding:8px;">전원 재연결 / 차단기 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E154</td><td style="padding:8px;">실내기 팬모터 이상 (회전 불량·간섭)</td><td style="padding:8px;">차단기 리셋 + 팬 이물질 확인</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E161</td><td style="padding:8px;">한 실외기의 실내기들이 냉방·난방을 동시에 다르게 운전</td><td style="padding:8px;">모든 실내기를 같은 모드로 통일</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E184</td><td style="padding:8px;">수위 감지 센서 이상 (물통 감지 오류)</td><td style="padding:8px;">물통 완전히 삽입·고정, 거름망 청소</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E192</td><td style="padding:8px;">실내기 커버가 열린 채 작동 감지</td><td style="padding:8px;">전원 끄고 커버 닫은 뒤 재연결</td></tr></tbody></table>

## 200번대: 실외기 통신·센서 코드

200번대는 **실외기와 실내기 사이, 또는 실외기 자체의 통신·센서** 문제다. 멀티(여러 대)·시스템 에어컨에서 자주 나타난다.

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">자가조치</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E201</td><td style="padding:8px;">설정된 실내기 대수와 실제 연결 대수 불일치</td><td style="padding:8px;">차단기 내렸다 올려 초기화</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E202</td><td style="padding:8px;">실외기↔실내기 신호 불통 (멀티형)</td><td style="padding:8px;">차단기 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E203</td><td style="padding:8px;">실외기 2대 이상 설치 시 실외기 간 신호 불통</td><td style="padding:8px;">차단기 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E221</td><td style="padding:8px;">실외기 외부 온도센서 이상</td><td style="padding:8px;">전원 재연결 / 차단기 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E251</td><td style="padding:8px;">압축기 토출 가스 온도센서 이상</td><td style="padding:8px;">차단기 리셋</td></tr></tbody></table>

> 📌 인테리어 공사나 이사 후 첫 가동에서 **E201·E202**가 자주 보인다. 실외기를 떼었다 다시 연결하는 과정에서 설정이 어긋난 경우가 많으니, 차단기 리셋 후에도 지속되면 설치 업체에 문의하는 편이 빠르다.

## 400번대: 냉매·압축기 코드 (전문 점검 구간)

400번대는 **실외기 작동, 냉매, 압축기** 관련으로, 자가조치로 풀리지 않으면 **전문 기사 점검이 필요한 경우가 많은** 구간이다.

{{broker:aircon_outdoor}}

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미 / 원인</th><th style="padding:9px;text-align:left;">자가조치 / 비고</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E400</td><td style="padding:8px;">실외기 압축기 제어 회로 온도센서 이상</td><td style="padding:8px;">차단기 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E401~E403</td><td style="padding:8px;">실외기·실내기 열교환기 성에·결빙</td><td style="padding:8px;">성에 자연해동 대기 후 재가동</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E404~E406</td><td style="padding:8px;">실외기 열교환기 온도센서 이상</td><td style="padding:8px;">실외기 주변 장애물 제거, 갤러리 창 개방</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E422</td><td style="padding:8px;">고압배관 서비스밸브 막힘·냉매 흐름 이상. 밸브 잠김·냉매 부족</td><td style="padding:8px;color:#dc2626;font-weight:600;">초기화 후 재발 시 기사 필요(냉매 작업)</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E425~E427</td><td style="padding:8px;">3상 4선식 380V 전원 연결 오류</td><td style="padding:8px;color:#dc2626;font-weight:600;">전기공사업체 점검 필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E440</td><td style="padding:8px;">실외 30℃ 이상에서 난방 운전 시도 (보호 동작)</td><td style="padding:8px;">운전 모드를 냉방으로 변경</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E461</td><td style="padding:8px;">압축기 과부하·과전류로 자동 정지</td><td style="padding:8px;color:#dc2626;font-weight:600;">차단기 리셋 후 재발 시 기사 필요</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E464·E465</td><td style="padding:8px;">IPM 과전류 / 압축기 과전류 차단</td><td style="padding:8px;color:#dc2626;font-weight:600;">차단기 리셋 후 재발 시 기사 필요</td></tr></tbody></table>

> ⚠️ **E422·E461·E464·E465**는 냉매·압축기·전기 계통과 직접 연관된다. 차단기 리셋으로 한두 번 풀리더라도 **반복된다면 부품 점검이 필요한 신호**다. 무리하게 계속 가동하지 말고 서비스 점검을 받는 편이 기기 수명과 안전에 좋다.

## 구형 모델 코드: E1·CF·CL

2014년 이전 벽걸이·창문형 모델에서 보이는 코드다.

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:center;">코드</th><th style="padding:9px;text-align:left;">의미</th><th style="padding:9px;text-align:left;">자가조치</th></tr></thead><tbody><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">E1</td><td style="padding:8px;">실내 온도센서 이상 (단선·오작동)</td><td style="padding:8px;">전원코드 분리 1분 후 재연결 / 스마트 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CF</td><td style="padding:8px;">필터 청소 알림 (에러 아님)</td><td style="padding:8px;">필터 세척 후 전원 리셋</td></tr><tr><td style="padding:8px;text-align:center;font-weight:700;background:#f1f5f9;">CL</td><td style="padding:8px;">자동 청소·건조 진행 중 (에러 아님)</td><td style="padding:8px;">완료까지 대기 (자동 전원 오프)</td></tr></tbody></table>

> 📌 일부 모델에서 **E3·E4·E5** 등이 보고되지만, 이는 모델·연식에 따라 의미가 다를 수 있다. 정확한 의미는 제품 모델명과 함께 삼성전자서비스에 확인하는 것이 안전하다.

## 표시등 깜빡임으로 에러를 알리는 모델 (코드 미표시형)

디스플레이가 없거나 숫자 코드 대신 **전원·운전·필터 같은 표시등(LED)이 깜빡이는** 벽걸이·시스템 모델도 있다. 이때는 깜빡이는 위치와 패턴으로 원인을 좁힐 수 있다(삼성전자서비스 공식 기준).

<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"><thead><tr style="background:#1e293b;color:#fff;"><th style="padding:9px;text-align:left;">깜빡임 패턴</th><th style="padding:9px;text-align:left;">의미</th><th style="padding:9px;text-align:left;">조치</th></tr></thead><tbody><tr><td style="padding:8px;">전원·시스템 외 다른 램프가 깜박</td><td style="padding:8px;">일시적 오동작</td><td style="padding:8px;">차단기 내리고 10초 후 다시 올리기</td></tr><tr><td style="padding:8px;">전체 램프가 함께 깜박</td><td style="padding:8px;">정전·전원 불안정으로 설정값이 지워짐</td><td style="padding:8px;">차단기 리셋 후 모드·온도 재설정</td></tr><tr><td style="padding:8px;">램프 3개가 번갈아 점멸 / <b>'88' 점멸</b></td><td style="padding:8px;">설치 후 스마트 인스톨(자동 설정) 미완료</td><td style="padding:8px;color:#dc2626;font-weight:600;">설치 업체에 스마트 인스톨 요청</td></tr><tr><td style="padding:8px;">필터 램프 하나만 깜박</td><td style="padding:8px;">혼용 운전(냉·난방 동시) — 고장 아님</td><td style="padding:8px;">모든 실내기를 같은 모드로 통일</td></tr><tr><td style="padding:8px;">전원 램프 외 깜박임이 지속</td><td style="padding:8px;">제품 이상 감지</td><td style="padding:8px;">서비스 점검</td></tr></tbody></table>

> 📌 **'88'이 깜빡이거나 램프 3개가 번갈아 점멸**하는 것은 고장이 아니라 설치 마무리(스마트 인스톨)가 안 된 경우가 많다. 새로 설치·이전한 직후라면 설치 업체에 문의하는 편이 빠르다.

## 해결이 안 될 때: 삼성전자서비스 접수

자가조치로 풀리지 않거나 400번대 코드가 반복된다면 공식 채널을 이용한다.

- **대표 전화**: **1588-3366** (평일 09:00~18:00, 토 09:00~13:00 — 운영시간은 변동될 수 있음)
- **출장 서비스 예약**: 삼성전자서비스 홈페이지(samsungsvc.co.kr) → 출장 서비스 예약
- **AI 챗봇 상담**: 홈페이지에서 24시간 운영
- 접수 전 **제품 모델명**(실내기 옆면·아래 라벨)과 **표시된 코드**를 메모해두면 상담이 빨라진다.

## 자주 묻는 질문 (FAQ)

**Q. E101이 떴는데 차단기를 내려도 계속 떠요.**
A. 차단기 리셋과 스마트 리셋을 모두 시도했는데도 반복된다면, 실내기·실외기 사이 통신선 접촉 불량이나 실외기 전원 문제일 수 있다. 이 경우 서비스 점검을 받는 것이 좋다.

**Q. E461이 떴어요. 계속 켜도 될까요?**
A. E461은 압축기 과부하·과전류로 자동 정지된 상태다. 차단기 리셋으로 일시 복구될 수 있지만 반복된다면 압축기·인버터 점검이 필요하다. 무리하게 재가동하면 부품 손상으로 이어질 수 있으니 반복 시 점검을 권한다.

**Q. 'CF'와 'CL'도 고장인가요?**
A. 아니다. CF는 **필터 청소 시기 알림**, CL은 **자동 청소·건조 진행 중** 표시다. CF는 필터를 세척해 말린 뒤 다시 끼우고 전원을 리셋하면 사라지고, CL은 완료될 때까지 기다리면 된다.

**Q. 에러코드 없이 냉방이 약할 때는요?**
A. 코드가 없다면 필터 막힘, 실외기 주변 통풍 불량, 설정 온도부터 확인한다. 그래도 냉방이 약하면 냉매 부족(E422 계열) 가능성이 있어 점검이 필요하다.

**Q. 스마트 리셋은 모든 모델에서 되나요?**
A. 주로 2017년 이후 인버터·무풍 모델에서 [확인]+[바람세기 ▽] 동시 입력으로 작동한다. 모델에 따라 방법이 다를 수 있으니, 안 되면 차단기 리셋을 이용한다.

**Q. 코드는 안 뜨고 표시등만 깜빡입니다.**
A. 디스플레이가 없는 벽걸이·시스템 모델은 LED 깜빡임으로 상태를 알린다. 전원·시스템 외 램프가 깜박이면 차단기를 내리고 10초 뒤 올려본다. 전체 램프가 깜박이면 정전으로 설정이 지워진 경우가 많고, **램프 3개가 번갈아 점멸하거나 '88'이 깜박이면** 설치 시 스마트 인스톨이 안 된 상태라 설치 업체에 인스톨을 요청하면 된다.

## 정리: 리셋부터, 반복되면 점검

삼성 에어컨 에러코드는 겁먹을 필요가 없다. **① 차단기 1분 리셋 → ② 스마트 리셋 → ③ 실외기·필터 확인** 세 단계만으로 통신·센서 계열 코드의 대부분이 해결된다. 다만 **E422·E461처럼 냉매·압축기 관련 코드가 반복**된다면 무리하게 가동하지 말고 서비스 점검을 받는 것이 기기 수명과 안전을 위해 낫다.

> ⚠️ 본 글의 에러코드·조치는 삼성전자서비스 공식 점검코드(작성 시점 2026년 6월)를 기준으로 정리했다. 모델·연식에 따라 코드 의미가 다를 수 있으므로, 정확한 진단은 제품 모델명과 함께 [삼성전자서비스](https://www.samsungsvc.co.kr/) 또는 1588-3366으로 확인하기 바란다. 냉매·전기 작업은 반드시 전문 기사에게 맡겨야 한다.

## 함께 보면 좋은 글

- [LG 에어컨 CH 에러코드 완벽 가이드 (CH05·CH38)](https://consistency.onestepblog.info/2026/06/lg-ch-ch05ch38.html)
- [캐리어 에어컨 에러코드·깜빡임 자가진단 (EC·E1·E5)](https://consistency.onestepblog.info/2026/06/ece1e5.html)
- [위니아(딤채) 에어컨 에러코드 (E1·E3·E4)](https://consistency.onestepblog.info/2026/06/e1e3e4.html)
