# NCP 인계: 네 원래 기준해 이후의 단일 packed canary

이 인계는 새 ABI2 구현의 실행 연결을 설명한다. 제출·시작·완료 상태는 실제 NCP 접수 및 반환 증거로 기록한다. 월간 quota를 반환한 Remote Desktop Commander는 재시도하거나 재연결하지 않는다. 접근 가능한 실행자는 저장 결과와 실행 중인 프로세스를 먼저 확인한다. 사용자에게 파일 다운로드·업로드·터미널 입력을 요청하지 않는다.

## 1. 먼저 기존 결과를 읽는다

원래 baseline은 m8/GL4/q0의 `(r2,512)`, `(r4,512)`, `(r8,512)`, `(r4,1024)`이며 각 case에서 Radau+DOP853을 실행한다. 최신 GitHub·백업·NCP 작업 디렉터리에 반환이 있으면 source/binary/table identity와 실제 완료 상태부터 분석한다. 부분 완료는 저장된 case부터 분석하고, 이미 완료된 case를 다시 실행하지 않는다. 기존 transport 6개, HE28 연구, HE29 50개 및 기존 VigilODE 96개 검사를 반복하지 않는다.

새 반환이 없고 중복 실행 중인 작업도 없을 때만 상위 `../CODEX_HANDOFF_PROMPT_KO.md`의 baseline 절차를 수행한다. 과학 source·test revision은 `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f`다. 이 isolated execution checkout에는 다음 **두 패치가 모두 필요**하다.

| 실행 경계 보정 | SHA256 | 변경 범위 |
|---|---|---|
| `ncp/REUSE_SOURCE_VALIDATION_20261019.patch` | `cd0b7ab40688b3c60ab689876690b2edd71aea5268b4e7ff285a637ca094a33e` | 완료된 pytest 한 줄을 생략하고 재사용 근거·overlay identity를 기록 |
| `ncp/REPAIR_INPUT_MANIFEST_20261020.patch` | `71f16bc8bc946bdd9107c476662fb83b9812cb4078045b933066fca300eb1e85` | `m8_r2_n64/TABLE.json`의 게시 SHA에서 누락된 `4b` 두 문자 복원 |

두 번째 패치는 원본 DATA를 바꾸지 않는다. 전체 SHA가 고정된 입력 archive와 그 내부 manifest가 가리키는 실제 64자리 SHA를 복원한다. Git에서 두 패치를 꺼내 SHA를 검사한 뒤 1569 checkout에 순서대로 적용하고 `START_REFERENCES.sh`를 시작하는 명령은 상위 handoff에 있다. 과거 미게시 복구용 `PUBLISH.sh`는 사용하지 않는다.

네 기준해가 모두 admit되기 전에는 아래 canary를 실행하지 않는다. baseline의 source·native binary·입력·table·Python·NumPy·SciPy 환경은 새 경로의 비교 기준이다. 같은 binary bytes의 기존 6점 qualification을 재사용하며 이를 전역 Grackle 동등성으로 해석하지 않는다.

## 2. 실제 게시된 ABI2 source pin을 읽는다

baseline shell의 `HE29_STAGE`와 `HE29_WORK_ROOT`는 기존 실행 영수증의 값을 유지한다. `HE29_PYTHON`을 명시해 실행했다면 동일 실행 파일을 사용하고, bootstrap이 만든 venv를 썼다면 그 venv를 사용한다. 다음 분석은 solver를 호출하지 않는다. incomplete JSON 저장 후 exit 1이면 여기서 멈춰 부분 결과를 분석한다.

