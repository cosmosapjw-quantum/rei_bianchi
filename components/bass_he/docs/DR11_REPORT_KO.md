# BASS_HE DR11A–B — cutoff migration, 고정 원자 shell, 새 S-branch pilot

2026-09-27 · PAPER_DERIVED_REIMPLEMENTATION / NOT_AUTHOR_CODE

## 0. 판정과 실제 수행 범위

DR10D의 PR #8 head `6dee41e37edae719225ec0fd60d36d39399522ed`를 원격 기준으로 삼았다. 이번 작업은 **DR11A first-hit migration / shell-coverage 명세 및 진단 구현**과 **DR11B 새 S-branch 3개의 경량 pilot**이다. DR11 전체의 Nmax-converged 충돌 계산이나 ionization admission을 완료한 것이 아니다.

- DR11A: finite-Markov migration 항등식, disjoint channel ledger, fixed-separated-shell coverage를 구현하고 새 테스트로 검증했다.
- DR11B: `3pσ–4pσ`, `4pσ–5pσ`, `3dσ–4dσ`를 실제 spectral/monodromy 계산했다. 실수축에서 두 named state를 각각 추적했으며, CF depth 96/160을 비교했다.
- 전체 Nmax=4/5 branch enumeration, 새 Δ(b), 해당 전체 P_rot와 Eq50/54, 물리적 단면적은 미실행이다.
- 과거 DR10C/D 결과는 해당 frozen scope로 보존한다. 과거 과학 suite를 새로 재실행하지 않았다.
- 원격 push / 새 PR / Google Drive+Dropbox 업로드는 실행되지 않았다. 이 패키지의 로컬 무결성·복원 검증과 원격 backup 검증은 구별한다.

기준 문헌은 Gusev–Solov'ev–Vinitsky, *Computer Physics Communications* 286 (2023) 108662, DOI `10.1016/j.cpc.2023.108662`이다. 특히 p.5 Eq17–18, p.8 S-series, p.10 Q-series와 antibounding 경고, p.11–12 Eq49–54를 원문 페이지 이미지와 함께 확인했다. Janev–Pop-Jordanov–Solov'ev 1997의 DR10C 비교는 부모의 scoped evidence로 승계했으며 이번 새 branch의 독립 저자 수치 oracle로 사용하지 않았다.

## 1. 가장 중요한 정정: cutoff 이동은 relabeling이 아니다

Nmax=N인 계산은 united-atom shell N을 absorbing boundary로 사용한다. Nmax=M>N으로 확장하면 N≤Nu<M 상태들은 이제 reversible, resolved 상태가 된다. 따라서 N→N+1에서 새롭게 resolved되는 것은 **기존 경계 shell N**이며, shell N+1은 새로운 경계다.

그 결과 기존 sink에 들어갔던 경로는 세 가지로 나뉜다.

1. 이미 resolved였던 Nu<N 상태로 되돌아온다.
2. 새로 resolved된 N≤Nu<M 상태에 남는다.
3. 새 경계 Nu=M까지 도달하여 unresolved로 남는다.

첫 항을 빼고 `old sink = newly resolved bound + new sink`로 쓰면 일반적으로 보존식이 성립하지 않는다. 단순한 후처리 분류가 아니라, 기존 absorbing event를 reversible event로 바꾼 **새 동역학**을 전파해야 한다.

### 1.1 언제나 성립하는 first-hit 분해

확장된 M 계산의 경로에서 Nu≥N을 한 번이라도 방문했는지 표시한다. 이 tag는 finite stochastic Eq50의 경로 bookkeeping이며, coherent quantum histories를 측정한다는 뜻이 아니다.

그 방문 확률을 H_N^(M), 방문 후 최종적으로 Nu<N인 확률을 R_N^(M), N≤Nu<M인 확률을 B_[N,M)^(M), 최종 upper-boundary population을 S_M이라 하면

\[
H_N^{(M)}=R_N^{(M)}+B_{[N,M)}^{(M)}+S_M.
\]

이 식은 확장된 **동일 event history 내부**의 정확한 분해다. 분류 전후의 총 population은 전혀 달라지지 않는다.

이제 별도로 계산한 옛 cutoff의 sink S_N과 비교하려면

\[
D_{\rm pre}=H_N^{(M)}-S_N
\]

을 반드시 보존해야 한다. 일반적인 비교식은

\[
\boxed{S_N-S_M=R_N^{(M)}+B_{[N,M)}^{(M)}-D_{\rm pre}.}
\]

