# HERE_RUX03_EVENT_BRIDGE_02: 사건 bundle 연결 준비

## 결론과 범위

가장 작은 구현 대상은 **기존 FT03 thermochemistry와 native node absorption에서 나온 사건·에너지 성분을 한 번만 모아 `AxisymLocalSources`로 투영하는 경계**다. 선택된 물리 모형은 warm extended, Case-A escape, 초기 q=10–50000 eV다. 새 원자 율, diffuse spectrum, cold IC 또는 coupled history가 필요하지 않다. 이번 준비 작업은 candidate implementation과 decision review를 수행하지 않았다.

동일 상태에서 전체 사건 bundle을 두 번 더해도 개별 사건의 원자핵·전하·에너지 보존식은 계속 성립한다. 따라서 **보존 residual만으로 실제 소비 여부와 단일 소비를 판별할 수 없다.** 아래 정량 primitive 비교와 주입 전후 차분이 필요하다.

`physmath-research-loop`와 실제 제공된 GPT-6 Astra v4.0.0 연구 하네스의 core, phase 6/7, 기존 연구 상태를 읽었다. 이전 supplier의 독립 판정 범위는 보존한다. 이 준비 노트의 근거 상태는 `derived`, `source-code-inspected`, `numerically checked`다. `native implementation verified`나 `PROMOTE`는 주장하지 않는다.

## 1. 실제 코드 경계

정확한 파일·SHA-256·읽은 위치는 `SOURCE_LOCATIONS.json`에 있다. 아래 위치는 회수된 `physical_v2`를 기준으로 한다.

| 경계 | 실제 위치 | 현재 동작 |
|---|---|---|
| 원자 계수 | `ft03_rates.rs:26–68` | 30000–110000 K guard. RR 3개, CI 3개, DR 2개, RR kinetic coefficient와 DR energy를 같은 T에서 계산한다. |
| 열·사건 생산 | `ft03_controlled.rs:89–168` | `ft03_rhs`가 실제 proper density prefactor를 적용하고 `collision_per_cm3_s`, `recombination_per_cm3_s`, `dr_per_cm3_s`, thermal derivative와 escape를 반환한다. |
| 선택 연구 RHS 시작 | `native/src/main.rs:44–56` | controlled 모델의 nH/nHe를 stage 값으로 덮어쓰고, `photon_cm3=[0,0,0]`로 FT03를 호출한다. FT03의 20/35/70 eV fixture 광자는 여기서 활성화되지 않는다. |
| 실제 광이온화 | `native/src/main.rs:71–99` | 모든 실제 photon node에 대해 Verner sigma, c, proper lower species와 node photon density를 곱한다. 광자 loss·종 사건·primary heat를 같은 사건에서 만든다. |
| 사건 투영 | `native/src/main.rs:100–140` | J, thermal, internal, escape와 external source를 합치고, 13종 isotope 슬롯 및 electron source를 만든다. |
| 실제 수신 callback | `native/src/main.rs:142–143`; `axisym_coupling.rs:183–231` | `axisym_coupled_derivative(..., |_,_| Ok(sources))`가 제공된 source를 `FnOnce`로 호출한 뒤 검증한다. |
| 기하/좌표 처리 | `axisym_coupling.rs:237–256`; native `144–151` | source에 proper dilution/expansion/shear work를 더하고, native에서 분율과 w 좌표로 변환한다. |

현재 `Ft03Rhs`에는 RR kinetic의 **채널별 값**이 없고, thermal·escape 총합과 사건률은 있다. 이를 새 공개 자료로 확장할 때는 원래 생산자가 이미 사용한 같은 coefficient evaluation의 moment를 전달하는 편이 명확하다. consumer에서 다른 alpha family를 재평가해 escape를 재구성하면 source 일치가 사라진다.

`RATES` 명령은 coefficient를 반환한다. `SIGMA`는 density가 없는 cross section이다. `RHS`가 실제 density prefactor를 적용한다. coefficient, Gamma, volumetric event rate를 같은 것으로 취급하지 않는다.

## 2. 최소 사건 좌표와 단위

종은 (HI,HII,HeI,HeII,HeIII,e), edge는 (HI→HII,HeI→HeII,HeII→HeIII)다. proper event rate 단위는 cm^-3 s^-1이다. 한 stage에서

