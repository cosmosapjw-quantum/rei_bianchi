# R2B-R1 formalism

## Conventions and units

The metric signature is `(-,+,+,+)` and `epsilon_123=+1`. The constants
`c`, `hbar`, and `k_B` are explicit. Extensive H/He counts and thermal energy
are per comoving cubic megaparsec: `cMpc^-3` and `erg cMpc^-3`. Proper atomic
number densities are in `cm^-3`, photoionization cross sections in `cm^2`,
proper lengths in `cm`, comoving opacity in `cMpc^-1`, and absorbed photon
current in `s^-1 cMpc^-3`.

## Canonical initial material state

The exact `CANONICAL_DIRECT_REEVOLVED` row at `z=6` supplies

`x_HII`, `x_HeII`, `x_HeIII`, `T`, and `Gamma_HI`.

The neutral-helium fraction is not independently fitted:

`x_HeI = 1 - x_HeII - x_HeIII`.

Let `W_i delta_i` be the fixed positive two-scale hierarchy mass measure,
normalized by

`sum_i W_i delta_i = 1`.

With the comoving mean hydrogen count

`N_H^c = n_H,0 (1 Mpc)^3`

and helium abundance by number `Y_He=0.079`, the node nuclei counts are

`N_H,i = N_H^c W_i delta_i`,

`N_He,i = Y_He N_H,i`.

The hierarchy supplies positive local fraction and temperature shapes. H and He
species are obtained by multiplying those shapes by the extensive nuclei
counts. The raw ideal-gas energy is

`U_i^raw = (3/2) k_B N_part,i T_i^prior`,

where

`N_part,i = N_H,i + N_He,i + N_e,i`.

One positive global factor

`lambda_U = U_global^canonical / sum_i U_i^raw`

is applied to every node. This closes the canonical total energy without
per-node fitting or state clipping. The recovered temperature obeys exactly

`T_i = 2 U_i / (3 k_B N_part,i)`.

This state is deterministic and canonical **under the locked hierarchy and
single-normalization policy**; it is not a claim that global moments alone
uniquely determine an arbitrary 46,080-node field.

## State-conditioned four-owner law

The mutually exclusive owners are

1. `EFFECTIVE_HI_SUBGRID`,
2. `EXPLICIT_HI_ATOMIC`,
3. `EXPLICIT_HEI_ATOMIC`,
4. `EXPLICIT_HEII_ATOMIC`.

The structural support matrix is exact:

```text
G1:  EFFECTIVE_HI_SUBGRID
G2a: EFFECTIVE_HI_SUBGRID + EXPLICIT_HEI_ATOMIC
G2b: EXPLICIT_HI_ATOMIC + EXPLICIT_HEI_ATOMIC
G3:  EXPLICIT_HI_ATOMIC + EXPLICIT_HEI_ATOMIC + EXPLICIT_HEII_ATOMIC
```

For explicit species `s`, the raw comoving response is

`r_sg(Y,t) = a n_s^proper(Y,t) bar_sigma_sg (1 Mpc)`.

The effective-HI subgrid **global amplitude** remains the externally locked
R2A response; it is not re-fitted. Its node distribution is state-conditioned.
For group `g in {G1,G2a}` the primary node measure is

`h_i,g^sub = W_i n_HI,i bar_sigma_HI,g exp[-tau_i,g/2]`,

`tau_i,g = n_HI,i bar_sigma_HI,g L_J,i`.

The exponential is evaluated directly. Large optical depths may underflow to
the mathematical limiting value zero; no state, photon count, or constraint is
clipped.

The raw owner responses are conditioned to the authoritative canonical total:

`p_o,g = r_o,g / sum_o r_o,g`,

`kappa_o,g = kappa_g^canonical p_o,g`,

`J_o,g = J_g^canonical p_o,g`.

Within each owner, node allocation uses the corresponding positive physical
measure `h_i,o,g`:

`q_i,o,g = h_i,o,g / sum_j h_j,o,g`,

`J_i,o,g = J_o,g q_i,o,g`.

Thus owner and node sums close while the authoritative total amplitude is never
redefined by `kappa=J/Phi`. The law is nonautonomous through the canonical BDF
forcing row and state-dependent through explicit species populations and the
subgrid neutral/temperature/Jeans measure.

## Ownership firewall

`EFFECTIVE_HI_SUBGRID` has the exact resolved source vector

`(S_H, S_He, S_U,resolved) = (0,0,0)`.

Its photons and absorbed energy remain in separate unresolved ledgers. The
`rec_bianchi` project contributes only XOR ownership and accepted-step
transaction semantics; no recombination rate, history, or state is imported.
