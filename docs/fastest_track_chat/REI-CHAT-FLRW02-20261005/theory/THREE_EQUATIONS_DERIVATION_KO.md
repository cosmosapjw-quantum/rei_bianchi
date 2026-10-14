# FLRW 세 방정식의 공통 보존 구조와 source-bound 복원 계약

작성일 2026-10-05. 선행 REI-CHAT-FLRW01의 유도·standalone 검산은 계승한다. 이번 문서는 fixed comoving control volume의 경계 flux, volume/mass/phase 평균의 구별, frequency 좌표 Jacobian, 명시적 photon ownership을 추가하여 실제 소비자 검사의 기준을 만든다. 아래 수학은 명시된 transport·atomic 모형 안에서의 직접 유도다. 실제 코드 실행·물리적 closure 인증은 별도의 evidence를 요구한다. Peebles effective recombination은 여기의 국소 재이온화 식을 대체하지 않는다.

## 1. 변수와 가정

FLRW metric signature는 (-,+,+,+), proper time은 t, scale factor는 a(t), H=dot(a)/a이다. comoving 위치를 r, proper peculiar velocity를 v라 두어 D_t=partial_t+(v/a)·grad_r로 정의한다. 수소 nuclei는 생성·소멸하지 않고 H I/H II는 같은 bulk velocity로 운반된다. 별도 species diffusion, 별 내부로 제거되는 gas, nonthermal secondary ionization은 필요 시 독립 항으로 추가한다. Photon 식은 FLRW comoving observer frame의 spectral moment다. Gas peculiar velocity의 상대론적 Doppler 효과를 무시하는 일반적인 비상대론적 transport 모형을 대상으로 하며, 이를 포함할 때는 collision operator를 같은 frame으로 변환해야 한다.

n_H=n_HI+n_p는 proper nuclei density, x=n_p/n_H이다. Pure H에서는 n_e=n_p=n_H x이며, H/He에서는 n_e가 독립 species 합으로 정해져 x^2 치환을 그대로 쓰면 안 된다. alpha는 지정한 Case-A 또는 Case-B coefficient, k_ci는 선택적 collisional-ionization coefficient다. 각 coefficient 단위는 cm^3 s^-1 또는 일관된 SI이고 Gamma_H는 s^-1이다.

이 문서에서는 다음 세 scalar를 구별한다.

- X_V=<x>: 일반적인 volume-weighted ionized fraction.
- X_M=<n_H x>/<n_H>: nuclei-weighted ionized fraction.
- Q_V=<b>: 명시적 geometric ionized-phase indicator b∈{0,1}의 filling factor.

일반 partial-ionization field에서 b를 지정하지 않고 x만으로 Q_V를 유일하게 결정할 수 없다. Sharp fully-ionized/neutral two-phase closure x=b가 시간 구간 전체에 유지될 때에만 X_V=Q_V이다. 단일 시각의 binary cell values는 geometric front velocity나 dot(Q_V)를 결정하지 않는다.

## 2. 첫째 식: proper continuity에서 국소 fraction 방정식

\[
\partial_t n_H+3Hn_H+\frac1a\nabla\!\cdot(n_H\boldsymbol v)=0,
\]
\[
\partial_t n_p+3Hn_p+\frac1a\nabla\!\cdot(n_p\boldsymbol v)
=I_H+C_H+I_{\rm sec}-R,
\]
\[
I_H=n_H(1-x)\Gamma_H,\quad
C_H=k_{\rm ci}n_e n_H(1-x),\quad
R=\alpha n_e n_Hx .
\]

n_p=x n_H를 대입하고 x 곱 nuclei continuity를 빼면 dilution과 compression 항이 정확히 소거되어

\[
\boxed{D_t x=(1-x)\Gamma_H+k_{\rm ci}n_e(1-x)
-\alpha n_e x+\frac{I_{\rm sec}}{n_H}.}\tag{L}
\]

광이온화와 재결합만 있는 pure H의 한 점에서는
\[
\dot x=(1-x)\Gamma_H-\alpha n_H x^2.
\]
Fraction에 -3Hx를 더하는 것은 이 모형에서 이중 dilution이다. Expansion은 n_H(t), radiation redshift, thermal evolution을 통하여 계수에 작용한다. 국소 recombination의 density factor는 n_e n_HII이고 n_e n_HI가 아니다.

