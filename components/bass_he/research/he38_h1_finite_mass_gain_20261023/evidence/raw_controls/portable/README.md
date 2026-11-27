# Portable HE38 raw oracle entry

Status: **PREPARED_NOT_SCIENCE_EXECUTED**. This entry closes portability finding F2.
The executed original raw_oracle.py, run_oracle.py, launch.py, CONTRACT.json and attempt_001
evidence remain unchanged. Their actual successful run is the scientific evidence.
The new entry has static AST equivalence, compilation and help checks only.

## Restoration and optional future reproduction

Restore the whole raw_controls directory, including its original raw_oracle.py and
CONTRACT.json, under the restored research unit's evidence/raw_controls directory.
The implementation-root must be the restored unit's components/finite_mass directory,
which contains the h1_finite_mass package.

Reading the completed saved result needs no rerun. This command displays options only:

~~~bash
python /absolute/restored/unit/evidence/raw_controls/portable/launch.py --help
~~~

If a future task explicitly requires a fresh independent validation, use a new attempt
identity and a separate output root. The following command performs the four frozen
raw quadrature cases, so it must not be run merely to inspect or restore existing results:

~~~bash
HE38_UNIT=/tmp/he32_resume_20261022/repos/BASS_HE/research/he38_h1_finite_mass_gain_20261023
python "$HE38_UNIT/evidence/raw_controls/portable/launch.py" \
  --implementation-root "$HE38_UNIT/components/finite_mass" \
  --output-root /tmp/he38_oracle_reproduction \
  --attempt "he38_fresh_$(date -u +%Y%m%dT%H%M%SZ)"
~~~

Set HE38_UNIT to the actual restored unit location. The example points to the restored
component, not to the historical /tmp/he38_implementation workspace.

## Safety and evidence semantics

The launcher takes all three path/attempt arguments explicitly; there is no default
attempt_001. Attempt names must be single safe components of at most96 characters.
An existing attempt directory is refused. An exclusive launch-start record atomically
reserves the chosen identity, preventing concurrent launches of the same name.
The runner also creates the attempt directory with exist_ok=False and writes every
START/result/per-case receipt exclusively.

The launcher enforces CPU30s, address space512MiB, one BLAS/OpenMP thread and wall90s.
Partial evidence remains on interruption. A failed or completed attempt identity is
never silently recycled; use a different identity only for a separately justified run.

Original raw_oracle.py and CONTRACT.json hashes are checked before use. The numeric
quadrature, production comparison and refinement loops are unchanged at the AST level.
Production is imported from the supplied implementation-root only after raw case files
have been saved. A future actual invocation records its own source hashes, START,
per-case NPZ/receipts, RESULT or FAILURE, and launch start/result records in the supplied
output root. Prepared code is not represented as an already completed new execution.

See ../PORTABILITY_REVISION.json and ../PORTABILITY_STATIC_VALIDATION.json.

