# E13C1: 광자의 생성·생존·흡수 시점과 에너지 전달

FINITE_SIX_FROZEN_PHOTON_TRANSACTIONS_INDEPENDENT_PASS__CONTINUOUS_MODEL_AND_OWNER_OPEN.

E13B 완료 원격14092a1c79916c5074005fa0a3bbf175ce8dc29a를 확인하고, E13A의 OFF/KF/GM 첫2개씩 총6개 저장 가스 거래에 대해 photon 경로만 재평가했다. 새 Newton/가스 advance/전체3x384/독립 material 재계산은0이다. 원 source62개는 불변이고 별도 native capture example만 추가했다.

## 물리 결과

s=ln(a), local g in[0,h], E=E0 exp(-g), P'=q-Lambda P에서 retarded birth/survival 적분을 독립 계산했다. species_i의 흡수수 A_i=lambda_i int(P dg), 흡수에너지 B_i=ev_erg E0 lambda_i int(exp(-g)P dg), 적색편이장부 Z=ev_erg E0 int(exp(-g)P dg)이다. 같은 frozen-subsegment 모델의 number/energy ledger를 닫는다. source와 opacity는 원 native가 선택한 경계/affine-gas stage에 고정되며 이것은 실제 연속 계수 오차의 인증이 아니다.

OFF 두번째 macro에서 이번 macro 안에 새로 생성된 광자의 흡수수 분율은 HI38.5604331%, HeI34.3186346%, HeII33.4617383%였다. 종별 총 평균흡수에너지(eV)는19.1496551/35.5731320/67.1667941이다. 이전 macro 생존광자 평균은19.3785967/35.6577908/67.1747240이고 새광자 평균은18.7848752/35.4111062/67.1510256이다. 이 고정 제조모형의 유한 spectral hardening/시간가중 결과이며 실제 RCT 자발방출 평균은 아니다.

새 구성적 반례: initial70eV 한 광자, Delta ln a=.1, source0, 총광학깊이1을 앞절반 또는 뒤절반에 배치했다. 두 경우 survivingN=.3678794411714423, finalU=23.30097585886557eV, absorbedcount=.6321205588285577가 같다. 그런데 평균흡수에너지는68.55888926/65.21523278eV, HeII binding54.41776eV를 뺀 heat/absorption은14.14112926/10.79747278eV로23.6449043% 다르다. 늦은흡수의B/이른흡수의B=exp(-.05). 이는 합성 시간순서 반례이지 원 HE모형에서 발견한23.6% 오류가 아니다. final photon N/U와 사건수만으로 누적가열은 결정되지 않는다. 보존식은 성립하면서 흡수와적색편이의 분배가 달라질 수 있다.

## 독립 계산과 검증

mpmath70digits, source binary64 literals/input의 exact lift, Verner의 log-expression, photon birth/survival의 양의 confluent-hypergeometric 적분으로 별도 구현했다. 독립 photon stock을 segment와 macro사이에 계속 전파하며 매번 native stock으로 reset하지 않는다. 원 grid/시간cut/가스stage/배경/에너지 anchor는 조건부입력이다.

actual14652segments, 58608 coefficient comparisons max3.12456e-15, 161172 kernel-owner max4.47722e-15, 190320 node-owner max5.20609e-15, aggregate max3.17030e-14. A/B 오차를 원 TOL=[1e-14,1e-14,1e-14,1e-26]로 투영한 최대는1.07721413e-5이고 사전기준1e-3 이하다. 원 native tracer와 원 characteristic190320값은 bit-identical, E13A aggregateA/B36개도exact이다.

24개 실제 record의90자리 직접구적168scalar와 비교하여 max1.573e-88; 기호14성분(행렬원소 포함), 새12Python tests PASS. E13B의 봉인 material RHS를 그대로 결합한6개 fullresidual의 maxnorm=.3920767642131432<1이다. 동일가스/source조건의 유한 확인이며 fullstage/원자fit 물리정확도/연속참오차interval은아니다.

독립 scientist review NOT_RUN. 원 Rustsyntax 실패와 rustfmt 부재(exit127), 첫 symbolic structural-equality 실패 후 simplify 교정을 보존했다. 실제 strict build와3capture/3analysis 모두exit0이다. 첫 physics run의24구적 후 symbolicfail 때문에 같은구적을1회 반복했으며 고유24개만 센다. rust1.94.1 archive SHA pin확인, PGP미확인. source/threshold/35eVclosure/tolerance/default 무변경.

## 재현과 다음

Full executable source, inputs, native witness, tests and evidence are in BASS_HE_E13C_PHOTON_PHYSICS_20261010_v1.zip:4096240bytes/SHA25606b5c02afb92e356ec66072a918e014f61fab5a795f26024fae55ca4d93acb33. Fresh local restore133payload+CRC, default verify-only exit0. Git에는 이 요약·계약·핵심계산코드만 있으며 전체 raw/의존성을 포함한다고 가정하지 않는다.

다음은 E13C2_VARIABLE_COEFFICIENT_BIAS_ON_FIXED_GAS_PATH다. 같은 gas path에서 연속 q(s),lambda_i(s)와 frozen-stage 근사를 비교해야 한다. 이미 완료된 kernel/convolution/6gas stage/full3x384를 재검증 루프로 반복하지 않는다. baselineRCTOFF, 실제atomic RCT photon/heat/recoilnull, physical/productionHOLD, HE-F2/F09OPEN, owneradoption별도, legacyGammaalias3.543295FAIL 유지.
