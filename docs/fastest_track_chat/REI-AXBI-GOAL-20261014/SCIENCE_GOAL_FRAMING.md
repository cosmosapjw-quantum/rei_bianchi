# Non-tilted axisymmetric Bianchi-I reionization: abundance history·그림 최종 계약

2026-10-14, read-only framing. 확인한 checkout: `477f3756044df89ff63cceb6b432e63015c07f0a`, branch `codex/axisymmetric-reionization-goal-20261014`. 과학 코드·기존 기록·원격 상태를 변경하거나 solver/build/test를 실행하지 않았다. 아래 식은 현재 코드의 기하 convention을 축대칭으로 전개한 계약이며, 계산 결과나 새 scientific PASS가 아니다.

## 1. 최종 목표와 계산 단위

최소 최종 결과는 **선택한 source-backed homogeneous H/He 시나리오에서 non-tilted axisymmetric Bianchi-I 재이온화 이력을 완성하고, 표준 BBN abundance plot처럼 proper cosmic time과 gas temperature에 따른 핵종/이온 비율을 그리는 것**이다. 이를 위해 기하, gas thermochemistry 및 energy–angle ionizing radiation을 결합하고 FLRW와 비교한다. BBN식 그림 형식을 사용하지만, 물리 계산은 donor가 공급한 핵종 inventory의 ionization/recombination이며 BBN 핵반응 연소망이 아니다. 전역 목표 구간은 평균 scale factor로 정의한 `zbar=20 → 4`로 둔다. 실제 공급 domain이 짧으면 달성한 구간과 미완료 구간을 명시하고 checkpoint에서 이어간다. 짧은 warm 구간만으로 full EoR 목표를 완료 처리하지 않는다. 완성 기준은 선언된 전체 지원 재이온화 구간의 abundance/neutral-fraction 이력, 수치·물리 근거, 시간·온도 그림과 보고서다. τ/visibility는 secondary nonblocking 제품이며 full τ 또는 observer-tail admission을 이 기본 목표의 완료 조건으로 요구하지 않는다.

기본 중력 closure는 아래의 shear를 포함한 prescribed cosmological background이고, 재이온화 radiation·gas thermal 변화의 추가 중력 feedback은 test-field 근사로 분리한다. 이에 따른 최종 주장은 **명시한 배경/IC/source/provider/closure에 조건부인 homogeneous 재이온화 예측**이다. GR background constraint를 만족하는 이 family를 observationally admitted model이나 실제 관측 fit으로 간주하지 않는다. q의 수치 선택은 AX01/AX03의 source/scenario 결정으로 남긴다. tilt, 다른 Bianchi 분류, spatial ionization topology, full polarized CMB, 새로운 원자 연구는 이 결과의 선행 요구가 아니다. 결과·그림·보고서는 첫 구간부터 누적한다.

## 2. 정확한 기하·방사선 convention

`(-,+,+,+)`, proper time `t`[s], 명시적 `c, ħ, k_B`를 사용한다. gas는 normal congruence를 따른다. unit normal `n`은 `n·n=-1`이며 physical four-velocity `U=c n`은 `U·U=-c²`다. 기존 donor의 unit four-velocity `u`는 이 `n`과 같고, `x0=ct` convention과 호환된다. proper-time 좌표에서는 `U=∂t`, `n=(1/c)∂t`다.

\[
 ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2,
 \quad H=\dot a/a,\quad s=\dot b,
\]
\[
 H_\perp=H-s,\quad H_\parallel=H+2s,\quad
 V=a^3,\quad \sigma^i{}_j=\operatorname{diag}(-s,-s,2s),
 \quad \sigma^2\equiv\tfrac12\sigma^i{}_j\sigma^j{}_i=3s^2.
\]

이는 `bianchi_i.rs::AxisymmetricPoint::snapshot`과 같다. `ConstantAxisymmetricBackground`는 일정 H/s의 prescribed adapter이며 우주론적 배경을 공급하지 않는다. `GeometryBackground::snapshot(t)`의 새 cosmological 구현을 연결한다.

