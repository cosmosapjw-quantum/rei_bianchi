# RUN16 의존성 및 재현 경로

## 기본 재개는 저장 결과의 사용이다

RUN13 M2 standard/tight, RUN16의 세 prefix controls와 세 response settings는 이미 완료됐다. 다음 연구를 위해 이력을 다시 적분할 필요는 없다. `RESUME_KO.md`, `results/GAS_PATH_RESPONSE.json`, `feedback/PREFIX_EXECUTION_RECEIPT.json`을 먼저 읽는다. 실제 실행 당시의 exact argv, wall time, code/input hashes는 다음 파일에 있다.

- `execution/EXECUTION_RECEIPT.json`, `execution/TEST_RECEIPT.json`
- `feedback/EXECUTION_RECEIPT.json`, `feedback/PREFIX_EXECUTION_RECEIPT.json`
- `results/FEEDBACK_BLOCK_SCALES.json`

다음 명령들은 필요한 경우 새 디렉터리에서 수행할 **선택적 재현 예시**다. 이번에 실행한 명령과 혼동하지 않는다. 각 producer는 기존 output을 덮어쓰지 않는다.

## Source identity

Repository: `cosmosapjw-quantum/rei_bianchi`.

Base: `c875005e30d9de1ce7f426898e46fe912068412c` (RUN15 최종 전달).

Branch: `research/rei-run16-gas-path-sensitivity-20261019`.

RUN16의 첫 소스/결과 checkpoint: `2cc5e0862dbe9770ef83c0b2437e27627ec26524`. 최종 science와 delivery commit은 `DELIVERY.json`을 따른다. Remote branch는 나중에 진행될 수 있으므로 실제 HEAD를 읽고 필요한 commit을 고정한다.

원래 native 입력은 `run13/recovered`, 상속한 fixed-path kernel은 `run15/postloss_diagnostic/postloss_fixed_gas_optical_response.py`, PCHIP comparator는 `run15/source_recovery/theory/compare_gas_paths.py`다. Dependencies의 byte SHA가 다르면 새 스크립트는 거부한다. 이 guard를 임의로 제거해 다른 physics/provider로 실행하지 않는다.

## 필요한 디렉터리

Git에서 `research/atomic_nuclear_ssot_20261017/run13`, `run15`, `run16`을 같은 부모 아래 가져온다. RUN13의 큰 원본 파일은 byte transport로 보존되어 있어, 아직 실제 targets가 없다면 다음 원래 복원 명령을 쓴다.

```bash
python3 research/atomic_nuclear_ssot_20261017/run13/git_transport/restore.py \
  --destination-root research/atomic_nuclear_ssot_20261017/run13
```

이는 원래 chunks와 whole-file SHA를 확인한 후 byte를 조합하는 작업이다. 기존 target이 다르면 덮어쓰지 않고 실패한다. 원본 source를 추정하거나 과학 계산을 다시 수행하는 과정이 아니다.

RUN16 추가분 ZIP에는 RUN16 files와 실행에 사용한 원래 `runtime/gas_rhs_server`를 넣는다. 원래 RUN13 전체 archive와 RUN15 전체 archive를 중복 포함하지 않으므로, 그 추가분만으로 전체 입력이 생기지는 않는다. Archive의 `ARCHIVE_MANIFEST.json` 및 `ARCHIVE_IDENTITY.json`은 정확한 baseline dependency를 명시한다.

## 가벼운 response 재현

Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0에서 실행했다. 아래 `rei_root`는 위 세 run 폴더의 실제 부모로 정한다.

```bash
rei_root=/absolute/checkout/research/atomic_nuclear_ssot_20261017
python3 "$rei_root/run16/gas_path_response.py" \
  --run13-root "$rei_root/run13/recovered" \
  --run15-root "$rei_root/run15" \
  --output-dir /absolute/new-response-output
```

