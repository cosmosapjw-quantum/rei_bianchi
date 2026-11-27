# C2e: fixed-sector pair와 충돌 채널의 spectral target

이 문서는 새 유도(derived)와 채택된 A2/C1b 결과를 구분한다. 새 molecular eigensolve, 충돌 전파, production 구간·허용오차 선택은 하지 않았다. 두 상태 coupling의 기존 수치 검증이 incoming 채널 또는 전체 채널 subspace의 검증과 같지 않다는 점을 정식화하고, 다음 구현에 필요한 정확한 대상을 정의한다. 모델·하네스의 외부 버전은 추정하지 않는다.

## 1. Hamiltonian, 함수공간, 단위

입력 authority는 원 연구 계약의 spinless·비상대론적·한 전자·clamped point-Coulomb 모형 및 A2의 charge-center convention이다. 핵 A는 H, 핵 B는 He이며 He 원자라는 표현은 이 한 전자 문제에서 hydrogenic He⁺ 전자상태를 뜻한다. 중성 He의 두 전자 spectrum을 사용하지 않는다. 핵 전하수는 \(Z_A=1,Z_B=2\), \(\kappa=e^2/(4\pi\epsilon_0)\), \(a_A=\hbar^2/(m_e\kappa)\), \(E_A=\hbar^2/(m_ea_A^2)\)다. 좌표 \(\mathbf r=(x_c,y_c,z)\)와 무차원 거리 \(x=R/a_A\)를 구분한다.

\[
\mathscr H=L^2(\mathbb R^3,d^3r),\quad
\mathbf X_A=-\frac{2R}{3}\mathbf e_z,\quad
\mathbf X_B=\frac{R}{3}\mathbf e_z,
\]
\[
H_R=-\frac{\hbar^2}{2m_e}\Delta
-\frac{\kappa}{|\mathbf r-\mathbf X_A|}
-\frac{2\kappa}{|\mathbf r-\mathbf X_B|}.
\tag{S1}
\]

내적은 첫 인자에 반선형이다. Friedrichs form domain은 \(H^1(\mathbb R^3)\), operator domain은 \(H^2(\mathbb R^3)\)이며 핵 이외의 인공 경계를 두지 않는다. 무한원에서는 bound state의 \(L^2\) 조건을 요구한다. 유한 상자의 경계조건은 이 연속 연산자 정의와 다른 수치 근사다. Coulomb 항의 translated Hardy bound와 Laplacian에 대한 상대 bound 0으로, 이 realization은 핵 위치와 무관한 공통 domain을 갖는다.

이 전자 에너지 규약에서는 \(\sigma_{\rm ess}(H_R)=[0,\infty)\)다. 핵 반발 \(2\kappa/R\)는 공통 scalar로 제외한다. 이를 더하는 규약에서는 bound energies와 continuum threshold가 모두 \(2\kappa/R\)만큼 이동하며, 상태와 모든 energy gap은 불변이다. 핵 반발을 더하고 threshold는 0으로 두면 안 된다. 핵 양자운동, 유한 핵 크기, spin, spin–orbit, 외장은 포함하지 않는다. \(\mathscr H\otimes\mathbb C^2\)의 spin-spectator 확장이면 모든 rank가 두 배가 되지만 여기서는 채택하지 않는다.

## 2. fixed-m pair의 정확한 의미

축대칭성으로부터
\[
\mathscr H=\bigoplus_{m\in\mathbb Z}\mathscr H_m,\qquad
\psi_m(\rho,\phi,z)=\frac{e^{im\phi}}{\sqrt{2\pi}}f_m(\rho,z),
\quad \|f_m\|^2=\int |f_m|^2\rho\,d\rho\,dz.
\]
Meridional operator는
\[
H_R^{(m)}=-\frac{\hbar^2}{2m_e}
\left(\partial_\rho^2+\rho^{-1}\partial_\rho+\partial_z^2
-\frac{m^2}{\rho^2}\right)+V_R.
\tag{S2}
\]
축 조건은 이 Friedrichs form에서 정한다. 핵의 특이점 자체를 제외한 regular axis branch는 \(f_m\sim\rho^{|m|}\), \(m=0\)은 regular even continuation을 갖는다. 핵에서는 Coulomb cusp와 form-domain 조건을 사용한다. 이를 임의의 축 Dirichlet 조건으로 바꾸면 안 된다. \(m\)은 여기서는 무차원 정수이고, \(L_z\) 고유값은 \(m\hbar\)다.

