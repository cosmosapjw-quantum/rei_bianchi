# C1 독립 reference: charge-center spherical partial-wave hp-FEM

상태: `DERIVED` + 아래에 한정한 `IMPLEMENTATION_VERIFIED`.
이 파일과 `code/partialwave.py`, `code/test_partialwave.py`는 독립 reference 작성자가 담당했다.
효율 구현인 prolate 표현의 코드·기저·적분을 재사용하지 않았다. 아직 arbitrary finite-R accuracy,
angular cusp convergence, C2 전체 coupling audit를 인증하지 않는다.

## 1. 단위와 함수 공간

계산 단위는 A2의 고정된 H 원자 단위 `a_A,E_A`다. 물리 결과로 복원할 때
길이는 `a_A`, energy는 `E_A=ℏ²/(m_e a_A²)`, angular momentum은 `ℏ`를 곱한다.
핵간 반발 에너지는 공통 scalar이므로 포함하지 않는다.

\[
z_A=-\frac{Z_B R}{Z_A+Z_B},\quad z_B=\frac{Z_A R}{Z_A+Z_B},\qquad
H=-\tfrac12\nabla^2-\sum_C\frac{Z_C}{|\mathbf r-z_C\mathbf e_z|}.
\]

실수 bright convention은

\[
\psi_0=\frac{G_0(r,\eta)}{\sqrt{2\pi}},\qquad
\psi_1=\frac{G_1(r,\eta)\cos\varphi}{\sqrt\pi},\qquad
G_m=\sum_{l=m}^{l_{\max}}\frac{u_l(r)}r A_{lm}(\eta),
\]

\[
A_{lm}(\eta)=(-1)^m\sqrt{\frac{2l+1}{2}\frac{(l-m)!}{(l+m)!}}P_l^m(\eta),
\quad \int_{-1}^1A_{lm}A_{l'm}\,d\eta=\delta_{ll'}.
\]

SciPy `lpmv`는 Condon–Shortley phase를 포함하므로 위 `(-1)^m`이 이를 제거한다.
따라서 `A_11>0`은 meridional bright positive phase와 일치한다.
전체 norm은 `Σ_l ∫|u_l|² dr`다. 구현의 `evaluate` 반환 G에는 azimuthal normalization이
포함되지 않으므로 원통형·prolate integration과 결합할 때 반드시 이 convention을 반영한다.

유한 원점 구간과 Dirichlet 구 외부 경계에서 `u_l(0)=u_l(rmax)=0`을 강하게 부과한다.
이 공간은 centrifugal quadratic form에 conforming하지만, 각 finite-element function마다
정확한 Frobenius law `u_l~r^(l+1)`을 강하게 강제한 것은 아니다. 해당 regularity는
정확한 eigenstate에서 성립하며, approximate state의 origin behavior는 refinement 대상이다.
점 원천 자체에는 softening을 넣지 않는다.

## 2. 정확한 각운동량 투영 후 radial weak form

두 테스트 함수에 대해

\[
K_l(u,v)=\frac12\int_0^{r_{\max}}u'v'\,dr+
\frac{l(l+1)}2\int_0^{r_{\max}}\frac{uv}{r^2}\,dr.
\]

핵 위치의 radial multipoles는

\[
V_L(r)=-\sum_C Z_C\operatorname{sgn}(z_C)^L
\frac{\min(r,|z_C|)^L}{\max(r,|z_C|)^{L+1}},
\]

이고 `z_C=0`은 별도로 `V_0=-Z_C/r`, `V_{L>0}=0`이다.
각 블록은

