# RUX 과학 결과·그림·보고서 실행 계획

기존 v2 `REI-ATOMIC-REUSE-RESET-20261012/PLAN.json`이 과학 의무의 원본이다. 이 계획은 RUX00–16의 원본 객체와 acceptance/stop 조건을 `EXECUTION_DAG.json`의 `verbatim_v2`에 그대로 보존하고, Codex 실행 순서·소유 파일·증거 경로를 덧붙인다. 첨부 standalone PLAN과 ZIP 내부 PLAN은 바이트가 같았다. 원본 계획을 Claude 전용 설정이나 오래된 M0→M1 절차로 대체하지 않는다.

이번 전달은 현재 checkout의 개발 준비와 저장된 결과 후처리다. 새로운 물리 solver는 실행하지 않았다. 사용자가 승인한 개발·push·draft PR 및 근거 있는 모델 선택에 별도 사용자 승인 슬롯을 만들지 않는다. 실제로 미해결인 물리 입력·closure·domain만 해당 소비자의 과학 의무로 남긴다.

## 바로 시작하는 작업

`RUX01`은 저장된 15개 endpoint 행에서 계산한 차이 CSV, endpoint 그림, 한국어 보고서, derivation receipt가 있으므로 구현 완료다. 원래의 synthetic/prescribed discrete 범위와 과학 HOLD는 유지된다. 이 출력은 시간 궤적이 아니며 기존 solver나 검산을 재실행할 이유가 없다.

현재 독립적으로 착수 가능한 것은 `RUX00`, `RETAINED-REVIEW`, `SIBLING-INTAKE`, `REPORT-DRAFT`다. 실제 ready 목록은 다음 명령으로 계산한다. 특정 wave 전체나 모든 PR merge를 기다리지 않는다.

```bash
python3 scripts/rux_codex/workflow.py --dag docs/fastest_track_chat/REI-CODEX-SCIENCE-20261014/EXECUTION_DAG.json check
python3 scripts/rux_codex/workflow.py --dag docs/fastest_track_chat/REI-CODEX-SCIENCE-20261014/EXECUTION_DAG.json ready
python3 scripts/rux_codex/workflow.py --dag docs/fastest_track_chat/REI-CODEX-SCIENCE-20261014/EXECUTION_DAG.json packet REPORT-DRAFT
```

`REPORT-DRAFT`는 방법·저장 결과·정확한 자료/그림 출처·아직 미완료인 물리 결과 절부터 작성한다. LaTeX 원본과 source manifest도 준비하고, 컴파일러가 없으면 Markdown을 즉시 제공한다. 설치된 컴파일러를 확인한 뒤 실제 compile argv를 기록한다. RUX05/08/09/10의 산출물이 생길 때마다 보고서를 갱신하며, 최종 과학 gate를 기다리느라 초안 작성을 멈추지 않는다.

## 의존성과 병렬 작업

| 묶음 | 구현·계산 순서 | 병렬로 가능한 일 |
|---|---|---|
| P0 | RUX00 → 선택 source 통합/입력·provider 계약 → RUX04 → RUX05 첫 FLRW 구간 | RUX02와 source 통합, `CC-PREP05` adapter 준비, RUX06 기존 transport 재사용, receiver 계약 |
| P1 | RUX05 이후 RUX07 첫 Bianchi 구간 및 RUX08 FLRW history | RUX07과 RUX08은 각 입력이 준비되면 독립 수행 |
| P2 | RUX07+08 → RUX09 paired history; RUX05부터 RUX10 receiver와 RUX11 그림 시작 | 구간 관측량·그림·보고서는 각 milestone에 맞춰 누적 |
| 최종 | 관련 전체 결과 → 독립 SCIENCE-REVIEW → RUX16 | 완료된 범위의 보고서·그림과 다른 독립 작업은 유지 |

기본 실행 후보는 E-P `coupled_primary::PrimaryStage`와 source-bound EB warm branch다. 부모 repo 기준은 `c07fc7e765ce204bc3e84016cc6874612e535b86`, 후보 provider는 PR114의 `a5c958c414dea41216b445c05f58df837f05cacb`다. `RUX00`이 실제 선택 계약을 채택하고 `SOURCE-INTEGRATION`이 정확한 구현을 통합해야 한다. 현재 source를 읽었다는 사실만으로 RUX00 전체 완료나 물리 admission을 선언하지 않는다.

`CC-PREP05`는 RUX02/03의 모든 물리 입력을 기다리지 않고 새 adapter와 manufactured changed-seam 테스트를 준비한다. 기존 implicit stage와 event ledger를 재사용한다. source integration writer가 공유 `lib.rs`/`coupled_primary.rs` 등록을 담당하고, adapter writer는 별도 모듈·테스트를 소유한다. 미래 실행 프로그램을 추측한 명령은 넣지 않는다. 실제 scientific run 전에 선택된 executable/argv·입력·source identity를 구간 receipt에 고정한다.

RUX06은 기존 transport와 새 변환 계약을 먼저 준비할 수 있다. 그 완료는 물리 Bianchi 실행이 아니다. RUX07은 RUX04에 직접 의존하고, 동일 시나리오에 geometry/clock을 실제로 결합했는지 확인한다. RUX10은 구간 observable부터 내보내되 full paired output은 RUX09와 실제 tail 근거를 요구한다. RUX11은 첫 구간 그림부터 작성하고, 전체 그림 세트의 입력이 생기기 전에는 진행 중으로 유지한다.

## 시나리오와 provider 경계

