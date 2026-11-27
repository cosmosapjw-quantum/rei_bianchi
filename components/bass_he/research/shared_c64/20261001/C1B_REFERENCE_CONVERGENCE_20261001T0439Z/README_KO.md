# BASS_HE C1b — R=2 독립 전자구조 reference

`C1B_R2_REFERENCE_CONVERGENCE_CLOSED`. B-centered spherical hp-FEM과 기존 독립 prolate 경로가 R=2a_A의 energy·charge-center angular coupling에 대해 사전 경험적 기준을 통과했다. Continuum certificate와 R 전역·collision 검증은 포함하지 않는다.

먼저 `BASS_HE_POST_R10R_THEORY_CLOSURE_REPORT_KO.md`를 읽고, 유도와 실제 계산은 `C1B_REFERENCE_CONVERGENCE_KO.md`, 판정은 `RESULT.json` 및 `VERIFICATION.json`, raw numerical evidence는 `evidence/`를 확인하면 된다. 초기 l40 실패, 단 한 번의 사전 operational amendment, 실행 코드와 사후 I/O 수정의 identity를 보존했다.

`BASS_HE_BENCHMARK_MATRIX.csv`는 C1과 byte-identical이며 native cell 수는 1,131개, matrix 행은 13개로 그대로다. `BASS_HE_COUPLING_DATABASE.csv`는 기존 bytes를 prefix로 보존하고 자체계산 진단 6행을 append했다. 새 primary source 또는 source-native cell은 없다.

새 package는 이번 raw state arrays와 C1 public input snapshot을 포함한다. C1 전체 ZIP은 `provenance/INPUT_IDENTITY.json`에 결속된 별도 immutable dependency로 유지하며 중첩하지 않는다. 게시·백업 성공 여부와 remote identity는 별도 external receipt를 읽는다.

다음 작업은 `NEXT_HANDOFF_KO.md`의 `C2_FINITE_R_COUPLING_NUMERICAL_AUDIT`이며, exact R-grid·tolerances를 실행 전에 고정해야 한다. `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`, production 변경 금지를 유지한다.
