# HE29의 선택적 VigilODE C ABI bridge

이 crate는 고정 VigilODE `a21d573980f66fe02891bd216153443b5352f921`의
`integrate_sequential_matrix_free_adaptive_observed`를 호출한다. 한 호출은
원래 HE29 cutoff 구간 하나를 정규화 시간 `u ∈ [0,1]`에서 전진시킨다.
새 solver나 물리식을 구현하지 않는다. 기존 네 Radau+DOP853 기준해 pair의
완료 상태는 이 lane의 성공 여부로 변경하지 않는다.

## 빌드 입력

필요한 레이아웃은 `work/rust_bridge`와 `work/vigilode`이다. 이 디렉터리를
`work/rust_bridge`에 놓고, Git에서 VigilODE의 위 SHA를 `work/vigilode`에
checkout한다. `Cargo.toml`의 path dependency는 이 레이아웃을 사용한다.
VigilODE를 파일 단위로 복원할 경우 root Cargo.toml과 Cargo.lock뿐 아니라
core/krylov/integrators의 Cargo.toml, 전체 src, integrators/build.rs 및
`fixtures/rodas5p_coefficients_snapshot.json`이 필요하다.

```bash
cargo build --manifest-path work/rust_bridge/Cargo.toml --release --locked --lib
```

Rust 1.94.1, edition 2024를 요구한다. 배포된 Cargo.lock은 a21d 원본의
registry package/version/checksum을 유지하며 실제 `cargo generate-lockfile
--offline`로 bridge 의존성 94개(root 포함)에 맞게 생성했다. 고정 vendor가
준비된 환경은 `--offline`을 추가할 수 있다. 원래 VigilODE release의
`panic=abort`를 이 FFI에 적용하지 않는다. 이 crate의 독립 workspace는
`panic=unwind`, opt-level 2, LTO false, codegen-units 16을 명시하며,
`panic=abort` 빌드는 compile_error로 거부한다.

## 실제 호출 계약

정확한 C 선언과 구조체 순서는 `include/he29_vigilode_bridge.h`에 있다.

```c
int32_t he29_vigilode_segment(
    size_t n, const double *z0,
    He29RhsCallback rhs, He29JvpCallback jvp,
    He29RhsCallback partial_u, void *context,
    double initial_step, double max_step, size_t max_attempts,
    double *z_out, He29Stats *stats,
    char *json_out, size_t json_capacity);
```

호출자는 길이 n의 유한 초기값, 출력 배열, 유효한 Stats와 JSON 버퍼,
호출이 끝날 때까지 살아 있는 세 callback/context를 제공한다. 모든
callback은 출력의 n개 값을 써야 하고, 실패하면 nonzero를 반환해야 한다.
버퍼의 비중첩·유효한 주소·수명은 C 호출자 계약이다. 권장 JSON 용량은
65536 byte이며 필요한 길이는 `json_required_bytes`로 반환한다.

Python 쪽의 `VigilODEBridge`는 build receipt와 library SHA256 및 네 Rust
source 파일의 해시를 확인한 뒤 CDLL을 연다. `segment(callbacks, z0)`는
통과한 endpoint와 evidence를 반환하고, 중단·실패는 `VigilODEFailure`에
evidence와 마지막 저장된 관측 상태를 담아 전달한다. Python callback의
예외는 모두 callback 내부에서 잡아 nonzero C status로 바꾼다.

| 값 | 의미 |
|---|---|
| 0 | [0,1] 두 관측이 완성되고 최종 값이 유한함 |
| 1 | attempt/min-step 등으로 중단된 부분 관측 |
| 2 | 인수·길이·유한성·설정 계약 실패 |
| 3 | 외부 RHS/JVP/partial_u callback 실패 |
| 4 | solver가 CoreError를 반환함 |
| 5 | bridge 안에서 Rust panic을 잡음 |
| 6 | 다른 solve가 실행 중이므로 동시 진입 거부 |
| 7 | JSON 버퍼가 부족함; 완전한 성공으로 해석 금지 |

`catch_unwind`는 unwind 가능한 Rust panic만 잡는다. 잘못된 외부 주소,
segmentation fault, process abort, C 경계를 넘어 던져진 외부 예외를
복구하지 않는다. bridge는 단일 전역 mutex와 sequential integrator만
사용한다. OdeProblem의 Send+Sync 타입 조건은 callback 병렬 실행 허가가
아니다.

## 물리 시간 및 Jacobian

`t = left + u Δt`, `y = S z`에 대하여 callback은 다음 양을 제공한다.

\[
f_u = \Delta t\,S^{-1}F(t,Sz),\qquad
J_u v = \Delta t\,S^{-1}J(t,Sz)Sv,
\qquad
\partial_u f_u = \Delta t^2 S^{-1}\partial_tF(t,Sz).
\]

HE29 Python adapter가 기존 `RefinedSourceModel.rhs/jac`, 기존 state scale,
원래 cutoff 구간과 source table을 그대로 사용한다. 부분 시간 미분의
finite difference는 실제 표현 가능한 시간과 구간 안의 점으로 계산한다.
VigilODE의 기본 비자율 central difference를 사용하지 않는다. 그 기본값은
`t±sqrt(eps)*max(|t|,1)`를 사용하므로 물리 구간 밖으로 나갈 수 있다.

적응 허용치는 고정된 `rtol=1e-10`, `atol_scaled=1e-12`이다. 선택한
linear method는 GMRES이며 나머지 `LinearSolverConfig`는 pinned default다.
Python의 exact-state Jacobian cache는 같은 물리 시간과 scaled-state
byte가 일치하는 경우만 재사용한다. native microphysics owner는 그대로다.

## 관측과 판단 범위

OutputSchedule은 [0,1]뿐이다. driver는 출력점에서 step을 잘라 endpoint를
직접 계산한다. dense interpolation을 사용하지 않는다. 반환된 estimator,
attempt 수, 선형해법 work counter는 solver 진단값이며 photon/energy/species
ledger나 연속적분 오차상한을 대체하지 않는다.

부분 반환에서 `final_u=0`과 초기 상태만 보일 수 있다. 이는 마지막으로
저장한 관측이 초기점이라는 뜻이다. 마지막 내부 step의 상태나 최종해로
재해석하지 않는다. 원래 HE29 ledger와 같은 table/model의 기준해 비교는
상위 Python runner가 별도로 수행한다.

## 작은 실제 FFI 검사

```bash
python rust_bridge/tests/smoke_bridge.py \
  --library /absolute/path/libhe29_vigilode_bridge.so \
  --receipt /absolute/path/BUILD_RECEIPT.json \
  --output /absolute/path/SMOKE_BRIDGE.json
```

검사는 동일한 Python 클래스로 알려진 두 상태 비자율 해와 양끝 domain,
callback 예외 전달, 한 attempt 후의 부분 관측을 확인한다. 기존 HE28/HE29
campaign 및 VigilODE의 이전 test/benchmark suite는 호출하지 않는다.
이 검사의 endpoint threshold는 작은 해석해 회귀 검사에만 해당하며 HE29
물리 허용치나 새로운 solver-wide 오차상한이 아니다.
