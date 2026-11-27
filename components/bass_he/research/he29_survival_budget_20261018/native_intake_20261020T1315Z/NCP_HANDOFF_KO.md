# NCP 인계: 입수된 네 기준해를 재사용하는 단일 packed canary

이 인계의 다음 실행은 기존 a5 코드의 **m8/GL4/q0, r4/table512, thread 1 canary 한 개**다. PR80의 실제 반환 네 pair와 저장된 09929 분석을 재사용한다. 별도 baseline, transport, 분석 CLI, 기존 검사, 제조 benchmark를 시작하지 않는다. 현재 NCP 프로세스와 디스크 경로의 생존 여부는 이 인계 작성 환경에서 `UNOBSERVED`다. 접근 가능한 실행자가 아래 intake를 수행한 뒤, 아직 없는 artifact와 실행만 처리한다. Remote Desktop Commander의 월간 quota에 따른 재시도·재연결 금지는 유지한다. 사용자에게 파일 전송이나 터미널 작업을 요구하지 않는다.

## 1. 반환으로 확인된 연결과 현재 관측을 구분한다

아래 경로는 PR80 native archive의 실제 `provenance/EXECUTION_COMMAND.json`, `execution/references/m8_r4_table512_process/COMMAND.json`, `execution/build/RECEIPT.json`, 네 `IDENTITY.json`에서 읽었다. 과거 저장 경로가 현재도 존재한다고 가정하지 않는다.

| 연결 | 고정값 또는 반환 당시 경로 |
|---|---|
| baseline work root | `/root/HE29_REFERENCE_20261020T120000Z` |
| 네 reference pair | 위 root의 `references/{m8_r2_table512,m8_r4_table512,m8_r8_table512,m8_r4_table1024}` |
| 재사용 Python | 위 root의 `venv/bin/python` |
| 실제 `sys.version` | `3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0]` |
| NumPy / SciPy | `2.3.5` / `1.17.0` |
| 기존 native binary | 위 root의 `build/he29_owner_server` |
| binary SHA256 | `a82e540797322027deaab6e6bcb2bde746de737adeedbf144313598c65f5b7e9` |
| owner receipt | 위 root의 `build/RECEIPT.json` |
| 원래 owner source | `f7830e2f55e7a1938bc3c98f61b60651f8dae474` |
| r4/table512 table SHA256 | `919ca6f42028bffc37cb208916ee5a9927356eb99344fe467f9b98e30e9fddcd` |
| 기존 controller checkout | `/root/HE29_NCP_20261020T105630Z/checkouts/controller_ed5adca` |
| 원본 DATA archive | `/root/HE29_NCP_20261020T105630Z/incoming/BASS_HE_HE29_RESUME_COMPLETE_20261018_a70d320c.tar.gz` |

반환 archive는 `BASS_HE_HE29_NATIVE_RETURN_20261020_c1c4c061.tar.gz`, 276206340 bytes, SHA256 `c1c4c06149bf9561141bc0f6b6f39c280bd554a5e1252ed0825f0e950f1c10c6`다. 필요할 때 실행자가 기존 인증 경로로 이 불변 DATA를 확보한다. archive 안의 source를 실행하지 않는다. 저장된 budget 분석 SHA256 `582e59e8f6b43698b060b44cc17aa2496358ba0491b66e84215e0ed01dcd9f00`와 네 admission을 재사용하며 `analyze_budget.py`, `analyze_references.py`를 다시 CLI 실행하지 않는다. 아래 a5 preflight 안의 기존 admission/identity 검사는 새로운 canary 입력을 묶는 필수 gate이므로 그대로 둔다.

실행자는 먼저 최신 GitHub/결과 branch, 백업의 이후 변경분, 알려진 `/root/HE29_REFERENCE_*`, `/root/HE29_NCP_*`, `/root/HE29_PACKED_*` 결과와 관련 현재 프로세스를 확인한다. 새 `PACKED_RAW.json`, `RESULT.json`, 실패, timeout, 이미 시작된 canary가 있으면 그 반환부터 판독하고 중복 실행하지 않는다. 프로세스가 없다는 결론은 실제 읽을 수 있었던 host·namespace·시각 범위에 한정한다. 신뢰할 관측이 없으면 `HOLD_DUPLICATE_STATE_UNOBSERVED`다.

## 2. 실행 source를 Git에서 고정한다

