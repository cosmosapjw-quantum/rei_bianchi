# HE-ANG-DDCS20-WINDOW: 유한 검출 구간의 DDCS 모멘트

상태: R5 유도 완료, R6 독립 검토 대기. 작성자 /root. 2026-10-24.

## 1. 결과와 정의역

Childers et al., *Physical Review A* **69**, 022709 (2004), DOI
https://doi.org/10.1103/PhysRevA.69.022709 의 Table IV를 사용한다.
입사 에너지 E0=20 eV에서 검출 전자 E=3,4,5,6 eV와
theta=15,20,25,30,40,60,90,120 degree의 32개 DDCS 값을 사용한다.
같은 표의 E=2 eV 8개 값은 원전 그대로 보존하되 주 계산에는 넣지 않는다.
추가 오차 각주의 '5% larger'를 임의로 수치화하지 않기 위해서다.

이 단위는 표의 보고된 DDCS를 양의 보간 함수로 연장한 **유한 window
검출 전자 측도**의 모멘트를 정의하고 계산한다. 보간 가정 아래 정확한
선형 모멘트와, 지정한 직사각형 입력 민감도 집합에서 정규화 모멘트의
전역 극값을 얻는다. 원전의 값 자체가 미지의 실제 연속 함수 전체를
확정한다는 주장은 하지 않는다.

E는 eV로 표시한 양의 수치 좌표, mu=cos(theta),
W=[3,6] x [cos(120 degree),cos(15 degree)]이다.
에너지 및 mu node는 증가 순서로 정렬하고 원래 angle-row 대응을 보존한다.
실험의 beam axis를 z축으로 삼고, 방위각에 무관한 분포로 완성하는
축대칭 가정을 명시한다. 따라서 dOmega=2 pi dmu다.
이는 laboratory 검출 변수에 대한 모멘트이며 CM 변환 또는 finite-mass
recoil event model을 공급하지 않는다.

Table IV의 수치 y_ij의 단위는 10^-19 cm^2/(sr eV)=10^-23 m^2/(sr eV)다.
원전의 E1=E0-EL은 검출 전자의 residual kinetic energy다.
동일 입자 중 원래 입사 전자를 추적하는 label로 해석하지 않는다.
추가 factor 2는 도입하지 않는다. 전체 전자-count 적분과 ionization event
cross section의 관계는 원전의 명시적 convention과 공급자 연결이 필요하다.

## 2. 양의 보간과 적분 연산자

mu 격자의 연속 piecewise-linear cardinal hat를 L_i(mu), E 격자의 hat를
H_j(E)라 하자. 각 cell에서 양 끝 node를 잇고, 내부 node의 두 인접 cell
밖에서는 0이다. 끝 node는 한 cell만 지지한다. 정의역 W 안에서
L_i,H_j>=0, sum_i L_i=sum_j H_j=1이다. 따라서

    f_h(E,mu) = sum_ij y_ij L_i(mu) H_j(E)

는 양의 데이터에 대해 양이고, node 값을 정확히 보존하며 cell의
네 값의 convex combination이다. 실제 DDCS는 D_h=10^-23 f_h다.
W 밖에서 f_h를 평가하거나 적분하는 호출은 실패시킨다. 0 외삽도 하지 않는다.

정수 r=0,1,2 및 q=0,1/2,1에 대해

    A_i^(r) = integral mu^r L_i(mu) dmu
    B_j^(q) = integral E^q H_j(E) dE
    R_rq = 2 pi 10^-23 sum_ij y_ij A_i^(r) B_j^(q)

를 정의한다. R_rq의 단위는 m^2 eV^q다. 한 에너지 node에서의
J_r(E_j)=2 pi 10^-23 sum_i y_ij A_i^(r)는 m^2/eV 단위다.
q=0인 B_j는 usual trapezoidal weights이지만 r=1,2와 q=1/2,1은
가중 함수를 node에서 곱한 뒤 단순 trapezoid하는 식이 아니다.
보간 함수와 가중 함수를 곱한 연속 적분을 계산해야 한다.

각 hat segment를 alpha+beta x로 쓰면 원시함수는

    alpha x^(s+1)/(s+1) + beta x^(s+2)/(s+2).

mu에는 s=0,1,2를, 양의 E에는 s=0,1/2,1을 적용하여 각 segment 끝에서
차를 취하고 합한다. mu의 음수 구간에서 fractional power를 쓰지 않는다.
위 유도는 유한 합과 유한 구간의 다항식/양의 거듭제곱 적분이므로
극한 교환이나 수렴 가정이 추가되지 않는다.

