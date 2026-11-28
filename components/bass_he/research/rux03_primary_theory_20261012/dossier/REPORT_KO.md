# BASS_HE 다음 이론 연구 루프

## 공통 Case A 사건에서 implicit primary의 잔차·미분·에너지 수지까지

**연구 단위:** `HERE_RUX03_PRIMARY_THEORY_03`  
**일자:** 2026-10-12  
**규약:** `physmath-research-loop` 내장 1.0.0, THEORY R1–R10  
**수신 소스:** rei_bianchi PR114 `a5c958c414dea41216b445c05f58df837f05cacb`

이번 루프에서는 기존 implicit primary에 공통 사건 provider를 연결하기 위한
수학적 계약을 유도했다. 광자 주입을 포함한 정확한 소거, 사건으로부터 열·보존형
잔차를 함께 만드는 식, 그 야코비안과 구간 확장의 조건, 영밀도 경계에서도 정의되는
계수 provider, 가변 광자 에너지의 유한 단계 work를 구체적인 계산식으로 얻었다.

가장 중요한 결과는 다음 두 식이다.

\[
\boxed{F_E=F_w+\nabla B\cdot F_v}
\qquad
\boxed{W_{\gamma,geom}=-\sum_q(E_q^+-E_q^-)N_q^-}.
\]

첫 식은 같은 사건을 쓰는 열 잔차와 보존형 에너지 잔차가 root 밖에서도 일정한
행 변환으로 연결됨을 보인다. 둘째 식은 endpoint-energy backward Euler 단계가
history의 광자 에너지와 정확히 닫히도록 하는 기하 work다. 두 결과를 기존 네 변수
solver에 연결할 수 있도록 1·2차 미분과 실제 구현의 판별 기준까지 구성했다.

전체 유도는 [공통 잔차·provider 유도](../derivations/SHARED_RESIDUAL_AND_PROVIDER.md)와
[독립 광자·기하 유도](../derivations/PHOTON_ELIMINATION.md)에 있다.
[구현 계약](CODING_CONTRACT_KO.md)은 다음 코딩 루프의 직접 입력이다.

## 1. 현재 가정과 재사용한 근거

이번의 stage는 `y=(x,a,b,w)=(HII,HeII,HeIII,w_eV/H)`를 미지수로 삼는다.
H/He 핵수비 `f=n_He/n_H>0`, stage 밀도, 평균 팽창률 H, node 에너지와 외부 source는
주어진 매개변수다. 전자수와 온도는

\[
e=x+f(a+2b),\quad d=1+f+e,\quad n_e=n_H e,
\]

\[
T=\frac{2\epsilon_{eV}w}{3k_Bd},\qquad
\epsilon_{eV}=1.602176634\times10^{-12}\ \mathrm{erg/eV}
\]

로 갱신한다. 기체는 `0≤x≤1`, `a,b≥0`, `a+b≤1`, `w>0`에 있으며 현재 provider의
온도 영역은 30000–110000 K다. Case A escape와 primary absorption을 사용하고,
CR/RCT/HH는 기존 설정대로 off다. RR·DR의 captured kinetic power는 사건률과 함께
별도의 원시 모멘트로 전달한다. 미분과 구간 포함관계는 해당 temperature box에서
각 계수·모멘트 함수의 C² 확장을 사용한다.

binding energy는 현재 소스의

\[
\chi=(13.598434599702,24.587389011,54.41776)\ \mathrm{eV}
\]

를 쓴다. cross-section의 13.60, 24.59, 54.42 eV 활성화 경계와 그 역할을 구별한다.
이 보고서의 `E_q`는 eV다. 독립 photon 문서는 에너지 ledger를 erg로 전개하며,
그 문서의 변환표가 같은 수량을 연결한다.

### 기존 구현에서 이미 확보된 내용

현재 source의 필요한 경로와 11개 파일을 조사했다. PR30, PR114, PR97, PR83의
head는 직전 기록과 같았고, retained clean-build receipt의 34개 source hash도
일치했다. 따라서 변경 없는 source와 증거를 재사용했다.

