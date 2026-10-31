# REI F4 Physical Fast | Curtin He II 원전 16채널 비열평형 첫 충돌 연구

**날짜:** 2026-10-31  
**현재 바탕:** PR #315, initial live HEAD `5a70156ec6424d9d9f1adeeb1391fd66939a1318`; 보호된 PR #313 HEAD `47f34ccb68f02262f40cd3dfd198aa97abd35183`, 원본 parent #311 HEAD `63052797e382b438ef375e8389f539118a7e2a0c`, read-only PR #314/#312. **전체 물리적 closure 아님.** `WORKING=33/88; CENTRAL=28/88; PHYSICAL_FAST=4/7; CANONICAL_DELTA=0; F4=PARTIAL; L4_READY=false; PRODUCTION=HOLD`.

## R1 연구 질문

이미 검증된 frozen BASS193 전자-핵종 배경에서 첫 Li II 2E1 광전자 소스 3,840 band의 He II 전자충돌을 **미공개 단면적 추정 없이**, 공개 Curtin CCC He II 원저자 표로 계산할 수 있는가? H I/He I 기존 CCC6, FS2010 Coulomb 정지력과 함께 16개 *선택된* 비탄성 채널을 경쟁시키고, 소스의 `N = ∫dμ`, `M = ∫E dμ`만으로 가능한 He II 사건 수와 최소 여기/결합에너지 구간을 구한다. 새로운 우주론 IVP/온도·광자 생산 소스의 additive injection은 허용하지 않는다.

## R2 원전 확보와 provenance

- 사용자 제공 원본 형식 ZIP `e-HeII_XSEC_LS.zip`: **9,596,492 bytes**, SHA-256 `e32f7d22a3dc54e7981e93369bb98ddd38109a784cff608e59e9657b3a3558db`, ZIP **3,122** 멤버, CRC PASS. 원본 바이트는 수정하지 않았다.
- 공식 원자 CCC 데이터베이스: <https://atom.curtin.edu.au/CCC-WWW/index.html>, He II, 2026-05, `n_i ≤ 9`; 1993 원저자 문헌: I. Bray, I. E. McCarthy, J. Wigley, A. T. Stelbovics, “Calculation of electron scattering on the He+ ion”, *J. Phys. B* **26** (1993) L831, DOI <https://doi.org/10.1088/0953-4075/26/23/006>.
- 이번 계산의 직접 수치 입력은 사용자가 업로드한 ZIP. 공식 링크의 동일 파일 바이트 다운로드는 성공하지 못해 **원저자 서버와 BYTE_IDENTITY=NOT_VERIFIED**. 파일 내 `README`와 헤더의 형식 및 물리 의미는 위 공개 원전 설명과 일치.
- 기존 전체 source PR313 private ZIP `REI_F4_CCC6_FIRST_EVENT_20261031_FULL.zip` **3,813,471 bytes**, SHA-256 `4e8d4602cd2a8105c957fbda90eff23dede3eb7688013eb9d987fa58f870cdd4`, CRC PASS. 이전 CCC6 수치는 Curtin 직접 원본이 아닌 pinned EXHALE reduced snapshot `7388232fac2c3cdadad613515006de008360f1ab`로 고정되어 있어 이번 He II 원자료와 오차/해상도가 균일하지 않다.

## R3 표기 및 단면적 방향과 전하 보존

원본 README에 의하면 파일 `nf.lf.ni.li` 형식은 `nf <- ni` 방향이며 `2P.1S`는 **He II 1s→2p 여기**, `1S.2P`는 역방향 탈여기. `2.1`은 초기 n=1에 대한 최종 n=2 합산 단면적, `2S.1S + 2P.1S`와 같은 채널을 **한 번만** 사용한다. `TICS.1`은 기저상태 총 이온화로 별도 합한다. 단위 `a0²`, `a0² = 2.800285205390782×10^-17 cm²`. 전자 속도 `v(E)=sqrt(2 E*eV_to_erg/m_e)`.

