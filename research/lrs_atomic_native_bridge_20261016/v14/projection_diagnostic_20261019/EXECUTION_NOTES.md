# Native V14 projection diagnostic: execution notes

## Scope and status

This additive example exercises the existing public native transport API at fixed gas and fixed geometry. It does not run the old 84-history / 7056-row campaign, the old 36 tests, or cosmological source-on histories. No native rate, closure, tolerance, or existing source file was changed. Full source-on cosmological second-order accuracy is **not established** by this diagnostic.

**NCP this turn: NOT EXECUTED.** The controller’s Desktop Commander probe failed with a monthly-usage `SERVICE_ERROR` and explicitly instructed no retry. The prior 2026-10-18 NCP smoke and full runs did complete. Controller review remains separate.

## Frozen identities

- V13 parent used by V14 restoration: `7fb18cec3d6d6eebad5fe418ec83b36d82cfff1e`.
- Frozen V14 code anchor: `f6046418d15e2f44418dfbc04ca67999f389a7df`.
- Source restoration: supplied `RESTORE_V14.py`, using its sibling V13 and V12 payloads; restore exit **0**. Its `V14_RESTORE_RECEIPT.json` verifies the four V14 payload hashes. The analyzer checks the receipt and those files again.
- New example SHA-256: `868a4f8e28acebce0f1d78ff62f0adaf6a5d411c6896ea0b528afb8a16a0085f`.
- Rust compiler: `rustc 1.94.1 (e408947bf 2026-03-25)`, host `x86_64-unknown-linux-gnu`, LLVM `21.1.8`.
- Cargo: `1.94.1 (29ea6fb6a 2026-03-24)`.
- Native summary CSV SHA-256: `ca4b20024bd2f8adfac5995ffeebfecd0c56f47d7cbe89d38f874a909402dc3e`.
- Per-cell CSV SHA-256: `3e9af61a432d40e743901c5000611a00788b3766b90840df4806a56466737b6b`.

## Actual executed commands

The actual run used scratch root `/workspace/scratch/6af5e9e6c737`. The following commands show its paths exactly:

```bash
source /workspace/scratch/6af5e9e6c737/v14_work/rust_toolchain/env.sh
export CARGO_TARGET_DIR=/workspace/scratch/6af5e9e6c737/v14_work/target
cd /workspace/scratch/6af5e9e6c737/v14_work/native_baseline/rust/rei_microphysics
cargo build --offline --locked --release --example v14_projection_diagnostic --jobs 2
/workspace/scratch/6af5e9e6c737/v14_work/target/release/examples/v14_projection_diagnostic \
  /workspace/scratch/6af5e9e6c737/v14_work/projection_diagnostic.csv
```

Build exit **0**, Cargo elapsed **10.09 s**. Native diagnostic exit **0**, measured subprocess elapsed **0.094112117 s**. The native diagnostic was launched once with a 60-second timeout. The execution receipt records source hash, compiler, timestamp, exit, elapsed time, and output hashes in `v14_work/projection_execution.json`.

The analyzer was executed once against the existing CSV, without recompiling or rerunning the native diagnostic:

```bash
cd /workspace/scratch/6af5e9e6c737
python3 v14_work/delivery/analyze_projection_diagnostic.py \
  --csv v14_work/projection_diagnostic.csv \
  --identity v14_work/native_baseline/V14_RESTORE_RECEIPT.json \
  --source v14_work/delivery/native_files/examples/v14_projection_diagnostic.rs \
  --out v14_work/delivery/evidence/PROJECTION_ANALYSIS.json \
  --figures v14_work/delivery/figures
```

Analyzer exit **0**. It verified the exact 62-row matrix and finite numeric fields. PNG inspection confirmed both panels, readable labels, labelled slope guides, and the caption distinguishing the fixed-gas operator from cosmological histories. Matplotlib used a temporary `/tmp` cache because its default configuration directory was read-only; the generated PNG/PDF succeeded.

## CSV conventions and interpretation

For `pair` rows, the base is one full interval `dt_s`; the result is two maps of `dt_s/2` with midpoint reconstruction. `m=2` identifies those two result maps. For `history` rows, the base is one map over total theta 1, the result is `m` maps, and `dt_s` is one result-map duration. Initial source injection is fixed at `dt_emit=1e10 s`, independent of absorption step size. The delta control has 60 eV photons and matches total injected broad-spectrum photon number on ray zero.

`photo_HI`, `photo_HeI`, and `photo_HeII` are accumulated native absorption-event counts per H. N/U conservation subtracts those native events or binding plus heat from initial-minus-final inventory. Cell U differences are in reference energy; global U is obtained through the native inventory API.

Pair slopes are local composition-defect slopes. The analyzer retains signed successive history differences for all seven observables, records sign changes, and returns null slopes whenever either difference is within 64 ulps of the relevant observable endpoints. The coarse HI history has a sign change, explicitly retained. Every delta-control pair and history slope is null under this roundoff rule. A local pair slope approaching two does not establish global second-order evolution.

