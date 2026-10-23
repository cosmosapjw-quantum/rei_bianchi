# Conditional sandbox implementation

This program retains all 21 absolute isotope-charge abundances. Atomic
temperature, spectrum and baryon density are prescribed inputs. The new
integrator evolves atomic populations only; resolved nuclear/beta events and
the thermal formula are separate local operators, without a coupled trajectory.

## Offline execution and evidence preservation

Installed runtime: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8.
No dependency installation, external history, donor checkout, Git metadata or
network access is required. All required small immutable inputs are in this
unit's `vendor/` and `fixtures/`, copied from the reviewed C2 checkpoint.

The actual first invocation, from the restored repository root, was:

```bash
bash research/rei_coupled_isotope_sandbox_20261022/run.sh
```

It passed 156 named checks with exit 0. The saved execution and all raw values
are in `evidence/EXECUTION.json` and `evidence/RESULTS.json`. The runner refuses
to overwrite an existing RESULTS.json. To reproduce later, use a separate copy
of this unit's source, vendor, fixtures, run.sh and execution contract with a
fresh evidence directory; preserve the delivered receipts. No reproduction
run was performed while writing this document.

The shell script fixes BLAS/OpenMP threads to one. The Python runner enforces
120 CPU seconds, 180 seconds through a wall alarm, and 1 GiB address space.
The recorded timers cover the diagnostic body after imports: 10.3994 seconds
wall and 10.2784 seconds CPU. They do not measure end-to-end shell startup or
import time. The 111128 KiB RSS measurement is the process peak. Matplotlib could not create its default configuration directory and
used a writable temporary cache; its complete warning is retained in stderr.
This did not affect the numerical comparisons or rendered plots.

## Fresh replay entry point and targeted coverage

One command executes the source in a fresh temporary artifact copy:

```bash
bash research/rei_coupled_isotope_sandbox_20261022/run_fresh.sh
```

An optional new path under `/tmp/` can be supplied. `--prepare-only` makes the
copy without scientific execution. The driver preserves the copied observations
in `recorded_evidence/` and the copied plots in `recorded_figures/`, leaving the
original unit untouched. It then calls the unchanged `run.sh` and the separate
source-onset script. This is a small artifact replay copy, not a Git clone or
worktree. Shell syntax, help and a prepare-only copy were checked successfully;
no extra baseline diagnostic was run to check this wrapper. The exact receipt
is `evidence/FRESH_ENTRYPOINT_CHECK.json`.

After the baseline run, one authorized coverage repair added exactly two
checks in `code/check_source_onset.py`: D II+D II→He3 III+n and
D II+D II→H II+T II, each with the product trace initially exactly zero. Both
use a supplied manufactured log coefficient and a wholly manufactured explicit
energy ledger. Each gave positive target source 1.7359929831205052e-12 per
baryon per second, exact integer baryon and bare-charge residual zero, and flux
relative error 1.5122924563072915e-15 against the polynomial reference.

The result is **156 baseline PASS + 2 targeted PASS**, in separate invocations;
it is not one 158-check run. The two-check receipt records the unchanged hashes
of all three original scientific code files. No baseline run, Radau solve,
midpoint trajectory or historical campaign was repeated for this repair.
Its raw output and source identity are in `evidence/TARGETED_SOURCE_ONSET.json`.

## API and ownership

`code/atomic.py` supplies `PreparedAtomic(T_K, uv, cutoff_eV)` with `rhs`,
`smooth_rhs` (a reference-only polynomial extension), `jacobian`,
`fast_electron_column`, `batch_rhs`, `solve_dense`, `solve_structured`, `solve`
and `step_midpoint`. Reconstruct a prepared object when its temperature or
spectrum changes. Do not alter its stored parameters or matrices in place.

The donor's beta matrix is never included in the prepared atomic source.
`step_midpoint` is the two-stage shared-block exponential method, fixed
T/UV/n_B and zero fast-electron pool. It neither clips nor renormalizes states.
The three common 2/3/4-state electronic blocks are reused across the relevant
isotopes; no isotope abundance or charge fraction is discarded.

The structured solve checks Thomas pivots, the rank-one correction denominator,
finite outputs and the original-equation normalized backward residual. An
unsafe result triggers a recorded dense fallback; a singular dense solve
continues to raise. All 27 measured physical-domain linear cases used the
structured path without fallback. Dense solve remains the default: its
observed median was 298.308 microseconds versus 1010.487 microseconds for the
shared/rank-one Python implementation, including its residual guard. The
algebraic reduction is exact within the stated model; fewer arithmetic
operations did not give a faster Python solve at dimension 21.

`code/local.py` provides resolved events, status-tagged logarithmic coefficients,
explicitly bounded interpolation, the outer scale/time transform and the
common-temperature local EOS formula. Each event coefficient is already a
fully resolved channel coefficient. This unit **rejects** all parent/probability
metadata; it does not ignore or infer branch weights. Multiple parent branches
must be resolved externally before using this interface. Integer stoichiometry,
baryon conservation, units and every energy ledger are checked on construction.
A missing/absent provider or missing energy ledger remains unresolved.

Event derivatives reduce the reactant exponent and therefore remain defined
at exact zero. Log flux is formed before exponentiation. Support zero, absent
input, zero reactant, zero density and representational underflow have distinct
statuses. Finite underflowed logs remain available. Default coefficient-table
mode is KNOT_ONLY; positive off-grid use needs an explicit curvature bound and
relative-error tolerance, and a zero interval must be explicitly declared.

## Observed accuracy and performance

The 54 atomic grid cases had maximum normalized RHS error 1.85151e-16,
Jacobian algebra error zero and complex-step error 1.42690e-16. The 27 linear
cases had maximum backward error 2.44743e-16 and forward difference 1.40747e-15;
maximum infinity-norm condition number was 1068.35. The smallest recorded
rank-one denominator was 1.0000000277.

For N=16/32/64/128 steps the isotope-weighted final errors against the independent
Radau oracle were 2.648239e-6, 6.588415e-7, 1.643064e-7 and 4.102601e-8.
Observed orders were 2.00703, 2.00354 and 2.00178. The maximum relative isotope
inventory defect was 1.07286e-15. This validates the selected finite smooth
case, without asserting a uniform stiff-limit bound.

Six scalar source/loss reference solves, at scales 1e-104 and 1e-120 and three
tolerances, resolved positive stock born from exact zero. Maximum component
relative error was 9.72540e-10. These six local scalar solves, the one local
atomic Radau oracle and four midpoint trajectories are distinct from the
54 algebraic grid cases. No cosmological IVP, C1/C2 diagnostic or historical
campaign was run.

Seven timing batches measured the same RHS with rebuilt rates at 133.591
microseconds versus prepared rates at 35.3385 microseconds: 3.7803x at the
chosen input. For batches of 64 states, the scalar loop median was 3405.580
microseconds (53.2122 per state), while vectorized evaluation took 93.9431
microseconds (1.46786 per state), a 36.2515x batch speed ratio. These numbers
include the relevant API validation; setup costs and all ranges are recorded
separately. Compare timing only within matched pairs: rebuilt/prepared RHS,
dense/structured linear solve, and scalar/vectorized batch of 64. Values across
those different workloads are not interchangeable performance comparisons. Timing is an observed sandbox comparison, not a correctness gate.

The three PNG figures show the convergence, componentwise trace resolution
and seven-batch timing ranges. The two normalized trace curves and their error
curves intentionally overlap after scaling; this illustrates the same resolved
scalar problem at two very small absolute abundance scales. The figures were
opened and visually inspected.
