# 다음 물리 연구 루프 — PHYS24_FIXED_MOMENT_HEIII_ENVELOPE

PHYS23에서 남긴 단일 후속 문제다. 이 문서는 PHYS24 실행 기록이 아니다.

## 1. 바로 풀 질문

실제 고정 초기 기체를 유지하고 \(I=[13.61,24.58]\) eV에서 nonnegative photon-number measure \(d\nu_0\)가
\[
\int d\nu_0=N_0,\qquad \int E\,d\nu_0=N_0\bar E
\]
를 만족할 때 가능한 초기 HeIII \(\epsilon^2t^4\) 계수의 최솟값과 최댓값을 구하라. \(\bar E\)에 따라 부호가 강제되는 영역과 양·음 모두 가능한 영역을 분류한다.

PHYS23에서는 같은 \(N,U\)의 두 spectrum이 HeIII 계수의 반대 부호를 낼 수 있음을 확인했다. Monoenergetic zero \(E_{\rm HeIII}\simeq15.43367\) eV만으로는 일반 spectrum의 부호가 정해지지 않는다. 이 정보 손실을 주어진 두 모멘트 아래의 응답 범위로 정량화하는 것이 동기다.

## 2. 입력 identity와 최소 읽기

저장소 cosmosapjw-quantum/rei_bianchi, branch forward/rust-reion-kernels-20260922, 기존 [draft PR83](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/83).

- PHYS23 scientific input commit: e334866a4ac1be963f573c0b35182d25eb4d666b.
- Input root tree: 05afdbe0aaee3f67f42ea3f1cdf946238faaf3e7.
- Scientific Rust src tree: cb69b4736dd046e4675557577eb8e0ead037d1f3.
- PHYS23 frozen contract SHA256: 888eb11c8a53f828b0ed5d3a053d91dc4da671d727e49c519cb3110bb5b6d200.
- Exact sign result SHA256: db437b4580ffea99f85659d7308507459ee4ce9347ba3a2ff570c428e4009b9a.
- Numerical result SHA256: 55670faaadc079bf08f2ea5ef98fe765f2d83f74928ebd4862f4d3fee44c0541.
- Inherited PHYS22 coefficient JSON SHA256: 6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79.
- Canonical Astra harness SHA256: dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7.

실제 PHYS23 publication commit, archive SHA, 최종 report/review SHA는 함께 전달한 detached publication receipt에서 읽는다. 위 input commit을 publication commit으로 오인하지 않는다. 시작할 때 현재 branch head와 필요한 source identity만 확인한다.

최소 읽기는 이 handoff → PHYS23_REPORT_KO.md §§3–4, 7–9, 11–13 → RESULTS_SUMMARY.json → independent/DECISION_REVIEW.json이다. 함수 구현은 contributions/numerics/spectral_response.py의 response/analytic/mixture helper를 필요한 만큼 읽는다. Main을 실행하여 닫힌 PHYS23 suite를 다시 시작하지 않는다. Exact source 상수와 signed ratio proof가 필요할 때만 contributions/signs/SPECTRAL_SIGN_DERIVATION_KO.md와 certificate JSON을 연다.

## 3. 이미 닫힌 내용

\(F_2=[\epsilon^2]F=\tfrac12\partial_\epsilon^2F|_0\), \(B=t\Sigma\), \(\Sigma=\varsigma\operatorname{diag}(1,-1,0)\), \(q=2\varsigma^2\)다. Metric \((-+++)\), proper seconds, energy eV, \(w\) eV/H, 계수에 추가 factorial 없음. 실제 IC와 source binary64 상수의 exact-real 해석을 그대로 유지한다. Native arithmetic 동등성은 입증하지 않았다.

\(D=E\partial_E\), \(\mathscr C=D(D+3)\), \(\lambda=c n_H(1-x_*)\sigma_{\rm HI}\)이며 gas IC는 spectral 미분에서 고정한다.

\[
a_{3,x}=\frac q{45}\int \mathscr C\lambda\,d\nu_0,\qquad
a_{3,w}=\frac q{45}\int \mathscr C[\lambda(E)(E-\chi)]\,d\nu_0,
\]
\[
a_{4,h_2}=\frac14\left(J_{h_2,x}a_{3,x}+J_{h_2,w}a_{3,w}\right).
\]