\[
C_a=n_e n_{a,\mathrm{lower}}\beta_a,
\quad R_a=n_e n_{a,\mathrm{upper}}\alpha_a,
\quad D_k=n_e n_{\mathrm{HeII}}\alpha_{\mathrm{DR},k},
\]
\[
P_{ag}=c\sigma_a(E_g)n_{a,\mathrm{lower}}n_{\gamma,g},
\quad P_a=\sum_gP_{ag}.
\]

광자 node는 이미 bin-integrated 또는 quadrature-weighted 수다. `weights`를 다시 곱하지 않는다. 선택 frontend는 `N_ref=a_rel^3 n_gamma`를 저장하므로 native 입력에서 `n_gamma=N_ref/a_rel^3`로 한 번 변환한다. RHS 사건률에 dt를 곱하지 않는다. 적분된 event count는 별도 step/history 자료다.

\[
J=(P+C-R)-(0,D_0+D_1,0).
\]

그러면

\[
\mathcal S_{\mathrm{species}}=(-J_0,J_0,-J_1,J_1-J_2,J_2,J_0+J_1+J_2),
\]
\[
\dot x_{\mathrm{HII}}=J_0/n_H,\quad
\dot x_{\mathrm{HeII}}=(J_1-J_2)/n_{He},\quad
\dot x_{\mathrm{HeIII}}=J_2/n_{He}.
\]

HeIII→HeII 재결합도 한 사건당 electron을 **하나** 제거한다. HeIII 분율에 charge 2가 있다는 이유로 해당 event source에 -2를 곱하면 안 된다.

RR captured kinetic coefficient는

\[
K_a(T)=k_BT\alpha_a(T)\left(\frac32+g_a\right),\quad g_a=d\ln\alpha_a/d\ln T,
\]

이며 erg cm^3 s^-1다. thermal power는 `n_e*n_upper*K_a`이다. 이미 density가 적용된 R_a에 K_a를 바로 곱하면 alpha를 두 번 적용한다. 사건당 에너지가 필요할 때만 K_a/alpha_a를 쓴다.

DR 두 성분은 같은 HeI ionization edge로 합쳐 species를 만들 수 있지만 thermal energy는 `sum(D_k*epsilon_k)`로 각각 합쳐야 한다. source는

\[
B_1=40.49664394833662\times11605\ \mathrm K,
\quad B_2=8.099328789667\times11605\ \mathrm K,
\]
\[
\epsilon_0=k_BB_1,\quad\epsilon_1=k_B(B_1+B_2)
\]

를 사용한다. 40.49664394833662를 그대로 eV 값으로 쓰지 않는다. 실제 moment를 eV로 변환하면 약 40.4983255744, 48.5979906893 eV다.

## 3. 사건별 에너지 투영

아래 에너지는 사건당 eV다. 최종 proper energy rate에는 사건률과 `EV_ERG=1.602176634e-12`를 곱한다. RR/DR epsilon은 위 source의 erg 값을 EV_ERG로 나눈 것이다.

| 사건 | species 방향 | binding | thermal | photon | escape |
|---|---|---:|---:|---:|---:|
| PI: edge a, photon E | +S_a | +chi_a | E−chi_a | −E | 0 |
| CI: edge a | +S_a | +chi_a | −chi_a | 0 | 0 |
| RR: edge a | −S_a | −chi_a | −epsilon_RR,a | 0 | chi_a+epsilon_RR,a |
| DR: HeII→HeI, k | −S_1 | −chi_HeI | −epsilon_k | 0 | chi_HeI+epsilon_k |

각 행의 energy 합이 0이다. 현재 escape는 **에너지 ledger**이고 recombination photon count나 spectrum을 정하지 않는다. escape를 광자 source로 바꾸는 물리 확장은 이번 Case-A escape bridge와 별개다.

실제 binding 값은 (13.598434599702,24.587389011,54.41776) eV다. sigma cutoff (13.60,24.59,54.42)와 바꾸지 않는다. HeIII 전체 binding은 chi_HeI+chi_HeII이지만, HeII→HeIII **edge 사건**에 적용하는 increment는 chi_HeII다.

한 bundle의 interaction 부분은

