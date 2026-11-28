# NCP local Codex: BASS_HE E8 이후 heavy 실행 시작

당신은 NCP local Codex다. 이 디렉터리의 `NCP_LOCAL_CODEX_BASS_HE_HEAVY_HANDOFF_20261008_KO.md`,
`NCP_LOCAL_CODEX_BASS_HE_HEAVY_DAG_20261008.json`, `INPUTS.json`을 먼저 읽고 충돌 없는 순서로 H0→H6를 실행하라.

**사용자의 PC에서 파일을 수동 전달받는 것을 전제로 하지 않는다.** 모든 코드·계약·선택된 실행 source는 Git에,
실행에 필요한 E6/E7/E8 원본 ZIP은 이미 두 cloud에 있으며, 이들을 한 번에 회수할 수 있는 NCP start bundle도 별도 cloud에 게시된다.
그 start bundle의 현재 Drive/Dropbox object ID, SHA256, byte size는 같은 Git 경로의 `BUNDLE_DELIVERY.json`에 있다.

## 0. 안전한 초기 절차

1. 현재 NCP CPU/NUMA/cgroup/메모리, 작업 중 프로세스, old workspace/locks/Git 상태를 read-only 조사하라.
2. `cosmosapjw-quantum/BASS_HE`의 `research/shared-c64-crossrepo-20260928` branch를 `git fetch`하고 HEAD를 읽되
   `reset --hard`, `git clean`, stash, force push/merge를 하지 마라.
3. 이 Git 경로의 `BUNDLE_DELIVERY.json`에서 NCP **preferred consolidated ZIP**의 object ID와 expected SHA를 읽어라.
   `rclone listremotes`와 기존 mount/cache/credentialed CLI를 확인하고, 한 provider에서만 download하라.
   이미 동일 SHA cached bytes가 있으면 재다운로드하지 마라. 다운로드 실패 시 다른 provider metadata/bytes로 fallback하라.
   자격증명을 출력하거나 새 인증을 임의 생성하지 마라.
4. Git에 올라온 `ncp_intake.py`로 `--expected-sha256`과 `--verify-only`를 먼저 확인한 뒤
   **새로운 빈 경로**에 restore하라. Inner E6/E7/E8 archive의 CRC와 payload SHA 검증을 통과해야 한다.
5. Restore 폴더의 `sources/`에서 E6/E7/E8이 각각 **다른 namespace**로 풀리며, `packages/`에는 ZIP 원본 bytes가 보존된다.
   `RESTORE_VERIFICATION.json`을 `CLOUD_INPUT_RECEIPTS.json`으로 연결해 H0/H1부터 진행하라.
6. No cloud credential이면 Git 공개 자료만으로 새 science PASS를 주장하지 말라. 접근 시도/오류와 최소 인증 조치를 `INPUT_RETRIEVAL_BLOCKED`로 반환하라.

## 1. 복원 명령 예시

(실제 repo/mount와 object 위치는 H0에서 검출해야 한다. 아래는 이미 bundle ZIP을 local cache에서 찾은 경우다.)

```bash
cd <BASS_HE_GIT_CHECKOUT>
python3 docs/atomic_reionization_handoff_20261004_v1/NCP_LOCAL_CODEX_HEAVY_20261008_v1/ncp_intake.py \
  --bundle <LOCAL_CONSOLIDATED_START_ZIP> \
  --expected-sha256 <BUNDLE_DELIVERY.json.archive.sha256> \
  --verify-only
python3 docs/atomic_reionization_handoff_20261004_v1/NCP_LOCAL_CODEX_HEAVY_20261008_v1/ncp_intake.py \
  --bundle <LOCAL_CONSOLIDATED_START_ZIP> \
  --expected-sha256 <BUNDLE_DELIVERY.json.archive.sha256> \
  --output <NEW_EMPTY_RUN_DIRECTORY>/intake
```

## 2. 수행 경계

E9은 실제 owner native 출력/385시각 일치부터. 기존 짧은 25행을 보간해서 대신하지 않는다.
처음 1~2 accepted steps 정확한 clock/bit identity를 검증한 뒤 조건부 최대 3×384 steps.
누락 원자 photon first-moment는 `null`로 남긴다. 독립된 energy moment 진단은 authority 확인 뒤 별도로.
원 provider/event source와 비선형/number/energy gates/4096 active nodes/32768 cache keys는 유지.
기존 성공 science를 재실행하지 않는다. physical HOLD, baseline RCT OFF, HE-F2/F09 global OPEN.

## 3. 산출물

REPORT_KO.md, RETURN.json, source lock/build and host inventory, raw stderr/stdout/exit, science gates,
Git non-force commit/tree, Drive+Dropbox create-only receipts, next handoff prompt.
`UPLOAD_VERIFIED`와 원격 다운로드 `RESTORE_VERIFIED`를 구별한다.