\[
V_{ll'}(r)=\sum_{L=0}^{2l_{\max}}V_L(r)
\int_{-1}^1 A_{lm}(\eta)P_L(\eta)A_{l'm}(\eta)\,d\eta.
\]

`L>l+l'`, `L<|l-l'|`, `L+l+l'` 홀수인 항은 정확히 0이다. 즉, 이 finite sum은
주어진 angular trial space 안에서는 **전체 point-Coulomb potential의 정확한 투영**이며
별도의 multipole-tail approximation을 추가한 것이 아니다. `r=|z_C|`의 표현은
angular integral로 해석하고, radial mesh를 그 지점에서 나눠 사용한다.

`m=0,1`에서 `A_lm A_l'm P_L`은 degree가 최대 `4 lmax`인 다항식이다.
`2 lmax+3`점 Gauss–Legendre가 이를 exact arithmetic에서 정확하게 적분한다.
triangle/parity zero는 floating-point noise를 제거하기 위해 명시적으로 마스킹한다.

## 3. hp radial discretization과 solve

기본 mesh는 `r_j=rmax expm1(4j/N)/expm1(4)`에 두 핵 반지름을 합친 것이다.
각 element는 Legendre–Gauss–Lobatto nodal degree-p Lagrange polynomial을 사용하고,
공유 endpoint를 조립한다. 적분에는 nodal Lobatto lumping/DVR를 쓰지 않고 별도
overintegrated Gauss–Legendre rule을 쓴다. 기본 p=4, radial quadrature=14다.
Mass, derivative, centrifugal, exact projected potential을 sparse matrix로 조립한다.

`H c=E M c`는 generalized symmetric `eigsh`로 푼다. Coulomb quadratic-form lower bound
`E≥-(ZA+ZB)²/2`보다 낮은 shift `σ=-(ZA+ZB)²/2-1`을 사용해 해당 sector의 lowest
Ritz eigenstate를 표적한다. 이 bound는 각 shifted-center Coulomb energy form의
kinetic fraction `Z_C/(ZA+ZB)` 분할로 얻을 수 있다. 양의 Coulomb charge만 허용한다.

동일 R의 fixed-sector lowest state만 반환한다. 서로 다른 R 사이의 state label은 이 함수가
정하지 않으며 energy sorting 기반 continuation을 제공하지 않는다. phase는 내부 9개
meridional probe의 signed sum을 양으로 맞춘다. 이는 phase convention일 뿐 전체 영역의
양성 검증도, near-degenerate cluster transport도 아니다.

정규화 `cᵀMc=1`과

\[
\epsilon_{\rm alg}=\frac{\|Hc-EMc\|_2}{\|Hc\|_2+|E|\|Mc\|_2}
\]

를 반환한다. `ε_alg`는 finite-matrix residual이다. 이것을 continuum PDE residual,
eigenvalue enclosure, missing-angular-space error, coupling bound로 사용하면 안 된다.
Floating-point quadrature 때문에 엄밀한 variational upper-bound certificate도 제공하지 않는다.

## 4. direct angular momentum lane

고정된 O에 대해 `L_y=-iℏ(z∂_x-x∂_z)`를 적용하면 동일 l에서

\[
\langle l,0|L_y|l,\pi_x\rangle=-i\hbar\sqrt{l(l+1)/2}.
\]

그러므로

\[
\frac{\langle g,L_y b\rangle}{-i\hbar}
=\sum_{l\ge1}\sqrt{l(l+1)/2}\int_0^{r_{\max}}u_{g,l}(r)u_{b,l}(r)\,dr.
\]

서로 다른 radial meshes이면 element boundary들의 합집합에서 polynomial product를
적분한다. 기본 quadrature는 그 product를 정확히 적분하기 충분하다.
함수 `direct_angular_coupling`은 energy gap, torque integral, force, R10R formula를
사용하지 않는다. 따라서 torque lane과 구현상의 독립성을 보존한다.
이 함수의 출력은 **L/(-iℏ)**이고 `i L/ℏ`와 동일한 실수다.

## 5. 실제 수행한 새 focused checks

명령:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python code/test_partialwave.py
```

환경: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0.
6개 test method 실행, 6 PASS, 0 failure/error, exit 0. 실제 log와 numerical JSON은
`evidence/REFERENCE_FOCUSED_TESTS_LOG.txt`, `evidence/REFERENCE_FOCUSED_TESTS.json`이다.

- UA Z=3 energies: `E_g=-4.499999999986029`, `E_b=-1.1249999999981295`.
- 위 analytic 값은 각각 `-9/2`, `-9/8`이며 acceptance는 absolute `5e-7`로 사전에 작성했다.
- generalized algebraic residual: `1.9024e-13`, `1.5990e-13`.
- norm: 두 상태 모두 `1.0`; H relative skew `<3.1e-17`.
- analytic 1s/2p radial wavefunctions 및 positive phase와 비교했다.
- angular orthonormality와 bright axis zero를 검사했다.
- UA direct angular selection: `L/(-iℏ)=3.3462e-16`, tolerance `1e-10`.
- 비정상 charge/R/domain/sector/discretization와 evaluation boundary를 거부하는 failure checks.

이것은 새 discretization의 analytic/invariant/failure checks다. 기존 A1/A2 CAS를 재실행하지
않았다. R=2 cross-formulation pilot은 integration owner의 별도 evidence가 소유한다.
united-atom의 매우 작은 energy error를 finite-R cusp/coupling error로 일반화하지 않는다.

## 6. 공개된 한계와 다음 validation

off-center point cusps는 origin-based angular series에 느린 algebraic convergence를 일으킬 수 있다.
따라서 이 표현은 작은 R/중간 R의 독립 reference 후보이고 큰 R에서는 많은 l을 요구한다.
`lmax`, radial mesh/order, radial quadrature, `rmax`를 따로 바꿔 convergence를 분해해야 한다.
domain truncation, omitted l, coupling/torque singularity에 대한 error certificate는 아직 없다.
또한 energy convergence만으로 L이나 torque convergence를 판정하지 않는다.

동일 charge-center origin의 smooth rotation operator는 위 direct lane으로 계산할 수 있지만
singular torque는 별도 quadrature/Hardy-form audit가 필요하다. 그 구현을 이 코드의
angular matrix identity로 대체하지 않는다. Dark azimuthal lane은 정확한 sin/cos 적분에서
0이지만 현재 API는 bright sector만 저장한다. Continuation과 cluster transport는 상위 C1
모듈의 책임이고 C2 finite-R grid는 이 파일에서 실행하지 않았다.
