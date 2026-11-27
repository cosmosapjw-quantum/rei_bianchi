# BASS_HE 개발계획 — B1 완료와 REI Atomic-Reuse 후속 경로

2026-10-12 KST · 사용자 첨부 RUX00–RUX16 DAG 반영

## 현재 결과와 다음 작업

B1의 처방된 전자 이력·Planck 초기 test radiation·cold elastic Thomson 비교는 실제 Python backend에서 끝났고 독립 판정은 **PROMOTE_SCOPED_PYTHON**이다. 여섯 대조군, pilot와 격자 세분을 포함한13개 실행의 수치 결과·그림·영수증을 보존한다. 원래 Rust/native 연결과 Python–Rust parity는 **HOLD_RUNTIME_ENVIRONMENT / NOT_RUN**이다.

다음 연구 경로는 **RUX00 → RUX02/RUX03 병렬 → RUX04 → 첫 FLRW/BI 결합 구간 → source-backed H/He 이력 → BASS τ·visibility**다. 일반적인 추가 정밀화 대기 상태를 구체적인 입력·사건 채택 작업으로 바꾼다. RUX02 이후에 RUX03를 불필요하게 직렬 배치하지 않는다.

| 기준 문서 | 역할 |
|---|---|
| [개편 계획 전문](research/b1_prescribed_thomson_20261012/replan/DEVELOPMENT_PLAN_KO.md) | 17개 RUX 노드의 실제 순서, 재사용/미완료 구분, 장소와 완료조건 |
| [실행 DAG](research/b1_prescribed_thomson_20261012/replan/ACTIVE_DAG.json) | 원본17개 ID·의존성 보존, 병렬 단계와 다음 HERE 작업 묶음 |
| [계획 독립 판정](research/b1_prescribed_thomson_20261012/replan/PLAN_DECISION.json) | 계획 검토 결과. 물리 실행 PASS와 구별 |
| [B1 보고서](research/b1_prescribed_thomson_20261012/REPORT_KO.md) | 실제 과학 결과와 비용·한계 |
| [B1 과학 독립 판정](research/b1_prescribed_thomson_20261012/review/DECISION.json) | 한정된 Python 결과의 채택 범위 |
| [새 local/NCP handoff](research/b1_prescribed_thomson_20261012/replan/NCP_LOCAL_CODEX_HANDOFF_KO.md) | 다음 HERE intake와 현재 NCP 새 작업0 |
| [전달 위치](research/b1_prescribed_thomson_20261012/DELIVERY_LOCATOR.json) | 원본 입력·결과·첨부 DAG가 들어 있는 전체 packet과 영수증 위치 |

## 적용 규칙

B1에서 확인한 특성선·시계·실제 Thomson 호출은 재사용한다. RUX06의 소비자 수송 광자 장부·주파수 경계 유량 보존, RUX10의 physical ne(t)·visibility·observer-tail 조건은 별도로 남긴다. 완료된 B1을 다시 돌리거나 원래 native 미완료를 PASS로 바꾸지 않는다.

물리 입력 archive의 존재는 admission이 아니다. 다음 HERE 묶음은 필요한 exact source authority와 physical 입력·담당 과정의 정합성을 확인하고, 첫 실행 가능한 시나리오 또는 정확한 누락 필드를 반환한다. F08/SYNC02/SYNC03·HE/CR/HH의 기존 범위 한정 결과는 재사용하며, 10월4일의 역사 DAG 상태를 소급 변경하지 않는다.

기본 H/He 화학·흡수·가열은 선택 시나리오의 필수 과정이다. 추가 HE 정밀도·특수 CR/HH·공간 구조는 질문과 민감도가 요구할 때 연결한다. 특히 첨부 S15 stock 진단에서 hard-particle provider를 추정하지 않고 RUX03에서 named-process 매핑을 확인한다. E13C11은 **PARKED_PENDING_OBSERVABLE_NEED**다.

이번 RUX 재편의 새 물리 실행은0이고 새 NCP work list는[]다. 경량 작업은 HERE에서 처리한다. 충분히 무거운 독립 미완료 작업과 실제 병렬 이득이 확인될 때만 64코어/128GB NCP packet을 만든다.

이 문서와 후속 overlay는 앞선 PR27의 향후 일정만 갱신한다. 이미 채택된 E13 결과의 과학 범위나 원래 영수증은 변경하지 않는다. 다른 저장소의 production 통합·병합을 이번 BASS_HE 계획 게시로 선언하지 않는다.
