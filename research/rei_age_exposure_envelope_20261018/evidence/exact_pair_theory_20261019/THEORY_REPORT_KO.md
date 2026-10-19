# 고정 노드 subnormal 두 모멘트 보정과 telemetry 의미적 동일성

## 범위와 결론

이 검토는 physmath-research-loop 1.3.0의 R2(원전 재사용), R5(구성적 유도), R6(범위가 정해진 독립 검증)이다. 원 native physics SHA는 `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`이다. 저장된 가중치의 binary64 반올림을 다루며, 고정된 128개 quadrature 노드와 기존 양의 지지집합을 유지한다.

실제로 재확보한 native time8 실패 셀에는 **한 quantum을 기존 양의 노드 사이에서 이동하는 보정이 존재한다.** 첫 번째 사전식 순서 후보는 노드 24 → 0이고, 원래의 광자 수 검사와 에너지 검사를 그대로 통과한다. 그 변화량 \(2\eta\)는 \(\eta=2^{-1074}\) 격자 위에서 총량을 정확히 보존하는 모든 비영 변화량의 최소 \(L^1\) 값이다.

이 보고서에서 전체 native 적분이나 age64를 실행하지 않았다. 새 age64 block-max NCP PASS 및 `ee3b6c8014bcb21e6d4c9ef3a3560dc40df61309`은 부모 연구자가 실제 GitHub/백업에서 확인한 입력 사실로 받았다. 본 검토의 직접 실행 근거는 복구된 셀의 정확 유리수 계산, 원래 순서의 binary64 Kahan 합 재계산, Wolfram의 정확 정수·유리수 검증이다.

`PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.

## 1. 원래 검사와 실제 입력

원본 `cell_quadrature`는 양의 이산 exponential tilt를 계산한 뒤 각 가중치를 독립적으로 \(z_i=\operatorname{RN}(n p_i)\)로 저장한다. 최종 검사는 그대로 다음과 같다.

\[
 |\operatorname{Kahan}\sum_i z_i-n|\le64\epsilon n,\qquad
 |\operatorname{Kahan}\sum_i\operatorname{RN}(q_i z_i)-u|
 \le128\epsilon\max(|u|,n\,\mathrm{width}),
 \quad \epsilon=2^{-52}.
\]

이번 입력의 정규화된 평균 잔차는 \(7.28135986364631\times10^{-17}\)이고, \(|F|<8\epsilon\)를 만족한다. 새 원인을 추정해서 노드를 바꾸거나 tilt를 재정의하지 않았다.

실제 입력 파일:
`runtime_probe/session_20261019T0933Z/N2_FULL_DIAGNOSTIC_BITS.json`

입력 전체 SHA256:
`cb8d9f33367beccb05fbe2a79e5f3482aacb28d91550bf6f2d55fb12866837c7`

| 항목 | 정확한 quantum 수 |
|---|---:|
| \(n=T\eta\) | \(T=1\,244\,638\,132\,025\) |
| \(u=U\eta\) | \(U=21\,215\,026\,808\,689\) |
| 저장된 가중치 합 | \(T\) |
| 원래 저장된 에너지 합 | \(E_0=21\,215\,026\,808\,687\) |
| 광자 수 허용치 | \(0\eta\) |
| 에너지 허용치 | \(1\eta\) |
| 양의 가중치 / 0 가중치 | 73 / 55 |

따라서 부호를 포함한 에너지 잔차는 \(-2\eta\)다. 절댓값만 보고 에너지 감소 방향을 고르지 않았다.

## 2. Subnormal 영역에서 에너지 합을 정수로 다루는 보조정리

**가정.** \(q_i\ge0\), \(z_i=t_i\eta\), \(t_i\in\mathbb Z_{\ge0}\), \(\sum_i t_i=T\), \(0<T<2^{52}\). 연산은 gradual underflow가 있는 binary64 round-to-nearest, ties-to-even이며 FTZ/DAZ를 사용하지 않는다. 또한

\[
 q_{\max}T+\frac{m}{2}<2^{52}.
\]

이는 실수 단위로 \(q_{\max}n+(m/2)\eta<\mathrm{MIN\_NORMAL}\)이다.

**결론.** 각 곱의 binary64 저장값과 그 양의 누적합은 모두 subnormal 격자에 있다. 따라서

\[
 \operatorname{RN}(q_i z_i)=r_i(t_i)\eta,\qquad
 r_i(t)=\operatorname{round}_{\mathrm{even}}(q_it),
\]
\[
 \operatorname{Kahan}\sum_i\operatorname{RN}(q_i z_i)
   =\eta\sum_i r_i(t_i)
\]

가 정확히 성립한다.

**증명.** 각 저장 곱은 해당 정확 곱에서 최대 \(\eta/2\) 떨어져 있다. 양의 저장 곱의 총합은 \(q_{\max}n+(m/2)\eta\) 이하이다. 가정에 의해 모든 부분합도 MIN_NORMAL보다 작다. 따라서 모든 부분합은 표현 가능한 정수 \(\eta\) 배수이며 덧셈이 정확하다. 원본 Kahan 식의 correction은 처음 0이고, 각 단계에서 \((\mathrm{next}-\mathrm{total})-y=0\)이므로 계속 0이다. 광자 수의 누적합도 같은 이유로 정확하다.

이번 실제 벡터는 이 조건을 큰 여유로 만족한다. 상한과 MIN_NORMAL 사이의 여유는 약 \(4.4823652222255595\times10^{15}\) quantum이다. 128개 실제 곱 모두에서 Python의 binary64 곱의 bit pattern과 정확 유리수 ties-to-even 계산이 일치했다. 원래 Kahan 에너지 합도 정확 정수 합 \(E_0\eta\)와 일치했다.

이 보조정리는 모든 native 셀에 자동 적용하는 가정이 아니다. 구현은 각 후보의 원래 두 검사를 최종 판정으로 사용하면 된다.

## 3. 고정된 두 기존 양의 가중치 사이의 구성적 이동

서로 다른 donor \(a\), receiver \(b\)에 대해

\[
 t'_a=t_a-k,\qquad t'_b=t_b+k,\qquad
 t'_i=t_i\ (i\ne a,b)
\]

로 둔다. 두 노드의 기존 양의 지지를 모두 유지하는 충분하고 정확한 정수 조건은

\[
 k\in\mathbb Z,\quad 1\le k\le t_a-1,\quad t_b\ge1.
\]

총량은 정확히 보존된다. 총량 자체가 subnormal이므로 새 개별 질량도 \(T\eta\)를 넘을 수 없다. 노드 \(q_i\)는 전혀 변하지 않는다.

\[
 \|\delta z\|_1=2k\eta.
\]

고정된 선형 응답 \(R(z)=\sum_iK_i z_i\)에 대해서는

\[
 \Delta R=k\eta(K_b-K_a),\qquad
 |\Delta R|=k\eta|K_b-K_a|
 \le 2k\eta\max_i|K_i|.
\]

이 관계는 그 상태에서 고정한 \(K_i\)에 대한 정확한 관계다. gas 상태·opacity·후속 시간발전이 함께 변하는 nonlinear Grackle 응답의 전역 상계는 아니다.

### 최소 변화량 증명

정수 변화량 \(\delta t\ne0\)가 \(\sum_i\delta t_i=0\)을 만족하면, 양의 성분 합과 음의 성분 절댓값 합은 같은 양의 정수 \(s\ge1\)이다. 따라서

\[
 \|\delta z\|_1=\eta\sum_i|\delta t_i|=2s\eta\ge2\eta.
\]

그러므로 \(k=1\)인 성공 후보 하나가 있으면, 그 후보는 두 노드 보정들뿐 아니라 모든 비영 총량 보존 정수 보정 중에서도 \(L^1\) 최소이다. 원래 실패 벡터 \(\delta t=0\)는 에너지 허용집합에 없으므로 더 작은 허용 보정은 없다.

## 4. 실제 실패 셀의 최소 보정

기존 양의 지지를 유지하는 모든 방향의 \(k=1\) 쌍을 열거했다. donor는 최소 2 quantum이어야 한다. 양의 노드가 73개이나 일부 donor가 1 quantum이므로 허용 방향 쌍은 5,040개다. 이 중 1,020개가 원래 에너지 허용치를 만족했다.

사전식 순서의 첫 성공 후보:

| 항목 | donor 24 | receiver 0 |
|---|---:|---:|
| 고정 노드 \(q\) | 16.91170559547167 | 17.060705918052392 |
| 이전 \(t\) | 21,974,456 | 178,060,863,171 |
| 이후 \(t'\) | 21,974,455 | 178,060,863,172 |

보정 전 정확 실수 에너지 합의 잔차는 이미 −0.3981688550230551η였다. 개별 곱을 저장한 뒤 합친 잔차 −2η와 구별해야 한다. 보정은 정확 실수 에너지를 +0.14900032258072216η만큼 바꾸어 잔차 −0.24916853244233295η를 만들며, 저장 에너지의 잔차를 −1η로 만든다. 이때 L1/N=2/1244638132025≈1.6068927574523545e-12다.

정확한 이진 유리수 노드는

\[
 q_{24}=\frac{4760221938622859}{281474976710656},\qquad
 q_0=\frac{1200540450237787}{70368744177664},
\]
\[
 q_0-q_{24}=\frac{41939862328289}{281474976710656}
 \simeq0.14900032258072216.
\]

최종 원본 binary64 계산:

- 광자 수 결함 \(0\eta\le0\eta\).
- 에너지 결함 \(1\eta\le1\eta\).
- 새 에너지 합 \(21\,215\,026\,808\,688\eta\).
- 노드 bit pattern과 양의 지지집합 보존.
- \(\|\delta z\|_1=2\eta\), 전역 최소 비영 총량 보존 변화량.

기록은 `ACTUAL_PAIR_K1_REVIEW.json`에 있다. 이는 해당 셀의 저장 가중치 보정 가능성을 증명한다. 전체 native 적분의 성공 여부는 이 보고서의 측정 범위 밖이다.

## 5. 더 큰 \(k\)가 필요한 경우의 유한 정수 탐색 구간

위 subnormal 보조정리 아래에서 다른 노드들의 정수 에너지 합을 \(C\)라 하면,

\[
 E(k)=C+r_a(t_a-k)+r_b(t_b+k).
\]

\(\alpha=q_at_a+q_bt_b\), \(\Delta=q_b-q_a\)로 쓰면 두 번의 반올림 오차 합의 절댓값이 최대 1 quantum이므로,

\[
 |E(k)-(C+\alpha+k\Delta)|\le1.
\]

기존 에너지 검사 \(|E(k)-U|\le\tau\)를 통과하는 모든 정수 \(k\)는 반드시

\[
 |C+\alpha+k\Delta-U|\le\tau+1
\]

을 만족한다. \(\Delta\ne0\)일 때 두 유리수 끝점을 정렬한 \([L,H]\)와 양의 지지 범위를 교차하면 완전한 필요 후보 구간은

\[
 k\in[\max(1,\lceil L\rceil),\,\min(t_a-1,\lfloor H\rfloor)]\cap\mathbb Z.
\]

여기서 \(L,H\)는 \((-\tau-1-(C+\alpha-U))/\Delta\), \((\tau+1-(C+\alpha-U))/\Delta\)다. 후보마다 정확 반올림식 또는 원래 binary64 검사를 평가한다. 필요조건을 충분조건으로 오인하지 않는다.

\(\Delta=0\)이어도 두 곱의 개별 반올림 때문에 \(E(k)\)는 달라질 수 있다. 이 경우 \(|C+\alpha-U|>\tau+1\)이면 후보가 없고, 그렇지 않으면 양의 지지 범위가 유한 후보 범위다. 에너지의 실수 기울기 부호만으로 방향을 버리면 \(k=1\) 최소 보정의 완전성이 사라질 수 있다.

실제 donor 24 → receiver 0의 정확 후보 구간은 \(k=1,\ldots,23\)이다. Wolfram의 정확 유리수 계산에서 \(k=1,\ldots,22\)가 1 quantum 허용치에 들어오고 \(k=23\)은 실패했다. 현재 셀에는 이미 \(k=1\) 최소해가 있으므로 더 큰 정수 탐색을 구현할 필요가 없다.

### 최소 Rust 구현 제안

현재 증거에 맞는 가장 작은 구현은 opt-in 실패 분기에서 모든 허용 방향의 \(k=1\) 쌍을 고정 순서로 살펴보는 것이다. 최대 후보 수는 \(m(m-1)\le128\cdot127\)이다. 기존 양의 donor의 bit count에서 1을 빼고 receiver에 1을 더하며, 후보는 원본 벡터의 별도 복사본에서 만든다. 노드와 기존 허용치는 그대로다. 두 원래 검사가 모두 통과한 첫 후보만 받아들인다. 실패하면 기존 결과와 오류를 그대로 유지한다.

이는 임의의 수치 \(k_{\max}\)를 정한 탐색이 아니라, 수학적으로 최소인 비영 \(L^1\) 층을 완전하게 조사하는 방법이다. 실패 상태의 정확한 표현은 “허용 \(k=1\) 보정 없음”이다. 더 큰 보정까지 불가능하다는 주장은 도출되지 않는다.

기존 count-only 보정과 합성할 경우, 이 보고서의 전역 최소 \(2\eta\) 주장은 **pair 보정 직전 이미 정확한 총량을 가진 에너지-only 실패 벡터**에 적용된다. 최초 벡터부터 count와 energy를 함께 조정한 모든 과정의 전역 최소성을 별도로 주장하지 않는다.

## 6. 실제 사용한 문헌과 적용 범위

SciSpace에는 키워드 목록 대신 고정 유한 노드, 양의 가중치, 정확한 질량 보존, 1차 모멘트 및 정수 quantum 제약을 포함한 완전한 질문을 보냈다. 반환된 논문 목록을 Exa 검색과 원문 읽기로 연결했다.

| 1차 자료와 확인 위치 | 읽은 결과와 이 연구에 재사용하는 부분 | 여기서 추가로 해결해야 하는 부분 |
|---|---|---|
| [Wilhelmsen, *Nonnegative Cubature on Convex Sets*, SIAM JNA 11(2), 1974](https://epubs.siam.org/doi/abs/10.1137/0711030), publisher abstract 및 권호 | 주어진 유한 노드에 비음 실수 가중치를 배치해 유한 함수공간을 정확 적분하는 충분조건과 Farkas 기반 구성을 다룬다. | 정수 quantum, strict support retention, 현재 binary64 최종 검사까지 보장하는 정리는 아니다. |
| [Sommariva–Vianello, *Compression of multivariate discrete measures and applications*](https://www.math.unipd.it/~marcov/pdf/compresscub.pdf), author PDF dated 2016-07-11, 식 (5), (6), (13), (15) | 고정 지원점의 부분집합에서 NNLS로 비음 가중치를 구하고, 모멘트 잔차와 함수 근사오차의 영향을 구분한다. 식 (13)은 계수와 모멘트 오차의 내적을 제한한다. | 실수 NNLS 가중치·지원점 pruning이 본 연구의 양의 지원 유지·정수 에너지 제약을 대신하지 않는다. 작은 모멘트 잔차가 모든 응답의 같은 크기 오류를 뜻하지 않는다. |
| [Cont–Heidari, *Optimal rounding under integer constraints*, arXiv:1501.00014v3](https://arxiv.org/html/1501.00014v3), §2.2, Props. 3.1–3.2 | 합이 정수인 비음 실수 벡터를 같은 합의 정수 벡터로 반올림할 때 floor/ceiling 구조와 큰 소수부분 우선 선택의 \(L^q\), \(q\ge1\), 최적성을 증명한다. | 보존 제약은 하나의 합이다. 서로 다른 \(q_i\)를 곱한 에너지와 개별 곱의 binary64 반올림 제약은 별도의 문제다. |
| [Garhuom–Düster, *Non-negative moment fitting quadrature for cut finite elements and cells undergoing large deformations*, Computational Mechanics 70, 2022](https://link.springer.com/content/pdf/10.1007/s00466-022-02203-9.pdf), original-paper abstract | moment-fitting에 NNLS 비음 제약을 도입하는 실제 수치 연구다. | nonlinear 재료 계산에서의 관찰을 Grackle 응답 상계나 정수 모멘트 성공 보장으로 옮기지 않는다. |

짧은 원문 대조:

- Wilhelmsen: “using nodes \(T_N\)” — 고정 노드라는 조건을 확인한다.
- Sommariva–Vianello: “will not be zero, in general” — 계산된 모멘트 잔차를 따로 관리한다.
- Cont–Heidari: “The same choice of \(S^{*}\) is optimal for every \(q\ge1\).” — 해당 단일 합 제약 범위에서의 최적성이다.
- Garhuom–Düster: “non-negative least square solver” — 실수 가중치 제약의 구현 방식이다.

여기서 정리한 subnormal 정수 에너지 보조정리와 실제 한 quantum 보정은 원전으로부터 빌린 포괄적 정리가 아니라, 명시된 원본 연산에 대해 본 검토가 직접 유도하고 검사한 결과다. 선행연구가 없다는 주장이나 새로운 strong no-go 주장을 하지 않는다.

## 7. Wolfram 실제 실행과 검증 수준

Wolfram context 도구를 먼저 호출했다. 그 응답은 관련 문서·계산 도구 제안이며, 문제의 증명이 아니다. 일부 최적화 문서는 machine-precision 해법만 지원한다고 설명하므로, 본 검증은 최적화 tolerance를 사용하지 않고 정확 정수 및 유리수를 사용했다.

실제 Wolfram evaluator 결과:

- 총량 보존, \(L^1=2|k|\eta\), 고정 선형 응답, 실수 에너지 이동 등식: 모두 `True`.
- ties-to-even 점검: \(\operatorname{Round}\{1/2,3/2,5/2,7/2\}=\{0,2,2,4\}\).
- 작은 유리수 노드와 정수 질량·허용치의 33,696개 조합: 실제 성공 정수 1,803개가 모두 유도된 필요 구간 안에 있었다.
- 실제 bit-derived dyadic 입력의 donor 24 → 0: \(k=1\) 정확 정수 에너지 및 허용치 통과 확인.

33,696개 점검은 일반 증명을 대신하지 않는다. 일반 필요조건은 위 반올림 오차 부등식으로 증명했다. 첫 decimal `Rationalize` 시도는 non-dyadic 유리수를 반환하여 실제 bit identity 검증에서 제외했다. 최종 검증은 Python의 실제 bit로 얻은 분자·분모를 Wolfram에 정수로 직접 전달했다. `WOLFRAM_CHECKS.json`에는 이 교정과 최종 원문 응답을 구별해 보존했다.

## 8. Telemetry 추가와 기존 age64 결과 재사용의 의미적 동일성

현재 읽은 donor의 `positive_solver.py`는 각 출생 구간에서 같은 초기 상태, 같은 active index, 같은 rtol/atol 및 DOP853 호출을 사용한다. `error_control.py`는 기존 block-max scalar를 반환한다. Native `P` 요청은 `physical(&Setup, active, x, &[f64])`를 호출하여 지역 변수로 출력 데이터를 구성한다. 읽은 소스에서 P가 입력 상태나 source를 변경하는 동작은 발견하지 못했다.

Telemetry 상태를 \(L\), 원래 적분기 상태를 \(X\), 원래 전이 연산을 \(\Phi\)라 하자. 수동 계측은

\[
 \widetilde\Phi(X,L)=(\Phi(X),\,L\mathbin{\|}J(X,\Phi(X)))
\]

의 형태여야 한다. 물리 상태 투영 \(\pi(X,L)=X\)에 대해

\[
 \pi\widetilde\Phi=\Phi\pi
\]

이면 로그가 달라도 물리 전이는 동일하다. 이 관계를 적용할 구체적 조건은 다음과 같다.

1. Norm telemetry는 **기존과 정확히 같은 scalar**를 반환한다. K, y, scale, rtol/atol, RK 계수, max_step, first_step, 제어기의 branch와 return을 변경하지 않는다.
2. Accepted-step 로그는 실제 승인 이후에 기록한다. 거절된 trial의 binding block을 승인된 step으로 보고하지 않는다.
3. 출생 pre/post 스냅샷은 상태를 복사한다. 실제 주입은 원래의 위치와 순서에서 단 한 번 이루어지고, P 요청은 관측만 수행한다.
4. 추가 P 요청이나 출력이 실패하거나 wall-time cap을 넘는 경우는 별도 실행 상태다. 동일성 주장은 같은 cap outcome과 성공한 관측 연산의 조건 아래에 있다. wall time/RSS가 동일하다고 주장하지 않는다.
5. 작은 no-op 검증은 observer off/on의 승인된 \(t,y\), RHS 입력/출력 시퀀스, nfev를 정확 비교한다. Birth 관측은 gas/ledger 및 아직 태어나지 않은 좌표를 바꾸지 않으며, 같은 상태에 P 호출을 끼워 넣어도 이후 R 응답이 같음을 검사한다.

이는 **NUMERICAL_IDENTITY / SEMANTIC_IDENTITY** 검토다. 추가 telemetry 때문에 달라진 전체 solver 파일이나 메타데이터의 BYTE_IDENTITY를 정확도 조건으로 요구할 근거는 없다. old/new source hash는 각각 보존하고, 위 관계와 no-op 결과를 명시한 current-use record로 연결하면 된다. 본 보고서는 아직 구현되지 않은 새 telemetry 코드의 검증 완료를 선언하지 않는다.

Age32와 age64는 연령 discretization이 다르므로 두 결과 자체가 수치적으로 동일해야 하는 것은 아니다. 재사용의 의미는 두 프로그램이 같은 물리·source 처방과 다른 고정 파라미터를 유지한 채 각각의 연령 해상도에서 동일한 알고리즘을 실행한다는 것이다. 새 age32와 이미 완료된 age64의 endpoint 및 공통 관측 시점 차이를 비교할 수 있다.

기존 age64에 새 출생 pre/post 기록이 없으면 그 기록은 `NOT_RECORDED`이다. 현재 공통 관측 비교에 필요한 데이터가 존재하는지를 판정하고, 없는 새로운 관측을 완료 상태로 채우지 않는다. 이런 telemetry 공백을 기존 endpoint 결과를 이유 없이 다시 실행할 근거로 확대하지 않는다.

## 9. 검토자 범위와 문맥

검토자는 부모가 요청한 Astra-tier 독립 reviewer 역할을 상속했다. 현재 모델의 실제 내부 식별자는 독립 측정하지 않았다. 본 검토는 구현 담당자와 분리된 한 번의 범위 지정 검토이며, 추가 child review tree를 만들지 않았다.

실제로 읽은 skill context:

- `/root/.codex/plugins/cache/created-by-me-remote/physmath-research-loop/1.3.0/skills/physmath-research-loop/SKILL.md`
- 같은 루트의 `references/POLICY_INTEGRATION.md`
- 같은 루트의 `references/THEORY_LOOP.md`, R2/R5/R6 정의와 completion contract.

위 N2 셀에는 원래 실패 분기에만 opt-in 적용하는 최소 \(k=1\) 검색으로 충분하다. 이후 N3 실행에서 드러난 다른 셀과 필요한 확장은 아래에 따로 기록한다. 실제 solver 전 구간 결과는 별도 실행 증거로 판정한다.


## 10. 후속 N3 실패의 실제 진단과 다음 구성

N3 구현 `subnormal_moment_rounding.py` 및 N1 입력 경로 변경을 실제 소스로 검토했다. 별도의 전체 native 캠페인은 실행하지 않았고, 독립 검토자가 5개의 작은 검증만 다시 수행했다. 여기에는 실제 두 실패 셀을 사용하는 Rust 1.94.1 컴파일/실행 검증이 포함된다. 5/5 PASS, 0.498초였다. 검토 중 소스 hash는 바뀌지 않았다.

확인한 범위는 원본 단일 실패 anchor 삽입, 변경 없는 first-largest count helper, 모든 방향의 \(k=1\) 쌍, 정규화된 \(F\) 수렴 조건, 양의 지지·0 가중치 유지, 원래 두 검사, 실패 후보의 원본 보존이다. N1은 명시한 input directory를 동결 manifest로 검증한 뒤 출력하며, 해당 디렉터리의 누락 파일을 네트워크로 몰래 채우지 않는다. 실제 153→156 준비와 기존 none/count-mode identity 일치는 부모가 보존한 N1/N3 receipt를 읽어 확인했고, 독립 테스트는 작은 계약 fixture라는 범위를 유지했다.

N3의 변경된 time8 전체 실행은 새 실패 셀에서 exit 1이다. 다음 결과가 그 전체 실행을 PASS로 바꾸지는 않는다.

새 입력:
`runtime_probe/session_20261019T0933Z/N3_FULL_DIAGNOSTIC_BITS.json`

SHA256:
`98108bddaaca2580053766b13f5c0eaeb76ce06687083dfb2465bd319a31fca9`

| 항목 | 새 N3 실패 셀 |
|---|---:|
| 목표 광자 수 \(T\) | 313,989,944,336 quantum |
| 목표 에너지 \(U\) | 5,352,011,796,590 quantum |
| 원래 광자 수 부호 잔차 | −1 quantum |
| 원래 저장 에너지 부호 잔차 | −15 quantum |
| 허용치 | count 0, energy 0 |
| first-largest count 보정 | index 1에 +1 quantum |
| count 보정 후 저장 에너지 잔차 | +2 quantum |

위의 완전한 필요 구간을 모든 4,692개 허용 방향 쌍에 구성했다. 그중 2,348개 구간이 비어 있지 않았다. 후보를 \((k,a,b)\) 순서로 정렬한 heap에서 평가하므로, 먼저 찾은 성공 \(k\)는 고정된 count-base에서 단일 pair 이동의 최소 \(k\)다. 164개 후보를 평가한 첫 성공은 **\(k=3\), donor 0 → receiver 14**였다. 이 탐색은 \(k=1,2\)에서 성공하는 단일 pair가 없음을 함께 확인했다.

| 항목 | donor 0 | receiver 14 |
|---|---:|---:|
| 고정 노드 | 17.060707880931837 | 16.967595637004692 |
| count-base 가중치 | 44,920,141,105 | 352,206,846 |
| 보정 가중치 | 44,920,141,102 | 352,206,849 |

보정 뒤 원래 Kahan count/energy 검사는 각각 \(0\le0\)이다. 양의 지지를 유지한다. 변화량은 count-base에서 \(6\eta\), 최초 벡터에서 \(7\eta\)다. **최소성은 고정한 count-base의 단일 pair 방법에 대한 최소 \(k\)**이며, 여러 pair를 함께 쓰거나 다른 count-base를 고르는 모든 방법의 전역 최소성은 주장하지 않는다.

이 pair의 정확 필요 구간은 \(k=2,\ldots,23\)이다. Wolfram의 정확 유리수 계산에서 \(k=0,1,2,3\)의 저장 에너지 잔차는 각각 \(2,1,1,0\) quantum이었다. 고정 실수 에너지 변화는

\[
 3\eta(q_{14}-q_0)
 =-\frac{39313150036305}{140737488355328}\eta
\]

이고, 최종 정확 실수 에너지 잔차는 \(-0.45076307035872887\eta\)이다. 저장된 합의 잔차 0과 이 실수 잔차를 구별한다.

### 이후 구현에 필요한 최소 변화

이 새로운 관측은 \(k=1\) 층을 넘어 위의 정확 유리수 구간을 쓰는 이유를 제공한다. 실제 노드들은 \([16,32)\)에 있어 \(q_i=A_i/2^{48}\), \(A_i<2^{53}\)이다. \(t_i<2^{52}\)이므로 \(A_i t_i\)는 105 bit 안에 들어간다. 원래 허용치의 정수 \(\tau\)에 대해

\[
 |(C-U)2^{48}+A_at_a+A_bt_b+k(A_b-A_a)|
 \le(\tau+1)2^{48}
\]

를 checked i128 연산과 정확한 signed ceil/floor division으로 풀 수 있다. 더 일반적인 dyadic denominator를 지원할 때도 표현 범위·overflow 조건을 명시한다. 지원 범위를 벗어나거나 탐색 자원이 소진되면 기존 오류를 유지하며, 탐색 부재를 수학적 불가능성으로 보고하지 않는다.

큰 near-equal-\(q\) 구간을 첫 pair에서 전부 훑는 대신 모든 비어 있지 않은 구간의 다음 \(k\)를 min-heap에 넣으면 최소 단일 pair \(k\)를 직접 찾을 수 있다. 새 성공 후보는 여전히 원래 두 검사를 최종적으로 다시 통과해야 한다. 이는 새 관측으로 필요한 범위를 넓힌 보정이며, 같은 실패 프로그램을 무작정 재실행하는 경로가 아니다.

## 재생성 명령

동일 입력을 가지고 다음 명령을 실행하면 native solver 없이 위의 정확 dyadic 분석을 다시 만든다. 코드와 결과 파일은 이 보고서와 같은 폴더에 있다. `--max-candidates`는 분석 도구의 자원 상한이고, 도달 시 `SEARCH_BUDGET_EXHAUSTED_NO_FEASIBILITY_CLAIM`으로 구분한다.

```bash
python exact_pair_replay.py /path/to/N2_FULL_DIAGNOSTIC_BITS.json --out N2_EXACT_REPLAY.json
python exact_pair_replay.py /path/to/N3_FULL_DIAGNOSTIC_BITS.json --out N3_EXACT_REPLAY.json
```

실제 저장된 재생성 결과는 N2에서 625개 필요 후보 후 \(k=1\), N3에서 164개 후 \(k=3\)를 찾았다. 두 결과 모두 원래 count/energy 검사를 통과했다. 이들은 각각의 고정 셀 재생 결과다.


