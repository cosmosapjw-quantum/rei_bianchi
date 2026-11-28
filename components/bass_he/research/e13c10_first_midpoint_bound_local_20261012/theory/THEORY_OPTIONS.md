# E13C10: 첫 변분 적분의 부호 있는 곡률 나머지

작성 역할: `AUTHOR_THEORY_CONTRIBUTOR`. 이 문서는 후보 생성과 검증 설계에 기여한 이론 산출물이며 독립 최종 판정이 아니다. E13C9의 완료된 수치 작업이나 전체 모집단 계산은 재실행하지 않았다.

## 1. 결론과 변경 범위

가장 작은 유효 변경은 **기존 midpoint 값과 기존 Jet2를 그대로 사용하면서, 각 cell의 두 번째 도함수 구간에서 부호를 버리지 않는 것**이다. 다음 구간은 같은 첫 변분 적분을 포함한다.

\[
I_k=h\int_0^1 F_k(x)\,dx
\in Q_{k,N}
 +\sum_{j=0}^{N-1}\frac{h}{24N^3}\,\mathcal D_{k,j},
\qquad
Q_{k,N}=\sum_j\frac hN F_k(m_j),
\]

여기서 \(\mathcal D_{k,j}\)는 cell 전체에서 \(F_k''(x)\)를 포함하는 **부호 있는** 구간이다. `Jet2.d2`는 정규화 좌표 \(x\)에 대한 실제 두 번째 도함수이며 Taylor 계수 \(F''/2\)가 아니다. 따라서 분모는 24이고 앞의 길이 인자는 \(h\)다. 코드 내부의 정규화 좌표 미분에 이미 들어간 \(h^2\)를 다시 곱하지 않는다. [S1, S2]

기존 구현은 같은 \(\mathcal D_{k,j}\)에서 \(M_{k,j}=\sup|\mathcal D_{k,j}|\)만 남겨

\[
I_k\in Q_{k,N}
 +\left[-\sum_j\frac{hM_{k,j}}{24N^3},
         +\sum_j\frac{hM_{k,j}}{24N^3}\right]
\]

를 사용한다. 새 식은 이 절댓값화에서 없어진 곡률의 부호와 cell별 범위를 보존한다. **새로운 3차·4차 도함수 가정이 필요하지 않다.** 같은 \(N\)에서 coefficient 호출 수는 기존과 같이 whole-cell Jet2 \(N\)회와 midpoint 값 \(N\)회다. [S3, 직접 유도 D1]

새로운 \(N=32\) 결과를 기존 \(N=512\) 또는 1024 결과와 비교하는 경우에는 아래의 같은 격자 포함 정리를 적용할 수 없다. 실제 raw 구간 비교가 필요하다. 다른 격자 사이의 포함을 보장하지 않는 정확한 다항식 반례를 실제 실행해 보존했다. [T1]

## 2. 고정된 수학적 대상과 전제

원래 `integrands(c, x)`가 반환하는 17개 첫 변분 함수 \(F_k\)를 그대로 사용한다. `P1`, 에너지 stock, source number/energy, 세 종별 absorption/energy/heat, 그리고 해당 total을 새로 정의하거나 서로 대체하지 않는다. 종별 heat weight와 total의 합산 위치도 원래 식을 보존한다. [S1]

필요한 전제는 다음과 같다.

1. 한 captured segment에서 \(h>0\), \(x\in[0,1]\)이고 \(F_k\in C^2([0,1])\)다.
2. \(\mathcal D_{k,j}\)는 해당 cell의 모든 정확한 \(F_k''\) 값을 포함한다. 입력 상수는 captured binary64의 exact realification이며, IV/Jet2 식의 각 연산은 기존 directed arithmetic 계약을 따른다.
3. source flag와 species mask의 불연속은 이미 segment 경계에 놓인다. 다른 event의 양쪽을 하나의 \(C^2\) cell로 합치지 않는다.
4. 로그, 제곱근, 나눗셈 및 gas positivity 조건은 기존 coefficient/domain 검사로 통과한 영역에서만 사용한다.

