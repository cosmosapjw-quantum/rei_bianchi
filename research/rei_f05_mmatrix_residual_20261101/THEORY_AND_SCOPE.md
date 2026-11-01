# F05 independent M-matrix residual research: same-parent native local error

**Parent:** Draft REI PR #348 HEAD `fcc90939b6b7cc842fae65d5a0ffbb69a3ec3120`. This work is strictly additive and source-free. Original frozen 26-event kernel and first-tick 160/131072 accepted parent SHA/float64 runtime are unchanged. Main, original worker, table data, gates, budget and canonical state are never modified.

## Theorem (derived)
For either conserved original H(2) or He(3) population block, native original MPRK corrector is (A p_1=p_0), where each original physical transition flux (f_{ij}\ge0), denominator (d_j>0), and (a_{ij}=-h f_{ij}/d_j\le0) for (i\ne j), (a_{jj}=1+h\sum_{i\ne j} f_{ij}/d_j). For every fixed admissible original physical parameter realization, (A) is a strictly column-diagonally dominant Z-matrix, thus a nonsingular M-matrix with (A^{-1}\ge0). Since (mathbf 1^T A=mathbf 1^T), its inverse is column stochastic, (mathbf 1^T A^{-1}=mathbf 1^T), hence (|A^{-1}|_1=1).

Write (delta p=p_1-p_0), (B=A-I), (b=-Bp_0). Then (A\delta p=b). For **any** trial vector (z), without presuming its numerical quality, (delta p-z=A^{-1}(b-Az)). Consequently (|\delta p_i-z_i|\le \|b-Az\|_1). An outward interval enclosure ([r_i]) of each real component of (b-Az) gives (\rho=\sum_i \max(|\underline r_i|,|\overline r_i|)), and therefore each exact physically realizable increment satisfies (delta p_i\in[z_i-\rho,z_i+\rho]).

This proof requires the original production/destruction *structure*, not the weaker condition that arbitrary independently chosen matrix-box entries preserve their column sums. The structure is checked against the original immutable `event_box`, `_matrix_interval`, and `population_step` definitions. The returned interval is then used in the already established exact thermochemical log-ratio identity; full minus two-half maps share the same physical parent, but enclosure arithmetic need not retain every correlation.

## Scope and failure controls
- This check removes dependency on **correctness of the trial BLAS inverse** for the additional increment solver. It does not formally certify all original native `run_step` interval roots or their inherited Krawczyk base.
- Original event-box initializes 5x5 flux intervals at exact zero; outward enclosure represents untouched zero by `-5e-324`. Observed 875,520 such entries per captured map, no larger negative lower. These are construction-level structural zeros, not a permitted negative physical reaction rate. A lower below `nextafter(0,-inf)` or negative flux upper is an explicit failure; nothing is clipped in the original model.
- Original denominator must remain positive, parent strictly positive, all resulting intervals finite. A 46,080-node calculation is not formal MPFI/CRlibm or a proof of accuracy of Python `numpy`/source native transcendental arithmetic.
- Local gate remains 2e-4 and public width 2e-3; independently rejected original crossbox 2.1245050576368385e-4 remains preserved. **No tick161 accepted** and central DAG cannot change merely because a candidate bound is small.

**Primary comparison:** Kopecz and Meister, *On Order Conditions for modified Patankar–Runge–Kutta schemes* (2017), [arXiv:1702.04589](https://arxiv.org/abs/1702.04589), discusses inverse positivity via the M-matrix property. The conditional residual bound here is derived directly; this citation is not external validation of the REI code.

## Physics discriminant and stop condition
This is an **independent same-source test** of the original first-interval local-error candidate, *not* another photon-temperature atlas and not a new canonical DAG node. Stop after 3 original shape lanes and direct artifact readback. Original owner integration is deferred to a separate explicit gate review. Drift watchdog: no unrelated optimization, source sweep, repeated governance review, or automatic second node.
