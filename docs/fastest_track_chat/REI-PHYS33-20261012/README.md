# REI-PHYS33-20261012

고정 source-real 커널의 0<δ≤0.001 eV 상단 분지 두 근을 지정한 tube 안에서 인증한 연구 기록이다. 정확한 공통 높이, 실제 분산, 전체 구간 미분 경계와 양의 Peano 표현을 사용했다. Physical HOLD는 유지한다.

## 읽는 순서

1. [연구 보고서](report/PHYS33_REPORT_KO.md)와 [전체 근 증명](report/ROOT_TUBE_PROOF_KO.md)
2. [최종 상태](state/FINAL_STATE.md), [최종 독립 판정](independent/DECISION_REVIEW.json), [closeout](state/CLOSEOUT.json)
3. [원시 최초 인증](evidence/CERTIFICATE_FIRST.json), [복원 재실행](evidence/CERTIFICATE_REPLAY.json), [실행 합산 기록](evidence/EXECUTION_RECEIPT.json)
4. [동결 계약](PHYSICS_CONTRACT.json), [프로토콜](EXECUTION_PROTOCOL.json), [실행 전 hash](evidence/PREEXECUTION_FREEZE.json), [최종 후보 hash](evidence/FINAL_CANDIDATE_FREEZE.json)
5. [정확한 다항식 유도](contributions/theory/DERIVATION_KO.md), [출처](SOURCE_MANIFEST.json), [후속 PHYS34 인계](next/PHYS34_NEXT_HANDOFF_KO.md)

## 실행 상태

첫 main과 복원 replay는 이미 각1회 완료하여 예산 SPENT다. 과학 프로그램을 다시 실행하라는 지시가 아니다. 실행 경로·입력·환경과 구조화된 결과는 evidence에 보존했다. 외부 실행도구의 원 stdout/stderr 별도 파일은 보존하지 않았으며, 관측된 exit_code0은 HOST_EXECUTION_ATTESTATION.json에서 owner 관측으로 구별한다.

독립 판정 이후의 최종 상태와 publication receipt가 predecision 기록보다 우선한다. publication receipt는 실제 원격 반영 뒤 배포 패키지에 추가되며, 자기 commit SHA를 순환적으로 포함시키는 파일을 미리 만들지 않는다. 저장소에서 해당 receipt가 없으면 commit 자체의 identity와 이 경로의 final state를 확인한다.
