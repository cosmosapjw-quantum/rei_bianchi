# A2 small-R: 정확한 molecular bright coupling의 첫 항

이 문서는 A2의 소-R 부분에 대한 **직접 유도(author proof)**다. 유한 원자 기저를 정확한 분자 상태로 대체하지 않는다. 독립 검토의 admission은 별도 review가 소유한다. 실제 molecular eigensolve, Coulomb 수치 적분, collision propagation은 수행하지 않았다. 기존 CAS와 tests도 재실행하지 않았다.

## 1. 결론, 상태와 convention

R10Q/R10R의 정확한 상태와 charge-center 원점을 그대로 쓴다. κ₁=k, κ₂=2k, k=e²/(4πε₀), m=mₑ, K=κ₁+κ₂=3k이며

\[
z_1=-\frac{\kappa_2}{K}R=-\frac23R,
\qquad z_2=\frac{\kappa_1}{K}R=\frac13R,
\]
\[
H_R=-\frac{\hbar^2}{2m}\Delta
-\frac{\kappa_1}{|\mathbf r-z_1\mathbf e_z|}
-\frac{\kappa_2}{|\mathbf r-z_2\mathbf e_z|},
\quad L_y=-i\hbar(z\partial_x-x\partial_z).
\tag{S.1}
\]

g_R는 normalized lowest m=0 state, b_R는 normalized lowest |m|=1의 real cosφ bright state다. R10R의 양의 meridional phase를 사용한다. r은 charge center에서 측정한다. 핵 repulsion은 공통 scalar라 제외했다. g_R,b_R는 R>0에서 정확한 H_R의 eigenstates다.

a_A=ℏ²/(mk), a_U=ℏ²/(mK)=a_A/3, ε=R/a_A, E_A=mk²/ℏ²를 정의한다. 아래 증명이 주는 결론은

\[
\boxed{\displaystyle
\langle g_R,L_y b_R\rangle
=-i\hbar\frac{4\sqrt2}{15}\epsilon^3
+O(\hbar\epsilon^{7/2}),\qquad \epsilon\downarrow0.}
\tag{S.2}
\]

O 상수와 충분히 작은 ε₀>0는 고정된 전자 Hamiltonian/sector에서 존재한다. 계산된 numerical constant나 전체 R 구간의 오차 certificate는 아니다. R^{7/2}는 아래 Sobolev 추정이 주는 안전한 remainder이며 optimal expansion order라는 주장은 없다. 가능한 R⁴ 또는 logarithmic 항의 계수는 이 문서에서 구하지 않는다.

이 결과는 **bare unboosted charge-center matrix element**에 대한 것이다. Full frame/ETF-completed generator 전체의 leading coefficient, capture probability, collision cross section을 뜻하지 않는다. 다만 A1b B.30의 full P⊕Q unitary dictionary를 통해 동일한 회전 operator contribution을 보존한다.

## 2. 외부 multipole만으로 첫 항을 얻을 수 없는 이유

H_U=−ℏ²Δ/(2m)−K/r, W_R=H_R−H_U를 둔다. α₁=−κ₂/K, α₂=κ₁/K, M_j=Σ_Cκ_Cα_C^j이면 M₁=0,

\[
M_2=\frac{\kappa_1\kappa_2}{K},\qquad
M_3=\frac{\kappa_1\kappa_2(\kappa_1-\kappa_2)}{K^2}
=-\frac{2k}{9}.
\tag{S.3}
\]

고정 r>max|z_C|에서만 ordinary multipole series를 쓰면

\[
W_R=-\frac{M_2R^2}{r^3}P_2(\cos\theta)
-\frac{M_3R^3}{r^4}P_3(\cos\theta)+\cdots .
\tag{S.4}
\]

Quadrupole은 parity-even이고 외부 octupole의 angular rank는 3이다. 따라서 외부 rank-3 항을 UA 1s↔2p에 그냥 적분하면 0이다. 그러나 (S.4)는 두 핵과 UA cusp를 포함하는 r=O(R)에서 유효하지 않다. 그 영역을 버리거나 multipole을 원점까지 연장하는 것은 leading R³ contact contribution을 놓친다.

아래에서는 distribution의 고차 Taylor 급수를 eigenfunction에 직접 대입하지 않는다. 정확한 shifted-Coulomb integral로 coefficient를 계산하고, 별도의 negative-Sobolev resolvent estimate로 정확한 molecular state와의 차이를 제어한다.

