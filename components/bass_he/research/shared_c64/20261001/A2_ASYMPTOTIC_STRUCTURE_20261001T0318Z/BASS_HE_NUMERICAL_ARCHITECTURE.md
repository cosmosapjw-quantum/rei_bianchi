# A2 이후 수치 구조: C1 설계를 위한 고정 analytic 계약

현재 구현 상태는 `C1_NOT_RUN`이다. 이 문서는 solver architecture 선택 결과가 아니라 A2에서 유도한 제약과 검증 기준이다. 기존 A1b의 exact P⊕Q와 동일한 Coulomb H/phase/origin을 유지한다.

| 계층 | 현재 authority | C1/C2가 해야 할 일 |
|---|---|---|
| 전자 snapshot | exact lowest m=0와 bright lowest abs(m)=1; R10R positive meridional phase | sector-preserving eigensolve, residual·gap 및 state continuation |
| 작은 R | L_O=−iℏ(4√2/15)x³+O(ℏx^{7/2}) | cancellation-sensitive scaled ratio 및 공간오차 분리 |
| 큰 R | L_O=−iℏ(32√2/243)x+O(ℏx⁻²) | origin lever와 intrinsic term을 각각 검증 |
| He-centered term | L_B=+iℏ(128√2/729)x⁻²+O(ℏx⁻³) | 큰 두 항의 수치 차만으로 평가하지 않는 직접 lane 준비 |
| torque | (E_g−E_b)L=⟨g,[H,L]b⟩ | direct와 별도 구현, singular integration 및 H¹ 오차 통제 |
| cluster | He n2+H1s의 rank-5, 내부 1/R detuning 및 n2 Stark block | projector/overlap continuation; 2s/2pz를 exact branch로 고정 금지 |
| frame/ETF | 원점·boost·rotation·phase가 완성된 동일 generator | atomic P와 exact molecular basis 간 full unitary/PQ dictionary |
| omitted sector | exact Q dynamics와 memory | numerical residual·channel/continuum convergence는 후속 단계 |

Reference는 고차 FEM/spectral 또는 이에 준하는 독립 표현, efficient 후보는 spheroidal/B-spline/기저 방식 중 원전·conditioning을 근거로 선택한다. 아직 어느 것을 채택했다고 기록하지 않는다. 실제 weak form, axis/cusp boundary, infinite-domain treatment 및 data type이 코드보다 선행한다.

두 analytic limit의 big-O 상수와 global c_±는 미계산이다. R_min 또는 R_max를 이론식만으로 임의 고정하지 않는다. Basis/domain/resolution refinement와 R-sequence refinement를 분리하여 discretization 오차가 leading coupling보다 충분히 작은지 확인하도록 acceptance contract를 만든다. 극한 계수에 fit해서 coupling curve를 생성하지 않는다.

Canonical cache key는 source/code identity, κ_A/κ_B/m/ℏ convention, exact R token, origin/frame/ETF, sector/cluster label, domain map, discretization identity, quadrature, precision 및 tolerance를 포함한다. 임의 rounded R key를 쓰지 않는다. 원본 solver output, reduced physical observable, benchmark source를 분리한다.

현재 실제 새 runtime는 한 번의 symbolic Wolfram batch뿐이다. Physical eigensolver, matrix grid, scattering, benchmark comparison은 NOT_RUN. C1은 architecture·최소 구현/검증 계약을 위한 다음 단일 node이고, C2 magnitude audit는 그 뒤다.
