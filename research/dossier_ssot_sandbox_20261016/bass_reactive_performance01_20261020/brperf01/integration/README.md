# BRPERF01: 온도 계수 재사용의 native H/He/D 통합 검증

**판정: `COMPLETE_VERIFIED_BOUNDED_NATIVE_GAS_CONTROL`.** 고정 체적, 광원 OFF, H/He/D 기체의 원래 midpoint–Strang 및 adaptive CX half-flow에서 direct 계수 재사용과 opt-in compact table을 연결했다. 권장 비교 대상인 8193-node table에서 45개 계획 이력/5040 macrostep을 모두 완료했다. 같은 시간 격자의 원 direct 계산과 비교한 최대 population family-scaled 차이는 `1.8257159e-11`, 최종 온도 상대차는 `2.2294831e-11`이다. 이 수치는 이 문서에 지정한 세 제어 이력의 직접 비교 결과다.

실제 BASS 배경과 photon source/birth/absorption driver를 포함하는 통합 계산은 이 crate의 검증 범위에 포함되지 않는다. `LONGSPAN_SOLUTION`, full-EoR, 전체 계의 보편적 2차 정확도 판정에는 변화가 없다. photon 최적화의 실제 ±shear 검증은 별도 `../photon/` 단위가 소유한다.

## 1. 연결 경로와 소유권

| Backend | 온도 계수 | 기체 업데이트 |
|---|---|---|
| `original_direct` | 원 `igm_rates(T)`와 원 D 내부 평가 | 원 `midpoint_gas::rhs/step_strang` |
| `reused_direct` | 원 `igm_rates(T)`를 EOS 온도에서 한 번 평가해 H/He/D가 공유 | `../native_rates/` receiver; 원 apply/CX/add_budget에 위임 |
| `legacy_65537` | 원 `IgmRateTable`, 65537 nodes | 같은 receiver |
| `compact_pchip` | `../rates/CompactRateTable`, 8193 nodes | 같은 receiver |
| `compact_pchip_simd` | 같은 table의 안전한 `f64x4` evaluation | 같은 receiver |

이 단위는 `FullState`, `NetworkConfig`, `GasRhs` 및 이벤트/에너지 owner를 바꾸지 않는다. receiver 자체의 소스 차분, 온도 bit identity 확인, D의 좁은 collision adapter 및 9개 회귀 검증은 `../native_rates/evidence/ADAPTER_AUDIT.json`과 `VERIFICATION.json`에 있다. 본 단위는 이를 실제 시간 이력에 연결한다. 모든 의존 소스와 실행 바이너리의 SHA-256은 `evidence/FINAL_SOURCE_IDENTITY.json`에 기록했다.

표는 온도만의 함수인 15개 원 계수에 적용한다. 밀도 곱, 전자수, 반응 사건수, 열/결합 에너지, CMB 항, Savin CX, 기하 및 광자의 소유권은 표에 넣지 않는다. 예를 들어 같은 계수 (k(T))를 공유하더라도 실제 사건율 (k(T)n_a n_e)는 각 species의 현재 밀도로 계산한다. HeI metastable excitation의 원 `cm^6/s` 밀도 곱도 receiver에서 원 산술 순서대로 유지한다. 원 source binding과 D의 제조된 H-equality 관계를 그대로 사용한다.

8193-node 선택 및 양수 PCHIP/분기점 direct fallback/serialization 검증은 `../rates/`가 소유한다. 이 단위의 1047-point probe는 원자 단위의 더 넓은 독립 probe와 다른 표본이다. 4097 nodes는 이 단위 표본에서는 `8.84525e-5`였지만 원자 단위의 더 넓은 probe에서 `1e-4` gate를 약간 넘었으므로, 4097 이력 결과는 해상도 비교 증거로만 보존한다.

## 2. 고정한 물리 fixture와 실행 계획

초기 밀도 단위는 `m^-3`이다. `HI=1000`, `HII=900`, `DI=25`, `DII=5`, `He4I=300`, `He4II=100`, `He4III=60`을 사용하고 나머지 6개 isotope population은 0으로 둔다. 초기 광자, 탈출 복사 에너지, CMB reservoir는 0이다. 체적은 고정이며 광원과 photo reaction은 OFF이다. CI, RR, CE, DR, free-free, CMB thermochemistry와 원 CX를 사용한다. CMB bath는 원 회귀 설정 20 K이다.

