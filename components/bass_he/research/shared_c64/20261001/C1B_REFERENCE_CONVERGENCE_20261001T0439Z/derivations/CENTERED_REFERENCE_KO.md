# C1b 독립 구면 reference의 좌표 중심과 직접 연산자

## 범위와 단위

C1의 독립적인 구면 부분파 hp-FEM 표현을 복사한 별도 연구 모듈이다. 원 C1 파일은 수정하지 않았다. 물리적인 두 중심 Coulomb Hamiltonian, charge-center 관측량, 전자 상태 선택은 유지하고 수치 구면 좌표의 중심만 `O` 또는 `B`로 선택한다. 기본값은 `B`다. C1의 prolate B-spline 분리 solver를 사용하거나 호출하지 않는다.

물리 단위는 먼저 \(a_A=\hbar^2/(m_e\kappa_A)\), \(E_A=\hbar^2/(m_ea_A^2)\)로 정의한다. 구현의 좌표와 에너지는 각각 \(a_A,E_A\)로 나눈 값이다. `ZA,ZB`는 고정한 \(\kappa_A\)에 대한 무차원 Coulomb 계수다. 원자 테스트에서 `ZA=0`으로 두어도 이 단위의 정의를 재설정하지 않는다. 핵 반발 에너지는 전자 Hamiltonian에서 제외한다.

원점 \(O\)는 charge center이며 핵 \(A\)는 음의 \(z\), \(B\)는 양의 \(z\) 쪽이다. \(a=Z_A R/(Z_A+Z_B)\)로 쓰면

\[
 (z_A,z_B)_O=(-Z_BR/(Z_A+Z_B),a),\qquad
 (z_A,z_B)_B=(-R,0),\qquad z_O=z_B+a.
\]

따라서 좌표 선택은 물리 변경이 아니다. 단, 유한 구면 경계 `rmax`가 정의하는 실제 공간 영역은 중심에 따라 달라진다. 무한 공간 동등성만으로 유한 영역 오차가 같다고 판단할 수 없으므로 O/B 비교와 별개인 tail refinement가 필요하다.

## 부분파와 Galerkin 형식

\[
 \psi_g=G(r,\eta)/\sqrt{2\pi},\qquad
 \psi_b=A(r,\eta)\cos\phi/\sqrt\pi,
\]
\[
 G_m=\sum_{\ell\ge m}\frac{u_{\ell m}(r)}r\,\mathcal A_{\ell m}(\eta),\quad
 \mathcal A_{\ell m}=(-1)^m
 \sqrt{\frac{2\ell+1}{2}\frac{(\ell-m)!}{(\ell+m)!}}P_\ell^m(\eta).
\]

여기서 \(P_\ell^m\)는 Condon–Shortley 위상을 포함하므로 \(\mathcal A_{mm}\)는 양수다. 각 구면 harmonic은 \(\eta\)와 \(\phi\)에 대해 정규화되며 \(\sum_\ell\int u_\ell^2 dr=1\)이다. 방사형 원점 및 외곽에 \(u_\ell=0\), 축에는 harmonic의 정칙성 조건을 적용한다. 점 Coulomb potential은 softening하지 않는다.

중심의 signed 위치를 \(z_C\)라 하면 각 multipole은

\[
 V_L(r)=-\sum_{C=A,B} Z_C\,\operatorname{sgn}(z_C)^L
 \frac{\min(r,|z_C|)^L}{\max(r,|z_C|)^{L+1}}.
\]

\(z_C=0\)인 항은 별도로 \(V_0=-Z_C/r\)만 더한다. 제한된 \(\ell\le\ell_{\max}\)의 행렬 원소에는 \(L\le2\ell_{\max}\)까지만 필요하다. B 중심에서 B cusp는 중심 potential로 정확하게 표현되지만 A의 off-center cusp에는 여전히 angular truncation 오차가 남는다. 낮은 \(\ell_{\max}\)에서 수렴한다는 보장은 없다.

Hamiltonian의 방사형 block은

\[
 H_{\ell k}=\frac12\delta_{\ell k}\!\int u_\ell'v_k' dr
 +\frac{\ell(\ell+1)}2\delta_{\ell k}\!\int\frac{u_\ell v_k}{r^2}dr
 +\int u_\ell V_{\ell k}v_k dr.
\]

