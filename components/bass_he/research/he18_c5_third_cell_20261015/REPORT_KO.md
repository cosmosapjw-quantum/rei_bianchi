# HE18 C5 coding research, 2026-10-15 KST

Scope: implement and actually execute warm third saved-cell source/Taylor certification, carrying 4 gas and all 2904 photon errors from the certified two-cell predecessor, without touching the separately running rei_bianchi Codex checkout. Parent BASS_HE commit 4c422f192f8415803f40e230a5a89d320096dd67. Finite source owner a5c958c414dea41216b445c05f58df837f05cacb.

## Implemented
New stage_third_cell.py validates immutable predecessor hashes (SECOND_ENDPOINT_MEMORY f6942afc... and TWO_CELL_VALIDATION e75fa7b2...), retained P01 source and HM12 data. It builds fresh third-cell frozen Hermite slopes by exactly two reference RHS calls; adjusts the global-clock offset to 2h, retaining the original initial-epoch shear integral and Verner/source-knot guards. No parent source or historical tests were changed. New propagate_third.py carries every raw photon component and its positive source/absorption contributions; verify_third.py checks source endpoints, physical gas tube, all 2904 radii, exact positive comparison resolvent and telescoped three-cell tau/probability. test_c5.py supplies synthetic positive and rejected-negative regressions.

## Actual result
Time interval 1.25e10 to 1.875e10 proper seconds. Third tau [7.9999127041675566475740565398145483,7.9999127041675595385018339347641212]e-9. Cumulative first-three-cell tau [2.3999748079131392336673775725385171,2.3999748079131397718184574360222098]e-8. Cumulative first-scattering probability [2.3999747791137440709715731353183002,2.3999747791137446091226400833118094]e-8.

Gain upper 0.0023050746469227773<1; global gas cube usage 0.11671494755452749<1. Third column radius 21728.26548459944962 m^-2. Propagated conditional gas temperature error bound 1.0496933724836153e-11 K. All 2904 outgoing raw photon radii are nonzero; 784 exactly transparent opacity nodes.

## Execution and status
Actual local midpoint and whole-node programs completed with exit0 (around 15s concurrently); assembly completed exit0 (around 8.7s), propagation and exact-rational verify completed exit0. Four public synthetic unit tests passed, including a real negative-radius rejection. Wolfram15.0.1 third-time/shear and Hermite symbolic checks 8/8 after correcting replacement/equality precedence in two initial test expressions. The initial failed CAS predicates and changed expressions were retained as expression-level failures, with unchanged science equations.

Claim status: source-scoped conditional exact-real certificate; the existing mpmath.iv 70dps implementation has no new independent formal review. No new native Rust binary64 roundoff calibration, global 16-cell history, real observer or cosmological reionization abundance result. Third-cell private P01 NPZ, emissivity and 2904-vector details are stored only in the evidence archive, not GitHub.

Next physical cell: [1.875e10,2.5e10] s requires its saved Hermite source, exact 2904 photon incoming radii and four gas bounds, global original-time shear, and per-cell branch/rate/roundoff checks. Original separate rei_bianchi AXBI development DAG and BBN-style abundance-history goal remain under their Codex owner.
