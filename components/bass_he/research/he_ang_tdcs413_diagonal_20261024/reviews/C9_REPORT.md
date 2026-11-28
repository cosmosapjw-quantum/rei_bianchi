# C9 independent implementation and actual-output review

Unit: HE-ANG-TDCS413-DIAGONAL. Date: 2026-10-24. Reviewer: separate `independent_review` Astra role requested by the user; runtime model identity not independently observable.

## Final verdict

**PASS_AFTER_BOUNDED_PRESENTATION_REPAIR.** Scoped numerical science and the repaired presentation are admitted. The single initial review pass found no source, kernel, oracle, or numerical implementation defect. It identified footer clipping and stale ledger summary text; both are now closed on actual evidence below. Initial findings and verdict are preserved verbatim in `C9_REPORT_INITIAL.md` and `C9_REPORT_INITIAL.json`. This is the bounded closure of the same review, not an additional scientific run or a new review tree.

## Scope and inspected evidence

R6 is reused unchanged. I inspected all five new code files, selected source input and candidate provenance, dependency/preparation records, R7 raw output, each of the three START and FINISH files, test stderr, analysis stdout and JSON, plot stdout, ledger, and the actual PNG. No reviewer test, scientific import, solver, plot, or optional numerical rerun was executed. The scope is the fixed nominal PWBE model and thirteen admitted source points; the full physical provider remains `SOURCE_INPUT_PENDING`.

The executed frozen theory hash is `da1669bad79e1ed6c6711a42aa13ec861908a9f1951a067473d249bcfed928da`, contract `38e10f6d0adb65dbd9b44a2f13773923df073974e83221ec7315af62eb596f5b`, and selected input `a3b645d59f73d1caf48c2790e7643b273734fd4795b0ff41085dc02164cc5290`. Initial executed core hash is `09bb9bd4fdae822e2a6305a97d75af5144e3c53de427f835b85333377819b1bf`, tests `3bd9d3d0a831cf77ab302f41b4dbf4f7aa27db95f4ea4810c63482d94e395954`, and analysis code `e53f2fa14c1772e5e146e2e06028c93cb039139674a27930ae1af8051234e89b`. The reused point kernel retains `9485f9a97689d14b819de2bdb3005643e7b1b12b2b321df7695129fa699c4c37`. The actual analysis artifact is `ac20cc5657ef5b6c6b0b916d2986ef29bc9d1e5af3eab44c60b4df967fb70ecf`.

## Code and oracle assessment

The closed diagonal code preserves the nominal rational energies, equal-share geometry, unpolarized weight, point-density normalization, positive-domain restriction, and model-peak bracket. The source loader retains the observed zero and null numerical fields for all three pre-model excluded settings. The generic minimax API rejects nonfinite and sign-invalid inputs; this review does not assert uniform relative accuracy for arbitrary extreme floating-point inputs outside the tested fixed case.

The tests reconstruct three-dimensional source vectors, momentum-transfer squares, literal transition prefactors, and the weighted singlet/triplet combination without calling the closed diagonal helper. The 80-digit analysis independently reconstructs those vector amplitudes rather than merely changing precision in the production formula. The prior point kernel is independently identified by hash and evaluated only at the thirteen new geometries. Exact Fraction controls use the independently derived toy optimum and residual objective. Interval-feasibility bisection follows a distinct computational route to the pair maximum. The high-precision minimax uses the same proved pair characterization, so its independence is arithmetic and model-input construction, not a second proof of that characterization; interval bisection and R6 supply the complementary checks.

All-row residuals, active opposite-sign residuals, model and observation/error scale invariances, the exactly proportional case, the zero observation, schema rejection, and peak bracket/domain signs are checked. Tests 7 and 8 enforce relative kernel/shape comparisons with zero absolute floor. The analysis explicitly applies the frozen absolute a/kappa tolerances separately from the tests' generic mixed tolerance. These are meaningful controls for this finite contract.

R7 raw output contains three true symbolic identities, eleven true rational-bound checks, and two true toy checks, with exact toy scale 2/3 and kappa 8/3. This is reused root execution evidence, not reviewer execution. The missing mpmath preparation event and its unknown cost are preserved. The root-authorized pinned pure-Python mpmath 1.3.0 wheel is separately metered and identified; the method and tolerances were unchanged.

## Actual outcomes and interpretation

All three initial child FINISH files have PASS, exit code 0, and no measured cap overshoot. The raw unittest log shows **11/11 methods PASS**, with no failures or errors. The analysis records all thirteen numerical comparisons passing.

| Quantity | Actual saved result |
|---|---:|
| Common scale a | 79.98401712311731 |
| Weighted maximum residual kappa | 4.514958607183564 |
| Active ordered pair | rows 9 and 4; 50 and 38 degrees |
| Model peak | 42.96377691157668 degrees |
| Zero-q angle | 44.02578398781171 degrees |
| Maximum relative K error against rounded 80-digit reference | 3.690884345585919e-15 |
| Maximum relative shape error against rounded 80-digit reference | 3.3120292964298546e-15 |
| Maximum relative reused-kernel difference | 2.4969857819742395e-15 |
| Absolute a difference from 80-digit reference converted to binary64 | 9.947598300641403e-14 |
| Absolute kappa difference from that reference | 3.552713678800501e-15 |
| Absolute kappa pair/bisection difference | 8.881784197001252e-16 |

The displayed zero peak-angle difference and zero N residual are binary64 results, not exact mathematical-zero certifications. The 80-digit results are numerical references, not directed-rounding enclosures.

