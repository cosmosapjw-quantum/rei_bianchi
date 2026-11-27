# NCP: 준비된 네 기준해와 새 read-only budget 분석

## 수행 범위

최신 GitHub·백업·접근 가능한 NCP 결과와 실행 중 프로세스를 먼저 읽는다. 새 HE29 반환은 source/binary/table identity를 확인한 뒤 분석한다. 이 인계의 마지막 관측은 기준해 0/4, 새 제출·시작 0건이다. Remote Desktop Commander의 기존 월간 quota와 재시도·재연결 금지를 유지한다. 접근 권한이 있는 실행자가 현지 상태를 확인한다.

실행 source는 Git이다. 원래 과학 revision `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f`, native owner `f7830e2f55e7a1938bc3c98f61b60651f8dae474`를 유지한다. NCP 작업은 컴파일·작은 환경 수정·실제 실행에 한정한다. 사용자는 파일 다운로드·업로드·터미널 명령을 대신 수행할 필요가 없다.

원래 `../CODEX_HANDOFF_PROMPT_KO.md`의 baseline 실행 블록은 그대로 사용한다. 완료된 source validation 생략과 입력 manifest 보정의 두 overlay를 모두 적용한다.

| overlay | SHA256 |
|---|---|
| `ncp/REUSE_SOURCE_VALIDATION_20261019.patch` | `cd0b7ab40688b3c60ab689876690b2edd71aea5268b4e7ff285a637ca094a33e` |
| `ncp/REPAIR_INPUT_MANIFEST_20261020.patch` | `71f16bc8bc946bdd9107c476662fb83b9812cb4078045b933066fca300eb1e85` |

기존 결과나 중복 실행이 없을 때 필요한 네 pair만 실행한다. 모두 m8/GL4/q0, 각 case Radau+DOP853이다.

| key | r | table nodes |
|---|---:|---:|
| `m8_r2_table512` | 2 | 512 |
| `m8_r4_table512` | 4 | 512 |
| `m8_r8_table512` | 8 | 512 |
| `m8_r4_table1024` | 4 | 1024 |

case당 process-group 상한3600초, table600초·예상 allocation2GiB, numerical thread1과 첫 실패 중단을 유지한다. 2GiB는 전체 RSS 강제 상한이 아니다. 완료 case를 재실행하지 않는다. HE28 transport6개, HE29 90/720·50 tests, 완료된 VigilODE·Schur·ABI2·이번 budget 검사도 재실행하지 않는다.

## 저장 반환을 분석하는 새 명령

다음은 적분기를 호출하지 않는다. baseline 실행 shell의 `HE29_STAGE`, `HE29_WORK_ROOT`는 실제 저장 작업의 경로를 그대로 사용한다. 다른 실행자가 이어받으면 해당 기존 receipt에서 경로를 찾는다. 임의의 빈 경로를 완료 결과로 대체하지 않는다.

별도의 Git 분석 checkout에서 최신 DELIVERY가 가리키는 실제 analysis code commit으로 이동한다. 이미 복원된 baseline DATA를 `--data-root`로 읽으므로 원래 archive나 입력을 다시 다운로드할 필요가 없다. source/manifest는 분석 Git pin에서 읽고 DATA의 각 SHA를 확인한다.

```bash
set -euo pipefail
HE29_REL=research/he29_survival_budget_20261018
HE29_BASELINE_CHECKOUT="$HE29_STAGE/BASS_HE"
HE29_BASELINE_WORK_ROOT="$HE29_WORK_ROOT"
HE29_PY="${HE29_PYTHON:-$HE29_BASELINE_WORK_ROOT/venv/bin/python}"
[[ -x "$HE29_PY" ]]
HE29_BUDGET_STAGE="$(mktemp -d "${TMPDIR:-/tmp}/he29-budget.XXXXXXXX")"
git clone --branch research/he29-survival-budget-20261018 --single-branch \
  https://github.com/cosmosapjw-quantum/BASS_HE.git "$HE29_BUDGET_STAGE/BASS_HE"
cd "$HE29_BUDGET_STAGE/BASS_HE"
HE29_BUDGET_DELIVERY_REV="$(git rev-parse HEAD)"
HE29_BUDGET_REL="$HE29_REL/continuation_20261020T0557Z"
HE29_BUDGET_REV="$("$HE29_PY" - "$HE29_BUDGET_REL/DELIVERY.json" <<'PY'
import json, sys
p = json.load(open(sys.argv[1]))['implementation_publication']
if p['status'] != 'PUBLISHED_EXACT_GIT_READBACK_PASS':
    raise SystemExit('HE29_BUDGET_CODE_PUBLICATION_UNCONFIRMED')
revision = p['code_commit']
if len(revision) != 40 or any(c not in '0123456789abcdef' for c in revision):
    raise SystemExit('HE29_BUDGET_FULL_CODE_SHA_REQUIRED')
print(revision)
PY
)"
HE29_BUDGET_WORK_ROOT="$HOME/HE29_BUDGET_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir "$HE29_BUDGET_WORK_ROOT"
cp "$HE29_BUDGET_REL/DELIVERY.json" "$HE29_BUDGET_WORK_ROOT/PUBLICATION_DELIVERY.json"
printf '%s\n' "$HE29_BUDGET_DELIVERY_REV" > "$HE29_BUDGET_WORK_ROOT/DELIVERY_COMMIT.txt"
printf '%s\n' "$HE29_BUDGET_REV" > "$HE29_BUDGET_WORK_ROOT/ANALYSIS_CODE_COMMIT.txt"
git checkout --detach "$HE29_BUDGET_REV"
[[ "$(git rev-parse HEAD)" == "$HE29_BUDGET_REV" ]]
[[ -z "$(git status --porcelain --untracked-files=all)" ]]
HE29_BINARY_ARGS=()
if [[ -f "$HE29_BASELINE_WORK_ROOT/build/he29_owner_server" ]]; then
  HE29_BINARY_ARGS=(--binary "$HE29_BASELINE_WORK_ROOT/build/he29_owner_server")
fi
HE29_BUDGET_RC=0
"$HE29_PY" "$HE29_BUDGET_REL/src/analyze_budget.py" \
  --root "$HE29_BASELINE_WORK_ROOT/references" \
  --data-root "$HE29_BASELINE_CHECKOUT/$HE29_REL" \
  --out "$HE29_BUDGET_WORK_ROOT/REFERENCE_BUDGET.json" \
  "${HE29_BINARY_ARGS[@]}" \
  > "$HE29_BUDGET_WORK_ROOT/stdout.log" \
  2> "$HE29_BUDGET_WORK_ROOT/stderr.log" || HE29_BUDGET_RC=$?
printf '%s\n' "$HE29_BUDGET_RC" > "$HE29_BUDGET_WORK_ROOT/EXIT_CODE.txt"
```

