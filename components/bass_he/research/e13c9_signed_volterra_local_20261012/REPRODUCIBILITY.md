# Reproducibility and recovery

## Current disposition

The scientific work in this package is complete and independently admitted only for the selected five paths. Routine receipt acknowledgement does not require any numerical replay. New NCP work is zero. Read REPORT_KO.md and CURRENT_STATE.json first.

## Restore the complete evidence if the working files were lost

The external recovery kit provides `restore_transfer.py` and a transfer manifest whose full SHA is given in the external handoff. Supply that exact external SHA and a fresh output directory. Choose either a complete archive or the directory containing every downloaded part. The helper selects parts by bytes/SHA, including downloads whose names gained `.bin`.

```bash
python3 restore_transfer.py \
  --manifest BASS_HE_E13C9_TRANSFER_MANIFEST.json \
  --manifest-sha256 EXTERNAL_HANDOFF_MANIFEST_SHA256 \
  --archive ACTUAL_COMPLETE_ARCHIVE_PATH \
  --output-dir E13C9_RESTORED_FRESH \
  --hydrate
```

For split transfers replace `--archive ACTUAL_COMPLETE_ARCHIVE_PATH` with `--parts-dir ACTUAL_DOWNLOADED_PARTS_DIRECTORY`. Do not silently retry a failure or reuse an existing output directory. The actual external handoff contains concrete file identifiers and hashes; the labels above are command arguments, not unverified values.

The package is restored under `E13C9_RESTORED_FRESH/package/BASS_HE_E13C9_SIGNED_VOLTERRA_LOCAL_20261012_v1`. Hydrated E13C8 evidence is under `E13C9_RESTORED_FRESH/runtime/E13C8`; beneath it, the original source is `runtime/E13C7_INPUT/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1` and the actual original NCP return is `runtime/E13C7_NCP_RETURN/BATCH`. Recovery imports no scientific modules and invokes no physics or MPI.

## Saved-data inspection

All original current-host paths in START/receipt/source-mapping evidence are historical provenance. Portable entrypoints accept explicit restored roots. For a necessary independent saved-data reconstruction into a fresh directory:

```bash
python3 E13C9_PACKAGE/code/analyze_local.py \
  --package E13C9_PACKAGE \
  --restored-e13c8 E13C8_RESTORED_ROOT \
  --output-dir NEW_SAVED_ANALYSIS_DIRECTORY
```

This analysis reads existing numerical outputs and weights; it performs no coefficient evaluation or integration. It must reproduce the exact selected metrics; wall/UTC metadata can differ. The initial path-resolution fix and exact numeric parity are recorded in `evidence/ANALYSIS_PORTABILITY_FIX`.

## Numerical replay is separate from recovery

The executed work list is in WORK_PLAN.json, with a preserved explicit node1162 M256 amendment. `run_path.py` accepts a selected node and M in that contract, matches cached baseline source/input/N/P/bytes, and writes a fresh output directory. Its existence is for a future, concrete reproducibility need; the current handoff does not ask NCP to replay any completed work.

```bash
python3 E13C9_PACKAGE/code/run_path.py \
  --package E13C9_PACKAGE \
  --restored-e13c8 E13C8_RESTORED_ROOT \
  --node 1162 --M 256 \
  --output-dir NEW_EXPLICIT_NUMERICAL_ATTEMPT
```

The existing source lock and per-path time/memory gates apply. No automatic retry, hidden intersection, changed physics or baseline first-quadrature replay is permitted. A meaningful future failure diagnosis must retain its first receipt and distinguish runtime/path issues from mathematical changes.

Manufactured controls retain their exact executed source and actual receipt. [REPRODUCIBILITY_CONTROLS.md](REPRODUCIBILITY_CONTROLS.md) gives a portable wrapper and its describe-only boundary check. The original 18 successful controls have not been rerun merely to move files.

## Evidence identity

The original association finding and source revisions are preserved. Four chosen M128 outputs bind the prior E13C9 source lock `e780cf0f48b83dc15b77d7b3899b55516a5309b5d3676b79492264d96458c87b`; the targeted M256 output binds `d33eb84fc2da780e27fd4b23cb3ae8a6a07908e1c8763c5e9a682795499e506c`. Their mathematical kernel is byte-identical (`5f20e1b5b0f4936f7bd443d19c7181fd2c7de9de762fe2fa3e9be98f8963cfc5`). The latter change adds only the explicit resolution unit in the execution boundary.

Complete PACKAGE_MANIFEST and the external delivery receipt bind the scientific records and delivery tooling separately. They do not replace the independent numerical decision or establish provider attestation.
