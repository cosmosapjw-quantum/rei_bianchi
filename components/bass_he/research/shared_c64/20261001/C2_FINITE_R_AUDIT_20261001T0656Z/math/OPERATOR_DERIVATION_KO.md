# C2 유한 R 연산자와 판정 범위

단위는 a_A, E_A, hbar이며 전하수 ZA=1, ZB=2이다. 핵 사이 반발 상수는 전자 Hamiltonian에 더하지 않는다. 모든 행렬원소의 원점 O는 물리적 전하중심이다. 수치 원점 B를 쓰는 독립 구면 전개와 비교할 때 z_B=ZA R/(ZA+ZB)만큼 평행이동한다.

Lbar_O=<g|L_y|b>/(-i hbar), pbar_x=<g|p_x|b>/(-i hbar/a_A)로 놓으면 Lbar_O=Lbar_B+z_B pbar_x이다. g의 방위각 인자는 1/sqrt(2pi), 밝은 b는 cos(phi)/sqrt(pi)이다. 타원좌표 meridional 진폭을 G,A라 할 때 physical measure는 rho d(rho) dz=R^3/8 (xi^2-eta^2) dxi deta이다. 원점 O에서 z=R xi eta/2+(ZA-ZB)R/[2(ZA+ZB)]이다.

독립 direct lane은 좌표 Jacobian을 역변환하여 A_rho,A_z를 구하고, pbar_x=integral G(A_rho+A/rho)/sqrt(2), Lbar_O=integral G[z(A_rho+A/rho)-rho A_z]/sqrt(2)를 평가한다. p는 에너지 차이나 dipole에서 역산하지 않는다.

force lane은 미분을 사용하지 않고 T_C=integral rho G A/[sqrt(2) r_C^3]를 각각 계산한다. Delta=E_b-E_g>0에 대해 Lbar_O=ZA ZB R(T_B-T_A)/[(ZA+ZB)Delta], Lbar_B=-ZA R T_A/Delta이다. Coulomb 두 끝점에서는 Duffy 변환을 사용한다. 이 구현은 direct와 배열을 공유하지 않으며 동일한 Galerkin 행렬의 commutator 곱으로 대체하지 않는다. 두 lane의 일치는 수치 검증 자료이며 연속공간 오차 상한은 아니다.

어두운 partner는 같은 |m|=1 진폭에 sin(phi)/sqrt(pi)를 곱한다. 미분 후 남는 phi 인자는 sin(phi)cos(phi)/(sqrt(2)pi)이며 meridional 인자는 z(A_rho-A/rho)-rho A_z이다. 32/64개 방위각 표본으로 실제 합을 계산한다. 수학적 영을 하드코딩하지 않는다. 이는 축대칭 모형의 azimuthal 선택규칙 진단이며 새로운 독립 dark 고유상태 계산 또는 수치 대칭 깨짐 연구는 아니다.

C1b에서 닫힌 것은 R=2의 경험적 독립 수렴이다. 이번 격자에서는 각 R에서 h, p, tail을 별도로 바꾸며 tail 변화는 64개 내부 radial cell을 그대로 두고 16개를 덧붙인다. 작은 residual, 밝은 상태 비영 또는 dark 영만으로 공간 수렴을 선언하지 않는다. 물리적 상태 겹침은 별도 공통 O 적분으로 검증한다.

A2의 소/대 R 계수와의 scaled 비교는 측정된 유한 점에서의 진단이다. R→0 또는 R→infinity의 오차, 미지의 Big-O 상수, collision 전체 구간이나 rank-5 cluster의 closure를 이 일곱 점으로 인증하지 않는다. scientific_PROMOTE=HOLD, Eq55=NOT_RUN을 유지한다.