D_pre=0은 first hit 이전의 event ordering, lower-state transition probabilities, rotation과 새 high-state coupling의 영향이 일치할 때만 성립한다. 새로운 nonadjacent Q coupling이 낮은 상태에서 추가로 출발하면 기존 모델과 pre-hit dynamics부터 달라질 수 있다. 단지 Nmax만 3→4→5라는 이유로 D_pre=0, sink의 단조 감소, 또는 고정 채널의 수렴을 가정하지 않는다.

### 1.2 구현

`src/bass_he/nmax_migration.py`는 never-hit vector U와 already-hit vector H를 전파한다. 매 event 및 rotation 뒤에 U의 Nu≥N 성분을 H로 옮긴다. 이미 H에 들어간 경로는 다시 U로 돌아가지 않는다. 물리적 상태는 낮은 Nu로 돌아갈 수 있지만 **방문 기록**은 지우지 않는다.

T를 column-stochastic event, L을 Nu<N의 diagonal projector, K=I−L이라 하면

\[
U'=LTU,\qquad H'=TH+KTU,
\]

따라서 U'+H'=T(U+H)이다. 이 수학적 증명에 더하여 기존 `apply_eq50()` marginal과 직접 비교하고, 별도의 명시적 path-tree enumeration 및 absorbing first-hit oracle로 검증했다. Markov chain의 tag를 실제 coherent scattering amplitude에 그대로 적용하면 다른 문제이므로 허용하지 않는다.

## 2. N=3→4→5 최소 ladder의 exact 결과

아래 확률 p,q,r은 0≤p,q,r≤1의 **독립 변수**다. 원자 충돌의 에너지·impact parameter에서 얻은 확률이나 물리적 단면적 수치가 아니다.

초기 L=Nu2, B=Nu3, C=Nu4, D=Nu5에 대해 incoming sequence는 p,q,r, outgoing은 r,q,p, rotation은 identity로 둔다. 마지막 shell만 absorbing이다. 이는 검증된 S_pσ branch의 Re(Rc) ordering과 맞는 최소 구조지만, 실제 전체 충돌 network가 아니다.

### 2.1 3→4

Nu3을 sink로 둔 옛 결과는 S3=p(2−p)이다. Nu3을 reversible로 풀고 Nu4를 sink로 둔 새 결과는

\[
R_{<3}=p^2(1-q)^2,
\]
\[
P_{Nu=3}=p(1-p)\{1+(1-q)^2\},
\]
\[
S_4=pq(2-q).
\]

세 항의 합은 정확히 p(2−p)이다. p=1,q=0이면 old sink=1이지만 확장 모델에서는 전부 Nu2로 돌아와 최종 Nu3,Nu4 population이 모두 0이다.

예를 들어 p=0.7,q=0.2에서

| 항목 | 확률 |
|---|---:|
| 옛 S3 | 0.9100 |
| Nu2로 귀환한 tagged population | 0.3136 |
| 새로 resolved된 Nu3 population | 0.3444 |
| 새 S4 | 0.2520 |

마지막 세 항의 합이 0.9100이다. `0.3444+0.2520`만으로 migration을 설명하면 0.3136이 누락된다.

### 2.2 4→5와 3→5

Nmax5의 최종 벡터는

\[
P_L=(1-p)^2+p^2\{(1-q)^2+q^2(1-r)^2\},
\]
\[
P_B=p(1-p)\{1+(1-q)^2+q^2(1-r)^2\},
\]
\[
P_C=pq(1-q)\{1+(1-r)^2\},\quad S_5=pqr(2-r).
\]

old S4로부터 Nu<4로 돌아온 총 tagged mass는

\[
R_{<4}=pq^2(1-r)^2
\]

이며 S4=R_<4+P_C+S5이다. Nu3 경계를 기준으로 기록한 귀환량은

\[
R_{<3}=p^2\{(1-q)^2+q^2(1-r)^2\}
\]

이고 S3=R_<3+P_B+P_C+S5이다. Wolfram와 독립 SymPy 계산에서 두 residual 모두 0이었다. Wolfram gateway의 undefined-symbol warning 발생 사실도 기록했다. 따라서 '경고 없는 Wolfram 실행'이라고 보고하지 않는다. 반환된 exact 결과와 독립 symbolic 계산은 일치한다.

4096개의 synthetic (p,q,r)에 대한 새 stress 결과:

