# R2C-R1 results and durable verdict

## Scope, assumptions, conventions, and units

The calculation is restricted to the homogeneous reionization subsystem. The
project conventions remain metric signature `(-,+,+,+)`, `epsilon_123=+1`, and
explicit `c`, `hbar`, and `k_B`; `hbar` does not enter this stage. No natural
unit conversion is used.

For every fixed micro node,

\[
M\,[\mathrm{H\,cMpc^{-3}}],\qquad
I=Mx_{\rm HII}\,[\mathrm{H\,cMpc^{-3}}],
\]

\[
U=\frac32 k_BMT\,[\mathrm{erg\,cMpc^{-3}}],\qquad
C,J_g\,[\mathrm{s^{-1}\,cMpc^{-3}}].
\]

All rates are in `Myr^-1`, all stage time intervals are in `Myr`, and every
exponential argument `k Delta t` is dimensionless. The locked cone is

\[
M\ge0,\quad 0\le I\le M,\quad U\ge0,\quad C\ge0,\quad
J_g\ge0,\quad J_{G1}+J_{G2a}\le C,
\]

together with inherited macro mass and volume caps. G2b/G3 effective-HI and
primary HeII/G3 entries remain literal exact zeros.

The tested model is intentionally narrower than a full chemistry operator. For
family `f` and one macro,

\[
Y_f(t)=Y_{f,\infty}+
       \Phi_f(t)\,[Y_f(0)-Y_{f,\infty}],
\]

where the rate law is shared by all 2,560 nodes in that macro. One mode uses
`Phi_f(t)=exp(-k_f t)`. The only permitted extension is a positive two-mode
mixture with both rates fixed to the prelocked lower and upper family bounds.
No rate is independently fitted to a node.

## Frozen rate evidence

The pre-feasibility rate lock contains 3,240 rows: three shape lanes, ten
substeps, 18 macros, and six families. Every row has a finite positive interval
or a dynamically irrelevant fixed scale; no feasibility result was inspected
while constructing it. Across the lock, the overall rate ranges are

| family | minimum [Myr^-1] | maximum [Myr^-1] |
|---|---:|---:|
| `M` | `4.41748e-05` | `9.77325e-02` |
| `I` | `4.42182e-05` | `1.08201e-01` |
| `U` | `4.32999e-05` | `2.17200e-01` |
| `C` | `4.41847e-05` | `8.66196e+00` |
| `J_G1` | `1.97226e-17` | `5.17258e-02` |
| `J_G2a` | `1.97829e-17` | `6.79970e-02` |

`C` and `J_g` remain interval nuisance families rather than calibrated
microphysics because the inherited state has no independent node-redistribution
equation for them.

## Full-run census

The single-writer final run wrote 540/540 equilibrium certificates and 540/540
trajectory certificates in `95.489827 s`.

| quantity | count |
|---|---:|
| total macro cases | 540 |
| equilibrium LP feasible | 43 |
| equilibrium Farkas no-go | 497 |
| one-mode trajectory selected | 1 |
| two-mode trajectory selected | 42 |
| analytic trajectory pass | 43 |
| full refinement pass | 27 |
| coarse `n=2` cone failures after analytic pass | 16 |
| whole shape lanes passing | 0 of 3 |

Per shape lane:

| shape lane | equilibrium feasible | one-mode | two-mode | refinement pass | whole-lane pass |
|---|---:|---:|---:|---:|---|
| `LOCAL_NEUTRAL_HAZARD_PRIMARY` | 16 | 0 | 16 | 9 | false |
| `RECOMBINATION_WEIGHTED_AUDITOR` | 14 | 0 | 14 | 8 | false |
| `SCRIPT_SELF_SHIELDING_AUDITOR` | 13 | 1 | 12 | 10 | false |

