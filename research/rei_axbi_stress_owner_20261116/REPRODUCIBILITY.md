# Reproduce the physical consumer

## Authorities and inputs

The input contract is `INPUT_MANIFEST.json`. Each file is `CASE/history.csv` and
has 312,238 rows. The four cases are ZERO, SHEAR_HALF_PLUS, SHEAR_HALF_MINUS,
SHEAR_MINUS. A missing SHEAR_PLUS is not a permissible synthetic input.

The source-full archive retained by PR374 is
`REI374_AXBI_ORIGINAL_FOUR_CASE_SOURCE_FULL_20261115.zip`, 279,069,631 bytes,
SHA-256 `c8efb1dbde8c51c7356013ad346e97bb0223b64d8a387844d46779d380d7510d`.
Its `private_inputs/CASE/history.csv` members are the original source data.
The exact source-full remote receipt is already published at
[PR374's pinned source receipt](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/4554fc34765422f1c67e91c99ecac1bc9559fcce/research/rei_axbi_owner_loop_20261115/SOURCE_FULL_REMOTE_RECEIPT.json).
Use the authorized source archive together with this unit's final stage archive.
The source archive's older `loop/` code is not this new stress consumer.

## Environment and invocation

Executed versions: Python 3.12.14; NumPy 2.3.5; pandas 2.2.3; SciPy 1.17.0;
Matplotlib 3.10.8 for the figure. No original Rust solver build is needed.
Restore this folder as an isolated copy before reproducing, so historical result
files and runtime receipts are preserved. From the repository root, with the
authorized source archive extracted under `recovered_source/`:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 research/rei_axbi_stress_owner_20261116/radiation_stress_consumer.py --inputs recovered_source/private_inputs
python3 research/rei_axbi_stress_owner_20261116/adversarial_audit.py --inputs recovered_source/private_inputs
python3 research/rei_axbi_stress_owner_20261116/plot_results.py
```

The consumer validates complete input bytes before use. `--output` can redirect
consumer products; the supplied audit and figure scripts read this unit's
`results/` directory. The output CSV is deterministic on the recorded environment;
JSON runtime measurements and SVG metadata are execution-specific. This turn ran
one successful physical consumer and one successful targeted audit, not multiple
byte-identical replays. The captured commands and exits are in `execution/`.

## Data semantics

`results/stress_history.csv.gz` has 4,004 actual native-row samples (1,001 per
case), not interpolated source trajectories. Its `native_row`, `a`, `zbar`, and
`time_s` identify each source sample. `time_s` is elapsed proper time since each
model's mean redshift 20. It is not cosmic age. SI pressures are J/m³, elapsed
time corrections are seconds, and the plotted years are Julian years of
31,557,600 seconds. Ratios are dimensionless.

`results/STRESS_SUMMARY.json` records extrema over **all** native rows, source
checks, separated radiation owners, endpoint clocks and numerical cross-checks.
Do not reconstruct extrema from the 4,004-row sample table. `SCALAR_PARITY.json`
contains half-shear odd parts with original floors. `ADVERSARIAL_REVIEW.json`
and `REFEREE_SCOPE_NOTE.md` give the verification evidence and its limits.

The fixed-background shear forcing omits the response terms needed for a fully
coupled linearized evolution. The energy-only expansion term is an approximation
diagnostic under the original contract, not a closed stellar/baryonic energy
budget. No abundance trajectory is changed by these scripts.

## Recovery and provenance

Original four input SHA-256 values and completed-case identities are preserved.
Each new stage ZIP contains `RECOVERY_COMMIT.txt` and `RECOVERY_SHA256.json`.
Local tags name checkpoints `backup/rei-axbi-stress-20261116/R01` through `R10`.
Remote private retention is recorded separately from blocked public GitHub push.
Do not infer public reachability of a local commit or tag. The final delivery
receipt outside the stage archives maps all ten checkpoint and archive hashes.

No original worker, dirty user checkout, source/IC/closure/tolerance, prior
failure, or cumulative heavy-run budget was modified. Remaining physical work
is the actual +0.01 recovery followed by the already specified AX11/AX12 runs.
