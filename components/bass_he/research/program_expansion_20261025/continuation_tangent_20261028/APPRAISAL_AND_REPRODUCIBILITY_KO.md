# TANGENT13 R8/C8 — 판정, 오차, 재현성

## 채택할 결과

제안 판정은 **ACCEPT_SCOPED_FULL_QUARTIC_MINIMUM_REFERENCE**다. 실제 EXFOR M0475002의 258 MeV 네 DCS점에 고정한 deterministic coordinate ERR-S 창, free endpoints, full nonnegative even-quartic family, 기존 detector moments와 uniform azimuth 조건에서 HEMISPHERES와 CAPS의 최솟값을 각각 폭 `<=1e-10`인 정확한 유리수 구간으로 감쌌다. 실제 폭은 약 `8.794662532001996e-15`, `1.6987466706439967e-14`다. C9의 최종 독립 admission 전 로컬 카운트는 12/17이며, admission 후 추가되는 것은 이 scoped reference 1개다.

## 수치 오차와 안정성의 실제 근거

전체 construction과 certificate 판정은 Python 표준 라이브러리 `Fraction`으로 수행했다. 비트 정밀도나 floating optimizer convergence에 의존하지 않는다. 부동소수점은 읽기 쉬운 표시와 저장값 plot에만 사용하며, 정확한 양 끝점·폭·부등식은 fraction으로 보존한다.

Root isolation은 outer/inner 각각 80회 유리수 이분법으로 수행했고, bracket 폭은 `1/(10*2^80)`, 약 `8.271806125530277e-26` 이하이다. 양 끝점 부호와 affine derivative 양성이 하나의 root를 `[4/5,9/10]`에서 격리한다. 이 결과가 그 구간 밖의 root를 배제하지는 않는다. Dual은 임의의 유리수 `r_out in [0,1]`에서의 평가 functional을 사용하므로, 최종 정확한 항등식과 multiplier 부호가 성립하면 root 근사의 정확성에 최적성 주장을 맡길 필요가 없다.

| 항목 | HEMISPHERES | CAPS |
|---|---:|---:|
| 저장된 `alpha`의 근삿값 | 0.6184085476376278 | 0.06075688134522765 |
| `lambda` 근삿값 | 0.601601498245952 | 0.5497440790323624 |
| `mu` 근삿값 | 0.16413062836207484 | 0.4105292450263255 |
| 정확한 dual 잔차 | (0,0,0) | (0,0,0) |
| `Delta_k` 근삿값 | 3.9091883949021255e-15 | 8.326021635113347e-15 |
| 최종 exact fraction 폭의 근삿값 | 8.794662532001996e-15 | 1.6987466706439967e-14 |

`Delta_k`는 saved moment intervals 전체를 포함하는 균일한 목적함수 보정이다. `M_j`의 근삿값은 `(1.0082293602815142, 2.3372538004267818, 2.3054443895846517)`이며, 실제 비교는 재사용 outer N16의 8개 저장 정점에서 정확히 계산했다. 정점 완전성은 QUARTIC12의 기존 proof와 source identity를 재사용한다. 정점 재열거, trigonometry, geometry solver, predecessor campaign은 호출하지 않았다.

최종 폭에는 row 확장/수축 차이, 유리수 후보 및 scale의 차이, moment enclosure를 모두 포함한다. 위 표는 실험 오차가 `1e-14` 수준이라는 뜻이 아니다. 원래 넓은 ERR-S 창을 고정한 최적화 문제의 **최소값 계산 오차**다. Window를 통계적 동시 신뢰구간으로 해석하거나 좁힌 적이 없다. M0475003의 에너지격자가 다른 총단면적 6점도 결합·보간하지 않았다.

분모 floor와 coefficient box가 유지되므로 부호가 다른 coefficient 때문에 interval arithmetic 방향이 바뀌는 위험을 명시적으로 처리할 수 있다. Exact singular-system/negative-multiplier/witness/window/width rejection controls가 통과했다. 목표를 이미 충족했으므로 해상도 sweep이나 추가 정밀도 시험을 새로 수행하지 않는다.

## Saved-only plot 판정

PNG/SVG 1회 생성은 exit0, saved-only=true, science calls0으로 완료됐다. Full CPU1.438273 s, wall1.388089466 s, maximum child RSS62640 KiB, caps CPU10/wall30/AS768 MiB/thread1이다. 파일과 receipt는 `evidence/plot/initial/`에 있다.

