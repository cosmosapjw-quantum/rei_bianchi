# Independent construction: CFL-limited SSPRK2 of native closed photon moments

검토자: 별도 agent /root/drive_v15_intake. 작성: 2026-10-19 UTC.
현재 근거 상태: **derived + literature-supported**, native 구현 diff와 새 수치 결과의 검토는 다음 단계.
이 문서는 V14 반복복원 시간오차를 수정하기 위한 고정기체·고정기하 부분연산의 독립 구성이다.

## 1. 선택과 실제 native API

**선택: 양의 node Forward Euler(FE) stage를 두 번 평가하는 SSPRK(2,2).**
각 stage에서 현재 moment로 기존 positive reconstruction을 새로 준비한다.
source spectrum, closure, threshold cut, Verner cross section, 물리 광속과 밀도를 유지한다.

읽은 소스:

- rust/rei_microphysics/src/axbi_covariant_transport.rs
  - 검토 시 SHA256: 79b4d0972db8ed65ba64e71edc7530e46274ce8299197295bf24c800f86dbee9.
  - PreparedAbsorption.nodes는 private이며 node에는 cell, q, number, sigma[3], excess_ev[3]가 있다.
  - prepare/prepare_legacy_serial은 현재 moments와 기하에서 양의 node를 만든다.
  - 기존 evaluate_with_rule은 준비된 node에 BE 또는 exponential survival을 적용하고 같은 node에서 사건·binding·heat를 적분한다.
  - 따라서 transport module 안에 opt-in FE 평가 또는 순간 RHS API를 소규모 추가하는 것이 직접적인 연결이다.
- rust/rei_microphysics/src/axbi_q_closure.rs
  - SHA256: 8c114090f11e5220659860e0ac4d9f03537b219d8384827e2bf8702d5d276c26.
  - 기존 bounded-exponential closure를 유지한다.
- 기존 진단 example: v14_work/delivery/native_files/examples/v14_projection_diagnostic.rs.

SSP convex 조합에 기존 exponential map을 그대로 넣으면 해당 map의 \(G=AL^2R\) 항이 남는다.
이번 단계에는 **순간 RHS에 대한 실제 FE stage**가 필요하다.
Explicit midpoint는 동일한 두 RHS 평가로 2차가 되지만, 이 문제에서 원하는 일반 convex-cone 보존을 바로 제공하는 SSP 표현이 없어 채택하지 않는다.
양의 exponential midpoint는 별도 consistency와 ledger 설계가 필요하므로 현재 최소 구현 후보에서 보류한다.

## 2. 정의와 단위

각 ray/cell의 moments를 \(M_k=(N_k,V_k)\)로 둔다.
\(N_k\)는 photons/total-H, \(V_k=U_{\rm ref,k}\)는 reference-eV/total-H다.
고정 ray geometry scale을 \(r_k>0\)라 하면 physical photon energy는
\[
U_\gamma=\sum_k r_kV_k.
\]
FLRW에서 \(q=aE\)를 선택한 특별한 정규화에서는 \(V=aU\)에 해당한다.
native 코드의 실제 invariant는 energy_ref를 사용한다.

고정 support \([q_{L,k},q_{R,k}]\)에 대해
\[
\mathcal C_k=\{(N,V):N\ge0,\quad q_LN\le V\le q_RN\}
\]
는 닫힌 convex cone다. 빈 cell은 native 표현상 N=V=lo=hi=0으로 정규화한다.

node \(i\)의 양의 weight를 \(w_i(M)\ge0\), reference energy를 \(q_i\)라 두고
\[
\sum_{i\in k}w_i=N_k,\qquad
\sum_{i\in k}q_iw_i=V_k,\qquad q_i\in[q_L,q_R]
\]
를 이론 전제로 둔다. 이는 moment-exact reconstruction \(AR=M\)이다.

\[
\kappa_{ij}=c\,n_j\,\sigma_j(r_kq_i)\ge0,\qquad
\kappa_i=\sum_j\kappa_{ij},
\]
여기서 \(n_j\)는 absorber cm\(^{-3}\), \(\sigma_j\)는 cm\(^2\), \(c\)는 cm/s,
\(\kappa\)는 s\(^{-1}\)다. 기체·기하·support는 이 연구 단위에서 고정한다.

순간 closed-moment RHS와 photo 사건률은
\[
F_{N,k}=-\sum_{i\in k}\kappa_iw_i,\qquad
F_{V,k}=-\sum_{i\in k}q_i\kappa_iw_i,\qquad
J_j=\sum_i\kappa_{ij}w_i.
\]
\(J_j\)는 events/total-H/s다.
photo.gamma_s[j]는 \(c n_H\sum_i\sigma_{ij}w_i\)이므로
\(J_j=(n_j/n_H)\,\Gamma_j\)다.
서로 다른 정규화의 두 양을 더하거나 바꿔 넣지 않는다.

