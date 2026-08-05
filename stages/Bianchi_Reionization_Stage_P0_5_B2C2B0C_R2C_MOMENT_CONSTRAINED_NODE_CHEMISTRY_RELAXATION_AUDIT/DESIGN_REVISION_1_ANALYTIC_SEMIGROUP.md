# R2C design revision 1 — analytic semigroup plus capacity projection splitting

This additive revision supersedes only the backward-Euler sentence in the immutable pre-calculation `OPERATOR_SPEC.md`; the original file and its pre-calculation hash remain preserved.

## Reason

C2-Ray advances the ionization rate equation with an analytical relaxation solution, and its H/He extension reports that temperature, rather than ionization fraction alone, supplies the stricter timestep sensitivity. A backward-Euler truncation error would therefore mix numerical integrator error with the physical reachability question posed by R2C.

## Revised auditor

For each consecutive hard R2B endpoint and each `tau={10,100,300} Myr`, infer the constant equilibrium

```text
Y_eq = Y_0 + (Y_1-Y_0)/(1-exp(-Delta t/tau))
```

for the extensive node measures

```text
M_i,
I_i = M_i x_HII,i,
U_i = (3/2) k_B M_i T_i,
C_i,
J_i,G1,
J_i,G2a.
```

The exact exponential semigroup is the physical reference. A separate backward-Euler family at refinement factors `1,2,4` advances the same inferred equilibrium; after each discrete current update, the inherited row-capacity/column-moment KL projection is applied. The discrete family is compared with the exact pointwise-projected reference. Backward Euler therefore measures numerical and projection-splitting convergence only; it does not decide whether the underlying equilibrium is physically admissible.

## Gates

1. The inferred equilibrium must remain in the nonnegative extensive cone, with `0 <= I_eq <= M_eq`; macro mass and volume caps remain hard.
2. No clipping is permitted. An infeasible equilibrium or projection is recorded with a dual/constraint certificate.
3. Every projected substep preserves the prescribed G1/G2a column moments and node row capacities.
4. The final backward-Euler/projected state is compared directly with the hard R2B endpoint and with the exact pointwise-projected reference; no endpoint replacement is allowed.
5. `dt`, `dt/2`, `dt/4` endpoint errors, refinement ratios, and observed orders are recorded. Production authorization requires all three shape lanes and all requested tau lanes to pass.
6. `tau=10 Myr` remains only an existence witness even if it passes.

The B2C0 HII case-B coefficient is used only to audit the inherited capacity shape; it is not a primordial-recombination surrogate and does not alter the hard capacity endpoint.