Photon number spectral density n_nu를 사용하면
\[
\Gamma_H=\int_{\nu_0}^{\infty}c\,\sigma_H(\nu)n_\nu\,d\nu,
\quad \nu_0=\chi_H/h,\qquad \chi_H\simeq13.6\,{\rm eV}.
\]
Energy intensity convention에서는 n_nu=4pi J_nu/(c h nu)이다. 이 등식은 local atomic absorption과 photon decrement를 하나의 event rate에 연결한다. 임의의 effective MFP opacity는 local n_HI sigma와 동일하다고 가정하지 않는다.

## 3. 둘째 식을 평균하기 전에 필요한 flux·covariance

고정된 comoving V에서 <f>=V^-1 integral_V f d^3r로 정의한다. Proper volume average도 homogeneous a^3가 분자·분모에서 소거되어 같은 평균이다. 여기의 시간미분과 평균 교환은 common H와 고정된 comoving integration weights를 전제로 한다. Moving control volume, 시간가변 cell weights, gas-selection cutoff에는 별도 Reynolds boundary/weight covariance 항이 필요하다. theta_v=(1/a)div(v), B_x=(aV)^-1 integral_boundary x v·dA라 두면 (L)로부터

\[
\dot X_V=\langle D_t x\rangle+\langle x\theta_v\rangle-B_x.
\tag{V}
\]

Periodic 경계에서는 <theta_v>=0이므로 두 번째 항은 Cov(x,theta_v)다. 반응이 없더라도 gas compression과 phase-volume transport는 X_V를 바꿀 수 있다. 한편
\[
X_M-X_V={\rm Cov}(\Delta,x),\qquad
\Delta=n_H/\bar n_H,\quad\bar n_H=\langle n_H\rangle .
\]
Photoionization rate도 <n_HI Gamma>=<n_HI><Gamma>+Cov(n_HI,Gamma)이고 recombination은 <alpha n_e n_p>다. 평균 coefficient나 density를 단순히 곱하는 것은 별도 closure이며 원 미시식의 exact average가 아니다.

Open boundary까지 추적하려면
\[
B=\langle a^3n_H\rangle,\quad P=\langle a^3n_p\rangle,\quad X_M=P/B,
\]
\[
{\cal B}_H=\frac{a^2}{V}\oint n_H\boldsymbol v\cdot d\boldsymbol A,\quad
{\cal B}_p=\frac{a^2}{V}\oint n_p\boldsymbol v\cdot d\boldsymbol A
\]
를 쓴다. 모든 boundary rate는 outward positive다. 그러면
\[
\dot B=-{\cal B}_H,\quad
\dot P=A_H+I_{\rm extra}-{\cal R}-{\cal B}_p,
\tag{M}
\]
\[
\dot X_M=\frac{A_H+I_{\rm extra}-{\cal R}-{\cal B}_p}{B}
+X_M\frac{{\cal B}_H}{B}.
\]
여기서 A_H=<a^3 I_H>, I_extra=<a^3(C_H+I_sec)>, Rcall=<a^3 R>이다. Periodic/closed matter domain이면 두 matter boundary rate가 0이 된다.

## 4. 셋째 식: proper/comoving photon spectrum과 threshold

n_nu는 proper volume당, proper frequency당 광자수이고 F_nu는 proper area당 spectral number flux다. s_nu는 proper spectral photon production rate다. 국소 opacity kappa_nu에 대해
\[
\boxed{\partial_t n_\nu+3Hn_\nu+\frac1a\nabla\cdot\boldsymbol F_\nu
+\partial_\nu(-H\nu n_\nu)=s_\nu-c\kappa_\nu n_\nu.}\tag{P}
\]

이는 nonconservative 표기로 partial_t n_nu-H nu partial_nu n_nu+2H n_nu+div(F_nu)/a=...와 같다. 3H는 conservative frequency flux와 함께 나타나고, nonconservative per-frequency number 식에는 2H가 나타난다. Energy intensity J_nu 식의 3H를 photon number per-frequency 식에 그대로 복제하면 틀린다.

공간만 comoving으로 바꾸면 N_nu=a^3 n_nu, Fcal_nu=a^2 F_nu이며
\[
\partial_tN_\nu+\nabla\cdot{\cal F}_\nu+
\partial_\nu(-H\nu N_\nu)=a^3s_\nu-c\kappa_\nu N_\nu .
\tag{Pc}
\]
Frequency도 q=a nu로 바꾸면 d q=a d nu이므로
\[
{\cal N}_q\,dq=N_\nu\,d\nu,\quad
{\cal N}_q=a^2n_{\nu=q/a},\quad
{\cal F}_q=a\,\boldsymbol F_{\nu=q/a},
\]
\[
\left.\partial_t{\cal N}_q\right|_q+\nabla\cdot{\cal F}_q
=a^2s_{\nu=q/a}-c\kappa_{\nu=q/a}{\cal N}_q .
\tag{Pq}
\]
q coordinate에서는 frequency drift가 사라지는 대신 물리 ionization threshold가 q_0(t)=a(t)nu_0로 움직인다. Leibniz rule의 -dot(q_0) Ncal(q_0)를 버리면 같은 광자가 잘못 남는다.

