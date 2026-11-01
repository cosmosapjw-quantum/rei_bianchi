# REI M1, tick160: original 26-event finite-parent-direction nonlinear stress experiment

- Origin: `cosmosapjw-quantum/rei_bianchi` original accepted first-interval 46,080-node state, tick 160/131072, parent Draft PR #328 `a85312cde63e5c0b0a7c0e5d182e79fe593bcf53`, parent original block archive SHA-256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`.
- Original 26-event nonlinear kernel SHA256 `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`; source state raw array SHA256 `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`.
- Original shape-lane list and clock, tables, photon owners, Hummer–Seaton and 26-event MPRK22(1)/Alexander SDIRK2 algorithm retained. Three lanes are **not** independent source histories. No new global IVP.
- One step `[160,161]`, `h=duration/131072`, original local-error strict `<2e-4`, original public width strict `<2e-3`; old failed uncertain-parent cross-box logT `2.1245050576368385e-4` stays immutable.

## Precise physical experiment

For each of the three original shape lanes and all 46,080 spatial nodes, construct a common nuclei-conserving point `P_0` inside the original component interval bounds. Construct eight 80%-toward-boundary physical points along four *global* parent directions: `logT`, `N_HII`, `N_HeII`, `N_HeIII`. Each ion adjustment is compensated by the same-element neutral reservoir, keeping original nodewise H/He totals unchanged. This generates nine selected parent states per lane, **not** all physically reachable parents. All source feedback and original geometry/clock are evaluated from the same `P` in both full and half routes:

`D_h(P;theta) = F_h(P;theta) - G_1(G_0(P;theta);theta)`

where `theta` is the original frozen source/clock path shared by all three actual nonlinear maps. Use the immutable 26-event kernel to obtain enclosing output intervals for each selected P. Log the full/half *independent-output interval difference* and separately an uncertified center-difference estimate. The nine sets test nonlinear sensitivity, not an interval Jacobian or rigorous full-parent error certificate.

## Constructive mathematical requirement for future admission

For a verified convex domain `Z` enclosing the whole original physical parent set `X` (including source correlations) and fixed source input `theta`, the fundamental theorem gives

`D_h(x;theta) = D_h(x*;theta) + integral_0^1 J_D(x*+s(x-x*);theta)(x-x*) ds`.

With shared uncertain source parameters `theta` the derivative includes `J_theta D`; they cannot be bounded by evaluating different independent source intervals. On a smooth branch,

`J_x D = J_x F - J_x G_1(G_0) J_x G_0`,
`J_theta D = J_theta F - J_theta G_1 - J_x G_1 J_theta G_0`.

Actual stage maps are nontrivial: H/He population is a positivity/conservation preserving MPRK22(1) map; thermal stage is an implicit Alexander SDIRK2 root; original four independent source evaluation sites and photon/OTS owner terms contribute to both `J_x` and `J_theta`. A rigorous `J_D` needs interval derivatives of the difference map and an *independent joint remainder* preserving the common source and parent. Event/nonsmooth table branches require certified partition or refusal, not an unexamined derivative. A finite sequence of candidate-point calculations cannot prove the bound over all `X`.

**Scientific admission gate**: only a source-authentic enclosure of the original whole-parent difference with the original `<2e-4`, the original `<2e-3` width, and ALL H/He/photon/energy/table/nonconvergence gates across all three lanes could permit retry of tick `[160,161]`. Even that is **not** the full first canonical interval acceptance. No numerical tolerance, original parent, original source or solver is modified by this experiment.

## Falsification and failure retention

- If any selected candidate is outside the source bounds, violates nuclei/positivity, or fails an original map phase, preserve the exact failure classification and don't invent a replacement.
- If any selected point interval difference is above the 2e-4 threshold, report the counterexample. It is evidence against assuming every point behaves as PR #328; not automatically proof of full-X failure (unreachable point possible).
- If all sampled points give `<2e-4`, call it a **finite point-set result**, never tick161 acceptance, never proof for all parents or observations.
- Separate numerical parent sample counts, lane labels and actual observation counts. Keep `CENTRAL=28/88`, `WORKING=33/88`, `FAST=4/7`, `CANONICAL_DELTA=0`, `AUTO_NEXT_NODE=false`, `NO_MERGE`, `NO_FORCE_PUSH`, `PRODUCTION=HOLD`.

Sources: original `attempt_worker.py` on frozen PR #320 lineage, source archived PR #328; original research on verified Taylor models Neher/Jackson/Nedialkov, *SIAM J. Numer. Anal.* 2007 DOI 10.1137/050638448 establishes why dependency/wrapping matters but does not certify the REI kernel.
