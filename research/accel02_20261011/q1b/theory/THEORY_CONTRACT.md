# Q1B0 fixed-q N/U closure and boundary contract

Status: **author-derived local contract, independent review pending; no coupled-ODE permission**. Host model identity is UNKNOWN. The user-selected Astra research harness is an instruction set, not evidence of the host model. This document continues the C08R1 rejection of Q1A; it does not repeat RUN002, EVENT003, Q0, G1 or G2. The source, conditional initial state, native H/He physics, geometry and scientific acceptance criteria remain frozen. Q1B is an explicit **numerical closure change** from point packets.

The derivations below use only the stated equations and probability identities. No published-method attribution, literature completeness claim, production-code execution or independent approval is asserted. Scope: non-tilted axisymmetric Bianchi I, first exercised in the FLRW geometry. CR, RCT, secondaries, diffuse reabsorption and geometry backreaction retain their prior OFF/HOLD status.

## 1. State and geometric convention

For one fixed initial angular ordinate, write

\[
E=R_c(t)q,\qquad \dot R_c=-\lambda_c R_c,
\quad \lambda_c=H+\sigma_{ij}n^i_cn^j_c
=H+s(3\mu_c^2-1).
\]

The reference-to-proper volume ratio is the dimensionless \(V=a_{\rm rel}^3\). The fixed angular weight is already included in \(F_c(q,t)\), the photon number per reference cm³ per \(d\ln q\). A fixed cell has edges \(a=q_L>0,q_R>a\). Define

\[
N_c=\int F_c\,d\ln q,\qquad Q_c=\int qF_c\,d\ln q,
\qquad U_c=R_cQ_c.
\]

**Stored variables are N and U.** N has units cm⁻³ referred to the initial volume; Q and U have units eV cm⁻³ in that same reference convention. Reconstruct Q=U/R only at the current time. Do not replace N by U divided by one representative photon energy. All angle sums retain their own R and λ. The finite angular sum of \(w_cR_c^{-3}\) need not equal V away from FLRW.

For monotonically redshifting directions, \(\lambda_c\ge0\), the permissible photon support is

\[
[a,b_c(t)],\qquad b_c(t)=\min(q_R,E_{\max}/R_c(t)),
\quad E_{\max}=50000\ {\rm eV}.
\]

If b≤a the cell is dormant and empty. This restriction excludes photons that have never entered the source/initial band. It does **not** remove photons with current E<10 eV: 10 eV is the source lower cutoff, not a photon deletion boundary. A growing permissible support does not assert that the exact spectrum fills the support; doing so is the declared power-law closure.

**Validity boundary:** the current cap Emax/R is not correct for a direction that later blueshifts. In that extension, historical reachable q support must include initial support and \(\sup_{t'\le t}E_{\max}/R_c(t')\); photons may subsequently have E>Emax, beyond the current provider's admitted band. That extension requires a new support/provider contract. It is not silently enabled here. The FLRW candidate satisfies the monotone restriction.

## 2. One operator for photons, gas and counters

For absorber α with current proper number density \(n_\alpha\), use the unchanged native cross section and define

\[
K_{0\alpha c}=c\int\sigma_\alpha(R_cq)F_c\,d\ln q,
\qquad K_{1\alpha c}=c\int q\sigma_\alpha(R_cq)F_c\,d\ln q.
\]

K0 has units s⁻¹; K1 has units eV s⁻¹. The moment equations are

\[
\dot N_c=S_{0c}-\sum_\alpha n_\alpha K_{0\alpha c},
\quad
\dot U_c=R_cS_{1c}-\sum_\alpha n_\alpha R_cK_{1\alpha c}
-\lambda_cU_c.
\]

The paired native gas inputs are

\[
\Gamma_\alpha=V^{-1}\sum_cK_{0\alpha c},\qquad
\mathcal H_\alpha={\epsilon_{\rm eV}\over V}
\sum_c(R_cK_{1\alpha c}-\chi_\alpha K_{0\alpha c}),
\]

where \(\epsilon_{\rm eV}\) converts eV to erg, and \(\mathcal H\) is heat per absorber per second. Never divide a rate by \(n_\alpha\); Γ and heat remain defined at zero absorber density. Native chemical χ and native cross-section thresholds remain distinct unchanged constants.

The same K values give reference-volume chemical power \(\epsilon_{\rm eV}\chi_\alpha n_\alpha K_0\), heat \(\epsilon_{\rm eV}n_\alpha(RK_1-\chi_\alpha K_0)\), and photon loss \(-\epsilon_{\rm eV}n_\alpha RK_1\). Their sum is exactly zero algebraically. The source-number, absorbed-number, source-energy and radiation-work counter derivatives are respectively