## 3. 정확한 UA transition-density integral

고정 UA eigenfunctions를 comparison vectors로 정의한다.

\[
g_0=N_s e^{-r/a_U},\quad
p_{z0}=N_pz e^{-r/(2a_U)},\quad b_0=p_{x0}=N_px e^{-r/(2a_U)},
\]
\[
N_s=\frac1{\sqrt{\pi a_U^3}},\qquad
N_p=\frac1{4\sqrt{2\pi}\,a_U^{5/2}},\qquad
\lambda=\frac3{2a_U}.
\tag{S.5}
\]

E₁⁰=−K/(2a_U), E₂⁰=−K/(8a_U), Δ_U=E₂⁰−E₁⁰=3K/(8a_U)=27E_A/8. L_y g₀=0, L_y b₀=−iℏ p_z₀이다.

실수 d에 대해

\[
F(d)=\int_{\mathbb R^3}\frac{z e^{-\lambda r}}{|\mathbf r-d\mathbf e_z|}\,d^3r
\tag{S.6}
\]

를 정의한다. Density의 angular content가 정확히 l=1이므로 Coulomb addition theorem의 l=1 항만 남는다. d>0일 때 원점을 포함한 정확한 적분은

\[
F(d)=\frac{4\pi}{3}\left[
\frac1{d^2}\int_0^d r^4e^{-\lambda r}\,dr
+d\int_d^\infty r e^{-\lambda r}\,dr\right].
\tag{S.7}
\]

d<0에서는 F(−d)=−F(d)다. 이는 exact angular reduction이지 exterior series의 부적절한 연장이 아니다. 두 radial integral의 작은-d 전개를 합하면

\[
F(d)=\frac{4\pi d}{3\lambda^2}
-\frac{2\pi d^3}{5}
+\frac{2\pi\lambda}{9}d|d|^3+O(|d|^5).
\tag{S.8}
\]

R³ 계수는 바깥 적분 하한의 보정 −d³/2와 안쪽 적분 +d³/5의 합에서 생긴다. 따라서 내부 영역을 포함하는 것이 실제로 결정적이다.

UA central potential의 s↔p matrix element는 0이고 Σκ_C z_C=0이므로

\[
\begin{aligned}
V_{sp}(R)&=\langle p_{z0},W_Rg_0\rangle
=-N_sN_p\sum_C\kappa_CF(z_C)\\
&=\frac{2\pi}{5}N_sN_pM_3R^3+O(E_A\epsilon^4)\\
&=\frac{M_3R^3}{10\sqrt2\,a_U^4}+O(E_A\epsilon^4)
=-\frac9{5\sqrt2}E_A\epsilon^3+O(E_A\epsilon^4).
\end{aligned}
\tag{S.9}
\]

여기까지는 정확한 atomic comparison-state integral이다. 이 식만으로 molecular asymptotic을 선언하지 않는다. 다음 절이 그 연결에 필요한 remainder를 증명한다.

## 4. 공통 domain과 작은-R resolvent 제어

이 절의 O 표기는 고정 길이 a_A, 에너지 E_A로 무차원화한 뒤 쓴다. 따라서 H^s norm의 차원 혼합은 없다. ℏ가 있는 angular momentum bound는 별도로 표시한다.

### 4.1 Coulomb graph bounds와 고립된 sector projector

Translated Hardy inequality와 Fourier interpolation으로 모든 핵 위치에 독립적으로

\[
\|u/|\mathbf r-\mathbf a|\|_2\le2\|\nabla u\|_2
\le\eta\|\Delta u\|_2+C_\eta\|u\|_2
\tag{S.10}
\]

가 성립한다. 따라서 H_R는 H²(R³)를 공통 operator domain으로 가지며, 충분히 작은 R에서 graph norm과 H² norm의 동등성 상수는 균일하게 잡힌다. 이는 H_R가 R에 대해 H²→L² analytic이라는 뜻은 아니다.

W_R=R^{-1}w(r/R)이고, 고정 w는 핵 및 원점에서 locally square-integrable Coulomb singularities를 가지며 infinity에서는 dipole cancellation 때문에 O(|r|^{-3})다. 그러므로

