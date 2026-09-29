# rei_microphysics 최종 반환 — 고정 parity FAIL

원 이론방에 붙여넣을 반환이다. `TESTED_SHA`는 아래 증거 commit을 만든 뒤 채운다. 이 문서는 기존 scientific state의 PASS를 변경하지 않는다.

- Repository: `cosmosapjw-quantum/rei_bianchi`
- Base `main`: `ae3402713c4b6530ab2b27f008f5f5d5c6a999ed`
- Source candidate: `5c56c8e905abb360c72603b8a5f7d653a869b159`
- Tested SHA: `PENDING_C2_COMMIT`
- Delivery SHA: 최종 원격 ref 확인 receipt에서 확정
- Branch: `forward/rust-reion-kernels-20260922`
- 결과: 일곱 함수의 Rust source 이식·컴파일·26개 Cargo 시험 PASS. 고정 f64 parity는 83/84 PASS, `transform_z_to_y`의 `transform_exp_extreme` FAIL. 따라서 전체 pinned-function parity와 BASS exact-rev dependency 후보는 **FAIL / 보류**.

## 고정 입력과 원문 회수

Python 원문 두 blob은 각각 `3d806e1c1d3bb523bb3c339d1a141f67d7f10069`, `6f5c13f02d0e549e581a02d3c4d8b8313b209bbf`로 base와 일치한다. `SOURCE_IMPORT_LOCK.json`과 Git의 `source_subset`은 Python 모듈 2개와 A7/A6 경계 자료 7개를 보존한다. A7 로컬 archive `BASS_ATOMIC_A7_T5_THEORY_READY_FINAL_20260922T1704KST.zip`는 8,541,005 bytes 및 SHA256 `9ef3929dd1164c482cb200a7c1a10e57e1e0a78c6ab47c9cc8dfd8f5fc23ce6a`로 이번 실행에서 확인했고, 추출된 A7 경계 파일 4개는 원 archive member와 byte 일치했다. source lock의 기존 A7/A6 manifest 검증 기록을 새로 실행한 것으로 주장하지 않는다. 이 subset은 physical rate source가 아니다.

## 명령·exit·원로그

원로그: [`evidence/final_local_20260929/`](evidence/final_local_20260929/). `final-commands.json`에 exact argv와 각 exit가 있다.

| 명령 | exit | 결과 |
|---|---:|---|
| `sha256sum -c docs/forward/rust-20260922/CODE_INPUT_MANIFEST.sha256` | 0 | 24개 경로 일치 |
| `python scripts/check_rust_forward_parity.py --check-contract` | 0 | 84 fixture, 5 protocol, 10 guard; Rust 실행 아님 |
| `python docs/forward/rust-20260922/evidence/test_checker_receipts.py` | 0 | receipt 10개, test double 범위 |
| `cargo fmt --manifest-path rust/rei_microphysics/Cargo.toml -- --check` | 0 | PASS, 첫 실행 exit 1 후 deterministic rustfmt 적용 |
| `cargo test --manifest-path rust/rei_microphysics/Cargo.toml --locked` | 0 | integration 21 + frontend 5 PASS |
| `.venv/bin/python scripts/check_rust_forward_parity.py --output <receipt>` (`cuhg-telemetry run` 경유) | 1 | 83/84 PASS, frozen comparison FAIL |
| `.venv/bin/python -m pytest <node-lift stage test> -q -k "positive_projection or signed_transfer"` | 0 | 기존 stage 모듈 3 PASS, 5 deselected; exact pinned Python 대 Rust 비교는 위 parity 참조 |

첫 기본 `python` parity는 JAX 미설치로 import 단계 exit 2였고 원로그를 보존했다. 저장소 `.venv`로 실행한 원 비교는 두 순서의 Rust child 모두 exit 0이었다. 유일한 비교 실패에서 `exp(-745)`의 Rust 값은 `4.94065645841246544e-324`, JAX 참조는 `0`이었다. 고정 `RTOL=5e-13`, `ATOL=0`, zero scale 때문에 실패한다. subnormal/FTZ를 위한 cutoff, floor, 허용치 변경은 하지 않았다. 이것은 f64 구현 비교이지 outward interval proof가 아니다.

| 함수 | fixture 판정 |
|---|---|
| `transform_z_to_y` | FAIL: extreme subnormal 1건; 나머지 9건 PASS |
| `pchip_eval` | PASS: 15/15, 밖 domain은 명시적 error API |
| `opacity_cMpc_inv` | PASS: 10/10, lowgroup HI owner와 G2a HeI 유지 |
| `photon_rates` | PASS: 14/14, 단독 group·무방출·redshift telescoping·네 site |
| `gamma_species` | PASS: 8/8, CGS/SI 및 `(1+z)^3` 한 번 |
| `positive_mass_projection` | PASS: 15/15, zero/negative/nonfinite 분기 |
| `signed_transfer_lift` | PASS: 12/12, 음수 transfer와 zero/invalid 분기 |

원 네 source site와 validated enclosure는 유지했다. `PROJECT_STATE.json` 및 `external/rec_bianchi.lock.json`은 미변경이다. S3 accepted/S4 partial/S5 gated/G10 open/G11–G13 gated, D86 canonical, P0 physical OPEN, HOST4 physical HOLD, HH propagation unauthorized를 유지한다. C9 CP0, P0 locator, HOST4 H19 COUNT, HH R10을 이 Rust source에 넣지 않았다. whole interval, 2048/4096 enclosure, full microstep sweep, benchmark, PR/merge/release는 실행하지 않았다.

다음 작업은 이 parity FAIL 상태의 port 종료다. BASS exact-rev integration은 통과한 Rust SHA가 없으므로 진행하지 않는다.
