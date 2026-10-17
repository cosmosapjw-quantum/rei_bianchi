# REI `ISO-COUPLE-P2`: H/He/D 공통 사건·열·광자 결합의 구성적 결과

2026-10-17 KST | Parent PR #180 | Scope `PASS_SCOPED_FIXED_VOLUME_MANUFACTURED_PHOTON_BINS`

## 1. 실제 입력의 위계

- 원본 소스 authority: `cosmosapjw-quantum/rei_bianchi` PR #150, commit `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7`. 10개 original source file Git blob identity는 `evidence/SOURCE_IDENTITY.json`으로 별도 재조회/비교한다.
- 선행 개발: PR #179 ISO-EOS, PR #180 ISO-COUPLE-P1 (original Savin temperature-dependent CX-only Heun). 이전 pass 유지; native 공용 production checkout에 변경 없음.
- 전자기 원자율: Grackle v3.4.1 `af7939494ce65007887ada7b98d1813df6843346` 및 Verner 피팅 (`atomic_provider.rs`). D CI/RR/CE 및 PI는 원본 `DAtomicProvider`의 명시적 H-equality approximation을 재사용한다. Savin (2002) 정·역방향 함수는 원래 입력을 보존한다.
- **공급자와 제조 입력의 차이:** 실험용 광자 빈 70/30 eV, 초기 수밀도 120/70 m^-3, 초기 기체와 `chi_D - chi_H = +0.0037 eV`는 **MANUFACTURED**. 연구용 source fit, 입자 수준 원자 물성의 채택, 우주론 광원 이력, 관측 적합이 아니다.

## 2. 공통 EOS와 물리 소유권

원본 `IsotopeNumberState`의 13상태를 그대로 사용하며, 비상대론적 단일온도·단일 공변 기체 정지계를 가정한다. 중성자·T·He3은 결합 화학식의 방관자이나 각 자유전자·전체 열용량에 기여한다. 화학적 변화는 H1, He4, D의 전하 전이에만 발생한다.

\[
 n_B=\sum_s A_s n_s,\quad n_e=\sum_s q_s n_s,\quad n_{\mathrm{th}}=\sum_s n_s+n_e,\quad
 U_{\mathrm{th}}=\frac32 k_B T n_{\mathrm{th}},\quad C_V=\frac32 k_B n_{\mathrm{th}}.
\]

전하 제약은 기존 nuclear charge state에서 n_e를 **한 번** 유도한다. 부가 D 전자, FF, CMB 전력을 다시 추가하지 않는다. HHe source `hhe_events.rs`의 진짜 문턱 `13.598434599702, 24.587389011, 54.41776 eV`를 사용하고 D는 같은 원본 H threshold + 별도 명시 입력을 요구한다.

반응 벡터 `ν`의 좌표를 `(HI,HII,HeI,HeII,HeIII,DI,DII)`로 두면

\[
\nu_H=(-1,1,0,0,0,0,0),\quad \nu_{He1}=(0,0,-1,1,0,0,0),\quad
\nu_{He2}=(0,0,0,-1,1,0,0),\quad
\nu_D=(0,0,0,0,0,-1,1),\quad \nu_{CX}=(1,-1,0,0,0,-1,1).
\]

핵자 가중치 `A=(1,1,4,4,4,2,2)`의 각 `A·ν=0`, 전하 가중치 `q=(0,1,0,1,2,0,1)`의 `q·ν=(1,1,1,1,0)`, CX의 열적 입자 수 변화 `(1+q)·ν_CX=0`이다. Wolfram kernel에서 직접 확인했다. 광이온화에서 전자 증가 1과 photon 감소 1을 합하면 증대된 사건 수 원장이 닫힌다.

## 3. 하나의 광자 → 하나의 흡수자

출생 광자 이력 대신 주어진 `b`번째 유한 원시 빈 `(E_b,N_b)`의 에너지와 개수를 유지한다. 고유시간 간격 `h` 중 흡수자 밀도를 고정하면 다음 식이 **빈별 정확**하다.

\[
\lambda_b=c\sum_a n_a\sigma_a(E_b),\qquad
\Delta N_b=-N_b\operatorname{expm1}(-\lambda_b h),\qquad
\Delta N_{ab}=\Delta N_b \frac{c n_a\sigma_a(E_b)}{\lambda_b}.
\]

총 광자는 한 번만 감소하고, 모든 `a`의 사건 합은 같은 `\Delta N_b`다. 흡수자는 HI/HeI/HeII/DI 네 종. 각 빈 모두 같은 시작 시각의 중성 원자 밀도로 계산하므로, 큰 시간간격에서 **동일 흡수자 중복 소모**의 가능성은 존재한다. 이 경우 결과를 억지로 잘라내지 않고 모든 단계를 `NegativePopulation`으로 거부하며, 작은 `h`를 사용한다. 유한 `N_b`를 전체 source-on EoR 스펙트럼으로 해석하지 않는다.

