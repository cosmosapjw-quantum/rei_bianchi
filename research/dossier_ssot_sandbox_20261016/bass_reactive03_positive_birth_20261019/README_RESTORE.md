# BASS-REACTIVE-03 전체 패키지 복원과 재현

이 패키지는 ISO-COUPLE P4의 양수 출생시각 적분을 재현하기 위한 독립 Rust 연구 패키지다. 원래의 receiver crate 97개 파일, 새 AP 확장 파일, 실제 BASS donor 입력, 원 source 계약, 실행 코드와 기록을 함께 보존한다. 원 저장소의 production branch를 수정하거나 부모 PR을 병합할 필요가 없다.

복원은 **아카이브 바이트 확인 → 압축 해제 → payload·원 source 확인 → 현재 실행환경 확인 → 실제 재실행** 순서로 한다. 기존 문서의 PASS는 새 실행의 PASS를 대신하지 않는다.

## 1. 필수 디렉터리 배치

아래 상대 위치를 유지한다.

| 경로 | 내용 |
|---|---|
| `ap/Cargo.toml`, `ap/Cargo.lock` | AP 구현을 포함하는 실제 Cargo target과 lockfile |
| `crate/ap_lib.rs` | 원 `crate/src/lib.rs`를 가져오고 AP 모듈을 추가하는 crate entry point |
| `crate/src/`, `crate/owner_src/`, `crate/tests/`, `crate/examples/` | 원 receiver 및 physical owner 코드와 새 integration tests/examples |
| `crate/fitted_birth.rs`, `crate/ap_midpoint.rs`, `crate/ap_budget.rs` | fitted birth rule, native bridge, S10 four-corner adapter |
| `crate/ap_native_driver.rs` | 실제 H/He/D·BASS 이력 재현 driver |
| `donor_input/donor/` | 원 donor CSV와 manifest |
| `contracts/PARENT_97_SOURCE_SHA256.json` | 변경하지 않은 원래 97개 receiver 파일의 SHA-256 |
| `scripts/run_native_matrix.py` | 독립 native 사례 실행 및 성공·실패 기록 |
| `MANIFEST.sha256` | 패키지 payload 바이트 manifest |
| `verify_manifest.py`, `RUN_STAGE.sh` | 복원 확인과 실행 entry points |

`ap/Cargo.toml`의 library 경로는 `../crate/ap_lib.rs`다. 원 fixture는 `CARGO_MANIFEST_DIR/../donor_input/donor`에서 입력을 읽으므로 `ap/`, `crate/`, `donor_input/`은 같은 부모 디렉터리 아래에 있어야 한다.

**새 연구를 재현할 때는 `--manifest-path ap/Cargo.toml`을 사용한다.** `crate/Cargo.toml`은 원 baseline을 실행하는 별도 entry point이며 새 AP 모듈과 검증을 포함하지 않는다. `cargo fmt`를 전체 트리에 무조건 적용하면 immutable owner까지 변경할 수 있으므로 복원 절차에서 실행하지 않는다.

## 2. 아카이브와 source 바이트 확인

받은 전체 ZIP의 크기와 SHA-256을 전달문에 기록된 값과 비교한 뒤 새 디렉터리에 압축 해제한다. `MANIFEST.sha256`는 아카이브 내부 payload를 검사하며 ZIP 자체의 SHA-256과 다른 대상이다.

```bash
sha256sum /absolute/path/REI_BASS_REACTIVE03_FULL.zip
```

파일명은 전달받은 실제 파일명으로 바꾼다. 이미 작업 중인 디렉터리에 덮어쓰지 않는다. 압축 해제 후 package root에서 다음을 실행한다.

```bash
python3 verify_manifest.py --root "$PWD"
```

이 검사는 manifest에 기록된 각 파일을 스트리밍 SHA-256으로 확인하고, 원 receiver 97개 파일을 별도 계약과 다시 대조한다. 절대경로·상위 디렉터리 이동·symlink·중복 manifest 항목은 거부한다. 출력의 `VERIFIED_PAYLOAD_BYTES`는 파일 identity 확인이며 수치 수렴이나 물리적 정확도 판정이 아니다. Manifest 자체는 자기 hash를 포함하지 않으며 외부에 기록된 ZIP hash로 연결한다.

