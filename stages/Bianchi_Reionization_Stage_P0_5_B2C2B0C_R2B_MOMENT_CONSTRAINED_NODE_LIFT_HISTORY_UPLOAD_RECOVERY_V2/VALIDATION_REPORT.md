# R2B validation report

## Core verdict

`DURABLE_PASS_R2B_NESTED_NODE_LIFT_KKT_CLOSURE_R2C_RELAXATION_AUDIT_AUTHORIZED`

All independently reloaded gates pass. The validator reconstructs the two large logical gzip files from verified 40 MiB binary parts, then reads node-state and two-group rows in lockstep. It does not reuse solver memory.

- Node-state rows: 1,382,400
- Node-group rows: 2,764,800
- Macro/global cases: 540/30
- Maximum macro residual: 9.581e-13
- Maximum global residual: 7.160e-14
- Maximum capacity relative overshoot: 1.213e-15
- Capacity failures above 1e-12: 0
- Maximum current-Gamma residual: 2.151e-16
- KKT stationarity/complementarity: 1.776e-15 / 2.450e-17
- Exact-zero gate: PASS (150 rows)
- Finite-relaxation inheritance: byte-exact PASS

## Interpretation

The constrained KL operator finds a feasible fixed-node allocation in every case. Capacity constraints are active on 1297–1467 nodes per macro. The photon TV envelope is large, so this stage is a static existence/closure result rather than a calibrated dynamical history.

## Scope firewall

No chemistry evolution, unresolved subtraction, front/Q_M, source/fesc, recombination adapter/surrogate, or Bianchi feedback was started.

## Fresh pre-package cross-check

A second implementation using pandas chunk-vectorization reconstructed the same logical files from binary parts and rechecked every emitted row. It exited 0 in 26.26 s with all 11 independent gates true. Its different summation order gave maximum global opacity residual `7.080e-14`, maximum capacity-relative overshoot `1.436e-15`, and maximum current-Gamma residual `9.143e-16`; all remain below the locked tolerances. The slower row-wise implementation's final rerun timed out at the infrastructure layer and is preserved as `ATTEMPT_3_ROW_VALIDATOR_RUNTIME_TIMEOUT`, rather than being mislabeled as a scientific failure.
