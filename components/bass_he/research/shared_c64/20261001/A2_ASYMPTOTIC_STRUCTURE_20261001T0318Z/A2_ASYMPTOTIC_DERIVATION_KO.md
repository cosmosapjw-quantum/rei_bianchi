# A2: 정확한 bright coupling의 두 극한과 frame/ETF 구조

이 문서의 새 수식은 직접 유도(derived)다. 원전이 뒷받침하는 상태 분류·국소화·원점 의존성과 새 정량적 증명을 구분한다. 완결 판정은 `review/A2_INDEPENDENT_REVIEW.json`과 `RESULT.json`이 소유한다. 아래의 두 저자 증명은 본 유도의 구성 부분이다: `derivations/SMALL_R_AUTHOR_KO.md`(S.1–29), `derivations/LARGE_R_AUTHOR_KO.md`(L1–23).

## 1. 물리 범위와 결과

한 전자, spinless, 비상대론적 clamped point-Coulomb Hamiltonian을 사용한다. κ=e²/(4πε₀), κ_A=κ, κ_B=2κ, m=m_e,

\[
a_A=\hbar^2/(m\kappa),\quad a_B=a_A/2,\quad a_U=a_A/3,
\quad E_A=\hbar^2/(ma_A^2),\quad x=R/a_A.
\tag{A2.1}
\]

Charge-center O에서 z_A=−2R/3, z_B=R/3이며 L_y^O=−iℏ(z∂_x−x∂_z)다. 이후 좌표 x 성분과 무차원 x=R/a_A는 문맥으로 구분한다. g_R는 exact lowest m=0 state, b_R는 exact lowest |m|=1의 real cosφ bright state다. 양의 meridional phase, 반선형 첫 인자 inner product, R10R의 Friedrichs realization을 유지한다. 핵 반발 2κ/R는 전자상태와 gap에 영향을 주지 않는 공통 scalar로 제외한다.

새 결과는 다음이다.

\[
\boxed{\mathcal L^O_{gb}(R)
=-i\hbar\frac{4\sqrt2}{15}x^3+O(\hbar x^{7/2})\quad(x\downarrow0).}
\tag{A2.2}
\]
\[
\boxed{\mathcal L^O_{gb}(R)
=-i\hbar\frac{32\sqrt2}{243}x+O(\hbar x^{-2})\quad(x\to\infty).}
\tag{A2.3}
\]

첫 식은 UA 시험함수의 적분만이 아니라 exact molecular eigenstates의 remainder까지 포함한다. 두 번째도 원자 lever를 exact molecular 값으로 무조건 대체한 결과가 아니다. Big-O 상수와 적용 반경은 고정 Hamiltonian에서 존재하지만 수치적으로 산출하지 않았다. 중간 R coupling 크기, 수치 수렴 또는 충돌 단면적 인증은 포함하지 않는다.

## 2. 작은 R: 내부 Coulomb 영역이 만드는 cubic 항

H_U=−ℏ²Δ/(2m)−3κ/r, W_R=H_R−H_U라 두자. Charge-center의 Σκ_Cz_C=0으로 외부 dipole은 사라진다. 하지만 r>max|z_C|에서만 유효한 multipole 급수를 핵 근처까지 연장할 수 없다. 외부 quadrupole은 parity-even, octupole은 rank 3이므로 UA s–p mixing의 실제 첫 항을 이 두 angular selection만으로 정할 수 없다.

정확한 UA comparison vectors g₀=N_s exp(−r/a_U), p_z₀=N_p z exp(−r/(2a_U))에 대해 λ=3/(2a_U)라 두면

\[
F(d)=\int\frac{z e^{-\lambda r}}{|\mathbf r-d\mathbf e_z|}\,d^3r
=\frac{4\pi}{3}\left[d^{-2}\int_0^d r^4e^{-\lambda r}dr
+d\int_d^\infty r e^{-\lambda r}dr\right]\quad(d>0),
\tag{A2.4}
\]

이고 F는 odd다. 안쪽과 바깥쪽 적분을 모두 보존하면

\[
F(d)=\frac{4\pi d}{3\lambda^2}-\frac{2\pi d^3}{5}
+\frac{2\pi\lambda}{9}d|d|^3+O(|d|^5).
\]

따라서 M₃=Σκ_C(z_C/R)³=−2κ/9,

\[
\langle p_{z0},W_Rg_0\rangle
=\frac{M_3R^3}{10\sqrt2a_U^4}+O(E_Ax^4)
=-\frac9{5\sqrt2}E_Ax^3+O(E_Ax^4).
\tag{A2.5}
\]

