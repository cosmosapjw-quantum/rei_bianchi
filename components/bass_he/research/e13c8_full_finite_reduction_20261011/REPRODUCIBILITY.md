# Saved-data reproducibility

These commands document the completed ChatGPT analysis. They are not new NCP
work orders. No repeated scientific integration is needed for this loop.

## Restore when local files are absent

Use the external handoff's exact transfer-manifest SHA and archive/part identities.
`code/restore_transfer.py` accepts either an actual complete ZIP path (any filename)
or a directory containing the downloaded parts. `--hydrate` also restores the
original source/input package and the actual heavy return. Every output directory
must be fresh. The helper writes `RESTORE_RECEIPT.json` or preserves
`FIRST_FAILURE.json`; it performs no network request and no scientific execution.

The concrete restore command and all remote file identities are in the external
handoff and recovery kit. Those contain the final outer archive SHA, which cannot
be included recursively inside the archive itself.

## Exact full reduction

After a hydrated restore, set `BASS_E13C8_RESTORE_DIR` to its actual absolute output
directory and choose a fresh analysis output. The source package and returned batch
are complete within the restored evidence.

```bash
python3 "$BASS_E13C8_RESTORE_DIR/runtime/E13C7_INPUT/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1/code/reduce_returned_batch.py" \
  --package "$BASS_E13C8_RESTORE_DIR/runtime/E13C7_INPUT/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1" \
  --batch-dir "$BASS_E13C8_RESTORE_DIR/runtime/E13C7_NCP_RETURN/BATCH" \
  --output-dir "$BASS_E13C8_RESTORE_DIR/FRESH_ANALYSIS_REDUCTION" \
  --mode ncp-return
```

Expected numerical status:
`PASS_MECHANICAL_PENDING_INDEPENDENT_REVIEW`. This is the original reducer's
immutable output marker. Final disposition is supplied separately by the already
completed `review/INDEPENDENT_DECISION.json` and `FULL_FINITE_ADMISSION.json`.

Expected reduction semantic:
`d647ba154b84baf22a3f85f9b7dca19f029b97f466838c036a9d3321f4c315d1`.

Expected actual CSV SHA-256:
`ab9879b989c7fcb08db666eddc086e808e2af92fe78c447519b2866ebe9b8d53`.

The program imports only saved-data arithmetic/relation code. It does not import
the integration vendor or run any path. Its actual execution record is
`analysis/REDUCTION_EXECUTION_RECEIPT.json`.

## Other derived analyses

The following programs have different input/output interfaces. Use their
documented `--help` and the hydrated paths above only if reproduction is needed.

- `code/analyze_finite_observables.py`: reduction plus original OFF_SEGMENTS.
- `code/analyze_telemetry_portable.py`: actual return plus source package, with a
  fresh `--output-dir`. The original `analysis/PERFORMANCE/analyze_telemetry.py`
  is retained as historical execution evidence; its identity-writing step assumed
  the script lived in the output directory. The portable copy fixes that path
  assumption without changing telemetry arithmetic.
- `analysis/RESIDUAL/analyze_saved_residual.py`: original package, actual BATCH,
  reduction, and the two complete prior-result inputs bundled in
  `analysis/RESIDUAL/inputs/`.
- `analysis/RESIDUAL/second_variation_parameters.py`: its `--residual-dir` is both
  an input and output tree. Stage required residual inputs, including
  `ACTUAL/PATH_RESIDUALS.json`, in a fresh tree and omit existing generated
  second-variation parameter files. This is saved-parameter arithmetic, not
  second-variation scientific integration.
- `code/plot_summary.py`: takes `--package` and writes `figures/` within it. For
  reproduction, stage the three required saved analysis JSON files in a fresh
  package tree without the existing figure outputs. It requires matplotlib and
  numpy for rendering only. Numerical analysis programs use the Python standard library.

All scripts preserve exact fractions as authoritative values. Human-readable
decimal strings and plotted doubles are display representations, not replacement
interval endpoints. Timing fields and local absolute paths can differ across
analysis hosts; scientific semantic identities omit irrelevant execution ordering.

Independent reviewer scripts and receipts are preserved for inspection. Their
original local paths and harness lineage document the actual review rather than
claiming those paths exist on every future host. The original raw inputs and the
reviewed arithmetic are present in the complete archive.