## 3. FE stage의 cone 보존: 직접 유도

\[
w_i^{\rm FE}=(1-h\kappa_i)w_i,\qquad
T_h(M)=A w^{\rm FE}=M+hF(M).
\]
충분조건은 각 실제 평가 stage에서
\[
0\le h\kappa_i\le1\quad\hbox{for all nonzero nodes}.
\]
그러면 \(w_i^{\rm FE}\ge0\)이며
\[
V^{\rm FE}-q_LN^{\rm FE}
=\sum_i(q_i-q_L)w_i^{\rm FE}\ge0,
\]
\[
q_RN^{\rm FE}-V^{\rm FE}
=\sum_i(q_R-q_i)w_i^{\rm FE}\ge0.
\]
따라서 \(T_h(M)\in\mathcal C\). 각 FE stage는 photon N과 physical U를 증가시키지 않는다.
이 결과는 opacity가 q에 대해 monotone이라는 가정을 사용하지 않는다.

Stage 1에서 구한 max opacity만으로 stage 2의 CFL을 확정할 수는 없다.
재복원으로 quadrature node 위치가 달라질 수 있기 때문이다.
**두 stage 모두 검사하고, 두 번째가 위반하면 전체 tentative SSP step과 그 사건 누적을 취소한 뒤 h를 줄여 다시 시작**한다.
허용값을 넘은 node를 clamp하는 것으로 승인 상태를 만들지 않는다.
\(\eta<1\)의 안전율을 쓰면 \(h\max_i\kappa_i\le\eta\)를 실행 receipt에 기록한다.
모든 \(\kappa_i=0\)이면 그대로 identity와 zero events다.

## 4. SSPRK2 구성과 2차: 직접 유도

\[
M^{(1)}=T_h(M^n),\qquad
M^{(2)}=T_h(M^{(1)}),\qquad
M^{n+1}=\tfrac12M^n+\tfrac12M^{(2)}.
\]
동치로
\[
M^{n+1}=M^n+\frac h2
\{F(M^n)+F(M^n+hF(M^n))\}.
\]
두 FE stage가 cone을 보존하면 convexity로 최종 상태도 cone에 속한다.

