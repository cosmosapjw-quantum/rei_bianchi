# COVARIANT_NATIVE_TRANSPORT 이론·코딩 계약

상태: R1–R10의 **표현 선택·국소 유도·코딩 계약** 완료. 실제 production 구현·회귀·전구간 수렴은 해당 worker와 독립 심사의 다음 의무다. 읽은 base는 PR150 이후 **8aa6cd081f218e3a4ff6180a547c790df234a073**. 완료된 28 checks를 재실행하지 않았다. root는 아래 선택을 이번 구현으로 채택했다.

## R1. 고정 목표와 범위

연속 MD14/BB50K source와 기존 cold Grackle Case-A H/He coupled Newton solver를 유지하면서 반복 physical-energy projection 때문에 생기는 문턱 오염을 제거한다. 먼저 FLRW 전구간 production을 완성하고 표현·source·시간 refinement 이후 승인된 NCP 64 core/128 GB full run으로 연결한다. Broad Bianchi reference-ray 식도 보존하지만 FLRW 결과가 곧 비등방성 전구간 인증은 아니다.

metric (-,+,+,+), proper seconds, proper density cm^-3, photons/H, thermal erg/H, photon energy eV/H를 사용한다. fit threshold와 binding energy는 다른 소유자다. source/chemistry 공통 dt와 이전 clock 변경은 재사용한다.

## R2. 실제 읽은 근거와 재사용

- research/flrw_production_integration_20261015/HANDOFF.json, NEXT_DAG.json, INDEPENDENT_REVIEW.json: clock/IC/standalone D/H 28 checks의 범위와 unresolved transport를 확인했다.
- rust/rei_microphysics/src/axbi_driver.rs: geometry_map → inject → evaluate/chemical_stage → geometry_map; BE photon elimination과 four-variable Newton; 공통 배열 step-doubling; checkpoint와 moments.
- axbi_q_grid.rs: original-source-cell GL8 적분, fixed reference-q N/U/support, geometry observation. 현재 centroid/frozen absorber를 native solver로 오인하지 않는다.
- axbi_q_closure.rs: positive bounded exponential reconstruction과 fit-threshold-cut GL8. 기존 quadrature defect 2e-9는 이번 native moment-match 기준으로 가져오지 않는다.
- axbi_q_reference.rs, axbi_q_advance.rs, axbi_q_capacity.rs: invariant photon, frozen expanding oracle, same-ray merge의 제한. capacity reference는 O((N-cap)N log N)이고 full production 알고리즘이 아니다.
- axbi_sources.rs, atomic_provider.rs, hhe_events.rs: source cell normalization·fit cuts·binding owners.
- 기존 cold bridge의 false-HeII 근거는 재사용하며 숫자를 다시 계산하지 않았다.

원전 문헌은 방법 비교에만 사용했다. Jiang, arXiv:2209.06240는 discrete ordinates와 conservative frequency/spatial FV를 제시한다. Yuan–Cheng–Shu, DOI 10.1137/16M1061072는 DG radiation transfer에서 양성 limiter가 별도로 필요함을 보인다. 이 논문들이 이 repo의 coupled q-cell scheme을 증명했다고 주장하지 않는다.

## R3. 변수와 명제

고정 reference geometry에서 ray j의 단위 방향을 n_ref,j라 한다. photon invariant는 k_i=a_ref,i ε n_ref,i이고

$$R_j(a)=\sqrt{\sum_i(a_{\mathrm{ref},i}n_{\mathrm{ref},j,i}/a_i(a))^2},\quad E_j(a,\epsilon)=R_j(a)\epsilon.$$

현재 방향은 위 벡터를 R로 나눈 값이다. FLRW에서는 R=a_ref/a이며 양·음 방향이 같은 에너지를 갖는다. ε는 reference-frame energy이고 driver의 shear parameter q_ref와 구별한다.

각 고정 ε cell은 (N,Q,L,H)를 저장한다. N=∫dν, Q=∫ε dν이며 실제 support를 [L,H]로 제한한다. 빈 cell은 N=Q=0. N>0이면 L N≤Q≤H N. Q의 단위는 reference-eV/H이다. geometry map에서 N,Q,L,H를 재투영하지 않는다. physical energy는 RQ이다. 재구성은 두 모멘트에 대한 선택된 closure이며 true spectrum의 유일한 복원이 아니다.

## R4. 후보 비교와 채택

