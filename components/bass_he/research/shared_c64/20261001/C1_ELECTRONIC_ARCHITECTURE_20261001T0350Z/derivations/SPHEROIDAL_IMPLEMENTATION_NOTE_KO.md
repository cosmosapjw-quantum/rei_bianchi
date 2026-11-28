# C1 분리형 B-spline 구현 및 좁은 검증

작성 범위는 `code/spheroidal.py`, `code/test_spheroidal.py`와 해당 evidence다. 기존 production code를 변경하지 않았다. `code-work` 지침과 이전 namespace의 `AGENTS.md`, A2 `NEXT_HANDOFF_KO.md`를 읽고 독립적인 연구 prototype을 작성했다. Authors' ARSENY code를 사용하거나 복제한 구현이 아니다.

## 컨벤션과 구현 식

길이 단위는 \(a_A=\hbar^2/(m_e k)\), 에너지 단위는 \(E_A=\hbar^2/(m_e a_A^2)\)다. 입력 R와 출력 energy는 이 단위의 무차원 수다. \(k=e^2/(4\pi\epsilon_0)\)이며 핵 반발 common energy는 포함하지 않는다. 핵 A는 midpoint 좌표 \(z=-R/2\), B는 \(z=R/2\)에 둔다.

\[
\xi=(r_A+r_B)/R,\quad\eta=(r_A-r_B)/R,\quad
\rho=\frac R2\sqrt{(\xi^2-1)(1-\eta^2)},\quad z=\frac R2\xi\eta.
\]

\(p=\xi^2-1,q=1-\eta^2\)라 놓으면 두 분리 operator는

\[
A_\xi(E)=-\partial_\xi p\partial_\xi+m^2/p-R(Z_A+Z_B)\xi-ER^2\xi^2/2,
\]
\[
A_\eta(E)=-\partial_\eta q\partial_\eta+m^2/q-R(Z_B-Z_A)\eta+ER^2\eta^2/2.
\]

최저 고정 \(|m|\) 상태는 각각의 최저 고윳값 \(\lambda_\xi(E),\lambda_\eta(E)\)를 구해 \(F(E)=\lambda_\xi+\lambda_\eta=0\)으로 선택한다. 유한 \(R>0\)와 regular endpoint 조건에서 각 ground Sturm–Liouville 상태를 선택하므로 energy sorting에 의한 서로 다른 상태의 continuation을 수행하지 않는다. 더 높은 상태와 near-degenerate cluster transport는 이 구현의 기능이 아니다.

\(X=p^{m/2}u,Y=q^{m/2}v\)로 factor를 분리하면 radial mass는 \(\int p^m uv\), kinetic weak form은

\[
K_\xi[u,v]=\int p^{m+1}u'v'\,d\xi-m(m+1)\int p^m uv\,d\xi,
\]

angular 쪽은

\[
K_\eta[u,v]=\int q^{m+1}u'v'\,d\eta+m(m+1)\int q^m uv\,d\eta.
\]

분리 potential을 각 mass weight에 곱한다. finite endpoint에는 regular finite-energy 자연 경계조건을 두며 log/negative-power 가지는 trial space에 포함하지 않는다. 외곽 \(\xi_{\max}=1+2L/R\)에서만 마지막 B-spline coefficient를 제거하여 Dirichlet 조건을 부과한다. 이는 무한영역 해와 동일하다는 주장이 아니며 L은 이후 별도로 변화시켜야 한다.

현재 기본값은 degree 7, radial 36 elements, angular 14 elements, element당 12점 Gauss–Legendre, \(L=24a_A\)다. radial knots는 \(\xi_j=1+(2L/R)(j/N)^2\)다. 각 행렬원소는 factor 후 polynomial이며 \(Q\ge d+m+2\) 조건으로 quadrature degree를 검사한다. 이 점은 별도 singular coupling quadrature의 정확도를 보장하지 않는다.

일반화 고유문제는 SciPy `eigh(..., subset_by_index=(0,0), driver="gvx")`, 에너지 root는 `brentq`로 푼다. mass-normalized eigenvector에서

\[
F'(E)=\frac{R^2}{2}(\langle\eta^2\rangle-\langle\xi^2\rangle)<0.
\]

bracket의 Coulomb 에너지는 \(n_{\min}=m+1\)을 사용한다. Lower/upper Coulomb trial bracket 바깥에 2% scale padding을 두는 것은 유한 basis root finder를 위한 장치이며 에너지 enclosure/certificate가 아니다. bracket이 닫히지 않으면 예외를 반환하며 임의 expansion이나 상태 대체를 하지 않는다. `R=0`은 이 chart의 입력으로 허용하지 않는다.

## API와 정규화