현재 해 구간에서 \(F\)가 충분히 매끄럽고 closure branch가 유지되면
\[
F(M+hF)=F(M)+hF'(M)F(M)+O(h^2),
\]
\[
M^{n+1}=M+hF+\tfrac12h^2F'F+O(h^3).
\]
따라서 고정된 비강성 문제의 closed-moment ODE에 대해 국소 3차 결함과 전역 2차가 성립한다.
V14의 \(G\) 대신 필요한 \(F'F\) 항을 실제 stage 재평가로 생성한다.
node-count 변경, support endpoint branch 전환, binary64 floor에서는 그 유효범위를 실행 데이터와 함께 표시한다.

문헌 관계: 이 SSPRK(2,2)와 CFL coefficient 1은 기존 결과다.
Gottlieb–Shu–Tadmor, *SIAM Review* **43** (2001) 89–112,
DOI [10.1137/S003614450036757X](https://doi.org/10.1137/S003614450036757X),
Lemma 2.1 및 Proposition 4.1 / Eq. (4.1).
[저자 보존 원문](https://math.umd.edu/~tadmor/pub/linear-stability/Gottlieb-Shu-Tadmor.SIREV-01.pdf)을
2026-10-19 Exa로 읽었다. SciSpace의 독립 탐색은 관련 SSP 문헌을 제공했으나
위 정확한 명제의 채택 근거는 원문이다.
이번 직접 기여는 native node·total-H 정규화·support cone·사건 회계에 대한 대응과 구현 계약이다.

## 5. 사건·binding·heat의 동일 stage 가중치

FE stage마다
\[
P_j^{(a)}=hJ_j(M^{(a)}),\quad
B^{(a)}=\sum_j I_jP_j^{(a)},\quad
Q^{(a)}=h\sum_{ij}\kappa_{ij}w_i(M^{(a)})(r_kq_i-I_j)
\]
를 계산한다. 여기서 \(a=0,1\), \(I_j\)는 native physical binding threshold다.
cross section이 양수인 node에서 \(r_kq_i-I_j\ge0\)인 원래 native 대응을 유지한다.

최종 증가량:
\[
P_j=\tfrac12(P_j^{(0)}+P_j^{(1)}),\quad
B=\tfrac12(B^{(0)}+B^{(1)}),\quad
Q=\tfrac12(Q^{(0)}+Q^{(1)}).
\]
그러면 정확산술에서
\[
\sum_k(N_k^n-N_k^{n+1})=\sum_jP_j,
\qquad
U_\gamma^n-U_\gamma^{n+1}=B+Q
\]
가 성립한다. 이는 extended ODE \((M,\ell)'=(F,J)\)에 같은 SSPRK2를 적용한 결과다.
stage 1의 photon map만 갱신하고 사건을 마지막 spectrum에서 계산하는 방식은 이 식을 보장하지 않는다.
기존 누적 ledger에 두 stage 사건을 각각 전량 더한 뒤 최종 moments만 절반합하는 방식도 잘못이다.

기체를 고정한 이 실험에서는 \(B,Q\)는 diagnostic deposition ledger다.
이것만으로 evolving gas의 chemistry·thermal equation을 2차로 적분한 것은 아니다.
전체 coupling에는 기체 species와 thermal state를 같은 stages에서 갱신하고,
기체 simplex·열에너지에 대한 별도 FE admissibility 조건을 만족시켜야 한다.

## 6. native binary64 구현에서 필요한 조건

1. cell_quadrature는 positive discrete tilt로 moments를 맞추지만
   count/energy fit에는 각각 \(64\epsilon\), \(128\epsilon\) 규모의 허용 경계가 있다.
   이론의 exact \(AR=M\)와 현재 binary64 fit을 구분한다.
2. FE survivor를 **양의 node 합**으로 계산하고 기존 support-end anchor와 compensated sum을 재사용한다.
   template−loss의 큰 수 차감은 cone 경계에서 미세한 음수나 에너지 slack 위반을 만들 수 있다.
3. 이러한 node 합은 \(h=0\)에서 기존 quadrature fit 오차만큼 template와 다를 수 있다.
   0-step은 명시적 identity로 두는 편이 적절하다. 무흡수 상태도 identity와 zero ledger로 처리할 수 있다.
4. 최종 convex merge는 동일한 원래 support envelope를 유지한다.
   한 stage가 빈 상태가 되어도 나머지 양의 성분의 support를 버리지 않는다.
   양의 convex 조합 후 N=0이면 canonical empty support를 쓴다.
5. exact delta lo==hi==q에서는 최종 energy_ref=q*number를 같은 곱셈으로 만든다.
   native validator는 해당 등식을 tolerance 없이 검사한다.
   별도로 계산한 두 U의 절반합은 q 곱셈과 rounding order가 달라 실패할 수 있다.
6. \(N,U,P,B,Q\)와 photon-loss residual은 각각 보존한다.
   tiny floating residual을 없애기 위해 사건을 임의로 재분배하거나 physical rate를 수정하지 않는다.
7. 입력 상태·기체·기하·h의 유효성 검사가 끝나기 전에는 caller state나 누적 ledger를 mutate하지 않는다.

## 7. Delta·zero-opacity·강성 극한

고정 delta에서 \(F_N=-\kappa N\)이고, 이 SSPRK2의 생존인자는
\[
R(-\tau)=1-\tau+\tfrac12\tau^2,\quad \tau=h\kappa.
\]
따라서 delta도 exact exponential에 대해 전역 2차다.
이전 exponential map의 delta full/two-halves가 ulp였던 기준을 새 SSP map에 그대로 적용하면 안 된다.
새 delta 기준은 analytic \(N_0e^{-\kappa T}\) 및 같은 고정종 사건 분할과의 수렴이다.

\(\tau\le1\)에서 stage positivity를 보장한다.
\(\tau=1\)의 1-step 생존 \(1/2\)는 \(e^{-1}\)와 상당히 다르다.
양성과 보존은 시간 정확도의 대체 지표가 아니다.

\(\kappa\to\infty\)에서 고정 h를 유지하는 방법은 아니다.
FE CFL에 따른 분할 수는 대략 광학깊이 규모로 증가한다.
연산 예산을 초과하면 명시적으로 bounded-run blocker를 남긴다.
uniform stiff accuracy, unconditional stability, asymptotic preservation은 이 구성의 채택 주장에 포함하지 않는다.

## 8. 다음 실제 판별과 주장 상태

변경 코드의 유한 검증 기준:

- broad positive native spectrum: full/two-halves 국소 결함 slope 약 3, 고정 T self-difference slope 약 2.
- delta: analytic exponential과 전역 2차, 올바른 species event split.
- 두 stage의 실제 CFL 위반 rejection 또는 명시적 subdivision, mutation rollback.
- zero dt, zero opacity, empty and exact-delta support.
- 각 stage 및 최종 cone invariants, 독립 photon N/U–event–binding–heat ledger residual.
- 기존 default/BE/exponential path의 수치식·분기 보존은 diff로 먼저 확인한다.

이 메모 단계에서 새 scientific run과 코드 수정은 수행하지 않았다.
고정 매질의 조건부 2차 구성은 **derived**.
실제 구현과 native 수렴 결과는 root/coder 실행 후 해당 diff와 receipt를 읽어 판정한다.
전체 source-on p2와 기존 HOLD 항목은 이 부분연산의 결과만으로 승격되지 않는다.

