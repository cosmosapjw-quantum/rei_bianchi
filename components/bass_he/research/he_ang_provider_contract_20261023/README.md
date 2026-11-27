# HE-ANG-CONTRACT — source, frame, event correlation

**COMPLETE_SCOPED:** HE-ANG의 공급자 계약과 exact/synthetic reference. Workflow **1.0.0**, approval **0.2**. 부모 HE-ANG의 실제 H1 각분포 공급자는 **SOURCE_INPUT_PENDING**이다.

[RESULTS_KO.md](RESULTS_KO.md)에 과학 결과와 범위를, [CLAIM_GATE.json](CLAIM_GATE.json)에 허용 주장을 기록한다. [DAG.json](DAG.json)은 R1–R10/C1–C10과 각 단계 evidence/백업/게시 상태를 연결한다. [NEXT_DAG.json](NEXT_DAG.json)은 다음 HE-ANG-SOURCE 및 closure 의존성이다.

HE-X1 `eb03981d15ad291375dd6d574a9c28809f85fc02`의 이론·32fixture·독립 검토를 재사용했다. 이번 새 실행은 R7 252predicate, C6 51control, C7 28grouped comparison 모두 PASS다. 이들은 서로 다른 검증 단위이며 물리 event 수로 합산하지 않는다. 기존 IVP·suite·provider scan·benchmark·render는0이다.

정식 유도는 [theory/DERIVATION.md](theory/DERIVATION.md), 코드 계약은 [CODING_CONTRACT.md](CODING_CONTRACT.md), reference 구현은 [code/README.md](code/README.md)다. 실제 raw 및 자원은 [RUN_RECORD.json](RUN_RECORD.json), [RESOURCE_LEDGER.json](RESOURCE_LEDGER.json), `evidence/execution/`에 있다. 초기 [BUDGET.json](BUDGET.json)은 동결 입력이며 현재 누적 사용량은 RESOURCE_LEDGER가 권위다.

독립 theory/code 검토는 `evidence/review/THEORY_REVIEW_FINAL.*`, `CODE_REVIEW_FINAL.*`다. [REPRODUCIBILITY.md](REPRODUCIBILITY.md)의 saved verifier를 기본 재개 경로로 사용한다. 과학 manifest와 delivery pin은 분리한다. 원 code README의 draft theory filename은 정식 경로 theory/DERIVATION.md에 대응한다.

[HANDOFF_RESEARCH_KO.md](HANDOFF_RESEARCH_KO.md)와 [HANDOFF_EXECUTOR_KO.md](HANDOFF_EXECUTOR_KO.md)는 각각 다음 연구 대화와 실행자용이다. [RETURN_TO_CENTRAL_KO.md](RETURN_TO_CENTRAL_KO.md)는 중앙 owner 반영용 상태다. `delivery/PUBLISHED_PINS.json`과 실제 containing Git commit이 게시 identity를 제공한다. 각 stage의 Dropbox/Drive ACK는 `delivery/`에 있다.

no_merge / no_activation. Metadata ready와 X1 필요조건은 경험적 angular calibration을 제공하지 않는다. HE32 minimal pilot의 gas pi_b=0, nonbaryonic matter stress, 미완료 종/핵반응망 범위를 유지한다.
