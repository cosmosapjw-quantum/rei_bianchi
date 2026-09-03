# PHYS-MATH and PHYS-MATH-CODE audit

## PHYS-MATH

Status: `PASS_NO_PHYSICS_DELTA`.

This test-only RED changes no equation, coefficient, tolerance, unit, sign, frame, gauge, opacity, thermochemistry, interval-arithmetic expression, or source term.

The BASS state-surface distinction remains mandatory:

```text
frequency-preserving primary pair
  f(q,e) <-> F_Aell(q)

integrated states requiring certified source projection or closure
  J_Aell^(i)
  G(e)
```

A runtime or first-interval result cannot by itself authorize a general frequency-dependent REI source on an integrated BASS state.  REC remains the representation-neutral source authority; BASS owns state evolution and representation machinery.

The formula SSOT remains limited to homogeneous photon transport and cold, non-tilted electron-rest Thomson scattering.  Finite electron tilt, recombination/reionization microphysics, numerical evolution, solver admission, and inference are outside that theorem scope.

## PHYS-MATH-CODE

### P0

1. `P0_CONFIGURABLE_GITHUB_AUTHORITY`
   - The preflight and controller expose a production-callable `api_base` and public `--api-base` option.
   - A non-GitHub endpoint can emulate absence observations and a successful reservation response.

2. `P0_EXECUTING_PACKAGE_NOT_BOUND_TO_VERIFIED_HEAD`
   - The active package self-checks its own adjacent index.
   - The supplied standalone repository is verified separately.
   - No cross-binding proves that the authorizing bytes are the exact package bytes under the verified `HEAD`.

### P1

1. Preflight observations do not fully bind API authority, repository, method, exact ref, expected target, ordinal, and HTTP status.
2. The receipt validator does not bind the controller's actual attempt-state root, output root, and successor-receipt path.
3. Only Python and rustc are rechecked immediately before orchestration; the complete 13-field successor toolchain is not.
4. Repository-level ruleset readback is empty; server-side update/deletion protection for `attempt-ledger/**` is not established.
5. A freshness/expiry policy for target-host preflight receipts is not yet enforced.

### What remains valid

- PR #45's import-order firewall is valid at source and exact-head CI level.
- Production import remains confined to the separate post-lease worker.
- No global ref, local lease, dispatch intent, native result, first interval, or provider admission was created by this RED.

### Disposition

```text
STOP_BEFORE_TARGET_HOST_PREFLIGHT
remaining_native_attempts = 1
global_attempt_ref        = ABSENT_404
native_runtime            = NOT_RUN
```

The next repair must be minimal: fixed GitHub authority, exact package-to-HEAD binding, exact receipt/path binding, and full pre-lease toolchain revalidation.  Server-side ref protection is a separate administrative gate.

## Plot/CRAG reading

Current path:

```text
verify repository
-> self-check possibly copied package
-> configurable API observations/reservation
-> local lease
-> worker
```

Required path:

```text
verify repository
-> bind executing package to exact HEAD blobs
-> fixed api.github.com authority
-> exact observations and path-bound receipt
-> recheck all 13 toolchain fields
-> verify attempt-ref protection
-> atomic global lease
-> persistent local lease
-> dispatch intent
-> worker
```

CRAG verdict:

- Correctness: the import-order claim survives.
- Retrieval: the stronger exactly-once authority claim exceeds current code evidence.
- Augmented: fake-authority and copied-package mutations defeat the stronger claim.
- Generation: the GREEN repair must add pre-reservation barriers without moving the worker before either lease.

Final classification: `NARROWED_CLAIM`.
