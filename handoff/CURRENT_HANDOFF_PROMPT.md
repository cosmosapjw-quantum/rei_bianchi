# CURRENT HANDOFF PROMPT — rei_bianchi

Treat this as a durable continuation of the private `rei_bianchi` project. The repository and hashes are the sole source of truth.

Before calculation read `PROJECT_STATE.json`, `docs/science/current_00_READ_FIRST.md`, `docs/provenance/DURABLE_STAGE_LEDGER.csv`, `external/rec_bianchi.lock.json`, `external/REC_BIANCHI_MONITORING_POLICY.md`, and this file; run `python scripts/verify_repo.py` and `pytest -q`; verify every input hash; create the next durable stage before calculation.

Conventions: metric `(-,+,+,+)`, `epsilon_123=+1`, explicit `c`, `hbar`, `k_B`, homogeneous background, tetrad plus 1+3, finite tilt and nonlinear large shear.

## Current durable verdict

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2-OWNER-CORRECT-PHOTON-CONSERVING-NONAUTONOMOUS-FIXED-POINT-HISTORY-RERUN
DURABLE_FAIL_CLOSED_R2C_R1B_R2B_R2_NOMINAL_DT_TO_DT8_FIRST_SLAB_FIXED_POINT_NONCONVERGENCE_INTERNAL_DT256_EXISTENCE_WITNESS_ADAPTIVE_MICROSTEP_LOCK_AUTHORIZED
```

All required first-slab macro steps `dt,dt/2,dt/4,dt/8` fail only the hard maximum Picard convergence gate. Positivity, H/He nuclei and the positive implicit thermal root remain closed. The interval/256 witness converges below `1e-10`, so do not interpret this as physical nonexistence. No production history is promoted.

## Next exact stage

Execute `P0.5-B2C2B0C-R2C-R1B-R2B-R2A-ADAPTIVE-INTERNAL-MICROSTEP-ACCEPTANCE-AND-GLOBALIZATION-LOCK`.

1. Freeze the R2B-R1 material state/owner law, R2B-R2 operator, 17-node BDF forcing and ten ledgers.
2. Start from the nominal `dt/8` macro partition and recursively bisect a rejected internal step; do not jump directly to the observed interval/256 witness.
3. Lock `dt_min=interval/1024`, fixed-point tolerance `1e-10`, owner/nuclei tolerance `1e-11`, photon hard gate `1e-8`, and step-doubling state error `2e-4`.
4. Accept only when positivity, H/He nuclei, photon owners, thermal balance, fixed-point convergence and local error all close.
5. Commit an accepted microstep exactly once; rejection, event rollback and restart preserve parent bytes.
6. Keep the hard maximum-node residual. Weighted density/mass tail metrics are auditors only.
7. Run `LOCAL_NEUTRAL_HAZARD_PRIMARY`, `RECOMBINATION_WEIGHTED_AUDITOR`, and `SCRIPT_SELF_SHIELDING_AUDITOR` without post-hoc lane selection.
8. Close the complete first canonical interval at all macro-output refinements before authorizing the full five-interval history.
9. Fail closed at `dt_min` with the earliest certificate: fixed point, local error, material capacity, thermal, subgrid exchange, or boundary/storage.
10. `rec_bianchi` remains semantics-only; import no numerical rate/state/history and implement no surrogate.
11. Do not start unresolved subtraction, front/Q_M, source/fesc fitting, CAMB transfer, or Bianchi feedback.

Repository policy: preserve failed attempts, update project state/handoff/registry/ledger in one durable commit, tag major locks, and never claim a push without successful push plus remote-SHA verification.
