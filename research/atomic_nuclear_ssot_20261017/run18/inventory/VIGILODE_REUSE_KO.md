# RUN18 VigilODE 재사용 조사

## 결론과 조사 범위

VigilODE의 구간 산술과 연속 잔차 provider 계약은 REI의 다음 gas/depth 검증 단위에 직접 재사용할 수 있다. 가장 작은 실행 경로는 **원본 `rodas5p-core/src/directed.rs`를 바이트 그대로 포함하고, REI의 저장된 DOP853 다항식과 정확 유리수 endpoint/jump를 별도 adapter에서 처리하는 것**이다. 기존 VigilODE의 RODAS5P quartic 검증기를 DOP853에 적용했다고 선언할 수는 없다. HHeD RHS, 원자 provider, BASS geometry, RUN13 입력은 이 조사에서 수정하지 않았다.

이번 단위는 원격 Git 조회, isolated sparse checkout, 실제 소스·계약·테스트 파일의 읽기와 바이트 identity 확인이다. Rust 빌드, 테스트 실행, RHS 호출, quadrature, IVP, 과거 RUN13 재실행은 모두 0이다. 역사적 PASS와 benchmark 값은 producer evidence로만 읽었다.

## 최신 원격 identity

2026-10-19 UTC 조회에서 기본 `main`은 `8d0c79184e09efb5bdadc24a6315c60a71a44264`이며, 해당 commit 시각은 2026-08-26이다. 따라서 현재 연구 소스로 main을 선택하지 않았다.

| 대상 | 실제 SHA | 이번 조사의 용도 |
|---|---|---|
| 최신 갱신 PR71 head `research/benchmark-results-20261019-dual` | `ac1cd2a4738c2441c92e5fdae5f70aba35e53544` | 실제 checkout |
| checkout tree | `471fb5a256f75e4ae7204831a2dbe24e4f152442` | 파일 identity |
| PR71 base `claude/nice-dijkstra-208xq0` | `a21d573980f66fe02891bd216153443b5352f921` | 현재 solver source anchor |
| 양쪽 공통 `crates/` tree | `c6598793eaa34a0be61e7d00af97dbd6b2aafcbf` | solver source 동일성 |
| `audit/production-readiness-20261018` | `da91553f019e011556ee042975f3cf05fc21a7c7` | 최신 제한·교정 근거 |
| `research/all-dag-completion-20261018` | `ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406` | 관련 source 변형 조회 |
| `research/cloud-completion-20261018` | `86afb40adcb0eda00c017c44b3553a8479c6c640` | 관련 source 변형 조회 |

