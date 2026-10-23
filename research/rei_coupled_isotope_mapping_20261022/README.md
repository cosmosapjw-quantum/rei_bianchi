# Coupled isotope C2 mapping

This additive research unit follows the reviewed C1 contract. It connects the
actual 21-state atomic implementation, six electronic RR rows, three DR rows,
18 nuclear families and saved events to the isotope-charge event interface.
Its one finite diagnostic passed 214 checks. It is not a production adapter
or a cosmological run.

Start with `REPORT_KO.md`, then `THEORY.md`, `CODE_MAP.md` and `BINDINGS.json`.
`REVIEW.md` gives the independent scoped decision. `RESUME.md` and `DAG.json`
record the next C3 action. `CONCURRENT_UPDATE.md` connects the separately
published bootstrap/thermal/provider result without replacing C2 inputs.

## Evidence

- `evidence/BINDING_CHECKS.json`: raw inputs, outputs, residuals and criteria.
- `evidence/EXECUTION.json`: exact command, runtime, resources and zero-IVP scope.
- `evidence/RR_PROVIDER_COMPARISON.json`: all 18 number/moment comparisons.
- `evidence/NUCLEAR_SAVED_SAMPLE.json`: case0, epochs0/128/256, with direction units
  and applicability distinct from negative-infinity storage.
- `SOURCE_IDENTITY.json`: exact selected source bytes and lineage.
- `fixtures/`: manufactured state and small read-only saved nuclear slices.
- `vendor/`: unchanged selected donor, RR candidate and nuclear contract inputs.

## Recorded execution and restoration

The actual command in the existing research workspace was

```bash
python research/rei_coupled_isotope_mapping_20261022/code/check_bindings.py
```

It requires NumPy and a Linux Python runtime (`resource` enforces the finite
CPU/address-space limits). The original run used Python3.12.14 and NumPy2.3.5.
The diagnostic writes its outputs in this unit's `evidence/` and `BINDINGS.json`;
the recorded outputs are already present and need not be rerun for review.

The compact C2 source checkpoint contains the selected atomic/RR source inputs
and a nuclear sample, **not the full original nuclear histories**. Repeating
all 214 checks also requires the read-only external original files listed in
`SOURCE_IDENTITY.json` at their recorded workspace paths: four nuclear files
from the PR219 scientific lineage and the two PR220 outer/compact mapping
references. Their pinned Git revisions and hashes are recorded. Restore those
inputs from the existing project checkout before running the full diagnostic;
the original recovery ZIP itself is not needed because its selected members
are included. This checkpoint is not advertised as a replacement for the full
old campaign archive or a source-only fresh83 launcher.

The frozen source identity and numerical run are kept separate from subsequent
delivery receipts. No old C1 file, existing provider source or previous run
has been overwritten by this C2 unit.
