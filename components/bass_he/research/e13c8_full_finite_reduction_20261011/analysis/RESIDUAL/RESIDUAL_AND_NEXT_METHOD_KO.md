# E13C8 잔여 폭의 원인과 다음 수치 방법 후보

## 이번 단계의 판단

이번 반환으로 2,331개 중량 경로가 모두 계산되었고, 기존 14개 비영 경로와
95개 정확한 영 경로를 합친 OFF 유한 대상의 34개 구간이 닫혔다. 다음 NCP
작업은 **0개**로 두는 것이 현재 근거에 맞다. 남은 상계의 원인을 보지 않은
전체 N2048 재계산이나 P80 재계산은 요청하지 않는다. 새로운 중량 작업의
필요성을 정하는 물리 정확도 조건은 아직 제시되거나 도출되지 않았다.

이 문서는 실제 오차를 측정한 결과가 아니다. 현재 저장된 **포함 구간의 폭**을
대수적으로 분해하고, 같은 고정 캡처 문제에서 다음 방법 후보의 수학적 근거를
정리한다. 폭이 작다는 사실만으로 물리 모형, 연속체, gas feedback, production,
receiver가 승인되지는 않는다. 최종 승격 판단은 별도 독립 검토의 대상이다.

자료: `ACTUAL/RESIDUAL_SUMMARY.json`, `ACTUAL/PATH_RESIDUALS.json`,
`ACTUAL/RESIDUAL_EXECUTION_RECEIPT.json`, `ACTUAL/SECOND_VARIATION_PARAMETERS.json`.

## 1. 실제 잔여 폭

이 분석은 새 계수 계산이나 ODE 적분 없이 저장된 2,345개 비영 경로를 읽었다.
기존 6개 경로의 원시 결과도 포함해 34개 전체 끝점이 E13C8의 원래 Fraction
합산 결과와 **정확히 일치**했다. 95개 영 경로의 기여는 정확히 0이다.
잔여 분해에 15.769초, Volterra 매개변수 집계에 4.539초가 걸렸다.

| 관측량 | 새 전체 폭 | 폭 / 절대량 중심 | 폭 / 캡처 보정 중심의 절댓값 |
|---|---:|---:|---:|
| 최종 photon stock P | 1.657292521990147877067e-18 | 1.070719079577143955123e-13 | 3.432911889863164840939e-6 |
| 총 heat H, eV | 9.214884781103738168091e-18 | 5.763469541119343255679e-13 | 3.540023958967017838960e-6 |
| 총 absorption A | 1.917651093696987418437e-18 | 6.569403897696643592831e-13 | 3.972228766815356645441e-6 |

중심은 포함 구간의 대수적 중점이다. true 해나 별도 정확 해를 뜻하지 않는다.
P의 캡처 보정 중심은 +4.827658195608997161810e-13이고,
H의 보정 중심은 −2.603057179249331916505e-12이다. 따라서 단순히 절대량에
대한 1e-13 수준의 폭만 말하면 실제 관심사일 수 있는 작은 보정량의 분해능을
과대평가할 수 있다. 보정량에 대한 위 수치도 확률적 오차 막대나 물리 허용오차가
아니다.

### 1.1 포함 반경의 정확한 양의 분해

각 segment의 저장된 출력 반경은 다음 네 부분으로 정확히 나누었다.

1. midpoint truncation radius와 그 후속 photon carry 기여;
2. 그 밖의 interval 평가·표현·중심 선택에서 생긴 수치 반경;
3. 저장된 coupling 상계와 그 후속 carry 기여;
4. 덧셈·seam 중심화·출력 끝점 표현의 남은 바깥쪽 반올림 여분.

| 관측량 | midpoint truncation | coupling 상계 | 그 밖의 수치·표현 |
|---|---:|---:|---:|
| P | 60.2578167210354% | 39.7421832789646% | 약 3.02e-43% |
| H | 65.9483598726485% | 34.0516401273515% | 약 2.42e-38% |
| A | 64.0568402078271% | 35.9431597921729% | 약 2.93e-43% |
| B | 63.9163648443997% | 36.0836351556003% | 약 6.07e-39% |
| Z | 94.3163632619690% | 5.68363673803103% | 약 1.22e-37% |

마지막 반올림 항은 이보다 더 작다. 이 집계는 현재 P60 구간의 표현 오차가
잔여 폭을 지배하지 않음을 직접 보여 준다. 추가 precision sweep을 요청할
구체적 위험이 없다.

