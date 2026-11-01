# REI IGM first canonical interval: source-authentic blocker and paired-parent defect (2026-11-01)

## Physics target (not a production acceptance)
Restore the **actual** Aug-29 first canonical FLRW thermochemistry interval run rather than re-run it blindly. The fixed original 46,080-node H/He/thermal owner, full 26-event OTS source, three shape lanes, MPRK22(1)–Alexander SDIRK2, exact stoichiometric photon/energy identities, Hummer–Seaton events, and tolerance limits remain immutable.

**Original source owner:** `agent/implementation/rei-first-canonical-interval-20260829-r1` at `053b97c56e089e28a83f37d79a4128ed3cdae9f4`, sealed blocked run commit `a35c8b3fceaf9c832b401bc01480f5e3b0b4af30`, `local_results/first_interval_r2_blocked_minimum_step.tar.gz` 11,637,524 bytes SHA-256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`.

### Observed source-authentic partial physical history
**Three accepted endpoints**, accepted tick `160/131072=0.001220703125` of the first BDF interval. All three original physical shape lanes are blocked at the next locked one-tick interval [160,161]. On attempted step widths 4, 2, 1 ticks, the *recorded* maximum \(\log T\) full-vs-two-half cross-image metric is respectively `2.144803577710519e-4`, `2.131269352698695e-4`, `2.1245050576368385e-4`; strict bound `2e-4`. The one-tick source state public width `2.257243260856967e-4 < 2e-3`, all 14 source ledger intervals zero-including, no table event. This is **NOT** successful first-interval acceptance. Error limit, minimum step, original state and all previous PRs are unchanged.

### Constructive derived theory
Let \(F_h(y,\vartheta)\) be one full step, \(H_h(y,\vartheta)=F_{h/2}(F_{h/2}(y,\vartheta),\vartheta)\) two halves using *the same* parent state and time/source realization. The needed object is \(D_h(y,\vartheta)=F_h-H_h\). The original cross-box metric \(\sup_{u\in F_h(X),v\in H_h(X)}|u-v|\) generally includes parent spread: \(D_{box}(I,I)=\mathrm{diam}(I)\), even for identical maps. This is not a correlation-preserving local truncation metric after a nonpoint parent. A legitimate universal bound of \(D_h(X,\Theta)\) needs joint Jacobian/remainder of **the difference map**, retaining source and parent correlations. Do not manually subtract box widths, use midpoint-only comparison, loosen 2e-4, or treat an illustrative pair method as the full nonlinear certificate.

Physical positive limiting case \(\dot x=\Gamma(1-x)-R x\) for H I/H II with a frozen electron bath: the backward Euler full/half difference is
\[
D_h(x)=(x-x_*)\frac{(kh)^2}{4(1+kh)(1+kh/2)^2},\qquad k=\Gamma+R,\quad x_*=\Gamma/k.
\]
Wolfram simplified the exact rational identity to zero. This is an H kinetics **limiting benchmark**, NOT the original 26-event history. With illustrative frozen \(\Gamma=10^{-12}/s\), \(R=2\cdot10^{-13}/s\), \(h=10^{11}\,s\), and \(x\in[0.2,0.8]\), old cross-box distance is `0.5358096424757159` versus the sharp same-parent distance `0.0018117784671718453`. This proves a mechanism for enclosure-floor inflation but not validity of replacing the original estimator without a new joint source-authentic bound.

### Executable original physical source inspection
`code/physical_probe.py` reads the **existing** immutable 35-member blocked tar.gz by SHA-256, recovers any `REIADP1\0` binary accepted states (46,080 nodes), and reports true H II/He II/He III fractions, temperature and 3/2 k_B T per-H thermal energy intervals. No state rows -> `BLOCKED_SOURCE_STATE_UNAVAILABLE`, **never fabricated physical rows**. GitHub's scoped workflow runs this actual owner on the inherited branch and preserves the summary; its result must be inspected before claiming physical extraction.

### Blind-referee finding and acceptance
- Original observed local-error excess: `1.245050576368384e-5` (6.225% of strict gate), across all three lanes; historical raw result, not newly rerun.
- Preliminary linear extrapolation to zero tick `2.117740762574982e-4` is **suggestive only**, not a proof of a nonzero floor.
- Exact positive limiting BE comparison and state-file schema synthetic tests are **not** same as actual nonlinear 46,080-node certificate. Need authentic paired sensitivity remainder and source-matched physics implementation on original accepted parent.
- No native subagent available; this is same-author hostile review, not distinct-author R6/C9.

**DAG (reported): CENTRAL 28/88, WORKING 33/88, PHYSICAL FAST 4/7, CANONICAL_DELTA=0. FIRST_CANONICAL_INTERVAL=NOT_CLOSED. PRODUCTION=HOLD. NO_MERGE, NO_FORCE_PUSH, NO_TOLERANCE_RELAXATION, NO_BUDGET_RESET, AUTO_NEXT_NODE=false.**

Primary literature: Pawlik & Schaye (2011), *MNRAS*, DOI `10.1111/j.1365-2966.2010.18032.x` on photon-conserving multifrequency H/He thermal physics; this citation is contextual, not independent validation of the new method.

Next **science-first**: consume original accepted source state at tick160; implement/tighten shared-parent \(D_h\) and named low-rank owner sensitivities for actual MPRK22/SDIRK2; test exact same frozen source under unchanged gates at [160,161]; only then re-run entire first interval. Preserve negative attempts and original owner bytes.
