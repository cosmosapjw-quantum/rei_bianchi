# BASS_HE THEORY07 — predictor 튜브와 이전 상태 family의 구성

연구 단위: `HERE_RUX03_PREDICTOR_TUBE_AND_REANCHORED_FAMILY_07`  
경로: `physmath-research-loop` 1.0.0, THEORY R1–R10  
부모 이론: BASS_HE PR34, `3932669f7904f7f68f2f07dced4cf1da9d472480`  
고정된 물리 소스: rei_bianchi PR114, `a5c958c414dea41216b445c05f58df837f05cacb`  
판정 권위: `review/DECISION.json` 및 `dossier/CLOSEOUT.json`  
작성일: 2026-10-13

## 1. 이번 루프에서 확보한 결과

전체 FT03 CI3/RR3/DR2와 광흡수를 유지한 7변수 이동 기체의 implicit stage에 대해, 실제 anchor 반응률로 만든 유리수 predictor와 두 개의 물리적 튜브를 구성했다. 새 인증 구간은

\[
0\le h\le10^9\,\mathrm s.
\]

THEORY06의 \(5\times10^8\,\mathrm s\)에서 두 배로 늘어났다. 새 끝점에서는 종전 충분조건에 들어간 \(HB\)가 \(1.6060877754793128>1\)이므로, 기존 중심의 unit cube 자체를 self-map으로 만드는 추정으로는 이 구간을 확보할 수 없다. 이번에는 반응에 따른 이동량을 predictor에 먼저 담고, 그 주위의 작은 잔차를 제어하여 해를 구성했다.

이 결과는 이전 기체 상태도 함께 변화시키는 compact family에 균일하다. 기존 고정 아핀 좌표에서 이전 상태를 \(\xi\)로 쓰면

\[
F(X,h;\xi)=X-\xi-hG_h(X),\qquad
\|\xi\|_\infty\le\eta=\frac1{100}.
\tag{1}
\]

모든 \(\mu\in[10^9,1.5\times10^9]\,\mathrm{eV/H}\)에 대해 이 구간에 같은 잔차의 유일한 \(C^1\) 해 가지가 있고, 각 고정 \(\xi\)의 가지는 \(X(0;\xi)=\xi\)에서 출발한다. 두 튜브는 \(h=5\times10^8\,\mathrm s\)에서 동일한 predictor를 사용하며 작은 endpoint box가 큰 endpoint box에 들어가므로 같은 해를 연결한다.

| 실제 인증량 | 첫 번째 튜브 | 두 번째 튜브 |
|---|---:|---:|
| \(h\) 전 구간, s | \([0,5\times10^8]\) | \([5\times10^8,10^9]\) |
| 선택한 predictor 상계 \(P_j\) | 0.4 | 0.77 |
| 반지름 \(\rho_j\) | 0.02 | 0.10 |
| 전체 Jacobian 수축계수 상계 \(q_j\) | 0.023012093111 | 0.046670186416 |
| 최소 self-map 여유 | 0.01032621961478 | 0.0601894501334 |
| 물리 cube까지의 여유 | 0.57 | 0.12 |
| predictor에서 실제 근까지의 오차 상계 | 0.009430555340586003 | 0.03686398004577188 |

모든 판정 부등식은 유리수 연산으로 확인했다. 표의 유한소수로 끝나는 여유와 수축계수는 바깥쪽으로 올림한 정확한 유리수 값이다. 실제 실행의 14개 named groups와 두 튜브의 14개 성분별 self-map 부등식은 서로 다른 집계다.

이전 상태에 대한 민감도는 더 작은 공통 cube 도함수 상계로 제어된다.

\[
q_Q=0.045092412438,\qquad
\|D_\xi X\|_\infty\le\frac1{1-q_Q}<1.05,
\]

\[
\|D_\xi(X-\xi)\|_\infty\le\frac{q_Q}{1-q_Q}<0.05.
\tag{2}
\]

또한 새 에너지 anchor를 각 이전 상태의 기체 속도로 잡는 유한 아핀 변환을 유도했다. 중심을 같은 이전 상태에 두면

\[
X_b=P(\xi)(X_a-\xi),\qquad F_b=PF_a,
\tag{3}
\]

이며, \(\|P-I\|_\infty<1/3000\), \(\|DP\|<1/30\)로 제어된다. \(DP\)를 포함한 민감도와 움직이는 anchor의 공변 전류 변분을 후반부에서 연결한다.

## 2. 유지한 물리 가정과 근거

이번 구성의 물리 모델, rate fit, 에너지·운동량 소유 관계는 채택된 THEORY06와 같다. 새 작업의 첫 읽기에서 PR34와 receiver PR114의 정확한 head가 그대로임을 확인했다. 근거 재사용은 `dossier/REUSE_RECORD.json`과 `source_map/CURRENT_SOURCE.json`에 입력 hash와 적용 범위로 남겼다.

