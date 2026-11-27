# HE-ANG-TDCS413-DIAGONAL: 명목 공면 대칭 TDCS와 공통 배율의 유한점 비교
작성: Astra root, 2026-10-24. 상태: R1–R5 유도 완료; R6 독립 검토와 R7 판별 계산 전.

## 1. 연구 위치와 입력
PR97의 정확 교환 PWBE와 독립 비편극 spin trace를 재사용하여, Weigold FIAS-R-39 (June 1978) Table 1의 명확히 판독된 13개 공면 대칭 점을 비교한다. 원전은 수소 H(1s)의 두 전자 coincidence TDCS다. 인쇄된 E0=413.6 eV, EA=EB=200 eV, thetaA=thetaB, phiA-phiB=pi를 보존한다. 측도는 dEA dOmegaA dOmegaB이며 선택된 고정 에너지에서는 dEA와 dEB의 에너지 껍질 Jacobian 절댓값이 1이다.

원전 16개 설정 중 45,46,48 degrees는 스캔의 값/오차 판독이 미해결되어 모델 계산 전에 제외했다. 입력은
(theta,y,s)=(32,10,3),(34,11,3),(36,17,3),(38,28,4),(40,50,4),(42,76,5),(43,82,6),(44,100,6),(50,30,3),(52,15,2),(54,4,1),(56,2,1),(60,0,1).
y와 s는 원표의 상대 단위이고 s는 보고된 점별 1sigma다. 38도의 28(4)는 직접 시각 판독이다.

관측값 0(1)을 유지한다. 공분산, 절대 교정, 수용함수는 미제공이다. sigma_N=0은 상대 기준 series의 표기다. 이 계산은 s를 양의 수치 가중치로 사용한다. 보고할 kappa는 가중 최대잔차이며 신뢰수준이나 통계적 유의도가 아니다. 원전의 점별 오차를 확정적 오차구간이라고 채택하지 않는다.

## 2. 명목 에너지 계약과 기존 모델
원문의 분리에너지 13.6 eV에 맞춰 명목 에너지 단위 U=27.2 eV를 정의한다. U는 원문의 반올림 에너지를 정확한 무차원 모델 껍질에 대응시키기 위한 계약이며, 정밀 측정된 Hartree 상수라는 주장이 아니다.
epsilon=200/U=125/17, epsilon0=413.6/U=517/34=2epsilon+1/2.
k=sqrt(2epsilon)=sqrt(250/17), r=k0=sqrt(517/17).
PWBE 유도의 원자 단위는 k=pa0/hbar, Eh=hbar^2/(me a0^2), H(1s) 결합 1/2이다. 여기서는 위 명목 무차원 에너지를 그 식에 대입하고 상대 형태를 비교한다. eV 반올림/기기 응답에 대한 불확실성 전파는 이번 계약 밖에 남는다.

기존 모델은 비상대론, 고정 중심, 첫 Born, 평면 outgoing waves, 초기 비편극 spin, exact swapped exchange다. 기존 source transition amplitudes D,X에 대해
S=|D|^2+|X|^2-Re(D X*)=|D+X|^2/4+3|D-X|^2/4.
원전 Eq21의 인쇄된 -2DX는 기존 독립 spin trace와 구별하여 그대로 보존한다. 이번 입력이 그 인쇄식을 승인하지 않는다.
동일 에너지에서 A/B는 검출기 표지다. 점별 밀도에 사건 수 계수 2나 1/2를 추가하지 않는다.

