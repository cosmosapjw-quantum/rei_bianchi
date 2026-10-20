# BRPERF01 native table 이력: 최종 ZIP 복원 gate

**판정: PASS — `FRESH_SOURCE_ZIP_NATIVE_TABLE_TRAJECTORY_RESTORE`.**

이 추가 gate는 integration, native_rates, rates, 원 parent crate의 고정 소스 ZIP을 실제로 새 디렉터리에 풀어 실행했다. 이전 build target이나 이미 만들어진 과학 CSV를 복원 실행 입력으로 사용하지 않았다. 원래 integration receipt의 fresh-restore `PENDING` 표기는 이 디렉터리의 `VERIFICATION.json`으로 해소된다. 이전 receipt와 원 source 파일은 수정하지 않았다.

## 실제 복원원

| 항목 | Identity |
|---|---|
| 파일 | `BRPERF01_NATIVE_INTEGRATION_SOURCE_RESTORE.zip` |
| SHA-256 | `f9113a1d132aa4c8c59e61dbeca355857e0ee555dea329aa798fd5833d599228` |
| 크기 | 360688 bytes |
| ZIP entries | 127 |
| Hash 검증 payload | 126개 source/contract 파일 |
| 추가 entry | `SOURCE_MANIFEST.json` |
| Manifest SHA-256 | `cc6a085d818023a79f043da50cd8000e2b8e34aba42fffd880a8b6d289af0979` |

ZIP에는 네 crate의 source directories, Cargo.toml/lock, 재현·분석 script, golden CSV hash 및 source contract를 담았다. 이전 target, runtime, vendor registry, 과학/타이밍 실행 산출물, 이 ZIP 자신은 포함하지 않는다. Manifest가 나타내는 126개 payload는 압축을 푼 직후와 모든 build/검증을 마친 뒤 각각 SHA-256·크기 일치를 확인했다. 원본 경로의 같은 126개 파일도 마지막에 모두 hash가 유지됐다. ZIP CRC 및 최종 SHA-256 readback도 통과했다.

## 새로 만든 환경과 재사용한 환경

`restore_tree/`는 ZIP에서 새로 추출했다. `empty_target/`은 첫 build 전에 존재하지 않던 새 빈 디렉터리로 생성하고 비어 있음을 확인했다. Cargo home도 `cargo_home/`으로 새로 생성하여 원 Cargo cache를 물려받지 않았다.

**Compiler와 offline registry는 재사용했다.** Rust 1.94.1 설치 prefix와 검증된 99-package vendor registry를 읽어 사용했으며, 새 Cargo home의 source replacement 설정이 이 registry를 가리킨다. Compiler의 재설치나 registry의 재다운로드를 수행했다는 주장은 없다. 정확한 executable versions, 경로, Cargo configuration hash, 기존 runtime/vendor verification receipt hash는 `RUNTIME_REUSE.json`에 있다.

## 실행한 gate

복원본 `integration/RUN_STAGE.py`의 science stage를 실행하여 scoped rustfmt, strict Clippy, offline locked release build, 4097/8193 두 해상도의 과학 실행과 독립 Python 분석을 완료했다. 이어 복원본 `VERIFY_RESTORE.py`와 native adapter tests를 실행했다.

| 검증 | 최종 결과 |
|---|---|
| 복원한 source payload hash | 126/126 PASS |
| Scoped rustfmt | PASS |
| Strict Clippy, all integration targets | PASS |
| Offline locked release build, 최초 빈 target | PASS |
| 4097-node native history | 45/45 COMPLETE, 5040 macrostep |
| 8193-node native history | 45/45 COMPLETE, 5040 macrostep |
| 두 해상도의 독립 Python EOS/ledger/유한성/parity 분석 | PASS |
| Deterministic numerical CSV byte/hash parity | 16/16 PASS |
| Fresh native adapter tests | 9 passed, 0 failed |
| 원본 source 및 복원 source 실행 후 hash 불변 | PASS |
| Benchmark 재실행 | 0회 |

9개 adapter test는 direct RHS/step/Strang bitwise parity, source/photo/ownership/temperature refusal, exact prepared-temperature binding, invalid coefficients, underflow rejection, evaluator 호출 수와 `Cx(WorkLimit)`의 transactional 거부를 포함한다. 실행 원문은 `FRESH_NATIVE_ADAPTER_TESTS.log`에 있다.

이전 final binary의 SHA-256은 `957eb548de494c4f99eb6166846a338426d895f476e33297c2551599f5b81d81`, 다른 복원 경로에서 새로 build한 binary의 SHA-256은 `f6f3d2e234a14a9957dceb1e7fbc6c028569cbbb4037c3ce37223be777ca4718`이다. Binary bytes의 동일성을 admission 조건으로 사용하지 않았다. 정확한 복원 source와 compiler를 고정하고, 실제 수치 산출물 16개가 원 golden CSV와 byte 단위로 일치하는 것을 확인했다.

## 증거와 범위

`VERIFICATION.json`은 실제 ZIP identity, 각 명령/종료 코드, 두 과학 분석 결과, 복원 소스 및 원본 소스 불변 검사, binary hash를 함께 담는다. `COMMANDS.json`, `science_output/COMMANDS.json`과 실행 log들이 세부 증거다. `FRESH_CSV_BYTE_PARITY.log`는 16개 CSV의 expected/actual SHA를 모두 보존한다.

이 gate는 native table trajectory를 새 소스 복원본에서 재현할 수 있는지 확인하는 마지막 추가 검증이다. 기존 성능 계측을 반복하지 않았으며 BASS–photon 전체 coupling, full-EoR, 일반적인 시간 수렴 또는 provider backup ACK를 새로 주장하지 않는다. GitHub·Drive·Dropbox 전체 백업은 root 단위의 최종 게시 결과에 연결한다.

이 단위를 전체 archive에 넣을 때 `empty_target/` 및 `cargo_home/`은 재생 가능한 실행 cache로 제외할 수 있다. 실제 복원원 ZIP, manifest, verification receipts, scripts, 로그 및 수치 output은 보존한다.
