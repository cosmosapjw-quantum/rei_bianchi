# NCP local Codex — E13C9 완료 상태 인계

현재 action은 **CLOSED_NO_NEW_HEAVY_TASK**이고 새 NCP work unit은 **0개**다. 이 인계문은 완료된 연구 상태를 전달한다. 별도 입력 첨부 없이 모든 과거 입력과 실제 반환을 복구할 수 있는 complete archive와 recovery kit의 실제 위치·bytes·SHA는 외부 전달문에 명시된다.

1. E13C8의 완료된 2,331개 경로 N1024 batch와 전체 유한 합산을 유지한다.
2. E13C9 국소 계산은 완료됐다. Node 1·1976·1620·2344의 M128과 node 1162의 M256, 합계 5개 경로·12개 segment가 `PROMOTE_SCOPED_LOCAL_SIGNED_VOLTERRA`다. 170/170개 raw 구간이 기존 구간에 포함되고 폭이 증가하지 않았다. 선택 가중합의 P 폭은 32.5711822283%, H 폭은 30.4812007649% 감소했다. 전체 경로의 새 2차 보정은 `NOT_RUN`이다.
3. Physical·continuum·production·receiver는 `HOLD`다. Provider attestation과 같은 workload의 serial speedup은 확인되지 않았다.
4. 이 인계에 따른 새 budget·physics·full-first2·N512·N1024·M256 bulk·MPI·native·benchmark 호출은 모두 0으로 유지한다. 여기서 완료된 국소 경로 12회와 제조 검증 18회를 NCP에서 반복할 필요가 없다.
5. 필요한 파일이 이미 있으면 기존 receipt와 새 상태만 대조한다. 실제 파일 소실이 있을 때만 외부 handoff에 명시된 archive와 kit를 새 디렉터리에 복구한다. 조각은 다운로드 파일명과 무관하게 실제 bytes/SHA로 선택한다. 첫 실패 receipt는 보존하고 자동 재시도하지 않는다.
6. 현재 새 중량 계약은 없다. 이 인계를 위해 서버를 새로 확보하거나 MPI를 실행할 필요가 없다. 이미 실행 중인 다른 작업과 서버 전원 상태는 이 인계의 범위 밖이다.
7. 짧은 상태 ACK로 충분하다: `ACK_E13C9_CLOSED; NEW_HEAVY_TASKS=0; E13C8_FULL_FINITE_UNCHANGED; E13C9_LOCAL5_ADMITTED; FULL_SECOND_CORRECTION=NOT_RUN`.

다음 수치 연구 질문은 선택 결과의 잔여 반폭 중 약 98%를 차지하는 기존 first-midpoint 상계를 줄이는 국소 방법 연구다. 정확한 전체 accuracy 목표, 검증된 새 방법, 아직 실행하지 않은 work list, 실측 비용과 병렬화 근거를 포함한 후속 계약이 성립할 때 NCP 중량 배치를 판단한다.
