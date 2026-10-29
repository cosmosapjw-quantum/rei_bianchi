# REI 17-state frozen UVB source tangent: actual calculation

**2026-10-29** · Source-conditional scientific child after REI PR261 · **NOT** a new IVP, not an actual trajectory derivative.

## Executive result

Using seven exact numerically matched saved `ON_refined` states and PR261's pinned Puchwein six moments, the source-only 17×2 calibration forcing is `B=(ln10) F_UVB (1,z-3.6)`. The 17×17 photo-only state Jacobian is Metzler and has exact zero column sums; the unweighted logarithmic norm `mu_1=0`. The 17×6 source-moment Jacobian has nonzero columns only for the three ionization rates. These are **derived** and **implementation-verified scoped**. Source-only chemistry does not certify full dynamics or Thomson optical depth.

| Saved mean z | electron/Href/s | P19 photoheating eV/Href/s | joint2-95 electron/Href/s |
|---:|---:|---:|---|
| 2.404494 | 1.317212e-16 | 6.308774e-16 | [8.176192e-17, 2.091108e-16] |
| 2.789073 | 1.764677e-16 | 8.003962e-16 | [1.159044e-16, 2.684201e-16] |
| 3.217095 | 2.483486e-16 | 1.122838e-15 | [1.702774e-16, 3.674462e-16] |
| 3.603020 | 3.429774e-16 | 1.600164e-15 | [2.383266e-16, 5.076625e-16] |
| 4.024262 | 4.914143e-16 | 2.376911e-15 | [3.402074e-16, 7.411493e-16] |
| 4.378370 | 6.655807e-16 | 3.289029e-15 | [4.535463e-16, 1.032831e-15] |
| 4.701690 | 8.756040e-16 | 4.399570e-15 | [5.838353e-16, 1.404728e-15] |

The joint2-95 ranges are pointwise images of the **conditional** PR260 Gaussian+EOS/Jeans union with the saved y held fixed. The old saved `ON_refined` populations were not computed under the new P19 source. They are frozen counterfactual states, not predictions of a calibrated physical REI evolution.

## Structural and numerical evidence

- Seven events: H1/D/T neutral→single ion, He3/He4 neutral→single and single→double ion. Old REI source `FAMILIES` topology and thresholds preserved; isotope-equality assumption explicit.
- Exact integer identities: baryon vector times S=0, heavy-state number times S=0, charge vector times S=one electron per event.
- At each fixed z, B has rank≤1; seven saved redshifts stacked into a 119×2 matrix give two nonzero singular values `3.959156070340e-15`, `1.211647070561e-15`. This is source-forcing rank, not a Fisher matrix.
- Source-only `mu_1=0` for all seven snapshots; maximum `A^T B` floating residual `4.067e-31` and `Q^T B-D_a e_dot` residual `0.000e+00`.
- Source rank-one identity maximum Frobenius residual `5.218e-31`.
- Seven selected rows numerically checked against GitHub CSV blob `189c2d903e25c18bee49e0ab6add3ba1d1805e93` at 17 significant digits using canonical 3059-character FNV-1a64 `174743cb945f8bfe`; selected JSON SHA256 `7653f7f75fcbe92465de1b22faabf565efee36e90d1d967499f68ff123a6bc77`. This is not full CSV byte identity.
- New Python unittest **15/15 PASS**. Independent direct-event C++20 compiled `-O2 -Wall -Wextra -Werror`, **7/7 row checks PASS**, maximum component-scaled relative discrepancy `3.251e-16`. Wolfram 12-state H/D/T/He3/He4 symbolic stoichiometry returned four zero residuals.
- P19 six-moment source input and PR261 nominal calibration reused, no prior GLS/IVP campaign replay, no rendering. Python test elapsed/user/system and C++ compile/run are preserved in `results/TEST_TIME.txt` and `results/CPP_TIME.txt`; original closed grants unchanged, unknown overhead not zero.

## New science vs previous PR261

PR261 supplied `D_a R_6` at fixed z, a formal tau tangent and six-rate pointwise envelope. This unit constructs the **actual REI 17-state stoichiometric source Jacobian** `J_R=∂F/∂R_6` and `J_y^UVB`, evaluates them at seven actual saved populations, and gives electron event-rate and photoheating envelopes. It does **not** claim full `J_y`, actual `D_a n_e`, BASS reduced30 transport, local Bianchi optical depth, self-consistent photoelectron thermalization or a physical posterior.

## Gate and next executable action

Original working **33/88**, central last **28/88**, new physical node delta **0**. This scoped theory/code unit **18/20**: R1–R5,R7–R10 and C1–C8,C10 have actual outputs, distinct-author R6 and C9 are **NOT_RUN**. Native subagent tools not exposed; algorithmic C++/Wolfram checks do not count as different-author review. F4 PARTIAL, L4 false, actual physical temperature/native25/radii null. NO_MORE_IVPs.

Next: obtain different-author R6/C9 of this exact source extraction and code; then obtain actual full source-accepted chemical Jacobian `J_y` and density/clock/geometry inputs before any `D_a n_e`, `D_a tau` or physical uncertainty propagation. Distinguish the old `ON_refined` prescribed electron bath from the new source electron event rate.
