# Validation matrix

| Axis | Status | Evidence |
|---|---|---|
| Saved positive subnormal heat | PASS | `material::photoheat_tests::saved_positive_subnormal_heat_is_certified`; exact bits `0002bdc74d339a20` |
| Sign and zero controls | PASS | structural zero accepted; certified negative and sign-uncertain cases rejected |
| NORMAL route | PASS | heat operation-order parity and kernel shared-route bit parity tests |
| Software regression | PASS | 12/12 locked local-library tests; repository Rust workspace tests and formatting pass; `git diff --check` exit 0 |
| First repaired common epoch | PASS | `comparison_12.json`; 37 fields, N/E and source checks |
| Temporal refinement at k12/24 | PASS_SCOPED | worst allowance ratio `0.023877179614106396` |
| Tail comparison at k12 | PASS_SCOPED | worst allowance ratio `1.1305353909436463e-12` |
| Original per-branch gates | PASS_SCOPED | coarse `0.636733...`, fine `0.318860...`, tail `0.670508...`; all below 1 |
| Kernel small-energy reassociation | PASS_SCOPED | k14 isolated fixture changes false negative heat to positive; NORMAL route unchanged |
| Paired weighted N/E readout | FAIL_BLOCKER | coarse k14: `paired readout requires extended material path` after stable kernel repair |
| Full 0.0008 suffix | NOT_COMPLETED | stopped at first repeated paired-path failure |
| z=12→10 / continuum | NOT_VALIDATED | spectral/source/time/state and historical-prefix bounds remain incomplete |
| Physical history | HOLD | manufactured numerical scope only |

The arithmetic bound added here covers the stored-coefficient photoheat product/subtraction and heat summation. It does not promote the existing owner ledger to a complete kernel/provider/state error enclosure.
