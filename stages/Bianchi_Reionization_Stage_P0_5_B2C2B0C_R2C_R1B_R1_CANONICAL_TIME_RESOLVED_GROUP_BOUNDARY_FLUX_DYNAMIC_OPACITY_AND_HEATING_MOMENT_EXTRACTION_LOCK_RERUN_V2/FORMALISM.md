# R1B-R1 formalism

## Conventions and units

Metric signature is `(-,+,+,+)`, `epsilon_123=+1`, and `c`, `hbar`, and `k_B` remain explicit. Number densities are in `cm^-3`, cross sections in `cm^2`, proper lengths in `cm`, global opacity in `cMpc^-1`, photon-current density in `s^-1 cMpc^-3`, and thermal rates in `erg cm^-3 s^-1`.

## Canonical time representation

For each of the five BDF intervals, the dense solution is evaluated on a global Chebyshev–Lobatto grid and integrated with stable Clenshaw–Curtis weights. The predeclared candidates are N={9,17,33,65}. N=9 fails; N=17 is the smallest common grid satisfying

`max dense residual < 2e-4` and `max N-to-next-N delta < 2e-4`.

The accepted representation has 85 time rows. It is an evaluation of the canonical dense solution, not endpoint interpolation.

## Atomic moments

For species `s` and group `g`, with photon-number spectrum `phi(E) proportional to E^-2.5`,

`bar_sigma_sg = int phi sigma_s dE / int phi dE`.

The optically thin and thick excess-energy limits are

`epsilon_thin = int phi sigma_s (E-E_th,s) dE / int phi sigma_s dE`,

`epsilon_thick = int phi (E-E_th,s) dE / int phi dE`.

Unsupported species/group pairs are structural exact zeros. The finite optical-depth kernel is `1-exp[-tau sigma(E)/bar_sigma]`.

## State-derived conditional opacity measure

At node `i`,

`tau_i,g = L_i sum_s n_s,i bar_sigma_sg`,

which is dimensionless. With fixed hierarchy weight `W_i`, define the differential absorption measure

`h_i,g = W_i tau_i,g`.

Conditional on nonnegativity, exact-zero support locality, a common incident macro flux, and absolute continuity with one common density, normalization forces

`q_i,g = h_i,g / sum_j h_j,g`.

The inherited global opacity and current are then disintegrated by the same `q`:

`kappa_i,g = kappa_g q_i,g`,

`J_i,g = J_g q_i,g = (J_g/kappa_g) kappa_i,g`.

This is conditionally unique under the stated axioms. It is not a theorem that the absolute global `kappa_g` follows from the node state alone; that normalization remains the canonical B2C2A-R1 input.

## Heating

For optical-depth coordinate `tau`,

`epsilon_sg(tau) = int phi [1-exp(-tau sigma/bar_sigma)] (E-E_th,s) dE / int phi [1-exp(-tau sigma/bar_sigma)] dE`.

The BDF source lane coincides with the thin limit to floating-point precision. Photon-number and energy ledgers remain separate. Thermal ownership is photoheating minus recombination/excitation/collisional-ionization/free-free cooling minus expansion work. No mass-transfer work is introduced here.