고정 proper threshold nu_0 이상을 적분하고 high-frequency boundary nu N_nu→0을 요구하면
\[
\dot G=S_\star+J_{\rm rec}-A_H-A_{\rm other}
-L_z-{\cal B}_\gamma,\tag{G}
\]
\[
G=\left\langle\int_{\nu_0}^\infty N_\nu d\nu\right\rangle,\quad
L_z=\langle H\nu_0N_{\nu_0}\rangle,\quad
{\cal B}_\gamma=\frac1V\oint\int_{\nu_0}^\infty{\cal F}_\nu d\nu\cdot d\boldsymbol A .
\]
S_star와 J_rec는 tracked ionizing photon NUMBER production의 평균이다. Recombination cooling energy를 mean photon energy로 나눠 J_rec를 추측하지 않는다. A_other에는 helium·dust 등 H photoionization을 만들지 않는 photon sinks를 넣는다. H>0에서 L_z≥0이고, photons는 전체 수에서 소멸하지 않지만 ionizing subset에서 빠진다.

유한 group [nu_l,nu_u]의 redshift 기여는
\[
\dot N_g\big|_{\rm redshift}
=H\nu_uN_{\nu_u}-H\nu_lN_{\nu_l}.
\]
같은 edge flux를 양쪽 group에 반대 부호로 사용해야 내부 flux가 telescoping된다. Lowest-edge exit와 최고 주파수 유입 경계만 전체 합에 남는다. Group average photon count만으로 arbitrary spectrum의 edge value가 정해지는 것은 아니다.

## 5. 세 식을 연결하는 하나의 inventory

동일 site·time·frequency domain에서 photon loss의 H 부분은 matter source와 동일하다:
\[
A_H=\left\langle\int_{\nu_0}^\infty
c\,n_{\rm HI}\sigma_H(\nu)N_\nu\,d\nu\right\rangle
=\langle a^3 n_{\rm HI}\Gamma_H\rangle .
\tag{E}
\]
(M)+(G)를 더하면 이 absorption event가 소거되어
\[
\boxed{\frac{d(P+G)}{dt}
=S_\star-({\cal R}-J_{\rm rec})+I_{\rm extra}
-A_{\rm other}-L_z-{\cal B}_p-{\cal B}_\gamma.}\tag{I}
\]
이것이 nuclei·ionized matter·ionizing photon inventory를 연결하는 핵심이다. Energy conservation 식은 아니며, collisional/secondary ionization의 에너지원은 별도 energy ledger를 필요로 한다.

eta=G/B, s_star=S_star/B, r_eff=(Rcall-J_rec)/B라 하면
\[
\frac{d(X_M+\eta)}{dt}
=s_\star-r_{\rm eff}+\frac{I_{\rm extra}-A_{\rm other}-L_z-{\cal B}_p-{\cal B}_\gamma}{B}
+(X_M+\eta)\frac{{\cal B}_H}{B}.\tag{IH}
\]
Per-H 변수에 -3H를 다시 추가하지 않는다. Matter boundary가 있으면 분모 B도 변하므로 마지막 항이 반드시 필요하다.

Geometry Q_V를 독립적으로 제공하고 Xi=X_M-Q_V라 두면 임의의 사전 고정 t_ref에 대해
\[
\begin{aligned}
\dot Q_V-(s_\star-Q_V/t_{\rm ref})={}&
-\dot\eta-\dot\Xi-(r_{\rm eff}-Q_V/t_{\rm ref})\\
&+\frac{I_{\rm extra}-A_{\rm other}-L_z-{\cal B}_p-{\cal B}_\gamma}{B}
+(X_M+\eta)\frac{{\cal B}_H}{B}.
\end{aligned}\tag{D}
\]
이 exact bookkeeping identity는 geometric closure를 생성하지 않는다. Xi_dot를 Q_dot에 맞춰 정의하여 잔차를 0으로 만드는 검사만으로 Q dynamics가 검증되었다고 할 수 없다. 각 RHS와 phase closure의 독립 evidence를 별도 기록한다.

