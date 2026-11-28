# C1 원전 근거와 전자구조 표현 선택

범위: 고정 핵간거리 R>0의 단일전자 point-Coulomb Hamiltonian, lowest m=0 및 lowest bright cosφ |m|=1. 이 문서는 원전에서 확인한 사실과 이번 C1의 수학적 판단을 구분한다. 실제 eigensolve, collision 계산, benchmark 재추출, C2 magnitude 검증은 하지 않았다.

## 1. 직접 확인한 원전

| ID | 버전·고정 식별자 | 읽은 부분과 허용되는 근거 |
|---|---|---|
| P06 | Gusev–Solov’ev–Vinitsky, CPC 286 (2023) 108662, DOI [10.1016/j.cpc.2023.108662](https://doi.org/10.1016/j.cpc.2023.108662); 사용자 제공 publisher PDF | PDF pp.1–3: two-center separation와 E, λ의 coupled recurrence root 방식. p.3의 인쇄식에 아래 결함이 있어 재유도 없이 전사 금지. ARSENY author code는 독립 reference가 아니다. |
| P01 | Liu et al., CPB 33 (2024) 083401, DOI [10.1088/1674-1056/ad5322](https://doi.org/10.1088/1674-1056/ad5322) | PDF pp.3–4 = journal pp.083401-2–3: two-center GTO AOCC와 pseudostate representation. 본 C1의 exact fixed-sector molecular eigenstate 수렴을 이 논문의 collision 비교로 대신하지 않는다. |
| P03 | Liu et al., PRA 67 (2003) 052705, DOI [10.1103/PhysRevA.67.052705](https://doi.org/10.1103/PhysRevA.67.052705) | PDF pp.1–5: hyperspherical channel에 B-spline, SVD와 R-matrix. 이 B-spline은 본 설계의 fixed-R prolate separated B-spline과 다른 문제/좌표다. 직접 구현 재사용 근거가 아니다. |
| P08 | Winter, PRA 76 (2007) 062702, DOI [10.1103/PhysRevA.76.062702](https://doi.org/10.1103/PhysRevA.76.062702) | PDF p.2: 두 중심 atomic Hamiltonian을 Sturmian basis로 대각화하는 방식. p.3–5의 collision convergence를 본 coupling의 인증으로 수입하지 않는다. |
| C1-S01 | Susi Lehtola, *Fully numerical Hartree–Fock and density functional calculations. II. Diatomic molecules*, [arXiv:1810.11653v4](https://arxiv.org/abs/1810.11653v4), published DOI [10.1002/qua.25944](https://doi.org/10.1002/qua.25944) | PDF pp.3–6, §§2.1–2.3: ξ=coshμ, η=cosν인 transformed prolate 좌표, radial finite elements × angular harmonics, 체적요소와 overlap. 이는 charge-center spherical expansion이 아니다. PDF 첫면 날짜 August 28, 2021과 margin v4 8 Mar 2019를 모두 보존한다. |
| C1-S02 | Tao–McCurdy–Rescigno, [institutional author manuscript](https://escholarship.org/content/qt4pg686xw/qt4pg686xw_noSplash_092438b4b7b44e626496b40d9a43c5af.pdf), dated 2008-11-25; published PRA 79 (2009) 012719 | PDF pp.1–5, §§II–IV: prolate FEM-DVR와 angular analytic expansion; odd-m endpoint factor와 quadrature-dependent diagonal metric. 원고와 publisher판 byte/식 동등성은 주장하지 않는다. |
| C1-S03 | H. Olivares-Pilón, [arXiv:1112.3463v2](https://arxiv.org/abs/1112.3463v2), *He₂³⁺ and HeH²⁺ molecular ions in a strong magnetic field: the Lagrange mesh approach* | PDF pp.3–4, §§2–3: shifted ξ, Laguerre/Legendre Gauss mesh, scale h, discrete potential. 자기장과 m=0 결과이므로 field-free bright m=1 benchmark로 쓰지 않는다. 방법 구조만 비교한다. |

새 논문 PDF는 이 agent가 URL에서 메모리로 읽고 SHA/크기를 산출했다. 별도 private 보존 여부는 최종 package manifest가 소유한다. 라이브러리·HelFEM·ARSENY를 설치/실행하거나 그 코드를 이번 구현으로 수입하지 않았다. 문헌상의 프로그램 이름은 현재 배포본의 version pin을 의미하지 않는다.

## 2. 실제 원전 결함: P06 p.3

**SOURCE_DEFECT_CONFIRMED_VISUALLY.** P06 p.3를 직접 렌더링하여 다음 인쇄를 확인했다: η=(r₁+r₂)/R, a=(Z₂+Z₁)/R, b=(Z₂−Z₁)/R. 첫 식은 ξ와 동일하면서 −1≤η≤1이라는 같은 페이지 정의와 모순이다. 또한 원자단위에서 Coulomb potential에 Laplacian denominator를 곱한 separated coefficient는 R Z에 비례해야 하므로 뒤의 1/R은 그 Hamiltonian과 맞지 않는다. 단순 text extraction 오류가 아니다.

**DERIVED 교정 원칙.** r_A와 r_B의 부호 컨벤션을 먼저 고정하고 ξ=(r_A+r_B)/R, η=(r_A−r_B)/R를 직접 정의한다. 이후 Cartesian point-Coulomb operator와 Jacobian으로 coefficient 및 separation-constant 부호를 독립 유도한다. 이 선택에서 r_A=R(ξ+η)/2, r_B=R(ξ−η)/2이며, Coulomb numerator는 −2[(κ_A+κ_B)ξ+(κ_B−κ_A)η]/[R(ξ²−η²)]다. 에너지단위 m_e κ_A²/ℏ², 길이단위 a_A=ℏ²/(m_eκ_A)를 명시한 뒤에만 무차원식으로 옮긴다. 특정 원전 λ 기호의 부호와 shift를 묵시적으로 공유하지 않는다.

C1-S02의 Cartesian map/체적요소, C1-S01의 transformed map는 이 재유도를 cross-check할 독립 문헌 근거다. 여기서 발견한 defect가 ARSENY 실행 코드에도 존재한다고 주장하지 않는다. 해당 코드 inspection/재실행은 이번 source task에서 하지 않았다.

## 3. 방법 비교와 채택 판단

다음 표의 실행 선택·오차 평가는 **C1의 유도/설계 판단**이다. 문헌에 보고된 다른 시스템의 자리수를 BASS_HE에 전용하지 않는다.

| 표현 | 장점 | conditioning·cusp·축·무한영역의 실제 위험 | 이번 결정 |
|---|---|---|---|
| Exact prolate separation + 두 1D conforming B-spline Galerkin 문제 | 두 핵이 foci이고 point potential의 geometry를 보존한다. 두 1D separation branches를 E와 함께 풀어 2D tensor eigensolve 부담을 줄인다. | m=1은 (ξ²−1)^(1/2)(1−η²)^(1/2) 정칙인자가 필요하다. ξ→1, η→±1 끝점 trace와 weak natural condition을 혼동하지 않는다. 겹침행렬은 일반 SPD이지 자동 I가 아니며 E-root residual와 공간 residual이 별개다. ξmax의 물리적 길이는 R에 따라 변한다. | **efficient lane 채택 적합**. 새 separated operator를 root 문서에서 유도하고 knot/order/quadrature/tail/precision를 독립 refinement 축으로 고정해야 한다. |
| Charge-center spherical harmonics + radial hp-FEM | angular kinetic와 L_y가 정확한 angular algebra로 계산되며 prolate separation과 서로 다른 geometry·discretization을 갖는다. multipole/Gaunt potential assembly가 별도 오류 탐지에 유리하다. | 두 핵은 원점 밖에 있으므로 cusp가 angular nonanalyticity를 만든다. radial hp만 증가하면 해결되지 않는다. 핵 반지름에 radial element 경계가 필요하고 ℓmax를 따로 증가시켜야 한다. 큰 R에서는 국소 atomic 폭을 분해할 angular 수요가 커진다. | **independent reference 설계로 조건부 채택**. 고정 ℓ 또는 동일 코드의 tolerance 변화만으로 고정밀 reference를 선언하지 않는다. resource cap 미달이면 NOT_CONVERGED. |
| Prolate hp-FEM / spectral element / radial FE × angular harmonics | C1-S01의 일반 variational 구조. point potential의 singular denominator가 Jacobian과 결합하여 완화된다. | spherical harmonics가 들어가도 spherical coordinates를 뜻하지 않는다. endpoint/overlap/outer boundary와 polynomial degree 수렴을 확인해야 한다. | 합리적 대체안. 선택된 efficient separation과 같은 좌표지만 2D weak formulation을 독립 구현한다면 단순 tolerance 변경 이상의 독립성이 있다. 현재 추가 구현하지 않는다. |
| FEM-DVR / Lagrange mesh | sparse 또는 quadrature diagonal local potential과 간단한 mesh refinement; C1-S02, S03에 구체적 구현식이 있다. | diagonal S/V는 quadrature identity이며 exact continuum inner product와 구별해야 한다. odd-m 보정 없는 polynomial DVR는 느리게 수렴할 수 있다. Laguerre scale h 변화와 N 증가가 별개다. 에너지의 엄밀 upper-bound 성질은 quadrature approximate 식에 자동 승계되지 않는다. | 예비 대안. 이번 독립 reference와 efficient lane을 이것으로 중복 정의하지 않는다. |
| Two-center STO / Coulomb-Sturmian | 핵 중심의 exponential 함수가 국소 cusp·tail을 표현하기 쉽고 A1b atomic asymptote와 연결하기 좋다. | cusp exponent를 맞춘 개별 s 함수가 있다고 전체 eigenfunction cusp가 자동 충족되지는 않는다. 두 중심 overlap의 선형종속, exponent/basis 균형, continuum representation이 별도 문제다. | 채널 검사 또는 보조 basis 후보. R10R exact molecular coupling의 독립 수렴 증거를 대체하지 않는다. |
| Two-center GTO | 적분 효율과 기존 P01 AOCC의 구현 선례. | 유한 GTO 합은 Coulomb s cusp의 비영 radial derivative를 정확히 재현하지 못한다. 중심 가까운 영역·singular torque는 energy보다 민감할 수 있다. 작은 R에서 basis dependence/overlap conditioning도 주의한다. | 이번 reference로 비채택. 기존 collision benchmark와의 일치로 basis를 조정하지 않는다. |

## 4. Spherical reference의 약점은 명시적 gate다

**DERIVED.** 핵 C가 O에서 d_C>0 떨어져 있으면 r=d_C 구면 위의 국소 핵 거리에는 2d_C sin(θ/2)가 들어간다. s형 Coulomb cusp exp(−αr_C)는 해당 angular 끝점에서 cosθ의 analytic 함수가 아니다. 따라서 charge-center spherical expansion에 exponential angular convergence를 가정할 수 없다. radial element를 핵 반지름에서 나누어도 각 방향 cusp의 ℓ-error는 남는다. large-R 원자 상태의 angular width는 규모상 a_C/d_C라서 필요한 ℓmax가 커질 수 있다. 이것은 구체적 ℓmax 하한이나 finite-R error bound를 증명한 것은 아니다.

따라서 reference contract는 최소한 (radial h, radial p, ℓmax, outer radius, quadrature, arithmetic precision)의 독립 변경을 기록하고, energy뿐 아니라 direct L_y, torque, normalized overlap/projector를 비교해야 한다. 고정 discretization에서 residual이 작아도 continuum error가 작다는 결론은 나오지 않는다. 작은 x의 L=O(x³)에서는 scaled absolute error를 제어해야 하므로 energy-only stopping criterion은 부적합하다.

## 5. Coupling·state label에 필요한 계약

이 항목은 **새 설계 요구사항**이며 문헌의 수치결과가 아니다.

- Direct lane은 differential L_y 또는 정확한 angular algebra에서, torque lane은 원래 두 핵의 singular spatial integrals에서 계산한다. 같은 저장된 L 값을 양변으로 변환하는 검산을 금지한다. 운동량 commutator는 제3 consistency relation으로 쓴다.
- 함수의 L² 수렴만으로 unbounded L_y나 singular torque convergence가 보장되지 않는다. weighted derivative/form 제어와 독립 near-nucleus quadrature가 필요하다. Cusp 인자를 도입해도 이 gate가 제거되지 않는다.
- fixed-m 단순 최저 eigenstate와 full n=2/H1s rank-5 asymptotic cluster를 구별한다. R 사이 overlap, positive phase, near-degenerate cluster projector transport를 저장한다. 계산된 eigenvalue order만으로 물리 label을 정하지 않는다.
- 대칭 문제의 dark sinφ coupling 0은 별도 angular parity 검산이다. equal-charge symmetry와 origin shift는 좌표와 연산자를 함께 바꿔 확인한다.
- Bound-state outer truncation을 continuum outgoing condition으로 착각하지 않는다. C1의 두 fixed-sector bound states에는 ECS가 필수가 아니다. 문헌의 ECS/continuum 성과를 이번 상태의 tail 인증으로 전용하지 않는다.
- conforming Ritz와 exact form 적분의 min-max 구조, approximate quadrature의 영향을 분리한다. 유한행렬 residual·정규직교만으로 continuum spectral pollution 부재 또는 Rayleigh gap 인증을 선언하지 않는다.

판정: **선택할 representation의 설계 근거는 충분하다. 구현 또는 전 구간 coupling 정확도는 미인증이다.** C1 architecture freeze와 C2 magnitude closure를 분리하며 모든 기존 HOLD/NOT_RUN gate를 보존한다.
