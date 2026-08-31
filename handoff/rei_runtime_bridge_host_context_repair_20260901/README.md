# REI runtime bridge host-context repair handoff

This package is the single diagnostic successor to the fail-closed runtime
attempt recorded in draft PR #30.  It replaces one invalid operational
assumption—"fresh linked worktree"—with a fresh standalone clone, and replaces
an environment-dependent compiler lookup with a required absolute `--rustc`
locator.  It does not change the production bridge, Rust source, locks,
certificates, numerical acceptance conditions, or scientific status.

## Research-loop decision

The observed exception occurred while checking the evidence-root location,
before Rust compilation, interval division, BASS/REC, the four-site operator,
or any canonical node replay.  Therefore it provides no new evidence for or
against the interval mathematics or the physical model.

Three candidates were compared:

| Candidate | Decision | Reason |
| --- | --- | --- |
| production prunable-aware parser | `HOLD` | coherent long-term fix, but changes a locked bridge and requires a new Section 0 binding |
| fresh standalone clone + explicit locator | `PROMOTE` | isolates stale Git metadata without changing scientific or production bytes |
| `git worktree prune` | `REJECT` | mutates shared Git administration state and is unnecessary for this run |

The interval-Newton/Krawczyk and directed-rounding literature supports judging
an executed enclosure through its mathematical certificate, not through host
metadata.  No such numerical execution occurred in PR #30, so the only valid
claim remains `NO_PASS_FIRST_CANONICAL_INTERVAL`.

## Policy compilation

The four supplied Universal directives are applied here as executable choices,
not copied into a new policy layer:

- progress-first: perform one materially different runtime attempt rather than
  another governance cycle;
- typed identity: stale linked-worktree records are execution metadata, while
  the bridge/source/receipt/artifact retain their exact byte gates;
- audit-compiled plan: each observed or predicted P0/P1 has one mechanical
  guard in `CONTRACT.json` and the focused tests;
- anti-stall checkpointing: PR #30 was attempt one; this package permits one
  diagnostic attempt and zero retries.

## What changed from the prior handoff

- execution is accepted only from a non-shallow standalone clone whose `.git`
  is its own common directory, whose worktree inventory has exactly one
  existing non-prunable root, and which has no object alternates;
- `--rustc` is mandatory, absolute, and bound to `REI_RUSTC_1_94_1` before the
  bridge is loaded; the path is only a locator and the existing bridge remains
  the compiler-byte and closure authority;
- worktree-context failures are typed before the locked production helper is
  reached;
- the prompt permits at most one native runner invocation and specifies exit
  `0`, `65`, and unexpected-exit checkpoint behavior.
- a fixed create-only attempt claim is acquired at runner entry, so a second
  invocation fails before dispatch even if it uses a different evidence root;
  the claim must never be deleted or replaced.

## Residuals deliberately preserved

A standalone clone avoids the reported stale record; it does not repair the
production `_worktree_roots()` parser.  A successful run still reports:

```text
RUST_BACKEND_CAPABILITY_PROCESS_BOUNDARY_MISSING
BLOCKED_PRESTART_ELF_INTERPRETER_IDENTITY_NOT_ESTABLISHED
PRUNABLE_WORKTREE_ENUMERATION_UNHANDLED
```

and keeps `adapter=STOP_INVALID`.  BASS/REC, Task 6, node 38382, REIAFF1,
formal/audit stages, the 46,080-by-3 pilot, and publication remain out of scope.

## Contents

- `CONTRACT.json` is the closed authority, risk, attempt-budget, and claim
  contract.
- `runtime_bridge_runner.py` performs the bounded create-only execution.
- `test_runtime_bridge_runner.py` covers the new host-context and locator
  failure classes without compiling or loading native code.
- `LOCAL_CODEX_RUNTIME_PROMPT.md` is the local Codex handoff.
- `MANIFEST.sha256` covers every package file except itself.