| 검사 | 최대 절대 오차 |
|---|---:|
| tagged marginal − current apply_eq50 | 0 |
| current apply_eq50 − analytical four-state ladder | 2.220446049250313e−16 |
| H3 − old S3 | 3.3306690738754696e−16 |
| H4 − old S4 | 2.220446049250313e−16 |
| N3 migration closure | 2.220446049250313e−16 |
| N4 migration closure | 1.3877787807814457e−16 |

이것은 보존·분류 알고리즘의 검증이지, 물리적 Nmax convergence 측정이 아니다.

## 3. united-atom N과 separated-atom n을 구별해야 한다

CPC Eq17에서 Z1=1,Z2=2이면 integer branch가 항상 적용되어

\[
q=2n_2+n,\quad n=n_1+n_2+|m|+1,\quad k=n_1,
\]
\[
N=k+q+|m|+1=\boxed{2n+n_2}.
\]

따라서 H(n)의 parabolic subchannels는 2n≤N≤3n−1에 걸쳐 있다. 모든 성분을 absorbing boundary **아래**에 두려면

\[
\boxed{N_{\max}\ge 3n}
\]

이 필요하고, 이 correlation-map의 표현 완결성 기준에서는 충분하다. 이것은 numerical/dynamical convergence의 충분조건이 아니다.

특히 H(n=2)의 세 folded-|m| 성분은

| (n1,n2,|m|) | united state | Nmax5에서의 역할 |
|---|---|---|
| (1,0,0) | (4,2,0)=4dσ | resolved |
| (0,0,1) | (4,3,1)=4fπ | resolved |
| (0,1,0) | (5,4,0)=5gσ | absorbing boundary |

즉 Nmax3→4→5 계획은 유용한 cutoff diagnostic이지만, **H(n=2) shell-total excitation을 완결된 observable로 비교하기에는 Nmax5도 부족**하다. H(n=2) coverage의 최소 sentinel은 Nmax6이다.

또한 Appendix A에서 3dσ는 He+(n=2,n1=0,n2=1,m=0)로 간다. 이 상태는 Nmax3에서 sink지만 Nmax4에서 resolved bound-model channel이 된다. 새로 풀린 것이 'He+(n=4)'가 아니다.

### 3.1 fixed-shell coverage 표

아래 표의 숫자는 probability가 아닌 folded-|m| parabolic channel 수다. 별도의 2배 degeneracy를 곱하지 않았다.

| separated shell | Nmax3 resolved/전체 | Nmax4 | Nmax5 | 전 성분을 sink 아래에 두는 최소 Nmax |
|---|---:|---:|---:|---:|
| H(n=1) | 1/1 | 1/1 | 1/1 | 3 |
| H(n=2) | 0/3 | 0/3 | 2/3 | 6 |
| He+(n=2) | 2/3 | 3/3 | 3/3 | 4 |
| He+(n=3) | 0/6 | 5/6 | 6/6 | 5, conditional map |

H-side result는 source Eq17에서 직접 유도했다. Z2-side의 N>3 map은 현재 `correlation.py`의 ordered-complement extension에 조건부이다. published Eq18의 prime/condition ambiguity가 있다는 부모 코드의 경고를 없애지 않았다. 단순한 round-trip consistency를 독립 물리 검증으로 승격하지 않는다.

### 3.2 channel ledger 계약

H(1s) entrance의 finite-model 최종 population은

\[
P_{H1s}+P_{H,\mathrm{exc},\mathrm{resolved}}
+P_{\mathrm{He}^+,\mathrm{resolved}}+P_{\mathrm{unresolved}}=1
\]

로 분리한다. upper-shell population을 bound와 unresolved에 이중 집계하지 않는다. 각 행의 formal asymptote는 참고 metadata이며 sink population을 그 bound yield로 재해석할 권한이 아니다. `survival_Z1_1s` 역시 elastic cross section이 아니다. Identity tail을 적분하지 않는다.

## 4. 세 개의 새 S-branch: 실제 numerical pilot

새 branch는 inherited exact-current `spectral.py`와 `arseny_reimpl` dependencies에서 계산했다. 단지 두 CF root가 같아졌다는 이유로 승인하지 않았다.

검증 절차는 F=0, spectral Jacobian rank loss, nonzero fold transversality/curvature 확인 후, Rc+0.001의 실수부를 따라 실수축에서 **서로 다른 named states를 독립적으로 continuation**하는 것이다. 반지름 0.001, 한 바퀴 48 steps로 한 바퀴에서 교환되고 두 바퀴에서 복원되는지 검사했다. CF depth 96과 160에서 각각 시행했다.

