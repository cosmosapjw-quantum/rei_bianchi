# HE-ANG-CONTRACT 결과: angular source·frame·event 상관의 유도와 실행 가능한 계약

단원: `research/he_ang_provider_contract_20261023` · workflow **1.0.0** · approval **0.2**

이 단원은 **COMPLETE_SCOPED**이며, 유한 질량 \(e+H\to e+e+p\) 사건의 angular provider가 공급해야 할 **출처, 정규화, frame, 두 전자–이온의 상관 정보**를 유도하고, 그 계약을 검사하는 stdlib/Fraction 코드를 구현했다. 새 exact witness에서 **252/252 predicates**, 구현의 **51/51 affected controls**, 저장된 witness와 새 accumulator 사이의 **28/28 grouped comparisons**가 통과했다. 실제 source 입력과 물리 불확실성의 보정은 `SOURCE_INPUT_PENDING`이다. [동결 계약](CONTRACT.json), [R7 영수증](theory/WITNESS_RECEIPT.json), [C6 영수증](evidence/execution/C6_RECEIPT.json), [C7 영수증](evidence/execution/C7_RECEIPT.json)

이 결과는 HE-X1 다음에 필요한 공급자 계약을 완성하기 위한 제한된 과학·구현 결과다. 물리적으로 보정된 새 H1 angular law의 선택, HE38 uniform-angular 모델의 교체, baryonic stress의 진화, 새 IVP는 이번 실행에 포함되지 않았다. 모든 provider-precheck 결과는 `empirical_admission=false`, `runtime_activation=false`를 유지한다. [Claim gate](CLAIM_GATE.json), [provider precheck](code/heang_contract/metadata.py)

> 독립 이론·구현 검토는 모두 **PASS_SCOPED**다. C9는 실제 C6/C7 raw, source bytes와 누적 비용까지 대조했으며 open code findings0, 추가 과학 실행 불필요로 판정했다. R1–R10/C1–C10의 실제 단계 상태와 backup ACK는 [DAG](DAG.json), 게시 identity는 [delivery/PUBLISHED_PINS.json](delivery/PUBLISHED_PINS.json)에 연결한다. [이론 최종 검토](evidence/review/THEORY_REVIEW_FINAL.json), [코드 최종 검토](evidence/review/CODE_REVIEW_FINAL.json)

## 1. 원래 목표에서 이번 단원이 다룬 차이

HE32는 8핵종·21상태, prescribed-UV photo+caseA RR pilot의 완료 근거다. 392 nominal과 2 angular guard, 총394 완료 IVP 및 그림6쌍을 재사용했다. 그 pilot의 gas는 \(\pi_b=0\)이며 matter stress는 nonbaryonic sector다. HE38에서는 명시된 finite-mass·uniform-Jacobi source 모델의 event kinematics와 gain moments를 이미 구현·검증했다. 이번 단원의 목적은 여기에 경험적 각분포를 임의로 붙이는 것이 아니라, **다른 angular law를 도입할 때 실제로 필요한 정보를 식별하고 그 입력 계약을 실행 가능하게 만드는 것**이다. [재사용 지도](evidence/intake/REUSE_MAP.json), [HE38 원 실행 기록](evidence/intake/HE38_RESOURCE_REUSE.json)

진척은 구체적인 의존성이 채워진 정도로 기록한다. 현재 얻은 것은 source/frame/event contract, 구성적 witness, 검증된 exact accumulator와 structural precheck다. 실제 source-qualified joint moments, species 간 교환계수, 열·광원 reservoir, \(\pi_b=\sum_s\pi_s\) closure는 각각 후속 입력을 필요로 한다. 따라서 이 제한 단원의 단계 수를 전체 물리 목표의 완료율로 환산하지 않는다. [후속 DAG](NEXT_DAG.json)

## 2. 재사용한 근거와 이번 intake의 실제 범위