이 coefficient는 핵 내부 기여를 포함하는 정확한 적분에서 나온다. 전자 Hamiltonian에 새로운 point interaction을 추가한 것이 아니다.

이를 exact molecular 결과로 연결하는 핵심은 다음의 별도 추정이다. 고정 a_A,E_A로 무차원화한 Sobolev 공간을 사용한다. Fourier potential은 q⁻²[K−Σκ_Cexp(−iα_CRq_z)]이고 charge dipole 소거로 numerator의 영차·일차가 모두 0이다. 작은/중간/큰 q를 나누어 적분하면

\[
\|W_R\|_{H^{-2}}=O(x^2),\quad
\|L_yW_R\|_{H^{-2}}=O(\hbar x^2).
\tag{A2.6}
\]

Translated Hardy inequality는 공통 domain H²와 R-uniform Coulomb graph bound를 준다. 3차원 H² multiplication algebra와 duality를 통해 W_Rg 및 (L_yW_R)g가 같은 H⁻² 차수를 유지한다. UA의 고립된 ground 및 fixed bright-sector contour에서 resolvent는 H⁻²→L²로 균일 유계다. Contour projector identity와 normalization은

\[
\|g_R-g_0\|_2+\|b_R-b_0\|_2=O(x^2)
\tag{A2.7}
\]

를 준다. L은 unbounded이므로 이것만으로 A2.2를 결론내리지 않는다. Bound-state decay로 L_yg_R∈L²의 존재를 먼저 확보하고, 분포 방정식

\[
(H_R-E_g)L_yg_R=-(L_yW_R)g_R
\]

에 reduced resolvent를 적용하여 ||L_yg_R||₂=O(ℏx²)를 별도로 얻는다. L_yg_R∈D(H_R)는 요구하지 않는다. 또한 W_R=R⁻¹w(r/R), w(y)=O(|y|⁻³)에서 ||W_Rp_z₀||₂=O(x^{3/2})다. 그러므로

\[
\langle p_{z0},W_R(g_R-g_0)\rangle=O(E_Ax^{7/2}),
\quad \langle L_yg_R,b_R-b_0\rangle=O(\hbar x^4).
\tag{A2.8}
\]

정확한 ground equation의 p_z₀ projection과 L_yb₀=−iℏp_z₀를 결합한다. 분모는 E_g−E₂^U→−27E_A/8이며 퇴화 cluster 내부의 영분모가 아니다. A2.5와 두 remainder가 A2.2를 준다. 이로써 coefficient의 atomic derivation과 molecular admission을 분리해 연결했다. 상세 Fourier integral, distribution product 및 contour 단계는 S.10–28에 있다. O(x^{7/2})는 안전한 bound이며 최적 차수나 로그항 부재를 주장하지 않는다.

## 3. 큰 R: fixed-sector quasimode와 singular torque

He 중심 좌표 y=r−X_B, r_B=|y|에서 A는 −R e_z에 있다. g_R→He1s, b_R→He2p_x를 보일 때 sector를 먼저 고정한다. IMS localization과 min–max를 사용하면 낮은 fixed-sector spectrum은 양 중심 원자 spectrum의 합으로 수렴한다. m=0의 target gap은 3E_A/2, bright |m|=1의 다음 He n=3과의 gap은 5E_A/18이다. 따라서 충분히 큰 R에서 두 target을 각각 고립시키는 fixed contour가 있다. H1s–He n=2의 전공간 퇴화는 이 두 sector ground의 분모를 0으로 만들지 않는다.

a=a_B, α=κ_A/κ_B=1/2라 쓰고 원자 φ_g,φ_b에 대해

\[
u_g=-\frac\alpha2z(r_B+2a)\phi_g,\qquad
u_b=-\alpha z(r_B+6a)\phi_b,
\quad (h_B-\epsilon_j)u_j=-\kappa_Az\phi_j.
\tag{A2.9}
\]

이 두 polarized quasimode는 직접 미분과 신규 CAS에서 확인됐다. Remote potential의 V₂=−κ_A(3z²−r_B²)/2 항은 fixed-sector reduced resolvent로 w_j=−S_jQ_jV₂φ_j를 정의하여 보정한다. |y|≤R/2의 Taylor bound와 나머지 영역의 exponential decay/local Coulomb integrability를 나누면

\[
\psi_j=\phi_j+R^{-2}u_j+R^{-3}w_j+O_{H^1}(x^{-4}),
\quad E_j=\epsilon_j-\kappa_A/R+v_j/R^3+O(E_Ax^{-4}),
\tag{A2.10}
\]

