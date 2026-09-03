# Plot/CRAG Audit — REI 03A3 State Figure

Figure: `AUTHORITY_BINDING_STATE.svg`

## Correctness

The figure matches the exact claim boundary: PR #45 import ordering, PR #46 RED, and PR #47 authority-binding source are complete; server-side protection, target-host preflight, native execution, result audit, first interval, and provider review are not complete.

## Retrieval

The figure agrees with the live GitHub readback: the attempt ref remains absent, no attempt-state artifacts were created by CI, and the native runtime was not invoked.

## Augmented hostile readings

Rejected readings:

- three completed boxes imply the runtime is mostly complete;
- a required protection-receipt validator implies active server protection exists;
- a successful source workflow implies target-host equivalence;
- a remaining-attempt box implies the attempt has been reserved;
- a provider-review node implies REC/BASS provider compatibility.

The dashed style is therefore load-bearing: it marks unexecuted or blocked nodes rather than partially successful runtime nodes.

## Generation

The figure predicts only the next admissible governance operation: establish and independently read back server-side attempt-ref protection. It does not predict whether target-host re-attestation or the native runtime will pass.

## Print-size assessment

The SVG is designed for double-column or screen display. At single-column width the bottom explanatory lines will be the first elements to become small; those lines should move to the caption if used in a paper. No scientific paper figure claim is made here.

```text
claim = NARROWED_AND_SURVIVING_SOURCE_STATUS
pixel_level_print_pass = NOT_RUN
```
