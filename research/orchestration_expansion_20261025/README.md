# 확장 연구 프로그램, 2026-10-25

`DAG.json`이87개 현재 계약·선행 조건·소유권의 정본입니다. `historical/baseline/`은 c5050305의 기존40계약·17연결·31반환 파일과7권위 원문을 보존합니다. 현재 계약 원문은 `authority/`에 있고 각 노드는 원문 JSON pointer를 유지합니다.

모든 원자 저장소는 각자의 과정 책임을 전체 구성 대상 (Z,A,isomer), 이온·상태·전자 pool·분자 동위원소체로 확장합니다. 현재21개 핵종/이온 population은 검증된 초기 목록이며 미래의 고정 상한이 아닙니다. 소스 없음·지원된0·구현·실행·독립 승인·전달 상태는 다릅니다.

| 저장소 | lead 책임 |
|---|---|
| WU088_HH | 핵종·종·원자/분자/핵/약반응, 가지·반응 에너지 입력 |
| rec_bianchi | 준위·population·분광·재결합·방출/흡수·복사 이력 |
| BASS_HE | 미분 충돌·유한질량/각분포 에너지운동량·열화/열폐쇄 |
| bass_cr | 외부 비열적 광자/전자/바리온 분포·주입·cascade·stopping |
| bass | 시공간·background·공변 T/Q 결합·cohort transport |
| vigilode | 적분·domain/failure·native gateway·오차 제어 |
| rei_bianchi | 선택 시나리오·소스/흡수체/환경·전체 결합 보존·관측량 |

전체 모형의 물리 완료율은 null이며 L4 준비 상태는 false입니다. 공급자 선택은 선택한 모형의 조건부 요구사항이며 모든7저장소 미래 작업의 동시 완료를 요구하지 않습니다. 이번 작업에서는 별도 compiler의 한 번의 한정 실행으로249개 정확 산술 검사를 통과하고 독립 승인을 받았습니다. 이는12개 합성 화학 event와1개 핵 bookkeeping event 및 명시된 guard/항등식에 한정됩니다. H5는 독립 검토된 조건부 이론 유도입니다. 경험적 결합 solver나 새 IVP를 실행하거나 과거 suite를 재계산하지 않았습니다. Compiler는 경험적 rate나 핵Q를 승인하지 않으며 H5 물리 epsilon은 null, 구현은 NOT_RUN입니다.

`charters/`, `task_assignments/`, `handoffs/`는7저장소의 권한·과업·인계를 제공합니다. 개별 PR 계획은 `node_plans/`, 원문 포함 계약은 `contracts/`, 주장 관문은 `gates/`, 현재 관찰은 `status/`, 재사용 소스는 `source_reuse/`에 있습니다. 구조 검사 결과는 `audit/STRUCTURAL_VALIDATION.json`입니다. `central_references/`의 branch/path 링크는 정본 위치를 가리키며 root가 중앙 게시 후 실제 commit SHA를 각 저장소 전달 manifest에 결합합니다.

Compiler의 canonical 구현 저장소는 WU088_HH이며 중앙 동일 소스는 immutable integration mirror입니다. 코드·raw의 과거 pending 문구는 바꾸지 않고 별도 승인/전달 관찰값을 붙입니다. Git 게시와 최종 백업은 별도 영수증으로 확인합니다.
