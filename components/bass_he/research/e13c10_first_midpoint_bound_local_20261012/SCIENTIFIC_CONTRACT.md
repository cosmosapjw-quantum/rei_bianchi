# E13C10 — signed curvature midpoint enclosure on the fixed captured OFF problem

## Objective, authority, and scope

Continue HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL01 from the actually restored E13C9 NEXT_DAG. The measurable question is whether retaining the signed second-derivative range in the first-variation integral can reduce the dominant inherited midpoint enclosure with inexpensive local work. The original motivation is a useful, rigorously bounded finite numerical representation of BASS_HE photon and energy transport. No physical model, gas evolution, interpolation, closure, captured input, mask, source, tolerance, or convention changes.

All short theory, implementation, controls, representative paths, analysis and review run HERE. Existing user authorization covers additive BASS_HE GitHub draft delivery and writes to the approved Drive and Dropbox backups; no merge or force push. This contract is an execution specification inside that authorization, not a new source of authority.

E13C8 full finite admission and E13C9 selected-path admission remain unchanged. Completed E13C7 NCP work is closed. E13C10 full population is NOT_RUN. Physical, continuum, production and receiver remain HOLD. A hash verifies identity, not the physical model or execution provider.

## Fixed sources and mathematical problem

- E13C9 complete archive SHA256: 41b4bfeae3b6795adbe2e78f5f519ee835ee8921b54bebd7d6c88ab63aae9bcc.
- E13C9 independent decision SHA256: 6d4ad71a803c5fd4d4a7fa8c08157e9bd2ec2a28698ae6578d474a6f9641d303.
- E13C9 signed Volterra source SHA256: 5f20e1b5b0f4936f7bd443d19c7181fd2c7de9de762fe2fa3e9be98f8963cfc5.
- Original E13C7 source lock SHA256: 386d0abd02a33b15a015166369cec981b00fd05987dbd146f2badcb9f604688f.
- directed_interval.py, local_enclosure.py and path_enclosure.py remain original, byte-identical source. Original Context verifies the 17 source-lock members and fixed input identities before use.
- Nodes 1, 1162, 1976, 1620, 2344 are the same five discriminating paths, with 12 serial segments. Their exact original baseline and admitted E13C9 result identities are in evidence/SELECTED_INPUTS.json.

On each segment u=h x, x in [0,1], retain the original 17 first-variation integrands f_k(x), frozen gains G_k, captured representation offsets, and signed second-Volterra kernels. The input correction is c+e, |e|<=eta. First integrals have zero incoming correction; add G_k c explicitly. Recompute every incoming-dependent prefix, signed second correction, S and radius using the NEW carry. Reuse only immutable, fine-grid local.bounds, which are independent of incoming correction. No old signed integral or old second-correction interval is substituted into a candidate.

Time is the original dimensionless log-scale-factor displacement. Photon/number quantities and eV-weighted energy/heat keep their inherited units. Exact binary64 lifts, energy conversion, cutoff versus binding-energy distinction, positive path weight once, signed seam, photon stitch, species sums and known tiny branch discrepancies are preserved. No interval intersection, fallback, clipping, tolerance relaxation or invented input.

## New quadrature and assumptions

For a dyadic cell [a,b], d=b-a, m=(a+b)/2, define K(s)=(s-a)^2/2 on the left half and K(s)=(b-s)^2/2 on the right. For f in C2 on the closed cell,

    integral_a^b f(x) dx = d f(m) + integral_a^b K(s) f''(s) ds,
    K>=0, integral K = d^3/24.

If original whole-cell Jet2 returns f''(cell) in [l,u], then the signed correction belongs to d^3 [l,u]/24. Sum directed midpoint terms and directed signed corrections, multiplying by the original positive h. This uses no unproved Simpson/Gauss fourth-derivative remainder. Equal-N mathematical containment in the old symmetric curvature enclosure does not establish cross-resolution nesting, propagated path nesting, or floating-point containment; those require actual raw comparisons. C2 alone does not imply a universal cubic width law.

Keep original E13C9 prefix midpoint/whole-cell rectangle method and its finite Volterra tail unchanged: total remainder (|G_k|+T_k) eta + T_k D S, D from the fine-grid D_L bound. First quadrature resolution N_first and second-correction resolution M are separate.

## Work plan and acceptance fixed before captured execution

