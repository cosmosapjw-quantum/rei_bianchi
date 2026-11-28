# Independent final C9 review — finite-mass direct CBA

## Split verdict

**Numerical model evidence: PASS_SCOPED. Execution status: two actual FAIL attempts retained. Export completion: PARTIAL.** The complete, durably saved scientific results support the declared finite-fixture claims. They do not convert either resource-terminated process into a successful process, complete the missing exports, or authorize another run. The independent review itself is complete with this explicit boundary.

Reviewer `/root/fm_cba_review5` did not author or execute the implementation. Requested model `gpt-6-astra`; observed runtime identity `NOT_OBSERVABLE`. Review comprised static code inspection, source/theory work already recorded in R6/R7, reading actual result/ledger files, read-only identity and stored-record consistency checks, and visual inspection of the actual PNG. No numerical kernel, science suite, integration, plot generation, Wolfram call or scientific replay was executed by this reviewer.

The accepted scope is the finite-M, nonrelativistic, labelled direct C1 Coulomb–Born channel with reduced-mass matching, both recoil phases and the derived invariant/Jacobi/lab measures. HE-ANG remains `SOURCE_INPUT_PENDING`; physical provider, exchange-complete events, total event sigma, physical recoil distribution and empirical angular correction remain unadmitted.

## Implementation and closed findings

All seven original code files were read, as were the later continuation and repair-runner files. The composition calls the immutable parent matched overlap twice at `a*Delta` and `-b*Delta`, applies the reduced-mass normalization, and implements the accepted flux and chart coefficients. The lab wrapper evaluates weights for every positive branch and propagates unresolved caustics and excluded continuum endpoints. The exact A-zero chart endpoint is explicit. Off-shell invariant weights report their shell residual rather than silently projecting input momenta.

Two pre-START static defects were fixed in the new wrapper, with no parent edits or model changes. C9-STATIC-01 replaced the inherited direction helper with `shell.normalize_direction`, so finite components whose norm is unrepresentable are rejected. C9-STATIC-02 moved zero-transfer rejection before the lab solver/empty-support returns, while preserving the separate A-zero endpoint. Actual test method 13 passed with assertions for both Jacobi-direction overflow inputs and lab zero transfer. Actual method 17 passed the A-zero status and independent invariant-weight-domain checks. These findings are closed.

C9-STATIC-03 is also closed: before START the root explicitly adopted the existing M=1e12 finite-mass approximation test at E0=3, Er=.2 and the specified directions, with scaled finite-versus-parent difference strictly below 1e-10. It is distinct from the 2e-12 kernel evaluation-error criterion and is not a uniform limit certificate. Actual test method 14 passed.

The complete first test result is **17 methods, zero failures, zero errors**, from the original test child. No unchanged parent scientific suite was replayed.

## Numerical evidence admitted

The actual `results/ANALYSIS.json` is complete, parses successfully, has aggregate `pass=true`, and contains the exact planned counts:

| Category | Actual evidence | Scoped finding |
| --- | --- | --- |
| Generic kernels | 12 fixtures; F and both shifted overlaps at binary64, mp50 and mp80 | All pass |
| Original-integral quadrature | Three cases, both recoil terms in each | All six term comparisons pass |
| Tiny transfer | 12 cases, including parallel and transverse directions down to 1e-14 | All pass true-relative comparison |
| Kinematics and normalization | Four masses | All shell, mapping and coefficient checks pass |
| Weighted fold | Orders 24, 48 and 96 | Fine-chart and fine-refinement requirements pass |
| Jacobi-angle illustration | 73 points, -180 through 180 degrees in steps of 5 | Complete saved grid and matching CSV |
| Mass trend | Eight masses | Complete saved illustration |

The largest stored generic binary64 scaled discrepancy across F/plus/minus is approximately **4.464e-16**, below 2e-12. The largest stored mp50-versus-mp80 scaled discrepancy is approximately **6.730e-51**, below 1e-40. Independent original-integral comparisons have largest stored scaled discrepancy approximately **1.354e-50**, below 1e-35. One quadrature discrepancy serializes as exact zero at working precision; this is agreement at the computed precision, not a proof of exact quadrature accuracy.

The largest stored tiny-transfer true-relative discrepancy is approximately **1.796e-15**, below 2e-12. The largest stored kinematic residual is approximately **1.476e-15**, below 2e-13; the largest stored normalization scaled discrepancy is approximately **8.327e-17**, below 5e-13. These are observed finite-fixture results, not global error bounds near arbitrary cancellation zeros, extreme masses or continuum endpoints.

At fold order 96, the pair-sphere and transformed two-root integrals are respectively `2.2489961639448635` and `2.248996163944868` in conditional-slice units `a0^2/p0^3`. The stored relative chart discrepancy is **1.974610792893064e-15**, and the stored fine refinement discrepancy is **6.160785673826359e-14**; both satisfy 1e-9. The order-24 chart discrepancy is about 1.759e-9. This is retained honestly as the coarser result; the frozen acceptance applies to the fine order/refinement, so it is not a failed acceptance hidden by aggregation.

The quadrature reference retains the original hypergeometric/exponential integrand after exact one-coordinate integration; it does not integrate the closed overlap formula. The high-precision algebraic reference alone shares the formula and is therefore complemented by this original-integral comparison. The fold uses two genuinely different coordinate charts with branch-dependent W, while sharing the intended physical model. Their agreement tests the chart/Jacobian composition, not physical calibration.

