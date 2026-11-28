# Reproduction — source, binary and inputs

## Layout and identity

The accompanying evidence ZIP contains this dossier, raw evidence, independent reference generator/result and the exact auxiliary acquisition metadata. The receiver repository remains the source authority; the ZIP is a scientific evidence packet, not a replacement Git repository.

Checkout `cosmosapjw-quantum/rei_bianchi` at exact commit `a5c958c414dea41216b445c05f58df837f05cacb`. The source and receipt hashes are recorded in SOURCE_REVISION_FINAL.json and EVIDENCE_INDEX.json. Preserve `research/physical_provider_20261010` at that commit, including `sources/acquisition.json`. The native build capture contains seven pinned input files; those seven alone are not a complete provider snapshot. The auxiliary metadata SHA-256 is `d9f3ce2a9174587124489d17542350cf01386eec8cdd5026be0399052f2e7b2b`.

The actual execution used Python3.12.14, NumPy2.3.5, SciPy1.17.0 on Linux x86_64. The CI build used rustc/cargo1.99.0. Use the preserved `evidence/build_v2/payload/binary/axisym_conditional` with its adjacent BUILD_RECEIPT.json if the host is compatible, or build a fresh binary and obtain its own receipt through the committed helper. Changing source, flags or compiler requires a corresponding new receipt.

## Actual commands

The following paths are examples relative to a complete receiver checkout. Set the two task-specific variables to the extracted evidence paths. Output directories must be new or intentionally selected; do not overwrite original evidence.

```bash
BRIDGE_BINARY=/absolute/path/to/evidence/build_v2/payload/binary/axisym_conditional
BRIDGE_RECEIPT=/absolute/path/to/evidence/build_v2/payload/BUILD_RECEIPT.json
python research/event_bridge_20261012/probe_events.py \
  --binary "$BRIDGE_BINARY" --build-receipt "$BRIDGE_RECEIPT" \
  --output /absolute/path/to/new_probe
python rust/rei_microphysics/python/source_bound_interval.py \
  --binary "$BRIDGE_BINARY" --build-receipt "$BRIDGE_RECEIPT" \
  --output /absolute/path/to/new_interval
```

The original execution and receipt files preserve the full commands, working directories, source/input maps, exit status and wall time. These example commands are reproducibility instructions and were not executed a second time for documentation.

## Expected scope

The probe performs two RHS and two EVENTS calls after one BIND. The first stage compares22primitive components with the independently prepared Decimal60 reference; the second uses a retained saved state as a callback diagnostic. The interval separately integrates from initial_state, then opens the retained solution for comparison. It makes257RHS calls and records17epochs for the selected warm Case A interval. Exact call counts can change under a materially different runtime, which then needs its own interpretation.

`PASS_SCOPED` concerns this discretization, model and event-consumption seam. The runner's `scientific_admission: HOLD` is retained. Neither the emitted recombination photon spectrum/count nor implicit primary/root/continuum certificates are supplied by this execution.

## Independent reference

`reference/decimal_event_oracle.py` is preserved at SHA-256 `d03e55829d823b9ce3567f5f09ca3c776c2fc6845945a7383e0599039ce752eb`; the original result is at SHA-256 `57c0ad93cc2cfe8edebf4728bb4405e2457ca5f77e90137896c0132222d7522f`. The original calculation ran through Python stdin. The preserved script retains those equations and input interpretation; it is not claimed to be the exact original execution entrypoint. It was authored independently of the candidate, computes direct source equations at 60 decimal digits and does not import the candidate. Its original input paths are historical provenance, not portable absolute paths. Rebind those paths to the exact hashed input files before intentionally rerunning it. It writes EVENT_REFERENCE_REPLAY.json to avoid overwriting the original result. The result is a reference calculation on decimal transcriptions of saved binary64 data, not a physical accuracy certificate.
