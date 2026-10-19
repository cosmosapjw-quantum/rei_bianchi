# BR06 Recovery R1: VigilODE 실사용과 Rust quadrature 경계

## 현재 적용 결과

VigilODE의 `rodas5p-core::damped_moments::compute_normalized_damped_moment`와 `directed::{Interval, exp_interval, sub_up, mul_down, add_down}`를 실제 계산에 사용한다. 원 core 파일은 수정하지 않았다. 새 `vigilode_moments.rs`는 양의 반구간 합성, source endpoint 조합과 폭 거부 조건만 담당한다. VigilODE의 RODAS5P 시간적분기나 Einstein/반응 owner를 BR06으로 교체하지 않았다. 현재 사용은 기록된 BR05 첫 단계의 동결 기체 source-integral 참조이며, 진화하는 전체 H/He/D 이력의 수렴 인증은 별도 DAG다.

검증 pin은 `a21d573980f66fe02891bd216153443b5352f921`이다. 읽기 전용으로 확인한 후속 `33f07ee3bfe067f47476bca71b26cf316e96d850`은 CLI 및 component-triage 연구 산출물을 바꾸었으며 사용한 core/krylov/integrator subtree와 Cargo/lock/license는 같았다. 이 관측은 보존된 14:33:49 UTC 기록이고, 복구 시점의 새 원격조회라고 표시하지 않는다. 정확한 과거 비교는 `REMOTE_ADVANCE_PROVENANCE.json`에 있다.

최종 17:57:36 UTC 읽기에서는 원격 branch가 `b56bb19ce85bc28a021138ee29689701a81bc4f0`까지 이동한 것을 확인하였다. a21 pin 대비 15 commits, 47개 파일이 바뀌었고, 이제 전체 core subtree도 동일하지 않다. 그러나 실제 사용하는 `damped_moments.rs`, `directed.rs`, `error.rs`의 Git blob은 모두 같았다. core 변경은 `ShiftedOperator`가 비정상 explicit matrix의 오류를 panic 대신 typed error로 돌려주는 수정과 관련 테스트다. BR06 scalar 경로는 이 operator를 호출하지 않는다. CLI도 바뀌었으며 fair-ab/krylov/integrator subtree, root Cargo/lock/toolchain/license, README와 fixtures는 그대로다. 정확한 비교는 `REMOTE_ADVANCE_PROVENANCE_R1_FINAL.json`에 있다. 검증 pin을 유지했고 새 HEAD 테스트나 자동 업그레이드는 수행하지 않았다.

## 왜 이 부분을 적용했는가

종료점 근처의 생존 광자는 작은 birth age에 집중된다. 정규화 age를 x, optical depth를 τ라 하면 필요한 스칼라 양은

    J_jk(τ) = ∫₀¹ exp(−τ x) x^j (1−x)^k dx,  0≤j,k≤2.

J00은 Φ, J10/J20은 출생 age의 첫째/둘째 원시 moment를 준다. 시간상 왼쪽·오른쪽 source 값을 각각 j_L,j_R라 하면 u=1−x이므로 선형 source 적분은 j_L J10+j_R J01이다. 물리적인 Δt 및 추가 age 차원의 Δt 거듭제곱은 directed scaling으로 별도로 곱한다.

큰 τ를 2z로 놓아 두 절반으로 정확히 나누면

    J_jk(2z) = 2^(−j−k−1) [ Σ_{l=0}^k C(k,l) J_jl(z)
                           + exp(−z) Σ_{r=0}^j C(j,r) J_rk(z) ].

모든 조합 계수가 비음수다. R1 adapter는 τ를 1 이하로 줄인 뒤 원 VigilODE kernel 9개를 부르고 이 식으로 복원한다. 음의 계수를 사용하는 높은 차수 cancellation recurrence를 도입하지 않는다. 수학적으로 비음수인 moment의 interval을 [0,∞)와 교차시키고, outward width가 보수적으로 계산한 atol+rtol×lower보다 클 경우 명시적으로 거부한다. 작은 interval을 얻었다는 사실과 kernel 포함관계 검증은 별도 증거로 남긴다.

이것은 scalar interval 검증이다. time-varying opacity/source/geometry를 동결해서 생기는 오차, 유한한 cohort age 표현의 오차, 원자 물리 입력 자체의 오차를 interval 안에 포함한다고 주장하지 않는다. 실제 birth cohort의 시간, geometry, Killing 상수, 방향, spectral/angular label은 BR06 주 참조 계산이 각각 보존한다. native scalar CSV에서만 8개 angular 방출률을 각 spectral label별로 더한다.

## 새로 실행한 수치 검증

새 R1 코드 SHA-256은 `b333bbaa9962f6e2ac09ace0afb9a3cccc76d2c56811be1e371d09557e5a3235`다. 중단 전 adapter의 원본 bytes는 복구하지 못했으므로 별도 revision으로 표시하였다. 이전 테스트 PASS를 계승하지 않았다.

`RECOVERY_R1_ADAPTER_FINAL_VERIFICATION.json`은 새 unit tests 3/3, strict Clippy, scoped rustfmt, 실제 252행 kernel CSV와 독립 theory agent의 Decimal110 검산을 묶는다. 선언한 τ=0부터 10^12까지 14점에서 dyadic 126/126행과 성공한 direct 117/117행이 포함관계를 만족했다. direct τ=10^12의 9개 NonFinite 거부를 그대로 남겼다. dyadic 최대 상대 폭은 1.65377316437947×10^−14다. direct kernel의 포함관계가 성립하더라도 일부 큰 τ의 폭은 매우 넓어 정확도 허용조건을 만족하지 않는다.

