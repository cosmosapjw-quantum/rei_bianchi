# HE33 바리온 압력모멘트: 유도와 채택 범위

## 정의·가정과 문헌의 역할

이 단원은 균질하고 non-tilted인 LRS Bianchi I의 바리온 기체를 위한
기계적 모멘트 부분문제를 완결한다. metric signature는 (-,+,+,+)이고
proper time t 및 비회전 공간 정규직교 기저를 쓴다. H,s,nu_pi의 단위는
s^-1, 압력과 응력은 Pa=J m^-3이다. c와 k_B를1로 두지 않는다.

단일 비상대론적 입자종 또는 하나의 유효 압력텐서로 표현한 frozen
mixture를 대상으로 한다. peculiar bulk velocity, 전자기장, 공간
heat-flux divergence는0이다. 각 주방향에서 P_ii/(n m c^2)<<1이
비상대론적 조건이다. 분포의 속도공간 경계항이 소멸해야 한다.
충돌을 하나의 nu_pi로 닫는 것은 prescribed relaxation 모형이다.
실제 primordial 혼합물의 종별 수송계수는 후속 의존성이다.

Kuldinow et al. JCP508(2024)113030 Eq.(10),(43)은 일반 pressure moment와
BGK형 relaxation 구조의 원전이다. Hakim의 author note Eq.(5),(22),(31)은
central moment 및 다종 source 모멘트, BGK와 LBO relaxation 계수의 차이를
대조한다. 아래 Bianchi 계수, 열수지, LRS 변환과 수치식은 이 단원의 직접 유도다.
원전 링크와 읽은 범위는 SOURCES.json에 있다.

## 1. 운동론에서 pressure tensor까지

K_ij=H delta_ij+sigma_ij, sigma=s D, D=diag(-1,-1,2)라 한다.
물리 peculiar velocity v_i에 대해

\[
 n=\int f\,d^3v,\quad P_{ab}=m\int v_av_b f\,d^3v,\quad
 p=\frac13{\rm tr}P,\quad \pi=P-pI.
\]

균질 운동론식은

\[
 \partial_t f-K_{ij}v_j\partial_{v_i}f=C[f]+I[f].
\]

영차 모멘트는 \(\dot n+3Hn=R\), \(R=\int I\,d^3v\)다.
이차 모멘트의 부분적분은

\[
m\int v_av_bK_{ij}v_j\partial_{v_i}f\,d^3v
=-3HP_{ab}-K_{ai}P_{ib}-P_{ai}K_{ib}
\]

를 준다. 따라서

\[
\boxed{\dot P+5HP+\sigma P+P\sigma=C^{(2)}+S.}\tag{1}
\]

5H는 physical volume의 희석3H와 두 속도 인자의2H 합이다.
P/n으로 정의한 온도텐서의 계수와 혼동하지 않는다.
collisionless drift의 (1)은 가우스 분포를 가정하지 않는다.

압력 비등방성 relaxation rate \(\nu_\pi\ge0\)와 source를

\[
 C^{(2)}=-\nu_\pi\pi,\qquad S=(2Q/3)I+J,\qquad {\rm tr}J=0
\]

로 정의한다. \(Q={\rm tr}S/2\)는 kinetic energy에 유입되는 power density
W m^-3이다. BGK에서는 nu_pi=nu_BGK이고 LBO의 해당 표기에서는
nu_pi=2 nu_LBO다. photoionization/RR 빈도를 그대로 대입할 관계는 없다.

## 2. Trace, STF와 LRS 변수

(1)의 trace 및 STF는

\[
\dot p+5Hp+\frac23\sigma:\pi=\frac{2Q}{3},\tag{2}
\]
\[
\dot\pi+(5H+\nu_\pi)\pi+2p\sigma+
 2(\sigma\pi)_{\rm STF}=J.\tag{3}
\]

일반 대칭 텐서에서 마지막 항은 \((\sigma\pi+\pi\sigma)_{\rm STF}\)를
뜻한다. LRS에서는 두 텐서가 가환한다. \(\pi=qD,J=jD\),
\(D^2=2I+D,D:D=6\)를 사용하면

\[
\boxed{\dot p=-5Hp-4sq+2Q/3},\tag{4}
\]
\[
\boxed{\dot q=-(5H+\nu_\pi+2s)q-2ps+j}.\tag{5}
\]

양의 변수는 \(X=P_\perp=p-q,\ Y=P_\parallel=p+2q\)다.
\(P\succeq0\)은 \(X,Y\ge0\), 즉 \(p\ge0,-p/2\le q\le p\)와 같다.

