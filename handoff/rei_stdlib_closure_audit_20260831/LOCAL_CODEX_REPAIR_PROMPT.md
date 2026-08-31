# Local Codex job — exact Rust stdlib closure materialization repair

Continue from the immutable intake checkpoint, not from a new inferred source:

```text
parent branch  agent/implementation/rei-git-small-authority-intake-20260831-r1
parent commit  507f7ce36d54d9879b8bdf4c2ed49994162ad16d
parent tree    ae747a8e28beaa1dda18f4eccc955b153950142d
parent PR      #26 (draft)
```

Create a fresh isolated continuation worktree and a new stacked draft branch.
Preserve all existing worktrees, untracked prototypes, receipts, and branches.
Before any authority interpretation, verify the parent commit/tree, `git fsck
--full`, inherited manifests, and this directory's `MANIFEST.sha256`.

## Proven explanation

The stopped Section 0 observation `7aae...` is exactly the closure of the 62
direct files supplied by the `rust-std` component. The unchanged locked digest
`1d6d...` is exactly the closure of those 62 files **plus both** exact
`llvm-tools-preview` files declared in `REPAIR_CONTRACT.json`. This is a
component-materialization omission, not a numerical or compiler-byte repair.

Do not modify `build_and_test.sh`, its expected digest, `INPUT_LOCK`, a source
file, or an existing stdlib file. Do not invoke `rustc`, `cargo`, repository
Python, JAX, a native build/runtime path, or an archive member before the
fresh Section 0 boundary described below.

## Absolute locators required

Use only the exact locations admitted by the prior Section 0 attempt:

- `RUST_ARCHIVE`: the real, non-symlink
  `08-rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz` whose SHA-256 is
  `294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40`.
- `STDLIB_DIR`: the real, non-symlink direct directory that the failed
  immutable Section 0 used for
  `RUST_SYSROOT/lib/rustlib/x86_64-unknown-linux-gnu/lib`.
- `EVIDENCE_DIR`: a newly created real directory outside the Git worktree;
  every output receipt path below must be absent before it is passed to a tool.

If any locator is unavailable or not exactly identified, create the durable
stacked draft STOP checkpoint with that first failure and stop. Do not discover
a substitute directory by running `rustc`.

Set only task-specific shell variables:

```bash
REI_PKG=handoff/rei_stdlib_closure_audit_20260831
RUST_ARCHIVE=/absolute/admitted/project_sources/08-rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz
STDLIB_DIR=/absolute/admitted/rust-prefix/lib/rustlib/x86_64-unknown-linux-gnu/lib
EVIDENCE_DIR=/absolute/new-evidence-directory
```

## A. Read-only confirmation of the stopped 62-member state

Run this once, with a new receipt path. Exit 65 is expected only for the
identified closure mismatch; it is not a prompt to change an input.

```bash
/usr/bin/python3 -I -S -B "$REI_PKG/stdlib_closure_audit.py" \
  --stdlib-dir "$STDLIB_DIR" \
  --rust-archive "$RUST_ARCHIVE" \
  --archive-prefix rust-1.94.1-x86_64-unknown-linux-gnu/rust-std-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/ \
  --expected-archive-sha256 294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40 \
  --expected-closure-sha256 1d6d31c8f1c99b69b120c91fcff14220bbfcf0e8f976096f0c4992b7e2edc799 \
  --reported-observed-sha256 7aae7f6cffe33365096e9f837378c9a26de46efd7d109eccd446d45703eee6c0 \
  --receipt "$EVIDENCE_DIR/stdlib-closure-base-audit.json"
```

Required interpretation before repair:

- `member_comparison.status` is `PASS` with 62 archive and 62 directory
  members;
- Python and shell legacy replays equal the reported `7aae...` value; and
- the first failure is
  `RUST_STDLIB_CLOSURE_SHA256_MISMATCH_CONFIRMED`.

Any other output is `STOP_INVALID`; preserve it and stop.

## B. Dry-run the only permitted repair

This consumes the exact archive but writes no stdlib file.

```bash
/usr/bin/python3 -I -S -B "$REI_PKG/materialize_missing_components.py" \
  --stdlib-dir "$STDLIB_DIR" \
  --rust-archive "$RUST_ARCHIVE" \
  --contract "$REI_PKG/REPAIR_CONTRACT.json" \
  --receipt "$EVIDENCE_DIR/llvm-tools-closure-repair-dry-run.json"
```

Proceed only if the new receipt says all of the following:

```text
status                    REPAIR_READY_DRY_RUN
base_member_count         62
supplement_member_count   2
missing_target_names      exactly both REPAIR_CONTRACT.json target names
```

A conflict, extra direct file, base mismatch, archive mismatch, receipt
collision, or any other result is `STOP_INVALID`. Do not delete, rename, or
overwrite a target to get around it.

## C. Apply exact create-only supplements once

Only after B passes, run the same command with `--apply` and a distinct absent
receipt path:

```bash
/usr/bin/python3 -I -S -B "$REI_PKG/materialize_missing_components.py" \
  --stdlib-dir "$STDLIB_DIR" \
  --rust-archive "$RUST_ARCHIVE" \
  --contract "$REI_PKG/REPAIR_CONTRACT.json" \
  --receipt "$EVIDENCE_DIR/llvm-tools-closure-repair-apply.json" \
  --apply
```

The only successful statuses are
`APPLIED_EXACT_SUPPLEMENTS_DIAGNOSTIC_ONLY` and, on an already exact retry,
`ALREADY_MATERIALIZED_EXACT_SUPPLEMENTS_DIAGNOSTIC_ONLY`. The receipt must
contain:

```text
post_repair_member_count      64
post_repair_closure_sha256    1d6d31c8f1c99b69b120c91fcff14220bbfcf0e8f976096f0c4992b7e2edc799
```

The program opens archive inputs no-follow, checks the archive SHA-256 again
on the descriptor used for copying, and uses create-only hard-link publication.
If it stops mid-copy, preserve the unique `.rei-stdlib-repair-*` forensic file
and stop rather than deleting it or retrying.

## D. Fresh immutable Section 0 only

The successful repair receipt is not a pass. Start a **fresh process** and
replay the same complete immutable Section 0 precondition command and the same
environment contract used by the parent intake job, without changing its
driver or expected digest. Record the complete result in a separate receipt.

Only a fresh complete Section 0 PASS may unblock the already-planned next
runtime-boundary gate. Do not run BASS/REC admission, four-site work, node
38382 replay, REIAFF1, formal systems, audits, or the canonical pilot in this
repair job unless a separately applicable immutable plan reaches them after
that gate.

## Durable closeout

Commit and push a stacked **draft** checkpoint containing only receipts and
policy/progress changes that are safe to version. Do not add the 192 MB archive
to Git. Report exact branch/commit/tree/PR and receipt SHA-256 values. On every
failure, retain:

```text
adapter                STOP_INVALID
canonical_pilot        NOT_RUN
first_interval         NO_PASS_FIRST_CANONICAL_INTERVAL
scientific_pass        NOT_CLAIMED
scientific_publication NOT_RUN
```
