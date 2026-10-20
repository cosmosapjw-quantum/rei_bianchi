# Codex NCP 인계 — 검증된 cell cache와 독립 Rayon batch

## 현재 상태와 실행 범위

사용자는 이 독립 LRS 연구의 구현·검증·동일 branch push·양쪽 백업 및 NCP 실행을 승인했다. 사용자에게 파일 다운로드나 수동 SSH/SCP를 요구하지 않는다. 기존 checkout을 사용하고 dirty 상태를 보존한다. Production v3/rux DAG와 별개다.

이 최적화의 sandbox 검증은 완료됐다. Rust 표적10개(기존7+신규3), 기존 Python 실행기4개, 실제 옵션 전달 smoke와 기존19개 설정의 cache 회귀가 통과했다. Independent C9 검토는 모든 원본 물리값·사건 회계의 finite numeric exact equality를 확인했다. 새 `--native-eval cell-cache`를 명시해야 최적화가 활성화된다. default는 `legacy`다.

실제 measured case binary SHA256은 `24f9d38e56d3380e830478b8afe7760b2f44fff7ab60167ed14aa668ae7f4ac0`, pinned VigilODE source는 `8a8bd409b1d96c7b7421f496d229e119fd3d284e`다. 원래 native152개와 VigilODE477개 bytes는 유지했다. source publication SHA와 최종 backup ACK는 이 디렉터리의 `FINAL_DELIVERY.json`을 따른다.

이 sandbox에는 지정된 `/home/cosmosapjw/.ssh/ncp_key`가 없어 이번 최적화의 NCP 실행은 NOT_RUN이다. 기존 source d87ba9ca의 NCP19설정 완료는 별도의 과거 근거다. NCP에서는 아래 정상 source를 컴파일하고 유한 실행만 수행하면 된다. compiler 차이를 과학 실패로 오해하거나 Rust를 강제 downgrade하지 말고 실제 `cargo -Vv`/`rustc -Vv`를 기록한다.

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

정상 runner는 고정 upstream source를 회수·검증하고 locked dependency fetch 후 offline locked release build, 표적시험10개, 기존과 같은19설정을 실행한다. source와 Cargo cache가 이미 있으면 `--vigilode-source`, `--cargo-home`, `--offline` 옵션을 사용한다. 완성된 source의 복원/해시 검사를 생략하지 않는다. Radau RHS cap200000·내부30초, 각 process 최대40초 및 총native예산180초를 유지한다. `MATRIX_RECEIPT.json`과 각case 원문을 읽고 실패·중단·미실행이 하나라도 있으면 완료로 표시하지 않는다.

## 독립 이력 병렬 batch

위19설정이 성공한 뒤 아래는 같은 binary로3개의 독립 N16 이력을 실행한다. 원래 history 내부는 단일 transport thread이고 GL2 시간순서는 그대로다. 사용 가능한 CPU 중최대4개를 고른다. 3개 이력이므로4slots의 실효 동시성은 최대3이다.

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

`timeout`과`taskset`은 필요하다. `/usr/bin/time`은 선택사항이며 없으면RSS는null이다. 실제children/batch exit와raw값을검사한다. 실패한child를삭제하거나동일경로에성공으로덮어쓰지않는다. NCP에서성능을비교한다면동일binary의legacy/cache를같은CPU·허용오차로교대로실행하고각physicaloutput을대조한다. sandbox와NCP의wall차이를최적화가속비로쓰지않는다.

## 결과 해석·게시·보존

실제source SHA, host/compiler, build/test stdout·stderr·exit, native raw, matrix/batch receipt를 같은PR198 branch와기존Drive/Dropbox경로에보존한다. archive전체readbackSHA와DAG진척을남긴다. 현재줄어든것은준비계산과실행시간이며메모리감소는증명되지않았다. 미래NCP결과가다르면실제오류나차이를먼저해석하고구체적인호환수정만수행한다.

원본default/adaptive/checkpoint, MD14, Verner/Grackle/EOS,FD step/error classification,Newton허용오차,GL2birth를성공용으로바꾸지않는다. 일반source-on차수,uniformstiff,일반양수성,CaseB/fullEoR/signedBianchi,positiveCMB/비영boundary,continuouscertificate는HOLD이며production admission은NOT_ISSUED다.

Codex의기존허가된환경에서접속할때사용자지정연결은다음과같다. 키내용은출력하지않는다.

```text
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
```