| pair | Rc, a.u. (depth160) | depth96→160의 abs(ΔRc) | named swap relative error | named restore relative error |
|---|---|---:|---:|---:|
| 3pσ–4pσ | 0.490824831704868 + 0.720151294265355 i | 1.6653e−16 | 1.64075e−11 | 2.48402e−12 |
| 4pσ–5pσ | 0.486348808711165 + 0.709626684949054 i | 2.4825e−16 | 1.60967e−12 | 3.55877e−12 |
| 3dσ–4dσ | 1.986110196585769 + 1.364958504266939 i | 0 at double precision | 4.02663e−12 | 6.20876e−12 |

세 번째 pair의 CF residual은 1.1022e−11, rank ratio는 4.4459e−11이다. 따라서 두 depth에서 같은 double value라는 사실을 16자리의 total absolute accuracy 증명으로 해석하지 않는다. 첫 두 pair의 residual은 각각 1.2413e−15, 5.0197e−15이다.

`3dσ–4dσ`는 이 작업에서 특별히 중요하다. 3dσ는 He+(n=2), 4dσ는 source Eq17에 의해 H(n=2,n1=1,n2=0,m=0) 쪽으로 상관된다. 따라서 기존 top-shell 해제는 더 높은 He+ bound capture만 여는 것이 아니라, **H excited-bound 채널과 연결된 경로도 연다.** 그러나 아직 이 branch의 Δ(b), probability, coherent path interference 및 full-network contribution을 계산한 것은 아니다.

CPC p.10은 branch의 위치와 S-series 관계에 따라 encircling 후 bound state 대신 virtual/quasistationary sheet에 도달할 수 있음을 경고한다. 따라서 일반화한 N>3 enumeration에서도 named endpoint sewing이 필요하다. 이번 세 결과는 명시한 path와 finite-CF approximation 안의 수치 확인이지, 모든 가능한 contour/higher-branch topology의 전역 완결성 또는 author-code agreement가 아니다.

### 4.1 계산 비용

depth96의 세 pilot은 약 5.70, 6.63, 7.66초, depth160은 10.25, 10.99, 12.86초였다. 첫 3pσ–4pσ fold 탐색 0.775초는 별도 보존·재사용했다. 각 two-circle 검사에서 192회 complex term solves가 수행되며 실수축/수직 anchor와 fold 탐색의 호출은 별도다. GPU를 사용하지 않았고 이 세 pilot을 위해 local heavy run이 필요하지 않았다. 전체 Nmax enumeration 및 b/E quadrature의 비용은 아직 측정하지 않았다.

## 5. 복구와 검증 provenance

컨테이너의 직접 GitHub 접속은 DNS 해석에 실패했다. GitHub connector로 PR7/8의 exact heads와 소스 tree를 읽었다. Library에서 AUDIT1 git bundle을 실제 복원했지만, 이것을 AUDIT7 전체 checkout이라고 부르지 않았다.

복원된 AUDIT1 안의 `arseny_reimpl` 13개 파일, `bass_he/{__init__,spectral,transport}.py` 3개 파일은 현재 PR8 tree와 **Git blob identity가 모두 일치**했다. 이 16개만 격리된 execution snapshot으로 가져왔다. AUDIT1의 오래된 geometry/rotation 파일은 이 snapshot에 포함하거나 실행하지 않았다.

실행 전에 각 blob SHA1과 파일 SHA256/크기를 `DR11A_RECOVERY.json`에 기록했다. 새 기능은 별도 `nmax_migration.py`에만 추가했다. 기존 Eq50나 correlation 함수를 변경하지 않았다. full audit7 install/전체 suite 통과 주장은 없다.

테스트 과정의 RED 기록은 구현 부재로 실패한 의도적 TDD evidence다. first-hit/ledger 19개와 shell-coverage 4개의 새 테스트가 각각 PASS했다. 기존 42-test compatibility suite를 반복 실행하지 않았다. 최종 파일 검증 receipt가 해당 snapshot과 실제 추가 테스트 결과를 기록한다.

source PDF는 패키지에 포함하지 않는다. source는 bibliographic identity, 읽은 page 범위, 코드 내 출처와 report로 추적한다.

## 6. 닫힌 것과 닫히지 않은 것

닫힌 scoped claim:

`FIRST_HIT_MIGRATION_REQUIRES_RETURN_CHANNEL`

