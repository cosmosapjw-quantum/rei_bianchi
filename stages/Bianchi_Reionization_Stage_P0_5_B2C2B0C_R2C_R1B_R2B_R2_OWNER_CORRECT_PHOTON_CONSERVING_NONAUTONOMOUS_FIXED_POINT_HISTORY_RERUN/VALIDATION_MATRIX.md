# Validation matrix

| Gate | Hard criterion |
|---|---|
| Owner opacity/current closure | relative residual `<1e-11` |
| Node allocation closure | relative residual `<1e-11` |
| Structural support/zero | exactly zero violations |
| Fixed-point convergence | residual `<1e-10` and declared iteration limit |
| Positivity | all species and `U_resolved` strictly nonnegative, no clipping |
| H nuclei | relative residual `<1e-11` |
| He nuclei | relative residual `<1e-11` |
| Group photon ledger | relative residual `<1e-8`; report `1e-10` engineering target separately |
| Resolved thermal ledger | relative residual `<2e-4` under refinement |
| Unresolved energy ledger | owner-routed closure `<1e-11` |
| Transaction | accepted parent byte-identical after rejection/rollback |
| Restart | accepted-state and ledger byte-identical round trip |
| Refinement | primary `dt`/2/4/8 endpoint deltas `<2e-4`; thermal checked separately |
| Lane policy | primary plus two fixed auditors; no post-hoc selection |