| 내용 | 실제 근거 | 이번 역할 |
|---|---|---|
| 광자 수를 정확히 소거해 네 기체 변수만 푸는 구조 | `coupled_primary.rs::photons`, `interval_rhs` | 기존 해법의 기반 |
| H와 세 상태 He의 양성 갱신 | ordinary/conservative point의 기존 대수식 | 공통 계수 provider에 그대로 연결 |
| 온도·rate·광자 분모의 구간 자동미분 | `ft03_interval.rs`, `interval_rhs` | 같은 식의 새 provider 확장 대상 |
| 보존형 thermal proposal와 compensation | `primary_stage_step_conservative` | 새 사건 수지와의 동치 유도 |
| 네 변수 Krawczyk root 검증 | `primary_stage_root` | 실제 새 residual의 포함관계로 이어갈 대상 |
| conditional Case A 사건 소비 | EVENT_BRIDGE_02의 source와 독립 판정 | 원시 사건·모멘트의 단위와 투영을 재사용 |

이번에는 기존 point·proposal·root·interval 경로가 하나의 물리 정의를 사용하도록
만드는 식과 검증 가능한 연결을 완성했다.
정확한 source 위치는 [SOURCE_MAP](../source_map/SOURCE_MAP.md), identity는
[CURRENT_SOURCE](../source_map/CURRENT_SOURCE.json)에 있다.

직전 EVENT_BRIDGE_02의 176개 native test, primitive 비교, 단일 production interval은
그때 수행한 conditional 경로의 근거로 재사용했다. 이번 실행은 아래의 새 기호 계산과
독립 수학 검토다.

## 2. 광자 주입을 포함한 정확한 소거와 유한 photon budget

하위 상태의 수를 H 핵 하나당

\[
\ell=(1-x,\ f(1-a-b),\ fa)
\]

로 쓰면, node q의 채널별 opacity는

\[
\lambda_{aq}=c n_H\ell_a\sigma_{aq},\quad
\lambda_q=\sum_a\lambda_{aq}
\]

다. incoming photon `p_q^-≥0`, prescribed source `s_q^(H)≥0`, 시간 간격 `h>0`에 대해

\[
\boxed{p_q^+(y)=\frac{p_q^-+h s_q^{(H)}}{1+h\lambda_q(y)}}.
\tag{1}
\]

이는 gas candidate를 분모에 남긴 원래 photon BE 방정식의 정확한 해다. source가
0인 식은 현재 구현에 있다. source를 포함해도 node별 대각 block이므로 네 기체
변수 구조가 유지된다.

이때 실제 흡수 사건 수를

\[
A_{aq}=h\lambda_{aq}p_q^+,
\quad W_q=p_q^-+h s_q^{(H)},\quad D_q=1+h\lambda_q
\]

로 정의하면

\[
p_q^++\sum_a A_{aq}=W_q
\tag{2}
\]

가 정확히 성립한다. 양의 분모와 비음수 numerator가 광자 양성을 준다. 투명 node에서는
`lambda=0`, `p^+=W`, `A=0`이므로 branching ratio를 따로 만들 필요가 없다.

### 흡수 경쟁의 미분까지 구한 결과

한 node의 독립적인 채널 opacity에 대한 allocation Jacobian은

\[
\frac{\partial A_a}{\partial\lambda_b}
=\frac{hW}{D}\left(\delta_{ab}-\frac{h\lambda_a}{D}\right).
\tag{3}
\]

`hW>0`에서 대각은 양수이고 비대각은 비양수다. 각 열의 합은

\[
\sum_a\frac{\partial A_a}{\partial\lambda_b}=\frac{hW}{D^2}>0.
\tag{4}
\]

한 흡수 채널의 opacity를 키우면 총흡수는 늘고, 유한한 photon 공급 안에서 다른
채널과 배분을 바꾼다는 사실이 식으로 분리된다. Jacobian의 고유값은

\[
\{hW/D,\ hW/D,\ hW/D^2\}
\]

다. 또한 `A_a≥0`, `sum A<W`에서 정확한 역함수

\[
\lambda_a=\frac{A_a}{h(W-\sum_bA_b)}
\tag{5}
\]

를 얻었다. 이 역함수는 node 하나의 독립 opacity에 대한 결과이며, 실제 여러 node는
같은 세 종분율을 공유한다.

실제 분율 좌표에서는 HeII를 늘릴 때 HeI는 줄고 HeII absorber는 늘어난다. 따라서
HeI 흡수는 감소하고 HeII 흡수는 증가하지만, 남는 광자 수와 HI 흡수의 변화 방향은
`sigma_HeII−sigma_HeI`에 달린다. 이 구체적인 chain rule이 interval/Jet 연결의
판별 사례가 된다.

source가 계속 있고 `lambda>0`를 고정한 큰 h 극한에서는

