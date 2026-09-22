# Local Codex: rei_microphysics 후보 검증

ROLE=LOCAL_CODEX_BOUNDED_RUST_VERIFICATION
REPO=cosmosapjw-quantum/rei_bianchi
BASE_COMMIT=ae3402713c4b6530ab2b27f008f5f5d5c6a999ed
TARGET_BRANCH=forward/rust-reion-kernels-20260922
NEXT_ACTION=FETCH_CANDIDATE_THEN_BUILD_AND_PINNED_FUNCTION_PARITY
PRODUCTION_MUTATION=NO

이 후보는 Rust를 컴파일하거나 실행하지 않은 source-first 이식이다. 원문/입력 계약과 작은 독립 toy의 검사는 Rust PASS가 아니다. 실제 candidate SHA는 전달된 remote ref receipt 또는 최초 fetch한 target ref에서 고정한다. 과거 PR #82, 과거 Python primitive 9 tests, pre-existing verify CI를 이 포트의 검증으로 사용하지 않는다.

## 이번 최소 수정: C1a

기준 C1 `dd6253912645a2f3a245f7b68413f8c51f15eec5` 이후 Python checker의 실패 기록만 수리했다. Rust 전체·Cargo pair·84개 frozen 함수 입력·두 원 Python reference·허용치는 C1과 byte-identical이다. C1a는 local C2 검증 완료가 아니다.

`evidence/test_checker_receipts.py`의 10개 검사는 subprocess/reference test double을 사용한 오류 기록 시험이다. 실제 Rust와 JAX를 실행하지 않는다. timeout, nonzero exit, reference import 오류, malformed reply 때도 새 `--output` receipt에 실패와 확보된 child 로그를 남긴다. 이미 존재하는 output이면 작업 시작 전에 실패한다. OS에 의해 checker 자체가 SIGKILL되거나 저장장치가 실패하면 완전한 JSON을 보장하지 않으므로 아래 외부 stdout/stderr 로그도 보존한다.

## 시작

이미 열려 있는 rei_bianchi checkout에서 origin, branch, AGENTS, dirty state를 먼저 확인한다. 새 worktree를 만들거나 사용자 변경을 reset/stash/clean하지 않는다. 같은 파일의 변경과 충돌할 때만 그 파일을 보류한다. 다음은 읽기/취득 명령이다.

```bash
git rev-parse --show-toplevel
git remote -v
git status --short
git branch --show-current
git fetch origin forward/rust-reion-kernels-20260922
git rev-parse FETCH_HEAD
git diff --stat ae3402713c4b6530ab2b27f008f5f5d5c6a999ed FETCH_HEAD
```

target branch를 안전하게 checkout하고 source snapshot SHA와 tree를 기록한다. main이 이동했어도 자동 rebase하지 않는다. 이 디렉터리의 SOURCE_IMPORT_LOCK.json, PARITY_POLICY.json, FORWARD_STATUS.json, evidence/STATIC_REVIEW_KO.md만 먼저 읽으면 된다. 전체 과거 dossier를 다시 읽거나 heavy continuation을 실행하지 않는다. 정확한 두 Python reference가 source_subset/python에 포함되어 있으므로 원 archive 추가 다운로드는 필요하지 않다.

```bash
rustc --version
cargo --version
python --version
sha256sum -c docs/forward/rust-20260922/CODE_INPUT_MANIFEST.sha256
python scripts/check_rust_forward_parity.py --check-contract
python docs/forward/rust-20260922/evidence/test_checker_receipts.py
cargo fmt --manifest-path rust/rei_microphysics/Cargo.toml -- --check
cargo test --manifest-path rust/rei_microphysics/Cargo.toml --locked
# 새 run 디렉터리에 원로그/JSON을 동시에 보존한다.
RUN_DIR=$(mktemp -d "${TMPDIR:-/tmp}/rei-microphysics-parity.XXXXXXXX")
if python scripts/check_rust_forward_parity.py --output "$RUN_DIR/parity.json" \
    >"$RUN_DIR/parity.stdout.log" 2>"$RUN_DIR/parity.stderr.log"; then
    PARITY_EXIT=0
else
    PARITY_EXIT=$?
fi
printf '%s\n' "$PARITY_EXIT" >"$RUN_DIR/parity.exit"
printf 'PARITY_EXIT=%s LOG_DIR=%s\n' "$PARITY_EXIT" "$RUN_DIR"
```

`PARITY_EXIT`가 0이 아니면 PASS로 진행하지 않는다. 0도 해당 고정 함수 f64 비교만 뜻한다.

