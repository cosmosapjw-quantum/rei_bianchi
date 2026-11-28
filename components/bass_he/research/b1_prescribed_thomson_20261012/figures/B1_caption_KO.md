# B1 overview — 그림 설명

처방된 전자 이력과 Liouville–편광 Thomson 수송의 첫 비교다. 초기 복사장은 기존
BASS benchmark의 등방·비편광 Planck test field이며 이후 photon emissivity는 0이다.
기하와 전자 이력은 평균 부피 redshift 20→4 구간으로 고정했다. B는 초기 s/H=+0.1인
LRS Bianchi I, M은 같은 평균 H와 같은 B 전자 이력을 갖는 등방 대조군,
B0는 B와 같은 기하에서 충돌 깊이만 0인 경우다. B_F와 M_F는 각각 같은 기하에
FLRW 전자 이력을 공통 B proper clock으로 처방한 경우다.

(a) 마지막 평균 z=4에서의 정규화된 사중극 q2. B와 B0의 차이는 실제 산란 효과이며
M은 등방 대조군이다. (b) 같은 시각에서 전단축에 수직한 방향(mu=0)의 선형 편광도.
세로축 단위는 percent이므로 0.30은 pL=0.003을 뜻한다. (c) 같은 기하와 평균 팽창에서
전자 이력만 바꾼 방향 반응의 차이, delta_hist q2=(B−M)−(B_F−M_F).
세로축은 10^-6 단위다. (d) 지정한 여섯 y에서 마지막 history 반응의 절댓값과
timestep·각도·에너지 해상도를 각각 높였을 때의 paired 반응 변화 절댓값의 합이다.
이 합은 이번 실행에서 관측한 수치 민감도이며 엄밀 오차 상계나 전체 물리 불확실성이 아니다.

가로축 y=(a/a_i)E/(k_B T_gamma,i)는 평균 팽창을 제거한 무차원 에너지 좌표다.
물리 에너지는 E/(k_B T_gamma,i)=y exp(-u), u=ln(a/a_i)다. a_i=1/21이며
가스의 처방 온도 20000 K를 복사 초기 온도 T_gamma,i와 동일시하지 않는다.

모든 그림은 저장된 실제 실행 결과만 후처리했다. 사용한 충돌 backend는 기존 BASS
Python 구현이며 이번 그림이 native Rust 실행을 증명하지 않는다. 유한 구간의
test-field/elastic Thomson 결과로, observer tail·관측 CMB C_l·전체 광학깊이 예측은 아니다.

재현 명령: `python3 figures/make_figures.py`.
스크립트는 각 result.npz를 해당 실제 실행 영수증의 SHA에 대조하고, 물리 solver를
호출하지 않고 `B1_overview.png`와 `B1_overview.pdf`를 생성한다.
