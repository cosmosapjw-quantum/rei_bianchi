# Codex NCP 인계 — 검증된 cell cache와 독립 Rayon batch

## 현재 상태와 실행 범위

사용자는 이 독립 LRS 연구의 구현·검증·동일 branch push·양쪽 백업 및 NCP 실행을 승인했다. 사용자에게 파일 다운로드나 수동 SSH/SCP를 요구하지 않는다. 기존 checkout을 사용하고 dirty 상태를 보존한다. Production v3/rux DAG와 별개다.

이 최적화의 sandbox 검증은 완료됐다. Rust 표적 10개(기존 7+신규 3), 기존 Python 실행기 4개, 실제 옵션 전달 smoke와 기존 19개 설정의 cache 회귀가 통과했다. Independent C9 검토는 모든 원본 물리값·사건 회계의 finite numeric exact equality를 확인했다. 새 `--native-eval cell-cache`를 명시해야 최적화가 활성화된다. default는 `legacy`다.

실제 measured case binary SHA256은 `24f9d38e56d3380e830478b8afe7760b2f44fff7ab60167ed14aa668ae7f4ac0`, pinned VigilODE source는 `8a8bd409b1d96c7b7421f496d229e119fd3d284e`다. 원래 native 152개와 VigilODE 477개의 bytes는 유지했다. source publication SHA와 최종 backup ACK는 이 디렉터리의 `FINAL_DELIVERY.json`을 따른다.

이 sandbox에는 지정된 `/home/cosmosapjw/.ssh/ncp_key`가 없어 이번 최적화의 NCP 실행은 NOT_RUN이다. 기존 source d87ba9ca의 NCP 19개 설정 완료는 별도의 과거 근거다. NCP에서는 아래 정상 source를 컴파일하고 유한 실행만 수행하면 된다. compiler 차이를 과학 실패로 오해하거나 Rust를 강제 downgrade하지 말고 실제 `cargo -Vv`/`rustc -Vv`를 기록한다.

## 먼저 확인

새 GitHub/Drive/Dropbox 실행 결과가 생겼다면 source SHA, command, stdout/stderr, 실제 exit와 raw를 먼저 읽는다. 이름이나 목록만으로 실행 완료를 판정하지 않는다. 이어 `RESEARCH_REPORT_KO.md`, `ROOT_ADMISSION.json`, `review/C9_REVIEW_KO.md`, `FINAL_DELIVERY.json`을 읽는다.

아래 명령은 NCP의 기존 `rei_bianchi` checkout에서 Codex가 실행한다. 기존 working tree를 checkout/reset/clean하지 않는다. 명시적 refspec으로 origin branch를 갱신한 뒤 고정 commit의 입력만 새 run 디렉터리에 추출한다. 새 clone/worktree는 필요 없다.

```bash
set -euo pipefail
REI_REPO="$(git rev-parse --show-toplevel)"
REI_BRANCH='research/rei-lrs-v14-physical-birth-20261018'
REI_REL='research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019'
git -C "$REI_REPO" status --short
git -C "$REI_REPO" fetch origin "+refs/heads/$REI_BRANCH:refs/remotes/origin/$REI_BRANCH"
REI_SOURCE_SHA="$(git -C "$REI_REPO" show "origin/$REI_BRANCH:$REI_REL/optimization_20261020/FINAL_DELIVERY.json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["source_publication_sha"])')"
REI_JOB_ROOT="/tmp/rei_lrs_opt_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$REI_JOB_ROOT/input"
printf '%s\n' "$REI_SOURCE_SHA" > "$REI_JOB_ROOT/EXEC_SOURCE_SHA.txt"
git -C "$REI_REPO" archive "$REI_SOURCE_SHA" research/lrs_atomic_native_bridge_20261016 | tar -x -C "$REI_JOB_ROOT/input"
REI_INPUT_ROOT="$REI_JOB_ROOT/input/research/lrs_atomic_native_bridge_20261016"
REI_TASK_ROOT="$REI_INPUT_ROOT/v14/vigilode_radau_20261019"
set +e
python3 "$REI_TASK_ROOT/prepare_and_run.py" \
  --input-root "$REI_INPUT_ROOT" \
  --output-root "$REI_JOB_ROOT/run" \
  --cargo cargo --all --native-eval cell-cache \
  > "$REI_JOB_ROOT/launcher.stdout" \
  2> "$REI_JOB_ROOT/launcher.stderr"
REI_EXIT=$?
set -e
printf '%s\n' "$REI_EXIT" > "$REI_JOB_ROOT/EXIT_CODE.txt"
test "$REI_EXIT" -eq 0
```