## 3. 대칭 절단의 한 변수 환원
mu=cos(theta), phi=pi이므로 두 전자의 횡운동량이 상쇄된다. 다음을 정의한다.
z=r-2k mu, q^2=z^2, Delta^2=r^2+k^2-2rk mu=k^2+r z,
h=(1+k^2)^(-2), t(z)=(1+z^2)^(-2), d(z)=(t-h)/(k^2+r z).
두 전자 교환 시 분모와 h가 같으므로 d=x이다. triplet가 0이고 비편극 reduced weight는 d^2이다. 이는 두 전자 전체 상태가 0이라는 뜻이 아니다.
K(theta)=(32/pi^2)(k^2/r) d(z)^2,
K는 기존 원자 단위 TDCS 수치이고 물리적 차원 인자는 a0^2/Eh per sr^2다.
비교에 쓰는 무차원 shape는 f(theta)=K(theta)/K(44 degrees)이다. 이 정규화는 conditioning을 위한 정확한 배율 변경이며 a를 최적화하므로 결과 kappa는 변하지 않는다.

분모의 부호는 임의의 z에서 가정하지 않는다. 이번 theta in[32,60]에서 -1<z<k이므로 Delta^2>14-6=8이고 t>h, K>0이다. 아래 증명과 구현의 정의역을 연결한다.

## 4. 창 안의 단일 최대점과 q=0의 차이
d'(z)=N(z)/[(k^2+r z)^2(1+z^2)^3],
N(z)=r h(1+z^2)^3-r(1+5z^2)-4k^2 z.
따라서 K의 도함수 부호는 이 창에서 N의 부호다.
k^2>14, r<6, 0<h<1을 사용한다.