새 wrapper는 a5 builder/runner의 `run_process` 바인딩만 PR79의 이미 검증된 `run_process_group`으로 연결한다. a5 science, Rust bridge, builder, runner 파일을 수정하지 않는다. wrapper는 별도 checkout에서 실행한다. 새 wrapper의 code pin은 이 lane `DELIVERY.json`의 `implementation_publication.code_commit`이며, 후속 문서 HEAD와 구분한다.

| 역할 | 실행 pin |
|---|---|
| 원래 HE29 science/tests | `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f` |
| ABI2 packed builder/runner/bridge | `a5d4711460c09b310b78c9692aa62534b7a843d3` |
| 재사용 process-group watchdog | `ed5adca43f474553a9bce7f5de45d464be5905cb` |
| VigilODE | `a21d573980f66fe02891bd216153443b5352f921` |

다음 준비 명령은 접근 가능한 NCP 실행자가 수행한다. 기존 제출이나 실행이 없는 경우에만 새 work root를 선택하고 그 경로를 접수 영수증에 기록한다. 기존에 정확히 같은 a5 build artifact가 있으면 그 경로를 `HE29_REUSED_BRIDGE_BUILD`로 지정하여 빌드도 재사용한다. 기존 경로를 관측하지 못했다는 이유로 오래된 work root를 삭제하거나 덮어쓰지 않는다.

```bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 OMP_DYNAMIC=FALSE
export OMP_PLACES=cores OMP_PROC_BIND=close RAYON_NUM_THREADS=1

HE29_REL=research/he29_survival_budget_20261018
HE29_NEW_LANE="$HE29_REL/native_intake_20261020T1315Z"
HE29_BASELINE_WORK_ROOT=/root/HE29_REFERENCE_20261020T120000Z
HE29_PY="$HE29_BASELINE_WORK_ROOT/venv/bin/python"
HE29_INPUT_ARCHIVE=/root/HE29_NCP_20261020T105630Z/incoming/BASS_HE_HE29_RESUME_COMPLETE_20261018_a70d320c.tar.gz
HE29_OPT_CODE_REV=a5d4711460c09b310b78c9692aa62534b7a843d3
HE29_CONTROLLER_REV=ed5adca43f474553a9bce7f5de45d464be5905cb
HE29_CTRL_REPO=/root/HE29_NCP_20261020T105630Z/checkouts/controller_ed5adca
HE29_OPT_STAGE="$(mktemp -d /root/HE29_PACKED_STAGE_XXXXXXXX)"
HE29_OPT_WORK_ROOT="$HE29_OPT_STAGE/work"
HE29_ENTRY_REPO="$HE29_OPT_STAGE/wrapper-source"
HE29_PACKED_REPO="$HE29_OPT_STAGE/packed-a5"
mkdir "$HE29_OPT_WORK_ROOT"
[[ -x "$HE29_PY" ]]

"$HE29_PY" -B - "$HE29_BASELINE_WORK_ROOT" > "$HE29_OPT_WORK_ROOT/RUNTIME_BINARY_INTAKE.json" <<'PY'
import hashlib, json, pathlib, sys
import numpy, scipy
root = pathlib.Path(sys.argv[1])
binary = root / 'build/he29_owner_server'
actual = {'python': sys.version, 'numpy': numpy.__version__, 'scipy': scipy.__version__,
          'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest()}
expected = {'python': '3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0]',
            'numpy': '2.3.5', 'scipy': '1.17.0',
            'binary_sha256': 'a82e540797322027deaab6e6bcb2bde746de737adeedbf144313598c65f5b7e9'}
print(json.dumps({'actual': actual, 'expected': expected, 'match': actual == expected}, indent=2))
if actual != expected:
    raise SystemExit('HE29_PACKED_RETURN_RUNTIME_OR_BINARY_MISMATCH')
PY

git clone --filter=blob:none --single-branch \
  --branch research/he29-survival-budget-20261018 \
  https://github.com/cosmosapjw-quantum/BASS_HE.git "$HE29_ENTRY_REPO"
HE29_ENTRY_DELIVERY_REV="$(git -C "$HE29_ENTRY_REPO" rev-parse HEAD)"
cp "$HE29_ENTRY_REPO/$HE29_NEW_LANE/DELIVERY.json" "$HE29_OPT_WORK_ROOT/WRAPPER_PUBLICATION_DELIVERY.json"
HE29_ENTRY_CODE_REV="$("$HE29_PY" -B - "$HE29_OPT_WORK_ROOT/WRAPPER_PUBLICATION_DELIVERY.json" <<'PY'
import json, sys
p = json.load(open(sys.argv[1]))['implementation_publication']
if p['status'] != 'PUBLISHED_EXACT_READBACK_PASS':
    raise SystemExit('HE29_PACKED_ENTRY_PUBLICATION_NOT_VERIFIED')
revision = p['code_commit']
if len(revision) != 40 or any(c not in '0123456789abcdef' for c in revision):
    raise SystemExit('HE29_PACKED_ENTRY_REQUIRES_FULL_CODE_SHA')
print(revision)
PY
)"
git -C "$HE29_ENTRY_REPO" checkout --detach "$HE29_ENTRY_CODE_REV"
git -C "$HE29_ENTRY_REPO" worktree add --detach "$HE29_PACKED_REPO" "$HE29_OPT_CODE_REV"
if [[ ! -d "$HE29_CTRL_REPO" ]]; then
  HE29_CTRL_REPO="$HE29_OPT_STAGE/controller-ed5"
  git -C "$HE29_ENTRY_REPO" fetch origin "$HE29_CONTROLLER_REV"
  git -C "$HE29_ENTRY_REPO" worktree add --detach "$HE29_CTRL_REPO" "$HE29_CONTROLLER_REV"
fi
HE29_ENTRY="$HE29_ENTRY_REPO/$HE29_NEW_LANE/ncp/packed_entry.py"
HE29_OPT_LANE="$HE29_PACKED_REPO/$HE29_REL/optimization_20261020"
printf '%s\n' "$HE29_ENTRY_DELIVERY_REV" > "$HE29_OPT_WORK_ROOT/WRAPPER_DELIVERY_COMMIT.txt"
printf '%s\n' "$HE29_ENTRY_CODE_REV" > "$HE29_OPT_WORK_ROOT/WRAPPER_CODE_COMMIT.txt"
```

