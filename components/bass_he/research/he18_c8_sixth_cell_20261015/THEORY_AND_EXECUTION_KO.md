# HE18 C8 여섯 번째 warm P01 셀: 이론, 실제 코딩 및 최적화 연구

2026-10-15 KST. 선택된 C5 구현과 해당 C6/C7 실행-물리 검증, C8 동일 정확도/자원 평가. 전체 R/C 10단계 완료를 주장하지 않는다. Native subagent: NOT_RUN. 별도 local Codex: NOT_INVOKED.

## 1. Source identity, physics and domain

BASS_HE parent PR61 commit b3a56b360f3d913002dd63f8097b1457cf170e6a. Frozen finite source rei_bianchi a5c958c414dea41216b445c05f58df837f05cacb. Previous FIVE_CELL_VALIDATION.json SHA256 ca7549fd025421579b5d79782f18a3dd8726176966a88355df29a511d2e89cf7; outgoing all 2904 component memory SHA256 a0a8999065d387c8a729aa882e45d6e2f3dc690dfca08faee8aea38e8404ef07. Each byte identity was checked before staging. A second fresh stage reproduced the reference and input payload bytes identically.

Signature (-,+,+,+), c, hbar and k_B remain explicit. Original proper-time [3.125e10,3.75e10] seconds from initial epoch. Non-tilted LRS Bianchi-I, warm FT03 CI3 RR3 DR2 Verner photo, HM12 emissivity and Case-A escape, four gas states and 2904 photon rays. No CR/RCT/HH addition. All per-ray photon cross-section and source-node positivity checks remained active. Original-epoch shear, not locally reset.

