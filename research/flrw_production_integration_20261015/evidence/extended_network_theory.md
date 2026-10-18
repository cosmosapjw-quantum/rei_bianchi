# FLRW 우선 생산 solver와 병렬 수행할 isotope-native ionic network

2026-10-15. 이론·원전 조사 및 작은 기호 검산의 완료 기록이다. 현재 단위는 H/He FLRW 개발을 막지 않는 D/H 확장의 구성식과 코딩 계약이다. 재이온화 실제 history나 atomic-rate admission을 새로 주장하지 않는다. repository 코드·branch는 변경하지 않았다.

## 결론과 실제 선택

최소 유용한 추가는 **D I / D II와 H–D charge exchange**다. 하나의 추가 nuclide와 두 ionic states이며, primordial donor의 D/H를 명시적으로 받아 시간·T_gas별 이온 분율을 계산한다. D의 neutral fraction을 H와 단순 복사하면 낮은 온도의 isotope charge-exchange 차이를 잃는다. 초기 구현은 isotope-native charge-exchange operator를 독립적으로 제공하고 D는 기본 OFF로 둔다. H/He production solver는 이 모듈의 완료를 기다리지 않는다.

| 후보 | 이번 결정 | 근거와 필요한 추가 입력 |
|---|---|---|
| D I/D II | 첫 추가 network의 추천 모델 선택 | 원전의 양방향 H–D CT rate가 존재한다. donor D/H, 동일 단위·온도·closure, 실제 D photo/recombination/thermal support가 있어야 full D history를 활성화한다. |
| 3He I/II/III | 다음 isotope-resolved 선택 | donor 3He inventory와 명시된 isotope approximation/provider가 필요하다. 4He fractions를 따른다는 근사는 가능한 별도 모델이지 새 isotope-resolved rate 데이터가 아니다. |
| 7Li I/II 및 고이온 단계 | source spectrum 준비 후 | Li I threshold 아래/위의 별도 광자 대역과 실제 rates가 필요하다. H-ionizing band만으로 Li neutral history를 완성하지 않는다. |
| metals | 현재 baseline에는 넣지 않음 | enrichment/abundance history, ion stages, spectrum, cooling·charge-transfer 자료가 선택된 경우에만 별도 source-backed 확장한다. 원시 무금속 baseline에 임의 금속 abundance를 넣지 않는다. |
| free n, T, molecules | 별도 donor/decay/chemical closure가 공급될 때 | registry에 항목이 있다는 사실은 EoR 초기상태·반응망을 공급하지 않는다. HD cooling은 atomic D extension의 자동 포함 항목이 아니다. |

현재 `isotope_state.rs`는 13개 nuclear/ionic entries를 정의한다. 과거 17-entry 문서에는 같은 nuclide의 여러 전하 상태가 포함된다. **17 entries는 17 nuclides가 아니다.** 현재 legacy HHe projection은 D/T/3He/n이 있으면 거절하며 이 동작을 유지한다. 추가 network는 proper-SI isotope state/moments를 직접 사용한다.

## 실제 읽은 원전과 provider 상태

검색은 사용자가 지정한 **SciSpace와 Exa**로 수행했다. SciSpace semantic search에서 원전 후보를 찾고 Exa로 원문을 읽었다. 검색 초록의 공급 여부와 직접 확인한 식을 구분한다.

