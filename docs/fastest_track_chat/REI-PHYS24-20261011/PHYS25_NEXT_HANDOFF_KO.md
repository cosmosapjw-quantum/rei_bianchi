# 다음 물리 연구 루프 — PHYS25_HEIII_SIGN_REVERSAL_VARIANCE_COST

PHYS24에서 남기는 단일 후속 질문이다. 이 문서는 PHYS25 실행 기록이나 최적성 판정이 아니다.

## 1. 바로 풀 질문

실제 고정 초기 기체, 광자 수 \(N_0=\operatorname{f64}(0.05)\) photon/H와 \(I=[a,b]=[13.61,24.58]\) eV를 유지한다. 이번에는 평균 에너지를 **\(m=18\) eV 한 값**으로 고정한다.

\[
V_* = \min_{P\ge0}\left\{\int_I(E-m)^2dP:
\int_I dP=1,\ \int_I E\,dP=m,\ \int_I k(E)\,dP\ge0\right\}.
\]

**HeIII 초기 \(\epsilon^2t^4\) 계수를 비음수로 만들기 위해 필요한 광자 에너지 분산의 정확한 최솟값과, 그것을 달성하는 스펙트럼을 구하라.** 단위는 \(V_*\)가 eV\(^2\), \(\sqrt{V_*}\)가 eV다. \(k(E)\)는 고정 \(N_0,q\)를 이미 포함한 PHYS24 단색 coefficient이며 단위 s\(^{-4}\)다.

동기는 PHYS24가 얻은 정보 손실의 크기를 실제 스펙트럼 폭으로 해석하는 것이다. 평균 18 eV에서는 가능한 \(a_4\)가 \([-1.189877382928\times10^{-64},+5.093491693437\times10^{-65}]\) s\(^{-4}\)여서 두 모멘트만으로 부호를 정할 수 없다. 최소한 얼마나 넓은 스펙트럼이 있어야 단색의 음의 부호를 바꿀 수 있는지 묻는다.

## 2. 입력 identity와 최소 읽기

저장소 cosmosapjw-quantum/rei_bianchi, branch forward/rust-reion-kernels-20260922, [draft PR83](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/83).

- PHYS24 scientific input commit: 6104a9655439b15143933a97b9926e61dfb62b53.
- PHYS24 input root tree: 4677621ec12994af5f637f582888713e23845361.
- Scientific Rust src tree: cb69b4736dd046e4675557577eb8e0ead037d1f3.
- PHYS24 계약 SHA256: fd60772fa082a651034b21b965133e57cc0c3e37bb14cdab531a5ca3965266e2.
- PHYS22 수치 Jacobian 입력 SHA256: 6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79.
- PHYS24 exact curvature 결과 SHA256: 48a301226276efa5ae42815358a9629a45f28a64ba0a8a553dc517f63913d552.
- PHYS24 numerical 결과 SHA256: 551ae060d935e5145e54a1c2af9deb5c5b2c4d8d7007d90295eb0bbad5e83d09.
- Astra harness SHA256: dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7.

실제 PHYS24 publication commit과 완성 archive/report/review SHA는 함께 전달된 detached PHYS24_PUBLICATION_RECEIPT.json을 따른다. 위 scientific input commit을 publication commit으로 오인하지 않는다. 다음 실행 시작 시 현재 branch head와 필요한 source identity만 새로 확인한다.

최소 읽기: 이 handoff → PHYS24_REPORT_KO.md §§3, 5–9, 10–13 → RESULTS_SUMMARY.json → independent/DECISION_REVIEW.json. 일반 모멘트 논리가 필요하면 contributions/moments/MOMENT_EXTREMIZERS_KO.md를 읽고, 함수 평가 구현은 contributions/numerics/moment_envelope.py의 response/Jet helper를 읽는다. 닫힌 main을 기본 준비로 실행하지 않는다.

## 3. 이미 닫힌 결과

\[
g(E)=\tfrac14\{J_x\mathscr C\lambda+J_w\mathscr C[\lambda(E)(E-\chi)]\},
\quad k(E)=\frac{qN_0}{45}g(E),\quad a_4(P)=\int k\,dP.
\]

\(D=E\partial_E\), \(\mathscr C=D(D+3)\), \(\lambda=c n_H(1-x_*)\sigma_{HI}\)다. Metric \((-+++)\), proper seconds, energy eV, \(w\) eV/H, \(F_2=[\epsilon^2]F=\tfrac12\partial_\epsilon^2F|_0\), time coefficient에 추가 factorial 없음을 유지한다.

PHYS24가 실제로 증명한 것은 고정 serialized numerical \(J\)를 정확한 유리수 입력으로 해석한 조건에서

\[
k''(E)>0\ (E\in I),\qquad k(a)>0>k(b),
\]
\[
\{a_4(P):P\in\mathcal P_m\}=[k(m),B(m)],
\quad B(m)=\frac{b-m}{b-a}k(a)+\frac{m-a}{b-a}k(b)
\]

