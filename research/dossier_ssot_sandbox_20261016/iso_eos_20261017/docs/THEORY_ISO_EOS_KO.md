# ISO-EOS: H/He/D 혼합기체 및 charge-exchange 열화학의 구성적 정식화

**범위:** 고유 부피에 고정된 비상대론적 단일온도 gas EOS + 하나의 H/D thermal CX event, 공변 연속계의 온도 방정식. 이 문서는 `ISO-COUPLE`의 완전한 질량작용 네트워크·EoR 적분을 완료했다는 뜻이 아니다.

## 1. 실제 소스와 연구선언

- Frozen parent: `cosmosapjw-quantum/rei_bianchi` PR #150 `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7`, 원본 `deuterium_thermal_charge_exchange.rs`, `deuterium_charge_exchange.rs`, `isotope_state.rs`, `deuterium_thermal_coupling.rs`. 사본의 Git blob SHA가 원본과 **일치**하도록 restoration에서 검증한다.
- `IsotopeNumberState` 원본 13개 상태: n, H⁰/H⁺, D⁰/D⁺, T⁰/T⁺, ³He⁰/⁺/²⁺, ⁴He⁰/⁺/²⁺. `Be7`, ⁶Li, ⁷Li, 다중준위 들뜬상태는 **이 타입 안에 없다**. 원 dossier 17-entry 벡터와 동일하다고 선언하지 않는다.
- Savin (2002), *ApJ* 566, 599–603, DOI [10.1086/324218](https://doi.org/10.1086/324218)에서 H⁺ + D⁰ ⇌ H⁰ + D⁺ 속도계수. 논문 범위 ~1–2×10⁵ K와 별개로 **기존 Rust 공급자 허용 범위 2.7–200000 K** 고정. Reaction energy defect `δχ=χ_D−χ_H`는 원자 공급자의 별도 자료여야 하며, 이번 수치 예제의 **0.0037 eV는 제조된 입력이지 실측·공급자 잠금값이 아니다**.
- Stancil, Lepp & Dalgarno (1998), [10.1086/306473](https://doi.org/10.1086/306473): 원시 D/He 네트워크 및 분자 경로가 중요하다는 범위 경고. 현재 간단한 CX 참조는 그 문헌의 144개 반응 모형을 대신하지 않는다.

## 2. 핵자·전하·열용량

우주론에서 원자종 번호 밀도 `n_s`는 **고유 부피당 m⁻³**. 여기서는 비열평형·전자 상대론·퇴화·핵반응 잔여 등을 무시한 common-temperature monatomic ideal-gas closure:

\[
 n_B=\sum_s A_s n_s,\quad n_e=\sum_s q_s n_s,\quad n_h=\sum_s n_s,\quad n_{th}=n_h+n_e,
 \quad u_{th}=\tfrac32 k_B n_{th}T,\quad p_{th}=k_B n_{th}T.
\]

여기서 `q_s`는 핵의 이온 전하수로서 원자당 단일 혹은 이중 이온화 전자 수이다. 방출 전자와 이온화된 원자의 전자를 별도 중복 계상하지 않는다. 중성자도 모형에 보존되는 비상대론적 열적 입자로 명시될 때만 `n_h`에 기여한다. 위 `n_B`는 **수소핵 개수**와 다르다. 재결합/재이온화 초기 적색편이·He 질량분율로부터 혼용하면 안 된다.

따라서 고정 조성의 `C_V=(3/2) k_B n_th` [J m⁻³ K⁻¹]. He⁰, He⁺, He²⁺는 각각 무거운 입자 하나에 더해 자유전자 0,1,2개를 제공한다. Ionized helium spectator는 H/D CX에는 화학량론적으로 참여하지 않아도 thermal capacity 및 `n_e`에 포함되어야 한다.

## 3. 단일 H/D CX 사건의 구조 보존

독립적인 전진 반응 extent `ξ` [m⁻³]로 `H⁺+D⁰→H⁰+D⁺`를 정하면, 화학량론 벡터(정렬 H⁰,H⁺,D⁰,D⁺)는 `ν=(+1,−1,−1,+1)`. 단위 열용량 입자 가중치 `(1,2,1,2)`, 핵자 `(1,1,2,2)`, 전하 `(0,1,0,1)`이므로

\[
 A\cdot\nu=0,\quad q\cdot\nu=0,\quad (1+q)\cdot\nu=0.
\]

Wolfram Language에서 이 세 내적을 직접 계산하여 모두 0인 것을 확인했다. He/T/기타 spectator 요소는 `ν=0`으로 정적 유지한다. 따라서 독립 공급자가 준 `δχ=χ_D−χ_H`에 대해

\[
 \Delta u_{chem}=\delta\chi\,\xi,\quad \Delta u_{th}=-\delta\chi\,\xi,
 \qquad \Delta T=-\frac{\delta\chi\,\xi}{(3/2)k_B n_{th}}.
\]

이 사건에는 광자 방출·CMB·free-free가 **없으며** 해당 사건의 원장은 0으로 남긴다. 다른 원자·복사 사건에는 자체 소유자가 필요하다. `ξ∈[-min(n_{H0},n_{D+}),min(n_{H+},n_{D0})]` 및 `u_th>=0`, `T∈[2.7,200000] K`를 위반하면 projection/clipping 없이 typed error를 반환한다.

국소시간 rate은 실제 원본 `Savin2002::rates`로
\[
 R_{CX}=k_f(T)n_{H+}n_{D0}-k_r(T)n_{H0}n_{D+},\qquad
 \dot T\big|_{CX}= -\frac{\delta\chi\,R_{CX}}{(3/2)k_B n_{th}}.
\]

이 식은 순간 RHS이고 시간적분이나 적응형 event solver가 아니다. 기존 `ThermalCxComponent`의 `UnsupportedSpectator`를 비활성화하지 않는다.

## 4. 팽창 기하에서의 온도 방정식

공통 중력계·물질 속도 uᵃ에 대해 `Θ=∇ᵃu_a`, `dot n_s+Θ n_s=Σ_r ν_sr R_r`, `dot n_th+Θn_th=R_part`, `R_part=Σ_s(1+q_s)Σ_r ν_sr R_r`. 비상대론적 내부 운동에너지 balance (조건부 무열류, 무점성 gas) `dot u_th+Θ(u_th+p_th)=Q_other−δχ R_CX`를 쓰면

\[
\boxed{\dot T=-\frac23\Theta T
 +\frac{Q_{other}-\delta\chi R_{CX}}{(3/2)k_Bn_{th}}
 -\frac{T}{n_{th}}R_{part}.}
\]

이 식은 선택한 화학에너지 기준을 이미 분리한 전개식이다. CX 한 반응에서 `R_part=0`; 일반 광이온화/재결합에서는 마지막 term이 빠지면 안 된다. 비기울어진 FLRW에서는 Θ=3H, 축대칭 Bianchi I normal congruence에서도 Θ=H₁+H₂+H₃=3H_mean. 그러나 비등방성 stress/shear work, tilt, different species temperatures, thermalization of nonthermal daughters는 이 gas closure의 밖이고 별도 보존 원장으로 되돌려야 한다.

## 5. Scope tests, expected scientific interpretation

제조된 H⁰=1000,H⁺=500,D⁰=50,D⁺=50 m⁻³의 10000 K 모델에서 n_th=2150m⁻³. He⁰=200,He⁺=200,He²⁺=100 m⁻³를 추가하면 `n_th=3050m⁻³`, 전자 수는 550→950m⁻³. H/D와 T를 고정했을 때 동일한 `ξ=10 m⁻³`, `δχ=0.0037 eV`의 순간 변화는 `ΔT_pure≈−0.133137 K`, `ΔT_He≈−0.093851 K`, ratio `2150/3050≈0.704918`. 이것은 **제조된 차폐·열용량 예제**이고 물리적 원시 원소 abundance를 대변하지 않는다.

검증된 것은 상대적인 thermal capacity, baryon/charge/energy cancellation, pure-H/D source mapping과 domain guards. **미검증:** native full-ionization RHS + He spectator CX time substep, source-on photon/gas ownership 결합, Bianchi expansion stiff step convergence, entire EoR chemical spectra and observation. 이는 독립 `ISO-COUPLE`에서 계속한다.
