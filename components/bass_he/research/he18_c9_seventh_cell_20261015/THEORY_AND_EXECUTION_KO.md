# BASS_HE HE18 C9, 일곱 번째 warm P01 셀: 이론 및 실제 코딩 결과

2026-10-15 KST. 선택된 다음 물리 셀 구현과 직접 연관된 C6/C7 검증, C8 실제 성능 실험. 전체 10단계 수행이나 독립적인 interval library 검증으로 표시하지 않는다.

## 1. 고정된 source, 부호, clock

BASS_HE PR62 parent SHA 490ac4a980b582d983f15975dc813ef5457efa02, 원래 warm finite source rei_bianchi a5c958c414dea41216b445c05f58df837f05cacb. 이전 SIX_CELL_VALIDATION.json SHA256 151941b372aa5b3ac0becc201eab94ab94818ab115ae7935deba84830e0c27ec와 이전 전체 SIXTH_ENDPOINT_MEMORY.json SHA256 7eed4308734f9623a9741b5587f4f0a6a9cae022326461a105d271c0d13908e9를 일치 확인한 후 사용했다. 원 source state, HM12 파일, Hermite endpoints, incoming gas4/photon2904 모두 보존했다.

고정 non-tilted LRS Bianchi-I, HM12/FT03 Case-A, CI3/RR3/DR2, Verner photon source. Proper time seventh slab [3.75e10,4.375e10] s; initial epoch global b(t)=integral_0^t sigma dt, not reset at each cell. Signature (-,+,+,+). Keep c,hbar,k_B explicitly, E=hbar omega, physical photon 4-momentum p=(E/c)(u+e); source CGS conventions.

Original direction cosine mu0, scale a(t)=V(t)^(1/3), total integrated shear b(t) give

    E(t)/E_init = sqrt[exp(2b(t))*(1-mu0^2)+exp(-4b(t))*mu0^2]/a(t),
    d ln E/dt = -H - sigma*(3mu(t)^2-1).

The kinematic frequency factor is invariant under mu0 -> -mu0, but this does not authorize dropping or merging distinct physical photons.

## 2. Constructive exact-rational memoization lemma

On each residual Bernstein panel, the already adopted pure function R takes three midpoint coefficient interval pairs c0,c1,c2 and a whole-cell cubic Taylor coefficient interval c3. A mathematical input key is K=(c0,c1,c2,c3), retaining each interval endpoint exactly. If K_j=K_k exactly, then R(K_j)=R(K_k) by equality of the deterministic Fraction operations. This permits caching only the repeated calculation R, NOT changing the photon evolution, chemical source, B/C coupling, observed ray direction, or outgoing uncertainty vector.

In the actual seventh saved source, 2904 photon residual inputs have exactly 1452 distinct keys, each appearing twice. All 2904 physical source records remain; C9 memo only avoids recomputing the same exact rational degree-two Bernstein bounds and inherited cubic Taylor remainder. The source's 16-panel positive weights and scientific tolerance are unchanged.

For p(z)=c0+c1*z+c2*z^2, z=a+(b-a)*t, 0<=t<=1:
  B0=c0+c1*a+c2*a*a,
  B1=c0+c1*(a+b)/2+c2*a*b,
  B2=c0+c1*b+c2*b*b.
The exact identity p(z)=(1-t)^2*B0+2*t*(1-t)*B1+t^2*B2 holds; weights are nonnegative and sum to 1. For interval-valued coefficient boxes, each B_i's lower and upper controls follow by sign-directed exact rational multiplication. This is a mathematical enclosure, not a heuristic photon angular merge.

Python 3.12 imposes a default 4300-decimal-digit text conversion limit for large integers. The seventh source's exact Fraction output exceeded it, causing the first assembly serialization to fail AFTER scientific arithmetic. A source-scoped, SHA-pinned runtime-only integer conversion cap of 50000 digits fixed this representation failure. No arithmetic precision, source process, physical constants or acceptance tolerance was changed. Failure and corrected execution are both archived.

## 3. Actual execution and physical outputs

Two stored-source endpoint RHS evaluations, no original full source IVP/ODE replay. Actual interval midpoint+whole photon evaluation on 2904 source nodes ran in two one-thread-capped processes, wall 11.8897981939 s, exit0/0. 784 exact-opacity-zero photon source nodes.