\[
\sum_c S_{0c},\quad
\sum_{c,\alpha}n_\alpha K_{0\alpha c},\quad
\epsilon_{\rm eV}\sum_cR_cS_{1c},\quad
\epsilon_{\rm eV}\sum_c\lambda_cU_c.
\]

Consequently \(\sum N-N_{\rm emit}+N_{\rm abs}\) is a linear conserved ledger, and the photon/gas energy transfer and expansion work pair with linear stored U. This identity does not prove a floating-point global ledger tolerance. Existing thermal work, Case-A escape and signed CMB-exchange counters retain their previous meanings and signs. No normalization change is authorized.

## 3. Exact declared source moments and initial state

For current proper source \(s_{\log}(E,z)\), put

\[
E_l=\max(R_cq_L,10),\quad E_h=\min(R_cq_R,50000),
\]
\[
S_{0c}=w_cR_c^{-3}\int_{E_l}^{E_h}s_{\log}\,d\ln E,
\qquad
S_{1c}=w_cR_c^{-4}\int_{E_l}^{E_h}E s_{\log}\,d\ln E.
\]

Both are exactly zero for Eh≤El. The factor R⁻³ follows from V times the initial-to-current angular Jacobian \(d\Omega/d\Omega_0=(VR^3)^{-1}\); q=E/R gives the additional R⁻¹ in S1. The energy-state source is **R S1**, not S1. Integrate the already pinned provider's declared interpolation, including its native jumps; do not reinterpret a jump or replace it with a smoothed source.

At the initial time R=1, integrate the already pinned UVB to obtain N and Q separately. Initial UVB is not an ongoing source. Source/IC cell checks compare against saved accepted references; they do not rerun old reference-generation work. Exact source moments are exact only for the declared interpolation, not for the physical radiation continuum.

## 4. Positive power-law reconstruction on nonzero support

For a<b, N>0 and a<Q/N<b, choose the unique finite p such that

\[
F(q)=N\rho_p(q),\quad
\rho_p={ (q/q_*)^p\over Z_0(p)},\quad
Z_k(p)=\int_a^b q^k(q/q_*)^p\,d\ln q,
\quad m={Q\over N}={Z_1(p)\over Z_0(p)}.
\]

q* is a fixed conditioning scale and has no physical effect. Strict monotonicity follows from
\(dm/dp=\operatorname{Cov}_p(q,\ln(q/q_*))>0\). Hence p exists uniquely for every strict interior mean. Stable expm1/log expressions and explicit limits at p=0 and p=−1 are required. A large finite p is not an exact endpoint.

Writing L=ln(b/a), the explicit formulas are
\[
m(p)=a\,{p\over p+1}\,{\operatorname{expm1}[(p+1)L]\over
\operatorname{expm1}(pL)},\quad p\ne0,-1;\qquad
m(0)={b-a\over L},\quad m(-1)={abL\over b-a}.
\]
The formula needs scaled/logarithmic evaluation when either exponent is large; its mathematical form is not an overflow-safe implementation by itself.

For any fixed-time kernel g(q), define \(A_g=N\langle g\rangle_p\). Then

\[
D_g={\operatorname{Cov}_p(g,\ln(q/q_*))\over
\operatorname{Cov}_p(q,\ln(q/q_*))},\quad
\left.{\partial A_g\over\partial N}\right|_U
=\langle g\rangle_p-mD_g,\quad
\left.{\partial A_g\over\partial U}\right|_N={D_g\over R}.
\]

Use g=cσ for K0 and g=cqσ for K1, with the same positive, threshold-split quadrature. These are fixed-time state derivatives; explicit support/geometry time dependence is not an extra term in this Jacobian. Density and gas response derivatives must still be included by the native adapter. The old point-packet diagonal photon Jacobian is inapplicable.

## 5. Empty origin: rates exist, one ordinary Jacobian generally does not

The closed realizability cone is
\(N\ge0,\;RaN\le U\le RbN\), with N=0 requiring U=0. At (N,U)=(0,0), define K0=K1=0 exactly. The physical RHS is well defined: \((\dot N,\dot U)=(S_0,RS_1)\). Source activity does not manufacture an absorption rate.

For an admissible cone direction h=(hN,hU), hN>0,

\[
\lim_{\varepsilon\downarrow0}{A_g(\varepsilon h_N,
\varepsilon h_U)-A_g(0,0)\over\varepsilon}
=h_N\left\langle g\right\rangle_{p(h_U/(Rh_N))}.
\]

