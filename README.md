# rei_bianchi

Durable development and backup repository for extending homogeneous
reionization and CMB transfer to nonlinear, finite-tilt Bianchi cosmologies.

## Unified IGM development

On this research line, REI owns the integrated H/He/D gas, photon and CR work. The source and test trees for WU088_HH, BASS_HE and bass_cr live under `components/`. The BASS geometry/radiation and REC ionization crates used by the native calculation resolve locally. The original host, donor and data identities are recorded in the [current DAG, PR plan and claim contract](research/unified_igm_20261127/DAG.json).

With Python 3.12+, the project dependencies and Rust/Cargo installed, run:

```bash
python -m pip install .
python scripts/run_unified_igm.py results/unified_igm_run
```

Supply a new output directory. Append `--offline` when the Cargo registry cache is populated. The command computes two bounded native intervals, matched signed-shear accepted-step traces and source-on/off material interventions at five original AXBI states. [Research results and domains](research/unified_igm_20261127/REPORT_KO.md) · [component owners](components/README.md) · [continuation by thread](research/unified_igm_20261127/HANDOFF_KO.md).

## Historical main-branch checkpoint

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-R1-R1-R1-CROSS-SITE-STATE-FEEDBACK-REMAINDER-AND-TABLE-EVENT-LOCK
DURABLE_PASS_R2_R1A_R1_R1_R1_R1_R1_FOUR_SITE_MICROSTEP_ENCLOSURE_LOCAL_ERROR_CONTAINMENT_TABLE_RESTART_AND_STRUCTURAL_LEDGER_PASS_FIRST_CANONICAL_INTERVAL_AUTHORIZED
```

The current code certifies one four-site FLRW thermochemistry microstep at
partition `2048` in all three shape lanes. The maximum public uncertainty width
is `4.52488656108585e-05 < 2e-3`; the validated full-step/two-half-step local
error is `1.1621773858117024e-04 < 2e-4`. The new image contains the inherited
static trajectories, interior samples, and the stagewise-switch witness that
escaped the old static hull. Exact structural nuclei, photon-owner, and
augmented-energy identities close, and table-event restart semantics preserve
parent bytes.

This is not the complete first canonical interval or production history.
Production node chemistry, `R2C-R2`, `B2C2B`, recombination splice, CAMB
transfer, and Bianchi feedback remain unauthorized.

Next:

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-R1-R1-R1-R1-UNCERTAINTY-QUALIFIED-FIRST-CANONICAL-INTERVAL-ADAPTIVE-HISTORY
```

Read in order:

1. [`handoff/CURRENT_HANDOFF_PROMPT.md`](handoff/CURRENT_HANDOFF_PROMPT.md)
2. [`PROJECT_STATE.json`](PROJECT_STATE.json)
3. [`docs/science/current_00_READ_FIRST.md`](docs/science/current_00_READ_FIRST.md)
4. [`docs/provenance/DURABLE_STAGE_LEDGER.csv`](docs/provenance/DURABLE_STAGE_LEDGER.csv)

## Branch and artifact policy

- `main`: resumable source, compact authoritative artifacts, manifests, handoff,
  and tooling.
- `archive/full-history`: historical bundles and verified chunks.
- Failed attempts remain separate and are never overwritten by later success.

## Recombination provenance

The selected native REC source is in `components/bass_rec/rec/`. The independent historical production and monitoring records are in `external/`. The active z=20 HMLA donor retains its source identity in `components/bass_rec/fixtures/REC_HMLA_Z20.json`.

## Verification

```bash
./scripts/bootstrap_sandbox.sh
python scripts/verify_repo.py
```

## Remote status

This checkout contains the durable local stage and Git delivery objects. A
remote write is claimed only after `git ls-remote`, branch/tag pushes, and a
post-push SHA comparison all succeed.
