# Conditional local isotope sandbox

Self-contained CPU work unit continuing the reviewed C1/C2 checkpoint.
**156 baseline checks PASS + 2 separately executed source-onset checks PASS.**
Scoped independent decision: `PASS_SCOPED_CONDITIONAL_LOCAL_SANDBOX`.

The unit retains 21 absolute isotope-charge abundances, reuses exact electronic
blocks, and implements the electron-feedback Jacobian, dense and structured
linear solves, positive second-order atomic midpoint, supplied resolved-event
sources, explicit energy bookkeeping, bounded coefficient interpolation and
the local common-temperature formula. The complete required small inputs are
included. Temperature and spectrum are prescribed in the atomic component;
full coupled nuclear/thermal/radiation evolution is a subsequent unit.

## Run offline

From the project root or the extracted package root:

```bash
bash research/rei_coupled_isotope_sandbox_20261022/run_fresh.sh
```

From this unit directory, use `bash run_fresh.sh`. A new directory under `/tmp/`
is printed. An optional new `/tmp/...` path may be passed. The driver copies
this small artifact, preserves delivered evidence/figures under `recorded_*`,
then executes the unchanged baseline runner and the two-check targeted runner.
The new observations are in the printed directory's `evidence/` and `figures/`.
This does not create a Git checkout or overwrite the delivered observations.

`--prepare-only` makes the copy without scientific execution. Syntax, help and
prepare-only were checked; the wrapper was not used to repeat the baseline in
this work unit. Direct `bash run.sh` was the actual first invocation and
deliberately refuses to overwrite an existing `evidence/RESULTS.json`.

Observed runtime: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8.
The pinned package versions are in `requirements.txt`. No network, GPU,
compiled extension or complete historical nuclear array is needed. One BLAS
thread; diagnostic CPU 120 s, wall 180 s and address-space 1 GiB caps.

## Main observed results

| Result | Observation |
|---|---:|
| Baseline diagnostic | 156 PASS, 0 FAIL; one invocation |
| Targeted zero-n/T source checks | 2 PASS, 0 FAIL; separate invocation |
| Baseline body wall / CPU, after imports | 10.3994 s / 10.2784 s |
| Process peak RSS | 111128 KiB |
| Prepared versus rebuilt RHS | 3.78x median speed ratio |
| Vectorized versus scalar batch of 64 | 36.25x median speed ratio |
| Dense versus shared/rank-one solve | Dense 3.39x faster; dense is default |
| Midpoint observed orders | 2.00703, 2.00354, 2.00178 |
| Midpoint N=128 isotope-weighted error | 4.10260e-8 |
| Old C1/C2 reruns / cosmological IVPs | 0 / 0 |

Timing comparisons use identical input and work within each pair. They are
observed local timings, not a full coupled simulation acceleration estimate.

## Files and evidence

| File | Purpose |
|---|---|
| [REPORT_KO.md](REPORT_KO.md) | Korean results, equations, figures, interpretation |
| [THEORY_DERIVATION.md](THEORY_DERIVATION.md) | Exact sharing, rank-one derivative, d≥1 proof, midpoint/scaling bounds |
| [EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md) | Frozen physical domain, criteria and finite run authority |
| [IMPLEMENTATION.md](IMPLEMENTATION.md) | API, units, error behavior and actual commands |
| [SOURCES.md](SOURCES.md) | Primary sources and actually evaluated Wolfram commands |
| [code/atomic.py](code/atomic.py) | Prepared atomic source, solves and stepper |
| [code/local.py](code/local.py) | Resolved events, coefficient status/interpolation, EOS and outer transform |
| [evidence/RESULTS.json](evidence/RESULTS.json) | Complete original 156-check raw output |
| [evidence/TARGETED_SOURCE_ONSET.json](evidence/TARGETED_SOURCE_ONSET.json) | Two manufactured n/T source-onset checks |
| [REVIEW.md](REVIEW.md) | Independent scientific assessment |
| [RESUME.md](RESUME.md), [DAG.json](DAG.json) | Completion scope, dependencies and next executable work |

All baseline code and input identities are recorded in `evidence/EXECUTION.json`
and `vendor/INPUT_COPIES.json`. The targeted receipt records unchanged original
code hashes. Storage/publication status is separate from scientific validity
and is recorded after delivery.
