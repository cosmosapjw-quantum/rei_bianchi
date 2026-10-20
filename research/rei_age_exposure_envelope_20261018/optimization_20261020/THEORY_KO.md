# 정확도를 유지하는 age-response 계산 최적화

## 연구 대상과 완료 기준

이 연구의 대상은 `vigilode_age_transport_20261019/rust`의 고정 계수 source-age 계산이다. 기준은 PR199의 `58dc257d1402daa3d0f64786279e13cd72bfb0c7`이며, 원래 64 source packets, 57,344 nodes와 birth clocks 8/16/32/64를 그대로 사용한다. `inputs/nodes.csv`의 SHA256은 `b83f5c07d83d9a6a04ca8120e8fcbe11dab67efb41cbcdd000e4f7eb6a25c17a`다. 물리적 정의와 기존 경계의 증명은 `../vigilode_age_transport_20261019/THEORY_KO.md`를 재사용한다.

이번 목표는 같은 입력의 같은 경계 계산을 더 적은 연산과 적절한 병렬 작업으로 수행하는 것이다. source label, 출생 시각, species별 계수, 광자수/H, 에너지 eV/H, 고유시간 s, 초기 inventory를 고정한다. 기존의 nonlinear native age64 reference나 B1 binary는 변경 대상이 아니다. 고정 계수 모형에 관한 최적화는 native age/time 수렴 상태를 바꾸지 않는다. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`를 유지한다.

완료 조건은 (i) 변환의 수학적 동등성, (ii) 같은 입력에서 출력과 경계의 보존, (iii) 같은 실행 환경에서 실제 비용 비교, (iv) 독립 구현 검토, (v) 복원 가능한 소스·실행 명령·결과의 게시다. 이번 변환은 같은 유리수 다항식과 같은 부동소수 연산 순서를 의도적으로 유지하므로 binary64 endpoint bit 일치가 적절한 판별 기준이다. 이는 임의의 서로 다른 수치방법에 적용하는 일반적인 byte-equality 요구가 아니다.

## 1. 실제로 비용을 줄일 수 있는 연산

기준 코드의 attenuation은

\[
 \tau=\left(\sum_s\lambda_s\right)(t_2-t_1),\qquad E=e^{-\tau}
\]

를 사용한다. 내보낸 binary64 계수와 시각을 정확한 dyadic 유리수로 해석한 뒤 계산한다. 기준 `Cache::survival`은 `(rate_id, t_2.to_bits(), t_1.to_bits())`를 key로 삼는다. 이 입력에서는 1,113 rate tuples와 53,408개의 cache evaluation이 있다. 같은 mass와 rate를 사용한다는 사실만으로 시각이 다른 attenuation을 재사용할 수는 없다.

원래 exponential kernel은 reduced argument의 Taylor 항마다 `BigRational` 곱셈·나눗셈·덧셈을 수행한다. `num-rational`의 정규화 비용을 매 항에서 지불하는 구조다. 두 번째 후보는 반복되는 정확한 age interval 구성과 cache lookup 앞의 독립 계산이다. 세 번째 후보는 동일한 입력·동일한 prefix 결과에 대한 exact rational 검산의 반복이다. 이 세 후보는 물리 모형이나 허용오차를 바꾸지 않고 구별하여 측정할 수 있다.

## 2. 유리수 Taylor를 정수 다항식으로 계산

기존 범위 축소를 그대로 사용한다. \(0<\tau<752\)이면 \(r=\tau/2^h\le1/2\)가 될 때까지 정확히 2로 나눈다. \(r=p/q\), \(p\ge0\), \(q>0\)로 쓰고

\[
S_j(r)=\sum_{k=0}^j\frac{(-r)^k}{k!}
\]

를 정의한다. 다음 정수 recurrence를 사용한다.

\[
 D_0=P_0=N_0=1,
\]
\[
 D_j=jqD_{j-1},\quad P_j=(-p)P_{j-1},\quad
 N_j=jqN_{j-1}+P_j.
\]

첫 두 식으로 \(D_j=j!q^j\), \(P_j=(-p)^j\)다. 세 번째 식을 \(D_j\)로 나누면

\[
\frac{N_j}{D_j}=\frac{N_{j-1}}{D_{j-1}}+
\frac{(-p)^j}{j!q^j}=S_{j-1}(r)+\frac{(-r)^j}{j!}=S_j(r).
\]

따라서 모든 차수에서 원래 유리수 Taylor와 정확히 같다. `BigInt`로 정수 recurrence를 계산하고 18차와 19차에서만 `BigRational::new`를 호출한다. 정수 overflow의 크기 제한을 새로 만들지 않으며, 큰 분자·분모의 메모리/연산 비용은 실행 비용으로 측정한다. 입력이 dyadic이라는 성질에만 의존하지 않으므로 일반적인 양의 유리수 argument에도 같은 증명이 적용된다.

### 경계의 보존

\(0\le r\le1/2\)에서 항 크기 비율은 \(r/(j+1)\le1/2\)다. 교대급수의 경계로

\[
S_{19}(r)\le e^{-r}\le S_{18}(r)
\]

이며 두 다항식 사이의 최대 간격은

\[
S_{18}-S_{19}=\frac{r^{19}}{19!}
\le\frac1{2^{19}19!}
=\frac1{63777066403145711616000}
\approx1.56796173985\times10^{-23}.
\]

기존 `rational_interval`은 변환된 f64 후보의 정확한 값을 원 유리수와 비교하고 필요한 방향으로 인접 수까지 조정한다. 다항식의 정확한 값이 같고 변환 함수도 같으므로 변환 endpoint가 같다. 그 뒤 동일 횟수의 VigilODE directed squaring을 수행하므로 최종 interval의 endpoint도 같다. 근사 차수나 오차 허용치를 낮춰 속도를 얻는 변환이 아니다.

\(\tau=0\)의 `[1,1]` 분기와 \(\tau\ge752\)의 `[0,2^{-1074}]` 분기를 보존한다. 후자는 \(e^{0.7}>1+0.7+0.7^2/2+0.7^3/6=12013/6000>2\), 따라서 \(1074\log2<751.8<752\)라는 기존 증명을 재사용한다. 중앙값이 underflow하더라도 양의 upper endpoint를 유지한다.

Wolfram Language에서 1–19차의 recurrence와 직접 Taylor 합의 symbolic difference가 모두 0임을 확인했다. 이는 위의 귀납 증명을 보조하는 유한 차수 CAS 검산이다. 일반 유리수·halving 경계·subnormal·752 전후와 실제 cache argument는 구현 검증에서 비교한다.

## 3. 독립 cache 계산의 병렬화

한 miss key \(k\)의 값은 고정된 rate와 두 시각으로 정해지는 순수 함수 \(F(k)\)다. 다른 key의 결과에 의존하지 않는다. 요청 key를 중복 제거한 뒤 indexed parallel map으로 계산하고, 결과를 정해진 index에 모아 cache에 넣을 수 있다.

수학적 연산의 순서를 바꾸는 부분은 없다. 각 key 내부에서는 같은 exact tau, 같은 Taylor 다항식, 같은 directed squaring을 사용한다. 이후 각 node가 읽는 cache 값이 같으면 기존 node loop와 순차 directed fold에 대한 귀납으로 모든 누적량이 같다. `HashMap`의 내부 배치는 그 map을 순회해 합산하지 않는 한 수치 순서를 결정하지 않는다. 실제 구현은 cache request와 insertion의 순서를 명시하고, 최종 합산은 원래 node/group 순서를 유지해야 한다.

같은 clock의 age interval \(T-b\)도 node별로 재계산할 필요가 없다. 해당 interval을 clock당 한 번 만들고 같은 값을 읽는 것은 참조 투명성을 이용한 공통 부분식 재사용이다. 계수·질량을 다른 순서로 묶어 더하는 group aggregation과는 다른 변환이다.

병렬 비용은 대략

\[
T(P)=T_{\rm serial}+T_{\rm jobs}/P+T_{\rm schedule}(P)+T_{\rm memory}(P)
\]

로 나뉜다. 이 식은 측정치를 대체하지 않는다. thread 수, 실제 CPU quota, 입력·빌드 identity, process별 wall/CPU/peak RSS를 함께 기록한다. cache staging은 동시에 보관하는 key와 결과를 늘릴 수 있으므로 속도 향상과 메모리 감소를 같은 말로 쓰지 않는다.

## 4. 같은 검산 결과를 재사용하는 조건

각 group의 leaf maps \((g_j,d_j)\)와 초기값 \(e_0\)를 고정하면 검산용 정확한 유리수 recurrence

\[
Q_0=e_0,\qquad Q_{j+1}=g_jQ_j+d_j
\]

는 실행 thread 수에 의존하지 않는다. 한 prefix 실행의 모든 \(R_j\)에 대해 \(R_j\ge Q_j\)를 검산하고, 다른 실행의 **모든 prefix endpoint bits**가 일치함을 직접 확인하면 같은 부등식이 다른 실행에도 성립한다. 최종 radius 하나만의 일치로 중간 prefix 전체의 검산을 대신할 수는 없다.

따라서 최적화 C는 전체 exact recurrence를 한 번 계산하고, 나머지 thread 실행에서는 모든 prefix bit를 비교할 수 있다. 필요한 검증 명제를 보존하면서 같은 BigRational recurrence의 반복을 줄인다. 독립 group의 검산은 병렬화할 수 있으며 각 group 안의 recurrence 순서는 보존한다. 기준 B의 반복 검산 모드를 남겨 같은 작업량의 속도 비교와 검산 재사용의 추가 효과를 구별한다.

기존 VigilODE의 tree는 rounded affine composition이 일반적으로 associative라고 가정하지 않는다. 정해진 tree의 각 node가 exact composition을 감싸도록 구현되어 있다. original `affine_transport.rs`와 `directed.rs`를 변경하지 않고 재사용한다. 다른 tree나 병렬 reduction으로 바꾸는 것은 이번 동등성 증명의 범위 밖이다.

## 5. SIMD와 새로운 Rust 패키지의 적용 판단

SIMD는 서로 독립적인 고정 폭 연산에 유효한 후보다. 현재 핵심 kernel은 가변 길이 BigInt 산술과 exact rational 변환을 포함한다. approximate vector `exp`를 도입하려면 그 구현의 오차 경계가 필요하다. 일반적인 SIMD exp 값을 지금의 rigorously enclosed exp와 교체할 근거는 없다.

부동소수 reduction도 순서에 민감하다. round-to-nearest에서 \(a=2^{53},b=c=1\)이면 `(a+b)+c`와 `a+(b+c)`가 다르다. 모든 값을 양수로 제한해도 이 문제가 사라지지 않는다. 개별 lane을 벡터화하고 마지막 fold 순서를 유지하는 설계는 가능하므로 SIMD 자체에 대한 불가능성 결론은 내리지 않는다. 실제 phase profile로 비용이 큰 고정 폭 연산을 확인한 다음 그 부분의 구현을 판단한다.

| 외부 자원 | 이번 적용 또는 판단 | 근거 |
|---|---|---|
| num-bigint 0.4.6 | 기존 BigInt 연산으로 정수 다항식 적용 | 기존 locked dependency 및 실제 소스 |
| num-rational 0.4.2 | 매 항 정규화 대신 최종 두 유리수 구성 | `Ratio::new`/`reduce` 원 소스 |
| Rayon 1.12.0 | indexed parallel map, 정해진 결과 순서, thread별 비용 측정 | 공식 API 및 기존 vendored source |
| VigilODE ee65d4db… | affine tree·directed arithmetic 원본 두 모듈 유지 | 기존 source pin과 SHA |
| VigilODE PR73 | actual matrix+shift bits가 같은 경우만 cache 재사용하는 원칙 | exact cache source와 COST.csv |
| VigilODE PR75 | 사용되지 않는 비싼 계산의 재사용/지연과 작업 크기 측정 | residual_first.rs 및 실제 COST.csv |
| std::simd / wide / pulp | 독립 lane SIMD 후보로 조사; 이번 exact-exp 대체에는 미적용 | stable/nightly 상태, reduction 순서와 dispatch API |
| rug / MPFR | directed transcendental 대안; 추가 native build와 interval 변경 비용이 있음 | 공식 rounding 문서 |
| faer | 행렬 workload용 후보; 현재 scalar rational kernel의 직접 병목과 연결되지 않음 | 공식 프로젝트 범위 |

새 패키지 수를 늘리는 것을 목표로 삼지 않는다. 이미 검증·vendor된 산술과 스케줄러의 적절한 API를 실제 병목에 적용한다. 외부 전체 solver의 교체는 현재 원 native 비교 기준을 변경하므로 이 최적화에 포함하지 않는다.

## 6. 연구와 성능 주장의 범위

실제 새 GitHub/백업 결과를 먼저 읽었다. BR06, RUN17, RUN18, LRS의 새 결과와 VigilODE PR71/73/74/75는 `intake/`에 조사 범위와 실제 읽은 수준을 기록한다. 별도 lane의 완료를 age32 완료로 바꾸지 않는다. 기존 고정 모형 네 설정을 성능 때문에 반복 측정할 경우 고유 과학 설정 수는 계속 4이며, 측정 process 수를 별도로 센다.

성능 비교는 같은 host·compiler·source/input identity에서 수행한다. 전체 명령의 wall time, CPU time, peak RSS와 내부 phase time은 구분한다. phase 내부 preload 시간은 전체 case/pair 시간에 이미 포함되므로 중복 합산하지 않는다. 한 번의 속도 비율은 잠정치이며 반복 측정의 중앙값·범위를 함께 보고한다. reference-check feature로 옛 지수 함수를 함께 계산하는 실행은 정확성 검사에 사용하며 속도 표본에는 넣지 않는다.

현재 정확도는 고정 exported coefficient 모형의 경계 계산에 관한 것이다. 이 구현의 빠른 실행은 원 nonlinear Grackle response bound, native time convergence, age32/64 continuum convergence의 증거를 추가하지 않는다. 다음 native age32 실행은 기존의 별도 비교 계약을 그대로 따른다.

## 원전 및 확인 위치

- https://docs.rs/num-rational/0.4.2/src/num_rational/lib.rs.html
- https://docs.rs/num-bigint/0.4.6/num_bigint/
- https://docs.rs/rayon/1.12.0/rayon/iter/trait.IndexedParallelIterator.html
- https://doc.rust-lang.org/stable/std/simd/
- https://docs.rs/wide/latest/wide/struct.f64x4.html
- https://docs.rs/pulp/latest/pulp/
- https://docs.rs/rug/1.30.0/rug/float/enum.Round.html
- https://www.mpfr.org/mpfr-current/mpfr.html
- https://docs.rs/faer/latest/faer/
- https://github.com/cosmosapjw-quantum/vigilode/pull/73
- https://github.com/cosmosapjw-quantum/vigilode/pull/75

SciSpace 검색의 Priest(1997) interval elementary functions와 Kulisch–Snyder(2011) exact dot product는 관련 문헌 후보로 기록한다. 이번에 확보하지 못한 full text의 정리를 차용하지 않는다. 핵심 정수 recurrence의 정당화는 위의 직접 증명과 별도 R6 검토에 근거한다. 새로운 수학적 정리의 문헌 대비 최초성은 주장하지 않는다.
