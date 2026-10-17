# Independent review: static-geometry cohort Phi clock

## Review basis

Static inspection of `crate/src/positive_age.rs`, its diff against the frozen legacy implementation, and `crate/tests/fixed_geometry_phi.rs`. The earlier `evidence/cohort_green.stdout` records six passing tests; the final inspected `evidence/cohort_guard_acceptance.stdout` records all nine cohort tests passing. This review did not execute tests, solvers, or symbolic calculations.

## Decision and closed findings

**PASS, scoped to the opt-in exactly static-geometry cohort update.** Final source inspection confirms closure of both malformed-history guard findings below. No blocking issue remains in the reviewed change. This is not admission of a general cosmological birth-age integrator.

1. Initial inspection found that signed `geometry_work_j_com3` was omitted from the finite-ledger guards. `SourceAgeBridge::drift` accumulates into this field, while `total_com_energy` does not validate it. This allowed a nonfinite initial geometry-work ledger to survive a successful step.
2. Initial inspection found that `chemistry_accepted += 1` could overflow a caller-supplied maximum counter. The opt-in path required checked arithmetic while preserving legacy behavior separately.

The final code now validates finite signed geometry work on input and output, and checks the accepted-step counter before processing and again when incrementing it. Finite negative geometry work remains allowed. Nonfinite inherited grey diagnostics are also rejected. The added `signed_geometry_ledger_and_counter_guards` test covers nonfinite signed ledger values, maximum-counter rejection, and acceptance of finite negative geometry work. These findings are closed by inspection.

## Correct implementation choices

- The opt-in entry point rejects nonzero owner Hubble/shear, unequal geometry snapshots, mismatched history/state clocks, hidden photon bins, incompatible or future cohort birth labels, and oversized cohort populations.
- Checked cohort-count multiplication/addition occurs before allocating new source cohorts. Geometry snapshots and state validation occur before cloning or physics processing; failures leave the immutable input unchanged.
- The strict `t0 < tm < t1` requirement deliberately rejects rounded-away midpoint progress. Newborn classification nevertheless uses the captured pre-append index, not timestamp equality.
- Only appended newborn cohorts receive the uniform-emission Phi partition. Existing cohorts retain exponential attenuation. The legacy `advance` path selects no newborn index and retains its previous attenuation arithmetic.
- Absorbed newborn photons flow through the existing single shared H/He/D event allocation. The D owner verifies these events; the subsequent full-network chemistry runs with photo disabled. There is no duplicate photo update.
- Comoving birth populations and injected energy are accumulated once; absorbed events are converted to proper-volume densities through the static volume factor.
- Input histories are treated as initial inventories, not proof that their prior evolution used Phi. The returned public history type does not enforce a permanent ban on legacy or variable-geometry continuation; that mixed use is explicitly outside the method's contract.

## Cohort semantics and remaining limits

A midpoint-labeled newborn cohort represents the surviving integral over an emission interval, not an exact birth time or resolved age distribution. At fixed geometry and energy, future absorption depends on the surviving population, so this representation is sufficient for the reviewed operator. It does not establish age moments or a variable-geometry source-age solution.

Gas opacity is frozen within each photo stage, and the coupled chemistry remains first order. The source's fixed-scale-factor rate is constant over the step. The method does not provide adaptive retries, full cosmological integration, spectral refinement, angular convergence, or higher-order coupled convergence.

The old-cohort exponential path retains legacy floating-point behavior; the hardened scalar kernel's extreme-range evidence must not be advertised as covering every old-cohort arithmetic operation. Newborn/source-age evidence does not admit full P4, SA-01, SA-02, FLRW-CONV, BI-SIGNED, or FULL_EOR.

Final test-source inspection also confirms dedicated cohort-cap and rounded-away-midpoint rejection tests, bringing the new cohort test file to nine tests. An explicit cohort-path downstream-failure test after births are staged would still strengthen coverage; clone-local processing already provides transactionality by inspection. The initial six tests directly cover two-step old/new partitioning, shared count/energy closure, variable geometry rejection, malformed input categories, incompatible cohorts, and distinction from legacy newborn exposure.
