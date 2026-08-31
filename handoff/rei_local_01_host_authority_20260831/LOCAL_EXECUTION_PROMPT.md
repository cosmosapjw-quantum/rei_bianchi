# REI-LOCAL-01 exact-authority local continuation

This is the normative technical procedure used by
`LOCAL_CODEX_JOB_PROMPT.md`. Give the latter file to the local Codex job; do
not ask the user to reconstruct this procedure as a sequence of manual shell
commands.

Resume from the pushed head of
`agent/implementation/rei-git-authority-transport-20260831-r1`. Its immutable
stack parent is commit `d549c91fe078b2e9f567c09f2be50df95fb28d79`, tree
`53f69801e733f045b4925cb9d4d4b21d6c1f71c3`. The historical reconstruction
base is PR #22 head `59c3c9d135860cf3d359a0b70c370eb65b918898`, tree
`c6ee7d9959c5f5ffe1aa87f056b8c90cd1dd9653`. The user-reported local
checkpoint `c7792c854f...` was unavailable on this executor and GitHub; do not
claim this branch is its byte-identical reconstruction.

## A. Pin Git and run preliminary immutable checks

Resolve the pushed branch to an exact commit/tree, create an isolated
worktree, run `git fsck --full`, and reject shallow, promisor, partial-clone,
alternates, lazy-object, and worktree-config state. Verify the Git-resident
handoff manifests before interpreting this handoff: both
`handoff/rei_local_01_host_authority_20260831/MANIFEST.sha256` and
`handoff/rei_local_01_host_authority_20260831/git_authority_transport/MANIFEST.sha256`
must pass. Do not inspect or use the sealed supplement yet.

## B. Assemble four Git-resident small inputs with one external Rust archive

The four exact small inputs are already committed at:

```text
handoff/rei_local_01_host_authority_20260831/git_authority_transport/small_inputs/
```

Verify them against both `SMALL_INPUTS_MANIFEST.json` and `CONTRACT.json`; do
not ask the user to download them again. Obtain only the exact Rust archive
under one real non-symlink external source directory:

```text
08-rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz
size        192287020
SHA-256     294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40
```

If the locator or bytes are unavailable, record
`RUST_ARCHIVE_SOURCE_MISSING` (or the observed exact-byte failure), push a
durable draft checkpoint, and stop before `materialize_authority.py`, the
sealed supplement, or any repository runtime/import path. Do not substitute a
semantic equivalent.

Select a fresh staging root and run:

```bash
/usr/bin/python3 -I -S -B \
  handoff/rei_local_01_host_authority_20260831/git_authority_transport/materialize_small_plus_rust.py \
  --git-small-root handoff/rei_local_01_host_authority_20260831/git_authority_transport/small_inputs \
  --rust-source-root /absolute/rust-archive-source \
  --contract handoff/rei_local_01_host_authority_20260831/CONTRACT.json \
  --small-manifest handoff/rei_local_01_host_authority_20260831/git_authority_transport/SMALL_INPUTS_MANIFEST.json \
  --destination-root /absolute/authority/staged-project_sources \
  --receipt /absolute/evidence/git-small-plus-rust-receipt.json
```

The staging tool preflights every member, uses file descriptors and
create-only publication, writes mode `0444`, and never executes an archive or
sources the environment script. Its receipt records the distinct Git and
external origins; it is not yet the final external-intake receipt.

## C. Materialize and verify the five exact staged inputs

Pass the freshly created staged root to the canonical materializer:

```bash
/usr/bin/python3 -I -S -B \
  handoff/rei_local_01_host_authority_20260831/materialize_authority.py \
  --contract handoff/rei_local_01_host_authority_20260831/CONTRACT.json \
  --source-root /absolute/authority/staged-project_sources \
  --destination-root /absolute/authority/project_sources \
  --receipt /absolute/evidence/project_sources_materialization.json
```

The destination root must be distinct from the source root. The command
preflights every source and existing destination before copying, uses
create-only atomic publication, writes mode `0444`, and never executes an
archive or the environment script. A second identical run must be idempotent.
Any symlink, wrong byte, conflict, same-open-inode mutation, partial write, or
receipt drift is `STOP_INVALID`.

This is point-in-time byte evidence, not a kernel lock. Run in an exclusive
authority tree with no concurrent writer. Then verify all 36 `INPUT_LOCK.json`
path descriptors and preserve that receipt before admitting the supplement.

## D. Admit the sealed native authority supplement

Obtain `REI_SEALED_BUILD_DRIVER_AUTHORITY_20260831.v2.tar.xz` and record these
values outside the archive before extraction:

```text
archive bytes       51199448
archive SHA-256     74b59278ade83c8b5935d5d592ae3d4d45e30634aece9daa6d80ea0b28e9719b
manifest SHA-256    f8f6c84eaf10acd5ddf5a8f4b24d7c35736b9a6bd92a45de505e2966a05e0391
```

Use the safe extractor and opaque verifier documented in
`handoff/rei_sealed_native_build_authority_20260831/LOCAL_EXECUTION_PROMPT.md`.
Do not overwrite `/usr/bin`, `/usr/lib`, `/lib`, or the host root. A verifier
PASS means point-in-time packaged-member byte identity only. Exclude concurrent
writers; pathname immutability is not kernel-enforced until the later process
boundary. Rendered `bwrap` arguments are a non-executable fragment with
unresolved fields, not permission to launch.

## E. Complete immutable Section 0

Pin the repository head/tree, run `git fsck --full`, reject shallow/promisor/
partial-clone/alternates/lazy-object/worktree-config state, and verify the two
handoff manifests plus the non-code manifest. Resolve all 36 unique
`INPUT_LOCK.json` path descriptors using the external authority root from A.
Recheck the compiler driver, GNU linker, Rust, LLVM, stdlib, MPFR, and GMP
identities from the isolated authority. Do not import repository Python, JAX,
or `jaxlib` during immutable intake.

## F. Stop before runtime until the process policy is complete

The supplement deliberately does not pin a complete `bwrap`/child/mount/
`/proc`/`/dev` access policy. Compile and independently audit that policy
before attempting Section 5. Until then, do not run a production evaluator,
BASS/REC admission, four-site operator, node replay, restart, or formal gate.
After the fresh-process boundary is green, continue with Sections 1 through 7
of `handoff/rei_local_01_rust_rebuild_20260830/LOCAL_EXECUTION_PROMPT.md`.
Its opening branch/base requirement is superseded by the active continuation
branch and exact pushed head/tree; its physics, validation, and claim-boundary
requirements remain normative.

The 46,080-by-3 canonical pilot remains excluded. If any prerequisite remains
open, terminate exactly as:

```text
adapter             STOP_INVALID
canonical_pilot     NOT_RUN
first_interval      NO_PASS_FIRST_CANONICAL_INTERVAL
scientific_pass     NOT_CLAIMED
scientific_publication NOT_RUN
```
