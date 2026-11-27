# HE32: Li까지 확장한 LRS Bianchi I 예비 계산의 물리 계약

작성 단위: `HE32 / theory R1–R10`, 운영 규약 `physmath-research-loop 1.0.0`.
이 단위의 산출물은 21개 핵종·전하 상태를 실제 전자 밀도와 연결하는
photoionization–radiative-recombination 모델, 그 구현용 원자율, 보존량 및
범위 검산이다. 다음 코딩 단위가 이를 기존 Einstein–Boltzmann 계에 결합해
z=20→2의 전체 sweep을 실행한다.

## R1. 연구 위치와 완료 계약

사용자 관측량은 공간 정규직교 성분의 Frobenius norm으로 정의한다.

\[
 \Sigma={\sqrt{\sigma_{ab}\sigma^{ab}}\over H},\qquad
 \Pi_i={\kappa_T\sqrt{\pi_{i,ab}\pi_i^{ab}}\over H^2}.
\]

부호는 `(-,+,+,+)`이고, 응력 단위는 J m⁻³이다. 따라서 초 단위 H에
대응하는 결합상수는 \(\kappa_T=8\pi G/c^2\)이다. 이는 계량의
Einstein 상수 \(8\pi G/c^4\)에 시간 좌표 변환의 \(c^2\)를 반영한 값이다.
기존 HE31의 `KAPPA_T`와 같은 규약이다.

연구 대상은 non-tilted LRS Bianchi I, primordial H–He–Li 양의 원자 이온
네트워크이며 추적 상태는 다음과 같다.

| 핵종 | A | Z | 추적 전하 q | 상태 수 |
|---|---:|---:|---|---:|
| n | 1 | 0 | 0 | 1 |
| ¹H | 1 | 1 | 0,1 | 2 |
| D | 2 | 1 | 0,1 | 2 |
| T | 3 | 1 | 0,1 | 2 |
| ³He | 3 | 2 | 0,1,2 | 3 |
| ⁴He | 4 | 2 | 0,1,2 | 3 |
| ⁶Li | 6 | 3 | 0,1,2,3 | 4 |
| ⁷Li | 7 | 3 | 0,1,2,3 | 4 |

총 21개 핵종·전하 population에 전자 census를 붙인다. 사용자 그림에 없던
⁶Li와 Li IV도 포함한다. z=20 전에 붕괴한 ⁷Be의 기여는 채택한 ⁷Li/H에
흡수하고, 더 짧게 사는 Li 동위원소는 이 post-BBN 초기 inventory의 동적
상태로 두지 않는다. 음이온·분자·전자 충돌 이온화·DR·전하교환·준위별
전달은 이번에 선택한 원자 photo/RR closure의 확장 과제다. 이 범위는
`PHYSICS_CONTRACT.json`에서 한 번에 관리한다.

완료 기준은 원표에서 확인한 여섯 원자 전이쌍, 단위와 정규화가 명시된
21-state lifting, 핵반응 감소의 조건부 오차 추정, 양성성/보존량 검산,
다음 코딩에 필요한 수치 입력 제공이다. 관측 재이온화 이력의 보정이나
완전한 분자·핵반응 네트워크의 새 검증은 이 결과의 완료 주장에 포함하지 않는다.

## R2. 최신 근거와 실제 재사용

최신 GitHub/백업 조사 결과에서 다음을 사용했다.

