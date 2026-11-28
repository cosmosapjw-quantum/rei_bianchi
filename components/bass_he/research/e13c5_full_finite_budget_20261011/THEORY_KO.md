# E13C5 full-first2 이후: 유한 합 예산과 연속 spectrum

## 기여의 범위

이 문서는 `E13C5_SELECTED_SUBSET_BUDGET_AND_MISSING_NODE_COMPLEMENT_CONTRACT`의 이론 기여다. 이미 완료된 PR20 full-first2를 받아 **전체 저장 node의 유한 합을 분해하고 기존 두 OFF N512 결과를 합치는 연구**로 다음 목표를 갱신한다. 새 coefficient, ODE, native, gas, NCP 과학 실행은 모두 0회다. 실제 전체 수치표와 final independent decision은 별도 산출물이 담당한다.

PR20 source head는 `0633ec2c9aed37593b9f1c05abc7156727408583`다. 직접 읽은 `CONTRACT.json`, `REPORT_KO.md`, `NEXT_DAG.json` 및 `full_first2.py`에 따르면 OFF/KF/GM 각각 node 0..2439를 포함한다. 특별 node 0,700,1620,2344만 세 segment이며 나머지는 두 segment다. 전체는 **7320 paths / 14652 segments**다. 과거 검토된 12 paths/36 segments를 재사용했다. 7320×3 segments로 확대하지 않는다.

기존 기준은 PR19의 `LINEAGE_REDUCTION_CONTRACT.md`와 `CONTINUATION_REPORT_KO.md`다. 그 당시 full-first2 HOLD 기록을 보존하면서 실제 완료된 PR20 finite cover를 현재 계보에 인정한다. 이 자료는 physical/production, 실제 atomic photon·heat·recoil, 새 gas evolution, receiver adoption을 자동 승인하지 않는다. 기존 과학 실행과 과거 판정을 반복하지 않는다.

## 1. 유한 합·보완 집합·continuum

Mode를 \(m\), spectral node를 \(p\), 관측량을 \(X\)라 하자. \(x_{m,p,X}\)는 해당 captured gas, source/mask, energy seam, initial stock에 결합된 시간 연속 경로 해의 exact 출력이다. 기존 양의 quadrature weight를 정확히 lift한 값을 \(w_{m,p}>0\)라 한다.

\[
Q_{m,X}=\sum_{p\in G_m}w_{m,p}x_{m,p,X},
\qquad G_m=\{0,\ldots,2439\}.
\]

이것이 PR20 full cover의 유한 합 대상이다. `PATHS.jsonl`의 `weighted_reduction`과 `cumulative_correction`은 경로별 대상이다. `RESULTS.json`의 `all_node_per_step`은 step별 endpoint와 transaction을 구분한다. 두 step의 photon endpoint를 더하면 마지막 photon stock과 다른 관측량이 된다.

OFF/KF/GM는 서로 다른 gas history다. 세 mode의 합을 하나의 물리적 결과로 만들지 않는다.

\[
S_m=\{0,700,1620,2344\},\quad R_m=G_m\setminus S_m,\quad
Q_{m,X}=Q^S_{m,X}+Q^R_{m,X}.
\]

각 mode에서 \(|S_m|=4,\ |R_m|=2436\)이다. 이제 \(R_m\)는 미실행 node가 아니다. Source-bound PR20 per-path interval을 직접 합하면 그 finite contribution을 얻는다. \(R_m\)와 node 사이의 연속 spectral coordinate 전체는 다른 대상이다.

별도의 연속 spectrum 모델을 정의할 때만

\[
\mathcal M_{m,X}=\int_D f_{m,X}(\eta)\,d\eta,\qquad
\mathcal E^{\mathrm{spec}}_{m,X}=\mathcal M_{m,X}-Q_{m,X}
\]

를 논할 수 있다. Domain/measure, node 사이 gas/source/mask와 초기 spectrum의 연장, actual quadrature rule, boundary/tail이 필요하다. 모든 node의 시간 적분 정밀도를 높이는 것만으로 node 사이 variation의 상계가 생기지 않는다.

## 2. Signed correction과 representation

동일 경로·관측량의 captured reference exact value를 \(c_{m,p,X}\)라 한다. 누적 moment라면 captured segment exact lift의 합을 사용한다.

\[
\delta_{m,p,X}=x_{m,p,X}-c_{m,p,X},\quad
C^{\mathrm{seg}}_{m,X}=\sum_pw_{m,p}c_{m,p,X},
\]
\[
\Delta_{m,X}=Q_{m,X}-C^{\mathrm{seg}}_{m,X}
=\sum_pw_{m,p}\delta_{m,p,X}
=\Delta^S_{m,X}+\Delta^R_{m,X}.
\]