[PR71](https://github.com/cosmosapjw-quantum/vigilode/pull/71)은 조회 시 open draft/unmerged였다. 실제 compare는 base보다 11 commits 앞서 있고 **19개 경로 add-only**이며 solver crate 변경은 0이다. PR body에 남아 있는 “6개 파일”은 최초 benchmark 게시 범위이고 최신 compare 전체는 아니다. 이어 붙은 strict solver comparison 실행 두 건은 각각 `BOOTSTRAP_ONLY`, `C2_RED/test_exit=1`로 보존되며 둘 다 `benchmark_executed=false`이다.

branches REST의 2개 page를 읽어 147개 ref를 확보했다. PR 조회는 최신 updated 20개 범위이며 모든 과거 PR을 검토했다는 뜻은 아니다. 선택 tree의 recursive 응답 6,070개 entry는 truncated=false였고 `AGENTS.md`는 없었다. 실제 checkout은 `/tmp/rei_vigilode_research`이다.

`directed.rs`와 `nonnormal_certificate.rs`는 위 세 관련 audit/cloud/all-DAG branch에서도 같은 Git blob이다. 반면 dense/provider 파일 일부는 다르므로 다른 branch의 이론·테스트 통과를 현재 source에 자동 이식하지 않는다. 자세한 원격 값과 API 범위는 `REMOTE_PRIMARY_SNAPSHOT.json`, `RELATED_COMMIT_IDENTITIES.json`에 있다.

## 실제 API와 REI 적용 경계

### 1. 바깥쪽 반올림 구간 산술 — 즉시 재사용 가능

[directed.rs](https://github.com/cosmosapjw-quantum/vigilode/blob/ac1cd2a4738c2441c92e5fdae5f70aba35e53544/crates/rodas5p-core/src/directed.rs)는 다음 API를 제공한다.

- `Interval::{new,point,exact_sum,add,sub,mul,div,scale,dot}`
- `add_up/down, sub_up/down, mul_up/down, div_up/down, sqrt_up/down, sum_up`
- `exp_interval`, power-of-two scaling helpers

덧셈은 TwoSum, 곱셈·나눗셈·제곱근은 FMA 기반 오차 부호와 작은 값의 보수적 인접 float 이동을 사용한다. `exp_interval`는 libm exp의 정확도를 보증으로 가정하지 않고, range reduction과 degree-20 Taylor interval 및 remainder를 계산한다. `x < -707`의 결과는 [0, 2^-1019]인 보수적 상자이고 `x > 709`는 거부한다. 작은 값 또는 구간 폭이 큰 입력에서 tight enclosure를 자동 보장하지 않는다.

이 파일의 외부 Rust 이름 의존은 `crate::{CoreError,CoreResult}`뿐이다. 따라서 명시적인 작은 error shim을 만들고 파일을 변경 없이 포함하는 경로가 가능하다. 전체 faer/serde workspace를 이 작은 산술 단위에 강제할 필요가 없다. public interval endpoints가 있으므로 adapter 입력은 `Interval::new`로 다시 검사하고 finite/domain 전제를 확인해야 한다.

원본 identity:

- 17,215 bytes
- SHA-256 `2adadb6a5d77073e0a7d3d60aedfbf37e124d15a586a880d7d5a8c8d5307a814`
- Git blob `89e2b3122b08db1849e4e56cc94f1f58c473b735`

### 2. 연속 잔차와 logarithmic norm — 계약과 비교 산술 재사용

[dense_output_v2.rs](https://github.com/cosmosapjw-quantum/vigilode/blob/ac1cd2a4738c2441c92e5fdae5f70aba35e53544/crates/rodas5p-integrators/src/dense_output_v2.rs)의 `ContinuousResidualProvider`는 두 메서드를 요구한다.

```rust
fn enclose_rhs(
    &self, time: Interval, state: &[Interval],
    rhs: &mut [Interval], work: &mut DenseSegmentWork
) -> DenseOutputResult<()>;

fn one_sided_log_norm_upper(
    &self, time: Interval, tube: &[Interval],
    work: &mut DenseSegmentWork
) -> DenseOutputResult<f64>;
```

계약은 입력 상자의 **모든** (t,y)에 대한 exact RHS 포함성과 전체 error tube의 **모든** 상태 Jacobian에 대한 Euclidean logarithmic norm 상한을 요구한다. State에 대해 C1인 vector field, identity mass matrix, 동일한 model/source와 provider binding은 caller 전제이다. trait 자체가 전제를 증명하지 않는다.

`Rodas5pQuarticSegment::verify_continuous_residual_tube`는 저장 다항식과 미분의 whole-interval enclosure를 구한 뒤 residual L2 상한과 signed mu를 사용한다. 구간 말단의 초기 오차 전파와 잔차 적분을 바깥쪽 반올림으로 계산하고, 구간 전체 최대 반경이 caller의 tube 안에 들어오는지 확인한다. 양·음·0 mu를 나누며 실패는 `TubeNotVerified` 등의 typed refusal로 남긴다.

한계는 명시적이다.

- private `Rodas5pQuarticSegment`는 8-stage RODAS5P `StepResult`와 그 quartic extension용이다. RUN17 DOP853 degree-7 coefficient 배열을 입력하는 public constructor가 없다.
- represented clock delta의 exact positive normal binary64 조건을 검사한다. 기존 REI의 time normalization 또는 endpoint representation을 조용히 바꿀 수 없다.
- adjacent segment, event, birth/threshold discontinuity, representation jump, controller rollback, full trajectory output authority를 연결하지 않는다.
- 일반 `OdeProblem`은 point callback뿐이므로 `request_continuous_residual_provider`는 의도적으로 unavailable을 반환한다.

그러므로 REI에서는 같은 구간 산술·provider 전제를 새 degree-7 저장 다항식 경로에 적용하고, join마다 이전 반경과 실제 표현 jump를 별도 운반해야 한다. 이 조사는 그 경로의 구현 또는 tube 성공을 주장하지 않는다.

### 3. 작은 gas Jacobian의 상한 — 후속 실용 후보

[nonnormal_certificate.rs](https://github.com/cosmosapjw-quantum/vigilode/blob/ac1cd2a4738c2441c92e5fdae5f70aba35e53544/crates/rodas5p-core/src/nonnormal_certificate.rs)의 `symmetric_part_upper(&[Vec<Interval>])`는 interval matrix의 symmetric part를 만들고, interval Cholesky 증명이 성립하면 그 상한을 쓰며 그렇지 않으면 outward Gershgorin 상한을 반환한다.

REI의 5차원 gas block에 대해서는 전체 tube의 interval Jacobian을 먼저 얻은 뒤 쓸 수 있다. 하지만 현재 sampled/finite-difference Jacobian을 interval matrix처럼 포장하면 전제가 성립하지 않는다. 분율, thermal coordinate, cohort depth를 함께 비교할 때는 고정된 scaling/norm을 먼저 정의해야 한다. 이 helper는 REI density/EOS/rate/geometry의 interval derivative를 제공하지 않는다. 모양과 finite interval의 입력 검사는 adapter에서 수행해야 한다.

`certify_exp_action*`은 **고정 유한 행렬**의 exponential action 증명이지 시간·상태에 따라 변하는 비선형 flow의 보증이 아니다.

### 4. source binding과 증거 구분 — 구현 패턴 재사용

`BoundPr101Problem`과 `BoundCollectiveProblem`은 point/interval provider가 같은 private model에서 생성되도록 묶는다. PR101은 고정 scalar witness의 한 segment 전용이며 초기 참해 반경은 caller premise이다. 반환 중심값과 interval 평가의 차이를 output radius에 더하는 방식은 REI representation defect 관리에 유익하다. PR101의 sin/cos model과 collective cubic/Gray–Scott의 특별한 구조는 HHeD rate 식을 대신하지 않는다.

`residual_gain.rs`의 `FrozenMetric,LinearTargetId,ResidualGainWitness,VerifiedCorrection`는 source/operator/epoch/metric identity를 권한 객체에 결속하는 예시다. 다만 증명 대상은 **고정 선형계 Wu=b의 해와 candidate의 차이**이다.

`outward_certificate.rs`의 `CertificateKind::StageTargetBound`도 선언된 quadratic stage system의 root와 candidate 차이를 감싼다. 소스가 명시하듯 embedded projection은 error proxy이며 ODE local/global error bound가 아니다.

## 테스트 및 연구 주장 확인

읽은 테스트는 실제로 존재하며 다음 위험을 다룬다. 이 조사에서 재실행하지 않았다.

| 테스트 파일 | 읽은 계약 |
|---|---|
| `a05_dense_global_output.rs` | immutable quartic, 실제 clock delta, point-provider refusal, 전체 구간 residual/tube, signed gain, 실패 work |
| `production_audit_pr101_provider.rs` | 같은 segment binding, 초기/전체 tube 반경, 출력 중심 displacement, shape/NaN/overflow, work |
| `production_audit_bound_collective.rs` | 다른 model의 authority 거부, exact dyadic RHS, full tube의 mu, 실패 기록 |
| `a11_gray_scott_log_norm.rs` | 해당 생성 모델의 supplied-box logarithmic norm |
| `safe_enclosure_exp_floor.rs`, `safe_enclosure_probes.rs` | exponential 작은 값 floor, midpoint radius, negative-rate time endpoint |

현재 [production decision](https://github.com/cosmosapjw-quantum/vigilode/blob/ac1cd2a4738c2441c92e5fdae5f70aba35e53544/research/production_audit_20261018/DECISION.json)은 unqualified production/global accuracy/certified packet 승격을 HOLD한다. 후속 `FINDINGS_STATUS.json`도 A05 whole-output authority와 complete packet arithmetic을 OPEN으로 유지한다. 최신 benchmark README는 bounded CSV evidence를 제공하지만 continuous-time certificate를 주장하지 않는다. 이 제한은 재사용 가능한 작은 기능까지 사용 금지한다는 의미가 아니다.

## 패키지·라이선스·변경 없음

Workspace는 Rust edition 2024, rust-version/toolchain 1.94.1, core version 0.1.0이다. 기본 integrators features는 비어 있고 audit2는 opt-in이다. 의존성과 exact Cargo.lock hash는 source manifest에 기록했다.

실제 LICENSE는 MIT, copyright (c) 2026 cosmosapjw-quantum이다. 파일 또는 상당한 소스를 옮길 때 copyright와 permission notice를 함께 보존한다. `directed.rs`와 LICENSE의 byte copies를 `reuse_origin/`에 남겼다. 이는 원저자의 구현이며 새 REI 코드라고 재명명하지 않는다.

조사의 완료 지위:

- **ESTABLISHED:** 위 원격 refs/tree, 선택 소스 바이트·Git blob identity, actual API의 존재.
- **ARCHIVED_EVIDENCE_ONLY:** VigilODE producer tests/benchmarks의 과거 실행 성적.
- **DERIVED:** 같은 산술을 degree-7 REI reconstruction/jump adapter에 연결하는 적용 경로와 필요한 전제.
- **UNRESOLVED:** REI continuous gas/depth RHS residual 상한, feedback Jacobian 전체 tube 상한, true initial radius, segment/event 전파를 합친 전역 인증.

다음 구체적 단위는 저장 RUN17 다항식 endpoint와 derivative를 exact rational로 해석하고, 동일 표현을 VigilODE outward interval로 평가하여 포함성을 확인하며, representation jumps를 보존하는 것이다. 그 결과는 표현 산술의 검증이며 아직 true gas trajectory의 residual tube 증명은 아니다.

