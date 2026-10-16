# SOURCE012 static blob supplement 001

상태는 `HOLD_COLLECTOR_FAILURE_NO_RETRY`다. 잘못된 첫 launcher 경로는 Python 시작 전에 exit 2로 끝났다. 실제 collector는 승인된 단 한 번 실행됐으나 `new_bytes` 지역 변수 오류로 exit 3이 발생했고, private 파일을 쓰기 전에 종료됐다. 이 첫 실제 collector 실패 뒤에는 재시도하지 않았다.

새로 캡처한 blob은 0개, 0바이트다. 따라서 다음 두 static dependency는 여전히 `HOLD_NOT_SUPPLEMENTED`다: `configs/rei_fastest_v1/science_scenario_v1.json`, `docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_first_interval.json`. 기존 409개/7,396,570바이트 private collection은 보존되어 있고, 누락 분류는 원본 부재가 아니라 이전 제한 실행의 Git pack mapping failure다. 이번 supplement는 해당 내용을 해소하지 못했다.

실제 collector process의 cumulative wall은 이전 2.59초에 실패 invocation 0.07초를 더해 2.66초다. malformed launcher 0.28초도 시작된 command attempt로 별도 합산되어 총 started-command wall은 2.94초다. 두 command 결과 모두 `WRAPPER_RECEIPT.json`에 보존했다. 새 scientific evidence나 reference 결과는 없으며 per-call Gamma, heat, prepared nodes, intermediate old state 및 successful positive independent reference는 계속 `null/HOLD`다. Native deadline/cost는 갱신하지 않았다.
