# RUN19 Unit B — 원래 gas RHS에 opt-in cubic T-table 연결

## 완료 범위

기존 Unit A의 `PreparedIgmRates` 재사용 경로에 32,769-node cubic 계수 평가기를 실제 연결했다. 같은 prepared bundle을 H/He와 D가 공유한다. `--rates cubic`을 선택하면 source-off RHS가 이 평가기를 사용하며, 기존 기본값은 Direct다. 서버의 `STEP` 경로는 기존 Direct owner를 유지한다. 실제 검증은 **새 native integration 4개 + 관련 서버 2개 테스트 PASS**, 보존 입력 9,216개의 RHS 비교, 캐시 저장/재사용/오류 제어, 그리고 한 번의 짧은 동일 실행 파일 성능 비교까지 수행했다. Native IVP와 RUN13 이력 계산은 0회다.

원래 기준은 `99e07bcff126d0a73a03bafc4b71e0b735dbcc3e`의 RUN13 native source다. 원래 91개 파일의 SHA-256와 Git blob을 다시 읽어 확인했으며 수정·추가 파일은 0개였다. 개발 fork는 Unit A의 94개 파일에서 99개 파일이 됐다. Unit A 대비 변경 6개, 추가 5개이며 삭제는 없다. 원본 보존 검사는 [ORIGINAL_SOURCE_IMMUTABLE_CHECK.json](ORIGINAL_SOURCE_IMMUTABLE_CHECK.json), 새 소스 전체와 변경 전후 identity는 [SOURCE_AFTER_MANIFEST.json](SOURCE_AFTER_MANIFEST.json), 실제 diff는 [NATIVE_DIFF_FROM_UNIT_A.patch](NATIVE_DIFF_FROM_UNIT_A.patch)에 있다.

## 구현과 적용 조건

`rate_cubic`은 root가 작성한 generic crate의 여섯 파일을 정확히 복사했다. `Cargo.toml`의 dev-dependency 경로만 `../../run13/recovered/code/rei_bass_coupled`로 바꾸었다. Generic 구현의 SHA-256는 `7c45be5d93778d33d6c300b063b08efc4649c0106f26ac22720220328be4988f`이며, 캐시 MAGIC이나 generic kernel을 이 단위에서 수정하지 않았다. 경로 차이는 [CUBIC_MANIFEST_PATH_ONLY.patch](CUBIC_MANIFEST_PATH_ONLY.patch)에 보존했다.

새 native `cubic_igm.rs`는 다음 계약을 구현한다.

- T-domain은 1–1,000,000 K이며 서버의 기본 캐시는 정확히 32,769 nodes다. 이 범위를 벗어나거나 source branch, 불확실한 zero/subnormal/부호 조건에 걸리면 원래 Direct 계수 평가로 돌아간다.
- Log T의 네 source nodes로 계수값을 보간한다. 보간계수의 양성을 가정하지 않으며, 원래 branch/floor/diagnostic 의미를 보존하는 guard가 있다. CI floor는 원래 정확한 값으로 재설정한다.
- 15개 물리 계수와 1개 zero padding을 node-major16으로 저장한다. T-only 테이블에는 밀도, 광자 source, opacity 또는 진행 중인 gas state가 들어가지 않는다.
- `IgmRateBackend::Cubic(Arc<...>)`가 기존 prepared API, exact-T workspace 및 scalar/typed batch 경로를 사용한다. 새 명시적 SIMD intrinsic이나 fast-math를 도입하지 않았다.
- 캐시 source ID에는 실제 `igm_rates.rs`, `rate_table.rs`, generic 구현, wrapper 자체의 컴파일 입력 bytes와 domain/algorithm policy가 길이 prefix와 함께 들어간다. 현재 bytes로 독립 재구성한 ID가 실행 바이너리의 META와 일치했다.

실제 source ID는 다음과 같다.

```text
53f101a30c0d6fdae246eb6ca545660e8bab5aaf22e34787c6ba15fd1ec8fcc4
```

서버는 `--table-cache FILE`을 cubic에서만 받는다. 파일이 없으면 build 후 create-only 저장을 수행하며, 존재하면 digest/source/domain/node 수를 검사해 읽는다. META에는 RHS/STEP evaluator, node 수, source ID, cache action, 실제 캐시 SHA가 기록된다. 이 ID와 SHA는 무결성·호환성 검사이며 producer authentication을 뜻하지 않는다.

## 실제 검증 결과

