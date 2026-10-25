# HI native massive-stress consumer — prepared implementation

Unit `HI_NATIVE_MASSIVE_STRESS_20261025`, isolated leaf
`research/rei_source_pair_binding/hi_massive_stress_20261025/`.

C3–C5 implements the root-frozen massive stress kernel, its mass derivative,
pressure source and signed mass/amplitude JVP. Source CSV and prior raw are exact
copies. Saved moments A/K/B/P and maximum kinetic energy are extracted from the
prior raw; previous consumer functions and tests are never imported or replayed.

`stress_source.py` creates exact per-term rational kernels and directly accumulates
signed integer dyadic enclosures at P128/P160. General rational denominator sums
are absent. Interval operations propagate endpoints. Binary64 output is certified
only when both endpoints round to the same finite value. Zero, final underflow,
subnormal and unresolved classifications remain explicit.

`focused_check.py` is one production/verification pass. It binds the 4368 HI/z2.479
rows, support maximum and prior fields; checks nesting, width, stable rounding,
Decimal100 alternative-kernel containment and relative error <=2e-15; then verifies
support, monotonicity and concavity certificates plus the frozen focused controls.
Synthetic a=2,X=3,da=-1,dX=2,dM=3 controls are distinct from physical density/history.

## Execution state

PREPARED_NOT_EXECUTED. No evaluator, project import, compilation, tests, CAS or
render has run in this preparation phase. No science outcome is claimed.

Root writes a separate `ROOT_GO.json` containing the exact unit,
`"science_execution": "GO"` and actual `PRE_EXECUTION_MANIFEST.json` SHA-256.
Then run once from this directory:

```bash
python3 -B run_focused_once.py /absolute/path/to/ROOT_GO.json
```

The launcher uses an exclusive durable attempt file, one primary Python child,
CPU hard cap6s, wall cap8s, memory512MiB and one-thread environment. It measures
actual wait4 user/system CPU, elapsed wall and max RSS and preserves stdout/stderr
and resource receipt for successful or failed termination. No network API exists
in the child implementation. No retry is implicit. Root interprets failures and
authorizes any targeted repair within the same cumulative new-unit cap.

## Scientific interpretation

Energies are eV, clock proper seconds, bath-rest zero-recoil target, no-deposition,
declared isotropic angular closure. W/3 is pressure injection per target per proper
second. Flux and STF are zero under that closure. Thermal heat remains null; no
rest-energy MA enters the existing energy ledger. Mass endpoints are standard-
uncertainty sensitivity probes, not confidence bounds. Actual n_HI/time history,
initial stock, geometry/time/frame matching and collision/stopping/photon supply
remain unresolved. L4_ready=false; whole-model completion=null.

Historical10s failure10.110448s and known-partial10.765369s remain preserved;
wholeL0=UNKNOWN_NOT_ZERO and original cumulative cap=NOT_FROZEN.
