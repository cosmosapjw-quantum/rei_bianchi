# Dimension, sign, and limiting-case audit

## Dimensions

- `M` and `I`: hydrogen-number density in `H cMpc^-3`.
- `U`: thermal-energy density in `erg cMpc^-3`.
- `C` and `J_g`: event/current density in `s^-1 cMpc^-3`.
- `k_f`: `Myr^-1`.
- `t` and `Delta t`: `Myr`.
- `k_f t`, attenuation, mode weights, KL, TV, and normalized LP coordinates:
  dimensionless.
- `c`, `k_B`, eV-to-erg, Mpc-to-cm, and Myr-to-s conversion factors are
  explicit in `src/rate_interval_model.py`.

## Sign conventions

All physical rates and mode weights are nonnegative. The LP inequalities use
`A_ub z<=b_ub` with `z in [0,1]`. SciPy HiGHS marginals have the opposite sign
convention from many nonlinear-solver Lagrange multipliers; the stage does not
trust them directly. It reconstructs an active-set nonnegative dual and stores
all columns, right-hand sides, weights, and slacks.

## Limiting cases

For one mode,

\[
a(k)=[1-e^{-k\Delta t}]^{-1}.
\]

- `k Delta t -> 0+`: `a ~ 1/(k Delta t)+1/2+...`, so the inferred equilibrium
  moves far beyond the endpoint; this is the slow-relaxation extrapolation
  hazard.
- `k Delta t -> infinity`: `a -> 1+`; the equilibrium approaches the target
  but never gives `a<1` for a finite positive scalar rate.
- coincident two-mode bounds: the mixture reduces continuously to one mode;
  the implementation returns a neutral weight because both rates are equal.
- weight `w=0` or `w=1`: the two-mode kernel reduces exactly to the fast or
  slow endpoint rate.
- zero endpoint change: the family is dynamically irrelevant; a shared
  reference scale is used only to evaluate the locked formula and adds no
  physical claim.

## Cone-coordinate implication

The current/capacity cone is equivalent to nonnegativity of

\[
(C-J_{G1}-J_{G2a},\ J_{G1},\ J_{G2a}).
\]

This observation motivates, but does not yet authorize, a later Metzler
positive-generator model. The next stage first tests whether deterministic
node-local physical rate fields remove the artifact of macro averaging.
