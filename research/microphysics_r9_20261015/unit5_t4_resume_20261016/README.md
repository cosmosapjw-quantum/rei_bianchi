# Unit5 checkpoint continuation

This implementation restores a repair001 checkpoint, recomputes every cached milestone without Hamiltonian actions, and continues the same two-pass fully reorthogonalized recurrence at zero-based index `m`. It imports the pinned repair001 baseline instead of duplicating the reconstruction, integral repair, spectral gates or refinement rule. Local results await the independent Astra decision.

`code/t4_resume.py` implements the legacy runner mapping, input/vector/seam validation, historical correction recovery or explicit null prefix, deterministic three-action cache checks, continuation, and the full resolvent residual using `J=(C+C†)/2`. The diagnostic reports the coordinate defect and scalar/density bounds; it adds no convergence criterion. Native execution reuses the unchanged nine reconstruction gates (three actions), then samples the cache (three actions), then adds one action per new column. It writes to a fresh output directory and never alters the source checkpoint.

The actual 394 MB Unit4 checkpoint was not acquired: **actual checkpoint compatibility NOT_RUN; native PySCF reconstruction NOT_RUN; actual 128 continuation NOT_RUN; actual refinement HOLD**. No physical Hamiltonian, NCP job, remote allocation, or network operation was performed. Synthetic files with the legacy metadata format establish adapter behavior only. The expired allocation remains expired, and its terminal historical actions remain UNKNOWN in `[86,160]`.

## Observed local execution

`results/final_run/execution.json` records exact commands, exit codes, elapsed times, Python/NumPy versions and executor identity limits. The bounded eight-test suite passed in its captured raw stderr. It covers serialized continuation, observable/projector agreement, complex Hermitian data, malformed arrays, operator/input/runner rejection, historical corrections, cached-action corruption, action/deadline exhaustion, charged post-action expiry, happy breakdown, reconstruction gates, process termination and residual bounds.

- A real 96-dimensional toy checkpoint stopped at 64 and resumed toward cap 128. It reached the available 95-dimensional complement's happy breakdown at 95, using exactly 31 new Krylov actions. This is not a demonstrated 128-column chain.
- The complex fixture stopped at 32 and extended to 64 with exactly 32 new actions. Restoring/recompression used zero actions and the optional cache checks used three.
- A supervised native-worker control-flow fixture loaded a synthetic legacy checkpoint, ran nine toy reconstruction gates and three cache checks, extended 64→95, and wrote spectra/residuals/receipt. Its 37 actions are exactly `3+3+31`. The receipt campaign interval is simulated bookkeeping only; the actual physical campaign remains UNKNOWN in `[86,160]`. This fixture injects the saved-input loader, substitutes the acquisition checksum for its toy checkpoint only, and uses a dense toy reconstruction. Its budget and supervisor disable the 20 GiB host-headroom test because the local sandbox has about 9 GiB available; the native implementation retains the baseline check. It neither tests actual input acquisition nor executes PySCF.
- The independent exact Fraction calculation proves its residual identity, scalar error identity and a rational sufficient bound inequality. SymPy imports failed in both available Python runtimes; their stderr and exit codes are retained. The two genuine Wolfram MCP errors remain in `evidence/WOLFRAM_ATTEMPTS.json`; **no Wolfram PASS is claimed**.

`results/execution.json` and `results/native_fixture_worker/` preserve the first synthetic integration attempt, which correctly deferred before any action because the baseline host-headroom requirement exceeded the sandbox's available memory. `results/final_run/` contains the subsequent explicitly toy-only run. No production policy was changed to obtain that result.

## Local commands

From this directory, the already executed commands can be reproduced with new output paths:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 UNIT5_OBSERVATIONS=/tmp/unit5-observations.json python tests/test_resume.py
python tests/exact_fraction_check.py
python code/t4_resume.py prepare --out /tmp/unit5-new-prepared
```

`tests/run_evidence.py` is the bounded evidence assembly script used for this delivery. Its default `results/final_run` directory is intentionally exclusive; choose a new `OUT` path for another execution. Each child command has a 30-second timeout. The dense fixtures have dimension at most 96 and no fixture exceeds 256 toy actions.

## Prepared future native command — not authorized or executed

The generated `results/final_run/prepared/allocation_template.json` contains `authorized:false`, null allocation identity/timestamps, a 70-new-action maximum, 7200 seconds, 12 OMP threads, one BLAS thread, 24 GiB, and cap 128. A separate explicit future allocation must supply `authorized:true`, a nonempty `allocation_id`, `issued_utc`, and `absolute_deadline_utc`. The time interval must be at most 7200 seconds and still current. This file does not grant such authorization.

After that separate authorization, the complete native entry point is:

```bash
python code/t4_resume.py run \
  --receipt /absolute/path/to/frozen_receipt.json \
  --data /absolute/path/to/frozen_saved_arrays.npz \
  --v6-source /absolute/path/to/frozen_v6.py \
  --checkpoint /absolute/path/to/unit4_checkpoint.npz \
  --milestone /absolute/path/to/unit4_milestone_064.json \
  --allocation /absolute/path/to/new_explicit_allocation.json \
  --out /absolute/path/to/new_unit5_output
```

`--milestone` is optional. Without it, omitted historical corrections remain null; they are never filled with invented zeros. The worker uses the supplied absolute new deadline, a 70-action budget, a 24 GiB address-space limit, and subprocess group wall/RSS supervision. All six validation actions count within those 70. A deadline crossed after an action still charges that action. A killed child without a final count records new actions UNKNOWN in `[0,70]`, never zero. A restored scientific stopping decision returns before further actions. Exact immutable inputs, the actual checkpoint checksum, pinned source, and explicit legacy/operator mapping remain enforced. The campaign total is an interval `[86+n,160+n]` when `n` new actions are known; no exact old terminal count is invented.
