# PHYS-MATH-CODE audit — successor Section-0 read-only preflight

## Disposition

```text
PREFLIGHT_SOURCE_IMPLEMENTED
TARGET_HOST_REATTESTATION_NOT_RUN
```

## Implemented controls

- exact PR #42 commit/tree binding;
- Git-blob binding for the PR #42 executable contract/runner and PR #41
  successor policy/emitter;
- closed package index without a self-hash cycle;
- fresh standalone-clone checks through the PR #42 pinned bridge path;
- exact successor-receipt status/schema/semantic-lock checks;
- read-only global-ref observations using HTTP GET only;
- explicit `404 = observed absent, authority effect NONE` semantics;
- persistent empty attempt-state root outside `/tmp` and Git worktrees;
- create-only output directory and receipts;
- source guard forbidding global lease, local lease, and native dispatch APIs;
- mandatory second read-only observation after Section-0 emission;
- unchanged first-interval/provider claim ceiling.

## Fail-closed behavior

The preflight stops before any execution state on:

```text
existing global attempt ref
ambiguous HTTP response or transport failure
wrong release head/tree or source blob
non-standalone or dirty clone
successor toolchain mismatch
historical receipt reuse
attempt-state contamination
output path under tmp/repository/state root
pre-existing output path
```

## Important remaining boundary

The GitHub workflow validates portable logic and observes the public ref, but a
hosted runner is not the target successor host.  A complete node requires the
actual 13-field toolchain re-attestation on a machine that can reproduce the
semantic lock.

No global lease may be created merely because this source passes CI.  The
single remaining attempt is consumed only by the later atomic remote
reservation.

## Residual risks

1. Two GET observations do not eliminate a race.  This is intentional: they
   are diagnostics only; the later atomic create operation is the authority.
2. Exact binary equivalence does not establish kernel/process isolation beyond
   the already declared residual blockers.
3. The target host must preserve both successor and preflight receipts outside
   ephemeral storage.
4. A failed Section-0 comparison must retain its mismatch evidence without
   broadening the semantic lock.

## Withheld claims

```text
SUCCESSOR_SECTION0_PASS_ON_REAL_HOST
GLOBAL_ATTEMPT_RESERVED
NATIVE_RUNTIME_PASS
FIRST_CANONICAL_INTERVAL
REI_PROVIDER_EXPORT
BASS_REC_REI_COMPATIBILITY
SCIENTIFIC_VALIDITY
```
