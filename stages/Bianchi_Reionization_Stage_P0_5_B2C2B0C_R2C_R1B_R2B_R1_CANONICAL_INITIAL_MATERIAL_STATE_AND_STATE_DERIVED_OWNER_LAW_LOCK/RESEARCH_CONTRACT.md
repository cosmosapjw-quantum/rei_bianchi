# R2B-R1 research contract

## Question

Can the two missing R2B inputs be identified from canonical durable evidence without a per-node fit: (i) the initial resolved H/He/thermal material state at `z=6`, and (ii) a nonautonomous state-dependent four-owner opacity/current law?

## Conventions

- metric `(-,+,+,+)`; `epsilon_123=+1`;
- explicit `c`, `hbar`, `k_B`;
- H/He number states in `cMpc^-3`; resolved internal energy in `erg cMpc^-3`;
- opacity in `cMpc^-1`; absorbed current in `s^-1 cMpc^-3`;
- no clipping, cloud-mass inversion, geometry inversion, owner reassignment, or post-hoc lane selection.

## Success conditions

1. One deterministic 46,080-node initial state closes H nuclei, He nuclei, all species fractions and total internal energy to `1e-11` relative or better.
2. Every state component is finite and nonnegative, and `T_i>0`.
3. The owner law is an explicit function of current material state, canonical time forcing, fixed geometry and the locked effective-HI closure.
4. Owner and node sums close, structural zeros remain exact, and perturbing a supported material state changes the corresponding owner fraction.
5. `EFFECTIVE_HI_SUBGRID` retains exact-zero resolved H, He and thermal sources.

## Claim boundary

A pass authorizes an owner-correct fixed-point rerun. It does not claim a converged history or production node chemistry.