`Coefficients.__call__`, `sigma`, `integrands`, `Jet2`를 실제 읽어 확인한 결과, 이 변경은 기존 midpoint 규칙이 이미 필요로 했던 동일한 정칙성과 domain 조건만 사용한다. 기존 코드의 계약을 넘어 새로운 물리 model의 정칙성을 주장하지 않는다. [S1, S2]

## 3. D1 — midpoint 오차의 정확한 Peano 표현

한 cell을 \([a,b]\), 길이를 \(\Delta=b-a\), midpoint를 \(m=(a+b)/2\)라고 하자. \(f\in C^2([a,b])\)에 대해 Taylor의 적분형 나머지를 \(a\)에서 쓰면

\[
f(x)=f(a)+f'(a)(x-a)+\int_a^b(x-s)_+f''(s)\,ds.
\]

선형 functional \(L(f)=\int_a^b f(x)dx-\Delta f(m)\)는 상수와 일차식을 소거한다. 적분 순서를 바꾸면

\[
L(f)=\int_a^b K_M(s)f''(s)\,ds,
\quad
K_M(s)=\frac{(b-s)^2}{2}-\Delta(m-s)_+.
\]

이를 두 반구간에서 정리하면

\[
K_M(s)=
\begin{cases}
\frac{(s-a)^2}{2}, & a\le s\le m,\\
\frac{(b-s)^2}{2}, & m\le s\le b.
\end{cases}
\]

따라서 \(K_M\ge0\)이고

\[
\int_a^bK_M(s)\,ds
=2\int_0^{\Delta/2}\frac{t^2}{2}\,dt
=\frac{\Delta^3}{24}.
\]

이제 모든 \(s\in[a,b]\)에서 \(\ell\le f''(s)\le u\)이면 양의 kernel에 대한 적분의 순서 보존성으로

\[
\frac{\Delta^3}{24}\ell
\le \int_a^b f(x)dx-\Delta f(m)
\le \frac{\Delta^3}{24}u.
\]

이 식에 \(h>0\)를 곱하고 cell들을 더하면 1절의 후보가 된다. 이 유도에는 어떤 대표 \(\xi\)를 수치적으로 선택하거나, \(f''\)가 상수·양수·단조라고 가정하는 단계가 없다. \(f''\)가 cell 내부에서 부호를 바꾸어도 그대로 유효하다. 이 문서의 정리는 직접 유도이며 문헌의 고차 quadrature 공식을 불러온 것이 아니다.

### 같은 격자의 포함과 개선 조건

\(M=\max(|\ell|,|u|)\)이면 항상 \([\ell,u]\subseteq[-M,M]\)다. 양의 배율과 구간 합은 포함을 보존하므로, **같은 midpoint 값·같은 cell·같은 도함수 enclosure를 사용하는 정확한 구간 연산**에서는 새 첫 적분 구간이 기존 대칭 구간에 포함된다. 교집합을 계산하는 정리가 아니라 새 계산식 자체에 대한 정리다.

원래 directed 구현에서도 동일한 연산 결합 순서를 사용하면 이 단조성을 유지할 수 있다. 각 부호 있는 항의 양쪽 끝은 해당 양의 radius 항의 외측 상한에 의해 제한된다. 다만 캐시의 midpoint 합을 다르게 재결합하거나, 전체 경로에서 새 중심·radius로 재중심화하고 서로 다른 항들을 더하면 마지막 자리까지의 raw 포함은 이 국소 정리만으로 끝나지 않는다. 후보의 실제 입장 기준은 계산된 원시 구간에 직접 적용해야 한다. [S2, S3, S4]

곡률이 양수로 좁게 둘러싸이면 기존 구간이 포함하던 불필요한 음의 remainder가 사라진다. 음의 곡률에서는 반대가 일어난다. 곡률 구간이 \([-M,M]\) 자체이면 그 cell에서 개선이 없을 수도 있다. 모든 cell이 균일한 양의 곡률을 가질 필요는 없다. 각 cell의 곡률 부호가 달라도 정확히 그 구간들을 더한다.

