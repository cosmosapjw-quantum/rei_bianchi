# V14 continuation: native SSPRK2 stage-A checkpoint

## Frozen status

**A: PASS_SCOPED. B: RUN_COMPLETE_REVIEW_PENDING.** Stage A contains the additive native fixed-gas, fixed-geometry closed-moment SSPRK(2,2) implementation and its independent review. B has completed 16 unique coupled histories and six targeted tests, but B source/results are deliberately absent from this immutable checkpoint while independent review proceeds. Across A/B, 13 new targeted native tests passed. The 52 A summary rows are transport diagnostics, not cosmological histories; the extra A example replay only added separate stage diagnostic columns and does not increase unique-case counts.

Stage-A independent admission is in `theory/INDEPENDENT_TRANSPORT_REVIEW.md`. It applies to the inspected native transport implementation, conservation/cone/CFL behavior and observed local/global refinement. It does not promote unconditional positivity, uniform stiff accuracy, the coupled adapter, full EoR, Case B, or signed Bianchi.

## Source and reproduction

This checkpoint depends on the exact retained baseline archive in `BASELINE_DEPENDENCY.json` (5,748,523 bytes; SHA-256 `63eefca04fb7bb3c4884e40ecfd3b7058a3be3d43c7aee110b8e0f928014ef04`). The baseline archive itself and the entire crate are not duplicated here. Restore V14 with its retained `input/v14/RESTORE_V14.py`, sibling V13 restoration script and V12 native owner; copy the three normal source/test/example files under `native_files`, and append the small owner hook exactly once. `execution_transport/FROZEN_RUNTIME_SOURCE_MANIFEST.json` records every frozen Rust/package source hash, with the original V14 driver hash and no later B source changes. The complete original transport owner byte prefix was preserved. Code, tests and the diagnostic example remain normal Git text files.

The local compiler was rustc 1.94.1 / cargo 1.94.1, installed from the user-provided archive into a local prefix without network or global changes. Exact commands, outputs, errors, exits and timings are in `execution_transport`. Only the seven new transport tests were run for A; historical suites and matrices were reused as immutable evidence rather than rerun.

Per-cell CSVs are stored as lossless `.csv.gz` to keep the payload small; decompress with Python gzip or `gzip -dk` before using receipts referring to the uncompressed filename. Main CSVs, summaries and all native code remain ordinary files. The prior baseline archive is a named immutable dependency; the final combined self-contained archive will include the restored native owner excluding target/toolchain.

## External execution

The earlier original NCP execution remains preserved evidence. **No new NCP run occurred here.** The specified local key was absent. Desktop Commander inventory reported the device online, but its next tool call was rejected because monthly usage paused calls; its instruction was not to retry/reconnect. `EXTERNAL_EXECUTION_STATUS.json` preserves this exact status. No SSH probe or retry is part of this checkpoint.

## Raw evidence

The final A summary has 52 rows and the per-cell file has 11,136 data rows. Maximum stage optical depth was 0.3539464411. The independent review recomputes number, physical energy, event-binding and scalar-polynomial consistency from raw data. Root review retains responsibility for claim scope. No Git or cloud mutation was performed by the mechanical checkpoint assembler.
