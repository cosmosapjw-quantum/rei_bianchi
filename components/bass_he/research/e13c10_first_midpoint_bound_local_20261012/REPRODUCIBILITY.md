# Reproducibility and preserved work

The authoritative scientific outcome is CURRENT_STATE.json plus the non-author INDEPENDENT_DECISION. Raw candidate/analysis files retain their historical pending statuses. Source/inputs/P60 and recorded failures are immutable.

The external final handoff binds actual COMPLETE/kit/transfer-manifest names, bytes and SHA256, with actual remote backup locations. The complete package embeds E13C9_COMPLETE.zip and E13C9_RECOVERY_KIT.zip; they hydrate E13C8 and then E13C7 source/input and completed heavy return. No additional user attachments are required.

From the small kit, restore an unavailable dataset once:

```bash
python3 -B restore_transfer_e13c10.py \
  --manifest BASS_HE_E13C10_TRANSFER_MANIFEST.json \
  --manifest-sha256 EXPECTED_FROM_FINAL_HANDOFF \
  --parts-dir ABSOLUTE_DOWNLOADED_PARTS_DIR \
  --output-dir ABSOLUTE_FRESH_RESTORE_DIR --hydrate
```

`--archive ABSOLUTE_COMPLETE_ZIP` is the alternative to `--parts-dir`; use one mode. The helper selects parts by actual bytes/SHA and tolerates the downloaded name suffix. Do not derive the expected SHA from the untrusted input itself. Do not rerun a successful restore merely to test the alternate transport mode. Preserve the first failed output and receipts; no automatic retry.

Restored paths below the fresh output:

| Item | Relative path |
|---|---|
| E13C10 package | package/BASS_HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL_20261012_v1 |
| E13C9 restore root | runtime/E13C9 |
| E13C9 package | runtime/E13C9/package/BASS_HE_E13C9_SIGNED_VOLTERRA_LOCAL_20261012_v1 |
| E13C8 restore root | runtime/E13C9/runtime/E13C8 |
| E13C7 original inputs | runtime/E13C9/runtime/E13C8/runtime/E13C7_INPUT |
| Completed heavy return | runtime/E13C9/runtime/E13C8/runtime/E13C7_NCP_RETURN |

The saved-source `run_path.py --package ROOT10 --restored-e13c9 RESTORED9 --node NODE --N N --output-dir FRESH` describes the captured executions in WORK_PLAN. They have already completed and must not be rerun as part of transfer verification. All argv, logs, first failures and raw RESULT are retained under evidence and runs.

`analyze_local.py --package ROOT10 --restored-e13c9 RESTORED9 --output-dir FRESH` and the reviewer script consume saved data. Their already completed receipts provide the evidence; do not repeat them to keep a host busy. A future changed analysis or method must have a concrete affected dependency and fresh bounded outputs.

The original selected input manifest has historical absolute locators. SELECTED_INPUTS_USAGE.md explains which restore-relative fields are authoritative. Both new analyzer and wrapper take explicit restored roots. Source-lock hashes define scientific code; PACKAGE_MANIFEST pins all final documents, source, plots, data and dependency archives.

Future NCP work is empty. Existing full/selected work stays closed. Refer to NEXT_DAG.json and NCP_ACTION.json for the next unexecuted local question and heavy gate. Verification of backup bytes and archive hydration is not provider attestation or new physics execution.

