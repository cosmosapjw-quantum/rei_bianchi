# 외부 source 연산자 및 n/T QSS 진단 — 실행·검토 결과

이 단위는 기존 ANGTHERM01의 같은201개 저장 epoch에서 외부 source 연산자와
유한 slowing/escape를 거친 n/T의 고정 epoch QSS 응답을 구성한다.
검사7개 방법과201 epoch/252열 평가 및 그림 실행이 각1회 완료되었다.
독립 판정은 **PASS_SCOPED**다. 실제 code·raw output·그림을 읽은 별도 저자가
한 번 검토했고 추가 scientific rerun은 하지 않았다.
시간발전 해, 새로운17상태 궤적 또는 보정된 우주론적 abundance를 주장하지 않는다.

새 입력은20/100eV 및5/25MeV의 처방 photon bath, 두 CR proton–He4 채널,
명시한 isotope별 ion 주입 분포, 빠른 n/T 주입과 열적 입자 escape다.
광이온화·광핵반응, 유한 slowing/escape/decay 경쟁, n+H capture,
n/T beta daughter와 전자/중성미자/열/방출광자/내부에너지 장부를 연결한다.
이 bath·cross section·branching·transport hazard·beta 에너지 분배는
예시적이고 비보정된 모형 선택이다. 현실적 매개변수로 검증하지 않았다.
기존 별도 배경257시점의18-family nuclear network는 재사용 비교 근거이며
이번 source와 합쳐 새로운 trajectory로 만들지 않는다.
Inverse-weak bath는 이 모형에 없으며 관련 문헌식 조사만 수행했다.

기준 population CSV와 같은201시점의 실제 nHref를 결속한다.
정규화는 particles/Href, event rate는 events/Href/proper-second다.
주입으로 baryon inventory가 변할 수 있으므로 Href를 현재 총 baryon density로
바꾸지 않는다. LiIV를 포함한17개 thermal state와 별도2개 fast reservoir를
사용하고 숨은4개 Li6 상태와 기존 closure를 보존한다.

대칭성 축은 기존 comoving tetrad에서의 scalar population/rate와
처방 isotropic angle-integrated flux다. Mean z는 저장 epoch의 표지다.
불변량 축은 닫힌 반응의 정수 baryon 수지, spectator/beta 전자를 포함한
charge 수지, 외부 주입/escape의 경계 수지 및 effective Q 에너지 장부다.
관측량 축은 source rate·조건부 stationary stock·배분 power다.
전달함수 없는 광도·관측 spectrum·광학깊이는 도출하지 않는다.
QSS의 실제 유효성에는 source/background 변화시간과 relaxation time 비교가
필요하며 이번 점별 진단은 그 동역학 검증을 대신하지 않는다.

원래 DAG 작업33/88·중앙28/88·증가0, 기존 빠른 경로4/7을 유지한다.
F4의 현상론적 source-model 하위 의무는 **COMPLETE_SCOPED**다.
원래 physical F4 완료 여부는 별도다. 문헌 근거는
`sources/SOURCE_SYNTHESIS.md`, 식과 계약은 `theory/FROZEN_CONTRACT.md` 및
`theory/DERIVATION_AND_DECISION.md`에 있다.

모든 bounded phase는 exit0이며 alpha0/1/10 응답을 기록했다.
기준 CSV/NPZ 결속과201 eta 정렬을 확인했고 실제 저장 nHref의 양 끝은
0.0017668803778189406 및5.151254745827818e-06 cm^-3다.
합성 밀도법칙으로 바꾸지 않았다. 최대 상대 baryon 잔차2.01410e-16,
charge8.17640e-16, effective-energy3.55698e-16, QSS8.52601e-17이다.
이 값은 실행된 내부 모형 검사이며 물리적 calibration 판정은 아니다.

실제 child+관측 wrapper debit은 planning0.909208, presentation1.155837 CPU초다.
추가 tail reserve1/0.5를 포함한 누적은19.204540885/56.217331494이며
원래 cap10/30으로 복귀했다. 자세한 원기록은 BUDGET_CLOSEOUT.json이다.
입수·저작·metadata 등 미계측 비용 UNKNOWN_NOT_ZERO는 보존한다.
Controller가 짧은 pwd/read 환경 접근 실패 뒤 복구를 관찰했으며 과학 실행은
영향받지 않았다. 이는 환경 상태이며 physics failure가 아니다.
독립 판정은 review/DECISION.json 및 REVIEW.md에 보존했다.
eta 정렬은 절대5e-15 serialization tolerance 이내이며 byte/exact equality 주장이 아니다.
메타데이터의 eta_exact_alignment 이름은 eta_serialization_alignment_pass로
한 번 고쳤고 원 JSON·raw stdout·CSV·PNG를 보존했다. 수치 재실행은0이다.
실제 최종 게시/백업 ACK는 DELIVERY_RECEIPT.json에 후속 기록한다.

