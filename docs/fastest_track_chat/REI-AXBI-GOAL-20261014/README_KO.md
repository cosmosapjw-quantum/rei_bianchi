# 재이온화 이력과 BBN 형식 abundance plot — 실행 목표

최종 목표는 **“재이온화 이력을 완성해서 표준적인 BBN plot처럼 시간/온도에 따른 핵종/이온의 비율을 그리는 것”**이다. 적용 모델은 non-tilted axisymmetric Bianchi I와 matched FLRW이며, 필수 결과는 실제 abundance history와 proper time 및 gas temperature에 대한 두 종류의 abundance 그림이다. 사용자가 채택한 개발·계산·결과 목표이며, 아직 완료된 과학 결과가 아니다. 기존 ADOPTED v2의 H/He–열–방향성 광자 coupled 의무와 claim 경계를 보존하면서 이 목표에 도달하는 실제 코드·입력·계산·그림·논문 경로를 구체화한다.

현재 기준은 `477f3756044df89ff63cceb6b432e63015c07f0a`다. 이전 warm initial-stock adapter와 한-step executable은 컴파일 및 두 targeted tests가 보고됐지만 runtime은 실행되지 않았다. 기존 PDF는 원본 endpoint 15행에서 얻은 **7 paired 차이**의 retained 보고서다. 실제 axisymmetric geometry, 시간 변화 emissivity, cold provider와 다중 epoch 이력은 아직 연결되지 않았다. [현재 결과 감사](CURRENT_RESULT_AUDIT_KO.md)와 [machine audit](CURRENT_RESULT_AUDIT.json)이 이 경계를 기록한다.

이전 state-aware `ready=[]`는 목표 완료가 아니라 provider 선택이 integration 완료를 기다리게 된 실행 전이 결함이다. 새 DAG는 scenario/provider/background/report 준비를 독립 READY로 연다. receiver 준비는 선택 작업으로 별도 둔다. 초기 READY는 AX01/02/03/13이며 AX09/10 τ·visibility는 secondary optional OFF다. missing input은 근거를 조사하고 하나의 실제 결정·supplier 작업으로 해결하며 나머지 실행 가능한 작업을 계속한다. 문서·push 또는 새로운 HOLD 보고서만으로 최종 목표를 완료하지 않는다.

| 먼저 읽을 파일 | 역할 |
|---|---|
| [LOW_COST_INDEX.json](LOW_COST_INDEX.json) | 작은 읽기 순서와 실제 CLI |
| [GOAL.json](GOAL.json), [DEVELOPMENT_PLAN_KO.md](DEVELOPMENT_PLAN_KO.md) | frozen 과학 목표·모델 범위·개발/계산/그림/논문 계획 |
| [EXECUTION_DAG.json](EXECUTION_DAG.json), [TASK_PACKETS.jsonl](TASK_PACKETS.jsonl), [STATE.json](STATE.json) | AX00–AX16의 의존성·단일 packet·실제 진행 상태 |
| [CAMPAIGN_PLAN.json](CAMPAIGN_PLAN.json), [OUTPUT_CONTRACT.json](OUTPUT_CONTRACT.json) | signed shear/refinement/robustness 캠페인과 결과 계약 |
| [CODEX_GOAL_PROMPT_KO.md](CODEX_GOAL_PROMPT_KO.md), [PR_PLAN.md](PR_PLAN.md) | 복사할 계속 실행 prompt와 로컬 PR 묶음 |

기준 모델은 homogeneous H/He, thermal state와 energy–angle photons의 실제 결합이다. 비경사 gas와 axisymmetry에 더해 초기 radiation·emissivity의 **μ-reflection symmetry** 및 대칭 microphysics를 확인해야 순 momentum flux/net force가 0이다. prescribed stress-free Bianchi I background에서 같은 물리 밀도·Λ를 가진 FLRW를 비교하고, 무시한 radiation-stress geometry feedback에는 유효성 오차 예산을 붙인다. 같은 H를 강제로 맞춘 대조는 별도 diagnostic이다.

기본 species는 HI/HII/HeI/HeII/HeIII와 electrons다. 실제 추가 진화한 isotope만 registry와 그림에 더한다. element ion fractions와 baryon-normalized Y_i를 구분하고 electron normalization을 명시한다. T_g가 재가열로 비단조이면 시간순 parametric curve/분기/화살표로 표시하며 T를 정렬해 한 값의 함수로 만들지 않는다.

계획 범위는 지원되는 mean-redshift `z̄=20→4` 전체다. 실제 source/provider가 다른 경계를 요구하면 근거 있는 과학 결정으로 구간을 수정한다. 짧은 warm fixture는 이 전체 목표의 완료가 아니다. resolved null shear response도 정량 bound와 수치 분해가 있으면 유효한 결과다. τ/full observer tail은 목표 완료의 선행조건이 아니다. full sky/QV/tilt/17-species/CR·HH 또는 엄밀한 전체 continuum proof를 이 baseline의 의무로 추가하지 않는다.

새 세션은 다음 명령으로 현재 state를 읽는다. workflow는 task packet을 반환하며 자동 LLM/무한 실행 client가 아니다.

```bash
python3 scripts/rux_codex/workflow.py --dag docs/fastest_track_chat/REI-AXBI-GOAL-20261014/EXECUTION_DAG.json check --state docs/fastest_track_chat/REI-AXBI-GOAL-20261014/STATE.json
python3 scripts/rux_codex/workflow.py --dag docs/fastest_track_chat/REI-AXBI-GOAL-20261014/EXECUTION_DAG.json ready --state docs/fastest_track_chat/REI-AXBI-GOAL-20261014/STATE.json
python3 scripts/rux_codex/workflow.py --dag docs/fastest_track_chat/REI-AXBI-GOAL-20261014/EXECUTION_DAG.json packet AX01 --state docs/fastest_track_chat/REI-AXBI-GOAL-20261014/STATE.json
```

bounded chunk 안에서 결과→필요한 독립 review→checkpoint→다음 ready로 자동 전이한다. 승인된 범위의 다음 chunk마다 사용자에게 “계속할까요”를 묻지 않는다. context/runtime가 끝나면 `PAUSED_RESUMABLE`과 실제 다음 명령을 저장한다. 플랫폼의 무제한 background 실행은 약속하지 않는다. archive 업로드나 매번의 새 approval을 계산 재개의 전역 gate로 두지 않는다.

현재 source manifest의 derived CSV 설명은 7행으로, compile log는 실제 `report.log.gz`와 gzip encoding으로 정정했다. 복사한 감사는 정정 전 관측을 그대로 보존한다. 데이터 재계산·PDF 재컴파일·과거 tests replay는 수행하지 않았다. 기존 11/8 준비 budget 예외와 cargo raw log 부재도 지우지 않는다.
