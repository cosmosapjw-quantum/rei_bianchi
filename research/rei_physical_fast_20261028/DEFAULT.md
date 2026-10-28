# Current case default

The user selected **ON_refined** as the current default. The additive
`implementation/current_entrypoint.py` resolves that choice through
`current_defaults.json`; `--case OFF_base`, `--case ON_base`, or
`--case ON_refined` explicitly overrides it. Selection only reports the existing
saved case and its settings. It neither imports nor invokes a solver.

ON_refined retains the same illustrative photon/CR/injection amplitudes and
thermal/fast escape as ON_base. It changes rtol/scaled-atol from1e-7/1e-11 to
2e-8/2e-12. OFF_base disables these new external amplitudes and escape while
retaining the prescribed old atomic bath and intrinsic processes. These
tolerances describe a numerical setting, not physical calibration precision.

Completed old code, configs, initial conditions and raw runs are preserved.
Physical F4 calibration and a compatible bath are separate contract-bound
adapter work in this unit; selecting ON_refined does not silently activate a
new physical source model or the proposed cold8K profile.
