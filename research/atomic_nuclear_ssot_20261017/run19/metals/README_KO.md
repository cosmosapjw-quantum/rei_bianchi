# RUN19 선택형 Li/Be 온도계수 provider

이 단위는 기존 PR150 Li6/Li7 number-rate source를 고정99 `LogRateGrid`와 함께 실제 컴파일하고, VF1996의 Be II·III·IV 형성 total radiative-recombination 세 계수를 같은 표 경로에 추가한다. 기본 HHeD provider, 원래 13-state registry와 완료된 RUN13 history는 그대로 둔다.

## 소스 계보와 라이선스

Li 구현은 [PR150 donor fd9a21c4](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/fd9a21c4d3886a495540b51d780a83b608e72ea2/rust/rei_microphysics/src/lithium_rates.rs)의 원문이다. `upstream/rei_bianchi` 아래 원래 경로와 `include_str!` 파라미터 파일 3개를 유지하며 source byte를 변경하지 않았다. 기존 4개 테스트도 import alias만 제공하여 원문 그대로 컴파일한다. 원래 MIT `LICENSE`가 함께 있다. Li 기능은 새로운 물리식의 최초 구현이 아니라 기존 구현의 compatibility forwardport다.

표는 [고정99 owner의 rate_table.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/99e07bcff126d0a73a03bafc4b71e0b735dbcc3e/research/atomic_nuclear_ssot_20261017/run13/recovered/code/rei_bass_coupled/owner_src/rate_table.rs)를 path dependency로 재사용한다. 원래 source SHA-256은 `334e0da513b07ae78e8bbc669ac09b7c74dd9abec3c48934cbc94442c0cef8a6`이다. 복제 구현이나 새로운 default evaluator를 도입하지 않았다.