| 근거 | 실제로 재사용한 부분 | 근거 상태와 선택 |
|---|---|---|
| REI PR211, `c9deb933761a8d2593d1176aee028cd423bdbc05` | `isotope_state.rs`, `TARGET_NETWORK_19.json`, Li RR/CI 원표와 provenance | 기존 13-state 전하 규약과 그림의 19개 반응 번호를 계승 |
| PR211에 보존된 `lithium_rates.rs`, 원본 `fd9a21c4…` | Badnell/Voronov 계수의 적용 구간, 동위원소 전자율 동일시 | 전체 thermal bundle의 5 eV 하한은 20000 K 밖이므로 전체 bundle을 그대로 호출하지 않음 |
| REI PR151, `8a4f5df4…`, `li_thermal_rates.py` | Verner PHFIT2/VF1996 공식과 선택 행, 고정 source SHA | 새 Python provider의 독립 원표 대조에 사용 |
| PR151 `NUCLEAR_PRIOR_RESULT.json` | Y₄=.2468382676, D/H=2.503248144e-5, ³He/H=1.049996333e-5, ⁷Li/H=5.36802116e-10 | central composition 시나리오로 사용. 원본 상태는 mechanical pass/pending review이며 covariance를 채택하지 않음 |
| HE31 receiver 및 HE29 vendor | Frobenius 정규화, canonical massive moments, gamma/nu 분리 | 기존 물리 계의 단위·정규화를 유지하고 전자 공급원을 교체 |
| Verner et al. 1996 및 Verner–Ferland 1996 공식 자료 [S1,S2] | ground-state photo fit와 total RR의 실제 숫자 | 내려받은 원표의 SHA와 각 행을 대조 |
| Cyburt et al. 2016, Table II [S3] | ⁶Li/H가 10⁻¹⁴ 규모인 fiducial 결과 | 이번 입력은 명시적 1e-14 trace 시나리오; 원문 수치는 1.288e-14 |
| Switzer–Hirata 2005 [S4] | 초기 우주 재결합 UV에 의한 Li 중성분 억제 | z20의 LiII=1은 이 물리에서 착안한 초기 시나리오로 구분 |
| NIST SRM4361C, Table 1 [S5] | T 반감기 4500 day | exact decay-control의 고정 입력 |

PR151 BBN 계산의 \(\Omega_bh^2=0.02205\)와 receiver cosmology는 다르다.
채택한 조성은 별도로 지정한 중앙 조성 입력이다. 그 값에 BBN covariance나
현재 cosmology와의 일치성을 부여하지 않는다. 해당 source output의 ³He/H와
⁷Li/H를 late composition 입력으로 직접 채택하므로 별도 T/Be7 잔량을 다시
더하지 않는다.

공식 원표 바이트는 `sources/SOURCE_MANIFEST_SUCCESS.json`, 선택한 6행은
`data/ATOMIC_PHOTO_RR.json`에 고정했다. 두 원표 SHA는 다음과 같다.

```
photo.dat a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389
table1.dat 2382f6896fe58ee1da58c9bd563fd7d02c0d94410dbd4150767eed26a54f5091
```

Exa 검색은 원전/공식 데이터의 발견에, SciSpace는 초기 원시 화학/리튬 문헌
교차 탐색에 실제 사용했다. 최종 숫자는 원표와 원문에서 확인했다. SciSpace
목록에 섞인 저장소 날짜나 비검증 확장 주장은 수치 근거로 채택하지 않았다.
Wolfram Language를 실제 호출해 보존행렬·LRS norm·각분포 양성성·Gamow
최솟값과 별도 고정밀 원자율을 계산했다.

## R3. 주장과 가정의 분리

아래의 선택이 이론과 코드의 공통 입력이다.

1. 전자·이온은 공통 Maxwellian gas temperature \(T_g=20000\,K\)를 가진다.
   온도와 UV는 외부 지정이며 광원 방정식·열균형을 동시에 푸는 모델은 아니다.
2. UV의 photon-number flux는 \(\Phi_E=C E^{-5/2}\),
   \(5.392\le E\le60\,eV\)이고 그 밖에서 0이다.
3. 정규화는
   \[\Gamma_{HI}(z)={10^{-12}\over1+\exp[(z-6)/0.3]}\ s^{-1}\]
   이다. 이는 넓은 stress sweep에 쓸 명시적 smooth input이며 관측 보정된
   재이온화 광원이 아니다. 초기 검토안의 중심 z8/폭.8은 \(\Gamma/H\)가
   너무 이른 시기에 커져 최종 채택 전에 중심 z6/폭.3으로 교정했다.
4. 원자 반응은 single photoionization과 total radiative recombination이다.
   electron-impact CI/DR를 제외한 영향의 작음을 별도로 주장하지 않는다.
5. 한 원소의 동위원소는 동일한 전자율을 사용한다. 동위원소 shift를 버린
   leading electronic approximation이다.
