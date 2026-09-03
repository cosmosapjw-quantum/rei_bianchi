# PHYS-MATH-CODE audit — fresh standalone handoff rebind

## Disposition

```text
HANDOFF_IMPLEMENTED
NATIVE_RUNTIME_NOT_RUN
```

## Equation-to-code effect

There is no equation-to-production-code delta.  The changed code is confined
to a new handoff package and one CI workflow.  The exact production files are
read-only inputs:

```text
INPUT_LOCK.json
rust_source_bound_thermal.py
RUST_IMPLEMENTATION_AMENDMENT.json
rust/source_bound_thermal.rs
```

## What the wrapper adds

1. Exact PR #37 predecessor commit/tree binding.
2. Exact patched `INPUT_LOCK` SHA-256 and semantic checks.
3. Exact unchanged production-bridge SHA-256 check.
4. Closed package verification by Git blob identity.
5. New material-delta-specific create-only attempt lease.
6. Receipt augmentation with patched-input and attempt lineage.

The inherited PR #31 runner remains a byte-identical base file.  Only its
handoff-module globals are adapted; the production REI bridge is never
monkeypatched.

## Test sufficiency

The standard-library-only suite includes positive and hostile cases for:

```text
closed package scope
unindexed file rejection
contract identity
actual PR #37 lock/bridge binding
lock hash drift
Section 0 exact regular-file input
standalone clone and alternates rejection
new O_EXCL claim
second-dispatch rejection
unexpected-error fail closure
```

The generic GitHub workflow validates package construction.  It deliberately
does not run the host-bound native path or weaken executable identity checks.

## Ranked findings

### P0 — none in the handoff design

No reproducible P0 remains before publication of this handoff package.

### P1 — native host result absent

The package cannot close the runtime node until the exact pinned host executes
one attempt.  A green generic CI result is not substitute evidence.

### P1 — release head/tree are delivery-time pins

The final handoff commit cannot contain its own SHA.  Local execution must copy
the exact published head/tree from remote readback before any attempt claim is
created.

### P1 — Section 0 scope must not drift

The old external receipt is accepted only for its original pinned
host/toolchain-identity role.  The patched lock is separately checked.  Any
claim that the old receipt itself attests the new lock is forbidden.

### P2 — inherited residuals

```text
RUST_BACKEND_CAPABILITY_PROCESS_BOUNDARY_MISSING
BLOCKED_PRESTART_ELF_INTERPRETER_IDENTITY_NOT_ESTABLISHED
PRUNABLE_WORKTREE_ENUMERATION_UNHANDLED
```

They remain explicit even after a future runtime exit `0`.

## Genuine completion

```text
new handoff contract and package closure
new attempt identity and non-reuse rule
pre-dispatch patched-input binding
focused portable tests
CI-only publication gate
```

## Still uncertain or unrun

```text
pinned-host executable identities in the next session
native Rust build and interval calls
first post-ntpath blocker
runtime receipt/native artifact
first canonical interval
provider or science readiness
```
