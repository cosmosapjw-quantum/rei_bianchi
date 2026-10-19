# BR05 native birth monitor 구현 인계

## 구현 상태

새 단위 `bass_reactive05_native_monitor_20261019`에 8개 소스·manifest 파일만 추가했다. 부모의 125개 입력 파일은 SHA-256을 다시 계산하여 모두 바이트 불변임을 확인했다. 신규 의미 있는 Rust test 9개, 신규 target scoped strict Clippy, scoped rustfmt 검사는 실제 PASS이다. 실제 작은 source-native 실행도 완료되어 최종 schema의 6개 CSV를 읽을 수 있다.

전체 all-target Rust tests와 strict Clippy, 계획된 긴 `Nt16/r8` 단일 실행은 독립 runtime 담당에게 인계했다. 해당 실행의 PASS나 과학 결과를 이 구현 문서가 선행하여 주장하지 않는다. 최종 8개 소스의 identity는 `SOURCE_IDENTITY_FINAL.json`에 고정했다.

## 최소 관측 지점과 물리 불변성

`crate/monitored_midpoint.rs`는 원 `crate/ap_midpoint.rs`에서 명시적인 10개 문자열 변환으로 생성했다. 타입명·공개 dispatcher·관측 인자를 추가하고, 실제 corrector의 세 지점에서 read-only observer를 호출한다.

1. 원 `emit_births`가 실제 cohort vector를 반환한 직후: 그 호출에 사용된 실제 `rate_gas`, 실제 birth vector, 기존 midpoint/end geometry를 읽는다.
2. 원 `photo`가 끝난 직후: 같은 append index의 실제 감쇠 count를 읽는다.
3. 원 chemistry, 두 CX half-flow, drift, 최종 ledger 검증이 모두 끝난 뒤: accepted state와 유지된 같은 cohort를 읽는다.

Half-step predictor에는 관측 인자로 `None`을 전달한다. 관측자가 source rate와 fitted rule을 재계산하는 작업은 입력과 실제 birth time·weight·label이 맞는지를 검증하기 위한 것이다. 재계산한 값을 물리 상태에 쓰지 않는다. 원 birth emission, photo, CX, chemistry, drift의 물리 문장은 그대로 남아 있다. 원 controller나 four-corner의 코드는 변경하지 않았다.

`MECHANICAL_HOOK_PROOF_FINAL.json`은 10개 변환을 역적용하면 원 AP 모듈의 SHA-256이 정확히 복원됨을 기록한다. 역변환 전 생성 코드를 scoped rustfmt에 통과시킨 결과도 실제 최종 모듈과 바이트 단위로 일치한다. 형식 정리는 새 파일만 대상으로 했으며 부모 모듈 트리를 재포맷하지 않았다.

## API와 실패 계약

`MonitoredMidpointBridge::advance_with_monitor(initial, config, dt, mode)`는 `Result<MonitoredStep, NetworkError>`를 반환한다. 바깥 `NetworkError`는 원 solver의 실제 실패다. 성공한 `MonitoredStep`은 원 `AgeStep`, 원 `RetardedDiagnostics`, 별도 monitor 결과를 가진다.

- `MonitorMode::Off`: 부모 `ApMidpointBridge`로 직접 위임하고 monitor 결과는 `None`이다. AP fitted와 legacy birth 모두 해당한다.
- `MonitorMode::On`: 실제 AP corrector hook을 사용한다. 성공한 관측은 `Some(Ok(StepMonitor))`이다.
- 관측 quota, 관측 입력 불일치 또는 참조 계산 실패: `Some(Err(MonitorError))`이며 이미 성공한 물리 step은 그대로 반환한다.
- On과 legacy `BirthMode::Off`의 조합: 물리는 부모에게 직접 위임한다. 관측 결과는 `UnsupportedBirthMode`이다. legacy 내부 rate gas를 임의의 다른 gas로 대체하지 않는다.
- `Cx(WorkLimit)`와 음수 population 같은 solver 실패는 원 `NetworkError` 분류로 반환한다. 모니터 오류로 바꾸지 않는다.

고정 격자 driver에서 exit 2는 원 solver 실패, exit 3은 물리 실행 이후 기록된 monitor 실패, exit 4는 monitor 파일 생성·쓰기 실패다. 파일 생성이 실행 전에 실패하면 물리 실행도 시작하지 않는다. 실행 중 monitor 오류가 생기면 정상 native CSV의 accepted physics 행을 계속 기록하고 마지막에 별도 실패 코드를 반환한다. 실패 이후 일부 내보내기만 완료된 경우 `MONITOR_EXPORT_PARTIAL`로 표시한다. Rust panic/build 오류는 이 exit 계약을 통과한 solver 결과로 간주하지 않는다.