\[
\frac{d}{dt}\binom XY=
A\binom XY+\binom{2Q/3-j}{2Q/3+2j},\quad
A=\begin{pmatrix}
-5H+2s-\nu_\pi/3&\nu_\pi/3\\
2\nu_\pi/3&-5H-4s-2\nu_\pi/3
\end{pmatrix}.\tag{6}
\]

이 단원의 step/advance는 Q=j=0인 기계적 연산자다.
thermalLedger는 필요한 Q를 계산하는 진단이며 그 열원을 시간 적분하지 않는다.

## 3. 열수지와 HE32 등온 계약의 연결

\(e_{\rm th}=3p/2\)이므로

\[
\boxed{\dot e_{\rm th}+3H(e_{\rm th}+p)+\sigma:\pi=Q}
\]
\[
\dot e_{\rm th}+5He_{\rm th}+6sq=Q.\tag{7}
\]

충돌 isotropization은 trace를 보존한다. shear work를 우변에 놓으면
\(-\sigma:\pi\)이며, Navier–Stokes 한계에서
\(\pi\simeq-2(p/\nu_\pi)\sigma\)이므로
\(-\sigma:\pi=12ps^2/\nu_\pi\ge0\)다.

공통 T와 \(p=n_{\rm part}k_BT\),
\(n_{\rm part}=n_{\rm nuclei}+n_e\)를 채택하고
\(\dot n_{\rm part}+3Hn_{\rm part}=R_{\rm part}\)라 하면

\[
\dot T=-2HT-\frac{TR_{\rm part}}{n_{\rm part}}
-\frac{2\sigma:\pi}{3k_Bn_{\rm part}}
+\frac{2Q}{3k_Bn_{\rm part}}.\tag{8}
\]

고정 T를 유지하는 총 kinetic power는

\[
\boxed{Q_{\rm iso}=3Hp+6sq+\frac32k_BT R_{\rm part}.}\tag{9}
\]

T를 지정 함수로 두는 일반 경우에는
\((3/2)k_Bn_{\rm part}\dot T\)를 더한다. 열원이 팽창 냉각과
shear work 및 입자수 변화의 어떤 부분을 공급하는지 분리해야 한다.
식(9)는 총 요구 power다. 이미 photo heating 등 물리적 power가 있으면
thermostat은 그 합과 (9)의 차이만 담당한다. 중복 가산하지 않는다.

이온화 potential/binding energy와 escaping radiation은 별도 에너지 장부다.
R_part만으로 threshold 비용을 계산하지 않는다. Frozen composition에서는
R_part=0이다. HE32의 pi_b=0,T=20000K를 실제 새 모형으로 확장하려면
이 source contract와 종별 relaxation을 함께 연결한다.

## 4. 양성성 및 극한

nu_pi>=0이면 A의 off-diagonal이 비음인 Metzler 행렬이다. 충분히 큰
alpha에 대해 A+alpha I가 성분별 비음이므로

\[
e^{At}=e^{-\alpha t}\sum_{k=0}^\infty
 \frac{t^k(A+\alpha I)^k}{k!}
\]

의 모든 성분이 비음이다. 따라서 t>=0에서 X,Y>=0이 보존된다.
시간의존 계수에도 각 양의 작은 구간 전파행렬의 극한으로 같은 성질이 있다.
유한 구현의 representability와 오차는 별도 검사한다.

p>0에서 r=q/p는

\[
\dot r=4sr^2-(\nu_\pi+2s)r-2s.\tag{10}
\]

r=-1/2,1의 우변은 각각 nu_pi/2,-nu_pi로 cone 안쪽을 향한다.
p=0의 vacuum은 X=Y=0 별도 branch로 처리하고 r는 null이다.
고정 s,nu_pi의 attracting ratio는

\[
r_*=-\frac{4s}{\nu_\pi+2s+
\sqrt{\nu_\pi^2+4\nu_\pi s+36s^2}},
\]

이며 s=0,nu_pi>0에서는 r*=0이다. s=nu_pi=0이면 r는 초기값으로 일정하다. nu_pi=0의 cone 경계는
초기 압력이 정확히0인 방향에 따라 invariant일 수 있어 interior attraction과
구별한다. nu_pi>>|s|에서 r*=-2s/nu_pi+O((s/nu_pi)^2)다.

nu_pi=0이면 직접 geodesic scaling으로

\[
P_i(t)=P_i(t_0)[a(t_0)/a(t)]^3[a_i(t_0)/a_i(t)]^2.
\]

등방 한계는 P~a^-5,n~a^-3,T~a^-2다.
Hydrodynamic approximation에는 relaxation보다 느린 팽창/shear/입력변화와
초기 relaxation layer 이후라는 추가 timescale 조건이 필요하다.

