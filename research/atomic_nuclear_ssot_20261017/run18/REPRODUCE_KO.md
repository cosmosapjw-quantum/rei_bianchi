# RUN18 명령·실행 경계와 이동 가능한 복원

이 문서는 실제 수행된 실행의 provenance와 향후 재현 명령을 구별한다. 저장된 RUN13 m2 및 RUN17 control은 재적분하지 않는다. ZIP 검증과 source readback은 과학 계산이 아니다.

## 1. 실제 생산자 명령

정확 Python reference는 아래 명령으로 한 번 실행했다. 원본 source와 출력 receipt의 해시가 theory manifest에 있다.

```bash
python -B /tmp/rei_run18_work/theory/exact_c0_depth_reference.py \
  --control-result /tmp/rei_run17_work/native/control_B_execution01/FIRST_BIRTH_CONTROL.json \
  --domain-certificate /tmp/rei_run17_work/residual/domain_execution01/RECONSTRUCTION_DOMAIN_CERTIFICATE.json \
  --output-dir /tmp/rei_run18_work/theory/execution01
```

Rust/Cargo는 `/tmp/rei_run15_salvage/recovery/toolchain/prefix/bin`의 실제 1.94.1 실행 파일을 사용했다. `PATH`, `RUSTC`, `CARGO_HOME`, `CARGO_TARGET_DIR`, `CARGO_BUILD_JOBS=2`의 정확한 값 및 각 stdout/stderr는 `runtime/build_execution01/BUILD_RECEIPT.json`에 있다. `cargo generate-lockfile --offline`, `cargo test --offline --locked --lib`, `cargo build --offline --locked --release --bin rei_exact_dense`가 실제 exit 0이었다. Tests는 4개 통과했다.

그 release binary를 다음 명령으로 실제 검증했다.

```bash
python -B /tmp/rei_run18_work/runtime/validate_exact_adapter.py \
  --fixture /tmp/rei_run18_work/theory/execution01/DENSE_B_F64_BITS.json \
  --reference /tmp/rei_run18_work/theory/execution01/EXACT_C0_DEPTH_REFERENCE.json \
  --binary /tmp/rei_run18_work/runtime/target/release/rei_exact_dense \
  --output-dir /tmp/rei_run18_work/runtime/adapter_execution01
```

정확한 원시 TSV/JSONL, 5,911-case 결과, 시간과 입력·binary identity는 `runtime/adapter_execution01/RUST_EXACT_VIGILODE_RESULT.json`을 따른다. native gas RHS 호출이나 IVP solve를 이 명령에 숨겨 넣지 않았다.

## 2. 새 위치에서 reference만 재생성할 때

실제로 복원된 RUN17과 RUN18 디렉터리를 지정한다. 아래 명령은 **향후 재현용**이며 이번 중단 복구에서 다시 실행하지 않았다. 참조 JSON의 원래 절대 NPZ 경로는 basename을 취하여 같은 control 디렉터리의 NPZ로 해석하고 기록된 SHA를 대조한다. Domain certificate의 입력 identity도 확인한다.

```bash
rei_run17_root=/absolute/path/to/run17
rei_run18_root=/absolute/path/to/run18
rei_new_reference=/absolute/path/to/new-reference-output

python -B "$rei_run18_root/theory/exact_c0_depth_reference.py" \
  --control-result "$rei_run17_root/native/control_B_execution01/FIRST_BIRTH_CONTROL.json" \
  --domain-certificate "$rei_run17_root/residual/domain_execution01/RECONSTRUCTION_DOMAIN_CERTIFICATE.json" \
  --output-dir "$rei_new_reference"
```

이 경로에는 Python/NumPy가 필요하다. 저장 binary64 계수를 exact Fraction으로 다루며 원래 coupled ODE를 다시 풀지 않는다. 새 출력의 시간·경로 metadata는 달라질 수 있으므로 기존 JSON 전체 SHA가 같을 것으로 가정하지 않는다. 정확한 rational 수치와 입력 source identity가 재현 기준이다.

## 3. 새 위치에서 Rust adapter만 오프라인 재현할 때

완료된 독립 reference와 hex fixture가 있으므로 RUN17 원본 NPZ 없이도 Rust 비교 단위를 재현할 수 있다. 전체 명령은 `runtime/REPRODUCE.md`에 있다. 순서는 다음과 같다.

1. `restore_vendor_from_archives.py`에 `--runtime-root`와 존재하지 않는 `--workspace-dir`을 지정한다. 보존된 공식 5개 crate archive에서 130개 source 파일과 5개 checksum map을 복원한다. 이 helper는 Cargo나 build script를 실행하지 않는다.
2. 실제 Rust 1.94.1 prefix와 helper가 새로 쓴 vendor config를 지정해 offline locked test와 release build를 실행한다.
3. 새 binary를 보존 fixture/reference와 `validate_exact_adapter.py`로 비교한다. 새 output 디렉터리를 쓴다.

원래 `runtime/vendor_config.toml`은 생산자 경로를 기록한 provenance다. 다른 위치에서는 새 helper config를 사용한다. Inari는 조사 자료이며 dependency graph에 넣지 않는다. Official dependency archives와 Cargo.lock checksum을 보존하지만 별도 배포 서명 검증이나 모든 호스트에서 동일한 binary hash를 보장하지 않는다. 새 binary가 달라도 원시 결과를 보존하고 exact rational 결과 및 inclusion checks로 의미상 재현을 판단한다.

이번 실제 복원 검사는 오프라인 vendor helper를 새 디렉터리에 실행해 source/checksum byte가 같음을 확인한 범위다. 그 뒤 Cargo를 다시 실행하지 않았다. `runtime/offline_restore_execution01/EXECUTION_RECEIPT.json`과 `OFFLINE_VENDOR_RESTORE.json`을 읽는다.

## 4. Source freeze·Git·ZIP

`SCIENCE_MANIFEST.json`은 `rei.run18.complete-science-manifest.v1` schema로 모든 payload의 path/bytes/SHA-256/Git blob/mode를 고정하고 자기 파일은 제외한다. `packaging/COMMANDS_KO.md`의 create 명령에 실제 science commit/tree와 단일 immediate parent를 넣는다. Helper는 local Git object와 RUN18 경로·blob·mode를 실제 대조한 후 ZIP을 만든다. 원격 fetch나 native 실행을 자동으로 수행하지 않는다.

`packaging/verify_archive.py`는 전체 ZIP CRC, manifest, 안전한 상대 경로, regular 0644/0755 mode, 100 MiB 상한을 확인한다. `--restore-to`는 새 디렉터리만 허용하고 실제 bytes/mode를 대조한다. ZIP 자체의 SHA, 생성 환경·시간·명령, remote upload/readback은 외부 delivery record에 둔다.

RUN18 ZIP에는 source·결과·adapter binary·공식 crate archive가 포함된다. 원래 RUN17 ZIP과 gas executable은 새로운 중복 payload로 추가하지 않고 기록된 baseline identity에 연결한다. 이식 가능한 Rust toolchain 전체와 모든 역사적 Git object를 제공하는 archive라고 선언하지 않는다.

## 5. 남은 엄밀성 조건

Exact polynomial checks가 whole-time native RHS enclosure를 제공하지는 않는다. True-IVP error를 얻으려면 admissible tube, 원래 physical owner의 interval rate extension, 동일한 좌표/scaling의 Jacobian 및 logarithmic norm, prefix 초기 오차, event/source forcing을 함께 포함해야 한다. 실제 구현과 테스트 결과 없이 native continuum bound 또는 uniform m4 완료를 선언하지 않는다.