고정 중앙 handoff는 `rei_bianchi@0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`이며, BASS_HE 입력은 HE38 publication `10e24aeaae21cf8e1427fba64233631d15444e67`와 science pin `2ce8afd80b7baf430c85ce5ace81a5bd4e9465c0`다. HE-X1 science pin `eb03981d15ad291375dd6d574a9c28809f85fc02`의 **32 fixtures /181 predicates 및 독립 PASS_SCOPED**를 동일한 source·result identity의 완료 근거로 재사용했다. 그 32개를 이번 새 controls의 개수에 더하지 않았고 실행도 반복하지 않았다. [Intake](evidence/intake/INTAKE_KO.md), [재사용 지도](evidence/intake/REUSE_MAP.json)

이번 intake는 현재 BASS_HE branch 목록과 최근30개 open PR metadata, 고정 중앙 X1 문서·결과·검토, 선택된 병렬 소유자의 변경분을 읽은 범위다. 기존 문헌·provider 조사는 HE38의 source qualification 기록을 재사용했다. 모든 저장소·대화·백업의 내용을 새로 전수 조사했다고 기록하지 않는다. HE38 복원 capsule의 원 SHA256과262 payload를 확인했으며, 129T diagnostic·oracle·benchmark·render를 재실행하지 않았다. [Intake](evidence/intake/INTAKE_KO.md)

병렬 소유자 ANGTHERM02/Li-threshold branch의 `906f217...→8d10231...` 변경17개는 그 소유 단원 안에 있었다. 해당 조건부 Li 결과는 읽기 전용 변경분으로 확인했으며 H1 joint collision provider로 채택하거나 그 branch의 코드·실행·reservation을 변경하지 않았다. [소유자 변경분](evidence/intake/OWNER_DELTA_8d10231.json)

## 3. 공통 event measure와 정규화

질량 convention은 HE38과 같은 Newtonian kinetic model이다.

\[
m=m_e,\qquad M=m_p,\qquad h=M+m,\qquad L=M+2m,
\]
\[
\mu=\frac{mh}{L},\qquad
E=\frac12\mu |v_e-v_H|^2,\qquad
a=\frac{v_e-v_H}{|v_e-v_H|},\qquad W=E-I.
\]

입사 에너지 \(E\)는 한 incoming pair의 상대 COM 에너지다. 열평균 에너지나 projectile-lab energy로 바꾸려면 그 변수 변환과 source preparation을 명시한다. Threshold \(I\)는 internal-energy ledger에 남으며, 질량 결손 \(I/c_{\rm light}^{2}\)을 kinetic mass 합에 부분적으로만 삽입하지 않는다. \(c_{\rm light},\hbar,k_B\)는 명시적으로 유지한다. Source가 wave number를 제공하면 \(q=\hbar k\), temperature를 제공하면 해당 에너지 관계에 \(k_B T\)가 등장한다. [유도 §1](theory/DERIVATION.md)

Primary object는 같은 incoming \(E,a,\mathrm{preparation}\)에서 정의된 양의 event differential cross-section measure다.

\[
\int d\Sigma=\sigma(E,a;\mathrm{preparation}),
\]
\[
q_1+q_2+q_p=0,\qquad
\frac{|q_1|^2+|q_2|^2}{2m}+\frac{|q_p|^2}{2M}=E-I.
\]

두 전자는 한 physical event에서 나온다. Unordered event를 한 번 세는 표현과 ordered exchange-symmetric lift를 구별하고, 이미 density에 포함된 \(1/2!\)나 energy-ordering restriction에 symmetry factor를 다시 곱하지 않는다. Full inclusive electron measure는 event당2, proton은 event당1이다. Slow-electron-only spectrum의 count1을 count2로 바꾸려면 같은 joint law에서 partner를 복원할 근거가 필요하다. Quantum exchange interference는 physical source의 의무이며 label symmetrization만으로 생성되지 않는다. [유도 §2](theory/DERIVATION.md)

