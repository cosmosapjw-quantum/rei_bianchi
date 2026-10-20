# BRPERF01 — 양의 compact H/He/D 온도 계수 표

## 판정과 범위

원본 `igm_rates(T)`의 15개 온도 전용 계수를 한 번씩 샘플하고, `ln(T)` 균일 격자의 계수 공간 PCHIP를 양의 Bernstein 합으로 평가하는 opt-in Rust 수신기를 구현했다. **추천 opt-in은 scalar 8,193-node 표이며, `RateBackend::default()`는 계속 Direct다.** 1–10⁶ K에서 검사한 44,577개 온도 × 15개 채널의 최대 상대오차는 **1.3001663416112308×10⁻⁵**였다. 이 값은 기록된 표본 집합의 오차이며 모든 실수 온도에 대한 엄밀한 상한은 아니다.

8,193-node 표의 payload는 **4,259,840 bytes**, 이전 65,537-node 표는 **9,109,624 bytes**다. 동일한 메모리 측정 API 기준으로 **53.2380%** 줄었다. 여섯 ABBA 블록의 Direct 대비 paired speedup 중앙값은 **4.9166배**였다. 동일한 `wide::f64x4` 구현은 bit parity를 만족했지만 이 SSE2/no-AVX 실행 환경에서 scalar보다 느렸으므로 추가 SIMD 가속을 성공으로 분류하지 않았다.

이 문서는 온도 계수 수신기와 그 독립 검산을 다룬다. `native_rates` 연결을 통한 H/He/D 반응 이력, 에너지 장부, RHS 실행 시간은 인접 `integration` 단위가 별도로 검증한다. 이 최적화는 광자 출생 적분, 분광·각도·시간 수렴, full EoR 초기조건 또는 양방향 Einstein 피드백의 완료 상태를 바꾸지 않는다.

## 원래 물리 입력과 분리 경계

원 Grackle 계보의 두 파일을 byte 변경 없이 참조한다. SHA-256은 다음과 같다.

| 원 파일 | SHA-256 |
| --- | --- |
| `igm_rates.rs` | `310164e620617f3089d488bd1f9668996b4a4cbd191383e45303def176ef81cf` |
| `rate_table.rs` | `334e0da513b07ae78e8bbc669ac09b7c74dd9abec3c48934cbc94442c0cef8a6` |

원 source pin은 `grackle-project/grackle`의 `af7939494ce65007887ada7b98d1813df6843346`이다. 표는 `igm_flat` 원 순서의 CI 3개, RR 3개, HeII DR, CE 3개, RR cooling 3개, DR raw cooling, free-free를 보존한다. CI/RR/DR은 cm³/s, 일반 CE/cooling은 erg cm³/s이며 **metastable HeI CE만 erg cm⁶/s**다. 해당 채널의 전자 밀도 제곱 인자를 다른 채널과 혼동하지 않는다.

T 의존 계수만 저장한다. 전자·이온 밀도 곱, 광장, CMB 온도와 에너지 교환, Bianchi 기하, 개체수 갱신, CX half-flow, 열·화학·기하 장부와 four-corner 제어기는 표 내부로 옮기지 않는다. D의 H-equality 계수 재사용은 기존 소비자 소유권을 따른다. Savin 전하교환의 두 경험적 방향 계수와 0.0037 eV 결함은 이번 compact 표에서 바꾸지 않는다. 경험적 CX 양방향 fit을 임의의 단일 Boltzmann 비율로 다시 정의하지 않는다.

## 방법 비교와 선택 이유

이전 `IgmRateTable(65537)`은 양의 채널을 log-rate 공간에서 선형 보간한다. 계수마다 exp 복원이 필요하고 큰 표를 읽는다. 계수 공간 선형 보간은 exp 없이 양수지만 같은 격자의 곡률 오차가 크다. 고차 비제약 다항식은 양의 source 노드만으로 중간값 양성을 보장하지 않는다. 이번에는 **계수 공간의 shape-preserving cubic Hermite**를 선택하여 한 번의 ln(T), 공통 cell 조회와 공통 4개 가중치를 15개 채널이 공유하도록 했다.