Root와 nonauthor reviewer가 실제 PNG를 읽었다. 상단의 bracket 숫자·선·폭은 읽을 수 있으나, 약 `1e-14` 범위의 numeric x tick labels와 offset이 겹친다. 이 시각적 한계를 `review/PLOT_REPORT_REVIEW.json`의 **PASS_SCOPED_WITH_DISPLAY_LIMITATION**으로 보존한다. 주황색 점은 표시 구간의 중점이며 물리적 최적 추정량이 아니다. 정확한 값은 본문의 표와 saved certificate를 사용한다. 허용된 1회 render 이후 재계산이나 추가 render를 하지 않았다.

## NG1–NG7 screen

이번 결과는 feasible square와 전역 하한 certificate의 구성이다. 새로운 strong no-go로 채택하지 않는다.

| 기준 | 실제 적용과 근거 |
|---|---|
| NG1 대상·양화 | CONTRACT/THEORY: 고정된 258 MeV full nonnegative even-quartic/data family의 모든 b에 대한 하한 |
| NG2 증명의 닫힘 | THEORY §§2–8과 실제 dual/witness/interval certificate로 해당 minimum bracket 증명 |
| NG3 비공허성 | 네 contracted windows를 통과한 양의 a를 가진 실제 square witness |
| NG4 기작 | 선택 data functional h와 nonnegative-cone evaluation functional의 양의 조합; 배제 기작을 주장하지 않음 |
| NG5 과학적 의미 | 기존 QUARTIC12 최소값 bracket의 full-cone 간격을 닫아 data-conditioned aperture reference 개선 |
| NG6 문헌 대비 | Markov–Lukacs positivity와 Charnes–Cooper fractional optimization은 선행 수학; 일반 정리의 새로움을 주장하지 않음. 정확한 현 자료 적용 결과를 제시 |
| NG7 범위·독립 검토 | 비저자 한 pass가 proof/source/실제 certificate/CAS/plot의 범위 일치를 검토. 전체 물리 가능성 배제 또는 production admission으로 확대하지 않음 |

## 재현 identity와 실행 기록

초기 실행 source S05는 `60df32e41ad6ca344c45eeeae516b3da85d90a92`, 교정된 실제 성공 실행 pin R01은 `3beb35dc7dea7a60642497dc373c98e75ca07536`, tree `8ac705d920a7faf1da7b3c4d83ecf0e3b0f9a2dd`다. 로컬은 복원한 partial source mirror이며 local Git D commit은 없다.

정확한 명령, Python executable 경로, threads=1, limits와 source/input hashes는 validation/plot 각각의 `START.json`에 있다. 이번 턴의 `sources/runtime_probe.json`은 Python3.12.14를 기록하며, 명시적 thread environment 설정은 게시된 `scripts/run_once.py`에 있다. 실행 시점의 platform 상세와 matplotlib version 및 전체 environment를 별도로 캡처했다고 주장하지 않는다. Random seed는 사용하지 않는다. 과학 코드는 표준 라이브러리만 사용하고, plot은 해당 실행 환경의 matplotlib에서 저장값을 읽었다. 원래 실패·진단·targeted retry의 비용과 reserve 이력은 `VALIDATION_KO.md`와 원시 receipts를 참조한다. 현재 새 science repair reserve는 0이다.

복원이나 감사 시에는 먼저 source와 입력 identity, 저장된 certificate와 receipt를 읽는다. 이 완료된 단위를 다시 실행하는 것은 현재 후속 작업이 아니다. 관련 입력·정의·구현이 바뀌는 새 명시적 작업이 생기면 그 의존성을 처음 사용하는 단계부터 새 계약으로 다룬다.

## 열린 물리 입력과 owner

Event/inclusive normalization 및 liquid-He medium/response projection, actual full angular/polarization law 및 photon encounter flux/history, named nonthermal birth/deposition/thermalization 및 global species binding의 세 입력 묶음은 계속 open이다. `population_rest_energy_witness`가 sole binding owner다. 독립 binding RHS와 `Gamma_thermal`, `Cv`, `species_heating`, `thermal_deposition`은 null, `birth_pool=UNASSIGNED`, `global_physical_completion=null`, `L4=false`, `production=NOT_APPROVED`, `activation=false`를 유지한다. 중앙 **28/88, HE delta0**이다.