For h=0 the derivative is zero. In general the expression is nonlinear in h, so it is a **one-sided cone-direction derivative, not a Fréchet derivative or one reusable matrix column**. A linear matrix exists only in special cases where \(\langle g\rangle_p\) is affine in m. In particular constant or affine kernels are not evidence that native nonlinear opacity admits that matrix. The derivative of the absorption term also includes absorber-density factors; derivatives with respect to densities vanish at the empty photon state, but photon-direction derivatives need not vanish.

An exact counterexample uses a=1, b=2, R=1 and g=q². Directions h₁=(1,1) and h₂=(1,2) have endpoint derivatives 1 and 4. Their sum h₁+h₂=(2,3) has mean 3/2 and p=1, giving derivative \(2\langle q^2\rangle=14/3\), not 5. The nonadditivity is −1/3. This is an analytic smooth-kernel counterexample; no native threshold pathology is needed.

Selected local API behavior: `EMPTY` returns exact zero rates and `NO_JAC_AT_EMPTY`. A caller may request a directional derivative only with a supplied admissible direction; its response must be labelled `CONE_DIRECTIONAL_ONLY`. No mean floor, positive N floor, clipping, arbitrary p, artificial photons, or fabricated zero Jacobian is permitted. A source-only predictor supplies a direction; it does not prove a general Jacobian.

## 6. Source entry, zero width and cone-preserving stages

At a newly entered upper source front b=a, a continuous bounded source supplies zero measure at that instant. The admissible stored state is exactly N=U=0; return `ZERO_WIDTH_EMPTY` and zero moments. A nonzero state on a collapsed dormant support is inconsistent with this continuous-source/IC contract and must be rejected. This is distinct from a mathematical monoenergetic distribution supplied as a new physical input, which is not authorized here.

For a monotone smooth crossing at t0 with λ0>0 and finite upper-band source value, write τ=t−t0 and \(A_0=wR_0^{-3}s_{\log}(E_{\max}^{-},z_0)\). To leading order,

\[
b-a=a\lambda_0\tau+O(\tau^2),\quad
S_0=A_0\lambda_0\tau+O(\tau^2),
\]
\[
N={A_0\lambda_0\over2}\tau^2+O(\tau^3),\quad
Q-aN={A_0a\lambda_0^2\over6}\tau^3+O(\tau^4),
\quad {Q\over N}=a+{a\lambda_0\over3}\tau+O(\tau^2).
\]

These asymptotics include finite absorption in the remainders; they assume a smooth nonzero source trace and a genuine expanding crossing. If A0=0 or λ0=0, no division by this expression is permitted and a different leading order applies. The instantaneous source mean approaches a+(b−a)/2, whereas accumulated photons approach a+(b−a)/3. Therefore seeding a new cell at an arbitrary representative point—even the instantaneous source mean—does not reproduce its accumulated first moment. This asymptotic is an analytic check, **not a selected approximate startup algorithm**.

Continuous cone invariance follows in Q coordinates. At Q=aN, the absorption contribution to \(\dot Q-a\dot N\) vanishes and the source gives S1−aS0≥0. At Q=bN, absorption likewise cancels from \(d(bN-Q)/dt\), leaving \(\dot bN+bS_0-S_1\ge0\). At N=0, \(\dot N=S_0\ge0\). These statements require nonnegative opacity/source and \(\dot b\ge0\).

They do **not** prove that unconstrained BDF predictors, Newton trials or accepted steps remain in the cone. The solver interface must distinguish an inadmissible trial stage from a physical accepted-state violation. `NONREALIZABLE_STAGE` must be rejected/backtracked by a demonstrated solver strategy; it must never be repaired by changing N or U. Generic SciPy BDF calling a function that rejects out-of-cone stages is not, by itself, such a strategy.

A possible future startup is to form strictly positive initial moments by integrating the genuine source over a finite first step, then solve the absorption/gas stage with an admissible method. Any source-first splitting or special start carries truncation error, must conserve paired counters, must be included in temporal comparison and must be justified against the stiff terms. It is **not selected or implemented by this document**. The current local API can be implemented immediately; full ODE remains blocked on an actual source-entry and nonlinear-stage method.

## 7. Endpoint limits and discontinuous kernels

At N>0 and m=a or b, the power-law family tends weakly to a Dirac measure at that endpoint. For a continuous g, \(A_g=Ng(a)\) or Ng(b). If g is differentiable on the support side, the one-sided interior derivative is Dg→g′(endpoint), with the corresponding N/U columns from section 4. Evaluate this analytic limit; do not request infinite p from an ordinary exponential routine.

Native cross sections are not continuous at ionization thresholds. For an endpoint coincident with such a threshold, weak convergence does not identify the integral of the discontinuous kernel. The support-interior power-law limit uses **g(a+) at a lower endpoint, or g(b−) at an upper endpoint**. Evaluating a literal Dirac atom with the provider's exact-equality branch can give a different answer. This issue is a numerical endpoint extension, not permission to modify the provider.