6. 초기 n=T=0, H/D 이온분율 2e-4, He 중성, LiII=1이다. 모든 이온 단계의
   연산자와 출력은 유지한다. LiIII/IV가 0으로 유지되는 것은 support와
   초기조건이 주는 해이며 단순히 목록에 넣고 빠뜨린 구현이 아니다.
7. primordial atomic gas는 등방성 유체 \(\pi_b=0\)로 닫고, 기존 massive
   nonbaryonic sector \(f_m=0.1\)가 \(\pi_m\)를 담당한다. 방사선은
   photon과 neutrino 기여를 별도로 계산한다.

이 가정 아래 exact statement, 조건부 추정, numerical check를 구분한다.
photo cutoff 때문에 선택 UV가 주는 높은 문턱 전이의 0은 exact statement다.
S-factor envelope 아래 핵융합 감소는 조건부 추정이다. 392개 sweep의 IVP
성공과 plot 완성은 다음 코딩 단계에서 얻을 별도 실행 근거다.

## R4. 표현 선택과 경량화

full21를 독립 미지수로 그대로 적분하는 표현과 원소별 charge fraction을
공유하는 표현을 비교했다. nuclear source를 제거한 선택 계에서는
원소별 분율을 2+3+4=9개 slot으로 계산하고 각 동위원소의 abundance를
곱하여 21개 population을 정확하게 복원할 수 있다.

동위원소 A,B의 전하 분율 차이 \(\delta=f_A-f_B\)는 공통 전자밀도에
대해 \(\dot\delta=Q_Z[n_e(t),T,\Gamma]\delta\)를 만족한다. 초기
\(\delta=0\)이면 선형 ODE의 유일성에 의해 계속 0이다. \(n_e\) 자체가
전체 조성에 의존하여 비선형이어도 두 동위원소가 보는 행렬은 같으므로
이 논증은 유지된다. 각 원소 simplex 제약을 쓰면 formal degree of
freedom은 1+2+3=6이다.

이 축약은 비영점 n/T decay-control에는 적용하지 않는다. 붕괴가 다른
원소의 특정 전하 상태에 입자를 주입하므로 그 검산은 full21 operator에서
수행한다. pilot IC에서는 zero invariant에 의해 같은 항이 정확히 소거된다.

따라서 고정 \(T_g\)에서 여섯 RR 계수와 spectrum integrals를 한 번만
준비하고, RHS에서는 단일 UV amplitude와 전자밀도로 9분율을 갱신한다.
이 선택은 isotope population과 전자 opacity를 유지하면서 반복 계산을 줄인다.

## R5. 구성적 유도

### R5a. 원자율과 UV 정규화

각 photo pair의 Verner fit [S1]은

\[
 \sigma(E)=\sigma_0[(x-1)^2+y_w^2]
 y^{P/2-11/2}(1+\sqrt{y/y_a})^{-P},\quad
 x=E/E_0-y_0,\quad y=\sqrt{x^2+y_1^2}.
\]

단면적의 원표 단위 Mb는 \(10^{-18}\,cm^2\)이다. 문턱 아래는 0이고
원표의 Emax 밖으로 외삽하지 않는다. 선택 spectrum의 상한60 eV는 가장
낮은 Emax=64.39 eV(Li I) 안에 있다.

\[
 I_j=\int_{\max(E_{th,j},5.392)}^{60}
 E^{-5/2}\sigma_j(E)\,dE,\qquad
 \Gamma_j=\Gamma_{HI}{I_j\over I_{HI}}.
\]

하한이 상한 이상이면 적분은 0이다. LiII→LiIII의 문턱75.64 eV와
LiIII→LiIV의 문턱122.5 eV에 대해 정확히 이 경우가 된다.

VF1996 total RR [S2]는

\[
 \alpha_j(T)=\frac{a_j}{\sqrt{T/T_{0,j}}
 (1+\sqrt{T/T_{0,j}})^{1-b_j}
 (1+\sqrt{T/T_{1,j}})^{1+b_j}}.
\]

총 재결합을 사용하므로 case A이다. He I는 기존 PR151과 같은 broad-range
b 행을 사용한다. 공식 표의 He I b 유효범위3–1e10 K/rms4.7%는 수치 구현
정확도와 구별하며, 전체 provider의 공통 범위는3–1e9 K로 둔다.

