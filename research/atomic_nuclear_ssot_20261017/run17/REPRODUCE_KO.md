# RUN17 재현 및 byte 복원

이 문서는 동결한 코드의 정확 명령과 새 출력용 명령을 구분한다. 아래의 재현 예시는 실행 영수증이 아니다. 이번 실제 실행 횟수와 결과는 README, JSON, stdout/stderr 및 PRE_NATIVE_CHECKPOINT에 있다. 게시 후 clean Git/ZIP readback 결과는 DELIVERY 기록에서 확인한다.

## 1. 원본 및 실행 환경

science commit과 ZIP SHA는 최종 DELIVERY.json에서 선택한다. 패키지의 RESTORE_COMMANDS.md에 해당 immutable commit의 sparse Git checkout과 archive 검증 명령이 들어 있다. 전체 Git 원본이나 toolchain을 이 delta ZIP에 중복하지 않는다. 원래 source는 부모45ee7192와 그 계보의 RUN13 recovered, RUN15, RUN16에 있다.

사용한 환경은 Python3.12.14, NumPy2.3.5, SciPy1.17.0, Linux6.18.55 x86_64/glibc2.39다. 새 Rust 빌드나 설치를 하지 않았다. 포함할 원래 gas_rhs_server는571904bytes, SHA2563454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b이다. 바이너리 byte restore, 실행 호환성, source/toolchain rebuild는 다른 검증 단계다.

Native A/B의 실제 source-root/run16-root는 기존 /tmp/rei_run16_repo였고, residual/domain은 새 /tmp/rei_run17_repo였다. 원본112source/input byte identity를 확인했으므로 경로 이름 차이를 물리 모델 차이로 해석하지 않는다. 모든 실제 경로는 아래 producer 명령과 원래 receipts에 보존한다. 새 환경에서 과거 절대경로를 만들 필요는 없다.

Git checkout에는 대부분의 RUN13 recovered 파일이 직접 들어 있으며, 기존 git_transport/restore.py는 MANIFEST에 지정된 **두 target의 raw chunks를 연결**한다. 다른 byte의 기존 target은 덮어쓰지 않으며 같은 target은 EXISTING_EXACT로 확인한다. 준비 노트 REPRODUCE_COMMAND_NOTES.json의 `restore_original333_if_absent` 명칭과 `only_when` 설명은 너무 좁다. 이 문서와 실제 원본 restore.py의 동작을 우선한다. 완전한 원본333개에는 원래 manifest 자체가 포함되고, RUN17 context는 그중112개의 실행 의존 파일을 확인한다. 그112개에는91native source와 checkpoint NPZ가 있으므로 binary와 packet만 복사해서는 안 된다.

## 2. 실제 producer 명령

아래는 이미 실행된 명령의 기록이다. 이 문서 작성 중에는 재실행하지 않았다. 정확한 stdout/stderr, argv, source SHA, 시간은 연결한 receipt를 따른다.

### native_A

```sh
python -B /tmp/rei_run17_work/native/first_birth_control.py --source-root /tmp/rei_run16_repo/research/atomic_nuclear_ssot_20261017/run13/recovered --run16-root /tmp/rei_run16_repo/research/atomic_nuclear_ssot_20261017/run16 --gas-binary /tmp/rei_run15_salvage/bin/gas_rhs_server --output-dir /tmp/rei_run17_work/native/control_A_execution01 --max-step-divisor 4 --native-call-cap 250 --wall-cap-seconds 20
```

Receipt: `native/control_A_execution01/FIRST_BIRTH_CONTROL.json`.

### native_B

```sh
python -B /tmp/rei_run17_work/native/first_birth_control.py --source-root /tmp/rei_run16_repo/research/atomic_nuclear_ssot_20261017/run13/recovered --run16-root /tmp/rei_run16_repo/research/atomic_nuclear_ssot_20261017/run16 --gas-binary /tmp/rei_run15_salvage/bin/gas_rhs_server --output-dir /tmp/rei_run17_work/native/control_B_execution01 --max-step-divisor 20 --reference-result /tmp/rei_run17_work/native/control_A_execution01/FIRST_BIRTH_CONTROL.json --native-call-cap 360 --wall-cap-seconds 20
```

Receipt: `native/control_B_execution01/FIRST_BIRTH_CONTROL.json`.

### residual

당시 cwd: `/workspace/scratch/3fb39b26f797`.

