# HE-ANG-TDCS54-ANCHORS independent C9 review

**Final verdict: PASS_AFTER_FIGURE_CORRECTION.** Scientific implementation and actual numerical evidence pass. The sole figure annotation finding C9-FIG-01 is closed by the authorized plot-only repair and visual readback. No current blocking finding remains.

Reviewer: `/root/independent_review`, separate Astra requested; runtime model identity is not independently exposed. One review pass with bounded same-review closure only. No reviewer test/solver/CAS execution, budget allocation, old-suite replay, or extra agent. R6 PASS is reused unchanged: theory SHA256 `ad7c75393f88346ff2891686275b9ed248dc7b7c10df4c841a8355d8f9264bf7` and contract SHA256 `8cf068da56addb699e18700d86a054666b301fe89da8f3c39ff5ae48b22211dc` still match the actual files and execution inputs.

## Read scope and identity

Read all five new Python files, source CSV/JSON and metadata/printed controls/paper summaries, preparation identity recorded in execution, actual 14-method test log/report, three individual FINISH records, RESOURCE_LEDGER, source_analysis JSON, reused-cost references, and rendered PNG. This is a content/hash review of the new unit. Old scientific reviews and code were not rerun or reopened.

Initial executed hashes, independently read back from current files:

| File | SHA256 |
|---|---|
| tdcs54.py | 830b2c8b1934c60141e250feb8ee8f1bbaba5f807f1455a00ae2763c91c44bec |
| test_tdcs54.py | bff109e0c46040351403ed7c206d916e01d1097383f5b1bad11c728195340f7e |
| run_source_analysis.py | 544bc48b4cd84eac8073813129b8110734ff83f0582963100947a0ea5ff3ed94 |
| plot_results.py | d3eca0e3b9f0bf3c46001ee3a2645c1131a12557496b51f3e0676dc491405f6b |
| run_bounded.py | 7b1594f6a5273ae39e0625f48a249e5e2795f70297b23bcb0d21e42da3b10342 |

The three runs record the same frozen input identities and preparation manifest SHA256 `8058296b8019b9ed6cca9b6635904d08eb2a72cf698c287d9d94f83838c7fc7b`. The full source CSV SHA256 is `f773fec5a984349cd059e1e05c4be2fd760ce9df883844daf45db4dd682fdce5`; the located-point CSV is `2bed0118da8655ab70ac41337ac97e9b32075e5f3c611be9363cb97cc910cf53`.

## Scientific implementation and oracle independence

The core parses positive exact decimal strings, integers, and Fractions into authoritative Fraction values; booleans, float inputs, malformed strings, nonfinite values, zero/negative density inputs are rejected. Zero is explicitly allowed only where required, such as δ or an angle. Feasibility, clipping, ratio, and printing-interval computations remain rational. Decimal display strings are secondary; direction-vector trigonometry alone uses binary64 under the specified geometric tolerance.

`ratio_profile` uses model/experimental nominal values in the declared scale direction. `feasible_scale_interval` implements the maximum lower/minimum upper intersection, includes touching endpoints, and constructs u_i=r_i/A only for a feasible scale. `minimax_profile` uses the extrema midpoint, clips only the scale, and recomputes q directly without imposing δ<1 on constrained q. `pair_contrast` cancels the common scale and returns the sharp deterministic box range. `source_angle_vectors` implements opposing CCW/CW senses, exact pair angles from the summed source degrees, and the slow polar angle. Printing compatibility combines the rounded numerator/denominator boxes and printed ratio box; positive endpoint requirements are explicit. No spin, exchange, count, or equal-sharing multiplier is introduced.

The 14 methods cover actual contract edges rather than merely echoing output structure: exact-input rejection; scale direction; constructive witnesses; touching and empty intersections; single/equal ratios; both sides of constrained clipping including q=15; δ=0 and invalid δ≥1; frozen anchor oracles; scale cancellation and sharp pair corners; signed directions, unit norms, 146°/140° pair angles; a nontrivial printing case whose nominal residual exceeds 0.005; all 24 literal values and located-row correspondence; false coordinates/metadata rejection; all 16 printed controls; and the nominal all-CDW discrepancy plus finite rational serialization at very large/small scales.

Expected anchor constants are the independent hand-derived fractions previously checked in R6, not results imported from kernel routines. Exact Fraction equality enforces those expectations, including A*=9435/9424 and 1717/1178, δ*=637/3145 and 565/3434, and the constrained CCC value 44/171. The independent geometry checks compare against analytic target angles and the slow vector (1/2,0,−√3/2). The near-printing example checks explicit interval fractions, including 181/219 and 183/217. These controls support scoped implementation acceptance; no numerical test is substituted for the already reviewed general derivations.

## Source and actual result assessment

