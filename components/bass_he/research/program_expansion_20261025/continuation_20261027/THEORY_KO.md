# HE-EXP-DRIFT-02: 같은 탄성 사건에서 얻는 작은 drift의 종별 열원

## 결과, 의존성, 근거 상태

PR102의 무 drift 열교환과 drift 1차 힘을 재사용하고, 같은 충돌법칙으로부터 종별 centered heat를 drift 2차까지 유도한다. 필요한 새 source 정보는 같은 상대 Maxwell 온도에서의 `Qbar12`다. 이 문서의 식은 아래 가정하에서 **derived**다. 실제 H–He fit 평가, isotope/mass binding, calibrated source uncertainty 및 physical-provider admission은 별도 입력 상태로 유지한다. 기존 HE101 C8/19-of-20/reserve0/PASS-FAIL-FAIL과 INTAKE01 실행원장은 변경하지 않는다. 새 계산이나 원 suite의 재실행 근거를 이 문서가 만들지 않는다.

재사용 기준은 BASS_HE commit `ac6042a6b0610b09d0576538767ee0299389a5eb`, 다음 경로다.

- `research/program_expansion_20261025/continuation_20261025/exchange/THEORY_KO.md`, blob `eba18f405465eae954682c05f790df6312805d5a`: finite-mass 탄성 사건의 raw/centered 에너지 관계.
- `research/program_expansion_20261025/continuation_20261025/pair_source/THEORY_KO.md`, blob `520d6a80832638dfb878040c050b8a791d38f6ff`: Bruno thermal-integral 정규화, 무 drift G 및 선형 K.
- 같은 `pair_source/CONTRACT.json`, blob `2f70d4fd22886342517d58afe57bb83212e5ace9`: H–He source-label, 50–50000 K 범위, isotope/mass와 불확실성의 열린 입력.
- 같은 `exchange/exchange_closure.py`, blob `931016f58d483ff2f061f3935e5fb9503b04c943`: raw-to-centered heat, energy/count ownership adapter.

공식 upstream 데이터는 `mutationpp/Mutationpp` commit `58678c0e038eb2f078fed3b45640741fdaf167dc`의 `data/transport/collisions.xml`이다. 정규화 구현의 원본 `CapitelliIntegrals.cpp`와 `.h`는 PR102의 `pair_source/upstream/`에 각각 blob `31de4007829f0149121e7b6adb99c2070cd5d4fe`, `27d6e7346d1c65deb0971947adb1620674f98a01`로 보존되어 있다. 기존 intake가 원문 정규화와 바이트를 보존한다. 아래 유도와 polynomial control은 기존 결과 이후의 새 계산이며 새 문헌 발견이나 physical calibration을 주장하지 않는다.

## 1. 가정과 단위

국소 정규직교 frame, metric signature `(-,+,+,+)`, proper time와 proper volume를 쓴다. 두 구별되는 종 a,b는 일정한 kinetic mass `m_a,m_b>0`, 양의 온도 `T_a,T_b`, 수밀도 `n_a,n_b>=0`를 가진 고전 비상대론적 Maxwell 분포다. 내부 상태와 species particle count는 탄성 사건에서 고정된다. Maxwell 분포의 무한 속도 support는 비상대론적 kinetic model의 이상화이며 물리 적용에서는 열속도와 bulk 속도의 상대론적 tail 오차가 유효범위에 들어야 한다.

분포는 서로 독립이고 각 종의 온도는 스칼라다. 비열적 입자, 비등방 pressure tensor, chemical reaction, internal transition, nuclear mass defect, photon momentum은 이 모델의 입력이 아니다. source는 상대속도 축에 대해 회전불변인 탄성법칙이며, 전체 COM 각도에 대해

\[
\sigma_1(g)=\int (1-\cos\chi)\,d\sigma(g,\chi)\ge0
\tag{1}
\]

