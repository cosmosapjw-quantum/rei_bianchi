# R2B-R2 owner-correct fixed-point history formalism

## Conventions and units

Metric signature is `(-,+,+,+)` and `epsilon_123=+1`. The background is homogeneous. `c`, `hbar`, and `k_B` remain explicit. Material abundances are extensive counts per comoving-volume node measure, proper node volumes are in `cm^3`, rates are in `s^-1`, `U_resolved` is in `erg cMpc^-3`, temperature is in K, and every product `rate * dt` is dimensionless.

## State and owner split

The accepted material state is

```text
Y=(N_HI,N_HII,N_HeI,N_HeII,N_HeIII,U_resolved).
```

At each Picard iterate the R2B-R1 law recomputes explicit H I, He I and He II owner responses and the state-conditioned subgrid node measure. Authoritative total `kappa_g,J_g` are not recalibrated. The unresolved `EFFECTIVE_HI_SUBGRID` owner updates only unresolved photon/energy ledgers and has exact-zero resolved H, He and thermal sources.

## Frozen-coefficient implicit map

For coefficient state `Y^(k)`, the five-species event matrix is assembled from photoionization, collisional ionization and full-OTS recombination/cascade channels. The next candidate solves

```text
[I-dt A(Y^(k))] n^(k+1)=n_parent.
```

The thermal candidate is the positive root of the scalar backward-Euler equation in `log T`; no post-step clipping is used. A convex damping step remains inside the positive material cone.

## Locked convergence gate

The hard residual is the maximum over all 46,080 nodes of H II fraction, He II fraction, He III fraction and `log T` changes. Weighted means are diagnostic only. A step is accepted only if this hard residual is at most `1e-10`, every species and temperature is positive, H and He nuclei close, and the thermal backward-Euler balance closes.

## Result boundary

At the required first slab sizes `dt,dt/2,dt/4,dt/8`, the Picard map did not converge within 40 iterations. The first interval divided by 256 did converge to residual `4.9730886075849412e-11`. Therefore the stage establishes a deterministic need for an internal adaptive microstep/globalization policy. It does not establish physical nonexistence and does not promote a production history.
