# Saved FULL005 pair: Thomson optical depth and visibility measure

## Result and scope

For two nonnegative saved electron-density reconstructions on the same expanding FLRW background, their electron-density difference norms give a uniform bound on every subinterval Thomson optical-depth difference. The same quantity bounds transmission differences and the total variation of the last-scattering probability measure, including the probability of no scattering. This connects the already computed full-overlap PL diagnostics to a directly interpretable radiative-transfer observable using compact inputs only.

The theorem below is exact under its stated assumptions. Substitution of the published binary64 norm summaries produces a conditional numerical envelope: those summaries carry numerical rounding but no outward-rounded norm enclosure. Report that distinction once in the result metadata. Solver convergence and continuum accuracy retain their existing HOLD status.

## R1–R4: frozen inputs, assumptions, and selection

- Source result commit: `0c3958d11d654513eb23cf462d5148e87ba6c9de`.
- Input: `research/flrw_full005_pair_diagnostics_20261016/actual_ncp_reuse_001/reused_actual_cached_001/results/full_pair_continuous_diagnostics.json`.
- Reference/candidate: `FLRW_FULL_Q512_001` / `FLRW_FULL_Q1024_001`.
- Coordinate: stored binary64 `x=ln(a)`; interval `[a,b]=[-3.044522437723423,-1.6094379124341003]`, width `1.4350845252893227`; 704041 union knots. Here `a,b` are interval endpoints, and the scale factor is `exp(x)`.
- Electron density is proper number density `n_e` in cm^-3, reconstructed piecewise linearly in this coordinate. Use the `ne_cm3` row, not `xe` or abundances as substitutes.
- Shared background `H(x)>0`, with `dx/dt=H`; its numerical/source identity must be explicitly supplied. A background parameter scenario may be evaluated with the status `CONDITIONAL_BACKGROUND_SCENARIO` if equality to the frozen FULL005 background has not been established.
- Background source intake at commit `c578683d995d375dbfc824cb080cb6b576d19348`, driver `Driver::new` and `Cosmology::hubble_flrw`, fixes `H0=67.4*1e5/3.0856775814913673e24 s^-1`, `Omega_m=.315`, `Omega_r=9.2e-5`, `Omega_Lambda=1-.315-9.2e-5`; both frozen configs have `q_ref=0`, `same_h=false`. Root's `intake/BACKGROUND_BINDING.json` records this input dependency. Preserve that receipt and these source excerpts.
- Both electron densities are assumed nonnegative. Convex PL interpolation preserves nonnegativity when every source knot is nonnegative. The compact pair-norm summaries do not independently establish knot positivity; applicability retains this theorem assumption unless a specific prior positivity receipt is observed and cited.
- Thomson scattering regime: photon energy `hbar*omega << m_e*c^2` and thermal electron energy `k_B*T_e << m_e*c^2`; the cold, energy-independent Thomson cross section is used. This is the line-of-sight scattering probability, with cosmological dilution already carried by proper `n_e`; no additional factor of scale factor multiplies `n_e dt`.
- Metric convention `(-,+,+,+)`. Keep `c`, `hbar`, `k_B`: `sigma_T=(8*pi/3)*(alpha*hbar/(m_e*c))^2`; `hbar,k_B` otherwise enter only the stated regime.
- Freeze the observable's nominal constants at `c=29979245800 cm/s`, `sigma_T=6.6524587051e-25 cm^2` (CODATA 2022 nominal value). The CODATA standard uncertainty is not a deterministic interval and is not silently added to the computational bound. If comparison with an existing solver's tau is later made, match its sigma_T first.

Published electron-density norms with measure `dx` are:

| Norm | Value | Unit |
|---|---:|---|
| `N_inf = sup abs(delta n)` | 2.7003617462766083e-10 | cm^-3 |
| `N_1 = integral abs(delta n) dx` | 9.797589160354307e-11 | cm^-3 |
| `N_2 = sqrt(integral delta n^2 dx)` | 1.054157221048039e-10 | cm^-3 |