wrapper는 a5와 ed5의 실제 Git root·HEAD·tree·tracked clean 상태를 읽고, target·controller·기존 execution 모듈의 SHA256을 확인한다. 서로 다른 checkout을 같은 root로 대체하거나 pinned source를 수정해 gate를 통과시키지 않는다. 기존 Python 경로가 없거나 버전/빌드 문자열이 다르면 실제 환경 상태를 보존하고 원래 runtime을 복구하는 작은 환경 작업만 수행한다. gate를 느슨하게 하지 않는다.

## 3. 필요한 bridge artifact만 만든다

새 build가 필요한 경우 **DATA 복원 전**에 아래 고정 a5 빌더를 wrapper로 호출한다. 기존 build의 raw library bytes와 `BUILD_IDENTITY.json`이 현재 계약을 충족하면 `HE29_REUSED_BRIDGE_BUILD`를 그 build 디렉터리로 설정해 재사용한다. 과거 개발 clean build·benchmark 검증을 다시 수행하는 단계가 아니다.

```bash
if [[ -n "${HE29_REUSED_BRIDGE_BUILD:-}" ]]; then
  HE29_BRIDGE_BUILD="$HE29_REUSED_BRIDGE_BUILD"
else
  HE29_BRIDGE_BUILD="$HE29_OPT_WORK_ROOT/build"
  "$HE29_PY" -B "$HE29_ENTRY" build \
    --packed-root "$HE29_PACKED_REPO" --controller-root "$HE29_CTRL_REPO" \
    --boundary-out "$HE29_OPT_WORK_ROOT/entry_build" -- \
    --out "$HE29_BRIDGE_BUILD" --source-revision "$HE29_OPT_CODE_REV"
fi
[[ -f "$HE29_BRIDGE_BUILD/BUILD_IDENTITY.json" ]]
[[ -f "$HE29_BRIDGE_BUILD/target/release/libhe29_optimized_bridge.so" ]]
```

이미 존재하는 clean VigilODE a21 checkout과 Cargo cache는 원래 옵션 `--vigilode-checkout PATH --offline`으로 재사용할 수 있다. 필요한 경우 `--cargo PATH --rustc PATH`도 원래 인자 그대로 넘긴다. Rust/Cargo는 1.94.1, host는 `x86_64-unknown-linux-gnu`다. 빌더는 잠긴 graph, generic x86-64, jobs 2, `cargo build --release --locked --lib`, compile wait budget 1800초를 그대로 유지한다. 위 새로운 binding만 ed5 watchdog을 사용한다.

