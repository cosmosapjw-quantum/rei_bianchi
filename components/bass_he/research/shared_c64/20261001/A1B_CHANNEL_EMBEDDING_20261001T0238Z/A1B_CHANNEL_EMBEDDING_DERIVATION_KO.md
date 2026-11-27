# A1b — 원자 중심 6채널 ETF와 점근 관측량의 명시적 구성

**직접 유도된 결과:** H(1s) 입사와 He⁺(1s,n=2) 출사를 포함하는 유한 R의 구체적 AOCC 기저, 양의 Gram matrix, Hermitian 진폭 방정식의 입력, 물리 projector와 장거리 위상을 정했다. 이로써 A1의 추상 기저 χ를 실제 함수로 바꾸었다. 이는 선택한 6차원 근사의 정의이며, exact R10R molecular g,b가 그 span 안에 있다는 주장은 아니다. 그 projection residual을 버리지 않고 §9의 exact P/Q completion으로 포함한다. 유한 6채널 축약의 정확도는 별도다. 독립 검토 판정은 `RESULT.json`과 `review`가 소유한다. A1b는 `A1_PHYSICAL_CHANNEL_EMBEDDING_SPECIFIED`, parent A1은 prescribed-classical-path의 exact P⊕Q 정식화 범위에서 `FRAME_COMPLETE_CONNECTION_DERIVED`다.

## 1. 고정된 물리 범위와 후보 선택

전자 하나, spinless, 비상대론적 점-Coulomb 전자 문제를 유지한다. 핵 궤적 X_A(t),X_B(t)는 외부 입력이다. A는 초기 수소, B는 He²⁺ projectile이다. k=e²/(4πε₀), κ_A=k, κ_B=2k, 전자 질량 m=m_e, p=−iℏ∇_r로 둔다.

\[
H(t)=\frac{p^2}{2m}-\frac{\kappa_A}{|r-X_A(t)|}
-\frac{\kappa_B}{|r-X_B(t)|},\quad
R=|X_B-X_A|>0,\quad \rho_C=r-X_C,\quad v_C=\dot X_C.
\tag{B.1}
\]

핵 반발 2k/R은 이 전자 Hamiltonian에서 생략한 공통 scalar다. §4에서 이를 복원한 위상 관계를 별도로 확인한다. 원자 orbital에도 m_e를 사용한다. reduced electron–nucleus mass, isotope shift, quantum nuclear motion을 추가하지 않는다. 따라서 H1s–He2의 에너지 축퇴를 명시적으로 유지한다. c, k_B가 등장하지 않는 비상대론 단일전자 문제이며 ℏ는 생략하지 않는다.

후보 중 **원자 중심 AOCC 기저**를 이번 bounded model로 채택한다. 위치·속도가 물리적으로 정해진 각 핵에 ETF를 붙일 수 있고 점근 parent center가 함수 정의에 포함되기 때문이다. MO switching은 spectral/subspace localization을 추가로 정해야 하고, HSCC/Jacobi는 핵 양자운동까지 포함하는 다른 범위다. 후보 채택은 정확도나 효율의 우월성 판정이 아니다. 원전 P01의 AOCC/ETF, P03의 MO ambiguity, P08의 점근 확률 사용은 `source_notes`에 페이지별로 분리했다. 아래 6채널 및 monopole 위상은 원전의 완전한 basis를 재현한 것이 아니라 현재 직접 정한 근사다.

궤적은 우선 각 유한 구간에서 C²이고 R≥R_min>0이라 가정한다. 산란 극한을 논할 때만 추가로 R(t)≥c₀(1+|t|), bounded v_C, |\dot v_C|=O(|t|⁻²)를 요구한다. 직선 궤적 R_vec=b_vec+v_rel t, b>0은 한 예다. 핵 궤적을 선택·비교하는 F1 계산은 수행하지 않았다. b→0에 균일한 bound도 주장하지 않는다.

## 2. 실제 orbital 함수와 6개 채널

각 중심의 a_C=ℏ²/(mκ_C), ρ=|ρ_C|에 대해 real Cartesian hydrogenic orbitals를 사용한다.

