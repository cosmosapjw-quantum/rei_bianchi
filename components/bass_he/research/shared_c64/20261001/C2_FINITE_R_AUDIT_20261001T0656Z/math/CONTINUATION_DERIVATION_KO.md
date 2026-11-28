# C2: 공통 charge-center에서의 fixed-m continuation

이 문서는 기존 C1/C1b prolate 정의와 A2의 exact lowest fixed-sector 상태를 연결하는 직접 유도다. 외부 문헌의 새로운 정량 결과를 주장하지 않는다. `continuation.py`는 기저 계수 내적 대신 실제 공간의 물리적 내적을 계산한다. 새로운 eigensolve는 이 작성·구현 검증에 포함하지 않는다.

## 1. 하나의 물리적 원점

전하가 \(Z_A,Z_B\)이고 분리가 \(R\)일 때 공통 charge-center \(O\)에서

\[
z_A(R)=-\frac{Z_B}{Z_A+Z_B}R,\qquad
z_B(R)=\frac{Z_A}{Z_A+Z_B}R,\qquad
c_O(R)=\frac{Z_A-Z_B}{2(Z_A+Z_B)}R.
\]

기존 prolate 좌표는 \(\xi=(r_A+r_B)/R\), \(\eta=(r_A-r_B)/R\)이다. 따라서

\[
\rho=\frac R2\sqrt{(\xi^2-1)(1-\eta^2)},\qquad
z=\frac R2\xi\eta+c_O(R),\qquad
\rho\,d\rho\,dz=\frac{R^3}{8}(\xi^2-\eta^2)\,d\xi\,d\eta.
\]

두 \(R\)의 같은 \(\xi,\eta\)는 같은 물리적 위치가 아니다. 또한 두 B 중심 좌표에서 같은 \(z-z_B(R)\)를 사용하는 것은 공통 O 내적이 아니다. 코드에서는 먼저 왼쪽 상태의 quadrature 점을 \((\rho,z)\)로 보내고, 이 물리적 점에서 오른쪽 핵까지 거리를 다시 계산한다.

\[
r'_C=\sqrt{\rho^2+(z-z_C(R'))^2},\quad
\xi'=(r'_A+r'_B)/R',\quad \eta'=(r'_A-r'_B)/R'.
\]

고정된 real azimuthal sector는 \(m=0\)에서 \(1/\sqrt{2\pi}\), \(m>0\)의 cosine sector에서 \(\cos(m\phi)/\sqrt\pi\)이다. 같은 sector의 각도 적분은 1이므로 meridional 함수 \(G\)만으로

