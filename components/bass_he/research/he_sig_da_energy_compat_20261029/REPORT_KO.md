# BASS_HE 후속 이론·코딩 루프 결과 (2026-10-29)

## 실행 기준
- 새 단위 `HE_SIG_DA_ENERGY_COMPAT_20261029`, 부모 `BASS_HE` PR105 `88a85c859744a0930b1cb776b4d9e8fa0794976d`.
- IAEA EXFOR M0475 source commit `939a14d7bba1ddce51975cb5e8711ce96b3b0871`; source SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`, Git blob `c49433293921dbb012d7f1b0387745732a598efa`.
- 기존 중앙 DAG `28/88`, HE `14/18`, 선행 조건부 `2/2` 유지. 새 국소 DAG `1/2` scoped admission, 둘째 노드는 native 독립심사 미실시로 pending. 물리 DAG delta=0.

## 새 결과
원 EXFOR M0475003 SIG 여섯 행의 통계오차 구간을 동시에 관통하는 비음수 전역 Lipschitz σ(E)의 최소 K는 **19/800 = 0.02375 nb/MeV**, 결정 pair는 201 MeV 하한 2.09 nb 및 225 MeV 상한 1.52 nb. 이 최소 K를 별도 **가정**하면 330 MeV SIG 가능 구간은 정확히 **[17/80,403/400]=[0.2125,1.0075] nb**. 원자료에는 330 MeV SIG 실측값이 없다. Kmin은 실험적으로 확인된 K 상한이 아니다.

기존 PR105의 비음수 각도 Lipschitz full-sphere I 구간과 가설 `I=kappa*sigma_event`를 결합하여 sharp support `J=S_K(330)∩[I_-/kappa,I_+/kappa]`와 Kcrit(Ltheta,kappa) 정리를 증명하고 constructive witnesses를 제시했다. `K=19/800`, `Ltheta=1/200`일 때:
- kappa=1: **[1.006886048242943325...,1.0075] nb** (폭 0.000613951757... nb).
- kappa=2: **[0.503443024121471663...,1.0075] nb**.

`Ltheta=1/700`에서 kappa=1은 이 최소 K와 양립 불가능, kappa=2는 양립 가능. kappa=1의 요구 최소 K는 0.059660907123485615 nb/MeV. `K=19/800`에서 kappa=1의 각도 임계 Ltheta는 약 **0.00499189684749502447 nb/sr/degree**. 모두 선언된 두 Lipschitz 가정, 좌표별 ERR-S 구간, PR105의 각도 교환대칭/azimuth 조건, 가설적 kappa에 의존한다.

## 실제 코드·검증
- Python3.13.5, 정확 `fractions.Fraction` 원자료·K·SIG 구간 및 constructive energy witness, Decimal80-digit angular endpoint 결합. `src/sig_da_bridge.py`.
- `python -m unittest discover -s tests -v`: **25/25 PASS**. 최초 `empty rows -> K=0` 결함 1개를 수정하고 재검사했다. EXFOR 원본 byte hash, source mutation, float/bool, kappa gate, conservation of Lipschitz constraints 포함.
- 별도 `scipy.optimize.linprog` HiGHS 7변수 finite LP: 6/6 가설/각도 조합에서 공식과 양 끝 차이 <1e-8 nb, incompatible case 검출.
- 별도 mpmath active-line exact breakpoint + analytic angular primitive + bisection으로 Ltheta,crit 계산. Wolfram 정확 유리수 `{19/800,17/80,403/400}` 확인.
- 세 그림 `results/Kcrit_vs_Ltheta.png`, `results/joint_support_kappa.png`, `results/kappa1_zoom.png` 생성 및 실제 열람. Full-scale에서 kappa1의 작은 구간이 점으로 보이는 문제를 zoom 그림으로 보완.
- 이전 BASS_HE full science suite, production IVP, source 15행 및 PR105 계산은 재실행하지 않았다. 새 테스트만 수행.

## 심사와 admission
- R6: CAS 및 독립 수치 알고리즘 교차검산 수행. 별도 native subagent reviewer `NOT_RUN`.
- C9: 본 세션의 bounded source/physics/plot review 수행. 별도 native subagent reviewer `NOT_RUN`; 둘째 조건부 DAG 노드 최종 승격 보류.
- 실험적 event/particle·half/full-sphere normalization, detector efficiency, liquid-He target response, photon field/history, actual angular/polarization law, named fast-D stopping/deposition/Cv는 unresolved.
- `R_event=null`, `physical_activation=false`, `L4=false`, `production=HOLD`. 이번 숫자를 실측 330 MeV total cross section 또는 물리적 사건률로 표기하지 않는다.

## 다음 실행
1. Arends 1976 원 논문/학위논문에서 coincidence event/particle normalization과 검출효율, 표적·beam response의 원문 정의를 source-lock.
2. 같은 물리 quantity임을 확인한 후, 실제 330 MeV total/exclusive event source 또는 오차가 인증된 외삽 모델을 결속. 그전에는 κ와 K를 가설로 유지.
3. 별도 native R6/C9 심사 후 둘째 조건부 노드 admission 결정. 물리 source 승격은 이와 별개.
4. 실제 photon history 및 target frame, named D fast pool과 stopping/deposition 연결. 기존 DAG와 완료된 계산 재실행 금지.