\[
\phi_{C,1s}(\rho_C)=\frac{e^{-\rho/a_C}}{\sqrt{\pi a_C^3}},\qquad
\epsilon_{C,n}=-\frac{m\kappa_C^2}{2\hbar^2 n^2},
\tag{B.2}
\]
\[
\phi_{C,2s}=\frac{(2-\rho/a_C)e^{-\rho/(2a_C)}}{4\sqrt{2\pi}\,a_C^{3/2}},
\quad
\phi_{C,2p_i}=\frac{(\rho_C)_i e^{-\rho/(2a_C)}}{4\sqrt{2\pi}\,a_C^{5/2}},
\quad i=x,y,z.
\tag{B.3}
\]

Cartesian axes는 우선 lab에 고정한다. 이 함수들은 정규화되고 같은 중심에서 서로 직교한다. Coulomb cusp를 가진 H² 함수이며, 여러 중심의 Coulomb potential을 곱해도 L²다. 따라서 이번 명시적 함수에는 strong Hχ와 χdot를 사용할 수 있다. A1의 일반 H¹ form-domain 정리에 이 추가 regularity를 소급 적용하지 않는다.

순서는 (A1s;B1s,B2s,B2p_x,B2p_y,B2p_z)다. E_h=mκ_A²/ℏ²를 두면 ε_A1=ε_B2=−E_h/2, ε_B1=−2E_h다. H1s와 He n2는 같은 에너지지만 서로 다른 위치·속도·charge arrangement를 가진다. 에너지 label만으로 parent를 지정하지 않는다. He n2 내부의 U(4) gauge와 2p triplet의 회전도 껍질 projector와 개별 directional amplitude를 구분해야 한다. π 한 성분만 남기지 않고 전체 2p triplet을 포함했으므로 orbital-axis 변경은 해당 3차원 block 안의 unitary basis 변경으로 표현된다. 6은 이 후보의 채널 수이지 수렴한 최소 물리 채널 수가 아니다.

## 3. 고정 lab r 미분을 갖는 ETF

기준시각 t_*를 하나 고정하고 \bar C를 다른 핵이라 하자. 각 orbital에 다음 action phase를 부여한다.

\[
\begin{aligned}
\Phi_{C\nu}(r,t)={}&m v_C(t)\cdot\rho_C
+\frac m2\int_{t_*}^{t}|v_C(s)|^2\,ds
-\epsilon_{C\nu}(t-t_*)\\
&+\kappa_{\bar C}\int_{t_*}^{t}\frac{ds}{R(s)},
\qquad
\chi_{C\nu}=e^{i\Phi_{C\nu}/\hbar}\phi_{C\nu}(\rho_C).
\end{aligned}
\tag{B.4}
\]

모든 항은 action이다. 임의의 finite-R switching이나 fitted parameter가 없다. 마지막 monopole phase는 채널별 시간 gauge이며 공간 span을 바꾸지 않는다. 반면 서로 다른 v_A,v_B의 공간 ETF는 bare 6-orbital span 자체를 일반적으로 바꾼다. 이것을 자동으로 A1의 동일-span gauge라고 부르지 않는다.

상수 v_C에서 첫 두 항은 m v_C·r−m|v_C|²t/2와 시간에 무관한 상수만큼 다르다. 이는 P01 식(3)의 ETF와 일치하는 운동학적 구조다. 원자 에너지 위상은 이미 B.4에 있으므로 K에 ε를 다시 더하지 않는다.

고정된 lab r에서 정확히

\[
\dot\Phi_{C\nu}=m\dot v_C\cdot\rho_C-\frac12m|v_C|^2-\epsilon_{C\nu}
+\frac{\kappa_{\bar C}}R,\qquad
\dot\chi=e^{i\Phi/\hbar}\left(\frac{i\dot\Phi}{\hbar}\phi-v_C\cdot\nabla\phi\right).
\tag{B.5}
\]

고립 원자 eigen-equation을 대입하면 다음 column identity를 얻는다.

\[
(H-i\hbar\partial_t)\chi_{C\nu}
=\mathcal V_C(r,t)\chi_{C\nu},\qquad
\mathcal V_C=-\frac{\kappa_{\bar C}}{|r-X_{\bar C}|}
+\frac{\kappa_{\bar C}}R+m\dot v_C\cdot\rho_C.
\tag{B.6}
\]