[native_tests01](native_tests01/COMMAND.json)의 네 새 테스트는 prepared H/He/D binding 및 ledger, floor·branch·domain, cache roundtrip·잘못된 source/node 수 거부, 그리고 97개 state × 5개 mask에서 scalar와 workers 1/2/4 batch의 비트 일치를 다룬다. 관련 서버 두 테스트도 함께 PASS했다. 과거 native 전체 suite와 root 소유 generic 5-test suite는 여기서 재실행하지 않았다.

보존한 Unit A 입력·출력의 SHA-256는 각각 다음과 같다.

```text
IPC_INPUTS.json.gz   3fca0213b9de609faa489878d2c735eb2d815b6ae8d72d44b335763320141826
IPC_REPLIES.json.gz  0c7c6bd48499c56ff89a0ea7612a7f9396c97be65adbd0ea7dd261d40f2f4b6c
```

실제 비교는 약 9,500–14,500 K의 제조된 9,216개 보존 입력에서 Direct/loglinear/cubic 세 경로를 계산했다. 총 gas point 평가 27,648회와 conditioning 분모를 위한 direct D point 평가 9,216회다. 이전 Direct 출력 258,048개와 loglinear 출력 258,048개는 각각 전부 f64 비트가 일치했다. 전체 IPC 성능 실험을 반복한 것은 아니다. 원시 각 행은 [GAS_POINT_ROWS.jsonl.gz](point_compare01/GAS_POINT_ROWS.jsonl.gz), 통계와 최대 위치는 [GAS_COMPARISON.json](point_compare01/GAS_COMPARISON.json)에 있다.

| 관측량 | loglinear 최대 상대차 | cubic 최대 상대차 | cubic 최대 절대차 |
|---|---:|---:|---:|
| H neutral/ion net RHS | 4.54481060699e-5 | 3.82773009536e-9 | 2.91109395549e-27 m^-3 s^-1 |
| D neutral/ion net RHS | 5.00530392308e-11 | 6.51354300809e-15 | 7.39557098645e-32 m^-3 s^-1 |
| He I net RHS | 1.28026163686e-11 | 1.15829771659e-14 | 2.95822839458e-31 m^-3 s^-1 |
| He II net RHS | 3.91976673024e-10 | 1.98518572240e-14 | 2.65007960348e-31 m^-3 s^-1 |
| He III net RHS | 1.26798423297e-10 | 2.17263787920e-15 | 1.04770588975e-31 m^-3 s^-1 |
| Heat RHS | 4.73089455397e-8 | 3.76923980387e-12 | 8.03119182366e-44 J m^-3 s^-1 |
| Chemical energy RHS | 7.17136292733e-5 | 1.39980816497e-8 | 6.34371081987e-45 J m^-3 s^-1 |

각 열의 최대값은 서로 다른 입력에서 발생할 수 있다. Net RHS는 서로 큰 반응항을 상쇄하므로 상대차만으로 평가하지 않았다. 각 성분에 대해 원래 f64 elementary flux의 절대값 합을 구했으며, H net의 최대 cancellation condition `sum_abs_flux/abs(net)`은 **17,703.8653**, chemical net은 **3,887.6648**였다. Cubic H net의 `abs(error)/sum_abs_flux` 최대값은 **1.29067574356e-12**였다. 이 값들은 보존된 유한 입력의 conditioning 진단이며 연속 상태 영역의 상한은 아니다.

양의 CI/RR 등의 event channel이 음수가 되지 않음을 검사했다. Signed energy ledger의 최대 상대 scale residual은 Direct **2.56517e-16**, loglinear **3.02123e-16**, cubic **3.59149e-16**이었다. Ledger의 작은 잔차는 spectral/trajectory 수렴 인증이 아니다.

## 실제 캐시 제어

네 개의 같은 보존 입력을 사용해 cold build/save와 warm load 각각 RHS를 평가했다. 총 gas point 평가 8회이며 응답 bytes가 일치했다. Warm load는 캐시 bytes를 바꾸지 않았다.

| 항목 | 실제 값 |
|---|---|
| 저장 파일 크기 | 4,358,393 bytes |
| 캐시 SHA-256 | `dcfa521f60165632e6fa1c0d10473b194c8aab73844ee0a44ed2454e18f7a23b` |
| Cold process + build/save + 4 RHS | 0.040972822 s |
| Warm process + load + 4 RHS | 0.020530472 s |
| 잘못된 source, 재계산한 valid digest | exit 64, `CUBIC_CACHE_IDENTITY`, RHS 출력 0개 |

이 시간은 각각 한 번의 기능 제어 측정이다. 반복 분포를 측정한 cache benchmark로 해석하지 않는다. [CACHE_PROBE.json](cache_probe01/CACHE_PROBE.json)과 성공 캐시·의도적으로 잘못된 캐시 모두 보존했다.

