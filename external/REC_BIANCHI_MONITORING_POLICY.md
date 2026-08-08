# rec_bianchi monitoring policy

`rec_bianchi` owns primordial recombination. `rei_bianchi` must never replace it with an implicit RECFAST/HyRec surrogate or absorb astrophysical reionization from it.

## Required checks

1. Before every new durable science stage:

```bash
./scripts/update_rec_bianchi_lock.sh
```

The resulting `external/rec_bianchi.lock.json` must be included in the stage input lock. A network/authentication failure is recorded as `REMOTE_UNAVAILABLE`; it is not silently treated as an unchanged dependency.

2. Weekly CI check:

`.github/workflows/rec-bianchi-monitor.yml` checks the private remote HEAD every Monday at 09:15 KST and on manual dispatch. Configure repository secret:

```text
REC_BIANCHI_READ_TOKEN
```

The token needs read-only access to `cosmosapjw-quantum/rec_bianchi`. The workflow uploads a fresh lock receipt. If the remote HEAD differs from the committed lock, the workflow fails so a human can review and intentionally update the adapter/input lock.

3. Before any primordial-to-CMB end-to-end claim:

- exact `rec_bianchi` commit SHA locked;
- provider declares `contains_astrophysical_reionization=false`;
- adapter/splice tests pass;
- electron fraction, matter temperature, derivatives, provenance, and interpolation error are carried across the handoff.

## Current status

The managed GitHub connector currently verifies `rec_bianchi/main` exactly, while a native `git ls-remote` may still be unavailable in an individual runtime. This permits read-only semantic monitoring but does not authorize an adapter, numerical-state import, surrogate, or primordial-to-CMB splice.
