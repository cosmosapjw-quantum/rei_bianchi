# A2 large-R author note: exact molecular bright pair, localization, and ETF completion

근거 상태: 아래 결과는 **직접 유도(derived)**다. R10Q/R10R의 exact state 및 charge-center convention과 A1b의 exact P⊕Q 정식화를 입력으로 사용한다. 새 molecular eigensolve, 충돌 계산, 공간 수치적분, 기존 CAS/test 재실행은 하지 않았다. 이 문서 작성 당시 독립 검토 전이다. 원자 함수의 적분 identity는 A1b/R10Q에서 검산된 것을 재사용하며, 새 분자 점근 정당화는 여기의 sector gap–quasimode–Hardy argument에 있다.

## 1. 표적, 단위, 위상

κ_A=k, κ_B=2k, a=a_B=ℏ²/(mκ_B)=a_A/2, α=κ_A/κ_B=1/2, E_h=ℏ²/(m a_A²)라 둔다. 두 핵 축은 z이고 B(He) 중심 좌표는 y=r−X_B=(x,y,z), r_B=|y|다. A는 y=−R e_z에 있다. 아래의 r은 혼동 없는 곳에서 r_B를 뜻한다.

\[
h_B=-\frac{\hbar^2}{2m}\nabla^2-\frac{\kappa_B}{r},\qquad
H_R=h_B-\frac{\kappa_A}{|y+R e_z|}.
\tag{L1}
\]

g_R는 exact lowest m=0 state, b_R는 exact lowest |m|=1의 real cosφ bright state다. R10R처럼 meridional wavefunction을 양으로 택한다. 기준 원자 상태는 φ_g=He 1s, φ_b=He 2p_x이며, ε_g=−2E_h, ε_b=−E_h/2, Δ_0=3E_h/2다. g_R,b_R는 이번 증명 이후에만 분리원자 근사와 오차로 연결된다. 유한 R에서 두 상태를 원자 trial function과 같다고 하지 않는다.

분자 charge-center O와 B의 거리는 X_B−O=(R/3)e_z이므로

\[
L_y^O=L_y^B+\frac R3p_x.
\tag{L2}
\]

이 문서의 모든 big-O는 fixed charges/mass에 대해 R/a_A→∞에서, 충분히 큰 R≥R_0의 구간에 균일하다. C와 R_0의 수치값은 계산하지 않았다. 작은 R 또는 임의의 충돌 궤적 전체에 대한 균일 인증은 아니다.

## 2. 왜 exact pair가 He 원자 상태로 국소화되는가

고정 m=0 및 real cosφ |m|=1 Hilbert subspace는 H_R에 불변이다. 각 sector의 낮은 spectrum은 R→∞에서 서로 분리된 A/B Coulomb spectra의 합집합으로 수렴한다. 이 단계는 단순한 물리적 추측 대신 다음 variational argument로 확인할 수 있다.

1. 각 핵 주변 반지름 O(R)의 축대칭 partition of unity와 두 핵에서 떨어진 외부 영역을 쓴다. IMS kinetic remainder는 O(ℏ²/(mR²))다. 각 핵 주변에서 다른 핵 potential은 O(1/R)이고 외부 영역 전체 potential의 하한은 −C/R다.
2. 동일 sector의 원자 bound functions를 cutoff하여 upper quasimodes를 만든다. Atomic exponential decay로 cutoff 오차는 작다. Lower min–max bound는 각 localized component의 원자 quadratic form과 외부 영역의 −C/R bound를 이용한다. Partition은 z-axis 회전 및 cosφ sector를 보존한다.
3. 따라서 0에서 떨어진 fixed negative energy window의 eigenvalue 수 및 순서는 atomic direct sum의 것으로 수렴한다. 그 결과 target 근방에는 단순 eigenvalue 하나가 있고 나머지 spectrum과 R에 독립적인 양의 거리가 있다.

m=0 target ε_g=−2E_h의 다음 limiting energy는 −E_h/2다. 밝은 |m|=1 target ε_b=−E_h/2의 다음 limiting energy는 He n=3의 −2E_h/9이며 gap은 5E_h/18이다. H의 최저 |m|=1 상태는 n=2, −E_h/8로 더 높다. 예를 들어 limiting gaps의 절반보다 작은 fixed contour를 택하면 충분히 큰 R에서 target spectral projection을 고립시킬 수 있다.

