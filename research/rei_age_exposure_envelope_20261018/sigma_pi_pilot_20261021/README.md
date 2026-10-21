# Source-free LRS Bianchi I Sigma/Pi pilot

This package uses the exact three PR147 Python kernels from source commit
`3b85dedce84d37b3e165da00685a8a984950aafe`. `SOURCE_MANIFEST.json` records
their unchanged SHA256 identities and the exact source lock and MIT license.
The new family is the axisymmetric LRS subset of non-tilted Bianchi I with
collisionless gamma/nu, massive canonical Vlasov cells, cold dust and Lambda.
No native thermochemical age/time or original PR147 histories are rerun.

Delivered state: all 91 nominal cases and three corner refinements completed.
The independent C9 decision is `PASS_SCOPED_PRELIMINARY`; its one operational
repair batch is `CLOSED_PASS`. There is no pending scientific result review
for this finite-grid pilot. Existing native age/time `HOLD` and production
`NOT_ISSUED` remain unchanged. The actual scientific execution used Python
3.12.14, NumPy 2.3.5 and SciPy 1.17.0.

Dependencies: Python 3.10+, NumPy, SciPy, Matplotlib, Linux `/proc` and cgroup
read access for resource sampling. No package download is performed.

## Commands

Inspect and regenerate figures from the delivered saved data first, from
this directory (these commands launch no IVPs):

```bash
python3 pilot.py plan --output results
python3 pilot.py check --output results
python3 pilot.py plot --output results
```

### Historical execution / recovery reference

The commands below document the approved execution interface. They are not
a request to rerun this completed pilot. Use `run --resume` only for genuinely
unfinished, separately approved cases in the same frozen set. Failed and
incomplete attempts are preserved rather than automatically retried. The
delivered 94 completed cases require no NCP execution.

```bash
python3 pilot.py run --profile sandbox --max-workers 4 --resume --output results --review-approval CONTRACT_REVIEW.json
python3 pilot.py run --profile ncp --max-workers 63 --resume --output results --review-approval CONTRACT_REVIEW.json
```

`CONTRACT_REVIEW.json` must be the independent review with matching contract
identity and decision `PASS_SCOPED_EXECUTION`. Scientific result admission is
separate: `C9_REVIEW.json` records the completed run's independent
`PASS_SCOPED_PRELIMINARY` decision. Production remains `NOT_ISSUED`.

## Inputs, outputs and interpretation

`plan` fixes 91 nominal and three specified refined corner cases. At each
initial Sigma_F there are 13 stress values: zero and six magnitudes with both
absolute stress signs. Both signs remain distinct at zero shear. The source
`Sigma_ref` is Sigma_half, so the adapter sets it to Sigma_F/sqrt(2). Pi uses
`kappa_t = 8*pi*G/c^2` for SI energy stress; the initial radiation multiplier
is calibrated analytically and checked against actual initialized fields.

`results/MANIFEST.json` preserves exact configs and source identity. Each
case has `INPUT.json`, `ATTEMPT.json`, `RESULT.json`, and compressed `raw.npz`
containing raw solver state, epochs and physical observables. Failures retain
their error/traceback and any solver states already returned. A solver that
raises before returning cannot provide an intermediate state; its attempt,
input and error remain. Files are written atomically. Existing incomplete or
failed attempts are preserved and are never automatically retried.

`finite_grid.csv` contains every nominal point, including empty/pending/failed
rows. PNG and PDF plots show actual sampled endpoints, both initial stress
signs, and empty/failed cells. Axes use discrete positions labelled by the
actual grid values; no interpolation adds samples. All plotted observables
are dimensionless. Raw physical stress is saved in J/m^3, H and s in s^-1,
and elapsed proper time in seconds from a=1/21.

`signed_final_shear_vs_signed_initial_stress.png` and its PDF show five
selected initial-shear curves (65 saved computed endpoints), with actual
signed initial Pi on the horizontal axis and signed final sqrt(6)*s/H on the
vertical axis. Lines only guide the eye between computed points.

`check` records all case statuses and the three endpoint refinement tests.
Hamiltonian residual means algebraic construction consistency. Brightness
positivity is checked only at the specified 64 Gauss nodes. Corner agreement
is a preliminary stability gate, not a global trajectory error bound.

## Resource and recovery behavior

Spawned workers persist across independent cases and set BLAS/OMP/MKL/
NumExpr threads to one before NumPy import. Every worker has nice=10. The
controller uses actual affinity/cgroup CPU and memory, idle samples summed
only across affinity-permitted CPUs, and memory headroom. It begins with at
most one nice worker until a nonzero CPU-tick delta is observed. Busy CPUs can receive one nice worker when
memory allows. No unrelated process is killed, reniced or paused.

Sandbox caps are four workers, 30 seconds/case, 240 cumulative charged child
seconds and 180 cumulative controller seconds. NCP caps are 63 workers,
60 seconds/case, 1800 child seconds and 1200 controller seconds. Controller
receipts persist charge across invocations of the same profile. Completed
matching cases are reused. A case with an incomplete attempt reserves its
full per-case allowance on the next invocation. Launches reserve the full
per-case budget; this can stop conservatively before exhausting the cap.
Only own workers may be terminated at time limits, and only per-case write
locks are used. Memory waits are bounded by the controller cap.

`EXE_SOURCE_MANIFEST.json` and `verification/executed_source/` preserve the
actual pre-repair code used for all 94 IVPs. `OPERATIONAL_REPAIR.json` records
the later scheduling, resume identity and postprocessing changes; none rerun
an IVP. Future `run --resume` compares the three current wrapper hashes and
semantic Python/NumPy/SciPy versions against `RESUME_CODE_IDENTITY.json`.
Executable installation path and full Python build string are diagnostic
metadata, allowing an equivalent runtime at another location. Changed or
missing semantic dependency/code identities are reported explicitly.

Setup-only caches store the parsed cosmology, exact immutable Legendre
matrices keyed by all function arguments, and exact immutable canonical
momentum packets keyed by all construction arguments. The physical RHS,
summation order, DOP853 solver and tolerances are unchanged. The adapter
invokes the identical solve_ivp call outside the source integrate method so
returned partial states can be saved before validation. No benchmark or
speedup claim is made.
