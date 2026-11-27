# MOVING_GAS_SOURCE_05 재개·구현 인계

단위: HERE_RUX03_MOVING_GAS_SOURCE_05. THEORY R1–R10.
날짜: 2026-10-13 KST. 운영 규약: physmath-research-loop 1.0.0 / design v0.2.

**작성 상태: author_complete.**
**Independent decision reference: review/DECISION.json.**
작성자의 유도와 실제 검산은 완료되었다. 최종 scoped adoption은 독립 검토자의
DECISION 한 곳에서 판정한다. 아래 review·delivery 준비 상태는 작성 시점의
snapshot이며, 최종 종료 상태는 별도 closeout·실제 영수증을 따른다.

## 1. 이번에 확보한 구성

이번 단위는 고정 local Eulerian tetrad·고정 lab 체적에서 common gas velocity가
바뀌는 유한 source stage를 구성했다. 보존된 H nuclei density
\(D=\gamma n_H\), Doppler-shifted atomic inputs, photon event, 조성,
gas energy·momentum과 Case A escape가 같은 endpoint를 공유한다.

핵심 식은 다음과 같다.

\[
\delta_q=\gamma(1-\boldsymbol\beta\cdot\mathbf e_q),\qquad
E'_q=\delta_qE_q,\qquad N'_q=\delta_qN_q,
\]

\[
\lambda_{iq}=cD y_i(1-\boldsymbol\beta\cdot\mathbf e_q)
\sigma_i(\delta_qE_q),\qquad
N_q^+=\frac{N_q^-+hS_q}{1+h\sum_i\lambda_{iq}},\qquad
A_{iq}=h\lambda_{iq}N_q^+.
\]

