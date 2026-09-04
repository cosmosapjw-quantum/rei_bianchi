# PHYS-MATH-CODE audit — 03A4 runtime-toolchain path binding

## Current claim

The source binds Section-0, read-only preflight, immediate pre-reservation re-attestation, protected global lease, persistent local lease, dispatch intent and post-lease worker to one canonical runtime-toolchain path snapshot.

## Actual evidence

- Draft PR #56 executed a six-obligation structural RED.
- A second test-only commit exposed four additional failures on the active freshness/live-readback controller lane.
- The combined behavior RED produced ten assertion failures and no errors.
- The GREEN validates the resolved files behind the exact paths used by the unchanged production bridge.
- A same-hash alternate copy is rejected.
- The preflight receipt records both the path rows and snapshot hash.
- The controller repeats the same validation before global reservation.
- Global, local and dispatch records carry one snapshot hash.
- The separate worker resolves and rechecks the same paths before `run_native_once`.
- Hosted CI has read-only contents permission and `REI_NATIVE_DISPATCH_FORBIDDEN=1`.

## Ranked residuals

### P1 — the interactive target host still has the wrong compiler bytes

Current `/usr/bin/x86_64-linux-gnu-gcc` resolves to package version `13.3.0-6ubuntu2~24.04.1` with SHA-256 `1b998261...`, not the locked `6117c525...`. Source GREEN cannot turn this host observation into a Section-0 PASS.

### P1 — full host epoch is not yet reconstructed

The historical compiler package is identified, but the full thirteen-field toolchain and pre-start ELF closure must be checked in one isolated canonical environment. Recovering only GCC is insufficient.

### P1 — canonical-path mutation window remains bounded but nonzero

Preflight, immediate pre-reservation and worker checks reduce path drift windows. A privileged host administrator can still mutate system paths between observations. This residual belongs to the host threat model and must be stated; source code cannot make a mutable host filesystem cryptographically immutable.

### P1 — native worker remains single-use and irreversible

Once the protected global ref is created, later failure consumes the final attempt. The source GREEN therefore does not authorize execution before isolated host reconstruction and a fresh static-preflight review.

### P2 — source layering is complex

The active package preserves legacy donors and wraps them. Tests now verify wrapper-to-donor delegation rather than requiring all process logic in one file. Future changes must retain exact package-index binding to avoid donor drift.

### P2 — historical package evidence is operator-local

The repository records the transcript hash, snapshot metadata, DEB hash and extracted binary hash, but does not independently fetch the operator's Dropbox bundle. It is provenance evidence, not timeless execution authority.

## Strongest failure mode prevented

Before this change, an alternate copy of the historical GCC could satisfy preflight while the unchanged post-lease bridge invoked the newer canonical compiler after global reservation. The attempt could be consumed before the mismatch was detected. The GREEN blocks that state by requiring witness-path equality and by carrying the same snapshot into the worker.

## Disposition

```text
runtime-path-binding source      candidate pending exact-head CI
historical compiler package      identified
current interactive host         incompatible
isolated host epoch              not reconstructed
successor Section-0              not run
static preflight                 not run
global/local leases              absent
native runtime                   not run
```