**He n=2와 H1s의 에너지 일치는 이 pair proof의 작은 denominator가 아니다.** H1s는 m=0이고 b_R는 |m|=1 sector다. He 2s와 2p_z도 m=0이다. 반면 전체 n=2 shell 또는 다른 m states를 다룰 때 이 sector argument를 무단 확대해서는 안 된다(§6).

## 3. Coulomb singularity를 통제한 molecular quasimode

외부 multipole 식은 |y|<R 안에서만 pointwise 쓴다:

\[
-\frac{\kappa_A}{|y+Re_z|}+\frac{\kappa_A}{R}
=\frac{V_1}{R^2}+\frac{V_2}{R^3}+O\!\left(\frac{\kappa_A r^3}{R^4}\right),
\quad V_1=\kappa_Az,\quad
V_2=-\frac{\kappa_A}{2}(3z^2-r^2).
\tag{L3}
\]

이 점별 expansion을 전 공간에 그대로 적분하지 않는다. |y|≤R/2에서는 Taylor remainder를 사용한다. 그 밖에서는 atomic function과 아래 보정 함수의 exponential decay를 쓰고, A 핵 근방의 1/|y+Re_z| singularity는 local L² integrability로 처리한다. 따라서 fixed exponentially localized polynomial-times-Coulomb function f에 대해

\[
\left\|\left[-\frac{\kappa_A}{|y+Re_z|}+\frac{\kappa_A}{R}
-\frac{V_1}{R^2}-\frac{V_2}{R^3}\right]f\right\|_2=O(R^{-4}).
\tag{L4}
\]

상수와 차원은 각 f의 atomic length/energy moments에 포함한다. moving singularity의 uniform operator-norm Taylor expansion을 주장하는 식이 아니다.

원자 상태에서 ⟨φ_j,V_1φ_j⟩=0이다. 다음 explicit dipole-polarization correction을 잡는다:

\[
u_g=-\frac{\alpha}{2}z(r+2a)\phi_g,\qquad
u_b=-\alpha z(r+6a)\phi_b.
\tag{L5}
\]

직접 product differentiation으로

\[
(h_B-\epsilon_j)u_j=-V_1\phi_j,\qquad
\langle\phi_j,u_j\rangle=0.
\tag{L6}
\]

이를 재현할 짧은 계산은 다음과 같다. t=ℏ²/(2m), φ_g∝e^{−r/a}, φ_b∝xe^{−r/(2a)}이고 f=z(Ar+B)라 두면

\[
\begin{aligned}
(h_B-\epsilon_g)(f\phi_g)
&=-t\phi_gz\left[\frac{4A-2B/a}{r}-\frac{4A}{a}\right],\\
(h_B-\epsilon_b)(f\phi_b)
&=-t\phi_bz\left[\frac{6A-B/a}{r}-\frac{2A}{a}\right].
\end{aligned}
\tag{L7}
\]

첫 식에는 A=−α/2,B=−αa, 둘째에는 A=−α,B=−6αa를 넣으면 된다. 이 보정은 각각 원상태와 z-parity가 반대다.

두 번째 보정을 fixed-sector reduced resolvent로 정의한다. P_j=|φ_j⟩⟨φ_j|, Q_j=1−P_j이고 여기의 Q_j는 A1b의 full six-channel complement와 다른 원자 sector projection이다.

\[
v_j=\langle\phi_j,V_2\phi_j\rangle,\quad
w_j=-\left[(h_B-\epsilon_j)|_{Q_j}\right]^{-1}Q_jV_2\phi_j.
\tag{L8}
\]

§2의 원자 sector gap 때문에 inverse는 bounded다. Forcing은 exponential atomic function에 다항식을 곱한 것이며, ε_j<0에서 pole을 제거한 Coulomb resolvent solution은 충분히 작은 양의 exponential weight를 갖는다. 이는 큰 r에서 −ε_j>0인 elliptic equation에 weighted energy estimate를 적용하여 확인할 수 있다. 여기서는 threshold energy나 degenerate n=2 full space에 이 inverse를 적용하지 않는다.

정규화한 quasimode

\[
\Phi_j(R)=\operatorname{normalize}\left(\phi_j+R^{-2}u_j+R^{-3}w_j\right),\qquad
\lambda_j(R)=\epsilon_j-\kappa_A/R+v_j/R^3
\tag{L9}
\]

는 (L4), (L6), (L8)에 의해 ||(H_R−λ_j)Φ_j||₂=O(R⁻⁴)를 만족한다. 이 오차를 spectral gap으로 나누면 exact normalized positive-phase state와의 L² 오차가 O(R⁻⁴)다. Coulomb form의 translation-independent lower bound