HI-only 열린 구간 전체의 HII·heat·50000 K 온도 부호는 음수이고, \(r(E)=\mathscr C[\lambda(E)(E-\chi)]/\mathscr C\lambda(E)\)는 엄격히 증가한다. Exact rational certificate가 닫았으므로 PHYS24의 기본 준비로 다시 실행하지 않는다.

HeIII의 식은 inherited serialized numerical \(J_{\rm np,*}\)에 조건부다. Mono zero의 수치 bracket 폭은 \(6.78\times10^{-21}\) eV지만 원자물리나 Jacobian의 물리적 정확도를 뜻하지 않는다.

## 4. PHYS24에서 사용할 scalar kernel

\(dP=d\nu_0/N_0\)를 probability measure로 두고
\[
g(E)=\frac14\left[
J_{h_2,x}\mathscr C\lambda(E)
+J_{h_2,w}\mathscr C[\lambda(E)(E-\chi)]
\right]
\]
를 정의하면
\[
a_{4,h_2}=\frac{qN_0}{45}\int g(E)\,dP(E),
\qquad
\int dP=1,\quad \int E\,dP=\bar E.
\]

\(g\)의 단위는 s\(^{-2}\), \(qN_0/45\)의 곱까지 포함한 \(a_4\)는 s\(^{-4}\)다. 기존 numerical helper response의 HeIII_t4_s-4는 이미 \(qN_0\)를 포함하므로 이를 다시 곱하지 않는다.

필요한 extrema는 평균 에너지를 고정한 선형 functional 문제다. Lower convex envelope와 upper concave envelope, 두 개 이하의 spectral line을 갖는 extremizer의 관계를 직접 유도하거나 정확히 근거를 대라. 이는 후속의 제안된 풀이 경로이며 이미 실행하여 인증했다는 뜻은 아니다.

\(r(E)\)가 증가한다고 \(g(E)\)의 convexity나 부호 평균이 평균 에너지에 의해 결정되는 것은 아니다. \(\mathscr C\lambda(E)\)의 크기도 weight에 들어간다.

## 5. 최소 완료 기준

1. \(I=[13.61,24.58]\) eV, \(N_0\), mean constraint, numerical \(J\)의 claim ceiling을 먼저 고정한다. Threshold 구간이나 gas IC를 바꾸지 않는다.
2. Scalar kernel의 단위와 normalization을 확인하고, 두 모멘트의 feasible response set을 정의한다.
3. Extremizer support 또는 convex envelope 표현을 해석적으로 정리한다. Dense grid LP만으로 continuum 최적성을 증명했다고 하지 않는다.
4. 필요한 stationary/tangent/chord/root만 작은 판별 계산으로 다룬다. Exact 또는 interval certificate가 없다면 numerical envelope·bounds라고 제한한다. 첫 실패와 허용오차를 보존한다.
5. \(\bar E\)에 따른 HeIII 부호의 강제/혼합 가능 영역을 도출하고 PHYS23의 같은 \(N,U\) 반례를 닫힌 입력으로 연결한다. 확인이 필요하면 한 번의 좁은 anchor만 사용한다.
6. 별도 decision reviewer, 보고서·결과·다음 질문 하나·재현 묶음과 허용된 동일 branch의 additive docs publication까지 완료한다.

모멘트 둘만으로 sign을 강제할 수 없는 구간이 넓다는 결론도 유효하다. Fixed mean을 넘어 임의 고차 모멘트나 finite history로 범위를 자동 확장하지 않는다.

## 6. 보호와 종료

Physical=HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED. Production source/default/runtime 변경 없음. Native run, gas IVP, PHYS19–23의 닫힌 과학 suite replay, 대규모 energy/history campaign은 기본 범위에 포함되지 않는다.

Archive byte 문제가 있으면 reproduce.py --verify-only를 먼저 사용한다. 새로운 portability 필요 없이 전체 replay를 시작하지 않는다. PHYS23의 최초 과학 실행은 exact 31/31, numerical65/65이며, 별도 portability 실행은 새 독립 물리 검산으로 합산하지 않는다. Remote ACK/tree/blob 일치와 fresh local archive restore는 다른 증거다.

기존 세션에서 허용한 동일 branch의 nonforce compare-and-swap additive docs publication은 이어갈 수 있다. 새 PHYS24 경로를 쓰고 기존 docs/source를 바꾸지 않는다. Merge나 타인에게 메시지 보내기는 포함하지 않는다.
