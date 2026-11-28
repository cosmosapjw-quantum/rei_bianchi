# BASS_HE HE_SIG_DA_ENERGY_COMPAT_20261029: 원자료 조건부 DA/SIG 결합

## 0. 선행 상태와 범위
- 저장소: `cosmosapjw-quantum/BASS_HE`. 선행 Draft PR105 HEAD `88a85c859744a0930b1cb776b4d9e8fa0794976d`; 선행 PR104 HEAD `89325f8510d2af3abe675326720068d0693845b8`.
- 원자료: IAEA-NDS/exfor_master commit `939a14d7bba1ddce51975cb5e8711ce96b3b0871`, `exforall/M04/M0475.x4`; SHA-256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`; Git blob `c49433293921dbb012d7f1b0387745732a598efa`.
- M0475003는 총단면적 SIG 여섯 점(201,225,253,285,320,359 MeV), M0475002는 330 MeV 각도별 DA 네 점(46,61,73,87° CM)을 제공한다. `ERR-S`는 통계오차이다. 오차폭을 **각 좌표별 허용구간**으로 쓰지만 이를 동시 신뢰구간으로 해석하지 않는다.
- 기존 PR105의 `I(L_theta)`는 CM 교환대칭과 azimuth-averaged polar law, 비음수 L_theta-Lipschitz 조건하에서 얻은 full-sphere angular integral이다. 실제 exclusive event sigma와의 계수 κ는 확인되지 않았다. 본 연구의 κ∈{1,2}는 두 가지 *가설*일 뿐 exhaustive convention 목록이 아니다.
- 이 연구는 SIG(E)의 **전 에너지 구간 [201,359]에서 하나의 Lipschitz 상수 K를 추가 가정**한다. 원자료는 K의 상한을 제공하지 않는다. K_min은 이 가정과 통계오차 구간을 동시에 만족할 수 있는 최소 K일 뿐 실제 물리적 매끄러움의 측정치가 아니다.

## 1. 정리 A: SIG 여섯 구간의 정확한 전역 K 최소값
각 에너지 E_i의 허용 SIG 구간을 [a_i,b_i]라 하고, g(E)≥0이며 |g(E)-g(E')|≤K|E-E'|를 요구한다. 이때 허용 함수 존재의 필요충분조건은

    K >= K_SIG := max_{i!=j} (a_i-b_j)_+ / |E_i-E_j|.

증명: 필요성은 g(E_i)≥a_i, g(E_j)≤b_j 및 Lipschitz 부등식에서 즉시 따른다. 충분성은 g_-(E)=max(0,max_i[a_i-K|E-E_i|]), g_+(E)=min_i[b_i+K|E-E_i|]를 구성하면 된다. 이들은 K-Lipschitz이고 모든 E에서 g_-≤g_+이며, 각 측정 에너지에서 해당 구간 안에 있다. (g_-+g_+)/2가 전역 비음수 K-Lipschitz witness다.

EXFOR M0475003를 정확 유리수로 대입하면 최대 항은 E=201 MeV 하한 2.09 nb와 E=225 MeV 상한 1.52 nb의 차이:

    K_SIG = (2.09-1.52)/(225-201) = 19/800 = 0.02375 nb/MeV.

E_*=330 MeV에서, K≥K_SIG를 지정했을 때의 날카로운 가능한 구간은

    S_K(330) = [max(0,max_i(a_i-K|330-E_i|)), min_i(b_i+K|330-E_i|)].

특히 K=K_SIG에서 S_K(330)=[17/80,403/400]=[0.2125,1.0075] nb. 양 끝은 E=320 MeV 행에서 결정된다. 이것은 실측 330 MeV SIG가 아니다.

## 2. 정리 B: 각도-에너지 조건부 결합의 sharp support
선행 PR105가 계산한 330 MeV full-sphere angular integral을 I∈[I_-(L_theta),I_+(L_theta)]라 하자. 추가로 **동일한 underlying event cross section에 대한 가설적 관계** I=κ σ_event(330)를 선언한다. 다른 에너지에서의 DA(E,θ)에는 별도 정칙성을 부과하지 않는다. 그러면 정확한 조건부 가능구간은

    J(K,L_theta,κ) = S_K(330) ∩ [I_-(L_theta)/κ, I_+(L_theta)/κ].

증명: 필요성은 두 개의 독립 제약의 교집합이다. 충분성은 임의 s∈J를 고른 뒤 (i) 정리 A의 여섯 SIG 구간에 330 MeV의 단일점 [s,s]를 추가해 전역 Lipschitz g(E)를 구성하고, (ii) 선행 angular extremal f_-,f_+의 convex combination f_t=(1-t)f_-+t f_+, t=(κs-I_-)/(I_+-I_-)∈[0,1]을 택하면 I=κs가 된다. 따라서 J의 모든 점은 이 **분리형 제약 모델** 안에서 달성 가능하다. 다른 에너지의 DA에 에너지 정칙성을 부과하면 충분성은 재검토해야 한다.

이 결합이 가능해지는 최소 에너지 K는

    K_crit(L_theta,κ) = max{K_SIG, max_i (a_i-I_+/κ)_+/|330-E_i|, max_i (I_-/κ-b_i)_+/|330-E_i|}.

선행 angular decimal endpoints는 exact geometry의 고정밀 근사이며 outward-rounded interval 증명은 없다. 따라서 위 정리의 함수식은 exact이나 아래 decimal 값은 numerically checked approximation이다.

## 3. 계산 예시: κ=1/2는 실험적으로 확정된 선택이 아니다
K=K_SIG=0.02375 nb/MeV, L_theta=1/200=0.005 nb/sr/degree를 가정하면 선행 I∈[1.006886048242943325...,2.423539172537023885...] nb와 결합하여

- κ=1: σ_event(330)∈[1.006886048242943325...,1.0075] nb, 폭 약 0.000613951757056675 nb.
- κ=2: σ_event(330)∈[0.503443024121471663...,1.0075] nb.

반면 L_theta=1/700일 때 κ=1은 K=K_SIG와 양립 불가능하며, κ=2는 가능하다. 이때 κ=1의 최소 K는 약 0.059660907123485615 nb/MeV이고 κ=2의 최소 K는 0.02375 nb/MeV이다. K=K_SIG 고정에서 κ=1의 각도 임계값은 독립 analytic-piece integration과 이분법으로 L_theta,crit≈0.00499189684749502446749 nb/sr/degree로 수치 확인했다. 이것은 **추가 가정들의 상호 양립성 진단**이지 κ=1이 물리적으로 배제된다는 증명이 아니다.

## 4. 보존되는 물리 blocker
원 논문의 coincidence/acceptance·효율·동일 D particle/event convention은 EXFOR raw 필드만으로 확정되지 않는다. 액체 He 표적의 반응 매질·운동·beam response, 실제 photon spectrum/history, polarisation, 독립 비열평형 fast-D source와 stopping/deposition/C_v가 필요하다. R_event=null, physical_activation=false, L4=false, production=HOLD. 원 물리 DAG 28/88, HE 14/18 및 선행 조건부 2/2는 증가시키지 않는다.

## 5. 검증 상태
- Wolfram Language: 정확 유리수 K_SIG=19/800, S_K(330)=[17/80,403/400] 검산.
- Python 3.13.5: 새 25개 targeted tests PASS, 처음 empty-source test FAIL 뒤 진단된 입력 검증 결함을 한 차례 수정하여 PASS. 원 BASS_HE full suite/IVP 재실행 없음.
- 독립 알고리즘: scipy HiGHS 7변수 LP에서 κ=1/2, L_theta=1/700,1/200,1/100 여섯 경우의 가능성과 양 끝을 formula와 1e-8 nb 이내 비교. 독립 analytic angular quadrature로 임계값 계산.
- Figure: Kcrit(L_theta), full-scale joint support, κ=1 zoom; 과장된 실측 해석 방지를 위한 축/캡션 검토. 독립 native subagent reviewer NOT_RUN.