원래 `run_process`의 timeout에서 group leader가 먼저 종료되면 남은 자식이 SIGKILL을 받지 못할 수 있던 `HE29-WATCHDOG-01`은 PR79에서 이미 진단·수정·검증했다. 이 lane은 그 함수와 기존 14개 검사를 재사용한다. timeout 뒤 최대 3초 TERM grace와 residual group KILL·leader reap이 있으며, 이 값은 전체 wall time의 수학적 상한이나 process-group을 이탈한 자식의 종료 보증이 아니다. watchdog 알고리즘을 새로 구현하지 않았다.

## 4. 기존 22개 DATA를 새 a5 checkout에 연결한다

원래 22개 DATA만 이미 검증된 입력 archive에서 복원한다. source/manifest는 a5 Git checkout에 유지한다. 기존 동일 DATA가 있으면 복원기는 bytes를 바꾸지 않고 확인만 한다. archive 크기는 129635 bytes, SHA256은 `a70d320c7ead5f1fd93170c18f1f80ae5eb58a293a6045a0f728bb7ae2743205`다.

```bash
"$HE29_PY" -B "$HE29_PACKED_REPO/$HE29_REL/ncp/RESTORE_VERIFIED_INPUTS.py" \
  --archive "$HE29_INPUT_ARCHIVE" \
  --root "$HE29_PACKED_REPO/$HE29_REL" \
  > "$HE29_OPT_WORK_ROOT/INPUT_RESTORATION.log" 2>&1
```

원래 1569 baseline의 두 패치와 PR79 controller overlay는 이전 reference 실행의 정체성으로 보존한다. 이 새 a5 checkout에는 그 baseline shell 패치를 적용하지 않는다. `START_REFERENCES.sh`, `PUBLISH.sh`, 원래 네 reference job을 호출하지 않는다. 입력 archive가 사라졌다면 실행자가 이미 지정된 불변 DATA 백업에서 확보하고 같은 SHA를 검사한다.

## 5. preflight와 단일 canary를 wrapper에서 실행한다

실행 직전에 현재 프로세스와 저장 결과에 새 변화가 없는지 같은 범위에서 관측한다. 기존 canary나 진행 중인 작업이 있으면 그 증거를 재사용한다. 신규 작업이 필요한 경우에만 다음 순서로 진행한다. `--` 뒤 원래 인자는 위치와 값이 그대로 target에 전달된다. `_worker` 직접 호출과 다른 case 옵션은 wrapper가 거절한다.

```bash
"$HE29_PY" -B "$HE29_ENTRY" preflight \
  --packed-root "$HE29_PACKED_REPO" --controller-root "$HE29_CTRL_REPO" \
  --boundary-out "$HE29_OPT_WORK_ROOT/entry_preflight" -- \
  --out "$HE29_OPT_WORK_ROOT/preflight" --source-revision "$HE29_OPT_CODE_REV" \
  --baseline-campaign "$HE29_BASELINE_WORK_ROOT/references" \
  --binary "$HE29_BASELINE_WORK_ROOT/build/he29_owner_server" \
  --owner-receipt "$HE29_BASELINE_WORK_ROOT/build/RECEIPT.json" \
  --library "$HE29_BRIDGE_BUILD/target/release/libhe29_optimized_bridge.so" \
  --bridge-receipt "$HE29_BRIDGE_BUILD/BUILD_IDENTITY.json"

"$HE29_PY" -B "$HE29_ENTRY" canary \
  --packed-root "$HE29_PACKED_REPO" --controller-root "$HE29_CTRL_REPO" \
  --boundary-out "$HE29_OPT_WORK_ROOT/entry_canary" -- \
  --out "$HE29_OPT_WORK_ROOT/canary" --wall-s 900 \
  --source-revision "$HE29_OPT_CODE_REV" \
  --baseline-campaign "$HE29_BASELINE_WORK_ROOT/references" \
  --binary "$HE29_BASELINE_WORK_ROOT/build/he29_owner_server" \
  --owner-receipt "$HE29_BASELINE_WORK_ROOT/build/RECEIPT.json" \
  --library "$HE29_BRIDGE_BUILD/target/release/libhe29_optimized_bridge.so" \
  --bridge-receipt "$HE29_BRIDGE_BUILD/BUILD_IDENTITY.json"
```