The summary conservation maxima normalized by initial inventory are about `1.39e-15` (broad N), `1.15e-15` (broad U), `1.73e-15` (delta N), and `1.84e-15` (delta U). Complete values, local slopes, signed history differences, sign flags, and roundoff flags are in `evidence/PROJECTION_ANALYSIS.json`.

## Reproduction wrapper

`RUN_PROJECTION_DIAGNOSTIC.sh` is intended for placement under repository directory `v14/projection_diagnostic_20261019/`, alongside this analyzer and `native_files/`.

```bash
# Reconstruct exact V14 using sibling ../RESTORE_V14.py, then run only this example:
./RUN_PROJECTION_DIAGNOSTIC.sh

# Or verify and reuse an existing restored V14 native root:
./RUN_PROJECTION_DIAGNOSTIC.sh /absolute/path/to/restored_v14 /absolute/path/to/fresh_output

# Reconstruct while choosing a fresh output directory:
./RUN_PROJECTION_DIAGNOSTIC.sh - /absolute/path/to/fresh_output
```

The wrapper requires Rust/Cargo on PATH. It refuses an existing requested output directory, verifies the frozen native identity and diagnostic source SHA, copies only this new example, builds offline/locked with two jobs and a 180-second limit, runs the diagnostic with a 60-second limit, then invokes the analyzer. It adds PNG/PDF figures when matplotlib is installed. It logs compiler/Cargo versions, stage commands, elapsed times, exits and output hashes in the new run's `EXECUTION.json`. The wrapper records hostname and platform in its execution receipt. Required end-to-end placement and restoration verification is recorded below; it replays the same 62-row matrix and adds no unique scientific cases or cosmological histories.


## Required end-to-end reproduction/plumbing replay

The wrapper was executed **once** from a fresh plain input layout copied from verified READY input, retaining `v12/native_owner`, `v13`, and `v14` siblings. The package was placed at `v14/projection_diagnostic_20261019`, and the default restoration branch was invoked with `-`. This replays the **same 62-row scientific matrix** to verify placement, restoration, build, and packaging; it adds no unique scientific cases or cosmological histories.

```bash
source /workspace/scratch/6af5e9e6c737/v14_work/rust_toolchain/env.sh
bash /workspace/scratch/6af5e9e6c737/v14_work/runner_replay_input/v14/projection_diagnostic_20261019/RUN_PROJECTION_DIAGNOSTIC.sh \
  - /workspace/scratch/6af5e9e6c737/v14_work/runner_replay_output
```

Actual wrapper exit **0**; restore exit **0**; expected Rust/Cargo **1.94.1**; build exit **0** in **9.256738101 s** under its 180-second limit; diagnostic exit **0** in **0.101428768 s** under its 60-second limit; analyzer exit **0** in **3.026065895 s**. Recorded hostname `4450a6b8b7d6`, platform `Linux-6.18.55-x86_64-with-glibc2.39`. Original native runtime remains **0.094112117 s**; replay runtime is separate.

Both raw CSVs matched original bytes exactly: 62 summary rows and 13312 per-cell rows, with the original SHA-256 values listed above. No timing columns or data-only exceptions were needed. The diagnostic Rust source SHA remained unchanged in all original, delivery, and replay copies. Full raw outputs and stage logs are under `v14_work/runner_replay_output`; `evidence/WRAPPER_VERIFICATION.json` preserves the stage receipt and actual comparison.

After removing the analyzer's hardcoded NCP status, it was rerun **once** against the original evidence, exit **0**. Analysis now records `execution_platform=NOT_INFERRED_FROM_CSV`; actual runtime hostname/platform belongs to execution receipts. The original-evidence metadata-correction invocation is the analyzer command above, with `MPLCONFIGDIR=/tmp/v14_projection_mpl` to use a writable plotting cache.

## Existing NCP summary correction and provenance

Only `global_maxima.max_species_event_residual_H` was corrected in the existing stage summary and archived execution summary, from **0** to **4.84017834763862e-14**. Existing per-interval values `1.1295470225255793e-14` and `4.84017834763862e-14` match the preserved full `ANALYSIS_INDEPENDENT.json`. The original zero is retained in correction metadata; no native simulation was rerun for this correction. `evidence/SUMMARY_CORRECTION_COMPARISON.json` records source hashes and verifies every other original JSON field was preserved.

Original `run_commit`, `source_head`, and related fields remain intact and receive separate provenance clarification. Source-intake/reference context is `2676c31df1bf18ec0c7d60108846f1e9c8ca853c`. Commit `ef94f08df149b57959b868646b397a2bff2b268b` is an evidence-publication commit at **2026-10-18 12:45:53 UTC**, after the full run finished at **12:41:16 UTC**, and is **not an attested runtime checkout SHA**. Source byte identity is the frozen V14 code anchor `f6046418d15e2f44418dfbc04ca67999f389a7df` plus the four recorded native hashes.
