# R2C finite-relaxation audit — durable fail-closed result

The fixed R2B node lift is **not** promoted to a production chemistry history.
After removing an initialization-only capacity-cone inconsistency, every
constant-equilibrium lane that is physically feasible converges under
`dt`, `dt/2`, and `dt/4`. The remaining failures are genuine model-adequacy
failures of the one-rate, one-equilibrium relaxation ansatz.

Durable verdict:

```text
DURABLE_FAIL_CLOSED_R2C_CONSTANT_EQUILIBRIUM_RELAXATION_NOT_ALL_LANES_REACHABLE
production_node_chemistry_authorized: false
B2C2B_authorized: false
```

Read `RESULTS_AND_VERDICT.md`, `FAILURE_ANALYSIS.md`, `VALIDATION_REPORT.md`,
and `NEXT_STAGE_PROMPT.md` before continuing.