## 4. 이 규칙이 보장하지 않는 것

### 서로 다른 N의 포함

coarse signed curvature 구간이 fine symmetric midpoint 구간보다 좁다는 보장은 없다. 정확한 예는 \(f(x)=x^4\), \(h=1\), domain \([0,1]\)이다. \(N=32\)의 새 raw 구간은 \(N=512\)의 기존 raw 구간에 포함되지 않는다. 두 구간은 모두 정확한 적분 \(1/5\)를 포함한다. exact Fraction 실행 결과의 양 끝은 `EXACT_POLYNOMIAL_CONTROLS.json`의 `cross_resolution_counterexample`에 있다. [T1]

그러므로 N32는 비용을 줄일 가능성을 판별하는 실제 새 local 계산이다. 첫 실패가 있으면 그 출력과 원인을 보존하고 해당 경로나 해상도에만 필요한 후속 계산을 수행한다. 실패 구간을 기존 구간과 교차하거나 기존 구간을 대신 반환하면 이 비교는 무의미해진다.

### C²만으로 보편적인 N^-3 차수를 주장할 수 없음

정확한 구간 모델에서 새 quadrature remainder 구간 폭은

\[
W_N=\frac{h}{24N^3}\sum_j
      \operatorname{width}(\mathcal D_j).
\]

whole-cell curvature 구간이 정확한 함수 범위에 수렴하고 그 최대 폭을 \(\omega_N\)라 하면

\[
W_N\le\frac{h\,\omega_N}{24N^2}.
\]

단지 \(C^2\)라는 전제는 \(f''\)의 연속성을 주며 보편적 Lipschitz 상수나 \(\omega_N=O(1/N)\)를 주지 않는다. 이상적인 수렴 enclosure에서 \(\omega_N\to0\)이면 \(o(N^{-2})\)까지는 따라오지만, \(O(N^{-3})\)는 별도로 \(\operatorname{width}(\mathcal D_j)\le C/N\) 같은 조건이 필요하다. 실제 source 식은 양의 domain 안에서 매끄러운 elementary composition이므로 이런 거동이 나타날 수 있다는 예상은 합리적이나, 그 예상은 모든 segment에 대한 검증된 차수 상수를 대신하지 않는다.

고정 P60에서는 중간 IV 과대폭과 반올림 누적이 남는다. midpoint 합의 연산 오차도 위의 이상적인 remainder 폭과 별개다. N32→64의 폭 감소율은 그 실행에서 얻은 수치 증거이며 보편적 order 정리가 아니다. Volterra의 `[2]` 표기 역시 quadrature 차수를 뜻하지 않는다. [S4, S5]

### 첫 적분의 포함과 전체 path의 포함은 별개

새 첫 적분은 다음 segment로 전달할 중심과 radius를 바꾼다. E13C9의 causal prefix와 signed second correction은 새 중심에서 다시 계산해야 한다. 같은 정확한 해를 포함하는 두 계산식이라도 center/radius 재구성, rectangle dependency, 부동소수점 결합, seam 전파가 서로 다르면 모든 raw path metric의 포함이 자동으로 따라오지 않는다. 최종 34개 metric의 raw 입장 검사는 따로 필요하다. [S3, S4]

## 5. 구현 권고와 기존 증거 재사용

새 code는 original `integrands`와 `Jet2`를 import하고 다음 한 줄에 대응하는 계산을 추가하면 된다.

```python
signed_curvature[k] += c.h * jet.d2 / (24 * N ** 3)
signed[k] = midpoint[k] + signed_curvature[k]
```