## 같은 실행 파일의 짧은 core 성능 비교

N=4,096, 각 row당 8,192 RHS × 5회, 두 온도 패턴과 16개 mode로 총 32 rows를 한 번 실행했다. 총 wall time은 **0.779697731 s**였다. 각 row의 사전 warmup은 4,096회다. 전체 timed RHS 1,310,720회와 untimed warmup 131,072회를 구분해 기록했다.

아래 값은 ns/RHS의 중앙값이며 대괄호는 실제 5회 최소–최대다. 고정된 CPU affinity 0–3, 같은 compiled binary와 같은 입력·worker 수를 사용했다. Scoped thread 생성/join은 batch 시간에 포함된다.

| 경로 | 같은 T | 변하는 T |
|---|---:|---:|
| 원래 Direct assembly | 1,118.03 [1,064.67–1,255.04] | 1,046.85 [1,008.20–1,078.54] |
| Shared Direct | 737.04 [667.56–771.17] | 669.45 [644.03–713.15] |
| Shared loglinear | 437.37 [393.08–447.27] | 440.31 [399.61–526.31] |
| Shared cubic | 338.65 [331.55–344.90] | 396.29 [378.60–457.25] |
| Cached Direct | 286.69 [259.00–288.58] | 787.31 [737.63–1,039.11] |
| Cached cubic | 280.12 [257.90–296.81] | 439.97 [420.34–526.76] |
| Direct workers=4 | 171.01 [112.61–194.60] | 308.61 [274.76–346.99] |
| loglinear workers=4 | 153.67 [146.94–162.44] | 263.76 [216.11–571.51] |
| cubic workers=4 | 158.07 [141.42–191.59] | 173.73 [167.55–184.77] |

같은 T에서는 prepared cache hit가 계수 보간의 중요도를 줄인다. 변하는 T에서 cubic shared와 four-worker 결과는 이 측정에서 개선됐지만, cubic batch1은 843.63 [477.22–1,000.70] ns/RHS, batch2는 440.25 [277.61–458.49] ns/RHS로 편차가 컸다. 이 불리한 행도 그대로 보존했다. 공유 호스트, 고정 mode 순서, 주파수 lock 부재를 포함한 한 번의 bounded 측정이므로 보편적 속도 향상이나 전체 궤적 속도를 추론하지 않는다. 실제 모든 rows는 [CORE_BENCH_SUMMARY.json](CORE_BENCH_SUMMARY.json), 원시 repeats는 [core_measure01/stdout.txt](core_measure01/stdout.txt)에 있다.

이 실행의 table 본체는 loglinear **9,109,624 bytes**, cubic **4,358,273 bytes**였다. 최초 생성 시간은 각각 **0.122932483 s**, **0.015160895 s**이며 steady RHS 타이머에서 분리했다. 저장 캐시는 header/digest 때문에 본체보다 120 bytes 크다.

## 재현 및 남은 범위

[REPRODUCE_COMMANDS.json](REPRODUCE_COMMANDS.json)은 실제 producer argv, 환경, 각 명령의 log SHA와 새 output/target을 지정하는 portable argv를 담는다. Rust 1.94.1, empty `RUSTFLAGS`, 원래 source의 canonical 상대 경로 및 pinned Cargo.lock dependency cache가 필요하다. Offline build 성공은 이 실행의 explicit Cargo cache에서 확인한 사실이다. 새 환경의 dependency cache가 비어 있을 때도 이미 offline 재현된 것으로 표시하지 않는다.

실제 세 바이너리는 `/tmp/rei_run19_runtime/unit_b_bin/`에 원본 bytes와 0755 mode로 별도 보존했으며 [BINARY_IDENTITIES.json](BINARY_IDENTITIES.json)에 SHA가 있다. 과거 Unit A 바이너리와 snapshot은 유지했다. Git commit, 최종 ZIP SHA, Drive/Dropbox 단계는 root의 별도 delivery 기록이 담당한다.

확립 범위는 변경된 API/guards/cache의 `IMPLEMENTATION_VERIFIED` 및 유한 RHS·conditioning·성능의 `NUMERICALLY_CHECKED`다. Root 소유의 더 넓은 계수 scan/이상적 보간식 증명은 별도 근거이며 여기서 실행한 PASS로 합치지 않는다. Table의 전체 f64 오차 enclosure, Jacobian/residual tube, gas/opacity feedback trajectory 제어 및 원래 spectral/angle/birth-time/DAG 의무는 계속 별도 미완료 노드다.