(a) -1<=z<=-1/2에서 x=-z in[1/2,1]:
N>56x-6-30x^2. 오른쪽은 오목한 이차식이고 양 끝에서 각각 14.5와20이므로 N>0.
(b) -1/2<=z<=0에서
N'=-4k^2-10rz+6rh z(1+z^2)^2 < -56+30=-26.
또 N(-1/2)>28-13.5=14.5, N(0)=r(h-1)<0이다.
따라서 이 구간에 유일한 z_star가 있고 N(z_star)=0이다.
(c) 0<=z<k에서는 t-h>0이고 t'<=0이어서
N=[t'(k^2+r z)-r(t-h)](1+z^2)^3<0.
결국 z in[-1,k)에서 K는 z_star까지 증가하고 이후 감소한다.

명목 창이 이 구간에 들어가는 것도 확인한다. r>5.514, k<3.835.
x=32pi/180은 0<x<1이고 pi>3.14다. 교대 Taylor 상계와 P4의 감소성에 의해
cos(32deg)<=1-x^2/2+x^4/24
<1-(628/1125)^2/2+(628/1125)^4/24<0.849.
그러므로 z(32)>5.514-2(3.835)(0.849)=-0.99783>-1.
theta가 증가하면 z도 증가한다. z(60)=r-k<k는 r^2<4k^2에서 따른다.
창에는 [-1/2,0]이 포함되는지 실제 명목 끝점으로 확인한다: z(32)<-1/2와 z(60)>0. 이 두 endpoint 부등식은 정확 상수/삼각 함수의 고정 입력 판별 항목이다. 첫 endpoint는 cos32>0.84, r<5.515, k>3.834로 z32<5.515-2*3.834*.84=-.92612<-1/2에서도 따른다. cos32>0.84는 cos x>=1-x^2/2와 pi<22/7로 확인된다.
유일한 전역 창 최대점은 theta_star=acos((r-z_star)/(2k))이다.
q=0인 theta_q0=acos(r/(2k))보다 theta_star가 작다. 단순한 q=0 peak 추정을 Delta^-4 인자가 이동시킨다는 직접적인 모델 귀결이다.

## 5. 공통 배율의 가중 최대잔차: 구성적 해
유한 n>=1에서 f_i>0, y_i>=0, s_i>0이고 적어도 한 y_i>0이라고 하자.
kappa(a)=max_i |a f_i-y_i|/s_i, a>=0.
실제 자료에서는 최적 a가 양수다. kappa>=0에서 가능한 a의 구간은
L(kappa)=max(0,max_i (y_i-kappa s_i)/f_i),
U(kappa)=min_i (y_i+kappa s_i)/f_i.
각 절댓값 부등식을 풀었으므로 가능성의 필요충분조건은 L<=U다.

모든 U_i>=0이므로 추가 nonnegative-scale 조건은 이미 충족된다.
L<=U는 모든 ordered pair i,j에 대해
(y_i-kappa s_i)/f_i <= (y_j+kappa s_j)/f_j
와 동치이며, 양의 분모로 곱하면
kappa >= (y_i f_j-y_j f_i)/(s_i f_j+s_j f_i).
따라서 정확한 유한 해는
kappa_star=max(0,max_{i,j} (y_i f_j-y_j f_i)/(s_i f_j+s_j f_i)).
모든 pair가 필요충분조건이므로 이는 단순한 pair 하한만이 아니라 완전한 minimax 값이다.
최적 배율은 [L(kappa_star),U(kappa_star)]에 속한다. 양의 kappa_star를 실현하는 active pair는
a_star=(y_i s_j+y_j s_i)/(f_i s_j+f_j s_i)
를 주며 양쪽의 부호가 반대인 잔차가 +-kappa_star에 닿는다. 다른 모든 행의 잔차도 직접 확인한다.
f_i를 공통 c>0배 하면 kappa_star 불변, a_star는1/c배다.
y=0인 행도 동일한 식으로 포함된다. log-ratio나 y에 대한 상대 오차를 쓰지 않는 이유다.
toy f=(1,2,4), y=(1,4,0), s=(1,1,1)의 독립 기준은 a_star=2/3, kappa_star=8/3, active pair=(2,3)이다.
이것은 유한 일차원 weighted Chebyshev 문제의 직접 구성이다. 문헌 전체에 대한 새로운 불가능성/배제 정리를 주장하지 않는다.

## 6. 실제 계산과 판정 계약
- 13개 입력과 제외된3개를 원문 decimal strings로 보존한다.
- binary64 closed shape와 원전 벡터식, 기존 PR97 point kernel의 새13기하값을 비교한다. 기존 suite를 다시 실행하지 않는다.
- mpmath80digits 독립 벡터식으로 f, 배율, kappa와 peak를 계산하여 변경된 의존성만 비교한다.
- kappa는 pair 최대의 직접 해와 interval-feasibility bisection의 독립 경로를 비교한다. 합성 toy는 exact Fraction으로검산한다.
- 원전 s에 대한 kappa=1 구간과 최적 구간, active pair/전13잔차를 보고한다. 결과가 kappa>1이더라도 도구/모델 실패로 분류하지 않는다. 이는 정해진 명목 모델과 가중 데이터의 관측 편차다.
- N의 root는 [-1/2,0]에서 이분법으로 계산하며 유일성은 위 논증을 사용한다. 보고하는 숫자는 선택 명목 모델의 peak이며 실험 peak의 추정치가 아니다.
- 32–60degree의 그림은 모델 연속곡선과13점/오차막대, 잔차를 보여준다. 45/46/48 제외 사실을 명시한다. 그림은 저장된 분석 JSON만 읽는다.

## 7. 판정 범위와 DAG
이 단위는 유도된 joint PWBE 모델을 실제 상대 joint TDCS의 한 절단과 연결한다.
HE-ANG-CONTRACT -> DDCS20 marginal / CCC exchange / TDCS54 sparse joint -> PWBE spin-azimuth -> 이번 TDCS413 diagonal benchmark 순으로 근거를 연결한다. 각 sibling의 원래 claim ceiling은 유지한다.
전체 HE-ANG-SOURCE-PAYLOAD의 source-consistent physical joint law 또는 amplitude/event provider에는 absolute scale, full support, detector-response/uncertainty, spin/count/exchange/frame/recoil 계약의 추가 입력이 남는다. Parent SOURCE_INPUT_PENDING을 유지한다.
HE-X1 32fixtures와이론, HE38, Hex, CONTRACT, DDCS20 결과를 재사용하고 무변경 replay0을 기록한다. C9-NB-01 future partialmu_window theta metadata 의무는 별도로 유지한다.