| 전이 lower ion | Γ/ΓHI | α(20000 K), cm³ s⁻¹ |
|---|---:|---:|
| H I | 1 | 2.5222817322050724e-13 |
| He I | 0.597858946081651 | 3.0796903995902207e-13 |
| He II | 0.01063343052799649 | 1.366322318674933e-12 |
| Li I | 2.215704764089562 | 1.391629532798999e-13 |
| Li II | 0 | 1.2628434754500734e-12 |
| Li III | 0 | 3.5503483003698474e-12 |

### R5b. charge chain, abundance와 전자 보존

원소 Z의 fraction vector를 \(f_0,\ldots,f_Z\)라 쓰면

\[
 \dot f_q=\Gamma_{q-1}f_{q-1}+n_e\alpha_qf_{q+1}
 -(\Gamma_q+n_e\alpha_{q-1})f_q
\]

이며 범위 밖 계수를 0으로 정의한다. \(\alpha_q\)는 q+1→q pair의
재결합 계수다. \(\sum_q\dot f_q=0\), 모든 off-diagonal rate≥0이므로
simplex가 보존된다. 로그 scale factor \(N=\ln(a/a_{20})\)에서는
오른쪽 전체를 **실제 target \(H(N)\)**로 나눈다.

\[
 n_{A,q}=n_{H,0}(1+z)^3r_Af_{Z,q},\qquad
 n_e=\sum_{A,q}q\,n_{A,q},\qquad
 n_{H,0}={\Omega_b\rho_{crit,0}\over m_u\sum_A A r_A}.
\]

이는 질량번호 \(A m_u\)를 사용하는 baryon census 규약이다. nuclide
mass defect를 별도로 계산하는 EOS는 아니다. 채택한 Y₄를 정확히 얻으려면

\[
 r_{He4}={Y_4(1+2r_D+3r_{He3}+6r_{Li6}+7r_{Li7})\over4(1-Y_4)}
 =0.0819407011917237.
\]

이에 따라 \(\sum A r_A=1.3278443733774397\),
\(n_{H,0}=0.19082106859398723\ m^{-3}\)이다. 전자 공급원은
\(\Gamma_T=c\sigma_T n_e\)로 photon hierarchy에 들어가고
\(d\tau_T/dN=\Gamma_T/H\)로 optical depth를 함께 적분한다.
Neutrino collision term에는 이 값을 넣지 않는다.

각 atomic forward event의 baryon 변화는0, ionic charge 변화는+1,
free-electron 변화는+1이다. 전하벡터에서 전자 계수를−1로 두면
모든 atomic stoichiometry column의 총전하는0이다. weak operator는
\(n_0\to H^++e^-+\bar\nu_e\),
\(T_q\to{}^3He_{q+1}+e^-+\bar\nu_e\) (q=0,1)로 둔다.
총 baryon과 총전하가 모두 보존된다. neutron mean lifetime878.4 s,
T half-life4500 day를 사용하고 유한 시간의 소실량은
\(-\mathrm{expm1}(-\lambda\Delta t)\)로 계산할 수 있다.

### R5c. 원본 19개 반응의 상태

그림 오른쪽 목록의 번호를 유지하고 중복 inverse를 명시한다.

| ID | 반응 | 이번 선택 계에서의 처리 |
|---:|---|---|
| 1 | HI+γ ↔ HII+e | H/D/T 각각 photo/RR; T inventory0 |
| 2 | HeI+γ ↔ HeII+e | ³He/⁴He 각각 photo/RR |
| 3 | HeII+γ ↔ HeIII+e | ³He/⁴He 각각 photo/RR |
| 4 | ⁴He+γ ↔ ³He+n | UV photobreak0; inverse n capture의 source inventory0 |
| 5 | ⁴He+γ ↔ T+p | UV photobreak0; inverse charged freezeout |
| 6 | ⁴He+γ ↔ D+D | UV photobreak0; inverse charged freezeout |
| 7 | ³He+γ ↔ D+p | UV photobreak0; inverse13과 같은 channel |
| 8 | D+γ ↔ p+n | UV photobreak0; inverse12와 같은 channel |
| 9 | T→³He+e+antiν | full21 exact decay operator; pilot T0 |
| 10 | n→p+e+antiν | full21 exact decay operator; pilot n0 |
| 11 | ⁷Li+γ ↔ ⁴He+T | UV photobreak0; inverse19와 같은 channel |
| 12 | p(n,γ)D | n inventory0; secondary event budget 포함 |
| 13 | D(p,γ)³He | charged freezeout |
| 14 | D(D,p)T | charged freezeout |
| 15 | D(D,n)³He | charged freezeout |
| 16 | T(D,n)⁴He | charged freezeout |
| 17 | ³He(D,p)⁴He | charged freezeout |
| 18 | ³He(n,p)T | n inventory0; secondary event budget 포함 |
| 19 | T(α,γ)⁷Li | charged freezeout |