The source analysis verifies literal CSV/JSON agreement before using the eight feature rows. The located subset is exactly row indices [1,3], the binary subset [0,2,4,6], and all-feature subset [0,…,7]. Only the two source-located rows receive direction vectors. Unknown peak angles remain absent; no curve is interpolated. Metadata preserves the infinite nucleus, unevaluated fast energy, CDW exchange-neglect, CCC99 unpublished underlying provenance, reproduced experimental source, and unadmitted physical-provider status.

The actual result JSON contains 24 source values, six values at two located coordinates, 16/16 compatible conditional printing controls, and the exact previously derived pair contrasts and geometric angles. The nominal all-CDW minimum is 1593/5849, displayed as approximately 27.2354%, beside the paper's separately preserved 26% summary. Their difference is stored explicitly as 7226/5849 percentage points. Paper summaries remain descriptive, not numerical gates. Deterministic δ=10% feasibility failures are explicitly labeled as scenario results rather than statistical rejection. There is no full-H provider or new physical uncertainty claim.

## Observed execution and accounting

| Planned child | Actual result | Measured CPU s | Measured wall s |
|---|---|---:|---:|
| 01 tests | PASS, 14 methods, zero failures/errors | 0.048481 | 0.0679204100 |
| 02 source analysis | PASS, 24 values, 16 controls, two coordinates | 0.033237 | 0.0357193850 |
| 03 plot | PASS, PNG/SVG generated | 1.214902 | 1.2202520070 |

All three actual FINISH records report exit zero, no timeout, no launch error, and no measured cap overshoot. Initial measured totals are CPU 1.29662 s and wall 1.3238918020069832 s. No scientific repair had yet been consumed at this first-pass snapshot. Source/plot stderr are empty; the test stderr is the successful unittest log.

The resource ledger and inherited references preserve previous costs, the prior CCC arithmetic/lock failure history, and UNKNOWN_NOT_ZERO values without transferring old allowances. Measured scientific invocation totals are inside the new 8 CPU/30 wall allocation. This does not establish an end-to-end CPU cap: host orchestration and unmetered preparation are explicitly UNKNOWN_NOT_ZERO, and remote total CPU is separately unknown. No replay is warranted to change that accounting qualification.

## C9-FIG-01 — CLOSED figure annotation overlap

- **Object:** left panel of `figures/tdcs54_source_controls.png`, kinematics annotation placed at axes coordinates x=.03, y=.95.
- **Observed evidence:** the marker at fast 4°, CCC99 TDCS 2.58 crosses the annotation's `210` text. Both reviewer and root observed the rendered collision.
- **Effect:** source values and numerical conclusions are correct, but one required angle label is partly obscured in the delivered graphic.
- **Minimal correction:** preserve the original plot/code evidence; move only the annotation horizontally to approximately x=.40, retaining all data/axes/labels; use the single authorized plot-only repair child. No test or source-analysis rerun is needed.
- **Closure:** inspected the preserved-before/current plot diff: the sole plot change is annotation x=.03 to x=.40. Inspected the narrowly authorized runner routing for C9-FIG-01, which permits only the fourth plot child after the three completed planned PASS children. Read actual `04_03_plot/FINISH.json` and stdout/stderr: exit zero, PASS, no timeout/launch error/overshoot, empty stderr. Its input hashes confirm the theory, frozen contract, kernel, tests, source-analysis code, and source inputs unchanged. Viewed the replacement PNG: both kinematics lines, including 210 degrees CW, are clear of the fast-4° CCC99 marker. The original plot/code/runner/PNG/SVG remain in `reviews/C9-FIG-01_BEFORE/`. No tests or source analysis were rerun.

The figure otherwise uses unconnected points at the two joint coordinates, distinguishes three producer series, and separately compares exact nominal minimax diagnostics with paper summary markers and a labeled deterministic scenario. Captions preserve the feature/coordinate distinction and the absence of a confidence interpretation.

### Final correction accounting and admission recommendation

The plot-only repair measured CPU 0.591269 s and wall 0.6193045279942453 s. Four measured scientific invocations total CPU 1.887889 s and wall 1.9431963300012285 s; one reserve was consumed, with zero observed failures or measured cap overshoots. Final plot code SHA256 is `f4a14c551803565fb0898a7f1715510dfe1e6c7b42276bf6c9ac01f2dd82ced7`, and runner SHA256 is `ac973688c19bf1a54fc46858c501f2393d7a550592ee80cede6b6d076f3743b1`. The accounting qualification above remains: these measured invocations fit the 8/30 allocation, while end-to-end CPU cap establishment remains false because unmetered orchestration/preparation and remote CPU are separately unknown.

**Recommend scoped science admission before publication:** DERIVED equations, IMPLEMENTATION_VERIFIED exact arithmetic/geometry/source intake, and NUMERICALLY_CHECKED_SCOPED actual source diagnostics are supported. No further scientific execution or review pass is warranted by the resolved finding. R6 is reused unchanged. This recommendation concerns reviewed scientific content and its figure; publication and external backup receipts remain parent-owned operations. Physical-provider admission remains false and HE-ANG remains SOURCE_INPUT_PENDING.
