# Local Codex task: bounded Rust runtime-bridge execution

## Task layer

`validate` only.  Do not repair or redesign the bridge.  This task begins only
after the exact Section 0 host repair captured in draft PR #28.

## Immutable inputs

- Handoff package: `handoff/rei_runtime_bridge_execution_20260831/`
- Base handoff commit: the branch containing this package, which must descend
  from `7c0a57878fd565599019a0743ffb796e00bdd101`.
- Required prior receipt: raw SHA-256
  `470fec225675a62a3c0121abcc4c568d345b088dd541a49fb18d91d6eacf104b`,
  with JSON `status` exactly `PASS_IMMUTABLE_SECTION_0`.

Read `CONTRACT.json`, `README.md`, and `MANIFEST.sha256` before execution.
If any is missing, malformed, or mismatched, stop with `STOP_INVALID`.

## Worktree and authority rules

1. Fetch the branch containing this package and create a fresh isolated local
   worktree from it.  Do not reset, clean, stash, rebase, or modify an existing
   worktree.  Do not overwrite any evidence directory.
2. Before execution, ensure that the worktree is clean, `git fsck --full` is
   clean, and the package unit test passes.  The runner independently repeats
   the hash-admitted Git ancestry and `fsck` checks.
3. Locate the actual fresh Section 0 JSON receipt.  Pass its absolute path to
   the runner; never recreate, summarize, or substitute the receipt.
4. Choose a nonexistent evidence-root outside every Git worktree, for example
   a fresh `/tmp/rei-runtime-bridge-...` directory.  The runner creates it
   once and emits its receipt there.  Never point at a preexisting directory.

Run exactly:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I -S -B \
  handoff/rei_runtime_bridge_execution_20260831/test_runtime_bridge_runner.py

env -i LANG=C LC_ALL=C PATH=/usr/bin:/bin TZ=UTC PYTHONDONTWRITEBYTECODE=1 \
  /usr/bin/python3 -I -S -B \
  handoff/rei_runtime_bridge_execution_20260831/runtime_bridge_runner.py \
  --repo "$PWD" \
  --section0-receipt /absolute/path/to/section0-receipt.json \
  --evidence-root /tmp/rei-runtime-bridge-unique
```

The runner is the only permitted native execution in this task.  It validates
the package, section receipt, predecessor ancestry, runtime closure, two fresh
external builds, artifact/receipt byte identity, a nonzero interval division,
and zero-divisor rejection.

## Decision rule

On exit `0`, preserve the full external receipt and record only its SHA-256
and this exact state in `progress.md`:

```text
runtime_bridge = RUNTIME_BRIDGE_PASS_WITH_PRESTART_PROCESS_BOUNDARY_RESIDUAL
process_boundary = RUST_BACKEND_CAPABILITY_PROCESS_BOUNDARY_MISSING
prestart_runtime = BLOCKED_PRESTART_ELF_INTERPRETER_IDENTITY_NOT_ESTABLISHED
adapter = STOP_INVALID
canonical_pilot = NOT_RUN
first_interval = NO_PASS_FIRST_CANONICAL_INTERVAL
scientific_pass = NOT_CLAIMED
scientific_publication = NOT_RUN
```

Then commit only the progress/evidence-index documentation that refers to the
external receipt, push a new continuation branch, and open a stacked **draft**
PR against the branch containing this handoff.  Read back the exact remote
head/tree and CI state.

On exit `65` or any unexpected exception, do not change production code,
locks, or scientific status.  Preserve the terminal output/evidence that
exists, record the first typed blocker, commit only that durable state if it
can be done without concealing the failure, and open a stacked draft PR.

## Explicit non-goals

Do not run BASS/REC admission, Task 6 production four-site computation, node
38382, REIAFF1, formal systems, PHYS-MATH/PHYS-MATH-CODE audits, the
46,080-by-3 pilot, or publication.  Do not use JAX/JAXLIB.  A successful run
is not an independently authenticated hostile process boundary and cannot
change the scientific claim ceiling.