정상 runner는 고정 upstream source를 회수·검증하고 locked dependency fetch 후 offline locked release build, 표적 시험 10개, 기존과 같은 19개 설정을 실행한다. source와 Cargo cache가 이미 있으면 `--vigilode-source`, `--cargo-home`, `--offline` 옵션을 사용한다. 완성된 source의 복원/해시 검사를 생략하지 않는다. Radau RHS cap 200000·내부 30초, 각 process 최대 40초 및 총 native 예산 180초를 유지한다. `MATRIX_RECEIPT.json`과 각 case 원문을 읽고 실패·중단·미실행이 하나라도 있으면 완료로 표시하지 않는다.

## 독립 이력 병렬 batch

위 19개 설정이 성공한 뒤 아래 명령으로 같은 binary의 독립 N16 이력 3개를 실행한다. 원래 history 내부는 단일 transport thread이고 GL2 시간 순서는 그대로다. 사용 가능한 CPU 중 최대 4개를 고른다. 이력이 3개이므로 4 slots의 실효 동시성은 최대 3이다.

```bash
REI_CASE_BINARY="$REI_JOB_ROOT/run/adapter/target/release/rei-vigilode-radau-research"
REI_BATCH_BINARY="$REI_JOB_ROOT/run/adapter/target/release/lrs_batch"
REI_CPUS="$(python3 -c 'import os; print(",".join(map(str, sorted(os.sched_getaffinity(0))[:4])))')"
REI_WORKERS="$(python3 -c 'import os; print(min(4,len(os.sched_getaffinity(0))))')"
set +e
timeout -k 2s 90s "$REI_BATCH_BINARY" "$REI_CASE_BINARY" \
  "$REI_JOB_ROOT/batch" "$REI_WORKERS" "$REI_CPUS" \
  > "$REI_JOB_ROOT/batch.stdout" 2> "$REI_JOB_ROOT/batch.stderr"
REI_BATCH_EXIT=$?
set -e
printf '%s\n' "$REI_BATCH_EXIT" > "$REI_JOB_ROOT/BATCH_EXIT_CODE.txt"
test "$REI_BATCH_EXIT" -eq 0
```

`timeout`과 `taskset`은 필요하다. `/usr/bin/time`은 선택사항이며, 없으면 RSS는 null이다. 실제 children/batch exit와 raw 값을 검사한다. 실패한 child를 삭제하거나 동일 경로에 성공 결과로 덮어쓰지 않는다. NCP에서 성능을 비교한다면 동일 binary의 legacy/cache를 같은 CPU·허용오차로 교대로 실행하고 각 physical output을 대조한다. sandbox와 NCP의 wall 차이를 최적화 가속비로 쓰지 않는다.

## 결과 해석·게시·보존

실제 source SHA, host/compiler, build/test stdout·stderr·exit, native raw, matrix/batch receipt를 같은 PR198 branch와 기존 Drive/Dropbox 경로에 보존한다. archive 전체 readback SHA와 DAG 진척을 남긴다. 현재 줄어든 것은 준비 계산과 실행 시간이며, 메모리 감소는 증명되지 않았다. 향후 NCP 결과가 다르면 실제 오류나 차이를 먼저 해석하고 구체적인 호환 수정만 수행한다.

원본 default/adaptive/checkpoint, MD14, Verner/Grackle/EOS, FD step/error classification, Newton 허용오차, GL2 birth를 성공용으로 바꾸지 않는다. 일반 source-on 차수, uniform stiff, 일반 양수성, CaseB/fullEoR/signed Bianchi, positive CMB/비영 boundary, continuous certificate는 HOLD이며 production admission은 NOT_ISSUED다.

Codex의 기존 허가된 환경에서 접속할 때 사용자 지정 연결은 다음과 같다. 키 내용은 출력하지 않는다.

```text
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
```
