# 로컬 계산 가이드 (Ubuntu 24.04 / Ryzen 5900X / 64 GB)

아래 계산은 branch의 과학식을 바꾸지 않고 sealed microstep을 3개 lane의
독립 프로세스로 병렬 실행합니다. 예상치는 현재 1-step 측정에서 외삽한
event-free 약 9시간이며, bisection과 디스크 속도에 따라 늘어납니다. peak
RSS는 약 1.7 GiB 이상을 예상합니다. 결과는 끝나도 `CANDIDATE_UNSEALED`입니다.

## 1. Branch 받기와 환경

```bash
set -o pipefail
git fetch origin agent/precalc-adaptive-history-parallel-runtime
git switch --track -c agent/precalc-adaptive-history-parallel-runtime \
  origin/agent/precalc-adaptive-history-parallel-runtime
git status --short --branch
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
STAGE=stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY
python -m pip install -r "$STAGE/requirements-runtime.txt"
python -m pip check
(cd "$STAGE" && sha256sum -c SHA256SUMS)
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s "$STAGE/tests"
```

이미 local branch가 있으면 `git switch ...` 후 `git pull --ff-only`를
사용하세요. JAX/Rust/Wolfram은 이 runtime의 load-bearing dependency가
아닙니다. 저장소 최상위 `requirements-lock.txt`의 optional JAX까지 설치하지
마세요. 이 branch에서 검증한 전용 `requirements-runtime.txt`는 JAX를
의도적으로 제외합니다. NumPy/SciPy/pandas와 실제 load-bearing 전이 의존성도
정확 버전으로 고정됩니다. import-only fail-closed guard가 설치되며 JAX가
설치되어 있기만 해도 preflight는 계산 전에 실패합니다.

권위 있는 현재 상태는 `PROJECT_STATE.json`, `handoff/CURRENT_HANDOFF_PROMPT.md`,
sealed predecessor, artifact-registry JSON, durable-ledger CSV입니다. 나머지
`docs/science/current_*`, registry CSV, ledger JSON 일부는 stale이므로 이번
계산의 입력으로 해석하지 마세요.

## 2. 1-endpoint smoke와 이어서 계산

```bash
set -o pipefail
STAGE=stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY
RUN_DIR="$STAGE/runtime/first_interval"
mkdir -p "$RUN_DIR"
"$STAGE/scripts/run_local_first_interval.sh" "$RUN_DIR" --max-accepted 1
python -m json.tool "$RUN_DIR/data/results.json"
python "$STAGE/analysis/validate_one_attempt.py" \
  --run-dir "$RUN_DIR" --output "$RUN_DIR/parity.json"
```

`PAUSED_LIMIT`, `accepted_endpoints: 1`, `accepted_tick: 64`이고 parity의
22개 exact check가 전부 통과한 경우에만 동일 checkpoint에서 전체 계산을
resume합니다. `tmux` 사용을 권합니다.

```bash
tmux new -s bianchi-first-interval
```

새 tmux shell 안에서:

```bash
set -o pipefail
source .venv/bin/activate
STAGE=stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY
RUN_DIR="$STAGE/runtime/first_interval"
mkdir -p "$RUN_DIR"
"$STAGE/scripts/run_local_first_interval.sh" "$RUN_DIR" --resume \
  2>&1 | tee -a "$RUN_DIR/full.console.log"
```

중단/재부팅 후에도 마지막 원자적 checkpoint부터 같은 `--resume` 명령을
사용합니다. `CONTROL.json`, `checkpoints/LATEST.json`, state SHA가 모두
검증되지 않으면 resume하지 않습니다. `$RUN_DIR/.RUN.lock`은 coordinator와
packager가 공유하는 영속 잠금 파일이므로 실행이 끝나도 삭제하지 마세요.
프로세스가 비정상 종료되면 커널이 잠금만 해제하고 파일은 그대로 둡니다.

진행 상태:

```bash
python -m json.tool "$RUN_DIR/CONTROL.json"
tail -f "$RUN_DIR/full.console.log"
```