Gaunt 적분은 유한 다항식 차수를 포괄하는 Gauss–Legendre quadrature로 계산하고 금지된 triangle/parity 항을 정확히 0으로 만든다. hp-FEM은 요소별 Lagrange–Lobatto 다항식이며 질량 행렬을 대각화하지 않는다. 바깥 원점의 Coulomb cusp를 통과하는 반지름은 요소 경계에 포함한다. 각 요소의 작은 dense block을 sparse 전역 행렬에 합친다. 전역 dense Hamiltonian은 만들지 않는다.

## 직접 각운동량, 운동량, 쌍극자

\(L_y=-i\hbar(z\partial_x-x\partial_z)\)이고 밝은 상태는 \(\cos\phi\) 방향이다. 수치 중심에 대한 직접 각운동량은 harmonic ladder 항등식에서

\[
 \overline L_c\equiv\frac{\langle g|L_{y,c}|b\rangle}{-i\hbar}
 =\sum_{\ell\ge1}\sqrt{\frac{\ell(\ell+1)}2}
 \int u_{g\ell}u_{b\ell}\,dr.
\]

실수 radial phase는 최저 meridional 상태의 양의 phase probe로 고정한다. 이 유한 점 phase 규칙은 유한 basis 상태의 모든 점에서의 positivity 증명이 아니다.

\(q=1-\eta^2\)일 때

