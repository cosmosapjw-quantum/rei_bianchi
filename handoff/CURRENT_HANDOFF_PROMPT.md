# CURRENT HANDOFF PROMPT — rei_bianchi

Treat this as a durable continuation of the private `rei_bianchi` project.  The
repository, locked hashes and receipts are authoritative; transcript claims are
not evidence.

## Before calculation

1. Read `PROJECT_STATE.json`, `docs/science/current_00_READ_FIRST.md`, this file,
   `docs/provenance/DURABLE_STAGE_LEDGER.csv`, `external/rec_bianchi.lock.json`
   and `external/REC_BIANCHI_MONITORING_POLICY.md`.
2. Run `python scripts/verify_repo.py` and file-isolated pytest if JAX state makes
   the monolithic process nondeterministic.
3. Run `scripts/update_rec_bianchi_lock.sh`; record exact remote HEAD or explicit
   unavailable status.  A changed SHA requires deliberate review.
4. Verify every next-stage input hash and create its durable directory, input
   lock, stage state, receipts, manifest and `SHA256SUMS` before calculation.

## Conventions

- metric `(-,+,+,+)`; `epsilon_123=+1`;
- explicit `c`, `hbar`, `k_B`;
- homogeneous background, tetrad and 1+3 formalisms;
- all 11 Bianchi types ultimately supported;
- finite tilt and nonlinear large shear.

## Current durable verdict

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R1-POSITIVITY-CONSERVATIVE-SECOND-ORDER-THERMOCHEMISTRY-PREFLIGHT
DURABLE_PASS_R2C_R1B_R2B_R2A_R1_MPRK22_ALPHA1_LSTABLE_SDIRK2_CLOSE_ALL_LANES_AT_PARTITION_2048_FAST_ROOT_BACKEND_PROMOTED_EVENT_RESOLVED_PDS_LOCK_REQUIRED
```

The numerical blocker is removed narrowly: nonautonomous MPRK22(1) chemistry
plus Alexander L-stable SDIRK2 thermal evolution passes all three locked lanes at
partition 2048.  The optimized analytic BE/SDIRK root backend reproduces the
80-bisection science reference and gives `10.126360x`
matched-accuracy warm speedup over backward Euler.

Production history is still unauthorized.  The deterministic PDS tensor is
constructed from the summed five-species RHS.  In a three-state helium block the
same net RHS can have different nonnegative event decompositions and therefore
different energy ownership.  Event-resolved full-OTS reaction ownership must be
source-locked before the first accepted interval.

`rec_bianchi/main` was connector-verified at
`61e9f672a7aeebd2cf3f361cdb02b4764207bae2` (PR-05C2A/v0.63).  Import only
ownership, transaction and bounded-no-go semantics.  Do not import numerical
rates, state, accepted history or create a recombination surrogate.

## Next exact stage

Execute:

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-EVENT-RESOLVED-FULL-OTS-PDS-OWNERSHIP-LOCK
```

1. Keep MPRK22(1), Alexander-SDIRK2, analytic-root backend, material state,
   owner law and ten ledgers fixed.
2. Refactor the original full-OTS source into nonnegative event-resolved reaction
   fluxes with exactly one population and energy owner per event.
3. Preserve the source fractional OTS branching coefficients; do not infer a
   direct HeI-to-HeIII event from the net RHS.
4. Require event sums to reproduce the source population RHS and thermal source
   at source-arithmetic precision.
5. Verify every stoichiometric vector, H/He invariant, structural zero, photon
   owner and subgrid exact-zero resolved source.
6. Fail closed if the source does not identify a positive event decomposition.
7. Only after this lock passes may `FIRST-CANONICAL-INTERVAL-ADAPTIVE-HISTORY`
   be authorized.

## Prohibited

No clipping, owner reassignment, `kappa=J/Phi` inversion, cloud/geometry
inversion, per-node fitting, post-hoc lane selection, recombination surrogate,
unresolved subtraction, front/Q_M, source/fesc fitting, CAMB transfer or Bianchi
feedback.

The user performs remote push.  Never claim a push without successful `git push`
and subsequent `git ls-remote` verification.