이후 실행 출력은 package 밖의 새 디렉터리에 두는 것을 권장한다. 원 `evidence/`와 donor 파일은 그대로 보존한다. `RUN_STAGE.sh`의 기본 출력은 `/tmp/rei_positive_birth.XXXXXX`이고, `REI_RUN_OUTPUT`으로 새 영구 경로를 지정할 수 있다.

## 3. Rust 1.94.1과 현재 실행환경

과거 runtime 실패를 현재 상태로 계승하지 않는다. 먼저 현재 환경에서 실제 버전 명령을 실행한다.

```bash
python3 -c 'import sys; print("PYTHON_PASS", sys.version)'
rustc --version --verbose
cargo --version
cargo clippy --version
```

이 단계가 검증에 사용한 Rust·Cargo 버전은 모두 `1.94.1`이다. Standalone installation을 사용한다면 아래처럼 **복원한 실제 설치 경로**를 지정한다.

```bash
export REI_RUST_PREFIX=/absolute/path/to/rust-1.94.1-prefix
export PATH="$REI_RUST_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$REI_RUST_PREFIX/lib:${LD_LIBRARY_PATH:-}"
```

이 prefix는 실행 가능한 `bin/rustc`, `bin/cargo`, Clippy component와 표준 라이브러리를 포함해야 한다. 설치 archive나 signature 파일을 갖고 있다는 사실만으로 설치·컴파일 성공을 주장하지 않는다. 이전 sandbox의 절대경로가 들어간 env script는 새 환경의 유효한 toolchain 경로를 보장하지 않는다.

`RUN_STAGE.sh`는 toolchain 설치를 수행하지 않는다. Cargo 명령은 모두 `--offline --locked`를 사용한다. 패키지의 receiver crate에는 registry dependency가 없지만, Rust 표준 라이브러리와 Clippy component는 실제 toolchain에 있어야 한다. Toolchain이 준비되지 않았다면 먼저 해당 실행 의존성을 해결하고 같은 패키지 바이트에서 다시 시작한다.

## 4. 제공 runner로 재현

Package root에서 다음처럼 실행한다. `REI_RUN_OUTPUT`은 **존재하지 않는 새 경로**여야 한다.

```bash
REI_RUN_OUTPUT=/absolute/path/to/new-reproduction \
  bash RUN_STAGE.sh all ap_n32_r2
```

`all`은 다음 순서로 수행한다.

1. 현재 Python 실행과 package·원 source manifest 확인.
2. 현재 Rust·Cargo 버전 확인.
3. `ap/Cargo.toml`의 full Rust tests, 모든 targets, strict Clippy.
4. Release examples build.
5. 동결 source의 16개 `(N_t, refinement)` 사례와 scalar/age-node 출력.
6. 선택한 native 사례 실행. 별도 사례를 지정하지 않으면 `ap_n32_r2` 하나를 실행한다.
7. 실행 후 package payload가 변하지 않았는지 재확인.

단계별 재현도 가능하다. 각각 새로운 출력 경로를 사용한다.

```bash
REI_RUN_OUTPUT=/absolute/path/to/new-integrity-check bash RUN_STAGE.sh verify
REI_RUN_OUTPUT=/absolute/path/to/new-tests bash RUN_STAGE.sh test
REI_RUN_OUTPUT=/absolute/path/to/new-frozen bash RUN_STAGE.sh frozen
REI_RUN_OUTPUT=/absolute/path/to/new-native bash RUN_STAGE.sh native off_gl2_n32 ap_n32_r2
```

기본 compile jobs와 test threads는 각각 2, native workers는 1이다. 필요한 경우 `REI_CARGO_JOBS`, `REI_TEST_THREADS`, `REI_NATIVE_WORKERS`로 지정한다. Native matrix script는 worker 수 1–3을 지원한다. 기본 Cargo target은 해당 실행 출력의 `target/`이다. **Fresh-restore 검증에서는 기존 target을 재사용하지 않는 기본값을 유지한다.** `REI_CARGO_TARGET`을 지정하여 다른 target을 사용할 경우 절대경로를 사용하고 그 선택을 기록한다.