`FIXED_SEPARATED_SHELL_COVERAGE_REQUIRED`

`H_n_COMPLETE_RESOLVED_COVERAGE_REQUIRES_NMAX_GE_3n`

`THREE_NEW_S_BRANCHES_NAMED_PATH_FOLD_CHECKED__FINITE_CF_DEPTH_STABLE`

열린 claim:

`FULL_NMAX_4_5_NETWORK_NOT_EXECUTED`

`BOUND_CHANNEL_DYNAMICAL_CONVERGENCE_NOT_ESTABLISHED`

`CONTINUUM_IONIZATION_NOT_ADMITTED`

특히 Nmax sink가 작거나 연속 cutoff에서 비슷하다는 것만으로 disjoint continuum ionization을 승인하지 않는다. 모형의 cutoff 안정성과 물리적 continuum observable의 식별은 별도 문제다. superpromotion limit에 대한 정당화 또는 독립적으로 continuum를 구분하는 flux/pseudostate/benchmark 등의 authority가 필요하다.

## 7. 다음 exact node

`DR11C_NMAX4_BRANCH_COMPLETION_AND_MATCHED_CHANNEL_PILOT`

진행 순서는 다음과 같다.

1. DR11 결과의 remote publication/backup barrier를 먼저 닫는다. 현재는 local archive와 additive patch 제공 단계이며 두 provider upload ACK가 없다.
2. 새 source-bound registry를 만든다. 이번 세 S-branch를 import하고 `3dσ–4fσ` 등 N=3→4 Q branches와 나머지 S/m≠0 branches를 하나씩 찾는다. 단순 adjacency 슬롯 목록을 실제 branch 목록으로 부르지 않는다. Nonadjacent Q 및 virtual-sheet caveat도 따로 기록한다.
3. named-sheet sewing이 확인된 branch만 새 Δ(b) 계산에 넣는다. frozen exponent policy를 기록하며 기존 source-factor2 판정과 독립인 새 ambiguity를 만들지 않는다. legacy `stueckelberg_delta()`가 internally duplicate-root solver를 호출한다는 점을 피하고, 이미 인증된 Rc를 사용하는 current certified geometry route로 연결한다.
4. Nmax4에서 기존 Nu3 states가 resolved되므로 해당 rotational blocks와 outward reversible returns를 포함한다. 현재 scoped assembler의 `Nmax != 3` guard를 그냥 제거하는 방식은 금지한다.
5. 동일한 energy/impact-parameter nodes, 동일한 공통 separated-channel projectors, boundary/omitted coverage metadata로 Nmax3/4를 비교한다. H_N^(M), D_pre, returned mass, newly resolved mass, new unresolved mass를 함께 저장한다.
6. 통과 후 Nmax5로 확장한다. H(n=2) shell-total이 목표라면 Nmax6 coverage sentinel을 추가한다. 표현 완결성 PASS 뒤에도 dynamical convergence는 별도 검증한다.
7. 각 단계의 measured runtime과 실패 분포로 sandbox 또는 local heavy handoff를 결정한다. 현재 세 소규모 pilot만으로 전체 계산 비용을 추정 확정하지 않는다.

이 다음 단계가 물리적 bounded-channel convergence를 확인하더라도, ionization은 별도 continuum authority가 닫힐 때까지 비활성 상태다.

## 자료 안내

아래 경로는 standalone archive의 루트 기준이다. Additive repository patch에서는 원시 JSON evidence를 `evidence/DR11_SNAPSHOT.json`에도 합본으로 보존한다.

- `evidence/DR11A_MIGRATION_STRESS.json`: 4096-set exact-structure stress.
- `evidence/DR11A_SYMBOLIC.json`: 독립 symbolic zero residuals.
- `evidence/DR11A_CORRELATION_INVENTORY.json`: Nmax3/4/5 disjoint labels 및 fixed-shell coverage.
- `evidence/S*_NAMED.json`: 각 depth/pair의 원시 certificate와 named monodromy 결과.
- `evidence/DR11_FINAL_STATE.json`: scope/claim/publication machine state.
- `evidence/DR11A_RECOVERY.json`: 원격 기준, local recovery와 exact-current dependency identities.
- `proofs/DR11_SYMBOLIC.wl`: 재실행 가능한 symbolic derivation.
- `proofs/dr11_branch_pilot_v1_executed.py`: 최초 두 pσ branch에 사용한 v1 script. 현재 generic-l script와 구분하여 보존.
