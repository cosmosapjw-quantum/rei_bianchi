# Independent finite-mass gain derivation handoff

Status: **PASS_SCOPED** for the declared original-source-coordinate finite-mass H1 ionization model. Workflow1.0.0 / approval0.2. This directory is a transient integration handoff to the parent research unit; final repository publication, backups and stage receipts are owned by the parent.

## Deliverables

- `DERIVATION.md`: full event kinematics, conditional species momenta/tensors, normalized event law, exact sharing compression, heat partition, 3×2 incoming-stress map, heavy-mass limit and scientific boundary.
- `check_derivation.py`: independent exact-rational event and Cartesian Wick controls, plus new 65-digit transfer/partition integrals. It imports no existing unit implementation.
- `CHECKS.json`: immutable receipt from the completed execution, including the exact script hash, grid, residuals and runtime.
- `PROVENANCE.json`: reused input identities and hashes of the completed handoff payloads. This is a file identity record, not a claim that existing source suites were replayed.

## Main implementation consequences

1. Keep neutral kinetic mass `h=M+m`, total kinetic mass `L=M+2m`, and reduced mass `mu=m*h/L`. The threshold is defined in relative energy.
2. Reuse the HE37 alpha/beta/gamma kernel and multiply by `sqrt(m/mu)`. The finite-mass transfer mean closes exactly: `Lambda=beta-theta*alpha`, `U1=theta*alpha`, `U2=beta-(I+theta)*alpha`.
3. Use DERIVATION Eq.(18) for species heat, Eq.(19) for the small heavy combined heat, Eq.(24) for species STF and Eq.(25) for total STF. Return direct total heat `-I*rate` and direct total STF; avoid subtracting large isotropic tensors to recover tiny STF.
4. For pure incoming electron stress, the total STF finite-mass/heavy-limit coefficient ratio is `sqrt(zeta)`, while the rate ratio is `1/sqrt(zeta)`.
5. The exact momentum and energy identities are kinematic results. Applying the LC cross section, conditional transfer law and independent isotropic Jacobi directions at finite mass is the declared model. No empirically calibrated differential H1 claim follows.

## Executed new controls

| Control | Grid | Result |
|---|---|---|
| Exact event momentum, energy and outgoing pressure gains | `M/m={1,17,1836}`, 36 independent signed-axis direction pairs each | All rational residuals exactly zero |
| Full incoming-STF linear response | Five STF bases × two incoming species × three masses; 90 species tensors | All rational residuals exactly zero |
| Scalar species partition | Three masses with independent gains+loss expressions | Exact conservation and formula equality |
| New conditional transferred-energy mean | `E/I={1.00000001,2,100}` | Gate `<1e-55` passed |
| New Maxwell transfer compression and positive remainder | `x=I/theta={0.8,8,80}`, 65 digits | Largest relative residual `1.90e-65` |

The completed command took 2.539 seconds, with peak RSS 19,300 KiB and exit code 0. New IVP, benchmark, render and old scientific suite replay counts are all zero. These controls verify the algebra and selected event law; empirical angular qualification and independent nonauthor implementation review remain parent-owned work.
