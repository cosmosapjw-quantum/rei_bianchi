# Unit 7: physical bridges

This directory contains the reviewed local Unit7 calculations: Li I absorption of saved cascade sources (A1/A2), donor-specific early-epoch Be7 conversion (B), and conservative present neutrino spectra plus emission bookkeeping (C). The final decision is **PASS_SCOPED_LOCAL_IMPLEMENTATION_ALL_THREE_LANES_AND_A2** in [review/IMPLEMENTATION_REVIEW.json](review/IMPLEMENTATION_REVIEW.json).

Historical `PENDING_INDEPENDENT_AUTHORITY_REVIEW` and `REVIEW_PENDING` labels in raw results, execution records and implementation notes record their original execution stage. The final joint review supersedes those pending labels; the historical files remain unchanged. This admission covers the stated local models only. No product runner, physical Hamiltonian action or external NCP execution was changed or performed; external actual refinement remains HOLD.

## Navigation

| Material | Location |
|---|---|
| Scientific report and limitations | [REPORT_KO.md](REPORT_KO.md) |
| Final independent decision and lane reviews | [review/IMPLEMENTATION_REVIEW.json](review/IMPLEMENTATION_REVIEW.json), `review/` |
| Frozen equations, inputs and tolerances | `spec/` |
| Original source intake and evidence | `intake/`, `evidence/*SOURCES.md` |
| Exact portable input copies | `inputs/laneA/`, `inputs/laneA2/`, `inputs/laneB/`, `inputs/verner/` |
| Original-to-portable path mapping | [progress/PATH_MAPPING.json](progress/PATH_MAPPING.json), input manifests and B result metadata |
| A1 two-photon continuum response | `code/li_photo_driver.py`, `results/laneA/`, [docs/LI_PHOTO_IMPLEMENTATION.md](docs/LI_PHOTO_IMPLEMENTATION.md) |
| A2 completed E1 plus continuum response | `code/li_e1_response.py`, `results/laneA2/`, [docs/LI_E1_RESPONSE_IMPLEMENTATION.md](docs/LI_E1_RESPONSE_IMPLEMENTATION.md) |
| B Be4 ↔ Be3 → Li3 history | [evidence/be_kinetics_history.csv](evidence/be_kinetics_history.csv), [evidence/BE_KINETICS_RESULT.json](evidence/BE_KINETICS_RESULT.json), [evidence/BE_KINETICS_EXECUTION.md](evidence/BE_KINETICS_EXECUTION.md) |
| C conservative bins and differential profile | [evidence/decay_neutrino_spectrum.csv](evidence/decay_neutrino_spectrum.csv), [evidence/decay_neutrino_profile.csv](evidence/decay_neutrino_profile.csv), [evidence/DECAY_SPECTRUM_RESULT.json](evidence/DECAY_SPECTRUM_RESULT.json), [evidence/DECAY_SPECTRUM_EXECUTION.md](evidence/DECAY_SPECTRUM_EXECUTION.md) |
| Saved-history scientific figure | [evidence/BE_DECAY_SPECTRA.png](evidence/BE_DECAY_SPECTRA.png), [evidence/BE_DECAY_SPECTRA.pdf](evidence/BE_DECAY_SPECTRA.pdf) |

CSV tables, result JSON, implementation code and frozen inputs are included in public Git. The lane-B raw NPZ arrays under `code/laneB/raw/` are **full-backup-only**; they are not required to read the reviewed CSV/results or reproduce a new calculation. Raw text logs retain the original failures and their dispositions. No numerical result is admitted solely by byte equality: the frozen numerical checks and independent reviews establish the scoped admission.

## Runtime dependencies