v_g=0, v_b=6κ_Aa_B²다. H¹ 추정은 L² residual·sector gap·Coulomb form coercivity로 얻는다. 무한거리 Coulomb singularity까지 pointwise multipole 급수를 적분한 결과가 아니다.

R10R의 exact torque identity를 적용한다. T_B=⟨g,x/r_B³ b⟩, T_A=⟨g,x/d_A³ b⟩이면

\[
\mathcal L^O_{gb}=-i\hbar\frac{(2\kappa R/3)(T_B-T_A)}{\Delta_R},
\qquad
|\langle f,x/d_C^3h\rangle|\le4\|\nabla f\|_2\|\nabla h\|_2.
\tag{A2.11}
\]

이 Hardy bilinear bound로 H¹ remainder를 직접 제어한다. u_j의 z-odd parity가 T_B의 R⁻² correction을 소거한다. T_B=4/(27√2 a_B²)+O(R⁻³), T_A=d_B/R³+O(R⁻⁴), d_B=64√2a_A/243이므로 A2.3이 따른다. 원자 함수의 bare lever coefficient만으로 molecular theorem을 선언하지 않았다.

같은 계산은 He-centered angular momentum에 대해 더 작은 항을 준다.

\[
\boxed{\mathcal L^B_{gb}
=+i\hbar\frac{128\sqrt2}{729}x^{-2}+O(\hbar x^{-3}).}
\tag{A2.12}
\]

정확히 L_y^O=L_y^B+(R/3)p_x다. Momentum expectation은 A2.10의 H¹ error와 parity로 먼저 통제하고, exact p_{gb}=−imΔ_Rd_{gb}/ℏ로 dipole을 얻는다. 이 순서로 unbounded x의 expectation을 H¹ convergence만으로 추정하는 오류를 피한다. 결과는 p_{gb}=−iℏ32√2/(81a_A)+O((ℏ/a_A)x⁻³), d_{gb}=d_B+O(a_Ax⁻³)다. A2.3의 전체 R⁻² coefficient는 이번에 계산하지 않았으며 A2.12와 동일시하지 않는다.

## 4. 전체 R에서 존재하는 비교 bound

새로운 fitted coupling curve를 만들지 않는다. 단지 양의 analytic comparison weight f(x)=x³/(1+x²)를 정의하자. R10R은 iℒ^O/ℏ>0를 모든 R>0에서 준다. H¹ sector-state continuity, uniform Hardy bound, smooth compact-support approximation에 대한 translated torque continuity, Δ_R>0를 결합하면 ℒ^O(R)는 R>0에서 연속이다. 여기서 translated singular kernel의 H¹→H⁻¹ operator-norm continuity를 주장하지 않는다.

A2.2–3에 의해 iℒ^O/(ℏf)의 양 끝 극한은 각각 4√2/15, 32√2/243이다. 나머지 compact interval에 extreme-value theorem을 적용하면 고정 H/He 계에서

\[
0<c_-\le\frac{i\mathcal L^O_{gb}(R)}{\hbar f(R/a_A)}\le c_+<\infty
\quad(0<R<\infty)
\tag{A2.13}
\]

인 상수가 존재한다. 이 global two-sided bound는 **비구성적 존재 명제**다. c_± 또는 유효 반경의 numerical enclosure는 없고, f를 실제 coupling 근사·보간식·단면적 입력으로 채택하지 않는다. C1/C2의 tolerance나 finite-R magnitude 인증을 대신하지 않는다.

## 5. 실제 completed connection: 원점과 spatial ETF를 함께 고정

Bare matrix element의 power가 전체 generator entry의 power와 같을 필요는 없다. 다음은 exact BO g,b에 공통 B-centered spatial ETF exp[im v_B·(r−X_B)/ℏ]와 scalar channel phase를 곱한, 명시적으로 선택한 다른 완성 기저의 두 entry다. 전체 Hilbert space까지 unitary 완성하며 2-state closure를 주장하지 않는다. Fixed body axes의 ∂_R은 m sector를 보존하므로 ⟨g,∂_Rb⟩=0이다. 충돌면 xz, Ω_y=θdot에서 product rule은

\[
K^{B\text{-ETF}}_{gb}=e^{i(\gamma_b-\gamma_g)}
\left[m a_{B,x}^{body}d_{gb}-\Omega_y\mathcal L^B_{gb}\right]
\tag{A2.14}
\]