초기 열 에너지는 원 EOS의 전체 열입자수로 (U_{
m th}=3k_B n_{
m part}T/2)를 만족하도록 구성한다. H binding energy는 13.598434599702 eV, 제조된 D binding energy는 H+0.0037 eV, HeI/HeII는 24.587389011/54.41776 eV이다. 이는 full-EoR 초기조건의 주장이나 새로운 isotope 데이터의 admission이 아니다.

| Case | 초기 T (K) | 구간 (s) | 각 backend의 시간 격자 |
|---|---:|---:|---|
| `COOL_RR_3000` | 3000 | (8\times10^{12}) | 48, 96, 192 |
| `MID_CE_10000` | 10000 | (8\times10^{12}) | 48, 96, 192 |
| `HOT_CI_60000` | 60000 | (2\times10^{11}) | 48, 96, 192 |

각 resolution의 전체 계획은 `3 cases × 3 Nt × 5 backends = 45 histories`이다. CX operator를 변경하지 않고 모든 backend에 동일하게 `rtol=1e-10`, `atol_normalized=1e-13`을 지정한다. 나머지 work controls는 원 default다. 고정 macrostep 제어 연구이므로 원 four-corner controller를 대체하거나 수정하는 경로가 없다.

`science_4097`와 `science_8193`는 각각 45/45 COMPLETE 및 5040 accepted macrostep이다. 18개의 original/reused-direct 사전 baseline 이력도 `baseline_before_compact/`에 보존했다. 최종 판정은 최종 바이너리에서 다시 실행한 두 과학 결과에 근거한다.

## 3. 직접 비교, 보존 및 시간 해상도

`evidence/science_8193/INDEPENDENT_ANALYSIS.json`은 Rust를 호출하지 않는 Python 검산 결과다. CSV의 population으로 전자수/입자수/EOS와 결합 에너지를 별도로 재구성하며, `math.fsum`으로 nuclei/baryon/에너지 합을 계산한다. 모든 numeric field의 유한성도 확인한다.

| 8193 primary 검증 | 결과 |
|---|---:|
| original ↔ reused-direct 전체 이력 bitwise 비교 | 9/9 pairs PASS |
| compact scalar ↔ SIMD 전체 이력 bitwise 비교 | 9/9 pairs PASS |
| 각 point probe의 original ↔ reused-direct RHS field bits | 35598/35598 PASS |
| 각 point probe의 compact scalar ↔ SIMD RHS field bits | 35598/35598 PASS |
| 최대 total-energy drift / 초기 total energy | (1.26338\times10^{-15}) |
| 최대 thermal budget 잔차 / 초기 thermal energy | (1.89644\times10^{-15}) |
| 최대 chemical budget 잔차 / 초기 binding energy | (1.03632\times10^{-15}) |
| 최대 D nuclei 보존 상대 잔차 | (1.65793\times10^{-15}) |
| 음수 population | 0 |
| photon source 및 photo event budget | 정확히 0 |

escape/CMB reservoir의 누적 변화와 각각의 원 budget은 Python에서 동일하게 재구성된다. 이 fixture는 기하를 고정하므로 geometry work와 photon ledger를 동적 검증했다는 주장을 하지 않는다. 작은 보존 잔차는 원 업데이트와 book-keeping의 일관성을 검사하며, rate approximation이나 시간 정확도의 증거로 사용하지 않는다.

같은 Nt에 대한 원 direct와의 차이는 별도 파일 `BACKEND_DIFFERENCES.csv`에 기록했다. Population 차이는 각 원소 family의 초기 총수 H=1900, D=30, He4=460으로 정규화하며 모든 저장 시각과 active species에 대해 최대를 취한다. 다음 값은 세 이력과 세 Nt 전체의 최대값이다.