1. Derive the positive-kernel identity and record genuine alternatives and limitations. Independently check exact polynomial/constant-curvature/sign-changing-curvature cases.
2. Exercise the new first-integral implementation against an independently assembled closed-form Decimal oracle for all 17 outputs: zero, signs, L=0, constant rate defects, varying redshift energy, species cancellation and incoming-correction semantics. Disclose shared Decimal elementary arithmetic and original integrand definitions.
3. Initial captured work: N_first=32 on the five declared paths; selected M=128 except node 1162 M=256. Start with nodes 1 and 1976, then remaining paths after checking the pilots. One N_first=64 calculation on node 1976 is the initially declared resolution discriminator. It runs only if the N32 candidate reaches that stage. Original N512/N1024 first quadrature and original NCP workload are not replayed.
4. Useful selected-path admission requires all 170 raw weighted intervals (17 absolute and 17 corrections per path) nested and nonincreasing against the admitted E13C9 paths, all segment/global number/energy/species ledgers containing zero, and at least 50% lower selected weighted P and H widths. This is a numerical improvement target, not a physical tolerance. Same-N signed versus symmetric comparison is diagnostic evidence, not permission to intersect.
5. If a raw comparison fails, preserve result and first finding. Refine only affected work after a concrete diagnosis and a recorded amendment, using fresh output; no blind rerun. If N32 is sufficient, stop optional whole-set resolution/precision sweeps. P60 remains fixed unless a specific rounding risk requires another diagnostic.
6. Initial local limits: per-path wall 120 seconds, at most 3 concurrent workers, 1 GiB address-space cap per process. Record actual coefficient calls, new first-integral work, recomputed second corrections, wall, CPU time and individual RSS distinctly. No extrapolated NCP speedup or provider attestation.
7. Final adoption requires an actual independent decision reviewer who did not generate the method or control design. Owner integrates and proposes; unresolved required failure prevents promotion. Preserve all first failures and original historical statuses.

## NCP boundary and completion

New NCP jobs start at zero. A future job requires a concrete unresolved full-population accuracy target, locally validated method, immutable input/source/work lock, not-yet-executed independent units, and measured cost/parallel benefit. Merely occupying 64 cores and 128 GB is not a scientific objective. This loop completes with actual local evidence, independent decision, current state, full backup and a self-contained NCP local Codex handoff stating actual work status and any legitimately open heavy task.

## Evidence-driven amendment after the initial N32 pilots

The first N32 pilots for nodes 1 and 1976 completed with overlapping but insufficiently nested raw intervals. See evidence/FIRST_N32_RAW_ADMISSION_FINDING.json and preserved initial source/contract/lock under evidence/SOURCE_REVISIONS/INITIAL_N32. In particular, coarse curvature width enlarged node1 heat bounds substantially; narrow QN/QE intervals could also cross a nearby endpoint of the old fine-grid symmetric enclosure. The other three N32 units and the contingent N64 diagnostic were not run and are superseded, not claimed completed.

The amended selected work uses the original per-path N (1024 for 1/1162/1976, 512 for 1620/2344) at P60. The saved original local.midpoint aggregate is a valid enclosure of the identical midpoint sum and is pinned by the full original result identity, source, path input, segment order, N and P. Reusing that sum while evaluating only N new whole-cell Jet2 ranges gives the signed Peano enclosure without repeating N old midpoint coefficient calls. Every prior local.bounds still has its original identity. This is reuse of an input-independent quadrature component, with no raw interval intersection or result fallback. Uncached operation remains for the preserved coarse method and manufactured comparisons.

Cached-midpoint implementation controls must compare against the independent exact/closed-form oracle and verify the midpoint sum is retained, zero new midpoint calls, and N whole-cell calls. The same-N signed versus symmetric comparison and the preserved N32 versus amended fine-grid actual outputs supply the relevant resolution evidence; no uninformative N64 replay is required. The 170 raw nesting/nonincrease requirement and 50% selected aggregate P/H target remain unchanged. Local wall and memory limits remain unchanged. All incoming-dependent second corrections, S and radii use the current new carry. Some deterministic second-correction subcalculations with identical incoming center may repeat during new path assembly; zero replay claims concern complete prior work units and the old first quadrature, not every low-level operation.

## Positive-kernel refinement after the same-N endpoint findings

The unrefined same-N pilots decreased every raw width, but node1 retained one nonnested correction QN endpoint and node1976 retained eight nonnested metrics. The smallest source overshoots were at rounding scale; HeI and later carry also showed a larger endpoint shift. These remain failures under the unchanged strict contract. Their complete code/lock/results and evidence/FIRST_SAME_N_RAW_ADMISSION_FINDING.json are preserved. No small-overshoot tolerance is introduced.

On each original cell, the Peano kernel mass on each half is exactly d^3/48. A fresh left-half derivative enclosure D_left and the already valid whole-cell derivative enclosure D_whole therefore give

    remainder in h d^3 (D_left + D_whole) / 48.

D_whole encloses the right half as a subset of its domain. This is a direct enclosure of two positive integrals, with no intersection, clipping, min against a previous interval, new differentiability assumption or change in midpoint values. For the two computed same-N pilots, reuse their raw whole-cell derivative boxes with exact result SHA, original source/input/N/P and cell-coordinate checks; only N new left-half evaluations are needed. For the other three paths, evaluate the whole cell and left half once each. Original midpoint sums remain cached, so all selected amended paths use zero new midpoint evaluations. The same source integrands generate both whole and left-half ranges, and the current carry still governs the unchanged Volterra assembly.

Required targeted controls cover exact positive/negative curvature, sign-changing curvature and closed-form 17-output containment for both cached-parent and fresh-parent branches. The final selected raw intervals must still satisfy all 170 nesting/nonincrease checks and the original 50% aggregate P/H objective. Stop further refinement once these gates and the independent decision are complete.