\[
\Delta U_\gamma=-\sum_{ab}E_b\Delta N_{ab},\quad
\Delta B_{PI}=\sum_{ab}\chi_a\Delta N_{ab},\quad
\Delta U_{\rm th,PI}=\sum_{ab}(E_b-\chi_a)\Delta N_{ab}.
\]

D의 별도 PI 입력을 호출자가 조립해 재사용하는 대신, **바로 이 광자 pool에서 획득한 D 사건과 잉여열만** `DAtomicProvider::photo_input_from_bound_rates`에 제공하고 원래 `d_atomic_rhs`의 photon/binding/thermal PI 열을 정밀 비교한다. 이 RHS를 PI에 추가 적용하지 않는다.

## 4. 원자적 에너지 분배

H/He는 원본 Grackle `igm_rates`의 CI, Case A RR/DR, CE, free-free를 같은 혼합 전자밀도로 호출한다. D는 `d_atomic_rhs`를 CX disabled, PI zero 방식으로 호출해 CI/RR/CE 원장을 가져온다. CI는 binding `+χ` / gas thermal `−χ`, RR은 binding `−χ`, kinetic cooling `−Q_RR`, escaped radiation `+(χ+Q_RR)`, CE/FF는 thermal `−Q` / escaped `+Q`를 **동일 사건마다** 사용한다. HeI metastable CE의 곱은 `n_e^2 n_HeII`이고, D의 free-free/CMB는 `d_atomic_rhs` 내부에서 재계산하지 않는다.

CMB 열 교환 `Q_CMB`는 원본 `igm_thermal.rs`의 CODATA 물리계수와 공통 `n_e`를 이용해 단 한 번 계산한다. CMB 에너지 reservoir는 `-Q_CMB h`; 즉 열원과 reservoir가 부호 반대이다. Case A RR/DR에서 빠져나간 광자는 `U_esc`로 가고, 원시 광자 빈에 새 photon으로 되돌리지 않는다. 온도는 모든 물리단계를 완료한 뒤 재구성된 `U_th / C_V`로 확인한다.

전체 상태의 변화하는 에너지 총량은

\[
\mathcal E=U_{\rm th} +\chi_H n_{HII}+\chi_{HeI}n_{HeII}
 +(\chi_{HeI}+\chi_{HeII})n_{HeIII}+\chi_D n_{DII}
 +\sum_b E_b N_b+U_{\rm escaped}+U_{\rm CMB}\,,
\]

여기서 T/He3 등 방관자 내부 에너지는 고정 상태에 있으므로 이 **변화**의 원장에서는 생략한다. 수치적으로 사건 기반 원장과 재구성 상태의 `\mathcal E`를 따로 점검한다. 작은 사건 변화량을 큰 에너지 재고량의 두 수를 빼는 것으로 검산하지 않는다.

## 5. 시간 적분의 정확도

현재 solver는 `photo (λ-frozen exact attenuation) → nonphoto Grackle+D point Euler → CX(원본 source-bound Heun full/two-half)`를 순차 적용하는 **1차 Lie split**이다. 각 복원 단계의 입력과 출력을 검사하며 원본 전달 상태는 수정되지 않는다. 이 단위의 photon birth=0, 경계 단위는 proper m^-3, J m^-3, s, K; expansion, shear, angular transport, recombination diffuse photon reinjection, nonthermal electron population은 포함하지 않는다.

실제 실험 5 scenarios × N∈{1,2,4,...,256} = **45 histories**에서 `max |ΔE/E|=7.125622657e-16`, `max |Δn_B/n_B|=3.111429243e-15`, `max |(Σ photo events)/(photon loss)-1|=1.763034163e-13`. `helium_mixture`에서 8/16/32 N 격자의 온도 수렴차수는 `p=1.0010235637`로 1차 방식과 합치한다. 이는 **해당 manufactured family의 경험적 국소 결과**다. 최소·최대 입력 조건을 포함한 전역 stiff scheme 수렴 보증이나 전체 cosmological τ 측정은 아니다.

## 6. 출처·검증 범위와 다음 과정

원전: Savin 2002, ApJ DOI `10.1086/324218`; Stancil et al. 1998 ApJ DOI `10.1086/306473`; Grackle 3.4.1 rate functions `https://grackle.readthedocs.io/en/grackle-3.4.1/RateFunctions.html`; Verner et al. 1996 `https://www.pa.uky.edu/~verner/photo.html`. Savin 독립 fit의 detailed balance 불일치 이력도 P1에서와 같이 유지하고 수정하지 않는다.

다음 `ISO-COUPLE-P3`는 실물 source-history 스펙트럼의 입수·광자 birth/cohort, Case A re-emission 재전달, 서로 다른 화학/광원 clock의 동기화, Bianchi-I의 H_i(t), 시간/각도/에너지/age 정밀화 시험이 필요하다. 현재 full `ISO-COUPLE`은 선행 `BI-SIGNED` HOLD 때문에 과학 승격하지 않는다. `FT-B1A`와 reduced history의 mean redshift와 관측방향 observed-z는 별개다.
