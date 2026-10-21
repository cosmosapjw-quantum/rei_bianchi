# Native 계수에서 출발하는 source-age 경계와 VigilODE affine 전파

작성일: 2026-10-19. 연구 범위: `vigilode_age_transport_20261019/`.

**판정 대상은 보관된 native source packet에서 추출한 계수로 정의한 고정 gas·고정 geometry·고정 node 양성 수송 모형이다.** 이 문서는 그 모형의 수학적 경계와 실제 Rust 구현의 연결을 설명한다. 원래 nonlinear Grackle 진화의 오차 경계를 얻었다고 주장하지 않는다. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.

## 1. 이번 연구가 추가하는 것

기존 연구는 source-matched reference와 age marginal만으로 photon response를 제어할 수 없는 반례를 이미 갖고 있다. 이번에는 기존 age64 준비 단계의 실제 source packet 64개, 총 57,344개 광자 node를 그대로 사용한다. 같은 packet의 출생 시각만 8/16/32개 시각으로 묶어 원래 64개 시각과 비교한다. 재구성된 packet을 새로 만들거나 실제 age32 native trajectory를 실행하는 실험이 아니다.

이 선택은 출생 시각의 영향과 opacity의 상관관계를 분리해 관찰할 수 있게 한다. 전체 native 해에 관한 결론을 얻으려면 시간에 따라 변하는 gas, geometry, closure와 node 재구성의 오차를 별도로 제어해야 한다. 이번 계산은 그 조건을 만들어 내지 않는다.

원본 physics SHA는 `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`이다. `prepare_export.py`는 기존 manifest 검증을 통과한 153개 입력에서 별도 준비 사본을 만든다. 원래 example과 transformed RHS는 유지하고 별도 example 및 읽기 전용 prepared-node 접근만 추가한다. `inputs/EXPORT_RECEIPT.json`, `inputs/native_setup.json`, 독립 C9의 `EXPORT_NODE_AUDIT.json`이 실제 연결 증거다.

## 2. 계수, 단위와 모형 정의

각 label i에 대해 다음 값을 고정한다.

| 기호 | 의미 | 단위 |
|---|---|---|
| w_i | 원래 source packet의 node photon weight | photons/H |
| b_i | 출생 proper time | s |
| T | 관측 proper time, 모든 출생 시각 이상 | s |
| E_i | 고정 endpoint geometry에서의 photon energy | eV |
| λ_i,s | species s의 고정 absorption hazard | s^-1 |
| Λ_i = Σ_s λ_i,s | 총 absorption hazard | s^-1 |
| a_i = T − b_i | source age | s |

species는 HI, HeI, HeII다. 원 native cross-section 함수와 고정 endpoint gas에서 계산한 `c n_a,s σ_i,s`가 CSV의 binary64 hazard가 된다. **본 모형은 이 내보낸 binary64 값을 정확한 dyadic 실수로 해석하고, 그 species 합을 정확한 실수 합으로 정의한다.** 원 RHS의 `c * compensated_sum(n_a,s * σ_i,s)`와 연산 결합 순서가 다를 수 있다. 따라서 원 RHS의 rate bit identity나 연속 원자물리 함수의 오차 포함을 주장하지 않는다.

고정 gas fractions는 `[0.010065857799832125, 0.010066719415292124, 0.000999219556540277]`, thermal state는 `1.1243735845579859 eV/H`다. source node는 이 gas에서 이미 감쇠한 endpoint survivors가 아니라 원래 birth templates다. 에너지는 endpoint geometry에 고정되어 cosmological redshift의 시간 진화를 이번 모형에서 다시 계산하지 않는다.

모든 입력 weight와 hazard가 유한·비음수이고 T ≥ b_i이면 양성 선형 수송의 해는

\[
n_i(T)=w_i e^{-\Lambda_i(T-b_i)}.
\]

Λ_i > 0일 때 species별 누적 photoevent는

\[
A_{i,s}(T)=w_i\frac{\lambda_{i,s}}{\Lambda_i}
                \bigl(1-e^{-\Lambda_i(T-b_i)}\bigr).
\]

Λ_i = 0이면 n_i = w_i, 모든 A_i,s = 0이다. 수치 구현에서도 이 passive node를 버리지 않는다. 실제 입력에는 4,096개가 있다.

보고하는 관측량은 N = Σ n_i, U = Σ E_i n_i, M1 = Σ a_i n_i, M2 = Σ a_i² n_i다. 단위는 각각 photons/H, eV/H, photon·s/H, photon·s²/H다. 정확한 모형에서

\[
N(T)+\sum_{i,s}A_{i,s}(T)=\sum_i w_i
\]