`BLOCKED_TABLE_EVENT`, `BLOCKED_MINIMUM_STEP`, `BLOCKED_PROTOCOL`,
`BLOCKED_TRANSPORT`는 성공이 아닙니다. 특히 table event에서는 parent가
보존되므로 반복 resume하지 말고 그대로 결과를 package해 공유하세요.

## 3. 결과 package, 별도 결과 branch, push

```bash
set -euo pipefail
RESULT_DIR="$STAGE/local_results"
mkdir -p "$RESULT_DIR"
python "$STAGE/analysis/package_local_results.py" \
  --run-dir "$RUN_DIR" \
  --output "$RESULT_DIR/first_interval_candidate.tar.gz"
(cd "$RESULT_DIR" && sha256sum -c first_interval_candidate.tar.gz.sha256)
git switch -c results/first-canonical-interval-local
ARCHIVE="$RESULT_DIR/first_interval_candidate.tar.gz"
if (( $(stat -c %s "$ARCHIVE") < 45 * 1024 * 1024 )); then
  git add -- "$ARCHIVE" "$ARCHIVE.sha256" "$ARCHIVE.receipt.json"
else
  PARTS_DIR="$RESULT_DIR/first_interval_candidate.parts"
  mkdir -- "$PARTS_DIR"  # 이미 있으면 중단; 기존 part를 절대 덮지 않음
  split -b 44M -d -a 4 --additional-suffix=.part \
    "$ARCHIVE" "$PARTS_DIR/part-"
  (cd "$PARTS_DIR" && \
    sha256sum part-*.part > parts.sha256 && \
    sha256sum -c parts.sha256)
  REASSEMBLED=$(mktemp -- "$RESULT_DIR/.candidate-reassembled.XXXXXX")
  trap 'rm -f -- "$REASSEMBLED"' EXIT
  cat -- "$PARTS_DIR"/part-*.part > "$REASSEMBLED"
  test "$(sha256sum "$REASSEMBLED" | cut -d ' ' -f 1)" = \
    "$(cut -d ' ' -f 1 "$ARCHIVE.sha256")"
  rm -f -- "$REASSEMBLED"
  trap - EXIT
  git add -- "$PARTS_DIR" \
    "$ARCHIVE.sha256" "$ARCHIVE.receipt.json"
fi
git commit -m "data(adaptive-history): add local first-interval candidate"
git push -u origin results/first-canonical-interval-local
```

Packager는 source run 내부 경로와 기존 output/sidecar를 덮어쓰지 않습니다.
같은 이름이 이미 있으면 새 output 이름을 선택하세요.

`runtime/` 전체(rolling checkpoint/snapshot)는 `.gitignore` 대상이며 push하지
마세요. Package에는 hash-chained transition/accept history와 attempt receipts,
retained snapshots, final rolling states, preflight, control, result summary가
포함됩니다. 45 MiB 이상이면 위 명령이 새 전용 디렉터리에 44 MiB verified
part를 만듭니다. 디렉터리가 이미 있으면 덮어쓰지 않고 중단하므로 새 이름을
선택하세요. 감사 측에서는 저장소 최상위에서 아래처럼 no-clobber 임시
파일로 재조립한 뒤 원래 `.sha256`을 검증할 수 있습니다.

```bash
set -euo pipefail
RESULT_DIR="$STAGE/local_results"
PARTS_DIR="$RESULT_DIR/first_interval_candidate.parts"
REASSEMBLED=$(mktemp -- "$RESULT_DIR/.candidate-reassembled.XXXXXX")
trap 'rm -f -- "$REASSEMBLED"' EXIT
(cd "$PARTS_DIR" && sha256sum -c parts.sha256)
cat -- "$PARTS_DIR"/part-*.part > "$REASSEMBLED"
test "$(sha256sum "$REASSEMBLED" | cut -d ' ' -f 1)" = \
  "$(cut -d ' ' -f 1 "$RESULT_DIR/first_interval_candidate.tar.gz.sha256")"
TARGET="$RESULT_DIR/first_interval_candidate.tar.gz"
test ! -e "$TARGET"
ln -- "$REASSEMBLED" "$TARGET"
rm -f -- "$REASSEMBLED"
trap - EXIT
```

Push 뒤 branch 이름과 commit SHA를 공유하면 독립 audit/replay를 이어갈 수
있습니다.