부호를 확인하면 H의 boost kinetic 항은 +v_C·p와 +mv_C²/2이고, iℏ∂_t의 translation/phase 항이 이를 상쇄한다. 가속항의 부호는 +m\dot v_C·ρ_C다. 이 항을 빠뜨린 순간, 가속 궤적으로의 일반화는 다른 방정식이 된다. `code/A1B_EXACT_CHECKS.wl`에서 미분 연산을 직접 수행한 residual이 0인지 검사했다. 한 Cartesian 성분의 product-rule identity를 확인한 것이며 3차원에서는 세 성분을 더한다.

## 4. 장거리 위상과 산란 boundary

전자만의 H에서는 다른 핵이 원자 C에 주는 leading scalar가 −κ_\bar C/R다. 이를 B.4에 포함하지 않으면 matrix에 O(1/|t|) diagonal phase가 남아 복소 amplitude의 평범한 극한을 사용할 수 없다. 확률의 수렴과 amplitude의 위상 수렴을 구분해야 한다.

직선 경로에서는

\[
\int_{t_*}^{t}\frac{ds}{\sqrt{b^2+v_{rel}^2s^2}}
=\frac1{v_{rel}}\left[\operatorname{asinh}\frac{v_{rel}t}{b}
-\operatorname{asinh}\frac{v_{rel}t_*}{b}\right].
\tag{B.7}
\]

이를 기존 원문에 있는 식이라고 주장하지 않는다. 미분 residual 0으로 직접 검산한 phase convention이다. 이 위상은 R=0 통과 경로에 그대로 사용할 수 없다.

공통 nuclear repulsion을 복원하려면 전자 해 전체에 exp[−(i/ℏ)∫2k/R dt]를 곱한다. 그러면 A 입사 채널의 monopole phase는 +2k−2k=0, B 출사 채널은 +k−2k=−k가 된다. 이는 중성 H+He²⁺ 입사와 양전하 H⁺+He⁺ 출사의 장거리 Coulomb 부호에 맞는다. 전자 확률에는 공통 scalar가 영향을 주지 않는다. P03의 quantum Coulomb matching과 양립하는 전하 구조지만, 그 논문의 Jacobi reduced mass나 각운동량 matching을 이 전자 궤적 모델로 대체한 것은 아니다.

B.6에서 localized orbital의 크기 안에서는

\[
-\frac{\kappa_{\bar C}}{|r-X_{\bar C}|}+\frac{\kappa_{\bar C}}R
=O(\rho_C/R^2).
\tag{B.8}
\]

정확한 L² bound는 공간을 |ρ_C|≤R/2와 나머지로 나누어 얻는다. 전자는 multipole mean-value bound, 후자는 원자 함수의 exponential tail과 locally square-integrable Coulomb singularity를 사용한다. 따라서 ||\mathcal V_Cχ_Cν||≤C_ν/R²+m|\dot v_C| ||ρ_Cφ_Cν||가 충분히 큰 R에서 성립한다(상수에는 exponentially small remainder를 흡수). §1의 tail 가정 아래 O(t⁻²)다. 수치 상수나 실제 궤적의 tail 오차 예산은 계산하지 않았다.

## 5. Gram matrix의 비특이성과 명시적 직교화

u=χ_A1s, V=[χ_B1s,χ_B2s,χ_B2p_x,χ_B2p_y,χ_B2p_z], X=[u,V], s=V†u로 둔다. B block은 공통 spatial ETF와 orbital별 scalar phase를 가지므로 V†V=I₅다.

\[
S=X^\dagger X=\begin{pmatrix}1&s^\dagger\\s&I_5\end{pmatrix},
\qquad \delta=1-s^\dagger s.
\tag{B.9}
\]

R>0에서는 u가 X_A에서 nonzero 1s cusp를 가지지만 모든 V 열은 그 이웃에서 real analytic하다. 만일 u가 V의 span에 속한다면 이 cusp를 analytic 함수로 표현하게 되어 모순이다. L² 등식이면 연속성에 의해 pointwise 등식이며 같은 모순이 적용된다. B block 자체가 정규직교이므로 6개 열이 선형독립이고 **δ>0**다. λ(S)는 1(중복4),1±||s||다. 이것은 각 R>0의 엄밀한 비특이성이지 전체 R·속도·impact parameter 영역의 conditioning bound가 아니다.

\[
W=\begin{pmatrix}\delta^{-1/2}&0\\-s\delta^{-1/2}&I_5\end{pmatrix},
\quad Y=XW=[w/\sqrt\delta,V],\quad w=u-Vs,
\quad W^\dagger SW=I_6.
\tag{B.10}
\]