를 공급한다고 가정한다. `sigma_1`의 차원은 m²다. 아래 결과는 이 transport moment만 사용한다. `sigma_0`, quadrupole moment, differential law 또는 joint recoil distribution은 여기서 복원하지 않는다. Forward scattering의 미분 단면적이 특이하더라도 (1)과 아래 필요한 속도 모멘트가 유한하면 이 momentum/energy 유도는 적용된다.

질량은 kg, 속도는 m/s, 온도는 K, 열원은 W/m³, 힘 source는 kg/(m² s²)다. `k_B`를 유지한다. `c`와 `hbar`는 이 고전 kinetic 식에 나타나지 않으며 1로 둔 것이 아니다. 종이 구별되므로 pair collision counting에 동일종의 `1/2`를 삽입하지 않는다.

## 2. 비영 drift에서 Gaussian conditional mean

다음을 정의한다.

\[
M=m_a+m_b,\quad a={m_a\over M},\quad b={m_b\over M},\quad
\mu={m_am_b\over M},\qquad a+b=1,
\tag{2}
\]
\[
\mathbf U=\mathbf u_a-\mathbf u_b,\qquad
\mathbf V_c=a\mathbf u_a+b\mathbf u_b,\qquad
T_*=bT_a+aT_b,\quad s^2={k_BT_*\over\mu},
\tag{3}
\]
\[
\beta={\mu(T_a-T_b)\over MT_*}={ab(T_a-T_b)\over T_*}.
\tag{4}
\]

`V_c`는 한 pair의 mass-weighted mean이며 수밀도를 포함한 전체 mixture bulk와 구별한다. 한 pair의 미시적 변수는 `g=v_a-v_b`, `V=a v_a+b v_b`다. 독립 Maxwell 분포에서

\[
\mathbf g\sim\mathcal N(\mathbf U,s^2 I),\qquad
\operatorname{Cov}(V_i,g_j)={k_B(T_a-T_b)\over M}\delta_{ij}.
\]

따라서 공동 Gaussian의 조건부 평균은 정확히

\[
\boxed{\mathbb E[\mathbf V\mid\mathbf g]
=\mathbf V_c+\beta(\mathbf g-\mathbf U).}
\tag{5}
\]

이는 PR102의 `U=0` 조건부 평균을 일반화한다. 온도가 달라도 `V`와 `g`의 잔여 조건부 fluctuation은 평균 0이어서 에너지 1차 모멘트에 추가 항을 만들지 않는다.

## 3. 같은 사건으로부터 얻는 정확한 힘과 centered heat

탄성 운동학은

