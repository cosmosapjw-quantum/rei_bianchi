# 연속 광원 H/He IGM: 첫 실제 코딩 수정 결과

2026-10-06 UTC. 대상은 z=12→11.5의 manufactured homogeneous FLRW, Case-A escape, C=1, primary-only H/He 모형이다. 관측된 재이온화 이력이나 Bianchi 수송 검증이 아니다.

## 결론

연속 방출을 고정 시각의 광자 묶음으로 근사하던 경로 옆에, **연속 emissivity를 RHS에 넣는 새 Rust 경로**를 구현했다. 기존 방정식의 임의 clipping, 온도 floor, 허용오차 완화 없이 검증했다. 기존 pulsed-source 진단과 rec_bianchi의 통과 기준선은 보존했다.

최종 Rust 계산은 81개 출력점에서 더 세밀한 독립 Radau 기준과 **원래의 모든 변수별 허용오차 및 광자 수·에너지 예산을 통과**했다. 시간·스펙트럼·출력 시각의 별도 비교와 독립 검토 결과를 함께 보아야 한다. 이 결과는 유한 구간·지정 모형의 수치 검증이지 continuum 오차정리나 임의 초기조건에 대한 보증이 아니다.

## 1. 바꾼 것

- comoving log-energy η=ln(E/eV)+ln(a)를 사용한다. 고정 η 노드의 물리 에너지는 E=eV exp[η−ln(a)]로 적색편이한다.
- E^-2 광원의 dE→dη Jacobian E와 proper-time→ln(a)의 1/H를 각각 한 번 적용한다.
- 구간 광원량을 coupled backward Euler의 광자 방정식에 포함한다. 광자 감소·H/He 이온화·결합에너지·열은 같은 absorption owner를 사용한다.
- 적색편이의 두 half step과 source/absorption의 공통 stage 에너지를 사용하여 에너지 ledger를 닫는다. 전체 방법은 BE 때문에 시간 1차다.
- uniform η grid와 threshold-bands grid를 분리했다. 후자는 source/흡수 문턱의 초기·최종 위치로 나뉜 좁은 구간에 양의 Gauss 노드를 집중한다. 자동 AMR가 아니다.
- source support와 absorber cutoff는 명시적 event와 channel mask로 처리한다. 두 event가 인접한 부동소수점 수여서 내부 midpoint가 없을 때도 양의 구간을 생략하지 않고 endpoint stage와 구간 mask를 사용한다. 에너지를 임의 이동시키거나 가까운 사건을 epsilon으로 합치지 않았다.
- source-free photon tail은 log-count를 보존한다. 부동소수점 underflow는 별도 상계와 기존 예산으로 관리한다.

새 경로는 opt-in 연구용 CLI다. 기존 API/진단 경로는 유지된다. 새 경로의 checkpoint/restart 및 자동 LTE 기반 시간적응은 아직 없다. 실패 시 마지막 accepted 위치를 기록하고 nonzero exit하며, 기존 출력 디렉터리는 덮어쓰지 않는다.

## 2. 실패를 보존하며 수정한 순서

1. 기존 경로는 첫 birth node 이전에 양의 연속 emissivity가 있어도 emitted_N=0이었다. 이 동작을 실패 검사로 고정한 뒤 새 경로에서 통과시켰다.
2. 연속 source 도입 후 같은 spectral grid에서 시간간격을 4배씩 줄이면 오차도 약 4배 줄었다. 1차 시간수렴과 일치한다.
3. uniform spectral grid는 256→512 panels에서도 active radiation energy가 5.13 허용치만큼 달랐다. 보존량 통과로 이를 숨기지 않았다.
4. threshold-bands로 바꾸어 32→64 panels/band 비교가 통과했다. Gauss2와 독립 Gauss4 비교도 통과했다.
5. adjacent-float event와 정확한 He cutoff 출력의 단측 convention 문제를 실제 실패 검사로 발견하고 mask로 수정했다.
6. 21개 출력점에서는 결합 비교가 통과했지만, 81개로 늘리자 초기 expansion-work 누적오차가 1.458 허용치로 실패했다. 시간간격을 다시 절반으로 줄인 최종 계산에서 0.714로 내려갔다. 실패 결과는 보존했다.

## 3. 최종 수치 계약과 결과

물리 source는 원래 의도한 constant proper emissivity 10^-15 photons/H/s, E^-2 SED 13.7–100 eV다. cosmology·초기 온도 30 K·잔류 HII 2×10^-4·중성 He·closure는 유지했다. 기존 birth_panels/energy_panels 설정은 새 경로에서 쓰지 않으며 별도 spectral 옵션으로 명시한다.

최종 candidate:
- threshold-bands 32 panels/band, 8 bands, 512 nodes
- max Δln(a)=3.90625×10^-7, 80 output panels =81 samples
- accepted steps 100,583, rejected steps 0, adjacent-event endpoint stages 16
- source/energy quadrature weight를 재정규화하지 않음

독립 기준:
- threshold-bands 64 panels/band, 1,024 nodes
- Radau rtol=2×10^-12, atol=2×10^-15
- 별도 Python 물리 구현, 실제 시간 source와 정확한 characteristic redshift
- source-on count/source-off optical-depth 좌표; 모든 accepted state의 보존량 및 물리 domain 검사

| 비교 항목 | 최종 측정 |
|---|---:|
| 전체 변수 최악의 허용치 비 | 0.921259, Γ_HeII |
| T 최대 절대차 | 0.154042 K |
| T 최대 상대차 | 2.16196×10^-5 |
| n_e/n_H 최대 절대차 | 6.01604×10^-7 |
| Γ_HeII 최대 상대차 | 9.21373×10^-4 |
| 초기 expansion-work 최악 허용치 비 | 0.713683 |
| candidate 광자 수 예산 비 | 0.002487 |
| candidate 에너지 예산 비 | 0.016900 |
| reference 광자 수 예산 비 | 0.189481 |
| reference 에너지 예산 비 | 0.061877 |

