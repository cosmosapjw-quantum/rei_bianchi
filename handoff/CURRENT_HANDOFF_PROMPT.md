# CURRENT HANDOFF PROMPT — rei_bianchi / BASS

Treat this as a durable continuation of the public `rei_bianchi` repository
inside the BASS project. Repository bytes, hashes, ledgers and receipts are
authoritative; transcript claims are not evidence.

## Before calculation

1. Read `PROJECT_STATE.json`, `docs/science/current_00_READ_FIRST.md`, this file,
   `docs/provenance/DURABLE_STAGE_LEDGER.csv`, `external/rec_bianchi.lock.json`,
   and `external/REC_BIANCHI_MONITORING_POLICY.md`.
2. Run `python scripts/verify_repo.py`, current-stage tests, the exact validator,
   and `sha256sum -c` in the current stage.
3. Refresh read-only `rei_bianchi` and `rec_bianchi` refs. Record exact SHAs or
   explicit unavailable status. Never infer a successful push from local Git.
4. Create the next durable directory, input lock, state, receipts, manifest and
   `SHA256SUMS` before calculation.

## Conventions

- metric `(-,+,+,+)`; `epsilon_123=+1`;
- explicit `c`, `hbar`, `k_B`;
- homogeneous background, tetrad and 1+3 formalisms;
- all 11 Bianchi types ultimately supported, finite tilt and nonlinear shear.

## Current durable verdict

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-R1-SPARSE-LOCAL-GENERATOR-AFFINE-TAYLOR-MODEL-ENCLOSURE-LOCK
DURABLE_FAIL_CLOSED_R2_R1A_R1_R1_R1_SPARSE_LOCAL_SOURCE_AND_LOW_RANK_GLOBAL_COUPLING_PASS_STATIC_SUBSTEP_CONTROL_ESCAPED_BY_ADMISSIBLE_STAGEWISE_SCHEDULE_VALIDATED_DISCRETE_MAP_REMAINDER_NOT_CLOSED
```

At one evaluation site, local source and global normalization couplings are
represented exactly and sparsely. The local tangent-rank lower bound is `92003`,
the global-rank upper bound is `11`, and fixed-site storage is
`8847360` bytes.

The locked MPRK22/SDIRK2 map has four uncertain source evaluation sites. Without
a source regularity axiom their controls are independent. A localized
upper-to-lower schedule passes all hard gates but escapes the static hull in
`x_HeIII`; therefore a validated discrete-map remainder is still open.

The next input rank lower bound is `368012`, global-rank upper bound `44`, and
local polynomial storage `16.875 MiB`. This remains tractable. BASS Rust may
accelerate sparse contractions only after Python containment tests; it is not a
replacement for outward validated arithmetic.

Read-only exact refs at seal time:

```text
rei_bianchi/main = 2ad999ae2b4210eb740113b31ffe1f63884adfeb
rec_bianchi/main = 5e5ea3a15a8611587b43e89bbb932b02d2e13c0d
```

Native container Git could not resolve `github.com`. No remote write, PR or
merge is inherited from this stage.

## Next exact stage

Execute:

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-R1-R1-EVALUATION-SITE-SPARSE-GENERATOR-VALIDATED-MPRK22-SDIRK2-DISCRETE-MAP-ENCLOSURE-LOCK
```

1. Keep the 26-event registry, MPRK22(1), Alexander-SDIRK2, exact He II Ly-alpha
   heating, unresolved OTS ledger, canonical forcing, owner law and all prior
   endpoints fixed.
2. Assign independent `(v,f,vf)` generator blocks at `population_t0`,
   `population_t1_predictor`, `thermal_tgamma`, and `thermal_t1_final`.
3. Differentiate the actual positive MPRK22 solves and safeguarded SDIRK2 root,
   including state-dependent owner normalization, while preserving local block
   support and named low-rank reductions.
4. Construct an outward interval/ellipsoidal remainder for cross-site and
   state-feedback terms; Rust remains optional until Python containment and ULP
   parity pass.
5. Localize Hummer–Seaton knot crossings and restart fixed-topology maps.
6. Include point parity, all inherited static trajectories, the stagewise
   schedule witness, coherent-grid and node-local adversarial samples.
7. Close nuclei, photon, resolved heat, unresolved OTS, escaped and total-energy
   ledgers as set inclusions.
8. Authorize the first uncertainty-qualified canonical interval only if all
   three lanes are certified and public widths remain below `2e-3`.

## Prohibited

No clipping, silent source-table extrapolation, temporal/global coherence
without a named source axiom, owner reassignment, `kappa=J/Phi` constitutive
inversion, post-hoc lane selection, recombination surrogate, CAMB transfer or
Bianchi-feedback implementation.
