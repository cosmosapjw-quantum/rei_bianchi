# HE32 최종 코딩 C1–C10: 실행 계약

## C1 목표와 baseline

HE31 전달 commit `88e415c45d8607c85cd3ab36aabeaed4378820ce`에서 분기했다.
HE32 최적화 checkpoint는 `e8bb035d31f59e34734947b9082bdbd60128b799`, PR85다.
이 단계는 물리 R1–R10의 명시적 UV photo/RR 모델을 실제로 z20→2 적분하여
392개 sweep, 21개 isotope/ion population, 물질·광자·중성미자의 stress와
6개 그림을 만든다. 수치 실행은 sandbox에서 끝내며, NCP 접속이나 빌드는
완료의 선행조건이 아니다. 상세 성능 벤치마크는 요청 범위에서 제외한다.

## C2 식–데이터–코드 대응

| 물리식/입력 | 구현 | 출력 |
|---|---|---|
| source-pinned Einstein/FV/even hierarchy | `src/compact_transport.py` | H, b, signed shear, gamma/nu towers |
| Verner photo + VF total RR | `src/atomic_photo_rr.py`, `data/ATOMIC_PHOTO_RR.json` | 여섯 전이쌍의 rate |
| 핵종 조성, 외부 UV와 T | `data/ISOTOPE_SCENARIO.json` | 초기 분율·조성·scope |
| 9분율 invariant와 full21 대조 | `src/primordial_network.py` | 21 abundance, 핵종별 전자 census |
| d f/dη=Q(ne,z)f/H_target | `src/coupled_pilot.py` | 각 궤적의 실제 화학 이력 |
| dτ/dη=cσT ne/H_target | 동일 ODE | 누적 Thomson optical depth |
| d[e^(3η)s/Href]/dη=e^(3η)3H0²π_X/(Href H) | 동일 ODE의 3개 budget 성분 | I_m,I_gamma,I_nu 및 residual |
| 실제 저장 결과만 그림으로 변환 | `src/plot_pilot.py` | PNG/SVG/CSV와 입력 SHA manifest |

H에는 isotropic baryonic rest density가 포함된다. 여기서 π_m은 fm=.1의
별도 nonbaryonic collisionless massive sector이며, primordial atomic gas는
명시적인 π_b=0 closure다. 단순히 non-tilted라는 조건으로 π_b=0를 도출하지 않는다.
Π_r는 photon과 neutrino의 부호 있는 LRS 성분을 더한 후 norm을 취한다.

## C3 수치 설계

각분포의 reflection-even invariant를 써서 L16 transport를39변수로 계산한다.
화학9, optical depth1, source budget3을 더하면 nominal state는52개다.
기본 FV는24×12 cells, cell당 Gauss order3을 유지한다. 초기 각분포
W=1+A P2가 −1≤A≤2에서 비음수인 조건을 모든 grid point에서 검사한다.

화학의 Γ/H가 큰 후기 구간 때문에 SciPy1.17의 BDF를 사용한다.
rtol=3e-11, atol=3e-13, max Δη=.025, 저장 node201이다.
동일 21개 abundance를 직접 적분하는 대신 원소별 charge fraction을 써서
Li6/H=1e-14의 작은 조성이 solver absolute tolerance 아래로 사라지는 문제를 피한다.
수치 결과의 음수나 simplex 잔차를 clipping/renormalization으로 숨기지 않는다.

Jacobian은 화학 generator와 ∂ne/∂f의 exact9×9 block, radiation linear
blocks를 사용한다. H와 FV moment에 걸린 b,q,E_gamma0,E_nu0의 네 smooth
geometry column만 central differences로 계산한다. 독립 directional derivative
검산이 이 혼합 Jacobian의 구현을 확인한다. 이 방법의 성능 배수를 주장하지 않는다.

## C4 실행 DAG와 자원

`run.sh` → 세 nominal boundary/control + 두 L24 angular guard → guard 판정
→ 나머지389개 새 nominal trajectory → 전체392 catalog → six figure pairs.
preflight의3개 nominal은 같은 identity로 본 sweep에서 재사용된다.
초기 빈 저장소 기준 새 과학 IVP는394개다. 기존 optimization의 paired IVP4개와
이 숫자를 섞지 않는다. 실패·중도결과와 실행 receipt는 보존한다.

HE30/C21K의 협동 실행기를 재사용한다. 현재 CPU affinity, cgroup quota,
실제 CPU busy와 RAM headroom을 관찰하며 공유 CPU/case lease를 획득한다.
한 worker의 native thread는1개, 동시에 최대64 workers, 기본 여유 CPU2개,
RAM16GiB이며 작은 host에서는 여유 RAM을 총량/8로 제한한다. 다른 작업은
중단하거나 신호를 보내지 않는다. 이 sandbox의 quota8 CPU/8GiB에 자동 적응하며
NCP64 CPU/128GiB에서도 같은 admission contract로 빈 자원을 사용한다.
1GiB/worker는 admission 예산이고 실제 RSS 측정 또는 성능 벤치마크가 아니다.

## C5 구현과 재개

source/data/config/runtime identity에 해당하는 완료 결과만 재사용한다.
NPZ에 메타데이터를 함께 넣고 create-only 원자적 저장을 수행한다. JSON 저장만
중단된 경우 `recover_receipt()`로 과학 적분 없이 복구할 수 있다.
실패한 identity를 다른 출력 폴더에서 조용히 반복하지 않는다. 미실행 DEFERRED
case는 다음 호출에서 남은 자원으로 이어간다. presentation 수정은 saved-data
렌더만 새 폴더에 수행하며 과학 입력이나 결과를 변경하지 않는다.

## C6–C9 필요한 검증과 수용 기준

- 원자율 원표/독립 provider 대조, full21↔9분율 RHS, weak operator baryon/charge
  보존, 화학·결합 Jacobian, output serialization/cache identity를 점검한다.
- 모든 actual case는 solver z2 도달, finite, ion simplex, 양의 sampled brightness,
  comoving particle number, optical-depth 단조성, 60eV에서 high-Li zero invariant,
  chart/domain 및 nuclear-freezeout 시간/밀도 envelope를 검사한다.
- source-budget absolute residual≤3e-8; isotope fraction 최소≥−2e-10,
  simplex residual≤2e-9. 음수 허용폭은 numerical acceptance이며 물리적 음의
  population을 뜻하지 않는다. 원자료는 그대로 보존한다.
- 두 강한 shear corner의 L16↔L24 비교는 실제 numerical risk에 대한 작은 guard다.
  saved-trajectory 최대 차이: signedΣ≤3e-7, Pm≤3e-8, Pr≤3e-7,
  ne relative≤3e-5, ion fraction absolute≤3e-5. 이 두 점 검사는
  전체 parameter domain에 대한 엄밀한 truncation certificate가 아니다.
- 별도 reviewer가 식·Jacobian·failure/reuse·figure 축/부호·실제 원자료를 검토한다.

## C10 전달 계약

최종 `RESULTS_KO.md`, `results/SUMMARY.json`, `results/ANGULAR_GUARDS.json`,
독립 검토, 실제 그림, source/runtime/input identity, Git publication readback,
Drive/Dropbox provider ACK를 연결한다. `DAG.json`은 단계별 status/backup/
publication/next를, `checkpoints/`는 create-only snapshot을 유지한다.
코드와 NCP/Codex 및 다음 대화 handoff는 결과 완성 후 고정한다.

기술 원전: https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.solve_ivp.html
