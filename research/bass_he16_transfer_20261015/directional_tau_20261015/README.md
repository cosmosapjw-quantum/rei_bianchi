# Reproduce directional Thomson optical-depth experiment (2026-10-15)

This is a **downstream cold AXBI postprocessor**, not a modification of the
coupled source ODE solver. It computes direction-dependent optical depths for
a normal-comoving observer at the last **shared prefix** epoch (mean z≈10.269).

Prerequisites: Python 3.12, NumPy, the parent adapter directory, and the
original five AXBI 200001-row histories from the user's machine. The published
source files contain SHA-bound result summaries but not the private/raw
histories and not the 26 MB compressed earlier source caches.

Expected source (read-only):

- research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_MINUS/history.csv
- same with SHEAR_HALF_MINUS, SHEAR_HALF_PLUS, SHEAR_PLUS
- research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO/history.csv

The five source_identity.txt files must hash to
d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185.
The first 200001 rows are checkpointed prefixes, not z=4 complete histories.

From the rei_bianchi repository root:

1. Set an existing source root and scratch destination, for example
   ROOT="$PWD/research/axbi_goal_20261014/runs",
   SCRATCH="/tmp/HE18_DIRECTIONAL_REPRO_20261015".
2. Build/recheck parent numerical caches (this step needs the original
   history files and the already published signed prefix reports):

    python3 research/bass_he16_transfer_20261015/clock_decompose_signed.py \
      --source-root "$ROOT" \
      --source-report-dir research/bass_he16_transfer_20261015/signed_q_20261015 \
      --cache-dir "$SCRATCH/parent_cache" \
      --out "$SCRATCH/SIGNED_CLOCK_REPLAY.json" --rebuild

3. Derive exact source-ID-matched b(a) caches and calculate directional redshift
   roots, sky moments, and signed responses:

    OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 \
      research/bass_he16_transfer_20261015/directional_tau_20261015/directional_tau.py \
      --source-root "$ROOT" --base-cache "$SCRATCH/parent_cache" \
      --geometry-cache "$SCRATCH/geometry_cache" --build-geometry \
      --out "$SCRATCH/DIRECTIONAL_TAU.json"

4. Independently evaluate the linear geometric prediction, frozen ZERO-gas
   counterfactual, measured performance, and reproducible plots using
   perturbative_directional.py, frozen_source_geometry.py,
   benchmark_directional.py, plot_directional.py in this folder. Each script
   accepts --help for exact arguments.

5. Tests run from the parent source directory and this folder separately:

    OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
      python3 -m unittest discover -s research/bass_he16_transfer_20261015 -p 'test_*.py' -v

    OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
      python3 -m unittest discover \
        -s research/bass_he16_transfer_20261015/directional_tau_20261015 \
        -p 'test_*.py' -v

The theoretical time unit is proper seconds; density is proper cm^-3 and
sigma_T c uses SI with factor 1e6. The observer's relative redshift is **not**
the redshift relative to our present epoch. No rigorous original ODE, opacity
or polarized transfer enclosure is asserted.

The exact original input provenance and generated cache data also remain in
the locally verified archives/Dropbox dual backup. Generated summary files in
this folder can be compared structurally/numerically using the pinned source
IDs, rather than assuming byte-stability of compressed cache ZIPs.