\[
q_R[f]\ge c\|\nabla f\|_2^2-C\|f\|_2^2
\tag{L10}
\]

및 eigen/quasimode residual equation을 사용하면 gradient 오차도 O(R⁻⁴)다. 즉 dimensionless atomic H¹ norm에서

\[
\psi_j(R)=\phi_j+R^{-2}u_j+R^{-3}w_j+O_{H^1}(R^{-4}),
\quad E_j=\epsilon_j-\kappa_A/R+v_j/R^3+O(R^{-4}).
\tag{L11}
\]

정규화 correction은 O(R⁻⁴)에 포함된다. 구체적인 quadrupole expectation은 v_g=0, v_b=6κ_Aa²다. 따라서 Δ_R=Δ_0+6κ_Aa²/R³+O(R⁻⁴). 에너지·상태 remainder의 차원은 각각 E_h(a_A/R)^4, (a_A/R)^4로 읽는다.

## 4. Exact molecular charge-center coupling의 계수와 remainder

R10R의 torque identity를 같은 원점/phase로 쓴다:

\[
\mathcal L^O_{gb}(R)
=-i\hbar\frac{C_R}{\Delta_R}\left(T_B(R)-T_A(R)\right),\quad
C_R=\frac{\kappa_A\kappa_B}{\kappa_A+\kappa_B}R,
\tag{L12}
\]
\[
T_B=\langle g_R,x/r^3\,b_R\rangle,\qquad
T_A=\langle g_R,x/|y+Re_z|^3\,b_R\rangle.
\tag{L13}
\]

이 singular bilinear form은 H¹×H¹에서 연속이다. 두 중심 모두 transverse x 좌표가 같아 |x|≤distance이고,

\[
|\langle f,x/d_C^3\,h\rangle|
\le\|f/d_C\|_2\|h/d_C\|_2
\le4\|\nabla f\|_2\|\nabla h\|_2.
\tag{L14}
\]

따라서 (L11)의 H¹ error를 이 form에 넣어도 uniform O(R⁻⁴)다. 별도의 unproved r∇ weighted convergence로 L 자체를 추정하지 않는다.

u_g,u_b는 z-odd이고 x/r³는 z-even이므로 T_B의 R⁻² correction은 정확히 0이다. 또 quasimode의 exponentially localized terms를 A 근처 singularity와 분리하면 T_A=d_0/R³+O(R⁻⁴)다. 여기서 원자 identity는

\[
T_{B0}=\frac{4}{27\sqrt2 a^2},\qquad
d_0=\langle\phi_g,x\phi_b\rangle=\frac{256a}{243\sqrt2}
=\frac{64\sqrt2}{243}a_A,
\tag{L15}
\]

이고 T_B=T_{B0}+O(R⁻³)이다. (L12)에 넣으면 최종적으로

\[
\boxed{\displaystyle
\mathcal L^O_{gb}(R)
=-i\hbar\frac{32\sqrt2}{243}\frac{R}{a_A}
+O\!\left[\hbar\left(\frac{a_A}{R}\right)^2\right].}
\tag{L16}
\]

이는 exact R10R molecular pair의 결과다. Leading coefficient는 원자 적분에서 왔지만, 이를 exact molecular asymptotic으로 승격한 근거는 (L3)–(L14)의 localization/error argument다. 위상은 R10R의 positive meridional convention이며, arbitrary state phase 아래 행렬원소도 그에 맞게 회전한다.

He-centered angular momentum은 별도로

\[
\mathcal L^B_{gb}=+i\hbar\frac{\kappa_A R}{\Delta_R}T_A
=+i\hbar\frac{128\sqrt2}{729}\left(\frac{a_A}{R}\right)^2
+O\!\left[\hbar\left(\frac{a_A}{R}\right)^3\right].
\tag{L17}
\]

따라서 charge-center의 O(R) 항은 origin lever다. 실제로 exact commutator p_gb=−imΔ_R d_gb/ℏ와 (L11)의 parity를 이용하면

\[
p_{x,gb}=-i\hbar\frac{32\sqrt2}{81a_A}
+O\!\left[\frac\hbar{a_A}\left(\frac{a_A}{R}\right)^3\right],
\quad d_{gb}=d_0+O\!\left[a_A\left(\frac{a_A}{R}\right)^3\right].
\tag{L18}
\]