에너지 밀도 `ε`[J m⁻³], 평균 압력 `p`[Pa], cosmological constant `Λ`[m⁻²]에 대해 Einstein constraint와 축대칭 shear 식은

\[
 H^2={8\pi G\over3c^2}\epsilon+{\Lambda c^2\over3}+s^2,
 \qquad \dot s+3Hs={8\pi G\over3c^2}(p_\parallel-p_\perp).
\]

여기서 Λ는 ε에 다시 포함하지 않는다. 최소 배경은 selected isotropic background fluids의 anisotropic stress를 0으로 놓아 `s=s_* (a_*/a)^3`로 계산하고, `db/dln a=s/H`, `dt/dln a=1/H`를 함께 적분한다. 총 radiation을 isotropic background로 다루는 근사와 ionizing radiation의 test-field 처리를 문서화한다. 배경 stress를 달리 선택하면 자유감쇠 식을 그대로 사용하지 않는다.

비교 family는 동일한 reference mean scale factor `a_*`, **동일한 물리적 matter/radiation 밀도 및 Λ**에서 `q_ref=s_*/H_F(a_*)`를 case별 signed parameter로 정의한다. `q_amp>0`는 선택할 최대 campaign amplitude이며 `q_ref∈{0,±q_amp/2,±q_amp}`다. instantaneous normalized shear는 별도 기호 `Σ=s/H`로 기록한다. `H_F`는 그 입력의 zero-shear FLRW rate다. 따라서 `H_q²(a)=H_F²(a)+s_q²(a)`이고 q_ref=0이 FLRW다. 아래 ±q 및 q family는 case parameter q_ref를 줄여 쓴 표기다. 같은 H0·모든 density parameter·추가 shear를 동시에 독립적으로 고정하여 constraint를 어기지 않는다. ±q는 평균 H가 같아도 축/횡 방향 팽창이 다른 두 history다. `a_o=1`과 좌표 gauge `b_o=0`의 기준 epoch도 고정한다. `zbar=a_o/a−1`는 일반적으로 관측 redshift가 아니다.

광자의 local tetrad energy `E`와 symmetry axis cosine `μ`는

\[
 \dot E=-E[H+s(3\mu^2-1)],\qquad
 \dot\mu=-3s\mu(1-\mu^2),
\]
\[
 \partial_t f-E[H+s(3\mu^2-1)]\partial_Ef
 -3s\mu(1-\mu^2)\partial_\mu f=C[f;\boldsymbol x,T]+S.
\]

`f`는 phase-space occupation이고 source/collision 항은 동일 convention으로 변환한다. number density per `dE dΩ`인 `nγ(E,μ)`와 혼동하지 않는다. 현 `CharacteristicRay::pullback/derivative/solid_angle_jacobian` 및 `RadiationState::transport`를 그대로 재사용하고 새 background/source 연결만 확인한다. packet count는 comoving이며 proper density는 `a³`으로 나눈다. energy grid 밖의 photon number/energy는 이미 존재하는 below/above boundary ledger로 보존한다.

**Non-tilted baseline의 추가 symmetry:** 축대칭만으로는 μ에 홀수인 dipole과 net radiation force를 없애지 못한다. 최소 IC와 source는 `f(E,μ)=f(E,−μ)`, `S(E,μ)=S(E,−μ)`로 선택하고 symmetric opacity를 사용하여 net momentum flux를 0으로 유지한다. quadrupole은 허용한다. 이 대칭을 깨는 source는 tilt/외력 closure를 요구하므로 baseline과 별도다.

위 기하 convention과 관측 redshift 관계는 Fleury–Pitrou–Uzan, *Light propagation in a homogeneous and anisotropic universe*, arXiv:1410.8473v3, §§II, IV (배경 식 1–10 및 null-geodesic/redshift 유도)와 대조했다. 해당 원문은 conformal shear의 제곱에 1/2를 넣지 않으므로 본 문서의 proper-time `σ²`와 구분한다. 원문: <https://arxiv.org/pdf/1410.8473>.