## 자료의 의미와 join

정상 stdout은 부모 native driver의 **54개 열**을 그대로 사용한다. 벽시계와 geometry cache hit/miss는 read-only diagnostic의 추가 source/snapshot 평가에 따라 달라질 수 있다. 실제 물리 상태·ledger·cohort 자료의 비트 parity는 별도 test로 확인했다.

| CSV | 실제 최종 sample 행 수 | 의미와 join |
|---|---:|---|
| `MONITOR_STEPS.csv` | 1 | 실제 corrector `rate_gas` 13종 population·thermal·EOS, midpoint/end 기하, accepted 13종과 thermal/binding/escaped/CMB, 전 cohort raw 수·연령 moment. `step`으로 join한다. |
| `MONITOR_RULES.csv` | 48 | 실제 birth energy의 bits, source-native HI/HeI/HeII/DI selector rates, tau, 원 rule의 단위-born constant-j/kappa 참조 mass와 shape. 키는 `(step, rule_id)`다. |
| `MONITOR_PANELS.csv` | 48 | `(step, rule_id, panel_id)`별 recurrence endpoints와 actual rule weights의 exact-bit 대조, physical/optical width, represented birth-clock width, roundoff defect, local frozen certificate. |
| `MONITOR_TEMPLATES.csv` | 384 | 실제 source template ordinal, spectral/angular label, raw birth direction, midpoint source rate, constant-j born count, actual-born 및 after-photo/accepted moment. source-weighted frozen propagation도 별도 이름으로 기록한다. |
| `MONITOR_BIRTHS.csv` | 768 | persistent append `cohort_index`, template/rule/node/panel join, 실제 tb·count·birth geometry, target/actual age, 두 시계 결함, source ratio, after-photo와 accepted count, K와 step-end ray. |
| `MONITOR_FINAL_COHORTS.csv` | 768 | 마지막 유지 cohort의 index·count·age·energy·direction. 전체 이력의 마지막에 한 번만 기록한다. |

실제 최종 열 이름은 `IMPLEMENTATION_VERIFICATION.json`의 `sample_final_schema`에 저장했다. 각 CSV의 첫 행도 같은 schema를 제공한다. 과학적 f64는 `.17e`로 내보낸다. 정의되지 않은 shape나 ratio는 빈 필드이며 0으로 바꾸지 않는다.

Append index는 이번 noncompact driver에서 지속되는 cohort ID다. 마지막 snapshot을 매 step 모두 내보내는 O(N²) 자료는 만들지 않는다. 출생 시계가 f64에서 우연히 같아지더라도 서로 다른 cohort index와 원 label을 유지한다. 원 birth time·geometry·direction·energy를 합치거나 다른 하나의 시각으로 옮기지 않는다.

`K_i`는 원 owner의 `CharacteristicRay::new`가 정규화한 방향을 사용하여 `a_birth_i * E_birth * n_unit_i`로 기록한다. 원 raw birth direction은 template CSV에 따로 보존한다. `K*_ev_scale` 열 이름은 기하학적 scale factor와 eV를 사용한 수치 convention을 명시한다. Parent audit는 이 값으로 `sqrt(sum((K_i/a_end_i)^2))`와 방향을 다시 계산할 수 있다.

## 세 측도의 분리

`kernel_*_unit` 진단은 단위 born count, 상수 방출률·상수 selector opacity의 참조 문제다. 각 rule의 target age와 actual emitted quadrature weight를 사용한다. 이 shape는 수치 kernel의 조건부 분포 진단이며 실제 비어 있는 source 측도의 shape로 해석하지 않는다.

Template의 `native_source_frozen_*` 진단은 실제 출생 count와 represented birth clock을 사용하면서 propagation만 selector opacity에 동결한 반사실적 비교다. 실제 source amplitude 변화가 포함되므로 그 참조 편차를 순수 birth quadrature 오차라고 부르지 않는다. 별도의 birth-row `native_source_frozen_survivor_com3`는 실제 count에 `exp(-kappa*(t1-tb))`를 직접 곱한다. Certificate 내부는 tau와 normalized age를 사용하므로 두 계산 경로의 마지막 f64 roundoff는 다를 수 있다.

