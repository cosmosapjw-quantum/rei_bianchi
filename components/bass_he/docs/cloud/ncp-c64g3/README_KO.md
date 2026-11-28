# NCP c64-g3: 승인된 설계와 Codex 구현 시작점

현재 문서 상태: `DESIGN_APPROVED_FOR_IMPLEMENTATION / IMPLEMENTATION_NOT_RUN`.
사용자는 2026-09-28 이 대화에서 기존 설계를 승인하고 GitHub 반영 및 Codex handoff 작성을 요청했다. 설계 승인은 배포 완료, 독립 과학 검수, 유료 자원 생성 승인이 아니다.

## 읽는 순서

1. 저장소 루트 `AGENTS.md`.
2. [DESIGN_KO.md](DESIGN_KO.md): 승인된 원본 설계. 원본의 `PROPOSED` 표기는 작성 시점 기록으로 보존했다.
3. [구현 계획](../../superpowers/plans/2026-09-28-ncp-c64g3-runner.md): 파일 경계, 인터페이스, 작업별 검증.
4. [CODEX_HANDOFF_KO.md](CODEX_HANDOFF_KO.md): 새 Codex task에 전달할 전체 실행 계약.
5. [RUN_PROFILE_DESIGN.json](RUN_PROFILE_DESIGN.json): 설계값이며 아직 runner에 입력할 실행 설정이 아니다.
6. [PLAN_BINDING.json](PLAN_BINDING.json): 기준 source와 원본 archive의 identity.

원본 archive: `BASS_HE_NCP_C64G3_REDESIGN_20260928.zip`, 29431 bytes.
SHA-256: `2624b629a1d2c4ea76bc85998e79c6691feb4de1854e7dd729ee5a0e64910269`.
설계/profile/SOURCES는 원본 bytes를 보존한다. SOURCES의 `source_context/...`는 원본 archive 내부 경로이며 이 docs 디렉터리에 있는 것으로 가정하지 않는다.

## 기준과 운영 경계

과학 기준은 `ac09160bae74f051e5e2e17d8a1cde4084576c16`, tree `43e6fb8a7bb88234031542de835fd1e2615974d5`이다. PR11의 pair-membership 수정 후보를 사용하며 PR10 원본이나 `main`으로 되돌아가지 않는다. 이 계획 branch는 해당 기준에 문서만 추가한다.

계획 branch: `plan/ncp-c64g3-codex-20260928`.
Codex는 그 exact plan commit에서 별도 `impl/ncp-c64g3-runner-*` branch/worktree를 만들어 작업한다. 계획 자체는 수정 이력을 남기는 SSOT이고 실행 상태/로그는 repository 바깥 scratch에 둔다. 계획과 다르게 구현해야 할 실제 충돌만 질문한다. 이미 승인된 목표를 반복해서 재설계하지 않는다.

Codex의 역할은 실행 계층 구현자다. Python reference로 동작하는 scheduler를 먼저 완성하고 Numba payload가 없다는 이유로 그 작업까지 중단하지 않는다. 없는 accelerator를 과거 구현으로 재구성하지 않는다. Numba kernel 재작성은 별도 승인 범위다.

허용: 격리 checkout의 구현, 테스트, venv 안의 필요한 dependency 설치, bounded scratch 실행, 구현 branch의 commit 및 non-force push와 draft PR. 금지: 기존 branch 강제 갱신, 사용자 변경 삭제, merge/default solver 전환, cloud 자원 생성/변경/삭제, firewall/credential 변경, 새 유료 compute 실행. 제공된 NCP host의 실측은 host identity와 예산이 별도로 명시됐을 때만 한다.

`runner_implementation`, `cloud_validation`, `backup_transport`, `scientific_PROMOTE`는 별도 상태다. 과학적 PROMOTE는 HOLD이며 Eq55, 새 P_rot/Eq50/Eq54, full-Nmax/continuum admission은 닫힌다. 기존 관련 단위 테스트 실행을 새 production 계산으로 오해하지 않는다.

## Codex 실행 환경

Codex CLI/IDE가 접근하는 checkout 또는 Codex cloud의 repository task에서 같은 handoff를 사용한다. Codex cloud가 NCP VM에 자동 연결된다고 가정하지 않는다. NCP 접근이 없으면 구현/로컬 검증/배포 packet까지 진행하고 host-only 검증만 `BLOCKED_HOST_ACCESS`로 남긴다. Codex 세션은 계산 supervisor가 아니며 장시간 계산은 구현된 non-root service가 담당한다.

공식 참고(2026-09-28 조회):
- https://developers.openai.com/codex/guides/agents-md
- https://developers.openai.com/codex/cli
- https://developers.openai.com/codex/cloud
- https://developers.openai.com/blog/run-long-horizon-tasks-with-codex

CLI 옵션, 모델 ID, 설치 명령을 추측해 고정하지 않는다. 설치된 `codex --version`과 `codex --help`를 확인하고 현재 계정의 정상 인증/권한을 사용한다. API key를 이 repository나 handoff에 넣지 않는다.
