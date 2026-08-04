# rei_bianchi

Durable development and backup repository for extending homogeneous reionization and CMB transfer to nonlinear, finite-tilt Bianchi cosmologies.

## Current scientific state

The latest authoritative stage is:

```text
P0.5-B2C2B0C-R1-NODE-RESOLVED-JOINT-CHEMISTRY-SINK-HISTORY-LOCK
DURABLE_FAIL_CLOSED_QUASISTATIC_MACRO_CLOUD_OPACITY_MASS_DIVERGENCE
```

Photon and H/He nuclei accounting close, but the independently quasi-static macro cloud closure is non-convergent. The first-interval sink fraction changes by a factor 4.503 between one and two steps; four/eight-step refinements have no feasible macro capacity allocation. At fixed effective opacity, macro cloud mass diverges as the sink ionized fraction approaches one. `B2C2B` therefore remains unauthorized.

The next stage is:

```text
P0.5-B2C2B0C-R2A-GLOBAL-MOMENT-CONSTRAINED-MACRO-SINK-DISTRIBUTION-LOCK
```

Read in order:

1. [`handoff/CURRENT_HANDOFF_PROMPT.md`](handoff/CURRENT_HANDOFF_PROMPT.md)
2. [`PROJECT_STATE.json`](PROJECT_STATE.json)
3. [`docs/science/current_00_READ_FIRST.md`](docs/science/current_00_READ_FIRST.md)
4. [`docs/roadmap/D0_PR_ROADMAP.md`](docs/roadmap/D0_PR_ROADMAP.md)
5. [`sandbox/SANDBOX_SETUP.md`](sandbox/SANDBOX_SETUP.md)

## Branch policy

- `main`: resumable source, compact authoritative artifacts, manifests, handoff, and tooling.
- `archive/full-history`: all currently available historical bundles, splitting files above 48 MiB into verified chunks.

## External recombination dependency

Primordial recombination remains a separate project:

```text
https://github.com/cosmosapjw-quantum/rec_bianchi
```

Before each new science stage, run:

```bash
./scripts/update_rec_bianchi_lock.sh
```

The reionization project must not implement or silently substitute the recombination module.

## Verification

```bash
./scripts/bootstrap_sandbox.sh
python scripts/verify_repo.py
```

## Remote status

The repository package was created in a runtime with no GitHub DNS/authentication. The local Git history and bundles are complete, but remote upload must be performed from an authenticated machine using `scripts/push_to_github.sh`.