\[
\|W_R\|_2=O(R^{1/2}),\qquad
\|W_Ru\|_2\le\|W_R\|_2\|u\|_\infty
\le CR^{1/2}\|u\|_{H^2}.
\tag{S.11}
\]

Resolvent identity/Neumann argument는 H_R→H_U의 norm-resolvent convergence를 준다. UA ground eigenvalue를 둘러싼 고정 contour와, real cosφ |m|=1 sector의 UA lowest eigenvalue E₂⁰를 둘러싼 고정 contour를 택할 수 있다. 각 sector projector는 rank one이다. Σ,m=0의 n=2 degeneracy를 artificial individual denominator로 분해하지 않는다.

각 contour에서 resolvent는 L²→H²로 균일 유계이고, adjoint/duality로 H^{-2}→L²에도 균일 유계다. g_R,b_R의 H² norm도 (S.10)과 bounded eigenvalues에서 균일하게 제어된다. Ground reduced resolvent

\[
S_R=(1-|g_R\rangle\langle g_R|)(H_R-E_g(R))^{-1}
(1-|g_R\rangle\langle g_R|)
\tag{S.12}
\]

는 ground orthogonal complement에서 정의하며, 작은 R의 유지된 spectral gap 때문에 역시 H^{-2}→L²로 균일 유계다. H^{-2}에서 rank-one projection은 g_R∈H²와의 dual pairing으로 정의한다.

### 4.2 Charge-center cancellation을 보존하는 H^{-2} bound

Fourier convention의 고정 상수를 제외하면

\[
\widehat W_R(\mathbf q)=\frac{4\pi}{q^2}A(Rq_z),\qquad
A(s)=K-\sum_C\kappa_Ce^{-i\alpha_Cs}.
\tag{S.13}
\]

A(0)=A′(0)=0이고

\[
|A(s)|\le C\min(|s|^2,1),\qquad
|A'(s)|\le C\min(|s|,1).
\tag{S.14}
\]

따라서 |Ŵ_R|≤C min(R²,q^{-2}). H^{-2} norm의 radial integral을 q<1, 1<q<R^{-1}, q>R^{-1}로 나누면

\[
\|W_R\|_{H^{-2}}^2
\le C\int_0^\infty\frac{q^2\min(R^4,q^{-4})}{(1+q^2)^2}\,dq
\le CR^4.
\tag{S.15}
\]

L_y의 Fourier 작용도 angular derivative다. q^{-2}의 angular derivative는 0이고 A에만 작용하므로

\[
|\widehat{L_yW_R}(\mathbf q)|
\le C\hbar\frac{R|q_x|}{q^2}|A'(Rq_z)|
\le C\hbar\min(R^2,R/q).
\tag{S.16}
\]

동일한 radial split으로

\[
\boxed{\|W_R\|_{H^{-2}}=O(R^2),\qquad
\|L_yW_R\|_{H^{-2}}=O(\hbar R^2).}
\tag{S.17}
\]

원점의 contact contribution을 버리지 않는 distribution norm 추정이다. W_R 또는 L_yW_R의 pointwise R² Taylor remainder를 전공간에서 주장하지 않는다.

### 4.3 정확한 eigenvectors의 L² 차이

3차원에서 H²는 multiplication algebra다. 따라서 f∈H²는 H²의 bounded multiplier이고 duality로

\[
\|fT\|_{H^{-2}}\le C\|f\|_{H^2}\|T\|_{H^{-2}}
\tag{S.18}
\]

가 성립한다. 이 부등식은 product rule, H²↪L∞, ∇f∈L⁴의 Sobolev interpolation으로도 직접 얻는다. f=g₀,b₀를 쓰면 ||W_Rf||_{H^{-2}}=O(R²)다.

Contour projector identity를 해당 UA eigenvector에 작용시키면 오른쪽 H_U resolvent는 scalar가 된다. (S.15), (S.18), uniform H^{-2}→L² resolvent bound를 사용하여

\[
\|(P_R-P_0)g_0\|_2=O(R^2),\qquad
\|(\Pi_R-\Pi_0)b_0\|_2=O(R^2).
\tag{S.19}
\]

여기서 P는 full ground projector, Π는 fixed bright |m|=1 sector의 lowest projector다. Positive overlap으로 phase를 고정하고 normalize하면

