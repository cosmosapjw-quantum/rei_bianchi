# Exact next-stage instruction — R2C-R1B

@Web+Wolfram Treat this as a durable continuation of the private
`cosmosapjw-quantum/rei_bianchi` project.

Execute stage:

```text
P0.5-B2C2B0C-R2C-R1B-PHOTON-CONSERVING-CUMULATIVE-BUDGET-NONAUTONOMOUS-RT-FORCING-LOCK
```

Canonical inheritance:

- R2A global reduced-DAE moments and exact photon ledger;
- R2B fixed macro/micro endpoint distributions and exact-zero lanes;
- R2C fail-closed constant-equilibrium attempts and initial projection records;
- R2C-R1 Farkas certificates, retained as no-go certificates for the rejected
  common-equilibrium surrogate;
- R2C-R1A state/flux/budget reclassification and all-row endpoint audits.

Before calculation:

1. Read `PROJECT_STATE.json`, `docs/science/current_00_READ_FIRST.md`,
   `docs/provenance/DURABLE_STAGE_LEDGER.csv`,
   `external/rec_bianchi.lock.json`,
   `external/REC_BIANCHI_MONITORING_POLICY.md`, and
   `handoff/CURRENT_HANDOFF_PROMPT.md`.
2. Run `python scripts/verify_repo.py`.
3. Perform a read-only probe of both private repositories. Record the exact
   remote SHA or an explicit unavailable status. Do not push from the runtime.
4. Verify every canonical input hash.
5. Create the new durable directory, input lock, stage state, receipts,
   manifest, and `SHA256SUMS` before calculation.

Physics requirements:

1. Remove `C` from the dynamical state vector. Retain
   `B_Delta t=N_HI,start+integral R_rec dt` only as a whole-interval necessary
   photon-budget auditor.
2. Evolve the material state `y=(N_HI,N_HII,U)` with explicit H-nucleus
   transfer sources. Treat `U` with a genuine particle/thermal equation, not
   the R1A audit proxy.
3. Treat group currents as radiation-coupled algebraic fluxes: instantaneous
   `J_g=Gamma_g N_HI` where valid, or the finite-cell photon-conserving
   time-averaged absorbed-count relation.
4. Construct a prelocked, nonautonomous RT forcing from inherited endpoint
   `Phi_g,kappa_g`, source/boundary evidence, and the existing photon ledger.
   Do not fit an arbitrary `Gamma_g(t)` independently at each node.
5. Use a C2-Ray-type fixed-point structure: alternate photon-conserving
   absorbed counts/time-averaged opacity with the analytic or positive
   chemistry update until both radiation and chemistry moments close.
6. At every node, macro, group, and substep, save the exact cumulative ledger:
   `absorbed photons = neutral depletion - collisional ionizations +
   recombinations + neutral inflow - neutral outflow`.
7. Preserve all inherited endpoint mass, ionization, current, opacity,
   transfer, exact-zero, macro-cap, and global reduced-DAE moments.
8. Check `dt`, `dt/2`, `dt/4`, and `dt/8`. Gate ionization/photon ledgers and
   thermal convergence separately; optically thick heating may require a
   stricter timestep than ionization.
9. If a lane is infeasible, do not clip, redistribute between macros, invert
   cloud mass from opacity, or introduce a post-result source. Save a dual or
   cumulative-ledger deficit certificate identifying the missing forcing.
10. Use Wolfram to verify the positive semigroup, cumulative identities,
    exact-zero sectors, and moment sums when available. Otherwise retain an
    executable `.wl` file plus independent exact/high-precision fallbacks.

Pass rule:

- authorize `R2C-R2` only if all three shape lanes close the node/macro/global
  photon and H/He ledgers and pass the separate thermal refinement gate;
- otherwise fail closed and identify the missing physical radiation/source or
  thermal operator;
- introduce a broader coupled positive generator only after the corrected
  photon-conserving nonautonomous closure has itself failed.

Still forbidden in R1B:

- unresolved subtraction;
- front/Q_M growth;
- source/fesc calibration;
- primordial recombination adapter or surrogate;
- CAMB transfer;
- Bianchi feedback;
- production promotion before all-lane closure.

Repository policy:

- preserve failed attempts separately;
- update `PROJECT_STATE.json`, current read-first, handoff, artifact registry,
  and durable ledger in the same durable commit;
- tag the major lock;
- make no remote-push claim without a successful local push and subsequent
  `git ls-remote` verification by the user.