```python
from spheroidal import solve, SpheroidalConfig
state = solve(2.0, ZA=1.0, ZB=2.0, m=0,
              config=SpheroidalConfig())
G, G_xi, G_eta = state.evaluate(xi, eta)
record = state.metadata()
```

`evaluate`는 broadcasting되는 scalar/array를 받고 물리적으로 정규화된 positive meridional amplitude와 두 coordinate derivative를 돌려준다. `m=0`에서는 \(g=G/\sqrt{2\pi}\), bright `m=1`에서는 \(b=G\cos\phi/\sqrt\pi\)다.

\[
\int\rho\,d\rho\,dz\,G^2=1,
\quad\rho\,d\rho\,dz=\frac{R^3}{8}(\xi^2-\eta^2)d\xi d\eta,
\]
\[
G=\left[\frac{R^3}{8}(\langle\xi^2\rangle-\langle\eta^2\rangle)\right]^{-1/2}XY.
\]

Finite-domain 외부 평가를 거부한다. odd m의 coordinate derivative는 \(\xi=1\), \(\eta=\pm1\)에서 발산할 수 있으므로 미분 적분에는 open quadrature nodes를 사용한다. 이 chart singularity를 Cartesian derivative 또는 물리적 발산과 동일시하면 안 된다. 내부 axis nodes/weights는 `_radial.nodes`, `_radial.weights`, `_angular.nodes`, `_angular.weights`로 현재 pilot integrator가 접근할 수 있다. Public production API로 안정화된 인터페이스는 아니다.

metadata의 radial/angular residual은 행렬 잔차
\(\|Ac-\lambda Mc\|/[(\|A\|_2+|\lambda|\|M\|_2)\|c\|]\)다. 원 continuum operator 잔차나 coupling 오차한계가 아니다. cache는 한 solve 안에서 exact float energy를 key로 사용한다. 반올림 key 또는 외부 persistent cache를 사용하지 않는다.

## 실제 검증과 실패 보존

Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0에서 다음만 실행했다.

1. `python code/test_spheroidal.py` — degree 5 최초 결과 exit 1. 에너지는 단일 중심 analytic값에 \(6.8\times10^{-11}\) 이내였으나 파동함수/미분 오차 약 \(3\times10^{-7}\)가 preset tolerance를 넘었다. `SPHEROIDAL_DEGREE5_FAILURE_LOG.txt`에 원 실패를 보존했다. 에너지만으로 coupling용 상태 정확도를 판정할 수 없음을 직접 드러낸 discretization failure다.
2. 기본 degree를 7로 변경한 redirect 실행 — tool exit 0이었으나 저장 로그가 중간에서 끝났다. 이는 과학적 PASS 근거로 사용하지 않고 `SPHEROIDAL_DEGREE7_INCOMPLETE_CAPTURE.txt`에 보존했다. 원인은 미확정인 output-capture anomaly다.
3. `python -u code/test_spheroidal.py` — 누락된 완료 증거를 회복하기 위한 최소 재실행. 실제 완료 transcript, exit 0, 4 tests PASS. `SPHEROIDAL_UNIT_CHECK_LOG.txt`에 tool chunk `c5376c` 결과를 보존했다. 실행시간 0.162초.

단일 중심 \(R=2,Z_A=0,Z_B=2\)의 기준값은 m=0의 He+ 1s 에너지 \(-2E_A\), m=1의 lowest bright 2p 에너지 \(-E_A/2\)다. 결과는 각각 \(-2.000000000001346\), \(-0.5000000000001357\)였다. analytic hydrogenic amplitude와 두 미분을 네 interior points에서 비교하고 meridional norm, phase, monotone derivative, discrete residual을 검사했다. 두 계의 radial/angular discrete relative residual은 \(8.6\times10^{-16}\) 이하, matching residual은 \(1.7\times10^{-12}\) 이하였다. 에너지 오차가 음수인 \(10^{-12}\) 크기 차이는 floating-point root/eigensolve 영향이며 엄밀한 variational enclosure를 주장하지 않는다.

입력 실패 검사는 R=0/NaN, 음전하, 총전하 0, 음수/noninteger/bool m, underintegrated quadrature, invalid extent/elements/degree를 포함했다. 실제 두 중심 R-grid, 외곽 및 basis convergence sweep, continuum residual certification, transport, direct/torque coupling은 이 작성자 검증 범위에 포함하지 않았다. Root coordinator가 별도 pilot를 수행할 수 있지만 그 결과와 본 검증을 구분해야 한다.

상태: `IMPLEMENTATION_VERIFIED_FOR_BOUNDED_SINGLE_CENTER_CHECKS`; `CONTINUUM_ACCURACY_NOT_CERTIFIED`.