\[
\|g_R-g_0\|_2=O(R^2),\qquad
\|b_R-b_0\|_2=O(R^2).
\tag{S.20}
\]

이것은 eigenstates의 강한 Sobolev Taylor expansion이 아니며, finite atomic span에 정확한 eigenstate가 들어간다는 주장도 아니다.

### 4.4 Unbounded L_y의 필요한 추가 제어

L² eigenvector convergence만으로 L_y matrix element의 convergence를 추론하지 않는다. Ground eigenstate는 음의 에너지가 0에서 균일하게 떨어져 있으며 nuclei가 bounded region에 있다. 바깥 영역에서 V_R−E_g≥c>0이고, bounded truncated exponential weight를 eigen-equation에 넣는 weighted energy identity

\[
\frac{\hbar^2}{2m}\|\nabla(wg_R)\|_2^2
+\int(V_R-E_g)|wg_R|^2
=\frac{\hbar^2}{2m}\int|\nabla w|^2|g_R|^2
\tag{S.21}
\]

를 사용하면 충분히 작은 고정 exponential weight의 함수/gradient 적분이 유한하다. 안쪽 cutoff 항은 bounded H¹ norm으로 제어한다. 따라서 r∇g_R∈L², L_yg_R∈L²가 우선 존재한다. 아래의 R 차수 추정은 이 존재성만 사용하며 weighted perturbation series에 의존하지 않는다.

Exact distribution commutator는

\[
(H_R-E_g)L_yg_R=-(L_yW_R)g_R.
\tag{S.22}
\]

Real g_R에 대해 ⟨g_R,L_yg_R⟩=0이다. Uniform H² norm, (S.17)–(S.18), reduced resolvent를 적용하면

\[
L_yg_R=-S_R[(L_yW_R)g_R],\qquad
\boxed{\|L_yg_R\|_2=O(\hbar R^2).}
\tag{S.23}
\]

분포 방정식은 공통 H² test domain의 dual identity로 읽는다. g_R(L_yW_R)는 H^{-2}에서 well-defined다. L_yg_R∈D(H_R)라는 불필요한 강한 premise는 사용하지 않는다.

## 5. 정확한 molecular coefficient를 고정하는 projection identity

필요한 마지막 추정은 unusually weak한 remainder만으로 충분하다. p_z₀(r)=N_p z e^{-r/(2a_U)}와 W_R=R^{-1}w(r/R)를 이용하면

\[
\|W_Rp_{z0}\|_2^2
\le CR^3\int_{\mathbb R^3}|w(\mathbf y)|^2|\mathbf y|^2\,d^3y
=O(R^3).
\tag{S.24}
\]

이 적분은 infinity에서 w=O(y^{-3}), 각 Coulomb singularity에서는 locally L²라는 사실로 유한하다. 따라서 (S.20)에서

\[
|\langle p_{z0},W_R(g_R-g_0)\rangle|
\le\|W_Rp_{z0}\|_2\|g_R-g_0\|_2
=O(R^{7/2})=o(R^3).
\tag{S.25}
\]

정확한 ground eigenequation을 고정된 UA vector p_z₀에 투영하면

\[
(E_g(R)-E_2^0)\langle p_{z0},g_R\rangle
=V_{sp}(R)+O(E_A\epsilon^{7/2}).
\tag{S.26}
\]

E_g(R)→E₁⁰이며 denominator는 ground-to-n=2 gap이다. 더 구체적으로 UA ground density의 spherical exact integral은 ⟨g₀,W_Rg₀⟩=O(E_Aε²)를 주고, ||W_Rg₀||₂=O(E_Aε^{1/2})와 (S.20)의 차이 항은 O(E_Aε^{5/2})이므로 E_g−E₁⁰=O(E_Aε²)다. 따라서 (S.26)의 분모 보정은 R³ leading coefficient를 바꾸지 않는다.

이제 L_y의 self-adjoint pairing과 (S.20), (S.23)을 쓴다.

\[
\begin{aligned}
\langle g_R,L_yb_R\rangle
&=-i\hbar\langle g_R,p_{z0}\rangle
+\langle L_yg_R,b_R-b_0\rangle,\\
|\langle L_yg_R,b_R-b_0\rangle|&=O(\hbar\epsilon^4).
\end{aligned}
\tag{S.27}
\]

Real phase에서는 (S.26)의 overlap이 real이다. 그러므로

