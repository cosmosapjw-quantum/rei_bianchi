# Finite-mass shell: formula-to-code map and execution design

This implementation is a scalar binary64 reference for the root-reviewed
nonrelativistic model. It does not use an earlier dynamics kernel, reconstruct
source amplitudes, or import any earlier scientific suite.

## API and conventions

All arguments are electron atomic units. `E0`, `B`, and `M` are finite and
strictly positive. Cartesian momenta have exactly three finite components.
Every detector direction is normalized by `normalize_direction`, whose result
records its original norm and whether normalization changed it. The Jacobi
convention is A spectator / (B,nucleus) pair.

| Root theory | Implementation | Result contract / independent control |
|---|---|---|
| §3 lab/Jacobi map | `to_jacobi(E0,M,p_A,p_B)`; `from_jacobi(E0,M,q,k)` | Cartesian dictionaries; inverse, determinant basis, direct lab energy/momentum controls |
| §3 global shell | `shell_state(E0,B,M,p_A,p_B)` | Raw F, internal energy, recoil Q, S5/empty/collapsed status; no claim that arbitrary input lies on shell |
| §4 conditional sphere | `conditional_sphere(E0,B,M,p_A)` | Raw H and radius², center, status, regular conditional volume; collapsed normalized distribution is not invented |
| §§5–6 complete ray branches | `solve_radial(E0,B,M,p_A,direction)` | All positive branches, zero endpoints, raw discriminant/scale, coarea weight; per-branch p_B retained |
| §10 stable quadratic | `solve_coefficients(alpha,beta,gamma)` | Stable h/alpha and 2gamma/h; no cutoff or branch merging; exact rawD and nextafter controls |
| §7 labelled phase volume | `phase_space_volume(E0,B,M)` | Kinematic Phi, zero at/below threshold; independent mp80 one-dimensional q integral |
| §8 W=1 moments | `constant_weight_moments(E0,B,M)` | Lab momentum/energy means and recoil variance; positive-node direct lab calculations |
| §7 positive degree4 rule | `sphere76_nodes()` | 12 axes plus 64 cube nodes; first three coordinates scale q and last three scale k; all monomials through degree4 tested |

For `abs(D)<=64*eps*(beta²+abs(2*alpha*gamma))`, the radial solver returns
`NEAR_CAUSTIC_UNRESOLVED`, retains raw D, and returns no finite coarea weight.
It never clips D to zero or declares no real support from that guard. Negative
ordinary D yields `NO_REAL_ROOTS`; ordinary real roots are classified by their
actual signs, with p=0 kept separately. The reference direct quadratic in
`run_analysis.py` independently forms the lab energy coefficients using
mpmath80, rather than reusing primary coefficient helpers.

The primary implementation is tested over the specified finite fixtures. It
does not certify all mixed-magnitude binary64 inputs or directed-rounded
interval endpoints. Nonfinite inputs and invalid dimensions are rejected;
derived quantities beyond binary64 range are not silently regularized.

## Targeted controls and analysis size

Fourteen new test methods are prepared, not yet executed. They cover the
Jacobi inverse/determinant, energy/momentum, support threshold, conditional
sphere, every ordinary root sign class, two positive hand roots, unresolved
near-caustic and nextafter cases, direction validation, coarea, swap symmetry,
all S5 monomials through degree4, lab moments, binding modes, and mass limits.

The planned analysis contains six proton-mass fixtures: nominal 20, 54.4,
and 413.6 eV, each with separate B=0.5 and B=mu/2 modes. It performs six
independent mp80 volume quadratures and one transformed two-root fold
quadrature. The latter directly sums both raw branches in the regular h
coordinate and compares with 4*pi*rho/alpha. It also checks 16 ordinary
radial reference cases and 76 positive lab-moment nodes per fixture.

The analysis saves 281 synthetic fold display rows and 606 finite-mass volume
ratio rows. These are display data and W=1 kinematic controls, not amplitude
cubature, a full event cross section, or a physical recoil probability law.
Actual timings and numerical outcomes remain unknown until the authorized
children run. No pilot or benchmark has been run to estimate them.

## Execution and dependency reuse

The three planned commands, only after native root GO, are:

```sh
python3 -B code/run_bounded.py 01_tests
python3 -B code/run_bounded.py 02_analysis
python3 -B code/run_bounded.py 03_plot
```

They have respective CPU/wall caps 2/6, 2/8, and 2/8 seconds. The distinct
increment is 8 CPU/30 wall seconds, 512 MiB and one thread. The remaining
2/8 reserve is one diagnosed root-authorized repair, never an automatic retry.
START/FINISH retain parent plus child CPU and measured wall time. Failed or
incomplete attempts block automatic continuation without resetting any cost.
Source/code and dependency hashes are ordinary frozen-input reproducibility
checks, not an additional authorization or authentication scheme.

mpmath1.3.0 is reused as the unchanged pure-Python wheel at
`finitemass_ops/dependencies/mpmath-1.3.0-py3-none-any.whl`, SHA256
`a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c`.
The runner prepends that workspace-relative wheel to PYTHONPATH; no install,
download, fallback precision or prior archive hierarchy is required. Restore
the dependency at that relative path beside BASS_HE before an authorized run.
Matplotlib and NumPy versions were inspected through distribution metadata
only. Plotting reads the saved passing analysis and imports no shell/reference
module. It produces one PNG/SVG with two panels and no new scientific values.

The actual current host affinity and cgroup limits are recorded in
`evidence/preparation/HOST_RESOURCE_OBSERVATION.json`. This small algebraic
scope uses the root-frozen scalar reference lane; no MPI/Fortran rewrite or
new benchmark is introduced. Historical suite results, failures, budgets and
UNKNOWN_NOT_ZERO records remain references in `evidence/REUSED_LEDGER_REFERENCES.json`.
