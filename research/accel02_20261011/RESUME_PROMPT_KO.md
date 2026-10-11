# C08R1 다음 시작 프롬프트

REI-ACCEL02 C08R1에서 Q1B0_CONTRACT_AND_CHECKPOINT_DESIGN부터 이어서 진행해줘. 먼저 `q1a/FINAL_STATUS.json`, `q1a/review/FINAL_DECISION_C08R1.json`, `q1a/REPORT_KO.md`, `q1a/Q1B_LOCAL_DAG.json`과 `NEXT_DAG.json`을 읽어라.

Q1A는 기각되었다. G1_FINE은 z15.9→4 전구간을 마쳤지만 N ledger3.5288241094e-9로 기준1e-9를 초과했다. G1_TIGHT는 BDF step-floor 실패로 전구간 시간수렴 미완료다. G2_FINE은 환경 중단으로 terminal/history가 없으며 C08C의 진행 snapshot만 복구되었다. 이를 실행 중·물리 실패·wall timeout으로 재분류하지 말라. 현재 wall-only resume CLI는 적용 불가이며 실행 횟수0이다. Source129epoch pair 하한만으로 이미 spectral gate FAIL이 증명되므로 무변경 G2 재실행으로 결론을 반복하지 말라.

RUN002·EVENT003·Q0 및 완료된 G1 계산을 반복하지 말라. source/IC/provider/closure/배경·물리와 기존 time2e-6, E1e-9, N1e-9, spectral1e-3, geometry1e-11 기준을 유지하라. N3 및 새 BASS native receiver는 HOLD다.

이번 단계의 목표는 고정 q-cell의 N/U 표현과 공유 K0/K1 source·opacity·gas·heat·counter 보존식, 빈 cell/source entry/endpoint realizability, native integrated-photo ABI와 Jacobian 계약을 구체화하는 것이다. Q1B는 제안이며 아직 구현 완료나 실행 가능 상태가 아니다. 계약 이후 SOURCE_IC, OPACITY_RECONSTRUCTION, NATIVE_JACOBIAN과 P0_DURABLE_CHECKPOINT를 병렬 진행하라. 기존 Q0의 저장 reference를 재사용하라. 새 local gates와 독립 GO 전에 비싼 전구간 ODE를 시작하지 말라.

P0는 전체 saved-epoch prefix, 다음 segment, accepted state/극값/domain/ledger/counter, 정확한 source/grid/binary/control 해시를 하나의 atomic generation으로 저장해야 한다. 실제 복구와 중단·재개 fixture를 확인하고 실행 중에도 GitHub 및 Drive/Dropbox durable receipt를 남겨라. RESTART.npz 하나만으로 exact resume라고 주장하지 말라. Segment 경계의 새 BDF 초기화와 integrator 내부 상태 복원을 구별하라.

단계별 실제 결과·독립 판정·machine-readable status·DAG·다음 한 작업을 checkpoint로 게시해라. 기존 PR110(REI)·PR140(BASS)의 새 native HOLD를 유지하면서 필요한 결과만 additive push하고 force/merge는 하지 말라. 세션이 길어지면 최신 receipt와 다음 시작점을 남겨라.