Li atomic 세 pair는 위 원본 목록 밖에 추가하여 ⁶Li/⁷Li 각각 적용한다.
원본의 핵반응4–19가 source-native fully reactive solver에서 모두
구현되었다고 재표시하지 않는다. 여기서는 아래 계산으로 지정한 저온
감소 모델을 구현한다.

### R5d. charged nuclear freezeout의 조건부 상한

상대 Maxwell 분포, bare Coulomb factor와 다음 envelope를 가정한다.

\[
 \sigma(E)={S(E)\over E}e^{-\sqrt{E_G/E}},\quad
 E_G=2\mu c^2(\pi\alpha Z_1Z_2)^2,\quad
 0\le S(E)\le10^6\ {\rm keV\,barn}\quad(E>0).
\]

Smax는 채택한 보수적 envelope 조건이며 모든 에너지에서 측정으로 입증한
보편 상한으로 취급하지 않는다. Maxwell 평균은

\[
 \langle\sigma v\rangle=\sqrt{8\over\pi\mu}(k_BT)^{-3/2}
 \int_0^\infty S(E)e^{-E/(k_BT)-\sqrt{E_G/E}}\,dE.
\]

지수의 \(E/k_BT\)를 반씩 나누고
\(g(E)=E/(2k_BT)+\sqrt{E_G/E}\)라 놓으면
\(g''>0\), \(E_*=(E_G(k_BT)^2)^{1/3}\)에서
\(g_{min}=3(E_G/(8k_BT))^{1/3}\)이다. 남은 지수의 적분은
\(\int_0^\infty e^{-E/(2k_BT)}dE=2k_BT\)이므로

\[
 \boxed{\langle\sigma v\rangle\le
 2\sqrt{8\over\pi\mu}{S_{max}\over\sqrt{k_BT}}
 \exp\!\left[-3\left({E_G\over8k_BT}\right)^{1/3}\right] .}
\]

목표 charged entrance의 최소 \(\mu=2m_u/3\), \(Z_1Z_2=1\),
\(T\le20000 K\)를 쓰면 \(E_G=652.7535625\,keV\), 지수108.5275622,

\[
 \langle\sigma v\rangle\le2.153542726\times10^{-56}\ cm^3s^{-1}.
\]

이 온도 구간에서 우변은 온도에 대해 증가한다. 감소질량과 전하곱을
증가시키면 지수가 더 억제되므로 이 선택이 공통 상한이다.
\(n_{partner}\le0.01\,cm^{-3}\), \(\Delta t\le1.1\times10^{17}s\)이면
각 channel의 event/baryon은 \(\epsilon=2.368896998\times10^{-41}\)
이하다. 실제 초기 baryon density는0.0023465585 cm⁻³이다. 이 시간 상한은
양의 다른 sector를 버린 dust floor
\(H\ge H_0\sqrt{0.9\Omega_m}\,a^{-3/2}\)로부터
\[\Delta t\le{2[(1/3)^{3/2}-(1/21)^{3/2}]\over3H_0\sqrt{0.9\Omega_m}}
=1.043600894\times10^{17}s<1.1\times10^{17}s\]
로 확인된다. 초기 검토안의1e17 s 대신 이 사전 상한을 채택한다.