| Backend | 최대 trajectory population 차이 | 최대 최종 T 상대차 | 최대 최종 thermal 상대차 | 최대 최종 binding 상대차 |
|---|---:|---:|---:|---:|
| reused-direct | 0 | 0 | 0 | 0 |
| legacy 65537 | (4.51464\times10^{-10}) | (2.65214\times10^{-9}) | (2.40819\times10^{-9}) | (5.80926\times10^{-10}) |
| compact 4097 | (5.73367\times10^{-11}) | (3.50902\times10^{-10}) | 원 CSV 참조 | 원 CSV 참조 |
| compact 8193 | (1.82572\times10^{-11}) | (2.22948\times10^{-11}) | (2.06641\times10^{-11}) | (1.52890\times10^{-11}) |

8193의 최종 escaped 및 CMB reservoir 최대 상대차는 각각 `6.3977167e-10`, `6.8946550e-12`다. 전체 계수 표본 오차가 작다는 순서와 세 진화 이력의 누적 오차 순서는 같을 필요가 없다. 계수의 국소 보간 오차, 실제 경로가 지나는 온도와 반응 가중치, 적분 중의 부호 상쇄가 모두 다르므로 여기서는 직접 관찰된 이력의 차이만 보고한다.

원 direct의 (N_t=192) endpoint는 다음과 같다.

| Case | 최종 T (K) | HII (m^-3) | DII (m^-3) | He4III (m^-3) |
|---|---:|---:|---:|---:|
| COOL | 2998.1126437915 | 883.6673233604 | 13.8576467148 | 57.4533082822 |
| MID | 9944.8996250540 | 887.5301318137 | 14.0867024333 | 58.9092101591 |
| HOT | 42301.6443469075 | 1004.8060804798 | 15.9390161095 | 59.9914316240 |

시간 해상도는 table 차이와 별도로 `TIME_GRID_DIFFERENCES.csv`에서 검사한다. 같은 방향의 두 차분이 각각 64 machine-epsilon 상대 문턱보다 클 때만 (p=\log_2|[q_{48}-q_{96}]/[q_{96}-q_{192}]|)를 표시한다.

| 원 direct Case | (T_{96}-T_{192}) (K) | T의 형식적 p | HII의 p | DII의 p |
|---|---:|---:|---:|---:|
| COOL | (2.34477\times10^{-8}) | 2.31781 | 1.92138 | 1.90272 |
| MID | (5.14820\times10^{-6}) | 1.92695 | 1.72264 | 1.75988 |
| HOT | 0.14386610 | 2.01425 | 2.01243 | 2.01250 |

HOT 사례는 이 세 격자에서 약 2차 차분비를 보인다. COOL/MID의 작은 차분은 CX 내부 허용오차 등과 분리한 더 깊은 수렴 분석이 필요하다. 이 결과를 전체 radiation–gas 계의 보편적 2차 정확도로 확대하지 않는다. 특히 HOT의 시간 격자 차이는 table8193의 동일-Nt 온도 차이보다 훨씬 크다.

## 4. 넓은 온도 범위의 native RHS와 15개 채널

Native state가 허용하는 `2.7.next_up() .. 200000.next_down()` K에서 1047개 EOS 온도를 사용했다. 1024개의 이동된 log-grid sample, 양끝점, 원 분기 온도들의 바로 아래/정확한 값/바로 위를 포함한다. 계수 table 자체의 domain `1..1e6 K` 전체에 대한 더 넓은 검증은 rates 단위에 있다.

| Backend | 1047-point 최대 coefficient 상대차 | population RHS group-scaled 최대차 | event RHS group-scaled 최대차 | energy RHS group-scaled 최대차 |
|---|---:|---:|---:|---:|
| reused-direct | 0 | 0 | 0 | 0 |
| legacy65537 | (3.80100\times10^{-7}) | (1.53030\times10^{-7}) | (4.62741\times10^{-8}) | (4.16678\times10^{-8}) |
| compact4097 | (8.84525\times10^{-5}) | (1.14692\times10^{-6}) | (3.17758\times10^{-7}) | (1.79668\times10^{-7}) |
| compact8193 | (1.27357\times10^{-5}) | (1.54788\times10^{-7}) | (3.88014\times10^{-8}) | (1.38694\times10^{-8}) |

