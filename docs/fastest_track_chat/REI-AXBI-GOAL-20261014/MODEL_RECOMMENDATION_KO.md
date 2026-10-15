# 실행 모델과 사고 모드 추천

이 프로젝트는 **coordinator·물리 계약·독립 판정에 Astra / high**, frozen 계약 안의 **Rust 구현·bounded run·HPC orchestration·plot/report에 6.1 Sol / medium**을 권한다. 실제 stiffness, 단위/clock 또는 energy-ledger debugging이 생길 때만 해당 작업을 high로 올린다. 단순 추출·schema/index 조립은 Luna / high가 적합하다.

| 역할 | 기본 추천 | 사용 범위 |
|---|---|---|
| Coordinator·physics authority | gpt-6-astra / high | scenario/background/provider domain, abundance normalization, acceptance와 다음 실행 선택 |
| 기계적 구현·실행 | gpt-6.1-sol / medium | 완전한 frozen packet의 구현·targeted tests·raw output·그림·보고서 |
| 좁은 탐색·추출 | gpt-6-luna / high | 지정 source의 사실·필드 추출; tolerance/closure를 새로 결정하지 않음 |
| 독립 최종 review | gpt-6-astra / high | 자신이 구현하지 않은 실제 diff·raw 결과·claim 검토 |

어려운 물리·수치 문제를 하나로 좁혔고 high로 해결되지 않는 관측 근거가 있을 때만 Astra xhigh/Extra high를 사용한다. Max/Ultra는 기본 OFF다. 명시적 DAG와 실제 native agents의 2–4 disjoint writers로 필요한 병렬화를 수행하면 된다.

단일 모델 환경에서 품질을 우선하면 **Astra / high**, 비용을 우선하면 **6.1 Sol / high**를 선택할 수 있다. 후자는 가능할 때 별도 Astra로 물리·acceptance·최종 claim을 검토한다. 독립 review를 확보하지 못한 경우 그 한계를 그대로 기록하며 self-review를 독립 심사라고 하지 않는다. 여러 모델을 사용할 수 있으면 기존 repo policy대로 과학 권한과 기계적 실행을 분리한다.

이는 [공식 model 설명](https://learn.chatgpt.com/docs/models)을 2026-10-14에 확인한 내용을 바탕으로 한 **프로젝트 운영 판단**이며, 이 저장소에서 측정된 benchmark가 아니다. latency·price·성능을 보장하지 않는다. 실제 account/runtime의 model 목록과 native capability를 먼저 확인하고 requested/observed identity 및 치환을 구분한다. 기존 role TOML과 reviewed 파일·user global config는 변경하지 않는다. 노드별 추천은 [MODEL_ROUTING.json](MODEL_ROUTING.json)에 있다.

NCP64/128은 Rust scientific solver의 계산 자원이며 LLM hosting 설정이 아니다. reasoning effort를 올려도 numerical time integration 자체가 빨라지는 것은 아니다. 기존 chunk/run budgets·누적 counters·checkpoint·scientific acceptance와 coordinator의 push 규칙을 그대로 유지한다.

복사할 wrapper:

~~~text
docs/fastest_track_chat/REI-AXBI-GOAL-20261014/MODEL_ROUTING.json을 읽고 실제 runtime/account에서 관측되는 모델과 native agents에 맞춰 역할을 배정하라. 요청 identity와 실제 identity를 분리하고 사용할 수 없는 모델의 치환을 기록하라. 이어서 같은 폴더의 CODEX_GOAL_PROMPT_KO.md를 읽고 frozen packet·phase budget·checkpoint·coordinator push 규칙을 유지하면서 실제 abundance history와 time/Tgas 그림이 나올 때까지 dependency-ready 작업을 계속하라. 모델 추천이 science gate나 unknown/null을 덮어쓰지 않는다.
~~~
