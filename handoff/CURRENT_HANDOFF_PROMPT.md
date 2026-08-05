# CURRENT HANDOFF PROMPT — rei_bianchi

Use this prompt at the beginning of a new work thread. The repository is the sole durable source; do not inherit transcript-only numerical claims.

---

@Web+Wolfram Treat this as a durable continuation of the private `rei_bianchi` project.

Canonical repository:

```text
https://github.com/cosmosapjw-quantum/rei_bianchi
```

External primordial-recombination repository:

```text
https://github.com/cosmosapjw-quantum/rec_bianchi
```

Before science work:

1. Read `PROJECT_STATE.json`, `docs/science/current_00_READ_FIRST.md`, `docs/provenance/DURABLE_STAGE_LEDGER.csv`, `external/rec_bianchi.lock.json`, and this file.
2. Run `python scripts/verify_repo.py`.
3. Run `scripts/update_rec_bianchi_lock.sh`; record the exact native remote HEAD or an explicit unavailable status. Also query the authenticated connector when available. Do not implement a recombination surrogate. Read `external/REC_BIANCHI_MONITORING_POLICY.md`; a changed remote SHA requires deliberate adapter/input-lock review.
4. Verify every canonical artifact and split logical-output hash used by the next stage.
5. Create the next durable stage directory, input lock, stage state, receipts, manifest, and SHA256SUMS before calculation.

Project objective:

Derive and implement the equations needed to extend homogeneous reionization and CAMB-level CMB transfer to all 11 Bianchi types with nonlinear large shear and finite tilt, using tetrad and 1+3 formalisms. Metric signature is `(-,+,+,+)`, epsilon_123=+1, and c, hbar, k_B remain explicit unless a stage declares otherwise.

Current durable verdict:

```text
P0.5-B2C2B0C-R2B-MOMENT-CONSTRAINED-NODE-LIFT-HISTORY-UPLOAD-RECOVERY-V2
DURABLE_PASS_R2B_SCIENTIFIC_EQUIVALENCE_RECONSTRUCTED_GIT_DELIVERY_R2C_AUTHORIZED
R2C relaxation-audit authorization: true
Production node chemistry authorization: false
B2C2B authorization: false
```

R2B lifted all 30 shape/substep cases and 540 macro states onto 1,382,400 fixed micro-node states and 2,764,800 active photon-group rows. Independent file-reloaded validation closed every macro/global mass, ionization, temperature, transfer, cycling-capacity, current-Gamma, opacity, KKT, ordering, physical-bound, exact-zero, and inherited finite-relaxation gate. The largest global opacity residual was `7.1603e-14`; no capacity violation exceeded the `1e-12` relative tolerance.

The static lift is not a production chemistry history. Its maximum photon-prior TV distortions are `0.8948` (G1) and `0.9194` (G2a), so temporal realizability must be audited before any history is promoted. R1 diagnostic histories remain fail-closed. `rec_bianchi/main` is connector-locked at `0d24bf7fc6b2643f0bf5fd7f693a6ebc3889958d`; no adapter review or surrogate has started.

Next exact execution instruction:

# Authorized next stage — R2C constrained node-chemistry relaxation audit

Execute `P0.5-B2C2B0C-R2C-MOMENT-CONSTRAINED-NODE-CHEMISTRY-RELAXATION-AUDIT` from the R2B lock.

1. Create a new durable directory, input lock, stage state, receipts, manifest, and SHA256SUMS before calculation.
2. Treat the R2B node distributions and all R2A macro/global moments as hard endpoint constraints; do not independently solve cloud abundance or derive mass from opacity.
3. Test whether the large node-level photon redistribution is dynamically reachable using finite-relaxation chemistry lanes and timestep refinement. Preserve tau=10/100/300 Myr results separately.
4. Require dt, dt/2, and dt/4 convergence of node mass/ionization/temperature/current moments before promoting any history.
5. Record projection work, KL/TV drift, active capacity sets, photon and H/He nuclei ledgers, and dual certificates at every substep.
6. Infeasible lanes must fail closed without clipping; tau=10 Myr remains an existence witness, not calibrated physics.
7. Keep G2b/G3 effective-HI and primary HeII/G3 exact zeros unless a separately authorized species-support stage changes them.
8. Do not begin unresolved subtraction, front/Q_M, source/fesc, recombination adapter/surrogate, CAMB transfer, or Bianchi feedback.
9. `rec_bianchi/main` is locked at `0d24bf7fc6b2643f0bf5fd7f693a6ebc3889958d`; any use requires a deliberate adapter/input-lock review first.

Only a convergent all-lane relaxation audit may authorize a production moment-constrained node chemistry history.

Repository/update policy:

- Save every accepted or fail-closed stage under `stages/` or as a compact bundle under `artifacts/compact/`.
- Update `PROJECT_STATE.json`, `handoff/CURRENT_HANDOFF_PROMPT.md`, `artifacts/registry/ARTIFACT_REGISTRY.json`, and `docs/provenance/DURABLE_STAGE_LEDGER.csv` in the same commit.
- Commit each durable stage and tag major locks.
- Never claim a push unless `git ls-remote origin` and `git push` both succeed and the remote commit SHA is recorded.
- Preserve failed attempts separately; never overwrite them with later success.

---