이 \(A_{iq}\)를 photon 제거, species 생성, full photon energy·momentum 전달에
한 번씩 같은 값으로 사용한다. Proper 사건률 \(R'\)가 주는 lab 체적당 적분
사건 수는 \(hR'\)이고, per-H 조성 변화는 이를 \(D\)로 나눈다. 한 endpoint에서
proper-clock step으로 표현하면 \(h/\gamma\)다.

Gas conservative 변수는

\[
E=(\rho+p)\gamma^2-p,\qquad
\mathbf M=(\rho+p)\gamma^2\boldsymbol\beta
\]

이며 \(\mathbf M\)은 physical momentum density에 \(c\)를 곱한 양이다.
입력 \(D>0,r>0\), endpoint 조성에서

\[
E>\sqrt{(Dr)^2+|\mathbf M|^2}
\]

이면 양의 thermal primitive가 정확히 하나 존재한다. 이는 알려진 gamma-law
admissibility 정리를 현재 \(D,r\)에 맞춰 다시 유도한 결과다. 이번 문서는
열에너지 excess 변수의 양수항 계산식·bracket·도함수와 정확한 warm subdomain을
함께 제공한다. 등호는 유일한 cold 수학적 경계이며 selected warm 모델의
새 시나리오가 아니다.

광자를 소거한 뒤의 full source residual은
\(Y=(\zeta,E,\mathbf M)\)의 7개 성분을 갖는다. Strict physical interior와
\(C^1\) provider neighborhood에서 \(h=0\)의 Jacobian이 항등행렬이므로,
충분히 작은 \(h\)에 대해 유일한 local physical branch가 존재한다.
고정 조성의 primitive 전역 유일성과 full coupled stage의 국소 유일성은
각각의 가정 아래 확보한 별도 명제다.

증명의 위치와 각 실제 검산은 [CLAIMS.json](CLAIMS.json)에 M01–M07로
묶었다. 세부 유도는
[MOVING_SOURCE_AND_THERMAL_BALANCE.md](../derivations/MOVING_SOURCE_AND_THERMAL_BALANCE.md)와
[PRIMITIVE_RECOVERY_AND_EXAMPLES.md](../derivations/PRIMITIVE_RECOVERY_AND_EXAMPLES.md)에 있다.

## 2. Scalar thermal provider와 연결하는 정확한 보정

같은 finite conservative stage를 endpoint gas frame으로 투영하면

\[
w_+-w_-=\frac h{\gamma_+}Q_{\rm th}^{(H)}
+\frac{\mathcal K_\gamma}{D\epsilon_{\rm eV}},
\]

\[
\mathcal K_\gamma=
D\left[
(r_-+\tfrac53\epsilon_{\rm eV}w_-)(\gamma_{\rm rel}-1)
-\tfrac23\epsilon_{\rm eV}w_-
\left(\frac{\gamma_+}{\gamma_-}-1\right)
\right],
\]

\[
\gamma_{\rm rel}
=\gamma_+\gamma_-(1-\boldsymbol\beta_+\cdot\boldsymbol\beta_-)
\]

을 얻는다. 이 식에서 thermal·binding·captured kinetic power는 기존 사건
ledger의 같은 endpoint 값이다. Smooth limit의 보정은
\(-\tfrac23w\,\Delta\log\gamma+O(h^2)\)이며, 기존 공변식
\(\dot w=Q_{\rm th}^{(H)}-\tfrac23\Theta w\)로 이어진다.

고정 lab 체적에서도 \(n_H=D/\gamma\)가 달라지므로 pressure work가 생긴다.
이 source 보정과 기존 Bianchi geometry work의 소유를 각각 유지한다.
현재 receiver의 work 출력은 순간 도함수이고 ODE가 누적한다.
THEORY03/04의 endpoint-energy discrete work와 이번 \(\mathcal K_\gamma\)는
각자가 정의된 유한 stage의 식으로 사용한다.

## 3. 그대로 재사용할 가정과 정확한 identity

| 항목 | 인계할 내용 |
|---|---|
| 직전 이론 | BASS_HE PR32, commit ca85cfc7353da190613f7fb37a6e0ffed9b51913 |
| 현재 receiver | rei_bianchi PR114, commit a5c958c414dea41216b445c05f58df837f05cacb |
| Source·재사용 증거 | source_map/CURRENT_SOURCE.json, SOURCE_MAP.md, VALID_REUSE_IDENTITY.json |
| Gas | One common velocity·temperature, 보존된 H/He nuclei, 물리적 fractions, \(D>0\), \(r>0\), \(|\beta|<1\) |
| 원자 모델 | Warm FT03 Case A CI/RR/두 DR/primary absorption 및 captured kinetic moments. CR/RCT/HH는 기존대로 off |
| 유효범위 | Rest \(T\in[30000,110000]\) K, Doppler 변환 뒤의 \(E'_q\in[0,50000]\) eV |
| Threshold 역할 | Fit cutoff 13.60/24.59/54.42 eV와 binding 13.598434599702/24.587389011/54.41776 eV를 구별 |
| Reference mass | 중성 원자와 bound electron을 포함한 \(m_{\rm ref}\)는 고정. Ionization은 \(B\)를 바꾸며 electron rest mass를 다시 더하지 않음 |
| Escape | Inherited RR/DR binding와 captured kinetic power의 comoving-isotropic emission moment |
| Photon measure | \(N_q,S_q\)에는 node weights가 포함됨. Doppler·volume·per-H 변환에서 같은 weight 또는 density factor를 중복 적용하지 않음 |

이전 THEORY04의 45개와 PRIMARY_THEORY03의 47개 check group은 같은 가정과
identity에서 재사용했다. 이번 계산 수에는 포함하지 않았다.

Current receiver는 proper common-frame scalar state와 reference photon
count를 저장하며 moving gas의 \(\boldsymbol\beta,E,\mathbf M\)를 진화시키지
않는다. Source survey가 이 차이와 실제 callback·normalization 위치를
기록했다. 현재 구현 완료 상태를 이번 수학적 구성으로 변경하지 않는다.

## 4. 실제 검산과 보존한 실패

| Suite | 최종 실제 결과 | 직접 근거 |
|---|---:|---|
| xAct moving tensor | 25/25 | evidence/XACT_MOVING_SOURCE_RESULT.json |
| Primitive author | 18/18 | evidence/PRIMITIVE_EXACT_RESULT.json |
| Root finite·clock·Jacobian | 12/12 | evidence/MOVING_SOURCE_EXACT_RESULT.json |

위 합계 55는 세 suite의 raw named group 관측 수다. 선언된 동일 Jacobian
목표 중복 1개를 합치면 54개 검사 목표가 된다. 어느 수치도 독립된 수학 정리
수를 뜻하지 않는다. Primitive의 positive-factor 검사와 root의 full
Jacobian 검사는 동일 determinant에 관한 교차 검증을 포함하고, 다른
scalar/tensor 표현에도 물리적 교차 검증이 있다. 수학적 결과는 M01–M07의
7개 claim family로 관리한다.

최종 실행은 Wolfram Language 15.0.1이고, xAct는 xTensor 1.3.0을 실제
로드했다. 최종 xAct 결과의 xPermExternalBackend=false를 그대로 기록한다.

초기 xAct 두 건은 Hold[Throw[Null]]로 끝났다. 실제 원인은 helper
Cp[i_]:=-Tp[i,b]normal[-b]의 고정 내부 dummy b와 호출 Cp[b]가 충돌한
implementation index-hygiene 오류였다. 해당 입력·debug 입력과 raw v1/v2를
보존했다. 동치인 전개된 current로 helper를 바꾸고 stress-current 관계를
독립적으로 추가 검산한 v3의 25개 결과가 최종 근거다. 두 실패는 물리적
반례나 추가 성공으로 세지 않는다. 정확한 진단과 별도 로컬 준비 단계의
syntax/API 교정은 evidence/EXECUTION_RECORD.md에 있다.

Root scalar 원본은 11 PASS와 1개의 조건부 부등식 미결정이었다.
FullSimplify가 그 부등식을 남겨 TrueQ가 false로 기록한 상태를
MOVING_SOURCE_EXACT_RESULT_v1.json에 보존했다. 이후 양의 Jacobian
항목 하나에 대해 비음수 다항계수와 계수 1의 엄격양의 단항식
\(a_r^3g^5\)를 실제 확인했다. 그 certificate로 같은 항목을 닫았으며,
나머지 11개를 재실행하지 않았다. Final aggregate는 12/12이고 targeted
certificate를 13번째 새 항목으로 더하지 않는다.

실제 input·raw·정규화 결과가 각 증거 파일에 있다. 이번 THEORY에서 native
build, chemical RHS, ODE history 또는 parameter scan은 실행하지 않았다.

## 5. 바로 재사용할 reference

초기 rest \(T_0=50000\) K와 interior 조성에 23 eV HI photon을 흡수시키는
정확한 family가 있다. Single beam은 양의 bulk momentum과 binding 증가,
새 electron count 및 \(D/\gamma\) proper-density dilution을 모두 포함한다.
작은 양의 fluence에서 warm·composition·Doppler 범위를 유지한다.

반대 pair는 흡수 momentum이 상쇄되고

\[
T^+=\frac{d_0T_0+T_{\rm exc}\xi}{d_0+\xi},\qquad
T_{\rm exc}=72733.757372464264931\ldots\ {\rm K}
\]

이므로 선택된 warm 범위 안에 남는다. Endpoint opacity를 계산한 뒤
BE photon inventory를 구성하므로 rate를 초기 상태에 고정하지 않는다.

이들은 HI absorption channel만을 분리한 analytic reference다.
그 reference의 CI/RR/DR increment가 0이라는 조건을 full FT03 모델의
가정 변경으로 사용하지 않는다. Full model의 paired limit은 대칭과 local
branch uniqueness로 따로 유도했다.

## 6. 다음 THEORY: full rates의 정량적 continuation certificate

다음 수학 작업은 full FT03 rates와 photon source가 결합된 stage에 대해
실제 \(M_0,L_0\) bound 또는 residual-Jacobian bound를 만드는 것이다.
정확한 unit ID와 DAG overlay는 [NEXT_DAG.json](NEXT_DAG.json)을 따른다.

첫 구성은 다음 입력을 고정한다.

1. \(D,f,Y_-\), lab photon energies·directions·counts와 source의 실제 identity,
   coordinate scales 및 norm을 명시한다.
2. 초기점 주위의 closed convex ball \(\mathcal B_r(Y_-)\)를 정하고,
   그 전체가 composition·primitive·warm·gas-frame energy의 허용영역 안에
   들어가도록 양의 margin을 증명한다. Provider cutoff를 넘는 부분은
   해당 piecewise 구간에 맞춰 분리한다.
3. Exact primitive derivatives, Doppler map, photon elimination과
   CI/RR/DR/photo provider를 결합해
   \[
   M_0=\sup_{\mathcal B_r\times[0,\bar h]}\|\mathcal S_h(Y)\|,\qquad
   L_0=\sup_{\mathcal B_r\times[0,\bar h]}
   \|D_Y\mathcal S_h(Y)\|
   \]
   의 유한한 정량 상한을 구성한다.
4. \(0<h\le\bar h\), \(hM_0\le r\), \(hL_0<1\)을 만족하는 양의 구간과
   반복 오차 bound를 제공한다. 이어가는 branch에서는 허용영역 경계 도달과
   Jacobian의 invertibility 상실을 각각 판별한다.

완료 근거는 source·box·norm identity, 실제 상한의 계산 또는 증명,
양의 step certificate와 boundary 처리다. 이번 local existence proof와
global constitutive inverse를 반복 실행하는 것은 그 새 상한을 대신하지
않는다. 원자 계수나 source identity가 유지되면 해당 앞선 근거를 그대로
사용하고, 새 box·Doppler 범위·도함수 bound가 처음 필요한 전이부터 작업한다.

## 7. CODING 재개와 남겨 둔 owner

첫 구현 의무는 기존 HERE_RUX03_PRIMARY_PROVIDER_03이며,
HERE_RUX03_COVARIANT_MOMENTS_04도 pending이다. 그 뒤의 moving stage는
[CODING_CONTRACT.md](CODING_CONTRACT.md)에 정리한 입력·출력·단위·
도메인·source ownership과 reference를 실제 consumer에 연결해야 한다.
원래 \(RUX02+RUX03\to RUX04\to RUX05\) owner DAG와 완료 상태는 유지한다.

현재 reference-volume photon·source와 fixed-lab-volume 변수를 연결할 때
entry/exit conversion을 명시한다. Photon source birth는 이전 provider
계약의 소유를 따라 한 번만 적용한다. Full directional API는 일반
\(\boldsymbol\beta\)를 지원하고, 기존 \(\mu\) ring adapter는 axial velocity
범위를 명시한다. Transverse velocity는 azimuth를 분해하거나 pointwise
양의 적분을 구성한다.

Future native acceptance는 같은 사건의 에너지·운동량 ledger, primitive
역대입, warm/energy guards, single-beam와 paired references 및 full-rate
source path를 실제 소비 경로에서 확인해야 한다. 이번 symbolic 계산을
그 native 실행의 완료 수로 사용하지 않는다.

## 8. 판정·게시 및 재검토 지점

작성 시점에는 독립 최종 채택과 delivery receipt를 준비했다. 실제 채택은
review/DECISION.json 한 곳을 참조하고, 최종 종료는 별도 closeout에서
기록한다. 과학 artifact identity와 이후 Git·backup identity는 각각의
영수증으로 확인한다.

다음 변화는 영향받는 결과부터 다시 검토한다: atomic channel/fit identity,
neutral-reference binding convention, event volume·clock normalization,
escape angular closure, photon source birth placement, Doppler support,
common-endpoint choice, EOS 또는 fixed-foliation source setting.

별도 all-Bianchi abundance-source/reference-current/class-B/relative-species-tilt
D2.3 범위와 기존 정책은 유지한다. 이번 단위는 새 strong no-go를 제안하지
않으며, 열린 continuation 의무를 위의 정량적 구성 작업으로 연결한다.