The width is dimensionless; the norm units coincide. The saved Tgas result remains reused context and is not required by this derivation.

## R5: optical-depth bound

Set `K=c*sigma_T`, `w(x)=1/H(x)`, and `r_i(x)=K*w(x)*n_i(x)`. Units: `K` is cm^3/s, `w` is s, and `r_i` is the nonnegative dimensionless differential opacity. The suffix optical depth `tau_i(x,b)=integral_x^b r_i` has derivative `-r_i(x)`; the accumulated prefix optical depth has derivative `+r_i(x)`. For any measurable subinterval `J` in `[a,b]`,

`tau_i(J) = integral_J r_i(x) dx`.

The triangle inequality followed by Holder gives

`abs(delta tau(J)) <= integral_J abs(delta r) dx <= B`,

`B = K*min(N_1*W_inf, N_2*W_2, N_inf*W_1)`,

where `W_inf=sup w`, `W_1=integral w dx`, and `W_2=sqrt(integral w^2 dx)` over the full common interval. Each term is dimensionless. This uses the full-interval norms to bound every suffix/prefix/bin without reconstructing the histories.

For a supplied lower bound `H_min>0`, a simpler bound is `B_floor=K*N_1/H_min`. If the background is

`H(x)=H0*sqrt(Omega_r*exp(-4x)+Omega_m*exp(-3x)+Omega_Lambda)`

with nonnegative density parameters and positive H0, `w` is nondecreasing, hence `W_inf=w(b)` and right-endpoint Riemann sums bound both moments from above:

`U_p(N)=h*sum_{j=1}^N w(a+j*h)^p`, `h=(b-a)/N`, `W_1<=U_1`, `W_2<=sqrt(U_2)`.

Left sums `L_p` bracket the exact integral; `U_p-L_p=h*(w(b)^p-w(a)^p)`. This establishes a mathematical quadrature enclosure without treating a quadrature error estimate as a proof. Floating-point evaluation of these formulae is separately reported as numerical evaluation. For nonnegative terms with `Omega_m>0`, a second analytic upper kernel is `w(x)<=exp(3x/2)/(H0*sqrt(Omega_m))`, with exact integrals `2*(exp(3b/2)-exp(3a/2))/(3*H0*sqrt(Omega_m))` and squared norm `(exp(3b)-exp(3a))/(3*H0^2*Omega_m)`.

The executable contract uses 8192 panels and checks `(U_p-L_p)/U_p <= 0.001` separately for the raw moments `p=1,2`. The initial 4096-panel proposal exceeded this unchanged tolerance for `p=2` in the coder's compact probe. One panel-count correction preserves the algorithm, background, norm inputs, and tolerance; `CONTRACT_AMENDMENT.json` records the observation and authorization.

For any common subinterval, define transmission `S_i=exp(-tau_i)`. Since `tau_i>=0`,

`abs(S_1-S_2)=exp(-min(tau_1,tau_2))*(1-exp(-abs(delta tau))) <= q`,

`q=1-exp(-B)<=min(B,1)`.

Evaluate `q` as `-expm1(-B)` for stability. Also `exp(-B)<=S_1/S_2<=exp(B)`; if reporting a relative-change envelope use `expm1(B)` and identify the denominator. The absolute envelope is the primary output.

## Last-scattering distribution and bins

For each reconstruction define the probability measure on the interval plus a distinct no-scatter state `empty`:

`mu_i({empty})=exp[-integral_a^b r_i]`,

`d mu_i/dx = g_i(x)=r_i(x)*exp[-integral_x^b r_i]`.

This measure is normalized: integrating the derivative of `exp[-integral_x^b r_i]` gives continuous mass `1-mu_i({empty})`. For `a<=u<v<=b`, its bin probability is

`mu_i([u,v])=exp[-integral_v^b r_i]-exp[-integral_u^b r_i]`.

