# Codex NCP 인계 — 검증된 cache 경로와 borrowed 실험 옵션
## 지시와 현재 상태
사용자는 독립 LRS 연구의 구현·동일 branch push·백업·NCP 실제 실행을 승인했다. production v3/rux와 별개다. 사용자에게 파일 다운로드나 수동 SSH/SCP를 요구하지 않는다. 이미 허가된 Codex/NCP 환경의 기존 checkout·인증을 사용하고 dirty 상태를 보존한다.

먼저 다른 대화에서 반환된 기록, PR198/관련 branch, Drive/Dropbox의 새 실행 receipt를 읽어라. 같은 source의 NCP 실행이 이미 반환되었다면 source SHA, command, stdout/stderr, exit, raw를 확인하고 결과 분석을 우선하라. 목록·PR 제목·CI success만으로 native 완료를 추정하지 말라.

현재 검증된 코드 source는 **5248822167e3fbe374f4333f7f2efdcdbfdaeeaf**다. 선택된 cell-borrowed v2 binary의 sandbox SHA256은 **3eeda61b64529a83b2604b6e08d448e5b11f067a81faf70bd12509076dde106a**이며 NCP 재컴파일 binary는 별도로 기록한다. pinned VigilODE source는 **8a8bd409b1d96c7b7421f496d229e119fd3d284e**다.

C9는 지정 cached clone 제거와 기존 fixture의 유한 동등성만 승인했다. v2의5쌍 중앙 native cache/borrowed 비율은 fixed0.932206, birth0.980651, disabled0.879171이었다. **가속은 입증되지 않았으므로 성능 목적의 실행은 cell-cache를 사용한다.** default는 legacy다. cell-borrowed는 명시적인 재현 실험 옵션이다. 기존 batch는 cell-cache를 선택한다.

이 대화 환경에는 /home/cosmosapjw/.ssh/ncp_key가 없었고 새 NCP 실행은 NOT_RUN이다. 과거 d87ba9ca source의 NCP19설정 완료와 구분한다. 새 source의 컴파일, 표적시험10개, 동일19설정의 실제 NCP cache 실행을 우선한다. sandbox의 제조문제·기존 이력을 새 문제로 세거나 추가 toy 실험을 만들 필요가 없다.

## source 추출과 정상 runner
NCP의 기존 rei_bianchi checkout에서 실행한다. 최신 metadata를 읽은 뒤 source가 바뀌었다면 source delta와 새 receipt를 먼저 해석한다. 아래는 현재 고정 source를 실행하는 명령이다. 새 clone/worktree를 만들거나 기존 checkout을 reset/clean하지 않는다.

