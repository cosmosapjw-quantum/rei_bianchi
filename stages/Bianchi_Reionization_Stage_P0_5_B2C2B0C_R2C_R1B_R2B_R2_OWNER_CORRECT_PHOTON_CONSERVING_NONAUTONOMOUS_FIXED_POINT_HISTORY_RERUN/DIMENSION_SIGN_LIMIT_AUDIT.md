# Dimension, sign, and limit audit

- Signature: `(-,+,+,+)`; `epsilon_123=+1`.
- `dt` is seconds; all atomic/photo rates are `s^-1`; rate-times-step is dimensionless.
- Number states are nonnegative counts on a comoving node measure; proper density is count divided by proper node volume in `cm^3`.
- `U_resolved` is `erg cMpc^-3`; heating/cooling/expansion terms are `erg s^-1 cMpc^-3`.
- Photon absorption is nonnegative. The subgrid resolved-source vector is exactly `(0,0,0)`.
- H and He nuclei sums use opposite-sign reaction vectors and close to below `8e-16` in all required failed slabs.
- Expansion-only limit: implicit thermal solve gives `T_{n+1}=T_n/(1+2 H dt)>0`.
- Zero-radiation limit leaves photon owner counts at zero.
- `dt -> 0` limit tends to the parent state.
- No clipping, owner reassignment, cloud/geometry inversion, or `kappa=J/Phi` constitutive inversion is present.