W의 시간미분은 B.10에서 직접 구한다. \(d=\sqrt\delta\), \(\dot\delta=-2\operatorname{Re}(s^\dagger\dot s)\), \(\dot d=\dot\delta/(2d)\)이고 \(\dot W\)의 첫 열은 \((-\dot d/d^2,-\dot s/d+s\dot d/d^2)^T\)다. 나머지 열의 미분은 0이다. 미분 조건을 따로 만족시키기 위해 K를 대칭화하지 않는다.

유용한 반례로, 두 중심을 같은 점에 놓고 공통 velocity·scalar phase를 취한 orbital Gram만 보면

\[
s=(16\sqrt2/27,-1/2,0,0,0)^T,\quad
\delta=139/2916>0.
\tag{B.11}
\]

따라서 중심 합체가 이 6개 orbital의 선형종속을 자동으로 뜻하지 않는다. 이것은 R=0 collision model의 승인도 아니며 B.4의 1/R phase를 R=0에서 정의하지 않는다. B.11은 orbital overlap의 별도 제한된 exact check다. 다른 relative boost나 arbitrary time phase를 같은 fixture로 취급하지 않는다.

## 6. 실제 S,h,D와 효율적 계산형

모든 적분은 lab r에 대한 Lebesgue 적분이다.

\[
S_{ab}=\int\chi_a^*\chi_b\,d^3r,\quad
D_{ab}=\int\chi_a^*\dot\chi_b\,d^3r,\quad
h_{ab}=\frac{\hbar^2}{2m}\int\nabla\chi_a^*\!\cdot\nabla\chi_b\,d^3r+
\int\chi_a^*V_{Coul}\chi_b\,d^3r.
\tag{B.12}
\]

이번 orbital에서는 exact atomic eigen-equation 때문에 다음 계산형이 동등하다.

\[
M_{ab}=h_{ab}-i\hbar D_{ab}
=\int\chi_a^*\mathcal V_{C(b)}\chi_b\,d^3r,
\qquad
K=W^\dagger M W-i\hbar W^\dagger S\dot W.
\tag{B.13}
\]

M은 일반적으로 Hermitian이 아니다. Sdot=D+D†이므로 K가 Hermitian이다. B.13은 큰 atomic-energy/translation 항을 계산한 뒤 빼는 대신 잔여 potential을 직접 적분할 수 있게 한다. 이것은 향후 안정적인 구현의 후보 계산형이다. reference는 B.12이고, 실제 quadrature·cusp 처리·두 표현 간 오차·roundoff 증폭은 C1/C2 이후 계약에서 검증해야 한다. 여기서는 해당 공간 적분을 실행하지 않았다.

M의 모든 column은 §4에서 O(t⁻²), s와 sdot는 exponential separation bound를 가지므로 W→I, Wdot→0이며 ||K||는 양쪽 시간 tail에서 적분 가능하다. 유한 구간에서 S>0와 smoothness를 가정했으므로 선택한 6차원 Hermitian ODE는 unitary evolution과 well-defined asymptotic scattering matrix를 갖는다. 이는 **선택된 Galerkin model**의 수학적 well-posedness다. full electronic Hilbert space의 정확 산란이나 핵 양자산란의 완전성은 아니다.

## 7. 출사 projector와 유한 종료시각의 함정

유한 R에서 물리적인 He bound-subspace projector는 P_B=VV†다. H parent projector P_A=uu†와 일반적으로 직교하지 않는다. Ψ_N=u a+V b라 하면

\[
p_B=\langle\Psi_N,P_B\Psi_N\rangle=\|b+s a\|^2,\qquad
p_A=|a+s^\dagger b|^2.
\tag{B.14}
\]

p_A+p_B는 일반적으로 전체 norm이 아니다. 예컨대 Ψ_N=u이면 p_A=1, p_B=||s||²다. 유한 separation에서 이것을 capture 확률 0으로 해석하거나 둘을 배타적인 확률로 합치는 것은 잘못이다.

모형 span의 직교 projector는

\[
P_N=P_B+\frac{|w\rangle\langle w|}{\delta},\quad
p_{A\perp}=\delta |a|^2,\quad
p_B+p_{A\perp}=c^\dagger Sc.
\tag{B.15}
\]