## Exact reuse, recovery and input identity

The runtime loss occurred before the first C9 code read. The reviewer recovered the exact previously reviewed theory, addendum and three R6/R7 files from retained complete content; their SHA256 values matched the historical identities. The root explicitly readopted theory `20ff07606d1428e5bdbf28eec55f5bca5540a81578b44ceaa5e5d442813cd636`. The later paragraph-reordered `791e...` version remains historical and is not the authoritative execution input. No scientific content was reconstructed by guessing an old hash.

Final read-only comparison found **no mismatch** among the original preparation manifest's frozen and external inputs, and no mismatch among the repair manifest's input files. Thus the original seven scripts, parent modules and pinned dependency remain the inspected versions.

The failed original analysis checkpoint is still exactly `e493132d5a1bb56112d5fb87890828949b3a0cbacbcffab634c5df67ff1da830`. Its 12 generic rows and first two quadrature cases equal the corresponding final rows. Independently serializing that saved prefix gives `299fa6b711028b1951f12338754dcf2d1123f8c838575fed4aea41a443f87055`, matching the continuation record. The continuation selected only the third quadrature case and previously unreached work. Completed tests and completed quadrature cases were reused, not rerun. Any work lost before a durable checkpoint is not represented as a completed result or a zero-cost event.

The full final JSON was atomically written only after exact output counts, prefix equality and all scientific acceptances had been checked. Plotting followed that write. Consequently the later process termination does not make the existing complete numerical JSON partial or erase its evidence. The missing plot/export-completion records remain a separate limitation.

## Actual execution outcome and resources

| Attempt | Actual status | CPU seconds, including runner | Wall seconds |
| --- | --- | ---: | ---: |
| Original targeted tests | PASS | 0.301362 | 0.31895837299816776 |
| Original analysis | FAIL, return code -9 | 6.1359639999999995 | 6.184616320999339 |
| Combined continuation and plot | FAIL, return code -9 | 5.4455029999999995 | 5.482404227004736 |

Both failed children exceeded their individual measured CPU ceilings of 6 and 5 seconds. Neither failure is rewritten PASS. Their return codes and observations are consistent with hard CPU termination; the exact kill source is not observable. There is no recorded numerical assertion failure in the complete saved analysis.

The ledger retains **11.882829 new CPU seconds** and **11.985978921002243 new wall seconds**, within the original cumulative 12/35 limits. Including recorded PR100 use, it retains **16.870803 CPU seconds** and **17.108468335994985 wall seconds**, within the stated additional-lineage 20/60 ceilings. These cumulative statements do not imply compliance with the failed per-child limits, and do not establish an end-to-end budget including unknown provider/model/preparation costs.

The single new-unit repair reserve is consumed, with zero remaining. The parent reserve is untouched. No further scientific execution is authorized. Completing a successful-process history or missing exports would require additional work outside the present exhausted authorization; this review does not request it.

## Actual figure and incomplete exports

The existing **PNG was independently opened and visually inspected**. It is legible and complete as a raster figure. The two panels show the 73-point Jacobi angular curves and the eight-point finite-M difference. Axes, units, nominal E0=250 eV and relative-pair Er=5 eV, theta_q=3 degrees, synthetic M=2 designation, direct/no-exchange scope, and distinction from lab EB are visible and correct. The proton and infinite-mass curves nearly overlap; the distinct line styles and labels are appropriate. The finite-M trend is presented as a fixed-angle illustration, not a uniform asymptotic bound.

Read-only comparison confirms the 73 CSV rows agree with the saved illustration values, the grid spans -180 to 180 by 5, and saved TDCS values are finite and nonnegative. The plot code reads only accepted saved JSON and performs no new model evaluation. Its save order writes PNG before SVG and then metadata, consistent with the observed files. The missing metadata prevents claiming that the planned producer-side completion receipt was emitted; the independent review's observed hashes do not impersonate that receipt.

The following required files are genuinely absent: **`FINITE_M_CBA.svg`, `FIGURE_METADATA.json`, and `REPAIR01_SUMMARY.json`**. They must remain absent/open in delivery claims. No substitute export was generated by this reviewer. C8/export completion should therefore remain **PARTIAL**, even though the numerical checks and available PNG are accepted at their stated scope. Full 20/20 completion, all-child success, or complete dual-format export would be inaccurate. Workflow stage counting belongs to the root's explicit stage mapping; the independent scientific judgment here does not turn a workflow fraction into a physical completion percentage.

## Exact reviewed output identities

| Output | Bytes | SHA256 |
| --- | ---: | --- |
| `results/ANALYSIS.json` | 136204 | `e62cb595be64728b30f08ccfe5c2a0eb68d941fbb325d8e81aa93251e0e586df` |
| `results/figures/FINITE_M_CBA.png` | 190699 | `d0d75f7e5422ced1b873f3e1c36e6704724357a2511a0d742e3a8b4f15f0c781` |
| `results/ILLUSTRATION.csv` | 4729 | `ef4ad133d9c180b9c87732f88d6423bd0c29c8e3ca4256c432becd2972d223a5` |
| `results/TEST_REPORT.json` | 2266 | `282f4bbf5c7d65a46e1fac6cbcb3a913673850bc9e7b8598875342ac8db73e77` |

Preserve and deliver these supported results together with both failed-process records, the consumed reserve, missing-export obligations and unchanged physical claim gates. No new science is needed to judge the evidence already present, and no further run is requested.