라는 사실이다. 단색이 유일한 하단, 양 끝점 혼합이 유일한 상단이다. \(k\)의 영점 \(E_-\simeq15.43367\) eV와 \(B\)의 영점 \(E_+\simeq19.55655\) eV 사이에서는 양·음 모두 가능하다. 영점 소수는 numerical bracket이며 물리 정확도나 rigorous root interval이라고 부르지 않는다.

일반 연속 커널의 고정 질량·평균 극값은 두 점 이하 측도로 달성할 수 있다. 엄격 볼록한 실제 커널에서는

\[
P_v=\frac{v-m}{v-a}\delta_a+\frac{m-a}{v-a}\delta_v,\qquad m\le v\le b
\]

의 응답이 \(k(m)\)에서 \(B(m)\)까지 연속·엄격 증가한다. 따라서 \(m=18\) eV에서 \(a_4=0\)을 주는 이 경로상의 \(v\)는 유일하게 존재한다. **그 두 선이 분산도 최소인지 PHYS24는 증명하지 않았다.** 두 선 경로의 유일성을 모든 영 응답 스펙트럼의 유일성으로 확대하지 않는다.

## 4. 제안하는 작은 판별 경로

먼저 위 목적함수와 inequality constraint를 고정하고 극값 존재·제약 활성화·지지점 수를 정리한다. 분산과 평균만으로 두 임의 스펙트럼의 응답 순서가 결정된다고 가정하지 않는다. 가능한 두 선 후보와 필요하면 세 선 후보를 구분한다.

연속 최적성에는 실제 증거가 필요하다. 예를 들어 상수 \(\lambda_0,\lambda_1,\lambda_2\)에 대해 \(\lambda_2\ge0\)이고

\[
(E-m)^2-\lambda_0-\lambda_1(E-m)-\lambda_2 k(E)\ge0
\quad(E\in I)
\]

를 인증하면 모든 허용 측도에 대해 \(V\ge\lambda_0\)라는 dual lower bound가 된다. 후보 지지점에서의 접촉·평균·영 응답이 이 bound와 맞는지 판별할 수 있다. 이 식은 가능한 증명 경로의 제안이며 인증 완료 주장이 아니다. \(k'''\) 등 새 도함수의 부호가 필요하다면 새 범위로 유도하고 인증한다. PHYS24의 \(k''>0\)만으로 그 부호가 따라오는 것은 아니다.

수치 탐색은 필요한 소수의 root/tangent/contact 계산으로 제한한다. Dense grid 최적값만으로 continuum 최적성을 선언하지 않는다. 정확 또는 interval certificate가 어려우면 엄밀 lower bound와 feasible upper bound를 분리하고, 수치 후보의 claim ceiling을 유지한다.

## 5. 최소 완료 기준

1. \(m=18\) eV, \(N_0\), support와 numerical \(J\) 조건을 동결한다. 다른 초기 기체나 전체 평균 구간으로 확대하지 않는다.
2. 분산 목적함수·HeIII 비음수 제약의 차원과 정규화를 확인한다. \(k\)에 \(qN_0\)를 중복 곱하지 않는다.
3. 후보의 존재/지지 구조를 유도하고, feasible spectrum과 필요한 bounded root/contact 계산을 실제 수행한다.
4. 전역 최적성의 정확한 증거 또는 분리된 lower/upper bound를 제시한다. 최초 실패·프로토콜·허용오차·원 로그를 보존한다.
5. \(V_*\)보다 작은 분산의 부호 의미, equality spectrum, 그보다 큰 분산에서 무엇이 가능/미해결인지 과장 없이 정리한다.
6. 별도 final reviewer, 보고서·결과·DAG·다음 질문 하나·재현 묶음, 허용된 동일 branch additive docs publication까지 마무리한다.

## 6. 보호와 재개

Physical=HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED. Production source/default/runtime 변경 없음. Native run, gas IVP, PHYS19–24의 닫힌 과학 suite replay, 광범위한 energy/history campaign은 기본 범위에 포함되지 않는다.

이번 입력의 새 최초 과학 실행은 exact20/20, numerical156/156이었다. 별도 portability 재생은 독립 물리 검산으로 합산하지 않는다. 파일 바이트 문제에는 reproduce.py --verify-only를 먼저 쓰며 전체 과학 replay를 기본 intake로 실행하지 않는다.

수치 방법 설계는 타 기여자의 성공 요약 전에 고정했으나 첫 실행 전에 그 요약을 받았다. 원 protocol과 INDEPENDENCE_ACTUAL.json을 함께 소비하여 비맹검 방법 독립성으로만 해석한다. 수치 노트의 문서 형식 정정은 원본 history와 FORMAT_CORRECTION.json에 있으며 과학 바이트 변경은 없다.

기존 세션에서 허용한 동일 branch nonforce compare-and-swap additive docs publication은 이어갈 수 있다. 새 PHYS25 경로를 쓰고 기존 source/docs를 바꾸지 않는다. Merge나 타인에게 메시지 보내기는 이 범위에 포함되지 않는다.