Absolute photon/count/heat가 비음수여도 correction \(\delta\)는 signed다. Selected correction의 작음이나 공통 부호만으로 complement의 크기·부호를 추정할 수 없다. PR20에서 같은 correction target을 합하면 그 추정 자체가 필요 없어졌다.

Native node 또는 AGGREGATE와 비교할 때는

\[
Q_{m,X}-C^{\mathrm{native}}_{m,X}
=\Delta_{m,X}+R^{\mathrm{seg\to node}}_{m,X}
+R^{\mathrm{node\to aggregate}}_{m,X}
\]

로 baseline을 연결한다. 각 항의 step/endpoint/transaction 의미를 일치시키고 signed anchors를 보존한다. Energy erg/eV는 기존 exact binary64-lift \(\epsilon\)으로 한 번만 변환한다. Continuum과 native의 차이는

\[
\mathcal M_{m,X}-C^{\mathrm{native}}_{m,X}
=\mathcal E^{\mathrm{spec}}_{m,X}+\Delta_{m,X}
+R^{\mathrm{seg\to node}}_{m,X}
+R^{\mathrm{node\to aggregate}}_{m,X}
\]

다. Actual physical model과 frozen-capture continuum의 모델 차이는 이 수치 식의 어느 항에도 자동으로 포함되지 않는다.

## 3. Full saved data로 complement를 닫는 admission 조건

다음 조건을 먼저 확인한다.

1. PR20 source/contract/START/PATHS identity, input pins, 3 modes×2440 unique nodes와 ordered segment coverage.
2. Same-target identity: fixed gas/stage, exact-lift capture rows, source-off/on, species mask, initial stock, carry, 모든 energy seam, normalization, baseline.
3. 정확한 양의 point weight. 동일한 node의 label/weight/mode를 섞지 않는다.
4. Selected record와 PR19/N512의 대응. `continuous_minus_frozen`과 `true_minus_captured_interval`에는 frozen-minus-captured bridge가 필요하다.
5. 유한 ordered endpoints와 inherited certificate validity. Overlap은 validity의 증명이 아니다.
6. Dedicated total heat, species interval 합, per-step/whole-path moment와 endpoint stock의 구별.

그 뒤 primary complement는

\[
I^R_{m,X}=\bigoplus_{p\in R_m}w_{m,p}I_{m,p,X}
\]

로 계산한다. 이미 weighted interval이면 weight를 다시 곱하지 않는다. Signed correction interval에도 같은 식을 쓴다. Full aggregate만 있다면 valid \(I^{\mathrm{full}}-I^S\)도 complement를 안전하게 둘러싸지만, 이번에는 per-path 자료가 있으므로 직접 합을 primary로 삼는다. Absolute aggregate만 확보하고 reference가 다른 signed correction을 인증했다고 할 수 없다.

## 4. Interval subtraction의 dependency

동일 canonical decomposition에서 \(W_F=W_S+W_R\)라 하자. Ordinary interval subtraction

\[
I_F-I_S=[L_F-U_S,U_F-L_S]
\]

의 폭은 \(W_R+2W_S\)다. 이것은 safe하지만 selected term을 독립적인 두 변수로 취급하여 부풀린다. 예를 들어

\[
I_S=[1,3],\quad I_R=[10,14],\quad I_F=[11,17]
\]

이면 \(I_F-I_S=[8,16]\)이다. 새 selected interval이 \([2,5/2]\)일 때 direct hybrid는 \([12,33/2]\), subtractive hybrid는 \([10,37/2]\)다.

Endpoint별 \([L_F-L_S,U_F-U_S]\)는 ordinary interval subtraction이 아니다. 정확히 동일 term에서 \(L_F=L_S+L_R,\ U_F=U_S+U_R\)가 성립하는 canonical endpoint bookkeeping임을 먼저 인증한 경우만 가능하다. 예를 들어 같은 selected target의 더 넓은 interval \([0,4]\)를 위 full interval에서 endpoint별로 빼면 \([11,13]\)이 되어 원래 valid complement \([10,14]\)의 endpoint를 배제한다.

따라서 primary는 유지하는 모든 path term과 교체 두 term의 exact rational 직접 합이다. Published aggregate의 outward slack은 따로 비교한다.

## 5. 두 OFF 경로의 full-sum refinement

