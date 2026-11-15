# AXBI per-case cost: measured schedule, structural overhead, next finite experiment

The completed +0.01 baseline has **312,237 accepted steps, 936,768 tentative trials, 19 rejected comparisons and 6,563,808 RHS evaluations**. This is not 312,237 failed or stiff solves. The missing endpoint is now complete; this audit changes neither the physical source nor AX11 admission. Original physics corpus SHA-256 is `d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185`; completed RETURN SHA-256 is `41b4949ad493380728455dfe1cf726ab2851c514c7cac0cd324c607a13ae66cb`.

## What determines the step count

The original `adaptive_step` (corpus lines 651–710) compares one full trial with two half trials and retains the half solution. The maximum defect covers H/He fractions, thermal energy and spectrum number/energy L1 differences. It accepts below 1e−5 and only doubles the step below 2.5e−6; otherwise it holds the existing dyadic step. Rejection halves it. No current output identifies which defect component controls the step.

Streaming the immutable ZERO and completed +0.01 histories independently gives **identical step bins and transition indices**, not merely equal total counts. The initial accepted Δln a is 1e−4/2¹⁸ = 3.814697265625e−10. Only 837 accepted steps occur before the main plateau. The plateau Δln a=3.125e−6 lasts 218,659 steps (70.03% of all accepted steps), from a≈0.04762165 to 0.09431091. Another 65,666 use 6.25e−6; 26,844 use 1.25e−5; 230 use 2.5e−5; the terminal step is clipped. Full counts and source hashes are in `STEP_SCHEDULE.json`.

The complete counter identity is 936,768 = 3×(312,237+19). Mean RHS work is 7.00687 calls per tentative trial. A successful one-update Newton solve normally uses seven calls: one residual, four finite-difference Jacobian columns, one line-search residual, and one final residual. The aggregate is only 6,432 calls above seven per trial. This is consistent with easy nonlinear convergence across most trials, though aggregate counters do not prove every trial used exactly one update. Physical stiffness has not been measured: no Jacobian eigenvalue ratio or controlling defect component was logged. The early zero-photon/source transient and long controller hold band require targeted diagnosis; neither is sufficient evidence for changing accuracy targets.

## Why each step is expensive

These are directly inspected source operations, not measured percentages of runtime:

| Operation | Source evidence | Consequence |
|---|---|---|
| Background clock and shear | `point_at_scale`, line 1695, recomputes 4097 Simpson nodes, even at the fixed reference a | Repeated calls for each ray and state duplicate identical work. At n_mu=8 a successful tentative has nominally 56 call sites through dt, two geometry maps, injection and validation, before compiler optimization. |
| Spectrum serialization | `output_row` and `output_batch`, lines 939 and 1163 | Every accepted step formats every angle-energy spectrum row; the buffer is then cleared if spectrum output is not due. Nominal cadence is 60 steps, with 30-second and terminal exceptions. |
| Feedback diagnostic | Lines 1096 and 1846 | A separate 4097-node angular quadrature is evaluated at every accepted step. It is scientifically meaningful output, but its runtime share is unmeasured. |
| Output guard | Lines 1115–1199 | Every batch flushes five streams, recursively totals directory bytes and serializes a checkpoint for reservation. This must remain safe if optimized. |

There is no instrumented profiler result, so no assertion that any one operation dominates or that a particular speedup is available. Exact reuse of identical background points and avoiding discarded formatting are the first bounded implementation candidates. Approximate interpolation of the background, lowering quadrature, relaxing local_target or substituting a new integrator would require separate numerical validation.

The geometry/absorption operator is genuinely directional: it remaps energies using ray pullback, weights injection by angular Jacobians, and applies energy-dependent absorption to angle-resolved stocks. It does not impose exact scalar ±q parity. The very small observed chemical odd response must remain unresolved; the separate sign-kernel and residence-time diagnostics address its interpretation.

## Allocation correction and concrete next PR

The new continuation actually performed 71,757 accepted steps and 1,513,308 RHS calls in **1760.7755 native wall seconds**, or 40.753 accepted steps/s. Its accounted cumulative wall counter is 9107.8768 s. That cumulative counter excludes unrecorded work after the interrupted predecessor's last checkpoint; the old full reservation and quarantined orphan replay debit remain separate. It is not a complete campaign CPU bill.

The current AX11 contract has 12 initial refinement runs and a total cap of 7,800,000 tentative trials. Twelve copies of the now measured baseline workload would already require **11,241,216 trials**, exceeding that cap by 3,441,216. This is a planning mismatch, not a mathematical lower bound on all refined trajectories. Do not inherit 650,000 trials or 200,000 accepted steps as viable per-case baseline caps.

For planning only, if local full-versus-two-half defect scales as h², tolerance reductions by 4 and 16 roughly imply 2× and 4× accepted steps. T1/T2 for two cases would then cost 12 baseline equivalents, about **30.36 cumulative native hours at the measured baseline rate**, before energy/angular refinement and any interruption overhead. This is an unverified conditional forecast, not permission to launch or evidence of convergence. Grid refinements change different kernels differently; do not multiply all runtime by node count without timing.

The next scoped PR belongs to **rei_bianchi/AX11**, with BASS handling the interface and VigilODE supplying solver advice only. Add per-component error and kernel-cost accounting; reuse exactly equal background points; skip unused spectrum formatting while preserving byte reservations and all required outputs. Verify a bounded replay from an exact saved checkpoint with identical accepted states/counters where arithmetic order is preserved. That replay is an implementation check, not a refined full history. Then bind finite original-IC T1/T2 paired runs against measured work and the existing allocation ledger; compare actual paired response differences to the unchanged 10% target and scientific floors. Do not count profiling or resource-only optimization as AX11 science progress.

Runtime: PYTHON_PASS for saved-history analysis. No new IVP, no native source mutation, no plot, and no canonical DAG count change were made by this audit.
