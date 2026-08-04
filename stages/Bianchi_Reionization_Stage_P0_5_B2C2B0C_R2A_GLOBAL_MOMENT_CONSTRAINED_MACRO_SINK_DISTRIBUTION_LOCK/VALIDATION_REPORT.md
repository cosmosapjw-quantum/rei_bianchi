# R2A validation report

## Core verdict

`DURABLE_PASS_R2A_CORE_MACRO_DISTRIBUTION_LOCK_TAU10_FEASIBILITY_WITNESS_R2B_AUTHORIZED`

- Core cases: 30/30
- Feasible identity KL projections: 30
- KKT gates passed: 30
- Maximum generalized KL distortion: 0.000e+00
- Maximum projection TV distortion: 0.000e+00
- Maximum mass moment residual: 0.000e+00
- Maximum opacity moment residual: 0.000e+00
- Maximum current-Gamma residual: 0.000e+00
- Minimum macro mass-cap slack / cosmic H: 4.133e-05
- Maximum macro volume filling: 9.065e-02
- Minimum cycling slack / global sink J: 5.438e-07

The three B2C2B0A priors are already strictly inside the locked feasible set.
Because generalized KL is non-negative and vanishes only at the prior, each
prior is the unique constrained solution. No clipping, opacity-driven cloud
mass inversion, or quasi-static macro abundance solve was used.

## Finite-relaxation auditor

The separate implied-equilibrium auditor produced 90 lane/substep/tau
rows. Absolute-state feasibility passed 48 rows;
shape-only feasibility passed 60 rows. The 10 Myr
lane is an all-case feasibility witness and is required together with the core
moment/KKT gate for R2B authorization. It is not a calibrated physical timescale.
The 100 and 300 Myr failures remain explicit non-clipped sensitivity constraints
that R2B must carry forward.

## Scope firewall

No node chemistry history, unresolved subtraction, front/Q_M, source/fesc,
primordial recombination surrogate, or Bianchi feedback was started. The R1
failed node diagnostics remain preserved as fail-closed evidence only.