| 항목 | 고정한 정의 또는 범위 | 이번 사용 방식 |
|---|---|---|
| 계량 | \((-+++)\) | 공변 전류와 anchor 투영의 부호 |
| 상수 | \(c,\hbar,k_B,\epsilon_{\rm eV}\) 명시 | 단위가 있는 식 유지 |
| 밀도와 좌표계 | 고정 Eulerian \(D=\gamma n_H=10^{-3}\,\mathrm{cm^{-3}}\), 고정 tetrad | 한 stage의 보존 변수와 lab time 정의 |
| 헬륨 함량 | \(f=2/25\) | abundance closure |
| 질량 에너지 | \(\mu\in[10^9,1.5\times10^9]\,\mathrm{eV/H}\) | 각 stage에서 고정, certificate는 family에 균일 |
| 공통 anchor | \(T_*=50000\,\mathrm K\), \(\beta_*=(0,0,41/841)\), \(\gamma_*=841/840\) | predictor 계수와 고정 기준 좌표 |
| 원자 과정 | CI 3개, RR 3개, DR 2개, primary photoabsorption | 모든 source와 derivative에 유지 |
| escape | 소스가 정한 Case A captured kinetic와 binding escape | 열 및 운동량 전류에 동일 사건으로 반영 |
| 광자 입력 | \((23,\pm e_x),(35,\pm e_y),(70,\pm e_z)\) eV, \(p_q^-=0.01\), 외부 source 0 | 이전 기체를 바꾸어도 고정 |
| 제외된 과정 | CR, RCT, HH | 부모 모델의 과정 선택 유지 |
| 종별 속도 | 공통 gas velocity | relative-species-tilt 의무와 분리 |

구성은 부모의 7차원 physical unit cube \(Q=[-1,1]^7\)를 사용한다. 이 cube 전역에서 primitive inverse가 물리적이며, 온도·속도 도함수와 Verner cutoff cell이 제어된다는 부모 결과를 재사용한다. rate cap과 primitive cap의 성공한 계산은 다시 실행하지 않았다. 새 anchor의 좁은 coefficient enclosure, 새 predictor, 새 parameter interval의 튜브 부등식, 새 anchor 변분만 계산했다.

이론의 기준 변수는

\[
e=\frac{E}{D\epsilon_{\rm eV}},\qquad
m=\frac{M}{D\epsilon_{\rm eV}},\qquad
M=c\times\hbox{물리적 운동량 밀도},
\]

\[
a=\mu+B(\zeta),\qquad
B=\chi_0\zeta_1+\chi_1\zeta_2+(\chi_1+\chi_2)\zeta_3,
\]

\[
t_a=\gamma_a(e-\beta_a\cdot m)-a.
\tag{4}
\]

\(\zeta=(n_{\rm HII},n_{\rm HeII},n_{\rm HeIII})/n_H\)이고, 기준 상태는 \((1/2,1/50,1/50)\)이다. 고정 scale은

\[
s_\zeta=10^{-3},\qquad s_t=\frac14\,\mathrm{eV/H},\qquad
s_m=a_*10^{-6}\,\mathrm{eV/H}.
\tag{5}
\]

에너지의 큰 질량 baseline을 직접 차분하는 대신 \(t_a\)와 작은 아핀 증분으로 계산한다. \(s_m\)는 실제 \(\mu\)에 의존하는 값을 보존한다. 경계를 세울 때만 \(s_m\ge1000\,\mathrm{eV/H}\)라는 균일 하한을 사용했다.

부모 고정 문서의 단위 표기 다섯 곳에는 `open brace + LF + m` 조각이 남아 있었음을 좁게 확인했다. 해당 값의 단위는 photon table의 eV 세 곳, \(L_T=1400\,\mathrm K\), \(L_w=0.26\,\mathrm{eV/H}\)이다. 새 문서에 올바른 표기를 사용하고 정오 기록을 남겼다. 부모의 고정된 bytes, 수식의 수치값, 실제 WL 계산과 채택 판정은 유지했다.

## 3. 전체 source에서 유리수 predictor를 구성한 방법

### 3.1. 정확한 anchor의 반응률 구간

기준 상태의 electron closure와 사건 prefactor는

\[
e_{H,*}=\frac{14}{25},\qquad
\alpha_*=D\gamma_*^{-2}e_{H,*}.
\]

Doppler factor는 처음 네 ray에서 \(841/840\), 마지막 두 ray에서 \(20/21,21/20\)이다. 따라서 gas-frame photon energy는 정확히

\[
E'_q=\left(\frac{19343}{840},\frac{19343}{840},\frac{841}{24},\frac{841}{24},\frac{200}{3},\frac{147}{2}\right)\,\mathrm{eV}.
\tag{6}
\]

HI 여섯 개, HeI 네 개, HeII 두 개로 총 12개의 active Verner cross section을 구간화했다. threshold 바깥의 항은 소스 정의에 따라 정확히 0이다. atomic rate와 captured kinetic coefficient도 같은 anchor에서 구간화했다.

유리수 거듭제곱의 근사값은 먼저 고정 격자의 후보 구간을 찾는 데 사용하고, 최종 포함은 정확한 정수·유리수 거듭제곱 부등식으로 확인했다. 지수 함수는 양의 Taylor 합과 나머지의 기하급수 상계를 이용해 포함했다. 마지막으로 원자 계수는 \(10^{-30}\), kinetic 계수는 \(10^{-40}\), 단면적은 \(10^{-34}\) 격자에서 바깥쪽으로 구간을 넓혔다. 최종 endpoint는 정수 문자열과 격자 지수로 보존하여 JSON의 부동소수점 변환을 피했다.

| 계수 종류, \(\mathrm{cm^3/s}\) | 첫 번째 | 두 번째 | 세 번째 |
|---|---:|---:|---:|
| CI midpoint | \(6.206967333470373\times10^{-10}\) | \(1.800470878674231\times10^{-11}\) | \(4.479061309971467\times10^{-15}\) |
| RR midpoint | \(1.265627389380609\times10^{-13}\) | \(1.474587980476599\times10^{-13}\) | \(7.321868393221612\times10^{-13}\) |
| DR midpoint | \(1.425548101548745\times10^{-14}\) | \(6.526687510134745\times10^{-16}\) | 두 channel |

