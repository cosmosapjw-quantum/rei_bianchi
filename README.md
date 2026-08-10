# rei_bianchi

Durable development and backup repository for extending homogeneous
reionization and CMB transfer to nonlinear, finite-tilt Bianchi cosmologies.

## Current scientific state

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-R1-R1-EVALUATION-SITE-SPARSE-GENERATOR-VALIDATED-MPRK22-SDIRK2-DISCRETE-MAP-ENCLOSURE-LOCK
DURABLE_FAIL_CLOSED_R2_R1A_R1_R1_R1_R1_FOUR_SITE_PRIMAL_PARITY_AND_LOCAL_IMPLICIT_CERTIFICATES_PASS_CROSS_SITE_STATE_FEEDBACK_REMAINDER_EVENT_RESTART_AND_SET_LEDGER_UNCLOSED
```

The current code reproduces the inherited four-site lower-corner trial exactly
and certifies all frozen-state local MPRK22 population blocks and fixed-heating
SDIRK2 roots over 46,080 nodes in all three shape lanes. The remaining blocker
is the outward nonlinear composition across independent evaluation-site
controls, state-dependent owner normalization, Hummer-Seaton topology events
and set-valued photon/energy ledgers. Production history and node chemistry are
not authorized.

Next:

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-R1-R1-R1-CROSS-SITE-STATE-FEEDBACK-REMAINDER-AND-TABLE-EVENT-LOCK
```

Read in order:

1. [`handoff/CURRENT_HANDOFF_PROMPT.md`](handoff/CURRENT_HANDOFF_PROMPT.md)
2. [`PROJECT_STATE.json`](PROJECT_STATE.json)
3. [`docs/science/current_00_READ_FIRST.md`](docs/science/current_00_READ_FIRST.md)
4. [`docs/provenance/DURABLE_STAGE_LEDGER.csv`](docs/provenance/DURABLE_STAGE_LEDGER.csv)

## Branch and artifact policy

- `main`: resumable source, compact authoritative artifacts, manifests and handoff.
- `archive/full-history`: historical bundles and verified chunks.
- Failed attempts remain separate and are never overwritten by later success.

## External recombination dependency

Primordial recombination remains in `https://github.com/cosmosapjw-quantum/rec_bianchi`.
Run `./scripts/update_rec_bianchi_lock.sh` before a new science stage and follow
`external/REC_BIANCHI_MONITORING_POLICY.md`. No surrogate or silent replacement
is allowed.

## Verification

```bash
./scripts/bootstrap_sandbox.sh
python scripts/verify_repo.py
```

## Remote status

The repository is public. In the runtime that sealed the current stage, native
Git and API DNS resolution failed, so no remote write, PR or merge is claimed.
Use the stage Git bundle from an authenticated network and verify post-push SHAs.