```sh
python3 -B /tmp/rei_run17_work/residual/first_birth_residual.py --source-root /tmp/rei_run17_repo/research/atomic_nuclear_ssot_20261017/run13/recovered --run16-root /tmp/rei_run17_repo/research/atomic_nuclear_ssot_20261017/run16 --control-result /tmp/rei_run17_work/native/control_B_execution01/FIRST_BIRTH_CONTROL.json --gas-binary /tmp/rei_run15_salvage/bin/gas_rhs_server --output-dir /tmp/rei_run17_work/residual/analysis_execution01
```

Receipt: `residual/execution_logs/EXECUTION_RECEIPT.json`.

### domain

```sh
python3 -B /tmp/rei_run17_work/residual/certify_reconstruction_domain.py --source-root /tmp/rei_run17_repo/research/atomic_nuclear_ssot_20261017/run13/recovered --run16-root /tmp/rei_run17_repo/research/atomic_nuclear_ssot_20261017/run16 --control-result /tmp/rei_run17_work/native/control_B_execution01/FIRST_BIRTH_CONTROL.json --residual-result /tmp/rei_run17_work/residual/analysis_execution01/FIRST_BIRTH_RESIDUAL.json --output /tmp/rei_run17_work/residual/domain_execution01/RECONSTRUCTION_DOMAIN_CERTIFICATE.json
```

Receipt: `residual/domain_execution01/EXECUTION_RECEIPT.json`.

### dense_tests

당시 cwd: `/tmp/rei_run17_work/residual`.

```sh
python3 -B -m unittest -v test_dense_reconstruction.py
```

Receipt: `PRE_NATIVE_CHECKPOINT.json`.

### comparison_tests

당시 cwd: `/tmp/rei_run17_work/residual`.

```sh
python3 -B -m unittest -v test_comparison_propagator.py
```

Receipt: `residual/COMPARISON_TEST_RECEIPT.json`.

### bernstein_tests

당시 cwd: `/tmp/rei_run17_work/residual`.

```sh
python3 -B -m unittest -v test_bernstein_domain.py
```

Receipt: `residual/BERNSTEIN_TEST_RECEIPT.json`.

## 3. 새 경로에서의 복원·검증 예시

먼저 실제 delivery의 science SHA에서 Git checkout하고 delta ZIP을 verify_archive.py로 새 폴더에 복원한다. 다음 변수들은 예시 폴더 구조다. 사용자는 실제 checkout/delta restore 경로를 선택할 수 있다.

```sh
RUN17_CHECKOUT=/tmp/rei_run17_clean_source
RUN17_SSOT="$RUN17_CHECKOUT/research/atomic_nuclear_ssot_20261017"
RUN17_ROOT="$RUN17_SSOT/run17"
RUN17_SOURCE_ROOT="$RUN17_SSOT/run13/recovered"
RUN17_PRIOR_ROOT="$RUN17_SSOT/run16"
RUN17_GAS_BINARY=/tmp/rei_run17_delta_restore/runtime/gas_rhs_server
RUN17_NEW_OUTPUT=/tmp/rei_run17_reproduce_new
RUN17_PYTHON=python3
mkdir -p "$RUN17_NEW_OUTPUT" "$RUN17_NEW_OUTPUT/tests" "$RUN17_NEW_OUTPUT/domain"
"$RUN17_PYTHON" -B "$RUN17_SSOT/run13/git_transport/restore.py" --destination-root "$RUN17_SOURCE_ROOT"
```

새 native/residual 출력 디렉터리는 CLI가 create-only로 생성한다. 미리 만들지 않는다. Domain JSON의 부모 디렉터리는 위처럼 먼저 만든다. 저장 JSON과 NPZ는 원래와 같은 디렉터리에 두며, 로더는 NPZ를 recorded path의 basename으로 찾는다. run17/native와 run17/residual의 상대 배치를 보존한다.

### 저장 계수의 domain 인증만 재현 — native0 / IVP0

```sh
"$RUN17_PYTHON" -B "$RUN17_ROOT/residual/certify_reconstruction_domain.py" --source-root "$RUN17_SOURCE_ROOT" --run16-root "$RUN17_PRIOR_ROOT" --control-result "$RUN17_ROOT/native/control_B_execution01/FIRST_BIRTH_CONTROL.json" --residual-result "$RUN17_ROOT/residual/analysis_execution01/FIRST_BIRTH_RESIDUAL.json" --output "$RUN17_NEW_OUTPUT/domain/RECONSTRUCTION_DOMAIN_CERTIFICATE.json"
```