이므로 출력 interval로 조합한 photon ledger가 0을 포함해야 한다. 에너지 ledger를 구성하려면 동일한 E_i를 감쇠·흡수 양쪽에 사용해야 한다. 별도로 반올림해 내보낸 excess energy와 threshold를 더해 E_i와 bitwise 같다고 가정하지 않는다.

## 3. 양성 exponential enclosure

일반적인 floating point `exp` 결과에 임의의 상대 오차를 덧붙이지 않는다. `num-rational::BigRational`과 `num-bigint::BigInt`로 입력 dyadic 값을 정확히 표현한 뒤

\[
\tau_i=\left(\sum_s\lambda_{i,s}\right)(T-b_i)
\]

를 정확히 계산한다. `serde_json`의 `float_roundtrip`과 충분한 자리의 CSV를 이용하며, C9는 읽어 들인 값과 내보낸 값을 별도로 점검한다.

τ = 0이면 interval은 정확히 [1,1]이다. 0 < τ < 752이면 이진 나눗셈으로 r = τ/2^k ≤ 1/2가 되게 한다. 교대급수의 항 크기가 감소하므로

\[
S_{19}(r)\le e^{-r}\le S_{18}(r),\qquad
S_m(r)=\sum_{j=0}^{m}\frac{(-r)^j}{j!}.
\]

두 다항식은 정확한 유리수로 계산한다. 유리수를 binary64로 바꾸는 후보 값을 얻은 후, 후보의 정확한 dyadic 값과 원 유리수를 비교하고 필요한 방향으로 인접 float를 선택한다. `to_f64` 자체를 방향 반올림 연산이라고 가정하지 않는다. 비음수 interval을 VigilODE의 원래 directed multiplication으로 k번 제곱하면 원래 exponential의 enclosure를 얻는다. 정확한 해가 [0,1] 안에 있다는 사실로 그 범위에 제한하는 것은 유효하다.

τ ≥ 752일 때는 [0,η], η = 2^-1074를 반환한다. 근거는 다음 유리수 부등식이다.

\[
e^{0.7}>1+0.7+0.7^2/2+0.7^3/6=12013/6000>2.
\]

따라서 ln 2 < 0.7, 1074 ln 2 < 751.8 < 752이고 e^-752 < 2^-1074다. central float가 0으로 underflow하더라도 양의 상한 η를 남긴다. 이 경계는 본 scalar 모형에서 유효하며, 원래 native subnormal count/energy representation 문제를 고친다는 뜻은 아니다.

Rust의 boundary tests와 별도 Python Decimal 100자리 계산이 이 구현을 확인한다. 이는 아래의 수학적 증명을 대체하는 절차가 아니라 정상값·subnormal·반올림 경계에서 실제 구현이 의도한 연산을 수행하는지 확인하는 증거다.

## 4. label을 보존하는 출생 시각 경계

두 설정 A, B는 같은 w_i, E_i, λ_i,s를 갖고 출생 시각 b_Ai, b_Bi만 다르다고 하자. 두 출생이 모두 일어난 시각과 그때의 차이를

\[
t_i^*=\max(b_{Ai},b_{Bi}),\qquad
d_i=w_i\left(1-e^{-\Lambda_i|b_{Ai}-b_{Bi}|}\right)
\]

로 정의한다. 지수함수의 곱셈 법칙에서 t ≥ t_i*에 대해 정확히

\[
|n_{Ai}(t)-n_{Bi}(t)|=d_i e^{-\Lambda_i(t-t_i^*)}
\]

가 성립한다. 그러므로 최종 시각의 label별 차이 합

\[
D(T)=\sum_i d_i e^{-\Lambda_i(T-t_i^*)}
\]

는 |N_A(T) − N_B(T)|의 상한이다. 각 label의 차이 부호가 다르면 total N에서 상쇄될 수 있으므로 D와 실제 signed total difference를 구분한다. 원래 packet이 같다는 가정이 이 식의 핵심이다.

동일한 논리로 energy 차이는 Σ E_i d_i exp[−Λ_i(T−t_i*)], species event 차이는 Σ (λ_i,s/Λ_i) d_i exp[−Λ_i(T−t_i*)]로 제어할 수 있다. 이 두 가중 경계는 이론적 확장이다. 실제 결과에 별도 필드가 없다면 실행 완료된 관측량별 bound로 세지 않는다.

## 5. VigilODE affine prefix를 실제로 사용하는 방법

재사용한 코드는 VigilODE의 `research/all-dag-completion-20261018` branch SHA `ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406`에 있는 `affine_transport.rs`와 `directed.rs`다. 두 파일은 원본 그대로이고 SHA와 MIT license를 `rust/VENDOR_PROVENANCE.json` 및 `LICENSE-VigilODE`에 기록한다. 전체 RODAS5P solver를 도입한 것은 아니다. 본 모형에 필요한 공개 affine-map/prefix/workspace API를 실제 호출한다.

