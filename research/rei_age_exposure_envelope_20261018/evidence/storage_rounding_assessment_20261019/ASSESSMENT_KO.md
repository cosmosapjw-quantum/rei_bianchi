# Subnormal 저장 중량의 최소 count 보정 평가 — 기록 복구본

**재구성:** scratch 초기화 전의 수학 유도, 완전히 표시된 8개 prototype 결과 및 도구 호출에 기록된 보고서에서 복구했다. 원래 ASSESSMENT.json의 기록상 SHA는 `0838adca18deeebac0cbcf992d652b7aec7cc5cef40f89fe278fec7307af483b`다. 원래 timestamp, 전체 emitted-node fixture와 일부 파일 hash가 없으므로 byte-identical 복구를 주장하지 않는다. 캠페인·solver·prototype은 초기화 뒤 다시 실행하지 않았다.

## 최소 후보와 정확한 구성

기존 count gate가 실패하고 \(0<N<\mathrm{MIN\_POSITIVE}\), 모든 중량이 유한한 비음수 subnormal 또는 0이며 기존 \(|F|<8\epsilon\) 평균 적합이 수렴한 셀만 대상으로 한다. 기존 quadrature 노드, base, tilt와 closure를 유지한다. 원래 양수 저장 중량 중 최초 최대 중량 하나를 고른다. 양수 중량이 없으면 실패를 유지한다.

\(\eta=2^{-1074}\)에 대해

\[
N=k\eta,\quad z_i=m_i\eta,\quad1\le k<2^{52},\quad0\le m_i<2^{52}
\]

다. Subnormal의 양수 비트 패턴을 정수 quantum으로 해석해

\[
d=k-\sum_i m_i,\qquad m'_j=m_j+d,\qquad m'_i=m_i\ (i\ne j)
\]

