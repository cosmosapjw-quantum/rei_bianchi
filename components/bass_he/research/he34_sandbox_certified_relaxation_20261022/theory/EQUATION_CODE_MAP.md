# HE34-SCR 식–데이터–코드 계약

workflow1.0.0 / approval0.2를 유지한다. 이 단원은 원전에서 지지하는 수송식, 새로 유도한 연속계 축약 상한, 실제 binary64 실행을 구별한다.

## 기계적 pressure model

`D=diag(-1,-1,2)`, `P=p I+q D`, `sigma=s D`이며 `r=q/p`, `N=ln(a/a0)`, `S=s/H`, `chi=nu_pi/H>0`이다. 여기서는 `chi`가 상수이고 `Q=j=0`이다. `u=ln[(p/p0)exp(5N)]`이므로 팽창의 `a^-5` 인자는 정확히 제거된다. `S`는 저장 배경의 201개 node를 잇는 부호 있는 선형 보간으로 **정의된 입력**이다.

| 물리/수학 항목 | 구현 | 검증 근거 |
|---|---|---|
| `r'=4Sr²-(chi+2S)r-2S`, `u'=-4Sr` | `src/certified_relaxation.py: solve_reduced` | `CERTIFIED_REDUCTION.md`, Wolfram identity, 독립 eigenpressure reference |
| 안정근 `b=-4S/(chi+2S+D)` | `_root`의 scaled hypot와 유리화 | constant-source matrix exponential, 부호가 바뀌는 별도 source |
| 정확한 frozen nonlinear 초기층 | `_candidate`의 `expm1` denominator | arbitrary admissible r0, `chi*h=1e14` Laplace moment 검산 |
| residual 및 contractive envelope | `solve_reduced`, `_propagate_bounds`, `_relaxation_integrals` | 유도된 `E,L`; 독립 고정밀 식과 source-varying control |
| pressure 적분 | `_constant_pressure`, `_pressure_increment` | constant-source 폐형식, rescaled-layer quadrature, tail bound |
| 연속계 수용 | `ReducedSolution.certified` | max E와 final L 각각 `1e-6` 이하 |
| 별도 수치 수용 | `run_control.py: require_numerics` | 유효한 approximation, quadrature convergence, 유한 estimate+tail `<=1e-9` |
| 독립 완전 pressure 대조 | `run_control.py: full_moments` | `Wperp,Wparallel` 두 선형 방정식의 segmented Radau |

`CERTIFIED_REDUCTION.md`의 대칭 cone 조건 `B+A<=1/2`는 충분조건이다. 실제 구현은 `b(S)`와 초기층의 해석적 단조 구간을 함께 사용한다. 두 항의 같은 방향 단조성이 증명되면 양 끝점으로, 그렇지 않으면 두 정확한 범위의 합으로 cone 포함을 확인한다. 따라서 물리 경계 `r0=-1/2,1`도 조건을 증명할 수 있는 경우 허용한다. 독립 리뷰가 이 확장을 재유도했다. sampling만으로 cone을 승인하지 않는다.

`certified=True`는 연속계 축약 오차에 관한 값이다. 이것만으로 수치 구적의 수렴을 뜻하지 않는다. root driver가 별도의 수치 gate를 강제한다. interval arithmetic를 쓰는 outward-rounded machine certificate는 구현하지 않았다. `kappa=chi-6 max|S|<=0`이면 이 상한을 사용하지 않는 것이며 원래 pressure equation의 부정적 결과를 뜻하지 않는다.

## 중성 H1/He4 점성

| 원전량/계산 | 구현 | 고정된 정규화 |
|---|---|---|
| Bruno collision fit 네 행 | `neutral_transport.collision_integral` | `Qbar=pi*1e-20*F(T)` m²; T 범위 50–50000 K |
| 순수 점성 및 nD | `prepare_neutral_transport` | 호출자가 질량 제공; kB SI 정의값 |
| 2×2 Chapman–Enskog 계의 정확한 유리 축약 | `NeutralTransport.viscosity`와 `viscosity_vectorized` | 공통 weight scale만 제거; floor, clipping 없음 |
| 저장 조성으로 neutral density 계산 | `checks/check_transport.py: load_background` | HE32의 fixed reference-H nucleus density; neutral-H를 분모로 사용하지 않음 |
| 물리 진단 | `checks/check_transport.py` | T=20000 K, mass convention A*m_u; `nu_match=p_neutral/eta` |

이 `nu_match`는 저주파 점성 일치의 정의다. PR87의 Lorentz instantaneous Grad projection이나 정확한 transient relaxation spectrum과 같다고 놓지 않는다. 이 값을 현재 constant-chi 기계 대조 계산에 삽입하지 않았다. 서로 다른 결과 파일과 명시적인 scope flag로 보존했다.

## source-stage 원본 파일과 현재 패키지의 대응

원본 유도 문서는 당시 prototype의 이름과 명령을 보존한다. 현재 패키지 경로는 다음과 같다.

| 원본 기록 이름 | 패키지 경로 |
|---|---|
| reduction `WOLFRAM_CHECK.json` | `evidence/prototypes/REDUCTION_WOLFRAM.json` |
| reduction `CONTROL_RESULTS.json` | `evidence/prototypes/REDUCTION_CONTROLS.json` |
| reduction `MANIFEST.json` | `evidence/prototypes/REDUCTION_MANIFEST.json` |
| transport `GENERAL_WEIGHTS_WOLFRAM.json` | `evidence/prototypes/TRANSPORT_WOLFRAM.json` |
| transport `REDUCTION_WOLFRAM.json` | `evidence/prototypes/TRANSPORT_SIMPLEX_WOLFRAM.json` |
| transport `PROTOTYPE_EXECUTION.json` | `evidence/prototypes/TRANSPORT_EXECUTION.json` |
| transport `UPSTREAM_MANIFEST.json` | `evidence/prototypes/TRANSPORT_UPSTREAM_MANIFEST.json` |

Prototype의 질량 `1.66053906660e-27 kg`는 당시 시험 매개변수였다. 실제 저장 배경 진단은 HE32/SciPy1.17의 `m_u=1.66053906892e-27 kg`를 명시해서 실행했다. 당시 prototype의 “benchmark 미실행” 문장은 그 단계의 상태이며, 현재 단계의 새 benchmark는 `results/NEUTRAL_TRANSPORT.json`과 `results/MECHANICAL_CONTROLS.json`에 있다. 원전 파일의 blob/hash를 확인한 기록은 보존하되 원문 PDF를 재배포하지 않는다.

## 재실행 정책

완료 receipt와 현재 code/input hash가 일치하면 이미 완료된 과학 실행을 재사용한다. `run_control.py`의 기본 재호출은 dependency-matched cache를 확인하고 `REUSED_COMPLETE_MECHANICAL_CONTROL`을 출력한다. 입력·코드가 달라졌으면 기존 결과를 먼저 보존하고 변경의 영향을 받는 새 검증만 명시적 이유와 함께 수행한다. `checks/check_transport.py`는 새 실행을 일으키므로 완료된 현 상태의 기본 재개 명령으로 사용하지 않는다.
