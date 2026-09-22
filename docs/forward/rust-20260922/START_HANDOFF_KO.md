# 최종 local Codex 인계: rei_microphysics

ROLE=LOCAL_CODEX_FINAL_BOUNDED_RUST_VERIFICATION
REPO=cosmosapjw-quantum/rei_bianchi
TARGET_BRANCH=forward/rust-reion-kernels-20260922
BASE_COMMIT=ae3402713c4b6530ab2b27f008f5f5d5c6a999ed
HANDOFF_TIMING=AFTER_ALL_APPROVED_SOURCE_PORTS_ONLY
PRODUCTION_MUTATION=NO

## 도착점

이 문서는 중간 단계 호출이 아니라 승인된 일곱 함수의 source 이식이 끝난 뒤 사용하는 최종 인계다. SOURCE_PHASE_CLOSEOUT.json의 COMPLETE는 source 작성 범위의 완료이며 컴파일·실행·parity PASS가 아니다. 실제 candidate SHA/tree는 전달된 게시 receipt와 fetch한 ref에서 고정한다. C1 dd625391, C1a 02634b07 이후 Rust frontend의 행별 오류 처리와 시험을 보완했다. C1a의 실패 receipt 보존은 그대로다.

원문과 library kernel 식, frozen 84 parity 입력, 5 protocol 입력, 2 Python shape 입력, RTOL=5e-13/global ATOL=0은 변경하지 않았다. Rust 검사 선언은 integration 21개와 example unit test 5개다. 실제 test 개수·성공 여부는 실행 로그에서 판정한다. Cargo.toml의 example test=true가 frontend 검사를 cargo test에 포함하도록 설정되어 있다.

## 읽기와 checkout

기존 rei_bianchi checkout에서 origin/branch/AGENTS/dirty state부터 읽는다. 새 worktree, reset/stash/clean, 자동 rebase를 하지 않는다. 다른 사용자 변경과 충돌하는 파일만 보류한다.

```bash
git rev-parse --show-toplevel
git remote -v
git status --short
git branch --show-current
git fetch origin forward/rust-reion-kernels-20260922
git rev-parse FETCH_HEAD
git show -s --format='%H %T %P' FETCH_HEAD
```

target을 안전하게 checkout한 후 이 폴더의 SOURCE_IMPORT_LOCK.json, PARITY_POLICY.json, SOURCE_PHASE_CLOSEOUT.json, FORWARD_STATUS.json만 먼저 확인한다. 원 Python reference 전체 bytes가 source_subset/python에 있으므로 과거 archive를 다시 다운로드하지 않는다. 기존 handoff의 whole-interval continuation을 시작하지 않는다.

## 최종 검증

다음 명령의 stdout/stderr/exit를 각각 새 run 폴더에 보존한다. 환경 성공/실패를 이전 세션에서 승계하지 않는다.

```bash
rustc --version
cargo --version
python --version
sha256sum -c docs/forward/rust-20260922/CODE_INPUT_MANIFEST.sha256
python scripts/check_rust_forward_parity.py --check-contract
python docs/forward/rust-20260922/evidence/test_checker_receipts.py
cargo fmt --manifest-path rust/rei_microphysics/Cargo.toml -- --check
cargo test --manifest-path rust/rei_microphysics/Cargo.toml --locked
```

실제 원 Python/JAX와 Rust를 함께 실행하는 parity는 다음과 같이 기록한다.

```bash
RUN_DIR=$(mktemp -d "${TMPDIR:-/tmp}/rei-microphysics-final.XXXXXXXX")
if python scripts/check_rust_forward_parity.py --output "$RUN_DIR/parity.json" \
    >"$RUN_DIR/parity.stdout.log" 2>"$RUN_DIR/parity.stderr.log"; then
    PARITY_EXIT=0
else
    PARITY_EXIT=$?
fi
printf '%s\n' "$PARITY_EXIT" >"$RUN_DIR/parity.exit"
printf 'PARITY_EXIT=%s LOG_DIR=%s\n' "$PARITY_EXIT" "$RUN_DIR"
```

nonzero exit면 PASS로 진행하지 않는다. --check-contract와 10개 Python receipt 회귀검사는 Rust를 실행하지 않는다. receipt 회귀검사의 subprocess/reference는 명시적 test double이며 물리 관측값이 아니다. child timeout/nonzero/import 오류 로그와 원 exit를 보존하고 reference 실패를 재작성 식으로 대체하지 않는다. 파일이 이미 존재하면 다른 새 output을 사용한다. checker 자체가 SIGKILL되거나 저장장치가 실패하면 JSON 완결성을 보장할 수 없으므로 외부 stdout/stderr도 남긴다.

## 허용된 수리와 금지

fmt와 compile/type/adapter의 구체적 오류 및 원문 불일치만 최소 수정할 수 있다. 기존 실패 로그와 manifest를 보존한 뒤 수정 파일의 hash를 갱신한다. 고정 fixture·policy·원문 pin을 결과에 맞춰 바꾸지 않는다. kernel 표현 변경이 필요하면 실제 원문/반례와 함께 기록한다. Rust/JAX의 subnormal·FTZ·reduction·libm 차이는 실제 실행으로 판정하며 cutoff/floor/threshold 조절로 감추지 않는다. 새 dependency와 전체 cargo update는 금지한다.

gamma 함수는 opacity table을 계산하지 않는다. 다만 현재 CLI의 공통 GroupParams decoder는 구조적으로 유효한 두 table을 요구한다. 이는 frontend 구성 계약이며 gamma의 물리적 table 의존성으로 해석하지 않는다. 원 dict의 모든 자유로운 입력 형태와 동일한 API라고 주장하지 않는다.

기존 Python src, PROJECT_STATE.json, external/rec_bianchi.lock.json, stage 데이터는 변경하지 않는다. scipy 최적화 두 함수, ODE/residual/rate fit, production 배선, 새 physical source는 범위 밖이다. 네 source site를 하나의 cache로 합치지 않는다. full pytest, 2048/4096 enclosure, 전체 interval/history, benchmark campaign은 실행하지 않는다.

S3 accepted / S4 partial / S5 gated / G10 open / G11-G13 gated, D86 canonical, P0 physical OPEN, HOST4 physical HOLD, HH propagation unauthorized를 유지한다.

## 최종 게시와 이 스레드로의 반환

local 최소 수리와 evidence/status 갱신을 한 C2에 묶는다. 최종 HEAD에서 필수 검증을 다시 실행한 뒤 계산 code/input/test/policy를 바꾸지 않는다. 그 HEAD와 원로그를 repository 밖 최종 receipt에 기록해 자기 SHA 삽입 commit 반복을 피한다. 모든 필수 검사 통과 때만 구현 검증 완료라고 한다.

```bash
git push origin HEAD:refs/heads/forward/rust-reion-kernels-20260922
git ls-remote origin refs/heads/forward/rust-reion-kernels-20260922
```

tested HEAD와 원격 SHA가 같으면 종료한다. 새 PR/merge/release/force push/workflow_dispatch 또는 전체 재다운로드는 하지 않는다. 자동 verify CI는 verify_repo.py 범위일 뿐 Rust 검증을 대체하지 않는다.

반환은 base/source-candidate/tested/delivery SHA, tree, branch, 변경 경로, command+exit+원로그, 일곱 함수별 PASS/FAIL/SKIPPED, 잔여 오류·HOLD·원격 ref를 포함한 RETURN_HANDOFF_KO.md 한 번으로 한다. 최종 검증된 delivery만 bass exact-rev 후보로 반환하고 bass repository는 변경하지 않는다.
