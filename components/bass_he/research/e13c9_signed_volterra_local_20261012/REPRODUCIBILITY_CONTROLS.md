# Portable access to the preserved manufactured controls

The original 18 manufactured executions already passed 3,686 checks. Their script, `tests/MANUFACTURED/run_manufactured_controls.py`, and `EXEC01` receipt remain byte-for-byte unchanged. Its script SHA-256 is `15806e4758038a788312dfe075f10a364682e3655a0ca35ed0ca602166ea091f`.

`code/run_manufactured_portable.py` supplies portable filesystem bindings around that preserved script. It accepts the E13C9 package root, the hydrated E13C8 restoration root, and a fresh output directory. It verifies the oracle, candidate, contract, original source/execution lock, all original source-lock members, and the original work-plan bytes before proceeding. In execution mode it imports the original script, explicitly rebinds only `SOURCE`, `CANDIDATE`, and `CONTRACT`, and calls the original `main` with the requested output directory.

## Read-only path and pin check

After E13C8 has been hydrated, run the following with the actual restored paths. The output directory is a proposed fresh path; describe-only mode does not create it, import the control script, or execute any controls.

```bash
python3 -B /absolute/path/to/E13C9/code/run_manufactured_portable.py \
  --package /absolute/path/to/E13C9 \
  --restored-e13c8 /absolute/path/to/RESTORED_E13C8 \
  --output-dir /absolute/path/to/new_controls_output \
  --describe-only
```

The E13C8 argument must contain
`runtime/E13C7_INPUT/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1`.
The JSON output records every actual bound path and byte pin. The one delivery boundary check performed for this wrapper is retained in `evidence/MANUFACTURED_PORTABLE_DESCRIBE.json`. Its scope is path/pin validation only; the already completed 18 manufactured executions were not repeated.

## Explicit future control execution

If a future task specifically requires repeating these short controls, use the same arguments with a fresh output directory and omit `--describe-only`. The original runner then creates fresh `START.json`, `CONTROL_RESULTS.json`, and `RECEIPT.json`, or preserves the first failure and partial results. This operation invokes the unchanged manufactured oracle and does not invoke captured physical coefficients or the completed NCP batch.

The byte pins are fixed to the tested E13C9 candidate and contract. A changed candidate or contract is a new validation task; this wrapper rejects a pin mismatch instead of silently treating the old evidence as applicable.
