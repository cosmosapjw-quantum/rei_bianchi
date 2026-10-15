# AX08 completed histories: matched proper time, matched scale factor and full H/He census

Selected 2026-10-15 theory/implementation/numerical-check loop, without any standalone Codex or physical solver launch.

Science source: finished ZERO and SHEAR_HALF_PLUS (q=+0.005) homogeneous non-tilted axisymmetric Bianchi-I original AX08 runs. This is deliberately ADDITIVE to rei_bianchi PR118, head ff752428ca5113b542573e9b99bdd50008a2b31e, and DOES NOT modify its active signed-minus run, q source, radiation/chemistry, runtime authority, or AX11 numerical certification.

## Real sources and immutable binding

Start at the already published reference and candidate source SHA256 entries in the upstream directory
research/axbi_goal_20261014/convergence/ax08_half_plus_20261015/paired_manifest.json.
The standalone script checks all history, abundances, source identity and terminal hashes, source-scenario IDs, and COMPLETE_REPRESENTED_INTERVAL in both frozen runs before reading science.

Each complete run has 312238 saved history rows and 1873428 atomic/ionic abundance rows, six species/rows per saved time: H_I, H_II, He_I, He_II, He_III, electron. The two complete datasets contain 3746856 actual abundance rows total.

Reproduce with the original immutable owner path, from this checked-out research directory:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 clock_census.py \
      --owner-root /home/cosmosapjw/Dropbox/bianchi/rei_bianchi \
      --output /tmp/A_UNIQUE_CLOCK_CENSUS_RESULT --workers 2

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 clock_census.py \
      --owner-root /home/cosmosapjw/Dropbox/bianchi/rei_bianchi \
      --output /tmp/A_DIFFERENT_UNIQUE_SERIAL_RESULT --workers 1

    rustc -O --edition=2021 abundance_audit_fast.rs -o /tmp/ax08_census_fast
    /tmp/ax08_census_fast ZERO /private/path/ZERO/history.csv /private/path/ZERO/abundances.csv
    /tmp/ax08_census_fast SHEAR_HALF_PLUS /private/path/SHEAR_HALF_PLUS/history.csv /private/path/SHEAR_HALF_PLUS/abundances.csv

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s . -p test_clock_census.py -v
    wolframscript -file ax08_clock_scalar.wl
    wolframscript -file ax08_charge_current_xact.wl

The actual SHA-hash-pinned source paths, benchmark evidence, and derived outputs are in the accompanying CLOCK_CENSUS_RESULT.json and BACKEND_COMPARISON.json; no private source data are copied into this public branch. See THEORY_AND_RESULT_KO.md.

## H/He physical normalization

For elemental fractions x_HI+x_HII=1, x_HeI+x_HeII+x_HeIII=1,
ne = nH*x_HII+nHe*(x_HeII+2*x_HeIII).
The original source registry Ybaryon equals nucleus number per baryon, NOT a mass fraction: the correct normalization is sum A_i Y_i =1, with A_H=1 and A_He=4. Do not sum the raw per-nucleus Y values as mass fractions. The current data give nHe/nH=0.08130135170951498 at initial and final snapshots; saved charge/current and all six-nuclide normalization identities agree to around 5e-16.

## Clock decomposition (critical science interpretation)

For monotone reference mean a_0(t), candidate a_q(t), and any scalar X, let t_0(a) denote the reference inverse clock. At each candidate event t_q(a) the following identity is exact (up to numerical interpolation in the saved files):

delta X at fixed proper time
= [X_q(t_q(a))-X_0(t_0(a))]
+ [X_0(t_0(a))-X_0(t_q(a))].

Term1 is the difference at matched mean scale a; term2 is the background proper-time drift. This does not require a perturbative q approximation. Sample all 4097 common log(a) points within overlapping proper-time support, NEVER extrapolate, and NEVER sort the gas temperature axis in the BBN-style plots.

This is a FINITE sampled-clock diagnostic, not a resolution/convergence estimate or an independently admitted shear detection. The full signed family still needs completion of the original minus branch and AX11 time, angular, energy and physics systematic error gates.

## Numerical work

- Python parallel: two independent source cases processed by two subprocesses with OPENBLAS_NUM_THREADS=1, reading only12 required history columns with NumPy and auditing every abundance row by streamed Python CSV. All 3,746,856 records were actually audited, not sampled.
- Lightweight std-only Rust streaming checker: reads whole history and all six original species per time with O(1) extra memory, validates source chronology, nuclei, electrons and baryons. Whole-data numerical maxima match Python within absolute 2e-15. The source hash bind remains in the Python parent.
- Actual comparative timings and source SHA are in BACKEND_COMPARISON.json. Distinguish file parsing/diagnostic speedups from the scientific AX08 production solver speed (unchanged).
- Actual Wolfram local 7 scalar checks and actual xAct/xTensor 11 tensor check groups/13 zero residuals. Neither proves coupled solver convergence.

## Outputs

CLOCK_CENSUS_RESULT.json, BACKEND_COMPARISON.json, HISTORY_IO_BENCHMARK.json and two figures:
ax08_matched_clock_decomposition.png and ax08_abundances_two_completed_cases.png.

The full physical BBN-like H/He abundance plot is based on actual finished q=0 and q=+0.005 histories; the full signed-family and resolved shear effect remain pending.