## 3. 최소 H/He·thermal·source 계약

`x_HI=1−x_HII`, `x_HeI=1−x_HeII−x_HeIII`, `y=n_He/n_H`, `x_e=x_HII+y(x_HeII+2x_HeIII)`, `n_e=n_H x_e`, `n_H=n_H,* (a_*/a)^3`를 사용한다. 동일 초기 물리 밀도·분율·source 가정에서 각 q의 gas와 radiation을 다시 풀며 ne/T를 고정하지 않는다.

수소 예로

\[
 \dot x_{\rm HII}=(\Gamma_{\rm HI}+C_{\rm HI}n_e)x_{\rm HI}
                 -\alpha_{\rm HII}n_ex_{\rm HII},\quad
 \Gamma_i=c\int\sigma_i(E)n_\gamma(E,\Omega)\,dE\,d\Omega.
\]

HeI↔HeII↔HeIII도 동일 process registry의 전이와 electron census로 연결한다. photoelectron heating은 같은 흡수 event의 threshold를 사용한 `c n_i ∫(E−χ_i) σ_i nγ dE dΩ`이며 opacity·ionization·heating을 별도로 중복 계산하지 않는다. 실제 thermal/rate API가 포함하는 collisional/recombination/Compton 등의 목록·domain·units를 고정한다.

단일 nonrelativistic gas temperature와 고정 y의 ideal mixture에서는

\[
 \dot T=-2HT-{T\dot x_e\over1+y+x_e}
 +{2(\mathcal H-\mathcal C)\over3k_B n_H(1+y+x_e)}.
\]

화학 binding energy·escape·방사선 energy 및 expansion work는 기존 augmented energy ledger에서 일관되게 관리한다. radiation energy moment의 기하 항은 `dot ε_γ+4H ε_γ+2s(P_parallel−P_perp)`이고, source·absorption·spectral boundary 항을 그 우변에 한 번씩 둔다.

기본 source 선택 작업은 source-backed isotropic comoving emissivity `εdot_N(E,zbar)`를 추천한다. 정규화, spectral support, history, escape fraction 및 homogeneous/clumping 가정을 선택하고 proper-source 변환을 명시한다. prescribed UVB를 선택하면 이미 전달된 radiation과 재전달하는 photon source의 중복을 해소해야 한다. 현 `rux_adapter`는 InitialStock만 받으므로 계속되는 emissivity/callback 연결이 실제 구현 작업이다. 상수 initial photon stock으로 전체 astrophysical reionization source를 대체하지 않는다.

재결합 closure는 Case-A explicit diffuse transport / Case-A escape ledger / consistent Case-B OTS 중 하나를 선택한다. 현재 warm Case-A escape는 emitted recombination spectrum/count를 공급하지 않는다. homogeneous 모델은 local fractions를 내보내고 QV로 바꾸지 않는다. 산란·secondary electrons·metals·spatial clumping 등 생략 항은 선택된 최소 baseline의 가정으로 기록하며, 관측량에 필요한 크기만 sensitivity로 평가한다.

### Abundance registry와 두 정규화

최소 tracked 상태는 `HI, HII, HeI, HeII, HeIII, e−`다. H/He의 isotope inventory와 primordial abundances는 지정된 donor에서 받아 고정한다. 구현이 hydrogen/helium을 isotope aggregate로 다루면 그 사실과 채택한 mass-number convention을 기록한다. 최소 `1H/4He` 모델은 그 근사를 명시한다. D/T/3He/Li 등의 추가 곡선은 **실제 donor abundance, supported ionic processes, charge states 및 코드 상태**가 registry에 있을 때만 추가한다. 오래된 17-state inventory 문서는 17개 species evolution 결과를 공급하지 않는다.

`i=(nuclide, charge state)`라 하고 A_i는 nucleon number, q_i는 ionic charge number라 하면