기존 C2의 target은 \(g_R\): \(m=0\) 최저 고유상태와 \(b_R\): \(|m|=1\) 최저 meridional state에 \(\cos\phi/\sqrt\pi\)를 곱한 real bright state다. \(\sin\phi/\sqrt\pi\)를 곱한 \(d_R\)가 dark partner이며, \(E_b=E_d\)는 정확한 축대칭 퇴화다. meridional 최저 상태의 positivity와 simplicity를 사용하면 각 고정 \(R>0\)에서 각각의 sector 내부 target은 위상을 제외하고 유일하다.

\(f_b\)를 \(m=0\) form의 시험함수로 사용하면
\[
E_g\le q_0[f_b]
=E_b-\frac{\hbar^2}{2m_e}\int\frac{|f_b|^2}{\rho^2}\rho\,d\rho\,dz
<E_b.
\tag{S3}
\]
따라서 \(\Delta_R=E_b-E_g>0\)다. 이것이 같은 sector의 ground branch를 다른 branch로 잘못 선택해도 된다는 뜻은 아니다. 수치 구현의 누락 상태·잘못된 잔차·부적절한 위상은 별도로 검사한다.

\(P_g^{(0)}\)와 \(P_b^{(1)}\)는 각 sector의 rank-1 Riesz projector로 정의할 수 있다. 반면
\[
P_{gb}=|g_R\rangle\langle g_R|+|b_R\rangle\langle b_R|
\tag{S4}
\]
는 전체 공간에서 \(H_R\)와 가환하더라도 전체 \(H_R\)의 isolated-energy Riesz projector는 아니다. 제외한 \(d_R\)가 같은 \(E_b\)를 갖기 때문이다. \([P,H]=0\)과 \(P=1_{\Sigma}(H)\)를 혼동하면 안 된다. \(g+b+d\)로 rank-3을 만들어도 다른 \(m=0\) 등의 상태와 energy coincidence가 가능하므로 full-space exterior gap은 자동으로 확보되지 않는다.

특히 \(Q_{gb}=1-P_{gb}\)에 대해 \(\operatorname{dist}[\sigma(H_R|_{\operatorname{Ran}P_{gb}}),\sigma(H_R|_{\operatorname{Ran}Q_{gb}})]=0\)다. 에너지 값의 집합 차 \(\sigma(H_R)\setminus\{E_g,E_b\}\)는 제외한 dark의 같은 에너지 값까지 지우므로, 이 부분 퇴화공간 선택의 gap을 나타내지 못한다. 다음 S5의 집합 차는 실제 Riesz spectral subset에만 적용한다.

따라서 기존 \(\langle g|L_y^O|b\rangle\)를 인정하기 위해 이 불가능한 full-space rank-2 isolation을 요구하지 않는다. 필요한 것은 각 상태를 지정한 sector 안에서 동정하는 것과 관측량 고유의 오차 제어다. 반대로 sector gap으로 전체 공간 cluster의 isolation을 선언하지 않는다.

## 3. Riesz projector와 외부 gap: 무엇을 제외하는가

자기수반 연산자 \(H\)와 선택된 유한 bound spectrum \(\Sigma\)에 대해, 반시계방향 contour \(\Gamma\)가 \(\Sigma\)만 감싸면
\[
P_\Sigma=\frac1{2\pi i}\oint_\Gamma (z-H)^{-1}\,dz,
\quad
\delta_{\rm ext}=\operatorname{dist}\bigl(\Sigma,\sigma(H)\setminus\Sigma\bigr)>0.
\tag{S5}
\]
전체 공간의 정의에서는 다른 모든 \(m\)과 continuum을 제외 spectrum에 포함한다. sector 정의에서는 \(H^{(m)}\)의 spectrum으로 제한한다. 내부 최소 gap은 \(\Sigma\) 안에서만 계산하는 별도 양이며, 이것이 0이라도 \(\delta_{\rm ext}>0\)이면 \(P_\Sigma\)는 붕괴하지 않는다. 개별 eigenvector와 subspace의 안정성을 나누는 이유다.