Construct two inhomogeneous Poisson processes from a shared process of intensity `min(r_1,r_2)` and independent excess processes with intensities `(r_1-r_2)_+`, `(r_2-r_1)_+`. Their marginal intensities are the required `r_i`. With probability `exp[-D]`, where `D=integral abs(r_1-r_2)`, no excess event occurs and the two last-event outcomes (including `empty`) coincide. The coupling inequality therefore proves

`TV(mu_1,mu_2) := sup_A abs(mu_1(A)-mu_2(A)) <= 1-exp(-D) <= q`.

Consequently every visibility bin, CDF value, and no-scatter probability differs by at most `q`. Equivalently, `integral abs(g_1-g_2) dx + abs(S_1-S_2) <= 2q`. For every bounded response `f` on the complete outcome space, `abs(E_1[f]-E_2[f]) <= (sup f-inf f)*q`. This is a useful bin/probability bound; no numerical pointwise visibility-density amplitude is required.

## R6–R8: discriminating checks and claim decision

1. Constant hazard against zero on width L: `D=r*L`, transmission difference and TV both equal `1-exp(-r*L)`. This verifies attainability of the probability bound in the stated class.
2. Cancellation: on `[0,1]`, reference hazard 1 and candidate hazard `2x` have equal total optical depth 1, while last-scattering distributions differ. At x=1/2 their CDFs, with `empty` ordered before the interval, differ by `exp(-3/4)-exp(-1/2)`. Thus endpoint signed tau difference alone loses visibility information. Here `D=1/2` gives the stated valid envelope.
3. Concentration: reference zero, candidate triangular hazard with base epsilon and area D. Its maximum is `2D/epsilon`; total variation remains `1-exp(-D)`. This demonstrates why a bound on a probability measure is not a pointwise density bound. This fixture only concerns the L1-only implication; the actual input also supplies Linf.
4. Zero difference gives zero B and q; cgs and SI evaluations agree when n, sigma, c are all converted consistently. Wrong mixing produces a known factor and must be rejected through units validation.
5. Background perturbation: if backgrounds differ, `delta(n/H)=delta n/H_1+n_2*(1/H_1-1/H_2)`. A zero delta n can then have nonzero delta tau. Shared-H is essential and must be recorded as observed or conditional.

The new result is a constructive conditional estimate and implementation target. No new strong no-go theorem or literature novelty claim is submitted; NG1–NG7 adoption is not applicable. The old PL diagnostics are reused unchanged. Independent review examines this derivation and the new compact calculation only.

## R9–R10: handoff and next action

Implement `THOMSON_PAIR_CONTRACT.json` against the local compact metrics and explicit background input. Measure only sandbox calculation cost in a new local receipt; carry the historical FULL005 debit and absolute deadline verbatim as archival provenance. This unit launches no NCP solver, renderer, saved-history analyzer, or remote job, and does not renew their allowance.

After scoped review, publish the conditional observable result as a side node depending on completed FULL005 PL diagnostics. Preserve the canonical source009 next action and full time/angular convergence HOLD. A future tighter result needs either local-in-x compact norm summaries or a justified outward enclosure of the current norms; neither is needed for this explicitly conditional evaluation.

## Source intake 2026-10-16

- Pinned repository input and reuse receipts above; current DAG at `fdfda0fec423ccb7175552c7dc066be93ce347e1`, `research/flrw_covariant_transport_20261015/NEXT_DAG.json`.
- NIST CODATA 2022 Thomson cross section, official table directly verified by root: https://physics.nist.gov/cuu/Constants/Table/allascii.txt ; nominal 6.6524587051e-29 m^2 and standard uncertainty 6.2e-38 m^2. Used only for the chosen observable constant.
- Optical-depth and visibility conventions directly verified by root in Wayne Hu's sources: https://background.uchicago.edu/~whu/tamm/webversion/node28.html and https://background.uchicago.edu/~whu/Courses/Ast282_06/ast282.pdf . The bounds and coupling proof here are directly derived from the specified intensity model.