\[
 n_b\equiv\sum_{i\in\text{full selected nuclear/ionic inventory}}A_i n_i,
 \quad Y_i\equiv n_i/n_b,\quad X_i\equiv A_iY_i,
 \quad \sum_i A_iY_i=1
\]

에서 n_b는 선택된 물리 모델의 전체 baryon inventory를 분모로 한다. 마지막 합은 모든 inventory를 추적할 때 1이다. 일부 reservoir를 추적 곡선에서 생략하면 그 몫을 registry에 보존하고 tracked species만의 마지막 합은 1보다 작을 수 있다. 생략분을 버려 분모를 재정규화하지 않는다. electrons는 n_b 합에 포함하지 않는다. `Y_e=n_e/n_b=Σ_i q_iY_i`는 별도의 charge check/전자 곡선이며, `x_e=n_e/n_H`와 다르다.

원소별 ion fraction은 `x_{E,q}=n_{E,q}/n_E`, `Σ_q x_{E,q}=1`이고, isotope-resolved species에는 해당 nuclide의 분모를 명시한다. `Y_i=x_i(n_nuclide/n_b)`이므로 x와 Y를 같은 이름·축 label로 사용하지 않는다. `1H/4He` baseline이면 `n_b=n_H+4n_He`, `Y_H,total=1/(1+4y)`, `Y_He,total=y/(1+4y)`, `Y_e=Y_H,total x_e`다. 특히 `Y_p`는 문헌에서 4He mass fraction을 가리킬 수도 있으므로 plot에는 `X_He4` 또는 `n_He4/n_b`처럼 정의를 직접 쓴다.

재이온화 중 nuclei의 생성·소멸 반응이 없는 baseline에서는 `dot n_i+3Hn_i=R_i`, `dot n_b+3Hn_b=0`, 따라서 `dot Y_i=R_i/n_b`다. dilution은 proper density에 존재하지만 이 ratio에 다시 넣지 않는다. ionization state 합의 nuclide inventory `Σ_qY_{nuclide,q}`는 일정하다. neutral curves HI/HeI도 최종 데이터에 명시적으로 내보낸다.

### BBN-style plotting 계약

필수 그림은 두 축 family다: **(A) abundance vs proper cosmic time, (B) abundance vs actual gas temperature T_gas**. 각 family에서 원소별 x panel과 BBN식 Y panel을 분리하고, electron normalization을 적는다. donor와 절대 cosmic-age origin이 연결되지 않은 구간의 시간축은 `t−t_ref`라고 표시하고 임의의 cosmic age를 만들지 않는다. zbar는 보조 축으로 제공할 수 있다.

T_gas는 팽창 냉각 뒤 photoheating으로 상승할 수 있으므로 **시간 순서의 parametric curve `(T_gas(t),Y_i(t))`**를 그린다. T로 행을 정렬하거나 서로 다른 heating/cooling branches를 하나의 single-valued 함수로 합치지 않는다. arrows·시간 색상·turning-point 또는 branch labels로 진행 방향을 표시한다. gas 온도를 BBN의 monotonic radiation-temperature clock으로 간주하지 않는다. 보조 `T_ref∝a⁻¹`를 보여주면 선택한 isotropic background reference temperature라고 명시하고, exact directional Bianchi-I CMB temperature라고 부르지 않는다.

로그 abundance 축은 유용하지만 정확한 0이나 resolution 이하 값을 양수 floor로 바꿔 계산 결과처럼 표시하지 않는다. omission/upper-limit marker와 plot-only convention을 명시한다. ±q·FLRW는 같은 registry·정규화·units로 비교하며, branch를 보존한 interpolation만 사용한다.

Abundance error는 normalization과 charge 제약으로 서로 연결된다. 실제 ensemble/추정 모델이 covariance를 공급하면 ordered species registry와 함께 covariance를 제공하고 보존 제약을 확인한다. deterministic refinement만 수행했다면 observed paired differences/error envelopes를 기록하고 확률적 covariance/posterior를 발명하지 않는다. 예를 들어 원소별 공분산 C_x가 정의되면 `C_x 1=0`, 완전 baryon-normalized ionic covariance C_Y면 `A^T C_Y A=0`을 해당 수치 정확도에서 만족해야 한다. ε_x와 ε_Y의 변환에도 동일 donor normalization과 상관관계를 유지한다.