```bash
set -euo pipefail
REI_REPO="$(git rev-parse --show-toplevel)"
REI_BRANCH='research/rei-lrs-v14-physical-birth-20261018'
REI_SOURCE_SHA='5248822167e3fbe374f4333f7f2efdcdbfdaeeaf'
git -C "$REI_REPO" status --short
git -C "$REI_REPO" fetch origin "+refs/heads/$REI_BRANCH:refs/remotes/origin/$REI_BRANCH"
git -C "$REI_REPO" cat-file -e "$REI_SOURCE_SHA^{commit}"

REI_JOB_ROOT="/tmp/rei_lrs_borrowed_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$REI_JOB_ROOT/input"
printf '%s\n' "$REI_SOURCE_SHA" > "$REI_JOB_ROOT/EXEC_SOURCE_SHA.txt"
git -C "$REI_REPO" archive "$REI_SOURCE_SHA" research/lrs_atomic_native_bridge_20261016 |
  tar -x -C "$REI_JOB_ROOT/input"
REI_INPUT_ROOT="$REI_JOB_ROOT/input/research/lrs_atomic_native_bridge_20261016"
REI_ADAPTER_ROOT="$REI_INPUT_ROOT/v14/vigilode_radau_20261019"

set +e
env -u CARGO_TARGET_DIR python3 "$REI_ADAPTER_ROOT/prepare_and_run.py" \
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

env -u CARGO_TARGET_DIR는 runner가 사용하는 adapter/target 경로와 외부 Cargo target override가 어긋나지 않게 한다. 현재 toolchain을 먼저 사용하고 실제 cargo -Vv/rustc -Vv를 기록한다. sandbox는 Rust1.94.1이었다. source/registry cache가 이미 있으면 --vigilode-source, --cargo-home, --offline을 추가할 수 있다. 없으면 runner가 pin과 manifest에 맞는 source를 회수하고 locked fetch 후 offline locked release build를 수행한다.

표적시험은 기존4 unit+6 integration이며, native19설정은10 Radau+9 SSPRK 회귀 대조다. 내부 cap/허용오차, case최대40초, native 총180초를 유지한다. MATRIX_RECEIPT.json뿐 아니라 각 case stdout/stderr/outcome/raw를 읽는다. 중단·미실행·오류를 성공으로 덮어쓰지 않는다.

## 같은 실행 파일의 borrowed 연결 확인
위 source를 실제 컴파일한 binary로 fixed RadauN2 하나만 먼저 실행한다. 이는 실제 NCP 옵션 호환 확인이며 새 가속 검증 캠페인이 아니다.

```bash
REI_CASE_BINARY="$REI_JOB_ROOT/run/adapter/target/release/rei-vigilode-radau-research"
REI_CPU="$(python3 -c 'import os; print(min(os.sched_getaffinity(0)))')"
set +e
timeout -k 2s 40s taskset -c "$REI_CPU" "$REI_CASE_BINARY" \
  "$REI_JOB_ROOT/borrowed_fixed_n2.json" fixed radau 2 \
  --native-eval cell-borrowed \
  > "$REI_JOB_ROOT/borrowed.stdout" \
  2> "$REI_JOB_ROOT/borrowed.stderr"
REI_BORROWED_EXIT=$?
set -e
printf '%s\n' "$REI_BORROWED_EXIT" > "$REI_JOB_ROOT/BORROWED_EXIT_CODE.txt"
test "$REI_BORROWED_EXIT" -eq 0
```

CellCache와 CellBorrowed의 physical fields 및 charged_rhs_attempts/occupied_cell_preparations/node_visits를 비교한다. wall과 native_evaluation의 모드/clone 계수는 의도한 비교 메타데이터다. null·NaN·실패 여부를 함께 읽고 숫자 차이를 허용오차의 근거 없이 숨기지 않는다. stdout만 보고 전체 물리 회계가 완전히 독립 검증되었다고 쓰지 않는다.

## 결과 반환과 다음 범위
source SHA·실제 compiler/host·binary SHA·command·stdout/stderr·exit·raw·분석을 같은 PR198 branch에 정상 파일로 게시하고 Drive/Dropbox 기존 연구 백업 경로에도 보존한다. 단계별 DAG와 전체 archive readback SHA를 기록한다. 이 source의 실제 실행만 필요하며 광범위한 refactor·새 toy 검증·기존76/Python57/과거84/19설정 재집계는 하지 않는다. 실제 호환 오류가 있으면 source delta가 남는 작은 수정과 해당 회귀만 수행한다.

새 NCP 실행이 불가능하면 source와 원인을 기록하고 NOT_RUN으로 남긴다. 사용자 지정 연결은 Codex가 기존 허가된 환경에서 사용할 때 다음과 같다. 키 내용은 출력하지 않는다.

```text
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
```

default/adaptive/checkpoint, MD14, Verner/Grackle/EOS, FD/허용오차, GL2 birth, 원시 P/C/R/D와 binding/heat/cooling/escape/CMB/work 분리는 유지한다. source-on 일반2차, uniform stiff, 일반 양수성, CaseB/fullEoR/signed Bianchi, positive-CMB/비영 boundary, continuous global certificate와 production admission은 기존 HOLD/NOT_ISSUED를 유지한다.