외부 eigenvalue와 접촉하면 energy contour를 통한 같은 rank의 연속성을 보장할 수 없다. 다른 \(m\)과의 crossing이면 joint \((H,L_z)\) labeling에 의한 sector projector의 direct sum은 계속 정의할 수 있는 경우가 있다. 그 direct sum을 전체 \(H\)의 spectral projector로 부르지 않는다. 같은 \(m\)의 excited branch에도 exact noncrossing을 가정하지 않는다.

인접한 \(R\)의 직교 열 \(U,V\)에는 공통 physical Hilbert inner product의 \(M=U^\dagger V=A\Sigma B^\dagger\)를 사용한다. \(V\mapsto VBA^\dagger\)의 polar/Procrustes transport이면 \(U^\dagger VBA^\dagger=A\Sigma A^\dagger\)가 비음이고, 임의의 \(U(k)\) 열 gauge에 대해 공변적이다. \(\sigma_{\min}(M)=0\)이면 transport가 유일하게 결정되지 않는다. 여기서 새로운 작음의 임계값을 만들지 않고 후속 등록 계약에서 받는다. 서로 다른 basis/mesh의 일반적인 경우, 계수 벡터 dot product는 이 내적을 대신할 수 없다.

## 4. 큰 R의 rank-5와 incoming channel

A2가 확립한 분리 원자 극한에서는
\[
E_{A,n}=-\frac{E_A}{2n^2},\qquad
E_{B,n}=-\frac{2E_A}{n^2}.
\]
따라서 \(-E_A/2\)의 cluster는 \(A1s\) 한 개와 \(B,n=2\) 네 개로 이루어진다.

| target | full-space rank | \(m=0\) rank | \(m=+1\) rank | \(m=-1\) rank |
|---|---:|---:|---:|---:|
| \(A1s+B,n=2\) | 5 | 3 | 1 | 1 |
| 위 target과 \(B1s\) ground | 6 | 4 | 1 | 1 |

실수 표현에서는 두 \(|m|=1\) 열을 \(p_x,p_y\)로 쓸 수 있다. \(m=0\)의 세 열은 원자 극한에서 \(A1s,B2s,B2p_z\)지만, A2의 remote dipole에 의한 \(B2s\)–\(B2p_z\) mixing 때문에 이들을 finite-R의 세 개별 고유상태 라벨로 고정하지 않는다. 극한에서 가장 가까운 외부 level은 \(B,n=3\)이므로 exterior gap의 극한은
\[
\min\{3/2,\ 5/18,\ 3/8,\ 1/2\}\,E_A
=\frac5{18}E_A.
\tag{S6}
\]
이는 sufficiently-large-R isolation의 해석적 근거이지, “\(R=32\)부터 이 수치 하한으로 보장됐다”는 주장이 아니다. A2는 유효 반경과 remainder constant를 구성하지 않았다.

기존 \(g_R,b_R\)는 각각 큰 R에서 \(B1s,B2p_x\)에 접근한다. incoming H(1s)는 이 두 상태에 포함되지 않는다. 따라서 기존 coupling database만으로 incoming capture probability를 계산할 수 없다. rank-5와 ground를 합친 여섯 상태도 원 계약 D1의 최소 세 상태 \(g,e,b\)와 같은 모형이 아니다. 세 상태의 admissibility에는 \(e\) 동정·사영·제외 공간 오차라는 별도 문제가 남는다.

큰 R의 rank-5에서 출발한 **동일한 projector를 연속적으로 추적하며** 전체 구간에서 exterior gap이 열린다는 것을 실제로 증명했다면, 그곳에서는 ground 바로 위 다섯 고유값이라는 ordering이 외부와의 교환 없이 유지된다. 각 R에서 서로 다른 isolated 묶음을 독립적으로 고르는 경우에는 이 결론을 적용하지 않는다. 그 exterior gap 자체가 현재 미검증이므로, 단순히 “큰 R의 다섯 채널을 adiabatic continuation한다”는 말만으로 “전 R의 최저 다섯 excited states”와 동일시하면 순환논증이다. spectrum의 energy order, symmetry-sector continuation, 원자 channel labeling을 별도로 기록한다.

## 5. UA limit: 조건부 ordering 장애와 일반적인 uniform-gap 장애

### 5.1 연속 연산자의 UA limit