\[
\Delta\mathbf p_a=\mu(\mathbf g'-\mathbf g)=-\Delta\mathbf p_b,
\qquad
\Delta E_a=\mathbf V\cdot\Delta\mathbf p_a=-\Delta E_b.
\tag{6}
\]

이다. 각도 적분과 collision flux `g`를 포함하고 정규화된 shifted Maxwell 평균을 `<>_U`로 쓰자.

\[
C=n_an_b\mu,\qquad
\mathbf A(\mathbf U)=\langle g\sigma_1(g)\mathbf g\rangle_{\mathbf U},\qquad
B(\mathbf U)=\langle g^3\sigma_1(g)\rangle_{\mathbf U}.
\tag{7}
\]

`[C]=kg/m^6`, `[A]=m^4/s^2`, `[B]=m^5/s^3`다. Raw 보존형 source는

\[
\mathbf R_a=-C\mathbf A,\quad\mathbf R_b=C\mathbf A,
\]
\[
E_a=-C\{\mathbf V_c\cdot\mathbf A+\beta[B-\mathbf U\cdot\mathbf A]\},
\qquad E_b=-E_a.
\tag{8}
\]

species count가 고정이므로 중심 열원은 `Q_s=E_s-u_s dot R_s`다. `V_c-u_a=-bU`, `V_c-u_b=aU`를 대입하면

\[
\boxed{Q_a=C[(b+\beta)\mathbf U\cdot\mathbf A-\beta B],
\quad Q_b=C[(a-\beta)\mathbf U\cdot\mathbf A+\beta B].}
\tag{9}
\]

`b+beta=b T_a/T_*`, `a-beta=a T_b/T_*`도 동일한 식이다. 직접 합으로

\[
\boxed{Q_a+Q_b=C\mathbf U\cdot\mathbf A
=-\mathbf U\cdot\mathbf R_a,\qquad
E_a+E_b=0.}
\tag{10}
\]

을 얻는다. 이것은 drift bulk energy의 감소와 두 종의 centered kinetic energy 증가가 같은 사건으로 연결된다는 식이다. 총량 `-U dot R_a`를 `Q_a,Q_b`에 더하는 별도의 heating source로 사용하면 이중 계산이다.

Gaussian density를 `U`로 미분하면

\[
\partial_{U_j}f_{\mathbf U}={(g_j-U_j)\over s^2}f_{\mathbf U},
\qquad
s^2\nabla_{\mathbf U}\cdot\mathbf A=B-\mathbf U\cdot\mathbf A.
\]

따라서 유도 경로가 다른 동등식은

\[
\boxed{Q_a=C[b\mathbf U\cdot\mathbf A-\beta s^2\nabla_{\mathbf U}\cdot\mathbf A],
\quad Q_b=C[a\mathbf U\cdot\mathbf A+\beta s^2\nabla_{\mathbf U}\cdot\mathbf A].}
\tag{11}
\]

이는 실제 nonlinear drag가 주어졌을 때 그 Gaussian 평균의 divergence로 열교환을 계산하는 정확한 관계다. 새로운 비열분포에 그대로 적용하지 않는다.

## 4. Taylor 전개를 정당화하는 조건

`T_a,T_b>0`이므로 `s>0`이다. 어떤 속도 `U_0>0`에 대해 다음은 충분조건이다.

\[
\int_0^\infty g^4[1+(g/s)^5]\sigma_1(g)
\exp[-g^2/(2s^2)+gU_0/s^2]dg<\infty.
\tag{12}
\]

이 조건이면 `|U|<=U_0`에서 적분과 `A`의 5차 및 `B`의 4차 미분을 교환할 수 있다. Cross section 자체를 `g`에 대해 미분할 필요는 없다. Gaussian density만 미분한다. 아래 remainder의 계수는 이 weighted integral, `s`, 질량, 온도, 밀도에 의존한다. `sigma_1`의 충분히 완만한 high-speed growth와 적분 가능한 low-speed behavior는 (12)의 실용적인 충분조건이다.

`epsilon=|U|/s`가 작다는 말만으로 모든 가능한 cross section의 일정한 오차 상한을 얻지는 않는다. High-speed에 집중된 transport weight는 큰 모멘트 비율을 가질 수 있다. 실제 finite tolerance는 공급된 speed law 또는 필요한 weighted-moment/remainder bound로 고정해야 한다. 유한 개 independently fitted thermal rows만으로 full-domain truncation bound를 만들지 않는다.

이하 `J_r=<g^r sigma_1(g)>_0`로 둔다. Shifted density

\[
f_{\mathbf U}=f_0\exp[(\mathbf g\cdot\mathbf U)/s^2-U^2/(2s^2)]
\]

와 등방 tensor 평균을 사용하면

\[
\mathbf A={J_3\over3s^2}\mathbf U
+\left({J_5\over30s^6}-{J_3\over6s^4}\right)U^2\mathbf U+O(U^5),
\tag{13}
\]
\[
B=J_3+\left({J_5\over6s^4}-{J_3\over2s^2}\right)U^2+O(U^4).
\tag{14}
\]

예를 들어 `A`의 3차항에서
`<g_i g_j g_k g_l F(g)>=(<g^4 F>/15)(delta_ij delta_kl+delta_ik delta_jl+delta_il delta_jk)`를 사용했다. `A`는 `U`의 홀함수, `B`는 짝함수다. 적분 우세조건이 없을 때 이 formal expansion을 오차 보증으로 승격하지 않는다.

## 5. Qbar11,Qbar12를 사용한 2차 열원

PR102 source 정규화에서 `g_0=sqrt(2)s`, `gamma=g/g_0`이며

\[
q_{11}=\overline Q_{11}=\int_0^\infty e^{-\gamma^2}\gamma^5\sigma_1(g_0\gamma)d\gamma,
\]
\[
q_{12}=\overline Q_{12}={1\over3}\int_0^\infty e^{-\gamma^2}\gamma^7\sigma_1(g_0\gamma)d\gamma.
\tag{15}
\]

따라서

\[
J_3={4g_0^3\over\sqrt\pi}q_{11}
=4s^2\bar g q_{11},\quad
J_5={12g_0^5\over\sqrt\pi}q_{12},\quad
{J_5\over J_3}=6s^2{q_{12}\over q_{11}},\qquad
\bar g={2g_0\over\sqrt\pi}.
\tag{16}
\]

`q11>0`인 채널에 대해

\[
K={CJ_3\over3s^2}={4\over3}n_an_b\mu\bar g q_{11},\qquad
G={3k_BK\over M},\qquad r_{12}={q_{12}\over q_{11}},\quad H={5\over2}-3r_{12}.
\tag{17}
\]

`[K]=kg/(m^3 s)`, `[G]=W/(m^3 K)`다. 식(9),(13),(14)를 결합하면

\[
\boxed{\begin{aligned}
\mathbf R_a&=-K\mathbf U+O(U^3),\qquad \mathbf R_b=-\mathbf R_a,\\
Q_a&=G(T_b-T_a)+K[b+\beta H]U^2+O(U^4),\\
Q_b&=G(T_a-T_b)+K[a-\beta H]U^2+O(U^4).
\end{aligned}}
\tag{18}
\]

같은 결과를 `A`의 divergence를 이용한 식(11)로도 얻는다. Linear drag와 quadratic heat를 함께 채택한 truncated model에서는

\[
Q_a^{[2]}+Q_b^{[2]}=KU^2=-\mathbf U\cdot\mathbf R_a^{[1]}
\tag{19}
\]

가 대수적으로 정확하다. 나중에 cubic drag를 추가하면 대응하는 quartic heat 합도 같은 차수로 추가해야 한다.

`q11=0`이 positive transport law에서 정확한 값이면 `sigma1=0`이 Gaussian weight에 대해 거의 모든 곳에서 성립하며 `q12=0`, 모든 교환 source가 0이다. `q11=0,q12>0`는 이 same-law positive measure와 양립하지 않는다. 수치 fit의 0을 물리적인 zero law로 임의 해석하지 않는다. 구현은 선언된 zero-law 경로 또는 양의 `q11` 경로를 명시해야 한다.

### 개별 quadratic 항의 해석

`b+beta H`와 `a-beta H`의 합은 1이지만, `Ta!=Tb`에서는 각각의 범위를 `[0,1]`로 제한할 근거가 없다. Drift가 기존 temperature-exchange rate도 바꾸기 때문이다. 음의 개별 quadratic correction을 0으로 clamp하면 식(18)의 같은 사건에서 유도한 값과 energy balance를 바꾼다. `Ta=Tb`일 때만 `beta=0`이고 두 항은 순수 frictional heat의 양의 분율 `b,a`다.

큰 두 항의 상쇄로 `Q_a` 자체가 작아질 수 있으므로 component 값 `G(Tb-Ta)`, `K(b+beta H)U²`와 absolute scale를 함께 보존한다. 작은 total heat에 대한 relative error 하나로 truncation을 판정하지 않는다.

## 6. 같은 law의 thermal-row 미분 identity와 fit diagnostic

질량, internal state, screening/medium parameter를 고정하고 `sigma1(g)`에 명시적 `T_*` 의존성이 없다고 하자. (15)를 `g` 적분으로 바꾸면

\[
q_{11}=g_0^{-6}\int_0^\infty g^5\sigma_1(g)e^{-g^2/g_0^2}dg.
\]

`g_0²`가 `T_*`에 비례하므로

\[
\boxed{T_*{dq_{11}\over dT_*}=3(q_{12}-q_{11}),\qquad
T_*{d\log q_{11}\over dT_*}=3(r_{12}-1).}
\tag{20}
\]

따라서 같은 exact law에서는

\[
H=-{1\over2}-T_*{d\log q_{11}\over dT_*},\qquad
Q_a^{[2]}=G(T_b-T_a)+K\left[b-\beta{d\log K\over d\log T_*}\right]U^2.
\tag{21}
\]

source의 두 행을 서로 독립적으로 fitting했으면

\[
\mathcal D(T_*)={T_*\over q_{11}^{fit}}{dq_{11}^{fit}\over dT_*}
-3\left({q_{12}^{fit}\over q_{11}^{fit}}-1\right)
\tag{22}
\]

를 행간 일치도 diagnostic으로 기록할 수 있다. Row-based heat와 derivative-based heat의 차이는

\[
Q_{a,row}^{[2]}-Q_{a,derivative}^{[2]}=+K\beta\mathcal D U^2,
\quad
Q_{b,row}^{[2]}-Q_{b,derivative}^{[2]}=-K\beta\mathcal D U^2.
\tag{23}
\]

이다. 이것은 두 approximation의 차이를 계산한 값이며 calibrated physical uncertainty, isotopic error 또는 full angular-law error가 아니다. 어느 행을 수정하거나 `q12`를 derivative로 대체하려면 source error와 모델 결정을 따로 기록한다. Source domain 밖에서 derivative 평가를 허용하는 근거도 되지 않는다.

같은 정의의 더 높은 행에는 일반적으로

\[
T_*{d\overline Q^{(\ell,j)}\over dT_*}
=(j+2)[\overline Q^{(\ell,j+1)}-\overline Q^{(\ell,j)}]
\tag{24}
\]

가 성립한다. source의 fixed law, fixed state, fixed reduced mass 조건을 유지해야 한다. Temperature-dependent effective interaction이면 우변에 `sigma`의 명시적 temperature derivative 적분이 추가된다. Coulomb screening 또는 population-dependent effective law에 (20),(24)를 무조건 적용하지 않는다.

## 7. 독립 기대값: Gaussian polynomial control

다음은 실제 H–He source의 모델이 아니라 새 대수 구현을 구별해 검사할 합성 control이다. 원 PR102 suite를 다시 실행할 이유가 되지 않는다. 이 문서 단계에서는 기대값을 유도했으며 실행은 부모의 새 bounded validation ledger가 소유한다.

### Control A: sigma1(g)=Lambda/g

`Lambda>0`의 단위는 m³/s다. 이때 `g sigma1=Lambda`이고 Gaussian 기본 모멘트만으로

\[
\mathbf A=\Lambda\mathbf U,\qquad
B=\Lambda(U^2+3s^2),
\]
\[
\mathbf R_a=-C\Lambda\mathbf U,
\quad Q_a=C\Lambda[bU^2-3\beta s^2],
\quad Q_b=C\Lambda[aU^2+3\beta s^2].
\tag{25}
\]

를 **모든 U에서 정확히** 얻는다. `q11=3 sqrt(pi) Lambda/(8g0)`, `q12=5 sqrt(pi) Lambda/(16g0)`, 따라서 `r12=5/6`, `H=0`, `K=C Lambda`다. 위 기대값은 code의 열원 공식을 그대로 계산해 비교하는 방식이 아니라 `g sigma1`가 상수인 원 integrand의 Gaussian 평균에서 얻는다.

### Control B: sigma1(g)=Lambda g

이번 `Lambda>0`의 단위는 m s다. `g sigma1=Lambda g²`이므로 Wick/Gaussian 모멘트에서

\[
\mathbf A=\Lambda(U^2+5s^2)\mathbf U,
\qquad
B=\Lambda(U^4+10s^2U^2+15s^4).
\]

이로부터 원 정확한 source는

\[
\mathbf R_a=-C\Lambda(U^2+5s^2)\mathbf U,
\]
\[
Q_a=C\Lambda[bU^4+5(b-\beta)s^2U^2-15\beta s^4],
\]
\[
Q_b=C\Lambda[aU^4+5(a+\beta)s^2U^2+15\beta s^4].
\tag{26}
\]

`q11=15 sqrt(pi) Lambda g0/16`, `q12=35 sqrt(pi) Lambda g0/32`, `r12=7/6`, `H=-1`, `K=5C Lambda s²`다. 따라서 제안한 truncated source와의 잔차는 정확히

\[
\mathbf R_{a,exact}-\mathbf R_a^{[1]}=-C\Lambda U^2\mathbf U,
\quad
Q_{a,exact}-Q_a^{[2]}=C\Lambda bU^4,
\quad
Q_{b,exact}-Q_b^{[2]}=C\Lambda aU^4.
\tag{27}
\]

이다. `U`를 1/2로 줄이면 force residual은 1/8, heat residual은 1/16이 되는 정확한 판별 기준을 제공한다. Floating subtraction이 작은 잔차를 소거하지 않도록 입력 크기와 comparison scale를 고정한다. 이 control은 실제 source 속도 적분이나 physical fit의 정확도를 검사하지 않는다.

### 추가 수학적 점검

- Zero drift: (18)은 기존 `Qa=G(Tb-Ta)`, `Qb=-Qa`와 일치한다.
- Equal temperature: `Qa=b K U²`, `Qb=a K U²`; equal mass이면 1/2씩이다.
- Species exchange: `a<->b`, `Ta<->Tb`, `U->-U`, `beta->-beta`에서 a,b의 source가 교환된다.
- Galilean boost: `ua,ub`에 같은 속도를 더해도 `U,T*,beta,Qa,Qb`는 불변이다. Raw 에너지는 (8) 또는 `Es=us dot Rs+Qs`로 변환한다.
- Infinite target mass: 온도와 projectile mass를 고정하면 `mu/M->0`, `beta->0`, `G->0`이고 projectile drift randomization은 `Qa->K U²`, target heat는 0으로 간다. source가 그 mass limit에서 유효한지는 별도 물리 입력이다.
- Density zero: 한 밀도가 0이면 힘과 열원은 0이다.
- General power law `sigma1=Sigma(g/v_ref)^p`의 적분이 존재하면 `r12=(p+6)/6`, `H=-(p+1)/2`; 실제 cosmic source의 power law를 가정하는 주장은 아니다.

## 8. 구현 계약과 소유권

새 adapter는 기존 PR102의 `G,K,T*` 계산을 재사용하고 같은 `T*`에서의 `q12` 및 row provenance를 추가로 받는다. 반환에는 최소한 `U²`, `beta`, `q12/q11`, 0차 temperature exchange, 두 종의 2차 correction, total `K U²`, force order1/heat order2, 미인증 remainder 상태를 보존한다. 출처가 다른 temperature 또는 source identity의 두 행을 조용히 섞지 않는다. Physical source approval과 source uncertainty를 이 대수 계산이 생성하지 않는다.

새 식은 `Gamma_a=Gamma_b=0`인 탄성 채널이다. `n_th`, `C_V`, chemical binding, internal excitation, nuclear Q, nonthermal reservoir의 owner를 바꾸지 않는다. 별도 source에서 생성된 fast particle의 birth energy를 (18)의 thermal heat에 더하지 않는다. 공통 bulk와 공통 temperature reduction을 사용하려면 그 시간척도 및 observable error 근거를 별도로 유지한다. 여기서는 두 서로 다른 온도와 bulk를 그대로 허용한다.

수용 기준은 원 integrand로부터 얻은 controls (25)–(27), source-row normalization, 보존식(19), species/frame symmetries, zero-density/zero-drift, 분리된 provenance와 finite-domain 입력 검사다. 동일 구현을 두 번 호출한 비교나 fit-row 잔차만으로 물리 공급자를 승인하지 않는다. 새 strong no-go를 제안하지 않으므로 NG1–NG7에 해당하는 새 배제 성과는 없다.
