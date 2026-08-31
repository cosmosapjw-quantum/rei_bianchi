# Local Codex task: standalone-host Rust runtime bridge validation

## Outcome and task layer

Task layer: `validate` only.

From the exact published handoff head, create a fresh standalone clone, run all
read-only/focused preflights, invoke the sealed native runner **at most once**
with the repaired-host Rust compiler supplied as an explicit absolute locator,
then preserve the exact outcome in one stacked draft checkpoint PR.

This does not repair production `_worktree_roots()` and cannot raise a
scientific claim.

## Release pins

```text
REPOSITORY=https://github.com/cosmosapjw-quantum/rei_bianchi.git
HANDOFF_BRANCH=agent/implementation/rei-runtime-bridge-host-context-repair-handoff-20260901-r1
HANDOFF_HEAD=<copy the exact 40-hex SHA from the delivery message>
HANDOFF_TREE=<copy the exact 40-hex tree from the delivery message>
IMMUTABLE_PREDECESSOR=723882d80d57ee8a919bc52ab74633b743447d0c
IMMUTABLE_PREDECESSOR_TREE=3fe6f79d210085d1f44de14cca53d9ed1cff347e
STACK_BASE_BRANCH=agent/implementation/rei-runtime-bridge-host-context-repair-handoff-20260901-r1
CONTINUATION_BRANCH=agent/implementation/rei-runtime-bridge-host-context-validation-20260901-r1
PACKAGE=handoff/rei_runtime_bridge_host_context_repair_20260901
ATTEMPT_CLAIM=/tmp/rei-runtime-bridge-host-context-repair-20260901.native-attempt.json
```

The commit cannot contain its own SHA.  `HANDOFF_HEAD` and `HANDOFF_TREE` are
therefore supplied by the delivery readback, not inferred from a mutable branch
after execution begins.  If either value is unavailable, stop with
`HANDOFF_RELEASE_PIN_MISSING`.

## Machine-bound required inputs

1. `SECTION0_RECEIPT`: absolute path to the existing regular, non-symlink JSON
   receipt with raw SHA-256
   `470fec225675a62a3c0121abcc4c568d345b088dd541a49fb18d91d6eacf104b`
   and status exactly `PASS_IMMUTABLE_SECTION_0`.
2. `RUSTC_LOCATOR`: explicit absolute path to the installed Rust 1.94.1
   compiler used by the successful repaired-host Section 0 context.  Do not use
   `command -v`, a rustup shim, the obsolete scratch default, or the Desktop
   archive itself.  Do not execute the compiler during preflight.  The runner
   treats this as a locator; the unchanged bridge authenticates its bytes.

If either exact input cannot be identified, do not invoke the runner.  Record
the first typed blocker and checkpoint.

## Hard boundaries

Do not use `git worktree add`, `prune`, `repair`, `remove`, or delete stale Git
metadata.  Do not reset, clean, stash, rebase, force-push, overwrite or reuse a
temporary/evidence path, change production/lock/scientific bytes, or retry the
runner.  Do not delete, replace, or bypass `ATTEMPT_CLAIM`; it must be absent
before the sole invocation and is thereafter permanent evidence that the
attempt budget is consumed.  Do not run JAX/JAXLIB, BASS/REC, Task 6, node 38382, REIAFF1, formal
systems, PHYS-MATH audits, the 46,080-by-3 pilot, or publication.

## Fresh standalone clone

Create a new mode-private session root with `mktemp -d`; its `repo` child must
not exist.  Clone the canonical remote normally and fully—no `--depth`,
`--filter`, `--shared`, `--reference`, alternates, or linked worktree.  Fetch
`HANDOFF_BRANCH`, require `FETCH_HEAD == HANDOFF_HEAD`, detach at that exact
commit, verify `HEAD^{tree} == HANDOFF_TREE`, then create
`CONTINUATION_BRANCH` from the handoff head only after proving that branch is
absent locally and remotely.

Before any repository Python import or runner invocation require:

- exact predecessor ancestry and tree;
- `.git` is a real directory and is also the clone's exact Git common dir;
- `git worktree list --porcelain` contains one existing root and no `prunable`;
- no shallow repository, partial clone, promisor remote, or object alternates;
- `git fsck --full --no-progress` exits 0 (dangling notices are not corruption);
- clean status and `git diff --check`.

Read `CONTRACT.json`, `README.md`, this prompt, and `MANIFEST.sha256`.  Verify
the closed manifest.  Then run exactly this focused non-native test command:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I -S -B \
  "$PACKAGE/test_runtime_bridge_runner.py"
```

Any preflight failure means `STOP_INVALID`; checkpoint without invoking the
runner.

## Sole native invocation

Create a fresh external `LOG_ROOT` with `mktemp -d`.  Set
`EVIDENCE_ROOT="$LOG_ROOT/runtime-evidence"` and require that child not to
exist.  Capture output without `tee`.  Invoke exactly once:

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

This is the only permitted runner/native invocation.  Never invoke it again,
regardless of exit status.  Require `ATTEMPT_CLAIM` to exist afterward and
record its SHA-256 in the checkpoint.

## Decision and durable checkpoint

- Exit `0`: accept only if the create-only receipt exists and its
  schema/status/claim ceiling match `CONTRACT.json`.  Hash the receipt,
  stdout, stderr, and exit record.  Preserve all three residual blockers and
  the scientific claim ceiling.
- Exit `65`: do not repair or retry.  Hash every extant log/evidence file,
  record the first typed blocker verbatim, and preserve all statuses.
- Any other exit: record `UNEXPECTED_RUNNER_EXIT_<code>`, hash extant
  evidence, do not retry, and preserve all statuses.

Edit only
`.superpowers/sdd/2026-08-30-rei-rust-rebuild-followthrough/progress.md`.
Record the exact release pins, standalone-clone proof, required-input hashes,
focused test command/count/exit, the single runner command/exit/log hashes,
receipt hash or explicit absence, first blocker, all `NOT_RUN` successors, and
unchanged claim ceiling.  Run `git diff --check` and the package unit test once
more only if the package itself was not modified; do not rerun the native
runner.

Commit and push `CONTINUATION_BRANCH` without force, then open a stacked draft
PR whose base is `STACK_BASE_BRANCH`.  Read back the exact remote head/tree,
OPEN+DRAFT state, base/head, merge state, and checks.  If the remote branch
already exists or publication credentials fail, stop with
`GITHUB_PUBLICATION_UNAVAILABLE`; never claim a PR that was not read back.

On success the maximum status is still:

```text
runtime_bridge         RUNTIME_BRIDGE_PASS_WITH_PRESTART_PROCESS_BOUNDARY_RESIDUAL
process_boundary       RUST_BACKEND_CAPABILITY_PROCESS_BOUNDARY_MISSING
prestart_runtime       BLOCKED_PRESTART_ELF_INTERPRETER_IDENTITY_NOT_ESTABLISHED
production_parser      PRUNABLE_WORKTREE_ENUMERATION_UNHANDLED
adapter                STOP_INVALID
canonical_pilot        NOT_RUN
first_interval         NO_PASS_FIRST_CANONICAL_INTERVAL
scientific_pass        NOT_CLAIMED
scientific_publication NOT_RUN
```
