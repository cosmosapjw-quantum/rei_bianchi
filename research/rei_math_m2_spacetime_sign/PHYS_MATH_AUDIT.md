# PHYS-MATH audit — first sequential review pass

Reviewed exact implementation fee018efd2f1d91e2ef859c0ee91874c0437bb62 after
run 33914082531 / job 101157086098. This review is a separate reasoning pass
by the implementing assistant, not an external independent reviewer.

## Surviving result

Direct ONF curvature and an independently differentiated Bianchi-V coordinate
metric agree. The declared positive K and q=-T_i0 imply M_i=-C_i-kappa_G*q_i.
The unchanged spatial divergence is C_i=-3*a_j*sigma_ij-epsilon_ijk*n_jl*sigma_kl.
No finite sampling replaces the generic exact-polynomial checks.

## Checks

- Definitions: temporal normal n and Bianchi nB remain distinct; Bianchi a is
  not physical acceleration. D and O curvature slots are explicitly typed.
- Projection: Ricci is contracted in the matching slot order. T_i0=-q_i and
  M_i=-E_i0 are applied separately; no sign is inferred from the Hamiltonian.
- Units: s=c*t; connection L^-1, curvature L^-2, rho/q energy density,
  kappa_G=8*pi*G/c^4. Physical flux is c*q.
- Limits/parity: flat isotropic constraint follows from the generic result;
  K quadratic identity is even, mixed curvature is odd. Coordinate V agrees
  for arbitrary symmetric initial K, not only the one-component example.
- Regularity: the coordinate metric is a valid local Lorentzian germ around
  s=0. It is off shell; no energy condition or physical cosmological solution
  is inferred from the counterexample.
- Hidden assumptions: geodesic normal, Fermi triad, homogeneous components,
  Jacobi nB*a=0. General lapse/rotation dynamics and propagation are not tested.

## Risk ledger

P0 historical claim: PR #62 comment 5545445810 mixed the correct spatial
carrier with the wrong geometric sign of the negative Einstein projection.
Resolved in this REI research result by an explicit contrary derivation and
counterexample; common-owner code adoption remains separate.

P1 integration: no executed BASS-native storage-order/projection bridge.
Do not claim the common geometry owner is repaired or background-ready.

P1 uncompleted scope: constraint propagation and actual coupled evolution
remain NOT_RUN. Static constraint identities are not a stability theorem.

P2 presentation: plotted floor is 1e-30 for exact zeros, not numerical error.
Direct raster/SVG visual inspection remains unavailable and unclaimed.

No new P0 mathematical inconsistency was found in this bounded oracle. The
research sign diagnostic is supported; provider/science promotion is rejected.