원본19에서 inverse를 중복 제거하면 charged entrance는8개다. 그 event
총수는8ε/baryon 이하이고 각 event가 만드는 자유 neutron은 최대1개다.
각 neutron은 capture 또는 decay에서 한 번 소비된다. T 생성은 charged
event와 neutron capture의 합 이하이므로 T decay는16ε 이하이다. 따라서
전체 nuclear event는32ε/baryon 이하이며, 각 event의 baryon-weighted
stoichiometric L1은 최대14이다. 결과적으로 nuclear abundance change는

\[
 \sum_A A|\Delta Y_A|\le448\epsilon
 =1.061265855\times10^{-38}
\]

이다. 이 마지막 합산 상한은 원본19의 finite registry에 대한 결과다.
추가 ⁶Li 핵반응을 포함하는 확장에는 같은 단일 charged-channel 추정과
그 확장의 유한 channel 수를 적용한다.

photodisintegration0은 선택 UV support가 모든 target nuclear breakup
threshold 아래라는 조건에서 정확하다. CMB hierarchy는 주파수 적분된
응력 계로 유지하며 고에너지 광핵 provider에는 넣지 않는다. 무한 support의
실제 Planck tail까지 수학적으로0이라는 주장은 이 계산에 쓰지 않는다.

### R5e. 외부 UV와 gas energy의 크기

등방 UV의 에너지밀도는 \(u_{UV}=c^{-1}\int E\Phi_EdE\)이고,
위 정규화에서 \(\Gamma_{HI}\le10^{-12}\)이면
\(u_{UV}\le1.0822180234\times10^{-16}\ Jm^{-3}\)이다.
z2에서 baryon rest energy가 최소이므로 전 구간에 대해

\[
 {u_{UV}\over\rho_b c^2}\le1.05995394\times10^{-7},\qquad
 {u_{thermal}\over\rho_b c^2}\le4.6941610\times10^{-9},\qquad
 {u_{atomic\ binding}\over\rho_b c^2}\le1.6230611\times10^{-8}.
\]

열에너지 상한은 모든 핵이 최대 전하까지 이온화했을 때
\((3/2)(n_{nuc}+n_e)k_BT\)를 사용했고, binding 상한은 실제 조성의
이온화 문턱을 합쳤다. 표준 등방 total background와의 UV 비율은 z2에서
1.5343e-8이다. 이들은 Einstein RHS의 instantaneous omitted-energy
크기에 대한 bookkeeping 근거다. 외부 thermostat의 이력 자기일관성이나
CI/DR 생략오차에 대한 상한으로 사용하지 않는다.

### R5f. LRS norm, 초기 positivity와 관측량

\[
 ds^2=-c^2dt^2+a^2[e^{-2\beta}(dx^2+dy^2)+e^{4\beta}dz^2],
 \quad D=\operatorname{diag}(-1,-1,2),\quad
 \sigma=\dot\beta D,\quad\pi_i=p_iD.
\]

\(\mathrm{tr}D^2=6\)이므로
\(\Sigma=\sqrt6|\dot\beta|/H\),
\(P_i=\sqrt6\kappa_Tp_i/H^2\), \(\Pi_i=|P_i|\)이다.
정규화 전의 응력을 먼저 더하므로
\(P_r=P_\gamma+P_\nu\),
\(\Pi_{total}=|P_m+P_r|\)이다. \(\Pi_m+\Pi_r\)는 상쇄를 보존하지 않는다.

Hamiltonian constraint는
\(H^2=H_{iso}^2+\dot\beta^2\)이므로
\(H^2=H_{iso}^2/(1-\Sigma^2/6)\)이다.
선택한 \(\Sigma_0\le0.6\)에서 분모는 최소0.94로 양수다.
massive/radiation의 초기 각분포 \(W=1+A P_2(\mu)\)는
\(-1\le A\le2\)에서 양수 또는0이다. 이는
\(P_2\in[-1/2,1]\)로 직접 확인된다.

방사선 \(P_r\)를 A로 바꿀 때
\[
 A_r={5P_r\over\sqrt6\,\Omega_{r,initial}^{(H)}}
 = {5P_r(1+q_0^2)\over\sqrt6 f_r},\quad
 q_0={\Sigma_0\over\sqrt{6-\Sigma_0^2}}.
\]