All 43 equilibrium-feasible cases have an analytically certified trajectory.
The two-mode path repairs 42 one-mode interior-cone failures, but it cannot
repair an equilibrium-box no-go. Of those 43 analytic passes, 16 violate the
cycling cone only at the coarsest two-step discretization; all 43 pass at four
and eight steps. These 16 are numerical-resolution warnings, not the dominant
model blocker.

## Dual/Farkas obstruction census

Every one of the 497 equilibrium failures has a self-contained
`SINGLE_ROW_BOX_FARKAS` certificate. An independent validator reconstructs the
six-dimensional columns, right-hand sides, bound terms, stationarity,
duality, and complementarity without importing the production solver.

| violated physical row | count |
|---|---:|
| `CYCLING_CAPACITY` | 209 |
| `J_G1_NONNEGATIVE` | 125 |
| `J_G2A_NONNEGATIVE` | 157 |
| `MACRO_MASS_CAP` | 6 |

Thus 491/497 no-go cases are in the radiative-current/cycling sector and six
are local macro mass-cap failures. The minimum reconstructed positive box gap
is `1.060054463e-02`; the largest, hence weakest, normalized negative dual
product is `-8.645235618e-14` and still closes with an independently replayed
zero-column residual.

A separate non-authorizing diagnostic asks how far one attenuation coordinate
alone would have to leave `[0,1]` to remove the emitted single-row obstruction.
It reports 97 cycling cases for which that smallest one-coordinate repair has
`a<=1`, so no finite positive scalar rate exists for that one-family repair.
For finite one-coordinate repairs, median required factors outside the locked
upper-rate evidence are about `6.98` for G1 and `4.04` for G2a; the six
mass-cap rows require roughly `1.489--1.510`. These numbers diagnose missing
rate evidence or coupling. They do **not** authorize post-result widening.

## Conservation, KKT, and exact gates

Fresh final validation gives:

- maximum endpoint relative residual: `5.7079543226e-17`;
- maximum current-Gamma relative residual: `9.1434612599e-16`;
- independently replayed maximum KKT relative stationarity:
  `2.0266184038e-16`;
- independently replayed maximum relative duality gap:
  `1.0393075289e-13`;
- independently replayed maximum complementarity:
  `1.0397722224e-13`;
- maximum Taylor-certificate work: 37 intervals, depth 11, below the locked
  limits of 200,000 and 24;
- exact-zero rows: `540/540`;
- node-rate fitting: false;
- clipping: false;
- dynamic KL projection: false;
- macro-to-macro moment transport: false.

The large raw HiGHS absolute stationarity value (`1.04e-7`) is a cancellation
scale effect involving dual terms of order `1e11`; the componentwise relative
stationarity and an independent active-set NNLS certificate close it. The
recorded failed attempts preserve the initial absolute-residual false negative
and the HiGHS marginal-sign/cancellation investigation.

## Wolfram and high-precision status

No native Wolfram executable or Wolfram plugin namespace was exposed in this
runtime, so no native execution claim is made. The repository contains
`wolfram_r2c_r1_multirate_cone_validation.wl`. Independent SymPy, 90-digit
Decimal, and 100-digit mpmath fallback checks pass for endpoint identities,
two-mode attenuation, Taylor derivative identities, Farkas cancellation, KKT
complementarity, exact zeros, and `Gamma(3/2)=sqrt(pi)/2`. The first fallback
run with an incorrect cancellation scale is preserved as Attempt 9 rather than
overwritten.

## Durable verdict

```text
DURABLE_FAIL_CLOSED_R2C_R1_MACRO_SHARED_COMMON_EQUILIBRIUM_MULTIRATE_CONE_NOT_ALL_LANES_REACHABLE
```

The stage rejects the hypothesis that one macro-shared positive rate family,
with a common equilibrium and the prelocked rate evidence, connects every R2B
node endpoint while remaining in the physical cone. It does not reject
physically derived node-local rate fields or a non-autonomous/coupled positive
operator. Production node chemistry, R2C-R2, and B2C2B remain unauthorized.