At the pair-computed optimum the independently evaluated binary64 endpoints are L=79.98401712311733 and U=79.98401712311731. The stored strict comparison consequently says `feasible:false`, with L-U=1.4210854715202004e-14. This is a rounding diagnostic explicitly labeled as a binary64 evaluation, not evidence that the exact optimum is infeasible. Bisection selects the adjacent rounded kappa, with the interval order reversed by the same tiny amount. The proved exact-real characterization and agreement of the objective, opposing residuals, and high-precision route support the claimed tolerance-level result; no clipping or rewriting of the raw boolean is needed.

At kappa=1 the endpoints are approximately 156.2421590878588 and 52.79610067753418, separated by 103.44605841032461 in the opposite order. Together with the actual optimum near 4.515 this reports a substantial deterministic weighted mismatch for the stated nominal model. It is not a p-value, confidence-level exclusion, general no-go theorem, absolute cross-section result, or attribution of the discrepancy solely to model physics when detector response and rounding remain outside the contract.

## Findings: object, evidence, effect, minimum repair

### C9-FIG-01 — CLOSED after actual bounded repair; initial presentation blocker

**Object:** initial `results/figures/TDCS413_DIAGONAL.png`, emitted by initial `plot_results.py` hash `5cd2de3ec2690de46a433960e44f447e43a7f667f854376a8d03c4c640d3b760`.

**Evidence:** direct PNG inspection shows the second footer line cut at both canvas edges. The beginning of the relative-azimuth qualifier and the end of the cross-section limitation are not completely visible. Both data panels themselves are readable and match the saved numerical results.

**Effect:** the exported figure fails to carry all its intended geometry and interpretation qualifications. Numerical admission is unaffected, but presentation completion cannot be claimed.

**Minimum repair:** preserve the original plot code and artifacts, wrap the footer, and use the original unused diagnosed reserve for one root-authorized saved-output-only plot child. Reinspect that actual figure. Do not rerun tests or analysis.

### C9-META-01 — CLOSED by current summary correction; initial documentation inconsistency

**Object:** initial post-run `evidence/execution/RESOURCE_LEDGER.json` summary fields.

**Evidence:** `state` still says `PREPARED_NOT_RUN`, and `zero_scope` says no new science child launched, despite three complete PASS attempts and nonzero measured costs in the same file.

**Effect:** the summary contradicts the retained actual execution record. This does not invalidate measured results or their START/FINISH provenance.

**Minimum repair:** update the summary state to the actual completed status and explain its cost scope, preserving every attempt and prior cost. No execution is required.

## Resource accounting and admission ceiling

The three initial children total CPU 2.1699260000000002 s and wall 2.270555465000143 s. Their measured costs are within the fresh unit's 10 s CPU / 40 s wall allocation. The reserve was unused at initial review. Old PWBE continuation costs stay in their original ledger and are not transferred here. Missing preparation, host/model/IO, and total remote evaluator CPU remain unknown rather than zero; an end-to-end CPU cap is not established. R7 separately reports body CPU 0.03232899999999983 s, body wall 0.032433 s, and tool wall 8.288 s, with total remote CPU unknown.

## Same-review repair closure

I inspected the preserved plot and runner diffs, the actual `04_03_plot/FINISH.json`, the repaired PNG, the unchanged analysis hash, and the corrected ledger summary. The plot change only restructures the footer into three readable lines and adjusts its vertical location. The final footer explicitly gives the source and exclusions, relative azimuth and nominal energy unit, retained zero, numerical-weight interpretation, unknown covariance, and relative-shape scope. Both panels remain consistent with the same saved results. The runner change restricts the original single reserve to this explicit saved-output repair after the three retained PASS children. Original code, runner, PNG/SVG, and diffs remain under `C9-FIG-01_BEFORE/`.

The fourth FINISH records PASS, exit 0, no timeout or measured cap overshoot, CPU 0.947641 s and wall 0.971467864999795 s. There was no test or analysis replay. The recorded core, test, source, theory, contract, and analysis-code identities remain unchanged. The saved `ANALYSIS.json` hash remains `ac20cc5657ef5b6c6b0b916d2986ef29bc9d1e5af3eab44c60b4df967fb70ecf`.

Final plot code SHA256 is `906e0e2e78d736582f1f366ff52088939664cc3c62b5320424489994240d4805`; runner is `e7b1bdc424661c4fd4cefcf30e3d3dba6802c0f580a4ede2d9ecc00337ed2bc2`. Actual PNG is `d26f1f4c91e00df206294b9980c10a5cf30378066a9aafbd3e17843c58bc521b`; SVG is `6aee63abd237bc2a16d5f79d9eb462b041d21a9f12045bd81784ee7f9027c16e`. Actual PNG visual inspection passes: neither footer edge is clipped and all three lines are readable. No further render is needed.

The ledger now explicitly records four completed PASS attempts—tests, analysis, initial render, and footer-only saved-output repair—and explains that initial zeros described preexecution only. Its visual-review-pending wording is the producer state preceding this independent receipt. C9-META-01 is closed; historical B1 and START records remain unchanged.

Final measured cumulative CPU is **3.117567 s**, wall **3.242023329999938 s**, with four completed children, reserve used 1 / remaining 0. These measured child costs fit the same 10/40 allocation; the end-to-end CPU qualification remains unchanged. There are no remaining blocking findings. Admit the finite nominal comparison and its figure, preserve the parent physical gate, and stop further scientific execution or optional audit for this review.