massive A는 기존 canonical quadrature의 unit-A stress를 사용해 같은
Frobenius 정규화로 역산한다. 코드에서는 모든 case의 A domain을 실제로
확인한다. norm axis는 양수로 그리고 signed P를 함께 보존하여 상쇄와
stress 방향이 바뀌는 case를 구별한다.

## R6. 독립 검증 결과

`WOLFRAM_STOICHIOMETRY.json`에서 21 nuclear-ion+electron22 열과 13 atomic
전이 column의 baryon·전하 잔차는 모두0이다. weak 세 column도0이다.
LRS norm factor6, P2의 extrema와 \(-1\le A\le2\)도 같은 도구에서 확인했다.

`WOLFRAM_GAMOW_BOUND.json`은 minimizer의 미분 잔차0, 양의2차미분,
최솟값과 남은 적분2kT를 기호적으로 확인한다.

원자율은 별도로 전사한 exact decimal 계수와 Wolfram 40자리 adaptive
NIntegrate를 사용해 비교했다. 이는 NumPy 128-point Gauss–Legendre
경로와 다른 수치 방법이다. `ATOMIC_SOURCE_ORACLE_COMPARISON.json`에
RR 최대 상대오차와 photo ratio 최대 절대오차가 보존되어 있으며 각각
2e-14,2e-12의 구현 비교 기준을 통과했다.

다른 agent가 공식 원표6행·원표 SHA·원 PHFIT2와 PR151 단면적의18개 점,
50자리 RR6개를 독립 대조했다. 판정은 `PASS_SCOPED_PHOTO_RR_PROVIDER`이고
근거는 `../upstream/INDEPENDENT_ATOMIC_REVIEW.json`이다. 이 검토는 수치
공식/원표 대응을 대상으로 하며 선택 UV나 isothermal scenario의 관측
타당성에 점수를 부여하지 않는다.

## R7. 작은 판별 계산

실제 실행 명령:

```
python investigation/he32/physics/code/derive_physics_contract.py
```

실행은 source-oracle 비교, nuclear bound, UV/gas energy bound, 정확한
baryon normalization을 출력하고 기계 계약을 만든다. 성능 benchmark나
IVP suite를 추가하지 않았다. 원자 provider 자체의 64/128-point 차이는
최대3.38e-14였으며, 작은 quadrature부터 독립 고정밀 값까지 같은 방향의
계수/정규화를 확인했다.

이 계산의 판별 결과는 Li photo upper pairs=0이 cutoff의 물리적 귀결임을
확인하고, 타당 범위 밖 thermal-bundle extrapolation 없이 모든 charge
stage에 적용 가능한 RR 계수를 확보한 것이다. 해당 결과에 의존하는
새 계산은 이번에 채택한 photo/RR model의 21-state evolution이다.

## R8. 결과 판정

| 결과 | 근거 수준 | 채택 범위 |
|---|---|---|
| 6-pair photo/RR provider | literature-supported, implementation-verified | source-domain 원자율 |
| 9-slot→21-state lifting | derived, 보존량 independently checked | isotope-equal rates/IC와 zero nuclear source |
| 핵융합 감소 상한 | derived, symbolic/numerical checked | 명시한 S envelope·density·temperature·time 조건 |
| UV/gas energy 누락 크기 | derived, numerically checked | 지정 UV/temperature의 instantaneous background bookkeeping |
| LiII 초기값, UV 이력, 등온 gas | prescribed input | pilot scenario |
| 전체 sweep/plot | 다음 코딩 단위에서 실행 | 이 노트의 수치 실행 완료 주장과 분리 |

새 strong no-go 정리를 제시하지 않았으므로 NG1–NG7의 novelty admission은
적용 대상이 아니다. 선택한 에너지 support에서 적분영역이 빈 사실과
양성성 domain을 새 불가능성 성과로 재명명하지 않는다.

watchdog의 구체적 수정은 다음 세 가지다. 기존 전체 Li thermal bundle은
20000 K를 벗어나므로 유효범위 안의 source-pinned photo/RR 표현으로
교체했다. formal species 목록만 늘리는 문제는 전자 census와 opacity에
모든 isotope population을 연결해 해소했다. 약붕괴가 없는9분율 축약을
비영점 n/T test에 적용하는 오류는 control 전용full21 연산자로 분리했다.