이 직교분할은 He subspace를 그대로 유지하지만 H channel을 w/√δ로 바꾼다. 이를 finite-R의 원래 atomic H1s projector와 같은 것으로 부르지 않는다. χ_A 자체를 유한시각에 초기화하면 orthonormal a-vector는 (√δ,s)^T이지 (1,0,…,0)^T가 아니다.

반면 t→±∞에는 s→0이므로 물리 projector와 coefficient modulus 해석이 일치한다. B.4의 phase convention에서 incoming condition을 c(−∞)=e_A로 정의하고, outgoing B1s와 Bn2 projector로 각각 확률을 얻는다. Bn2는 (2s,2p_x,2p_y,2p_z)의 4차원 projector라 U(4) basis change에 불변이다. 이는 원문 수치표를 새로 합산한 것이 아니라 이론적 관측량 정의다. 유한 T 시작·종료를 쓰는 구현에는 initial-overlap 오차, missing interaction tail, monopole phase가 각각 필요하다. 이번에는 T를 정하거나 오류량을 추정하지 않았다.

P03의 quantum hyperspherical matching에서는 2s/2p 축퇴가 asymptotic dipole channel을 요구하며 해당 계산이 shell sum만 보고한다. 이 사실을 semiclassical fixed-trajectory model의 개별 amplitude 계산 결과와 혼합하지 않는다.

## 8. R10R bare bright 항과 ETF의 정확한 경계

R10R의 g,b는 charge-center origin O_c에서 정의된 **정확한 clamped molecular states**다. 이번 φ_B1s와 φ_B2p_x는 finite R에서 그와 같은 함수가 아니다. 분리 극한의 atom/channel label이 같다는 이유로 등호를 쓰지 않는다. Bare atomic frame X₀를 ETF·time phases 없이 정의하고 그 orthonormal basis Y₀, projector P₀를 사용하자.

\[
g=Y_0 z_g+r_g,\quad b=Y_0 z_b+r_b,
\quad z_j=Y_0^\dagger j,\quad r_j=(1-P_0)j.
\tag{B.16}
\]
\[
\begin{aligned}
\langle g,L_{O_c}b\rangle={}&z_g^\dagger(Y_0^\dagger L_{O_c}Y_0)z_b
+\langle r_g,L_{O_c}Y_0z_b\rangle\\
&+\langle Y_0z_g,L_{O_c}r_b\rangle+\langle r_g,L_{O_c}r_b\rangle.
\end{aligned}
\tag{B.17}
\]

R10R의 L-domain 조건과 atomic functions의 regularity 아래 이 분해는 의미가 있다. 아직 r_g,r_b를 계산·제어하지 않았으며, L이 unbounded이므로 L² overlap만으로 세 remainder를 제한할 수 없다. R10R의 exact nonzero theorem은 첫 projected term만의 nonzero나 이번 dressed K의 nonzero를 증명하지 않는다. 이것이 6채널만으로 축약할 때 남는 구체적인 model-reduction gap이다. §9에서는 이 remainder를 생략하지 않는 exact complement dynamics를 정의한다.

그럼에도 translation이 왜 중요했는지는 정확한 atomic identity로 보인다. 같은 중심 B의 서로 다른 orthogonal orbitals g₀,b₀에 대해, 모든 행렬요소에 동일한 scalar energy-phase factor를 포함하면

\[
h_{g_0b_0}=v_B\cdot p_{g_0b_0}+(V_A)_{g_0b_0},\qquad
-i\hbar D_{g_0b_0}=m\dot v_B\cdot r_{g_0b_0}-v_B\cdot p_{g_0b_0},
\tag{B.18}
\]
\[
M_{g_0b_0}=(V_A)_{g_0b_0}+m\dot v_B\cdot r_{g_0b_0}.
\tag{B.19}
\]

운동량 coupling은 **정확히 상쇄**된다. intrinsic L_B의 1s–2p 행렬요소는 0인 반면 다른 origin에서는

\[
L_{O_c}=L_B+(X_B-O_c)\times p,\qquad
\langle B1s|\rho_x|B2p_x\rangle=\frac{64\sqrt2}{243}a_A,
\tag{B.20}
\]
\[
\langle B1s|p_x|B2p_x\rangle=
\frac{i m}{\hbar}(\epsilon_{B1}-\epsilon_{B2})
\langle B1s|\rho_x|B2p_x\rangle.
\tag{B.21}
\]

