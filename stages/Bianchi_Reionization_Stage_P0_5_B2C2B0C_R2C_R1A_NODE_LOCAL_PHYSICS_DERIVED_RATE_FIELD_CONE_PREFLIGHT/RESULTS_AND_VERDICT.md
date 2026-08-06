# R2C-R1A results and durable verdict

## Research question and predeclared hypotheses

The stage asked whether the 491 radiative-current/cycling failures in R2C-R1
were removed by deterministic node-local rates, or whether they arose because
a whole-interval photon budget had been promoted to an independently relaxing
state.

Three hypotheses were frozen before the all-node audit:

1. **H1 — unchanged scalar taxonomy:** retain independent scalar relaxation
   families for `M,I,U,C,J_G1,J_G2a`, but make their rates node-local;
2. **H2 — state/flux/budget reclassification:** evolve material chemistry,
   derive radiation currents algebraically from the radiation field and
   neutral population, and enforce photon conservation through a cumulative
   interval ledger;
3. **H3 — immediate broader coupled generator:** introduce additional coupled
   positive-state coordinates before testing H2.

The decision is `REJECT H1`, `PROMOTE H2`, and `HOLD H3`.

## Conventions, units, signs, and scope

The project conventions remain metric signature `(-,+,+,+)`,
`epsilon_123=+1`, and explicit `c`, `hbar`, and `k_B`; no natural-unit
conversion is made. The metric does not enter this local homogeneous
chemistry proof.

- `M`, `N=N_HI`, and `I=N_HII`: H nuclei per comoving Mpc^3;
- `J_g`: absorbed photons or primary H photoionization events per second per
  comoving Mpc^3;
- `Gamma_g`: photoionization rate per neutral H atom, `s^-1`;
- `alpha_B n_e` and `beta_HI n_e`: down/up reaction rates, `s^-1`;
- `U_audit=(3/2) k_B M T`: an explicitly labelled thermal audit coordinate.
  It is not promoted as the production gas internal energy because the latter
  must count electrons, helium, changing mean molecular weight, and all
  heating/cooling channels.

No node-wise free rate fitting, clipping, dynamic KL repair, cloud-mass
inversion, inter-macro moment transport, or post-result rate-bound widening
was used.

## Physical operator and exact identities

Let

\[
 u(t)=\sum_g\Gamma_g(t)+\beta_{\rm HI}[T(t)]n_e(t)\ge0,
 \qquad
 r(t)=\alpha_B[T(t)]n_e(t)\ge0.
\]

For fixed H mass and without transfer,

\[
 \frac{d}{dt}
 \begin{pmatrix}N\\I\end{pmatrix}
 =
 \begin{pmatrix}-u&r\\u&-r\end{pmatrix}
 \begin{pmatrix}N\\I\end{pmatrix}.
\]

The generator is Metzler and has zero column sums. Hence it preserves
`N>=0`, `I>=0`, and `N+I=M`. Nonnegative inflow and proportional outflow
preserve the same cone and give `dot M=S_+-S_-`.

The group current is an algebraic radiation–reaction flux,

\[
 J_g(t)=\Gamma_g(t)N(t)\ge0,
\]

or the corresponding finite-cell time-averaged photon-conserving relation.
The neutral equation gives the cumulative ledger

\[
 \int_{t_0}^{t_1}J\,dt
 =N(t_0)-N(t_1)-\int Q_{\rm coll}dt+\int R_{\rm rec}dt
 +\int S_{N,+}dt-\int S_{N,-}dt.
\]

By contrast, the inherited quantity

\[
 C_{\Delta t}=\frac{N_{\rm HI,start}}{\Delta t}+\bar R_{\rm rec}
\]

obeys

\[
 C_{\Delta t/q}-C_{\Delta t}
 =(q-1)\frac{N_{\rm HI,start}}{\Delta t}.
\]

It therefore depends on the selected bookkeeping interval. Its invariant
meaning is the integrated necessary budget

\[
 B_{\Delta t}=\Delta t C_{\Delta t}
 =N_{\rm HI,start}+\Delta t\bar R_{\rm rec},
\]

not an independently evolving pointwise state.

## All-row numerical audit

| quantity | result |
|---|---:|
| state rows | 1,382,400 |
| active photon-group rows | 2,764,800 |
| macro cases | 540 |
| shape/substep cases | 30 |
| endpoint state-cone failures | 0 |
| non-finite direct-rate rows | 0 |
| negative group-current rows | 0 |
| negative group-opacity rows | 0 |
| nonpositive flux rows | 0 |
| maximum current–Gamma residual | `9.143461e-16` |
| maximum locked-moment residual | `3.540507e-14` |
| `C` refinement-noninvariant global cases at `q=2` | 10/10 |
| maximum `C` relative change at `q=8` | `0.895358` |
| old mass-proportional `C` versus local diagnostic mismatch | 1,382,400/1,382,400 node rows |
| old/local macro budget mismatch | 540/540 macros |

