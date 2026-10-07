# SYNC03 HH: ACTIVE 연구 상태와 조건부 전자밀도 전달의 연결

[중앙 정본](../../../README_KO.md) · [기계 판독 상태](SYNC_STATE.json). 이 파일은 수신용 additive handoff이며 원 owner CURRENT 상태와 코드는 변경하지 않는다. 게시와 수신자의 실행 ACK는 별개이고, 직접 채팅 전달 및 recipient execution ACK는 아직 완료되지 않았다.

수신한 원자 source pin은 `47accb0b3ac9adca40913dc06c797a509c1a7b49`, branch `research/r31ao-unequal-order-ladder-20260930`, PR 33다. 최신 component는 `HH-TH05-20261007`, gate는 `STRICT_HH_IONIZATION_ORDER_AND_POSITIVE_OPTICAL_MEMORY_ENCLOSED`다.

## 새 두 연구 루프의 완료 범위

실제 F08의 T0/T1/T2 × FLRW/BI 여섯 이력, 112,000 cells를 원 BASS cold-Thomson source module에 연결했고 독립 Decimal 검사 784,054개가 PASS다. REI 입력 pin `84afbe7660ec79e5e43822e7aea49a0a9ee8daea`, BASS source pin `1e45e0f48cd83dcb21c23d4087fa5526195331d7`다. `D=1`, proper ne, normal seconds를 사용했다. 각 cell은 endpoint-linear opacity의 적분과 동등한 평균-opacity 표현이고, 실제 관측자까지의 tail은 제공되지 않아 유한 구간 tail=0 및 별도 0.1 진단만 계산했다. 전체 BASS build나 production routing 완료를 뜻하지 않는다.

그 수신 계약을 동기화한 다음, 원 supplier의 simultaneous discrete endpoint box를 전제로 같은 유한 선형 관측량을 Decimal90 방향반올림으로 전파했다. T2의 `tau_BI-tau_FLRW = 3.44222649358e-12`, 조건부 구간은 `[3.25112367913e-12, 3.63332930801e-12]`다. 이 유한 관측량의 조건부 부호는 양수지만 연속 이력의 부호·물리적 관측 신호는 인증하지 않았다. Optional RCT/HH/CR ON 계산을 새로 실행하지 않았다.

## 최신 결과와 과거 상태의 관계

CURRENT_SYNC_STATE WAITING and SYNC02 PARKED are stale. HH research ACTIVE; no renewed activation permission gate. Canonical S0 OFF control preserved.

완료된 원자 구성요소:

- HH ON05B finite matched moving-cohort histories in short prefix
- TH05 strict HII order against OFF and positive cohort optical memory under inherited exact-real FT03+LCS assumptions

## 기존 owner에게 예약된 다음 단위

`HH-ON06`: 입력은 ON05B/TH05 source-bound evidence; actual F08 point/thermal/HH-event/intervalJet/root/model/checkpoint source다. 반환은 coherent bounded native ON pilot; same provider and immutable budget identity throughout returned path다.

수락조건:

- no OFF certificate attached to ON
- same provider point and interval root definitions
- retain original failed attempts/budgets
- F09 whole campaign stays single REI owner
- do not require renewed activation approval

## 겹치지 않고 병렬로 준비할 단위

`HH-SYNC03-NE-TRANSFER`: 입력은 TH05 exact-real species response bounds if fully provided; loop2 optical-depth transfer contract다. 산출물은 conditional species-to-electron transfer eligibility record이며, 아직 optional ON 수치 결과를 만들어냈다고 기록하지 않는다.

수락조건:

- total delta-ne includes helium terms nHe(delta HeII+2 delta HeIII)
- strict HII increase alone does not certify total electron-density sign
- same density/clock and matched time domain required
- no transfer to low-T IGM without source-consistent HH model
- no synthetic ON tau result

## 원래 원자 lane과 주장 한계

HH research ACTIVE; canonical S0 OFF; physical/production HOLD; legacy 24/289 accepted; 265 unbounded; epsilon_C and epsilon_R null; B22 OPEN_UNDETERMINED; consumed scopes preserved를 보존한다. 기존 source identity·실패·tolerance·소비된 실행권한은 그대로다. 원자 정밀 lane 완결은 이번 baseline 관측량 소비의 선행조건이 아니다. 기존 owner 작업을 복제하거나 완료한 point/source suite를 동기화만을 위해 반복하지 않는다.

ON05B recovery core dual backup complete; full 413950057-byte native raw archive dual backup not complete. This handoff does not repair that historical gap.

최종 Git commit과 Drive/Dropbox 실제 완료 영수증은 root publication 후 연결된다. 이 준비 단계 파일은 미완료 게시·백업·recipient ACK를 성공으로 선기록하지 않는다.

게시 직전 두 원자 delta는 중앙 `publication/LATE_ATOMIC_DELTA.json`에 exact fetched source와 blob/SHA identity로 보존했다. Loop2에 사용한 frozen intake/gate는 바꾸지 않았다.
