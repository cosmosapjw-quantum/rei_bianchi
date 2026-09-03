# Local Codex task — one post-`ntpath` standalone runtime attempt

## Task layer and hard stop

Task layer: `validate` only.

Start from the exact published handoff release, create a fresh standalone clone,
verify every precondition below, then invoke the native runner **exactly once**.
Preserve the first outcome without repair or retry.  A successful runtime result
opens only a separate audit node; it does not authorize the first canonical
interval.

## Release pins

```text
REPOSITORY=https://github.com/cosmosapjw-quantum/rei_bianchi.git
HANDOFF_BRANCH=agent/implementation/rei-runtime-bridge-ntpath-rebind-handoff-20260903-r1
HANDOFF_HEAD=<copy exact 40-hex SHA from delivery readback>
HANDOFF_TREE=<copy exact 40-hex tree from delivery readback>

PATCHED_PREDECESSOR=5b6957237bbe8edfdfe3c980910cba690d23775c
PATCHED_PREDECESSOR_TREE=805e92779ba6e7d956d5ac936f0934f5879fd3a1
PATCHED_INPUT_LOCK_SHA256=20db870e76ff8a82f2b6f6d38d90eb915b73d5564d6dfbee60a524862ab2e989
PRODUCTION_BRIDGE_SHA256=91fe316f1e8b81d64e9929d7a4814b77808fdf486e2ca67cd2f615e8617fce85

STACK_BASE_BRANCH=agent/implementation/rei-runtime-bridge-ntpath-rebind-handoff-20260903-r1
CONTINUATION_BRANCH=agent/implementation/rei-runtime-bridge-ntpath-rebind-validation-20260903-r1
PACKAGE=handoff/rei_runtime_bridge_ntpath_rebind_20260903
NEW_ATTEMPT_CLAIM=/tmp/rei-runtime-bridge-ntpath-rebind-20260903.native-attempt.json
OLD_CONSUMED_CLAIM=/tmp/rei-runtime-bridge-host-context-repair-20260901.native-attempt.json
```

The handoff commit cannot contain its own final SHA.  Obtain `HANDOFF_HEAD` and
`HANDOFF_TREE` from the delivery/readback, not from a mutable branch after the
run begins.  Missing pins imply `HANDOFF_RELEASE_PIN_MISSING` and no dispatch.

## Machine-bound inputs

1. `SECTION0_RECEIPT`: the existing regular non-symlink receipt with raw
   SHA-256
   `470fec225675a62a3c0121abcc4c568d345b088dd541a49fb18d91d6eacf104b`
   and status exactly `PASS_IMMUTABLE_SECTION_0`.
2. `RUSTC_LOCATOR`: the exact absolute executable Rust 1.94.1 compiler locator
   used by the pinned host context.  Do not use `command -v`, a rustup shim, an
   archive path, or an unverified replacement.

The Section 0 receipt is a host/toolchain identity input.  The patched
`INPUT_LOCK.json` is separately authenticated by the new runner wrapper.

## Forbidden actions

Do not delete or replace either attempt claim.  The old claim must remain
consumed; the new claim must be absent before dispatch and permanent after it.
Do not use `git worktree add/prune/repair/remove`, shallow or filtered clones,
alternates, reference/shared clones, force push, reset, clean, stash, rebase,
or a preexisting evidence root.  Do not edit the production bridge, patched
lock, Rust source, hashes, tolerances, formulas, or scientific tests.  Do not
broaden the stdlib allowlist.  Do not run JAX/JAXLIB, BASS/REC admission,
node 38382, REIAFF1, the 46,080-by-3 pilot, the first canonical interval, or
provider publication.

## Fresh clone and preflight

Create a private fresh root and clone normally with full object history.  Fetch
`HANDOFF_BRANCH`, require `FETCH_HEAD == HANDOFF_HEAD`, detach at that commit,
and require `HEAD^{tree} == HANDOFF_TREE`.  Before repository Python import,
prove:

- `PATCHED_PREDECESSOR` is an ancestor and its tree is exact;
- `.git` is a real private directory and the exact common Git directory;
- exactly one existing nonprunable worktree root;
- no shallow repository, promisor remote, partial-clone filter, alternates, or
  shared object store;
- `git fsck --full --no-progress` exits 0;
- clean worktree and `git diff --check`;
- `OLD_CONSUMED_CLAIM` exists and `NEW_ATTEMPT_CLAIM` does not exist.

Read `CONTRACT.json`, `README.md`, `PACKAGE_INDEX.json`, this prompt, the two
audit ledgers and the plot audit.  Run the handoff-only tests exactly once:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I -S -B \
  "$PACKAGE/test_runtime_bridge_runner.py"
```

Any preflight failure means `STOP_INVALID`; create a documentation-only stacked
checkpoint and do not invoke the native runner.

## Sole native invocation

Create a new external `LOG_ROOT`; require `EVIDENCE_ROOT` not to exist.  Capture
without `tee` and invoke exactly once:

```bash
set +e
env -i LANG=C LC_ALL=C PATH=/usr/bin:/bin TZ=UTC \
  PYTHONDONTWRITEBYTECODE=1 \
  /usr/bin/python3 -I -S -B \
  "$PACKAGE/runtime_bridge_runner.py" \
  --repo "$PWD" \
  --section0-receipt "$SECTION0_RECEIPT" \
  --rustc "$RUSTC_LOCATOR" \
  --evidence-root "$EVIDENCE_ROOT" \
  >"$LOG_ROOT/runner.stdout" 2>"$LOG_ROOT/runner.stderr"
RUNNER_EXIT=$?
set -e
printf '%s\n' "$RUNNER_EXIT" >"$LOG_ROOT/runner.exit"
```

Never invoke it again.  Require the new claim to exist afterward and hash it.

## First-outcome classification

- Exit `0`: accept only an exact create-only runtime receipt whose status,
  patched-input identity, attempt lineage, backend identity and claim ceiling
  match `CONTRACT.json`.  Do not run a successor.  Open the runtime-result audit.
- Exit `65`: preserve stderr verbatim as the new first blocker, every extant
  evidence/log hash, explicit receipt/artifact absence or presence, and stop.
- Other exit: record `UNEXPECTED_RUNNER_EXIT_<code>`, preserve evidence, stop.

Do not repair or retry inside this node.

## Durable publication

Edit only the durable progress checkpoint and add a create-only result receipt
or handoff-result directory if the existing repository policy requires it.
Record exact release pins, host inputs, clone proof, test result, sole command,
exit, claim hash, log/evidence hashes, first blocker and all unrun successors.
Do not change production bytes.

Create `CONTINUATION_BRANCH` from the exact handoff head, commit without force,
push, and open a stacked Draft PR against `STACK_BASE_BRANCH`.  Read back the
remote head/tree, OPEN+DRAFT state, base/head and checks.  No merge or ready
transition.

## Maximum possible claim

Even if exit `0`:

```text
runtime_bridge         RUNTIME_BRIDGE_PASS_WITH_PRESTART_PROCESS_BOUNDARY_RESIDUAL
process_boundary       RUST_BACKEND_CAPABILITY_PROCESS_BOUNDARY_MISSING
prestart_runtime       BLOCKED_PRESTART_ELF_INTERPRETER_IDENTITY_NOT_ESTABLISHED
production_parser      PRUNABLE_WORKTREE_ENUMERATION_UNHANDLED
adapter                STOP_INVALID
canonical_pilot        NOT_RUN
first_interval         NO_PASS_FIRST_CANONICAL_INTERVAL
provider_export        NOT_AUTHORIZED
scientific_pass        NOT_CLAIMED
scientific_publication NOT_RUN
```
