# E13C4: 고정 gas path에서 1차 보정의 국소 잔여오차를 둘러싸기

## 범위, 근거와 책임

**근거 상태: `derived`; §10의 새 exact toy 계산에 한하여 `implementation-verified`.** 이 문서는 이론 contributor의 산출물이다. 여섯 실제 구간에 대한 enclosure 실행과 최종 독립 decision review는 owner가 별도 증거로 판단한다. contributor는 후보의 승격을 결정하지 않는다.

직접 읽은 기준은 E13C3 `THEORY.md` 전체, 특히 §§5–6, `NEXT_DAG.json` 전체, `inputs/e13c2/code/decimal_collocation.py`의 정의·coefficient helper·frozen 표현 부분, 그리고 저장된 `evidence/decimal/DECIMAL_RESULTS.json`의 계약·입력·근거 구조다. GPT-6 Astra research harness v4.0.0의 공통 core, phase 6, evidence policy와 coding harness의 core 및 ultralight 계약을 적용했다. 하네스의 비어 있는 state/contract 템플릿은 실행 증거로 사용하지 않았다.

목표는 기존 E13C3의 **정확한 1차 response와 연속 모델 사이의 잔여오차**에 실제 outward enclosure를 부여하고, 이를 **저장된 유한 정밀도 후보의 수치 오차**와 분리하는 것이다. E13C2 연속 solver, 기존 oracle, native/gas/Newton 경로는 다시 실행하지 않았다. 새 계산은 Python 표준 라이브러리의 정확 유리수와 형식적 지수식으로 작성한 작은 toy 검산 하나다.

현재 local 초기조건은 여섯 구간 각각에서 captured `f0`를 그대로 쓰고 true incoming defect를 정확히 0으로 두는 것이다. 이는 global continuous history를 매 구간 재정의하라는 지침이 아니다. 전체 path의 해와 비교하려면 실제 incoming defect 및 그 불확실성을 전파해야 한다.

## 1. 동일한 국소 문제와 전제

국소 무차원 좌표를 \(u=s-s_a\in[0,h]\), \(s=\ln a\)로 놓는다. 현재 energy characteristic은

\[
E(u)=E_0e^{-u},\qquad E_h=E_0e^{-h}
\tag{1}
\]

이다. \(P\)는 기존 photon stock 정규화, \(\lambda_i\)는 종별 dimensionless opacity, \(q\)는 \(u\)에 대한 photon injection이다. Count는 \(P\)와 같은 정규화를 갖고, 이 문서의 absorbed energy·heat·redshift는 eV에 그 정규화를 곱한 단위로 쓴다. erg로 바꾸는 경우에만 상속된 \(\epsilon\)을 한 번 곱한다.

정확한 실수 문제와 frozen 문제는

\[
P'=q-\Lambda P,\quad \Lambda=\sum_i\lambda_i,\qquad
P_f'=q_f-LP_f,\quad L=\sum_i\lambda_{if}.
\tag{2}
\]

\(q_f,\lambda_{if},E_0,h,P_{fa}\)와 gas endpoints, 모든 수치 상수는 **상속된 binary64 값을 정확히 실수로 올린 정의**를 유지한다. 수학적 midpoint의 연속 coefficient를 새로 계산하여 frozen coefficient를 바꾸지 않는다. Captured coefficient와 그 midpoint 값의 차이도 \(\delta q=q-q_f\), \(\delta\lambda_i=\lambda_i-\lambda_{if}\)에 포함된다. 따라서 아래 적분 bound에 midpoint mismatch를 별도로 누락할 여지가 없다. 도함수만으로 variation bound를 대체한다면 E13C3의 \(h|\Lambda(h/2)-L|\) 항을 유지해야 한다.

전제는 다음과 같다.

1. \(h\ge0\), \(P_{fa}\ge0\), \(q_f\ge0\), \(\lambda_{if}\ge0\), \(\Lambda(u)\ge0\)가 해당 구간에서 성립한다. 따라서 \(P_f\ge0\)이다.
2. 계수는 현재 event branch에서 유한하고 적분 가능하다. Frozen 및 실제 source/opacity mask, 에너지 anchor, affine gas path와 배경은 바꾸지 않는다. Source 또는 threshold의 사건 하나를 가로질러 coefficient 정의를 섞지 않는다.
3. 아래 절댓값 적분에는 연속성이나 2차 미분이 필수적이지 않다. §7의 midpoint 오차정리를 사용할 때만 각 cell의 고정 branch 연장이 \(C^2\)이고 모든 log·sqrt·division의 domain을 전체 cell에서 확인한다.
4. Local enclosure의 입력은 고정된 exact-lift 값이다. 원자 단면적 모델의 물리적 불확실성, 실제 RCT emission spectrum, gas solver 오차나 관측 불확실성을 포함하는 구간이 아니다.