| 후보 | 이 문제에서 얻는 것 | 이번 구현 판정 |
|---|---|---|
| physical-E adaptive FV | conservative flux·AMR 가능 | 팽창 advection flux와 moving threshold를 새로 설계해야 하며 반복 투영 결함과 분리된 새 검증 필요 |
| FEM/DG | h/p 적응·고차 표현 | positivity limiter·basis·implicit radiation coupling·mass matrix가 추가됨; 현재 homogeneous 문제의 최소 변경이 아님 |
| 모든 birth의 positive Lagrangian packets | source-free transport와 delta 문턱이 직접적 | 장기 연속 source에서 메모리/비용 증가; 임의 merge는 opacity 오차를 발생시킴. 작은 독립 oracle로 보존 |
| **fixed reference-ε positive two-moment/support FV** | geometry advection 없이 고정 메모리, 기존 four-variable Newton과 공통 step-error 배열 유지 | **이번 채택**. graded grid refinement + threshold-split positive quadrature로 제어 |

동적 cell splitting은 부모 두 모멘트만으로 true child spectrum을 복원하지 못한다. 이번에 없는 정보를 만들어 adaptive라는 이름으로 채우지 않는다. 고정·graded reference grid의 독립 refinement와 cell 내부 quadrature subdivision을 구분한다. 향후 adaptive grid는 conservative child reconstruction 및 그 closure error를 별도 정의한 뒤 추가할 수 있다.

## R5. 실제 유도: source, BE, 보존, 관측량

### Source

source original spectral cell c의 photon fraction f_c와 shape φ(E)=E²/(exp(E/kT)-1)를 유지한다. emitter-frame에서 mapped ε cell과 원래 spectral cell의 교집합 [l,h]를 적분한다.

$$\Delta N_{jc}=\dot N_{\rm src}\Delta t\,w_j^{\rm now} f_c
 \frac{\int_l^h\phi(E)dE}{\int_{E_{c,l}}^{E_{c,h}}\phi(E)dE},$$
$$\Delta Q_{jc}=\dot N_{\rm src}\Delta t\,w_j^{\rm now} f_c
 \frac{\int_l^h E\phi(E)dE}{R_j\int_{E_{c,l}}^{E_{c,h}}\phi(E)dE}.$$

교집합 경계는 R_j ε_edges, native source cell edges 및 native fit cuts에서 분할한다. GL8 positive weights를 사용한다. 원래 photon fraction을 단순히 GL node 수로 나누지 않는다. 원래 source의 Simpson-derived cell mean과 GL8-derived first moment 차이는 source quadrature approximation으로 보고·refine하며, source totals를 새 grid에서 잃은 광자로 조용히 재정규화하지 않는다.

Broad Bianchi에서 fixed reference-angle source는 native driver가 이미 사용하는 현재 J_Ω 가중치의 normalization을 보존한다: w_now=w_ref J/Σw_ref J. R은 dE=R dε에 한 번, J는 각도에 한 번 적용한다. FLRW J=1. local-birth-ray API와 fixed-reference-ray API의 Jacobian 계약을 혼합하지 않는다.

source 13.6..100 eV, z20→4 FLRW이면 ε_max=420 eV. 기존 broad-family guard보다 넓은 ε_max≥433 eV를 유지하고 실제 mapped source support가 밖이면 injection을 transactionally 거부한다. 아래 HI threshold로 적색편이된 광자는 ε domain 안에 남으며 N/U/work inventory에서 사라지지 않는다.

### Quadrature and coupled BE

old cell plus source를 (N*,Q*)라 한다. old state와 reaction geometry만으로 양의 node bank (ε_l,W_l)를 만들고 Newton 밖에서 cache한다:

$$\sum_lW_l=N_*,\quad \sum_l\epsilon_l W_l=Q_*,\quad W_l\ge0,\quad L\le\epsilon_l\le H.$$

fit thresholds는 atomic_provider의 **13.60,24.59,54.42 eV**다. reaction-frame cut은 ε=E_fit/R. binding χ는 HHeModel의 **13.598434599702,24.587389011,54.41776 eV**다. 서로 대체하지 않는다.

trial gas에서 proper absorber n_j를 얻고

$$\lambda_{jl}=c\,n_j\,\sigma_j(R\epsilon_l),\quad
n_l=\frac{W_l}{1+\Delta t\sum_j\lambda_{jl}},\quad
A_{jl}=\Delta t\,\lambda_{jl} n_l.$$

