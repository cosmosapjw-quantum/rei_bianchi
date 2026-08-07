# CURRENT HANDOFF PROMPT — rei_bianchi

Treat this as a durable continuation of the private `rei_bianchi` project. The
repository, hashes, ledgers and committed receipts are the sole source of truth.

Before calculation read `PROJECT_STATE.json`,
`docs/science/current_00_READ_FIRST.md`,
`docs/provenance/DURABLE_STAGE_LEDGER.csv`,
`external/rec_bianchi.lock.json`,
`external/REC_BIANCHI_MONITORING_POLICY.md`, and this file; run
`python scripts/verify_repo.py` and `pytest -q`; verify every input hash; create
the next durable stage before calculation.

Conventions: metric `(-,+,+,+)`, `epsilon_123=+1`, explicit `c`, `hbar`,
`k_B`, homogeneous background, tetrad plus 1+3, finite tilt and nonlinear large
shear.

## Current durable verdict

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-ADAPTIVE-INTERNAL-MICROSTEP-ACCEPTANCE-AND-GLOBALIZATION-LOCK
DURABLE_FAIL_CLOSED_R2C_R1B_R2B_R2A_DT1024_LOCAL_ERROR_FAILURE_FIXED_POINT_AND_CONSERVATION_GATES_PASS_DEEPER_DT4096_AUDITOR_PASS
```

The recursive controller starts from `dt/8` and bisects only rejected steps.
Fixed-point nonconvergence is the earliest certificate through partition 64;
from partition 128 onward all full and half trials converge. At the prelocked
minimum partition 1024, owner/photon, H/He nuclei, positivity, thermal balance,
rollback and restart gates pass, but the hard maximum full-versus-two-half local
error is `0.00083986559199900057`, above `2e-4`.

Post-lock auditors give `0.0002626521892992173` at partition 2048
and `7.872276255582733e-05` at partition 4096. The latter is a
feasibility witness only and does not rescue this stage. The error is dominated
by `log T`, with `x_HeII` second. No microstep was accepted and no production
history was promoted.

The array-native owner hot path is promoted at `31.838842x` parity-verified
speedup. Whole-solver speedup remains unclaimed. The JAX thermal candidate is
diagnostic only after reproducible science-sequence synchronization stalls;
NumPy is the stable production oracle.

`rec_bianchi/main` is connector-verified at
`61e9f672a7aeebd2cf3f361cdb02b4764207bae2` (PR-05C2A/v0.63 bounded
directional-coupling no-go; PR-05C2B next). Only ownership, transaction,
component-ledger and fail-closed semantics are referenced. No numerical
recombination input or surrogate is imported.

## Next exact stage

Execute `P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R1-POSITIVITY-CONSERVATIVE-SECOND-ORDER-THERMOCHEMISTRY-PREFLIGHT`.

Use `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_ADAPTIVE_INTERNAL_MICROSTEP_ACCEPTANCE_AND_GLOBALIZATION_LOCK/NEXT_STAGE_PROMPT.md` verbatim as the bounded execution
contract. The primary candidate is a second-order nonautonomous positive and
conservative MPRK thermochemistry update, with the existing backward-Euler
partitions 1024/2048/4096 retained as auditors. Do not change the hard maximum
error metric or promote partition 4096 post hoc.

Production node chemistry, R2C-R2, B2C2B, recombination splice, unresolved
subtraction, front/Q_M, source/fesc fitting, CAMB transfer and Bianchi feedback
remain unauthorized.

Repository policy: preserve failed attempts, update project state/handoff/registry/ledger
in one durable commit, tag major locks, and never claim a push without a
successful push plus remote-SHA verification.
