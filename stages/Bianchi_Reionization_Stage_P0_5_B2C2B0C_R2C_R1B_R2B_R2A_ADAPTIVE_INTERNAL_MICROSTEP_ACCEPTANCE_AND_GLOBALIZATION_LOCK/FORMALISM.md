# Formalism — adaptive owner-correct thermochemistry

## Conventions and units

Metric signature is `(-,+,+,+)` and `epsilon_123=+1`. The present stage is a
homogeneous-background scalar reionization calculation. `c`, `hbar` and `k_B`
remain explicit in the inherited atomic, thermal and geometric adapters.
Material species are comoving number densities in `cMpc^-3`; thermal energy is
stored in the inherited resolved-energy coordinate; time is evaluated in
seconds internally and reported in Myr where useful.

## State and owner map

The structure-of-arrays material state is

```text
Y = (N_HI, N_HII, N_HeI, N_HeII, N_HeIII, U_resolved)[node].
```

At each forcing time the authoritative group totals `kappa_g(t)` and `J_g(t)`
are inherited. State-conditioned nonnegative owner responses `r_og(Y,t)` define

```text
p_og = r_og / sum_o r_og,
kappa_og = kappa_g p_og,
J_og = J_g p_og.
```

Within an owner, node response `h_iog` defines

```text
q_iog = h_iog / sum_i h_iog,
J_iog = J_og q_iog.
```

Unsupported owner/group pairs are exact zero. The effective-HI subgrid owner
has the exact resolved-source vector `(0,0,0)` for H, He and `U_resolved`.

## Globalized fixed point

For the implicit physical map `G(Y)` the trial iteration is

```text
Y_(k+1) = Y_k + lambda_k [G(Y_k)-Y_k],
lambda_k in {1,1/2,1/4,1/8,1/16,1/32,1/64}.
```

The largest candidate preserving the positive cone, structural zeros and the
predeclared residual decrease is selected. If every candidate fails, the
attempt is rejected and bisected; no projection or clipping is permitted.

## Adaptive step-doubling contract

The first canonical interval begins at partition 8. A rejected interval alone
is recursively bisected up to partition 1024. Each attempted interval computes
one full backward-Euler trial and two successive half trials. Every trial must
independently pass fixed-point, positivity, H/He nuclei, owner/photon, thermal
and unresolved-energy gates before the blockwise local error is evaluated.

The accepted candidate would be the two-half-step state. The hard blockwise
error is the maximum of the declared `x_HII`, `x_HeII`, `x_HeIII` and `log T`
coordinates. An accepted microstep commits exactly once. Failure, rejection,
event rollback and restart preserve the parent state and ledger bytes.

## Exact identities

Hydrogen and helium updates close by construction:

```text
N_HI + N_HII = N_H,
N_HeI + N_HeII + N_HeIII = N_He.
```

Uniform partitioning preserves an exactly integrated budget:

```text
sum_(m=1)^n (dt/n) J = dt J.
```

The Wolfram and exact-fallback receipts verify these identities, owner sums,
the damped-Picard convex identity and the exact subgrid zero source.