정규화를 통일하기 위해 event measure의 총질량을 \(Z\)로 둔다. Conditional law에서는 \(Z=1\), cross-section-weighted law에서는 \(Z=\sigma\)다.

\[
N_e=2Z,\qquad N_p=Z,
\]
\[
P_s=\int\sum_{i\in s}q_i\,d\mu,\qquad
R_s=\int\sum_{i\in s}\frac{q_iq_i^T}{m_s}\,d\mu,
\]
\[
K_s=\frac12\operatorname{tr}R_s,\qquad
S_s=\frac12R_s,\qquad J_s=\operatorname{STF}(R_s).
\]

이 문서와 구현의 canonical tensor는 **\(R=\int qq^T/m\)**다. Conditional \(R\)의 단위는 energy이고, cross-section-weighted \(R\)의 단위는 area×energy다. Number density와 relative flux를 적분하기 전의 이 event moment를 곧바로 압력 Pa나 gas stress 진화율이라고 부르지 않는다. \(\sigma=0\)이면 weighted moments는0이며 conditional probability는 정의되지 않는다. 코드에는 조건부 law를 만들지 않고 영의 weighted moments를 반환하는 별도 경로가 있다. [유도 §3](theory/DERIVATION.md), [exact implementation](code/heang_contract/exact_events.py)

독립 이론 검토의 F1은 conditional 식을 weighted 식에 사용할 때의 \(Z\)를 명확히 하는 교정이었다. 최종 유도·machine template·코드는 모두 같은 정규화를 사용하며, F1은 최종 bytes 대조로 종료됐다. [검토 최종 판정](evidence/review/THEORY_REVIEW_FINAL.md)

## 4. Full inclusive electron marginal로 복원되는 ion 정보

고정 입사 \(E\), 동일 frame·preparation·normalization, 완전한 inclusive coverage, 같은 event-support ledger를 전제로 full electron DDCS는 electron \(N_e,P_e,R_e,K_e,J_e\)를 결정한다. 여기서 event momentum·energy conservation을 적용하면

\[
P_p=-P_e,\qquad K_p=Z(E-I)-K_e
\]

를 얻는다. 따라서 **ion 평균 운동량과 ion energy, 즉 recoil tensor의 trace까지는 복원**된다. \(Z=1\)일 때는 \(K_p=E-I-K_e\)다. [유도 §3–4](theory/DERIVATION.md)

Full ion second tensor에는 electron-pair cross moment가 들어간다.

\[
C_{12}=\int(q_1q_2^T+q_2q_1^T)\,d\mu,
\qquad
R_p=\frac mM R_e+\frac1M C_{12}.
\]

그 trace는 이미 에너지 ledger가 정한다.

\[
\operatorname{tr}C_{12}
=2MZ(E-I)-2(M+m)K_e.
\]

추가 입력은 \(C_{12}^{\rm STF}\), 또는 이를 결정하는 호환 가능한 same-law recoil tensor다. 완전한 joint event law, coincidence/event data, source-qualified joint-moment certificate가 이를 공급할 수 있다. 같은 preparation·normalization·frame의 recoil measurement와 공통 event support 증거로 필요한 moments를 직접 공급하는 경로도 가능하다. 특정 physical model이 추가 상관 관계를 정한다면 그 모델과 uncertainty를 계약에 넣어 사용할 수 있다. [유도 §4](theory/DERIVATION.md)

## 5. 같은 electron marginal과 다른 ion STF를 갖는 구성

이번에 새로 만든 구성은 필요한 상관 정보가 어떤 양인지 직접 드러낸다. \(W>0\), \(m,M>0\)에서

\[
p^2=\frac{mM}{m+M}W
\]

로 두고, \(s=\pm1\)을 같은 확률로 선택한다. \(b(\phi)\)는 \(a\)에 수직인 단위원에서 균등한 방위각을 갖는다. Conditional event law A와 B를 다음과 같이 정의했다.

