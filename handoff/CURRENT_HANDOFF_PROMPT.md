# CURRENT HANDOFF PROMPT — rei_bianchi

Treat this as a durable continuation of the private `rei_bianchi` project. Repository files, hashes, ledgers and receipts are authoritative; transcript claims are not evidence.

## Before calculation

1. Read `PROJECT_STATE.json`, `docs/science/current_00_READ_FIRST.md`, this file, `docs/provenance/DURABLE_STAGE_LEDGER.csv`, `external/rec_bianchi.lock.json`, and `external/REC_BIANCHI_MONITORING_POLICY.md`.
2. Run `python scripts/verify_repo.py`, current stage tests, and `sha256sum -c` in the current stage.
3. Refresh read-only `rei_bianchi` and `rec_bianchi` refs. Record an exact SHA or explicit unavailable status.
4. Verify every next-stage input hash and create its durable directory, input lock, state, receipts, manifest and `SHA256SUMS` before calculation.

## Conventions

- metric `(-,+,+,+)`; `epsilon_123=+1`;
- explicit `c`, `hbar`, `k_B`;
- homogeneous background, tetrad and 1+3 formalisms;
- all 11 Bianchi types ultimately supported, with finite tilt and nonlinear large shear.

## Current durable verdict

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-AFFINE-SET-PARAMETERIZED-TAYLOR-MODEL-CONTINUOUS-BRANCH-ENCLOSURE-LOCK
DURABLE_FAIL_CLOSED_R2_R1A_R1_R1_SOURCE_SAFE_PARAMETER_RANK_NOT_REPRESENTED_COHERENT_GLOBAL_TAYLOR_AUDITOR_NARROW_SPARSE_LOCAL_GENERATOR_LOCK_AUTHORIZED
```

The load-bearing source family contains node-local independent branch coordinates. The exact local He III cascade sensitivity determinant is

```text
r_i^2 (1-v_i) [((ell-m)+m y_i)-ell z_i].
```

At the canonical state, `45923` node blocks have robust rank two and the remaining `157` retain rank at least one, yielding source-safe rank lower bound `92003`. A two-global-coordinate coherent Taylor model cannot contain this tangent set. Its maximum empirical width `3.39993083287e-05` and maximum withheld residual `1.96719085466e-10` are auditor results only.

`rei_bianchi/main` was read-only connector-verified at `fdad2e141afe056a9a5e672c7870c021c2e2558f`. `rec_bianchi/main` was verified at `2d777b1c7e56dcdf1e17feb1f728410ea0792df8` (PR-05C2C0/v0.65). Do not import numerical recombination rates, state, radiation history, or implement a surrogate.

## Next exact stage

Execute:

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-R1-SPARSE-LOCAL-GENERATOR-AFFINE-TAYLOR-MODEL-ENCLOSURE-LOCK
```

1. Keep the 26-event registry, MPRK22(1), Alexander-SDIRK2, exact He II Ly-alpha heating, unresolved OTS ledger, canonical forcing, owner law, and all previous endpoints fixed.
2. Give every node two independent first-order generators (`v_i`, `f_i`) and one local mixed generator (`v_i f_i`); do not collapse them to global parameters.
3. Preserve block-local support. Carry owner-normalization and forcing coupling as separately named low-rank global generators.
4. Remove H/He invariant directions analytically and prove generator-wise nuclei conservation.
5. Localize Hummer–Seaton table-knot events and restart the set representation there. No extrapolation or numerical floor.
6. Propagate a validated interval or ellipsoidal remainder and record generator rank, remainder radius, wrapping growth, event distance, and all set-valued ledgers per accepted step.
7. Reproduce point parity, all 24 prior trajectories, coherent auditor points, and interior node-local falsification samples.
8. Authorize an uncertainty-qualified first canonical interval only if all three shape lanes are continuously certified and every public width is below `2e-3`.

## Prohibited

No clipping, silent source-table extrapolation, global-coherence assumption without a named source-extension axiom, owner reassignment, `kappa=J/Phi` constitutive inversion, per-node fitting, post-hoc lane selection, recombination surrogate, CAMB transfer, or Bianchi feedback implementation.

The user performs remote push. Never claim a push without successful `git push` and post-push `git ls-remote` verification.
