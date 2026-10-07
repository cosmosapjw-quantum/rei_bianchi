# SYNC03 HE: 새 IGM RCT와 실제 F08 관측량 수신의 연결

[중앙 정본](../../../README_KO.md) · [기계 판독 상태](SYNC_STATE.json). 이 파일은 수신용 additive handoff이며 원 owner CURRENT 상태와 코드는 변경하지 않는다. 게시와 수신자의 실행 ACK는 별개이고, 직접 채팅 전달 및 recipient execution ACK는 아직 완료되지 않았다.

수신한 원자 source pin은 `eae1d2209fd9a555bea461032f272c7c7c19766e`, branch `research/shared-c64-crossrepo-20260928`, PR 17다. 초기 intake 이후 최신 관측 pin은 `9b46aab79eeafd452a5fb35b1c0fd00eef6f5683`이며 component는 `HE-FAST-IGM-RCT02`, gate는 `BOUNDED_COMMON_DOMAIN_NATIVE_RHS_HISTORY_CHECKED__RECEIVER_INTEGRATION_OPEN`다. 원 intake pin은 루프2의 고정 입력으로 유지한다.

## 새 두 연구 루프의 완료 범위

실제 F08의 T0/T1/T2 × FLRW/BI 여섯 이력, 112,000 cells를 원 BASS cold-Thomson source module에 연결했고 독립 Decimal 검사 784,054개가 PASS다. REI 입력 pin `84afbe7660ec79e5e43822e7aea49a0a9ee8daea`, BASS source pin `1e45e0f48cd83dcb21c23d4087fa5526195331d7`다. `D=1`, proper ne, normal seconds를 사용했다. 각 cell은 endpoint-linear opacity의 적분과 동등한 평균-opacity 표현이고, 실제 관측자까지의 tail은 제공되지 않아 유한 구간 tail=0 및 별도 0.1 진단만 계산했다. 전체 BASS build나 production routing 완료를 뜻하지 않는다.

그 수신 계약을 동기화한 다음, 원 supplier의 simultaneous discrete endpoint box를 전제로 같은 유한 선형 관측량을 Decimal90 방향반올림으로 전파했다. T2의 `tau_BI-tau_FLRW = 3.44222649358e-12`, 조건부 구간은 `[3.25112367913e-12, 3.63332930801e-12]`다. 이 유한 관측량의 조건부 부호는 양수지만 연속 이력의 부호·물리적 관측 신호는 인증하지 않았다. Optional RCT/HH/CR ON 계산을 새로 실행하지 않았다.

## 최신 결과와 과거 상태의 관계

Root CURRENT_FASTEST_STATE retains old HE-F2C and F08 NOT_EXECUTED fields. Read newer additive HE-FAST-REJOIN01 and actual F08 return; retain old document as history.

완료된 원자 구성요소:

- current IGM plus separate RCT point API, 13 native tests, 56 points
- new IGM operational common domain [1000,10000] K
- STEP06 current library build at recorded source pin

## 게시 직전 HE02 완료와 다음 owner 단위

추가 commit `9b46aab79eeafd452a5fb35b1c0fd00eef6f5683`은 source-free 제조 IGM의 공통영역 기준 이력을 완료했다. 원 native RHS를 DOP853/Radau로 적분한 23 solve, 960 accepted time steps, native 과학 평가14,758회를 보고했다. 모든 sampled stage/output/Jacobian probe의 실제 EOS 온도는1939.61987106275..2005.45819027047K다. 이 수신을 위해 재실행하지 않았다. 연속 모든 시각의 엄밀 invariant-domain 증명, 실제 receiver integration, physical admission은 아니다.

이제 예약할 작업은 `HE-FAST-IGM-RCT03_RECEIVER_NATIVE_INTEGRATION`이다. 기존 source-free 기준 이력과 현재 owner `igm_step`을 입력으로 받고 RCT candidate·thermal residual·endpoint·종별 event 및 energy 장부를 동시에 연결한다. 같은 source-free IC/source/Ebar로 비교한 뒤 photon/source 단계를 검증한다. 새로운 generic 적분기나 HE02 기준 이력을 다시 만들지 않는다. 실제 integration 및 affected checks가 반환되기 전 owner adoption을 완료로 세지 않는다. baseline OFF, 원 moment null, source·수치 budget과 physical HOLD는 유지한다.

## 겹치지 않고 병렬로 준비할 단위

`HE-SYNC03-OBSERVABLE-BUDGET`: 입력은 new finite F08->BASS receiver contract; HE existing source domain/closure metadata다. 산출물은 transfer applicability record and future ne uncertainty input schema이며, 아직 optional ON 수치 결과를 만들어냈다고 기록하지 않는다.

수락조건:

- do not transfer new IGM RCT onto hot FT03 F08
- direct electron source zero is not coupled delta-ne zero
- supply stage-valid species perturbation bounds before numeric optional tau bound
- separate source spread, explicit closure and numerical error

## 원래 원자 lane과 주장 한계

HE-L1/L2/L3 PARKED_OPEN; scientific_PROMOTE HOLD; EOR_THEORY_GATE NOT_SATISFIED; Eq55 NOT_RUN; physical nuclear normalization/source moments OPEN; 17-fold KF96/GM25 nominal discrepancy unresolved; HE-F2 global false; HE-F3/F09 incomplete를 보존한다. 기존 source identity·실패·tolerance·소비된 실행권한은 그대로다. 원자 정밀 lane 완결은 이번 baseline 관측량 소비의 선행조건이 아니다. 기존 owner 작업을 복제하거나 완료한 point/source suite를 동기화만을 위해 반복하지 않는다.

최종 Git commit과 Drive/Dropbox 실제 완료 영수증은 root publication 후 연결된다. 이 준비 단계 파일은 미완료 게시·백업·recipient ACK를 성공으로 선기록하지 않는다.

게시 직전 두 원자 delta는 중앙 `publication/LATE_ATOMIC_DELTA.json`에 exact fetched source와 blob/SHA identity로 보존했다. Loop2에 사용한 frozen intake/gate는 바꾸지 않았다.
