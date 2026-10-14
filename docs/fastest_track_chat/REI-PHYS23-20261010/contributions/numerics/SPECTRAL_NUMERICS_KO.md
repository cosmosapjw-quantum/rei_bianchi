# PHYS23 독립 수치 기여 — spectral response와 양의 spectrum

2026-10-10 · 수치 기여자이며 최종 decision reviewer가 아니다.

## 1. 결론과 근거 수준

새 65개 검산이 최초 과학 실행에서 모두 통과했다. 원래 HI 단면적을 로그 에너지에서 직접 차분한 결과와 analytic curvature를 비교했고, 고정된 PHYS22의 13.7 eV 값에는 한 번의 작은 연결 검사만 수행했다. 새 gas IVP, native 계산, PHYS22 main 또는 이전 suite는 실행하지 않았다.

선언한 대표 에너지에서 HII, 열에너지/H, 온도와 HeII 계수는 모두 음수다. HeIII는 14 eV에서 양수이고 16 eV에서 음수이며, 수치적 zero bracket은 약 15.43367086782694 eV다. 이 기여문의 유한 표본과 bracket은 구간 전체의 영점 부재나 영점의 유일성 증명이 아니다. HeIII 계산은 PHYS22에서 닫힌 수치 Jacobian을 조건으로 한다.

양의 두 선 spectrum과 같은 광자수·총 에너지를 가진 단일 평균 에너지 spectrum 사이에도 계수가 다르다. 특히 14/24 eV에 같은 에너지를 배분한 spectrum은 HeIII 첫 계수가 양수지만, 같은 총 광자수와 총 에너지를 가진 17.6842105263 eV 단일선은 음수다. 따라서 평균 에너지 하나로 이 국소 반응을 보존하는 closure는 일반적으로 성립하지 않는다.

근거 상태는 직접 전사·유도 및 numerically checked / implementation-verified다. 전체 band의 엄밀 부호 분류는 별도 analytic certificate가 실제로 제공하는 범위만 사용할 수 있다.

## 2. 고정 모델, 단위와 상속 입력

연구 계약 SHA256은 888eb11c8a53f828b0ed5d3a053d91dc4da671d727e49c519cb3110bb5b6d200이다. PHYS22_INITIAL_COEFFICIENTS.json의 SHA256은 6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79이다. 이 JSON의 초기계수와 local nonphoto Jacobian을 읽었으며, PHYS22 코드의 함수나 main은 import하지 않았다.

Metric signature는 \((-+++)\), proper time은 초, 에너지는 eV다. \(B=t\Sigma\), \(\Sigma=\varsigma\,{\rm diag}(1,-1,0)\), \(q=2\varsigma^2\), \(\varsigma=((1.01e{-14})-(0.99e{-14}))/2\)의 source binary64 literal 차이를 쓴다.

\[
F_\epsilon=F_0+\epsilon^2F_2+o(\epsilon^2),\qquad
F_2=\tfrac12\partial_\epsilon^2F|_0,\qquad
F_2(t)=a_3t^3+a_4t^4+\cdots .
\]

아래 수치에는 물리적 \(q\) 또는 shear 제곱이 이미 포함돼 있다. \(t^n\) 계수에 추가 factorial은 없다. 온도는 정확한 실수 해석에서 50000 K로 정규화했다. PHYS22 Decimal 입력과 같은 convention이며 native binary64 연산을 매 단계 재현하는 계산은 아니다.

실제 초기 기체는 \(n_H=10^{-4}\,{\rm cm}^{-3}\), \(f=0.083\), \((x,h_1,h_2)=(0.9,0.3,0.6)\), \(T=50000\,{\rm K}\), 초기 광자수 \(N_0=0.05\) photon/H다. \(c=29979245800\,{\rm cm\,s^{-1}}\), \(k_B=1.380649\times10^{-16}\,{\rm erg\,K^{-1}}\), \(e_{\rm V}=1.602176634\times10^{-12}\,{\rm erg/eV}\)를 유지한다.

source 상수는 모두 해당 binary64 literal의 정확한 실수값으로 옮겼다. 진단 에너지는 표기된 정확한 십진수이고, 13.7 eV anchor만 source binary64 값이다. 범위는 \([13.61,24.58]\) eV이며 차분에 사용한 모든 에너지도 source cutoff 사이에 있다. HI 열역학 threshold \(\chi=13.598434599702\) eV와 HI opacity cutoff 13.60 eV, HeI opacity cutoff 24.59 eV를 구분한다.