균일 좌표와 차분을

\[
x_i=i h,\quad h=\frac{\ln10^6}{N-1},\quad y_i=k(\exp x_i),\quad d_i=y_{i+1}-y_i
\]

로 놓는다. 내부 노드의 cell-scaled 기울기는 인접 차분의 부호가 다르거나 하나가 0이면 0, 그 외에는

\[
\widehat m_i=\frac{2d_{i-1}d_i}{d_{i-1}+d_i}
\]

다. 구현은 작은 rate의 제곱이나 곱에 의한 underflow를 피하기 위해

\[
\widehat m_i=\operatorname{sgn}(d_i)
\frac{2\min(|d_{i-1}|,|d_i|)}{1+\min(|d_{i-1}|,|d_i|)/\max(|d_{i-1}|,|d_i|)}
\]

를 쓴다. SciPy의 공식 PCHIP 문서에 제시된 weighted harmonic derivative는 균일 격자에서 이 식으로 환원된다. 원 방법 참고: Fritsch & Butland (1984), SIAM J. Sci. Comput. 5(2), 300–304, DOI `10.1137/0905021`; [SciPy 공식 문서](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html). 실제 조회 receipt는 `evidence/PRIMARY_PCHIP_WIDE.json`에 있다.

각 cell의 Bernstein controls와 가중치는

\[
\begin{aligned}
B_0=y_i,\quad B_1=y_i+\widehat m_i/3,\\
B_2=y_{i+1}-\widehat m_{i+1}/3,\quad B_3=y_{i+1},\\
w(q)=((1-q)^3,\,3(1-q)^2q,\,3(1-q)q^2,\,q^3).
\end{aligned}
\]

로 두고 \(k_h(T)=\sum_{r=0}^{3}w_rB_r\)로 평가한다. harmonic 기울기는 현재 cell의 차분과 같은 부호이며 크기가 해당 차분의 2배 이하이므로, 두 내부 control도 비음수 endpoint 값 사이에 있다. 따라서 정확한 실수 연산에서는 비음수 control과 가중치의 합이며, 구현 역시 뺄셈 없이 양의 곱과 덧셈으로 평가한다. 부호가 깨진 control이나 subnormal/nonfinite control을 발견하면 그 cell은 직접 평가로 돌린다. 0인 DR 채널은 0으로 유지한다.

Wolfram Language가 독립적으로 Hermite식과 Bernstein식의 차이 0, 가중치의 합 1, 0≤q≤1에서 가중치 비음수를 반환했다. 실행식과 응답 `{0, 1, True}`는 `evidence/WOLFRAM_BERNSTEIN.json`에 보존했다. 이 대수 검사는 보간식의 성질을 검증하며 원자 rate fit의 물리 정확도를 판정하지 않는다.

## 분기, floor, 진단과 입력 거부

source의 CI floor 10⁻²⁰ cm³/s, 원 eV/K 변환 11605.0, `T/11605 <= 0.8` 저온 DR 분기, H RR 5500 K 분기 및 CE/DR 지수 cap을 유지한다. 원 `igm_branch_knots()`와 floor-mask 전환 cell을 식별하고 **좌우 두 cell**까지 direct fallback으로 확장한다. endpoint 주변도 fallback한다. 보간기 도함수의 인접 노드가 불연속을 가로지르는 문제를 이 buffer로 피한다.

low-DR에서 DR rate와 사용되는 DR cooling은 0이지만, `dr_raw_cooling`과 `dr_excluded` 진단은 원 정의대로 유지한다. floor가 활성인 CI는 보간 후에도 정확히 10⁻²⁰으로 복원하며 diagnostic에는 해당 full coefficient를 둔다. CE cap 진단도 원 문턱 계산과 같은 비교를 사용한다.

NaN, 무한대, 0 이하 온도와 1–10⁶ K 범위 밖 요청은 원 direct owner에 전달되어 동일하게 거부된다. 외삽이나 경계값 고정은 하지 않는다. population과 광원 입력은 이 API에 들어오지 않으므로 그 유효성 검사는 기존 native 소비자 책임이다.