\[
p_q^+-\frac{s_q^{(H)}}{\lambda_q}
=\frac{p_q^--s_q^{(H)}/\lambda_q}{1+h\lambda_q}
\]

이므로 photon 수는 source/absorption의 정상값으로 접근한다. source가 없고 opacity를
키우면 총흡수는 초기 photon supply로 포화한다. 두 극한과 transparent 경계는 같은
유리식에서 직접 따라온다.

## 3. 공유 사건에서 열 잔차와 보존형 잔차를 함께 구성

H 핵 하나당 CI, RR, DR 사건률을 `C_i,R_i,D_r`, captured kinetic power를
`K_i,L_r`, 광자 사건률을 `P_iq`로 쓴다. 사건률은 1/s, power는 eV/s 단위다.

\[
j_i=C_i-R_i+\sum_qP_{iq}-\mathbf1_{i=1}\sum_rD_r,
\quad G=(j_0,(j_1-j_2)/f,j_2/f).
\]

binding energy는

\[
B=\chi_0x+f\chi_1a+f(\chi_1+\chi_2)b
\]

이고, 사건으로부터 열과 escape를 투영하면

\[
Q=-\sum_i\chi_iC_i-\sum_iK_i-\sum_rL_r
  +\sum_{iq}(E_q-\chi_i)P_{iq},
\]

\[
Q_{esc}=\sum_i(\chi_iR_i+K_i)+\chi_1\sum_rD_r+\sum_rL_r.
\]

각 사건의 항을 직접 합해

\[
\boxed{Q+\nabla B\cdot G+Q_{esc}=\sum_{iq}E_qP_{iq}}
\tag{6}
\]

를 얻었다. 예를 들어 RR 한 사건에서는 열에서 `K`가 빠지고 binding에서 `chi R`이
빠지며, escape에 `chi R+K`가 들어간다. 이 상쇄는 별개의 평균 에너지를 도입하지
않고 실제 모멘트를 그대로 사용한다.

이제

\[
F_v=v-v^- -hG,\qquad F_w=w-w^- -h(Q-2Hw)
\]

를 기본 잔차로 삼는다. 광자와 escape를 복원한 뒤의 보존형 energy row는

\[
F_E=(1+2hH)w-w^-+\Delta B+hQ_{esc}-\sum_qE_q A_q
\tag{7}
\]

이며, 식 (6)에서

\[
\boxed{F_E=F_w+\boldsymbol b_\chi^T F_v},\qquad
\boldsymbol b_\chi=(\chi_0,f\chi_1,f(\chi_1+\chi_2))
\tag{8}
\]

가 나온다. 이 식은 최종 해에서만 성립하는 energy check보다 강하다. gas residual이
남아 있는 임의의 candidate에서도 두 잔차의 차이가 정확히 정해진다.

따라서 `F=(F_v,F_w)`, `F^E=(F_v,F_E)`는

\[
F^E=L_\chi F,\quad
L_\chi=\begin{pmatrix}I_3&0\\\boldsymbol b_\chi^T&1\end{pmatrix}
\]

로 연결된다. `L_chi`는 상수인 가역 행렬이므로 같은 root를 가지며,
`J^E=L_chi J`다. 정확한 미분과 가역 야코비안을 사용하는 Newton increment는
동일하다. 현재 ordinary/conservative fixed-point proposal의 반복 경로까지 같다는
뜻은 아니며, 이 관계는 두 경로의 최종 방정식을 묶어 준다.

식 (7)은 흡수량을 큰 photon reservoir의 차분으로 복원하지 않고 `A=h lambda p^+`에서
직접 계산한다. 열 proposal의 양성과 warm-domain 판정도

\[
U=w^- -\Delta B-hQ_{esc}+\sum_qE_qA_q,
\quad \widetilde w=U/(1+2hH)
\]

에서 바로 얻는다. `c_v=3k_B/(2epsilon_eV)`일 때 그 proposal이 warm domain에 들어갈
필요충분조건은

\[
(1+2hH)c_vdT_{min}\le U\le(1+2hH)c_vdT_{max}
\tag{9}
\]

다. 이렇게 화학의 양성 구조와 열 상태의 실제 budget 조건을 함께 사용할 수 있다.

## 4. 경계에서 정의되는 provider와 실제 미분 구성

현재 provider는 proper-volume 사건 bundle을 주지만, implicit H/He proposal은
생성·소멸 계수를 직접 필요로 한다. 이 연결에는 rate·moment 계수의 공통 객체가
맞는다.