```bash
set -euo pipefail
HE29_REL=research/he29_survival_budget_20261018
HE29_BASELINE_WORK_ROOT="$HE29_WORK_ROOT"
HE29_PY="${HE29_PYTHON:-$HE29_BASELINE_WORK_ROOT/venv/bin/python}"
[[ -x "$HE29_PY" ]]
"$HE29_PY" "$HE29_STAGE/BASS_HE/$HE29_REL/src/analyze_references.py" \
  --root "$HE29_BASELINE_WORK_ROOT/references" \
  --out "$HE29_BASELINE_WORK_ROOT/PRE_PACKED_ANALYSIS_$(date -u +%Y%m%dT%H%M%SZ).json"

HE29_OPT_STAGE="$(mktemp -d "${TMPDIR:-/tmp}/he29-packed.XXXXXXXX")"
git clone --branch research/he29-survival-budget-20261018 --single-branch \
  https://github.com/cosmosapjw-quantum/BASS_HE.git "$HE29_OPT_STAGE/BASS_HE"
cd "$HE29_OPT_STAGE/BASS_HE"
HE29_OPT_DELIVERY_REV="$(git rev-parse HEAD)"
HE29_OPT_CODE_REV="$("$HE29_PY" - "$HE29_REL/optimization_20261020/DELIVERY.json" <<'PY'
import json, sys
publication = json.load(open(sys.argv[1]))['implementation_publication']
if publication['status'] != 'PUBLISHED_EXACT_READBACK_PASS':
    raise SystemExit('HE29_OPT_IMPLEMENTATION_PUBLICATION_NOT_VERIFIED')
revision = publication['code_commit']
if len(revision) != 40 or any(c not in '0123456789abcdef' for c in revision):
    raise SystemExit('HE29_OPT_PUBLICATION_REQUIRES_FULL_SHA')
print(revision)
PY
)"
HE29_OPT_WORK_ROOT="$HOME/HE29_PACKED_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir "$HE29_OPT_WORK_ROOT"
cp "$HE29_REL/optimization_20261020/DELIVERY.json" "$HE29_OPT_WORK_ROOT/PUBLICATION_DELIVERY.json"
printf '%s\n' "$HE29_OPT_DELIVERY_REV" > "$HE29_OPT_WORK_ROOT/DELIVERY_COMMIT.txt"
printf '%s\n' "$HE29_OPT_CODE_REV" > "$HE29_OPT_WORK_ROOT/CODE_COMMIT.txt"
git cat-file -e "$HE29_OPT_CODE_REV^{commit}"
git checkout --detach "$HE29_OPT_CODE_REV"
[[ "$(git rev-parse HEAD)" == "$HE29_OPT_CODE_REV" ]]
[[ -z "$(git status --porcelain --untracked-files=all)" ]]
HE29_OPT_LANE="$PWD/$HE29_REL/optimization_20261020"
```

후속 `DELIVERY.json`에서 **실제 구현의 `implementation_publication.code_commit`**을 읽으므로 후속 문서 commit과 실행 source commit을 구분한다. 첫 checkpoint `8cb0ebb91a78d2f1b751caa1c3ffc5d170ddfe41`와 이전 ABI1 source `57642252991b5c453db66eb5a078e6a62cc6f4ea`를 최종 ABI2 source로 대체 사용하지 않는다. `DELIVERY.json`이 없거나 게시 readback이 끝나지 않았으면 미완료 게시 상태를 기록한다.

baseline checkout에는 두 overlay가 남아 있으므로 그 checkout을 강제로 되돌리지 않는다. 위의 별도 publication checkout은 코드의 clean build identity를 만들기 위한 것이다.

## 3. DATA 복원 전에 고정 Rust bridge만 빌드한다

새 빌더는 Rust/Cargo 1.94.1, VigilODE `a21d573980f66fe02891bd216153443b5352f921`, 잠긴 Cargo graph와 generic `x86-64`를 사용한다. source/stage 다섯 파일, Git HEAD/tree/clean 상태, dependency Cargo.lock, rustc/Cargo binary SHA 및 버전을 빌드 전후에 비교한다. `RUSTC_WRAPPER`와 `RUSTC_WORKSPACE_WRAPPER`는 명시적으로 비우고 `CARGO_ENCODED_RUSTFLAGS`로 `-C target-cpu=x86-64`를 고정한다.

```bash
"$HE29_PY" "$HE29_OPT_LANE/ncp/build_bridge.py" \
  --out "$HE29_OPT_WORK_ROOT/build" \
  --source-revision "$HE29_OPT_CODE_REV"
```

기존 clean pinned VigilODE checkout과 Cargo cache가 있으면 `--vigilode-checkout`과 `--offline`으로 재사용할 수 있다. 필요하면 실제 설치된 Rust/Cargo 실행 파일을 `--rustc`와 `--cargo`로 지정한다. 빌더는 source가 Git에서 확보된 것인지 확인하며 archive의 코드를 실행하지 않는다. 빌드는 `cargo build --release --locked --lib`이고, 작업 수 2·시간 상한 1800초다. baseline solver, 과거 검사, 새 canary를 자동 실행하지 않는다.

다음 단계에서는 이 빌드의 `build/BUILD_IDENTITY.json`과 `build/target/release/libhe29_optimized_bridge.so`를 사용한다. scratch 합성 검사에 사용한 처음·최종 라이브러리의 영수증은 개발 근거이며, NCP의 새 compiler/library 정체성을 대신하지 않는다. 빌드 실패 시 `BUILD_FAILURE.json`과 `commands/*/{COMMAND.json,stdout.log,stderr.log,RECEIPT.json}`을 먼저 보존한다.

