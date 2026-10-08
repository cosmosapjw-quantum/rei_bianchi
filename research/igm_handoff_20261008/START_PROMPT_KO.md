# Local Codex 시작 프롬프트

cosmosapjw-quantum/rei_bianchi의 IGM reionization 후속 작업을 이어서 수행하라.
handoff branch는 `research/igm-cross-thread-handoff-20261008`, PR target은 `forward/rem-hhe-igm-20261006`이다. target 기준 SHA는 `39c39eab1cc2f1a215723680accc123e67ef13b6`이다. 최신 ref를 읽고 handoff의 PUBLICATION.json/manifest와 비교하되 dirty worktree나 진행 중인 owner branch를 덮어쓰지 말고 별도 worktree를 사용하라.

먼저 `research/igm_handoff_20261008/`의 README_KO.md, HANDOFF.json, DAG.json, RECEIVER_CONTRACT.json, RESULTS.json, evidence/INDEPENDENT_REVIEW.md를 읽어라. `python3 research/igm_handoff_20261008/scripts/verify_package.py`와 `python3 research/igm_handoff_20261008/scripts/reproduce.py --output <새 경로>`를 실행하여 작은 offline 연결부만 확인하라. 과거 Rust/interval/whole-history campaign을 동기화 목적으로 재실행하지 마라.

첫 작업은 DAG의 `IGM-RATE-EXPORT01`이다. PR86 accepted-record 경로와 원 instantaneous photon observer를 조사하고, 같은 source/provider·exact epoch·gas state에 결속한 Gamma[HI,HeI,HeII]와 incident-energy moment[eV/absorber/s]를 내보내는 read-only adapter를 구현하라. 새 연결부의 finite-rule/conditional family 의미를 유지하고 actual source/export fixture로 시험하라. 추가 observer/provider 호출이 필요하면 계수와 실행 범위를 먼저 기록하고 가장 작은 한 fixture만 검증하라. 기존 accepted solver 수치·default·closure·tolerance는 바꾸지 마라. 원 순간 moment가 없으면 MISSING_INSTANTANEOUS_JOINT_MOMENTS를 반환하고 필요한 producer 필드를 명시하라. 적분 A/B, opacity, nonphoto RHS의 0을 순간율로 변환하지 마라.

HE E6, HH ENERGY03, REI BRIDGE11은 각각 owner 예약 작업이다. 반환 여부를 먼저 확인하고 중복 계산하지 마라. HE/HH 온도 domain은 현재 불연속이며 HH passive-energy clock은 gas 진화 clock이 아니다. CR/RCT/HH의 IGM 기본 OFF와 precision-atomic PARKED lane, 원래 실패·physical HOLD를 보존하라. PR85 compensated-log tail을 PR86 canonical Wide로 간주하지 마라. projected evolving feedback·full-history·provider 활성화는 이 adapter의 완료 조건이 아니다.

가능한 독립 작업은 DAG의 BASS observable schema와 REC initial-condition schema다. 이들로 실제 history가 없는 부분을 채워 만든 것으로 취급하지 마라. 완료 시 변경 source identity, 실제 명령/exit, 단위·clock·state mismatch 음성시험, extra observer work, 남은 blocker, 독립 review를 TASK_RETURN.json에 남기고 IGM target을 향한 draft PR로 반환하라. merge/force-push는 하지 마라.
