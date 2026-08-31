# Independent PHYS-MATH-CODE audit

Date: 2026-08-31

Recovery classification: `RECOVERED_FROM_SUMMARY_NOT_BYTE_IDENTICAL`

Verdict: `PASS_WITH_RESIDUAL_HOST_BLOCKERS / STOP_INVALID`

## Scope and method

An independent review pass examined the Rust interval kernel, Python native
bridge and input closure, certificate and node boundaries, REIAFF1 codec, BASS
custody/publication substrate, tests, policies, and handoffs. The first pass
was intentionally adversarial. Every material finding below was reproduced by
a failing regression before the single coherent post-audit P0/P1 repair was
applied. A separate release pass then reread the repaired paths and reran their
focused suites.

## First-pass findings and dispositions

| Severity | Finding | Disposition |
|---|---|---|
| P0 | Runtime closure trusted caller-authored path/import observations and was not required by production entrypoints. | Replaced by a factory-minted invocation capability with automatic open/import/Popen/dlopen observation, cached-import tracking, taint-on-caught-violation, and thread/fork rejection. Production authentication, build, and native replay require the capability. |
| P0 | Compiler and native libraries could be executed or loaded before their bytes were authenticated. | Fixed tools now use absolute paths, a minimal environment, and exact pre-execution hashes. MPFR/GMP and the on-disk libc/libgcc/interpreter closure are checked before artifact loading. |
| P0 | Node replay accepted predecessor-returned node count, endpoint digest, and hard-gate flags as evidence. | Production replay is non-constructible until an independent verified-replay ABI exists; self-attested replay remains only in an explicitly test-only fixture. |
| P0 | Pinned `field_trial.py` could execute unpinned parent-module state. | Production validates the leaf source identity but refuses execution until the complete parent dependency closure and isolated loader are supplied. |
| P1 | REIAFF1 accepted multiple base64 spellings of identical certificate bytes. | Decoder now requires canonical base64 re-encoding; the alias mutation is rejected. |
| P1 | BASS Git custody admitted alternates/promisor/worktree-origin changes across exact reads. | Common/worktree configuration, object namespace, alternates, promisor markers, and effective remote authority are descriptor/inode-bound and revalidated around reads. |
| P1 | BASS publication could report a stale lexical destination or split an event across renamed parent namespaces. | Parent directories are pinned for the operation/event, identity drift is rejected, and receipts bind the validated final inode/namespace. |
| P1 | A publication callback could make the final inode writable after validation. | Mode is rechecked after the callback and on the final inode; only exact `0444` is admitted. |

The earlier mutable node-artifact, rollback-path race, and self-attested BASS
receipt findings were also retained in the same repair history: node bytes are
sealed into distinct `memfd` snapshots, rollback quarantines through retained
directory descriptors, and claim-bearing BASS graph admission requires
process-local admitted Git authorities plus an independent complete-payload
digest.

## Release-review evidence

| Component | Fresh focused result |
|---|---|
| Certificate graph/operator seam plus node boundary | 28/28 pass |
| REIAFF1 format and mutation matrix | 14/14 pass |
| Runtime automatic observer | 14/14 pass |
| Lock-independent bridge identity/boundary regressions | 6/6 pass |
| BASS custody, graph, publication, transaction and rollback | 33/33 pass |
| Rust generic interval kernel | 11/11 pass |
| Independent exact-rational corner oracle | 96 families / 6,144 systems pass |

No new P0/P1 correctness issue was found in the release pass. The runtime
observer is invocation-scoped enforcement, not a claim of a hostile
same-process security boundary.

## Residual blockers

- `P0 / RUST_THERMAL_REPLAY_ABI_MISSING`: no admitted Rust ABI recomputes and
  certifies the four physical sites.
- `P0 / NODE_38382_FIXTURE_MISSING`: endpoint, full-field, owner context, and
  reduction bytes are absent.
- `P0 / NODE_38382_FIELD_PARENT_AUTHORITY_MISSING`: the complete field-module
  dependency closure and isolated loader are absent.
- `P0 / NODE_38382_VERIFIED_REPLAY_ABI_MISSING`: no independent verifier
  derives the 46,080-node replay facts from sealed bytes.
- `P0 / BASS_REC_EXACT_AUTHORITY_MISSING`: exact BASS and REC Git authorities
  are not materialized.
- `P0 / RUST_BACKEND_CAPABILITY_PROCESS_BOUNDARY_MISSING`: Python type-state
  and audit hooks do not establish hostile same-process isolation.
- `P0 / BLOCKED_PRESTART_ELF_INTERPRETER_IDENTITY_NOT_ESTABLISHED`: the
  already-running Python process image cannot be authenticated before startup
  from inside itself; the exact on-disk closure is checked before native
  artifact loading only.
- `P1 / BLOCKED_OPERATOR_ABI`: the strict REIAFF1 codec has not been exercised
  in a real continuous-versus-split four-site restart.
- `P2 / FORMAL_TOOLCHAIN_NOT_RUN`: local Wolfram/xAct, SageMath, Singular,
  Lean/mathlib, and Rocq receipts remain host-bound.

The 46,080-by-three canonical pilot was not run. These blockers prohibit a
canonical interval, scientific pass, performance claim, scientific/canonical
publication run, ready-for-review transition, or merge. A fail-closed draft PR
is allowed. The final state remains
`STOP_INVALID / NO_PASS_FIRST_CANONICAL_INTERVAL`.