먼저 t_i*가 지난 pair만 포함하는 E(t)를 생각한다. birth event 사이에서 양의 sensitive hazard들의 최소값 Λ_min으로

\[
E_{j+1}\le g_j E_j+\delta_j,\quad
g_j=e^{-\Lambda_{\min}(t_{j+1}-t_j)},\quad
\delta_j=\sum_{t_i^*=t_{j+1}}d_i
\]

를 얻는다. Λ_i = 0이면 d_i = 0이므로 error recurrence에서는 제외하지만 원래 광자 관측량에는 남긴다. 관측 시각 T까지 마지막 감쇠 구간도 포함한다. **중간 E(t)는 두 출생이 모두 끝난 label의 차이 합이다. 아직 한쪽만 태어난 전체 population 차이를 뜻하지 않는다.** T에서 모든 pair가 포함되어 N 차이의 경계가 된다.

각 map은 x ↦ g x + δ다. 두 map의 합성은

\[
(g_2,\delta_2)\circ(g_1,\delta_1)
 = (g_2g_1,\;g_2\delta_1+\delta_2).
\]

g, δ가 비음수이므로 합성·적용은 단조다. leaf 계수와 연산을 위쪽으로 반올림하면 모든 prefix의 상한을 얻는다. 원본 `AffineErrorMap`, `parallel_error_prefix`, `AffinePrefixWorkspace`가 이 계산을 수행한다. 고정된 tree/order와 thread 1/2/4의 bit parity를 확인하지만, 이번 작은 계산에서 병렬 속도 향상을 주장하지 않는다.

### 관측된 느슨함을 줄이는 hazard grouping

첫 실제 계산에서 전역 Λ_min은 많은 node의 감쇠를 거의 무시하여 넓은 경계를 만들었다. 이에 **같은 정확한 species-rate tuple을 갖는 node끼리 그룹**으로 묶는다. 그룹 G에서는 Λ_i = Λ_G가 동일하므로

\[
E^G_{j+1}=e^{-\Lambda_G(t_{j+1}-t_j)}E^G_j
          +\sum_{i\in G:\,t_i^*=t_{j+1}}d_i
\]

가 정확한 실수 등식이다. 각 그룹의 birth event들과 최종 T tail에 같은 원래 VigilODE API를 적용하고, 정해진 그룹 순서로 최종 상한을 합한다. 정확한 실수에서 Σ_G E_G(T) = D(T)이므로 전역 최소 hazard로 인한 느슨함이 사라진다. 남는 차이는 enclosure와 합산의 반올림 폭이다.

node별 직접 계산 D_upper와 그룹 prefix의 upper는 같은 D를 각각 포함한다. **두 upper endpoint가 반드시 특정 순서로 정렬될 필요는 없다.** 서로 다른 outward 연산의 오차 폭 때문이다. 각각 유효함을 입증한 뒤 두 upper의 최소값을 쓰는 것은 유효하다. 임의 tolerance로 endpoint 순서를 강제하지 않는다.

grouping을 추가한 분석 replay는 동일한 보관 CSV와 동일한 4개 설정의 구현 보완 검증이다. 원래 결과는 `results/global_min_before_grouping/`에 남긴다. 이를 독립된 새 물리 사례 4개 또는 새 native trajectory로 중복 계산하지 않는다.

## 6. age marginal의 W1과 필요한 상관관계

label별 출생 시각 이동 비용을

\[
C=\sum_i w_i|b_{Ai}-b_{Bi}|
\]

라 하자. 1−e^-x ≤ x에서

\[
D(T)\le\sum_i w_i\Lambda_i|b_{Ai}-b_{Bi}|
e^{-\Lambda_i(T-t_i^*)}\le\Lambda_{\max} C
\]

를 얻는다. 이는 opacity와 age를 연결하는 label coupling을 유지하는 경계다.

단지 두 age marginal이 같다는 사실로는 이 비용을 0으로 치환할 수 없다. 예를 들어 w = (1,1), Λ = (0,1), T = 1이고 b_A = (0,1), b_B = (1,0)이면 age marginal과 hazard marginal이 각각 같다. 그런데 N_A = 2, N_B = 1+e^-1이다. W1(age marginal) = 0이지만 photon response 차이는 1−e^-1 > 0이다. joint age–hazard 상관관계가 다르기 때문이다. `verify.py`가 실제 Rust e^-1 enclosure를 이용해 이 반례를 검사한다.