복구 후 원 48 spectral label의 native scalar 검산은 별도의 `theory/evidence/native_moments_r1/NATIVE_MOMENTS_DECIMAL_RECOVERY_R1.json`에서 7개 양×48=336개 포함관계를 새로 확인하였다. 최대 상대 폭은 1.37024582538387×10^−14다. exported binary64 τ, duration, source endpoint를 정확한 입력으로 해석하며, 실수 κΔt와 binary64 곱의 차이까지 자동으로 감싸는 것은 아니다. 실제 source 시간함수와 선형 endpoint 모델의 차이도 별도로 계산한다. 원시 age moment와 평균 age를 혼동하지 않는다.

## 실제 적용한 Rust package

`gauss-quad = "=0.3.2"`, default features off, std on을 사용했다. exact crate checksum은 `7ca151f2176d5222ce406dc00c8f42c4f5bfd974af994df74288cbd2e1907171`이며, 실제 vendored package의 22 payload files와 lock checksum은 `implementation/REGISTRY_RECOVERY_IDENTITY.json`에 묶였다. Cargo metadata와 원 source를 직접 읽었다. license는 MIT OR Apache-2.0, rust-version은 1.89.0이고 현재 sandbox 검증에는 Rust 1.94.1을 사용하였다.

실제 API는 `gauss_quad::legendre::GaussLegendre::new(NonZeroUsize)`와 nodes/weights이다. 원 source는 Bogaert 알고리즘에 의한 O(n) node/weight 생성을 명시한다. BR06은 결과를 [0,1]로 옮기고 내부 node, 양의 weight, 순서, raw weight sum을 검사한다. 이 규칙을 birth age, opacity 적분, event 적분에 사용하며, 각 해상도를 따로 제어한다. 단순 고정 전체구간 GL의 이름만 바꾸지 않고, optically thick age layer에 맞추어 양의 작은 패널로 분할한다.

고정 소스 스칼라 moment는 VigilODE interval kernel이 직접 맞는 도구다. 변수 기하의 실제 photon 경로는 양의 quadrature와 기존 Killing/opacity owner가 맞는 경계다. 추가 일반 ODE solver나 rootfinding crate로 기존 CX half-flow/four-corner 제어기를 바꾸는 작업은 이 bounded reference의 목적에 필요하지 않다. ODE solver 성능 우열이나 VigilODE production readiness에 관한 새 주장을 하지 않는다. VigilODE README의 2026-10-18 production audit는 packet/polynomial 최적화와 equal-work 성능 비교를 여전히 연구 범위로 명시한다.

## 정확한 복구와 한계

선택한 5개 crate, root Cargo/lock/toolchain/license, 14개 fixture 및 README 총 477개 파일을 Git subtree/blob와 각 payload hash로 복구하였다. `COMPLETE_SELECTED_SOURCE_RECOVERY_IDENTITY.json`이 파일마다 근거를 보존한다. `VIGILODE_EXACT_477_PAYLOAD_RECOVERY.tar`는 새 deterministic container이며, 중단 전 ZIP/tar 전체의 byte identity를 주장하지 않는다. 필요했던 coefficients fixture도 pin에 맞추어 복구했고 full core 의존성 빌드를 실제로 통과했다. 이 계수 fixture가 build에 필요하다는 것과 BR06이 RODAS5P solver를 실행했다는 것은 다른 사실이다.

새 wrapper의 source label 중복 거부 누락은 C9 복구 검토에서 발견되어 좁은 입력 검증과 실제 malformed CSV 테스트로 수정되었다. valid-input numerical/source parity는 유지되었다. 최종 R1 C9는 `c9_r1/C9_RECOVERY_R1_FINAL_REVIEW.json`에서 제한된 범위로 종료하였다. 최종 rlib로 새 22개 thin-opacity 사례를 실제 실행하고 독립 Decimal400으로 22/22를 확인했다. 20개 thin-route HI absorption은 correctly rounded, 두 normal-route 사례는 최대 2 ULP다. 독립 geometry work의 최대 상대오차는 이 통제 문제에서 3.91658895392577×10^−16이다. 이 결과는 별도 receipt에 묶으며 scalar moment PASS로 대신하지 않는다.

## 직접 읽은 일차 근거

- Pinned VigilODE README: https://github.com/cosmosapjw-quantum/vigilode/blob/a21d573980f66fe02891bd216153443b5352f921/README.md
- Pinned damped moments: https://github.com/cosmosapjw-quantum/vigilode/blob/a21d573980f66fe02891bd216153443b5352f921/crates/rodas5p-core/src/damped_moments.rs
- Pinned directed arithmetic: https://github.com/cosmosapjw-quantum/vigilode/blob/a21d573980f66fe02891bd216153443b5352f921/crates/rodas5p-core/src/directed.rs
- gauss-quad applied source: `implementation/vendor/registry/gauss-quad/src/legendre/mod.rs`, `Cargo.toml`, `LICENSE-MIT`, `LICENSE-APACHE`.
- Original algorithm linked by that source: https://doi.org/10.1137/140954969 (algorithm citation, not a newly reproduced paper result).
- New independent scalar evidence: `theory/evidence/vigilode_scalar_r1/VIGILODE_DECIMAL_RECOVERY_R1.json` and `theory/evidence/native_moments_r1/NATIVE_MOMENTS_DECIMAL_RECOVERY_R1.json`.
