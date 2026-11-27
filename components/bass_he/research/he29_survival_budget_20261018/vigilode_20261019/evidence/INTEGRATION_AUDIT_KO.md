# HE29 선택적 VigilODE 통합 — 고정 소스 조사와 새 FFI 실행

## 현재 결론

고정 VigilODE `a21d573980f66fe02891bd216153443b5352f921`의 실제 sequential
RODAS5P/GMRES integrator를 호출하는 Rust cdylib를 구현했고 Rust 1.94.1에서
`cargo build --release --locked --offline --lib`가 통과했다. 동일한 상위
Python `VigilODEBridge`와 `SegmentCallbacks`를 사용하는 새로운 작은 FFI
검사 3개도 실제 실행에서 통과했다. 이 결과는 새 연결부가 동작한다는
증거이며 HE29의 네 기준해 pair, native 물리 case, 성능 우위를 완료로
올리는 결과가 아니다.

보호 대상은 HE29 코드·테스트 `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f`,
원래 microphysics owner `f7830e2f55e7a1938bc3c98f61b60651f8dae474`,
네 Radau+DOP853 pair와 기존 허용치다. 이 하위 작업은 이를 수정하지
않았고 기존 HE28/HE29 또는 VigilODE suite를 재실행하지 않았다.

`skill_context_used`: physmath-research-loop 1.3.0의 SKILL,
POLICY_INTEGRATION, THEORY_LOOP, CODING_LOOP, SUBAGENT_MODE를 읽었다.
범위는 R2/C2–C3의 실제 저장소 조사 및 부모가 추가 위임한 새 bridge C5다.
추가 하위 agent나 이전 연구의 전면 재심사를 만들지 않았다.

## 1. GitHub 상태와 정체성

| 대상 | 실제 관측 |
|---|---|
| default `main` | `8d0c79184e09efb5bdadc24a6315c60a71a44264` |
| 사용한 활성 branch | `claude/nice-dijkstra-208xq0` |
| 고정 활성 소스 | `a21d573980f66fe02891bd216153443b5352f921` |
| 별도 all-DAG branch | `ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406` |
| 별도 cloud-completion branch | `86afb40adcb0eda00c017c44b3553a8479c6c640` |
| 실제 읽은 원래 benchmark 묶음 | PR71의 `fa07baf27a37674848d963e30e010d54e4af3f33` |
| PR71 중간 관측 | `0bab431e1031f86eb3ddb44371240bce49ae2376` |
| PR71 마지막 관측 | `1b64c5b6b08340496d30dc8bf134f8725a65f510`, open/draft, updated 2026-10-19T12:59:46Z |