The endpoint-local `N/dt+R` reconstruction is retained only as a diagnostic.
It falls below inherited `J` on 957,298 node rows because it lacks
the required time averages and radiation solve; it is not used as a
replacement production budget.

The direct endpoint photoionization rates are finite and positive over the
inherited support, from `2.160862e-17` to `4.550023e-13 s^-1`. These are endpoint
diagnostics, not a calibrated interior forcing law.

## Why the Farkas blocker disappears

R2C-R1 inferred a common equilibrium from

\[
 y_1=y_{\rm eq}+(y_0-y_{\rm eq})e^{-k\Delta t},
 \qquad
 y_{\rm eq}=y_0+\frac{y_1-y_0}{1-e^{-k\Delta t}}.
\]

For finite positive `k Delta t`, the multiplier in the second expression is
greater than one, so the equilibrium lies beyond the target endpoint along
the secant direction. A convex physical endpoint segment can therefore be
feasible even when the extrapolated common equilibrium leaves the cone.

The inherited certificate partition is retained exactly:

| certificate row | count | corrected interpretation |
|---|---:|---|
| `CYCLING_CAPACITY` | 209 | uses interval budget as pointwise state |
| `J_G1_NONNEGATIVE` | 125 | extrapolates an algebraic flux equilibrium |
| `J_G2A_NONNEGATIVE` | 157 | extrapolates an algebraic flux equilibrium |
| `MACRO_MASS_CAP` | 6 | extrapolated equilibrium exceeds cap although endpoints do not |

Thus 491 certificates reject the independent `C,J_g` common-equilibrium
surrogate. They do not constrain the corrected material-state/cumulative-
ledger problem. For the remaining six mass cases, both endpoints lie below
both inherited caps and every affine endpoint/cap segment is feasible.

The convex endpoint audit gives:

- macro endpoint pairs: 540;
- state-segment failures: 0;
- mass-cap endpoint failures: 0;
- current-sign endpoint failures: 0;
- minimum neutral slack: `4.049234e+58`;
- minimum cosmic-cap slack: `2.282884e+62`;
- minimum volume-cap slack: `2.448951e+63`.

## Literature consistency and limits

The correction agrees with the C2-Ray method: absorbed-photon depletion is
matched to photoionizations, the ionization equations use an analytical
relaxation solution, and the radiation rate is iterated with time-averaged
opacity/neutral state. It also respects the later H/He/multifrequency result
that ionization fractions can converge with comparatively long steps while
accurate temperatures require a stricter optical-depth-dependent timestep
gate.

This literature supports the operator taxonomy. It does not by itself prove
that the inherited R2B endpoints possess a unique interior radiation history;
that is the task of R2C-R1B.

## Wolfram and high-precision status

No native Wolfram executable or Wolfram plugin namespace was exposed in this
runtime. No native Wolfram execution claim is made. The stage retains
`proofs/wolfram_r2c_r1a_state_flux_budget_validation.wl` and independently
passes:

- exact SymPy identities for H-nucleus conservation, Metzler signs, budget
  refinement, the integrated photon ledger, and equilibrium extrapolation;
- 90-digit Decimal replay of the largest recorded refinement covariance;
- 100-digit mpmath checks of the positive two-state semigroup, column sums,
  and `Gamma(3/2)=sqrt(pi)/2`.

The Precise Special Functions plugin was likewise not exposed in this turn;
the 100-digit mpmath calculation is explicitly a fallback, not a plugin result.

## Durable verdict and authorization

```text
DURABLE_PASS_R2C_R1A_STATE_FLUX_BUDGET_RECLASSIFICATION_RESOLVES_FARKAS_BLOCKER_R1B_AUTHORIZED
```

The structural R2C-R1 Farkas blocker is resolved: it cannot be carried forward
as a no-go theorem for physical histories. The corrected state/flux/budget
operator basis is promoted.

Authorization remains deliberately narrow:

- `R2C_R1B_authorized = true`;
- `production_node_chemistry_authorized = false`;
- `R2C_R2_authorized = false`;
- `B2C2B_authorized = false`.

The unresolved task is the interior, nonautonomous, photon-conserving
radiation/chemistry/thermal history, not endpoint feasibility.