\[
\{\beta_i(T),\alpha_i(T),\delta_r(T),\kappa_i(T),\zeta_r(T)\}.
\]

상위 상태 수를 `u=(x,fa,fb)`라 두면

\[
C_i=n_H\ell_i e\beta_i,quad R_i=n_Hu_i e\alpha_i,quad
D_r=n_Hfae\delta_r,
\]

\[
K_i=n_Hu_i e\kappa_i/\epsilon_{eV},\quad
L_r=n_Hfae\zeta_r/\epsilon_{eV}.
\tag{10}
\]

이 식은 어떤 population이나 전자수가 0이어도 정의된다. 동시에 같은 계수로
기존 H/He 생성·소멸 빈도를 구성할 수 있으므로, 영밀도에서 사건률을 population으로
나누어 계수를 되찾는 절차를 없앤다. 현재 H/He의 양성 resolvent는 이 계수를 그대로
소비한다.

### 1·2차 미분의 닫힌 식

`t=(1,f,2f)`라 하면 화학 좌표 r,s에서

\[
T_r=-Tt_r/d,\quad T_w=\tau/d,
\quad T_{rs}=2Tt_rt_s/d^2,
\quad T_{rw}=-\tau t_r/d^2,\quad T_{ww}=0.
\]

모든 primitive는 affine population m에 대해 `n_H A(v)c(T)`, `A=m e` 형태다.
따라서

