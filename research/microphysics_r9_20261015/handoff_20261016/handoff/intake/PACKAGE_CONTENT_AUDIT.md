# R9 C10 package-content audit

Scope: read-only inspection of the restored Unit2 tree and new C10 handoff sources, before final packaging. No remote command or physics calculation was performed. Current NCP state remains **unknown**.

- Original Unit2 archive: 43,479,461 bytes; SHA256 `725cf8bf53d366b179d41708c4efc9477b29c6c6e0a748ac2d3585dbe33709a1`. Identity matches the recorded actual restore verification. The original archive's Dropbox content hash was already verified in `UNIT2_RESTORE_RECEIPT.json`.
- Restored Unit2: 726 files, 47,550,815 bytes; 83 solver receipts, 77 accepted receipts and 6 failed/deferred attempts; 77 NPZ files.
- All seven C10 frozen source/contract/input/launch/lockfile/test/log identities match the specified SHA256 values.
- All 77 saved NPZ files match their receipt hashes; no accepted receipt lacks its NPZ. This is byte integrity, not a new residual or complete-basis check.
- V6/V7 source, V6 theory contract, historical 3e input and launch/deck, exact dependency lock, backend test, complete raw receipts/arrays, prior independent reviews, convergence tables and English MD/TeX/PDF report are present.
- C10 recovery source, fixture tests, actual local implementation-test receipt, contract, Codex handoff and NCP instructions are present.
- No credential filename or explicit private-key PEM marker was found in the scoped scan. The scan did not print secret contents and does not claim exhaustive secret detection.

## Packaging adjustment

`overlay/README_COMMANDS.md` currently documents fixture execution using `overlay/tests`, while the final bundle layout is described as `handoff/tests`. Update the bundled documentation or retain the named directory. The test code itself derives the sibling `unit2/ncp_results` path correctly for either directory name.

## Required distinctions

The threeelectron_v6 terminal receipt remains absent from the historical snapshot; the archive cannot establish the current NCP outcome. The new collector must inspect the existing actual NCP case first, without a blind replay. Rust logs and verification receipt are present, but the Rust source tree itself is not included in Unit2; C10 inspect/collect does not require it. Reproducing the historical full Rust build requires the pinned repository commit recorded in `NCP_RUST_VERIFICATION.json`.

This audit covers the restored tree and handoff sources. The final bundle manifest and archive hash are a later packaging output and must not be inferred from this audit.
