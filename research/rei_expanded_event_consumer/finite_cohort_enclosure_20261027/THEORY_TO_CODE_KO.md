# 이론에서 코드로 넘기는 계약

## 결과

\[
D_{A,B}(F)=\int K_{A,B}(\tau)\,dF(\tau),\qquad
K_{A,B}(\tau)=G(B-\tau)-G(A-\tau).
\]

선택한 finite cohort의 \(G\)와 이미 닫힌 누적 response bounds를 입력으로 받아, 정보집합의 sharp infimum/supremum과 유한 LP witness를 반환한다. 전체 물리 source의 기록 밖 주입을 추정하지 않는다. 이론 원문은 theory/THEORY_KO.md, 독립 판정은 reviews/R6_INDEPENDENT_REVIEW.json이다.

## 식과 구현 대응

| 수학 대상 | 코드 | 보존할 조건 |
|---|---|---|
| \(h(s)=\beta+\alpha s\) | AffineSegment | exact Fraction, 양 끝 density 비음수, 음의 slope 허용 |
| 선택 cohort의 partition | _segments | 0 시작, 연속한 partition, gap은 explicit zero segment |
| \(G(x)\) | _primitive / integrated_cohort | 각 segment clamp 및 정확한 affine primitive |
| \(K_{A,B}\) | kernel | \(0\le A\le B\), 고정된 proper clock |
| \(\sum_j\lambda_jK_j\) | _ranges | kernel을 먼저 합친 뒤 extrema 계산 |
| cell \(q_i^-,q_i^+\) | CellExtremum | cell 양 끝·shifted breakpoints·내부 stationary roots |
| \(X=\{x:l\le x\le u,\ x_i\le x_{i+1}\}\) | _validate | 0=l0=u0, monotone closed bounds, mandatory all-time cap |
| \(V=\{0,l_i,u_i\}\) | _optimize | bound-level finite vertices |
| \(M_k(v)=c_{k-1}v+\operatorname{opt}_{y\le v}(M_{k-1}(y)-c_{k-1}y)\) | prefix best and parents | inclusive y=v, deterministic earliest ties |
| 单一 window | cohort_bounds | \(0\le A\le B\le t_m\) |
| signed scalar combination | combined_cohort_bounds | 同一 cumulative chain과 cell 내부 atom 위치 공유 |
| 원래 F-space의 closure endpoint | BoundsResult | INFIMUM/SUPREMUM, excluded-left location 표시 |

## 데이터와 단위

모든 numeric argument는 type Fraction 자체다. int/bool/float/string 암묵 변환을 금지한다. source와 grid는 tuple이며 결과 dataclass는 frozen이다. \([h]=\mathrm{s}^{-1}\), \([G]=[K]=1\), \([D]=[F]\)이다. 이 함수 안에서는 SI 변환이나 baryon-density projection을 수행하지 않는다.

Count와 energy response는 각각 scalar information set에서 평가한다. N/E product는 outer set이며 source 대안을 합산하지 않는다. 실제 recipient nb, source-matched spectrum/history/bath, native25와 별도 photon port는 기존 interface gate에 남긴다. Integrated event에 \(1/H\)를 곱하지 않는다.

## 수용 기준

1. R7의 exact box, affine, lower-nonattainment 사례를 정확한 Fraction equality로 재현한다.
2. 작은 grid의 독립 Cartesian-chain oracle과 목적함수가 일치한다.
3. invalid type/grid/bounds/cap/window/source partition을 zero case에서도 거절한다.
4. combined kernel은 개별 bounds 합산과 구분하며 fixed-F window additivity를 유지한다.
5. witness chain은 feasible하고 objective와 일치하며, closure atom을 무조건 attained라고 부르지 않는다.
6. large integers를 Fraction으로 보존한다. 원문4개/PREEXEC의 큰 정수는 다시 직렬화하지 않는다.

새 코드20tests와 이전 affine16tests의 최초 실행은 별도 planning budget gate 뒤에 둔다. 현재 실제 실행0이며 tolerance를 임의로 완화하지 않는다. 기존 causal3189/3189와 FD 결과는 새 primitive 실행 증거로 바꾸지 않는다.

## 계산 비용과 경계

DP는 \(O(m|V|)\) arithmetic operations와 parent storage를 사용한다. Kernel extrema 전처리와 정확한 정수의 bit cost는 별도다. Scientific runtime, memory 또는 speedup의 실측 주장은 없다. Cell closure의 최적 위치가 제외된 왼쪽 끝점이면 mass를 오른쪽에서 접근시키는 수열로 inf/sup을 해석한다.