\[
Q_{ion}=\mathrm{EV\_ERG}\sum_a\chi_aJ_a,
\]
\[
Q_{th}=\mathrm{EV\_ERG}\sum_{ag}(E_g-\chi_a)P_{ag}
-\mathrm{EV\_ERG}\sum_a\chi_a C_a
-\sum_a n_e n_{a,upper}K_a-\sum_kD_k\epsilon_k,
\]
\[
Q_{esc}=\mathrm{EV\_ERG}\sum_a\chi_aR_a+\sum_a n_e n_{a,upper}K_a
+\sum_kD_k(\mathrm{EV\_ERG}\chi_{HeI}+\epsilon_k),
\]
\[
Q_{\gamma,int}=-\mathrm{EV\_ERG}\sum_{ag}E_gP_{ag}.
\]

따라서 `Qion+Qth+Qgamma_int+Qesc=0`이다. 실제 외부 emissivity의 에너지율 S_E를 넣으면 `Qgamma=S_E+Qgamma_int`이고 `Qion+Qth+Qgamma+Qesc-S_E=0`이다. 수 장부는 `dot N_ref=S_N,ref-a_rel^3 sum(P)`다. 외부 source는 유지하며, interaction reference를 계산한다는 이유로 HM12 source를 zero로 대체하지 않는다.

## 4. 단일 저장 stage 정량 기준

`EVENT_REFERENCE_1STAGE.json`은 **epoch 0 한 점**의 60자리 Decimal 식 평가다. 저장된 2904개 초기 weighted photon node를 사용했다. 후보 함수나 native 코드를 import/실행하지 않았다. 17-epoch campaign 또는 과거 11 histories를 다시 실행한 것이 아니다.

| proper 사건률 [cm^-3 s^-1] | H edge | HeI edge | HeII edge |
|---|---:|---:|---:|
| PI | 4.241383898928e-22 | 4.707427854131e-23 | 5.268843080358e-24 |
| CI | 5.799170187917e-23 | 2.968365607051e-25 | 1.306781532330e-24 |
| RR | 4.821300917710e-22 | 4.302161116644e-23 | 6.575624612687e-24 |

HeII→HeI DR 사건률은 `4.159085584305e-24`, `1.904183514199e-25` cm^-3 s^-1다. RR alpha는 `(1.265627389381e-13,1.474587980477e-13,7.321868393222e-13)` cm^3 s^-1이며 RR captured kinetic은 `(2.95999134516,3.64513196989,3.33983837847)` eV다.

interaction power [erg cm^-3 s^-1]는 thermal 약 `−3.835911428384e-34`, photon `−1.541763420942e-32`, escape `1.580122535224e-32`다. 초기 equilibrium에서 binding 순율은 약 `1.48e-44`로 상쇄된다. Decimal energy residual은 abs-term scale 대비 약 `4.43e-59`이며, 이는 **유도식의 정량 검산**이다. native binary parity나 물리적 정확도 판정이 아니다.

이 initial state는 fixed-T ionization equilibrium으로 만들어져 edge net/absolute-event-scale이 약 1e-12, 1e-12, 1e-15다. JSON은 저장 float의 decimal 문자열, Y=0.24의 정확한 비율, source decimal 상수로 계산했으므로 binary64의 중성분율 subtraction 순서와 bitwise 일치하지 않는다. tiny net derivative를 relative 기준으로 비교하지 않는다. RR/DR/CI/PI primitive 성분과 그 양의 합으로 정규화한 net 차이를 비교한다.

이 reference 한 점은 `a_rel=1`이다. 따라서 **time/volume conversion 검증까지 완료한 것으로 사용할 수 없다.** source bridge가 그 변환도 바꾸면 nonunit a_rel인 저장 마지막 stage의 affected callback 한 번을 추가하거나 동등한 단위 변환 oracle를 사용한다. 그 확인도 ODE history 재실행을 요구하지 않는다.

## 5. 최소 판별 계산 제안

1. 선택 state에서 새 producer가 내는 CI[3], RR[3], DR[2], PI[3], RR kinetic[3], DR energy[2], PI photon-loss/energy를 위 reference와 비교한다. 처음부터 total derivative만 비교하지 않는다.
2. 같은 state/geometry/source에서 **하나의 HeIII RR 사건률만 +delta**인 bounded injection을 넣고 actual RHS 차분을 읽는다. 기대 proper source 차분은 `(0,0,0,+delta,−delta,−delta)`, binding `−chi_HeII*delta`, thermal `−epsilon_RR,HeIII*delta`, escape `(chi_HeII+epsilon_RR,HeIII)*delta`다. event와 energy의 units를 맞춘다. 이 결과가 한 배로 나타나야 실제 소비/단일 소비의 최소 증거다.
3. process별 연결까지 바꾸면 동일 방식으로 PI·CI·DR의 distinct perturbation도 좁게 검사한다. PI는 photon loss와 primary heat를 함께 읽고, DR는 두 번째 resonance처럼 RR와 energy moment가 다른 성분을 선택하면 잘못된 재사용을 판별하기 쉽다. 모든 edge를 보편적으로 변경했다면 보편 claim을 위한 edge별 basis 검사를 별도로 설계한다. 한 RR probe만으로 모든 process mapping을 검증했다고 하지 않는다.

