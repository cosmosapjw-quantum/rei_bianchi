# HE_DD_INVERSE_RECIPROCITY_20261029: 불변질량 역반응·동일입자 계수

## 0. 계보 및 주장 상한

부모 `cosmosapjw-quantum/BASS_HE` PR106 HEAD `b5ee8c135accb98ba0f9533a4beb0c8c6210933e`, 원자료 `IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871:exforall/M04/M0475.x4` SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`. 이전 중앙 DAG 28/88, HE 14/18, PR105 2/2, PR106 1/2는 유지한다. 현재 신규 국소 과학 단위는 invariant reciprocal kinematics와 source/event semantics 분리 두 노드이며 실제 rate 승격은 하지 않는다.

원전: Arends et al., *Experimental investigation of the 4He(γ,d)d reaction*, Phys. Lett. B 62 (1976) 411–412, DOI `10.1016/0370-2693(76)90671-7`. Silverman et al., *d+d→4He+γ cross section measurement at 376 MeV*, Phys. Rev. C 29 (1984) 35, DOI `10.1103/PhysRevC.29.35`. 후자의 공개 abstract는 T_d=376 MeV에서 CM 73°,91° 측정, Arends 비교비 2.0±0.9 및 1.7±0.9, 시간반전 일관성의 넓은 오차범위를 기술한다. 그 비교비가 원시 DA인지 detailed-balance 변환 후의 비인지는 본 연구에서 원문 full text로 확인하지 못했으므로 정규화 추론에 사용하지 않는다.

## 1. 정의·컨벤션

Metric (-,+,+,+), c를 유지한다. M=M_alpha c²=3727.3794118 MeV, m=m_d c²=1875.61294500 MeV는 PR104 고정 입력이며 최신 핵질량평가로 재인증한 값이 아니다. s=(p_total c)²의 양의 에너지 제곱을 쓴다. 광자 helicity 2, 4He spin 0 (degeneracy 1), d spin 1 (degeneracy 3)이다. 광자/헬륨 초기상태는 비편극, 시간반전 대칭의 spin-summed 2→2 진폭을 전제한다. CM 각도는 시간반전 방향 변환을 거쳐 비교하며 동일 d 교환에 대해 f(theta)=f(pi-theta)이다.

## 2. 불변질량의 양방향 정확 사상 (derived)

광자+정지 4He: s=M²+2ME_gamma. 입사 d+정지 d: s=4m²+2mT_d. 따라서

T_d(E_gamma)=[M²+2ME_gamma-4m²]/(2m),
E_gamma(T_d)=[4m²+2mT_d-M²]/(2M).

두 함수는 정확한 역함수다. 고정 입력에서 E_gamma=213 MeV는 T_d=375.7505606070078278437 MeV, E_gamma=330 MeV는 T_d=608.2630266481291211285 MeV, T_d=376 MeV는 E_gamma=213.1255176097737602415 MeV. 따라서 Silverman의 376 MeV 자료는 330 MeV 정방향 단면적을 직접 정규화하지 않는다. 213 MeV EXFOR 측정과도 0.1255176 MeV 불변질량 대응 오차가 있어 별도 에너지 의존성 가정 없이 같은 실험점으로 취급할 수 없다.

CM 광자 에너지 k=(s-M²)/(2 sqrt(s)), CM d 운동량 에너지 q=p_d c= sqrt(s-4m²)/2. 두 값 모두 MeV이다. 광분해 역치 E_gamma,thr=(4m²-M²)/(2M)>0. q=0에서는 아래 비율이 특이해지므로 threshold에서 미분단면적 비율을 직접 평가하지 않는다.

## 3. 시간반전 reciprocity와 동일입자 정의 (derived)

Spin sum S=Sum|M|², C=1/(64π² s). 동일한 s와 시간반전 대응 CM 방향에서

(dσ/dΩ)_{γα→dd,ordered}=C(q/k)(S/2),
(dσ/dΩ)_{dd→αγ}=C(k/q)(S/9).

따라서 ordered final-d angular density, 또는 inclusive single-D density를 기준으로 하면

R_ordered=(dσ/dΩ)_inverse/(dσ/dΩ)_forward,ordered
         =(2/9)(k/q)²=(2/9)(s-M²)²/[s(s-4m²)].

물리적 event differential을 full sphere에 대칭적으로 확장하면서 1/2!를 적용하는 convention은 f_event,full=f_ordered/2이고, 그 기준 비율은 R_event,full=2 R_ordered이다. 반면 동일 초기 d들의 homogeneous-gas collision *pair rate*에는 1/2 factor가 따로 존재한다. 이것은 differential cross-section의 κ와 동일한 객체가 아니며 중복 적용하면 안 된다.

330 MeV에서 R_ordered≈0.03604202060960059241, R_event,full≈0.07208404121920118482. 이는 이론적 ratio이지 330 MeV의 실측 inverse 단면적이 아니다. 실험의 실제 DA가 ordered/inclusive인지 full-sphere event인지 본 공개 원문·EXFOR만으로는 확정하지 못했다.

## 4. 실제 EXFOR DA로부터 조건부 수치 예시 (derived + numerically checked)

EXFOR M0475002의 E_gamma=213 MeV, θ_cm=73° 행은 DA=0.41±0.09 nb/sr, 330 MeV θ=73° 행은 0.07±0.05 nb/sr이다. ERR-S는 각 행의 통계오차이며 이 연구에서는 좌표별 감도 구간으로만 취급한다. 시간반전, 같은 s, 각도 대응, 위 spin 및 source convention을 추가로 가정하면 E_gamma=213 MeV와 정확히 대응하는 T_d=375.75056... MeV에서:

- ordered/inclusive-D: inverse DA∈[0.00821648004202110,0.01283825006565797] nb/sr.
- full-sphere event-density: inverse DA∈[0.01643296008404220,0.02567650013131594] nb/sr.

330 MeV에 정확히 대응하는 T_d=608.263... MeV에서는:

- ordered/inclusive-D: inverse DA∈[0.000720840412192012,0.004325042473152071] nb/sr.
- full-sphere event-density: inverse DA∈[0.001441680824384024,0.008650084946304142] nb/sr.

위 네 구간은 모두 **정방향 실측 DA를 reciprocity 식에 통과시킨 조건부 예측**이지 역반응 실측값, 독립 사건률 또는 동시 신뢰구간이 아니다. Silverman의 θγ=91°와 Arends의 θd=87°는 각도도 직접 일치하지 않는다.

## 5. Daughter lab boost와 보존법칙 (derived)

γ=(M+E_gamma)/sqrt(s), β=E_gamma/(M+E_gamma), μ=cos θ_cm, q²=(s-4m²)/4라 하면

E_±=(M+E_gamma)/2 ± E_gamma q μ/sqrt(s),
(p_{z,±}c)=E_gamma/2 ± γ q μ,
(p_⊥c)²=q²(1-μ²).

각 daughter의 E_±²-(p_{z,±}c)²-(p_⊥c)²=m², 에너지합 M+E_gamma, z 운동량합 E_gamma는 정확히 성립한다. 사건당 rest-energy 변화 2m-M, kinetic sum M+E_gamma-2m, 광자 에너지 변화 -E_gamma의 합은 0이며 바리온수·전하도 보존한다. 생성률·광자 bath·target response·stopping은 여기서 계산하지 않는다.

## 6. 검증과 남은 물리 의무

Wolfram CAS: inverse-energy composition 2개, s equality, ratio identity 1개 모두 정확 0; 추가 mass-shell polynomial 계수 3개와 ratio identity 1개 정확 0. Python3.13.5 new scoped unittest 32/32 PASS; independent Decimal80 eight cases에서 max error 2e-73 (비교용 Decimal95). 한 차례 검산 harness의 기본 Decimal28 context 때문에 거짓 실패가 발생했으며 precision을 명시해 해결했다. Python numerical lab-boost mass-shell residual <1e-50. 그림 두 개는 물리 단면적 측정값이 아닌 kinematic diagnostic이다. 이전 BASS_HE full suite 및 IVP는 재실행하지 않았다.

남은 물리 게이트: Arends/Silverman full text의 DA normalization, coincidence/acceptance/efficiency, angular/polarization, 330 MeV inverse 또는 qualified total source, 실제 photon field/history, nonthermal D pool, stopping/deposition/Cv. R_event=null, physical_activation=false, L4=false, production=HOLD. Native independent R6/C9 reviewer NOT_RUN.