## 4. Secondary 수신기와 claim ceiling

이 절의 τ/visibility는 지원된 abundance history에서 파생하는 후속 제품이다. 미확정 observer tail은 이 제품의 full-total claim만 제한하며 재이온화 abundance history·그림·보고서의 완료를 막지 않는다.

cold Thomson 및 homogeneous non-tilted gas에서 **고정된 proper-time endpoints**의

\[
 \tau(t_1,t_2)=c\sigma_T\int_{t_1}^{t_2}n_e(t)\,dt
\]

는 한 background 안에서 방향 독립이다. q가 다르면 ne와 clock history가 달라지므로 같은 τ일 필요는 없다. proper ne에 Q나 dilution을 추가로 곱하지 않는다.

observer direction cosine `μ_o`, `Δb=b(t)−b(t_o)`에 대해

\[
 1+z_{\rm obs}(t,\mu_o)={a_o\over a(t)}
 \sqrt{(1-\mu_o^2)e^{2\Delta b}+\mu_o^2e^{-4\Delta b}}.
\]

고정 observed z는 emission endpoint `t_e(z,μ_o)`가 달라져 directional τ를 만들 수 있다. 그 방향성은 고정 시간 구간의 Thomson opacity에 임의 각도 인자를 붙여 얻는 것이 아니다. 강한 diagnostic shear에서 directional redshift가 단조가 아니면 root branch를 명시한다.

zbar20→4 history는 우선 **그 구간의 τ**를 제공한다. 오늘의 observer까지 필요한 geometry/ne tail이 없으면 total τ와 normalized physical visibility/probability는 null로 남기고, 유효한 segment/represented quantities를 즉시 보고한다. full sky·polarization은 이 최소 결과의 산출물이 아니다.

Prescribed-background 근사의 사후 점검은 `ε_ion` 및 thermal correction의 background energy 대비 크기와 생략 stress가 유도할