RHS group normalization은 같은 온도에서 해당 단위를 가진 원 RHS field들의 최대 절댓값이다. Population, 사건율(부호 있는 CX 및 D electron diagnostic 포함), energy rate는 서로 다른 단위의 그룹이다. 이 검사는 34개 field 전체를 포함한다. 구조적 zero는 그대로 zero이며 비음수 계수가 유지된다.

60000 K에서 원 계수 15개를 하나씩 1% 변화시켜 각 계수가 native RHS에 실제로 연결되어 있음을 확인했다. `CHANNEL_INFLUENCE.csv`의 15/15 채널에서 최소 하나의 field가 변한다. 이는 배선/소유권 영향 검사이고 모든 온도에서 모든 채널이 활성이라는 주장은 아니다. 예를 들어 원 DR 저온 branch는 유지된다.

## 5. native RHS 계측

권장 판정에 사용하는 원시 계측은 **`evidence/native_rhs_abba_final/`**이다. Release 바이너리, 64개 동일 native gas fixture, 매 window 32768 RHS evaluations, backend마다 6개 ABBA/BAAB 쌍, 5개 독립 프로세스를 순차 실행했다. warmup 2개/backend와 A/A controls 3쌍/process를 별도로 보존한다. CX half-flow는 이 RHS microbenchmark의 범위 밖이며 `use_cx=false`, `owner=AtomicRhs`로 고정한다. 모든 mode는 동일한 유효 상태/CI/RR/CE/free-free/CMB 산술을 사용한다.

`std::hint::black_box`로 입력과 전체 RHS 결과를 소비하며, 결과의 비선형 wrapping checksum을 저장한다. 최종 raw data에서 direct/reused-direct checksum은 `4f629510f7b1754e`로 동일하고 table별 checksum은 별도로 비영이다. 타이밍의 통계 단위는 한 process에서 얻은 6 paired speedup의 중앙값이며 아래는 그 5 process 중앙값과 범위다. 독립 CPU 작업을 멈추도록 다른 단위와 시작/종료를 조율했지만 공유 샌드박스의 잡음은 남는다.

| Backend | paired speedup 중앙값 | process 중앙값 범위 | 중앙 trial ns/RHS | table setup 중앙값 | setup 손익분기 RHS 호출 수 |
|---|---:|---:|---:|---:|---:|
| reused-direct | 1.41147× | 1.39723–1.49686× | 695.19 | 0 | 0 |
| legacy65537 | 2.17612× | 2.07671–2.20859× | 449.47 | 134.122 ms | 251809 |
| compact8193 scalar | 2.91818× | 2.69265–3.06154× | 359.18 | 7.739 ms | 11601 |
| compact8193 SIMD | 2.88468× | 2.46764–3.00474× | 402.82 | 같은 table | 11917 |

각 comparison의 baseline window가 다르므로 `전체 ns 중앙값의 비`는 `paired speedup 중앙값`과 같지 않을 수 있다. 손익분기는 관측한 table setup 시간과 각 comparison의 중앙 baseline/trial ns 차이를 사용한 (\lceil t_{\rm setup}/(t_{\rm direct}-t_{\rm trial})\rceil) 추정이다. 표 저장/복원 I/O를 포함하지 않는다. Legacy의 storage reporting은 9,109,624 bytes, compact8193은 4,259,840 bytes로 약 53.24% 작다.

15개 A/A window ratio의 중앙값은 1.04668, 범위는 0.83379–1.15336이다. 따라서 작은 scalar/SIMD 차이에 확정적인 우열을 부여하지 않으며, 측정한 큰 direct 대비 차이와 process 범위를 함께 보고한다. SIMD는 선택 가능한 구현으로 남는다. Reused-direct만 원 direct와 bitwise 같은 정확도 조건이다. 두 table의 근사 오차는 앞 절에서 별도로 정량화했으며 서로 동일한 coefficient 오차를 맞춘 성능 비교가 아니다. 이 계측은 전체 CX/광자/배경 이력의 end-to-end 가속 측정이 아니다.

## 6. 실패 분류와 남은 DAG