\[
 C_{\ell k}=\int_{-1}^{1}\mathcal A_{\ell0}\sqrt q\,\mathcal A_{k1}\,d\eta,
\quad
 D_{\ell k}=\int_{-1}^{1}\mathcal A_{\ell0}
 \left[-\eta\sqrt q\,\mathcal A_{k1}'+\frac{\mathcal A_{k1}}{\sqrt q}\right]d\eta.
\]

원통 좌표에서 \(\partial_x[A\cos\phi]\)를 azimuth 적분하면 \((A_\rho+A/\rho)/\sqrt2\)가 남는다. 다시
\(\partial_\rho=\sqrt q\,\partial_r-\eta\sqrt q\,\partial_\eta/r\)를 대입하여

\[
 \overline p_x\equiv\frac{\langle g|p_x|b\rangle}{-i\hbar/a_A}
 =\frac1{\sqrt2}\sum_{\ell k}
 \left[C_{\ell k}\int u_{g\ell}u_{bk}'dr
 +(D_{\ell k}-C_{\ell k})\int\frac{u_{g\ell}u_{bk}}r dr\right],
\]
\[
 \overline d_x\equiv\frac{\langle g|x|b\rangle}{a_A}
 =\frac1{\sqrt2}\sum_{\ell k}C_{\ell k}\int r u_{g\ell}u_{bk}dr.
\]

두 연산자 모두 \(|\ell-k|=1\)만 허용한다. \(\mathcal A_{k1}=\sqrt q\) 곱하기 다항식이므로 위 angular integrand의 겉보기 축 singularity는 소거된다. 구현은 축을 제외한 Gauss 점을 사용한다. 원점 요소에서 \(u_g,u_b\) 모두 \(r\) 인자를 가지므로 \(u_g u_b/r\) 역시 정칙하다. 서로 다른 방사형 mesh는 경계의 합집합에서 적분한다. 같은 finite radial domain과 같은 수치 원점을 요구한다.

원점 이동은 물리적인 연산자 항등식

\[
 L_{y,O}=L_{y,B}+a p_x
\]

를 사용한다. 따라서 B 중심 상태에서 \(\overline L_O=\overline L_B+(a/a_A)\overline p_x\), O 중심 상태에서 \(\overline L_O=\overline L_c\)다. 이 직접 lane은 에너지 차, commutator 또는 singular force/torque를 사용하지 않는다. 그 때문에 \(\overline p_x=(\Delta E/E_A)\overline d_x\)와 direct/torque 일치를 별도의 검증으로 사용할 수 있다. 차원은 각각 \(\hbar,\hbar/a_A,a_A\)로 복원된다.

## tail mesh와 두 Ritz root

`boundaries=None`은 기존 exponential grid에 두 핵의 반지름을 삽입한다. 명시적인 `boundaries`는 strictly increasing이며 처음과 끝이 정확히 `0,rmax`이고 핵 반지름을 정확한 원소로 포함해야 한다. 입력을 묵시적으로 재격자화하지 않는다. 따라서 이전 경계를 그대로 두고 바깥에 요소만 추가한 tail 시험을 구현할 수 있다. 이 검사는 discretization 입력 검증이며 외곽 오차가 작다는 판단 자체는 후속 관측량 비교가 맡는다.

`nroots=1|2`는 같은 finite generalized eigenproblem의 최저 Ritz root 한 개 또는 두 개를 계산한다. Coulomb form 하한보다 작은 shift를 사용하는 shift-invert 방식이며 deterministic 시작 벡터를 사용한다. 각 root의 algebraic residual을 별도로 남긴다. 반환 상태는 최저 root이고 `ritz_eigenvalues`, `ritz_residuals`, `discrete_sector_gap`은 metadata다. 이 gap은 finite domain/basis의 값이며 continuum isolation certificate 또는 Kato 오차 경계가 아니다. 둘째 root의 고유벡터를 저장하거나 excited-state continuation을 구현했다는 주장을 하지 않는다.

## 새 구현 검증과 남은 수치 판정

`test_centered.py`는 다음 다섯 개의 변경 seam을 검사한다.

1. `ZA=0,ZB=2,R=2,center='B',m=0,lmax=0,nroots=2`에서 정확한 1s/2s 원자 에너지 \((-2,-1/2)E_A\), 차이 \(3E_A/2\), 두 algebraic residual 및 origin metadata.
2. 해석적인 charge \(Z=3\) 1s/2p radial 함수에서 \(\overline d_x=128\sqrt2/(243Z)\), \(\overline p_x=16\sqrt2 Z/81\), \(\overline L_c=0\), charge-center translation. 서로 다른 radial partition을 사용한다.
3. 동일한 정규화 radial 함수의 \(\ell=1\) 직접 generator 원소가 1인지 확인.
4. tail extension이 기존 내부 grid를 byte-equivalent float 값으로 보존하는지, 누락된 핵 경계와 중복 경계를 거부하는지 확인.
5. 잘못된 origin, root count, 영인 총전하, domain mismatch 입력을 거부하는지 확인.

결과는 `evidence/CENTERED_UNIT_RESULT.json`과 `CENTERED_UNIT_LOG.txt`에 보존했다. 이 다섯 검사는 통과했다. 원 C1의 변경되지 않은 test suite는 재실행하지 않았다. 이 문서 작성 agent는 H/He \(R=2\) angular/radial pilot을 실행하지 않았다. 실제 C1b 독립 수렴, torque 일치, outer-domain 오차의 최종 판정은 coordinator의 사전 수치 계약과 새 pilot 결과에 달려 있다.

## 출력 경계 수정과 실행 identity

독립 검토는 unit runner가 기존 JSON을 `write_text`로 덮어쓸 수 있다는 I/O 결함을 지적했다. 이미 실행된 원본 bytes를 `evidence/EXECUTED_TEST_CENTERED_V1.py`에 보존한 뒤, `code/test_centered.py`에 suite 실행 전 existing-output guard와 `evidence_io.atomic_json`을 적용했다. 원자 solve, 수학식, tolerance, test assertion은 변경하지 않았고 과학 계산도 다시 실행하지 않았다.

- 실제 과학 검증을 수행한 원본 runner SHA-256: `a15898f0adfdd0896ee0db2592f68de956145112f51f407b9dad6bb0708d6a2b`.
- I/O 수정 후 배포 runner SHA-256: `64252667e349cfb8610a46c05782870319552f1215146df51c65238de1ef4ab9`.
- 보존된 과학 결과 JSON SHA-256: `ca816ede43fdc9b7e7721fdc314d426b84858e30e9680378fa66558cc0d42495`.

새 subprocess regression은 `solve` 호출 시 즉시 실패하도록 계측하고 기존 출력이 있는 상태에서 runner를 실행했다. `setUpClass`에 도달하기 전 기대한 `FileExistsError`로 종료(exit 1)했고, 과학 결과의 실행 전후 SHA-256은 같았다. 이 I/O regression은 PASS이며 `CENTERED_UNIT_IO_REGRESSION.json`과 `CENTERED_UNIT_IO_REGRESSION_LOG.txt`에 별도로 기록했다. 최초 unit PASS와 수정된 I/O 경계 검증은 서로 다른 실행 identity다.