`SCENARIO_DECISIONS.json`의 미확정 값은 null이다. 각 값에는 다음 해결 작업과 소유 노드가 있다. sourced data와 정당화된 모델 선택을 구분한다. 온도 3e4–1.1e5 K의 warm provider를 6–20 K의 cold IC에 자동 적용하지 않는다. cold 구간이 선택되면 `LOWT-PROVIDER`의 실제 지원률·thermal family·domain 근거를 완료해야 한다. 숫자 guard를 넓히거나 admission flag를 바꾸어 지원으로 대체하지 않는다. 지원된 warm 모델을 선택하면 그 범위와 cold 미포함을 명시하며, 별도의 low-T 작업을 전체 진행 장벽으로 만들지 않는다.

Case-A transport, Case-A escape ledger, Case-B/OTS 중 선택한 closure와 photon/heat/work/boundary 소유자를 하나로 고정한다. Case-A escape의 에너지 손실은 emitted recombination spectrum/count를 공급하지 않는다. proper electron density에는 추가 Q 인자나 중복 dilution을 적용하지 않는다. observer tail이 없으면 physical total tau/probability는 null이고, 근거 있는 구간 적분은 별도로 제공할 수 있다.

물리 shear의 효과와 계산 정밀도를 비교할 때에는 사용한 free-decaying Bianchi-I, observer 및 quadrupole-compliance 가정을 명시한다. 모든 허용 shear가 어떤 수치 바닥보다 작다는 무조건 명제를 사용하지 않는다. full angular 결과에 정확한 ± scalar symmetry를 가정하지 않으며 cubic response 가능성을 보존한다. homogeneous xHII는 QV가 아니다.

## sibling 저장소와 선택적 작업

`LOWT-PROVIDER`는 BASS_HE의 핵심 provider 공급 계약이며, 선택적 RUX12 HE precision sensitivity와 별개다. `CC-RECV`는 bass의 기존 receiver 계약을 준비한다. 실제 sibling 변경 전에는 local repo mapping과 파일 소유권을 확인한다. rec 입력과 선택 cosmology가 다르면 필요한 background/clock/IC만 정확히 요청한다. CR/HH/공간 확장 RUX13/14/15와 precision RUX12는 기본 OFF이며, 이름 붙은 지원 process와 중간 observable/error-budget 필요가 있을 때 활성화한다.

`SIBLING-INTAKE`는 저장된 계약의 읽기 작업이다. OBSERVER15 R8의 same-SHEAR12 GL32 certified cubic R7-A와 R9 후속 계약, HE47→R3, CR58→NT_COULOMB_MATCHED_PARTITION_DECISION, HH64→PHYS32는 관련 소비자에 연결하되 전체 RUX의 선행 장벽으로 삼지 않는다. warm HE/HH의 source 일치가 absolute cosmological IVP를 공급하지는 않는다. CR finite-rate는 다른 target이다.

## 실행·검토·완료의 구분

현재 checkout을 사용하고 파일이 겹치지 않는 writer만 병렬 배치한다. 저장소별 git mutation coordinator는 한 명이다. 추가 worktree는 실제 도구가 지원하고 명시적으로 승인된 경우에만 만든다. Codex에서 사용 가능한 agent 기능을 확인하고, 없으면 같은 ready packet을 순차 실행한다. 요청 model 이름과 관측된 실행 model을 분리하며, 확인할 수 없으면 null로 기록한다. `.claude` 설정/hook을 Codex enforcement로 간주하지 않는다.

`TASK_PACKETS.jsonl`은 위 DAG의 동일 의무를 압축 전달한다. 소스 전체를 읽어야 하며 작은 인덱스가 원본 계약을 대신하지 않는다. 구현 담당은 code·targeted test·bounded execution을 수행하고, Astra는 source/scenario 계약과 fresh-context 독립 과학 gate를 담당한다. `COMPLETED`에는 실제 출력과 evidence 경로가 필요하다. 해당 파일의 존재나 테스트 PASS는 과학 admission과 다르다.

새 구간은 durable checkpoint와 정확한 source/input/output receipt를 유지한다. 기존 완료 검산은 그대로 재사용하고 변경된 seam이나 새 물리 구간에 필요한 확인만 수행한다. 실패는 해당 소비자와 claim을 멈추며, 실패 파일과 독립적으로 완료된 작업을 보존한다. 기존 Physical/continuum/production HOLD, interval160_161 FAIL, tick160, auxiliary escape FAIL 및 선택적 채널 OFF를 조용히 승격하지 않는다.

RUX16의 최종 보고서는 실제로 지원된 전체 history·paired/receiver scope, 독립 과학 검토, 최종 그림, source/figure/data manifest와 재현 명령을 요구한다. 수치·원자·source·geometry·spectral/spatial closure 불확실성을 분리한다. 초안이나 push 완료를 최종 과학 결과로 표현하지 않는다.

## 누적 실행 한도

각 준비 packet의 누적 한도는 wall 1800초, 명령 최대 8회(그중 build/targeted test 최대 2회), scientific solver 0회, 자동 재시도 0회다. agent handoff/respawn 때 초기화하지 않는다. 한도에 도달하면 구체적인 partial output과 다음 행동을 남기고, coordinator가 필요한 새 구간을 명시적으로 배정한다. 향후 RUX05 이후의 계산은 실제 entrypoint와 argv, wall/CPU/RSS, attempt·accepted checkpoint·총 run 한도, 첫 구체적 실패 stop, checkpoint 경계를 run receipt에 먼저 묶는다. 물리 tolerance는 과학 계약에서 가져오며 이 운영 한도가 발명하지 않는다. `CC-PREP05`가 새 Rust example entrypoint를 소유하고, RUX11은 metadata뿐 아니라 실제 PNG/PDF/SVG 그림도 소유한다.