sigma는 physical E에서 원래 AtomicProvider로 평가한다. 같거나 아래인 threshold의 행동도 provider를 따른다. photon survivors는 N_new=Σn_l, Q_new=Σε_l n_l다. 같은 node bank에서

$$\Gamma_j=c\,n_H\sum_l\sigma_j(E_l)n_l,$$
$$\mathcal H_j=c\,n_H\,{\tt ev\_erg}
\sum_l\sigma_j(E_l)(E_l-\chi_j)n_l.$$

Gamma는 absorber당 s^-1, H는 absorber당 erg/s다. 이 둘을 IgmPhotoInput으로 기존 AxbiProvider.point에 넣는다. radiation photo effects를 연구용 Gas::photo로 다시 적용하지 않는다. 기존 H=0 split expansion, CI/RR/DR/CE/free-free/Compton, Case-A escape와 cold EOS/rate domain은 유지한다.

각 node에서 W_l-n_l=Σ_j A_jl이며 E_l(W_l-n_l)=Σ_j[χ_j+(E_l-χ_j)]A_jl다. 따라서 chemistry의 photo event count와 photon loss, binding·heat가 동일 사건에 묶인다. BE positivity는 nonnegative rates와 dt에서 무조건 유지되며 gas admissibility/Newton 성공은 여전히 별도 조건이다.

geometry half map의 photon work는 W_gamma=(R0-Rm)Q_old+(Rm-R1)Q_afterchem. source는 midpoint에서 넣고 그 local physical energy를 source_U에 계상한다. 일반 geometry에서 work 부호를 무조건 양수로 제한하지 않는다.

### Radiation moments

M0=Σ_j R_j Q_j, M1=Σ_j μ_j R_j Q_j, M2=Σ_j P2(μ_j)R_j Q_j. angular stock에 이미 count weights가 있으므로 weights/J를 다시 곱하지 않는다. FLRW isotropic source/initial data에서 odd moment=0, quadrupole=0 control을 유지한다.

## R6. 독립 검산과 구체적 위험 교정

새 국소 BE algebra를 Wolfram Language로 확인했다. number residual=0, energy residual=0, 0≤N_new≤W=True, first-moment merge identity=0, geometry half-work를 포함한 energy residual=0. 입력과 실제 출력은 THEORY_TRANSPORT.json에 보존했다. 이는 새 식의 symbolic 확인이며 기존 28 checks를 반복한 것이 아니다. weak finite-step algebra를 global accuracy proof로 확대하지 않는다.

양성 quadrature의 convex-hull 조건도 직접 확인했다. positive weights의 mean은 node convex hull 안에 있어야 한다. target Q/N이 GL node hull 밖이면 endpoint panels를 refine하거나 typed cap failure를 반환한다. mean clipping 또는 넓은 support를 임의 δ로 바꾸는 회피는 금지한다. 정확한 mean=L 또는 H이면 nonnegative measure가 해당 endpoint δ여야 하므로 exact delta branch가 맞다. L=H인 실제 δ도 exact 처리한다.

root가 freeze한 내부 moment-match 기준은 |ΣW−N|≤64 eps N, |ΣεW−Q|≤128 eps max(|Q|,N(H−L)). 기존 science/Newton/ledger acceptance는 완화하지 않는다. 대표적인 near-endpoint cancellation failure가 있으면 실제 사례를 root에 반환한다.

큰 |β| bounded exponential의 endpoint-distance y=|β|(1-signβ x) quadrature는 허용된다. |β|>30에서 y≤48 truncation을 쓴다면 omitted normalized mass ≤exp(-48)/(1-exp(-2|β|))<1.426e-21이며, absolute Q-tail bound는 N max(|L|,|H|) times this mass다. endpoint-distance first-moment tail은 N(H−L)49 exp(-48)/(2|β|(1-exp(-2|β|))) 이하이다. 원래 physical support는 유지하고 moment fit 기준을 통과해야 한다. 이 tail은 quadrature 진단이며 실제 escaped photons나 source truncation으로 장부에 넣지 않는다.

## R7. 판별 검증 계약

이 이론 역할은 symbolic 검산만 실행했다. 다음은 변경된 구현에서만 실행할 신규 판별이다.

