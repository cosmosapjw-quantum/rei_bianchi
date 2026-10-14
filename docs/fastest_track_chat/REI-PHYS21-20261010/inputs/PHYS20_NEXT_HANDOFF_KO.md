# PHYS20 → PHYS21_SECOND_ORDER_SCALAR_SHEAR_RESPONSE

rei_bianchi의 다음 **물리 연구 루프**를 수행하라. 이번 패키지의 PHYS20 결과를 상속하고, 같은 FLRW first-macro source/time proof를 다시 줄이는 반복으로 돌아가지 않는다.

## 기준과 읽을 순서

1. `PHYS20_REPORT_KO.md`, `PHYSICS_CONTRACT.json`, `RESULTS_SUMMARY.json`, `RESEARCH_DAG.json`을 읽는다.
2. `independent/DECISION_REVIEW.json`과 그 판정 대상 SHA를 확인한다. 실제 independent review와 owner summary를 혼동하지 않는다.
3. `SOURCE_MANIFEST.json`은 `cosmosapjw-quantum/rei_bianchi`, `forward/rust-reion-kernels-20260922`, 입력 commit `718468dc75cb81fdfe0f2792aab5c8d0dbc54607`에 결속한다. 당시 scientific Rust subtree는 `cb69b4736dd046e4675557577eb8e0ead037d1f3`다.
4. 최신 branch가 움직였다면 source subtree와 실제 관련 파일의 차이만 조사한다. 문서가 추가되었다는 이유로 이미 완료한 물리 검산을 재실행하지 않는다. Publication commit과 archive identity는 별도 receipt에서 확인한다.

Canonical model-matched research harness를 적용한다. 현재 패키지는 GPT-6 Astra research v4.0.0, ZIP SHA256 `dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7`을 실제 읽고 수행했다. 하네스 템플릿은 과거 실행 증거가 아니다.

## 현재 닫힌 것

- Exact `E=E_b g(t)/g(b)`, physical-angle Jacobian `J=det(A)⁻¹/g³`, birth source `J_b`와 current density `1/J_t`의 구분.
- `δlnE=−q_iq_jΔB_ij`, causal survival memory를 포함한 absorption/primary heating의 first-order kernel.
- 현재 입체각당 kernel에는 추가 `−3ΔB`가 있다. Per-emitted-photon absorption과 present-angle absorption의 부호가 다를 수 있다.
- 동일한 H/scalar density와 ε-independent isotropic initial/source, 적절한 differentiability/uniqueness 아래 연속 구면의 coupled scalar first derivative=0. `C¹ ⇒ derivative zero`; bounded `C² ⇒ O(ε²)`를 구분한다.
- Actual midpoint grid: `Q=diag(1/3+1/(6N²),1/3+1/(6N²),1/3−1/(3N²))`. 현재 xy shear는 특별한 permutation 대칭으로 linear null이다. 같은 eigenvalue shear의 회전 `diag(1,0,−1)`에는 spurious linear term `−σΔ/(2N²)`가 생긴다.
- Selected xy free-energy leading coefficient `8/15`, native `C_N=8/15+1/(3N²)−7/(60N⁴)`; N=8의 coefficient bias `+0.971221923828125%`.
- Uniform-q source의 continuum artifact `(4/5)σ²bΔ`. 올바른 normalized-J finite grid에도 잔여 coefficient `2/(3N²)−7/(6N⁴)`가 남는다.
- Threshold δ-line의 `(E−E_th)_+` 반응은 `2E_th|u|/(3π)` cusp를 허용한다. Parity alone은 quadratic onset의 증명이 아니다.

## 다음 실제 물리 목표

**PHYS21: smooth-regime coupled scalar의 선두 quadratic shear response를 방향 quadrupole와 causal gas feedback으로 분리하라.**

현재는 first variation의 정확한 상쇄와 free-photon quadratic benchmark만 닫혀 있다. FT03의 실제 evolving gas에서 온도·ion fraction·Γ·scalar τ의 2차 계수와 부호는 아직 계산하지 않았다.

우선 physical-birth-angle 변수에서 second variation을 정리한다. 고정 gas의 `K=P L`에 대해 출발점은

`δ²K = P₀[δ²L − 2 δL δΘ + L₀((δΘ)² − δ²Θ)]`

이다. 이는 다음 단계의 계산 출발식이며 이번 패키지가 full coupled second derivative를 실행했다는 뜻은 아니다. Metric energy의 second variation, survival variance, source measure covariance를 모두 보존한다. 필요한 angular contractions는 isotropic second 및 fourth moments로 계산하고, correct source의 b-independent free-energy benchmark로 먼저 대조한다.

그다음 `gas first variation=0`을 이용하여 second-order scalar forcing과 linear causal gas response를 분리한다. 기존 continuous-gas evidence를 source-bound하게 소비할 수 있으면 사용한다. 고정 neutral fraction probe를 실제 evolving gas 계수로 승격하지 않는다. 새 closure 또는 새로운 physical source normalization을 묵시적으로 도입하지 않는다.

Angular quadrature를 바꿔야 한다면 연구용 비교로 격리하고 `Q2/Q4` 조건을 먼저 고정한다. 기존 native source/default를 자동 변경하지 않는다. Gauss–Legendre 또는 isotropic moment-matched rule은 선택 후보이며 이미 채택된 production prescription이 아니다.

## 실행 범위와 stop condition

정확 기호 유도와 작은 directional/moment kernels까지 진행한다. 같은 firstmacro 8/16/32 campaign, 전체 raw, native/gas IVP, NCP, HH–RCT–CR 공동 ON, 다른 원자물리 lane의 precision 작업은 이 handoff의 기본 실행 범위에 없다. 구체적인 second-order functional·검산·제한 또는 실제 source-data blocker를 산출하면 이 bounded loop를 닫는다.

`physical=HOLD`, `[160,161] FAIL`, `tick160`, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED를 보존한다. PHYS19 FLRW 숫자를 Bianchi error certificate로 옮기지 않는다. Same-branch additive/nonforce publication의 기존 범위를 유지하고, source/default/runtime_returns를 변경하지 않는다. 새 checkpoint-owner integration은 별도 lane이며 PHYS21의 이론 선행조건이 아니다.

산출물은 정의–유도–computational form–actual verification–claim ceiling을 연결하는 보고서, machine-readable 결과/DAG, 정확 source identity, 다음 handoff다. 실제 독립 reviewer는 후보/검증 설계에 참여하지 않은 실행자로 한정하고, 같은 실패를 변한 근거 없이 재시도하지 않는다.
