# C9 addendum — portable prepare/runner 최종 검토

검토자: `/root/dropbox_v15_intake` (독립 Astra). 새 runner의 작성자가 아니며, 이번 검토에서는 source 및 보존된 실제 prepare/subprocess 자료를 읽고 hash를 대조했다. 새 native build·과학 이력 실행·Git/cloud 변경은 수행하지 않았다.

**판정: PASS_RUNNER_ADDENDUM. 확인된 blocker 3건 CLOSED, 미해결 blocker 없음.** 앞선 19개 native 설정에 대한 C9 판정과 실행 수는 그대로 유지한다. 이번 추가 검증은 준비·실행기의 process 제어에 관한 것이며 새로운 native 물리 사례로 집계하지 않는다.

## 최종 source 결속

| 파일 | SHA256 |
|---|---|
| `prepare_and_run.py` | `d741b1c9aa737627ae6acfaa3036ad8e6c61c4f791c7c5fd2a206efedd4def8e` |
| `README.md` | `e12166ed8cca48092a3067d333d7c85f23f53df39641150dfcce58e0a8a68359` |
| `Cargo.lock` | `789482fe16f54ba36bd4502bbc072429029d27de0778c7d3b7bdd0984457f337` |
| `BASE_NATIVE_MANIFEST.json` | `07b4f1c0af410413f3cf171cb0e60a3e6ea54e064af3c56811a5dbf1e74d8795` |
| `VIGILODE_SOURCE_MANIFEST.json` | `57319f1325ac12be58da31c5ead8520b7d86d65b40f6f7d1ffdac294affd4c11` |

`RUNNER_FINAL_PREPARE_AUDIT.json`에 최종 source hash, 실제 준비 결과, 여섯 stub subprocess의 원본 outcome·로그 hash 및 archive mapping 검증을 저장했다. 초기 준비 결과에 대한 검증은 `RUNNER_INITIAL_PREPARE_AUDIT.json`에 별도로 남아 있다.

## Git 경로와 source 복원

선언된 일반 Git 배치는 `research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/prepare_and_run.py`이다. 이 위치에서 runner의 `ROOT.parents[1]`은 기존 bridge root를, `ROOT.parent/time_centered_ssprk2_20261019/restore_ssprk2_native.py`는 이미 게시된 SSPRK sibling 복원기를 가리킨다. 다른 배치에서는 명시적 `--input-root`, `--ssprk-restore`를 사용한다. Runner를 이 선언과 다른 하위 `implementation/` directory에 그대로 배치하면서 default 경로가 같다고 주장하면 안 된다.

새 output workspace는 기존 경로가 있으면 거부한다. 원래 V14→SSPRK 복원 chain의 stdout/stderr/exit를 먼저 보존하고, 152개 baseline 파일을 hash로 검증한다. 이후 exact 173-byte transport hook을 붙이고 새 native module을 복사한다. 기존 parent는 hook을 제외한 prefix로 다시 비교하며 다른 151개 baseline byte도 다시 비교한다.

최종 실제 output `v16_work/prepare_only_symlink_fixed_verified`에서 152개 native baseline, hook, 477개 VigilODE 파일을 직접 읽어 검증했다. 불일치 0개이다. 복원된 adapter의 `Cargo.lock`, `src/lib.rs`, `src/main.rs`, `tests/focused.rs`는 앞서 실제 실행한 최종 N=4 및 19-case matrix의 source hash와 동일하다. 상대 Cargo dependency는 fresh workspace의 `native_owner/rust/rei_microphysics`와 `vigilode/crates/{rodas5p-integrators,rodas5p-core}`로 올바르게 해석된다.

VigilODE source pin은 `8a8bd409b1d96c7b7421f496d229e119fd3d284e`이다. Local source closure를 지정하면 477개 파일을 복사 전·후 검증한다. Archive 경로는 전체 SHA256 `823164c2e78c0b3229e45df0087dd9af094d6900b6eb76f1dd66d9f3fb4af409`에 결속된다. 온라인 다운로드도 immutable URL 한 곳의 이 archive만 허용하며 hash를 검증한 뒤 추출한다. 추출은 exact root prefix 및 477개 whitelist에 제한되고, 상위 경로 이동·중복·비정규 whitelisted member·누락을 거부한다. `extractall`은 사용하지 않는다.

이번 최종 prepare 관측은 검증된 local source closure를 사용한 경로이다. Archive 다운로드 경로는 실제 source로 검토했으며, 동일 archive의 이전 전체 byte 검증을 재사용한다. 이번 단계에서 다운로드·native build·과학 실행을 새로 했다고 주장하지 않는다.

## Cargo lock과 실행 환경