## 4개 해상도의 실제 결과

각 해상도마다 20,001개의 offset log-uniform 온도와 모든 cell의 q=0.211, 0.5, 0.789를 검사했다. scalar/SIMD 채널 mismatch는 모두 0이었다.

| 노드 | 검사 온도 | 메모리 bytes | fallback cells | 최대 source 상대오차 | 10⁻⁴ 표본 기준 |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1,025 | 23,073 | 532,480 | 40 | 7.70451294×10⁻³ | 미달 |
| 2,049 | 26,145 | 1,064,960 | 43 | 8.97607721×10⁻⁴ | 미달 |
| 4,097 | 32,289 | 2,129,920 | 45 | 1.06664028×10⁻⁴ | 미달 |
| 8,193 | 44,577 | 4,259,840 | 48 | 1.30016634×10⁻⁵ | 통과 |

가장 큰 오차는 모두 지수 cap을 벗어난 HI CE 채널에서 나왔다. 8,193-node의 해당 온도는 약 1723.5255 K다. 이 비교는 물리 source를 그대로 둔 보간 오차 연구다. 이전 65,537-node log-linear 표는 같은 집합에서 약 3.83×10⁻⁷ 최대오차로 **더 정확하다**. 새 compact 표는 설정한 표본 오차 기준 안에서 메모리와 평가 비용을 줄이는 선택이며, 모든 지표를 동시에 개선했다는 주장은 하지 않는다.

한 번의 build는 각 source 노드당 정확히 한 번 원 `igm_rates`를 호출한다. 이는 구조적으로 N source 호출이다. build 시간은 실행 기록에 남겼지만 반복 측정한 kernel benchmark와 같은 강도의 성능 판정으로 사용하지 않는다.

## 독립 검산

Python은 총 **14,910개 channel sample**을 읽어 두 경로로 독립 검산했다. SciPy `PchipInterpolator`는 출력된 실제 ln(T) 간격을 이용하고, 별도 Decimal 60자리 계산은 Hermite basis와 harmonic derivative를 직접 계산한다. Rust의 Bernstein 평가를 복사하지 않는다.

| 노드 | SciPy 최대 상대차 | Decimal 최대 상대차 | fallback bit mismatch |
| ---: | ---: | ---: | ---: |
| 1,025 | 5.73×10⁻¹⁴ | 4.44×10⁻¹⁶ | 0 |
| 2,049 | 9.53×10⁻¹⁴ | 4.44×10⁻¹⁶ | 0 |
| 4,097 | 6.62×10⁻¹⁴ | 4.44×10⁻¹⁶ | 0 |
| 8,193 | 7.06×10⁻¹⁴ | 4.44×10⁻¹⁶ | 0 |

이 검산의 독립성은 수치 보간기에 대한 것이다. 원자 fit 노드 자체는 고정된 원 owner의 출력이다. 물리 source에 대한 이전 독립 검증과 이번 보간기 검증을 혼동하지 않는다.

Rust 단위검사는 5개다. 기본 Direct parity, 잘못된 온도 거부, source 호출 횟수 계약과 양의 controls, 분기 주변 full diagnostics parity, 10,001개 온도에서 scalar/SIMD 전체 필드 bit parity, source-bound cache readback 및 손상 거부를 포함한다. 캐시 검사는 1,026개 노드로 실행하여 2의 거듭제곱 interval 수에 한정되지 않은 metadata round trip을 검사한다.

## 실행 시간과 SIMD 판정

각 candidate에 대해 `Direct → candidate → candidate → Direct` 순서로 6번, 매 run 100,000개 동일 온도 query를 실행했다. 모든 15개 계수와 일부 diagnostics를 checksum으로 소비했다. 각 경로 10,000개 query warmup을 수행했고, 다른 단위의 benchmark와 겹치지 않도록 조정했다. 관측값은 삭제하거나 빠른 구간만 고르지 않았다.