\(R\downarrow0\)의 전자 연산자는
\[
H_U=-\frac{\hbar^2}{2m_e}\Delta-\frac{3\kappa}{r}.
\tag{S7}
\]
이 극한은 공통 공간에서 norm-resolvent로 성립한다. 필요한 추정을 명시한다. 무차원화한 \(1/r\)를 매끄러운 cutoff로 \(f+g\)로 나누되 \(f\in L^{3/2}\)는 compact support, \(g\)는 bounded uniformly continuous로 잡는다. translation continuity와 Sobolev embedding에 의해
\[
|\langle u,(V_R-V_0)v\rangle|
\le\epsilon(R)\|u\|_{H^1}\|v\|_{H^1},\qquad \epsilon(R)\to0.
\tag{S8}
\]
여기서 \(L^{3/2}\times L^6\times L^6\)의 Hölder exponent는 \(2/3+1/6+1/6=1\)이다. translated Hardy estimate는 공통 form coercivity를 준다. 충분히 큰 고정 \(c\)와 \(B=(T+c)^{-1/2}\)로 \((H_R+c)^{-1}=B[I+BV_RB]^{-1}B\)를 인수분해하고 S8 및 역연산자의 resolvent identity를 적용하면 norm-resolvent convergence를 얻는다. \(V_R-V_0\)의 \(L^\infty\) norm이 작다는 잘못된 가정은 쓰지 않는다.

일률적 하한도 명시할 수 있다. \(T=-\hbar^2\Delta/(2m_e)\)로 두면
\[
H_R=\frac13\left(T-\frac{3\kappa}{r_A}\right)
+\frac23\left(T-\frac{3\kappa}{r_B}\right)
\ge-\frac92E_A.
\tag{S9}
\]
각 괄호는 단지 위치를 평행이동한 Z=3 hydrogenic Hamiltonian이다.

radial Coulomb quantization \(n=n_r+l+1\), \(l=0,\ldots,n-1\), \(m=-l,\ldots,l\)로부터
\[
E_n^U=-\frac{9E_A}{2n^2},\qquad
d_n=\sum_{l=0}^{n-1}(2l+1)=n^2,
\quad d_{n,m}=n-|m|\quad(n\ge |m|+1).
\tag{S10}
\]
\(n=2\) shell은 full rank 4(\(m=0\) 두 개, \(m=\pm1\) 각 한 개), \(n=3\)은 full rank 9다. 이 정수·유리수 관계만 이번 경량 exact check로 확인했다. 함수해석적 증명을 수치 검사로 대신하지 않았다.

### 5.2 ordering을 선택했을 때의 장애

target을 “전체 공간의 최저 다섯 excited states”로 **별도로 정의한다면**, UA에서 \(n=2\) 네 개와 \(n=3\)의 일부 한 개를 선택하므로 나머지 \(n=3\) 상태와의 gap은 0으로 접근한다. 실제 큰 R channel continuation이 이 target인지는 아직 결정되지 않았다.

마찬가지로 \(m=0\)의 “최저 세 excited states”를 선택하면 UA \(n=2,m=0\) 두 개와 \(n=3,m=0\)의 일부 한 개가 되어 **sector 내부** exterior gap도 닫힌다. 이와 달리 기존 bright 최저 \(|m|=1\)은 UA \(n=2,|m|=1\) 단독 상태에 접근하며 다음 shell과의 gap은 \(5E_A/8\)이다. ground \(m=0\)은 \(n=1\)에 접근하며 다음 shell과의 gap은 \(27E_A/8\)이다. pair의 sector gap이 유한하더라도 rank-5 cluster의 gap이 유한한 것은 아니다.

### 5.3 uniform full-space rank-5 isolation의 no-go

다음 세 조건을 동시에 요구하자.

1. \(P_R\)는 전체 \(H_R\)의 유한 bound-spectrum Riesz projector이며 rank 5다.
2. exact ground를 제외하여 \(P_RP_g(R)=0\)이다.
3. 모든 \(0<R\le R_0\)에서 continuum을 포함한 외부 spectrum에 대한 gap에 일률적 하한 \(\delta>0\)가 있다.