## 6. Madau형 filling-factor 식이 나오는 추가 조건

Sharp phase b가 유지될 때 delta_I=<Delta|b=1>, C_I=<Delta^2|b=1>/delta_I^2라 두면
\[
X_M=Q_V\delta_I,\quad
\dot Q_V=\frac{\dot X_M-Q_V\dot\delta_I}{\delta_I}.
\tag{F}
\]
이 관계는 delta_I(t) 또는 phase-front evolution이 별도로 주어질 때만 Q evolution을 닫는다. 유한 cell의 순간 binary 값에 local x_dot를 대입한다고 front-motion law가 생기지 않는다.

0<Q_V<1에서는 delta_I>0, Q_V delta_I≤1이 필요하며 neutral-phase mean density는
\[
\delta_N=\frac{1-Q_V\delta_I}{1-Q_V}\ge0
\]
여야 한다. Q_V=1이면 delta_I=1이다. Q_V=0에서는 conditional mean delta_I가 정의되지 않으므로 front onset의 one-sided limit을 별도 지정한다.

고정 alpha와 ionized phase의 electron factor chi_e=n_e/n_H 아래에서
\[
r_{\rm rec}=\alpha\chi_e\bar n_H Q_V\delta_I^2 C_I.
\]
Global C_HII=<n_HII^2>/<n_HII>^2는 C_I/Q_V다. 두 clumping 정의를 바꾸면 Q의 power도 바뀌므로 C_I와 C_HII를 무기록 치환하지 않는다. alpha(T)와 electron factor가 변하면 exact average <alpha n_e n_p>로 돌아간다.

Closed matter/photon 경계, delta_I=1와 dot(delta_I)=0, negligible photon-storage derivative·threshold loss·other sink·extra ionization, 일관된 alpha_B OTS를 추가하면
\[
\boxed{\dot Q_V=
\frac{\dot n_{\rm ion}^{\,c}}{\bar n_H^{\,c}}
-\frac{Q_V}{t_{\rm rec}},\quad
t_{\rm rec}^{-1}=\alpha_B\chi_e C_I\,\bar n_H^{\,c}a^{-3}.}\tag{Q}
\]
Madau et al. 1999의 Eq18 proper bubble volume에는 3H V_I가 있지만, Eq20의 dimensionless filling factor에는 별도의 dilution이 없다. 원 논문도 clumping을 평균할 수 있는 scale와 thin-front 한계를 전제한다. Q=1 도달 후 source surplus는 photon storage나 loss로 가야 하며 Q를 clip하고 나머지를 삭제하면 inventory가 깨진다.

문헌의 Q라는 문자만으로 volume filling factor라고 판정하면 안 된다. Madau et al. 1999 Eq20은 ionized-region filling factor를 대상으로 하지만, Gnedin & Madau 2022 Eq32 다음 정의는 Q=<n_HII>/<n_H>라는 mass/nuclei-weighted fraction이다. 후자의 Eq33을 현재 표기로 옮기면 먼저 X_M에 대응시켜야 한다. Q_V와의 동일시는 위의 density/phase 조건을 별도로 확인한다. Gnedin & Madau의 publisher Eq39 렌더링은 재결합 곱에 n_HI를 보이므로 그대로 전사하지 않는다. 같은 논문의 Eq35 및 원자 반응 의미와 일치하는 n_e n_HII를 사용하고 source-ledger에 이 표기 충돌을 남긴다.

## 7. Case-A/B와 재결합 photon ownership

1. Case-A primary-bath/open-radiation mode: alpha_A로 matter recombination을 제거하고 J_rec_tracked=0이다. Recombination radiation은 tracking 밖 reservoir로 export한다. 이때 (I)의 net loss는 R_A다. Export를 별도의 동일 photon sink로 또 빼면 double counting이다. 이는 선언된 tracked inventory의 모형이며 실제 전체 우주에서 ground-continuum photons가 사라진다는 주장이 아니다.
2. Explicit diffuse mode: matter는 alpha_A, radiation은 실제 spectrum에서 J_rec를 센다. Pure H ground capture가 한 ionizing photon을 내고 다른 ionizing recombination tails를 무시할 수 있는 제한에서 J_rec=R_1=R_A-R_B이다. 그러면 합산 inventory는 R_B를 갖는다. 이 합산 cancellation 자체에는 즉시흡수 가정이 필요하지 않고 photon storage는 남는다.
3. Local OTS Case-B mode: ground capture와 같은 H의 즉시 재이온화를 함께 소거하여 alpha_B와 primary photons만 남긴다. 이때 같은 ground source를 명시적으로 다시 더하면 안 된다.

