# RUN19 Unit A — native T 계수 공유와 source-off 배치

## 변경과 검증 범위

원본 SSOT는 `99e07bcff126d0a73a03bafc4b71e0b735dbcc3e`의
`run13/recovered/code/rei_bass_coupled`이다. 새 코드는 `run19/native`에만
두었다. 원본 91개 파일과 기존 RUN13 standard/tight 이력은 수정하거나
재실행하지 않았다. 이 단위는 source-off 순간 gas RHS의 구현과 성능을
다루며 새로운 gas/transport IVP는 0회다.

`gas_rates`는 Direct 기본값을 유지한다. 새 `gas_rates_with_backend`는
현재 EOS 온도에서 하나의 `PreparedIgmRates`를 만들고 H/He와 D가 공유한다.
D의 H-equality approximation, 계수식, 단위변환, CI/RR/CE/CX와 에너지
ledger assembly는 그대로다. `d_atomic_rhs_from_prepared`는 온도의
`to_bits()`, evaluator ID, photo/provider의 D threshold와 source를 검사한다.
evaluator ID는 수치 알고리즘 종류이며 개별 table 인스턴스나 오차인증 ID가 아니다.
CX-only mask2도 기존 D atomic validation을 유지한다.

`GasRateWorkspace`는 하나의 immutable backend를 빌려 쓰는 one-entry cache다.
새 상태에서 EOS를 다시 계산하고 온도 비트가 같을 때만 T 계수를 재사용한다.
밀도, 전자수, 불투명도와 heating power는 캐시하지 않는다. 두 다른 온도를
같은 구간으로 묶거나 온도를 양자화하지 않는다. `gas_rates_batch_into`는
호출자 소유 출력에 기록하고 worker별 workspace를 사용한다. worker는 1–4,
batch는 최대 65,536개다. 오류가 나면 부분 출력 전체를 폐기해야 한다.

서버는 기존 `RHS`, `STEP`, `STEP_TIGHT` 숫자 배열을 보존하면서
`--rates direct|table`, `--workers 1..4`, `META`, `RHS_BATCH`를 추가했다.
`STEP` 계열은 선택된 RHS backend와 무관하게 기존 Direct owner를 사용한다.
이번 단위에서 STEP/trajectory를 실행하지 않았다. 새 배치 프로토콜은 다음과 같다.

```text
RHS_BATCH count mask Tcmb (n[13] U)*count
BATCH_OK count 28
OK <28 outputs>          # 입력 순서로 count행
BATCH_END evaluations preparations exact_temperature_hits
```

입력 parsing과 scalar 출력은 고정 크기 배열을 사용하고, 요청 line buffer를
재사용한다. 배치 응답은 묶음 끝에서 flush한다. 명시적 SIMD, fast-math,
Horner/FMA 변환은 도입하지 않았다. 현재 vectorization 이득을 주장하지 않는다.

## 이번 실행의 실제 검사

- `run19_shared_rates`: **6 PASS**, compilation 포함 2.886225624 s, test body 0.01 s.
- server example tests: **2 PASS**, compilation 포함 0.243530725 s.
- 11개 온도 × 3개 조성 × 8개 mask = 264개 순간 상태에서 원래 gas assembly의
  27개 vector 성분과 chemical 값이 새 Direct 경로와 **f64 bits 동일**하다.
- D direct/prepared의 전체 event 및 thermal ledger equality, 온도/evaluator/
  threshold guards, source/mask 오류, density-dependent power 재평가를 검사했다.
- Direct 및 opt-in table에서 typed batch worker 1/2/4가 scalar와 bits 동일하다.
- IPC의 동일 backend scalar/batch/worker/반복 간 응답 byte identity를 확인했다.

원래 gas assembly는 동일 benchmark/test executable에 원본 파일 그대로
include했다. 해당 원본이 호출하는 D direct entry는 이번 fork에서 공통화한
동일 event/energy assembly를 사용한다. 과거 binary를 재현했다고 주장하지 않는다.
기존 Rust 160 tests, Python 역사적 검증과 RUN13 IVP는 반복하지 않았다.

## 측정된 속도와 비용

AMD EPYC 9V74, affinity 0–3, cgroup CPU quota 8, 메모리 한도 8 GiB.
Rust 1.94.1 / LLVM 21.1.8 release 기본 설정, fast-math와 target-cpu override 없음.
공유 cloud CPU의 짧은 측정이며 clock/frequency를 고정하지 않았다. 원시 반복값과
최솟값/최댓값을 함께 보존한다. end-to-end trajectory 속도나 일반적인 병렬
speedup으로 승격하지 않는다.

Core 본 측정은 72개 조건, 조건당 8,192 RHS × 5회이며 전체 1.765060725 s였다.
대표 N=512, 매번 다른 온도에서는 원래 assembly **1,070.14 ns/RHS**,
shared Direct **722.04 ns/RHS**, opt-in loglinear table **446.65 ns/RHS**였다.
같은 온도에서는 원래 **1,097.25 ns**, shared Direct **684.98 ns**,
exact-T workspace **287.47 ns**였다. 온도가 바뀌는 경우 workspace 조회비용이
추가될 수 있으며, 이 경우의 cache hit은 0이었다.

