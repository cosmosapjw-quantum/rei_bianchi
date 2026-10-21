# Source-age 분포와 반응 함수 변화의 분리

2026-10-18. PR171 원래 native 물리 소스를 변경하지 않는 조건부 유도·경량 코드.

양의 유한 측도 nu_A,nu_B의 질량을 m_A,m_B, 정규화한 분포를 mu_A,mu_B라 한다. 공통 반응 h에 대해 |h|<=G_h, h=h_smooth+sum J_i 1[a>=c_i], Lip(h_smooth)<=L_h라면

B_h = G_h |m_A-m_B| + min(m_A,m_B) [L_h W1(mu_A,mu_B) + sum |J_i| |mu_A([c_i,infinity))-mu_B([c_i,infinity))|]

는 |integral h dnu_A-integral h dnu_B|의 실수 상한이다. 작은 질량만큼 정규화한 차이를 취하고 나머지 질량을 G_h로 평가하면 된다. Smooth 부분에는 두 측도의 임의 coupling을 써서 |h(a)-h(b)|<=L_h|a-b|를 적분하고 최솟값을 취한다. Jump 부분은 각 tail probability 차이의 정확한 적분이다. Zero mass에는 정규화하지 않는다.

## 서로 다른 gas/opacity 반응

전체 두 지지집합에서 |g_A-g_B|<=delta가 별도로 보장된다면

|integral g_A dnu_A-integral g_B dnu_B|
 <= min(B_gA + m_B delta, B_gB + m_A delta).

증명: 첫 항에서는 integral g_A dnu_B를 더하고 빼서 공통 반응 차이와 nu_B에서의 반응함수 차이로 분해한다. 반대 분해는 nu_A를 사용한다. 두 유효 상한 중 작은 것을 택한다. delta는 단순 endpoint 샘플로 추정해서는 안 된다. 실제 nonlinear Grackle의 유효 delta를 이번 코드가 제공한다는 주장은 없다.

## 날카로운 부정대조

동일한 측도 nu_A=nu_B=2 delta_{age=1}이면 W1=0이고 질량 차이도 0이다. 그런데 prescribed survival g_A=exp(-age), g_B=exp(-2 age)는 관측량 차이가 2(exp(-1)-exp(-2))=0.46508831586965926이다. 공통 반응 bound를 다른 opacity 이력에 잘못 적용하면 0을 반환한다. 새 paired_bound는 union support의 delta가 주어질 때 이 예에서 정확한 값을 반환한다.

## 검산

복원된 remote 74 tests + 새 8 tests = 82/82 PASS. RED에서 위 동일측도 반례가 0 대 0.46508831586965926으로 실패했고, owner-response term을 추가한 뒤 같은 test가 PASS했다. 100개의 무작위 양의 이산측도와 별도 24개의 prescribed source/constant-opacity 수치 사례에서 두 triangle bound가 참 관측량 차이를 포함했다. SciPy QUAD의 continuum controls는 이산측도 비교와 별도 값으로 보존한다. Binary64 outward interval certification, actual native age64/spectral128/time convergence 및 production admission은 미수행이다.