고온 free-bound tails, helium cross-absorption, secondary ionization, finite escape/redshift는 위 단순 ground-photon 상쇄를 수정한다. alpha_A→alpha_B 변경은 source provenance와 closure 변경이며 단순 속도 최적화가 아니다.

## 8. 후속 coupled controlled model: 이번 E3에서 미실행

Primary bath의 초기 spectrum과 source를 nu^-p, p>1로 두고, nu≥nu_0에서 grey absorption sigma가 주파수와 무관하며 온도·atomic coefficient를 prescribed input으로 주면 redshift·grey loss·동일 기울기의 source는 power-law shape를 보존한다. y=n_gamma,>/n_H, Gamma=c sigma n_H y이므로
\[
\dot x=c\sigma n_H(1-x)y-\alpha_A n_Hx^2,\quad
\dot y=s-c\sigma n_H(1-x)y-H(p-1)y,
\tag{CANDIDATE}
\]
\[
\dot(x+y)=s-\alpha_A n_Hx^2-H(p-1)y,\quad
n_H=n_{H0}a^{-3}.
\]
Threshold loss H(p-1)y는 해당 ansatz 안에서 정확하다. p>2를 택하면 상한 없는 photon energy integral도 유한하다. 그러나 이 식은 grey power-law·isothermal·recombination-radiation export라는 후속 controlled 모형이며, 이번 연구 루프에서 coupled x+y trajectory를 실행한 결과가 아니다. 실제 UV spectral fit, energy evolution, geometric filling 또는 Bianchi 결과도 아니다. 향후 actual Case-A provider를 유지하면서 cosmological expansion/redshift adapter를 검산하는 후보로 둔다.

이번 실제 E3는 source-free·collisionless photon-only finite-band power-law trajectory다. p=3에서 각 고정 proper-frequency group의 comoving count가 N_g∝exp(-2s), s=ln(a/a_initial)을 따르는 특수 경우를 native photon adapter로 검산했다. 유한 band의 최고 경계에는 연장된 power-law tail에서 오는 nonzero redshift inflow를 명시적으로 공급하므로, 위의 무한 upper-boundary 소멸 조건과 구별한다. 이 검사는 coupled matter/photoabsorption/recombination history를 실행하지 않았다. 실행 판정·호출 수·수렴 오차의 권위 있는 기록은 research/INDEPENDENT_EXPERIMENT_PLAN.json의 E3와 evidence/PHOTON_HISTORY_RESULT.json이다.

## 9. 분석적 반례와 actual code의 판정 범위

ANALYTIC_FIXTURES.json에 dilution, density bias, ionization morphology, rate covariance, advection/compression, open-boundary normalization, moving threshold, group telescoping, storage, OTS double counting, phase-density dynamics의 명시적 예를 둔다. 값은 직접 식으로 도출한 expected value이며 각 실행 여부는 runtime evidence에 기록한다.

현재 F03 static Case-A input과 새 cosmological/redshift example은 분리한다. F03 source-bound absorption/species identity가 통과해도 F04의 nonlinear map certificate, 실제 cosmological history, arbitrary spectrum edge closure, geometric filling law가 자동 통과하지 않는다. 기존 엄격 오차 gate와 historical failure는 이 이론 문서로 변경되지 않는다.

원전:

- Mellema et al., C2-Ray, arXiv:astro-ph/0508416v2; DOI 10.1016/j.newast.2005.09.004. Local rate와 동일 absorbed-photon event 사용 원리.
- Madau, Haardt & Rees, arXiv:astro-ph/9809058v1; DOI 10.1086/306975. Eq2 spectral intensity, Eq18 proper bubble volume, Eq20 filling factor.
- Haardt & Madau, arXiv:1105.2039v3; DOI 10.1088/0004-637X/746/2/125. Eq1 cosmological RT, Eqs17–19 photoionization/recombination와 species density.
- Gnedin & Madau, 2022, DOI 10.1007/s41115-022-00015-5. Eq32 뒤 Q 정의와 Eq33의 표기 차이를 확인하는 보조 원전; 평균·transport 유도의 기초 식은 위 연구 논문과 직접 유도에 둔다.

원 논문을 일반 closure의 증명으로 과장하지 않는다. 추가 평균·경계·좌표변환과 후속 coupled grey ansatz는 위 가정에서 이번에 직접 유도한 계약이며 실제 E3의 실행 범위와 구별한다.
