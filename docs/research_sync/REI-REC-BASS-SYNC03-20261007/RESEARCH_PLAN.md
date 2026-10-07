# 조정된 연구계획과 실행 경계

## 즉시 채택할 변화

1. F08 paired plot 및 CR F04E를 완료로 취급한다. 새로 완료한 F08→BASS 수신과 조건부 τ 전파를 다시 구현하지 않는다.
2. HE의 새 IGM [1000,10000]K 점별 domain을 이용한다. Hot S0의 RCT ON으로 이 승인을 전용하지 않는다. HH는 ACTIVE 연구 lane이며 S0 OFF와 양립한다.
3. T0/T1/T2의 integrated Δτ 부호는 조건부 endpoint 함수에서 양수다. T2 source box 반폭이 마지막 refinement 변화보다 약309배 크지만, 이는 아직 정량화하지 않은 연속/물리 오차보다 크다는 뜻이 아니다. T3 전체 캠페인 재실행을 자동 다음 단계로 두지 않는다.
4. 코드 이월은 완성된 source-pinned 수신·분석 스크립트의 호환성 점검과 실행부터 시작한다. 새 solver 또는 새 원자 provider를 재설계하지 않는다.

## 현재 owner와 겹치지 않는 병렬 작업

| ID | 필요한 입력 | 수행/산출물 | 수락조건 | 상태 |
|---|---|---|---|---|
| P-IGM-EXPORT | PR84의 이미 통과한 short IGM history, 실제 nH/He fractions/time source contract | 보존 이력에서 proper ne SI/normal-time adapter CSV + hashes 생성 | 실제 density/fraction 계산법, nHe convention, 출력시각, physical/model guard 보존. 새 solver 실행 없음. | READY: source inspection/export only |
| P-IGM-OBSERVER | P-IGM-EXPORT 반환 | 이번 실제 BASS 소비자 재사용; τ/cell mass·공통 tail stress·독립 적분 | source-specific 단위/clock/observer/tail 승인 후 실행, full EoR 명칭 금지 | WAIT_INPUT |
| P-OBSERVER-SURFACE | F08 실제 a_i=exp(H_i t), ray/observer authority | 동일 normal-time 결과와 동일 observed-redshift terminal surface 비교의 이론·입력 계약 | D와 redshift surface를 분리; normal clock에서 방향 의존 opacity를 꾸며내지 않음 | READY_THEORY; actual sky run requires authority |
| P-OPTIONAL-NE | HE/CR/HH 최신 반환·실제 ON/OFF 이력 schema | nH·δxHII+nHe·(δxHeII+2δxHeIII) species budget 및 receiver acceptance 파일 | RCT 직접 electron source0과 feedback0 구분; HII 양의 부호만으로 총 ne 부호 주장 금지 | READY_CONTRACT; actual ON history WAIT_OWNER |
| P-TIME-ERROR | 이력 해상도 표·현재 root/step certificate의 정확한 scope | endpoint functional과 continuum observable 사이의 필요한 defect/regularity 조건 목록 | 기존 시간오차 gate/tolerance 유지; 새 certificate 없이 차이를 bound로 부르지 않음 | READY_AUDIT; closure WAIT_EVIDENCE |
| P-QV-CLOSURE | 현재 homogeneous local fraction 정의 및 선택할 two-phase source/sink convention | local ionization fraction과 volume filling-factor의 구분·FLRW closure acceptance 명세 | 실제 closure를 정하지 않은 xHII→QV rename 금지; rate/photon budgets의 중복계수 검사 | READY_THEORY; no new solver |

한 작업이 다른 작업의 반환을 필요로 하면 DAG edge를 따른다. READY는 완성/물리 승인이라는 뜻이 아니다. 각 작업은 실제 source pin·출력·claim ceiling을 고정한 뒤 별도 작은 PR로 진행할 수 있다.

추가 독립 후보 `P-HE-REFERENCE-OBSERVER`: 새 HE RCT02의 봉인된 23 기준 이력 ZIP을 identity 검증해 읽고, 실제 저장된 ON/OFF ne 이력을 이 observer consumer에 전달한다. Native receiver RCT03를 대신 구현하지 않는다. 저장된 실제 history byte를 확보한 뒤에만 실행하며, 결과는 manufactured reference model scope로 유지한다.

## 기존 owner에게 남기는 경로

| Owner 경로 | 다음 산출물 | 본 작업의 경계 |
|---|---|---|
| REI SPEC | FT_SPEC_BRIDGE02의 기존 F08 schedule/cohort admission | 원 SPEC/native source 및 production core 변경 없음 |
| REI IGM | continuous boundary와 coupled midpoint의 긴 이력 gate | 공개 branch84 결과를 읽고 export만 수행 가능 |
| HE | HE-FAST-IGM-RCT03: 실제 receiver native 연결. RCT02 native RHS 기준 이력 23개는 이미 완료 | point 검증 재실행/새 적분기 구현 안 함 |
| CR | prepared photon bridge owner import·실제 history load/callback counts | F04E 재수행 금지; scoped0과 global null 유지 |
| HH | ON06의 일관된 native point/thermal/interval/root/model/checkpoint | OFF certificate를 ON에 붙이지 않음 |
| BASS PR133 | native boundary gain·현재 build integration | full build 작업 복제 안 함; 이번은 isolated exact modules |

## Mid/long-term 원자 lane

원래 BASS_HE 독립 원자 계산, bass_cr 원 source/operator/derivative/production qualification, WU088_HH basis/ladder/physical rate gate는 보존한다. 과거 문서/실패/backup 상태를 고치거나 삭제하지 않는다. 이번 패킷의 `intake/atomic` 및 각 저장소 handoff가 정확한 현재 pin과 원 gate를 연결한다. 종전 SYNC02 immutable archive `rei_bianchi@7c5469101f8d6ef027c8c3119cc5c053e15ba1d9`도 유지한다.

장기 lane 결과를 fastest lane으로 가져올 때는 provider identity → domain/units → local rate parity → solver-stage budget → paired history → observer consumer 순으로 별도 admission한다. 기존 baseline은 해당 admission을 기다리지 않는다. 원본 연구를 호출할 때는 task ID/source pin/계산 범위/기존 실패 gate/실행 자원을 먼저 고정한다.

## 완료와 남은 문턱

현재 새 그림은 이용 가능하다. 다음 physical scientific plot에는 physical sources/ICs, 시간 적분 오차, observer tail 및 필요한 Thomson finite-temperature authority가 필요하다. 이번 수신 결과만으로 완료일을 확정하지 않는다. 실제 ChatGPT 스레드의 read/execute ACK도 저장소 게시와 별도로 남긴다.