Required API behavior is `ENDPOINT_LIMIT` plus an explicit `INTERIOR_ONE_SIDED_TRACE` request. If the unchanged provider adapter can establish that trace, return the limit rate with its side and provenance. Otherwise return `ENDPOINT_TRACE_REQUIRED`, with no fabricated K values. At a threshold coincidence the ordinary derivative status is `NO_JAC_AT_THRESHOLD_ENDPOINT` even when the limit rate is known. A nextafter value is not automatically a verified analytic trace. Moving an endpoint across a threshold is an event to be specified by the later solver contract; no silent cross-threshold derivative is allowed.

## 8. Minimal implementable local API and error vocabulary

The following interfaces are a contract, not a claim of existing production code:

```text
classify_state(a, q_right, R, N, U, support_history)
  -> DORMANT_EMPTY | ZERO_WIDTH_EMPTY | EMPTY | INTERIOR
     | LOWER_ENDPOINT | UPPER_ENDPOINT | NONREALIZABLE

source_moments(time, cell, fixed_angle, pinned_provider)
  -> S0, S1, state_source=(S0,R*S1), support, provider_identity

reconstruct(classified_state)
  -> finite_power_law(p, normalization) | zero_measure
     | endpoint_limit(side) | error

opacity_moments(reconstruction, native_sigma, fixed_time_geometry)
  -> K0[3], K1[3], trace_metadata, quadrature_metadata
     | ENDPOINT_TRACE_REQUIRED

state_jacobian(reconstruction, opacity_moments)
  -> interior_J | smooth_endpoint_one_sided_J
     | NO_JAC_AT_EMPTY | NO_JAC_AT_ZERO_WIDTH
     | NO_JAC_AT_THRESHOLD_ENDPOINT

directional_opacity_at_empty(admissible_direction, same_inputs)
  -> dK0[3], dK1[3], status=CONE_DIRECTIONAL_ONLY
```

Inputs must be finite and use positive R, positive fixed cell edges and nonnegative angular weights. Classification has no hidden tolerance that changes state. Floating tolerances may quantify a residual for diagnosis but may not convert a negative/invalid stored state into an accepted one. Empty-rate evaluation need not request a native cross section at an unoccupied E>50keV point. Jacobian status must be propagated to the caller, not converted into zero columns. Units, source history, grid identity and support policy are versioned inputs.

## 9. Alternative if the empty-origin Jacobian remains the blocker

One feasible alternative is the endpoint measure on a<b,

\[
F\,d\ln q=A\delta_a+B\delta_b,\quad
A={bN-Q\over b-a},\quad B={Q-aN\over b-a}.
\]

It is nonnegative exactly on the cone and has exact N/Q moments. For a fixed kernel convention, \(A_g=A g(a)+B g(b)\) is linear in N,U even at the origin. Under support growth and source/opacity-free evolution, \(\dot A=\dot bB/(b-a)\), \(\dot B=-\dot bB/(b-a)\), preserving positivity. This does not eliminate the b=a startup singularity or threshold-point convention. It is also a different, endpoint-biased numerical closure and must earn independent local and spectral validation. **It is not selected, not implemented here, and not interchangeable with the power-law closure's tests.**

## 10. Decision and remaining gates

Q1B0 can unblock source/IC moment implementation and a power-law reconstruction/opacity **local** API. The exact empty-origin behavior, zero-width rejection, endpoint trace requirements and failure vocabulary are now specified. It does not claim that the full implicit solver is ready.

Required before a new full interval:

1. Positive moment reconstruction and new source/IC checks against saved references, including dormant/partial/entered support.
2. Native, threshold-split K0/K1 and the endpoint trace adapter; interior and admissible-direction Jacobian tests.
3. A versioned integrated-photo native adapter that uses exactly those paired rates and counters, with unchanged gas microphysics.
4. A demonstrated source-entry and admissible nonlinear-stage strategy, including its temporal error and stiff behavior.
5. Durable checkpoint recovery preserving state, counters, source/grid/provider identities, retained history and explicit solver-restart semantics.
6. Independent local decision, followed only then by the unchanged whole-interval temporal/spectral/ledger/domain tests.

The protected criteria remain: mean redshift 15.9→4; nine-field time comparison 2×10⁻⁶; energy/initial-energy and photon-number/initial-nH ledgers 10⁻⁹; geometry 10⁻¹¹; all 24 spectral fields 10⁻³ on 129 and 65 epoch sets with their own fine amplitudes; strict finite/physical domains and no clipping. Old N4 reduced evidence remains scoped; a new native BASS receiver is still HOLD.