읽은 직접 source는 atomic_provider.rs의 Verner fit과 cutoff 부분, hhe_events.rs의 단위·threshold 상수 부분이다. 실제 initial state와 닫힌 결합식은 고정 PHYS22 report와 JSON에서 가져왔다. Generic fixture의 다른 광자 spectrum이나 단면적 표로 바꾸지 않았다.

## 3. 분석식과 별도의 직접 미분 경로

이 HI-only 열린 구간에서 source 단면적은

\[
\sigma(E)=\sigma_0(x-1)^2\,x^{P/2-5.5}\bigl(1+\sqrt{x/y_a}\bigr)^{-P}\times10^{-18}{\rm cm}^2,
\qquad x=E/E_0.
\tag{N1}
\]

\(\sigma_0=5.475\times10^4\), \(E_0=0.4298\) eV, \(y_a=32.88\), \(P=2.963\)의 source literal을 사용한다.

\[
D=E\partial_E,\quad \mathscr C=D^2+3D,\quad
\alpha=D\log\sigma,\quad \zeta=\alpha(\alpha+3)+D\alpha
\]

라 두고 \(v=\sqrt{x/y_a}\)로 쓰면

\[
\alpha=\frac{2x}{x-1}+\frac P2-\frac{11}{2}
-\frac{Pv}{2(1+v)},\qquad
D\alpha=-\frac{2x}{(x-1)^2}-\frac{Pv}{4(1+v)^2}.
\tag{N2}
\]

따라서 \(\mathscr C\sigma=\sigma\zeta\)이고,

\[
C_h(E)=\mathscr C\{\sigma(E)(E-\chi)\}
=(E-\chi)\sigma\zeta+E\sigma(2\alpha+4),
\tag{N3}
\]

\[
C_T(E)=C_h(E)-e_{\rm th}\mathscr C\sigma(E),\qquad
e_{\rm th}=\frac{3k_BT_*}{2e_{\rm V}}
=6.46299994660888\ldots\,{\rm eV}.
\tag{N4}
\]

PHYS22의 닫힌 초기시간 식에 넣으면

\[
a_{3,x}=\frac{qN_0c n_H(1-x_*)}{45}\mathscr C\sigma,\quad
a_{3,w}=\frac{qN_0c n_H(1-x_*)}{45}C_h,
\]

\[
\theta_3=\frac{qN_0c n_H(1-x_*)}{45}\frac{\mathcal A_T}{\Pi_*}C_T,
\quad
\mathcal A_T=\frac{2e_{\rm V}}{3k_B},\quad
\Pi_*=1+f+x_*+f(h_{1,*}+2h_{2,*}).
\tag{N5}
\]

차원은 HII \(a_{3,x}\)에 \({\rm s}^{-3}\), \(a_{3,w}\)에 \({\rm eV\,H^{-1}\,s^{-3}}\), \(\theta_3\)에 \({\rm K\,s^{-3}}\), He \(a_4\)에 \({\rm s}^{-4}\)다.