**coupling 부분은 불가피한 실제 오차나 증명된 수렴 바닥이 아니다.** 같은
입력에서 N을 늘리면 절댓값 적분의 구간 상계도 더 날카로워지고, 앞 segment의
반경과 후보 중심이 바뀌면 뒤 segment의 S도 달라진다. 따라서 현재 비율을
N→∞의 비율로 외삽하지 않는다. 전체 반경에 보편적인 N^-2 법칙을 주장하지도
않는다. 이 표가 알려 주는 것은 현재 승인 후보에서 어떤 종류의 상계가 얼마나
큰가이다.

구현은 `analyze_saved_residual.py`의 `decompose()`에 있다. 저장된 local
midpoint radius를 numerical radius에서 빼고, |gain|을 이용해 기존 photon
반경의 네 부분을 다음 segment에 전파한다. 각 출력 반경과 마지막 전체 반폭의
합은 Fraction 산술로 정확히 맞아야 한다. 음수 분해항은 허용하지 않는다.
A/B/H total은 별도 total-integrand 출력 대신 기존 `common.new_metrics()`와
동일하게 species별 구간의 합으로 구성한다.

### 1.2 어디에 남아 있는가

| 경로군 | 경로 수 | P 잔여 폭 비중 | H 잔여 폭 비중 |
|---|---:|---:|---:|
| HI만 활성인 경로 | 700 | 87.9164645% | 57.5572537% |
| HI와 HeI 활성 경로 | 920 | 10.5073982% | 33.6787817% |
| HI·HeI·HeII 활성 경로 | 725 | 1.5761372% | 8.76396463% |

이 분류는 경로의 활성 species 수에 따른 분류이다. 경로 안에서 mask가 바뀌는
event 경로는 해당 경로의 최대 활성 species 수로 분류된다. species 자체의
heat 기여율과 혼동하지 않는다.

관측량을 실제 species별로 나누면 아래와 같다. 이 역시 값의 비율이 아니라
각 species 포함 구간의 **폭**이 총 폭에서 차지하는 비율이다.

| 관측량의 폭 | HI | HeI | HeII |
|---|---:|---:|---:|
| absorption A | 97.9093086% | 0.360899270% | 1.72979215% |
| absorbed energy B | 93.2829783% | 0.655386049% | 6.06163564% |
| heat H | 94.6746751% | 0.764580688% | 4.56074419% |

정확한 분수와 계산 정의는 `ACTUAL/SPECIES_WIDTHS.json`에 있다. Photon stock은
이런 species별 출력 분해를 정의하지 않았으므로 위 표에 넣지 않는다.

P 폭이 가장 큰 경로는 기존 N512 node101, node102, node106이다. 각각 전체 P
폭의 1.10059%, 1.09636%, 1.08397%를 차지한다. H 폭은 N512 node410,
node413, node414가 각각 약 0.4418%씩 가장 크다. 극소수 경로 하나가 전체
상계를 압도하는 상황은 아니다. 상위 64개만으로 P 폭의 24.8913%, H 폭의
10.4287%를 덮는다. P 폭의 50%에는 180개, H 폭의 50%에는 426개 경로가
필요하다. 향후 정확도 목표가 정해지면 전체 균일 재계산 대신 목표 관측량별
폭 감소 / 실측 비용 순서를 설계할 자료는 마련되었다.

## 2. 다음 짧은 방법 연구: signed Volterra correction

이 절은 기존 고정 캡처 계수에 대한 **직접 유도**이다. 새로운 second-variation
중심, quadrature enclosure, 전체 경로 결과는 아직 계산하지 않았다.

### 2.1 정의와 전제

한 segment에서 t∈[0,h], 고정 계수 Λ_f≥0, q_f, 캡처 초기 stock f_0를 둔다.
P_f는 이 고정 계수 ODE의 해이고, 실제로 비교하는 P는 동일한 캡처 gas 보간과
고정 branch를 사용하는 가변 계수 선형 ODE의 해이다.

\[
P_f'=q_f-\Lambda_fP_f,\quad
P'=q-\Lambda P,\quad
\delta=P-P_f,\quad
\Delta\Lambda=\Lambda-\Lambda_f,
\quad r=(q-q_f)-\Delta\Lambda P_f.
\]

기존 유한 대상에서 Λ≥0, P_f≥0이고 계수는 유한 segment에서 적분 가능하다.
고정 branch 안의 smooth formula를 그대로 사용한다. 물리적 threshold를 새로
선택하거나 e0를 clamp하지 않는다. 초기 보정은 δ(0)=c+e, |e|≤η로 표현한다.
다음 연산자를 정의한다.

\[
F(t)=e^{-\Lambda_ft},\qquad
(Kz)(t)=\int_0^tF(t-v)\Delta\Lambda(v)z(v)\,dv,
\qquad
\delta_1(t)=F(t)c+\int_0^tF(t-v)r(v)\,dv.
\]

variation-of-constants로 정확히

\[
\delta=\delta_1+Fe-K\delta.
\]

