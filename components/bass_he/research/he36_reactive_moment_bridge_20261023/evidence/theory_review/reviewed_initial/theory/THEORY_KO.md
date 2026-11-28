# HE36 반응 pressure-moment 연결

## 1. 확보한 결과와 정의역

공통 평균속도·공통 온도 T의 비상대론적 두 종에 대해, 상대속력만의 양의 반응 kernel K(g)가 **제거하는 부모 분포**의 입자수·열·STF pressure source를 유도했다. 결과는 사건률 α뿐 아니라 에너지 모멘트 β,γ를 필요로 하며, 유한질량에서는 두 종의 STF가 서로 결합한다. 생성·산란된 입자의 분포는 이 loss 계산으로 정해지지 않는다. 따라서 loss+명시적으로 공급된 gain/source를 합한 뒤에만 net reaction heat/pressure로 해석한다.

국소 orthonormal 공통 bulk rest frame을 쓰며 spacetime signature는(-+++)다. c,ℏ,k_B는1로 놓지 않는다. 아래 비상대론적 Gaussian은 k_BT≪m_s c²를 전제로 한다. 미분 연산에는 K와 적분 domain이 T와 무관하고 지배수렴에 필요한 적분 가능한 경계가 있다는 조건이 필요하다. Screening 등으로 K 자체가 T에 의존하면 아래 도함수 항등식에 별도 ∂_T K가 추가된다.

θ=k_BT[J], μ=m_a m_b/(m_a+m_b), E=μg²/2. 상대 Maxwellian 에너지 measure는

\[
d\mathcal M_T(E)=\frac{2\sqrt E}{\sqrt\pi\,\theta^{3/2}}e^{-E/\theta}\,dE.
\]

정의 α=⟨K⟩, β=⟨EK⟩, γ=⟨E²K⟩의 단위는 각각 m³/s, J·m³/s, J²·m³/s다. Pressure tensor P_s=n_sθI+π_s, trπ_s=0이며 thermal energy는 trP_s/2다. 압력 source S_s에 대해 Q_s=trS_s/2, J_s=S_s−2Q_s I/3를 사용한다.

## 2. Scalar rate에서 필요한 에너지 모멘트로

\(T\partial_Td\mathcal M_T=(E/\theta-3/2)d\mathcal M_T\)를 적분하면

