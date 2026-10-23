# Preparation, saved-data inspection and a separate clean reproduction

## What can be inspected without a new scientific run

From this unit directory:

```bash
./run_fresh.sh --prepare-only
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python code/species_saved_analysis.py
```

The first command checks the34 copied-input identities and starts no IVP. The second reads existing NPZ histories and rewrites only the species-analysis JSON/summary. `FINAL_RUN_RECEIPT.json`, `RESULTS_OBSERVED.md`, `results/analysis_summary.json` and `results/species_analysis.json` contain the retained observations. The published result arrays are preserved.

The `bounded_run.py --batch` entries document the original interrupted execution and its historical recovery commands. The existing execution ledger deliberately refuses a second attempt of a completed batch. Those entries are not a portable clean-run sequence.

## Dependencies

Python3.12, NumPy, SciPy and Matplotlib are required. Exact observed package versions are recorded in `FINAL_RUN_RECEIPT.json`; the solver environment is also in `results/environment.json`. The copied atomic loader uses only Python/NumPy source fits and its bundled author tables. No Rust, Fortran compilation, network access, package installation or donor solver import is needed. The shell recipe below requires Linux/Bash, GNU `timeout`, `cp`, `mktemp`, and `/usr/bin/time`.

## Clean-copy reproduction recipe — provided, not executed in this session

This sequence copies only the scientific unit to a fresh `/tmp` directory. It removes output directories only inside that newly created copy. It neither changes the published unit nor creates another repository checkout. Choose the actual source path if this unit has been moved.

The separate process caps below allocate CPU20+80+80+80+40=300 seconds and wall30+110+110+110+60=420 seconds. Each IVP batch is below the original per-invocation CPU120/wall180 ceiling. An outer wall420 cap also covers orchestration. Lower execution caps can stop a slow machine; they do not authorize tolerance, solver or physical changes. The three direct run_cases invocations cover the ten completed cases, including the separately authorized same-background mean-redshift case10.

```bash
set -eu
source_unit=/workspace/scratch/d5baa30c266d/rei_isotope/research/rei_angular_thermochemistry_20261023
repro_dir=$(mktemp -d /tmp/ANGTHERM01_reproduction.XXXXXX)
cp -a "$source_unit/." "$repro_dir/"
rm -rf -- "$repro_dir/results" "$repro_dir/figures"
mkdir "$repro_dir/results" "$repro_dir/figures"
cd "$repro_dir"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export MPLCONFIGDIR="$repro_dir/mpl_cache"
export PYTHONPATH="$repro_dir/code"
./run_fresh.sh --prepare-only

timeout 420s bash <<'REPRODUCTION'
set -eu
(ulimit -t 20; ulimit -v 1572864
 /usr/bin/time -v -o results/checks.time \
   timeout 30s python code/algebra_checks.py --output checks_pre_ivp.json \
   > results/checks_stdout.log 2> results/checks_stderr.log)
(ulimit -t 80; ulimit -v 1572864
 /usr/bin/time -v -o results/batch1.time \
   timeout 110s python code/run_cases.py --cases 1 2 3 \
   > results/batch1_stdout.log 2> results/batch1_stderr.log)
(ulimit -t 80; ulimit -v 1572864
 /usr/bin/time -v -o results/batch2.time \
   timeout 110s python code/run_cases.py --cases 4 5 6 7 \
   > results/batch2_stdout.log 2> results/batch2_stderr.log)
(ulimit -t 80; ulimit -v 1572864
 /usr/bin/time -v -o results/batch3.time \
   timeout 110s python code/run_cases.py --cases 8 9 10 \
   > results/batch3_stdout.log 2> results/batch3_stderr.log)
(ulimit -t 40; ulimit -v 1572864
 /usr/bin/time -v -o results/analysis.time \
   timeout 60s python -c 'import analyze_results, species_saved_analysis, plot_lithium; analyze_results.main(); species_saved_analysis.main(); plot_lithium.main()' \
   > results/analysis_stdout.log 2> results/analysis_stderr.log)
REPRODUCTION
```

The direct commands produce fresh per-case JSON/NPZ outputs and `/usr/bin/time` receipts rather than replaying the historical recovery ledger. Partial raw states are saved at every completed threshold segment. A failure stops the sequence and preserves finished cases; it does not license automatic reruns. These commands are documentation only: no new reproduction IVPs were executed while preparing this file.