기저상태 He II 표적의 추가 10개 채널: `n=2,3,4,5,6,7,8,9,10` (9개 총합 여기) + `TICS.1` 이온화 (1개). 이전 H I/He I 6개와 함께 16개. He II 실제 화학종 밀도 `n_{HeII}(j)`와 `n_e=n_b q^T Y` (21종 전체 charged bath)를 원래 193 state에서 읽었다. He II 이온화는 `He II -> He III + e`, 1차원 에너지 장부에서 추가 전자 +1, 원자 전하 +1이며 동적으로 갱신하지 않는다.

CCC 원본 기준 바닥상태 이온화 `I_CCC=54.4232 eV`, 여기 임계 `χ_n=I_CCC(1-1/n²)` (fine structure 및 recoil 생략). 과거 PR #315의 NIST 기준 `54.41776 eV`와 **0.00544 eV 차이**가 있어 이번 계산에는 동일한 Curtin 규약을 사용한다. `n=10` 자료의 10,290 eV에서 서로 다른 두 행이 중복되지만, 실제 `E ≤ 60.922559447552 eV`이므로 표는 100 eV 이하만 파싱한다. 원본 파일은 불변.

## R4–R5 선택 이론 및 유도

Metric signature `(-,+,+,+)`; 광속 `c`, Planck 상수 `ħ`의 자연단위 흡수 없이 FS2010 Coulomb 계수를 계승. 전자 kinetic energy `E`는 eV, proper time `t`는 s, 수밀도는 cm^-3, 단면적은 cm². 기존 baseline `LOW=13.7 eV`, `E_PAIR=60.922559447552 eV`; 소스 분포는 원래 저장된 네 first absorber × 5 band의 지지집합과 `N,M`에 한정된다.

\[
 b_{ee}(E,j)=-\frac{dE}{dt}=
 \frac{4\pi(\alpha\hbar c)^2 n_e(j)\ln\Lambda(E,j)}{m_e v(E)\epsilon_{\rm eV}},
 \quad v(E)=\sqrt{\frac{2E\epsilon_{\rm eV}}{m_e}},\quad
 \epsilon_{\rm eV}=1.602176634\times10^{-12}\,{\rm erg/eV}.
\]

`lnLambda(E,j)=ln[4E/(7.40×10^-11 n_e/cm^-3)]`, 실제 domain에서 >1. 각 채널 a는
\[
 h_a(E,j)=\frac{n_{t(a),j}\,\sigma_a(E)v(E)}{b_{ee}(E,j)},\quad
 H(E,j)=\sum_{a=1}^{16}h_a(E,j),\quad [h_a]={\rm eV}^{-1}.
\]

첫 선택된 사건 생존 및 채널별 확률은
\[
 S(E_0,j)=e^{-\int_{E_c}^{E_0}H(E,j)dE},\qquad
 P_a(E_0,j)=\int_{E_c}^{E_0}h_a(E,j)e^{-\int_E^{E_0}H(u,j)du}dE,
\quad S+\sum_a P_a=1.
\]

임의 구간의 누적 hazard `Δ_a≥0`, `Δ=ΣΔ_a`에 대해
\[
 P_a^{k+1}=e^{-\Delta}P_a^k+\frac{\Delta_a}{\Delta}(1-e^{-\Delta}),\qquad
 S^{k+1}=e^{-\Delta}S^k,
\]
여기서 `Δ=0`의 둘째 항은 0. 이 recurrence는 **동일 16채널의 상호경쟁**을 반영하므로 기존 CCC6 yield를 그대로 두고 He II yield를 단순히 더하는 방식이 아니다.

첫 사건 당시 전자 운동에너지 expectation
\[
 G_a(E_0)=\int_{E_c}^{E_0} E h_a(E)\exp[-\int_E^{E_0}H(u)du]dE
\]
를 사용하면, 첫사건 전 Coulomb 전달량 `C_pre = E0 - ΣG_a - E_c S`, 원자 에너지 요구량 `Q_bind=Σχ_a P_a`, 첫사건 후 남은 전자들의 총 kinetic energy expectation `K_post=ΣG_a-Q_bind` (이온화의 두 outgoing electrons 합에너지)이고
\[
 E_0=C_{\rm pre}+Q_{\rm bind}+K_{\rm post}+E_c S.
\]
이 식은 *선택된 첫 사건 장부*의 정리이지 열화·recombination·방출광자 closure가 아니다.