이 조합은 불가능하다. S9와 조건3에 의해 선택 spectrum은 고정 compact interval \([-9E_A/2,-\delta]\) 안에 있다. 따라서 \(n\to\infty\), threshold 0으로 도피할 수 없다. S8의 norm-resolvent limit에 의해 이 구간의 bound spectrum은 유한 개 UA shell의 근방에만 존재한다. 각 UA shell의 모든 eigenvalues는 같은 \(E_n^U\)로 모이므로 한 개를 채택하고 다른 것을 제외하면 exterior gap이 0으로 접근하여 조건3에 모순이다. 따라서 충분히 작은 R의 target은 UA의 **완전한 shell**들의 합집합에 대응해야 한다. ground를 제외하면 그 rank는 \(4,9,16,\ldots\)의 어떤 유한 합이지만 5가 될 수 없다. 따라서 세 조건은 동시에 성립하지 않는다.

이 명제는 adiabatic branches의 구체적인 UA correlation을 가정하지 않으며 “최저 다섯 excited” ordering보다 일반적이다. 다만 배제하는 것은 \(R\to0\)까지의 **일률적인 full-space exterior gap**뿐이다. \(R_{\min}>0\)인 compact interval의 rank-5 isolation, 각 finite R의 branch continuation, symmetry-restricted projector, Q 공간을 보존한 dynamics는 이것만으로 배제되지 않는다. ground를 포함한 rank-5는 UA의 \(1+4=5\)가 가능하므로 ground exclusion은 증명의 본질적 가정이다. 현재 large-R rank-5는 ground를 포함하지 않으므로 이 구별이 필요하다.

rank-5와 ground의 union을 고정 rank-6 full-space isolated projector로 UA까지 일률적으로 유지하려 해도 UA의 complete-shell ranks로 6을 만들 수 없어 같은 counting obstruction이 있다. 여섯 채널 근사의 finite-R 사용 자체를 전면 부정하는 주장은 아니다.

## 6. symmetry reduction과 dynamics의 구별

정적 \(H_R\)는 모든 \(m\) sector를 보존하지만 body-frame dynamics의 \(-\boldsymbol\Omega\cdot\mathbf L\)는 일반적으로 sector를 결합한다. 특히 \(L_y=(L_+-L_-)/(2i)\)는 \(\Delta m=\pm1\)이다. radial connection이 고정 body axes에서 \(m\)을 보존한다는 사실만으로 시간발전이 독립 \(m\) block들의 곱이라고 할 수 없다. ETF의 spatial boost에도 정적 block 구조를 자동 적용하지 않는다.

조건부로 정확한 차원 축소는 가능하다. 실제 채택한 핵 궤도·boost·가속도가 모두 xz 평면 안에 있고 generator가 \(y_c\mapsto-y_c\) reflection을 보존하며 초기 incoming state가 even이면 odd block은 생성되지 않는다. 이 경우 large-R rank-5의 reflection-even 부분은 rank 4(\(A1s,B2s,B2p_z,B2p_x\))이고 \(B2p_y\)는 odd다. 그러나 이것은 현재 미확정 궤도·representation을 선택할 근거가 아니며 조건을 만족하는 후속 계약에서만 사용할 수 있다. reflection-even 공간에도 모든 \(\cos(m\phi)\)가 있으므로 fixed \(|m|=1\) sector와 같지 않다.

## 7. 구현·인증에 필요한 경계

후속 구현은 `pair_sector`, `large_R_rank5_full`, `symmetry_resolved_continuation`, 필요시 명시적으로 채택한 `planar_even`을 별도 target type으로 둔다. 각 target은 Hilbert space, sector ranks, ground inclusion, energy origin, continuum threshold, 선택 근거, contour/gap의 대상 spectrum, physical inner-product adapter를 갖는다. representation gauge와 energy ordering은 별도 field다.

유한요소/B-spline의 Ritz eigenvalue gap은 연속 연산자 \(\delta_{\rm ext}\)의 하한이 아니다. 예를 들어 채택된 Ritz upper bound가 \(U_k\), 다음 제외 eigenvalue의 **독립적으로 유효한 lower bound**가 \(L_{k+1}\)인 ordered contiguous target이면 상부 gap의 하한으로 사용할 것은 \(L_{k+1}-U_k>0\)다. 두 upper bound의 차가 아니다. 비연속 target이나 아래쪽도 제외하는 cluster는 양쪽 모든 exterior spectrum에 대응하는 enclosure가 필요하고 continuum도 포함해야 한다. 보이지 않는 상태가 없다는 state count를 동반하지 않는 작은 matrix gap은 certificate가 아니다.

