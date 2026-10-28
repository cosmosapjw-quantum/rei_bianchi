# 초기조건·Bianchi I shear/stress 연구 단위

2026-10-28 KST. 사용자가 초기 입자 조성과 Bianchi I 초기 shear 및 radiation/matter anisotropic stress의 경향성 연구를 병행하도록 요청했다. 이번 산출물은 기존 case 의미와 초기값 감사, 문헌에 근거한 초기조건 후보, 제약을 만족하는 shear/stress 매개화와 해석적 응답, 이를 구현하는 비-IVP helper 및 한 번의 제한 검증이다. 기존 시간진화는 반복하지 않는다.

기준은 PR248 HEAD `022f2ed85595364f05834d8eb1573434efce92d0`이며 기존 완료 계산·원시값을 보존한다. 전체 working DAG 33/88, 중앙 28/88, 기존 physical fast 4/7, 승인된 phenomenological pilot 7/7을 출발점으로 둔다. 새 연구 단위의 준비 또는 테스트 통과를 기존 전체 노드 완료로 환산하지 않는다.

병렬 역할: next_history_sources는 초기조건 원전·값·가정, next_physics_contract는 Bianchi I 유도·물리 계약, next_implementation은 case 감사와 계약의 코드화, next_intake_delivery는 최신 관련 source·담당자 대조와 최종 보존을 담당한다. 독립 판정은 비저자 next_independent_review의 한 번의 검토로 닫는다. 요청된 tier와 실제 runtime 모델 identity는 구별하며 후자는 UNKNOWN이다.

주요 경계: 기존 pilot은 지정된 photon/T/electron bath를 사용한다. 새로운 초기조건을 그 bath에 조용히 대입하지 않는다. 새로운 Bianchi 배경/Einstein feedback IVP는 이번 범위에 포함하지 않는다. 이론상 일반 STF tensor와 구현상 기존 LRS를 구별한다.

백업/게시: 기존 PR248 및 이중 백업이 출발 checkpoint다. 이번 결과도 기존 상시 승인 아래 새 stacked draft PR과 이중 백업으로 보존한다. 원본 archive는 재업로드하지 않는다.