보존식은 exact stoichiometry 확인, event ledger는 정량 mapping 확인, perturbation은 실제 callback 소비 확인이라는 서로 다른 역할을 가진다. count source를 생산하고 보고서에만 저장한 뒤 원래 RHS를 그대로 호출하면 첫 두 개가 맞아도 마지막 검사를 통과하지 못한다.

후보가 원래 binary64 coefficient를 그대로 재사용하면 구 production body와 direct projector의 primitive 값은 매우 가깝거나 동일할 수 있다. 외부 고정 기준과의 tolerance는 parent가 실행 전에 정한다. near-zero J에는 `abs(delta J)/sum(P+C+R+D)`처럼 event scale을 쓰고, 에너지에는 모든 interaction term의 절대합을 쓴다. physics tolerance를 바꾸거나 net cancellation을 맞추도록 계수를 조정하지 않는다.

## 6. 중복/누락 위험

- thermo state에 fixture photon을 되살리고 실제 node PI를 더하면 photo events와 heat가 두 번 들어간다.
- `ft03_rhs.derivative[3]`에 이미 RR/CI/DR cooling이 들어 있는데 bundle의 같은 cooling을 추가하면 이중 계상이다. 새 projector가 그 항을 **대체**하는지 기존 total을 소비하는지 한 경로로 정한다.
- FT03 `alpha_rr[1]`에 DR를 미리 합친 다음 `dr[]`도 빼면 DR가 두 번 들어간다. 두 DR를 합쳐서 하나의 임의 kinetic energy를 적용해도 energy moment가 달라진다.
- raw Grackle alpha/beta를 공급해도 실제 warm stage의 FT03 call은 바뀌지 않는다. `Ft03Model.gas`의 generic alpha/beta는 0이므로 `hhe_rhs`만 호출하면 FT03 thermo가 사라진다.
- 전체 escape를 spectrum이나 emitted photon count로 변환할 원자 정보는 없다. single event photon을 임의 가정하지 않는다.
- `axisym_coupled_derivative`가 u에 -5Hu를 적용하고 native가 w=u/(nH*EV)로 바꾸면서 +3Hw를 돌려준다. 결과는 -2Hw다. 외부에서 -2HT 또는 -2Hw를 다시 더하지 않는다.
- cgs source를 SI로 보낼 때 species/count rate는 1e6, energy density/rate는 0.1이다. native 결과를 되돌릴 때 반대 변환과 reference-volume 변환을 구분한다.
- generic axisym source guard는 baryon/charge/power를 확인한다. 이 선택 H/He 모형에서는 H nuclei와 He nuclei 각각의 보존도 명시적으로 확인할 수 있다.

## 수행 기록과 다음 소비자

새 계산은 단일 source-equation stage reference 1개이며 Decimal sigma 평가 8712회(지원되는 비영 성분 5272개)를 포함했다. wall time 약 1.34초, native build/RHS call/ODE/transport/history replay/NCP/외부 쓰기 0회다. source equality는 code identity이고 실행 provenance나 물리적 타당성을 대신하지 않는다.

parent가 실제 owner survey에 따라 하나의 source/native 경로를 고정하고 candidate를 구현한다. 새로운 native interval을 실행할 경우 source–clean build–binary를 묶는 기존 조건을 유지한다. 이 준비물은 최종 decision reviewer의 판정을 제공하지 않는다.

직접 Decimal 계산식은 `decimal_event_oracle.py`로 보존했다. 원 실행은 stdin 명령이었다. 저장 스크립트는 원 결과 보존을 위해 별도 `EVENT_REFERENCE_REPLAY.json`에 출력하며, source-equation 계산은 동일하다. 저장본은 AST 구문 검사만 수행했고 추가 reference 계산을 실행하지 않았다.