또한 \(\|P-\widehat P\|\)의 L² bound만으로 \(L_y\) matrix element를 인증하지 않는다. \(L_y=-i\hbar(z\partial_{x_c}-x_c\partial_z)\)는 비유계이고 좌표 weight를 포함한다. 일반적인 unweighted H² bound도 이를 일률적으로 제어하지 못한다. 예컨대 멀리 평행이동한 고정 packet은 H² norm을 유지하지만 \(r\nabla\) norm은 증가시킬 수 있다. direct lane에는 weighted derivative/tail estimate 또는 대상 bound-state class에서 증명된 graph/form bound가 필요하다. A2 torque lane의 Hardy bilinear bound는 다른 computational form을 제공하지만 거기서도 H¹ state error와 양의 energy-gap 하한, origin/force identity의 정확한 대응이 필요하다. 기존 residual·h/p/q/tail 차이를 엄밀 enclosure라고 부르지 않는다.

새 거리나 허용오차 없이 즉시 구현할 수 있는 최소 단위는 이 target들의 입력 검사와 manufactured degenerate-spectrum에 대한 subspace transport/claim rejection이다. 후속의 trajectory-independent electronic reference pilot은 production collision domain을 선택하지 않고도 별도 계약에 exact R 배열·target·잔차/gap/관측량 예산·wall/RSS cap을 등록하여 수행할 수 있다. 이를 collision-relevant 전체 범위의 검증으로 승격하려면 채택 trajectory 및 parameter 범위가 주는 실제 R 영역과의 연결이 추가로 필요하다. 이 문서는 새 rank-5 solve, 숨은 crossing 탐색, production default 변경을 승인하지 않는다.

## 8. 근거 상태, 실제 수행, 미실시

계승한 직접 자료는 A2 `provenance/A2_ASYMPTOTIC_DERIVATION_KO.md`, C1b `provenance/C1B_NEXT_HANDOFF_KO.md`, C2d `NEXT_HANDOFF_KO.md`와 `review/NEXT_DEPENDENCY_RECOMMENDATION_KO.md`, 원 연구 계약 `provenance/USER_CONTRACT_ORIGINAL.txt`다. byte identity는 동반 JSON에 기록한다. A2의 fixed-sector asymptotics와 rank-5 large-R isolation은 계승한 해석 결과이며, C2e가 다시 증명·계산하여 완료했다고 취급하지 않는다.

이번 신규 derived 결과는 S3 gap 구별의 적용, S4의 full-rank-2 Riesz 불가, S8–9의 UA continuity/lower-bound 명시, S10을 사용한 조건부 ordering 장애와 uniform rank-5 no-go, 구현에서 구별할 target과 관측량 error semantics다. S6/S9/S10의 유리수·퇴화수 경량 exact check는 동반 JSON에 입력·출력을 보존한다. 신규 과학 수치 solve는 `NOT_RUN`이다.

보조적인 문헌 동정으로 Kato의 [Perturbation Theory for Linear Operators, DOI 10.1007/978-3-642-66282-9](https://link.springer.com/book/10.1007/978-3-642-66282-9) 출판사 metadata/목차를 확인했다(2026-10-01 UTC). 책 본문을 확보했다고 주장하지 않는다. Kato, *Fundamental properties of Hamiltonian operators of Schrödinger type*, Trans. AMS 70 (1951) 195–211의 [AMS 원저 PDF](https://www.ams.org/journals/tran/1951-070-02/S0002-9947-1951-0041010-X/S0002-9947-1951-0041010-X.pdf)는 검색으로 동정했으나 fetch는 403이었다. 이를 신규 원문 검증이 끝난 정리의 근거로 대신하지 않는다. 이 문서의 신규 수학적 주장은 위 추정과 독립 검토로 평가한다.

`full_C2_closed=false`, `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`, `Eq55_next_node_authorized=false`, `production_default_change=NOT_AUTHORIZED`를 유지한다. collision domain, finite-R 외부 gap, continuum enclosure, incoming-state solver, 정량적인 channel error는 미완료다.
