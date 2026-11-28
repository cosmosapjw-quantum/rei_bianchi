# Codex handoff: BASS_HE c64-g3 실행 계층 구현

아래를 Codex의 repository task 또는 해당 checkout에서 시작한 CLI/IDE task에 전달한다. 이 prompt를 전달하는 행위는 아래 제한 범위의 구현 시작 지시다. 계획만 다시 제시하고 멈추지 말고 실제 코드·테스트·실행 가능한 반환 패키지를 만들어라.

## 목표와 SSOT

Repository: `cosmosapjw-quantum/BASS_HE`.
계획 branch: `plan/ncp-c64g3-codex-20260928`.
과학 기준 commit: `ac09160bae74f051e5e2e17d8a1cde4084576c16`.
과학 기준 tree: `43e6fb8a7bb88234031542de835fd1e2615974d5`.

작업 시작 시 사용자가 함께 전달한 publication receipt의 exact plan commit/tree를 확인하라. 계획 branch가 이후 이동했으면 새 diff를 읽고 기록하며, 무단 rebase/upgrade하지 마라. exact receipt가 없는 경우 현재 읽은 remote plan SHA를 명시적으로 freeze하고, base 대비 계획 문서 외 변경이 없음을 먼저 확인하라. 기존 `main`이나 PR10 원본을 계산 기준으로 사용하지 마라.

최초 1회 읽을 문서는 root/applicable `AGENTS.md`, `docs/cloud/ncp-c64g3/README_KO.md`, `DESIGN_KO.md`, `RUN_PROFILE_DESIGN.json`, `PLAN_BINDING.json`, `docs/superpowers/plans/2026-09-28-ncp-c64g3-runner.md`다. 이후에는 해당 작업에 필요한 파일만 읽고, 매 단계 전체 문헌·저장소 감사를 반복하지 마라. 원본 DESIGN/profile의 PROPOSED는 작성 당시 상태이며 README/PLAN_BINDING의 사용자 승인이 운영 상태를 갱신한다.

승인된 설계대로 단일 c64-g3의 persistent spawned workers, 단일 controller, immutable case results와 durable ledger를 구현한다. 현재 물리모형, CF, Sturm anchor, complex continuation 알고리즘을 다시 쓰는 과제가 아니다.

## 분업과 권한

너는 구현자다. 기존 수정 후보의 independent scientific reviewer 역할을 동시에 자처하지 마라. 계획 T0-T7을 순서대로 실행하되 도구가 지원하면 독립 파일 소유권이 있는 작업만 소수 subagent에 분리한다. 사용 가능한 skill이 없으면 이 written plan으로 직접 진행한다.

허용: 격리 branch/worktree 생성, 실행 계층·테스트·문서 구현, 필요한 project-venv dependency 설치, bounded local/sandbox 검증, owned branch commit/non-force push/draft PR, 결과 패키징. 이전 사용자 변경은 보존한다.

금지: main/기존 연구 branch 강제 갱신, merge, default scientific solver 교체, 임의 cache 삭제, NCP 자원 생성·증설·정지·삭제, firewall/credential 발급·변경, 무단 유료 compute. 기존 계정과 대상 host가 구체적으로 제공되고 예산이 승인된 경우에만 NCP 실측한다. Codex cloud가 NAVER VM에 자동 연결된다고 가정하지 마라. API key를 요구·출력하거나 repository에 저장하지 마라.

## 반드시 지킬 구현 계약

