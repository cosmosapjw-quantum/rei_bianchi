# C1b 이후 전자구조 수치 아키텍처

`C1B_R2_REFERENCE_CONVERGENCE_CLOSED`. 상세 수식·구현·domain 분석은 `C1B_REFERENCE_CONVERGENCE_KO.md`와 `derivations/CUSP_CENTERING_ANALYSIS_KO.md`를 기준으로 한다.

| 경로 | 표현과 관측량 | 이번 증거 |
|---|---|---|
| Efficient | Prolate separation, factored weighted B-spline; direct Cartesian derivatives와 point-force/Duffy torque | C1 refined 결과 재사용, 내부 knots 보존 tail30→40 |
| Reference | B-centered spherical hp-FEM; direct L_B와 radial-derivative p로 L_O 변환; exact finite force moments | l96 선택, l72→96 및 h/p/q/box 분리 검사 |

물리 Hamiltonian·charge-center 관측량·단위·positive meridional phase는 동일하다. 두 경로는 좌표·basis·assembly·고유문제 구조가 다르다. B 중심은 A의 off-center cusp를 제거하지 않으며, B direct/torque는 finite-space commutator로도 닫힐 수 있어 state 수렴 증거로 단독 사용하지 않는다.

`partialwave_centered.py`는 첫 두 same-sector Ritz roots와 direct L/p/d, `force_projected.py`는 unit-charge force moments와 boundary stress, `state_increment_audit.py`는 안정적인 직접 squared-difference L² 증분을 제공한다. Raw NPZ와 size/SHA·origin/grid identity를 결속하고 atomic create-only 출력을 유지한다. Exact continuum gap/residual certificate는 없다.

기록된 max RSS는 spherical drivers만의 관측이다. Prolate-tail 실행 v1의 계측 누락과 전달용 수정은 `provenance/POST_EXECUTION_PRECISION_NOTES.json`에 있다. 전체 peak 또는 모든 실행의 cap 적용을 주장하지 않는다.

다음 C2는 exact R-grid, tolerances, continuation/phase 및 resource 계약을 먼저 고정한다. R2의 l96을 전 구간 정확도로 전용하지 않는다. A2 scaled limits, rank-5 cluster transport, collision 계산은 이번에 미실행이다. `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`, production 변경 금지를 유지한다.