(L2), (L17), (L18)은 (L16)과 일치한다. L16의 다음 R⁻² 계수 전체를 이번에 계산하지 않았으며, intrinsic coefficient L17과 그 전체 correction을 혼동하지 않는다.

## 5. ETF completion: 어떤 항이 상쇄되고 무엇이 남는가

이 절의 벡터 가속도는 \(\mathbf a_C=\dot{\mathbf v}_C\)이고 그 Cartesian 성분을 \(a_{C,x}\)라 쓴다. Bohr 반지름 \(a=a_B\)와 구분한다. 아래 \(|a_B|\), \(a_B=0\)처럼 궤적 문맥의 표기는 모두 이 가속도의 norm 또는 영벡터를 뜻한다.

A1b의 원자 ETF column은 exact하게

\[
(H-i\hbar\partial_t)\chi_{C\nu}
=\left[-\frac{\kappa_{\bar C}}{|r-X_{\bar C}|}
+\frac{\kappa_{\bar C}}R+m a_C\cdot\rho_C\right]\chi_{C\nu}.
\tag{L19}
\]

따라서 generic atomic residual의 leading term은 dipole O(κa_A/R²)와 가속항 O(m|a_C|a_A)다. He shell의 common scalar 1/R phase는 이미 제거되어 있다. 속도 v_C·p 항은 kinetic boost와 basis translation 사이에서 정확히 상쇄된다. Large-R static bare L이 O(R)이라는 사실만으로 이것을 남은 O(R) 전이 generator 또는 양의 rate라고 읽지 않는다.

더 세밀하게, **exact molecular pair 자체**를 B-centered orbitals로 표현한 뒤 공통 spatial ETF exp(im v_B·ρ_B/ℏ)와 A1b의 atomic reference phases를 곱하자. 분자축의 body rotation을 Q(t), Ω_y=dotθ로 두고 R>0 smooth trajectory만 쓴다. 양 상태에 같은 ETF를 적용하므로 orthogonality가 유지된다. Product rule에서 얻는 pair의 exact off-diagonal은

\[
K^{\rm mol,ETF}_{gb}=e^{i(\gamma_b-\gamma_g)}
\left[m a_{B,x}^{\rm body}d_{gb}
-\Omega_y\mathcal L^B_{gb}
-i\hbar\dot R\langle g_R,\partial_Rb_R\rangle\right].
\tag{L20}
\]

여기서 γ는 채택한 scalar atomic/channel phase다. 미분의 존재는 A1b의 smooth-path/form regularity 범위에서 이해한다. ∂_R은 고정 body axes를 유지하므로 b의 |m|=1 sector를 보존하고, 마지막 radial term은 g의 m=0과 orthogonal하여 0이다. θ-rotation이 밝은 plane xz인 이 pair에 대해 d_y=d_z=0이다. 다른 states 또는 arbitrary full matrix에 이 radial zero를 확대하지 않는다.

Charge-center 표현에서 같은 cancellation을 확인하려면 body B 위치 q_B=(R/3)e_z와

\[
v_B^{body}=V_O^{body}+\Omega\times q_B+\dot q_B
\tag{L21}
\]

를 쓴다. Boost/translation의 momentum 계수는 (v_B−V_O−dot q_B)·p=(Ω×q_B)·p이고, −Ω·L_O=−Ω·L_B−(Ω×q_B)·p와 정확히 상쇄된다. 이것은 L_O를 임의로 L_B로 바꾼 것이 아니라 동일 transformed generator의 모든 미분 항을 보존한 결과다.

따라서 (L17)–(L18)은

\[
K^{\rm mol,ETF}_{gb}=e^{i(\gamma_b-\gamma_g)}
\left[\frac{64\sqrt2}{243}m a_{B,x}^{body}a_A
-i\hbar\Omega_y\frac{128\sqrt2}{729}\left(\frac{a_A}{R}\right)^2
+O\!\left(m|a_B|a_A(a_A/R)^3+\hbar|\Omega_y|(a_A/R)^3\right)\right].
\tag{L22}
\]

일정 속도 직선 nuclear paths이면 a_B=0이고 Ω_y=O(R⁻²), 따라서 이 특정 molecular-pair entry는 O(R⁻⁴)다. 일반 prescribed trajectory에서는 가속항이 지배할 수 있어 universal R⁻⁴이라고 할 수 없다. Coulomb central acceleration처럼 a_B가 순간 분자축 방향이면 a_{B,x}^{body}=0이지만, 이 역시 궤적 조건이다. 일반 A1b tail 가정 a_B=O(t⁻²), R≳|t|, bounded relative velocity는 더 약한 O(t⁻²) pair bound만 준다.

