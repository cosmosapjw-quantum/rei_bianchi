# REI PHYS29 — 작은 반폭의 이차 문턱 이동

이 묶음은 PHYS28의 일차 민감도를 이어 실제 광자 분산 W 고정의 이차계수와 완전한 항별 분해를 다룬다.

## 읽는 순서

1. [연구 보고서](report/PHYS29_REPORT_KO.md): 문제, 직접 유도, 수치와 한계.
2. [최종 판정](independent/DECISION_REVIEW_KO.md)과 [연구 종료](state/CLOSEOUT.json): 승격 범위의 실제 권위.
3. [전체 이론 유도](contributions/theory/DERIVATION_KO.md), [첫 raw](contributions/numerics/SECOND_ORDER_FIRST.json), [수치 노트](contributions/numerics/NUMERICS_NOTE_KO.md).
4. [사전 프로토콜](contributions/numerics/PROTOCOL.json), [첫 실행](contributions/numerics/EXECUTION.json), [재현](portability/REPLAY_RECEIPT.json).
5. [기계 판독 요약](report/PHYS29_RESULTS_SUMMARY.json), [주장 의존성](evidence/CLAIM_DAG.json), [다음 PHYS30 인수문](next/PHYS30_NEXT_HANDOFF_KO.md).

주요 수치: d*=1.45408210662, d0=−0.245144110608(무차원). 실제 분산 보정의 기여는 양쪽 모두 정확히1/3이다. 반폭 .05eV의 기존 수치근에 대한 이차 예측 잔차는 +0.0000601195534502, +0.00000746873854034 eV²다. 정확근 정리와 저장된 수치점의 A-level 계수 평가를 구별한다.

첫 main1회와 별도 경로 replay1회가 각각238/238 PASS였고 raw137037B가 동일하다. 총 joint(k,k′,k″)16회, 새 물리 root0, 옛 main/suite/import/root0이다. 재현 사용법은 [USAGE_KO.md](portability/USAGE_KO.md)에 있다. 이미 완료한 이번 연구의 재현을 자동 반복하지 않는다. 파일 복구 확인에는 과학 실행 없는 verify-only를 사용한다.

최종 payload의 SHA256·크기·모드는 MANIFEST.json, candidate의 사전 동결은 evidence/CANDIDATE_FROZEN.json에 둔다. intake 시점 상태·사전 버전은 역사 기록이며 현재 종료 상태와 구별한다. 과학 input/code/protocol은 실행 후 변경하지 않았다. 그림의 표시 수정은 이전 버전과 실제 관측을 남겼다.

실제 ZIP·Git 게시·전달 결과는 묶음 밖의 PHYS29_PUBLICATION_RECEIPT.json과 뒤이은 전달 ACK로 확인한다. hash cycle을 만들지 않으며 원격 전체 ZIP 복구를 선제 주장하지 않는다.

**Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime 변경0.**