A→B 축을 z로 놓으면 X_B−O_c=(R/3)e_z여서 bare origin-lever part의 Ly 행렬요소는 nonzero이고 R에 비례한다. 이 bare 사실과 B.18의 상쇄는 모순이 아니다. body rotation·origin translation·ETF를 동시에 변환해야 같은 물리 basis를 나타낸다. 이는 exact molecular R10R 행렬요소 전체가 상쇄된다는 증명이 아니며 그 finite-R deformation은 B.17의 residual이 소유한다.

Lab에 고정한 p triplet을 순간 핵축에 맞춰 회전하면 같은 triplet span 안의 gauge connection이 추가된다. 한 transverse component의 static potential selection rule만으로 경로 전체의 capture amplitude가 0이라고 결론 낼 수 없다. 다른 p 성분과 time ordering이 존재한다. 외부 원자의 potential와 acceleration이 남는 B.19도 양의 독립 rate가 아니다.

Q12에 대해서는 probability에서 phase를 역복원하지 않는다. 이 후보에서는 동일 H와 χ로부터 M,K를 계산하여 radial·rotation·translation 효과를 한 번 포함한다. 이전 hidden-crossing Q12 probability를 별도 transition operator로 더하지 않는다. Q12 branch와 exact BO channels의 정량적 대응은 아직 미완료다. CPC의 ω와 현재 active θdot orientation도 새로 해결했다고 주장하지 않는다.

## 9. 정확한 P/Q 보강: 원계약의 R10R sector를 보존

6채널만을 full model로 채택하면 B.17의 세 remainder가 generator에서 빠진다. 그 상태를 원계약 A1의 완료로 판정하지 않는다. 이 문제는 수치 overlap을 먼저 계산해야 해결되는 문제가 아니다. **정확한 complement를 유지하는 보강 정식화**를 지금 명시하고, 6채널 Galerkin은 그 뒤의 별도 근사로 정의한다.

Y=XW, P=YY†, Q=1−P에 대해 전체 전자 상태를

\[
\Psi=Y a+\eta,\qquad Y^\dagger\eta=0,
\qquad F=HY-i\hbar\dot Y,
\quad K_{PP}=Y^\dagger HY-i\hbar Y^\dagger\dot Y
\tag{B.22}
\]

로 분해한다. Y의 열은 H², Ydot는 H¹이므로 F의 각 열은 L²다. 따라서 F는 C⁶→L²의 유계 finite-rank map이다. 미분한 orthogonality 조건 Y†ηdot=−Ydot†η를 함께 쓰면 정확히

\[
i\hbar\dot a=K_{PP}a+F^\dagger\eta,
\tag{B.23}
\]
\[
i\hbar Q\dot\eta=QHQ\eta+QFa,
\qquad
 i\hbar\dot\eta=(QHQ-i\hbar\dot P)\eta+QFa.
\tag{B.24}
\]

마지막 식의 −iℏPdot는 시간에 따라 움직이는 Q 공간의 제약을 보존한다. 이를 버리면 full-space TDSE와 동등하지 않다. η의 strong Hη 표현에는 η∈D(H) 등 필요한 추가 domain 조건을 요구하고, 일반 form-domain 해에는 대응하는 weak form으로 해석한다. U_*의 H² 보존은 주장하지 않는다. 시간의존 Coulomb Hamiltonian의 통상적인 unitary well-posedness 및 아래 공통 form-domain regularity를 전제로 하며, 본 연구가 새로운 다입자 산란 존재 정리를 증명한다는 뜻은 아니다.

B.23–24에서 ||a||²의 변화는 (2/ℏ)Im(a†F†η), ||η||²의 변화는 그 음수다. 따라서 full norm을 보존하면서 P와 Q 사이의 coherent probability exchange를 포함한다. η=0를 설정하고 QFa를 버리는 것이 바로 §6의 Galerkin 근사다. Q의 작용이 실제로 0임을 보인 결과가 아니다.

### 9.1 하나의 명시적 unitary 완성 기저

A_Y=Y†Ydot는 anti-Hermitian이다. 다음 유계 anti-Hermitian operator를 정의한다.