\(K_{\mathrm{OFF}}=\{0,700\}\), \(K_{\mathrm{KF}}=K_{\mathrm{GM}}=\varnothing\)라 한다. 새 interval이 같은 exact target을 포함하면

\[
I^{\mathrm{new}}_{m,X}
=\bigoplus_{p\notin K_m}w_{m,p}I^{\mathrm{old}}_{m,p,X}
\ \oplus\
\bigoplus_{p\in K_m}w_{m,p}I^{512}_{m,p,X}
\]

는 같은 full finite sum의 valid enclosure다. KF/GM per-path 과학 자료는 그대로다. 이것은 두 항의 enclosure 교체이지 finite coverage 변경이 아니다.

새 interval이 old 내부에 있으면 nested refinement다. 동일 target에 대한 양쪽 certificate가 valid이고 intersection이 nonempty이면

\[
I^\cap_{m,p,X}=I^{\mathrm{old}}_{m,p,X}\cap I^{512}_{m,p,X}
\]

도 valid하다. 통계적 독립은 필요하지 않는다. 서로 다른 target의 overlap은 충분조건이 아니다. Primary replacement와 optional intersection-enhanced output을 명시적으로 구별한다. 공집합을 hull이나 평균으로 숨기지 않는다.

종별 합과 dedicated total도 동일 scalar target이면 intersection할 수 있다. 이때 폭 감소를 개별 species/path의 독립 기여로 임의 분배하지 않는다.

## 6. 개선 이득의 상한과 남는 floor

같은 mode/observable/reduction route를 고정하고

\[
b_{m,p,X}=w_{m,p}(U_{m,p,X}-L_{m,p,X}),\qquad
W_{m,X}=\sum_pb_{m,p,X}
\]

를 정의한다. Already-weighted interval 입력이면 \(b\)는 그 자체의 폭이다. Direct Minkowski sum의 exact endpoints에서는 width decomposition이 equality다. Published aggregate와의 추가 outward slack은 path 과학 remainder에 배분하지 않는다.

두 항의 실제 개선량은

\[
G_K=\sum_{p\in K}(b_p^{\mathrm{old}}-b_p^{\mathrm{new}}),\qquad
W^{\mathrm{new}}=W^{\mathrm{old}}-G_K.
\]

Nested/new-intersection이면 \(G_K\ge0\)다. 단순 replacement가 넓어졌다면 negative gain을 그대로 기록한다. 다른 term을 고정했을 때 가능한 최대 개선량과 남는 폭은

\[
G_K\le B_K\equiv\sum_{p\in K}b_p^{\mathrm{old}},\qquad
F_K=W^{\mathrm{old}}-B_K=\sum_{p\notin K}b_p^{\mathrm{old}}.
\]

\(F_K>0\)이면 \(W^{\mathrm{old}}/W^{\mathrm{new}}\le W^{\mathrm{old}}/F_K\)다. \(F_K=0\)이면 유한 ratio ceiling을 이 식으로 얻지 못한다. Old width가 0이면 improvement ratio 자체가 유용하지 않다.

이 floor는 **고정한 per-path Minkowski route의 floor**다. Cross-path correlation, conservation identity 또는 새로운 direct-total certificate를 쓰면 representation을 바꾸어 더 줄일 수 있다. 자연의 intrinsic uncertainty, 모든 알고리즘의 절대 하한, continuum error 하한으로 표현하지 않는다.

같은 식을 네 selected nodes 전체에도 적용한다. Selected width 비중이 작으면 그 네 node의 정밀도만 높여 full width를 크게 줄일 수 없다. 반대로 큰 weighted contribution이 소수에 집중되면 targeted refinement가 효율적일 수 있다. 실제 데이터로 이 두 가능성을 구별한다.

## 7. Signed correction과 precision 언어

Final interval이 \([L,U]\)일 때 허용되는 sign 판정은 다음과 같다.

| 조건 | 판정 |
|---|---|
| \(L>0\) | strictly positive |
| \(U<0\) | strictly negative |
| \(L=U=0\) | exactly zero |
| \(L=0<U\) | nonnegative; strict positivity 미인증 |
| \(L<U=0\) | nonpositive; strict negativity 미인증 |
| \(L<0<U\) | sign undetermined |

Midpoint 부호, selected nodes의 부호, zero-containing ledger는 full correction sign을 인증하지 않는다. 사전 물리 tolerance \(\tau_X\)에 대해 \(\max(|L|,|U|)\le\tau_X\)이면 absolute bound를 인증할 수 있다. Relative claim에는 의미가 고정되고 0에서 떨어진 denominator lower bound가 필요하다. Radius, 전체 width, relative width, correction 크기는 구별한다.