N=4096 varying-T typed batch Direct의 worker 1/2/4는 각각
**691.37 / 394.37 / 299.43 ns/RHS**였다. table은
**449.19 / 307.29 / 163.25 ns/RHS**였다. N=512에서는 thread 시작·join 비용이
이득을 줄이거나 역전시켰다. worker 4를 새 기본값으로 삼지 않았다.

기존 65,537-node loglinear table 생성은 본 core 측정에서 **0.11005696 s**,
coefficient/mask payload는 **9,109,624 bytes**였다. 생성은 steady timing과 분리했다.

IPC는 **새 optimized scalar 서버와 새 batch 프로토콜**을 비교했다.
총 24개 조건 × 3회, command 전체 3.472792330 s였다. N=4096 Direct에서
같은 온도는 **22.600 → 4.544 µs/RHS**(batch1), 다른 온도는
**28.397 → 6.418 µs/RHS**였다. 이 시간에는 pipe roundtrip과 서버 float
formatting이 들어가고, 요청은 미리 format했으며 Python float 변환은 포함하지
않는다. raw 입력과 출력은 gzip으로 보존했다. table 서버의 META까지 startup
118.5–145.8 ms는 table 생성 포함값이며 steady 시간에 더하지 않았다.

## 정확도의 구분

Direct sharing/cache는 계수 보간을 추가하지 않는다. 선택적 loglinear table은
기존 근사이므로 Direct와 다른 결과를 낸다. 보존 IPC 9,216개 manufactured point
비교에서 CI/RR 양의 event 성분 최대 상대차는 **2.3688404866e-7**, heat는
**4.7308945540e-8**였다. 작은 차를 취한 H net species에서는 상대차가
**4.5448106070e-5**, chemical net에서는 **7.1713629273e-5**까지 커졌다.
이것은 cancellation의 실제 관측이며 raw coefficient 정확도를 net RHS 상대오차로
그대로 옮길 수 없음을 보여준다. 채널별 절대차와 해당 입력 index도 보존했다.
이 표본은 continuous table bound, Jacobian bound 또는 trajectory error bound가 아니다.

## 실행환경 복원

현재 첨부 Rust archive 192,287,020 bytes의 SHA-256은 실제로
`294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40`으로 확인했다.
51,085 tar members에서 unsafe path/link 0개였다. signature 인증은 하지 않았다.
rustc/cargo/rust-std 세 구성만 `/tmp/rei_run19_runtime/prefix`에 설치했고
작은 compiler probe를 실제 compile/run했다. prefix file bytes는 595,716,032다.
가용 소스는 dependency 없는 crate라 큰 vendor나 네트워크 설치가 필요하지 않았다.

`runtime/restore_minimal_rust.py`는 이 결과 뒤에 추가한 portable recipe이며
이번 실행에 다시 사용하지 않았다. 실제 설치 명령은 `install_and_probe.py`와
`INSTALL_PROBE_RECEIPT.json`에 있다. 첨부의 기존 03-env 경로와 09-bootstrap
전체 설치/전체 테스트는 실행하지 않았다.

## 재현

새 checkout에서는 원본 RUN13 gas source도 함께 있어야 한다. 실행환경을 선택한
후 `native`를 cwd로 두고, 새 output 디렉터리와 외부 target 디렉터리를 사용한다.

```sh
cargo test --release --offline --locked --target-dir "$REI_TARGET" --test run19_shared_rates
cargo test --release --offline --locked --target-dir "$REI_TARGET" --example gas_rhs_server
cargo build --release --offline --locked --target-dir "$REI_TARGET" --example gas_rhs_server --example run19_gas_bench
taskset -c 0-3 "$REI_TARGET/release/examples/run19_gas_bench" --target-evaluations 8192 --repetitions 5
taskset -c 0-3 python -B examples/run19_ipc_bench.py --binary "$REI_TARGET/release/examples/gas_rhs_server" --output "$REI_NEW_IPC_OUTPUT" --repetitions 3
```

`REI_TARGET`와 `REI_NEW_IPC_OUTPUT`은 사용자가 선택한 새 writable 경로다.
`PATH`, `LD_LIBRARY_PATH`, `RUSTC`, `RUSTDOC`, `CARGO_HOME`, `RUSTFLAGS`의 실제
producer 값은 각 COMMAND.json에 있다. 코드·입력·로그·binary SHA는
UNIT_A_RECEIPT와 manifest에 있다. Unit A 원격 commit, archive SHA와 backup
위치는 root가 실제 게시 완료 뒤 별도 delivery receipt에 기록한다.

## 다음 미완료 작업

표현이 다른 T table의 비용/정확도 tradeoff와 cancellation-aware gas error를
같은 source에서 검증하고, 인증 목적이면 coefficient/Jacobian/trajectory
error budget을 따로 연결해야 한다. 원래 spectral continuum, angular,
birth-time 및 전체 물리 DAG 의무는 이 최적화로 완료되지 않는다.
추가 Li/Be RR 공급자와 isotope registry 통합도 이번 gas kernel에 포함하지 않았다.