‘허용치 비’와 ‘예산 비’는 1 이하가 통과다. fraction/ne 허용치는 10^-6+10^-3|reference|, T는 10^-6 K+10^-3|reference|, Γ는 10^-22 s^-1+10^-3|reference|다. 광자/에너지 ledger 허용치도 기존 comparator 그대로 적용했다. 기준 수치와 허용치를 결과에 맞춰 변경하지 않았다.

별도 점검:
- Rust 전체 223 tests PASS, Python 전체 22 tests PASS.
- fine reference tolerance tightening: 0.1배 허용치 기준 최악 6.88×10^-6, PASS.
- 32→64 spectral refinement: 최악 0.916209, PASS.
- 비정합 위상 61개 출력의 spectral refinement: 최악 0.980896, PASS. 여유가 작으므로 오차가 완전히 없다는 해석은 부적절하다.
- 같은 Rust time bound에서 출력 21→81 변경 후 공통 시각 비교: 0.1배 허용치 기준 최악 0.012935, PASS.
- Gauss2/Gauss4 독립 quadrature 비교도 PASS.

## 4. fluctuation과 오류전파 해석

과거 21개 출력에서 T의 잦은 극값 12개가 나타났고, 동일한 pulsed forcing을 푸는 독립 Radau도 이를 재현했다. 새 연속 방출 계산은 81개 출력에서 두 개의 넓은 turning point를 보이며 독립 기준과 위치가 일치한다. 단조 온도를 강제로 요구하거나 곡선을 smoothing한 결과가 아니다.

첨부 그림은 원래 pulsed reference, 새 Rust, refined continuous reference를 나란히 보여 준다. Γ의 잔여 spectral 오차에는 작은 격자성 진동이 남아 있다. 이번 기준 안에 들어왔지만, 이것이 좌표별 adaptive error controller가 다음 단계로 유용한 이유다.

variable_error_decomposition.csv는 각 출력에서 다음 EOS의 유한 오차를 정확히 분해한다:

T ∝ w/(1+r+x_e), r=n_He/n_H.

에너지 변화 기여와 입자수 변화 기여의 합은 실제 상대 T 오차와 약 4×10^-16 이내에서 일치한다. 전자수 오차는 HII, r·HeII, 2r·HeIII 기여로 분리했다. 이는 EOS의 대수적 분해이며, 전체 비선형 동역학계의 variational propagator 또는 전역 안정성 증명은 아니다.

## 5. 재현

저장소 기준 revision은 4567b91785dbba1964fd807ab9c6873f542c1030이며, 동봉 source delta와 patch가 이번 변경이다. 원본 README의 설치·테스트 지침을 따른다.

```sh
cargo test --manifest-path rust/rei_microphysics/Cargo.toml --offline
cargo build --release --manifest-path rust/rei_microphysics/Cargo.toml --example igm_continuous --offline
cargo run --release --offline --manifest-path rust/rei_microphysics/Cargo.toml --example igm_continuous -- \
  --config configs/igm_manufactured_v1.cfg --output NEW_RUST_OUTPUT \
  --spectral-grid threshold-bands --spectral-panels 32 \
  --max-dln-a 0.000000390625 --output-panels 80
OPENBLAS_NUM_THREADS=1 python tools/igm_continuous_reference.py \
  --config configs/igm_manufactured_v1.cfg --output NEW_REFERENCE_OUTPUT \
  --spectral-grid threshold-bands --spectral-panels 64 \
  --rtol 2e-12 --atol 2e-15 --times-csv NEW_RUST_OUTPUT/history.csv
python tools/igm_compare.py --candidate NEW_RUST_OUTPUT/history.csv \
  --reference NEW_REFERENCE_OUTPUT/history.csv --output comparison.json
```

Cargo target 경로는 CARGO_TARGET_DIR 및 manifest 위치 설정에 따라 달라진다. 실행된 Rust binary SHA-256은 3b26bdf8460d72650271ebdd43a0fa2c30dbca7aa5c3042f5647040747847c7a다. 증거의 원본 config와 CLI override, producer source, binary·CSV hash를 함께 확인한다.

독립 검토는 최종 81-row 비교를 직접 재계산하고 실제 Rust 223 tests를 실행하여, 이 manufactured fixture와 검사한 격자에 한정한 ACCEPT로 판정했다.

## 6. 남은 범위

- 자동 시간 LTE 제어, 에너지·각도 국소 refinement 및 remap 오차제어는 아직 구현하지 않았다. 현재 threshold-bands는 물리 문턱을 활용한 고정 격자다.
- 새 경로에 checkpoint/restart를 추가해야 장기 production 실행에 적합하다.
- rec_bianchi의 pure-H 검증은 그대로 두었으며 RECFAST 직접 비교를 이번에 실행한 것은 아니다.
- 전체 reionization redshift 범위, 관측에 맞춘 emissivity/IGM, arbitrary closure, Bianchi shear·anisotropic stress, polarized CMB coupling은 별도 검증이 필요하다.
- 원래 pulsed diagnostic의 FAIL을 삭제하거나 같은 문제의 PASS로 바꿔 적지 않았다. 이번 PASS는 명시적으로 continuous-source 문제의 새로운 경로에 한정된다.

BASS의 실제 구현 감사와 다음 적응형 연결 설계는 별도 문서로 제공한다. background BDF의 기존 시간적응을 보존하고 Q full-f 수송 및 microphysics의 오류 기준을 연결하는 것이 후속 범위다.