출력의 `logs/*.command.json`은 실제 argv를, `logs/*.log`는 실제 stdout/stderr를 보존한다. 마지막 `RUN_COMPLETION.json`은 요청한 단계의 실행 완료와 새 증거 hash를 기록한다. 이 파일을 장시간 해의 물리적 채택 판정으로 해석하지 않는다.

## 5. 직접 실행 명령

Runner 없이 실행하려면 다음과 같이 source tree 밖의 새 target과 출력 디렉터리를 명시한다. 아래 경로는 새 복원 환경에 맞게 설정한다.

```bash
export REI_PACKAGE=/absolute/path/to/restored-package
export REI_REPRO=/absolute/path/to/new-reproduction
mkdir -p "$REI_REPRO/frozen"
export CARGO_TARGET_DIR="$REI_REPRO/target"

python3 "$REI_PACKAGE/verify_manifest.py" --root "$REI_PACKAGE"
cargo test --manifest-path "$REI_PACKAGE/ap/Cargo.toml" --offline --locked --all-targets
cargo clippy --manifest-path "$REI_PACKAGE/ap/Cargo.toml" --offline --locked --all-targets -- -D warnings
cargo build --manifest-path "$REI_PACKAGE/ap/Cargo.toml" --offline --locked --release --examples

"$CARGO_TARGET_DIR/release/examples/ap_frozen_oracle" "$REI_REPRO/frozen"
python3 "$REI_PACKAGE/scripts/run_native_matrix.py" "$REI_REPRO/native" \
  off_gl2_n32 ap_n32_r2 --workers 1 \
  --binary "$CARGO_TARGET_DIR/release/examples/ap_native_driver"
```

`ap_frozen_oracle`는 출력 디렉터리가 먼저 존재해야 하며, 내부 파일은 `create_new`로 생성한다. 같은 디렉터리에 재실행하여 이전 결과를 덮어쓰지 않는다.

Native driver 하나를 직접 실행하는 계약은 다음과 같다.

```bash
"$CARGO_TARGET_DIR/release/examples/ap_native_driver" \
  SIGNED_MINUS 121 32 0 8e12 false false 2 4 1e-12 2
```

| 위치 | 인자 | 의미 |
|---|---|---|
| 1 | `SIGNED_MINUS` | donor 사례. `SIGNED_PLUS`도 별도로 실행 가능 |
| 2 | `121` | 고정 donor grid |
| 3 | `32` | 시간 macrostep 수 |
| 4–5 | `0`, `8e12` | 시작시각과 구간 길이, s |
| 6 | `false` | 기존 source cell mean. `true`는 split-positive spectral quadrature |
| 7 | `false` | 원 donor table. 기존 `true` 모드는 시작점의 일정 expansion/shear background로 바꾸는 별도 비교이며 gas-opacity 동결 oracle과 다름 |
| 8–9 | `2`, `4` | legacy birth-GL 설정과 opacity substeps |
| 10 | `1e-12` | 원 CX relative tolerance; absolute tolerance는 기록된 제어기에 따라 `0.01 × rtol` |
| 11 | `2` | fitted refinement. `off`는 원 bridge 직접 dispatch |

Birth refinement는 `1, 2, 4, 8, 16` 중 하나다. Native matrix 전체 13개 사례는 `run_native_matrix.py`에 사례 이름을 생략하여 실행할 수 있다. 이 경우 `ap_cx_worklimit`의 예상된 work-limit 기록도 보존된다.

## 6. 무엇을 비교할 것인가

동결 oracle은 원 source와 species별 opacity를 사용하지만 gas·geometry를 고정한다. `AP_FROZEN_FINAL.csv`에서 analytic survivor, fitted survivor, species별 흡수 사건수 및 photon/energy ledger를 대조한다. `AP_RULE_NODES.csv`와 `AP_SCALAR.csv`는 생존수와 별도로 age distribution의 moment·refinement를 확인하는 입력이다.

Native CSV에는 54개 필드가 있으며 source, species별 사건수, photon count, geometry work 외에 다음 raw energy 항목을 포함한다.

- `photon_energy_com3`
- `gas_thermal_com3`
- `gas_binding_com3`
- `escaped_com3`
- `cmb_reservoir_com3`
- `initial_total_energy_com3`

