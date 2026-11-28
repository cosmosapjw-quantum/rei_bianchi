# C1 독립 과학·구현 검토

최종 판정은 **`ELECTRONIC_DISCRETIZATION_NOT_CONVERGED`**다. `architecture_design_frozen=true`는 허용되지만, 독립 reference의 수렴 또는 C2 진입을 뜻하지 않는다. 다음 단일 dependency는 **`C1b_INDEPENDENT_REFERENCE_CONVERGENCE`**이며 broad R-grid, collision, Eq55는 실행하지 않는다.

검토자는 solver·coupling·pilot 작성자와 분리된 `/root/c1_independent_review`다. A2 handoff, 원 사용자 계약, root AGENTS, 두 구현과 유도, operator integration, 사전 numerical contract, 실행 로그/결과, source comparison, 최종 C1 derivation/architecture를 읽었다. 독립 식 검토와 코드 경로 검토, 실행 provenance hash 확인을 수행했다. 물리 eigensolve·기존 A1/A2 CAS를 재실행하지 않았고 같은 코드 replay를 독립 수렴 검증으로 취급하지 않았다. 이 문서는 물리·수치 claim gate의 검토이며 이후 Git/백업 전달 성공을 인증하는 문서가 아니다.

## 1. 식·구현 검토 결과

- Prolate map의 A/B 방향, charge-center midpoint shift, separated charge/energy 부호는 Cartesian point-Coulomb Hamiltonian과 일치한다. Factored weak forms의 radial `−m(m+1)`과 angular `+m(m+1)`은 올바르며, weighted norm으로부터 physical normalization `R³(〈ξ²〉−〈η²〉)/8`과 monotone `F′<0`가 나온다. Fixed-m Coulomb bracket은 root-finding 장치와 엄밀 enclosure를 구분했다.
- Spherical `A_lm`의 Condon–Shortley 보정과 positive bright phase가 일치한다. Multipole/Gaunt 합 `L≤2lmax`는 선택한 angular subspace에서 전체 Coulomb potential의 projection이다. 핵 반지름에서 radial mesh를 나눠도 off-center angular cusp error는 남는다. `sqrt[l(l+1)/2]`의 direct angular coefficient 부호도 맞다.
- Direct lane의 Cartesian Jacobian inverse, `z(Aρ+A/ρ)−ρAz`, momentum/dipole 계수 `1/√2`가 맞다. Torque lane은 미분값을 쓰지 않고 원래 Coulomb-force form을 적분한다. `L_O/(−iℏ)=C_R(T_B−T_A)/Δ`, `L_B/(−iℏ)=−Z_A R T_A/Δ`와 origin lever 부호가 일치한다. 같은 analytic 값을 양변에 재사용하는 구현이 아니다.
- Singular torque의 prolate corner는 방향에 따라 극한이 달라질 수 있다. 두 Duffy triangle의 map/Jacobian `hξhηt`는 올바르며 별도 q16→q24 evidence가 있다. Polynomial Galerkin quadrature의 exactness를 force quadrature에 전용하지 않았다.
- `a_A,E_A`는 physical H scale로 고정되어 ZA=0 fixture에서도 변하지 않는다. 전이 gap `E_b−E_g`와 미측정 same-sector isolation gap이 분리되어 있다. Molecular virial `2T+V+R∂RE=0`, HF의 isolated-branch 조건 및 moving-basis/box 항의 주의도 적절하다.
- Continuation의 physical cross-overlap 및 cluster polar transport는 설계이며 실행 결과가 아니다. Equal-charge/dark 검사는 parity fixture이고 molecular eigensolve 증거가 아니다. 원전 비교는 source claim과 새 유도·설계를 구분했다. P06 인쇄 결함의 시각 확인은 source 담당자의 evidence이며 검토자가 PDF를 다시 렌더링했다는 주장은 하지 않는다.

## 2. 수치 claim gate

사전 `NUMERICAL_CONTRACT.json`의 기준을 적용한다. 아래는 `R=2 a_A`, ZA=1, ZB=2의 완료된 단일점 pilot에서 읽은 값이다.

| 항목 | 관측 absolute 차이 | 사전 기준 | 판정 |
|---|---:|---:|---|
| reference l18 vs prolate refined E_g | 1.2838976132703017e−3 E_A | 1e−5 E_A | FAIL |
| reference l18 vs prolate refined E_b | 5.078256047896801e−7 E_A | 1e−5 E_A | PASS |
| reference l18 vs prolate refined L_O | 8.197204874715869e−5 ℏ | 1e−5 ℏ | FAIL |
| prolate direct vs torque O | 7.435718707426986e−13 ℏ | 1e−7 ℏ | PASS in pilot |
| prolate momentum commutator | 9.89319737243477e−13 | 1e−7 | PASS in pilot |
| prolate origin identity | 4.440892098500626e−16 ℏ | 1e−10 ℏ | PASS in pilot |
| prolate force q16→q24 L_O | 1.0352663171175891e−11 ℏ | 1e−8 ℏ | PASS in pilot |