The observed environment used Python **3.12.14**, NumPy **2.3.5**, SciPy **1.17.0** and Matplotlib **3.10.8**. A1 uses Python standard-library quadrature and SciPy for its independent integration; A2 uses standard-library finite sums and the saved A1 kernel/input data. B requires NumPy/SciPy; C requires NumPy; plotting additionally requires Matplotlib. Shell commands below use a POSIX environment with GNU `timeout`; B/C also use POSIX signal alarms. No network access, Unit6 checkout, compiler or external product runner is needed when the copied inputs are present. The public Fortran oracle was not run because a compiler was unavailable; the source port and independent formula checks remain explicitly qualified.

## Reproduction

Preserve this directory's saved evidence. Run reproduction commands only in a **fresh copied directory**, for example a fresh directory copy containing this complete published Unit7 tree; a full-backup copy may additionally include the NPZ arrays. Change to that copy's root first. The scripts write to fixed paths relative to their own source files and overwrite their corresponding outputs, logs and execution metadata. Do not edit the frozen contracts to replace their historical absolute paths: each implementation prefers the exact portable copies already included here.

Set the observed single-thread environment once in the fresh copy:

```sh
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
```

A1 regeneration runs the prescribed 64/128/256 ladder, independent integration and nine focused checks in the current repaired driver:

```sh
timeout 30s python code/li_photo_driver.py > results/laneA/li_photo_run.log 2>&1
```

The original execution had a module-state test-import failure followed by one authorized saved-output validation repair; its traceback and retry are historical evidence. `code/li_photo_validate_saved.py` is that saved-evidence repair helper, not a required step after a new successful A1 driver run.

A2 is separately reproducible **without rerunning A1**. It consumes the byte-pinned A1 response, source moments and contract copies in `inputs/laneA2/`, plus the saved `results/laneA/provider_reconstruction.json`. It sums the 6,608 saved E1 rows and performs its eight focused checks; no new continuum quadrature occurs. Leave those frozen A2 input copies intact even if separately regenerating A1:

```sh
timeout 5s python code/li_e1_response.py > results/laneA2/li_e1_run.log 2>&1
```

B runs the two focused tests, then the prescribed production/refinement histories and independent Radau start comparisons. Its internal cumulative numerical limit is 30 seconds; the saved execution needed no extension:

```sh
python -m unittest discover -s tests/laneB -v > code/laneB/raw/tests_stdout.txt 2> code/laneB/raw/tests_stderr.txt
python code/laneB/run_kinetics.py > code/laneB/raw/run_stdout.json 2> code/laneB/raw/run_stderr.txt
```

C consumes B's saved CSV and JSON, so run it after B when regenerating both. Its three focused tests and spectrum export are:

```sh
python -m unittest discover -s tests/laneC -v > code/laneC/raw/tests_stdout.txt 2> code/laneC/raw/tests_stderr.txt
python code/laneC/run_spectrum.py > code/laneC/raw/run_stdout.json 2> code/laneC/raw/run_stderr.txt
```

The C exporter has a 15-second internal numerical limit. To redraw the two-panel figure from existing B/C evidence without integrating new kinetics:

```sh
python code/laneC/plot_saved_results.py
```

Fresh execution records describe that fresh execution; they do not automatically inherit the independent decision for the original saved evidence. Preserve failures and compare the contract's numerical checks rather than changing tolerances or normalizing outputs to force agreement.

## Claim boundaries

A1/A2 give conditional smooth direct-absorption, primary photoelectron energy and shell-threshold bookkeeping for the saved sources. They do not establish actual cosmological illumination, final charge fractions, Auger/fluorescence yields or deposited heat. B assumes the frozen fully ionized trace bath and specified recombination/photoionization/bound-capture model, excluding continuum capture, a second electron and late evolution. C uses the paper's rounded line energies and branches with freely streaming ultrarelativistic neutrinos, summed over propagated flavors. Its conservative raw-F bin closures do not imply machine-precision accuracy of the rate-derived differential profile, whose independent agreement is about 0.104%. No exact Q closure, present electron-flavor spectrum or neutrino mass determination is claimed. Numerical agreement measures solution error within these models, not atomic or rate-model uncertainty.
