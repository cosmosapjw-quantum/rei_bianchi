# Validation matrix

| Axis | Status | Evidence |
|---|---|---|
| Repository CI-equivalent commands | PASS | root fmt/workspace tests, handoff verify/reproduce, rate reproduce, BASS and REC all exit 0 |
| Numerical library | PASS | 18/18 locked tests |
| Tracked stock below binary64 tail | PASS | `tracked_kernel_carries_stock_below_binary64_tail` |
| Extended-range discrepancy accounting | PASS_SCOPED | `Wide::abs_diff` regression and loss-carrying node reconciliation |
| NORMAL scalar regression | PASS | existing bit-parity and A/B route tests |
| Accepted-record replay | PASS | live two-transition capture/replay exit 0; scalar/ledger permutation explicit |
| Former coarse k17 blocker | RESOLVED | `repair-coarse-tracked-stock-k17n`, exit 0 |
| Common k17/34/17 comparison | PASS | temporal `0.023889076639814984`, tail `9.888200732218342e-13` |
| Full 0.0008 suffix | PASS | coarse/fine/tail 31/62/31 advances, all exit 0 |
| Final k48/96/48 37 fields | PASS_SCOPED | temporal `0.023932797389989293`, tail `4.080871757717751e-12` |
| Final suffix source N/E | PASS_SCOPED | maximum allowance ratio `0.1962283868484479` |
| Original per-branch gates | PASS_SCOPED | maxima below 1: coarse `0.74807`, fine `0.38222`, tail `0.88347` |
| Nested research package fmt | BASELINE_FAIL | preserved compact snapshot; repository-owned CI fmt passes |
| Later horizons through z=10 | NOT_RUN | 0.0008 stopping point retained |
| Continuum error authority | HOLD | spectral/source/time/Jacobian, historical-prefix and joint remainder incomplete |
| REC/BASS broader science | HOLD_OR_UNKNOWN | REC Gate I/matched evolution HOLD; BASS outside-window optical depth UNKNOWN |
| Physical history | HOLD | manufactured numerical scope only |

The accepted claim is `MANUFACTURED_MODEL_DISCRETE_REFINEMENT_PASS` for the executed 0.0008 horizon. It is not a z=12 to 10 or continuum certificate.