\[
\begin{aligned}
\langle g_R,L_yb_R\rangle
&=\frac{i\hbar}{\Delta_U}\frac{M_3R^3}{10\sqrt2a_U^4}
+O(\hbar\epsilon^{7/2})\\
&=i\hbar\frac4{15\sqrt2}\frac{M_3}{K}
\left(\frac R{a_U}\right)^3+O(\hbar\epsilon^{7/2})\\
&=-i\hbar\frac{4\sqrt2}{15}\left(\frac R{a_A}\right)^3
+O(\hbar\epsilon^{7/2}).
\end{aligned}
\tag{S.28}
\]

이로써 (S.9)의 atomic calculation과 정확한 molecular conclusion을 잇는 누락 가능 항 두 개를 각각 o(R³)로 통제했다. 단순한 first-order perturbation coefficient의 추측으로 멈추지 않는다.

## 6. 퇴화, 부호, 단위와 경계 검사

1. b_R는 axisymmetry가 보존하는 fixed real cosφ |m|=1 sector에서 rank-one lowest eigenprojector로 정의한다. UA n=2 full shell의 2s 및 p_z degeneracy를 임의로 분리한 denominator를 쓰지 않았다. (S.26)은 고정 test vector에 대한 exact eigen-equation이며 denominator는 E₁⁰−E₂⁰≠0이다.
2. M₃<0이므로 (S.28)의 허수부는 음수다. 모든 fixed R>0에서 Im⟨g,L_yb⟩<0이라는 R10R theorem과 일치한다. 임의 rephasing은 phase factor를 바꾸지만 cubic zero/nonzero 구조를 바꾸지 않는다.
3. R=0에서는 L이 l을 보존하여 정확히 0이다. 앞 식의 ℏ×dimensionless 구조는 angular momentum 단위와 일치한다. E_A, a_A, ℏ,m,k를 삭제하지 않았다.
4. κ₁=κ₂이면 reflection으로 coupling이 모든 R에서 정확히 0이다. 일반식의 M₃=0은 이 경계와 일치하나, M₃=0만으로 더 높은 order를 예측하지 않는다. 한 charge가 0인 경우도 charge center가 유일한 Coulomb 중심이 되어 coupling은 0이다.
5. 극한은 static snapshot R↓0이다. A1b의 scattering-channel 1/R phase를 R=0까지 연속 연장하지 않으며 핵충돌 경로의 R=0 통과도 다루지 않는다.
6. Uniform bound의 구간은 0<R≤R₀인 sufficiently small neighborhood다. R₀/상수의 numerical enclosure, finite-R magnitude와 full scattering error budget은 NOT_RUN이다.

## 7. Frame/ETF 및 P⊕Q와의 연결 한계

A1b B.30에서 J_b는 onto이고 g,b의 full coordinates를 쓰므로

\[
\langle\mathfrak g,J_b^\dagger L_yJ_b\mathfrak b\rangle
=-i\hbar\frac{4\sqrt2}{15}\epsilon^3+O(\hbar\epsilon^{7/2})
\tag{S.29}
\]

를 그대로 대입할 수 있다. 이는 P–P만의 matrix element가 아니라 P–P/P–Q/Q–P/Q–Q 전부의 합이다. Rotation term −θ̇L_y의 해당 contribution은 +iℏθ̇(4√2/15)ε³+O(ℏ|θ̇|ε^{7/2})이며, θ̇가 bounded라는 경로 조건을 덧붙이면 cubic estimate가 시간 generator에서도 유지된다.

그러나 −V·p, ETF/internal phase derivative, other connections 및 Q memory/backcoupling은 함께 존재한다. 이 bare cubic term만으로 전체 effective off-diagonal coefficient의 leading power/nonzero를 확정하지 않는다. Total generator entry는 basis/time-gauge에도 의존한다. 가속도·회전속도·time gauge의 R scaling을 지정하지 않으면 하나의 universal small-R completed coefficient는 정의되지 않는다. 이 한계는 small-R bare theorem의 unresolved proof gap과 다르다.

검증 상태: (S.7)–(S.9)의 exact integral과 (S.10)–(S.28)의 functional estimates는 직접 유도다. 본 author note가 CAS 실행이나 독립 검토 PASS를 자체 선언하지 않는다. 해당 증거는 root evidence/review에서 연결해야 한다.