이번 contiguous coarsening은 birth order를 유지한다. 정확히 그 단조 coupling에 대해서는 normalized age measures의 W1이 C/Σw_i와 같다. 일반적인 재배치나 opacity가 다른 다른 source reference로 이 등식을 확장할 수 없다. optical depth τ를 상태로 사용하면 e^-τ의 Lipschitz 상수는 1이지만, 그 τ 분포를 age marginal만으로 알 수 있는 것도 아니다.

## 7. age moment는 별도 경계가 필요하다

N 차이가 0이어도 passive node의 출생 시각이 바뀌면 M1과 M2는 변한다. 따라서 위의 D만으로 age-moment 차이를 인증하지 않는다. A_max가 두 설정의 모든 최종 age를 덮으면, 고정 Λ ≥ 0에 대해

\[
\left|\frac{d}{da}(a e^{-\Lambda a})\right|
 =|1-\Lambda a|e^{-\Lambda a}\le1,
\]

\[
\left|\frac{d}{da}(a^2 e^{-\Lambda a})\right|
 =a|2-\Lambda a|e^{-\Lambda a}\le2A_{\max}.
\]

평균값 정리로 |ΔM1| ≤ C, |ΔM2| ≤ 2 A_max C가 성립한다. 두 survivor mass가 N_min > 0 이상이면

\[
|\Delta(M1/N)|\le\frac{C+A_{\max}D}{N_{\min}}.
\]

이는 이번 이론 검토의 추가 결과다. 별도의 outward 수치 평가를 출력하지 않았다면 실행된 age-moment error certificate로 보고하지 않는다.

## 8. 왜 전체 VigilODE solver 교체까지 진행하지 않았는가

실제 공개 API와 최신 보관 CSV를 읽었다. REI가 사용하는 block-max/vector-atol, 출생 event 경계, 외부 callback의 상태·telemetry와 원 solver의 scalar-atol/WRMS·nonautonomous 차분·rollback 의미를 연결하려면 별도의 adapter와 검증이 필요하다. `StepResult.accepted`나 완료된 solver 행만으로 requested-grid 정확도 통과를 판정할 수 없다. 최신 VigilODE CSV에도 완료 상태와 accuracy gate의 차이를 보여 주는 사례가 있다.

이번 고정 scalar 수송은 exact solution과 양성 affine-map 구조가 있으므로 그 구조에 맞는 기존 코드를 재사용한다. `num-rational 0.4.2`, `num-bigint 0.4.6`, `num-traits 0.2.19`는 exact dyadic 계산에, `rayon 1.12.0`은 원 prefix 구현에 실제 사용한다. Cargo.lock과 22개 dependency source/license를 포함해 offline build가 가능하도록 한다. 다른 ODE solver 또는 MPFR package를 사용하지 않은 것은 아직 필요한 별도 기능이나 오차 계약이 없기 때문이다.

## 9. 증거와 admission 경계

- 입력: `inputs/`의 전체 CSV, model, 원 setup, export receipt. Source hashes와 실제 계수 독립 점검은 C9 receipt에 연결한다.
- 실행: `results/STUDY.json`, `RUN_COMMANDS.json`, stdout/stderr, `ANALYSIS.json`, `CASES.csv`, `BOUNDS.csv`.
- 검증: Rust tests, Decimal 100자리 exponential 및 label defect 재계산, C9의 독립 actual-data 재계산, 원본 vendor hashes와 thread parity.
- 연구 도구: SciSpace는 관련 primary literature 후보 탐색, Exa는 공식 Rust source/API 확인, Wolfram은 cutoff·pair identity·photon ledger의 별도 대수 확인에 사용했다. 이 도구들의 응답을 원 nonlinear gas bound의 근거로 삼지 않는다.
- 이전 과학 판정: 완료된 native age64 block-max와 spectral128 결과는 재사용한다. 새 native age32 비교는 READY, native time8/16/32는 표현 문제로 HOLD, 실제 nonlinear response bound는 NOT_ESTABLISHED다.

## 출처

1. REI 원본 source: <https://github.com/cosmosapjw-quantum/rei_bianchi/tree/35d9747a0bbedcafdb568467ce7c1e7a25f965b6>.
2. VigilODE affine source: <https://github.com/cosmosapjw-quantum/vigilode/blob/ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406/crates/rodas5p-integrators/src/affine_transport.rs>.
3. VigilODE directed arithmetic: <https://github.com/cosmosapjw-quantum/vigilode/blob/ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406/crates/rodas5p-core/src/directed.rs>.
4. num-rational BigRational API: <https://docs.rs/num-rational/0.4.2/num_rational/type.BigRational.html> 및 version-pinned Cargo/vendor source.
5. 실제 과학 결과의 근거는 위 source만이 아니라 이 디렉터리에 보관된 입력·실행·검토 receipt다. 소스만 존재하는 상태와 실제 실행 완료를 구분한다.