를 만든다. \(m'_j\ge0\)이면 \(m'_j=k-\sum_{i\ne j}m_i\le k\)이므로 subnormal/0 범위 안이다. 실제 D 구현은 \(m'_j=0\)도 거부하는 더 보수적인 양수 후보를 사용한다.

정수 합을 overflow 확인과 충분한 폭으로 계산하고 `from_bits`로 구성하면 새 합은 정확히 \(N\)이다. 모든 부분 합이 \(N\) 이하인 비음수 정수 \(\eta\) 배수이므로 원래 compensated `sum()`도 count 결함 0을 반환한다. Energy는 각 곱셈의 반올림을 포함하므로 실제 새 중량에서 기존 두 gate를 다시 검사해야 한다. 하나라도 실패하면 원래 result와 오류를 유지한다.

## 최소 변화와 조건부 응답 경계

이 후보의 변화량은

\[
L=\sum_i|z'_i-z_i|=|d|\eta.
\]

정확한 count를 회복하는 모든 보정은 \(\sum_i\delta_i=d\eta\)이므로 삼각 부등식으로 \(\sum_i|\delta_i|\ge|d|\eta\)다. 따라서 후보가 가능하면 전역 최소 \(L^1\)을 달성한다. 최대 중량의 선택은 단일 노드 보정 중 해당 노드의 상대 변화도 최소로 한다.

기존 확률 \(0\le p_i\le1\), 저장 identity \(z_i=\operatorname{RN}(Np_i)\), round-to-nearest 가정하에 각 저장 오차는 \(\eta/2\) 이하이다. 노드 수를 \(M\)이라 두면

\[
|d|\eta\le N\left|1-\sum_i p_i\right|+\frac{M\eta}{2},
\qquad
\sum_i|z'_i-Np_i|\le\frac{M\eta}{2}+|d|\eta.
\]

초기화 전 prototype은 실제 출력 확률·중량으로 위 전제를 대조하고 유리수로 경계를 확인했다. \(F\) 수렴만으로 정규화 오차까지 통제했다고 말하면 안 된다. 기존 normalization 경로와 product identity가 전제다. 이 조건부 주장에 임의 cap은 필요하지 않지만 \(L/N\)이 모든 작은 셀에서 작다고 주장하지 않는다.

보정 전후 동일한 유한 kernel \(K_i\)에 대해서만

\[
R_K(z)=\sum_iK_i z_i,\qquad
|R_K(z')-R_K(z)|\le\max_i|K_i|\,|d|\eta
\]

가 성립한다. 한 노드 보정의 변화는 정확히 \(K_jd\eta\)다. 이는 고정 kernel의 선형 응답 경계이며 state-dependent opacity 또는 nonlinear Grackle trajectory의 전역 경계가 아니다. Underflow로 0이 된 float 곱을 인증값으로 쓰면 안 된다.

## 실제 관측과 실패 유지 대조군

실제 로컬 time8의 최대 중량은 index 1, \(q=17.05661220055637\)이다. 정수 중량은 `59071863404851`에서 `59071863404846`으로 줄어 양수로 남았다. \(d=-5\), \(L=5\eta=2.4703282292062327\times10^{-323}\), \(L/N=2.0812219540887456\times10^{-14}\)였다. 정규화 합 오차는 `-1.0719364120723678e-17`; 기존 저장 오차의 실제 \(L^1\)은 `21.934707551595743` quantum으로 \(M/2=64\) quantum 경계 안이었다.

| 입력 | 기존 count / energy defect | 보정 후보 결과 | 판정 |
|---|---:|---:|---|
| 실제 local time8 | \(5\eta/89\eta\) | \(0/4\eta\), energy gate \(116\eta\) | 두 원래 gate 통과 |
| uniform \(N=1\) | 0 / 0 | 후보 미실행 | 원래 출력 유지 |
| uniform \(N=2^{-1032}\) | \(2\eta/3\eta\) | 0 / 0, gate 0 | 통과 |
| uniform \(N=2^{-1069}\) | \(2\eta/3\eta\) | \(0/\eta\), energy gate 0 | 원래 오류 유지 |
| uniform \(N=2^{-1071}\) | \(2\eta/3\eta\) | \(0/\eta\), energy gate 0 | 원래 오류 유지 |
| uniform \(N=2^{-1073}\) | \(2\eta/3\eta\) | 기존 양수 중량 없음 | 원래 오류 유지 |
| `[13.6,24.59]`, 중앙 평균, \(N=2^{-1050}\) | \(\eta/14\eta\) | \(0/4\eta\), energy gate 0 | 원래 오류 유지 |
| 같은 support, 하단 10% 평균, \(N=2^{-1050}\) | \(0/3\eta\) | count 이미 통과 | 원래 오류 유지 |

이 결과는 실제 노드 벡터 prototype이다. 생산 source 교정이나 전체 solver 성공으로 취급하지 않았다. 이후 구현 담당자의 제한된 D 실행은 최초 count 셀을 통과한 뒤 energy-only 오류로 실패했으며 별도 최종 검토에 기록했다.

## 두 기존 노드에 대한 확장식: 미구현

현재 실제 셀에 두 노드 확장은 필요하지 않았다. 서로 다른 기존 노드 \(q_a<q_b\), count 잔차 \(D=d\eta\), 정확한 실수 energy 잔차 \(H=U-\sum_iq_i z_i\)에 대해

\[
\delta_a=\frac{q_bD-H}{q_b-q_a},\qquad
\delta_b=\frac{H-q_aD}{q_b-q_a}
\]

다. \(\delta_a=x\eta,\ \delta_b=(d-x)\eta\)로 구성하면 count를 유지한다. 비음수 feasible 범위는 \(-m_a\le x\le m_b+d\)다. 실수 해에 가장 가까운 feasible 정수가 반 quantum 이내일 때 정확한 에너지 잔차는 \((q_b-q_a)\eta/2\) 이하이며

\[
L\le\frac{|q_bD-H|+|H-q_aD|}{q_b-q_a}+\eta
\]

다. 실제 machine energy gate는 별도로 재검사해야 한다. 0 tolerance나 representability 한계 때문에 언제나 해결된다는 보장은 없다. 이 식은 기존 중량의 보정이며 전체 분포를 임의 두 노드 closure로 치환할 근거가 아니다. 확장을 구현하거나 캠페인을 추가 실행하지 않았다.

**복구 한계:** `INPUT_FIXTURES.json`의 전체 emitted nodes와 원래 fixture stdout은 남아 있지 않다. Scalar input metadata와 실제 표시된 측정 결과만 복구했다. `prototype_single_largest.py`는 기록된 소스에서 복구하되 완전한 입력 fixture 없이 재실행 가능한 패키지라고 주장하지 않는다. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`다.