이 명령은 저장된 reconstruction의 exact-rational certificate를 계산한다. 처음 과학 결과와 비교할 때 wall time, 절대경로 및 실행 영수증의 차이를 수학적 certificate 차이로 해석하지 않는다. Continuous admissibility의 범위를 true-IVP enclosure로 바꾸지 않는다.

### 집중 unit tests — 12개, native0

각 suite는 독립 실행이며 의미 있는 범위에서 필요한 것만 선택한다.

```sh
"$RUN17_PYTHON" -B "$RUN17_ROOT/residual/test_dense_reconstruction.py"
"$RUN17_PYTHON" -B "$RUN17_ROOT/residual/test_comparison_propagator.py"
"$RUN17_PYTHON" -B "$RUN17_ROOT/residual/test_bernstein_domain.py"
```

Dense suite의 작은 제조 linear-decay IVP는 solver의 recurrence/derivative 검증용이다. 기존 native history를 풀지 않는다. Comparison module의 현 게시본은 docstring만 수정했으며 실행본은 history/comparison_propagator_executed.py에 보존되어 있다. binding receipt에 따라 결과의 source SHA를 해석한다.

### 저장 B 경로에서 잔차 point evaluation 재현 — native 호출 포함 / 새 IVP0

```sh
"$RUN17_PYTHON" -B "$RUN17_ROOT/residual/first_birth_residual.py" --source-root "$RUN17_SOURCE_ROOT" --run16-root "$RUN17_PRIOR_ROOT" --control-result "$RUN17_ROOT/native/control_B_execution01/FIRST_BIRTH_CONTROL.json" --gas-binary "$RUN17_GAS_BINARY" --output-dir "$RUN17_NEW_OUTPUT/residual"
```

원래 실행800native calls, 코드 cap1000calls/20s다. 이는 byte 복원 절차가 아니라 선택적인 bounded numerical 재현이다. Snapshot source/packet/prefix/context/binary hash와 B divisor20을 검증한다.

### 선택적인 첫 birth A/B 재현 — 새 native coupled IVP2회

완료된 A/B는 보존되었으므로 다음 DAG 작업에서 자동 반복하지 않는다. 새로운 실행 환경의 구체적 호환성 문제를 해결할 때만 같은 제한으로 사용할 수 있다. RUN13 전체 M2나 RUN16 prefix를 재적분하지 않는다.

```sh
"$RUN17_PYTHON" -B "$RUN17_ROOT/native/first_birth_control.py" --source-root "$RUN17_SOURCE_ROOT" --run16-root "$RUN17_PRIOR_ROOT" --gas-binary "$RUN17_GAS_BINARY" --output-dir "$RUN17_NEW_OUTPUT/native_A" --max-step-divisor 4 --native-call-cap 250 --wall-cap-seconds 20
```

```sh
"$RUN17_PYTHON" -B "$RUN17_ROOT/native/first_birth_control.py" --source-root "$RUN17_SOURCE_ROOT" --run16-root "$RUN17_PRIOR_ROOT" --gas-binary "$RUN17_GAS_BINARY" --output-dir "$RUN17_NEW_OUTPUT/native_B" --max-step-divisor 20 --reference-result "$RUN17_NEW_OUTPUT/native_A/FIRST_BIRTH_CONTROL.json" --native-call-cap 360 --wall-cap-seconds 20
```

B는 reference A가 필요하며 call cap360을 명시한다. 기본값250으로 B를 실행하면 현재 소요349calls를 수용하지 못한다. 두 control의 max-step divisors는4와20이며 일정한2배mesh refinement가 아니다.

## 4. source 및 결과 identity

SCIENCE_MANIFEST.json은 모든 frozen payload 파일의 path/bytes/SHA256/Gitblob/mode를 기록한다. 자기 자신은 제외한다. 이후 delivery 파일은 별도 delivery manifest에 기록하고 frozen science를 수정하지 않는다. Archive에는 내부 ARCHIVE_MANIFEST와 ARCHIVE_IDENTITY를 넣고, ZIP 자체 SHA/업로드/다운로드 receipt는 밖에 기록한다.

구현과 그림의 원래 실행본, 실패/수정 이력도 보존했다. exact bytes의 복원과 numeric result의 재현을 구분한다. 클린 복원의 새 실제 결과는 후속 DELIVERY에 따로 기록해야 하며 이 예시 명령만으로 PASS를 기입하지 않는다.