각 원래 band의 측도 `dμ(E)`는 저장된 `N=∫dμ`, `M=∫E dμ` 및 범위 `[E_l,E_u]`만 가진다. 지정된 계산 격자의 선형 보간 kernel `g(E)=P_{HeII}(E)`에 대한 정확한 source moment enclosure는
\[
 N\operatorname{co}(g)(M/N)\le\int g(E)d\mu(E)\le N\operatorname{ca}(g)(M/N),
\]
`co`, `ca`는 lower convex / upper concave envelope다. 서로 다른 출력의 marginal extrema는 동시 실현을 보장하지 않는다. `N g(M/N)`은 단지 collocation 대표값이다.

## R7 실제 계산 결과 (frozen BASS193)

단독 He II 10채널을 기존 6채널과 동일 경쟁 생존 연산자에 포함해 총 **16채널** 계산. 원래 **193 epochs**, **3,840** band, **192** arrival 합계, **1,544** mono 응답. 기준 2100 uniform + 원전 knot => 실제 **3071 energy nodes**. 초기 광전자 `4.374110632809567e-12 /b`, 초기 운동에너지 `6.749242464433258e-11 eV/b`.

| 선택된 첫 사건 | 하한 (/b) | 대표 collocation (/b) | 상한 (/b) |
|---|---:|---:|---:|
| He II 첫 비탄성 전체 | 4.67627994294043e-30 | 4.67629956009751e-30 | 5.81123936681799e-18 |
| He II n=2 excitation | 4.03985793987991e-30 | 4.03985825018464e-30 | 5.81123936649235e-18 |
| He II n=3–10 | 6.35841285428682e-31 | 6.35911660604032e-31 | 3.25633407790593e-28 |
| He II total ionization | 5.29649308835856e-34 | 5.29649308835856e-34 | 1.53719786142765e-33 |
| 16 selected channels | 5.39878455410954e-15 | 5.40979174240706e-15 | 6.50609701378190e-15 |

He II 첫사건의 원자 최소 여기/결합 에너지 moment `1.96277433126489e-28 eV/b` (collocation), upper `2.37199681733900e-16 eV/b`. 첫 He II 충돌에 동반하는 전하/electron 수 변화는 이온화 첫사건의 숫자와 동일하며 collocation `5.29649308835856e-34`개/b (temperature evolution 아님). 16채널 전체는 이전 6채널 결과의 **사후 덧셈이 아닌 전면 재평가**. 이전 6채널 collocation `5.409791742394313e-15 /b`와 새 전체가 거의 일치하나, He II upper는 스펙트럼 미결정성 때문에 크게 열려 있다.

Original data-only kinematic reachability upper of He II n2 was `3.1712e-13 electrons/b`; *actual selected event probability* upper is `5.8112e-18/b`, 약 5.5×10^4배 작다. 이는 단지 문턱 도달 가능한 전자 수와 물리 충돌 확률의 구별이다.

## R6 적대적 검산 결과

