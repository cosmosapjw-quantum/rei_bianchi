# Blind-referee 자기 적대적 감사: 원본 광자 source Hessian

1. **선형대수 증명 범위:** `p_s=a_s e^{δ_s}/(e+Σa_t e^{δ_t})`의 1·2계 미분과 전역 source momente의 quadratic remainder는 직접 유도됨. 이는 `original _explicit_photo_fields`의 고정 외부 forcing photon partition에서만 적용된다. 다른 26개 원자 이벤트, 각 evaluation-site의 구간 연산, implicit thermodynamic roots와 선형 Krawczyk certificate를 자동으로 검증하지 않는다.
2. **부모 상관관계:** 모든 original node 상자 주변의 `S_HI,S_HeI,S_HeII` 구간은 실제 가능한 correlated source set의 **외접 상자**다. 8개 corner는 그 상자의 모서리이지 물리적으로 동시에 실현되는 original source histories가 아니다. 둘의 구별을 어기면 불법적 과잉 claim.
3. **고정 numerator counterfactual:** 노드별 광이온화 flux의 비국소 Hessian은 로컬 `N_is`를 고정한 전역 denominator 변화만 다룬다. 동일한 원자 상태의 local numerator 변화는 누락되므로 전체 `J_F`나 `J_D`로 표기해서는 안 된다.
4. **물리 차원:** source photon current 및 local event rate의 기본 차원은 `s^-1`, source heating은 `erg/s`; 로그 모멘트 변수는 dimensionless 비율 `ln(S/S_ref)`. 수정된 Thomson optical depth 또는 reionization history를 계산한 결과가 아니다.
5. **엄밀 계산의 층위:** 정확한 수식은 reals에서 정의되고, source float64 endpoint의 Decimal exact sum은 input binary identity를 보존한다. 그러나 `log`, `exp`, `np.dot`, endpoint의 floating point outward 2ULP는 모든 플랫폼의 **전체 수치 연산에 대한 machine-certified interval enclosure**는 아니다. 따라서 source submap analytic bound의 구현은 `NUMERICALLY_CHECKED`, 엄밀하게 신뢰 가능한 full-X F05 물리 증명은 `UNRESOLVED`.
6. **실제 입력 신원:** 실행 전에 source-owner 11.64MB original tar SHA, 46,080 original accepted source state, 4 original photon groups, group current/absorber/cross-section, 시간·clock, and full source physical original inclusion 확인. 소스가 누락되면 계산은 실패, 대체 synthetic output을 원본으로 사용하지 않는다.
7. **수치 안정:** p=0, group owner absent, zero moment width에서 정확히 0 Hessian/remainder를 보존한다. source Γ의 범위와 합성 정상화를 검산하며 ratio p_s의 행이 새로운 photon number를 만들지 않는지 확인한다. `KMS`나 detailed balance는 가정하지 않는다.
8. **남은 핵심 과학:** cross-site source Jacobian + local nonlinear rate/heat Jacobian + 4-site implicit MPRK22/SDIRK2 derivative/remainder `J_D(X,Θ)` + source forcing θ의 공통 realization + event reachability. 이 범위가 새 전체 오차 조건 `<2e-4`를 충족한 후에만 기존 `[160,161]`를 평가하고 진행한다.

**Verdict:** 이 단위의 실제 물리 데이터와 source Hessian은 물리적으로 유효한 하위 커널을 확장한다. `CENTRAL 28/88 (+0)`, `FIRST_CANONICAL_INTERVAL BLOCKED`, `PRODUCTION HOLD`. 별도 작성자 감사 미수행.
