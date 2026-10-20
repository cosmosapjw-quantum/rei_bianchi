# RUN19 VigilODE compatibility addendum

## Conclusion

The current temperature coefficient work can reuse VigilODE's unchanged directed-arithmetic source without replacing the REI time integrator. In particular, interval addition and multiplication can propagate separately bounded source-node and floating-point errors through the four-node coefficient interpolant. The newly derived ideal interpolation error and the weight condition number at most 5/4 provide a concrete error-budget contract. The existing RUN18 arithmetic tests do not, by themselves, establish those new source-node or transcendental error bounds.

The newer supplied-JVP coupled-stage API offers a persistent worker-pool pattern and explicit model-epoch invalidation, which are useful implementation references. It does not immediately supply a drop-in solver for the present REI model or turn a coefficient table into a certified Jacobian or solution bound. RUN19 may evaluate coefficient reuse and acceleration while retaining its original direct/default owner and opt-in table policy.

## Actual sources read

| Evidence | Identity and interpretation |
|---|---|
| RUN19 inventory | /tmp/rei_run19_inventory/INVENTORY_KO.md records selected VigilODE commit 6c945b6c6e0e024d8f733c21da8d35fbcc3c5f2a and unchanged directed.rs Git blob 89e2b3122b08db1849e4e56cc94f1f58c473b735. This agent read the saved inventory; it did not perform an additional remote query. |
| New coupled-stage README | /tmp/rei_run19_inventory/upstream_selected/vigilode/crates/vigilode-coupled/README.md, SHA-256 3fa8dc955923b26ab30ced10580f6d51e721e7b78fb69df0368f72ef9c50212f. The actual saved text was read in full. |
| Existing continuous-residual contract | RUN18 theory/VIGILODE_AND_LITERATURE_RECEIPT.json, in the restored REI commit 99e07bcff126d0a73a03bafc4b71e0b735dbcc3e. It records the original dense_output_v2.rs source and caller premises; this is retained historical source evidence. |
| Existing directed arithmetic | RUN18 delivery/vigilode_closeout/VIGILODE_FINAL_FRESHNESS.json records the preserved 17,215-byte directed.rs, SHA-256 2adadb6a5d77073e0a7d3d60aedfbf37e124d15a586a880d7d5a8c8d5307a814. Its historical branch heads are not labelled current heads here. |

The selected newer README specifies autonomous identity-mass equations, supplied JVPs, a shared twice-reorthogonalized basis with stored J0V, a bounded small projected system, and eight stage callbacks evaluated at the same frozen iterate. It explicitly distinguishes an operational full-space residual screen from an embedded time-error check. Final adaptive acceptance, a trajectory controller, and dense output are absent. The claimed 19 tests and benchmark counts in that README are ARCHIVED_EVIDENCE_ONLY for this work; this agent did not rerun them.

## Concrete compatibility boundaries

1. **Coefficient arithmetic.** The imported interval kernel can enclose weighted sums of source-node intervals. Cubic weights include negative entries, so ordinary positivity of node values does not make the interpolation a positive quadrature. For a central four-node stencil, the proved sum of absolute weights is at most 5/4. Source-node uncertainties, query-coordinate uncertainty, and arithmetic rounding must be accounted for in addition to the ideal fourth-derivative interpolation bound. A positive-result fallback establishes admissibility of accepted values; it is not an independent numerical-error certificate.

2. **Coefficient derivatives.** The current native table contract supplies values, and prior C9 derivative/Jacobian admission remains on hold. Neither small value error nor a positive cubic result bounds its derivative. A supplied-JVP solver needs an explicitly defined derivative of the same admitted model, including branch and fallback semantics. A direct-owner JVP with a tabulated RHS is a different pairing until a compatibility argument and corresponding defect are supplied.

3. **Time and events.** Present REI geometry, expansion and CMB factors depend explicitly on time, and births and threshold crossings introduce event panels. Applying an autonomous API would require an explicit time-state augmentation with the correct time derivatives or a separately declared approximation. A fixed-time coefficient lookup alone does not supply that conversion. Event-side ownership and cumulative reconstruction jumps remain part of a full trajectory argument.

4. **Continuous certification.** The previously read ContinuousResidualProvider contract requires an outward RHS over the entire time/state box, a uniform full-tube Euclidean Jacobian logarithmic-norm upper bound, identity mass, C1 state dependence on the admitted panel, and binding to one model. The private RODAS5P quartic representation is not the saved RUN17 degree-seven DOP853 representation. The recorded pointwise or block-infinity-norm diagnostics are not substituted for the required full-tube Euclidean bound.

5. **Parallel reuse.** Reusing an application-scope worker pool and binding cached/prepared data to a model epoch are compatible design patterns for the native rate work. Performance requires a matched-worker benchmark. The new coupled-stage README expressly does not assert that four workers always improve throughput, and its step benchmarks are not REI adaptive-trajectory speedups.

## Status and next constructive use

IMPLEMENTATION_VERIFIED remains limited to the actual tests and executions attributed to their individual units. This addendum is SOURCE_READ and DERIVED compatibility analysis: native RHS calls 0, IVP runs 0, new VigilODE executions 0, additional remote queries 0.

A useful next arithmetic extension is to feed admitted intervals for the original temperature nodes, coefficients and logarithmic query coordinate through the frozen four-node value expression and add the analytic interpolation remainder. Until those input bounds and branch admissions are supplied, the RUN19 rational estimates are ideal decimal-model bounds and its CPU results are finite numerical checks.

The original P4-S4C-SPECTRAL-EDGE-SUPPORT obligations for full continuous residual/feedback tubes, spectral continuum and nonlinear solution error remain open. No new gate or replacement DAG is introduced.