Be 파라미터와 식은 [Verner & Ferland 1996 저자 자료](https://www.pa.uky.edu/~verner/rec.html), [논문 Eq. (4)](https://arxiv.org/pdf/astro-ph/9509083)를 따른다. 원본 table1, descriptor, 공개 index와 가져온 receipt를 보존했다. 실제 컴파일되는 세 행은 원문 전체 행을 그대로 추출한 `data/vf1996_be_rr_rows.dat`이며 SHA-256은 `0792b2794c4a4d996c02537cb2e83f6b7855b58daba6e89c9675cf97e2cd2570`이다. 저자 자료에 별도 software/data licence 표기가 있다는 주장은 하지 않는다. 새 코드의 MIT와 인용한 수학식·계수 사실의 출처를 구분한다.

`provenance/ORIGINAL_SOURCE_MANIFEST.json`에 원문별 byte/hash와 원격 provenance가 있다. `provenance/R9_SCOPE_CORRECTION.json`은 앞선 inventory의 부정확한 “R9 Li/Be 6채널” 서술을 정정한다. 실제 R9 config는 HI, HeI, HeII, LiI, LiII, LiIII다. 원본 잘못된 요약을 삭제하거나 Be가 R9의 해당 6채널에 있었다고 주장하지 않는다.

## 지원하는 계수와 물리 범위

| 모듈 | 원래 계수 owner | 유효 범위 / 채널 |
|---|---|---|
| Li `lithium_rates` | Voronov CI + Badnell RR/DR | 전 채널 bundle의 교집합 `5/8.617385e-5 K`부터 `1e7 K`. 채널별 RR의 더 낮은 유효 T는 기존 `record()` 그대로다. |
| Be `beryllium_rr` | VF1996 total RR | `3 K ≤ T ≤ 1e9 K`; Be III→Be II, Be IV→Be III, Be V→Be IV의 세 채널. |

모든 계수의 단위는 cm³/s다. Proper density m⁻³와 결합할 때 `1e-6`을 곱해 m³/s로 변환한다. 밀도, photon field, 배경, abundance, thermal power는 온도표에 넣지 않는다. k_B나 다른 기본 상수를 1로 놓거나 소스의 온도 변환 상수를 교체하지 않는다.

Be의 식은

\[
\alpha(T)=\frac{a}{\sqrt{T/T_0}\,[1+\sqrt{T/T_0}]^{1-b}\,[1+\sqrt{T/T_1}]^{1+b}}
\]

이다. `a,α`는 cm³/s, `T,T₀,T₁`는 K이다. `record_forming_charge()`는 생성되는 이온의 전하를 받는다. Be I 형성은 `MissingSource`이며 구조적 zero로 대체하지 않는다. Be 상태는 q=1..4만 보유하고 함수명도 전체망 RHS 대신 `number_contribution`으로 둔다. 따라서 q=1에서의 미구현 q=1→0 손실이 물리적으로 없다는 주장은 하지 않는다.

Li6/Li7과 선택형 Be7/Be9 label은 `ElementalElectronicEquality`를 명시해야 한다. 실험 isotope-specific rate를 뜻하지 않는다. Be7 label은 decay, electron capture, daughter, nuclear lifetime 또는 abundance를 가정하지 않는다. 현재 Li 원문의 Li8/Li9는 기존대로 nuclear decay/daughter closure 미완료 오류를 유지한다.

19개 반응 목표망은 `network/TARGET_NETWORK_19.json`과 한국어 표에 전부 보존했다. Li의 전자 재결합계수는 ⁷Li 광핵 분해나 T(α,γ)⁷Li의 핵 계수가 아니다. 오른쪽 그림 목록의 전체 목표, 원래 nuclear T1–T8과 미완료 EoR/연속 수렴 의무는 축소하지 않았다.

## 실제 API

`LithiumBackend::{direct,tabulated}`와 `BeRrBackend::{direct,tabulated}`가 원문 source를 선택한다. `prepare(T)`는 값을 정확한 T와 evaluator ID 및 table node 수에 결합한다. `require_prepared(T,...)`와 backend의 `number_contribution`은 다른 T, Direct/Table 교체 및 다른 node 수의 bundle을 거부한다. 자유함수인 기존 Li owner API도 보존되어 있으므로 caller는 원하는 경로를 명시적으로 선택한다.

```rust
use rei_run19_metals::beryllium_rr::{BeRrBackend, BerylliumIsotopeNumberState};
use rei_run19_metals::lithium_rates::IsotopeRatePolicy;

let backend = BeRrBackend::tabulated(8193)?;
let prepared = backend.prepare(10_000.0)?;
// Proper densities below are a caller-supplied example, not primordial abundances.
let state = BerylliumIsotopeNumberState::new([1., 2., 3., 4.], [5., 7., 11., 13.])?;
let source = backend.number_contribution(
    10_000.0, &prepared, &state, 19.0,
    IsotopeRatePolicy::ElementalElectronicEquality,
)?;
// source.electron_m3_s is the combined contribution, to add once to a global ledger.
```

Be table은 scalar/SoA/1–4-worker ordered batch를 제공한다. 이 단위에서 SIMD, whole-driver speedup 또는 build-amortized throughput을 측정했다고 주장하지 않는다. Root의 별도 cubic/IPC 최적화와 섞지 않는다.

## 실행 결과

`validation01`의 원문 Li 4개 테스트가 실제 PASS했다. 첫 새 테스트 묶음에서는 5 PASS, 1 FAIL이었다. 실패한 비교는 다른 log-domain f64 계산값을 Decimal80 golden처럼 다루며 `<8eps`를 요구했고, 실제 차이가 정확히 `8eps`인 경계였다. 소스 식·계수는 맞았다. 단일 진단과 실패 출력은 모두 보존했다.

직접 denominator 식의 독립 Decimal80 기준 18개 값을 만든 뒤 해당 새 테스트 묶음 6개만 다시 실행하여 PASS했다. 이미 PASS한 Li 4개를 다시 실행하지 않았다. 현재 독립 테스트 수는 **10개**이며, 과거/재실행 횟수나 반복 기준점으로 늘려 세지 않는다. Rust 직접식과 Decimal80 반올림값 18개 사이 최대 상대 차이는 `4.440892098500626e-16`이다. 고정 native dependency의 원래 91개 파일 hash가 변경되지 않았음을 실제 확인했다.

원문 Li 테스트의 1,015 T scan 최대 상대오차는 `1.1733732758756332e-6`이다. 별도 새 pointwise scan은 다음과 같다.

| 실제 새 scan | 값 |
|---|---:|
| Li 온도 점 | 259 |
| Be 온도 점 | 1,023 |
| coefficient 기록 행 | 6,177 |
| isotope number-contribution 행 | 1,282 |
| Li table/direct 최대 상대차 | `1.0729097573713986e-6` |
| Be table/direct 최대 상대차 | `7.877227004016163e-8` |
| nuclei residual / event 합 최대 | `1.1887233610617907e-16` |
| ionic charge−free electron residual / event 합 최대 | `4.474005917728148e-16` |

`validation02/scan`의 두 CSV가 실제 계산값을 보존한다. 가스 밀도와 자유전자 밀도는 제조된 점별 진단 입력이다. 초기 우주의 abundance, charge-neutral plasma 해 또는 시간 이력으로 해석하지 않는다. 이번 단위의 trajectory integration과 전체 gas/radiation rerun은 **0회**다.

Be 10,000 K의 Rust 직접계수는 형성 Be II/III/IV 순서로 `1.486512849657365e-12`, `5.118059016664182e-12`, `1.0826026237647781e-11 cm³/s`다. 기존 Li Badnell RR의 q=1,2,3 채널은 같은 T에서 `2.4379829879920255e-13`, `2.124882458920259e-12`, `5.613945730353164e-12 cm³/s`다. 후자는 VF1996 Li fit을 조용히 대체한 값이 아니다. Li 전체 CI/RR/DR bundle을 10,000 K에서 호출하면 기존대로 domain 오류다.

표의 sampled 비교는 물리적 fit uncertainty, 도함수 정확도, 비선형 opacity feedback, gas-history 오차 또는 spectral continuum bound를 포함하지 않는다. 핵 보존 residual이 작다는 사실 역시 그 수렴 증명이 아니다.

## 재현 명령과 전달 경로

실제 작업 manifest는 `/tmp/rei_run19_repo/.../run13/recovered/code/rei_bass_coupled`를 path dependency로 사용했다. 최종 Git 배치가 `run19/metals`이면 이 dependency의 표기만 `../../run13/recovered/code/rei_bass_coupled`로 바꿀 수 있다. source owner나 계산식은 바꾸지 않는다. 원본 RUN13 payload는 필요할 때 같은 Git 계보의 `run13/git_transport/restore.py`로 복원하며 완료된 IVP는 다시 돌리지 않는다.

```bash
python3 -B scripts/run_validation.py \
  --prefix /tmp/rei_run19_runtime/prefix \
  --output /tmp/rei_run19_metals/validation01 \
  --target-dir /tmp/rei_run19_metals/build_target

python3 -B scripts/make_be_reference.py

python3 -B scripts/run_validation.py \
  --prefix /tmp/rei_run19_runtime/prefix \
  --output /tmp/rei_run19_metals/validation02 \
  --target-dir /tmp/rei_run19_metals/build_target \
  --test-target trace_providers
```

위는 기록된 순서다. 이미 존재하는 출력 directory나 Decimal reference 파일에 다시 쓰려 하지 말고 새 working copy/출력 경로를 사용한다. 실제 argv, 환경, stdout/stderr, compile exit와 binary hash는 각 `EXECUTION_RECEIPT.json`에 있다. 기본 Rust profile을 유지했고 fast-math/RUSTFLAGS를 새로 주입하지 않았다. Git 게시와 두 cloud backup의 최종 commit/ZIP identity는 부모 RUN19 delivery manifest가 소유한다.

## 다음 미완료 작업

이 provider를 기본 gas13에 활성화하려면 source-compatible ionic registry/projection, 밀도·전자 ledger, thermal/photo moment와 실제 사용 온도 범위를 먼저 정의해야 한다. Be I/CI/DR와 Be7 nuclear evolution은 별도 source 문제다. 원래 19반응의 핵 계수 이식과 T1–T8, 전체 coupled history 및 연속 오차 budget은 계속 미완료다. 표의 persistence/cubic backend 연결은 별도의 RUN19 최적화 단위에서 다룬다.
