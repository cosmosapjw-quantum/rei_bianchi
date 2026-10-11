# C09B 다음 재개 프롬프트

REI-ACCEL02 C09B의 `Q1B_SOURCE_ENTRY_POSITIVE_STEP`에서 재개해줘. `research/accel02_20261011/recovery/LATEST.json`, `q1b/FINAL_STATUS.json`, `q1b/NEXT_DAG.json`을 먼저 읽고 실제 게시 head와 source/binary 해시를 대조해줘. C09A 이전 Q1A 기각을 다시 판정하려고 RUN002·EVENT003·Q0·G1·변경 없는 G2를 재실행하지 마. 이미 통과한 source/IC·reconstruction·native protocol 검사도 변경된 코드나 새 반례가 없으면 반복하지 마.

다음 구현은 `q1b/theory/SOURCE_ENTRY_NEXT.md`와 `SOURCE_ENTRY_ALGORITHM_DECISION.json`의 제안에 따른 실제 source 누적·redshift work·moment-exact positive quadrature·implicit absorption·native gas 네 변수의 허용영역 내 해법이야. 이 문서는 아직 production 구현이나 승인된 시간 적분기가 아니야. 빈 셀 Jacobian을 임의로 0으로 만들거나 photon seed/floor/clipping을 넣지 말고, 누적 source의 N/Q를 실제로 적분해줘. 국소 해석 기준으로 1/3 평균과 h/h2/h4 수렴·stiff absorption·공통 counters를 검증하고, 정밀도와 시간오차 조건이 충돌하면 `ENTRY_PRECISION_TIME_BUDGET_CONFLICT`를 보존해 원인을 해결해줘.

병렬로 실제 native opacity의 남은 threshold trace/좁은 support 처리와 production checkpoint validator/hook을 연결해줘. opacity IC 진단의 실패나 한계를 `FINAL_STATUS.json`에서 확인하고, 초기 시각의 성공을 전구간 수렴으로 옮기지 마. `checkpoint/atomic_checkpoint.py`는 generic manufactured 경로만 검증됐으므로 실제 driver에 연결한 새 복구 비교가 필요해. 현재 native ABI의 combined work를 새 photon-redshift substep에서 이중 계산하지 않도록 thermal/radiation work 소유권을 분리하고 실제 검사를 남겨줘.

기존 물리와 허용 기준을 그대로 유지해. source/closure·진입 solver·실제 checkpoint의 국소 gate가 닫힌 뒤에는 좁은 redshift 검사를 반복하지 말고, 미리 고정한 C1/C2와 동일 grid 시간 비교를 전체 mean-volume z=15.9→4에서 진행해줘. 시간9field 2e-6, full24field spectral/angular 1e-3(65/129 집합 각각의 fine amplitude), initial-energy/initial-nH ledger 1e-9, geometry1e-11, strict domain/no clipping은 완화하지 마. 새 Bianchi 비교와 BASS native receiver는 그 이후야. 기존 reduced N4와 CR/RCT 별도 lane의 상태는 유지해줘.

각 새 실행·첫 실패·수정 후 독립 판정마다 source/binary/control identity와 전체 이력을 남기고 additive GitHub 게시 및 기존 Drive/Dropbox 목적지에 checkpoint를 저장해줘. 과거 통과를 반복하는 대신 새로 바뀐 부분만 검증해. 장기 실행은 완전한 prefix·counter·accepted extrema를 실제로 복원할 수 있을 때만 시작해줘.

## 최소 읽기 순서

1. `FINAL_STATUS.json`, `NEXT_DAG.json`, `RUN_CONTRACT.json`.
2. `review/INDEPENDENT_DECISION_FINAL.json`, `review/INDEPENDENT_NATIVE_CI_ADDENDUM.json`.
3. `theory/SOURCE_ENTRY_NEXT.md`, `theory/EMPTY_CELL_DECISION.json`.
4. 최신 opacity 증거와 `checkpoint/README.md`.
5. 필요한 함수만 `source_cells.py`, `reconstruction.py`, `opacity_native.py`, `native/src/main.rs`에서 읽기.

## 실행 파일

- 기존 SIGMA: `n1/native/target/release/rei_n1_native`, SHA256 `3e3a3ef4d89019d791f4e2f4cf25108ac2c6d5e365c58a928d9ff8a85234a0ac`.
- 새 CELL_RHS_V1: `q1b/native/target/release/rei_q1b_cell_native_v1`, SHA256 `e29245acfee5be4d43c27935e2abd212d578685efa70dffbeffa8f96dd3e4b6f`.
- 두 binary는 checkpoint ZIP에 포함되고 Git 소스에는 추가하지 않는다. 실행 권한과 해시를 확인한다. 다운로드된 artifact는 검증됐지만 이중백업 전체의 remote restore를 검증했다고 주장하지 않는다.

## 새 IC 실패의 병렬 해결

C1/C2 초기 opacity pair는 사전 local headroom1e-4에서 실패했다. C2 단독은 실제 UVB 기준에 통과했다. C2를 baseline으로 한 번 이분할한 C3를 새 create-only 파일로 동결하고 새 C3의 source/IC와 C2/C3 비교만 수행해줘. 기존 C1/C2 raw와 직접 UVB 기준은 재사용하고, 단면적·보간·기준을 바꾸지 마. C3는 C09B에서 아직 구현/검증하지 않았어.