각 명령 stdout/stderr/exit를 새 원로그로 보존한다. --check-contract는 JAX/Rust를 실행하지 않는다. 인수 없는 checker는 원 Python을 실제 실행하고 `cargo run --locked --example eval_fixture`를 호출한다. 실패 시 Rust-only 또는 재작성 Python 수식으로 대체하지 않는다. --output은 새 경로만 허용한다.

## 수리 범위

13개 Rust tests, 84개 frozen 함수 입력, 5개 malformed protocol, 2개 Python nested-prior 오류 case와 독립 단위/owner/telescoping/site invariant가 대상이다. 실제 수는 fixture와 시험 결과로 확인한다. 기대값은 관측값이 아니다.

허용치 RTOL=5e-13, global ATOL=0을 변경하지 않는다. cancellation-sensitive RHS/PCHIP는 고정 reference 항의 절댓값 합을 같은 단위 scale로 사용한다. 특별값과 underflow는 별도 분류한다. 특히 exp(-745) 등에서 JAX/backend의 FTZ와 Rust의 subnormal 보존이 다를 수 있다. 이것은 미검증 위험이며 예상 실패를 실행값으로 기록하지 않는다. 차이가 관측되면 원문/helper 의미와 플랫폼 근거를 먼저 확인하고, 임의 cutoff/floor나 tolerance 완화로 숨기지 않는다.

fmt의 순수 형식 수정, compile error, source-to-code 오타, checker 오류는 scope 안에서만 최소 수정할 수 있다. 기존 실패 로그와 원 manifest를 먼저 보존하고, 수정 후 기존 CODE_INPUT_MANIFEST에 열거된 파일들의 hash만 다시 계산한다. source pin과 frozen fixture/policy를 Rust 결과에 맞춰 수정하면 안 된다. 새 입력/허용치가 필요하다고 판단되면 실패로 반환한다. Cargo.lock은 외부 dependency 없는 수기 후보이므로 local --locked 수용을 확인하고 해당 crate 범위만 수리한다. 전체 cargo update/vendor graph 이식은 금지한다.

Python reference 패키지는 local 환경의 JAX/NumPy/SciPy이며 exact version과 JAX x64/backend를 기록한다. 필요한 환경 문제가 있으면 package/compiler/service와 구현 실패를 구별한다. 과거 runtime PASS/FAIL을 승계하지 않는다. C++ probe는 이 작업에 필요하지 않다.

## 중단선

원 Python src, PROJECT_STATE.json, external/rec_bianchi.lock.json, 기존 stage 데이터는 수정하지 않는다. source copy에 들어 있는 chemistry/residual/fit은 reference 전체 byte 복원용이지 Rust 이식 대상이 아니다. source_subset/atomic_parent_*는 boundary-only다. 일곱 API를 production solver에 배선하지 않는다. 네 source site를 cache 하나로 합치지 않는다.

S3 accepted / S4 partial / S5 gated / G10 open / G11-G13 gated, D86 canonical, P0 physical OPEN, HOST4 physical HOLD, HH propagation unauthorized를 유지한다. full repository pytest, 2048/4096 enclosure, whole interval/history, scientific eigensolve, benchmark campaign, 새 physical source는 금지한다. targeted 기존 tests가 있으면 실제 일곱 함수 import/call을 확인하고 작은 범위만 선택한다.

## 최종 commit/push/반환

최신 미검증 후보(C1a) 다음으로 local 최소 수정과 evidence/status/handoff를 한 C2에 묶는다. C2의 최종 HEAD에서 필수 세 명령과 manifest/diff 검사를 다시 실행하고 이후 계산 입력/source/test/policy를 바꾸지 않는다. 최종 로그와 tested SHA는 repo 밖 return receipt에 기록해 자기 SHA 삽입 commit 반복을 피한다. 모든 필수 검증이 닫힌 경우에만 implementation-verified로 표시한다. 실패가 남으면 PARTIAL/FAIL로 반환하고 보존한다.

```bash
git push origin HEAD:refs/heads/forward/rust-reion-kernels-20260922
git ls-remote origin refs/heads/forward/rust-reion-kernels-20260922
```

원격 ref와 tested HEAD가 같으면 R1 확인을 종료한다. 재clone/전체 readback을 반복하지 않는다. 새 PR, merge, release, force push, workflow_dispatch는 하지 않는다. 자동 CI scope와 결과는 별도로 기록한다. 최종 verified SHA만 bass exact-rev dependency 후보로 반환하고 bass 자체는 변경하지 않는다.

반환 항목: base/source-snapshot/tested/delivery SHA와 tree, actual branch, changed paths, command+exit+원로그, 7함수별 PASS/FAIL/SKIPPED, 변경하지 않은 scientific HOLD, remote ref. 이 스레드로 붙여 넣을 RETURN_HANDOFF_KO.md와 실패 원인/최소 다음 행동을 남긴다.