Metric convention \((- ,+,+,+)\), 상속된 \(c\), source normalization과 binding energy는 그대로다. 종 \(i\)가 비활성이면 현재 branch에서 \(\lambda_i=\lambda_{if}=\delta\lambda_i=0\)이다. 비활성 종의 \(\chi_i\)가 현재 photon energy보다 크다는 이유로 활성 종의 양의 heat weight 검사를 실패시킬 필요는 없다.

## 2. 정확한 first variation과 공통 kernel

\[
\delta\Lambda=\Lambda-L,\qquad
r=\delta q-\delta\Lambda P_f,\qquad
e=P-P_f,
\tag{3}
\]

로 두면 \(e'+\Lambda e=r\)이다. 정확한 incoming defect \(e_a\)를 사용하는 first variation은

\[
e_1'+Le_1=r,\qquad e_1(0)=e_a.
\tag{4}
\]

\(\mathcal J_a(z)=\int_0^a e^{-zt}\,dt\)를 쓰면

\[
P_f(u)=P_{fa}e^{-Lu}+q_f\mathcal J_u(L),\quad
W(v)=e^{-L(h-v)},\quad K_0(v)=\mathcal J_{h-v}(L),
\]

\[
K_E(v)=E(v)\mathcal J_{h-v}(L+1).
\tag{5}
\]

\(\mathcal J_a(0)=a\)로 정의하여 \(L=0\)에서 나눗셈 특이점을 만들지 않는다. Frozen damping은 전개하지 않으므로 \(Lh\ll1\)은 전제가 아니다. 세 kernel은

\[
W+LK_0=1,\qquad E_hW+(L+1)K_E=E(v)
\tag{6}
\]

를 만족한다.

현재 \(e_a=0\)에서는 endpoint·종별 count·absorbed energy·heat·redshift의 1차 보정을 다음 **signed integrand**의 한 번 적분으로 쓸 수 있다.

| 보정 | 적분할 함수 \(F(v)\) |
|---|---|
| \(e_1(h)\) | \(Wr\) |
| \(\Delta A_i^{(1)}\) | \(\delta\lambda_iP_f+\lambda_{if}K_0r\) |
| \(\Delta B_i^{(1)}\), eV | \(E\delta\lambda_iP_f+\lambda_{if}K_Er\) |
| \(\Delta H_i^{(1)}\), eV | \((E-\chi_i)\delta\lambda_iP_f+\lambda_{if}(K_E-\chi_iK_0)r\) |
| \(\Delta Z^{(1)}\), eV | \(K_Er\) |
| \(\Delta Q_N\) | \(\delta q\) |
| \(\Delta Q_E\), eV | \(E\delta q\) |

Heat는 \(B-\chi A\)라는 정의를 유지하되, enclosure 계산에는 처음부터 \(E-\chi\) weight를 넣으면 서로 큰 두 interval의 차를 만드는 폭 증가를 줄일 수 있다. 이 표현의 변경은 새로운 물리적 heat 모델을 넣는 것이 아니다.

## 3. True defect와 photon remainder

다음 양은 모두 **정확한 적분**을 먼저 뜻한다.

\[
D=\int_0^h|\delta\Lambda|\,du,\qquad
B_r=\int_0^h\bigl(|\delta q|+|\delta\Lambda|P_f\bigr)\,du,
\qquad S=|e_a|+B_r.
\tag{7}
\]

Nonnegative true opacity 때문에 true Green 함수가 1 이하이고, 따라서

\[
\|e\|_\infty\le S.
\tag{8}
\]

\(R=e-e_1\)에 대해서는

\[
R'+LR=-\delta\Lambda e,\quad R(0)=0,
\qquad
R(u)=-\int_0^u e^{-L(u-v)}\delta\Lambda(v)e(v)\,dv.
\tag{9}
\]

그러므로

\[
\|R\|_\infty\le SD,
\quad |R(h)|\le S H_h,
\quad \left|\int R\right|\le S H_0,
\quad \left|\int ER\right|\le S H_E,
\tag{10}
\]

\[
H_h=\int W|\delta\Lambda|,\quad
H_0=\int K_0|\delta\Lambda|,\quad
H_E=\int K_E|\delta\Lambda|.
\]

현재 local 조건에서는 \(S=B_r\)다. \(\int|r|\)의 별도 상계가 있다면 (8)에 그 상계를 사용할 수도 있지만, unsigned triangle quantity인 \(B_r\)와 실제 signed response를 같은 양으로 기록해서는 안 된다.

## 4. 종별 잔여오차와 cancellation을 보존하는 형태

정확한 moment remainder는

\[
R_{A_i}=\lambda_{if}\int R+\int\delta\lambda_i e,
\qquad
R_{B_i}=\lambda_{if}\int ER+\int E\delta\lambda_i e,
\tag{11}
\]

이며 \(R_{H_i}=R_{B_i}-\chi_iR_{A_i}\)다. \(V_i=\int|\delta\lambda_i|\), \(V_{E,i}=\int E|\delta\lambda_i|\)로 놓으면 E13C3의 bound를 회복한다.

\[
|R_{A_i}|\le S(\lambda_{if}H_0+V_i),\qquad
|R_{B_i}|\le S(\lambda_{if}H_E+V_{E,i}).
\tag{12}
\]

한 단계 더 나아가 (9)를 (11)에 넣고 적분 순서를 바꾸면 **같은 true defect \(e(v)\)**를 곱하는 단일 kernel로 합칠 수 있다.

\[
\boxed{R_{A_i}=\int_0^h
 [\delta\lambda_i-\lambda_{if}K_0\delta\Lambda]e\,dv,}
\tag{13}
\]

\[
\boxed{R_{B_i}=\int_0^h
 [E\delta\lambda_i-\lambda_{if}K_E\delta\Lambda]e\,dv.}
\tag{14}
\]

\(w_i=E-\chi_i\), \(K_{H_i}=K_E-\chi_iK_0\)로 쓰면

\[
\boxed{R_{H_i}=\int_0^h
 [w_i\delta\lambda_i-\lambda_{if}K_{H_i}\delta\Lambda]e\,dv.}
\tag{15}
\]

따라서 대괄호 안의 effective integrand를 \(T_X\)라 할 때

\[
|R_X|\le S\int_0^h |T_X(v)|\,dv
\tag{16}
\]

가 성립한다. 이 bound는 절댓값 안에서 direct variation과 field-response variation의 cancellation을 보존한다. 식 (15)–(16)은 \(w_i\)가 signed인 일반 경우에도 유효하다. Weight positivity는 다음의 더 단순한 triangle 분해에 필요하다.

활성 종에서 구간 전체에 \(E\ge\chi_i\)가 성립하면

\[
K_{H_i}(v)=\int_v^h (E(u)-\chi_i)e^{-L(u-v)}\,du\ge0,
\]

\[
\boxed{|R_{H_i}|\le
S\left[\lambda_{if}\int K_{H_i}|\delta\Lambda|
       +\int w_i|\delta\lambda_i|\right].}
\tag{17}
\]

Signed heat kernel을 positivity 확인 없이 양의 상계처럼 쓰면 부등식 자체가 틀릴 수 있다. Interval dependency 때문에 (16)의 계산 상계가 (17)보다 항상 작지는 않다. 둘 다 독립적으로 유효한 outward upper value를 얻었다면 그 최솟값도 유효한 상계다. 이 최솟값 선택은 tolerance를 완화하는 절차가 아니다.

## 5. 총 heat와 source/redshift의 구조

활성 종에 대해

\[
g_f(v)=\sum_i\lambda_{if}w_i(v)=LE(v)-C_f,
\quad C_f=\sum_i\chi_i\lambda_{if},
\]

\[
g_\delta(v)=\sum_iw_i(v)\delta\lambda_i(v),
\qquad K_g(v)=\sum_i\lambda_{if}K_{H_i}(v)=LK_E-C_fK_0
\tag{18}
\]

로 놓는다. 첫 변화의 총 heat integrand는

\[
F_{H,\mathrm{tot}}=g_\delta P_f+K_g r
\tag{19}
\]

다. 총 heat의 exact remainder 및 결합 bound는

\[
\boxed{R_{H,\mathrm{tot}}=\int_0^h
 [g_\delta-K_g\delta\Lambda]e\,dv,\qquad
|R_{H,\mathrm{tot}}|\le S\int|g_\delta-K_g\delta\Lambda|.}
\tag{20}
\]

모든 활성 종의 heat weight가 음수가 아니면 다음 두 triangle bound도 사용할 수 있다.

\[
|R_{H,\mathrm{tot}}|
\le S\left[\int K_g|\delta\Lambda|+\int|g_\delta|\right]
\]

\[
\le S\left[\int K_g|\delta\Lambda|
  +\int\sum_iw_i|\delta\lambda_i|\right].
\tag{21}
\]

첫 줄은 종 사이의 weighted cancellation을 남기고, 두 번째 줄은 species variation의 양의 합만 사용한다. (20)은 다시 두 성분 사이의 cancellation까지 남긴다. 유도상으로 더 날카로운 식과 interval 구현에서 실제 더 작은 upper value를 주는 식을 구분해서 기록한다.

Source 차이 \(\Delta Q_N=\int\delta q\), \(\Delta Q_E=\int E\delta q\)에는 photon first-variation의 수학적 truncation이 없다. 이들은 모델이 고정되어 있을 때 이미 정확한 source 차이이며, **유한 수치 적분의 enclosure 폭은 별도**로 남는다. Redshift의 차이는 \(\Delta Z=\int Ee\)이므로 \(|R_Z|\le S H_E\)다.

True ledger와 정확한 1차 ledger의 차이를 취하면

\[
R(h)+\sum_i R_{A_i}=0,
\qquad E_hR(h)+\sum_iR_{B_i}+R_Z=0.
\tag{22}
\]

따라서 총 count remainder는 endpoint remainder의 음수이고, 총 count의 상계는 곧 \(S H_h\)다. 그러나 종별 count는 (22)로 따로 결정되지 않는다. 총 absorbed energy의 cancellation도 species heat의 cancellation을 뜻하지 않는다. Heat에는 종별 binding energy가 가중되어 있기 때문이다.

\(\delta\Lambda=0\)이면 photon response는 정확하지만 \(\delta\lambda_i\ne0\)와 \(e\ne0\)가 함께 존재할 수 있다. 이때

\[
R_{A_i}=\int\delta\lambda_i e,\qquad
R_{H,\mathrm{tot}}=-\sum_i\chi_i\int\delta\lambda_i e
\tag{23}
\]

는 일반적으로 0이 아니다. §10의 정확한 반례가 이 점을 확인한다.

## 6. Incoming uncertainty와 full path의 제한

이번 local 실행에서는 \(e_a=0\)이 정확하다. 향후 경로 전파에서 \(\widetilde e_a\)를 쓰고 \(|e_a-\widetilde e_a|\le\eta_a\)만 아는 경우에는

\[
S_*=|\widetilde e_a|+\eta_a+B_r,\quad
R(u)=e^{-Lu}(e_a-\widetilde e_a)-\int_0^u e^{-L(u-v)}\delta\Lambda(v)e(v)\,dv.
\tag{24}
\]

따라서 endpoint는

\[
|R(h)|\le e^{-Lh}\eta_a+S_*H_h.
\tag{25}
\]

종별 count·energy·heat의 결합 kernel bound에는 각각 다음 initial-response 상계를 더한다.

| 양 | 추가할 incoming-error 상계 |
|---|---|
| Count \(A_i\) | \(\eta_a\lambda_{if}\mathcal J_h(L)\) |
| Absorbed energy \(B_i\), eV | \(\eta_a\lambda_{if}E_0\mathcal J_h(L+1)\) |
| Heat \(H_i\), eV | \(\eta_a\lambda_{if}|E_0\mathcal J_h(L+1)-\chi_i\mathcal J_h(L)|\) |
| Total heat, eV | \(\eta_a|LE_0\mathcal J_h(L+1)-C_f\mathcal J_h(L)|\) |
| Redshift, eV | \(\eta_a E_0\mathcal J_h(L+1)\) |

이 표의 항과 \(S_*\int|T_X|\)를 합한다. Positive weight인 경우 표의 heat 절댓값 안은 음수가 아니다. \(\eta_a\)를 빼면 \(D=B_r=0\)인 상수 계수 문제조차 0이 아닌 incoming error를 놓친다.

다른 exact equation \(R'+\Lambda R=-\delta\Lambda\widetilde e_1\)로부터

\[
\|R\|_\infty\le\eta_a+D(|\widetilde e_a|+B_r)
\tag{26}
\]

도 얻는다. 이는 scalar sup norm에 유용하지만 frozen weighted damping의 정보를 자동으로 포함하지 않는다. 서로 다른 부등식의 더 작은 항을 임의로 짜깁기해서는 안 된다.

실제 path에서는 incoming uncertainty 외에도 stage transition, captured/exact frozen representation, energy anchor와 source branch의 연결을 운반해야 한다. 여섯 독립 local bound가 성립했다는 사실만으로 first2 full path 또는 새 gas evolution의 certificate가 되지는 않는다.

## 7. 전체 구간 enclosure와 midpoint 오차정리

### 7.1. 절댓값 적분은 전체 cell의 range로 제한한다

\(t=u/h\in[0,1]\)에서 \(N\)개 cell을 사용한다. 각 cell의 모든 \(t\)에 대해 \(f(t)\in[\ell_j,r_j]\)를 보장하면

\[
\int_0^h f(u/h)\,du
\in \frac hN\sum_{j=0}^{N-1}[\ell_j,r_j]
\tag{27}
\]

다. Interval arithmetic의 각 연산이 outward inclusion을 제공하고, grid 자체가 전체 \([0,1]\)을 덮으며, 적분 폭 및 합도 outward로 계산될 때 유효하다. Endpoint나 midpoint 값만 넣은 sampled rectangle은 (27)의 range enclosure가 아니다.

\(|\delta\Lambda|\), \(|\delta\lambda_i|\), \(|T_X|\)는 구간 내부의 영점에서 미분 불가능할 수 있다. 이 양들은 whole-cell interval Riemann bound로 평가한다. 부호를 cell 전체에서 인증하지 않은 채 sampled derivative 또는 2차 derivative를 abs에 적용하여 midpoint 오차를 제한하지 않는다.

### 7.2. Signed firstvariation 적분에는 interval second derivative를 쓴다

정확한 보정 하나가 \(I=h\int_0^1 f(t)\,dt\)라고 하자. Cell \(C_j=[j/N,(j+1)/N]\), midpoint \(m_j=(j+1/2)/N\)에서 \(f\)가 \(C^2\)이고

\[
|f''_t(t)|\le M_j\quad(t\in C_j)
\tag{28}
\]

가 검증되었다면 Taylor 정리의 적분형 또는 pointwise remainder로부터

\[
\left|h\int_{C_j}f(t)\,dt-\frac hN f(m_j)\right|
\le\frac{hM_j}{24N^3}.
\tag{29}
\]

증명에서 \(f(m_j)\)를 제외한 선형항은 대칭 적분으로 0이고, 남은 항은 \(\frac12M_j\int_{-1/(2N)}^{1/(2N)}x^2dx=M_j/(24N^3)\)다. 전체 midpoint 합의 truncation bound는

\[
B_{\mathrm{mid}}=\sum_j\frac{hM_j}{24N^3}
\tag{30}
\]

이며, global \(M\) 하나를 사용한다면 \(hM/(24N^2)\)다. \(f''_t\)는 **normalized coordinate \(t\)**에 대한 2차 derivative다. \(u\)에 대한 derivative를 그대로 쓰면 chain factor \(h^2\)를 잃는다.

각 midpoint의 평가값도 outward interval \(F_j\)로 계산한다. 그러면 정확한 integral의 enclosure는

\[
\boxed{J=\frac hN\sum_jF_j+[-B_{\mathrm{mid}},B_{\mathrm{mid}}].}
\tag{31}
\]

2차 interval jet의 zeroth component는 whole-cell coefficient range를, second component는 (28)을 제공해야 한다. 계수·kernel·signed heat integrand의 모든 elementary 연산과 derivative 연산이 inclusion을 보존한다는 구현 검증은 owner의 별도 책임이다. Decimal precision을 높였다는 사실만으로 (28)이나 (31)이 따라오지 않는다.

고정 source/threshold branch의 경계에서 값 하나를 달리 주는 것은 적분값을 바꾸지 않는다. 그러나 해당 branch 식의 \(C^2\) 연장이 cell closure까지 유한해야 midpoint 정리를 적용할 수 있다. 실제 branch transition이 cell 내부에 있으면 분할해야 하며, smoothness를 선언만 하고 진행해서는 안 된다. 현재 task의 mask·anchor를 새 사건 위치로 바꾸는 것도 허용되지 않는다.

N 증가에 따른 enclosure 폭의 감소는 sharpness의 관찰이다. 유효한 inclusion은 각 N 자체의 논증으로 성립하며, 관찰된 N 수렴률이나 고정밀 두 결과의 일치가 그 논증을 대체하지 않는다.

## 8. 저장된 후보를 감싸는 오차: 세 층의 분리

어떤 output의 정확한 continuous-minus-exact-frozen 차이를 \(X\), 정확한 first variation을 \(X_1\), 저장된 후보의 수치 값을 \(C\)라고 하자. 위 유도로 \(|X-X_1|\le B_{\mathrm{rem}}\)를 얻고, (31)로 \(X_1\in J=[J_-,J_+]\)를 얻었다면

\[
\eta_{\mathrm{num}}=\max(|C-J_-|,|C-J_+|),
\]

\[
\boxed{|X-C|\le B_{\mathrm{rem}}+\eta_{\mathrm{num}}.}
\tag{32}
\]

이는 saved candidate가 새 midpoint 방식으로 계산되었다는 가정을 요구하지 않는다. \(C\)가 GL12나 이전 Decimal candidate여도, 정확한 값 \(X_1\)을 감싸는 검증된 \(J\)와의 최대 거리로 충분하다. 단, \(C\)를 어떤 실수로 읽었는지를 명확히 해야 한다. 저장된 decimal 문자열을 정확히 읽은 값의 certificate와 원래 메모리에 있던 binary 값의 bit-exact certificate는 동일한 주장으로 취급하지 않는다.

세 층은 각각 별도로 보고한다.

1. **Mathematical truncation:** \(B_{\mathrm{rem}}\). Exact firstvariation과 exact variable-coefficient 해 사이의 차이다.
2. **Candidate numerical enclosure:** \(\eta_{\mathrm{num}}\). Signed integral의 midpoint truncation, outward arithmetic와 저장 candidate의 값 차이가 포함된다.
3. **Inherited representation:** candidate가 exact frozen baseline이 아니라 native saved output에 보정을 더한다면, exact-frozen와 native-frozen의 차이 및 해당 endpoint/anchor 연결 항을 추가해야 한다.

예를 들어 \(X_{\rm exact}=X_f+\Delta X\)이고 native 후보가 \(X_{f,\rm cap}+C\)이면

\[
|X_{\rm exact}-(X_{f,\rm cap}+C)|
\le |X_f-X_{f,\rm cap}|+B_{\mathrm{rem}}+\eta_{\mathrm{num}}.
\tag{33}
\]

첫 항을 enclosure로 계산하지 않았다면 (32)의 correction certificate를 (33)의 native-output certificate로 넓혀 쓰지 않는다. 현재 source/redshift와 energy anchor도 이 의미 구분 안에 유지한다.

기존 saved continuous reference는 계산 결과와의 **compatibility check**에 사용할 수 있다. 저장된 reference의 order 차이나 precision 차이는 수치 불확실성의 진단 자료이며, 독립적인 interval proof가 없으면 exact reference enclosure가 아니다. 이를 (32)의 엄밀 상계에 합쳐 proof를 완성했다고 주장하지 않는다. 이번 방법의 엄밀성은 reference와의 일치가 아니라 fixed-input inclusion 및 부등식에 근거한다.

## 9. 근사 차수와 admissibility의 한계

Fixed finite interval에서 \(\delta q,\delta\lambda_i\)가 필요한 weighted \(L^1\) norm으로 \(O(\varepsilon)\)이고 \(P_f\)가 bounded이며 \(e_a=O(\varepsilon)\)이면 \(S,D,V_i=O(\varepsilon)\)이므로 photon·species remainder는 \(O(\varepsilon^2)\)다. 이 말은 coefficient variation에 대한 차수다. \(e_a=O(1)\)를 독립적으로 고정하면 \(D|e_a|\)가 남으므로 uniform 2차 주장으로 바꿀 수 없다.

Midpoint 적분의 N에 따른 오차 차수와 이 coefficient-variation 차수는 다른 양이다. 양쪽을 각각 제한해야 saved candidate의 완전한 bound가 된다. Local remainder 상계가 작다는 결과를 기존 algebraic TOL, 임의의 1% defect ratio, 실제 물리 budget과 동일하게 취급하지 않는다. Relative ratio는 denominator의 정확한 의미와 near-zero conditioning을 함께 밝혀 sharpness 진단으로만 쓴다.

이번 유도가 직접 여는 것은 **같은 여섯 exact-lift local initial-value problem에 대한 numerical enclosure**다. 실제 atomic photon/heat/recoil의 입력, HE-F2/F09의 owner gate, receiver adoption과 production은 별도다. `baseline_RCT=OFF`, actual moments `null`, physical/production `HOLD`, HE-F2/F09 `OPEN`, receiver `SEPARATE`, Gamma alias `3.543295 FAIL`을 유지한다.

## 10. 새 exact toy 계산과 남은 검증 경계

`exact_remainder_toys.py`는 `fractions.Fraction`으로 모든 coefficient를 계산하고 \(T=e^{-1}\)에 대한 Laurent polynomial을 정확히 다룬다. 실제 초월함수의 float 평가를 사용하지 않았다. 부호 부등식에 필요한 \(T\) 범위는

\[
e\in\left[\sum_{k=0}^4\frac1{k!},\;
\sum_{k=0}^4\frac1{k!}+\frac{1/5!}{1-1/6}\right]
\]

라는 유리수 Taylor-tail bound를 역수로 취해 얻었다. 다항식×지수 적분은 닫힌 유한식과 별도의 적분부분법 recurrence를 대조했다.

**실행 결과: 63개 검사 PASS, FAIL 0, actual exit 0, elapsed 0.0741202199997133 s.** 실제 코드 SHA-256은 `a241ef2d128ac223686f445ea87db42f43217ef4037ca31d9700203e13ec417c`다. 실제 command, environment, before/after SHA, raw stdout/stderr와 최초 과학 실패 여부는 `EXECUTION.json`, `stdout.txt`, `stderr.txt`, `EXACT_TOY_RESULTS.json`에 보존했다. 최초 과학 실패는 없었다. 선택 정책 파일의 이름을 추정해 읽다가 난 별도 read failure는 올바른 경로를 확인하여 해결했으며, 과학 실행과 구분해 기록했다.

검산의 판별점은 다음과 같다.

| 사례 | 정확한 결과와 판별 대상 |
|---|---|
| 모든 coefficient 일정, incoming 0 | Frozen ODE와 true solution이 일치하고 defect·remainder는 0이다. |
| \(L=0\), \(\delta q=u\) | \(e=e_1=u^2/2\). Nonzero source와 energy/redshift ledger가 singular division 없이 닫힌다. |
| 두 양의 종, \(\delta\Lambda=0\) | \(e=u\), \(\delta\lambda_1=(u-1/2)/2\), \(\delta\lambda_2=-\delta\lambda_1\)에서 종별 count remainder는 \(+1/24,-1/24\)다. |
| 같은 cancellation 예, \(E=6e^{-u}\), \(\chi_1=1,\chi_2=2\) | 모든 활성 heat weight가 양수이고 총 absorbed-energy remainder는 0이지만, 총 heat remainder는 정확히 \(+1/24\) eV이다. |
| \(\Lambda=1+u/2\), \(e=u\)를 만드는 source | (13)–(15)의 effective kernel identity와 photon/count/energy/redshift remainder ledger가 정확히 성립한다. |
| Constant coefficient, \(\eta_a=1/8\) | \(D=B_r=0\)이어도 endpoint·count·energy incoming remainder가 양수다. \(\eta_a\) 누락을 검출한다. |
| \(E_0=1,\chi=2\) | \(K_H(0)<0\). Positive heat kernel 전제가 실패하는 반례다. 비활성 종이면 coefficient가 0이어서 기여는 정확히 0이다. |
| Quadratic midpoint 적분 | Normalized second derivative와 상수 \(1/24\)를 사용한 bound가 실제 오차와 정확히 같다. |
| \(|t-1/2|\), N=3 | 실제 적분 \(1/4\)와 midpoint 값 \(2/9\)가 다르다. Smooth 구간의 sampled curvature 0만으로는 오차를 제한할 수 없고, whole-cell range 상계 \(7/18\)는 유효하다. |

이 계산은 이론의 부호·누락 항·상쇄 구조·적분 오차정리에 대한 독립적인 exact toy 검증이다. 실제 Verner coefficient와 여섯 physical input에서의 interval inclusion, Decimal elementary operation, interval jet 구현, 최종 결과의 sharpness를 대신 검증하지 않는다. 그 항목은 owner의 계산 및 실제 독립 decision reviewer의 읽기·판정 범위에 남는다.