## 3. 검출 전자의 물리량

epsilon=1.602176634 x 10^-19 J/eV를 정확한 eV 변환 상수로 사용한다.
전자 질량 m_e는 기호로 유지한다. 이 저에너지 단위는 비상대론적
p=sqrt(2 m_e epsilon E)를 사용한다. 수치 보고에서 m_e 값을 임의 선택할
필요가 없도록 momentum과 tensor의 scale-free 계수를 함께 제공한다.

부분 검출 cross-section N_W=R_00>0,
에너지 가중량 U_W=epsilon R_01,
종방향 운동량 가중량 P_z=sqrt(2 m_e epsilon) R_(1,1/2)이다.
축대칭 완성에서 P_x=P_y=0이고 raw second momentum tensor는

    S = 2 m_e epsilon diag((R_01-R_21)/2,
                           (R_01-R_21)/2, R_21).

trace S=2 m_e U_W이며 S는 양의 준정부호다.
STF tensor는 S - trace(S) I/3이다. 이 등식은 검출된 outgoing electron의
관계이며, 원래 incident electron/ion을 포함한 net collision source의
보존 식으로 승격할 수 없다. 한 사건의 다른 전자/ion recoil는 미지다.

정규화한 유용한 출력은

    mean(mu) = R_10/R_00,
    mean(P2) = (3 R_20-R_00)/(2 R_00),
    mean(E) = R_01/R_00,
    mean(sqrt(E) mu) = R_(1,1/2)/R_00.

조건부 momentum covariance를 2 m_e epsilon으로 나누면

    diag((R_01-R_21)/(2 R_00),
         (R_01-R_21)/(2 R_00),
         R_21/R_00 - (R_(1,1/2)/R_00)^2).

마지막 성분은 X=sqrt(E) mu의 분산이므로 >=0이다. Cauchy-Schwarz로
R_(1,1/2)^2 <= R_00 R_21이 직접 얻어진다. 앞의 두 성분은
E(1-mu^2)>=0의 평균이다. 이는 실제 수치 출력의 invariant다.
N_W를 photon/electron/ion event rate나 total ionization sigma로 부르지 않는다.
추후 정해진 beam flux를 곱하면 같은 window에서의 검출 response가 되지만,
thermal 평균과 network source에는 별도 incident distribution 및 event 계약이 필요하다.

## 4. 보고된 오차로 정한 결정론적 민감도 집합

원전은 각 angle row의 percent u_i를 1 standard deviation으로 제시한다.
셀 사이/에너지 사이 covariance를 주지 않으며 값은 연속체 polynomial fit과
공통 측정 절차를 공유한다. CCC H(n=2) excitation reference DCS 자체의 오차는
보고된 error bar에서 제외된다. 그 reference는 angle에 의존한다.

따라서 통계적 독립이나 Gaussian 분포를 가정하지 않는다. 이번 계산에서
명시적으로 **선택한 민감도 집합**은 모든 선택 셀 k=(i,j)에 대해

    l_k=y_k(1-u_i/100), h_k=y_k(1+u_i/100), l_k <= z_k <= h_k.

이는 각 셀이 해당 범위 안에 있는 모든 조합을 탐색하는 deterministic box다.
이 집합의 극값은 confidence interval, simultaneous 1-sigma coverage 또는
실험 전체 uncertainty bound가 아니다. 미지의 covariance를 추정하지 않는다.
특히 공통 normalization, 각도 의존 reference, 보간 오차와 미관측 영역의
기여를 포함했다고 말하지 않는다. box의 독립 좌표는 계산상의 허용 집합이지
실험 오차의 독립 확률변수가 아니다.

선형 functional w.z의 최소/최대는 각 w_k 부호로 l_k 또는 h_k를 고르면
정확하게 얻어진다. 대칭 halfwidth delta_k=(h_k-l_k)/2이면
|w.(z-y)| <= sum_k |w_k| delta_k이고 bound는 달성된다.

정규화 functional F(z)=(b.z)/(a.z)를 고려한다. a_k>0, 0<l_k<=h_k이므로
분모는 양수다. q_k=b_k/a_k를 증가 순서로 정렬한다.