Seventh cell optical depth:
  [7.99989941545568464556869,7.99989941545569230796931]*10^-9.
First-seven-cell cumulative optical depth:
  [5.59993656739662254337525,5.59993656739662544835640]*10^-8.
Cumulative first-collision probability 1-exp(-tau):
  [5.59993641060017767587974,5.59993641060018058086073]*10^-8.

Seventh column error radius 57590.74168542691 m^-2.
Positive four-gas comparison gain 0.0023051242095932347 < 1.
Original global gas-box usage 0.27233204017739626 < 1.
Conditional gas-temperature propagation error 2.6614873707793613e-11 K.
All 2904 incoming and outgoing photon error components and all four gas errors were propagated with exact Fraction arithmetic.

## 4. Measured optimization at equal scientific accuracy

Same frozen inputs, same source jet bytes, one Ubuntu workstation:

  Existing exact Fraction 16-panel assembly: 7.96 s.
  Exact input-key memoization assembly: 6.72 s.
  Empirical speedup: 1.1845238095238095.

All 8712 source-scoped photon scalar bounds (2904 times sup/integral/weighted integral) agree EXACTLY as rational values. RESIDUAL_COUPLING.json has identical entire parsed content. CERTIFICATE.json differs solely in its execution-time metadata, with identical depth interval, comparison P matrix, gain and gas errors. A fresh staging re-executed two endpoint RHS calls and reproduced the original P01 NPZ, HM12 emissivity, adapted full 2904 prior error input and saved Hermite reference byte-for-byte.

Independent saved-Taylor panel diagnostic for 8/16/32 subdivisions checked every photon's sup, integral and weighted-integral enclosure: no bound increased with panel refinement, actual elapsed times are stored in evidence. Productive selected source still uses 16 panels. Non-admitting NumPy vectorized 2904-energy preview took 0.09294599 ms and identified the same 784 rigorous zero-opacity nodes, but its binary64 screening never controls source branches or certificate admission.

## 5. Actually performed mathematical verification and scope

- Local Wolfram Language 15 with actual xAct xTensor 1.3.0: eight kinematic tensor groups, nine zero residuals, exit0. Null ray, screen projection and LRS shear sign verified.
- Cloud Wolfram15.0.1 and an executable local Wolfram scalar script: eight exact global-clock, parity, quadratic Bernstein partition/positivity and collision-probability identities PASS, exit0.
- Public synthetic Python regression tests: seven of seven PASS, including exact repeated keys, 2904-output preservation, negative photon-radius refusal, source/staging byte guards and controlled big integer serialization.
- Private physical seven-cell exact rational verifier: eleven of eleven PASS. Before correcting only metadata labels the older verifier result was preserved; the corrected verifier was executed again with the same optical depth values. Current public summary includes SHA256 of the final returned result.
- Native subagent NOT_RUN because no native delegation tool available; two scientific subprocesses are actual process-level parallelization, not claimed native subagents. The user-requested standalone Codex was NOT invoked, and other repo worktrees were not modified.

External current evidence checked: rei_bianchi PR117 targets the actual axisymmetric Bianchi-I ionic abundance/temperature history; it is a different active revision from this frozen source. bass_cr PR70 source-shape-free HeI threshold moment envelope and WU088_HH PR77 Coulomb cusp strip are different models and cannot provide physical reaction-rate overrides here. Scientific method backdrop is Neher/Jackson/Nedialkov 2007 (DOI 10.1137/050638448) and Berz/Makino 1998 (DOI 10.1023/A:1024467732637). Neither independently validates the actual interval backend.

Claim scope: SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES. No independent formal proof of mpmath.iv, native binary64/provider rounding, global 16 saved source cells, complete cosmological reionization H/He abundances, observer foreground, atomic-data systematics or external independent scientific referee.

Next: eighth saved source cell proper [4.375e10,5.000e10]s with original global shear, full four gas and all 2904 rational photon incoming error radii; updated threshold and source-knot guard. The separate main rei_bianchi BBN-style H/He abundance history remains its own critical path. Full private evidence and dual-provider backup record will be referenced from EVIDENCE_INDEX.json.
