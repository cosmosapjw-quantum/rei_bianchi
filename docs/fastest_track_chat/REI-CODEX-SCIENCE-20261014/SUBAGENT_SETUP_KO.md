# VS Code Codex 역할과 실제 capability

2026-10-14에 확인한 공식 [subagents 문서](https://learn.chatgpt.com/docs/agent-configuration/subagents)에 따라 `.codex/agents/*.toml`에 `name`, `description`, `developer_instructions`를 둔다. `model`, `model_reasoning_effort`는 선택 필드다. 이 설정은 요청 identity이고, 해당 사용자의 runtime에서 실행된 model identity 증거는 별도다.

| 역할 | repo 파일 | 기본 요청 | 권한 |
|---|---|---|---|
| 기계적 구현/실행 | `.codex/agents/rux_worker.toml` | gpt-6.1-sol / medium | frozen packet의 허용 경로·bounded 명령 |
| 좁은 source 탐색 | `.codex/agents/rux_explorer.toml` | gpt-6-luna / high | read-only, packet이 허용한 관측 기록 |
| 과학 framing/독립 판정 | `.codex/agents/rux_scientific_reviewer.toml` | gpt-6-astra / high | read-only; 한 targeted repair 허가 가능 |

현재 IDE는 native agent 기능을 기본 지원한다고 공식 문서에 설명돼 있지만, 새 세션에서는 실제 노출 도구·모델 목록·MCP·shell·network·sibling 경로를 먼저 inventory한다. 설치 상태나 이 세션의 요청만으로 실제 native agent 사용을 주장하지 않는다. 모델이 unavailable이면 사용자의 관측 가능한 목록 중 같은 권한 역할을 수행할 모델로 치환하고 요청/관측/치환 사유를 반환한다. 과학 계약을 판단할 수 없는 낮은 tier로 치환한 경우 claim admission은 HOLD로 두고 기계적 안전 준비·retained report는 계속한다.

Custom agent는 상위 세션의 permissions와 MCP를 상속한다. 이 TOML은 sandbox/approval을 바꾸지 않는다. 사용자 global config, 인증, API billing 또는 서버는 변경하지 않는다. 전역 동시 실행 설정이 필요한 경우 현재 키는 `agents.max_concurrent_threads_per_session`이며, 여기서는 user config를 자동 작성하지 않는다. 예전 `features.multi_agent` 설정이나 Claude worktree/bootstrap을 복사하지 않는다.

운영 규칙:

1. coordinator 한 명이 기존 checkout의 branch/status/head/remote를 확인한다. dirty/untracked를 보존하며 자동 clone/worktree는 만들지 않는다.
2. 동시에 2–4 writer를 사용할 수 있는 실제 capability와 서로 독립인 write path가 있을 때만 dispatch한다. 같은 파일은 직렬화하고 shared Rust files는 한 owner에게 모은다.
3. 각 worker에게 DAG에서 추출한 단일 full packet을 전달한다. 최소 index만으로 구현하지 않는다. selected source SHA, allowed paths, commands, cumulative limits와 stop 조건을 매번 포함한다.
4. branch 전환·checkout·stage·commit·push는 coordinator만 한다. sibling은 workspace 안의 실제 checkout을 read/open하며 타 owner repo에 쓰지 않는다.
5. 구현자가 아닌 reviewer가 실제 diff와 raw outcome을 한 차례 확인한다. 실제 defect면 한 targeted repair와 필요한 regression을 수행하고 닫는다. optional 주변 감사를 무한히 늘리지 않는다.
6. native agents가 노출되지 않으면 **동일 frozen tasks를 직렬 수행**하고 `native_delegation: NOT_EXPOSED`를 반환한다. mock agent나 요청 model을 관측 identity로 쓰지 않는다. 독립 scientific review를 실제로 확보하지 못했으면 그 claim만 pending으로 보고한다.
7. external sandbox denial이 발생하면 denied action과 다음 좁은 scope 제안을 반환한다. 권한 설정·자격증명·별도 host를 통해 우회하지 않는다. 기존 owner 승인 범위의 실행에는 반복 확인을 요구하지 않는다.

Coordinator는 아래처럼 처음 가능한 packet부터 추출하고, 의존성이 충족되면 다음 작업으로 전이한다.

```bash
python3 scripts/rux_codex/workflow.py --dag docs/fastest_track_chat/REI-CODEX-SCIENCE-20261014/EXECUTION_DAG.json ready
python3 scripts/rux_codex/workflow.py --dag docs/fastest_track_chat/REI-CODEX-SCIENCE-20261014/EXECUTION_DAG.json packet REPORT-DRAFT
```

위 명령은 packet assembly이며 model invocation이 아니다. native UI에서 역할을 선택해 packet을 전달하거나 동일 계약으로 직렬 수행한다.