## 4. 동일한 22개 입력 DATA만 복원한다

입력은 원본 `BASS_HE_HE29_RESUME_COMPLETE_20261018_a70d320c.tar.gz`의 DATA만 사용한다. 전체 archive SHA256은 `a70d320c7ead5f1fd93170c18f1f80ae5eb58a293a6045a0f728bb7ae2743205`, 크기는 129635 bytes다. 기존 검증 archive가 있으면 `HE29_INPUT_ARCHIVE`로 재사용한다. 없으면 인증된 기존 rclone remote에서 실행자가 확보한다.

```bash
if ! "$HE29_PY" "$HE29_REL/ncp/RESTORE_VERIFIED_INPUTS.py" \
    > "$HE29_OPT_WORK_ROOT/INPUT_PREFLIGHT.log" 2>&1; then
  HE29_OPT_INPUT_ARCHIVE="${HE29_INPUT_ARCHIVE:-}"
  if [[ -z "$HE29_OPT_INPUT_ARCHIVE" ]]; then
    command -v rclone >/dev/null
    HE29_OPT_INPUT_ARCHIVE="$HE29_OPT_WORK_ROOT/BASS_HE_HE29_RESUME_COMPLETE_20261018_a70d320c.tar.gz"
    HE29_OPT_INPUT_REMOTE=BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_HE29_RESUME_COMPLETE_20261018_a70d320c.tar.gz
    if rclone listremotes | grep -Fxq 'dbx:'; then
      rclone copyto "dbx:$HE29_OPT_INPUT_REMOTE" "$HE29_OPT_INPUT_ARCHIVE"
    elif rclone listremotes | grep -Fxq 'gdrv:'; then
      rclone copyto "gdrv:$HE29_OPT_INPUT_REMOTE" "$HE29_OPT_INPUT_ARCHIVE"
    else
      echo HE29_AUTHENTICATED_INPUT_REMOTE_UNAVAILABLE >&2
      exit 10
    fi
  fi
  "$HE29_PY" "$HE29_REL/ncp/RESTORE_VERIFIED_INPUTS.py" \
    --archive "$HE29_OPT_INPUT_ARCHIVE" \
    > "$HE29_OPT_WORK_ROOT/INPUT_RESTORATION.log" 2>&1
fi
```

복원기는 전체 archive와 각 DATA의 SHA를 검증하고 불일치 파일을 덮어쓰지 않는다. 새 입력 확보를 위해 `START_REFERENCES.sh`를 다시 호출하지 않는다. 접근이 없으면 실제 환경·입력 blocker를 기록한다.

복원된 DATA가 Git에서 untracked인 것은 허용된다. runner는 NUL 구분 Git porcelain을 읽어 **tracked 변경은 거절하고, untracked는 고정 INPUT_SHA256에 있는 경로·해시와 일치하는 DATA만 허용**한다. 그 밖의 untracked 파일도 거절한다. 이 때문에 빌드를 먼저 수행하고 DATA 복원을 뒤에 둔다. 새 로그·결과·build 디렉터리는 모두 checkout 밖에 둔다.

## 5. preflight 뒤 단일 r4/table512 canary

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 OMP_DYNAMIC=FALSE
export OMP_PLACES=cores OMP_PROC_BIND=close RAYON_NUM_THREADS=1

"$HE29_PY" "$HE29_OPT_LANE/src/run_packed.py" preflight \
  --out "$HE29_OPT_WORK_ROOT/preflight" \
  --source-revision "$HE29_OPT_CODE_REV" \
  --baseline-campaign "$HE29_BASELINE_WORK_ROOT/references" \
  --binary "$HE29_BASELINE_WORK_ROOT/build/he29_owner_server" \
  --owner-receipt "$HE29_BASELINE_WORK_ROOT/build/RECEIPT.json" \
  --library "$HE29_OPT_WORK_ROOT/build/target/release/libhe29_optimized_bridge.so" \
  --bridge-receipt "$HE29_OPT_WORK_ROOT/build/BUILD_IDENTITY.json"

"$HE29_PY" "$HE29_OPT_LANE/src/run_packed.py" canary \
  --out "$HE29_OPT_WORK_ROOT/canary" --wall-s 900 \
  --source-revision "$HE29_OPT_CODE_REV" \
  --baseline-campaign "$HE29_BASELINE_WORK_ROOT/references" \
  --binary "$HE29_BASELINE_WORK_ROOT/build/he29_owner_server" \
  --owner-receipt "$HE29_BASELINE_WORK_ROOT/build/RECEIPT.json" \
  --library "$HE29_OPT_WORK_ROOT/build/target/release/libhe29_optimized_bridge.so" \
  --bridge-receipt "$HE29_OPT_WORK_ROOT/build/BUILD_IDENTITY.json"
