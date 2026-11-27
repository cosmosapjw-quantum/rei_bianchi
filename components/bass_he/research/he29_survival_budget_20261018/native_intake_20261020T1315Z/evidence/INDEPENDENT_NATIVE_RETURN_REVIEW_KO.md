# HE29 새 native 반환 독립 검토

판정: **PASS_SCOPED — 네 기준해4/4를 원래 finite-model 계약에서 수용 가능**. 이번 검토는 새 반환 자료의 계약·해석 검토이며 완료된 코드감사·검사·적분은 재실행하지 않았다. 중대 finding은0건, 비차단 보고 사항은1건이다.

## 핵심 근거

- 저장된 budget242718bytes의 SHA256은 `582e59e8f6b43698b060b44cc17aa2496358ba0491b66e84215e0ed01dcd9f00`이며 producer DELIVERY의 값과 같다. 저장된 분석은4/4·cohort1·signed residual6개·contrast3개·algebraic closure4개이며 exit0이다.
- 네 case의 science6/input22/parent20/binary/build/runtime/thread maps가 모두 같다. 과학 source6개는 현재 Git checkout bytes와 대조했고, parent/input map은 고정 manifests와 같다. 원래 full-state reference source도 Git pin에서 읽어 identity hash에 대조했다.
- 각 Radau/DOP853 method JSON은 RESULT의 해당 result와 정확히 같다. method count+qualification6이 case native_calls와 같고, TABLE의 선언된 source hash와 RESULT가 같다. source table arrays를 새로 만들거나 검증했다고 주장하지 않는다.
- 모든 method가 rtol1e-10, scaled atol1e-12를 기록하고19개 ledger를 반환한다. 원래 reference source는 전체 model state/scale을 solve_ivp에 전달한다.

| case | Radau–DOP853 ΔT [K] | 최대 fraction 차 | case wall [s] | native calls |
|---|---:|---:|---:|---:|
| m8_r2_table512 | 4.61852778e-14 | 9.99498878e-20 | 675.036132 | 144,450 |
| m8_r4_table512 | 2.30926389e-14 | 6.60685699e-20 | 1190.317610 | 249,782 |
| m8_r8_table512 | 2.66453526e-14 | 1.16890547e-19 | 2111.131792 | 407,634 |
| m8_r4_table1024 | 6.03961325e-14 | 1.57548128e-19 | 1689.786683 | 359,580 |

8개 method의 최대 절대 number/energy/species defect는 각각 `2.71050543e-20/H`, `6.28837260e-18 eV/H`, `1.29172524e-19`이다. 원래 gate 안에 있고 반환 endpoint의 gas/temperature/photon 양성성 조건도 충족한다.

## 실행 및 해석

세번째 patch는 BOOTSTRAP의 campaign 호출을 pinned fresh-only controller로 바꾸고 controller·analysis path를 요구한다. 네 process COMMAND는 원래 baseline reference_runner.py의 case 경로를 그대로 사용한다. physics·적분 허용치·원 gate를 바꾸지 않는다. controller는 네 case를 never-started로 분류한 뒤 순차 실행했고 timeout0, exit0을 기록한다.

두 method의 차이와 hull은 저장된 finite 후보의 차이다. r4/table512→1024의 저장 hull은0을 포함하므로 method 후보 전체에서 부호가 확정되지 않는다. 두 strip contrast의 부호 전환에서 단조 수렴·Richardson 차수를 주장할 근거는 없다. r2,n32 transport residual이1e-9K를 넘는 사실은 Radau–DOP853용 gate 실패를 뜻하지 않는다. 네 algebraic closure0은 공통 reference 소거 확인이며 독립 물리 보존법칙 검사가 아니다.

원래 transport의c4 binary와 이번a82 binary는 byte identity가 다르고6점 qualification은 그6점에서 차이0이다. source/model/table/thread의 비교 계약은 만족하지만 전역 native/Grackle 동등성으로 확대하지 않는다.

## 비차단 보고 사항 RPT1

Producer DAG의 현재4/4 상태와 상속된 `BASELINE_4_OF_4_REQUIRED`/`NATIVE_HOLD` 라벨이 함께 있다. raw snapshot은 보존하고 새 current DAG에서4/4와 canary preflight eligibility를 명시하면 된다. archive 내부 backup PENDING은 업로드 이전 snapshot으로 읽고 이후 PR80 영수증을 별도로 적용한다.

## 단일 packed canary의 남은 조건

Baseline 선행조건은 충족됐다. 기존a5 코드와 VigilODEa21, 반환a82 owner binary, 동일 Python3.12.3/NumPy2.3.5/SciPy1.17.0 및 thread1을 사용해 기존 build/preflight를 수행한다. 재생성한 r4/table512 table은 `919ca6f42028bffc37cb208916ee5a9927356eb99344fe467f9b98e30e9fddcd`와 같아야 한다. 전체 상태·19 ledger·원 norm·gate를 유지하며 현지 실행자가 중복 실행과 저장 canary를 먼저 관측한다. 이번 검토의 제출/시작/solver/native 호출은 모두0이다.

세부 값·원자료 경로·실행 기록·범위는 `INDEPENDENT_NATIVE_RETURN_REVIEW.json`에 보존했다.