## R9. 코딩 입력 계약

`code/atomic_photo_rr.py`의 API는 다음과 같다.

```python
from atomic_photo_rr import AtomicPhotoRR
provider = AtomicPhotoRR(data_path=path_to_atomic_json)
values = provider.rates(T_K=20000., uv_amplitude=gamma_HI)
# values['ionization_per_s']: [HI,HeI,HeII,LiI,LiII,LiIII]
# values['recombination_cm3_s']: same pair ordering
# values['thresholds_eV'], values['metadata']
```

단면적과 spectrum integrals는 constructor에서 한 번 계산한다. 같은
provider를 재사용하며 T와 amplitude는 finite/domain을 검사한다.
기본 데이터 위치는 module의 부모 디렉터리 바깥 `data/ATOMIC_PHOTO_RR.json`이다.

`PHYSICS_CONTRACT.json`은21 states, isotope priors, initial fractions,
UV/temperature, electron lifting, signed norm, weak operators와scope를
기계가 읽는 형태로 제공한다. `NUCLEAR_FREEZEOUT_BOUND.json`과
`UV_GAS_ENERGY_BOUND.json`은 해당 조건과 계산값을 함께 제공한다.

최종 receiver는 (i) target H 안의 live chemistry, (ii) 동일 ne의 photon
Thomson term와 optical depth, (iii) separate Pi_m/Pi_gamma/Pi_nu/Pi_r,
(iv) 21 population 출력을 연결한다. 만일 provider input/UV/temperature가
바뀌면 새 의존성인 원자율·freezeout/energy bound부터 재평가한다.

## R10. 종료, 보존과 다음 DAG

이 물리 단위는 위 조건으로 코딩 가능한 유도와 provider를 완료했다.
실제 파일과 원표 identity는 `PHYSICS_ARTIFACT_MANIFEST.json`으로 묶는다.
parent가 전체 캠페인의 backup/publication receipt 및 phase ledger에
이 파일들을 포함한다. 이 분담 단위는 외부 push나 원격 backup을 별도로
수행했다고 표시하지 않는다.

다음 DAG는 `R10 → final coding C1–C5 (chemistry/receiver integration)
→ C6–C7 (small coupled checks) → C8–C10 (392-case run, plots, packaging)`이다.
원표·source oracle·기존 canonical formula의 identity가 같으면 재감사하지
않고 사용한다. 새 실행에서 관측한 positivity/hierarchy truncation 위험은
그 case의 guard calculation으로만 확인한다.

### 출처

- [S1] D. A. Verner et al., 1996, *ApJ* **465**, 487, photoionization fits.
  공식 데이터: https://www.pa.uky.edu/~verner/photo.html ;
  https://www.pa.uky.edu/~verner/dima/photo/photo.dat .
- [S2] D. A. Verner and G. J. Ferland, 1996, *ApJS* **103**, 467.
  공식 데이터/설명: https://www.pa.uky.edu/~verner/rec.html ;
  https://www.pa.uky.edu/~verner/dima/rec/table1.dat .
- [S3] R. H. Cyburt, B. D. Fields, K. A. Olive, T.-H. Yeh, 2016,
  *Rev. Mod. Phys.* **88**, 015004, Table II.
  https://arxiv.org/abs/1505.01076 ; https://arxiv.org/pdf/1505.01076 .
- [S4] E. R. Switzer and C. M. Hirata, 2005, *Phys. Rev. D* **72**, 083002.
  https://arxiv.org/abs/astro-ph/0507106 .
- [S5] NIST SRM4361C certificate, Table1 and reference3
  (Lucas–Unterweger, 2000).
  https://tsapps.nist.gov/srmext/certificates/4361c.pdf .
- [S6] Galli and Palla, 1998, *A&A* **335**,403, primordial chemistry inventory;
  source of the broader molecular-network comparison, not adopted rate values.
  https://arxiv.org/abs/astro-ph/9803315 .
- [S7] REI PR151/PR211 and HE31/HE29 source files listed in R2;
  exact recovered bytes and git blob proofs are in `../upstream/`.
