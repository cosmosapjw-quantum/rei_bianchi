# CURRENT HANDOFF PROMPT — rei_bianchi

Treat this as a durable continuation of the private `rei_bianchi` project.
The repository and its hashes are the source of truth; transcript-only claims
are not evidence.

Canonical repository:

```text
https://github.com/cosmosapjw-quantum/rei_bianchi
```

External primordial-recombination repository:

```text
https://github.com/cosmosapjw-quantum/rec_bianchi
```

## Before calculation

1. Read `PROJECT_STATE.json`, `docs/science/current_00_READ_FIRST.md`, this
   file, `docs/provenance/DURABLE_STAGE_LEDGER.csv`,
   `external/rec_bianchi.lock.json`, and
   `external/REC_BIANCHI_MONITORING_POLICY.md`.
2. Run `python scripts/verify_repo.py` and `pytest -q`.
3. Run `scripts/update_rec_bianchi_lock.sh`; record an exact remote HEAD or an
   explicit unavailable status. A changed SHA requires deliberate adapter review.
4. Verify every input hash used by the next stage.
5. Create the new durable stage directory, input lock, stage state, receipts,
   manifest, and `SHA256SUMS` before calculation.

## Conventions

- metric signature `(-,+,+,+)`;
- `epsilon_123=+1`;
- explicit `c`, `hbar`, and `k_B`;
- homogeneous background only;
- tetrad and 1+3 formalisms;
- all 11 Bianchi types ultimately supported;
- finite tilt and nonlinear large shear.

## Current durable verdict

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R1-
CANONICAL-INITIAL-MATERIAL-STATE-AND-STATE-DERIVED-OWNER-LAW-LOCK

DURABLE_PASS_R2C_R1B_R2B_R1_
CANONICAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK_
R2B_R2_AUTHORIZED
```

Fixed inputs from R2B-R1:

- exact `z=6` positive 46,080-node material state
  `(N_HI,N_HII,N_HeI,N_HeII,N_HeIII,U_resolved)`;
- 85-row canonical BDF forcing;
- canonical authoritative total group `kappa_g,J_g`;
- exact species/group support and Verner H/He moments;
- state-derived explicit H/He owner responses;
- externally locked effective-HI global amplitude with state-conditioned
  `LOCAL_NEUTRAL_HAZARD_PRIMARY` node distribution;
- `RECOMBINATION_WEIGHTED` and `SCRIPT_SELF_SHIELDING` as auditors only;
- exact-zero resolved source for `EFFECTIVE_HI_SUBGRID`;
- ten separate photon/energy ledgers;
- transaction semantics imported from `rec_bianchi` only at the interface level.

The global effective-HI amplitude is not re-derived from material state. No
recombination numerical state, rate, accepted history, or surrogate is imported.

## Next exact stage

Execute:

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2-
OWNER-CORRECT-PHOTON-CONSERVING-
NONAUTONOMOUS-FIXED-POINT-HISTORY-RERUN
```

1. Freeze the R2B-R1 initial state, forcing, owner law, support matrix, and
   ledgers in the new input lock.
2. At each slab, recompute the owner/node fractions from the current accepted
   material state and canonical forcing; preserve authoritative total
   `kappa_g,J_g`.
3. Iterate transactionally:

   ```text
   owner-correct averaged opacity
   -> absorbed photon counts
   -> positive implicit H/He chemistry
   -> resolved thermal update
   ```

4. `EFFECTIVE_HI_SUBGRID` updates only unresolved photon/energy ledgers and has
   exact-zero resolved H/He/U sources.
5. Run `dt`, `dt/2`, `dt/4`, and `dt/8` for the primary lane and both auditor
   lanes. Do not select a lane after seeing results.
6. Gate fixed-point convergence, positivity, H/He nuclei, group photon number,
   resolved thermal energy, unresolved energy bookkeeping, accepted-step
   commit, rejected-step rollback, and restart independently.
7. For failure, save the earliest certificate without clipping or owner
   reassignment: material capacity, fixed point, thermal, subgrid exchange, or
   boundary/storage.
8. Approve production node chemistry only if every required primary gate closes.

## Prohibited

- `kappa=J/Phi` constitutive inversion;
- clipping, cloud-mass inversion, or geometry inversion;
- inter-owner photon transfer;
- post-hoc lane selection;
- recombination surrogate or premature splice;
- unresolved subtraction, front/Q_M, source/fesc fitting;
- CAMB transfer or Bianchi feedback in this stage.

## Repository policy

Save accepted and fail-closed attempts separately. Update `PROJECT_STATE.json`,
this handoff, the artifact registry, and durable ledger in the same durable
commit. Tag major locks. The user performs remote push; never claim a push
without successful `git push` and subsequent `git ls-remote` verification.