원래의 photon 포함 구간은 δ1을 중심으로 두고 Kδ를 대칭 상계로 감싼다.
그 부호를 계산한 다음 후보는

\[
\delta_{[2]}=\delta_1-K\delta_1.
\]

중괄호 [2]는 여기서 Neumann/Volterra의 다음 유한 항을 뜻한다. 전체 알고리즘의
N 수렴 차수를 명명하는 표현은 아니다. 정확한 잔여 관계는

\[
\delta-\delta_{[2]}=(I-K)Fe+K^2\delta.
\]

따라서 **초기 보정이 정확한 η=0인 경우에만** 잔여를 K²δ만으로 쓸 수 있다.
뒤 segment에서 현재 incoming uncertainty를 지우면 잘못된 포함 구간이 된다.

### 2.2 operator norm과 기존 저장 상계

Λ_f≥0이므로 F≤1이다. 따라서

\[
\|K\|_{\infty\to\infty}
\le \sup_{0\le t\le h}\int_0^tF(t-v)|\Delta\Lambda(v)|\,dv
\le D:=\int_0^h|\Delta\Lambda(v)|\,dv.
\]

여기서는 기존 `local.bounds.D_L.hi`를 D의 상계로 사용할 수 있다. 이 값은
whole-cell 계수 구간을 적분한 상계이다. 마지막 시각에만 정의된
`local.bounds.H_h.hi`를 sup operator norm으로 바꾸어 쓰지 않는다.

또한 δ'=r−Λδ와 Λ≥0으로

\[
\|\delta\|_\infty\le |c|+\eta+\int_0^h|r(v)|\,dv
\le |c|+\eta+B_r=:S.
\]

B_r는 기존 코드의 ∫(|Δq|+|ΔΛ|P_f) 상계이며, S 역시 기존 결과에 저장되어
있다. 따라서 η=0일 때 uniform 잔여 상계는 D²S이다. η가 0이 아닐 때는
(1+D)η+D²S가 안전한 uniform 상계다.

endpoint 상계는 더 날카롭다. 기존

\[
H_h\ge\int_0^hF(h-v)|\Delta\Lambda(v)|\,dv
\]

를 쓰면

\[
|\delta(h)-\delta_{[2]}(h)|
\le (F(h)+H_h)\eta+H_hDS.
\]

이 식은 second-variation 적분을 정확히 표현했을 때의 해석적 잔여이다. 실제
구현에서는 δ1, Kδ1의 구간 적분 오차, 표현 오차, 후보 중심화 오차를 추가한다.

### 2.3 species moments

M_i=∫w(t)λ_i(t)P(t)dt로 두고 w는 1, E, E−χ_i 중 하나이다. 기존 mask,
eV 단위, binding χ_i와 branch cutoff의 구분을 유지한다. 다음을 정의한다.

\[
Q_i(v)=\lambda_{fi}\int_v^h w(t)F(t-v)\,dt,\qquad
k_i(v)=w(v)\Delta\lambda_i(v)-Q_i(v)\Delta\Lambda(v),
\]

\[
G_i=\lambda_{fi}\int_0^h w(t)F(t)\,dt,
\quad T_i\ge\int_0^h|k_i(v)|\,dv.
\]

기존 first variation은

\[
M_{i,1}=\int_0^h w\,\Delta\lambda_iP_f\,dt
         +\int_0^h w\lambda_{fi}\delta_1\,dt.
\]

적분 순서를 바꾸면 정확한 moment 차이는

\[
M_i-M_{fi}=M_{i,1}+G_i e+\int_0^h k_i(v)\delta(v)\,dv.
\]

다음 부호 있는 항 M_i,2=∫k_iδ1을 계산하면

\[
|(M_i-M_{fi})-(M_{i,1}+M_{i,2})|
\le (|G_i|+T_i)\eta+T_iDS.
\]

T_i는 기존 코드의 effective/triangle 상계 중 적합한 최소값을 사용할 수 있다.
Z=∫EPdt의 경우 direct Δλ_i 항이 없고 k_Z(v)=−K_E(v)ΔΛ(v), T_Z=H_E이다.
QN과 QE는 source 적분이므로 이 photon coupling 잔여가 없다. 최종 photon
energy는 endpoint E(h)를 곱한다. Species total은 기존과 동일한 species별
구간 합으로 정의한다.

### 2.4 단위·부호·극한 검사

- t=s−a_j는 무차원 log-scale-factor 좌표이므로 D는 무차원이다. S는 photon
  stock 단위이고 H_hDS도 같은 단위다. Heat의 T_i는 eV 가중을 가지므로
  T_iDS는 기존 heat moment 단위와 맞는다.
