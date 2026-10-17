# Independent technical review: fixed-volume uniform photon births

## Decision

**PASS, strictly scoped to the opt-in fixed-proper-volume low-level API.** No blocking correctness regression was found in the final inspected implementation. This is a static review plus inspection of existing execution evidence, not an independent rerun or a proof over all floating-point inputs.

Reviewed `crate/src/birth_clock.rs`, the `photo_step_births` and `step_fixed_volume_uniform_births` changes in `crate/src/full_network.rs`, the module export, and `crate/tests/uniform_birth_clock.rs`. The original full-network source was compared with the frozen P3 source. Existing test and scalar-oracle logs were read; no solver or test was executed for this review.

## Correctness and ownership

- The constant-emission, frozen-opacity partition uses old-photon exponential survival and newborn survival `B Phi(tau)`, with the complementary absorption driving the shared species events.
- Original old-bin populations are passed separately. They are not reconstructed by subtracting births from a rounded total.
- The small-optical-depth absorption complement is evaluated directly. Multiplication ordering preserves the reviewed minimum-subnormal optical-depth/large-birth case. Large-optical-depth old-photon survival uses a log product to avoid premature exponential underflow.
- One shared opacity allocation supplies H, He, and D photo events, heating, and binding changes. The D atomic owner verifies the same D events and does not apply a second photo transaction.
- The external ledger counts the energy of all prescribed births, including those absorbed during the step. The final invariant subtracts that injected energy once.
- State changes are staged on a clone. Invalid input, overdraw, downstream failure, ownership conflict, or ledger failure cannot mutate the input state. The API does not itself implement adaptive retry or source-rate reintegration.
- All-zero births use the exact legacy entry point. The legacy photo path retains its previous arithmetic. No changes to the cosmological driver are present in the reviewed diff.

## Evidence inspected

`evidence/accepted_all_tests.stdout` records 89 passing tests across six nonempty groups, including 21 new birth-clock tests. New coverage includes an actual-network four-absorber analytic exposure check that rejects the old full-duration newborn exposure, D-only events, zero photo-fit opacity, zero-birth parity, all-channel energy closure, CX ownership rejection, and a downstream nonfinite CMB failure with unchanged input.

`evidence/oracle_normal.stdout` records 1,890 scalar cases evaluated against a 450-decimal-digit reference, with no failures under `abs_error <= 5e-13*abs(reference) + 4*smallest_subnormal_f64`. This is scalar partition evidence, not full-chemistry accuracy evidence. Relative error near unrepresentable zero can be large while satisfying the absolute subnormal allowance; the result must not be described as a uniform relative-error bound.

## Scope and remaining limits

The API accepts integrated nonnegative births per existing bin over the actual step, at fixed bin energy and fixed proper volume. Gas opacity is frozen at the beginning of the photo update. The coupled photo/collision/CX composition remains first order. The source must be uniform over that interval for the analytic birth partition to apply as stated.

The API is not wired into the P3 cosmological driver. Consequently this patch does not repair or validate that driver's existing birth clock, establish a variable-geometry birth-age solution, or admit any cosmological source-on result. It provides no new admission for the full P4 stage, SA-01, SA-02, FLRW-CONV, BI-SIGNED, or FULL_EOR.

The scalar oracle is a finite sampled verification, not exhaustive floating-point certification. Overflows and invalid gas states remain fail-closed. The source-on conservation check uses an inventory-scaled tolerance, so it does not establish relative accuracy of an arbitrarily tiny injected or absorbed increment against a much larger reservoir.

The test named `retry_recomputes_births_once` verifies independent failed and successful calls and returned injection accounting. It does not implement or validate an automatic retry scheduler. Any future caller must supply births appropriate to each accepted subinterval and retain transactional accounting across retries.

No publication, production integration, merged status, higher-order coupled convergence, or broader physical claim follows from this scoped review.