위 명령은 native RHS 또는 coupled IVP를 호출하지 않는다. 현재 기본 설정 E12/T24, E16/T24, E16/T32를 계산한다. 결과 JSON에는 runtime/path가 들어가므로 fresh 실행 JSON 전체 SHA가 producer JSON과 같은지는 과학 재현의 판정 기준이 아니다. 고정 입력/코드의 SHA와 해당 수치 필드, raw node arrays를 각각 비교한다.

Focused tests를 실행할 목적이 있으면 `run16`을 working directory로 두고 다음을 사용한다.

```bash
python3 -m unittest -v test_gas_path_response.py
```

과거 Rust160/Python11/guard10 또는 기존 whole histories를 이 명령에 추가하지 않는다.

## Native point/prefix 재현

원래 gas executable은 571,904 bytes, SHA-256

```text
3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b
```

이다. 이번 추가분 또는 이전 RUN15 archive의 같은 binary를 사용한다. ZIP에서 실행 mode가 보존되지 않는 환경이면 해당 파일에만 execute permission을 부여한 후 hash를 확인한다.

이 binary의 이전 실제 복원은 Rust/cargo 1.94.1, target `x86_64-unknown-linux-gnu`, 원래 crate에서 `cargo build --release --offline --locked --example gas_rhs_server --jobs 2`였다. 실행 당시 toolchain component identity, 환경 및 build command는 RUN15 `recovery/postloss_runtime_delivery/postloss_gas_build/ORIGINAL_GAS_REBUILD_RECEIPT.json`에 있다. 그 fresh build는 실제로 같은 SHA를 냈다. 이번 RUN16에서 toolchain 설치나 Rust build를 다시 실행하지 않았다. 다른 환경에서의 byte identity가 자동 보장된다고 주장하지 않는다.

다음은 archived reference를 읽는 선택적 예시다.

```bash
rei_binary=/absolute/unpacked-run16/runtime/gas_rhs_server
python3 -B "$rei_root/run16/feedback/recorded_state_feedback.py" \
  --source-root "$rei_root/run13/recovered" \
  --gas-binary "$rei_binary" \
  --output-dir /absolute/new-point-output \
  --native-budget-seconds 20

python3 -B "$rei_root/run16/feedback/source_free_prefix.py" \
  --source-root "$rei_root/run13/recovered" \
  --gas-binary "$rei_binary" \
  --point-result "$rei_root/run16/feedback/execution01/RECORDED_STATE_FEEDBACK.json" \
  --output-dir /absolute/new-prefix-output \
  --wall-cap-seconds 20

python3 -B "$rei_root/run16/feedback/prefix_step_halving.py" \
  --source-root "$rei_root/run13/recovered" \
  --gas-binary "$rei_binary" \
  --point-result "$rei_root/run16/feedback/execution01/RECORDED_STATE_FEEDBACK.json" \
  --prefix-result "$rei_root/run16/feedback/prefix_execution01/SOURCE_FREE_PREFIX.json" \
  --output-dir /absolute/new-prefix-halfstep-output
```

`--point-result`와 `--prefix-result`는 의도적으로 **게시된 reference JSON**을 받는다. Fresh 실행의 JSON에는 새 absolute path와 timing이 들어가므로 원래 reference SHA와 다르다. Fresh 결과를 그대로 다음 guard에 대입해 실패했다고 물리 오류로 분류하지 않는다. 다른 reference/input으로 확장하려면 해당 source/input contract를 별도의 새 연구 단위에서 명시한다.

Prefix A/B/C는 0부터 첫 birth 직전의 gas-only 비교다. Source가 작동한 이후를 계산하지 않으며, escape/CMB/event ledger를 포함한 restart state가 아니다. 원래 M2 transport checkpoint에 조립해 이어 붙이지 않는다.

## 증거 수준

Byte identity 검사는 과학적 semantic identity와 다르다. RUN16의 Git readback은 새 source/raw evidence 전달을 확인한다. Fresh native build/전체 toolchain 복원, numerical replay, directed-rounding certificate는 각각 별도 단계다. 실제 완료한 단계는 최종 `DELIVERY.json`과 하위 receipt에만 표시한다.