\[
S(R,R')=\int_0^\infty\!\rho\,d\rho\int_{-\infty}^{\infty}\!dz\,
G_R(\rho,z)G_{R'}(\rho,z)
\]

를 얻는다. 이는 \(\langle\psi_R,\psi_{R'}\rangle_{L^2(\mathbb R^3)}\)이고 coefficient dot product가 아니다. 실수 상태만 구현했으며 복소 계수는 거부한다. 서로 다른 \(m\), 전하 또는 real azimuthal orientation을 섞지 않는다.

## 2. 유한 영역, 독립 적분, 위상

각 계산 상태는 고유의 \(1\le\xi\le\xi_{\max}\) 밖에서 0으로 연장한다. 바깥 Dirichlet 값이 0인 기존 radial 기저와 일치한다. 내적은 왼쪽 영역 또는 오른쪽 영역을 매개화하여 각각 계산한다. 양쪽 적분이 같아야 하므로 방향 차이를 별도 진단한다. 각 self norm도 각자의 전체 영역에서 적분하며, 한 상태 영역 안에서 다른 상태 norm을 구해 1로 요구하지 않는다.

`pair_overlap(left,right,order)`는 두 방향 raw overlap, 평균, 각 self norm, norm으로 나눈 overlap 및 위상 부호 제안을 반환한다. scalar BSpline을 계수로 한 번 구성해 미분 없는 값을 벡터 평가하고 radial element 하나씩 처리한다. 이 계수 contraction은 함수 평가를 만드는 과정이며 상태 사이의 내적을 대체하지 않는다. float64와 기존 상태 normalization을 그대로 사용한다. radial element들의 최종 합은 `math.fsum`으로 누적한다.

수렴된 \(S\)가 음수면 새 상태의 전체 위상을 \(-1\)배한다. 상태 자체는 이 routine이 변경하지 않는다. 여러 단계의 위상은 앞 단계의 누적 위상과 곱해야 한다. 단지 \(S>0\)이라는 이유로 충분한 continuation이라고 판정하지 않는다.

## 3. 결과 전 고정한 operational 기준

과학적 finite-R 격자는 \([0.25,0.5,1,2,4,8,16]\), continuation 경로는 \([0.25,0.5,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]\)이다. 후자 18점 중 11점은 상태 수송 확인용이다. 관측 결과에 맞춰 격자 또는 기준을 완화하지 않는다.

각 인접 쌍은 order 24와 32를 먼저 비교하고, 사전 지정한 최대 order 48까지만 추가 진단할 수 있다. 채택할 두 order의 raw 양방향 내적 및 normalized overlap 차이 최대가 \(10^{-7}\) 이하여야 한다. 높은 order의 방향 차이와 두 self-norm 오차도 각각 \(10^{-7}\) 이하여야 한다. 수렴된 normalized overlap의 절댓값이 \(0.5\) 이상이어야 양의-overlap 위상을 채택한다. 수치적 Cauchy-Schwarz 검사는 \(|S_{norm}|\le1+10^{-7}\)이다. 실패하면 해당 단계는 `HOLD`이고 phase adoption은 없다. 이 값들은 수치 수송의 사전 operational gate이며 연속체 오차의 엄밀한 bound가 아니다.

희소 과학 격자만으로 common-O continuation을 하는 것이 부적절한 이유는 큰 R에서 확인할 수 있다. He1s 원자 함수가 common O에서 \(\Delta z_B=\Delta R/3\)만큼 이동하면 \(Z_B=2\)에서 원자 overlap은

\[
S_{1s}=e^{-d/a_B}\left(1+d/a_B+\frac{d^2}{3a_B^2}\right),\qquad d=|\Delta R|/3,\quad a_B=1/2.
\]

예를 들어 8→16은 약 0.076으로 작다. 이는 실제 C2 molecular 결과나 허용오차를 계산한 것이 아니라, sparse step이 단순한 공간 이동만으로도 작아질 수 있음을 보여 주는 설계 근거다. 추가 수송점은 \(\Delta R\le1\)로 제한한다. 이 원자 추정으로 molecular overlap을 대신하지 않는다.

## 4. 물리적 claim의 경계

구현은 두 개의 별개 sector에서 가장 낮은 regular 상태를 다룬다. C1의 각 radial/angular Sturm-Liouville ground는 양의 meridional 위상을 고르며, A2의 exact fixed-m lowest-state 정의와 연결된다. 하지만 유한 Galerkin ground 선택, 양의 overlap, 작은 discrete residual은 연속체 projector의 인증된 gap이나 정확한 eigenstate 오차 bound가 아니다. 실제 고립성 근거와 실측 수렴은 별도로 기록해야 한다.

특히 H1s+He n=2의 rank-5 cluster 수송은 여기서 구현·검증하지 않았다. 두 fixed-m sector ground의 overlap을 rank-5 overlap singular value로 부르지 않는다. 단일 상태의 overlap 부호를 polar/Procrustes subspace transport의 대체물로 쓰지 않는다. 본 node가 통과하더라도 전체 R 구간에 대한 검증, 모든 중간 R의 label 수송, collision propagation 또는 Eq55로 확대하지 않는다.

## 5. 구현 검증 범위

`test_continuation.py`는 charge-center/prolate 왕복, 서로 다른 R에서 같은 물리적 점, 선형 radial·상수 angular spline으로 만든 정확한 다항식 self norm, zero extension, 위상 반전, sector 거부 및 실패 시 phase 보류를 검사한다. 제조한 spline의 norm은 다항식 원시함수로 구하며 eigensolve를 호출하지 않는다. Molecular quadrature 수렴은 C2 본 계산의 별도 결과다.