실제 코드는 dictionary 초기화, dyadic partition, directed IV 연산과 source/input 검증을 포함해야 한다. Python의 ambient Decimal 연산이나 binary64 midpoint로 바꾸지 않는다. N은 positive dyadic 정수로 제한하면 기존의 정확한 partition 표현을 유지할 수 있다. 각 cell의 signed curvature interval, midpoint sum, 합산 curvature remainder, `supabs` 비교용 radius, coefficient 호출 수를 보존하면 reviewer가 구현과 유도를 연결할 수 있다. 비교용 radius를 실제 결과를 교정하는 데 사용하지 않는다.

E13C9의 원래 fine-grid `local.bounds`는 incoming correction과 무관한 \(D\), \(B_r\), moment kernel norm의 유효한 enclosure다. 따라서 동일한 source·segment input·P·kernel을 확인한 뒤 이를 새 first integral과 함께 재사용할 수 있다. 더 거친 N32 직사각형으로 그 bound들을 대체해야 할 수학적 의무가 없다. 오히려 원래 bound를 유지하면 바뀐 첫 적분 방법의 효과를 분리하고 이미 유효한 더 좁은 norm bound를 보존한다. [S1, S3, S4]

재사용할 수 없는 것은 옛 incoming \(c,\eta\)에 의존한 \(S=|c|+\eta+B_r\), old outgoing radius, old signed second-correction 값이다. 새 carry를 사용하여 기존 E13C9의 `prefix_and_correction`와 `remainder_bounds`를 호출한다. M은 기존 선택값을 유지하는 것이 이 국소 판별의 자연스러운 시작이다. 바뀐 first quadrature를 새로 계산하는 것은 완료된 옛 quadrature를 검증 명목으로 반복하는 것과 다른 의존성의 계산이다. [S4, S5]

## 6. 실질적인 대안 비교

| 후보 | 필요한 remainder 정보 | coefficient 평가량의 구조 | 이 루프에서의 판단 |
|---|---|---|---|
| 부호 있는 midpoint curvature | 기존 whole-cell \(f''\) 구간, 양의 kernel | \(N\) Jet2 + \(N\) midpoint = \(2N\) | 최소 변경. 먼저 실제 local 판별을 수행할 후보 |
| 기존 symmetric midpoint의 격자 증가 | 기존 \(\sup|f''|\) | N 증가에 비례 | 일반적 대안이지만 완료된 fine-grid 작업을 다시 할 이유는 없음 |
| 부호 있는 trapezoid curvature | 기존 \(f''\) 구간, 음의 kernel | \(N\) Jet2 + \(N+1\) endpoint 값 | remainder 질량이 midpoint의 두 배. endpoint 재사용 이점이 실제 workload에 있는 경우에만 추가 검토 |
| C² Peano kernel로 검증한 Simpson | 기존 \(f''\) 구간과 kernel의 양·음 부분 | \(N\) Jet2 + \(N\) midpoint + \(N+1\) endpoint = \(3N+1\) | 4차 도함수 없이도 유효한 다른 후보. 추가 값·assembly·control 비용을 정당화할 남은 문제가 있을 때 검토 |
| cell 내부 곡률 범위의 추가 분할 | 같은 C², 더 작은 범위의 Jet2 | 분할한 만큼 whole-cell jet 추가 | dependency 폭이 지배하는 경우 유용. 현재 결과가 요구하기 전에는 추가하지 않음 |
| 검증된 Jet4 또는 더 높은 derivative를 이용한 고차 규칙 | 새 고차 derivative 계약과 연산 구현 | 별도 구현·검증·비용 측정 필요 | 기존 Jet2만으로 정당화할 수 없음. 현재 최소 목적의 필수 변경이 아님 |

### D2 — trapezoid 대안의 부호

\(Q_T=\Delta(f(a)+f(b))/2\)에 대해

\[
\int_a^b f-Q_T
=-\frac12\int_a^b(s-a)(b-s)f''(s)\,ds.
\]

kernel은 음수이며 절댓값 적분은 \(\Delta^3/12\)이다. 따라서 signed enclosure는 \(-\Delta^3[\ell,u]/12\)다. same-cell 곡률 구간으로 얻는 폭은 midpoint의 두 배다. 규칙 중심이 다르므로 이것만으로 어떤 실제 전체 경로 결과가 더 좁은지 단정하지 않는다.

