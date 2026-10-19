# Workspace 소실 후 실제 Rust 및 gas 재빌드

2026-10-19 새로 보이는 실행환경에는 rustc/cargo가 없었다. 공식 Rust 1.94.1 Linux x86_64 구성요소만 다운로드하여 SHA-256 및 tar safety를 확인하고 `/tmp`의 새 prefix에 설치했다. 시스템 설정과 사용자 shell 설정을 수정하지 않았으며 installer에는 `--disable-ldconfig`를 사용했다.

## 공식 다운로드

| Component | Bytes | SHA-256 |
|---|---:|---|
| rustc | 78,645,148 | `0a6b16ca476461c6238f48efcb74a7aa08a3983e61adf587f208ba48504d87e1` |
| cargo | 10,972,128 | `03595624775204f80ff3a67986f69c8918e4cd311877ced635108888013a1e39` |
| rust-std | 29,846,424 | `74109ee2c19098f1d7122087dd338a8f643203b3ce678c9d58169db733e17a03` |

각 URL은 `https://static.rust-lang.org/dist/<component>-1.94.1-x86_64-unknown-linux-gnu.tar.xz`이며 대응 `.sha256`도 실제 다운로드했다. 총 download는 119,463,700 bytes, 전체 압축 해제 file bytes는 595,819,178이다. 모든 archive 항목의 경로·링크·type·size·mode를 점검한 뒤 Python tarfile의 data filter로 추출했다. PGP signature 검증은 수행하지 않았다.

재현 recipe는 `download_official_rust.py`, 설치 및 원본 gas build recipe는 `install_and_rebuild_gas.py`다. 작은 receipt는 `toolchain/OFFICIAL_COMPONENTS_RECEIPT.json`, 상세 설치·버전·build log와 prefix file manifest는 `postloss_gas_build/`에 있다. Toolchain prefix는 이번 실제 실행에서 `/tmp/rei_run15_salvage/recovery/toolchain/prefix`였다.

## 원본 실행 파일의 byte identity

원본 Git checkout `3dcb5f7aed8d33ff64f7952e9465f4239a216c89`의 RUN13 native crate를 다음 설정으로 실제 재빌드했다.

```text
cargo build --release --offline --locked --example gas_rhs_server --jobs 2
```

Source 밖의 새 target/cache와 official toolchain을 사용했다. Rustc full commit은 `e408947bfd200af42db322daf0fadfe7e26d3bd1`, Cargo full commit은 `29ea6fb6a5db279426f4cc4e17aa385f05a0cfbc`로 확인했다.

결과:

```text
gas_rhs_server
bytes = 571904
sha256 = 3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b
historical_byte_identity_match = true
```

실제 build는 약 3.88초였다. 원본 code 91개의 전체 inventory는 gas와 신규 quadrature build 전후 동일했다. Native IVP, gas binary 실행 probe 및 cargo test는 이 재빌드 작업에서 모두 0회다. 이전 160 native tests 또는 9 quadrature tests를 새 PASS로 재분류하지 않는다.

`postloss_gas_build/ORIGINAL_GAS_REBUILD_RECEIPT.json`이 실제 명령·환경·결과의 SSOT다. 원래 네 saved endpoint의 84 observable 재구성은 독립 에이전트가 `postloss_endpoint_reconstruction/POST_LOSS_SAVED_ENDPOINT_84_RECEIPT.json`에 별도 실제 receipt로 남겼다.

## 백업 범위

`toolchain/downloads`, `toolchain/extracted`, `toolchain/prefix`, 각 `target` 및 `cargo_home`은 큰 runtime artifacts다. Source/evidence archive는 작은 recipe, 공식 URL·체크섬, component receipt, installed-file manifest와 실행 로그를 포함하고, 이 큰 directory는 명시적으로 제외할 수 있다. 원래 historical archive를 덮어쓰지 않는다.

새 compile 가능한 quadrature source와 세 bounded CLI controls는 sibling `../postloss_native/`에 있으며, 소실 전 전체 `lib.rs`의 byte 복원과 구분한 새 provenance를 갖는다. 그 source template은 canonical Git 상대경로 또는 explicit source-root materialization을 지원한다.