이 값들은 `ANCHOR_RATE_RESULT.json`의 정확한 구간 midpoint를 보여주는 표시값이다. 해당 실행은 10/10 named groups를 통과했고, 그 안에서 rational-power bracket 112개와 exponential enclosure 5개를 확인했다.

### 3.2. 광자 제거 분모를 유지한 predictor

각 ray에서

\[
\lambda_{iq}=cD y_i(1-\beta\cdot e_q)\sigma_i(E'_q),\quad
\Lambda_q=\sum_i\lambda_{iq},\quad
r^\gamma_{iq}(X,h)=\frac{\lambda_{iq}(X)p_q^-}{1+h\Lambda_q(X)}.
\tag{7}
\]

유리수 midpoint 계수에 hat을 붙이면 predictor는

\[
p(h)=h\widehat G_h(0),\qquad \overline X(h,\xi)=\xi+p(h).
\tag{8}
\]

단순히 \(hG_0(0)\)를 사용하는 대신, 식 (7)의 \(1+h\widehat\Lambda_q\) 분모를 유지했다. 보존된 정확한 compact 표현은

\[
p_{\{1,2,3,4,7\}}(h)
=h\left[a_p+B_p(1+h\widehat\Lambda)^{-1}\right],
\tag{9}
\]

이며 7번 행에는 추가로 실제 \(a_*(\mu)\)로 나누는 인자가 있다. \(a_p,B_p,\widehat\Lambda\)의 모든 성분은 `ANCHOR_RATE_RESULT.json`의 유리수 문자열이다. transverse 두 행은 정확한 opposite-ray parity로 0이다.

화학 source는 HI/HeI/HeII edge incidence를 사용한다. thermal source는 anchor에서 정확히 \(\Gamma_*=1\)이므로

\[
S_t(0,h)=\sum_{iq}(E'_q-\chi_i)r^\gamma_{iq}
-\sum_i\chi_iR_{CI,i}-K.
\tag{10}
\]

운동량 source에는

\[
S_m(0,h)=\sum_{iq}E_qe_qr^\gamma_{iq}
-\gamma_*\beta_*(K+B_{esc})
\tag{11}
\]

가 그대로 들어간다. anchor에서 열 식이 간단해지는 사실은 일반 endpoint에서 escape 항이나 그 도함수를 없애는 근거가 되지 않는다. 튜브에서는 부모의 전체 source derivative를 사용한다.

### 3.3. 계수 구간 오차를 잔차로 운반

계수 구간 halfwidth를 \(e_c\)라 하자. 비음이 아닌 opacity에 대해 직접 두 분수를 빼면

\[
|r^\gamma_{iq}(0,h)-\widehat r^\gamma_{iq}(h)|
\le p_q^-\left(e_{\lambda,iq}+H\widehat\lambda_{iq}e_{\Lambda,q}\right),
\quad0\le h\le H.
\tag{12}
\]

원자 사건·kinetic·binding halfwidth도 exact prefactor로 선형 전파했다. 전체 7행에 대한 \(\varepsilon(H)\)를 구성하고 실제 anchor 계산에서 \(H_2\varepsilon(H_2)\)를 바깥쪽으로 올림했다. 그러므로 저장된 displacement cap을 \(H_2\)로 나눈 값은 \(h=0\)을 포함한 전체 구간의 source-defect bound다. 단순한 \(h\)-별 displacement estimate를 \(H_2\)로 나누는 추론을 사용하지 않았다.

최종적으로

\[
\sup_{0\le h\le10^9}\|p(h)\|_\infty
\le0.76110187134,
\]

\[
\sup_{0\le h\le10^9}\|hG_h(0)-p(h)\|_\infty
\le7.84285288\times10^{-17}.
\tag{13}
\]

후자의 작은 값은 계수 구간화의 정확도다. 실제 endpoint와 predictor 사이 오차는 source가 endpoint에서 변하기 때문에 더 크며, 다음 튜브 부등식으로 별도로 제어한다.

## 4. 두 튜브를 실제로 닫은 증명

### 4.1. 도함수 근거의 재사용 범위

부모에서 확보한 전체 source의 행별 경계는

\[
\|\operatorname{row}_iD_XG_h(X)\|_1
\le\ell_i(H)=\ell_i^{(0)}+H\ell_i^{(1)},\quad
X\in Q,\quad0\le h\le H.
\tag{14}
\]

이 선형 \(H\) 의존성은 제거된 광자 분모를 미분하여 얻었다. 그 증명은 \(1+h\Lambda_q\ge1\)을 사용하므로 동일한 물리 cube 안에서 각 유한 \(H\ge0\)에 적용된다. 이전에 숫자로 평가한 \(H_0\)가 식 (14)의 적용 한계인 것은 아니다. 이번에는 저장된 \(\ell^{(0)},\ell^{(1)}\)을 그대로 사용하여 \(H_2=10^9\)에서 새 판정을 했다.

### 4.2. 고정된 비자명 전처리자

anchor에서 \(T,\gamma,\beta\)를 고정하되, abundance target, electron closure와 광자 제거 분모의 abundance 미분을 유지한 chemical 3×3 행렬 \(J_j^{fr}\)를 구성했다. 각 slab의 중심 \(h_{c,1}=2.5\times10^8\), \(h_{c,2}=7.5\times10^8\)에서

\[
A_j=\operatorname{diag}\left((I_3-h_{c,j}J_j^{fr})^{-1},I_4\right).
\tag{15}
\]

역행렬의 존재와 정확한 역대입은 새 Wolfram 계산으로 확인했다. 이는 실제 전체 Jacobian의 특정 블록을 정확히 계산했다는 주장이 아니다. 효율적인 고정 전처리자를 선택하는 구성이고, 인증은 실제 primitive·thermal·momentum 의존성을 포함한 식 (14)의 전체 7행으로 수행한다.

### 4.3. 전체 구간의 self-map과 수축

튜브를

\[
\mathcal T_j(h,\xi)=
\{X:\|X-[\xi+p(h)]\|_\infty\le\rho_j\}
\tag{16}
\]

로 둔다. \(\eta+P_j+\rho_j<1\)이므로 모든 튜브가 물리 cube에 들어간다. predictor 잔차는 평균값 적분과 식 (12), (14)로

\[
|F_i(\overline X,h;\xi)|
\le R_{j,i}=H_j\left[\varepsilon_i+\ell_i(H_j)(\eta+P_j)\right].
\tag{17}
\]

고정 전처리자에 대한 두 벡터는

\[
Y_j=|A_j|R_j,
\qquad
z_j=|I-A_j|\mathbf1+H_j|A_j|\ell(H_j).
\tag{18}
\]

\(z_j\)는 \(I-A_jF_X\)의 전체 Jacobian 행 절대값 합을 제어한다. 성분별 행렬 원소의 경계를 가장하지 않는다. 모든 성분에 같은 반지름을 쓰는 \(\ell^\infty\) 튜브에서는 이 행별 norm이 충분하다.

실제로 각 \(i=1,\ldots,7\)에서

\[
Y_{j,i}+\rho_jz_{j,i}<\rho_j,\qquad
q_j=\max_i z_{j,i}<1
\tag{19}
\]

을 확인했다. 따라서 \(X\mapsto X-A_jF(X,h;\xi)\)가 해당 closed tube를 strict self-map으로 보내는 contraction이고, 각 입력마다 한 근을 갖는다. \(A_j\)가 가역이므로 이 fixed point는 원래 잔차의 영점이다.

모든 \(h\)를 covering하는 근거는 \(h/(1+h\widehat\Lambda_q)\)의 단조성과 전구간 도함수 경계다. sampling point를 늘려서 전구간 결론을 대체하지 않았다. 입력 WL과 완전 수신된 raw/normalized 결과는 `TUBE_CERTIFICATE_CHECK.wl`과 `evidence/TUBE_CERTIFICATE_*`에 보존했다.

### 4.4. 접합점과 전체 cube의 유일성

접합점에서 두 predictor가 같고 \(\rho_1<\rho_2\)이므로

\[
\mathcal T_1(5\times10^8,\xi)
\subset\mathcal T_2(5\times10^8,\xi).
\tag{20}
\]

첫 근이 두 번째 튜브의 유일성 영역에 들어가서 동일한 근이 된다. 이는 동일한 \(\xi\)별 포함 관계이며, 서로 다른 이전 상태의 box union이 겹친다는 조건으로 바꾸지 않는다.

더 나아가 식 (14)로 전체 cube에서 \(\|hDG_h\|_\infty\le q_Q<1\)이다. 두 근 \(X,Y\in Q\)가 있으면

\[
\|X-Y\|_\infty\le q_Q\|X-Y\|_\infty
\]

이므로 같아야 한다. 해의 존재는 predictor 튜브로 확보했고, 유일성은 더 넓은 convex cube로 확장했다. strict physical inclusion과 가역 Jacobian이 있으므로 실수 유한차원 implicit-function theorem으로 공동 \(C^1\)성을 얻는다. 이는 parameter-dependent contractions의 표준 정리를 현재 잔차에 적용한 것이며, Glöckner 원전의 Definition 4.4, Proposition 4.5와 Theorem 4.7을 대조했다.[L1]

## 5. 이전 상태 family와 오차 전파

기체 이전 상태의 \(\xi\)만 변하고 \(D,f,\mu,p_q^-\)가 각 문제에서 고정되어 있으므로, 고정 chart에서는 source의 직접적인 \(\xi\) 의존성이 없다. 식 (1)을 미분하면

\[
J=I-hD_XG_h,\qquad J D_\xi X=I,
\]

\[
D_\xi X=J^{-1},\qquad
D_\xi(X-\xi)=J^{-1}-I=J^{-1}hD_XG_h.
\tag{21}
\]

이 식은 실제 source가 이전 gas data를 별도 argument로 사용하지 않는다는 확인에 의존한다. 이전 photon inventory를 함께 바꾸는 경우에는 \(F_\xi\)에 추가 항이 필요하다.

새 공통 상계는 정확히

\[
q_Q=\frac{22546206219}{500000000000},\quad
\|J^{-1}\|_\infty\le\frac{500000000000}{477453793781},\quad
\|D_\xi(X-\xi)\|_\infty\le\frac{22546206219}{477453793781}.
\tag{22}
\]

\(\eta=0.01\)의 입력 family에서 이전 abundance 변화는 각 성분 \(10^{-5}\) 이하이고, primitive Lipschitz 결과에 따라 이전 온도 변화는 14 K 이하, 이전 속도 변화는 \(3\times10^{-8}\) 이하이다. 이는 물리적으로 비어 있지 않은 일곱 변수 입력 family다.

근사 이전 상태 \(\widetilde\xi\)와 trial endpoint \(\widetilde X\in Q\)에 대해 실제 잔차를

\[
r=\widetilde X-\widetilde\xi-hG_h(\widetilde X)
\]

라 쓰면, 원래 근의 식을 빼서

\[
\|X(h;\xi)-\widetilde X\|_\infty
\le\frac{\|\xi-\widetilde\xi\|_\infty+\|r\|_\infty}{1-q_Q}.
\tag{23}
\]

따라서 입력의 오차와 실제 잔차의 오차를 한 번에 운반할 수 있다. 부동소수점 잔차 \(\widetilde r\)를 사용할 때는 실제 오차 enclosure \(\eta_F\)를 포함하여 \(\|r\|\le\|\widetilde r\|+\eta_F\)를 넣어야 한다. primitive observable의 오차는 그 Lipschitz 상수를 곱해서 얻는다.

한 튜브 안의 trial point에는 보다 직접적으로

\[
\|X-\widetilde X\|_\infty
\le\frac{\|A_jF(\widetilde X,h;\xi)\|_\infty}{1-q_j}
\tag{24}
\]

가 성립한다. 실제 residual·행렬 곱·primitive inverse의 반올림 항을 보존하는 일이 다음 코딩 adapter의 핵심 의무다.

## 6. 이전 상태를 기준으로 한 유한 아핀 재좌표화

### 6.1. 같은 물리 상태의 두 에너지 anchor

기준 anchor \(a\)와 새 anchor \(b\)를 사용한 식 (4)를 직접 연결하면

\[
t_b=\frac{\gamma_b}{\gamma_a}t_a
+\left(\frac{\gamma_b}{\gamma_a}-1\right)a
+\gamma_b(\beta_a-\beta_b)\cdot m.
\tag{25}
\]

\(B(\zeta)\)가 아핀이므로 \(z=(\zeta,t,m)\)의 변환도 아핀이다. lab momentum, Eulerian density와 시간 foliation은 이 계산에서 같고, energy coordinate가 바뀐다. 각 이전 상태에서 \(u_b=u_{gas}(\xi)\)로 잡고, 새 좌표의 중심을 그 동일한 이전 상태로 선택하면 큰 상수항이 정확히 상쇄되어 식 (3)이 나온다.

새 source와 잔차는

\[
G_{b,h}(X_b;\xi)=P(\xi)G_h(\xi+P(\xi)^{-1}X_b),
\]

\[
F_b(X_b,h;\xi)=X_b-hG_{b,h}(X_b;\xi)=P(\xi)F_a(X_a,h;\xi).
\tag{26}
\]

원래 BE 보존 잔차의 영점 집합을 정확히 옮긴 것이다. 이 등가성은 큰 \(e\)를 복원한 뒤 다시 빼는 수치 계산법을 요구하지 않는다. 작은 증분 \(X_a-\xi\)에 \(P\)를 적용하면 된다.

### 6.2. 상수와 미분항

고정된 동일 scale을 쓰면 \(P\)의 thermal 한 행만 바뀐다. \(\alpha=\gamma_b/\gamma_a\), \(b_\chi=(\chi_0,\chi_1,\chi_1+\chi_2)\)라 두면

\[
P_{t,\zeta}=(\alpha-1)\frac{s_\zeta}{s_t}b_\chi^T,
\quad P_{t,t}=\alpha,
\quad P_{t,m}=\frac{s_m}{s_t}\gamma_b(\beta_a-\beta_b)^T.
\tag{27}
\]

부모 primitive derivative를 이용하여 실제 행 norm을 합하면

\[
\|DP\|<\frac1{30},\quad
\|P-I\|_\infty<\frac1{3000},\quad
\|P\|_\infty\le\frac{3001}{3000},\quad
\|P^{-1}\|_\infty\le\frac{3000}{2999}.
\tag{28}
\]

변분을 취할 때는 반드시

\[
D_\xi X_b[v]=DP[v](X_a-\xi)+P(D_\xi X_a[v]-v)
\tag{29}
\]

를 사용한다. 움직이는 좌표라는 이유로 \(DP\) 항을 버릴 수 없다. 식 (22), (28)과 \(\|X_a-\xi\|\le P_2+\rho_2=0.87\)를 대입하면 새 중심 좌표의 old-state 민감도가 \(0.07623749588932581<2/25\)로 제어된다. `FAMILY_VARIATIONS_RESULT.json`에서 이 상계와 새 infinity norm의 수축률 \(1/20\) 미만, 역 Jacobian norm \(21/20\) 미만을 실제 유리수로 확인했다.

고정 \(\xi\)에서 Jacobian은

\[
J_b=PJ_aP^{-1}.
\tag{30}
\]

pullback norm \(\|v_b\|_{a,\xi}=\|P^{-1}v_b\|_\infty\)에서는 원래 수축계수가 그대로 유지된다. 보통 infinity norm을 사용하면 \(\|P\|\|P^{-1}\|\) 인자를 포함한다. 새 \(1/20\) 상계는 \(P(hG_X)P^{-1}\)에 대한 것으로, 앞의 preconditioned corrector 상계 \(q_j\)와 구별한다. 실제 튜브의 self-map은 affine image로 옮기고 corrector도 \(A_{b,j}=P A_jP^{-1}\)로 함께 옮기면 정확한 conjugacy가 된다. transformed box를 axis-aligned hull로 대체하는 구현에는 그 hull 전체가 들어갈 물리 정의역과 도함수 경계가 필요하다. exact zero-set equivalence와 특정 norm에서의 interval certificate는 각각 필요한 조건을 갖추어 사용한다. Deuflhard–Heindl의 affine-invariant Newton 문헌을 이 구분에 맞추어 대조했다.[L2]

추후 \(P=P(h,\xi)\)인 coordinate choice를 쓰면 branch derivative에는 \(P_h(X_a-\xi)\)가 더해진다. 이번 두 튜브에서는 각 이전 상태의 chart와 scale을 \(h\)에 대해 고정한다.

## 7. 공변 moving-anchor 항과 xAct의 역할

가스 stress tensor와 Eulerian energy current를

\[
T^{ab}=(\rho+p)u^au^b+pg^{ab},\qquad
C^a=-T^{ab}n_b=(\rho+p)\gamma u^a-pn^a
\tag{31}
\]

로 쓴다. 에너지 anchor의 투영은

\[
\Psi_b=-u_{b,a}C^a.
\]

anchor와 gas current가 함께 변하면

\[
\delta\Psi_b=-(\delta u_b)\cdot C-u_b\cdot\delta C.
\tag{32}
\]

이전 상태와 anchor가 일치하는 점에서 정규화 \(u\cdot\delta u=0\)를 쓰면 첫 항은 \(-p\,\delta\gamma\)이고, 고정 anchor의 변분과 합쳐서

\[
\delta\Psi_b=\gamma\,\delta\rho+\rho\,\delta\gamma.
\]

고정 \(D=\gamma n_H\), \(\rho=n_H\epsilon_{\rm eV}(a+w)\)에서는

\[
t_b(\mathrm{old})=w(\mathrm{old}),\qquad
\delta t_b(\mathrm{old})=\delta w.
\tag{33}
\]

이를 부모의 고정 anchor 관계 \(\delta t_a=\delta w+(2/3)(w/\gamma)\delta\gamma\)와 구별해야 한다. 총미분의 대상이 달라지는 데 따른 정확한 추가항이다.

두 변분의 mixed term도

\[
\delta_1\delta_2\Psi_b
=-(\delta_1\delta_2u_b)\cdot C
-(\delta_1u_b)\cdot\delta_2C
-(\delta_2u_b)\cdot\delta_1C
-u_b\cdot\delta_1\delta_2C
\tag{34}
\]

처럼 네 항으로 유지된다. 광자 current와 kinetic/binding escape current의 mixed anchor/rate·gas 변분을 이 식과 연결했다. 실제 xAct 계산은 이러한 새 identity 9개 그룹, 그 안의 tensor 잔차 12개를 모두 0으로 확인했다. xTensor 1.3.0을 Wolfram 15.0.1에서 로드했고, 공식 xAct archive의 SHA256 guard `7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be`가 일치했다. 부모의 성공 사례는 재실행하지 않았다.

실제 실행과 채택 상태는 아래의 근거 표 및 `evidence/EXECUTION_RECORD.json`에 모은다.


## 8. 인증이 주는 물리적·수치적 정보

새 끝점 \(h=10^9\,\mathrm s\)에서 predictor의 화학·열 좌표는

\[
p_{1:4}\simeq(0.7611018713393163,\ 0.1099592289862403,
\ 0.009590372389136660,\ 0.03110852545258848).
\tag{35}
\]

이는 rate enclosure로 구성한 predictor 값이며, 근을 수치적으로 푼 값은 아니다. 실제 근은 그 주위의 인증된 범위에 존재한다. 예를 들어 모든 허용된 이전 gas input에서 HII fraction은

\[
\left|\zeta_{HII}^+-\left(\zeta_{HII}^-+
10^{-3}p_1(10^9;\mu)\right)\right|
\le10^{-3}e_2,
\quad e_2=\frac{35143531225}{953329813584}.
\tag{36}
\]

여기서 식 (35)의 소수는 표시값이므로 실제 계산에는 저장된 정확한 rational predictor를 사용한다. \(10^{-3}e_2\)는 약 \(3.6864\times10^{-5}\)이다. He와 thermal/momentum row는 행별 refinement \(|X_i-\overline X_i|\le Y_i+z_i e_j\)를 사용할 수 있다.

전체 family의 endpoint가 기준 상태로부터 이동하는 크기는

\[
\|X\|_\infty\le\eta+P_2+e_2
\simeq0.8168639800457719<1.
\tag{37}
\]

부모 primitive 도함수 경계로 바꾸면

\[
|T-50000\,\mathrm K|<1144\,\mathrm K,
\qquad |\beta-\beta_*|_2<2.451\times10^{-6}.
\tag{38}
\]

이 warm physical box 안에서 source fit와 cutoff cell이 유지된다. 하나의 endpoint를 sampling하여 물리적이라고 판단한 결과보다 강하게, 두 parameter slab의 모든 입력을 포함하는 경계다.

수치 corrector에 대한 결과도 확보했다. 정확한 산술에서 predictor부터 \(k\)회 고정 전처리자 갱신을 적용할 경우

\[
\|X^{(k)}-X\|_\infty\le q_j^k e_j.
\tag{39}
\]

\(k=10\)의 상계는 첫 튜브 약 \(3.92734\times10^{-19}\), 두 번째 약 \(1.80717\times10^{-15}\)다. 실제 반복은 실행하지 않았다. 이 식은 구현에서 필요한 precision·residual budget을 고르는 이론적 근거이며, 실제 부동소수점 endpoint 인증에는 식 (23)–(24)의 rounding 항을 붙인다.

구간 확장의 주된 이득은 predictor가 큰 반응 변위를 흡수하여 남은 잔차를 줄인 데서 나온다. 전처리자는 실제 고정 3×3 inverse로 구성했으며, 넓은 전체-row 경계에서의 수축 상계는 \(q_j\)로 인증했다. 입력 민감도에는 더 작은 공통 \(q_Q\)를 사용하여 불필요한 norm 손실을 줄였다.

## 9. 근거와 실행 상태

### 9.1. 실제 새 실행

| 계산 | 실제 새 실행 | 확보한 결과 |
|---|---|---|
| Anchor coefficient/predictor | Wolfram 1회, 0.303558 s | 10/10 named groups, 112 power bracket·5 exponential witness, 완전 수신 |
| 두 full-rate 튜브 | Wolfram 1회, 0.019472 s | 14/14 named groups, 2×7 strict tube 부등식, physical inclusion·same-root join |
| Family·finite reanchor | Wolfram 1회, 0.093849 s | 12/12 named groups, 유한 아핀 등가성·DP·norm 경계 |
| 새 공변 변분 | Wolfram + 실제 xAct 1회, 1.526537 s | 9/9 named groups, 내부 tensor 잔차 12/12가 0 |

새 science evaluator 호출은 총 4회이며, named groups는 10+14+12+9=45개다. 모두 실제 반환 결과가 true였다. 빌드·native 테스트·chemical RHS·stage 반복·ODE 및 scientific Python 실행은 0이다.

스칼라 family 결과의 `residual_count=69`는 영식 항목과 Boolean 조건을 함께 센 값이다. 이를 69개의 tensor zero로 합산하지 않는다. named group 수와 내부 witness 수를 별도로 기록한다.

독립 검토는 저자 역할을 맡지 않은 `/root/dropbox_checkpoint`가 수행한다. 문헌 대조, full-source·norm·정의역 전이, 실제 입력과 원응답, claim 범위를 검토하며 최종 판정은 `review/DECISION.json`에 남긴다. root와 anchor/family 저자의 계산 성공 보고만으로 채택을 대신하지 않는다.

### 9.2. 근거를 재사용한 곳과 최소 교정

유효한 부모 물리 cube, primitive differential bound, rate/derivative cap, source incidence·finite residual, 고정 anchor covariant identity를 재사용했다. 성공한 이전 계산의 재실행은 0이다. 새 defect cap을 \(H_2\)로 나누는 전이는 독립 검토자가 실제 `errCap >= H2*epsilon(H2)` 구성을 확인하여 닫았다. 부모 표기 다섯 곳의 잔여 LF 문제는 값·단위 대응을 기록하는 display-only 정오로 처리했다.

문헌 검색은 Exa 3회와 SciSpace 1회였고, 이번 새 의무에 대응하는 원전 두 편의 필요한 절을 읽었다. 전체 논문을 읽었다거나 검색 반환 항목을 모두 검증했다고 집계하지 않는다. 문헌 raw cache와 실제 읽기 범위는 `review/SEARCH_EVIDENCE.json`, `review/SOURCE_EVIDENCE.json`에 연결했다. 저작권이 있는 논문 전체 원문은 공개 dossier에 재배포하지 않는다.

현재 한계의 범위는 한 곳에서 정리한다. 이 결과의 \(h\)는 고정된 이전 입력을 갖는 implicit stage residual의 parameter다. \(H_2\)는 확보한 충분조건의 끝점이고 최대 허용 시간이라는 판정은 아니다. native source binary, 실제 stage/Picard/Newton 반복, ODE 시간 이력과 temporal truncation error는 실행·인증하지 않았다. 전역 RUX03나 별도 all-Bianchi·class-B·relative-species-tilt 의무의 완료 상태도 바꾸지 않았다. 새 strong no-go 또는 전역 문헌 novelty 주장은 이 루프의 채택 대상이 아니다.

## 10. 코딩 계약과 다음 열린 구성

### 10.1. 구현에 넘기는 정확한 입력

`dossier/CODING_CONTRACT.md`는 부모의 provider·공유 사건·primitive/JVP 계약을 재사용하고 다음 delta를 추가한다.

1. source commit과 coefficient interval을 연결한 \(a_p,B_p,\widehat\Lambda\), actual \(a_*(\mu)\), exact opposite-ray parity를 유지한 predictor.
2. 두 \(h\) interval, \(\eta,P_j,\rho_j\), 고정 chemical-block \(A_j\), full-seven-row \(Y_j,z_j\)와 정확한 양의 여유.
3. 같은 \(\xi\)에서 endpoint enclosure가 다음 튜브의 uniqueness box에 들어가는 포함 증거.
4. 실제 잔차·반올림·primitive inverse 오차를 포함한 \(1/(1-q_Q)\) 운반식.
5. 작은 증분에 작용하는 \(P\), 움직이는 old-state 중심의 \(DP\), transformed norm 및 radius.

코딩 소유자는 기존 네 항목을 유지한다: `HERE_RUX03_PRIMARY_PROVIDER_03`, `HERE_RUX03_COVARIANT_MOMENTS_04`, `HERE_RUX03_MOVING_GAS_STAGE_05`, `HERE_RUX03_CONTINUATION_CERTIFICATE_ADAPTER_06`. 이론이 닫혔다는 사실은 이 네 native 구현 의무의 실행 증거를 대신하지 않는다.

### 10.2. 다음 이론: 공동 입력과 두 stage의 포함 관계

다음 단위는 **`HERE_RUX03_JOINT_INPUT_AND_TWO_STAGE_ENCLOSURE_08`**이다. 첫 열린 구성은 이전 photon inventory도 \(p_q^-=p_{0q}(1+\pi_q)\)로 변화시키는 joint gas/photon family다. 명시적인 compact \(\pi\) 영역을 선택한 뒤

\[
F(X,h;\xi,\pi)=X-\xi-hG_h(X;\pi),\qquad
D_\pi X=F_X^{-1}hD_\pi G_h
\tag{40}
\]

와 제거된 \(p_q^+\)의 total derivative를 구성해야 한다. 식 (40)은 다음 문제를 고정하는 형식적 출발식이며, photon-input domain의 정량 certificate는 이번 채택 결과에 포함시키지 않는다.

이후 첫 stage의 gas·photon joint output enclosure가 실제 두 번째 stage의 새 anchor/input domain에 들어가는지를 증명한다. 현재 old-gas family는 기준점 주위 \(\|\xi\|≤0.01\)이고, 끝점 predictor의 첫 성분은 약 0.76이므로 첫 endpoint를 같은 old-input family에 그대로 넣을 수 없다. 새 중심의 primitive·rate domain과 photon 입력 범위를 실제로 구성해야 한다. 이 포함 관계를 확보한 뒤에만 stage별 perturbation/residual budget을 합성한다.

두 stage의 implicit 구성은 고정 \(D\)·tetrad에서 동일 사건의 photon·gas·escape energy/momentum balance와 함께 다룬다. 실제 시간 적분의 truncation error나 바뀌는 geometry는 그에 맞는 별도 입력과 근거가 필요하다. 다음 DAG는 이 수학 의무와 기존 native dependency를 구별하여 보존한다.

## 11. 주요 근거 위치와 문헌

### 새 직접 유도·계산

- `derivations/ANCHOR_RATE_ENCLOSURES.md`: 실제 rate와 cross-section 구간, midpoint predictor, full-interval magnitude와 error propagation.
- `derivations/PREDICTOR_TUBE_CONSTRUCTION.md`: P1–P28, full-source defect·고정 전처리자·튜브 정리·접합·유일성·오차.
- `derivations/TUBE_CERTIFICATE_NUMBERS.md`: 실제 정확한 두 튜브 상수와 7행 표.
- `derivations/OLD_STATE_FAMILY_AND_REANCHORING.md`: F1–F24 및 후속 actual output, old-state sensitivity·finite affine map·DP·moving-anchor current.
- `evidence/*_CALL_INPUT.json`, `*_RAW*.json`, `*_RESULT.json`: 실제 입력, 원응답, 완전 수신 여부와 정규화 결과.
- `review/DECISION.json`: 독립 판정과 claim별 확보 범위.

### 재사용한 부모

[P1] [BASS_HE PR34의 고정된 science manifest](https://github.com/cosmosapjw-quantum/BASS_HE/blob/3932669f7904f7f68f2f07dced4cf1da9d472480/research/rux03_continuation_certificate_20261013/dossier/SCIENCE_MANIFEST.json), SHA256 `9f223a9663ecec8da1edf90ee896d3aeabbf4f4c5bdd111df3e4f08b838c3192`.

[P2] [부모 독립 판정](https://github.com/cosmosapjw-quantum/BASS_HE/blob/3932669f7904f7f68f2f07dced4cf1da9d472480/research/rux03_continuation_certificate_20261013/review/DECISION.json), SHA256 `d0c1f12ed54157fecdb963bc3781683669fc7a25d6d30459b6e9255707f08fa6`.

[P3] [실제 물리 source의 FT03 rates](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/ft03_rates.rs)와 `source_map/CURRENT_SOURCE.json`의 controlled/provider/event 연결.

### 원전 대조

[L1] Helge Glöckner, *Finite order differentiability properties, fixed points and implicit functions over valued fields*, arXiv:math/0511218v2 (2007). [저자 원문](https://arxiv.org/pdf/math/0511218), printed pp. 34–38, Definition 4.4, Proposition 4.5, Remark 4.6, Theorem 4.7. 필요한 parameter regularity를 대조했으며, 수치 domain·H·H/He rate 경계는 이번 직접 구성이다.

[L2] P. Deuflhard and G. Heindl, *Affine Invariant Convergence Theorems for Newton’s Method and Extensions to Related Methods*, SIAM J. Numer. Anal. 16(1), 1–10 (1979), [DOI:10.1137/0716001](https://doi.org/10.1137/0716001). 공식 서지와 §1의 원 논문 OCR 재현을 대조했다. 공식 PDF의 전체 읽기나 손상된 §2 반경 식의 검증을 주장하지 않는다.

[L3] S. Day, J.-P. Lessard and K. Mischaikow, *Validated continuation for equilibria of PDEs* (2007), [원문](https://www.math.mcgill.ca/jplessard/papers/validated_continuation.pdf), Theorem 2.1 등 부모에서 읽은 범위를 재사용.

[L4] J. B. van den Berg, J.-P. Lessard and K. Mischaikow, *Global smooth solution curves using rigorous branch following* (2010), [원문](https://www.math.mcgill.ca/jplessard/papers/branch_following.pdf), Lemmas 5·7와 Proposition 8의 부모 읽기 범위를 재사용.

[L5] S. M. Rump, *Verified solution of large systems and global optimization problems* (1995), [원문](https://www.tuhh.de/ti3/paper/rump/Ru95b.pdf), §3 Theorem 3.2 등 부모 읽기 범위를 재사용. 실제 full-Jacobian 조건을 별도로 충족하여 이번 cube 유일성을 유도했다.