1. q_ref=0, E_birth=54.42 eV δ를 팽창시켜 모든 reaction E<54.42일 때 HeII events가 정확히 0임을 확인. 초기 equality를 단순 정지계에서 반응시키는 다른 문제와 혼동하지 않는다.
2. source-free geometry에서 N,Q invariant, E=RQ, redshift work identity; 반대 방향 대칭과 FLRW M1/M2=0.
3. source를 원래 spectral cell에 GL subcells로 적분하고 injected N/U·support·clock를 비교. source support 초과 시 부분 commit 금지.
4. frozen trial의 BE node photon/event/binding/heat identities, δ·empty·neutral-zero·near-endpoint cases.
5. 기존 coupled gas residual과 같은 Gamma/heat, strict T domain/no clipping, four-variable Newton convergence.
6. full-vs-two-half는 동일 parent cell 배열 N,Q로 비교. 새로운 cohort 순서나 quadrature node 배열을 zip하지 않는다. energy error는 Σ R_j |Q_full−Q_half|로 계상한다.
7. versioned q-state checkpoint/resume에 N/Q/support/reference geometry/grid/mode를 저장. projected legacy state를 새 state로 재해석하지 않는다.
8. independent graded-energy/source/time refinement: altered transport accuracy와 whole-history observables를 분리 판정. conservation만으로 spectrum convergence를 주장하지 않는다.

새 검증은 구현 의존성이 바뀐 범위에만 수행한다. 기존 warm certificate, PHYS50, clock/DH 원전 suite, 기존 312237-step history는 재실행 대상이 아니다.

## R8. 판정

**채택:** bounded fixed reference-q two-moment/support FV, threshold-cut positive moment-matched quadrature, existing coupled BE gas solver. 이는 repeated physical-E projection을 구조적으로 제거하고 같은 gas API/장부를 유지한다.

**남는 의무:** closure/energy/source/time convergence와 runtime 비용. 두 모멘트가 arbitrary sigma moments를 결정한다는 명제는 거짓이다. 예를 들어 같은 N,Q인 서로 다른 양의 두 spectral measures는 threshold 양쪽 질량과 sigma 적분이 다를 수 있다. 이를 새로운 strong no-go 성과로 포장하지 않고, closure error를 grid refinement로 제어해야 하는 통상적 사실로 사용한다. NG1–NG7의 novelty/independent-new-theorem 조건을 주장하지 않는다.

## R9. 최소 native 연결 API와 자원

core는 immutable grid/reference/source 설정, state N/Q/L/H, prepared quadrature cache, trial-gas evaluation, source injection, observation을 분리한다. cache는 old cell·geometry·dt에 묶이고 trial density만 evaluate가 받는다. evaluate 반환은 survivors N/Q, identical-node Gamma/heat, event/energy diagnostics다. gas commit/ledgers는 기존 chemical_stage가 소유한다.

geometry_map은 photon arrays를 재투영하지 않고 work와 gas adiabatic map만 적용한다. inject는 source originals의 GL8 moments를 같은 q cells에 더한다. moments/output/spectrum은 physical E=R ε와 support를 명시한다. 기존 physical-node output이라는 metadata는 수정한다. checkpoint는 새 representation version을 쓴다.

고정 N_E×N_mu cells의 state memory는 최소 4×8×N_E×N_mu bytes와 edges이며 step 수와 무관하다. quadrature node cap과 scratch copies를 별도 상한으로 기록한다. source/atom kernel lookup은 trial 밖에 cache할 수 있다. gas 4×4 Newton을 64 threads에 무리하게 분산하지 않는다. ray/cell reductions는 deterministic order를 지키고, NCP에서는 독립 refinement/control histories를 우선 병렬화한다. 실제 workers·RSS·wall time은 bounded probe에서 측정해야 하며 이 문서는 speedup을 주장하지 않는다.

현재 단계는 graded fixed grids와 adaptive quadrature만 구현한다. child-data 없는 dynamic split/merge와 broad cohort pruning을 추가하지 않는다. material memory/cap failure는 durable state와 실제 원인을 남긴다.

## R10. 종료·재개

이론 contract unit은 완료되어 core worker에게 전달되었다. parent/root가 core와 driver integration, targeted execution, fresh independent review를 진행한다. 완료된 evidence는 보존한다. representation/refinement prerequisite과 actual NCP host/resource contract가 만족되면 기존 승인에 따라 fresh FLRW z20→4 full run을 진행하며 재승인을 요구하지 않는다.

연결된 원전:

- [Jiang 2022, multigroup finite volume RT](https://arxiv.org/abs/2209.06240)
- [Yuan–Cheng–Shu, positivity-preserving DG RT 원문](https://archive.ymsc.tsinghua.edu.cn/pacm_download/113/1121-paper-siam.pdf)