- **Savin (2002), ApJ 566, 599–603, DOI 10.1086/324218**, §§2–4, 식(1),(2),(6), Table 2를 읽었다. [원문 PDF](https://iopscience.iop.org/article/10.1086/324218/pdf). Ground-state D+H+↔D++H의 계산표는 1–2×10⁵ K를 다루지만 **analytic fit의 명시 정확도 구간은 2.7–2×10⁵ K**다. forward reaction은 endothermic이며 보고된 threshold는 약 3.7 meV(43 K)다. fit의 지수상수와 물리 energy defect를 혼동하지 않는다. 이 문헌은 CT provider 후보를 실제 공급한다. 코드로 통합·검증된 provider는 아직 아니다.
- **Switzer & Hirata (2005), Phys. Rev. D 72, 083002**, §§II–IV를 읽었다. [arXiv 원문](https://arxiv.org/pdf/astro-ph/0507106). Li I ionization threshold가 약 5.39 eV이며 H recombination distortion photons도 ionization에 기여하는 구체 모델을 제시한다. 현재 reionization source에 그 원문의 spectrum을 자동 이식하지 않는다. 이 결과는 Li 공급 계약에 sub-Lyman-limit spectral support가 필요하다는 선택 근거다.
- **McQuinn & Switzer (2009), Phys. Rev. D 80, 063010**, §II의 n_3He+=n_H f_3He x_HeII 관계를 읽었다. [arXiv 원문](https://arxiv.org/pdf/0905.1715). 이는 3He abundance와 helium ion fraction을 연결하는 모델 사용례다. 해당 논문을 독립 isotope-specific ionization/recombination rate table로 취급하지 않으며 hyperfine 관측 계산을 이번 목표에 추가하지 않는다.

SciSpace는 Stancil–Lepp–Dalgarno(1998), Faure et al.(2024), Galli–Palla의 network도 찾았다. 이번 rate transcription의 원전으로 채택하지 않았으므로 세부 rates를 수입하지 않는다. Cooke–Pettini(2015)는 추가 후보 초록 수준이며 아래 유도의 근거가 아니다.

### Savin Table 2의 검증된 transcription 계약

T는 K, 다음 k는 cm³ s⁻¹이며 SI 반환에는 **10⁻⁶**을 곱한다.

\[
 k_f(T)=2.00\times10^{-10}T^{0.402}e^{-37.1/T}
        -3.31\times10^{-17}T^{1.48},
\]
\[
 k_r(T)=2.06\times10^{-10}T^{0.396}e^{-33.0/T}
        +2.03\times10^{-9}T^{-0.332}.
\]

`f: D0+H+→D++H0`, `r`은 역방향이다. 원문의 fit 차이는 각각 6%, 4% 미만으로 기술되며, 이는 전체 atomic theoretical uncertainty나 cosmological prediction error가 아니다. `2.7≤T≤200000` 밖에서는 이 fit provider를 거절한다. 1 K 표가 있다는 이유로 analytic fit을 1 K까지 내리지 않는다. `37.1 K` 또는 `33 K`를 chemical threshold로 사용하지 않는다. Δχ는 별도의 source-bound `χ_D−χ_H` [J/event]로 주입한다.

## 일반 stoichiometric ionic network의 구성식

species i는 `(nuclide A,Z; ionic charge q; explicit excitation if modeled)`로 식별한다. electron은 `A=0,q=−1`인 별도 bookkeeping species다. 원자 ground state만 추적하는 경우 isotope별 neutral ground를 chemical reference로 삼고, q번 이온화 상태의 chemical energy는 `c_i=Σ_{j=0}^{q−1}χ_{nuclide,j}`다. fit cutoff와 binding threshold는 별도 필드다.

반응 r의 reactant/product 정수 계수 α_ir,β_ir에서 `S_ir=β_ir−α_ir`를 정의한다. proper density n_i[m⁻³], event rate R_r[m⁻³s⁻¹]이면

\[
 \dot{\boldsymbol n}+3H\boldsymbol n=S\boldsymbol R,
 \quad n_b=\sum_i A_i n_i,\quad Y_i=n_i/n_b,
 \quad \dot{\boldsymbol Y}=S\boldsymbol R/n_b.
\]

마지막 식은 nuclear reactions·external baryon injection이 없는 현재 ionic network에서 `A^T S=0`, `dot n_b=−3Hn_b`를 사용했다. isotope별 nucleus-count row L도 `LS=0`이며 `L Y`가 일정하다. 모든 종이 포함되면 `ΣA_iY_i=1`, omitted donor reservoir가 있으면 그 값을 명시적으로 포함한다. electrons는 baryon 합에서 제외한다.

전하 row `q^T S=0`를 만족해야 한다. no-positron neutrality closure에서는 `n_e=Σ_{ions}q_i n_i`다. electron을 독립 적분하면 초기 neutral constraint와 동일 S를 유지하고, algebraic elimination이면 모든 rate/Jacobian의 n_e 의존성을 chain rule로 반영한다. negative ions나 nonthermal electrons를 추가하면 census와 EOS를 그 species registry에 맞춰 확장한다.

예를 들어 two-body rate는 `R=k(T)n_i n_j`; photoionization은 `R=n_i Γ_i`,

\[
 \Gamma_i=c\int\!\sigma_i(E)n_\gamma(E,\Omega)dE d\Omega,
 \quad Q_{\mathrm{photo},i}=c n_i\int(E-\chi_i)\sigma_i n_\gamma dE d\Omega.
\]

여기서 nγ는 proper volume·energy·solid angle당 photon number다. 이미 angle-integrated 입력에는 다시 4π를 곱하지 않는다. identical-reactant symmetry factor는 선택된 coefficient의 정의에서 확인해 R에 한 번만 반영한다. k[cm³s⁻¹]→[m³s⁻¹]은10⁻⁶, cooling[erg cm³s⁻¹]→[J m³s⁻¹]은10⁻¹³이다.

### Thermal·binding·radiation 장부

common nonrelativistic Maxwellian ideal-gas closure에서 `ν=Σ_{heavy}Y_i+Y_e`, `e_th=3n_bν k_B T/2`다. 이 ν는 반응으로 변하는 thermal particle count이며 nuclear baryon count가 아니다.

\[
 \dot T=-2HT-{T\dot\nu\over\nu}+{2Q_{th}\over3k_B n_b\nu},
 \qquad \dot\nu=\boldsymbol1^T S\boldsymbol R/n_b.
\]

위 식을 `dot e_th+5He_th=Q_th`에 역대입하면 정확히 성립한다. `e_chem=n_b c^T Y`는 `dot e_chem+3He_chem=c^TSR`를 따른다. nuclear inventory가 고정되어 있으므로 각 nuclide에 상수를 더한 reference energy는 반응 defect를 바꾸지 않는다: `(c+L^Tλ)^T S=c^T S`.

각 event의 장부는

\[
 q_{th,r}+\Delta c_r+E_{\gamma,out,r}-E_{\gamma,in,r}=0,
 \qquad \Delta c_r=c^T S_{:r}.
\]

- photoionization: photon에서 E를 빼고 chemical에 χ, thermal에 E−χ를 더한다. 같은 χ를 다른 cooling routine에서 다시 빼지 않는다.
- collisional ionization: thermal에서 χ를 빼고 chemical에 χ를 더한다; photon은 없다.
- radiative recombination: chemical −χ, thermal −κ, photon/escape +(χ+κ). κ는 해당 rate-weighted kinetic-energy moment이며 임의로3k_BT/2를 대입하지 않는다. provider cooling이 thermal loss인지 total emitted energy인지 metadata로 구분한다.
- nonradiative D/H CT: chemical +(χ_D−χ_H), thermal 그 반대, photons/electrons의 변화는0. reverse의 부호는 모두 반대다.

Case-A transport/Case-A escape/consistent Case-B OTS 중 고른 recombination closure로 photon owner를 하나만 둔다. escaped energy를 local augmented ledger에 기록하면 escape 당시의 frame/energy와 expansion-work convention을 명시한다. 외부로 나간 radiation의 후속 진화를 암묵적으로 재합산하지 않는다. FLRW gas+tracked radiation의 work와 source·escape·boundary flux를 더하면 위 event cancellations와 함께 total energy ledger가 닫힌다.

## 구체 H/D 예제와 실제 Wolfram 검산

행 순서 `(H0,H+,D0,D+,e)`와 열 `(Hion,Hrec,Dion,Drec,CTf,CTr)`에서

\[
 S=\begin{pmatrix}
 -1&1&0&0&1&-1\\1&-1&0&0&-1&1\\
 0&0&-1&1&-1&1\\0&0&1&-1&1&-1\\
 1&-1&1&-1&0&0
 \end{pmatrix}.
\]

독립 conservation rows는 `L_H=(1,1,0,0,0)`, `L_D=(0,0,1,1,0)`, `q=(0,1,0,1,−1)`다. `A=L_H+2L_D`. chemical vector `(0,χ_H,0,χ_D,0)`는 defects `(χ_H,−χ_H,χ_D,−χ_D,χ_D−χ_H,χ_H−χ_D)`를 만든다.

Wolfram context를 먼저 호출한 뒤 evaluator로 실제 계산했다. **rank(S)=2, left-nullspace dimension=3**, `LS=qS=A^TS=0`; particle changes는 `(1,−1,1,−1,0,0)`, thermal 역대입과 five event energy residuals는0이다. Hion에서 electron 생성을 의도적으로 제거한 counterexample은 charge residual `(1,0,0,0,0,0)`을 내므로 검산이 해당 오류를 검출한다. 코드/실제 응답은 `extended_network_wolfram.wl/json`에 보존했다. 물리 rate나 cosmological solver 실행은 없었다.

D trace fraction x_D의 순간 계수 A_D=Γ_D+C_D n_e+k_f n_H+, B_D=α_D n_e+k_r n_H0이면 `dot x_D=A_D(1−x_D)−B_D x_D`. frozen background에서 equilibrium은 A_D/(A_D+B_D)이고 relaxation rate는 A_D+B_D다. CT-only equilibrium residual도 evaluator에서0이다. trace approximation을 채택해 H를 고정할 때는 full coupled reaction conservation claim과 구분한다.

## 정확한 frozen-rate charge-exchange finite map

이는 **고정된 rate와 고정된 proper volume의 반응 substep**에 대한 exact kinetic map이다. temperature-dependent rates를 매 순간 갱신한 전체 thermal/expansion 문제의 exact solution이라고 부르지 않는다.

`A=H0+H+`, `B=D0+D+`, `C=H++D+`, `x=D+`로 놓으면

\[
 \dot x=f(x)=k_f(B-x)(C-x)-k_r x(A-C+x),
 \quad \max(0,C-A)\le x\le\min(B,C).
\]

초기점 x에서

\[
 F=f(x),\quad K=k_f[(B-x)+(C-x)]+k_r[x+(A-C+x)]\ge0,
\]
\[
 d=\sqrt{[k_f(B-C)-k_r(A-C)]^2+4k_fk_r AB},
 \quad \theta=\begin{cases}2\tanh(dh/2)/d&d>0,\\h&d=0,\end{cases}
\]
\[
 \xi={F\theta\over1+K\theta/2},\qquad
 (H0,H+,D0,D+)_{new}=(H0+\xi,H+-\xi,D0-\xi,D++\xi).
\]

이 판별식은 cancellation 없는 nonnegative 표현이다. θ는 small-argument limit를 사용하고 큰 dh에서 exponential overflow를 만들지 않는다. F=0 또는 h=0이면 identity다. 물리 경계에서 벡터장이 안쪽을 향하므로 analytic map이 feasible interval을 유지한다. binary64 구현은 negative/nonfinite가 나오면 진단 오류를 반환하며 독립 species clipping으로 conservation을 깨지 않는다.

thermal update는 `e_th,new=e_th−Δχ ξ`, chemical change는 `+Δχ ξ`다. electron과 thermal particle count는 CT에서 변하지 않는다. energy가 음수가 되면 substep을 거절하고 기존 상태를 보존한다. production caller는 실제 T-dependent coupled equation에 필요한 step control/iteration을 담당한다. expansion을 분리한 abundance variable에서는 `dY/dt=n_b(t)F(Y)`이므로 rates가 고정일 때 `h` 대신 ∫n_b dt를 쓰는 구성도 가능하나, 이번 proper-density standalone API에는 섞지 않는다.

두 번째 Wolfram evaluator는 위 map의 Riccati ODE residual, d=0 limit residual, 초기 displacement 및 판별식 차이가 모두0임을 확인했다. dimensionless manufactured 값 `A=10,B=3,C=6,x=1,kf=2/5,kr=1/7,h=7/3`에서 `D+_new=1.96318481884852365308088403099`를 얻었다. 이는 실제 atomic rate가 아니다. `extended_network_finite_step.wl/json`에 원래 코드와 결과가 있다.

## 낮은 tier 구현자에게 전달할 frozen coding contract

**쓰기 허용:** 새 `rust/rei_microphysics/src/deuterium_charge_exchange.rs`, 새 `rust/rei_microphysics/tests/deuterium_charge_exchange.rs`만. `lib.rs` 등록·기존 adapter·production solver·branch 변경은 coordinator 소유다. test는 필요한 경우 새 파일을 `#[path]`로 불러 독립적으로 구성한다. 기존 `try_legacy_hhe_projection`의 extra-species reject는 유지한다.

**API 최소값:** 명시적 네 proper-SI densities와 thermal energy를 받는 `DhState`; forward/reverse SI coefficient, temperature/domain/source identity를 가진 rate record; `Savin2002::rates(T)`; 명시적 `delta_chi_j`와 source tag를 받는 `step_frozen_rates(state,rates,dt,defect)`; 결과는 new state, signed event extent, chemical/thermal deltas, conserved totals 및 numerical method scope. 이름은 구현자가 일관되게 정할 수 있으나 물리 계약을 바꾸지 않는다. errors는 invalid/nonfinite input, domain, negative final state/thermal energy, arithmetic overflow를 분리한다. abundance, IC, Δχ를 기본값으로 만들지 않는다.

**Required targeted tests, 새 것만:**

1. 위 matrix/전하·nuclide/baryon nullspace를 작은 정확한 integer check로 확인; electron 누락한 반응은 fail을 검출한다.
2. Savin fit에서2.7와200000K 허용, 그 밖·NaN·negative 거절. 원문 Table1의20K `(1.04e−10,8.90e−10)`,100K `(8.63e−10,1.32e−9)`,10000K `(8.04e−9,8.07e−9)` cm³/s에 대해 source fit tolerance6%/4%와 일치하고 SI factor10⁻⁶을 확인한다. fit accuracy를 machine-equality로 테스트하지 않는다.
3. Wolfram manufactured finite-step 결과와 scale-aware binary64 error 안에서 일치. 단위는 manufactured이며 physical run이 아니다.
4. frozen-rate semigroup: h1 후 h2와 h1+h2 결과 비교. h=0, zero rates, equilibrium 및 empty donor의 identity/명시 오류 정책을 확인한다.
5. pure-forward equal-reactant `d=0`에서 analytic second-order depletion과 비교; pure-reverse, extreme finite stiffness, 양방향 equilibrium에 대한 feasible interval·positivity·H/D totals·charge 보존을 확인한다.
6. CT chemical/thermal deltas 부호와 합0, electron 변화0; endothermic step이 thermal energy를 초과하면 transaction reject하고 입력을 그대로 보존한다. fake cutoff energy를 사용하지 않는다.
7. D=0에서 module이 HHe state를 바꾸지 않는 no-op임을 확인한다. 별도 D default activation·legacy projection bypass가 없어야 한다.

**실행 한도:** root가 이 계약의 작은 build/test 구간을 배정한다. production/native history는 이 계약의 실행 항목이 아니다. 테스트는 신규 목표만 실행하고 반복적인 전체 science 검산을 만들지 않는다. 수치 error tolerance는 manufactured map/finite arithmetic의 검증값이며 cosmological tolerance로 재사용하지 않는다.

## R1–R10 실제 수행 상태와 다음 단위

| 단계 | 이번 단위에서 실제 수행한 내용 |
|---|---|
| R1 | FLRW first와 병행하는 ionic extension 범위, write-free 이론 단위 및 기존 사용자 abundance 목표를 고정했다. |
| R2 | 지정된 physmath1.0 THEORY_LOOP/EVIDENCE 지침, 기존 isotope/atomic APIs, SciSpace+Exa 원전을 읽었다. |
| R3 | donor nuclei와 ionic states, literature provider와 admitted code, frozen-rate map과 coupled history를 분리했다. |
| R4 | D first/3He optional/Li spectral dependency/metals-supply 조건을 비교해 D CT를 첫 구성으로 선택했다. |
| R5 | stoichiometric FLRW equations, neutrality, thermal·binding identities, exact CT finite map을 유도했다. |
| R6 | Wolfram exact nullspace 및 독립 residual 역대입으로 conservation/thermal/event identities를 확인했다. |
| R7 | electron-missing counterexample과 manufactured exact finite step을 실제 evaluator에서 계산했다. |
| R8 | derived + symbolically_checked 구성식과 source-supported Savin fit을 채택; 전체 D provider/history는 미실행·미공급을 구분했다. |
| R9 | 두 새 파일의 API·domain·rate coefficients·허용변경·targeted tests를 coding contract로 전달했다. |
| R10 | 원문 locator·Wolfram 코드/응답·JSON 상태를 보존하고 lower-tier implementation을 다음 단위로 지정했다. |

strong no-go 연구 성과는 주장하지 않는다. 이론 단위 완료와 실제 rate-provider 구현/재이온화 완성은 구별한다. 다음 작업은 위 standalone module 구현·신규 tests이며, full D history의 activation에는 donor D/H와 D photo/recombination/energy-source 계약이 별도로 필요하다.
