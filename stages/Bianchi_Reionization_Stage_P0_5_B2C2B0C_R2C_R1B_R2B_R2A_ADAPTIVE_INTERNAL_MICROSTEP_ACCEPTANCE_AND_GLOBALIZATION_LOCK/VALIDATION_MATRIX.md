# Validation matrix

| Gate | Threshold | Result | Status |
|---|---:|---:|---|
| Fixed point, partition 1024 | `1e-10` | all full/half trials below threshold | PASS |
| H nuclei | `1e-11` | `6.660e-16` | PASS |
| He nuclei | `1e-11` | `7.134e-16` | PASS |
| Photon owner closure | `1e-8` | `2.796e-16` | PASS |
| Resolved thermal balance | `1e-10` | `1.269e-14` | PASS |
| Positivity | `>0` | `2.150e-155` | PASS |
| Subgrid resolved source | exact zero | `(0,0,0)` | PASS |
| Rollback and restart | byte exact | true | PASS |
| Local error, partition 1024 | `2e-4` | `8.399e-04` | **FAIL** |
| Deeper auditor, partition 2048 | `2e-4` | `2.627e-04` | FAIL, non-load-bearing |
| Deeper auditor, partition 4096 | `2e-4` | `7.872e-05` | PASS, non-load-bearing |
| Owner-kernel parity | stage tolerance | true | PASS |
| Owner speedup | `>=5x` or combined gate | `31.839x` | PASS/PROMOTED |
| Whole-solver speedup | comparable legacy required | unavailable | NOT PROMOTED |
| JAX sequence stability | required for promotion | reproducible stall | NOT PROMOTED |
| Wolfram identities | exact zero | exact zero | PASS |
| Decimal-90 replay | exact ordering/gates | pass | PASS |
| Research harness | pinned SHA and validator | pass | PASS |
| Coding harness | pinned SHA and validator | pass | PASS |

| Repository pytest | all 150 collected tests | 150 PASS in 33 fresh-process file shards; monolithic process timeout disclosed | PASS WITH ISOLATED EXECUTION |