\[
\begin{aligned}
A:\quad &q_1=\frac{sp}{\sqrt2}(a+b),\quad
q_2=\frac{sp}{\sqrt2}(a-b),\quad
q_p=-s\sqrt2p\,a,\\
B:\quad &q_1=\frac p{\sqrt2}(sa+b),\quad
q_2=\frac p{\sqrt2}(-sa+b),\quad
q_p=-\sqrt2p\,b.
\end{aligned}
\]

두 law 모두 매 event마다 운동량과 에너지가 보존된다. \(q_1\cdot q_2=0\), \(|q_1|^2=|q_2|^2=p^2\), \(|q_p|^2=2p^2\)이므로 전체 outgoing kinetic energy는 \(p^2/m+p^2/M=W\)다. A는 \(b\mapsto-b\), B는 \(s\mapsto-s\)로 전자 exchange symmetry가 성립한다. 연속 균등 방위각에서 두 law 모두 axial symmetry를 갖는다. [구성·증명](theory/DERIVATION.md), [witness 명세](theory/WITNESS_SPEC.json)

두 전자의 에너지는 \(p^2/(2m)\)이며, 각 전자 marginal의 \(\cos\theta\)는 \(\pm1/\sqrt2\)에 같은 확률을 갖고 방위각은 균등하다. 임의의 적분 가능한 전자 관측함수 \(f\)에 대해

\[
\left\langle f(q_1)+f(q_2)\right\rangle_A
=\left\langle f(q_1)+f(q_2)\right\rangle_B
\]

임을 변수 치환으로 보였다. 일치하는 것은 선택한 몇 개의 전자 모멘트만이 아니라 **complete inclusive electron measure**다. 두 law의 차이는 같은 event에서 두 전자의 longitudinal 부호를 어떻게 짝짓는가에 있다. [연속 방위각 증명](theory/DERIVATION.md)

그 결과

\[
K_e=\frac{p^2}{m},\qquad D_e=\frac{K_e}{4},\qquad
K_p=\frac{p^2}{M}
\]

는 같고, ion의 anisotropy는

\[
D_p^A=K_p,\qquad D_p^B=-\frac{K_p}{2},
\]
\[
J_p^A-J_p^B=3K_p\left(aa^T-\frac13\mathbf1\right)
\]

로 달라진다. 동일한 inclusive electron marginal·total cross section·scalar energy ledger만으로는 이 두 양의 kinematically admissible law 중 하나를 선택할 수 없다. 이 구성의 귀결은 지정된 inclusive-only interface에 필요한 추가 correlation field다. 실제 H1 quantum scattering이 A나 B라는 경험적 주장이나, 다른 물리적 구성 전체를 배제하는 일반 명제로 확장하지 않는다. [유도 §5](theory/DERIVATION.md), [독립 이론 검토](evidence/review/THEORY_REVIEW_FINAL.md)

### 연속 proof와 유한 exact control의 대응

수직 평면의 orthonormal basis \(e_1,e_2\)에 대해

\[
b\in\{e_1,-e_1,e_2,-e_2\},\qquad w_b=\frac14
\]

를 사용하면 \(\langle b\rangle=0\), \(\langle bb^T\rangle=(\mathbf1-aa^T)/2\)가 정확하다. \(s=\pm1\)을 결합하면 law당8 event다. \(N,P,R,C_{12}\)는 이 방위각 변수에 대한2차 이하 모멘트이므로 이 quadrature가 연속 방위각 결과를 정확하게 적분한다. 유한 event 집합의 회전 대칭은 fourfold이며, 연속 분포의 axial symmetry와 구별한다. [유도 §5](theory/DERIVATION.md)

