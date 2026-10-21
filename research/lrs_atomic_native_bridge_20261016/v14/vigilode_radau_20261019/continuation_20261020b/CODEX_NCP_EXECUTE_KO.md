## 현재 전달 상태 — 실제 게시와 archive·sidecar 양쪽 전체 읽기 검증 완료

실제 stage1 commit은 **82364d3d2548a1e864468cb781336f825fc18c29**이며 원격 22파일의 전체 내용과 Git blob SHA가 모두 일치했다. 실행 source **5248822167e3fbe374f4333f7f2efdcdbfdaeeaf**와 과학 판정은 그대로다. 이 최종 metadata의 Git identity는 이를 담는 **ENCLOSING_COMMIT**이며, 아직 수행하지 않은 최종 ref 이동·원격 readback의 성공을 미리 주장하지 않는다.

고정 archive `REI_LRS_NCP_RETURN_RECOVERY_20261020.tar.xz`는 **1,816,608 bytes**, SHA256 `089a1ab2bf05f3368b77b5ec330bfb394b176e7f0b89ce7e32ce6eb2c71390be`다. 233파일의 manifest SHA256은 `6f438f505571d396c91ae1b13f2baabf41bc9497c64b71291539496a4ac9cebe`다. Drive `1XMokGRZfOeE284bvC0wJHuzD86rNMLRl`, Dropbox `id:BSpOijBcT10AAAAAAD_aEw`에서 전체 회수한 bytes·SHA256이 모두 일치했다.

별도 sidecar `REI_LRS_NCP_RETURN_RECOVERY_20261020_ACK.json`도 **4,735 bytes**, SHA256 `71ed1fbf1a5179d13199f321d6b01cf7591b4a9e116dc31342d02bc7b455a6c0`으로 Drive `1sMHEilLsvPF19lWhQ8gr1CgLzS8aB5TB`, Dropbox `id:BSpOijBcT10AAAAAAD_aFQ`의 전체 회수가 모두 일치했다. 모든 회수 process exit는0이다. Drive의 원천 HTTP 상태는 connector가 노출하지 않으며 raw fetch 성공 및 materialization HTTP200을 확인했다. Dropbox 직접 GET은 HTTP200이다.

archive 내부 PREPARED_NOT_PUBLISHED는 동결 당시 상태다. 실제 순서는 archive 동결 → Git 게시와 archive 양쪽 읽기 검증 병행 → sidecar 양쪽 읽기 검증 → 최종 metadata commit이다. archive·sidecar bytes와 과학/analysis/review 원문은 바꾸지 않았다. 이번 native 실행·build·Rust/native/numerical source 변경은0이며, 원래 C10 archive 필드는 역사 범위로 보존한다.

[최종 실제 ACK](ncp_return_analysis_20261020/FINAL_PUBLICATION_ACK.json)에서 실제 게시·archive·sidecar 회수 receipt와 승인 범위를 확인한다. 다음 과학 작업은 실제 profile이 지목하는 optimizer 하나에 한정하며 완료된 native 실행을 강제 반복하지 않는다.

# 현재 상태 — NCP 반환 완료, 2026-10-20T110800Z

상태 갱신: 2026-10-20T17:20:33Z. 실행 source **5248822167e3fbe374f4333f7f2efdcdbfdaeeaf**, VigilODE pin **8a8bd409b1d96c7b7421f496d229e119fd3d284e**의 실제 NCP 결과를 회수했다. metadata intake HEAD는 **90c46b3d305ae7d1c3a6d54cd5de6b55dfdc70ec**이며 실행 source와 구분한다.

Locked release build exit 0 (345.147809 s), Rust 4 unit + 6 integration = **10 PASS**, 기존 **cell-cache 19설정(10 Radau + 9 SSPRK 대조) 모두 완료**다. 누적 RHS 시도 38,840, raw 내부 경과시간 합계 4.937230308 s다. `cell-borrowed` fixed Radau N2의 exit 0과 유한 물리값 일치가 반환됐다. 이 대화의 새 native 실행·build는 각각 **0**이며 저장된 반환 증거를 분석한다.

NCP binary SHA256은 **c93db685071037797d057f58d2fc88d5dccd5255b3d6441cd1a55d9a2d7f7992**다. 이전 C10 sandbox binary `3eeda61b64529a83b2604b6e08d448e5b11f067a81faf70bd12509076dde106a`와 다른 실행 산출물이다. borrowed 개별 argv·inputs receipt·outcome receipt·binary hash는 archive에 없다. 동일 binary 연결은 delivery의 진술이며 독립 borrowed receipt로 복원되지 않는다. 명령을 추정하지 않으며 이 제한만으로 native 재실행을 의무화하지 않는다.

N2의 RHS 395·cell preparations 2,680·node visits 252,800은 같고 지정 상태/node clone은 cache 338/216,320 대 borrowed 0/0이다. raw wall은 cache 0.041180299 s, borrowed 0.061808789 s이며 stderr 마지막 0.091509 s는 측정 경계가 다르다. **speedup·memory reduction은 NOT_ESTABLISHED**, default legacy·성능 경로와 batch cell-cache는 유지한다. source-on 일반2차·uniform stiff·일반 양수성·Case B/full EoR/signed Bianchi·넓은 positive-CMB/비영 boundary·continuous global certificate는 HOLD, production은 NOT_ISSUED다.

archive `REI_LRS_V14_CACHE_BORROWED_NCP_20261020T110800Z.tar.gz`: 47,372,583 bytes, SHA256 `b1cb2ce21c14626794c69585822a29ed016206769ec1dd217ae59ec3f70f53bd`. 이전에 게시된 이 archive의 양쪽 full readback receipt와 이번 회수 증거를 구분한다. 저장소 CI 두 job의 cargo fmt 실패·cargo test skipped도 NCP 표적시험 PASS와 별개다.

다음 행동은 반환 결과를 사용하고, 실제 profile이 병목을 보일 때 후속 optimizer 하나만 선택하는 것이다. 완료된 build·19설정·N2 smoke를 강제로 반복하지 않는다. 이번의 승인 범위는 ADMIT_SCOPED_NCP_EXECUTION_AND_FINITE_SAVED_OUTPUT_AGREEMENT이며, 독립 판정 PASS_SCOPED_NCP_EXECUTION_AND_FINITE_SAVED_OUTPUT_AGREEMENT와 함께 반환 분석 STATE와 review/에 기록했다.

[반환 분석](ncp_return_analysis_20261020/REPORT_KO.md), [상태](ncp_return_analysis_20261020/STATE.json), [다음 대화](NEXT_THREAD_PROMPT_KO.md)를 먼저 읽는다.

---

## 보존한 C10 기록 — 2026-10-20 07:39 UTC 상태

아래 NOT_RUN은 당시 시점에만 적용한다. 아래 실행 명령은 보존된 선택적 재현 절차이며 완료된 NCP 작업을 재실행하라는 지시가 아니다. borrowed 실제 argv를 이 명령으로 대체하지 않는다.

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