\[
\partial_i(n_HAc)=n_H(A_ic+A c'T_i),
\]

\[
\partial_{ij}(n_HAc)=n_H[A_{ij}c+A_ic'T_j+A_jc'T_i
 +A(c''T_iT_j+c'T_{ij})]
\tag{11}
\]

로 value·gradient·Hessian을 함께 전달한다. photon 분모의 미분도 직접 포함한다.
같은 coefficient expression을 point scalar와 outward interval Jet으로 평가하고,
그 위에 같은 선형 사건 투영을 적용하면 계수의 포함관계가 전체 residual의
포함관계로 전달된다. 이 식이 point와 interval을 연결하는 수학적 계약이다.

현재 RR kinetic coefficient

\[
\kappa=k_BT\alpha\left(\tfrac32+\frac{d\log\alpha}{d\log T}\right)
\]

를 미분하면

\[
\kappa''=k_B[5\alpha'+\tfrac{11}{2}T\alpha''+T^2\alpha''']
\tag{12}
\]

가 생긴다. 따라서 rate의 낮은 차수 미분만 제공하는 인터페이스로 moment Hessian을
대체할 수 없다. 이번 구성은 moment를 자체 C² 함수로 제공하거나, 현재의 명시적
analytic moment 식을 같은 Jet으로 평가하도록 정했다.

interval의 행 변환은 표현식의 의존성에도 영향을 준다. 실수 대수에서
`R^E=R L_chi^-1`이면 preconditioned residual과 Jacobian은 같지만, 구간 entry를
독립적으로 곱하고 더하면 상쇄의 의존성이 사라져 box가 커질 수 있다. 최소 구현
계약은 기존 thermal residual을 canonical interval field로 유지하고, 공통 사건을
그 field에 연결하는 방식으로 정했다.

## 5. source·부피·기하를 같은 단계에서 닫는 구성

현재 reference-volume photon은 `N=V n_gamma`, `V=a_rel³`이고
`n_H,ref=Vn_H`다. 따라서

\[
p=N/n_{H,ref},\qquad s^{(H)}=S_{ref}/n_{H,ref}=s_{proper}/n_H.
\]

proper-density 입력의 동등한 update는

\[
n_q^+=\frac{(V_-/V_+)n_q^-+h s_q^+}{1+h\lambda_q}.
\tag{13}
\]

reference-variable 식을 변환한 결과이므로 dilution은 incoming factor `V_-/V_+`에
들어 있다. 기존 source callback의 quadrature weight·angular Jacobian도 source
정의에 이미 포함된다.

현재 paired caller처럼 source를 먼저 photon 입력에 합산하면

\[
\Phi(p^-+h s^{(H)},0)=\Phi(p^-,s^{(H)})
\tag{14}
\]

다. 따라서 기존 pre-stage birth와 직접 source numerator는 동일한 stage 표현이며,
하나의 경로에서 한 번 합산하면 된다. 이 동치는 불필요한 source API 변경 없이
provider 연결을 진행할 수 있는 근거다.

### 광자 에너지가 달라지는 history의 정확한 work

BE 사건을 endpoint node energy `E_q^+`로 계산한다고 하자. 유한 차분의 정확한
곱셈 법칙은

\[
E_q^+N_q^+-E_q^-N_q^-
=E_q^+(N_q^+-N_q^-)+(E_q^+-E_q^-)N_q^-.
\tag{15}
\]

이 식과 사건 수지를 결합하면, reference-volume 총에너지 `mathcal E`에 대해

\[
\boxed{\Delta\mathcal E+\Delta\mathcal E_{esc}+2hH U^+
 -\sum_q\Delta E_q N_q^-=h\sum_q E_q^+S_q^+}
\tag{16}
\]

가 성립한다. 여기서 `U`는 reference gas thermal energy이고, 모든 에너지를 eV 또는
erg 중 하나로 일관되게 사용한다. redshift로 `Delta E<0`이면 photon geometry work는
양수다.

연속 work의 endpoint 적분 `h sum nu_q E_q^+ N_q^+`를 쓰고 싶다면, 정확히 닫히는
work로 가는 보정은

\[
\delta W_\gamma=-\sum_q\Delta E_q N_q^-
               -h\sum_q\nu_q^+E_q^+N_q^+.
\tag{17}
\]

매끈한 기하와 해에서는 O(h²)다. source와 absorption이 모두 없는 한 node에서
`E^+=E^-exp(-nu h)`이면 이 차이는

\[
E^-N^-[1-(1+\nu h)e^{-\nu h}]
=\tfrac12 E^-N^-(\nu h)^2+O(h^3)
\]

로 직접 확인된다. 이번 결과는 선택한 BE stage를 history에 붙이는 식이며, 기존
continuous conditional RHS의 energy identity는 그대로 재사용한다.

같은 이유로 기본 열 변수 w를 T로 바꾸어 풀 때도 원래 endpoint residual에
`w=c_vdT`를 대입하는 방식이 정확하다. 연속 T 방정식에 BE를 별도로 적용하면
기본 energy residual과 `c_v Delta T Delta d`만큼 차이가 난다. 이 유한 단계 항까지
유도해 다음 구현에서 time-discrete map을 정확히 유지하도록 했다.

## 6. 실제 검산과 독립 검토에서 개선한 내용

Root의 첫 Wolfram 실행은 19개 exact symbolic group을 검사했고 모두 True였다.
대상은 사건 identity, full/reduced residual 행 변환, preconditioner 변환,
T·primitive·photon의 gradient/Hessian, RR moment 미분, 단일 RR 사건의 변화량,
T 좌표의 유한 단계 defect였다. 실제 engine은 Wolfram Language 15.0.1이다.

독립 검토는 단일 채널 witness의 설명 하나를 좁혀야 한다고 지적했다. 상수 RR 계수
증분은 한 번 소비와 population·전자수 의존성을 검증하지만, kinetic coefficient의
온도 미분까지 판별하지는 않는다. 그 구분을 고친 뒤, 열린 미분 의무를 직접
검사할 수 있도록 다음 companion을 구성했다.

\[
\delta\alpha_{HeIII}(T)=\rho_\star(T/T_\star)^2,
\quad \delta\kappa_{HeIII}(T)=\epsilon_{eV}\eta\delta\alpha_{HeIII}(T).
\]

`r_delta=n_H f b e delta alpha`라 하면 같은 candidate에서

\[
\delta F=h r_\delta(0,-1/f,1/f,\eta),
\quad \partial_w\delta F_w=2h\eta r_\delta/w,
\quad \partial_{ww}\delta F_w=2h\eta r_\delta/w^2.
\tag{18}
\]

양의 내부 상태에서 이 두 thermal derivative는 양수다. injected moment의 T 의존성을
상수로 freeze하면 이 값이 0이 되므로 실제 구현의 누락을 판별할 수 있다. 이 새
구성의 직접 event perturbation, escape, 잔차와 1·2차 미분을 별도 Wolfram 실행의
9개 group으로 검사했고 모두 True였다. Root의 두 실행에서 **28개 group이 통과**했다.

독립 photon 유도도 별도 Wolfram 실행에서 광자 수지·allocation·정규화·기하
product rule 등을 19개 group으로 검산해 모두 True를 얻었다. 세 실행의 검산 group은
**19 + 19 + 9 = 47개**다. 첫 photon 검산 시도는 SymPy가 없어 import 단계에서
종료되었고, 같은 수식을 사용 가능한 Wolfram evaluator로 검산했다. 이 환경 의존성과
실제 실행 원자료는 [RESULTS_SUMMARY](RESULTS_SUMMARY.json)에 구별해 기록했다.
수학적 증명과 exact symbolic 대조를 이번 근거로 삼았으며, 신규 native build나
ODE history를 이번 이론 결과로 계상하지 않았다.

검토자의 범위, 최초 지적, 수정 확인과 최종 판정은
[REVIEW_KO](../review/REVIEW_KO.md)와 [DECISION](../review/DECISION.json)에 있다.

## 7. 문헌과 이번 기여의 위치

관련 원전은 필요한 식과 주변 논증을 직접 읽었다. 문헌 전체를 읽거나 새로운
수렴·독창성 조사를 완료했다는 범위로 사용하지 않았다.

| 원전 | 직접 확인한 내용 | 이번 결과와의 관계 |
|---|---|---|
| Friedrich et al. 2012, 식 (8)–(13), §3.2 | He 세 상태 생성자와 상태 의존 계수의 반복 | 기존 positive chemistry의 구조를 확인 |
| Rosdahl et al. 2013, Appendix A 식 (A9) | photon numerator/denominator update; gas 계수는 시작 시점에 평가 | 분모 식의 선례와 현재 nonlinear candidate 소거의 차이를 특정 |
| Reynolds et al. 2009, §3.2.1 | fully implicit Newton의 Schur block 소거; 일부 Jacobian 의존성은 lagging | 정확한 block 대수와 미분 근사의 역할을 구별 |
| Blanes–Iserles–Macnamara 2022, Proposition 3.4 | graph-Laplacian의 비음수 BE resolvent | 전체 He 생성자의 양성 갱신을 뒷받침 |

Friedrich의 coupled OTS와 현재 Case A escape는 각자의 closure로 취급한다.
기존 소거·resolvent를 새 성과로 주장하는 대신, 이번에 닫은 결과는 공유 사건의
off-root 잔차 관계, coefficient/interval 전달식, source 정규화·소유,
finite-step geometry work와 실제 판별 witness다.

원문 링크와 읽은 페이지·식 번호는 [LITERATURE_MAP](../review/LITERATURE_MAP.md)에 있다.

- Friedrich et al.: https://arxiv.org/pdf/1201.0602
- Rosdahl et al.: https://arxiv.org/pdf/1304.7126
- Reynolds et al.: https://arxiv.org/pdf/0901.1110
- Blanes et al. 출판본: https://personales.upv.es/serblaza/2022_M2AN.pdf

## 8. 다음 코딩 루프에 넘기는 정확한 결과

다음 단위는 `HERE_RUX03_PRIMARY_PROVIDER_03`이다. 공통 coefficient/event 정의를
실제 ordinary point, conservative point, endpoint, interval/root와 paired caller에
연결하고, 식 (18)의 단일 소비·미분 witness를 그 경로에서 실행하면 된다.

현재 코드에서는 conditional의 event provider가 private인 반면 primary의 여러
callsite가 FT03를 직접 선택한다. 또한 paired caller는 conservative point와
ordinary-point centre를 쓰는 root를 함께 사용한다. 구현 계약은 이 실제 연결들을
하나의 변경 단위로 묶고, 값만 바뀌고 interval이 이전 식에 남는 경로를 구체적으로
검사하도록 정리했다.

그 뒤에는 RUX02의 physical source 입력과 RUX03의 rate-domain 조건을 맞춰
`RUX02 + RUX03 → RUX04 → RUX05`의 원래 의존성을 따른다. 이번 이론 결과가 그
구현과 scenario 연결에 필요한 식·가정·증명·판별 기준을 제공한다.

## 주요 자료

- [CLAIMS.json](CLAIMS.json): 주장별 근거 유형과 정확한 범위.
- [RESULTS_SUMMARY.json](RESULTS_SUMMARY.json): 실제 실행과 재사용 근거.
- [CODING_CONTRACT_KO.md](CODING_CONTRACT_KO.md): 다음 구현의 callsite와 판별 기준.
- [HANDOFF_KO.md](HANDOFF_KO.md): 재개 순서와 남은 의무.
- [공통 잔차·provider 전체 유도](../derivations/SHARED_RESIDUAL_AND_PROVIDER.md).
- [독립 광자·기하 전체 유도](../derivations/PHOTON_ELIMINATION.md).
