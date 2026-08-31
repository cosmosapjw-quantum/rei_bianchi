# REI Rust host-authority continuation checkpoint

## Authority and recovery class

- current task layer: `validate`
- usable continuation base: commit
  `59c3c9d135860cf3d359a0b70c370eb65b918898`, tree
  `c6ee7d9959c5f5ffe1aa87f056b8c90cd1dd9653`
- reported local checkpoint: `c7792c854fb00ba6bbed31baa9c2e3da13ceee9e`,
  tree `bc039fff363ff4a131741845b494986177c44dc8`
- reported-checkpoint evidence class: `USER_REPORTED_NOT_MATERIALIZED`
- availability scope: `ABSENT_FROM_CURRENT_EXECUTOR_AND_REMOTE`
- usable as base: `false`
- recovery: `NOT_BYTE_RECOVERABLE_HERE`

This is a new continuation from the recoverable PR #22 head. It does not claim
byte identity with the user's unpushed local checkpoint.

## Material deltas

1. `OBSERVED_INDEPENDENT`: all five formerly missing inputs match the exact
   locked sizes and SHA-256 values; container topology checks passed without
   executing any member.
2. `OBSERVED_CURRENT_EXECUTOR`: all 36 unique `INPUT_LOCK` path descriptors
   passed using the explicit scratch authority locator. Repository Python and
   JAX were not imported; runtime and later gates were not run.
   A final isolated materialization replay copied all five bytes and an
   idempotent second invocation returned the identical receipt.
3. `IMPLEMENTED_TDD`: the fail-closed external authority materializer rejects
   symlinks, nonregulars, traversal, unsorted/duplicate/prefix-colliding
   entries, partial writes, same-open-inode mutation, source/destination
   overlap, and receipt conflicts. Verification is point-in-time and requires
   an exclusive no-concurrent-writer intake tree; kernel-enforced path
   immutability remains part of the unrun process boundary. Focused tests pass.
4. `OBSERVED_INDEPENDENT`: exact GCC-driver (`6117c525...`) and GNU ld
   (`5b674ea1...`) bytes exist on this executor, but two ELFs alone are not a
   build closure.
5. `PACKAGED_NON_SCIENTIFIC`: sealed native authority archive version 2 contains
   2,191 regular files and 57 literal symlinks with external archive and
   manifest digests. Opaque verification passes; no packaged program ran.
6. `IMPLEMENTED_TDD`: the package verifier and non-executing mount-plan
   renderer fail closed. The renderer retains seven unresolved external policy
   fields and cannot launch `bwrap`.
7. `AUDIT_REPAIRED`: the local Codex bootstrap now verifies Git and all five
   inputs before sealed intake, explicitly supersedes only the older
   branch/base precondition, defines durable runtime-policy/receipt artifacts,
   and labels pre-boundary path verification as point-in-time. A manifest
   completeness regression closes the stale/unlisted prompt defect.
8. `FINAL_CURRENT_EXECUTOR_REPLAY`: a fresh canonical-contract materialization
   copied all five supplied bytes to mode `0444` and produced an identical
   second receipt. A fresh safe extraction of the v2 archive verified 2,390
   tar members and 2,248 declared rootfs members (2,191 regular files and 57
   symlinks), without executing any packaged member.

## Current gates

| Gate | State |
|---|---|
| five external inputs | `PASS_EXTERNAL_BYTE_IDENTITY_ONLY` |
| 36 path descriptors | `PASS_CURRENT_EXECUTOR_ONLY` |
| native package member identity | `PASS_PACKAGED_MEMBER_BYTE_IDENTITY_ONLY` |
| production materialization on user host | `NOT_RUN` |
| hostile fresh-process runtime boundary | `NOT_RUN` |
| BASS/REC and all later gates | `NOT_RUN` |
| canonical pilot | `NOT_RUN` |

Focused final validation: materializer `21/21`, sealed extractor/verifier
`25/25`; both new manifests and all three inherited handoff/non-code manifests
pass. `git fsck --full`, `git diff --cached --check`, AST/JSON parsing, and the
repository registry verifier pass. These are intake/delivery checks only.

## Claim ceiling

```text
adapter             STOP_INVALID
canonical_pilot     NOT_RUN
first_interval      NO_PASS_FIRST_CANONICAL_INTERVAL
scientific_pass     NOT_CLAIMED
scientific_publication NOT_RUN
```

Next executable action: on the user host, verify the exact Git checkout,
materialize the five exact inputs, verify all 36 locked path descriptors, then
safely verify/extract the sealed native authority and complete the native
Section 0 closure. Next implement and independently audit the complete
kernel-mediated pre-start policy. No later gate is authorized before it passes.