이 값으로 최종 총에너지를 직접 합하고 `initial_total_energy_com3 + source_energy + geom_work`와 비교한다. `thermal_change_com3`, `chemical_change_com3`, `photo_energy_com3`는 누적 reaction budget이다. `photon_energy_com3`는 현재 생존 광자의 에너지이므로 `photo_energy_com3`와 구별한다.

시간 해상도, birth refinement, spectral representation, opacity substeps를 한 번에 하나씩 바꾼 이력을 비교한다. 작은 number/energy ledger 잔차는 수렴성 근거를 대신하지 않는다. `wall_s`, 실행 경로, binary SHA 같은 환경 의존 항목은 과학적 관측량과 구분한다. Fresh build의 binary SHA가 달라졌다고 소스·물리 출력이 자동으로 달라지는 것은 아니며, 같은 binary hash도 입력·출력의 정확성을 대신하지 않는다.

## 7. 실패와 중단의 분류

| 실제 관측 | 분류와 처리 |
|---|---|
| ZIP hash 불일치, payload hash 불일치 | `ARTIFACT_INTEGRITY_FAILURE`. 그 파일을 기준 입력으로 채택하지 않고 원 archive를 다시 확보 |
| 필수 donor·source·manifest 없음 | `INPUT_DEPENDENCY_MISSING`. Rust 실행 가능 여부와 분리 |
| 현재 `rustc` 실행이 command-not-found로 실패 | `COMPILER_MISSING`. 과거 기록을 근거로 판정하지 않음 |
| Rust·Cargo 버전이 1.94.1과 다름 | `TOOLCHAIN_VERSION_MISMATCH`. 기록된 실행환경과 구별 |
| Clippy component 없음, offline dependency 없음 | 실행환경 또는 `PACKAGE_MISSING`. 물리식·수치방법 실패로 분류하지 않음 |
| binary를 실행할 수 없음, loader 오류, signal 종료 | `EXECUTION_FAILED` 또는 구체적인 환경 원인. raw stderr·exit code 보존 |
| `Cx(WorkLimit)` | `RESOURCE_LIMIT_CX`: 내부 CX 계산예산 소진. 수렴 실패·물리적 해 부재로 재분류하지 않음 |
| `NoForwardProgress` | f64 시간/연령 표현 또는 timestep 진행 한계. 임의의 출생시각으로 이동하여 성공 처리하지 않음 |
| `NegativePopulation`, `NegativeEnergy`, `TemperatureOutsideSource` | 입력/시도한 단계의 domain 또는 positivity 거부. 해당 입력과 단계 길이에서 원인을 진단 |
| `SourceMismatch`, owner 충돌 | source·입력·소유권 불일치. 서로 다른 연구 계보를 무검증 병합하지 않음 |
| `PhysicsLedger` | 구현·수치·입력 근거를 검사해야 하는 보존 검산 실패 |
| `.running.csv`, `.running.stderr`만 남고 완료 JSON 없음 | 중단된 시도. 마지막 완료 checkpoint로 승격하지 않고 보존·inventory 후 새 출력 위치에 재실행 |

첫 단계 `Cx(WorkLimit)`이면 데이터 행이 0개인 CSV도 정상적인 실패 증거다. Native matrix의 전체 명령이 0으로 종료되더라도 `ap_cx_worklimit`는 성공한 물리 이력으로 바뀌지 않는다. 사례별 JSON의 `status`, `rows`, `exit_code`, `failure_class`를 함께 읽는다.

## 8. 이 패키지의 물리적 범위

이 구현은 원 MD14/BB50k source, H/He/D competing absorption, 원 reaction·energy owner, BASS one-way background를 유지한다. 새 native source-scale 매개변수는 도입하지 않았다. 원 MD14 source constructor는 엄격 양수 emissivity를 요구하므로 zero-source 검증은 scalar inventory 및 기존 source-off 검증 범위와 구별한다.

Constant-opacity source integral의 정확성, 유한 age-cohort 표현의 근사, 진화하는 H/He/D 이력의 수렴을 각각 판정한다. 전 구간 해의 최종 채택 상태와 다음 DAG는 패키지의 실제 결과 보고서·상태 JSON을 따른다. 완전한 age·spectral·angular 수렴, 보편적인 전체 2차 정확도, 양방향 Einstein feedback을 이 복원 절차의 성공만으로 주장하지 않는다.