Prolate refined `L_O/(−iℏ)=0.34097775775750866`는 **pilot estimate**다. Same-state operator consistency가 매우 좋아도 독립 표현의 magnitude convergence를 대체하지 않는다. Spherical l18의 약 5e−13 algebraic residual과 단위 norm은 누락된 angular 공간의 오차를 측정하지 못한다.

Spherical l12→l18은 radial grid/domain을 고정했는데 L이 `1.7606594391172958e−4 ℏ` 변했다. 따라서 unresolved angular truncation은 실제 증거가 있다. 남은 mismatch 전부를 angular cusp 하나에 귀속하는 증명은 아니다. C1b에서는 radial h/p, quadrature, box도 분리해 확인해야 한다. Prolate base→refined는 mesh와 extent를 함께 바꾸므로 독립 tail-error estimate가 아니다. Method spread에 통계적 error bar를 붙이지 않았다.

이 실패를 감추기 위해 기준을 완화하거나 추가 l24 pair를 실행할 필요는 없다. 이미 사전 gate 미충족과 다음 필요한 dependency가 명확하다. 설계 고정과 discretization 미수렴을 동시에 기록하는 현재 STOP이 증거에 맞다.

## 3. 발견한 구현 결함과 수정 검토

초기 `run_pilot.py`의 create-only preflight가 예외를 던져도 outer failure logger가 기존 JSONL에 FAILED를 append할 수 있었다. 또한 final JSON은 atomic/fsync writer를 사용하지 않았다. 이 결함은 완료된 첫 물리 실행의 숫자를 무효화하지 않지만, 재실행 시 기존 evidence를 바꿀 수 있어 수정이 필요했다.

작성자는 실행된 원본을 `evidence/EXECUTED_RUN_PILOT_V1.py`로 보존하고, preflight를 failure logger 바깥으로 옮겼다. 현재 writer는 fsync한 임시 파일을 create-only atomic hard-link로 게시하고 디렉터리를 fsync한다. JSONL도 fsync한다. 임시 경로에서 기존 log 불변, overwrite rejection, JSON readback, temporary cleanup을 검사한 I/O-only regression은 PASS다. 이 수정 후 물리 pilot는 재실행하지 않았다.

검토자가 직접 확인한 원본 driver SHA256은 `e6bd2f5c1689d211b970bd9e246d5b5edd8c3225b9d212096465e477b67b76a9`이며, 실제 START event의 `run_pilot.py` SHA와 동일하다. 실행본과 전달 코드가 다른 이유와 identity가 보존됐다. 이 결함은 **CLOSED_BY_SCOPED_FIX**다.

Degree5 single-center amplitude/derivative failure와 degree7 불완전 output capture도 보존되어 있다. 최종 degree7의 완료 transcript는 별도 기록이며 실패를 소급 PASS로 바꾸지 않았다. 새 coupling 4 tests는 exact atomic fixture·geometric lever·parity·input rejection으로만 해석한다. Spherical 6 tests와 prolate 최종 4 tests의 PASS를 finite-R 전체 accuracy로 일반화하지 않는다.

## 4. 남는 제한과 gate

아직 확보되지 않은 것은 continuum/dual-form residual certificate, rigorous same-sector gap, 각 오차축의 독립 수렴, 실제 R-continuation/cluster transport, asymptotic scaled sequences, numerical HF/virial, continuum/collision accuracy다. A2의 Big-O constants와 유효 반경은 numerical tolerance 근거가 아니다. 새로운 source-native benchmark cell, interpolation, fit, shell sum은 없다.

현재 fail-closed delivery에 남는 blocking code/equation defect는 발견하지 못했다. 그러나 C2 magnitude closure를 막는 **수치 수렴 blocker는 그대로 열린다**. C1b가 먼저 독립 reference와 efficient representation의 사전 기준을 충족하는지 판정해야 한다.

```
CODE_I02_CLOSED=true
full_certificate_fail_closed=true
scientific_PROMOTE=HOLD
Eq55_next_node_authorized=false
Eq55=NOT_RUN
production_default_change=NOT_AUTHORIZED
```

검토 판정: **ACCEPT_FAIL_CLOSED_C1_RESULT**. 전체 프로그램 완료·production promotion·finite-R magnitude certification은 승인하지 않는다.
