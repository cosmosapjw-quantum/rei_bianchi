# Implementation and observed execution facts

The self-contained Python implementation is `code/local_flows.py`; the finite
diagnostic is `code/run_diagnostic.py`. It reads the three copied JSON providers
and uses installed NumPy, SciPy and Matplotlib offline. The scientific formulae
and acceptance limits come from `EXECUTION_CONTRACT.md` and `THEORY.md`.

The full thermal path integrates two states `[x,w]`; the reduced path integrates
one state `[w]` and reconstructs x from the stable closed primitive. Both use
DOP853 at the same tolerances/output grid and reconstruct escaped energy by
the invariant. The independent Radau path integrates its own escaped-energy
state. Fixed primitive coefficients are prepared at module import; initial
alpha(Ti) is cached for the shared full/reduced model. The beta production path
uses exact positive decay/RR stages in the prescribed Strang order. Its
independent finite-domain reference uses normalized I/K Bessel coefficients
without a coefficient ratio; exact zero-density limits use elementary forms.

## First scientific diagnostic

The original helper was invoked once, from the restored project workspace,
under CPU120s, wall180s, AS1GiB and BLAS1. Exact shell commands and observed
exit codes are in `results/implementation_metadata.json`. The first invocation
exited 0: 103 of 103 checks passed, with 82 arrays and three PNGs. There were
no failed scientific runs to repair. Body wall time was 40.260782102 s and
body CPU time 38.323068887 s; these clocks begin **after Python/library imports**.
Peak RSS was 113576 KiB and is process-wide. The requested executor label was
gpt-6.1-sol; observed tool-environment versions are recorded separately and do
not establish an observed inference-runtime model identity.

`results/raw_arrays.npz`, `results/results.json`, `results/checks.json` and
`results/execution.json` retain the first run. All first-run source bytes are
preserved in `results/first_run_source.zip`, with a source SHA256 list. The
figure inspection is recorded in `results/figure_inspection.json`.

## Authorized delivery repair

The controller identified that the original input comparison read the sibling
unit and that its helper wrote into the delivered evidence directory. The
successful first-run byte comparisons populate `inputs/copy_manifest.json`.
The final driver verifies its local input copies against those source hashes;
it no longer reads a sibling unit. The helper creates a fresh `/tmp` directory
with this unit's source/input files and keeps delivered evidence intact.

Run `bash run_fresh.sh --prepare-only` to validate fresh-copy hashes/imports
without integrations. The observed prepare-only invocation exited 0, preserved
in `results/prepare_only.json` and its stdout/stderr logs. Run
`bash run_fresh.sh` for a new independent diagnostic directory. The helper
prints that directory. This replay entry point was prepared and its input
loading verified; scientific experiments were not rerun for this packaging
repair. `results/packaging_patch.diff` records the changes to executed files.
The scientific `local_flows.py` is byte-identical to the first-run snapshot.

## Authorized timing-only follow-up

`TARGETED_FOLLOWUP.md` authorizes one paired timing clarification in response
to wide ranges in the first run. `code/run_paired_timing.py` reuses the saved
grids/endpoints/references; it does no new Radau solve, quadrature or convergence
sweep. Both methods are warmed and each pair runs seven batches, alternating
method order, with three solves per method/batch. Wall and process CPU clocks
cover integration/output/reconstruction and exclude result assessment.

The one invocation exited 0 under CPU30s, wall45s, AS1GiB, BLAS1. Body wall
time was 4.362194691 s; body CPU time was 4.358364734 s. Process peak RSS was
97632 KiB. The 96 repeated output checks passed the unchanged reference
criteria; 12 representative output arrays and all individual batch clocks are
preserved in `results/paired_timing_outputs.npz` and `results/paired_timing.json`.
The actual paired timing PNG was inspected. Ranges still overlap substantially;
the observations do not establish a universal robust speed winner. The
controller owns default selection and scientific admission. No further timing
extension was performed. The two reported body CPU intervals sum to
42.681433621 s; imports/startup are excluded from those reported intervals.

## Handoff

All observed commands, source identities, clock scopes and narrow packaging
changes are in `results/implementation_metadata.json`. Independent scientific
review and the controller's admission/report are separate from these mechanical
execution facts. No cosmological campaign, historical diagnostic, new provider,
beta thermal partition, network access or publication action occurred here.