### D3 — 4차 도함수가 필요 없는 C² Simpson 대안

표준 4차 도함수 Simpson remainder를 가정하는 것과 별도로, 2차 Peano kernel 자체를 이용할 수 있다. 정규화한 한 cell \([0,1]\)에서

\[
Q_S=\frac{f(0)+4f(1/2)+f(1)}6,
\quad
K_S(t)=
\begin{cases}
t(3t-1)/6,&0\le t\le1/2,\\
(1-t)(2-3t)/6,&1/2\le t\le1.
\end{cases}
\]

이 kernel은 부호를 바꾸며 \(\int K_S=0\)이고

\[
\int(K_S)_+=\frac1{162},\qquad
\int(K_S)_-=-\frac1{162}.
\]

따라서 \(f''\in[\ell,u]\)이면 길이 \(\Delta\)인 cell에서

\[
\int f-Q_S
\in\left[-\frac{\Delta^3}{162}(u-\ell),
           +\frac{\Delta^3}{162}(u-\ell)\right].
\]

같은 curvature range를 사용했을 때 remainder 구간 폭은 \(\Delta^3(u-\ell)/81\)이며 signed midpoint 폭의 \(8/27\)이다. 이 식은 C² kernel bound이고, 4차·5차 정확도 보증을 뜻하지 않는다. 여기서는 이 대안의 정확한 kernel 질량과 다항식 identity까지만 계산했다. 실제 captured 코드로 구현·실행·승격하지 않았다. [T1]

## 7. 경계 사례와 판별 기준

- 상수·일차 함수: \(f''=0\)이면 midpoint가 정확하다. 새 remainder는 정확히 0이어야 한다. 실제 directed 연산에서 함수 평가의 반올림 구간은 별도다.
- 이차 함수: \(f''\)가 일정하면 새 curvature correction이 정확한 midpoint 오차를 재현한다. 양·음 곡률을 각각 확인해야 부호 오류를 잡을 수 있다.
- 곡률 부호 변화: \((x-1/2)^3\)의 한 cell은 대칭 곡률 구간을 가지므로 signed 규칙이 symmetric 규칙보다 좁아지지 않을 수 있다. 이것은 정리의 실패가 아니다.
- stationary curvature: \((x-1/2)^4\)에서는 \(f''\)의 최솟값이 endpoint가 아니라 내부에 있다. whole-cell enclosure를 endpoint 샘플의 최소·최대로 대체하지 않는다.
- source off, exact-zero prefix, \(\Lambda_f=0\): 기존 exact-zero branch와 `response_j`의 zero-rate 분기를 유지한다. 나눗셈의 singular limit를 새 식에서 만들지 않는다.
- total coupling은 0이지만 개별 종 coupling이 0이 아닌 경우: 종별 첫 적분을 유지한다. total이 0이라는 이유로 species moment를 지우지 않는다.
- incoming center/radius: 첫 forcing integral은 source-only로 유지하고 \(G_kc\), incoming uncertainty, second correction과 tail은 새 carry로 계산한다.
- source/mask event와 microscopic branch discrepancy: 기존 segment와 seam을 유지한다. event를 통과해 곡률 정리를 적용하거나 discrepancy를 clamp하지 않는다. [S1–S5]

실제 입장 판단에는 원래 정확한 number/energy/heat ledger의 0 포함, 각 경로의 모든 raw metric 포함·비증가, 실제 자원 영수증, 그리고 비기여 독립 decision reviewer가 필요하다. 이 이론 문서와 exact polynomial control은 그 판단의 일부 근거이며 전체 물리 검증을 대체하지 않는다.

## 8. 실제 수행과 근거 상태