독립 수치 경로는 \(z=\log(E/E_{\rm eval})\)에서 원래 식 (N1), \(\sigma(E)(E-\chi)\), \(\sigma(E)(E-\chi-e_{\rm th})\)를 직접 평가한다. 각 함수의 1·2차 \(z\) 미분을 \(z_j=jh\), \(j=-4,\ldots,4\)의 9점 중심차분으로 구하고 둘을 \(f''+3f'\)로 결합한다. \(\alpha,D\alpha,\zeta\)는 이 차분 경로에 사용하지 않는다.

차분 가중치의 0–8차 moment를 정확한 Fraction으로 검사했다. \(h=10^{-5}\)와 \(h/2\)의 두 결과 \(C_h,C_{h/2}\)에서

\[
C_{\rm R}=\frac{256C_{h/2}-C_h}{255}
\tag{N6}
\]

로 8차 오차를 소거한다. Decimal precision은 110자리, 비교 허용오차는 \(10^{-42}\)다. 유한 표본에서 관측한 최대 상대 차이는 \(1.61994\times10^{-51}\)다. 이는 고정밀 수치 일치이며 rigorous derivative-error enclosure는 아니다.

독립 차분을 적용한 에너지는 기본 9개 대표점, 19 eV, 별도 구성한 반례의 평균 17.01327843259209 eV다. HeIII root의 양 끝점은 원래 단면적 차분으로 He 계수를 한 번 더 확인했다. 등에너지 혼합 반례의 17.68421052631579 eV 단일선 값은 동일한 analytic spectral 함수의 평가이며, 그 점에 별도의 차분 실행을 추가하지 않았다.

## 4. 대표점과 조건부 HeIII zero

| \(E\) [eV] | HII \(t^3\) [\({\rm s}^{-3}\)] | \(T\) \(t^3\) [\({\rm K\,s^{-3}}\)] | HeIII \(t^4\) [\({\rm s}^{-4}\)] |
|---:|---:|---:|---:|
| 13.61 | \(-4.613692813\times10^{-47}\) | \(-1.804207194\times10^{-42}\) | \(+1.945885384\times10^{-64}\) |
| 13.7 anchor | \(-4.514368738\times10^{-47}\) | \(-1.817528627\times10^{-42}\) | \(+1.814201995\times10^{-64}\) |
| 14 | \(-4.202057077\times10^{-47}\) | \(-1.855301408\times10^{-42}\) | \(+1.407223736\times10^{-64}\) |
| 16 | \(-2.685340421\times10^{-47}\) | \(-1.925203462\times10^{-42}\) | \(-3.737897975\times10^{-65}\) |
| 18 | \(-1.793104307\times10^{-47}\) | \(-1.831767069\times10^{-42}\) | \(-1.189877383\times10^{-64}\) |
| 20 | \(-1.239740141\times10^{-47}\) | \(-1.683178725\times10^{-42}\) | \(-1.539988970\times10^{-64}\) |
| 22 | \(-8.816862143\times10^{-48}\) | \(-1.523540790\times10^{-42}\) | \(-1.657230632\times10^{-64}\) |
| 24 | \(-6.418167318\times10^{-48}\) | \(-1.370657313\times10^{-42}\) | \(-1.656696721\times10^{-64}\) |
| 24.58 | \(-5.875771229\times10^{-48}\) | \(-1.328676231\times10^{-42}\) | \(-1.643819006\times10^{-64}\) |

He의 직접 photo weight는 이 에너지 영역에서 0이다. PHYS22의 \(y=(x,h_1,h_2,w)\) 좌표에 대한 수치 \(J_{\rm np}\)로

\[
a_{4,\rm HeIII}
=\frac14\left(J_{{\rm np},2,0}a_{3,x}
+J_{{\rm np},2,3}a_{3,w}\right)
\tag{N7}
\]

를 계산했다. 이는 gas IVP 없이 성립하는 국소 선형 응답식이다.

\[
J_{{\rm np},2,0}=-6.01326833811097\ldots\times10^{-17},\qquad
J_{{\rm np},2,3}=+2.52759476961633\ldots\times10^{-18}.
\]

\[
r(E)=\frac{C_h(E)}{\mathscr C\sigma(E)},\qquad
r_{\rm crit}=-\frac{J_{{\rm np},2,0}}{J_{{\rm np},2,3}}
=23.790476267775107\ldots\,{\rm eV}.
\tag{N8}
\]

\(r\)는 signed curvature 계수의 비다. 광자 에너지, excess energy, 또는 흡수 event당 열에너지와 동일시하지 않는다. \(a_{3,x}<0\)인 점에서 \(J_{{\rm np},2,3}>0\)이므로 \(r<r_{\rm crit}\)일 때 HeIII 응답은 양수, \(r>r_{\rm crit}\)일 때 음수다.

대표점에서 얻은 [14,16] eV bracket에 68회 bisection을 적용했다. 마지막 bracket은

\[
\begin{aligned}
E_{\rm lo}&=15.4336708678269396893391958609786929201845850911922752857208251953125,\\
E_{\rm hi}&=15.433670867826939689345972124556727322897131671197712421417236328125
\end{aligned}
\]

eV이며 폭은 \(6.7762635780344\times10^{-21}\) eV다. 끝점 HeIII 계수는 각각 \(+3.059378979\times10^{-85}\), \(-1.920559409\times10^{-85}\,{\rm s}^{-4}\)로 계산됐다. 차분 경로에서도 두 부호가 같았다. 차분·analytic 비교를 취소 전 두 항의 절댓값 합으로 정규화한 최대 오차는 \(6.73\times10^{-52}\)다.

이 수치 자릿수는 고정된 serialized \(J_{\rm np}\) 입력에 대한 bracket 정밀도다. 원자물리 fit의 물리 정확도, native Jacobian의 인증 오차, 전체 구간의 유일성까지 이 정밀도로 안다는 뜻은 아니다.

## 5. 광자수·에너지 정규화와 혼합의 반례

양의 초기 photon-number measure를 \(d\nu_0\)라 하면

\[
a_{3,x}[\nu_0]=\frac q{45}\int\mathscr C\lambda(E)\,d\nu_0(E),\quad
a_{3,w}[\nu_0]=\frac q{45}\int\mathscr C[\lambda(E)(E-\chi)]\,d\nu_0(E).
\tag{N9}
\]

\(D\)와 \(\mathscr C\)는 각 cohort의 energy weight에 작용한다. Spectrum이나 measure 자체를 미분하지 않는다. 본 진단의 support는 cutoff를 피하므로 boundary-distribution 항을 포함하지 않는다.

고정 광자수에서는 \(d\nu_0=N_0\,dP_N\), \(\int dP_N=1\)로 쓴다. 고정 총 에너지 \(U_0\)와 normalized energy measure \(dP_U\)를 쓰면

\[
d\nu_0(E)=\frac{U_0}{E}\,dP_U(E),\qquad \int dP_U=1 .
\tag{N10}
\]

그러므로 같은 “반반”도 광자수에 대한 반반과 에너지에 대한 반반은 서로 다른 measure다. 정규화 조건을 바꿀 때는 그 변화까지 계산해야 한다.

### 5.1 같은 광자수를 갖는 14/24 eV의 반반 혼합

\[
d\nu_0=\frac{N_0}{2}(\delta_{14}+\delta_{24}),\qquad
\bar E=19\ {\rm eV}.
\]

이 혼합과 \(N_0\delta_{19}\)는 총 광자수와 총 에너지가 모두 같다.

| 계수 | 두 선 혼합 | 19 eV 단일선 |
|---|---:|---:|
| HII \(t^3\) [\({\rm s}^{-3}\)] | \(-2.421936904\times10^{-47}\) | \(-1.485173697\times10^{-47}\) |
| \(w\) \(t^3\) [\({\rm eV\,H^{-1}\,s^{-3}}\)] | \(-5.959302754\times10^{-46}\) | \(-5.756335885\times10^{-46}\) |
| \(T\) \(t^3\) [\({\rm K\,s^{-3}}\)] | \(-1.612979360\times10^{-42}\) | \(-1.760718114\times10^{-42}\) |
| HeIII \(t^4\) [\({\rm s}^{-4}\)] | \(-1.247364921\times10^{-65}\) | \(-1.404734127\times10^{-64}\) |

단일선 대비 HII 계수의 절댓값은 약 63.0743% 크고 온도 계수의 절댓값은 약 8.39082% 작다. 이 차이는 photon number와 mean energy를 맞추는 것만으로 응답을 결정할 수 없음을 보인다.

### 5.2 같은 에너지를 배분한 간단한 부호 반례

기준 총 에너지를 실제 production 초기 광자의 \(U_0=N_0E_b\), \(E_b=\text{binary64}(13.7)\)로 두고

\[
dP_U=\tfrac12\delta_{14}+\tfrac12\delta_{24},\qquad
d\nu_0=\frac{U_0}{28}\delta_{14}+\frac{U_0}{48}\delta_{24}.
\tag{N11}
\]

로 정의한다. 광자수 weight의 비는 \(12:7\)이며

\[
N_{\rm mix}=\frac{19U_0}{336}
\simeq0.03873511904761905\ {\rm photon/H},\qquad
\bar E=\frac{U_0}{N_{\rm mix}}=\frac{336}{19}
=17.68421052631579\ldots\ {\rm eV}.
\tag{N12}
\]

이때 비교할 단일선은 \(N_{\rm mix}\delta_{\bar E}\)다. 양쪽이 같은 \(N_{\rm mix}\)와 \(U_0\)를 가지며, 고정 광자수 family의 \(N_0=0.05\)와는 별도 정규화다.

| 계수 | 등 에너지 14/24 eV 혼합 | 같은 \(N,U\) 단일선 |
|---|---:|---:|
| HII \(t^3\) [\({\rm s}^{-3}\)] | \(-2.239191691\times10^{-47}\) | \(-1.476872617\times10^{-47}\) |
| \(T\) \(t^3\) [\({\rm K\,s^{-3}}\)] | \(-1.298980916\times10^{-42}\) | \(-1.434680504\times10^{-42}\) |
| HeIII \(t^4\) [\({\rm s}^{-4}\)] | \(+2.156856153\times10^{-65}\) | \(-8.525853862\times10^{-65}\) |

HII와 온도의 계수는 둘 다 음수지만 HeIII의 부호는 반대다. 이 반례는 에너지를 단순 평균한 단일선 closure의 제한을 보이며, production source 변경을 제안하거나 유한시간 history의 부호를 주장하는 결과는 아니다.

JSON에는 고정 \(N_0\) family에서도 같은 현상을 보이는 구성 예를 보관했다. 14 eV의 photon fraction \(p=0.6986721567407912\ldots\), 나머지를 24 eV에 두면 평균은 17.01327843259209 eV다. 혼합 HeIII \(t^4\)는 \(+4.839791932\times10^{-65}\), matched 단일선은 \(-8.675716405\times10^{-65}\,{\rm s}^{-4}\)다. 이 추가 구성은 혼합의 HeIII zero fraction과 평균 단일선의 zero fraction 사이의 중간값을 골랐으며 대규모 spectrum 탐색을 하지 않았다.

### 5.3 왜 광자 평균 에너지로는 충분하지 않은가

어떤 support에서 \(\mathscr C\lambda<0\)가 별도로 확립되어 있다고 하자. 그러면

\[
R_\nu=
\frac{\int\mathscr C[\lambda(E)(E-\chi)]\,d\nu_0}
{\int\mathscr C\lambda(E)\,d\nu_0}
=\frac{\int[-\mathscr C\lambda(E)]r(E)\,d\nu_0}
{\int[-\mathscr C\lambda(E)]\,d\nu_0}
\tag{N13}
\]

는 양의 curvature weight로 평균한 \(r\)다. 광자수로 평균한 \(E\)와 다른 양이다.

\[
\theta_3=\frac{\mathcal A_T}{\Pi_*}a_{3,x}(R_\nu-e_{\rm th}),\qquad
a_{4,\rm HeIII}=\frac14a_{3,x}J_{{\rm np},2,3}(R_\nu-r_{\rm crit}).
\tag{N14}
\]

따라서 적절한 초기 spectral 정보는 \(\int\mathscr C\lambda\,d\nu_0\)와 \(\int\mathscr C[\lambda(E)(E-\chi)]\,d\nu_0\)의 두 signed response moment다. 이 대수적 충분성은 해당 차수와 HI-only 영역에 한정되며 높은 시간 차수나 전체 photon history의 closure를 보장하지 않는다.

## 6. 실제 실행과 종료

실행 프로그램은 spectral_response.py이며 Python 3.12.14와 표준 라이브러리만 사용한다. 신규 경로에 결과를 쓰도록 실행한다.

    python3 -B contributions/numerics/spectral_response.py --output NEW_RESULT.json

기존 결과 파일을 덮어쓰지 않으며 계약·상속 JSON hash가 다르면 중단한다. 실제 최초 과학 실행은 2026-10-10 13:13:11.912738 UTC에 시작해 13:13:12.161955 UTC에 끝났고, 측정 elapsed time은 0.247661825초, exit code는 0이었다. 이 시간은 해당 경량 진단의 관측값이며 performance benchmark 주장은 아니다.

| 새 검산 | 항목 수 |
|---|---:|
| 정확한 stencil moment 집계 | 1 |
| 세 spectral curvature의 독립 직접 차분 | 33 |
| 입자수를 포함한 온도 identity | 11 |
| 단 한 에너지의 PHYS22 anchor 연결 | 5 |
| HeIII bracket 폭·부호와 끝점 직접 차분 | 5 |
| Photon number·mean·energy 정규화 | 3 |
| 혼합의 계수 선형성 | 5 |
| 구성한 같은 평균 spectrum의 HeIII 부호 반례와 H/T 부호 | 2 |
| 합계 | 65/65 PASS |

최초 환경 probe에서 기본 Python과 primary Python 경로의 mpmath import가 실패했다. 두 경로는 현재 관측상 같은 실행기로 resolve된다. 이를 과학식·구현의 실패로 분류하지 않았다. 의존성을 설치하지 않고 표준 라이브러리 차분 경로로 진행했으며 원인과 실제 오류를 EXECUTION.json에 보관했다. 과학 실행의 첫 실패는 없다.

SPECTRAL_RESPONSE.json은 계산값과 65개 판정, EXECUTION.json은 실제 명령·시간·exit code·hash, stdout.log와 stderr.log는 원 출력이다. DEPENDENCIES.json은 입력과 부분 source 읽기의 identity를 보관한다.

수치 sign scan을 정리로 승격하지 않고, native·gas IVP·old-suite 실행은 각각 0회로 종료한다. Physical=HOLD이며 source/default/runtime mutation은 없다. 유한시간 remainder, threshold crossing, Einstein backreaction 및 다른 원자물리 lane은 이 기여의 범위 밖이다.