**최소의 threshold 구성:** 정렬된 첫 t개 좌표는 h, 나머지는 l로 두고
t=0,...,n의 n+1개 후보 F를 계산한다. 후보의 최소가 box 전체의 최소다.
**최대의 threshold 구성:** 정렬된 첫 t개는 l, 나머지는 h로 두고 동일하게
n+1개 후보 중 최대를 고른다. prefix sums로 정렬 후 O(n) 연산이다.
전체 O(n log n), 메모리 O(n)이다. 각 극값의 실제 z witness를 반환한다.

증명: compact box 위에서 F는 연속이므로 최소 r_*가 존재한다.
F(z)>=r_* iff (b-r_* a).z>=0이고, 최솟값의 z_*에서는 equality다.
선형 식의 최소는 c_k=b_k-r_*a_k<0이면 h_k, c_k>0이면 l_k에서 달성된다.
c_k=a_k(q_k-r_*)이므로 이 vertex는 정렬 순서의 threshold 모양이다.
c_k=0인 좌표는 어느 endpoint를 골라도 equality이며 모두 같은 쪽으로
고른 threshold 후보가 존재한다. 이 후보에서 F=r_*이므로 유한 scan이
정확하다. 최대는 부호별 선택을 뒤집으면 같은 증명이다.

이 증명은 b_k 부호를 제한하지 않으며 negative mean(mu)/P2에도 적용된다.
상수 q와 tie도 처리한다. a_k=0, l_k<=0, 비유한 입력은 이번 계약 밖이다.
moment ratio에서는 a_ij=A_i^(0) B_j^(0)>0이므로 조건을 충족한다.
물리 단위의 양의 공통 factor 2 pi 10^-23는 ratio에서 소거한다.
모든 데이터에 같은 양의 scale을 곱하면 정규화 값과 box ratio bounds는
불변이지만, 원전 reference의 angle-dependent 오차가 소거된다는 뜻은 아니다.

## 5. 보간 가정의 판별과 경계

piecewise-linear mu 모델을 주 모형으로 고정한다. 하나의 대조 모형은
동일 node 값을 piecewise-linear theta로 보간하고 실제 Jacobian sin(theta)를
곱해 적분한다. 두 결과의 차이는 보간 표현의 민감도다. 두 모형만으로
실험 연속 함수의 오차 bound 또는 convergence order를 정할 수는 없다.

이 한계는 구체적으로 확인된다. 어떤 열린 cell 내부에서만 양이고 모든
node/경계에서 0인 연속 bump를 f_h에 양의 크기로 더하면 node 값과 양성을
보존하면서 N_W가 증가한다. 예를 들어 해당 cell [a,b]x[c,d]에서
(mu-a)^2(b-mu)^2(E-c)^2(d-E)^2, 밖에서 0인 함수를 쓸 수 있다.
이는 보간 불확실성 구분을 위한 기존 수준의 구성적 관찰이며 새로운
strong no-go 또는 원전의 불가능성 정리로 주장하지 않는다.

## 6. 실제 검증과 코딩 연결

R6은 별도 Astra reviewer가 원전 convention과 위 유도를 검토한다.
R7은 Wolfram에서 bounded symbolic integration/ratio derivative를 확인한다.
추가 CPU 수치를 생성하지 않는 순수 도구 검산도 actual output을 보존한다.
C6은 closed-form polynomial controls, direct cellwise Gaussian quadrature와
analytic hats의 비교, 작은 box의 전체 vertex 열거 대조를 수행한다.
C7은 실제 32개 입력에서 위 모멘트 및 positivity/PSD invariant를 계산한다.
C8은 하나의 theta 대조 모형, quadrature 16/32 비교, 비용과 환경을 남긴다.
수용 기준과 자원은 CONTRACT.json을 따르며 C9 독립 검토 전 admission은 보류한다.

## 7. 재사용과 다음 물리 의무

HE-X1의 이론, 32 fixtures 및 독립 검토는 동일 의존성으로 재사용한다.
HE-ANG provider 계약과 HE38/Hex intake는 다시 실행하지 않는다.
이번 실측 marginal window는 X1을 경험적 angular correction으로 바꾸지 않는다.
HE-ANG parent는 source-qualified joint electron law, full support, spin/count
normalization, finite-mass/frame/recoil correlation 의무 때문에
SOURCE_INPUT_PENDING을 유지한다. 다음 유용한 입력은 검출 convention이
명시된 joint outgoing moment/amplitude table 또는 그와 동등한 event sampler다.
