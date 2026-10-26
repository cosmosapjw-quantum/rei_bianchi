# H1 primary source implementation

Prepared source: `primary_electron.py`; frozen suite: `test_primary_electron.py`;
bounded execution wrapper: `run_bounded_tests.py`. Scientific execution completed once under the controller's byte-bound authorization and GO; child exit code 0.

The emitter exposes only H1 atoms from the original opacity integrand, using
the frozen 8/12/16 quadrature and original time-root helper. It reads the saved
background through the original interpolant loader and evaluates the native
HI cross section with the inherited Mb-to-m² conversion. Portable input copies
and their original paths are listed in `runtime_inputs/PROVENANCE.json`.
Six prior ledgers retain the source campaign debit of 8.201436 CPU seconds and
8.23558345200945 wall seconds. No endpoint campaign budget is transferred.

The suite writes `PRIMARY_SOURCE_ATOMS.npz` before moment and tangent tests.
Arrays hold observer photon energy, primary kinetic energy, birth energy,
two source atom bases and two per-reference source weights. Physical weights
are exactly reference density times the saved reference weights. JSON stores
only compact moments, CDFs, threshold eligibility, derivatives and readiness.
Eligibility fractions have no stopping or heating interpretation.

The current test plan implements the frozen checks: saved source moments,
single-owner energy partition, finite support and positivity, complex-step
derivatives in actual H1 abundance, each amplitude and reference density,
the physical two-density-factor derivative, zero boundaries, invalid bindings,
duplicate ownership, omitted-density/birth-energy/threshold negative controls,
and absent heat for an unqualified stopping provider.

Run from the unit root only after authorization:

```sh
python3 implementation/run_bounded_tests.py
```

The controller supplies `RUN_AUTHORIZATION.json` with suite
`test_primary_electron.py`, manifest bindings and the six carried ledger paths.
Exactly one child attempt receives 1 CPU second, 5 wall seconds, an ITIMER_PROF
soft stop at 0.8 CPU seconds, 1 GiB and one BLAS thread. Scientific imports and
NPZ output are inside that child. Raw wait4 usage, stdout/stderr, snapshots and
partial results are retained even when the child fails. There is no automatic
retry. No IVP, historical full-suite replay, Git mutation or publication occurs.

Static syntax parsing with the standard library succeeded. The 13 frozen numerical checks passed. Independent scientific admission belongs to the controller.
Requested executor: gpt-6.1-sol/high; runtime model identity: UNEXPOSED.

Observed result: 307200 positive forward atoms; child CPU 0.563139 s and wall 0.5670031609988655 s. Source-campaign cumulative CPU 8.764574999999999 s and wall 8.802586613008316 s. Raw arrays, compact payload, all checks, stdout/stderr, exact input snapshot and wait4 receipt are under `attempt01/`. The next physical input is a qualified stopping/secondary-outcome provider; heat remains unspecified.