all-DAG와 cloud-completion은 a21d와 각각 diverged다. 비교에서 a21d는
all-DAG에 대해 ahead 12/behind 21, cloud-completion에 대해 ahead 19/behind
9로 나왔다. branch 이름의 “completion”을 최신 공통 구현으로 간주하거나
이 branch들의 결과를 a21d binary 결과로 합치지 않았다. API 근거는
[고정 활성 소스](https://github.com/cosmosapjw-quantum/vigilode/tree/a21d573980f66fe02891bd216153443b5352f921)와
[PR71](https://github.com/cosmosapjw-quantum/vigilode/pull/71)이다.

GitHub exact-revision connector로 실제 파일을 materialize했다.
`FETCHED_MANIFEST.json`과 `LOCAL_IDENTITY.json`은 원본 source 및 당시
benchmark evidence 166개, 5,647,456 byte 모두의 Git blob 일치를 기록한다.
이 중 a21d 파일은 161개다. 이후 관측한 PR71의 작은 status 파일 4개는
`LATEST_PR71_RETURN.json` 및 `latest_pr71_1b64/`에 별도 보존했다.
현재 소스에 없는 실행 결과를 만들어 넣지 않았다.

## 2. 실제 코드에 있는 수치 방법과 Rust 의존성

RODAS5P의 arbitrary-vector problem, adaptive sequential matrix-free driver,
endpoint output collector, dense/banded fast driver, small-static 및
matrix-free fast workspace, GMRES/LGMRES/GCRODR 경로가 실제 Rust source에
있다. 별도의 BDF1/2 및 RadauIIA reference 구현도 있지만 이를 SciPy
Radau/DOP853와 동등한 기준해로 교체하지 않는다.

| crate/기능 | 읽은 구현 및 이번 사용 |
|---|---|
| `rodas5p-integrators` | OdeProblem, RODAS5P, adaptive driver, output collector; 이번 bridge가 직접 호출 |
| `rodas5p-krylov` | Krylov linear solver; 이번 lane은 GMRES 선택 |
| `rodas5p-core` | 계수, 선형해법 설정, 오류형, WorkCounters |
| `faer 0.24.4` | 고정 workspace의 실제 dense/sparse linear algebra 의존성 |
| `rayon 1.12.0` | upstream 의존성에 포함됨; 이번 foreign callback 경로는 sequential |
| `serde/serde_json` | 설정·진단 직렬화; json은 `1.0.151` 고정 |
| `sha2 0.10.9`, `hex 0.4.3`, `thiserror 2.0.19` | 기존 core의 실제 의존성 |

root workspace는 version 0.1.0, edition 2024, rust-version 1.94.1, MIT다.
MIT LICENSE 본문과 Cargo.toml을 읽었다. 기본 integrators feature는 빈
배열이며 audit2 연구 feature는 이번 bridge에서 활성화하지 않았다.
[root Cargo.toml](https://github.com/cosmosapjw-quantum/vigilode/blob/a21d573980f66fe02891bd216153443b5352f921/Cargo.toml),
[integrators Cargo.toml](https://github.com/cosmosapjw-quantum/vigilode/blob/a21d573980f66fe02891bd216153443b5352f921/crates/rodas5p-integrators/Cargo.toml),
[LICENSE](https://github.com/cosmosapjw-quantum/vigilode/blob/a21d573980f66fe02891bd216153443b5352f921/LICENSE).

기존 source tree에는 관련 세 crate의 test 파일 262개가 존재한다. 이는
파일 존재 조사이고 이 하위 작업의 test 실행 수가 아니다. 이전 161-suite,
`solve_stiff` example, 이전 benchmark를 실행하지 않았다.

## 3. 실제 API와 연결 결정

`OdeProblem::new(name, dimension, rhs, rhs_batch, jacobian, jvp, partial_t,
autonomous, mass_matrix, exact_solution)`는 `CoreResult<OdeProblem>`을
반환한다. scalar/vector callback은 Arc의 `Fn + Send + Sync`다. 필요한
입력 길이는 `dimension`이며 Jacobian 또는 JVP 중 적어도 하나가 있어야
한다. RHS만 주고 자동 finite-difference JVP가 생길 것으로 가정하면 안 된다.
[problem.rs](https://github.com/cosmosapjw-quantum/vigilode/blob/a21d573980f66fe02891bd216153443b5352f921/crates/rodas5p-integrators/src/problem.rs).

이번 bridge는 RHS, JVP, explicit partial-time callback을 모두 주며,
autonomous=false, mass_matrix=None, exact_solution=None이다. 호출 함수는
다음과 같이 실제 공개 API와 일치한다.

```rust
integrate_sequential_matrix_free_adaptive_observed(
    &problem, (0.0, 1.0), z0, &linear, &adaptive, &output,
)
```

`linear.method = Gmres`; 나머지 pinned default는 linear rtol 1e-11,
atol 1e-13, restart 40, maxiter 200, preconditioner None, initial guess
Previous다. adaptive rtol 1e-10, scaled atol 1e-12는 HE29 그대로다.
step budget 인수는 한 cutoff 구간의 정규화 시간에 적용한다.
[solver_types.rs](https://github.com/cosmosapjw-quantum/vigilode/blob/a21d573980f66fe02891bd216153443b5352f921/crates/rodas5p-core/src/solver_types.rs),
[integrate.rs](https://github.com/cosmosapjw-quantum/vigilode/blob/a21d573980f66fe02891bd216153443b5352f921/crates/rodas5p-integrators/src/integrate.rs).

비자율 문제에서 partial_t를 생략하면 upstream은
`t±sqrt(eps)*max(abs(t),1)` 중심 차분을 사용한다. 큰 proper time 또는
cutoff/table 경계에서 이 점은 원래 구간 밖일 수 있다. 상위 Python
callback이 기존 physical RHS와 구간 안의 실제 binary64 시간으로 시간
미분을 계산하도록 했다. 이 수치 미분을 매끄러움 증명이나 엄밀 미분값으로
표현하지 않는다.

각 구간에서 `t=left+uΔt`, `y=Sz`로 정규화하면 기존 물리식 F와 Jacobian J를
`Δt S^-1 F`, `Δt S^-1 J S v`, `Δt² S^-1 ∂tF`로 전달한다. 원래 Python
`RefinedSourceModel`의 sparse Jacobian을 동일 시간·동일 scaled-state
byte에서만 cache한다. 이런 연결은 원래 microphysics stdio 경로를 유지한다.
이번 구현은 native microphysics를 다시 작성하거나 in-process 구현과의
동등성을 주장하지 않는다.

OutputSchedule은 [0,1]이며 driver가 step을 조정해 endpoint를 실제로
계산한다. 별도의 dense interpolation은 없다. 결과는 observed의 t/y,
success/message, WorkCounters, internal/output-clipped steps와 adaptive
attempt/accept/reject 진단이다. 내부 error estimator는 state 오차의
전역 상한이 아니며 photon/energy/species ledger를 대체하지 않는다.
[output.rs](https://github.com/cosmosapjw-quantum/vigilode/blob/a21d573980f66fe02891bd216153443b5352f921/crates/rodas5p-integrators/src/output.rs).

## 4. 완료한 코드와 실제 build

최종 crate는 BASS_HE 작업본의
`research/he29_survival_budget_20261018/vigilode_20261019/rust_bridge/`에 있다.
Cargo.toml, Cargo.lock, src/lib.rs, C header, README_KO.md,
tests/smoke_bridge.py를 작성했다. path dependency는 staging의
`work/rust_bridge`, `work/vigilode` 레이아웃에 맞춘다.

기존 별도 workspace의 Rust 1.94.1과 vendored registry를 읽기 전용으로
재사용했다. 새 CARGO_HOME은 현재 작업의 `vigilode_build/cargo_home`,
target/TMPDIR은 별도 `/dev/shm/he29_vigilode_20261019`다. 기존 benchmark
target 또는 다른 workspace cache를 수정하지 않았다. Cargo가 offline으로
원본 lock의 버전/source/checksum을 유지하여 94 package의 새 root lock을
생성했다. source/test physics를 바꾸지 않았다.

첫 compile은 materialization에서 빠진 원본 integrators/build.rs 때문에
compile-time profile env 3개가 없어서 실패했다. 고정 a21d의 실제 build.rs
(Git blob `725309e91c989f79e5a5e75307addd7ae3478937`)를 복원해 해결했다.
프로파일 env를 임의로 꾸며 넣지 않았다. 최종 source snapshot을 검증한
build는 45.5167초, exit 0이다. 처음 실패의 진단 및 hash 요약은 별도
receipt에 남겼고, 그 최초 raw log는 뒤이은 attempt에 의해 덮인 사실을
명시했다. 최종 build raw JSONL/log와 source-before snapshot은 보존했다.

| 새 binary | 값 |
|---|---|
| 파일 | `vigilode_build/artifacts/libhe29_vigilode_bridge.so` |
| 크기 | 5,245,352 byte |
| SHA256 | `8d2f1271726781d2b000f0cd5eaadb0adac8029eb9357f786bfd647cea390460` |
| receipt | `vigilode_build/receipts/BUILD_RECEIPT.json` |
| compile identity | a21d upstream 파일 161개와 네 bridge source의 before/after 일치 |

`SOURCE_IDENTITY_ADDENDUM.json`은 161/166의 관계를 명시한다. 처음 intake
161개는 a21d source 158개와 fa07 evidence 3개였고, 이후 source 3개와 CSV
2개를 더했다. 최종 166개 중 compile source snapshot은 a21d 161개다.
그 snapshot에는 필수 integrators/build.rs와 coefficient fixture가 이미
포함된다. 이 수는 Rust compilation unit 수가 아니다. addendum을 쓰는
동안 BUILD_RECEIPT의 SHA256
`dd1e5a58b94a7f5d6981377a05d80386cff9d6079d3c9266b043670f7c6c48bf`와
이를 가리키는 raw smoke receipt는 한 byte도 바꾸지 않았다.

release는 panic=unwind, opt-level 2, LTO false, codegen-units 16이다.
callback 실패·부분 결과·Rust panic·동시 진입·JSON 부족을 서로 다른
status로 전달한다. Python은 모든 foreign callback 예외를 잡아 nonzero
status로 변환한다. 잘못된 외부 포인터, segfault, process abort는 이
`catch_unwind` 범위에 속하지 않는다.

## 5. 새로운 작은 실제 FFI 결과

`VigilODEBridge`가 실제 library와 source receipt를 확인한 뒤 CDLL을
열었고 같은 `SegmentCallbacks`를 통해 다음 3개를 실행했다.

| 새 검사 | 실제 결과 |
|---|---|
| 두 상태 비자율 해와 양끝 domain | PASS; 최대 scaled endpoint 절대 차이 `4.065636716177323e-13` |
| callback의 Python 예외 | PASS; status 3, success false, 첫 callback에서 중단 |
| max_attempts=1 | PASS; status 1, success false, 저장된 관측은 초기 u=0 상태 |

해석해는 scaled state `z1=1+u+u²`, `z2=2 exp(-3u)+u`이며 physical
time 범위는 [37.25,37.625], scale은 [3,0.002]다. 완료 case는 46 attempts,
45 accepted, 1 rejected, 375 RHS callback, 2139 JVP, 46 partial-time
callback, direct factorization 0이었다. 모든 physical 조회는 구간 안에
있었다. 양끝 시간미분 오차 최대는 `5.475868647408788e-9`다.

smoke endpoint threshold 3e-9는 이 작은 해석해 연결 검사에만 쓰였다.
HE29 fraction/temperature/ledger gate를 바꾸지 않았다. 작은 모델의 0.106초
실행시간은 BASS_HE 또는 타 solver 대비 성능 수치가 아니다.
원본 HE29 case 실행은 0개이며 기존 suite 실행도 0개다.
실제 raw evidence는 `vigilode_build/receipts/SMOKE_BRIDGE.json`
(SHA256 `2cce1fce56812d9e64c73d8aa51876b8eb5463e64c80dd32a926169561e6502b`)이다.

## 6. 기존 benchmark를 어디까지 사용할 수 있는가

기존 run1 measured source는 `ccaeaa50beb4580505a36d25ccb919ec3ca38c7f`,
run2 measured Rust source는 `8a8bd409b1d96c7b7421f496d229e119fd3d284e`다.
후속 a21d tip을 그 binary의 measured revision으로 바꾸지 않았다.
README만 인용하지 않고 fa07의 원래 CSV 2개를 읽고 byte/Git blob을 맞췄다.

run1 endpoint CSV는 154 completed rows다. run2 CSV는 2700 rows 중
2639 ok, 54 refused, 7 solver_failure이다. ok 중 기록된 R_up<=1은 2329개,
<=10은 2580개, <=100은 2626개다. 예를 들어 nonlinear ProtheroRobinson,
uniform101, rtol1e-8, h0scale1에서 seq-direct R_up은
6.632710004483773e-7, dense-off는 1751.990412875421,
dense-enforce는 1.0933030660056111이다. 이 차이는 endpoint 관측과 dense
출력의 근거를 섞지 말아야 한다는 실제 이유다.

[run1 원본 CSV](https://github.com/cosmosapjw-quantum/vigilode/blob/fa07baf27a37674848d963e30e010d54e4af3f33/research/benchmark_results_20261019/run1/endpoint_results.csv),
[run2 원본 CSV](https://github.com/cosmosapjw-quantum/vigilode/blob/fa07baf27a37674848d963e30e010d54e4af3f33/research/benchmark_results_20261019/run2/ct_results_2700.csv).

Production audit의 범위도 generic RODAS5P의 문제별 scoped use이며,
global output accuracy, packet/Leja binary64 total certificate 및 Diffsol
headline speed/allocation은 HOLD다. 빠진 예전 profiler/time/allocation
전체 receipt를 지금 검증한 데이터로 취급하지 않았다.
[원본 production decision](https://github.com/cosmosapjw-quantum/vigilode/blob/a21d573980f66fe02891bd216153443b5352f921/research/production_audit_20261018/DECISION.json).

## 7. 작업 중 새로 게시된 PR71 반환

0bab의 run39252371864는 `BOOTSTRAP_ONLY`, `benchmark_executed:false`였다.
마지막 1b64 관측은 run39255702592를 추가했다. 이 묶음에는 build/native
작은 test 로그와 binary hash가 있으나 전체 accuracy/timing campaign은
막혔다. 실제 MANIFEST의 source는
`bab3902b3501d7fede9add7fd646074b9368adb8`, binary SHA256은
`36fdc0c12435a9fa3bdaa4cac4833c16a62c389b9db26a4734fcfc697f2d4dc7`이다.
arms는 vigilode-fast, diffsol-bdf, netlib-dvode다.

EXIT_STATUS는 exit_code 1, stage accuracy_and_timing이며 campaign.log는
첫 Robertson reference를 JSON으로 저장하다 NumPy int32가 직렬화되지
않아 중단된 stack trace를 담는다. BLOCKER.json도 TypeError/BLOCKED다.
따라서 새로운 완료 비교나 HE29 native 반환으로 셀 수 없다. 새 비교
코드/lock을 현재 a21d bridge dependency에 조용히 섞지 않았다.
[MANIFEST](https://github.com/cosmosapjw-quantum/vigilode/blob/1b64c5b6b08340496d30dc8bf134f8725a65f510/research/strict_solver_comparison_20261019/runs/39255702592/MANIFEST.json),
[BLOCKER](https://github.com/cosmosapjw-quantum/vigilode/blob/1b64c5b6b08340496d30dc8bf134f8725a65f510/research/strict_solver_comparison_20261019/runs/39255702592/BLOCKER.json),
[campaign log](https://github.com/cosmosapjw-quantum/vigilode/blob/1b64c5b6b08340496d30dc8bf134f8725a65f510/research/strict_solver_comparison_20261019/runs/39255702592/campaign.log).

## 8. HE29에 남긴 구체적인 다음 경계

이미 구현한 lane은 기존 physical RHS/Jacobian과 table/clock을 그대로
연결하면서 Rust의 integrator와 Krylov/linear algebra를 재사용한다.
가스와 photon이 결합된 Jacobian을 자동으로 banded라고 선언하지 않았다.
현재 full sparse Jacobian의 JVP와 exact-state cache는 기존 구조를 쓰지만
새 arrowhead preconditioner의 정확도/성능을 검증한 결과는 없다.

다음 HE29 실행은 원래 ledger 및 같은 model/table의 결과를 함께 반환해야
한다. 선택적 VigilODE 결과는 네 원래 Radau+DOP853 pair의 완료를 대체할
수 없다. native stdio 비용 제거, dense 출력, 전역 정확도·성능 승격은
해당 변경과 입력을 실제로 검증한 후에만 판단한다. 연속 spectrum, 전체
EoR, upstream Grackle 전체 동등성, 관측 Bianchi/CMB HOLD는 유지한다.
