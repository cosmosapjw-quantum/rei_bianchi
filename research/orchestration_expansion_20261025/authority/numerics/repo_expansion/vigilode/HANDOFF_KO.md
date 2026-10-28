# 다음 작업 인계

이 저장소의 확장 역할과 과제는 REPO_CHARTER_KO.md 및 TASK_ASSIGNMENT.json에 고정했다. 기준 source는 a01f1c5c78e6b06e23565cd4e482716f99efbe97, 관측 branch는 research/d5-callback-contract-20261025다. 이 계획 branch가 active source 소유권을 이전하지 않는다.

첫 과제는 V6-actual-model-derivative다. 상세 과학 계약은 중앙의 VIGILODE_CONTRACTS.json와 THEORY_AND_PR_PLANS.md에 있다. completed work를 재사용하고 정확히 남은 입력·구현만 진행한다. 전체 범위의 완료나 새 실행 예산은 이 문서에서 발급하지 않는다.

Astra 과학 계약 → lower-tier 구현/한정 실행 → 별도 Astra raw/diff 검토의 역할을 유지한다. 원래 acceptance, 물리 단위·frame·clock, 기존 누적 debit을 보존한다. 실제 실행 command와 현재 남은 예산이 아직 고정되지 않은 작업은 실행 상태 NOT_RUN으로 둔다.

V6는 실제 물리 RHS/Jacobian/domain과 native 담당 source·예약·dirty 상태를 요구한다. D5 gateway와 기존 native AffineErrorNorm/Transaction/output hook을 재사용한다. 원자 자료의 유효성은 물리 provider의 책임이다.

기존 active branch, local dirty/untracked work, 과거 failure와 delivery receipt를 보존한다. 중복 계산·NCP 재제출·unknown budget 초기화는 하지 않는다.

