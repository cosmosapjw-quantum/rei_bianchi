# Validation matrix

| Axis | Status | Evidence |
|---|---|---|
| Repository CI-equivalent commands | PASS | handoff verify/reproduce, rate reproduce, BASS, REC, root fmt, root workspace tests all exit 0 |
| Numerical library | PASS | 16/16 locked tests |
| Positive heat below scalar readout | PASS | `canonical_positive_heat_may_project_to_zero` |
| NORMAL A/B operation order | PASS | existing bit-parity regression |
| Paired storage/observer/checkpoint | PASS_SCOPED | coarse/fine/tail V2 common-state runs and V2 to V3 restart |
| Common epoch 37 fields | PASS_SCOPED | `comparison_14.json` |
| Temporal refinement | PASS_SCOPED | worst allowance ratio `0.023882550275375468` |
| Tail comparison | PASS_SCOPED | worst allowance ratio `9.736692500318166e-13` |
| Original per-branch gates | PASS_SCOPED | all reported gate ratios below 1 through common state; coarse k15/k16 also below 1 |
| Negative/structural-zero controls | PASS | unresolved and negative signs remain rejected; structural zero retained |
| V1/V2 migration | PASS_SCOPED | old partial migration plus actual V2 k14 to V3 k15 resume |
| Nested research package fmt | BASELINE_FAIL | preserved compact snapshot files; repository-owned CI fmt passes |
| Canonical transport into characteristic | FAIL_BLOCKER | incoming value/loss is not consumed even before scalar underflow |
| Accepted-record replay API | HOLD_NONACTIVE | final canonical segment pair is not restored before comparison |
| Coarse k17 | FAIL_BLOCKER | scalar stock projects to zero while finite canonical log tail remains |
| Full 0.0008 suffix | NOT_COMPLETED | stopped at k17 |
| z=12 to 10 / continuum | NOT_VALIDATED | error authority and later horizons incomplete |
| Physical history | HOLD | manufactured numerical scope only |

No result is promoted beyond `PASS_SCOPED` for the executed manufactured-model rows.
