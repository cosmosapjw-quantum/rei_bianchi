# REI runtime-bridge execution handoff

This package is the immediate successor to the successful immutable Section 0
repair recorded by draft PR #28.  It deliberately exercises the pinned
Rust/MPFR bridge in a fresh Python process, but it does **not** claim to solve
the bridge's explicitly documented hostile-process-boundary limitation.

## What this can establish

- the repaired host can pass the bridge's own hash-admitted runtime identity
  checks;
- two fresh external Rust builds are byte-identical at the lock's expected
  artifact hash;
- the built native library reports the pinned ABI and rejects a
  zero-containing denominator before returning a result;
- the local run is tied to the exact Section 0 receipt by its raw SHA-256.

## What this cannot establish

The bridge itself says that its Python capability is invocation-scoped and is
not a hostile same-process boundary.  A child process cannot independently
authenticate the loader that started that child.  Therefore a successful run
has this exact terminal status:

```text
RUNTIME_BRIDGE_PASS_WITH_PRESTART_PROCESS_BOUNDARY_RESIDUAL
RUST_BACKEND_CAPABILITY_PROCESS_BOUNDARY_MISSING
BLOCKED_PRESTART_ELF_INTERPRETER_IDENTITY_NOT_ESTABLISHED
```

It leaves `adapter=STOP_INVALID` and never authorizes BASS/REC, four-site
operator, node-38382 replay, REIAFF1, formal/audit work, the canonical pilot,
or a scientific claim.

## Contents

- `CONTRACT.json` fixes the predecessor, required Section 0 receipt, backend
  identities, allowed actions, and claim ceiling.
- `runtime_bridge_runner.py` is a create-only external-evidence runner.  It
  has no numerical fallback and invokes the public bridge factories only.
- `LOCAL_CODEX_RUNTIME_PROMPT.md` is the exact local Codex handoff.
- `test_runtime_bridge_runner.py` is a small unit test for the runner's
  manifest and Section 0 receipt guards.

Verify `MANIFEST.sha256` before using the package.  The manifest covers every
package file except itself.