| Candidate | Direct 중앙값 ms | Candidate 중앙값 ms | paired speedup 중앙값 |
| --- | ---: | ---: | ---: |
| 기존 65,537 log-linear | 44.787 | 30.265 | 1.5131× |
| compact 1,025 scalar | 43.075 | 9.411 | 4.7685× |
| compact 2,049 scalar | 42.939 | 8.734 | 4.9319× |
| compact 4,097 scalar | 43.111 | 9.145 | 4.9078× |
| compact 8,193 scalar | 44.524 | 9.070 | 4.9166× |
| compact 4,097 SIMD | 44.827 | 9.926 | 4.6795× |
| compact 8,193 SIMD | 43.160 | 10.232 | 4.4201× |

paired speedup은 각 ABBA block에서 A 평균/B 평균을 구한 뒤 6개 비율의 중앙값이다. 두 시간 열의 중앙값 비율과 정확히 같을 필요는 없다. 8,193 scalar의 블록별 speedup 범위는 4.0635–5.2893이다. SIMD 범위는 2.4396–6.8472로 더 넓다. 스케줄링과 캐시 영향이 있는 샌드박스 측정이며 전체 복사·반응 trajectory 가속률로 바로 옮기지 않는다.

Rust 패키지 `wide = 1.7.1`을 실제 사용했다. 이 빌드는 SSE2가 켜지고 AVX는 꺼져 있다. `f64x4`의 scalar와 같은 연산 순서를 써 모든 평가 표본에서 bit parity를 얻었다. 별도 unsafe 코드, fast-math, FMA는 추가하지 않았다. 현재 결과에 따라 scalar를 추천하고 SIMD 경로는 명시적 선택으로 제공한다. 외부 패키지를 썼다는 사실을 추가 성능 성공으로 대신하지 않는다.

## 캐시, 재현과 실패 분류

`sha2 = 0.10.9`를 사용하여 schema ID와 실제 compile된 두 원 source byte string을 묶고, serialized payload에도 SHA-256을 붙인다. cache는 magic, source digest, node 수, cell blocked/floor mask, 64개 f64 control, payload digest로 구성된다. 다른 source, 잘린 payload, 손상된 payload, 비정상 mask/control을 거부한다. 이는 accidental corruption과 source mismatch 검출이며 재계산된 hash를 가진 악의적 payload의 인증 체계는 아니다.

`RUN_STAGE.sh`는 tests, strict Clippy, scoped rustfmt, 4해상도 probe와 Python oracle을 수행한다. `--bench`를 주면 kernel ABBA도 실행한다. 원 parent source를 포함한 snapshot과 빈 target에서의 재컴파일은 `prepare_restore.py` 및 `evidence/FRESH_*`에 기록된다. offline registry와 Rust toolchain은 별도로 고정된 공통 runtime을 재사용하며 이 범위를 restore 기록에서 밝힌다.

오차 기준을 넘긴 1,025/2,049/4,097 표는 **COEFFICIENT_ACCURACY_TARGET_MISS**다. 물리적 해 부재, population 음수 또는 CX 수렴 실패로 재분류하지 않는다. SIMD의 추가 성능 미확인은 **NO_EXTRA_SPEEDUP_ON_MEASURED_TARGET**다. 이 모듈에서 `Cx(WorkLimit)`는 실행하지 않으며 native integration의 원 분류를 유지한다. original GL photon birth bias나 장구간 해의 수렴 상태는 이번 계수 표의 PASS로 승격하지 않는다.

다음 DAG는 (1) 독립 native 반응 이력과 장부의 최종 합산, (2) 선택된 표 오차의 더 엄밀한 per-channel bound 또는 적응 격자 연구, (3) AVX-capable target에서 SIMD의 별도 측정, (4) background 및 full source-on radiation과 공통 온도 재사용을 안전하게 연결하는 검증이다. 이번 unit의 완료 범위는 양의 compact 수신기, source-bound 재사용 cache, 실제 속도·메모리 비교와 독립 수치 검산이다.
