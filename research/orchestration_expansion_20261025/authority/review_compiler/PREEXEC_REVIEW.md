# Independent preexecution scientific review — REI-CHEM-LEDGER-01

Date2026-10-25. Reviewer is independent of this unit's contract and implementation authors; earlier work was molecular literature intake. Requested Astra scientific-review role; actual runtime model identity unobserved. Read actual intake/AGENTS.md, ROOT_SCOPE_AND_ASSEMBLY_CONTRACT.md, authority/rei/FROZEN_COMPILER_CONTRACT.md and THEORY.md, root Wolfram output, and staged chem_ledger.py, fixtures.json, run_checks.py, run_bounded.py, plot_saved.py and README.md. No compiler import, test, solver, or fixture execution performed. Review artifacts only are written.

## Verdict

Theory and frozen finite scientific scope: PASS. Initial implementation preexecution disposition: one targeted evidence repair required before scientific execution. No extra physics, empirical rate, solver or adjacent governance requirement is introduced. After the repair, review only its changed lines; do not restart this completed static review. Final C9 admission remains pending observed raw results, resource receipts and actual plotted image.

## Blocking finding R1 — guard plot contains literal expected residuals labelled as observed

In run_checks.py, calls for `reject_chemical_isotope_swap`, `reject_missing_electron` and `reject_double_electron` pass manually authored isotope/charge residual dictionaries into `rejection()`. That helper checks the raised exception string but simply forwards the supplied residuals into the output row. `plot_saved.py` then plots these dictionaries under saved exact residuals. Thus these guard diagnostics are expected values, not residuals obtained from the rejected reaction. The successful conservation fixtures and bolometric energy control already use computed residuals.

Impact: exception guards may be correctly rejected, but the required raw/plot artifact cannot yet serve as observed evidence of guard residual magnitudes/signs. This is relevant to the frozen requirements for literal expected independence, raw observed residuals and the diagnostic plot.

Smallest repair: derive each rejected guard's observed isotope/charge residual from its actual mutated reaction stoichiometry and species records; compare it to a separately literal expected residual dictionary; save the computed object as observed `residuals`. Keep the exception-string check and all frozen inputs/signs unchanged. The four-isotope element/baryon-preserving control may use the same helper, but no extra scientific case is necessary. The renderer should continue to read saved data only. The bolometric control needs no change.

## Completed scientific checks

- The21-population catalog exactly covers n; H1,D,T q0–1; He3,He4 q0–2; Li6,Li7 q0–3. Both free-electron pools remain distinct. Nine synthetic extension records include the explicit C12/C13/C12m witness. Missing energies remain unqualified.
- Nuclear identity `(Z,A,isomer)`, state, signed charge and pool survive canonicalization. Species charge upper bound and explicit negative-ion qualification match the frozen schema. Multiple identical isotope components are correctly accumulated.
- Chemical isotope and charge conservation are distinguished from nuclear baryon/charge conservation. The latter reports isotope change and leaves physical Q unqualified. No neutrino or empirical beta-energy claim is silently made.
- The electron-count identity is `n_e,total = Z^T A − q^T`, where free electron rows have empty composition and q=−1. Therefore chemical isotope/charge invariance implies full-electron rest-energy-reference cancellation. This argument cannot eliminate arbitrary nuclear rest-energy changes in transmutation; the contract correctly forbids that extension.
- Column energy signs independently agree with fixtures: PI +10−15+5=0; capture −10+15−5=0; attachment −2+2=0; H2 formation−5+5=0 and dissociation+5−5=0; isotope exchange0; charge exchange+1−1=0; LiH−5+5=0; HeH+−8+8=0; pool transfer0−3+3=0; synthetic carbon formation−3+3=0 and reverse+3−3=0. These are synthetic exact witnesses only.
- Reference-change theorem follows `epsilon' nu − epsilon nu = lambda^T C nu`. Two distinct rational shifts include nonzero charge coefficients and electron rows. Reverse sides negate stoichiometry and independent energy increments without implying a reverse rate or detailed balance.
- Literal expected stoichiometry/energy is stored in fixtures.json separately from the compiler. Derived source and reverse expectations use those literals, not the compiler's current output. Source tests retain exact0,1,1/7,10^-100 and signed−2,3/5, with no tolerance.
- Event keys preserve full reaction sides, catalysts, multiplicity, direction/process, normalization, frame/domain and state resolution. Ownership conflicts apply to active providers on the same slot/event; inactive alternatives and distinct declared process/partition remain distinct under the frozen semantics. The compiler does not discover physical equivalence from arbitrary user-supplied names; no stronger claim is admitted.
- Physical bolometric increments are counted in the energy residual while diagnostic tallies are excluded. Explicit electron source reconstruction duplication is rejected. Energy residual nonzero is a reported failing conservation witness; `SYNTHETIC_EXACT` denotes input/arithmetic qualification, not physical validation.
- WU leads species/reaction interface; REI is consumer/central staging. REC spectral and HE collision ownership remain intact. The leaf name does not silently reassign authority.
- Runner is single child/worker, resource-limited and first-attempt-preserving. Plot code reads saved rows and does not import the compiler. Actual limits/exit/resource usage and final source identity must be read after execution; they are not inferred from this static review.

Root Wolfram evidence independently supports five chemical columns, electron/energy/reference/reverse cancellation and the isotope counterexample. It is algebraic evidence with remote CPU unmeasured, not a replacement for the pending implementation run. No new no-go theorem or global model-completion claim is made.

PASS after repair → execute the already authorized single bounded child → save raw rows/receipts and one plot → independent final evidence/visual review → scoped claim only if accepted.

## Bounded follow-up: R1 closed; explicit frozen photon-count datum

Latest run_checks.py was reread at the changed helper only. `rejection()` now obtains stoichiometry, isotope deltas and signed charge from the mutated input; saves these as observed residuals; and separately compares against literal expectations in `guard_residual_identities`. `encode_residuals()` serializes integers as exact numerator/denominator. R1 is closed without test execution.

The executor raised one remaining interpretation of an existing explicit acceptance: case01 says one ionization event removes one photon with independently specified15eV. A radiation-energy increment−15 and a process tag alone do not record photon count. Requested root authority decision on the minimal completion: separate photon count per event−1 and photon energy15eV for case01, +1 for its exact reverse, with literal count/source/reverse and count×energy checks. Do not put photons in the charged material species ledger or infer photon counts for other fixture channels. This is completion of the named fixture datum, not a request for a radiation solver or additional species. All other static findings are closed; no further review surface is introduced. Final C9 remains pending actual raw and visual evidence.