\[
\beta=\theta\left(T\alpha'+\frac32\alpha\right),\qquad
\gamma=\theta^2\left(T^2\alpha''+5T\alpha'+\frac{15}{4}\alpha\right).
\tag{1}
\]

일반적으로 \(T\partial_T M_j=M_{j+1}/\theta-3M_j/2\)다. M3도 같은 준비된 quadrature로 계산해 γ의 도함수 검산에 사용하지만 새 물리 channel은 추가되지 않는다.

K≥0이면 α,β,γ≥0 및 Cauchy–Schwarz로 αγ≥β²다. 유한 support[L,U]에서는 Lα≤β≤Uα이고 γ≤(L+U)β−LUα도 성립한다. 이는 채택된 양의 유한모형 내부의 moment consistency다. 미측정 tail의 상한은 아니다. Empirical α(T)를 두 번 미분해 얻은 γ는 fit-derivative construction이며 independent microscopic γ 정확도 자료를 대신하지 않는다. Mao RR loss factor와 별도 number-rate fit을 결합한 hybrid에 식(1)을 자동 적용하지 않는다.

## 3. 정지한 무한질량 표적 bath의 STF loss

이 절은 표적의 thermal velocity를 무시하는 heavy fixed-target 극한이다. E=m_s c²/2이며 μ→m_s다. 유한질량의 Maxwellian bath에는 §4의 CM 에너지와 질량 분율을 포함한 식을 사용한다.

한 종의 작은 Grad 방향을

\[
f_s=f_{M,s}\left[1+\frac{m_s}{2n_s\theta^2}\pi_{s,kl}c_kc_l\right]+O(\pi_s^2)
\tag{2}
\]

로 정의한다. 이 식은 f의 **무한소 first variation**이다. 유한 π를 넣은 polynomial이 모든 속도에서 양수가 되는 것은 아니다. 숫자로 |π|/p가 작다는 사실만으로 threshold 먼 꼬리에서의 유한 진폭 오차를 제한하지 않는다.

등방 angular 평균 \(\langle\hat c_i\hat c_j\hat c_k\hat c_l\rangle=(\delta_{ij}\delta_{kl}+\delta_{ik}\delta_{jl}+\delta_{il}\delta_{jk})/15\)를 사용한다. Traceless π와 수축하면 첫 항이0이고 나머지 두 항이 같은 π_ij를 준다. \(m_s^2c^4=4E^2\)이므로

\[
R_s=-n_sn_t\alpha,\quad Q_s=-n_sn_t\beta,\quad
J_s=-n_t\kappa_2\pi_s,
\]
\[
\boxed{\kappa_2=\frac{4\gamma}{15\theta^2}
=\alpha+\frac43T\alpha'+\frac4{15}T^2\alpha''.}
\tag{3}
\]

α는 사건수의 평균이고 κ2는 STF 가중 평균이다. κ2를 전체 CI/RR의 net pressure relaxation rate라고 부를 수 있는지는 gain/source 항과 closure에 달려 있다.

## 4. 유한질량 두 부모의 incoming-loss

a=m_a/M,b=m_b/M,M=m_a+m_b. 공통 T에서 V=(m_ac_a+m_bc_b)/M와 g=c_a−c_b는 독립 Gaussian이고 cov(V)=θI/M, cov(g)=θI/μ다. c_a=V+bg,c_b=V−ag를 사용한다. 평균 운동에너지의 분해는

\[
\langle\tfrac12m_ac_a^2K\rangle=\tfrac32a\theta\alpha+b\beta,
\quad
\langle\tfrac12m_bc_b^2K\rangle=\tfrac32b\theta\alpha+a\beta.
\]

따라서

\[
R_a=R_b=-n_an_b\alpha,
\quad Q_a=-n_an_b(\tfrac32a\theta\alpha+b\beta),
\quad Q_b=-n_an_b(\tfrac32b\theta\alpha+a\beta).
\tag{4}
\]

STF의 fourth-velocity contraction은 V⁴, V²g², g⁴ 세 항이다. \(\kappa_1=2\beta/(3\theta)\)로 두면

\[
A=a^2\alpha+2ab\kappa_1+b^2\kappa_2,
\quad B=b^2\alpha+2ab\kappa_1+a^2\kappa_2,
\quad C=ab(\alpha-2\kappa_1+\kappa_2),
\]
\[
\boxed{\begin{pmatrix}J_a\\J_b\end{pmatrix}
=-\begin{pmatrix}n_bA&n_aC\\n_bC&n_aB\end{pmatrix}
\begin{pmatrix}\pi_a\\\pi_b\end{pmatrix}.}
\tag{5}
\]

예를 들어 π_a의 자기 항은 m_a²/θ² times [ (θ/M)²α+2(θ/M)b²(2β/3μ)+b⁴(4γ/15μ²)]이며 정확히 A로 정리된다. 교차 항은 두 g계수 부호가 반대여서 가운데 항의 부호가 바뀌고 C를 준다. 이것은 탄성 산란의 gain−loss operator와 다른 반응 incoming term이다. 두 부모의 합 Q=−n_an_b(3θα/2+β)는 제거된 center-of-mass kinetic energy까지 포함한다. 이를 재결합 net cooling 또는 nuclear heat로 쓰면 생성물의 CM/운동에너지를 중복 제거하게 된다.

## 5. 부호와 구조를 이용한 단순화

n_a,n_b>0에서 W=diag(1/n_a,1/n_b)는 식(5)의 loss block을 대칭화한다. 직접 전개하면

\[
AB-C^2=(a+b)^2\{(a-b)^2\alpha\kappa_2+
2ab\kappa_1(\alpha+\kappa_2)\}.
\tag{6}
\]

물리적으로 양의 α,β,γ와 유한 양의 질량에서 양의 determinant이므로, 밀도와 계수를 고정한 loss subproblem의 weighted quadratic STF norm은 소산된다. 반응으로 밀도가 변하는 전체 문제에서는 W의 시간 미분도 따로 포함해야 한다. 퇴화한0kernel/0density에서는 해당 준정부호 한계만 적용한다. 이는 각 종의 signed π성분이 개별적으로 단조 감소한다는 뜻이 아니다.

K∝E^s,s>−3/2에서 κ1/α=(2/3)(s+3/2), κ2/α=(4/15)(s+3/2)(s+5/2), C/(abα)=4s(s−1)/15다. 상수 단면적(s=1/2)은 C<0이다. 동일 질량·밀도에서는 A=B=79α/60,C=−α/60이고 loss eigenvalue는13nα/10,4nα/3이다. 음의 C를 clipping하면 원래 angular/energy projection을 바꾼다. 구현은 모든 STF 성분에 같은2×2block을 사용하며 거대한 velocity 또는 reaction Jacobian을 구성하지 않는다.

## 6. 한 온도에서 scalar 자료만으로 정해지지 않는 항

고정 θ0=k_BT0에서

\[
K_1=K_0,\qquad K_2=\frac{2K_0}{5}(E/\theta_0-5/2)^2\ge0
\]

를 구성한다. T=T0에서 두 kernel 모두 α=K0,β=3θ0K0/2지만 γ는15θ0²K0/4와27θ0²K0/4다. 따라서 고정 bath κ2는 K0와9K0/5다. 유한 동일질량 pair의 두 loss eigenvalue는 (nK0,nK0)와(nK0,7nK0/5)다. 표준 라이브러리 exact rational integration과 Wolfram의 독립 값이 이를 확인했다.

이는 한 온도의 (α,β)만 공급된 adapter의 비식별성을 보이는 구체적 반례다. 모든 T의 정확한 α(T)가 주어진 상황의 불가능성을 주장하지 않는다. 새로운 문헌 전체 strong no-go 성과로 채택하지 않으며 NG6 등 신규성 심사는 열지 않았다. 실용적 결과는 γ 또는 그것을 정하는 검증된 microscopic kernel을 입력으로 요구하는 것이다.

## 7. 실제 유한 표의 계산 형태

CCC H1 CI 표는 입사 electron laboratory energy E_tab[eV],σ[a0²]의87행이며 추가π/multiplicity가 없다. μ=m_e인 heavy fixed-target 진단에서

\[
M_j=\sqrt{\frac{8\,\mathrm{eV_J}}{\pi m_e}}\theta_{\rm eV}^{-3/2}
\int_{13.6058}^{968.61}E_{\rm tab}^{j+1}\sigma(E_{\rm tab})e^{-E_{\rm tab}/\theta_{\rm eV}}dE_{\rm tab}\,\mathrm{eV_J}^{j}.
\tag{7}
\]

양의 endpoint interpolation과 bin별 GL16으로 node/weight/σ/E거듭제곱을 한 번 준비한다. 온도 batch마다 exponential 하나를 네 모멘트에 공유한다. 먼 threshold tail에서는 공통 exponential anchor를 분리해 로그 값과 underflow 여부도 보존한다. 이것은 유한 piecewise-linear model의 수치 근사이며 missing tail=0의 물리적 선언이 아니다. γ를 작은 차분의 α''로 구하는 것보다 양의 직접 moment 적분이 적용 조건과 부호를 분명히 보존한다.

유한질량으로 단순 μ교체하면 E_tab와 E_rel이 섞인다. σ(g)로 동일 speed dependence를 채택하려면 E_tab=m_e g²/2, E_rel=μg²/2, θ_tab=(m_e/μ)k_BT의 사상을 따로 선언해야 하며 finite-mass microscopic source 검증도 남는다. 이번 실제 데이터 계산은 그 승격을 하지 않는다.

## 8. 핵수 변화, 생성물 tensor, 열 장부

REI pin9620e1의 resolved event 코드는 baryon당 Y와 event rate r를 사용한다. 여기서 사용하는 21상태 inventory는 전하중성인 heavy species와 자유전자이며 positron·음이온을 포함하지 않는다. Heavy-species stoichiometry ν, ionic charge q에서 electron source=q·ν r,nucleus source=1·ν r다. 모든 retained 입자가 같은 thermal pool에 있을 때 thermal-particle source=(1+q)·ν r이며, 바리온 밀도 n_b를 곱해 SI volumetric R_part를 얻는다. 별도의 fast-electron population을 유지하면 그 수 source를 thermal count에서 빼야 한다. dEfast 에너지 장부만으로 fast-electron 수 source를 정할 수 없으므로 추가 수 입력을 요구한다. 원자과정에서 핵수가 보존되고 별도 fast population이 없을 때만 thermal R_part=R_e가 된다.

기존 event energy registry Q0+W=dI+dEth+dEfast+dEexc+dEgamma_ret+Egamma_esc+Enu를 그대로 재사용한다. 새 tensor attachment는 **사용자가 공급한** J/event 단위의 net central kinetic second moment를 event당 자료로 받으며 tr(tensor)/2=dEth를 확인한다. 이 tensor가 없으면 unknown이다. Parent-only loss와 net scalar heat를 같은 사건 자료로 붙이지 않는다. Ground CI에서 outgoing electrons가 같은 thermal pool에 남으면 net pool loss는 threshold defect이며 incoming β 전체가 아니다. Nuclear Q를 모두 heat로 넣는 가정도 자동 도입하지 않는다.

일반 속도 frame으로 확장할 때는 mass m_s가 일정한 종의 central source가

\[
C_s=R_{2,s}-u_sF_s^T-F_su_s^T+m_sR_{n,s}u_su_s^T
\tag{8}
\]

임을 사용한다. 탄성 fixed-number 공식에서 마지막 항을 누락하면 birth/death의 boost 변환이 틀린다.

HE33 thermal equation과 연결하면 \(\dot T=-2HT+[2(Q-\sigma:\pi)/(3k_B)-TR_{part}]/n_{part}\)다. Baryon당 thermal energy로부터 T를 복원할 때 particle-count 효과를 에너지 RHS에 중복 넣지 않는다. 실제 coupled gas/metric integration은 이번 실행이 아니다. Isotope quotient의 재사용은 \(R_{full}(Lz)=L R_{red}(z)\)와 thermal/tensor projection도 함께 commute하는 경우에만 허용한다. 온도·UV·D-specific energy 또는 nuclear-transmutation 때문에 그 조건이 깨지면 큰 상태 표현을 유지한다.

## 9. 검증 경로와 적용 결정

Root의 직접 Gaussian 유도, 별도 연구자의 독립 유도, exact rational polynomial check, Wolfram 식검산을 연결했다. 구현 검증에는 함수식 자체를 다시 계산하는 비교와 독립된 Cartesian6D Gauss–Hermite 원적분을 사용한다. Actual CCC moments는 다른 SI-energy adaptive integral 및 GL32와 비교한다. 검증 수치·실행 identity는 RESULTS_KO.md와 receipt에서 보고한다. 잘못된 도구 기호·환경 의존성·숫자 계산 순서의 실패도 각 원본과 함께 보존한다.

원전 맥락은 SOURCES.md, root와 독립 유도의 구체적 일치는 independent_DERIVATION.md, 당시 exact 실행은 independent_CHECKS.json에 있다. 전체 B2와 B1/B3/B4/B5는 GLOBAL_GOAL_DAG.json의 상태를 유지한다.