Photon/count/energy/heat의 단위가 다르므로 raw width를 서로 더해 “전체 budget”을 만들지 않는다. 외부에서 정한 scale/tolerance가 없으면 관측량별 width와 순위를 보고한다.

## 8. Continuum 반례와 새 조건

두 node \(\eta=0,1\), positive weights \(1/2,1/2\)에서

\[
f_A(\eta)=A\eta^2(1-\eta)^2,\quad A>0
\]

는 nodal value와 finite quadrature가 정확히 0이지만 \(\int_0^1 f_A\,d\eta=A/30\)이다. \(A\)는 임의로 크다. Polynomial이므로 연속성/매끄러움/analyticity만으로도 quantitative upper bound는 나오지 않는다. 일반 finite grid에는 \(\prod_p(\eta-\eta_p)^2\)로 같은 반례가 성립한다.

다음 continuum 계약에는 actual coordinate/measure/domain/tail, quadrature rule, event/threshold partition, node 사이의 physical input 정의, branch별 derivative/range bounds가 필요하다. 실제 rule이 길이 \(h_j\) cell의 midpoint이고 \(|f''|\le M_j\)라면 Taylor remainder를 적분하여

\[
|\mathcal M-Q_{\mathrm{mid}}|\le\sum_j M_jh_j^3/24
\]

를 얻는다. 이는 conditional illustration이며 PR20 weight에 자동 적용하지 않는다. Threshold/source jump를 지나는 cell은 분리하거나 jump contribution을 따로 제한한다. Cell-wide range \([\ell_j,u_j]\)가 있으면 \(\sum_jh_j[\ell_j,u_j]\)로 continuum 자체를 둘러싸는 방법도 가능하다.

## 9. 다음 계산 선택을 위한 actual-data 계약

새 coefficient job 전에 다음을 saved-only streaming postprocessing으로 저장한다.

1. Mode/node/observable별 exact target ID, baseline, weight, endpoints, weighted width, provenance, segment count, event/mask/source class.
2. 각 mode/observable의 full·selected·complement width, signed correction interval과 sign.
3. 두 OFF replacement의 actual gain, maximal-gain ceiling, unchanged-term floor와 old/new ratio.
4. 관측량별 weighted-width 순위 및 top-\(k\) 누적 비중. Unweighted width 순위를 대신 사용하지 않는다.
5. Published rounding slack과 exact canonical term sum의 구별. Incoming/local midpoint/coefficient remainder/representation/anchor로 따로 식별할 수 없는 항은 `NOT_IDENTIFIABLE_FROM_SAVED_FIELDS`로 둔다.
6. 기존 measured cost의 mode/branch/N/P/host/reuse 범위. 평균 비용을 새로운 node의 인증된 wall 상한으로 간주하지 않는다.

사전에 물리적으로 정한 \(\tau_X\)가 있다면 \(s_p=\max_X b_{p,X}/\tau_X\)와 같은 deterministic screening이 가능하다. Cost가 측정됐다면 gain/cost를 비교할 수 있지만 prediction과 guarantee를 구별한다. \(\tau_X\)가 없으면 post-hoc threshold를 만들지 않고 raw quantity별 Pareto table을 보고한다.

Two-path ceiling이 필요한 finite gain을 허용하면 targeted refinement가 후보가 된다. Ceiling이 작으면 dominant complement path 또는 reduction dependency를 먼저 다루는 편이 타당하다. 현재 질문이 continuum accuracy이면 finite radius만 계속 줄이기 전에 spectral model/error contract를 세운다.

## 10. 현재 인계와 완료 기준

새 NCP 계약은 **saved-only exact full-budget postprocessing parity 한 번**이다. 과거 N512/PR20 solver를 재실행하지 않는다. Primary science coefficient/native/gas invocation은 0이다. 과거 NCP_READY는 source·evidence dependency로 보존하되 이 새 job의 entrypoint와 혼동하지 않는다.

이 기여의 다음 measurable goal은 source-bound 7320-path reduction에서 3 modes의 full/selected/complement budgets, 두 OFF refinement의 actual full gain/floor, 관측량별 dominant nodes를 얻고 새 산출물에 한 번의 independent review를 받는 것이다. `exact_toys.py`의 elementary identities/counterexamples는 이론 계약의 좁은 확인이며 PR20의 재검증 또는 물리 admission 판정이 아니다.