| exit | 뜻과 다음 행동 |
|---:|---|
| 0 | 네 pair와 필요한 대비·입력이 이 분석 계약에서 유효. 결과와 실제 source/binary/table receipt를 보존하고 다음 과학 분석으로 전달 |
| 1 | 누락·부분 완료·cohort 불일치 등으로 일부 행 HOLD. 저장된 유효 부분을 분석하고 필요한 미완료 case만 확인 |
| 2 | 잘못된 입력·반환 또는 분석 실행 오류. stdout/stderr, 저장 JSON의 구체적 오류를 읽고 최소 수정. 출력 파일이 없으면 CLI 자체 실패로 기록 |

출력은 create-only이며 기존 JSON을 덮어쓰지 않는다. 다른 snapshot을 읽을 때는 새로운 분석 디렉터리를 사용한다. 실제 binary 경로가 없으면 `binary_bytes_readback=NOT_PROVIDED`가 기록된다. 기록된 binary SHA 검증과 실제 bytes 읽기를 혼동하지 않는다.

baseline checkout의 검증 DATA가 사라졌다면 이미 보존된 원본 `a70` archive를 기존 `../ncp/RESTORE_VERIFIED_INPUTS.py --archive ... --root ...`로 복원한다. 전체 SHA와22 DATA를 확인하는 기존 복원기를 사용한다. source를 archive에서 복구해 실행하거나 입력 복원을 위해 `START_REFERENCES.sh`를 다시 호출하지 않는다.

## 해석과 반환

새 output의 signed residual은 저장 transport와 선택한 수치 기준 후보의 차이다. `product_hull`은 key별 독립 후보 선택, `coherent_hull`은 모든 key의 동일 method 선택이다. exact hull width와 binary64 display width를 구분한다. 두 method의 일치를 참 해의 오차반경으로 사용하지 않는다.

모든 native 반환에서 `IDENTITY.json`, `TABLE.json`, `SAVED_POINT_PARITY.json`, 각 method JSON, `RESULT.json` 또는 `FAILURE.json`, native stream 및 process COMMAND/RECEIPT/stdout/stderr를 보존한다. method 적분 시간과 case 전체 시간을 따로 유지한다. 이번 analysis JSON·분석 code pin·DATA root provenance·exit code도 같은 반환에 포함한다.

원래 절대 fraction1e-11, 방법 간 온도차1e-9K, number3e-15/H, energy3e-12eV/H, species3e-12 및 양성성 gate를 유지한다. 네 pair 모두 admit되기 전에는 optional packed canary를 시작하지 않는다. 그 다음 단일 r4/table512 canary에는 이미 게시된 `a5d4711460c09b310b78c9692aa62534b7a843d3`와 `../optimization_20261020/NCP_HANDOFF_KO.md`를 사용한다. VigilODE a21, thread1, 원래 full-state ledger norm을 유지한다.

새 반환은 별도 results branch/Draft PR 및 create-only Drive·Dropbox 백업으로 보존한다. PR78은 Draft/open/unmerged다. source commit, archive SHA/size, provider ID/content_hash, 실제 raw readback과 내부 검증을 각기 기록한다. 제출·시작은 실제 접수 근거가 있을 때만 표시한다.

연속 스펙트럼, 전역 gas-temperature 오차상한, 전체 EoR, upstream Grackle 전체 동등성, 관측 Bianchi/CMB는 해당 범위 검증 전까지 HOLD다.
