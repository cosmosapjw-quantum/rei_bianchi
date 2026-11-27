# A1b 이후 수치 구조와 실행 경계

A1의 정식화는 exact P⊕Q 전자 문제 범위에서 완료됐다. 다음은 A2 이론 분석이며 C1 전자 solver 설계·실행은 아직 대기다. 이 문서는 수치 solver의 성능이나 수렴을 인증하지 않는다.

기준 모형은 prescribed C² nuclear paths와 단일전자 clamped Coulomb Hamiltonian이다. 유한 P는 H1s와 He1s/2s/2p 세 방향에 명시적 ETF·원자 에너지·remote monopole 위상을 붙여 만든다. S,h,D는 같은 χ에서 계산한다. Reference form은 본문 B.12, 계산형 후보는 atomic eigen-equation으로 상쇄를 선행한 B.13이다. 후자는 spatial quadrature 구현 전에 reference와 독립적으로 비교해야 한다.

전체 상태는 Ψ=Ya+Zζ이며 Γ로 정의한 Z가 P의 exact complement를 운반한다. K_PP는 기존 Galerkin generator, K_QP=Z†(HY−iℏYdot), K_PQ는 그 adjoint, K_QQ는 complement의 Coulomb quadratic form이다. 모든 block을 유지하면 full TDSE와 동등하다. Q를 제거하면 B.32의 initial-Q source와 memory kernel이 생긴다. Six-channel code가 이를 생략할 경우 정확한 근사 선언이 필요하며 full formulation closure를 수치 정확도 근거로 사용하지 않는다.

현재 구현은 supplied overlap s에 대한 Gram, orthonormalizer, projector quadratic forms만 제공한다. 실제 orbital overlap s(t), sdot, 공간 적분, BO eigenstates, Q propagator 또는 물리 collision evolution은 공급하지 않는다. `code/README_KO.md`의 8개 tests와 `code/check_pq_completion.py`의 별도 fixture는 순수 유한차원 검증이다. 환경은 Python3.12.14/NumPy2.3.5, assertion atol2e-12, rtol0이다. Delta rejection1e-12는 helper의 fail-closed guard이며 전체 R 공간의 conditioning certificate가 아니다. 같은 환경·의존성의 이미 PASS한 검사를 반복하지 않는다.

후속 수치 계약은 다음을 분리해야 한다: physical S conditioning, full h−iℏD 대비 residual matrix의 cancellation, cusp·두 중심 quadrature, exact molecular state/subspace projection, finite-time 초기 overlap, interaction tail, long-range phase, time/impact integration, Q return 및 continuum. 서로 다른 오차를 하나의 Gaussian uncertainty로 바꾸지 않는다.

정확한 원자 비교 dipole와 coalescent Gram은 CAS로 확인했지만 실제 finite-R molecular coupling sample은 없다. R10R g,b의 좌표는 full J_b†g,b로 정의되고 전체 L block identity가 성립한다. P-only overlap이나 독립적인 atomic rate로 대체하지 않는다. CPC omega adapter는 현 구현에 들어가지 않으며 이를 import할 때 별도 convention check가 필요하다.

모든 후속 cache key에는 source commit, orbitals/phase/referenceepoch, frame/origin, trajectory, constants, channel/subspace label, exact R token, grid와 tolerance를 포함한다. 이번 helper는 physical cache를 만들지 않는다. C1의 prolate-spheroidal/FEM/B-spline/DVR/atomic-orbital 방법 비교는 A2 결과를 받아 정의한다.