\[
 \delta s(t)={1\over a^3(t)}\int_{t_*}^{t}a^3(t')
 {8\pi G\over3c^2}[P_\parallel-P_\perp]_{\rm omitted}(t')\,dt'
\]

를 기록하는 방식이 최소다. 실제 backreaction bound를 입증하기 전에는 이를 perturbative diagnostic estimate라고 부른다. q→0에서 s로 나눈 상대량만 쓰지 말고 `|δs|/H` 등 절대 기준도 둔다. 이 근사 오차가 declared accuracy를 지배하면 해당 정밀도 claim을 낮추거나 그 feedback만 다음 단계로 구현한다.

### Moment와 plot 축을 고정하는 출력 convention

`nγ(E,μ)`가 **proper volume·energy·solid angle당 photon number**일 때

\[
 J_\ell(E,t)=2\pi\int_{-1}^{1}P_\ell(\mu)n_\gamma(E,\mu,t)d\mu,
 \quad n_\gamma(t)=\int J_0dE,\quad
 \epsilon_\gamma(t)=\int E J_0dE.
\]

이 J는 photon-number angular moment이며, conventional specific intensity라는 뜻으로 사용하지 않는다. normalization된 average가 아니라 solid-angle integral이다. 따라서 `P_parallel=2π∫dE E∫dμ μ²nγ`, `P_perp=π∫dE E∫dμ(1−μ²)nγ`, `P_parallel−P_perp=∫dE E J₂`다. energy flux는 `F_z=c∫EJ₁dE=0`인 baseline을 사용한다. occupation f에서 변환한다면 photon polarization 두 개에 대해 `nγ=2E² f/[(2πħ)³c³]`다. 코드의 eV/cm³ 표기는 별도 SI 변환을 명시한다. source가 이미 angle-integrated면 추가 2π/4π를 곱하지 않는다. energy grid와 μ grid의 배열 axis를 output metadata에 기록한다.

observer endpoint t_o를 향한 convention은 `τ_o(t)=cσ_T∫_t^{t_o}n_e(t′)dt′`, `dτ_o/dt=−cσ_T n_e`, **positive** `g_t(t)=cσ_T n_e(t)exp[−τ_o(t)]`다. `g_t`의 단위는 s⁻¹이고 `∫_{t_i}^{t_o}g_t dt=1−exp[−τ_o(t_i)]`다. forward cumulative τ를 쓰는 별도 plot과 혼합하지 않는다. endpoint가 zbar4인 segment에는 `τ_segment`와 `g_segment`라고 쓰며, 이 truncated kernel을 오늘의 full visibility로 정규화하지 않는다.

`zbar`가 큰 값에서 작은 값으로 진행하는 history plot과 receiver 적분 방향을 분리한다. `g_zbar=g_t |dt/dzbar|=g_t/[(1+zbar)H]`는 positive density per redshift다. fixed-observed-z에서 단조 ray면 `g_zobs=g_t/[(1+zobs)|H+s(3μ²−1)|]`; 여기의 μ는 해당 ray의 **현재 local** cosine이다. receiver angle average는 **observer** μ_o에서 수행하고, 다른 epoch의 μ 분포로 바꿀 때는 기존 solid-angle Jacobian을 사용한다. |H_direction|이 0인 turning point에서는 이 chart를 쓰지 말고 proper time/명시적 root branch로 계산한다.

## 5. 정량 산출물과 최소 수렴 목표

초기 family는 **5개 history** `q_ref={0, ±q_amp/2, ±q_amp}`로 충분하다. `q_amp`는 선택된 background/source 조건에서 정하고, 물리 허용 family와 resolution 확인용 큰 diagnostic family를 구분한다. free-decaying Bianchi-I의 특정 quadrupole 조건을 모든 허용 shear·모든 수치 바닥에 대한 보편 명제로 확대하지 않는다. +q와 −q scalar 결과의 정확한 동일성도 가정하지 않는다. 분해는 `Δ_even=[O(q)+O(−q)]/2−O(0)`, `Δ_odd=[O(q)−O(−q)]/2`로 측정하며 cubic 가능성을 보존한다.

| 최종 제품 | 최소 수량·내용 |
|---|---|
| scenario/background | 한 source-backed baseline lock, 5개 q와 실제 달성 zbar 구간·proper clocks, density/source/closure 및 q=0 constraint 비교 |
| primary abundance histories | 모든 q에 대해 ordered species registry, proper time, T_gas, zbar, HI/HII/HeI/HeII/HeIII와 electron의 명시적 x·Y 정규화, nuclei/charge/error 기록; 지원된 covariance 또는 deterministic paired error 구분 |
| coupled supporting histories | `a,b,H,s`, proper densities, radiation number/energy 및 angular monopole/quadrupole, source/process/energy/boundary ledgers |
| paired effects | FLRW 차이, ± even/odd 및 amplitude scaling; 가능하면 x_HII=0.1/0.5/0.9 crossing redshifts·duration, crossing이 없으면 명시적 null |
| secondary observables | segment τ와 numerical/source/tail 구분; 지원된 endpoint의 directional maps/receiver. full τ admission은 primary abundance 결과의 선행 gate가 아님 |
| mandatory figures | abundance-vs-proper-time와 time-ordered abundance-vs-T_gas 두 family, 각각 x/Y·neutral/electron 정의·FLRW/±shear·error labels. paired differences와 conservation/resolution 자료를 함께 제공 |
| supporting figures | 필요에 따른 background/constraint, radiation angular/spectral evolution; τ/visibility는 별도 nonblocking family |
| report | methods→첫 결과→full results를 누적한 MD/LaTeX/PDF와 data/figure/source manifest; 최종 claim과 limitations 및 재현 argv |

최소 검증은 새 코드·새 물리 입력에 한정한다. 적용 가능한 기존 ray/packet/receiver 근거는 재사용한다.

1. **구조·극한:** 새 cosmological constraint 및 s a³ 보존(해당 closure), q=0 FLRW limit, axial/transverse redshift, μ-parity, species/nuclei/charge 및 x↔Y 변환, neutral fractions, nonnegative photons 및 thermal energy, 단일 event ownership, 누적 energy/work/escape/boundary closure. 기존 tolerance를 임의로 완화하지 않는다.
2. **resolution:** 대표 변화 구간에서 시간·에너지·각도 resolution을 분리한 refinement로 지배 오차를 찾고, 최종 claimed observable에는 필요한 최소 3-level sequence 또는 해당 method의 정당화된 estimator를 사용한다. 혼합 효과를 지배하는 경우에만 joint refinement를 추가한다. 모든 조합을 전체 history에서 무조건 반복하지 않는다.
3. **paired accuracy:** 채택 v2의 `numerical_target_fraction=0.1`을 유지한다. resolved shear contrast를 주장하려면 paired numerical error가 `0.1 |ΔO|` 이하가 되게 한다. near-zero는 실행 전 정한 absolute floor와 resolution limit를 보고하며, floor 아래 결과는 unresolved/bounded 결과로 완결할 수 있다. empirical refinement estimate를 rigorous continuum certificate로 부르지 않는다.
4. **robustness:** q_amp/2의 amplitude scaling, 동일 source의 허용 normalization/spectral/domain sensitivity를 최소한의 정당화된 alternatives로 확인한다. numerical·atomic·source·geometry/IC·spectral/spatial closure uncertainty를 분리한다. physical case 전체를 바꾸는 새 source는 별도 scenario로 표기한다.
5. **finite progress:** 첫 supported FLRW 구간→동일 입력 첫 Bianchi 구간→FLRW history와 Bianchi 증분→5-case paired abundance family→abundance plot/report final review 순서로 durable output을 남긴다. receiver는 지원된 자료가 있을 때 병행하며 필수 마지막 단계가 아니다. checkpoint마다 그림·보고서를 갱신한다. 기존 τ/history 실패를 지우거나 반복 계산으로 대체하지 않는다.

### 새 형식·수치 테스트 개념: 실행하지 않음

- **Registry/normalization:** supplied nuclei만 존재하고 mass number/charge/denominator/units가 명시되는지 확인한다. 같은 manufactured H/He state의 x→Y→x roundtrip, `Σx=1`, nuclei sum, electron charge를 확인한다. electron을 baryon sum에 넣거나 neutral을 누락하는 오류를 직접 잡는다.
- **Dilution invariance:** reaction-free expanding manufactured state에서 n_i와 n_b가 같은 a⁻³로 변하고 Y 및 nuclide-total x가 일정한지 확인한다. 실제 cosmological history를 다시 실행하는 테스트가 아니다.
- **Temperature branches:** `[T_low,T_high,T_low]` 같은 manufactured heating/cooling sequence를 plot builder에 주어 row/time order와 branches가 유지되는지 확인한다. T-sorting으로 다른 상태가 합쳐지면 실패한다.
- **Error/covariance:** 실제 covariance 입력이 있을 때만 symmetry/positive-semidefiniteness/normalization null directions를 검사한다. covariance가 없을 때 plotting code가 임의 error band를 생성하지 않는지도 확인한다.
- **Completion:** 선언한 full supported interval의 species tables와 두 필수 plot families 및 new-run numerical evidence가 있으면 abundance goal을 판정한다. observer-tail/total-τ가 null인 정상 사례가 이 판정을 막지 않는 구조를 확인한다.

## 6. 현재 위치에서의 정확한 다음 구현·공급 작업

| 작업 | 현재 근거와 다음 완료 조건 | RUX 연결 |
|---|---|---|
| cosmological scenario 선택 | `PHYSICAL_INPUT_ADMISSION`의 null cosmology/clock/IC를 source-backed 하나의 모델로 채운다. 20 K와 6.137 K는 같은 입력으로 간주하지 않는다. rec donor와 cosmology가 다르면 필요한 matching IC/background만 공급받는다. | RUX02/04 |
| cold H/He rates + thermal | PR114는 기존 FT03 warm 30000–110000 K의 conditional receiving path이며 cold provider가 아니다. 기존 검증 가능한 rate/thermal source를 자율적으로 선택하고 적용 domain·coefficients·point 및 필요한 interval/root 경로를 연결한다. BASS_HE가 공급할 수도 있지만 새로운 precision atomic 연구의 완료를 기다리지 않는다. | LOWT-PROVIDER, SOURCE-INTEGRATION, RUX03 |
| continuous source + canonical driver | `rux_adapter`의 InitialStock 전용 seam에 선택 emissivity/UVB의 정확한 API와 event ownership을 구현한다. Rust `rux_science`를 실제 cosmological driver로 연결하고 source/config/run argv를 고정한다. | CC-PREP05, RUX05 |
| cosmological axisymmetric background | 기존 `GeometryBackground`에 H(a),s(a),b(a),t(a)를 넣고 기존 ray/packet transport를 재사용한다. 일정 H/s fixture를 zbar20→4 물리배경으로 승격하지 않는다. | RUX06/07 |
| abundance tables + figures | nuclei/ionic registry와 x/Y/electron normalization을 고정하고 accepted states에서 time 및 time-ordered T_gas 그림과 error 자료를 생성한다. 추가 nuclei는 실제 supported inventory만 추가한다. | RUX08/09/11 |
| secondary receiver | rei에서 admitted proper-ne segment를 export하고 기존 receiver interface를 연결한다. tail 미해결은 τ/visibility의 total claim만 막고 기본 abundance 완료와 분리한다. | CC-RECV, RUX10 |
| final scoped review | 전체 선언 구간의 새 physical source/domain·abundance/neutral-fraction accuracy·normalization·approximation size·필수 시간/온도 그림을 검토하고 최종 report를 정리한다. full τ admission을 요구하지 않는다. | RUX16 |

기존 `CC-PREP05` receipt의 준비 명령 11/8과 raw-log 미보존은 역사적 사실로 보존한다. 8-command 준비 예산을 이후 모든 개발의 영구 승인 장벽으로 사용하지 않는다. 현재 승인 범위에서 coordinator가 다음 실제 작업 단위에 source/config, cumulative run/time/resource limits와 stop condition을 새로 배정하면 된다. 이 계획 요청 자체는 새 solver 실행을 지시하지 않는다.

## 읽은 로컬 근거

- `AGENTS.md`, `CLAUDE.md` 및 adopted `docs/fastest_track_chat/REI-ATOMIC-REUSE-RESET-20261012/PLAN.json`.
- `rust/rei_microphysics/src/{bianchi_i.rs,angular_photons.rs,axisym_contract.rs,rux_adapter.rs}`.
- `research/rux_science_20261014/{SELECTED_SOURCE_CONTRACT,PHYSICAL_INPUT_ADMISSION,SOURCE_INTEGRATION_RECEIPT,ADAPTER_IMPLEMENTATION_RECEIPT,LOW_TEMPERATURE_PROVIDER_CONTRACT,BASS_RECEIVER_CONTRACT,TRANSPORT_REUSE_AND_BINDING,EXECUTION_CHECKPOINT}.json`.
- 현재 물리 history/시나리오/새 provider admission은 아직 없다. 보존된 F08·SYNC evidence는 그 기록의 claim scope에서만 재사용한다.

2026-10-14 user steering 반영: primary final goal은 BBN-style abundance history versus proper cosmic time 및 actual T_gas다. 이는 donor nuclei의 ionization history이며 BBN burning network가 아니다. 위 변경은 planning contract에만 적용했고 과학 계산·테스트는 실행하지 않았다.