`exact_polynomial_controls.py`를 한 번 실행했다. 8개 다항식 × 5개 격자에서 40개 enclosure 행을 만들고, exact integral 포함, 같은 격자 nesting, 이차 exactness, Peano identity와 kernel mass, 다른 격자 반례를 **Fraction 정확 산술로 207개 확인**했다. 실패는 0개, 측정 경과 시간은 0.04056861999561079 s였다. captured coefficient 호출, 기존 과학 실행 반복, NCP invocation은 모두 0이다. [T1]

| 주장 | 상태 | 범위 |
|---|---|---|
| signed midpoint curvature 포함 정리 | `derived` | C² cell + valid derivative range + outward evaluation |
| 같은 격자의 이상적 구간 포함 | `derived` | 동일 midpoint·cell·curvature ranges |
| 부호·상수/일차/이차·Peano kernel exact control | `numerically_checked`, `implementation_verified` | 본 문서의 별도 exact Fraction toy 코드 |
| 기존 source가 필요한 Jet2와 정규화 규약을 제공함 | `implementation_verified` (interface source inspection) | 아래 pin으로 실제 읽은 immutable 코드 |
| N32 실제 captured 경로가 fine-grid baseline에 입장함 | `NOT_RUN_BY_THIS_AGENT` | 주 실행자의 별도 새 실행과 독립 판정에 의존 |
| Simpson C² 대안의 kernel 질량과 다항식 identity | `derived`, `numerically_checked` | 후보 대안의 이론 수준, captured 구현 없음 |
| 전체 모집단·물리·continuum·production·receiver | `HOLD` / `NOT_RUN` | 이 문서로 claim ceiling을 올리지 않음 |

## 9. 출처와 식별자

S1–S3의 경로 기준은 복구된 `BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1`, S4–S6의 경로 기준은 복구된 `BASS_HE_E13C9_SIGNED_VOLTERRA_LOCAL_20261012_v1`다. 이름/해시는 과학적 정리의 대체물이 아니며 실제로 읽은 source의 정체성을 고정한다.

| ID | 실제 읽은 source / 적용 부분 | bytes | SHA-256 |
|---|---|---:|---|
| S1 | `code/vendor/local_enclosure.py`: `Coefficients`, `integrands`, `solve_control` | 20261 | `fade8983b7db8974c479ac4473424b7d572e8f7a0f09c042669fb3c40c32e370` |
| S2 | `code/vendor/directed_interval.py`: `IV`, `Jet2`, `value`, `response_j` | 9103 | `ce4a44b11d1c0a3a5c52861033fa817a587bca9a5b852fab48329213b9a732e5` |
| S3 | `code/vendor/path_enclosure.py`: `local_integrals`, gains, remainder, segment 및 carry 연결 | 21111 | `c424c8b980ece05618e427e4373f13a41fe7b4d02a8ddd4a0b3fa7da30109d73` |
| S4 | `code/signed_volterra.py`: signed correction와 새 incoming, 동일 midpoint 재사용 조건 | 12570 | `5f20e1b5b0f4936f7bd443d19c7181fd2c7de9de762fe2fa3e9be98f8963cfc5` |
| S5 | `SCIENTIFIC_CONTRACT.md`: 고정 captured OFF 의미와 raw admission 조건 | 6232 | `6e19a3f37520f30309ef18db1353f61c1affd8711a2797f42452dae4a2ecbc83` |
| S6 | `NEXT_DAG.json`: 미완료 E13C10 목적과 derivative 제한 | 1722 | `d5e413144f389b3cea4e674a50e2cefe43b51d2debce8881c0fd9738f3261571` |
| T1 | 본 디렉터리 `exact_polynomial_controls.py`, `EXACT_POLYNOMIAL_CONTROLS.json` | 영수증 참고 | script SHA는 JSON의 `source_sha256`에 고정 |

연구 하네스 `PROJECT_INSTRUCTIONS.md`, 현재 state template, `04_hypothesis_space.md`, `06_physics_math_validation.md`와 복구된 `references/REPO_AGENTS.md`도 실제 읽었다. 본 작업은 읽기, 직접 유도, 짧은 exact toy 계산 및 신규 문서 작성에 한정했으며 original source를 변경하지 않았다.
