# NCP local Codex handoff — B1 실제 결과 반영

현재 새 NCP 작업은0개다. B1의 bounded Python 과학 실행은 HERE에서 완료됐다.
기준 실행6개와 refinement6개 및 pilot1개를 다시 돌리는 지시가 아니다.

## 적용할 상태

- project: cosmosapjw-quantum/BASS_HE
- node: REI_BASS_PRESCRIBED_THOMSON_RESPONSE_B1
- execution: EXECUTED_SCOPED_PYTHON
- backend: EXPLICIT_EXISTING_BASS_PYTHON
- final scientific admission: review/DECISION.json을 따른다
- original Rust/native seam: HOLD_RUNTIME_ENVIRONMENT
- native_rust_invocations: 0
- NCP_action: NO_CURRENT_HEAVY_WORK
- new_work_units: []
- E13C11: PARKED_PENDING_OBSERVABLE_NEED

정확한 게시 commit/PR/백업 위치는 이 packet의 PUBLICATION.json과 전달 영수증을 따른다.
보고서, CURRENT_STATE.json, analysis/B1_NUMERICAL_ASSESSMENT.json,
review/DECISION.json을 먼저 읽는다. 현재 판단에는 별도 대형 archive 복구가 필요 없다.

## 보존할 실제 결과

기존 frozen FLRW/r=.1 이력, 기존 Planck IC, cold elastic Thomson test-field,
mean-volume z20→4 범위에서 F/M/B/B0/B_F/M_F를 계산했다.
공통 physical-energy y=(a/a_i)E/(kB*T_i) slice에서 원래 Python collide를 호출했다.
같은 B clock에 대한 F 이력 투영은 기존 Q-cell measure×H_F(mid)/H_B(mid)다.
N4 ne_eff를 순간 밀도로 복사하거나 R15 rate를 radiation spectrum으로 사용하지 않았다.

z4,y1:
- q2_B = −0.0364635999884248
- pL_B_equator = 0.0008083203048727583
- history_delta_q2 = −2.464318940992305e−7
- paired time/angle/energy 변화량 합 = 1.0913006609492015e−12

수치 변화량은 경험적 민감도이고 rigorous enclosure나 statistical CI가 아니다.
원래 ODE 정확도, observer tail, CMB Cl, production native를 새로 채택하지 않는다.

## runtime 경계

HERE에 Rust compiler/prebuilt bass library가 없고 compiler 취득이 실패했다.
최초 실패를 source_notes/native_environment_failure.json에 보존했다.
기존 Python source를 명시적으로 선택해 실제 물리 비교를 끝냈다.
Rust C ABI/native binding source는 준비돼 있지만 빌드와 parity는 NOT_RUN이다.
Python 성공을 Rust 성공으로 보고하지 않는다.

짧은 Rust 빌드/대조만을 위해64코어128GB NCP allocation을 만들지 않는다.
실제로 무거운 후속 packet이 생긴 경우 그 packet의 범위·backend·미실행 work list를 따른다.
source/physics/precision을 조용히 바꾸거나 완료 계산을 성능 측정용으로 재실행하지 않는다.

## 새 NCP packet의 조건

목표 관측량과 요구 정확도, 고정 source/input, HERE pilot wall/CPU/RSS,
독립적인 미완료 scenario 목록, 실제 병렬 이득, 실행 명령과 fresh output/반환 규칙이
함께 있을 때만 해당 작업을 실행한다. 현재 그러한 새 work list는 없다.

추후 실행에서는 실제 topology·affinity/quota·NUMA·가용 RAM을 확인하고,
MPI/OpenMP/BLAS 중첩을 막으며 실가용 RAM의 최소20%를 남긴다.
시간 순서가 있는 trajectory나 Thomson으로 결합된 각도를 독립 작업처럼 나누지 않는다.

현재 반환할 문구:
“B1 Python 수송 결과 반영. native 연결은 미실행/HOLD.
새 NCP work 0, E13C11 대기. 완료된 수송 실행은 재시작하지 않음.”

새 host attestation, NCP 실행 성공 또는 전체 B1 native 완료를 선언하지 않는다.