```

`run_packed.py`는 기존 `run_vigilode.baseline_contract`, `check_sources`, `analyze`, `check_result`, `admit_pair`, `run_process`를 재사용한다. 네 쌍의 source/input/binary/thread identity가 서로 같고 현재 실행 source와 같아야 한다. Python·NumPy·SciPy 값도 네 case 모두 현재 runtime과 같아야 한다. compiler receipt의 publication SHA와 실제 runner의 Git HEAD를 맞춘다.

model은 `OptimizedRefinedSourceModel`의 부모 source-table 생성 경로를 그대로 사용하며 m8/GL4/q0, r4, table512만 생성한다. 완성된 table SHA가 저장된 r4/table512의 SHA와 같아야 solver를 시작한다. owner는 기존 `f7830e2f55e7a1938bc3c98f61b60651f8dae474` binary를 그대로 사용한다. 새 native microphysics 구현이나 새 reference solver를 만들지 않는다.

packed 경로는 같은 VigilODE RODAS5P–GMRES, scaled-state `rtol=1e-10`, `atol=1e-12`, 전체 상태와 19개 ledger, endpoint 출력, dense output 비사용을 유지한다. NCP canary의 packed thread는 1로 고정돼 있다. 개발용 2·4 thread 비교나 case 병렬화는 이 명령에서 실행되지 않는다.

| 범위 | 기존 제한과 판정 |
|---|---|
| canary 전체 | 기본 900초, 최대 3600초의 POSIX process-group 상한 |
| source table | 600초, 예상 allocation 2GiB; 전체 process RSS 상한이 아님 |
| endpoint trace | 128MiB, 매 segment flush·fsync |
| 결과 admission | number defect 3e-15/H, energy defect 3e-12eV/H, species defect 3e-12, 원래 양성성 |
| 저장된 두 method와 비교 | 각각 절대 fraction 1e-11, temperature difference 1e-9K |

첫 실패에서 멈추고 raw 결과를 분석한다. `_worker`를 직접 시작하면 외부 시간 상한을 우회하므로 controller의 `canary` mode를 사용한다. source-only PASS나 합성 FFI PASS는 실제 HE29 admission으로 집계하지 않는다. 새 커널·빌더·entrypoint 검증의 보존 receipt를 재사용하며 기존 suite를 반복하지 않는다.

## 6. 성공·실패 모두 반환한다

별도 결과 branch/Draft PR와 create-only 백업에는 다음 연결을 보존한다.

- publication DELIVERY commit과 실제 code commit, baseline 1569, owner f7830, VigilODE a21d
- `build/BUILD_IDENTITY.json`, compiler/Cargo/lock/library SHA, build commands·stdout·stderr·실패 원본
- baseline 네 case의 IDENTITY/RESULT/TABLE hash와 Python·NumPy·SciPy 값, 기존 native build receipt
- `preflight/PREFLIGHT.json`, `canary/PREFLIGHT.json`, `canary/process/*`, `canary/SUMMARY.json`
- `canary/case/IDENTITY.json`, `TABLE.json`, `SEGMENT_ENDPOINTS.jsonl`, `PACKED_RAW.json`, `RESULT.json` 또는 `FAILURE.json`, `native.jsonl.gz`

최종 output은 원래 admission 전에 `PACKED_RAW.json`에 저장한다. segment 실패는 마지막 완료 상태·부분 관측·callback 오류와 telemetry를 endpoint trace에 남긴다. process timeout이면 이미 저장된 prefix와 controller process receipt를 보존하고 완료로 바꾸지 않는다. 완전한 native JSONL footer나 최종 case receipt가 없는 경우도 있는 그대로 기록한다.

새 canary는 baseline pair 완료 수를 늘리지 않는다. DAG에는 재사용 4쌍과 새 단일 canary의 제출·시작·완료·실패를 분리한다. archive SHA/size, provider object ID/content_hash, raw-byte readback을 각자 기록하고 c47c5efc·798afac1 등 불변 archive는 덮어쓰지 않는다. 연속 스펙트럼, 전체 EoR, 전역 gas-temperature 오차상한, upstream Grackle 전체 동등성, 관측 Bianchi/CMB는 해당 범위의 근거가 생길 때까지 HOLD다.
