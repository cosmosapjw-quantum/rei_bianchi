# REI Codex 과학 실행·결과 인계 — 2026-10-14

기존 **ADOPTED v2의 H/He–열–방향성 광자 coupled main path**를 실행하고, 실제 데이터·그림·보고서를 남기기 위한 Codex overlay다. v2의 과학 의무·gate·보호 상태는 바꾸지 않는다. 이전 M0 prescribed/control 우선순위로 돌아가지 않는다.

사용자 승인 범위에는 이 additive handoff의 commit/push와 draft PR, frozen 계약 안의 bounded 준비·실행이 포함된다. main/타 owner branch 병합, 강제 push, 외부 작업 취소, scientific claim 자동 승격은 포함하지 않는다. 실제 push/PR 결과는 최종 반환 기록을 따른다.

읽기 비용을 줄이려면 [LOW_COST_INDEX.json](LOW_COST_INDEX.json) → [CODEX_HANDOFF_KO.md](CODEX_HANDOFF_KO.md) → 해당 노드의 [TASK_PACKETS.jsonl](TASK_PACKETS.jsonl) 순서로 읽는다. 과학 gate의 원본은 [adopted v2 PLAN.json](../REI-ATOMIC-REUSE-RESET-20261012/PLAN.json)이다. Index는 packet의 frozen acceptance를 대체하지 않는다.

| 파일 | 역할 |
|---|---|
| [EXECUTION_DAG.json](EXECUTION_DAG.json), [PLAN_KO.md](PLAN_KO.md) | v2 의무를 보존한 실행 순서·선행조건·실행 후 전이 |
| [TASK_PACKETS.jsonl](TASK_PACKETS.jsonl) | 저비용 작업자에게 전달할 노드별 scope·source·명령·gate |
| [SCENARIO_DECISIONS.json](SCENARIO_DECISIONS.json) | 근거가 있는 구체적 선택과 null 결손 |
| [PR_INVENTORY.json](PR_INVENTORY.json), [PR_PLAN.md](PR_PLAN.md) | 관측된 101개 open PR와 선택 sibling 3개; 앞으로의 로컬 PR 묶음 |
| [REPO_REVIEW_KO.md](REPO_REVIEW_KO.md) | 현재 코드와 최신 source별 claim 경계 |
| [SOURCE_INPUTS_PUBLIC.json](SOURCE_INPUTS_PUBLIC.json), [BACKUP_STATUS_PUBLIC.json](BACKUP_STATUS_PUBLIC.json) | 공개 가능한 파일 identity·재사용 범위·백업 확인 수준 |
| [SUBAGENT_SETUP_KO.md](SUBAGENT_SETUP_KO.md) | VS Code의 실제 capability 확인, native 역할 설정 및 직렬 fallback |
| [RETURN_CONTRACT.json](RETURN_CONTRACT.json) | 실제 명령·산출물·scope·claim·실패·push 반환 형식 |

현재 작업 기준은 PR83 `c07fc7e765ce204bc3e84016cc6874612e535b86`이다. main `ae3402713c4b6530ab2b27f008f5f5d5c6a999ed`에는 active Rust가 없다. PR 제목/branch 이름 하나가 전체 runnable stack을 대표하지 않는다. 최신 metadata를 확인하되 exact source를 노드별로 freeze하고 필요한 delta만 통합한다.

먼저 저장된 15개 F08 endpoint를 이용한 [retained 보고서](retained/REPORT_KO.md), [paired CSV](retained/paired_endpoint_differences.csv), [그림](retained/endpoint_response.png), [derivation 기록](retained/DERIVATION_RECEIPT.json)을 제공한다. 이는 saved endpoint의 paired difference 재표현이며 새 ODE 실행·시간 이력·physical EoR 검증이 아니다. 이 경량 결과는 새 물리 입력 admission과 독립이다. REPORT-DRAFT는 RUX01 뒤에 methods·retained results·pending sections를 바로 작성하고 이후 physical milestone마다 갱신한다. 전체 source-backed paired 결과와 τ/visibility는 해당 데이터·gate가 갖춰지는 대로 이어서 만든다.

공개 저장소에는 원본 첨부·warm history·private provider ID·raw receipt를 넣지 않는다. 별도 전달되는 비공개 transport packet 안의 `PRIVATE_INPUTS.json`이 payload와 정확한 복원 위치를 제공한다. 공개 파일명/hash가 같다는 이유만으로 payload를 이미 복원했다고 보고하지 않는다.

검증 및 다음 packet 추출:

```bash
python3 scripts/rux_codex/workflow.py --dag docs/fastest_track_chat/REI-CODEX-SCIENCE-20261014/EXECUTION_DAG.json check
python3 scripts/rux_codex/workflow.py --dag docs/fastest_track_chat/REI-CODEX-SCIENCE-20261014/EXECUTION_DAG.json ready
python3 scripts/rux_codex/workflow.py --dag docs/fastest_track_chat/REI-CODEX-SCIENCE-20261014/EXECUTION_DAG.json packet REPORT-DRAFT
```

이 CLI는 task packet을 검증/추출한다. LLM client·API 계정·billing·서버를 설치하거나 자동 과학 계산을 시작하지 않는다. 실행 state는 private/local 파일로 기록하고 `--state PATH`로 제공할 수 있다. 실제 산출물과 정밀 blocker가 나올 때까지 이어서 수행하며, 다음 계획만 남기는 것을 완료로 보지 않는다.