R7에서는 coordinate mass-ratio 사례와 회전된 unequal-mass 사례, 총2 cases×A/B=4 laws의32 events를 저장했다. 이 데이터는 **consistent arbitrary rational kinetic units의 manufactured fixture**이며 경험적 SI source data가 아니다. 특히 \(M/m=1836\) 같은 fixture 값은 measured mass constant의 보정 결과로 사용하지 않는다. C7은 이 저장된32 events와 expected moments를 읽어 새 accumulator와 비교했고 oracle을 다시 생성하지 않았다. [R7 raw 결과](theory/WITNESS_RESULTS.json), [C7 raw 비교](evidence/execution/SAVED_ORACLE_COMPARISON.json)

## 6. Frame·coordinate·flux 계약

Raw moments의 passive Galilean boost와 orthogonal basis 변화는 \(q'=O(q-m_sU)\) 순서로 정의한다.

\[
N_s'=N_s,\qquad P_s'=O(P_s-m_sN_sU),
\]
\[
R_s'=O\left[R_s-UP_s^T-P_sU^T+m_sN_sUU^T\right]O^T.
\]

Reactive source에는 signed number source가 있으므로 \(m_sN_sUU^T\)를 유지한다. Gain-only tensor에 적용되는 양성성은 signed gain-minus-loss source에 대한 요구로 옮기지 않는다. 구현의 RawMoments와 boost는 arbitrary 입력 tensor의 PSD나 physical realizability를 인증하는 도구가 아니다. [유도 §6](theory/DERIVATION.md), [구현](code/heang_contract/exact_events.py)

Stationary target이면 \(E=\zeta E_{\rm lab}\), \(\zeta=(M+m)/(M+2m)\)다. Relative-flux-normalized total cross section의 입사 에너지 parameter를 다시 표시하는 식은

\[
\sigma_{\rm lab}(E_{\rm lab})
=\sigma_{\rm COM}(\zeta E_{\rm lab})
\]

이며, 이 parameter relabeling에 별도의 \(\zeta\)를 곱하지 않는다. 실제 incoming-energy density를 적분하며 변수를 바꿀 때는 그 density에 해당 Jacobian이 필요하다. Outgoing DDCS는 \(d^3q=m|q|\,d\epsilon\,d\Omega\)에 따라 같은 joint event measure 전체를 pushforward한다. 방향이 정의되지 않는 zero momentum에서는 momentum-space measure나 bin pushforward를 사용한다. [유도 §6](theory/DERIVATION.md)

Finite-mass joint density가 \(d\epsilon_1d\Omega_1d\Omega_2\) 형태로 주어지면 \(q_2=r n_2\)의 물리 root를 source가 명시해야 한다.

\[
A r^2+B r+C=0,\quad
A=\frac1{2m}+\frac1{2M},\quad
B=\frac{q_1\cdot n_2}{M},\quad C=A|q_1|^2-W.
\]

비음수 물리 roots의 기여를 모두 합한다. Simple root에서는 radial delta-shell Jacobian \(r^2/|2Ar+B|\)가 필요하다. Coalescing root에서는 measure 또는 정규화된 적분으로 처리하며 분모0에 직접 나누지 않는다. 단일 root를 임의로 선택하거나 source coordinate 변환에서 이 Jacobian을 누락하면 동일한 finite-mass event law를 적분하는 계산이 되지 않는다. 이 계약은 해당 reference와 domain을 요구하지만 이번 단원에서 새 physical amplitude나 differential source를 계산하지 않았다. [유도 §2](theory/DERIVATION.md)

일반 source의 rate는 \(\sigma(E,a;\mathrm{preparation})\)와 relative speed를 사용한다. Explicit unpolarized rotationally invariant preparation이 있을 때만 scalar \(\sigma(E)\)로 축약한다. 독립 이론 검토의 F2는 이 preparation 의존성의 표기와 machine interface를 맞추는 교정이었으며 종료됐다. 서로 맞지 않는 CCC total과 Le–Cambier partition을 그대로 결합하는 것은 이 계약이 허용하지 않는다. 별도 hybrid model을 연구할 경우에는 새 law identity, compatibility와 uncertainty 의무를 먼저 정해야 한다. [유도 §7](theory/DERIVATION.md), [이론 검토 F2](evidence/review/THEORY_REVIEW_FINAL.md)

## 7. 실행 가능한 provider gate와 과학적 의미

Precheck는 sigma, electron marginal, moments, recoil/correlation이 같은 source/law/preparation/angular-source identity에 결합됐는지 확인한다. 제공된 실제 payload bytes의 SHA256을 검증하며, fixture CLI는 실제 payload 내부의 identity, normalization, 단위, 질량·threshold, COM-energy interval과 frame 의미까지 대조한다. Digest binding은 stale 또는 서로 다른 자료가 실수로 결합되는 문제를 식별한다. 원전 내용의 물리적 타당성을 자동으로 입증하지는 않는다. [Metadata 구현](code/heang_contract/metadata.py), [CLI](code/heang_contract/cli.py), [API 설명](code/README.md)

| Structural 결과 | 의미 | 후속 의무 |
|---|---|---|
| `REJECTED_INCONSISTENT` | 잘못된 형식, 상충하는 identity/domain, digest 불일치 등의 구체적 결함 | Raw input과 실패를 보존하고 그 결함을 수정 |
| `DEFERRED_DEPENDENCY` | 실제 bytes, frame/root/Jacobian, candidate certificate, uncertainty 등 필수 입력 미비 | 빠진 특정 입력을 공급 |
| `PARTIAL_SCOPED` | 일관된 일부 범위가 있으나 coverage 또는 joint correlation이 제한됨 | 가용 capability와 빠진 범위를 분리해 후속 판단 |
| `STRUCTURALLY_READY_REQUIRES_SOURCE_REVIEW` | 현재 선언과 content binding이 구조적으로 일관됨 | 독립 physical source review 필요 |

위 네 상태 모두 `empirical_admission=false`, `runtime_activation=false`다. Source의 calibration reference가 있다는 사실과 그 calibration이 실제로 충분하다는 판정은 구별한다. Physical normalization·shape·correlation·coverage uncertainty와 quadrature·floating-point error도 별도 ledger에 남는다. 기존 HE38 raw \(10^{-8}\) gate는 선택된 모델 내부의 수치 기준으로 재사용하며, 새 provider의 empirical error bar로 사용하지 않는다. [유도 §8–9](theory/DERIVATION.md), [Provider template](theory/PROVIDER_TEMPLATE.json)

HE-X1의 `PASS / FAIL / INDETERMINATE` namespace도 그대로 보존했다. 기존32-fixture PASS는 algorithm/theorem evidence이며 새 candidate의 판정이 아니다. Candidate에는 현재 moment payload와 일치하는 `candidate_moments_sha256`, certificate provenance, 그 candidate의 실행·해석 증거가 따로 필요하다. Manufactured example의 PASS는 direct event-support algebra에 의한 analytic application으로 기록했고, 과거 X1 실행을 새 candidate execution으로 표시하지 않았다. [구현 설명](code/README.md), [예제 candidate](code/example/candidate.json), [C6 raw 결과](evidence/execution/AFFECTED_CONTROLS_RAW.json)

## 8. 실제 실행 결과와 독립성

| 새 실행 | 입력·검사 범위 | 실제 결과 | 원본 근거 |
|---|---|---|---|
| R7 exact witness | 2 cases,4 laws,32 events | 252/252 predicates PASS | [Raw](theory/WITNESS_RESULTS.json), [receipt](theory/WITNESS_RECEIPT.json) |
| C6 affected controls | Exact event·normalization·frame·signedN·실패경로·binding·partial metadata·CLI | 51/51 PASS, failure0 | [Raw](evidence/execution/AFFECTED_CONTROLS_RAW.json), [receipt](evidence/execution/C6_RECEIPT.json) |
| C7 saved-oracle correspondence | 저장된 R7의2 cases/4 laws/32 events를 새 accumulator와 대조 | 28/28 grouped comparisons PASS, oracle regeneration0 | [Raw](evidence/execution/SAVED_ORACLE_COMPARISON.json), [receipt](evidence/execution/C7_RECEIPT.json) |

252 predicates,51 control cases,28 grouped comparisons는 서로 다른 계수 단위다. 이를 하나의 독립 물리 사례 수처럼 합하지 않는다. C7의28 groups는 law당 electron \(N,P,R\), proton \(N,P,R\), \(C_{12},D_e,D_p,K_e,K_p\)의7개 비교 groups에 대응한다. [C7 비교 코드](code/compare_saved_witness.py), [C7 raw](evidence/execution/SAVED_ORACLE_COMPARISON.json)

C6에는 유리수 해석 기대값뿐 아니라 \(\sigma=0\), signed reactive \(N\), 비직교 frame, momentum·energy support 위반, binary-float/bool 입력, stale candidate certificate, actual payload corruption, partial support, unknown physical uncertainty, CLI의 nonzero exit 경로가 포함됐다. C7은 R7 생성기를 재실행하지 않고 저장 oracle을 소비했다. C6의 해석 기대값과 C7의 독립 저장 oracle은 서로 다른 계산 경로로 새 구현을 점검한다. 일반 연속 source와의 일치 범위는 analytic proof와 향후 source qualification에 의해 정해진다. [C6 raw](evidence/execution/AFFECTED_CONTROLS_RAW.json), [C7 raw](evidence/execution/SAVED_ORACLE_COMPARISON.json)

독립 이론 검토는 corrected normalization, preparation-aware rate, A/B 구성, frame 및 root/Jacobian 계약을 읽고 `PASS_SCOPED`, open theory findings0으로 판정했다. C9 최종 코드 검토도 실제 source와 C6/C7 receipts를 대조하여 PASS_SCOPED, open code findings0으로 판정했다. 112개 행정 identity 대조는 추가 과학 case 수에 더하지 않는다. Reviewer의 과학 실행과 project import는0이다. [이론 검토](evidence/review/THEORY_REVIEW_FINAL.md), [코드 최종 검토](evidence/review/CODE_REVIEW_FINAL.json)

## 9. 예산과 실행 재사용

이번 HE-ANG-CONTRACT는 기존 단원에서 남았다고 추정한 시간을 가져오지 않고 **새 CPU10 s / wall30 s / address-space256 MiB** 한도를 동결했다. Per-invocation 한도는 CPU2 s / wall5 s였다. 아래 값은 각 새 scientific child와 그 wrapper가 실제 charge한 기록이다. 파일·archive·API 게시 bookkeeping 비용과 분리되어 있다. [동결 예산](BUDGET.json), [누적 ledger](RESOURCE_LEDGER.json)

| 실행 | Charge CPU s | Charge wall s |
|---|---:|---:|
| R7 | 0.211275 | 0.1680309520015726 |
| C6 | 0.177225 | 0.17479019000165863 |
| C7 | 0.203702 | 0.1739993850060273 |
| 기록된 누적 | 0.5922019999999999 | 0.5168205270092585 |
| 이 새 계약의 잔여 | 9.407798 | 29.48317947299074 |

새 ledger에 scientific child3건의 START/FINISH가 있고 현재 unknown-cost records는 비어 있다. 이 잔여는 해당 contract controls의 잔여일 뿐, 새 provider scan·IVP나 다른 단원으로 이전되는 예산이 아니다. 실행을 더 해야 할 구체적인 의무가 없으면 완료 증거를 재사용한다. [누적 ledger](RESOURCE_LEDGER.json)

과거 X1에는 Python 진입 전 실패 wrapper의 CPU가 `UNKNOWN_NOT_ZERO`로 남아 있으며, 그 성공 실행 시간만 차감해 과거 전체 residual budget을 확정하지 않는다. HE38 원 ledger와 ANGTHERM/D10의 consumed·unknown 기록도 보존한다. 이 문서의 새0.592202 CPU s를 모든 역사적 연구의 전체 계산량이라고 해석하지 않는다. [과거 예산·소유권](evidence/intake/BUDGET_AND_OWNERSHIP.json), [HE38 원 기록](evidence/intake/HE38_RESOURCE_REUSE.json)

이번 단원의 새 physical-provider scan, 새 문헌 scan, IVP, benchmark, render와 HE-X1/HE38/HE32 replay는 모두0이다. Source·frame contract의 새 exact evidence3건과 복원·저장 bookkeeping을 구별해 집계했다. [Intake](evidence/intake/INTAKE_KO.md), [C6 receipt](evidence/execution/C6_RECEIPT.json), [C7 receipt](evidence/execution/C7_RECEIPT.json)

## 10. 다음 DAG와 남은 실제 입력

후속 순서는 다음과 같다. [NEXT_DAG](NEXT_DAG.json)

| 노드 | 현재 역할·입력 상태 | 다음에 필요한 근거 |
|---|---|---|
| HE-X1 | `COMPLETE_SCOPED_REUSED` | 완료 theorem·fixtures·review 재사용 |
| HE-ANG-CONTRACT | 본 단원의 source/frame/event 계약 및 exact implementation | COMPLETE_SCOPED; 이론·구현 독립 검토 및 단계별 전달 기록 |
| HE-ANG-SOURCE | `SOURCE_INPUT_PENDING` | Immutable differential law payload 또는 same-law moment certificate, actual coverage, frame/flux/preparation, recoil correlation, calibrated uncertainty |
| HE-EXCHANGE | `SOURCE_INPUT_PENDING` | HE35 조건부 pair 근거를 재사용하고 source-qualified elastic transport coefficient·timescale 공급 |
| HE-RESERVOIR | `SOURCE_INPUT_PENDING` | 실제 spectrum·thermal reservoir, early-z provider 또는 later-start matching IC, 선택한 추가 channel의 source ownership |
| HE-CLOSURE | 위 source·exchange·reservoir 입력에 의존 | Species \(T,u,\pi\), source projection과 reduction error, \(\pi_b=\sum_s\pi_s\)의 정당화 |
| HE-FEEDBACK | `NOT_SCHEDULED` | 먼저 저장된 background에서 제한 gas control, 이후 별도 metric feedback 계약 |

새 angular law를 채택하면 그 source/model identity를 새로 pin하고 angular gain moments와 그에 의존하는 coefficients를 검증한다. HE38의 kinetic convention·보존식은 가정이 같으면 재사용하지만 uniform-angular law에 의존한 coefficients를 자동으로 옮기지 않는다. Total cross section이나 energy-sharing law까지 바뀌면 해당 radial moments·partition compression도 영향 범위에 포함한다. [유도 §10](theory/DERIVATION.md)

원래 목표의 baryonic anisotropic stress, 열·광원 진화, CI/DR/CX와 추가 종·핵반응 daughter 범위는 이 의존성들을 통해 별도 계약으로 이어진다. Positive birth kinetic energy와 thermalization rate를 동일시하지 않고, nonbaryonic matter stress와 gas \(\pi_b\)를 계속 구별한다. [고정 handoff의 보존 범위](evidence/intake/central_snapshot/research/orchestration_longterm_20261023/assembly/HANDOFF_BASS_HE_KO.md)

단계별 실제 preflight, backup ACK, publication 상태는 [DAG.json](DAG.json)에 귀속한다. 최종 publication pin은 [게시 identity](delivery/PUBLISHED_PINS.json), 원격 저장 receipt는 delivery/의 실제 ACK와 [두 종류 handoff 중 연구용](HANDOFF_RESEARCH_KO.md)·[실행자용](HANDOFF_EXECUTOR_KO.md)에 연결한다. 과학적으로 얻은 계약과 검증 결과는 이 전달 상태와 분리해 유지한다.