Lockfile은 byte 단위로 복사되고 재생성하지 않는다. 실제 frozen registry cache에서 `private-gemm-x86 0.1.20`은 yanked로 표시되어 있다. Lockfile checksum은 `0af8c3e5087969c323f667ccb4b789fa0954f5aa650550e38e81cf9108be21b5`이다. 이 사실 때문에 lock 없이 dependency를 재해석하는 경로를 만들면 안 된다. 현재 runner는 `cargo fetch --locked`를 먼저 사용하며, offline 요청이면 fetch에도 `--offline`을 붙인다. 이후 build와 focused tests는 모두 `--offline --locked --release`이다.

실행 전 실제 Cargo/Rustc `-Vv`, invocation executable byte hash 및 host metadata를 보존한다. 현재 보존된 실제 toolchain 출력은 Cargo/Rustc 1.94.1이다. Toolchain identity 조회와 Python stub은 native 연구 실행으로 집계하지 않는다.

## 발견한 구체적 문제와 최종 수정

1. **실패한 case를 기록한 뒤 전체 runner가 exit 0으로 끝나던 문제 — CLOSED.** `run_cases`는 failed/truncated/family-blocked/budget-unrun 행이 하나라도 있으면 `overall_exit_code=1`과 해당 matrix를 기록하고 1을 반환한다. `main`의 반환값은 실제 process exit로 전달된다. 실제 process 회귀에서 첫 family 실패 후 후속 refinement는 미실행, 독립 family는 완료, 전체 exit는 1인 경로를 확인했다.

2. **다음 case가 남은 총 예산보다 오래 실행될 수 있던 문제 — CLOSED.** 매 case의 timeout은 `min(40, remaining_budget)`이다. Truncation에서는 미완성 raw의 짧은 시간값에 의존하지 않고 실제 whole-process wall을 청구한다. 0.05초 예산을 준 실제 Python subprocess 회귀는 timeout으로 중단되고, 다음 family를 `NOT_RUN_TOTAL_BUDGET`으로 남겼다. OS 종료 처리에 필요한 작은 초과 시간도 감추지 않고 측정값에 포함한다.

3. **Cargo/Rustc symlink를 resolve하여 multicall 실행 이름이 바뀌던 문제 — CLOSED.** 새 `invocation_path`는 절대 경로만 구성하고 symlink는 dereference하여 실행하지 않는다. 따라서 Cargo/Rustc shim basename을 유지한다. 파일 hash는 링크가 가리키는 byte를 읽으므로 실행 경로와 byte identity를 각각 기록한다. 실제 symlink dispatch stub은 `dispatch=cargo`, `dispatch=rustc`와 `-Vv` 인자를 출력했고 두 process가 exit 0이었다.

관련 README도 실제 cap 소유권으로 정정되었다. 두 방법은 native RHS attempts 200000을 제한한다. Radau는 추가로 내부 30초 Budget을 사용한다. 기존 SSPRK chemical API에는 내부 wall 검사 자체가 없으므로 모든 case의 외부 process timeout 및 남은 총 예산으로 구분해서 서술한다. 기존 raw의 `config.case_wall_cap_s`는 Radau Budget 설명이며, 과거 raw byte는 변경하지 않았다.

Source archive는 각 member와 원래 source path의 명시적 mapping을 입력 receipt에 저장한다. 실제 성공 stub의 archive를 열어 이 mapping과 byte hash를 직접 대조했다.

## 실제 준비·회귀 결과와 유한 실행 범위

- `receipts/prepare_only_symlink_fixed/outcome.json`: exit 0, wall 0.5158324259973597초, native builds 0, scientific runs 0.
- 실제 nested native restore: exit 0, stdout/stderr 전체 hash 일치.
- `prepare_runner_symlink_tests` 출력: 네 process-plumbing test OK. 이들은 명시적으로 `PROCESS_TEST_STUB`이며 native solver·history가 아니다.
- 보존된 여섯 subprocess outcome은 의도한 실패·성공·timeout·Cargo/Rustc dispatch를 포함하고 각각의 stdout/stderr hash가 일치한다.
- `--prepare-only`는 source 복원·검증 이후 종료하며 Cargo fetch/build/test/과학 case로 진행하지 않는다.
- `--all`의 실제 source 목록은 fixed Radau 4개 + fixed SSPRK 3개 + source-on 6개 + disabled-source 6개로 정확히 19개이다. 먼저 실행하는 Cargo test target은 library 분류 회귀 1개와 focused native test 6개, 총 7개이다. Python process 회귀는 이 `--all` native test 수에 섞이지 않는다.
- 이번 최종 검토에서 이 19개 또는 Rust test 7개를 다시 실행하지 않았다. 새 runner의 복원 결과가 이미 검토·실행된 동일 수치 source와 lock을 재현한다는 근거를 사용한다.

Root가 위의 최종 runner bytes, README, manifests와 실제 prepare/process receipts를 C10 게시·백업에 함께 결속하면 된다. 추가 native 실행을 완료 조건으로 요청하지 않는다.