\[
\Gamma=[\dot P,P]+Y A_Y Y^\dagger,
\qquad \Gamma^\dagger=-\Gamma,
\qquad \Gamma Y=\dot Y,\qquad Q\Gamma Q=0.
\tag{B.25}
\]

U_*(t_*)=I, Udot_*=ΓU_*의 해는 unitary이고 U_*(t)Y(t_*)=Y(t)다. Q_*=Q(t_*)와 Z(t)=U_*(t)|_{Ran Q_*}를 두면

\[
\mathcal J(t):\mathbb C^6\oplus Ran Q_*\longrightarrow L^2,
\quad \mathcal J(a,\zeta)=Ya+Z\zeta
\tag{B.26}
\]

는 onto unitary map이다. 별도의 fitted ETF나 임의 complementary switching은 넣지 않았다. Y의 중심별 ETF를 유지하고 나머지 공간을 위 parallel transport로 완성했다. 필요하다면 Ran Q_*의 임의의 고정 정규직교 기저를 사용하여 countably infinite amplitude representation을 얻는다. Q 안의 unitary 선택은 표현 gauge이며 full Ψ를 바꾸지 않는다.

Y,Ydot∈H¹이고 유한 구간의 해당 norm이 유계이면 Γ는 H¹에도 유계로 작용하여 U_*가 Coulomb form domain을 보존한다. K_QQ는 q_t(Zξ,Zζ)의 닫힌 semibounded form으로 정의한다. Z†Zdot=0이므로 그 block의 parallel-transport connection은 0이다. 다른 block은

\[
i\hbar\partial_t\binom a\zeta
=\mathbb K\binom a\zeta,
\quad
\mathbb K=
\begin{pmatrix}
K_{PP}&K_{PQ}\\K_{QP}&K_{QQ}
\end{pmatrix},
\tag{B.27}
\]
\[
K_{QP}=Z^\dagger F,
\qquad K_{PQ}=F^\dagger Z=K_{QP}^\dagger,
\qquad K_{QQ}=Z^\dagger H Z\quad\text{(quadratic form)}.
\tag{B.28}
\]

K_PP는 앞서 유도한 동일한 6채널 Hermitian matrix다. Off-diagonal blocks는 유계이며 서로 adjoint다. K_QQ의 자기수반 form realization과 적절한 시간 regularity 아래 𝕂는 자기수반 coupled generator다. 이 식은 6개 orbital을 모든 exact state와 동일시하지 않으면서도 전체 전자 Hilbert space를 유지한다. Q의 미지 수치 자료는 정식화의 누락이 아니라 후속 계산 대상이다.

### 9.2 R10R와 전체 frame connection의 정확한 위치

A1의 active origin/rotation map 𝒰_{O,Q}를 사용하여 𝒥_b=𝒰†𝒥라 두면, 충분한 domain을 가진 상태 또는 공통 core 위에서

\[
\mathbb K=
\mathcal J_b^\dagger
\left(H_{body}-V\cdot p-\Omega\cdot L\right)\mathcal J_b
-i\hbar\mathcal J_b^\dagger\dot{\mathcal J}_b.
\tag{B.29}
\]

Lab의 B.27과 같은 generator의 다른 좌표 표현이다. 회전 표현의 L은 unbounded이므로 이 body 식의 domain을 모든 H¹로 넓혀 주장하지 않는다. 물리 기준은 lab의 unitary pullback이며, R10R의 exponentially localized bound states와 atomic trial states처럼 필요한 L-domain을 만족하는 상태에서 행렬요소를 취한다. 원점·회전·ETF·internal-energy·non-Abelian connection은 𝒥_b와 그 미분 안에서 함께 변환된다. 기존 A1의 원점/boost covariance 유도를 재사용한다.

정확한 R10R body states g,b의 전체 좌표를 𝔤=𝒥_b†g, 𝔟=𝒥_b†b라 하면

\[
\langle\mathfrak g,(\mathcal J_b^\dagger L_y\mathcal J_b)\mathfrak b\rangle
=\langle g,L_y b\rangle
=-i\hbar\frac{C_RT_R}{\Delta_R}\ne0.
\tag{B.30}
\]

