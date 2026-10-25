# Portable fixed collision consumer

The complete local operator and derivative driver are prepared. This is a finite instantaneous operator check, not a cosmic radiation history, continuum refinement, thermal solver, physical n/T production model, or generic chemistry compiler. The existing provider and fixed selected21/13-edge registry are copied exactly with provenance. No old opacity suite is rerun.

The actual unchanged z=2 source formula and actual saved density are paired with the exact prior synthetic positive target fixture. The photon fixture is a one-second source inventory. Initial B=epsilon.y, K=Xext=1e-20 eV/reference are disclosed positive derivative-fixture ledger values. Physical reference density is independent of the normalized state. Main Lambda=0; a separately prescribed affine Lambda check recomputes its value for every perturbation. The energy helper adds only explicitly supplied E_dot.N geometry work.

`coupled_collision.py` provides residual, 40x40 analytic Jacobian, two source-amplitude columns, independent-density partial and primitive event diagnostics. Analytic block construction remains a fixed consumer of inherited event identities. It does not replace WU's generic species/event compiler.

The one driver checks a scalar primitive-event and analytic derivative oracle, centered collision FD with injection off, per-active-entry complex step with injection on, source and density partials, affine normalization, isotope/baryon/charge/binding/energy identities, exact zero faces, positivity, coordinate representation equivalence, and strict finite physical domains. The CS gate resolves every tiny rare-isotope entry and tests structural zeros separately. FD uses frozen positive coordinate scales and row sums of absolute scaled derivatives. No max(1, derivative) floors are used. All numerical imports and checks occur within the measured child.

Root must freeze exact bindings and change RUN_AUTHORIZATION.json authorized=true only after the independent static review. Then execute exactly once from any cwd:

```
python /workspace/scratch/dfc32e6e80f9/pilot/coupled_collision_20261025/implementation/run_bounded_tests.py
```

All runtime input paths are relative to this unit. The runner carries all five exact historical ledgers without reset, uses one worker, BLAS=1, a 1 GiB address limit, integer RLIMIT_CPU=1 s, ITIMER_PROF=0.8 s and wall=5 s. It preserves wait4 rusage, raw outputs, pre-execution source snapshots and post-execution hashes. It permits only attempt1 and never retries automatically. A substantive failure returns to root/Astra for classification.

Requested execution identity is gpt-6.1-sol/high. The actual model identity is not exposed in this worker's runtime metadata and is recorded as UNEXPOSED. Metadata preparation used only stdlib parsing/copying; no scientific evaluation was run during authorship.
