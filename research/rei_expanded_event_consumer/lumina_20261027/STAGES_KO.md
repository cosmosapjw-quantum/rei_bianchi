# 전체 목표 기준 단계 기록

모든 행의 분모는 동일한 원래 canonical DAG 88개다. 단계 처리나 테스트 수를 노드 수에 더하지 않았다. 중앙 브랜치는 27/88이며 기존 stacked 변경은 미병합이다.

| 단계 | 실제 결과 | 전체 DAG | 보존·게시 |
|---|---|---|---|
| R1 연구 위치 | PR235, 이전 한도·완료·예약 복원 | 29/88 | pinned source 재사용 |
| R2 근거 | Lumina 원전·네 수치표·새 ANGTHERM02 결과 확보 | 29/88 | 원본 bytes·출처 기록 |
| R3 전제 | 체적 중앙값, 질량가중 평균, 실제 관측량 구분 | 29/88 | FROZEN_CONTRACT |
| R4 표현 | 반응 행렬·복사 moment·관측자 경로 구성 | 29/88 | FROZEN_CONTRACT |
| R5 유도 | 보존량·에너지 파트너·열방정식·지지집합 조건 | 29/88 | 유도·7개 moment 행 |
| R6 독립 검증 | 물리/수학 범위 내 PASS | 29/88 | 독립 review |
| R7 판별 검산 | Wolfram 대수 검산 완료; 로컬 실행은 자원 종료 | 29/88 | 실제 출력·실패 receipt |
| R8 판정 | 이론·source 범위 채택, 실행 검증 HOLD | 29/88 | ADMISSION |
| R9 구현 연결 | 식–자료–코드 계약과 구현 작성 | 29/88 | 11개 frozen input |
| R10 인계 | 실제 미완료와 승인 대기 명령 보존 | 29/88 | HANDOFF |
| C1 baseline | 기존 source·계산·gate 유지 | 29/88 | RESTORE_RECEIPT |
| C2 대응 | 실제 표와 operator에 식 연결 | 29/88 | adapter source |
| C3 설계 | metadata/단위/에너지 상한/후기 소유 규약 | 29/88 | contract·tests |
| C4 자원 | 0.1 CPU초 예약; 실제 0.103581525초 차감 | 29/88 | 누적 9.978508078/10 |
| C5 구현 | 어댑터·13개 검사·제한 runner 작성 | 29/88 | 정적 검토 PASS |
| C6 구현 실행 | SIGPROF, 테스트 결과 미확립 | 29/88 | attempt01 그대로 보존 |
| C7 과학 검증 | 이론·정적 코드 PASS, runtime HOLD | 29/88 | 독립 판정 분리 |
| C8 재현·비용 | 입력 동일성 확인; runtime 결론 미완료 | 29/88 | 원본 로그·해시·장부 |
| C9 독립 검토 | 물리→코드→원자료 그림 검토, runtime HOLD | 29/88 | INDEPENDENT_REVIEW |
| C10 판정·인계 | 승인 대기 재개 코드와 체크포인트 작성 | 29/88 | 최종 저장 식별자는 delivery receipt |

새 source 그림은 원본 표의 직접 표현이며 실패한 어댑터의 출력이 아니다. 이후의 durable 백업·게시 ACK와 commit/tree는 delivery 최종 기록에 둔다.