`max_rate_calls=1`로 deliberately exhausted CX control을 별도로 실행했다. 5 backend 모두 첫 단계에서 `Cx(WorkLimit)`을 반환하고 accepted macrostep은 0이다. `WORK_LIMIT_CONTROL.csv`는 계획된 45개 과학 이력과 구분한다. 이를 수렴 실패나 물리적 해 부재로 분류하지 않는다.

두 계측 복구 기록도 보존했다. 첫 checksum의 순수 rotate-XOR는 반복 fixture에서 0으로 상쇄되었다. 전체 RHS `black_box`와 과학 결과는 영향을 받지 않았으나 observable checksum 증거를 보강하여 재측정했다. 이어 checksum-only formatting gate 실패 뒤 이전 바이너리를 실행한 shell 연결 실수는 `STALE_LAUNCH_FAILURE.json`에 기록하고 해당 run을 최종 성능 판정에서 제외했다. 마지막 실행은 하나의 checked subprocess chain으로 fmt/strict Clippy/build 완료 후 시작했다. 두 기존 디렉터리는 삭제하지 않았다.

처음 `cargo fmt --all --check`가 원 parent dependency까지 읽어 기존 formatting 차이를 보고한 일도 있었다. 쓰기는 없었고, 이후 own `src/lib.rs`, `src/main.rs` 두 파일에만 scoped rustfmt 검증을 수행했다. 원 owner는 수정하지 않았다.

| DAG 노드 | 상태 | 다음의 직접 의존성 |
|---|---|---|
| Direct bundle native receiver parity | COMPLETE_VERIFIED | 원 owner 불변 확인 |
| Fixed-volume H/He/D table integration | COMPLETE_VERIFIED_BOUNDED | 전체 이력 및 독립 CSV 검산 |
| Native RHS ABBA/setup memory control | COMPLETE_MEASURED_SHARED_SANDBOX | 원시 final 계측과 A/A 범위 |
| BASS + photon + compact rates 연결 | NOT_IMPLEMENTED_IN_THIS_UNIT | source/birth/geometry owner별 연결과 재검증 |
| Full coupled-history performance | NOT_MEASURED | 동일 정확도/허용오차 workload를 고정한 전체 profile |
| 보편적 2차/전체 EoR/양방향 Einstein feedback | HOLD | 기존 연구 DAG의 미완료 항목 |

## 7. 재현 및 산출물

선택한 Rust 1.94.1과 검증된 offline registry를 환경에 지정하고 다음을 실행한다. Runner는 source 파일을 수정하지 않고 지정한 새 output directory만 만든다. `CARGO_TARGET_DIR`을 다른 단위와 분리한다.

```sh
export CARGO_TARGET_DIR="$PWD/target"
python3 RUN_STAGE.py "$PWD/evidence/fresh_science"
python3 RUN_STAGE.py "$PWD/evidence/fresh_bench" --stage bench
```

`RUN_STAGE.py`는 scoped rustfmt, strict Clippy, offline locked release build, 두 resolution의 과학 이력, 독립 Python 검산을 순차 실행한다. Benchmark 재현 시에는 외부 계산과 CPU 경쟁을 조율한다. `--skip-build`는 이미 build identity를 확인한 실행에만 사용한다. 과학 CSV의 정확한 hash는 `evidence/GOLDEN_CSV_SHA256.json`에 있고 construction timing은 비교 대상에서 제외한다. 최종 checksum 수정 뒤 다시 실행한 모든 deterministic 과학 CSV는 수정 전 과학 CSV와 SHA-256까지 동일했다.

이 crate는 standalone numerical harness다. 기존 native receiver의 9개 Rust unit test, rates의 5개 test, 전체 parent suite를 자동으로 새 실행 PASS로 상속하지 않는다. 해당 단위들의 실행 증거와 최종 통합 archive의 fresh-restore suite 결과는 각각의 verification receipt를 참조한다. 본 단위에서 직접 실행한 검증/재현 범위는 `evidence/VERIFICATION.json`에 있다. 게시/클라우드 backup/전체 fresh restore는 root 단위가 최종 source tree에 대해 수행한다.
