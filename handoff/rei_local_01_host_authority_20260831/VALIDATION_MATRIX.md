# Host-authority validation matrix

| Gate | Current evidence | State |
|---|---|---|
| Five missing `project_sources` bytes | exact size/SHA, independent container/topology audit | `PASS_EXTERNAL_BYTE_IDENTITY_ONLY` |
| All `INPUT_LOCK` path descriptors | 36 unique paths replayed without repo imports/JAX | `PASS_CURRENT_EXECUTOR_ONLY` |
| Sealed `cc` and GNU `ld` anchors | exact locked hashes on source executor and in package | `PASS_BYTE_IDENTITY` |
| Packaged native member graph | 2,191 regular files + 57 literal symlinks, external manifest pin | `PASS_PACKAGED_MEMBER_BYTE_IDENTITY_ONLY` |
| Authority pathname immutability | point-in-time verification only; concurrent-writer exclusion and kernel read-only binding are not established | `NOT_RUN` |
| Complete hostile runtime closure | mount policy, child, `bwrap`, `/proc`/`/dev`, and observed receipt not established | `NOT_RUN` |
| BASS/REC authority | dependency-order successor | `NOT_RUN` |
| Real four-site Rust operator | dependency-order successor | `NOT_RUN` |
| Node 38382 predecessor replay | dependency-order successor | `NOT_RUN` |
| Real REIAFF1 split restart | dependency-order successor | `NOT_RUN` |
| Wolfram/xAct, Sage, Singular, Lean/mathlib, Rocq | local successor after runtime/physics gates | `NOT_RUN` |
| 46,080-by-3 canonical pilot | explicitly excluded | `NOT_RUN` |

The archive and manifest close only the transfer identity of their packaged
members. They do not claim that the package is a complete runnable root, that
any binary executed, or that a scientific certificate was produced.
