# RT-C8: Grackle 3.4.1 반응률 테이블 정확도와 생성비용 포함 성능 실측

날짜: 2026-10-17 KST. **원래 `rei_bianchi` native production 소스는 수정하지 않음.** 코드·입력 귀속은 `contracts/C8_RESULTS.json` 참조.

## 재사용 근거 및 발견

기존 DAG `RT-R9_R10`과 `RT-C1_C7`은 이미 완료되었음. 실제 Google Drive의 C07 아카이브에서 R1–R10/C1–C7 checkpoint와 65,537-node Rust 구현을 복원했으며, `igm_rates.rs`, `rate_table.rs`, `igm_thermal.rs`의 실제 Git blob SHA가 PR #150과 일치함. focused archive는 `src/joint_affine.rs` 누락으로 처음 컴파일 실패. Dropbox 원본을 가져와 PR #150 SHA `05c6fe32890eb335a3987082a134ac2c7fcd6feb`와 정확히 맞춘 후 compile 성공. 이는 빌드/패키징 오류의 수리이지 원래 물리 모델 수정이 아님.

## R5/R9: 수학적 계산 계약

각 양의 채널 계수를 **고정된 공급자 단위**로 수치화하고 `x=ln(T/K)`, `g_j(x)=ln(k_j(T)/u_j)`로 표기한다. `u_j`는 해당 채널의 고정된 차원기준계수이며 저장 코드가 이미 선택한 source 단위에 대응한다. 로그 온도 등간격 표에서 양의 normal 구간은

`k_tab(T)=u_j exp((1-theta)*g_j(x_i)+theta*g_j(x_(i+1)))`, `theta=(x-x_i)/h`.

그 채널이 `g_j∈C²`이고 한 셀의 연속 곡률 `|g_j''|<=M_j`이면 Lagrange 잔차에 의해

`|g_j-Lg_j|<=M_j*h²/8`, `|k_tab/k_dir-1|<=exp(M_j*h²/8)-1`.

`h=ln(10^6)/65536 = 2.1080796139471853e-04`, `h²/8=5.5549995734246422e-09`. 해당 공급자의 허용 상대오차 `1e-5`를 충분조건으로 보장하려면 **각 매끈한 셀마다** `M_j <= 1800.1711554`이어야 한다. 표본 최댓값만으로 이 곡률 조건을 인증할 수 없음. 실제 source 분기·구조적 영점·CI floor·CE cap·subnormal 신원은 direct fallback과 별도 마스크가 필요함. Wolfram `g=a x²` 제조해에서 차이는 `a*x*(x-h)`, 최댓값 `a h²/4`로 일치한다. 전 구간의 미분가능성을 주장하지 않음.

## C8 실제 소스-동일 검증

- Rust 버전: `rustc 1.94.1 (e408947bf 2026-03-25)`.
- 입력 archive: `60d05e181aa74f5da81be1e30cdf8f3edbe2cccc52044753e0992483a4c41cf9` SHA-256; ZIP CRC PASS.
- 15개 저장 채널 + DR 냉각 등 종속 출력. 영역 `1 <= T/K <= 1e6`. 대상 rate 함수 `Grackle af7939494ce65007887ada7b98d1813df6843346`의 기존 Rust 포트를 사용.
- 랜덤·순서 온도와 분기 양옆의 총 **20,510개 온도**를 실제 검사. 15개 개별 상대오차의 최대 `3.8172670147e-07` (채널 `9`, T=`6895.691312` K)로 원래 제한 `1e-5` 충족.
- 구조적 정확 0 표본 수 13,627, 마스크 검사 20,510; 누적 masking 오류 관측 0. bounded invalid 입력은 source validation으로 거부됨.
- 테이블 65,537 노드, 차단 셀 8개, 힙 payload 9,109,624 B (8.688 MiB). 실제 빌드 `~0.1191`초 (C8 accuracy run). 이 값은 run-specific이며 universal estimate가 아님.
- C8 코드 새 Rust 테스트 2/2 PASS, `rustfmt --check` PASS, isolate된 C8 코드 `clippy -D warnings` PASS.

## 실측 성능: table 초기화비용은 무료가 아니다

모두 Rust `--release --offline --locked`, 32,768 독립 온도, 3회 wall 실행의 median. 기존 direct와 동등한 입력 및 허용 상대오차를 사용. `n=4096` 세트와 분기 검사는 결과 JSON에 수록.

| 분포 | Direct (ms) | Scalar 배율 | SoA 배율 | 4 worker 배율 | 초기화 포함 4 worker 손익분기 |
|---|---:|---:|---:|---:|---:|
| ordered_logT | 12.380 | 3.437× | 2.767× | 5.303× | 340483 queries |
| random_logT | 12.107 | 0.842× | 1.005× | 2.505× | 470201 queries |

손익분기 수 N*는 B/(c_direct-c_table), 차이가 양수일 때만 존재. 단위는 동일한 평가 쿼리 횟수이며, table을 여러 실험·worker가 **정말로 공유한다**는 가정이 필요하다. Random scalar가 direct보다 느린 경우 손익분기 없음. 이 결과는 CPU cache/배치 분포와 3회 median에 민감하고 생산 이력의 throughput을 보증하지 않음.

기존 C6 point RHS benchmark도 **동일 환경에서 다시 1회 재생**: 1024개의 gas point 에 대해 이미 적용된 PreparedDirect vs Table point 시간은 크게 다르지 않음. 해당 자료는 새 C8의 전체 solver 벤치마크가 아니며 기존 benchmark가 잘못된 고정 `compiler=rustc1.85.1` 메타데이터를 출력한다. 실제 컴파일러는 상술한 Rust 1.94.1임.

## 주의·FAIL 기록

최초 focused archive에는 `joint_affine.rs`가 없어 build `E0583` 발생. 정확한 Git blob 복원으로 수정됨. 전체 원본 Rust crate에 대해 Rust 1.94.1 `clippy -D warnings`는 **기존 소스의 lint 51개 때문에 실패**, 새 코드 전용 패키지에서 strict clippy PASS. 기존 1.85 경고 정책을 수정하지 않고 앞으로 별도 품질작업으로 분리.

이번 추가 C8의 검증은 direct Rust source parity를 기준으로 한다. Grackle 원본 C 리터럴 신원은 앞서 보존된 별도 테스트/문헌에 의존하며, 이번의 새 외부 독립 라이브러리 실행은 하지 않았다. 전시간 궤적·Jacobian·완전 이온화 피드백·Case A/B 조합·FIRMS source-age·signed Bianchi 물리진화는 아직 미검증. 기계적인 상대오차 PASS는 물리적 source correctness를 대신하지 않는다.

**판정:** `PASS_SCOPED_C8_RATE_LOOKUP_ACCURACY_AND_CONDITIONAL_BENCHMARK`; `FULL_NATIVE_EOR_SCIENTIFIC_ADMISSION=HOLD`. 다음 노드: `RT-C9_C10`의 fresh-context 검토로 source failure/mask/floor/evaluator selection을 확인한 뒤 C10 판정. 전체 production 경로는 계속 별도 HOLD.

## 근거

- PR #150 original production https://github.com/cosmosapjw-quantum/rei_bianchi/pull/150
- C07 archived source/intake https://drive.google.com/file/d/18Y6q51tpoe83cT-mTs1WHdVrUlpyJuFq/view
- Grackle v3.4.1 rate function docs https://grackle.readthedocs.io/en/grackle-3.4.1/RateFunctions.html
- Smith et al. 2017, DOI: 10.1093/mnras/stw3291
