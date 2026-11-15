# R3/C3 — claim map and numerical contract

All four inputs are completed *represented* histories of the original
conditional model. They are not independently converged solutions.
Exploratory values have already been inspected; this is a frozen output
and acceptance contract, not a claim of a blinded preregistration.

| Claim | Evidence status and discriminating check | Claim ceiling |
| --- | --- | --- |
| Four full histories were restored | Full-file SHA-256 equals original completed-case manifest; 312,238 finite ordered rows per case; endpoints zbar20,4 | Implementation verified input identity |
| Element fractions and Y_i describe the same H/He state | Reconstruct n_e = n_H x_HII + n_He(x_HeII+2x_HeIII), H and He complements, sum A_i Y_i=1; residual <=1e-12 | Derived normalization on saved states |
| Fixed-zbar and fixed-elapsed-time responses differ | Keep both a/t coordinates; evaluate the exact decomposition below; independent search/interpolation audit | Numerically checked saved-model response, not a new physical detection |
| Small q affects the physical-density-fixed clock at order q^2 | Stable analytic integrand for t_q-t_0; independent adaptive quadrature; compare with saved clock | Background/clock consistency, not source-evolution error |
| Local HII milestones advance/delay in a specified coordinate | First consecutive upward crossing; no extrapolation; preserve native bracket and censored status | Piecewise-linear saved-history milestone; numerical evolution uncertainty UNKNOWN |
| REC electron collision law is usable on this source | Exact proper n_e, physical seconds, same non-tilted frame; conditional survival sum equals -expm1(-tau) | Segment optical depth only; no full observer tau or polarized sky |
| A donor's angular correction is not universal | Original Gauss-Legendre 8-node positive rule reproduces isotropic moments; compare donor midpoint rule separately | Cubature calibration only |

## Coordinate definitions and exact decomposition

Use metric signature (-,+,+,+),

    ds^2 = -c^2 dt^2 + a^2 exp(-2b)(dx^2+dy^2) + a^2 exp(4b) dz^2.

Here t is elapsed proper time since that model's mean-redshift-20 initial
surface, a_i=1/21 and b_i=0. With fixed physical density parameters,

    H_F(a)^2 = H0^2 (Omega_r a^-4 + Omega_m a^-3 + Omega_Lambda),
    s_q(a) = q H_F(a_i) (a_i/a)^3,
    H_q(a) = sqrt(H_F(a)^2+s_q(a)^2),
    dt_q/d ln a = 1/H_q(a),       db_q/d ln a = s_q(a)/H_q(a).

For any saved scalar X, define the two different comparisons

    Delta_a X(a) = X_q(a)-X_0(a),
    Delta_t X(t) = X_q(a_q(t))-X_0(a_0(t)).

Then, using the same interpolation operator throughout,

    Delta_t X(t) = Delta_a X(a_q(t))
                  + [X_0(a_q(t))-X_0(a_0(t))].

The second term is the clock displacement evaluated on the reference
history. This identity does not prove that either term is a converged
response, and is not a coupled SAME_H counterfactual. Locally,

    Delta_t X = Delta_a X - X'_0(ln a) H_F(a) [t_q(a)-t_0(a)]
                + higher-order coordinate terms.

The exact background clock displacement is negative for nonzero q. Let
r=s_q/H_F and v=sqrt(1+r^2). Avoid subtracting two nearly equal reciprocals:

    dt_q/d ln a - dt_0/d ln a = -r^2/[H_F v(v+1)].

This has units seconds; integrate over dimensionless ln a. It vanishes
at q=0 and starts at -s_q^2/(2 H_F^3). The geometry clock is exactly even
in q. Scalar radiative responses need not be exactly even: a traceless
axisymmetric shear has a nonzero cubic invariant, so odd higher-order
terms are allowed. No missing +0.01 history may be manufactured by parity.

## Interpolation, sample grids, uncertainty

Use every accepted saved row as input. Set a 1001-node uniform-ln(a) grid
for the equal-zbar comparison and a 1001-node uniform-ln(a_0) reference
grid mapped to elapsed time over the *common* time domain. No clamping
outside either source domain. Preserve candidate/reference a,t,z and
evaluate X linearly in ln(a) between neighboring accepted states.

Milestones are the first upward crossing in the original ordered rows.
Linearly locate it in ln(a), interpolate the corresponding t/T in that
same native bracket, and save both bracket ends. Compare a PCHIP inverse
within the same monotonic local bracket and a separate scalar implementation
as diagnostics. Neither method difference nor native bracket width is a
rigorous error bound on the physical evolution. Original AX11 refinement
uncertainty remains UNKNOWN, including when the paired shift is smaller
than a saved timestep. Do not round that uncertainty to zero.

Abundances use f_He=n_He/n_H=Y_He/[4(1-Y_He)] from the frozen scenario.
The baryon-number convention is n_b=n_H+4 n_He, ignoring the small mass
defect in this bookkeeping definition. Electron Y_e=n_e/n_b is not
n_e/n_H. The temperature plot is a time-ordered parametric trajectory;
it is never sorted into a false single-valued function of temperature.

Preserve the original response floors (fraction 1e-7, temperature 0.01 K)
as claim context, not as a substitute for evolution error. New arithmetic
checks: charge/nuclei 1e-12 absolute normalized; decomposition 2e-12 for
fractions and 2e-8 K for temperature; symbolic identities exact;
original GL8 isotropic moments 2e-14. These check the consumer only and
do not relax any original physical or solver acceptance gate.
