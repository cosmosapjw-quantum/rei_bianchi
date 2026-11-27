# 사건법칙과 계산 단순화

계산에 필요한 최저 차수 정보는 종별 raw N,P,R와 같은 법칙의 pair cross tensor다. 사건 전체 표를 매번 rate/boost 함수에 전달할 필요는 없다. 같은 event measure에서 한 번 적분한 이들 모멘트와 source/domain/error certificate를 캐시하면 임의의 Galilean shift와 basis rotation은 3×3 행렬 연산으로 계산된다. 수치적 속도 향상 배수는 이번에 측정하지 않는다.

## 선택한 경로

1. **Joint event route:** positive weighted events의 momentum/energy support를 검사하고 N,P,R,C12를 한 순회에서 합산한다. 입력 n에 O(n) 산술, 누적 모멘트에는 고정 크기 메모리를 사용한다. Event normalization과 inclusive electron count2를 보존한다.
2. **Certified moment route:** 큰 joint source의 moments-only 공급을 허용하되 각 moment와 total sigma의 같은 law/source/domain/normalization identity, event-support compatibility 및 오차 certificate가 필요하다. Moment cone만으로 joint existence 또는 경험적 source admission을 대체하지 않는다. 이번 구현의 fixture는 route1로 실제 합산하고 route2의 필요한 필드를 precheck한다.
3. **Marginal route:** 완전 inclusive electron law는 electron moments, ion P 및 energy trace를 제공한다. ion full R/STF는 C12의 STF 또는 호환 recoil certificate를 추가로 받는다. 미결정 부분을0으로 채우지 않는다.

## 대안과 의존성

전자의 독립성을 새로 가정해 곱분포를 만드는 방법은 finite-mass energy/momentum shell과 실측 correlation을 바꿀 수 있다. 따라서 이를 입력 데이터의 보간법으로 채택하지 않는다. 새로운 explicit model을 연구하는 경우에는 별도 model identity와 source uncertainty를 갖추면 비교할 수 있다.

5변수 shell density를 사용하는 공급자는 모든 물리 root와 phase-space Jacobian을 소유한다. 임의의 한 root를 선택하거나 detector-cut subset을 전체 event law로 자동 정규화하지 않는다. Zero outgoing momentum은 방향이 정의되지 않으므로 momentum measure로 처리할 수 있다.

## 유한 판별 구성

임의의 rational m,M,kappa>0, a=e_z, b∈{±e_x,±e_y}, s=±1에서 A/B를 만든다. 각 법칙8 event, weight1/8. 모든 momenta가 rational이고 W=2 kappa²(1/m+1/M)이므로 positivity, exchange, momentum/energy shell, full discrete electron marginal equality 및 다른 ion STF를 exact fractions로 검사할 수 있다. 연속 azimuth law에 대한 증명은 별도의 analytic identity다. 4방위 quadrature가 연속분포 자체라는 주장은 하지 않는다.

raw frame 검사도 exact rational boost와 orthogonal signed-permutation rotation으로 수행한다. 이 구조는 작은 비용으로 기존 X1 또는 HE38의 완료 suite를 반복하지 않고 새 의존성만 판별한다.