기존 preflight는 네 reference의 source/binary/input/parent/thread/runtime, 실제 bridge receipt/library, a5 publication identity를 확인한다. worker는 동일 부모 model 생성 경로로 r4/table512 table을 만들고 저장 reference의 SHA와 같을 때만 solver를 시작한다. 초기 상태는 원래 model의 초기 상태이며, reference endpoint를 초기 조건으로 넣지 않는다. 기존 NativeOwner와 같은 binary bytes의 6점 qualification을 재사용한다.

| 실행/과학 계약 | 유지값 |
|---|---|
| case / solver | m8/GL4/q0, r4/table512 한 개 / 기존 VigilODE RODAS5P–GMRES |
| norm / thread | full gas/photon state 및 19개 ledger, thread 1 |
| 적분 허용치 | scaled-state `rtol=1e-10`, `atol=1e-12` |
| 원래 admission | number `3e-15/H`, energy `3e-12 eV/H`, species `3e-12`, 원래 양성성 |
| 저장된 두 method 각각과 비교 | 절대 fraction `1e-11`, 온도차 `1e-9 K` |
| 실행 wait budget | canary 900초, 자동 확대 없음 |
| table / endpoint trace | 기존 table 600초·예상 allocation 2GiB, trace 128MiB |

첫 실패나 timeout에서 멈춰 prefix와 failure를 반환한다. wall budget, 격자, 허용치, positivity gate를 자동 변경하지 않는다. 네 reference admission은 이미 완료된 재사용 4/4로 남으며 이 canary가 baseline 완료 수를 늘리지 않는다.

## 6. 실제 제출·시작·결과를 따로 반환한다

이 문서 작성과 wrapper 검증만으로 NCP 제출·시작·canary 완료를 주장하지 않는다. 실행자가 실제 접수 ID, 관측 시각/host, 관련 PID/PGID, 명령과 선택한 경로를 별도 영수증으로 남긴다. 모든 출력은 checkout 밖 새 디렉터리에 create-only로 저장한다. wrapper 경계의 성공은 target가 성공으로 돌아왔다는 뜻이며 과학 admission은 원래 canary의 raw/RESULT를 읽어 판정한다.

- `WRAPPER_PUBLICATION_DELIVERY.json`, wrapper delivery/code commit, 기존 a5/ed5/a21 pin을 보존한다.
- `entry_{build,preflight,canary}/{STARTED.json,SOURCE_IDENTITY.json,RECEIPT.json 또는 FAILURE.json}`을 보존한다. 잘못된 CLI나 이미 존재하는 boundary를 거절한 경우 기존 경계 bytes를 덮어써서 새 실패 파일을 만들지 않는다.
- 새 build가 있었다면 `BUILD_IDENTITY.json`, library raw bytes, build commands/stdout/stderr/실패를 보존한다. 재사용 build라면 실제 library/receipt 경로·SHA와 재사용 근거를 보존한다.
- `preflight/PREFLIGHT.json`, `canary/PREFLIGHT.json`, `canary/process/*`, `canary/SUMMARY.json`, case의 `IDENTITY.json`, `TABLE.json`, `SEGMENT_ENDPOINTS.jsonl`, `PACKED_RAW.json`, `RESULT.json` 또는 `FAILURE.json`, `native.jsonl.gz`를 보존한다.
- 결과 Git branch/Draft PR와 create-only archive/백업의 SHA·크기·object ID·raw readback 상태를 기록하고 기존 PR78은 Draft/open/unmerged로 유지한다. 실제 readback이 없으면 성공으로 올리지 않는다.

기존 CSR 8.35–8.78배와 제조 IVP 1.38–1.53배는 별개 이전 측정이다. 서로 곱하거나 이번 native canary 속도로 사용하지 않는다. 새 raw canary 반환 전 packed HE29 속도는 미측정이다. 저장 후보 hull은 참 ODE 오차반경이 아니다. 연속 스펙트럼, 전역 gas-temperature 오차상한, 전체 EoR, upstream Grackle 전체 동등성, 관측 Bianchi/CMB는 HOLD를 유지한다.