를 준다. a_{B,x}는 He 핵 가속도의 성분이며 Bohr length a_B와 다르다. q_B=(R/3)e_z와 v_B^{body}=V_O^{body}+Ω×q_B+dot q_B를 넣으면 momentum 항 +(Ω×q_B)·p가 −Ω·L_O의 lever와 정확히 상쇄된다. Translation·rotation·boost를 함께 변환한 결과다.

큰 R에서는

\[
K^{B\text{-ETF}}_{gb}=e^{i\Delta\gamma}
\left[\frac{64\sqrt2}{243}m a_{B,x}^{body}a_A
-i\hbar\Omega_y\frac{128\sqrt2}{729}x^{-2}
+O(m|\mathbf a_B|a_Ax^{-3}+\hbar|\Omega_y|x^{-3})\right].
\tag{A2.15}
\]

직선 등속 핵 경로이면 a_B=0, Ω_y=O(R⁻²)이므로 이 particular entry는 O(R⁻⁴)다. 일반 prescribed trajectory에서 가속항은 남는다. 원자 six-channel entry, full P/Q generator, 전체 capture amplitude에 이 R⁻⁴를 확대하지 않는다.

작은 R의 같은 B-ETF 표현도 별도로 구한다. A2.7 및 uniform H²로 δψ의 H¹ norm은 O(x)다. Momentum pairing의 두 선형 오차는 derivative를 고정 UA 함수에 옮겨 O(x²), 이차 오차는 O(x³)로 제어한다. Energy shift도 O(E_Ax²)다. Ground shift는 S.26 뒤의 spherical integral로, bright shift는 ⟨b₀,W_Rb₀⟩의 안/밖 분할로 얻는다. 후자는 nuclear region의 |b₀|²=O(r²)와 외부 quadrupole의 적분 가능성을 쓰며, ||W_Rb₀||₂=O(x^{3/2})와 A2.7이 exact-state 보정도 통제한다. 따라서 exact commutator에서

\[
p_{gb}=-i\hbar\frac{16\sqrt2}{27a_A}+O((\hbar/a_A)x^2),
\quad d_{gb}=d_U+O(a_Ax^2),\quad d_U=\frac{128\sqrt2}{729}a_A.
\tag{A2.16}
\]

L_B=L_O−(R/3)p에 따라

\[
\mathcal L^B_{gb}=+i\hbar\frac{16\sqrt2}{81}x+O(\hbar x^3),
\quad
K^{B\text{-ETF}}_{gb}=e^{i\Delta\gamma}
\left[m a_{B,x}^{body}d_U-i\hbar\Omega_y\frac{16\sqrt2}{81}x
+O(m|\mathbf a_B|a_Ax^2+\hbar|\Omega_y|x^3)\right].
\tag{A2.17}
\]

Charge-center의 공통 ETF exp[im V_O·(r−O)/ℏ]를 선택하면 같은 product rule의 entry는 m a_{O,x}d−Ω_yℒ^O이고, 가속도가 0이며 Ω가 bounded일 때 회전 entry는 +iℏΩ_y(4√2/15)x³+O(ℏ|Ω_y|x^{7/2})다. 이 O-ETF와 B-ETF는 단순 scalar rephasing만이 아니라 exp[im(v_B−V_O)·r/ℏ]라는 spatial unitary로 관계된다. 전체 완성 공간에서 K′=U†KU−iℏU†dot U로 같은 TDSE를 나타내지만 두 개별 entry의 power는 달라도 된다. 상대 radial velocity가 유한하면 이 boost는 R→0에서 identity가 될 필요도 없다.

A1b의 scattering-channel phase κ_other∫dt/(ℏR)는 R>0 산란 tail용이다. Static UA limit에서 이를 연장하지 않는다. 필요하면 G_CC=exp[−iκ_other∫dt/(ℏR)]로 해당 위상을 제거하고 K′=G†KG−iℏG†dot G의 diagonal −κ_other/R를 함께 보존한다. 이것은 단지 time gauge의 변경이며 R=0 핵충돌 경로나 무한 핵 반발의 물리적 통과를 승인하지 않는다.

## 7. 퇴화 cluster와 full P/Q tail

큰 R의 ε=−E_A/2 cluster는 A1s와 B n=2의 5개 상태다. Cluster 내부를 individual zero denominators로 나누지 않고 fixed exterior contour의 rank-5 projector를 쓴다. 중심별 monopole은 A1s에 −κ_B/R, B n=2에 −κ_A/R를 주므로 차이 (κ_B−κ_A)/R가 지수적으로 작은 intercenter mixing보다 크다. He rank-4 shell 안에서

