# Dimension, sign, and limit audit

## Dimensions

| quantity | dimension used in this stage |
|---|---|
| `M,N,I` | H nuclei cMpc^-3 |
| `J_g,Q_coll,R_rec,S_N` | s^-1 cMpc^-3 |
| `Gamma_g, alpha_B n_e, beta_HI n_e` | s^-1 |
| `kappa_g` | cMpc^-1 |
| `Phi_g` in inherited current–Gamma representation | s^-1 cMpc^2 |
| `C_Delta t` | s^-1 cMpc^-3 |
| `B_Delta t=Delta t C_Delta t` | H nuclei or photons cMpc^-3 |
| `U_audit` | erg cMpc^-3 |

Every term in the neutral H equation has units `s^-1 cMpc^-3`. Every
exponential argument uses a rate times a time and is dimensionless.

## Signs and invariant cone

For `u,r>=0`, the H generator

\[
A=\begin{pmatrix}-u&r\\u&-r\end{pmatrix}
\]

has nonnegative off-diagonal entries and zero column sums. At `N=0`,
`dot N=rI>=0`; at `I=0`, `dot I=uN>=0`. With nonnegative inflow and
proportional nonnegative outflow, the nonnegative orthant remains invariant.

The all-node endpoint audit found zero negative `M`, `N`, `I`, `J_g`, or
`kappa_g` rows and zero `x_HII` values outside `[0,1]`.

## Limits

- `Delta t -> Delta t/q`: `C` changes by `(q-1)N_start/Delta t`; it is not a
  refinement-invariant state.
- `Delta t -> 0`: the rate-form storage term diverges for nonzero neutral
  inventory, while the integrated storage budget remains `N_start`.
- `k Delta t -> infinity`: a common-equilibrium relaxation approaches its
  equilibrium from the initial state.
- finite `k Delta t > 0`: solving backward for the equilibrium extrapolates
  beyond the target endpoint by the factor `1/(1-exp(-k Delta t))>1`.
- `u=0` or `r=0`: the positive generator reduces continuously to one-way
  recombination or ionization without leaving the H cone.
- `N -> 0`: `Gamma=J/N` is not used as a numerically divided state; the
  photon-conserving absorbed-count relation is the correct finite-cell form.

## Thermal warning

`U_audit=(3/2)k_BMT` is only a sign/dimensional monitor. A production thermal
equation must include the total particle number, changing electron fraction,
helium, mean molecular weight, and explicit heating/cooling. Therefore no
thermal-history authorization follows from `U_audit>=0`.
