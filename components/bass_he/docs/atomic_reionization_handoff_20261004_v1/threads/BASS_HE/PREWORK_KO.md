# BASS_HE: 외부 원자 입력 경로의 선행 물리 연구

작성일 2026-10-04. 범위: 자료 원문 확인, 반응·단위·에너지 회계 유도, 제한 산술 검산. 새 전자구조·산란·thermal integration·cosmological runtime는 수행하지 않았다. 아래 도출 결과와 실제 코드 검증은 구별한다.

## 1. 최신 상태가 바꾸는 선택

현재 branch `research/shared-c64-crossrepo-20260928`의 확인된 HEAD는 `fb36402516f160bf31d87eccb9914c5e0b009f4b`, tree는 `c98b3dd0551451430d3298fd5a0a5806dbda57b9`다. 앞선 외부조사에서 참조한 B5C1 이후 B5C2가 완료·복구되었다. 더 중요한 점은 **B3 원자 rate/count export가 이미 존재**한다는 것이다. API를 새로 만들지 않고 기존 엄격한 request/packet 구조를 재사용한다.

B3의 `GM25_W82_RCX_CONSTANT_200_10000_K_V1`은 `1.70e-13 cm3/s`를 제공한다. García Muñoz 등 [arXiv:2511.21966v1, Appendix B.3](https://arxiv.org/html/2511.21966v1#A2.SS3)을 직접 확인했다. 저자들은 West(1982) 단면적으로 반응률을 계산했으며 200–10000 K에서 위 상수로 근사할 수 있다고 설명한다. Arnaud–Rothenflug(1985)와 일치하고 KF96보다 한 자릿수 이상 크다는 비교도 원문에 있다. 이 단락은 재적분의 세부 수치표·공명 처리·오차 상계를 제공하지 않는다. 본 작업에서 재적분한 것은 아니다.

[Kingdon–Ferland(1996), Table 1](https://uknowledge.uky.edu/physastron_facpub/150/)의 He²⁺ 행은 `1e-14 cm3/s`이며, 유의미한 비복사 기여가 없는 과정의 방사성 계수를 해당 크기로 두는 처방이라는 본문 설명이 있다. 표의 1000–10^7 K 범위가 모든 실제 메커니즘의 정밀 유효범위라는 뜻은 아니다. 두 값의 비는 정확히 17이다. 현재 근거로는 단위오류나 전하상태 오독으로 이 차이를 제거할 수 없다. **source conflict=unresolved; 서로 다른 문헌 선택에 대한 감도 family**로 다룬다. 큰 쪽이 물리 상계, 작은 쪽이 하계라는 주장도 하지 않는다. 두 출처에 충실한 비교 공통 구간은 1000–10000 K다. 범위 이탈 시 명시적으로 거절하고 모형 구간 또는 별도 근거 있는 공급자를 다시 정한다.

기존 B3는 GM25만 실제 구현되어 있다. KF96는 이 계획의 신규 명시적 source 후보다. 두 값을 합산하지 않고, 동일 반응의 대체 scenario로 사용한다. GM25 기존 코어 해시·출력·source conflict 인지 요구를 보존한다. 기존 B3 열·recoil·광자에너지·spectrum·source uncertainty의 `null`은 0으로 바꾸지 않는다.

## 2. 반응 벡터와 자유전자

종 순서를 `(HI,HII,HeI,HeII,HeIII,e)`로 고정한다. ground-state 방사성 전하교환은

\[
\mathrm{He}^{2+}+\mathrm H(1s)\to \mathrm{He}^{+}(1s)+\mathrm H^++\gamma,
\qquad R=k(T)n_{\rm HeIII}n_{\rm HI}.
\]

사건당 벡터는 `nu=(-1,+1,0,+1,-1,0)`다. H핵·He핵·총전하의 선형 보존 벡터와의 내적은 모두 0이다. 직접 자유전자 변화는 0이고 광자 birth는 +1이다. 후속 광흡수는 별개 사건이다. NRCT도 같은 종벡터이나 직접 광자 birth는 0이다. He²⁺ impact ionization은 `(-1,+1,0,0,0,+1)`이므로 CX와 혼동하지 않는다. He⁺+H→He+H⁺는 두전자 과정으로 다른 반응이다.

원자 provider는 `k` 또는 `nu*k`를 출력한다. 밀도곱, 유체 고유시간, 우주론 팽창, 광수송은 소비자가 소유한다. H/He의 부존량을 이미 곱한 rate를 bare coefficient처럼 다시 곱하지 않는다. `thermal_rate`와 `event_count_coefficients`도 한 반응의 두 표현이며 두 source가 아니다.

## 3. 약 40.8 eV의 소유권

이온화 threshold들을 같은 energy_model_id에서 `chi_HI`, `chi_HeI`, `chi_HeII`로 정하면 화학적 에너지 벡터는

\[
w=(0,\chi_{\rm HI},0,\chi_{\rm HeI},\chi_{\rm HeI}+\chi_{\rm HeII},0),
\quad w\cdot\nu=\chi_{\rm HI}-\chi_{\rm HeII}=-Q.
\]

따라서 `Q=chi_HeII-chi_HI≈40.8 eV`다. HeI의 첫 이온화 에너지 약 24.6 eV를 잘못 차감하면 안 된다. 사건당 국소 에너지 보존은

\[
\Delta E_{\rm thermal}+\Delta E_{\rm fast}+\Delta E_{\rm bulk}+E_\gamma-Q=0
\]

이다(필요시 excitation과 recoil 항을 별도 보유). free final-state의 ground RCT에서는 정확히 `E_gamma=Q+E_rel,in−E_rel,out`이며 recoil/COM 운동 항의 convention도 같아야 한다. **상수 k만으로 평균 광자에너지나 열침적률을 복원할 수 없다.** `E_gamma=Q`, prompt heating=0은 사용할 수 있는 별도 근사 closure이지 문헌 반응률에서 유도된 spectrum이 아니다. 이를 사용한다면 consumer의 `MONO_Q_ZERO_PROMPT_HEAT_APPROX_V1` 같은 독립 ID와 한계·감도를 기록한다. 이번 문서는 그 closure를 production에 승인하지 않는다.

이 단순 closure에서 탈출광자라면 chemical sink −Q와 escaping radiation +Q만 기록한다. 국소 흡수라면 photon birth와 absorption을 각자 한 번 기록하고, 흡수체 이온화 threshold와 photoelectron excess heat에 나눠 넣는다. `Q`를 먼저 전체 열로 넣고 광자의 photoheating을 다시 더하면 이중계산이다. RCT의 direct free-electron 변화 0은 이후 photoionization의 +1을 없애지 않는다.

## 4. H/He coupled OTS

에너지별 실제 국소 흡수계수 `kappa_i(E)=n_i sigma_i(E)`에 대해, 모든 해당 광자가 국소 흡수된다고 선언한 OTS 모형은 `p_i(E)=kappa_i/sum_j kappa_j`로 흡수체를 배분한다. escape가 있으면 별도 transport/escape 모형이 필요하며 이 비만으로 escape probability를 결정할 수 없다. 흡수체가 없을 때 0/0을 계산하지 않고 escape/no-local-absorption으로 처리한다.

mono-Q=40.8 eV 예제에서는 HI와 HeI가 흡수할 수 있고 HeII threshold≈54.4 eV 아래다. HI 흡수 시 사건 전체 free-e 증가+1, 열 `Q−chi_HI≈27.2eV`; HeI 흡수 시 +1, 열 `Q−chi_HeI≈16.2eV`다. 이는 rounded-threshold/즉시열화 예제이며 실제 spectrum이나 2차전자의 에너지분배 결과가 아니다. 실제 photon spectrum의 상단·2차전자 처리를 바꾸면 해당 항을 다시 계산한다.

기존 R1 homogeneous `sum n sigma`와 기존 Rust effective opacity/sink coefficient의 의미를 섞지 않는다. 동일 photon의 흡수를 microscopic opacity와 unresolved absorber sink에 중복 귀속하지 않는다. species별 Case-B 계수를 나열하는 것만으로 mixed H/He diffuse field의 OTS가 닫혔다고 선언하지 않는다. 공급자는 sigma/rate만 내보내며 이 소유권 선택은 rei_bianchi 계약에 속한다.

## 5. 실험계 에너지와 Maxwell 평균

두 종이 같은 온도 T의 drift 없는 Maxwell 분포이면 reduced mass `mu=ma*mb/(ma+mb)`를 사용하여

\[
k(T)=\sqrt{8/(\pi\mu)}(k_BT)^{-3/2}\int_0^\infty E\sigma(E)e^{-E/(k_BT)}\,dE.
\]

`E`는 COM 상대운동 에너지다. 서로 다른 Ta,Tb에서는 `Trel=(mb*Ta+ma*Tb)/(ma+mb)`이며 공통 bulk tilt는 상대 drift가 아니다. 유한 drift 또는 실제 비Maxwellian 분포는 별도 평균을 요구한다. Bianchi shear만으로 미시 분포의 비Maxwellian성을 자동 추론하지 않는다.

target-rest에서 projectile energy-per-u가 **실제 projectile mass/u로 나눈 값** epsilon이라면 `E_lab=(ma/u)epsilon`, `E_cm=(mu/u)epsilon`. 기존 C0의 alpha mass/u=4.001506179129와 H mass/u=1.00782503223으로 `mu/u=0.8050611795851188`이다. 질량수 convention으로 E_lab=4epsilon이면 계수가 조금 달라진다. 정수질량 4:1의 0.8은 명시적 근사이며 physical-mass-u 결과와 약 0.6287% 다르다. 원자료의 per-u 정의를 먼저 보존한다.

CollisionDB Agueny 자료 1–100 keV/u는 정수질량 근사로 E_cm=0.8–80 keV다. T=10^4 K의 k_BT≈0.862 eV에 비해 첫 점조차 약 928 k_BT이다. 이 고에너지 표의 Maxwell 적분을 계산해도 저에너지 지배구간을 복구하지 못한다. 하단을 0으로 채우거나 threshold 아래로 외삽하는 것은 데이터가 아니라 새 모형이다. 더 낮은 Janev fit의 100 eV/u도 E_cm≈80 eV에서 시작하며 RCT와 NRCT의 메커니즘 자체도 다르다.

## 6. 이번 채팅에서 닫은 것과 남은 것

`evidence/prework_checks.py`는 exact rational/Decimal로 세 보존 내적, chemical defect, OTS 예제 에너지 합, cm3↔m3 단위, 17배 비율, reduced mass 변환, 공개 표의 무차원 하단을 검산한다. 결과는 `evidence/PREWORK_CHECKS.json`이다. 이 검산은 식·단위의 자체 일관성만 확인하며 source 정확도나 기존 B3 실행을 대신하지 않는다.

현재 완료: 최신 branch/source의 선별 read, GM25/KF96 충돌 확인, 반응·에너지·domain·소유권 계약, legacy 재개 seam, Codex task/acceptance 구성. 남음: KF96 source를 기존 B3 구조에 추가하는 구현, runtime 통합, photon/thermal closure admission, paired cosmological sensitivity. 기존 59/76개 시험의 기록을 이번 실행 PASS로 재표시하지 않는다. 기존 원자 gate가 unresolved여도 문헌 input 기반 시나리오 연구는 진행할 수 있으나 그 결과를 정밀 원자률 인증으로 부르지 않는다.
