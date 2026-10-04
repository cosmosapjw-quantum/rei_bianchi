# FLRW06: pending real native spectral-stage regression

같은 rei_bianchi / forward/rust-reion-kernels-20260922 / draft PR83을 사용한다. 다음 chat task ID는 계속 REI-CHAT-FLRW06_NATIVE_SPECTRAL_STAGE_REGRESSION이다. Native 없이 FLRW07로 완료 승격하지 않는다. 새 이론 하위단위 moment-cone guard와 80자리 finite-node reference는 완료다.

먼저 live ref를 읽고 b553698a114fbff05640ab6ecb95d260410de492 이후 관련 diff만 확인한다. 외부 REI-F04는 최신 runtime 반환에서 pinned static FT03 numerical domain에 한해 completed이고 다음 외부 task는 REI-F05다. 예전 pending 문구를 현재 상태로 반복하지 않는다. 그 인증을 expanding spectrum/physical history로 확대하지 않는다. 외부 시험을 재실행하지 않는다.

원 FLRW05 ZIP의 96개 node bytes는 이 ZIP의 inputs/FLRW05_NATIVE_CALL_VECTORS.json에 그대로 있다. inputs/CASES.json은 baseline3, joined/reordered/split, scale-factor gauge, zero, threshold의11개 valid와6개 reject를 포함한다. Rust scientific modules는 SOURCE_BINDING.json에 고정한다. Python의 기대값과 native 반환은 별개다.

실제 rustc와 기존 repo가 있는 환경에서 압축 해제 디렉터리 기준으로 실행한다:

    python research/run_native.py --repo /path/to/rei_bianchi --output /path/to/new_result_directory

이 스크립트는 network/cargo/과거suite/history를 실행하지 않는다. git show로 원 source6개를 읽어 SHA-1 blob을 확인한 뒤 scientific module5개를 변경 없이 임시 디렉터리에 복사한다. 원 lib.rs의 공통 type 정의를 그대로 사용한 minimal root와 준비한 driver만 추가하여 단일 rustc compile 및 단일 probe process를 실행한다. Full crate integration test와는 다른 범위다. Error78는 compiler 또는 repo prerequisite blocker이며 성공이 아니다. Source mismatch/compile/run/oracle failure는 원인을 보존하고 멈춘다. 결과 디렉터리는 새로 생성하므로 기존 반환을 덮어쓰지 않는다.

PhotonInput absorption은 native photo API의 bin0/1/2 actual returns로만 구성된다. Python expected sink는 stdin에 쓰지 않는다. 판정은 compile/run exit, source/blob/input/binary/stdout identity와167개 bounded scalar comparisons, 6개 정확한 오류코드, scaled photon-number ledger를 사용한다. 167비교는 아직 실제 실행0이며 protocol self-test가 이를 대신하지 않는다.

반환 status가 NATIVE_EVENT_PHOTON_POINTWISE_REGRESSION_PASS여도 expanding accepted-step history, independent U consumer, physical source, interval 또는 Q geometry는 승인되지 않는다. Native module는 Number/PI event/heat이며 새로운 에너지-state 시간적분기는 아니다. 원 raw photo/FT03 thermal model을 무기록으로 합치지 않는다.

양의 두 moment 조건은 N>=0, U-LN>=0, RN-U>=0다. 고정 RHS의 FE 단계에 대한 exact hmax는 각각 음의 방향으로 움직이는 face까지의 시간 중 최솟값이다. 본 bound는 error estimator/stability limit/production step policy가 아니다. 유한 지수형 reconstruction은 strict interior 또는 explicit vacuum을 요구하고 boundary-delta를 clip하지 않는다. 기존 positive remap/attenuation의 대체로 임의 explicit Euler를 production에 넣지 않는다.

정지 원 F00/F03/FT03, CODEX_SYNC, runtime_returns 및 physical HOLD는 수정하지 않는다. strict local<2e-4/public width<2e-3, 과거[160,161] FAIL=2.1245050576368385e-4와 tick160을 보존한다. Same branch append-only non-force, 기존 Drive/Dropbox create-only backup, R1metadata와 byte restore와 science 판정을 분리한다.