`native_after_photo`와 `native_accepted`는 실제 solver의 count와 raw 연령 moment다. 진화하는 opacity와 Killing 경로가 반영되어 있다. 이 값을 상수-kappa reference error certificate라고 해석하지 않는다. 실제 native 분포와 reference 분포의 적절한 비교 또는 mass-TV 보정은 독립 이론/분석 작업의 계약을 따른다.

`clock_age_defect_x`는 `(t1-tb)/dt-x_target`, `clock_age_defect_s`는 `(t1-tb)-dt*x_target`다. 후자는 전자에 dt를 다시 곱한 값과 나눗셈 roundoff 때문에 다를 수 있어 둘 다 보존했다. Panel에서도 nominal width와 두 represented endpoint의 차이를 따로 기록한다.

원 source의 positive 계약은 유지한다. 새 native source-off 물리 경로를 만들지 않았다. 빈/zero raw 측도, subnormal count, raw moment term의 underflow는 진단 helper에서 명시적으로 다룬다. `born_count_underflow`와 frozen-reference/source survival underflow는 양의 입력으로부터 0이 반올림된 경우를 표시한다. 최종 native count가 0이라는 사실만으로 정확한 흡수와 f64 underflow의 원인을 역추정하지 않는다.

## 실제 검증과 보존한 첫 실패

신규 9개 test는 다음 위험을 검사한다: fitted/legacy의 Off 직접 위임, 양·음 BASS에서 On의 전체 물리 bit parity, predictor 제외와 실제 birth append join, 실제 rate gas 및 source opacity 일치, normalized Killing ray, quota와 잘못된 monitor control의 물리 무영향, legacy 관측 미지원의 별도 분류, `Cx(WorkLimit)` 및 음수 population의 원 분류와 입력 불변, zero/thick opacity의 panel width와 clock rounding, 바뀐 weight·불완전 panel의 거부, empty/zero/subnormal/invalid measure, CSV 행 join과 기존 파일 덮어쓰기 거부다.

`SCOPED_TESTS_INITIAL.log`와 `SCOPED_TESTS_FINAL.log`에 각각 9/9 PASS를 보존했다. 최종 underflow flag와 직접 초 단위 clock defect를 포함한 버전도 테스트했다. 최초 strict Clippy는 새 driver의 중첩 `if` 하나를 `collapsible_if`로 지적했다. 같은 파일을 조건 연결 구문으로 고친 뒤 strict Clippy가 PASS했다. 최초 로그는 `SCOPED_CLIPPY_INITIAL.log`, 최종은 `SCOPED_CLIPPY_FINAL.log`에 남아 있다. 이를 물리·수렴 실패로 분류하지 않는다.

작은 실제 source-native 실행은 `SIGNED_MINUS`, donor grid 121, `Nt=1`, `T=1e9 s`, `r=1`이다. 최종 출력은 `sample_final/` 아래에 있다. 이전 schema sample은 `sample/`에 별도 보존되어 있고 후속 분석은 `sample_final`을 사용한다. 계획된 긴 Nt16/r8 실행을 반복 실행한 자료가 아니다.

## 재현 명령

샌드박스의 Rust 1.94.1 env를 불러온 뒤 새 manifest를 사용한다. 원 부모 manifest와 원 소스 파일을 수정하지 않는다.

```bash
source /workspace/scratch/996fc62899da/toolchains/rust_1_94_1_env.sh
cargo test --manifest-path br05/Cargo.toml --locked --offline --test native_birth_monitor
cargo clippy --manifest-path br05/Cargo.toml --locked --offline --lib --test native_birth_monitor --example native_birth_monitor_driver -- -D warnings
```

Driver는 원 11개 인자 뒤에 `monitor-off` 또는 새 출력 디렉터리 하나를 받는다.

```text
native_birth_monitor_driver case grid nsteps t0 duration split frozen birth_gl opacity cx_rtol off|refinement monitor-off|output_dir
```

기계 복제의 재검증은 이미 존재하는 final source를 수정하지 않는 `--verify-only`로 실행한다. `--proof`는 새 확인 결과 파일을 지정한다.

```bash
python3 generate_monitored_midpoint.py --unit /path/to/unit --proof /tmp/BR05_HOOK_REPLAY.json --verify-only
```

코드가 고정된 이후에는 runtime의 실제 전체 검증·실행 영수증, 독립 수치 감사와 이론 감사를 합쳐 bounded unit의 최종 판정을 내린다.
