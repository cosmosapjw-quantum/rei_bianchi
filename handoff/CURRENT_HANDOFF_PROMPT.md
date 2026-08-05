# CURRENT HANDOFF PROMPT — rei_bianchi

Use this prompt at the beginning of a new work thread. The repository is the
sole durable source; do not inherit transcript-only numerical claims.

---

@Web+Wolfram Treat this as a durable continuation of the private `rei_bianchi`
project.

Canonical repository:

```text
https://github.com/cosmosapjw-quantum/rei_bianchi
```

External primordial-recombination repository:

```text
https://github.com/cosmosapjw-quantum/rec_bianchi
```

Before science work:

1. Read `PROJECT_STATE.json`, `docs/science/current_00_READ_FIRST.md`,
   `docs/provenance/DURABLE_STAGE_LEDGER.csv`, `external/rec_bianchi.lock.json`,
   and this file.
2. Run `python scripts/verify_repo.py`.
3. Run `scripts/update_rec_bianchi_lock.sh`; record the exact native remote
   HEAD or an explicit unavailable status. Also query the authenticated
   connector when available. Do not implement a recombination surrogate. Read
   `external/REC_BIANCHI_MONITORING_POLICY.md`; a changed remote SHA requires
   deliberate adapter/input-lock review.
4. Verify every canonical artifact and logical-output hash used by the next
   stage.
5. Create the next durable stage directory, input lock, stage state, receipts,
   manifest, and SHA256SUMS before calculation.

Project objective:

Derive and implement the equations needed to extend homogeneous reionization
and CAMB-level CMB transfer to all 11 Bianchi types with nonlinear large shear
and finite tilt, using tetrad and 1+3 formalisms. Metric signature is
`(-,+,+,+)`, epsilon_123=+1, and c, hbar, k_B remain explicit unless a stage
declares otherwise.

Current durable verdict:

```text
P0.5-B2C2B0C-R2C-MOMENT-CONSTRAINED-NODE-CHEMISTRY-RELAXATION-AUDIT
DURABLE_FAIL_CLOSED_R2C_CONSTANT_EQUILIBRIUM_RELAXATION_NOT_ALL_LANES_REACHABLE
Production node chemistry authorization: false
B2C2B authorization: false
R2C-R1 model-adequacy authorization: true
```

R2C audited 90 shape/tau/substep cases and 1,620 macro equilibria. After a
macro-local initial KL projection put the constructed z=6 boundary inside the
node capacity cone without changing macro G1/G2a totals, all equilibrium-
feasible cases converged under dt, dt/2, and dt/4. Feasible/convergent counts
were 18/30, 10/30, and 6/30 for tau=10, 100, and 300 Myr. At tau=10 Myr, all
12 failures were node cycling-capacity deficits; one SCRIPT case also had nine
negative inferred photon currents. Thus the R2A tau=10 global/macro witness
does not survive the node-level gate.

The largest projection column residual was `4.57e-16`, relative capacity
violation `3.13e-17`, KKT stationarity `2.22e-16`, current-Gamma residual
`1.95e-16`, and H/He nuclei residuals were exactly zero. No clipping was used.
Native Wolfram was unavailable; the included `.wl` script and independent
SymPy/90-digit Decimal fallback passed. `rec_bianchi/main` remains connector-
locked at `0d24bf7fc6b2643f0bf5fd7f693a6ebc3889958d`; no adapter review or
surrogate has started.

Next exact execution instruction:

# R2C-R1 rate-derived positive multirate relaxation-cone lock

Execute
`P0.5-B2C2B0C-R2C-R1-RATE-DERIVED-POSITIVE-MULTIRATE-RELAXATION-CONE-LOCK`.

1. Create the durable R2C-R1 directory, input lock, stage state, receipts,
   manifest and SHA256SUMS before calculation.
2. Keep all R2A macro/global endpoints, R2B node support/endpoints, R2C
   initialization projection, exact ledgers, and fail-closed certificates
   canonical. This is a model-adequacy preflight, not a production history.
3. Define positive, separately auditable rate families for `M`, `I`, `U`, `C`,
   and `J_g`. Do not fit an unconstrained independent rate to every node.
4. Derive admissible rate intervals from reduced-DAE secants and available
   photoionization/recombination/heating/cooling/cycling terms. Unidentified
   rates remain interval nuisance parameters, not calibrated physics.
5. Test a one-mode positive kernel first. Only after a locked failure may a
   bounded two-mode completely monotone mixture be tested. Prelock all rate
   bounds and mode counts.
6. Require the analytic trajectory to remain inside the full mass,
   ionization, thermal, current, macro mass/volume, and node capacity cone.
   Check analytic extrema or a prelocked certified collocation rule.
7. Preserve macro/group/global endpoint moments exactly. KL projection is an
   algebraic cone operator with KKT certificates only; no clipping, cloud-mass
   inversion, or moment transport between macros.
8. Store primal feasibility, dual/Farkas certificates, rate-identifiability
   intervals, active sets, kernel weights, KL/TV work, and exact photon/H/He
   ledgers for all three priors.
9. Prelock absolute/relative integration tolerances and use at least dt/2,
   dt/4, dt/8 for candidates passing the analytic cone gate.
10. Keep G2b/G3 effective-HI and primary HeII/G3 exact zero. Do not begin
    unresolved subtraction, front/Q_M, source/fesc, primordial recombination
    adapter/surrogate, CAMB transfer, or Bianchi feedback.

Only an all-lane positive-kernel cone pass may authorize a later R2C-R2
rate-derived node-chemistry history. Otherwise preserve the no-go with a dual
certificate identifying the missing physical degree of freedom.

Repository/update policy:

- Save every accepted or fail-closed stage under `stages/` or as a compact
  bundle under `artifacts/compact/`.
- Update `PROJECT_STATE.json`, this handoff, the artifact registry, and durable
  ledger in the same commit.
- Commit each durable stage and tag major locks.
- Never claim a push unless `git ls-remote origin` and `git push` succeed and
  the remote commit SHA is recorded.
- Preserve failed attempts separately; never overwrite them with later success.

---
