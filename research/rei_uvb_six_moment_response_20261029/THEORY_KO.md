# REI UVB six-moment source-response bridge · theory (2026-10-29)

## Scientific boundary and sources

The frozen source is the Becker–Bolton (2013) seven-point log10 HI photoionization-rate inference and full correlated covariance, SHA256 `13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b`. Prior PR260 `7438e2e85e8f0ecb03292558280521bbf58e707d` established the conditional GLS coefficient set `U_q=Z+E_q`. The new source projection uses 13 consecutive knots (2.32≤z≤4.89) of the **fiducial nonequilibrium** Puchwein et al. (2019) H/He photoionization and heating table (original Git blob `218d81f68447da438228a7b102e1cec96a8e8a1a`, PR251 commit `c5ab42c8673db614e7fb16695ad071c65becb81b`). This is a numeric subset projection, not raw-byte identity to the full 59-row table. Its log-positive interpolation reproduces all seven previously frozen HI template values within 1.16e-15 dex.

Let `a=(beta,kappa)^T`, `t(z)=(1,z-3.6)^T`. `beta` has units dex and `kappa` dex per redshift; `R^P_X(z)` has units `s^-1` per target for photoionization or `eV s^-1` per target for photoheating. The conditional model assumes a **common six-moment rescaling** with unchanged spectral shape, which is not six-channel observational calibration:

`R_X(z;a)=R^P_X(z) exp[ln(10) t(z)^T a]`, `2.4≤z≤4.75`.

The fit variable is the *mean redshift coordinate* used in the table. In Bianchi spacetimes the observed photon redshift can be direction-dependent and has not been mapped to this mean variable. No extrapolation to the saved z20 initial state is authorized. H/He heating and helium rates inherit the common-amplitude **model assumption**, not independent observational covariance. No Li, nuclear, CR, photon spectrum or Compton input is supplied by the six moments.

## Exact derivatives and nonlinear envelope

At fixed `z` and fixed template, `D_a R_X = (ln10) R_X t^T`, `D_a^2 R_X = (ln10)^2 R_X t t^T`.

With `Z=c+G[-1,1]^8`, `E_q={δ:δ^T V^-1 δ≤q}` and `U_q=Z+E_q`, define

`L(z)=t^T c - ||G^T t||_1 - sqrt(q t^T V t)`,
`U(z)=t^T c + ||G^T t||_1 + sqrt(q t^T V t)`.

Then each positive source moment has exact pointwise extrema `R^P_X(z)*10^L(z)` and `R^P_X(z)*10^U(z)` over this conditional coefficient set. Different z and species need not share a coefficient witness. q=0 is deterministic EOS–Jeans support; q1=3.8414588206941236 gives at-least-95% coverage for **one predeclared scalar functional** under PR260's fixed-template known-C Gaussian model; q2=5.991464547107982 gives at-least-95% simultaneous coefficient coverage and hence simultaneous source-history envelope under the same model. Neither is independent six-moment observation. Coverage needs correct mean, true nuisance in box, fixed model and known C.

For `δa`, put `u=(ln10)t^T δa`. The exact Taylor remainder is `R_X(a)[exp(u)-1-u]`, nonnegative and bounded by `0.5 R_X(a) exp(|u|) u^2`. This is a parameter-space truncation bound, not a physical trajectory error.

## Conditional source event and energy ownership

For externally supplied target fractions `y_X=n_X/nHref`, **holding y fixed**, photoevents per Href/s `P_X=y_X Γ_X`, photoheat per Href/s `Q_X=y_X ε_X` in eV/Href/s. With externally supplied ionization threshold `I_X` in eV, ionization-storage gain is `I_X P_X`; absorbed photon energy is `Q_X+I_X P_X`. Fixed-y derivatives multiply the rate Jacobian by `y_X`. In a real chemistry/thermal trajectory, `D_a y_X` is additional and the total derivative includes `Γ_X D_a y_X` and `ε_X D_a y_X`. No frozen-y result is an evolved population response.

## Clock and Thomson optical-depth boundary

For **mean** scale factor `x=ln(a/a_ref)`, `1+z_m=a_ref/a`, `dz_m/dx=-(1+z_m)`, and `d/dt=H d/dx` in normal proper time. In an open Puchwein log-linear knot cell,

`dR_X/dx=-(1+z_m) R_X [d ln R^P_X/dz_m + ln(10) kappa]`, `dR_X/dt=H dR_X/dx`.

At a table knot the interpolation has distinct one-sided slopes; no unique derivative is fabricated. Direction-dependent observed redshift requires a separate tetrad/line-of-sight map.

The pinned BASS PR234 source row is `dτ_T/dx=K n_e/H`, with `K=GAMMA_PER_NE/10^6` in its source convention. At fixed K,

`D_a(dτ_T/dx) = K/H * D_a n_e - K n_e/H^2 * D_a H`.

This is algebraic, **not a computed tau response**: actual `D_a n_e` needs the physical chemistry/thermal variational equation and initial data, `D_a H` needs geometry response, and K, density, source clock and directional redshift must be bound to actual provider identities. BASS PR234 has R6/C9 distinct-author HOLD and no physical whole-corridor certificate. A manufactured K=1 test is not an astrophysical K value. A future tangent system would be `dS/dt=J_y S + J_R D_a R + J_g D_a g`, with physical IC/BC; it was **NOT_RUN**.

## Source status, evidence and limits

The source moment response and pointwise support were derived and checked by 21 targeted Python tests, including independent QR vs Cholesky, 256 nuisance corners at three z (not old GLS campaign replay), six-moment rate Jacobian/Hessian, finite differences, MP80 mean-clock derivative, exact energy ownership, and error/domain negative controls. Wolfram separately simplified source Jacobian, Hessian, tau tangent and exponential convexity (corrected evaluation: five zeros and True). First CAS tau check had a substitution-precedence defect and is preserved in the execution note. No different-author native R6/C9 tool was exposed; selected unit is 18/20 scoped, not 20/20. No IVP, physical source-rate solver or figure render.

Physical F4=PARTIAL, L4_ready=false, native25/actual REI T/physical radii=null; original REI DAG working33/88, central last28/88, delta0. Historic main/presentation budgets and UNKNOWN_NOT_ZERO overhead are not reset or transferred.