## 5. 안정적인 고정계수 계산식

\(u=s\Delta t,v=\nu_\pi\Delta t,h=H\Delta t\)를 쓰고

\[
d=3u+v/6,\quad \delta=\sqrt{d^2+2v^2/9},\quad
b_+=\frac{8u^2}{\delta+u+v/2},
\]
\[
\ell_+=-5h+b_+,\quad \ell_-=-5h-(v+2u)-b_+.
\]

u=v=0은 등방 지수감쇠 branch다. 이 rationalized b+는 큰 v에서
\(-v/2-u+\delta\)의 상쇄를 피한다. \(r_d=d/\delta\)일 때
projector의 작은 weight는

\[
\alpha_{\rm small}
=\frac{(\sqrt2\,v/(3\delta))^2}{2(1+|r_d|)}.
\]

큰 weight는 1-alpha_small이다. d의 부호에 따라 alpha_+,alpha_-를 배치하면

\[
M_{11}=\alpha_+e^{\ell_+}+\alpha_-e^{\ell_-},\quad
M_{22}=\alpha_-e^{\ell_+}+\alpha_+e^{\ell_-},
\]
\[
M_{12}=\frac{v}{6\delta}e^{\ell_+}(1-e^{-2\delta}),\quad
M_{21}=2M_{12}.\tag{11}
\]

모든 항이 양의 합이므로 log-sum-exp로 각 최종 압력까지 직접 계산할 수 있다.
작은 weight의 log는 log(v),log(delta)로 계산하고,
\(1-e^{-2\delta}\)에는 -expm1(-2delta)를 쓴다.
이 방식은 작은 projector의 상쇄와 fast exponential의 조기 underflow를
함께 막는다. source는 두 실제 실패와 교정 전 출력을
evidence/ROUNDOFF_FINDINGS.json에 보존한다.

representable하지 않은 scaled coefficients, 최종 pressure overflow 또는
양의 최종 pressure underflow는 명시적 RangeError다. 물리상태를 clipping하거나
정규화하지 않는다. 소실되기 쉬운 작은 차 q는 (Y-X)/3으로 계산한다.
q가 p보다 binary64 roundoff 아래인 경우 상대적 q 정확도를 보장하지 않는다.

시간의존 계수에는 midpoint sampling \(A(t+h/2)\)의 exponential을 연쇄한다.
매끄러운 고정 문제에서 전역2차이며 고정계수에는 정확하다.
이는 arbitrary time-dependent stiff initial layers에 대한 uniform-order
인증과 구별한다. 해당 범위까지의 실제 수렴 증거가 필요하면 별도 gate를 둔다.

## 6. 비교한 수치 선택과 판정

Drift-half/BGK-full/drift-half Strang은 양성성을 보존하지만
nu_pi*dt→infinity에서 마지막 half drift가
r≈-s*dt를 남긴다. 정확한 해의 r≈-2s/nu_pi와 다르다.

독립40자리 CAS의 H=.2,s=.14,nu_pi=1e8,dt=.1,P0=(1,1)에서

- full exponential r=-2.799999992159999978e-9,
- Strang r=-0.01390065209951805960.

따라서 (11)을 채택했다. 이 결과는 특정 splitting의 유한-step 오류 진단이다.
새 물리적 no-go를 채택하지 않으므로 NG1–NG7의 새 no-go 채택은
NOT_APPLICABLE이다. 모든 명제는 정의/가정, 직접 유도, CAS·수치 검산,
아직 남은 물리 calibration을 나누어 기록한다.

## 7. 원래 목표와 후속 결합 범위

HE32는 photo+caseA RR, prescribed UV, fixedT, gas pi_b=0인 완료 pilot이다.
HE33은 그중 gas stress에 필요한 mechanical operator를 추가했다.
현재 prescribed nu_pi의 manufactured controls로 HE32 gas stress의 실제
크기를 예측하지 않는다.

다음 의존성은 종별 nu_pi/교환행렬, 반응의 운동·열 모멘트, 공통T의
유효성, binding/radiation energy, Einstein feedback이다.
nu_s*pi_s의 합은 일반적으로 하나의 nu_pi*sum(pi_s)와 같지 않다.

같은 기저에서 최종 signed stress source는
p_m+p_gamma+p_nu+q_b이고 norm은 합한 뒤 sqrt(6)을 곱한다.
p_m의 기존 nonbaryonic 소유권을 유지한다.
q_b만 shear 방정식에 넣고 e_b,p_b의 배경/열수지를 생략하려면
그 근사를 test-background로 명시해야 한다.