1. 정확한 plan commit에서 `impl/ncp-c64g3-runner-*`를 만든다. dirty checkout을 reset/stash/delete로 정리하지 않는다. 안전한 별도 worktree를 사용한다.
2. 첫 작업은 T1의 Python reference one-case tracer다. 원본 Numba source/patch/tests/lock이 복구되지 않으면 ACCELERATOR_PAYLOAD_UNAVAILABLE로 기록하고 Python scheduler 개발을 계속한다. 임의로 과거 가속 코드를 재구성하거나 신설하지 않는다.
3. protected science 파일은 수정하지 않는다. replay의 branch/gate 상수만 필요 시 한 pure contract 모듈로 최소 추출하고 기존 CLI도 같은 소유자를 사용하게 한다. science defect는 별도 finding으로 보고한다.
4. process start method는 spawn. 각 worker가 backend를 직접 활성화하고 응답으로 증명한다. NumPy/SciPy/Numba import 전 BLAS/OMP/MKL/NUMEXPR/NUMBA threads=1. parent monkey patch를 상속한다고 가정하지 않는다.
5. 기존 source/control ->7EP ->14D0+gate ->42finite-rho ->closeout barrier를 유지한다. geometry task는 branch/rho/depth/panels/source/backend/endpoint certificate로 식별한다. 32/64는 독립 실행이며 한 contour 내부는 순차다.
6. ledger는 local block filesystem에서 controller만 쓴다. attempt별 파일 fsync, validation, exclusive atomic publication, directory fsync 후 COMMITTED. restart 시 valid final을 ledger에 반영하고 재계산하지 않는다. stale epoch, tampered payload, conflicting final은 fail closed. SQLite live snapshot은 일관된 backup 절차를 사용한다.
7. per-call120s, calibration900s, pilot dispatch3600s를 지킨다. 실제 worker 종료·회수를 검사하며 기다리기 timeout을 kill로 간주하지 않는다. grace/JIT/실패 비용을 모두 기록한다. retry 기본0, numerical failure 자동 retry 금지.
8. worker 초기 cap32와 sweep[1,8,16,24,32,48,56,64]는 실측 후보이지 최적값이 아니다. affinity/cgroup/memory/ready-task로 제한한다. 메모리65% soft/75% hard는 실제 할당량 기준이며 전체 job에 적용한다.
9. systemd service는 non-root, mount dependency, owned workers 종료, 무한 자동 restart 금지로 제공한다. 설치/시작은 host 승인 전 수행하지 않는다. 계산 생존을 Codex나 SSH 세션에 의존시키지 않는다.
10. PASS에는 정확한 command, exit status, raw output과 source/env binding이 필요하다. 기존 통과 결과는 변경 없는 재개에서 반복하지 않는다. 새 코드/환경 영향이 있는 검증만 수행한다. 새 fault behavior는 RED -> GREEN을 남기되 setup/import error를 behavioral RED로 포장하지 않는다.
11. checkpoint export와 provider 전송을 분리한다. 완료 segment만 새 이름으로 백업하고 두 provider ACK/ID/size/checksum을 보존한다. credential이 없으면 local export는 완료하고 transport만 BLOCKED로 기록한다. upload와 restore를 구별한다.
12. Eq55, 새 P_rot/Eq50/Eq54 production, full Nmax/continuum gate는 닫는다. 과학 PROMOTE=HOLD는 runner 개발을 막지 않지만 runner 성공도 그 HOLD를 해제하지 않는다.

## 완료 및 반환

각 task의 exact interfaces/tests는 구현 계획에 있다. repository 바깥에 EXECUTION_STATE.json과 append-only COMMAND_LOG.jsonl을 두고, 중단 뒤 첫 미완료 task만 재개하라. 전체 구현이 가능하면 T7까지 진행하고, host-only 미수행을 명확히 구분해 deployable package를 반환하라. 없는 runner 파일이나 아직 지원하지 않는 CLI option을 실제 실행 명령으로 제시하지 마라.

최종 반환물: 코드 commit/tree 및 patch 또는 bundle, 테스트/JUnit·빌드·설치 기록, source/환경 identity, recovery fault evidence, 실제 측정했을 때만 WORKER_SWEEP/REPLAY_CLOSEOUT, runbook과 실제 지원 CLI 명령, RUN_RETURN.json, ZIP+SHA256. user private data와 원 논문 PDF는 제외한다.

RUN_RETURN에는 다음 상태를 분리한다: implementation, local_tests, cloud_preflight, cloud_replay, accelerator, publication, dual_backup, independent_review, scientific_PROMOTE. 미수행은 null/NOT_RUN, blocker는 원인과 다음 최소 조치를 쓴다. 테스트 수나 속도는 이전 숫자를 복사하지 않는다.

GitHub 권한이 있으면 owned 구현 branch에 non-force push하고 draft PR을 연다. 계획 branch를 PR base로 사용해 implementation delta를 분리하고 exact base/head를 기록한다. 권한이 없으면 로컬 구현·검증을 마치고 publication만 BLOCKED로 남긴다. merge하거나 과학 gate를 올리지 마라.