1. **File direction:** `2P.1S`, `2S.1S`와 역방향 `1S.2P`, `1S.2S`의 microreversibility \(\sigma_\uparrow=g_f E_f/(g_iE_i)\sigma_\downarrow\), 811 대응 총에너지 열에서 최대 상대 차이 `5.6428e-4` (2P), `5.3217e-4` (2S). `g(2P)/g(1S)=3`, `g(2S)/g(1S)=1`. 이 자료의 반올림 정밀도를 고려하면 file interpretation 지지.
2. **No duplicated partial/summed channel:** `2.1 = 2P.1S + 2S.1S` 동일 표본 812개에서 기계정밀도까지 일치. `3.1,4.1`도 일치; `5.1`, `:.1`과 세부 준위 합에는 54.5–60.9 eV에서 최대 약 **0.24%, 0.74%** 차이가 관찰되므로 원저자 `n`-합산을 이번 source owner로 지정하고 이 차이를 source-semantic uncertainty로 기록한다. 둘을 더하지 않는다.
3. **Threshold basis:** Curtin의 `I_CCC=54.4232 eV`, 이전 NIST `54.41776 eV`; 혼합하면 인위적인 threshold-notch 발생 가능. 전체 uncertainty budget은 원자 표의 실험오차까지 포함하지 않는다.
4. **Domain/duplicated line:** `:.1` 10,290 eV의 서로 다른 마지막 행 2개; 계산은 13.7–60.923 eV이고 원본을 변경하지 않으며 100 eV 이하만 직접 파싱했다.
5. **Kinetic and charge:** 16채널 P+S 정규화 최대 잔차 `8.12e-14`; first-event energy ledger 최대 잔차 `1.42e-14 eV` (부동소수점); 단위 `cm^-3·cm²·cm s^-1/eV s^-1 = eV^-1` 일치.
6. **Independent integration methodology, same-author:** 3개 실제 BASS epoch × 3개 에너지에서 `solve_ivp(DOP853)` ODE와 유한-cell recurrence 비교, He II 확률 최대 상대 차이 `1.3612e-5`, 전체 첫 충돌 최대 `1.8743e-6`. **distinct-author R6 NOT_RUN**.
7. **Grid:** uniform 900+raw knots=1871 nodes; 2100+raw knots=3071 nodes; 4200+raw knots=5171 nodes. He II upper 2100→4200 상대 차이 `2.90e-4`; 전체 16채널 total upper 차이 약 `3.76e-7`. 따라서 He II 상한의 4자리 이상 숫자는 수치 민감도와 조건부 원자 소스 오차를 함께 고려해야 한다.
8. **Scientific limitations:** 모든 He II 표적이 ground `1s`인 근사, He II nf>10/elastic/recoil/angular diffusion 및 E<13.7 eV의 Coulomb/atomic transfers 미포함; 실제 ionization daughter-energy distribution, 이후 cascade, radiation, helium excitation level evolution, temperature/opacity/REI17 F,J 미구현. 기존 input Li II 2E1 조건부 source를 관측량 또는 astrophysical lower bound로 주장하지 않는다.

## R8–R10 물리 판정 및 다음 작업

**SCOPED_SOURCE_CONDITIONAL, numerically checked + implementation verified only for first-event and source N/M enclosures.** He II 원전 수치 파일 사용으로 소스 미확보 blocker는 해소했다. 이전 PR #314 Aggarwal et al. 2017 *Atoms* 5,19 DOI 10.3390/atoms5020019의 Maxwellian rate와 이번 **비열평형 단일 전자 sigma(E)**는 같은 물리량이 아니므로 가산하지 않는다. 다음 과학적 모호성은 3,840 band의 내부 에너지 분포와 충돌 이후 이온화 daughter energy 분배다. 후속 계산은 이원화:

- 합당한 대체: 원래 광전자 spectrum 또는 source generator에서 더 높은 moment(최소 2차)와 spectral histogram을 생산하여 위 큰 `[lower,upper]`를 실제로 좁힐 것. 해당 자료가 없다면 현재 moment hull을 과학적 불확실성으로 보존.
- 이후 초기 16채널 first event와 energy/charge kernel을 **원래 REI17 native F,J source replacement** 포트로 옮기고 excitation radiative cascade/ionization differential daughter spectrum을 분리 구축할 것. 설계 완료만으로 L4 또는 production gate를 통과시키지 않는다.

`NO_MORE_IVPS=true; NO_MERGE=true; NO_FORCE_PUSH=true; NO_BUDGET_RESET=true; AUTO_NEXT_NODE=false`. 이전 PR #315는 read-only source parent, PR #314/#312는 read-only siblings. 별도 native subagent 없음: `native_subagent=NOT_RUN`; 직접 자기 적대적 검산 수행.