\[
\Pi_{B2}z\Pi_{B2}=-3a_B(|2s\rangle\langle2p_z|+|2p_z\rangle\langle2s|),
\tag{A2.18}
\]

이고 Q₂=3z²−r_B²의 diagonal은 (2s,2p_x,2p_y,2p_z) 순서에서 (0,−12,−12,24)a_B²다. Remote dipole은 κ_AΠzΠ/R², quadrupole은 −κ_AΠQ₂Π/(2R³)다. Leading R⁻² projected dipole block의 m=0 eigenvectors는 (2s±2p_z)/√2이며 더 높은 차수에서 다시 보정되므로 2s와2p_z를 finite-R exact eigenbranch로 고정하지 않는다. Full shell projector는 U(4) gauge와, p-triplet은 spatial rotation과 함께 변환한다. Exact R10R pair의 fixed-sector 정의와 이 cluster 기저는 구분한다.

A1b가 채택한 atomic ETF columns에는 정확히

\[
(H-i\hbar\partial_t)\chi_{C\nu}
=\left[-\frac{\kappa_{\bar C}}{|r-X_{\bar C}|}+\frac{\kappa_{\bar C}}R
+m\mathbf a_C\cdot\rho_C\right]\chi_{C\nu}
\tag{A2.19}
\]

가 성립한다. Remote Taylor region과 exponential remainder를 나누면 residual norm≤C E_A x⁻²+C m a_A max_C|a_C|다. 중심 간 overlap 및 그 derivative는 bounded velocity 아래 exponential times polynomial이고, 충분히 큰 R에서 S⁻¹ 및 orthogonalization은 균일 유계다. 따라서 R(t)≥c(1+|t|), bounded velocities, a_C=O(t⁻²)라는 A1b tail에서, energy scale을 포함한 f(t)=O(t⁻²)에 대해

\[
\|K_{PP}(t)\|+\|K_{QP}(t)\|+\|K_{PQ}(t)\|\le C f(t).
\tag{A2.20}
\]

K_QQ는 unbounded full complementary operator이며 그 operator norm의 감쇠는 주장하지 않는다. U_Q가 unitary인 A1b의 domain/regularity 조건 아래 exact memory kernel은

\[
\|K_{PQ}(t)U_Q(t,s)K_{QP}(s)\|\le C^2 f(t)f(s)
\tag{A2.21}
\]

이고 단위는 energy²다. Tail forcing의 적분은 O(1/T)로 제어되지만 이미 쌓인 Q amplitude나 유한 충돌 구간의 model reduction error를 0으로 만들지 않는다. Full P⊕Q를 유지하며 η=0 또는 양의 rate/sink로 바꾸지 않는다.

## 8. 검증과 claim 경계

신규 Wolfram exact CAS 한 회에서 shifted-Coulomb series, cubic coefficient 4√2/15, 두 polarization ODE residual 0, n2 dipole/quadrupole 및 intrinsic coefficient를 확인했다. 입력은 `code/A2_EXACT_CHECKS.wl`, 실제 출력은 `evidence/WOLFRAM_RAW_RESPONSE.json`이다. CAS는 functional-analytic estimate와 physical completeness를 증명하지 않는다. 그 부분은 두 저자 증명과 별도 독립 검토의 대상이다.

문헌은 `source_notes/A2_PRIMARY_SOURCES_KO.md` 및 JSON manifest에 출처·페이지·바이트 identity를 기록했다. GK1961의 UA 에너지·SA localization, P24의 origin connection을 새 Ly 계수의 문헌상 인증으로 쓰지 않는다. 새 primary PDF는 private archive에만 포함한다. 추가 원문 일부의 fetch 실패는 source-access failure로 보존하며 수식 실패와 구분한다.

물리 eigensolve, 실제 coupling grid, Coulomb 공간 수치적분, 충돌 전파, impact 적분, benchmark fitting, channel/continuum convergence, Eq55는 모두 NOT_RUN이다. 새 과학 Python suite는 실행하지 않았고 기존 검증을 재실행하지 않았다. A2 closure는 명시한 exact pair의 analytic asymptotics와 선택된 connection/projector 구조에 한정된다. Nonconstructive constants를 수치 오차 certificate로 사용하지 않는다. Full scattering completeness나 6채널 정확도는 후속 문제다.

독립 검토가 이 범위를 admission하면 다음 단일 node는 C1의 electronic solver architecture다. C1을 실행했다고 하지 않는다. `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`, `production_default_change=NOT_AUTHORIZED`를 유지한다.
