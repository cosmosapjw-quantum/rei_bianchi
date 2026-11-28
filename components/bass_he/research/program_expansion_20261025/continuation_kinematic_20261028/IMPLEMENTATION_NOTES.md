# KINEMATIC08 implementation notes

## Implementation boundary

This draft implements the root controller's frozen scientific contract. It imports the immutable APERTURE07 source by a deterministic sibling path and reuses its rational parser, contract exceptions, Bernstein polynomial integrals, interval normalization, set algebra, reflection and interval bounds. It does not call or modify inherited suites. The deterministic import is intended for the final repository layout under `continuation_kinematic_20261028`; the draft directory is not an execution layout.

The production module uses exact rational arithmetic, comparisons and signs of quadratic surds. It computes no floating square root. `PhysicalAngularMap.compare` rejects a stopped physical direction. Only the private boundary comparison uses its specified limiting extension. In a fold topology the fold is itself enclosed by rational bisection. That bracket is separate from the at most four boundary brackets, and its positive-width strip is added to the outer set only. Full support and singleton windows have exact special cases modulo a continuous measure.

The one-daughter API accepts asymmetric positive Bernstein density and a supplied signed rational mathematical weight `w0+w1*mu`. The pair API requires even coefficients and windows with no positive-width overlap. It computes coincidence from one shared `mu`, then integrates the resulting event set. Pair energy is the exact enclosure `G*Y`; the selected plus/minus label energies on coincidence are each `(G/2)*Y`. These are not arbitrary detector-specific daughter energies. No binding, heating, heat capacity, deposition or empirical-rate port is introduced.

## Prepared validation

Fourteen new test methods cover the frozen contract. The independent numeric oracle constructs CM energy and momentum using separate Decimal80 square roots of `s` and `H`, applies a Lorentz boost, and compares the resulting direction with the exact comparator at rational boundaries separated by `1e-50`. The native source test verifies the retained NIST file SHA256 and parses its existing fixed-column rest-energy fields; its density is explicitly manufactured. Exact declared rest-energy scalars do not certify their measurement uncertainty.

The five prepared negative controls distinguish loss of longitudinal sign, a normalization factor of two, omission of the fold strip, independent-marginal coincidence and incorrect physical energy scaling. Each saves its actual witness only after its assertions succeed. No control edits the production module or invokes a second suite.

`validate_once.py` runs the new suite once, accumulates all plot data in that process, records each test's CPU/wall duration, and serializes the raw failure/error traces as well as the payload. Native rows include comparator and bisection operation counters. No second payload-building scientific call exists. `plot_saved.py` reads only that saved JSON and imports no scientific module.

`run_bounded.py` requires the authorized source commit and a clean tracked tree, creates a new output directory, limits its child process to one thread and 512 MiB address space, and limits validation to CPU 10 s / wall 30 s or plotting to CPU 6 s / wall 15 s. Its receipt records observed child CPU, controller CPU, combined CPU, wall time, peak child RSS, start/finish, command, source hashes and exit code. It preserves failure records and never overwrites an output directory. Source freeze and execution authorization belong to the root controller.

`measure_execution.py` launches that complete runner as a subprocess and measures its full lifetime plus waited descendants, including its Python startup, scientific child, final receipt writes and interpreter shutdown. The external create-only resource receipt applies the same CPU 10 s / wall 30 s validation cap or CPU 6 s / wall 15 s plot cap to that complete boundary. It records outer orchestration CPU separately and explicitly excludes its own final metadata write from recursive measurement. An outer timeout allows at most a two-second cleanup margin while any observed wall time above the unchanged cap fails the resource gate. This wrapper changes no scientific allowance and creates no new attempt or reserve.

## Execution status at preparation

No scientific tests or plots have been run while preparing this draft. Root must copy the allowed draft paths into the live node, review/freeze the source and explicitly authorize the bounded command. Initial validation allowance is one run with one diagnosed targeted repair reserve. Prior APERTURE07, PHOTON05 and HE101 evidence and consumed budgets are unchanged.

## Prepared commands after root source freeze

From the final node directory, substitute the exact root-authorized source hash and a fresh output directory:

```bash
python -B scripts/measure_execution.py --mode validate --source-commit SOURCE_COMMIT --output evidence/validation_attempt1 --receipt evidence/WHOLE_PROCESS_RESOURCE.json
python -B scripts/measure_execution.py --mode plot --source-commit SOURCE_COMMIT --saved-json evidence/validation_attempt1/SAVED_PLOT_DATA.json --output evidence/plot_attempt1 --receipt evidence/WHOLE_PROCESS_PLOT_RESOURCE.json
```

The second command requires its own root authorization after review of the first run. The plot receipt states zero scientific function calls. Plot floats serve visualization only; all saved certificates retain rational strings.
