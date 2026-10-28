# 17-state finite pilot: 승인 후 실행 전 checkpoint

2026-10-28 UTC. 기준 PR246 HEAD `ea805aefa8b73a33414e688ead8e5aca3f4296fa`, 실제 readback 확인. 새 branch `research/rei-pilot17-run-20261028`.

새 사용자 지시의 실제 승인 문구는 “제안한 작업은 실행 승인할게.”이다. Root는 앞서 구체적으로 제안한 OFF_base, ON_base, ON_refined 세 case와 current cloud bounded-pilot host의 좁은 NO_MORE_IVPs/실행위치 예외를 승인한 것으로 확정했다. 실제 권한은 기존 runner가 읽는 `research/rei_source_history_20261028/OWNER_IVP_OVERRIDE.json`에 기록한다. 기존 계약·제안은 historical 원문으로 유지한다.

순서대로 세 case만 실행하며 각 child30CPU s/wall120s, worker1/3GiB/자동재시도0이다. 첫 실패 시 보존·중단한다. Main inherited595.225063, temporary cap700, 새 reservation100(최대child90+observer/tail10), cumulative maximum695.225063이다. 종료 후 원래 main cap600과 예외 밖 NO_MORE_IVPs를 유지하고 소비를 초기화하지 않는다.

Postprocess는 inherited presentation57.912723494에 child3CPU s/wall30s/reservation3.5의 fresh allocation을 더하여 cumulative maximum61.412723494<기존 승인65다. Planning20.819461885/승인30 유지, 새 planning compute 없음. 종료 후 policy planning10/presentation30으로 복귀하고 누적 charge와 UNKNOWN_NOT_ZERO를 보존한다.

지금 상태 NOT_RUN. 이 authorization과 새 unit checkpoint/budget 게시·선택 readback 완료 뒤에만 root와 executor에게 실행 가능 상태를 통보한다. 기존 non-IVP tests/diagnostic/plot는 재실행하지 않는다. 원래33/88, 중앙28/88, fast4/7은 새로운 실제 결과·독립 수용 전 그대로다.
