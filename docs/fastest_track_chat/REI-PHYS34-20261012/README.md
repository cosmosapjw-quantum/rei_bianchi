# REI-PHYS34-20261012

하단 분지의 고정 source-real 유한 폭 인증. 정확한 lower A=−3.2582515E−137 s⁻⁴, actual W, δ∈[0,0.001] eV, lower 저장 중심±0.25 eV² tube.

과학 실행은 first1/replay1 모두25/25 PASS_SCOPED이며 두 raw가 바이트 동일하다. 최종 채택 상태는 `state/FINAL_STATE.md`와 `independent/DECISION_REVIEW.json`을 먼저 읽는다. `RESEARCH_STATE.md`는 final decision 전 snapshot이다.

- `report/PHYS34_REPORT_KO.md`: 결과·과학적 의미·재현성·한계
- `report/ROOT_TUBE_PROOF_KO.md`: 실제 수치조건과 하단 존재·유일성·엄격 순서의 증명
- `report/NUMERICAL_SUMMARY.json`: 원 interval 끝값과 표시용 바깥 경계
- `contributions/theory/LOWER_BRANCH_DERIVATION_KO.md`: 실행 전 조건부 직접 유도
- `PHYSICS_CONTRACT.json`, `EXECUTION_PROTOCOL.json`, `evidence/PREEXECUTION_FREEZE.json`: 실행 전 고정
- `code/`: 바이트 동일 interval/polynomial helper, 하단 main 및 실제 process capture
- `evidence/CERTIFICATE_FIRST.json`, `evidence/CERTIFICATE_REPLAY.json`: 실제 연속영역 및 근 인증
- `evidence/process/`, `evidence/run_ledger/`, `evidence/EXECUTION_RECEIPT.json`: 실제 stdout/stderr/종료코드와 소진 예산
- `evidence/REPLAY_INPUT.zip`, `evidence/RESTORATION_RECEIPT.json`: 별도 경로에 실제 복원한 입력
- `evidence/FINAL_CANDIDATE_FREEZE.json`, `independent/`: 판정 대상 identity와 실제 독립 최종 결정
- `next/PHYS35_NEXT_HANDOFF_KO.md`: 두 분지 프로파일 이동 차이에 대한 다음 미실행 의무

raw `claim_ceiling`은 실행 전 계약 snapshot이며 사후에 수정하지 않았다. 새 결과는 raw의 실제 status/checks/certificate와 final decision으로 읽는다. 근 유일성은 지정한 tube 안의 명제다. source-real 조건부 수학 인증을 입력 불확실성이나 coupled history의 물리 승인으로 바꾸지 않는다.

Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0.

최종 원격 반영 영수증 `publication/PUBLICATION_RECEIPT.json`은 commit 후 관측으로 작성하므로 전달 archive에 별도로 포함된다. 같은 commit 안에 자신의 최종 commit hash를 기록하는 순환 구조를 만들지 않는다. frozen report의 publication 설명은 계획이며 실제 여부는 이 detached receipt로 확인한다.