**L20–L22는 완전한 2-state dynamical closure가 아니다.** Exact molecular orbital basis를 다른 공간까지 unitary 완성해야 full TDSE와 동등하다. A1b의 선택된 6 atomic channels와 full P⊕Q에서는 F=HY−iℏYdot, K_QP=Z†F, K_PQ=F†Z를 유지한다. Atomic columns의 tail norm으로 ||K_PP||,||K_QP||,||K_PQ||=O(t⁻²)는 주어진 tail에서 제어되지만, unbounded K_QQ의 operator norm이 0으로 간다는 결론은 없다. Q 제거의 memory kernel은 그대로 남으며, 유한 구간에서 축적된 Q amplitude나 전체 transition amplitude를 이 tail power로 없앨 수 없다.

## 6. 퇴화 cluster와 projector 구조

큰 R에서 ε=−E_h/2 근방 full electronic cluster는 B n=2의 4개 상태와 A1s의 1개 상태, 총 5차원이다. 전체 cluster를 다른 atomic energies로부터 분리하는 fixed spectral contour로 projector Π_5(R)를 정의할 수 있다. 내부를 individual denominators로 나누기 전에 cluster operator를 취해야 한다.

He n=2 projector Π_B2=P_2s+P_2px+P_2py+P_2pz에 대해, body z 방향 remote dipole은

\[
\Pi_{B2}\frac{V_1}{R^2}\Pi_{B2}
=-\frac{3\kappa_A a}{R^2}
\left(|2s\rangle\langle2p_z|+|2p_z\rangle\langle2s|\right).
\tag{L23}
\]

이는 이번에 직접 angular/radial hydrogenic integration으로 정해지는 identity이며 sign은 φ_2s∝(2−r/a)e^{−r/(2a)}, φ_2pz∝ze^{−r/(2a)}에 따른다. 밝은 transverse x 및 dark y는 이 dipole block에서 0이다. Leading R⁻² projected dipole block의 m=0 eigenvectors는 (2s±2p_z)/√2이고 eigenvalue shifts는 ±3κ_Aa/R²다. 두 eigenvalue 사이의 separation은 6κ_Aa/R²이며, R⁻³ quadrupole과 더 높은 차수는 이 eigenvectors를 다시 보정한다. 따라서 개별 2s와2p_z를 finite-R eigenbranch로 단정할 수 없다.

또한 A1s의 remote monopole은 −κ_B/R, Bn2의 것은 −κ_A/R다. 서로 다른 charge arrangements의 O(1/R) detuning (κ_B−κ_A)/R를 먼저 유지한다. Localized atomic basis의 intercenter overlap/coupling은 exponential times polynomial in R이며, 이 fact가 finite-R physical probability를 결정하지는 않는다. Rank-4 He shell projector는 U(4) basis changes에 불변이고 rank-3 p projector는 rotations에 공변이다. Exact g/b는 §2의 각 fixed sector에서 정의했으므로 이 전체 cluster의 arbitrary basis gauge와 구분된다.

## 7. 이 note가 닫는 것과 남기는 것

- Derived: exact R10R molecular bright charge-center coupling의 leading R power, coefficient −iℏ32√2/(243a_A), uniform sufficiently-large-R remainder O(ℏ(a_A/R)²).
- Derived: exact intrinsic He-centered coupling leading +iℏ128√2/729(a_A/R)²; same-origin lever 및 ETF cancellation.
- Derived: fixed-sector isolated-projector/quasimode/H¹–Hardy route와 full near-resonant n2 projector structure.
- Conditional derived: 선택한 exact molecular ETF basis에서 pair generator (L20), 궤적 의존 large-R powers. Frame/gauge 선택을 명시하지 않은 universal completed-generator coefficient는 정의되지 않는다.
- Not asserted: whole-Hilbert-space asymptotic completeness, Q-sector norm decay, six-channel accuracy, finite-R numerical coupling magnitude, nonzero physical capture probability, observed discrepancy의 해결, collision or benchmark results.

검토 우선점은 fixed-sector spectral count, quasimode residual의 moving singularity 처리, H¹ 오차로 singular torque를 제어하는 단계, L16/L17의 계수·부호, L20의 basis/trajectory dependence다. 이 문서는 전체 A2 small-R closure를 판정하지 않는다.