For original direction cosine mu0 and anisotropic integrated shear b(t)=integral_0^t sigma(t')dt', with a(t)=V(t)^(1/3),

  E(t)/E_initial
    = sqrt(exp(2b(t))*(1-mu0^2)+exp(-4b(t))*mu0^2)/a(t),

and d ln E / dt = -H - sigma(3mu(t)^2-1). Wolfram 15.0.1 verified this sixth-cell global t/h=5+u shift, longitudinal/transverse limits, plus the exact quadratic Bernstein partition identities. Local xAct xTensor 1.3.0 performed eight actual kinematic tensor check groups with nine zero residuals; this is not a proof of the backend's interval outward rounding.

## 2. New exact Bernstein cache: derivation

On any panel z=a+(b-a)t, 0<=t<=1, p(z)=c0+c1*z+c2*z^2 has Bernstein controls

  B0=c0+c1*a+c2*a^2,
  B1=c0+c1*(a+b)/2+c2*a*b,
  B2=c0+c1*b+c2*b^2.

Direct expansion yields p(z)=(1-t)^2*B0+2t(1-t)*B1+t^2*B2. All three Bernstein weights are nonnegative and sum to1, so |p(z)|<=max(|B0|,|B1|,|B2|).

For uncertain exact-rational coefficients c_j in [lo_j,hi_j], each Bk is affine in the c_j with rational weights w_jk. Thus the exact lower bound of Bk is sum_j min(w_jk*lo_j,w_jk*hi_j); the exact upper bound is sum_j max(...). Caching w_jk, the panel length and the positive weighted-integral panel factor for 16 equal subintervals changes only arithmetic cost, not the enclosure. Crucially the same inherited third Taylor derivative remainder is attached: sup third tail <= |c3|/8, integrated tail <=|c3|/32, and weighted integrated tail <=|c3|/64 under the same old reference coordinate domain. No tolerance change and no new rate/closure approximation.

This identity holds for any coefficient signs. The public unit tests exercise mixed-sign rational boxes and degenerate zero-width coefficients, original-time shift and adjacent saved-endpoint maps. Actual real sixth-cell residual has 2904 photon nodes with three primary bounds each, and the 8712 exact rational bounds are byte-semantic equal between baseline and cached implementations.

## 3. Actual sixth-cell output

Two actual saved-source RHS endpoint evaluations freeze the sixth Hermite reference; no source IVP/ODE re-integration. Mid/whole-cell interval/Taylor passes executed as two separate one-thread-capped processes, total wall 12.5679183340 seconds. The exact rational source comparison and full 2904 incoming+outgoing photon radii passed 11 scientific checks. Source-scoped numerical results:

  sixth tau in [7.99990273761694361549,7.99990273761694969410]e-9
  six-cell cumulative tau in
    [4.79994662585105407881,4.79994662585105621756]e-8
  six-cell first scattering probability in
    [4.79994651065361786686,4.79994651065362000561]e-8.

Sixth gas comparison gain 0.0023051118189799658<1, global gas-tube usage 0.2334280707646479<1. Sixth column error radius 45686.87362223744 m^-2, conditional gas-temperature propagated error 1.8532344530895156e-11 K. 784 photon rays have rigorously zero cross-sections throughout source branch. Every photon outgoing radius remains nonnegative.

## 4. Actual resource and nested-panel results

Matched saved scientific inputs; workstation Ubuntu 24.04, Python3.12, mpmath.iv 70dps, exact Fraction assembly.

  assembly original Bernstein, wall 9.03s, peak RSS169284 KB.
  assembly cached exact Bernstein, wall 7.37s, peak RSS159952 KB.
  observed speedup 1.2252374491; 8712/8712 exact component bounds unchanged.

The cache is not a looser tolerance or an alternative source surrogate. Independent nested-panel scans of the same 2904 saved photon Taylor jets:

  8 panels: 1.303672s.
  16 panels: 2.612138s.
  32 panels: 5.116729s.

For each refinement, all 2904 sup/integral/weighted-integral enclosure upper bounds are nonincreasing. Production remains 16 panels, others are measurement-only. NumPy float64 preview processed all 2904 ray energies in 0.044674ms, yielding exactly the 784 transparent channels also proved by the interval source. This preview is never used to skip physics or to establish a source result.

## 5. Latest external work and scientific distinctions

rei_bianchi PR117 currently has head 450bad5712d6bc3c58598ea8421232128411b573 and targets non-tilted axisymmetric Bianchi-I BBN-style H/He ionic fraction and time/temperature plots. It is newer and distinct from the frozen source used in this controlled optical-depth study. Its planning status is not converted into a new physical EoR result here.

bass_cr PR69, head669cbebe5e0a4383d7999aa354a3f320eff39fd2, resolves a separate cold-source HeI positive quadrature centroid bias. Binding energy and Verner fit edges differ, so these source rates are not transplanted into warm HE. WU088_HH PR76, head e83f4bda79fecda26bb3854e94c0cdc786173835, solves a different two-centre cusp-shell angular residual and is not an ionization rate input.

Methodological original papers: Neher, Jackson and Nedialkov, SIAM J Numerical Analysis (2007), DOI 10.1137/050638448, discusses Taylor-model ODE overestimation and wrapping; Berz and Makino (2017), DOI 10.1007/978-3-319-63501-9_7, treats domain subdivision. These do not independently verify the local mpmath.iv kernel.

## 6. Execution/admission and next

This unit produced actual source code, a successful local sixth-cell calculation and speed benchmark. Public Python regression 7/7 pass, whole real sixth-cell exact rational validation 11/11, local xAct 8 groups/9 zero residuals, online Wolfram 7/7 symbolic assertions. Failed pre-staging template edits were not accepted; the final source patches were matched against observed previous runtime before staging. None altered equations, tolerances or original archived inputs.

Scientific claim: SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES. Independently audited interval backend, native binary64+provider roundoff, external scientific referee, remaining 10 cells, observer foreground, physical recombination/reionization and ion-fraction history are still separate obligations. No separate local Codex invoked, no other live repo modified.

Next seventh saved P01 proper interval [3.75e10,4.375e10]s, inheriting all four gas errors, 2904 photon errors and original global shear time, with no source-knot/threshold relaxation. In parallel, the main rei_bianchi program should pursue BBN-style ionic abundance histories; the optical-depth certificate is optional and not a mandatory critical-path gate.
