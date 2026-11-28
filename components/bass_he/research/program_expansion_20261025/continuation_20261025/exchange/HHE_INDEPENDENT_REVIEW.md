# H–He 선택 공급자 독립 검토

Reviewer: `/root/exchange_closure`. Author of reviewed pair source: `/root/source_pair_research`.
Scope: `../pair_source/{h_he_intake.py,test_h_he_intake.py,THEORY_KO.md,CONTRACT.json,RAW_IDENTITIES.json}`, shared immutable source paths and the preserved upstream normalization code. This is one complementary independent review pass, not another implementation or execution campaign.

## 판정

**PASS_SCOPED_DERIVATION_AND_STATIC_IMPLEMENTATION.** 식의 가정은 서로 다른 고전 Maxwellian 두 종, 탄성·회전대칭 pair law, heat에는 상대 drift 0, drag에는 drift 1차다. Source uncertainty, isotope/state calibration, 실제 fit 평가와 physical provider admission은 이 판정에 포함되지 않는다. Reviewer는 fit·IVP·historical suite를 실행하지 않았다.

## 독립 유도

공통 평균속도 0에서 `Var(g_i)=k_B(T_a/m_a+T_b/m_b)=k_BT_*/mu`, `Cov(V_i,g_i)=k_B(T_a−T_b)/M`이므로 Gaussian conditioning은

`E[V|g]=mu(T_a−T_b)g/(M*T_*)`

를 준다. Maxwell radial variable `gamma=g/sqrt(2*k_B*T_*/mu)`의 density `4*gamma² exp(−gamma²)/sqrt(pi)`를 직접 적분 measure에 넣으면

`<g³ sigma1>=4*k_B*T_*/mu * gbar * Qbar11`.

Event identity `Delta K_a=V·Delta p_a` 및 azimuthal average `int Delta p_a d_sigma=−mu*sigma1*g`로부터

`Q_a=4*k_B*n_a*n_b*(mu/M)*gbar*Qbar11*(T_b−T_a)`

를 얻는다. 이 경로는 작성자의 함수 호출이나 수치 값을 사용하지 않는다. Shifted relative Maxwellian의 drift derivative `partial_Uj f=mu*g_j*f/(k_BT_*)`를 독립 적용하면

`R_a=−(4/3)*n_a*n_b*mu*gbar*Qbar11*U+O(U³)`

도 일치한다. 교환의 두 부호, 평형/진공 한계, 양의 pair entropy source, heavy-target heat suppression이 모두 같은 식에서 따른다. 코드의 `fa*fb`는 `mu/M`와 같고 reduced-mass의 scaled 계산도 정확한 대수적 재표현이다.

Source normalization에서 `(l,s)=(1,1)`의 prefactor는 1이고 `(2,2)`는 1/2다. `sigma2_Legendre=(3/2)Q_cos2`이므로 THEORY Eq.(2)의 1/3도 일치한다. Local preserved `CapitelliIntegrals.h`의 `setFactor(PI)`와 `setUnits("Å-Å")`, `CapitelliIntegrals.cpp`의 Bruno Eq11 구현을 읽었으며 SI factor `pi*1e-20`와 일치한다. Thermal collision integral을 energy-resolved DCS로 사용하는 경로는 없다.

## 구현·소유권 검토

* `load_h_he_fit_input`은 canonical raw SHA256/Git-blob identity, 한 명시적 H–He pair, 9개 종류와 7개 finite decimal token, 기존 Q11/Q22의 Decimal equality를 요구한다. 실제 바이트/parse 통과의 실행 근거는 부모의 bounded source-validation receipt에 둔다.
* Source interpolation/fit evaluation을 수행하는 호출이 없다. 새 7개 row는 SOURCE_INPUT_ONLY, 기존 2개 row는 원 scoped result 재사용으로 구분된다.
* `conditional_h_he_moments`는 질량·밀도·온도 및 양의 source 값, 정확한 T_star binding과 source/mass provenance를 요구한다. Domain은 T_star의 50–50000 K이고 extrapolation 경로가 없다.
* Output은 conditional evidence label 및 `physical_provider_admitted=false`를 유지한다. Heat의 무 drift 가정과 linear drag를 O(U²)에서 임의로 합치지 않으며 frictional heating 의무를 THEORY에 남긴다.
* Count, binding, nonthermal birth, nuclear Q를 elastic heat에 추가하는 코드가 없다. Exchange closure의 일반 raw/central source convention과도 정합한다.

## 해결된 source-copy 지적

초기 `pair_source/upstream/collisions.xml`은 raw materialization에서 끝 newline 1 byte가 추가되어 canonical source와 byte identity가 달랐다. Review가 이 중복을 발견해 전달했고 작성자가 중복 파일·stale identity row를 제거했다. 최종 read에서는 canonical `../sources/raw/mutationpp_collisions.xml`의 source SHA256 `25e0ac6affa33361e9652d3fd3f43760f40f1a500c0a4993b1ace82c5ce501c2`, blob `d86bf74e05e6bcac9db67cfc03055621ebed2f8c`, 155227 B를 참조한다. `RAW_IDENTITIES.json`에는 code/license 4개만 남아 있다. 교정 이유와 이전 copy 오류는 작성자의 source-intake note에 보존한다. Scientific input이나 원 HE34 결과는 바뀌지 않았다.

## 남은 정확한 입력

선택된 isotope/state/mass와 H/He source label의 mapping, 그 mapping에서의 실제 Qbar11(T_star) 값과 calibrated source uncertainty, 해당 값의 평가를 위한 별도 numerical allowance가 필요하다. 이것은 조건부 유도·소프트웨어 interface 판정과 분리된 physical input obligation이다.