- K의 정의에는 ΔΛ의 부호를 보존한다. Photon second variation의 부호는
  −Kδ1이다. Moment second variation은 +∫k_iδ1이다.
- ΔΛ=0이면 K=0이고 photon first variation은 초기 uncertainty를 제외하고
  정확하다. Moment Δλ_i가 개별적으로 남을 수 있으므로, 총 ΔΛ=0만으로 모든
  species의 second variation이 0이라고 주장하지 않는다.
- ΔΛ=0 및 모든 Δλ_i=0이면 coupling 보정들이 사라진다. δ0=0과 r=0이면
  δ≡0이다. 이는 기존 source-off exact-zero 경로와 양립한다.
- D<1은 위의 유한 2항 항등식을 유도하는 데 필요한 전제가 아니다. 유한
  D와 S만으로 상계가 성립한다. 관측된 작은 D는 다음 항의 실용적 가능성을
  평가하는 자료다.
- 다음 segment의 c와 η는 새 photon 출력과 기존 정확한 captured stitch를
  통해 전파해야 한다. signed energy seam ΔE·P도 기존과 같은 부호로 ledger에
  한 번만 반영해야 한다. 이 유도는 seam을 삭제하거나 gas를 새로 진화시키지 않는다.

## 3. 실제 매개변수와 아직 계산하지 않은 것

4,694개 비영 segment의 저장 D 상계는 다음과 같다.

| 통계 | D 상계 |
|---|---:|
| 최소 | 3.760750138766317322320e-11 |
| 중앙값 | 1.018367276279714471190e-8 |
| 95% 순서 통계 | 1.761809287022617094435e-7 |
| 최대 | 2.563619625862844502438e-7 |

기존 S와 T를 그대로 대입했을 때, 다음 formal direct coupling 항 TDS와 기존
TS의 가중합 비는 마지막 P segment에 대해 1.5216106602263e-7, heat species
segment 합에 대해 7.4884901928514e-8이다. 이 값은 **완전한 새 반경의 예측값이
아니다.** 이전 segment에서 전해지는 uncertainty, 새로운 δ2 적분 구간 폭,
수치 중심화, species/branch별 비용은 아직 계산되지 않았다. 기존 출력의 작은
coupling 상계에 추가로 작은 D를 곱할 수 있다는 방법 후보의 근거만 제공한다.

기존 파일에는 각 segment의 적분 합과 상계가 저장되어 있다. 이 정보만으로
δ1(v)의 모든 prefix 값이 재구성되지는 않는다. 따라서 저장된 endpoint 숫자에
D를 곱해 새 포함 구간으로 교체할 수 없다. 다음 실행 단계에서는 prefix
first-variation 함수와 signed second-variation 적분을 실제로 enclosure해야 한다.

다음 Chat 단계의 후보는 **같은 고정 캡처 문제에서 causal Volterra prefix
enclosure를 구현하고 소수 경로에서 검증하는 작업**이다. 우선 적분 순서를
이용해 O(N) 또는 그에 가까운 causal 구성을 설계한다. O(N²) 중첩 quadrature를
그대로 전체 경로에 제출하지 않는다. 작은 ordinary HI 경로와 다중 species
경로에서 기존 raw interval과의 overlap, 포함 증명, carry, signed seam, 비용을
확인한 뒤 전체 작업의 가치와 정확도 조건을 다시 판단한다. 실행할 경로·N/P·
시간 한도·승격 기준은 별도 계약에 먼저 고정한다.

이번 단계에서는 해당 후보의 새 적분이 **0회**, 새 second-variation 중심이
**NOT_RUN**, 새 포함 구간 승격이 **NOT_RUN**이다. NCP로 넘길 구현·작업량·
benefit/cost가 아직 확정되지 않았으므로 신규 heavy task는 0개가 적절하다.

## 증거 상태

| 항목 | 상태 | 한계 |
|---|---|---|
| 현재 폭과 네 부분의 합 | saved-data exact arithmetic PASS | 상계의 분해이며 실제 오차의 분해는 아님 |
| 모든 34 끝점의 기존 전체 합 재구성 | PASS | 독립 최종 승인과 별개 |
| Volterra 항등식과 norm/moment 상계 | 직접 유도, 독립 검토 대기 | 고정 캡처 계수와 기존 포함 전제에 한정 |
| 저장 D/S/T 매개변수 집계 | saved-data exact arithmetic PASS | 새 second-variation 적분을 대신하지 않음 |
| 새 numerical candidate | NOT_RUN | 다음 별도 계약의 경량 prototype 대상 |
| 추가 NCP heavy task | 0개 | 실제 유용성·비용·필수성이 정해지면 다시 판단 |
| physical/continuum/production/receiver | HOLD | 이번 finite 폭 감소로 해소되지 않음 |