𝒥_b가 onto이므로 P–P, P–Q, Q–P, Q–Q 네 block을 모두 포함한 **정확한 identity**다. 이 회전 operator contribution의 matrix element는 +iℏθdot C_RT_R/Δ_R이며 A1에서 정한 부호와 같다. 이것만이 전체 effective matrix element라는 주장은 아니다. 다른 connection 항 및 그 간섭이 B.29에 한 번 포함된다. Radial Q12와 관련된 derivative amplitude도 같은 full basis/BO basis transformation에서 계산하며, 옛 probability를 독립 rate로 추가하지 않는다.

B.17의 remainder를 0으로 놓지 않았으므로 원래 exact g,b theorem을 다른 유한 원자 상태에 대입하는 오류를 피한다. 이로써 **원계약이 요구하는 exact sector를 포함한 하나의 coherent generator가 정의되었다.** R10R의 nonzero와 observable capture의 nonzero 또는 수치 크기는 여전히 다른 주장이다. CPC의 source-specific ω adapter는 이 명시적 active-frame 구현에 사용하지 않았고 미확정으로 남긴다. 해당 adapter를 후속 구현에 사용하려면 별도로 검증해야 한다.

### 9.3 Q 제거의 정확한 대가와 근사 계약

Q block propagator U_Q(t,s)가 정의되는 regularity 범위에서

\[
\zeta(t)=U_Q(t,t_0)\zeta_0
-\frac{i}{\hbar}\int_{t_0}^{t}U_Q(t,s)K_{QP}(s)a(s)\,ds.
\tag{B.31}
\]

따라서 a의 정확한 방정식에는

\[
\begin{aligned}
i\hbar\dot a(t)={}&K_{PP}(t)a(t)+K_{PQ}(t)U_Q(t,t_0)\zeta_0\\
&-\frac{i}{\hbar}\int_{t_0}^{t}
K_{PQ}(t)U_Q(t,s)K_{QP}(s)a(s)\,ds
\end{aligned}
\tag{B.32}
\]

가 들어간다. Kernel의 단위는 energy²이며 dt/ℏ를 곱하면 energy가 된다. η₀=0이어도 memory/backcoupling 항은 일반적으로 남는다. 이 항을 단일 양의 rate, irreversible upper-shell sink 또는 ad hoc incoherent probability로 바꾸지 않는다. 6채널 근사는 initial complement와 이 memory를 생략한다고 명시한다. 누락량·채널 확대·continuum은 C1/C2/E1/E2에서 계산해야 하며 아직 작다고 판정하지 않는다.

## 10. 검증 범위와 다음 연구

선택한 finite model의 omitted-space residual은 Q_N[\mathcal V_{C(1)}χ₁,…,\mathcal V_{C(6)}χ₆]c다. Exact propagator 및 domain 조건 아래 Duhamel bound는 초기 오차에 ℏ⁻¹∫||residual||dt를 더한다. 이 적분의 finite-R 크기를 계산하지 않았으므로 정확도 인증은 없다. §9의 augmentation은 잔차를 숨기는 대신 해당 sector를 동역학에 명시적으로 복원한다.

신규 검증은 exact CAS 한 회, 8개 Gram/projector 구현 검사와 별도의 P/Q completion matrix fixture다. P/Q fixture는 Γ의 anti-Hermiticity, ΓY=Ydot, QΓQ=0, full block의 Hermiticity와 norm exchange를 확인한다. 유한 행렬 fixture를 물리적 complement 계산으로 세지 않는다. 기존 A1 12개 tests와 R10R/legacy scientific suites는 재실행하지 않았다.

독립 검토에서 §9의 정확한 보강을 확인했다. 이에 따라 A1의 **정식화**를 명시한 full P⊕Q 범위에서 완료로 판정하고 원래 DAG의 다음 단일 node A2를 진행 가능 상태로 둔다. C1은 A2가 아직 미완료이므로 대기다. 6D Galerkin scattering matrix의 unitarity는 그 근사의 성질이다. Full P/Q evolution의 선택된 6채널 확률 합이 1이라거나 Q continuum의 점근 완비성을 증명했다고 주장하지 않는다. Six-channel model accuracy, actual BO projection coefficients, finite-R coupling magnitude, continuum completeness, collision propagation 및 benchmark agreement는 그 판정에 포함하지 않는다. 실제 electronic eigensolve, Coulomb spatial quadrature, collision propagation, cross-section integration, benchmark comparison, Eq55는 모두 NOT_RUN이다. Scientific promotion과 production 변경은 허용하지 않는다.
