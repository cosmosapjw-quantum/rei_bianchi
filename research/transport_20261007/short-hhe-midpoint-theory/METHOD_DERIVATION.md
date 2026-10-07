# Short H/He coupling: midpoint shared-owner transaction

Date: 2026-10-07. Status: proposed numerical method; this theory note reports no implementation or new history run.

## 1. Decision and scope

Use the four endpoint unknowns y1=(xHII,xHeII,xHeIII,w), with w in erg/H. Use a global arithmetic gas midpoint for nonphoto chemistry/thermal evolution. For radiation, use a segment-centered affine reconstruction of these same fraction/conserved variables, the actual background at the segment midpoint, and the unchanged positive frozen-rate characteristic kernel. All absorbed counts and absorbed energies come from that kernel; all nonphoto owners come from the same one midpoint RHS evaluation used by the residual.

This has classical local error O(h^3) on smooth event-free coupled intervals and second-order global convergence on a fixed finite characteristic grid under the regularity/stability assumptions below. At a step containing a finite-grid threshold event, gas derivatives may jump: only O(h^2) local error is generally guaranteed there. Finitely many such steps retain global O(h^2). No stiffness-uniform or spectral-refinement-uniform error bound is claimed.

This is a proposal for a separate numerical experiment. The existing BE results and failed history evidence remain unchanged. The microscopic provider, cross sections, source spectrum, case-A escape/primary-only closure, CHI/CUTOFF distinction, diagnostic floors/caps, original budgets, field tolerances, exact zeros and rejection policy are unchanged.

Existing evidence: the original BE lane passes its physical/number/energy/spectral checks but fails seven finest 4→8 temporal fields. The saved work_E ratio is 238.51722448645498, with successive observed orders 1.03090 and 1.02107. Independent continuous-source Radau completed, but its preceding reference-tightening pair is not established because the looser attempt failed its original number gate. These are evidence for proposing a higher-order method, not validation of this one.

## 2. Exact semidiscrete problem and units

Let s=ln(a), h=s1-s0>0, sm=(s0+s1)/2, and eta=ln(E)+s. On one fixed characteristic E(s)=exp(eta-s) eV. Let f_eta(s) be photon number per H per unit eta; integration uses the existing positive fixed eta weights. On an open segment whose source/threshold masks are constant,

  f' = q_s(s) - Lambda(s,y) f,        Lambda=sum_i lambda_i,
  lambda_i(s,y) = c n_abs_i(s,y) sigma_i(E(s))/H(s).

The absorbers are nHI=nH(1-xHII), nHeI=nHe(1-xHeII-xHeIII), nHeII=nHe xHeII. H denotes Hubble rate (s^-1). fHe=nHe/nH is constant for this prescribed FLRW background, mathematically; its existing binary64 evaluation convention must remain shared with material conversion.

The source is specified per proper second: Q_t=source_rate photons/H/s. Its E^-2 number spectrum, normalized on [Emin,Emax], becomes

  C = 1/Emin - 1/Emax,
  q_t(eta,s) = Q_t/[C E(s)],
  q_s(eta,s) = q_t/H(s),

inside the moving source window, and zero outside. eta is dimensionless, so q_s has photon/H per unit eta per unit s. A source specified directly per unit s would not receive the additional division by H. This experiment keeps the existing proper-time specification.

Let F_t(y,p) and W_t(y,p) be the zero-photo provider fraction_dt and w_dt. Define G=(F_t,W_t)/H. Photo number and energy derivatives are

  A_i' = integral_eta lambda_i f d eta,
  B_i' = integral_eta epsilon E(s) lambda_i f d eta,

with epsilon the existing eV-to-erg owner. The photo gas increments are

  P(A,B) = ( A_HI,
             (A_HeI-A_HeII)/fHe,
             A_HeII/fHe,
             sum_i [B_i-epsilon CHI_i A_i] ).

Thus y'=G+P(A',B'). No rate is obtained by dividing absorbed counts by an absorber fraction. Endpoint Gamma remains the direct c nH integral sigma_i f d eta, including zero-absorber boundary states.

## 3. Exact proposed residual and interface

Input: immutable cfg, fixed grid, immutable old State=(s0,y0,f0,ledgers), endpoint s1, endpoint trial y1. Return a private Evaluation containing residual, candidate radiation density/owners, and nonphoto owner increment. No state or cumulative ledger mutates during evaluation.

1. Require a resolved positive h and midpoint sm strictly inside (s0,s1). Evaluate p0=p(s0), p1=p(s1), pm=p(sm). Admit old endpoint, trial endpoint with p1, and all subsequently evaluated stages. Compute ym=(y0+y1)/2 in the four stored variables; derive Tm and ne from its unchanged EOS with pm. Do not average temperatures, proper thermal energy density, rates or endpoint EOS outputs.
2. Obtain r=igm_point_rhs(ym,pm,zero_photo) exactly once for the residual and nonphoto ledger. Let dtm=h/Hm. Construct MaterialOwners::stage(r,pm,h), unchanged formula including dtm/nHm for volume rates.
3. For each existing eta, retain exact source-entry, source-exit and HI/HeI/HeII CUTOFF times. Split exactly as the existing topology routine. For every surviving open segment [a,b], let delta=b-a, m=(a+b)/2, theta=(m-s0)/h and yseg=y0+theta*(y1-y0). Require 0<theta<1, resolved m, and admit yseg and its EOS/provider with pseg=p(m). Compute Eseg=exp(eta-m). Obtain lambda_i from the unchanged packet_opacity(yseg,Eseg,pseg.nH,pseg.nHe)/pseg.H. Obtain q_s from the original source expression using Eseg and pseg.H, and the exact source mask on this open segment.
4. Feed the carried incoming stock, q_s, lambda_i, delta and the existing exact-event energy anchor into V2::kernel. Never substitute analytic continuous-source counts/energy or midpoint heat for kernel owners. Carry the returned stock and final energy across all segments, and accumulate all positive eta-weighted owners A_i,B_i,Q_N,Q_E,redshift,outflow. Use the existing exact causal-front and support checks.
5. Form d=P(A,B) with the shared fHe convention. The exact nonlinear residual is

  R_HII   = y1[0]-y0[0]-A_HI-dtm*r.fraction_dt[0],
  R_HeII  = y1[1]-y0[1]-(A_HeI-A_HeII)/fHe-dtm*r.fraction_dt[1],
  R_HeIII = y1[2]-y0[2]-A_HeII/fHe-dtm*r.fraction_dt[2],
  R_w     = y1[3]-y0[3]-sum_i(B_i-epsilon CHI_i A_i)-dtm*r.w_dt.

6. Keep the existing Newton/finite-difference/line-search limits and tolerances. A finite-difference perturbation of y1 must rebuild ym, every yseg, and the whole private radiation transaction; the derivative must not freeze those stages. A perturbation is endpoint-domain/provider-admitted first, then all stage states are admitted. Only gas/provider inadmissibility permits the predeclared backward finite-difference alternative; event/underflow/kernel failures are not permissions for silent fallbacks. Check the final endpoint with p1 independently even when ym is admissible.
7. Accept only after the unchanged original number and full energy budgets pass on the assembled endpoint state and cumulative owners. Endpoint T, ne/nH, Tcmb, Gamma, redshift and inventory are evaluated at s1, not sm. Rejection preserves old state and every ledger exactly. No clipping, renormalization, automatic step retries or BE fallback.

A minimal signature change for radiation is a read-only gas path descriptor `(s0,s1,y0,y1)` plus cfg.background, rather than a single `(p,y)`. This is an interface specification, not source code. The nonphoto helper and photo_delta formulas do not need changes. Stage metadata should be testable without changing scientific outputs.

### Exact-event anchoring is mandatory

Use the event convention in `../short-hhe-coupling/CONTRACT_ADDENDUM_EVENT_ANCHOR.md`. An event is recognized only by exact stored binary64 equality with tau_i=eta-ln(CUTOFF_i). For a segment ending at such an event, E_start=CUTOFF_i/exp(-delta) is permitted only when multiplication by exp(-delta) returns CUTOFF_i exactly. An exact starting event uses its CUTOFF. Reject incompatible exact start/end anchors. Ordinary endpoints use exp(eta-a). Keep the same ordinary Eseg for sigma and q. Carry the kernel's final energy through aggregation and enforce the existing 2e-12 cross-segment energy-continuity check. Adjacent floats are not events; no epsilon, nextafter, clipping or post-hoc energy replacement is permitted.

## 4. Smooth local-order derivation, including radiation feedback

All expansions in this section are original derivations for the stated finite-dimensional semidiscrete problem. Assume one event-free transaction, C^2 coefficient functions/provider branch, an interior admitted solution, bounded derivatives independent of h, and a locally unique nonlinear solution. Write v0=y'(s0), g0=f'(s0)=q0-Lambda0 f0. Inserting the exact endpoint into the arithmetic stage gives

  ym = y0 + (h/2)v0 + O(h^2).

Hence, with total derivatives along the exact coupled solution,

  lambda_i* = lambda_i0 + (h/2) dot(lambda_i)0 + O(h^2),
  q* = q0 + (h/2) dot(q)0 + O(h^2).

The dot(lambda_i) term includes the gas evolution driven by radiation, explicit background evolution, and E'=-E. Freezing opacity at y0 would omit lambda_y v0 and create an O(h^2) local defect. Merely describing a midpoint background would not cure that.

The kernel solves the frozen inhomogeneous radiation equation exactly. Its average trajectory obeys

  integral_0^h fhat(t) dt = h f0 + (h^2/2) g0 + O(h^3).

The h^2 g0/2 term is essential: it includes photons born and absorbed during this step and the depletion of pre-existing photons. Replacing it with h f0 gives first-order gas coupling even if the gas opacity is at a midpoint. The kernel endpoint is

  f1 = f0 + h g0
       + (h^2/2)[dot(q)0-dot(Lambda)0 f0-Lambda0 g0] + O(h^3),

which is exactly the second-order Taylor expansion of f.

For each absorption count,

  A_i = h lambda_i0 f0
        + (h^2/2)[dot(lambda_i)0 f0+lambda_i0 g0] + O(h^3).

Using exact characteristic redshift inside the same kernel gives

  B_i = epsilon E0 { h lambda_i0 f0
        + (h^2/2)[dot(lambda_i)0 f0+lambda_i0 g0-lambda_i0 f0] } + O(h^3).

The last term is E'=-E. It is lost, for example, if absorbed energy is approximated using the starting energy epsilon E0 A_i. In contrast, epsilon E_mid A_i reproduces this quadratic term, but still differs from the exact shared kernel B_i at higher order and cannot replace it while preserving the same exact energy identity. These A/B expansions equal their continuous time integrals through h^2. The same derivation applies to Q_N, Q_E and redshift using their kernel trajectory integrals.

For the nonphoto term,

  h G(ym,sm) = h G0 + (h^2/2)[G_s+G_y v0]0 + O(h^3).

Every nonphoto diagnostic rate J is evaluated as the same midpoint integral h J(ym,pm)/(Hm nHm), with signs handled as in the provider; it likewise has O(h^3) local error on a smooth branch. Indicator-valued diagnostic owners can jump at branch transitions and are excluded from this smooth statement. Summing the photo and nonphoto expansions yields the exact coupled y1 expansion through h^2. No uncoupled-radiation assumption is used.

At h=0 the residual Jacobian with respect to y1 is I; for sufficiently small h it is I+O(h). The implicit-function argument therefore converts an O(h^3) residual defect into O(h^3) endpoint error on the local admitted solution branch. Classical stable accumulation on a fixed finite interval gives O(h^2) global error. This is not proof that the capped Newton solver finds that branch for arbitrary h.

### Segment-centered extension

For a smooth gas path throughout a macro-step, its affine interpolation satisfies

  y_lin(s)=y0+[(s-s0)/h](y1-y0)=y(s)+O(h^2)

uniformly on the step. On each event segment, this causes coefficient error O(h^2), hence an integrated defect O(delta h^2), while midpoint freezing of smooth explicit coefficients gives O(delta^3). Summing segments gives O(h^3), provided the coupled gas really remains C^2 across the macro-step. Exact splitting treats source-mask/cross-section jumps without sampling across them.

This statement is useful for prescribed smooth gas/background kernel tests. It must not be extended blindly to fully coupled gas at a finite-grid absorption jump; see section 6.

## 5. Exact shared-owner conservation

Within one frozen characteristic segment, define If=integral fhat ds and IE=integral epsilon E fhat ds. The unchanged kernel returns

  A_i=lambda_i If,  B_i=lambda_i IE,
  Q_N=q delta,      Q_E=integral epsilon E q ds,
  Z=IE,            N1=fhat(delta), U1=epsilon E1 N1.

It follows by integrating f'=q-Lambda f and U'=epsilon E q-sum_i epsilon E lambda_i f-U that

  N1-N0 + sum_i A_i - Q_N = 0,
  U1-U0 + sum_i B_i + Z - Q_E = 0.

Exact event splitting, source on/off, changing frozen coefficients from segment to segment, and positive eta quadrature preserve these telescoping identities. At HI outflow, transfer the final N and U to the same outflow owner, so the endpoint active stock vanishes without loss of either budget.

Binding per H is the existing linear functional

  b(y)=epsilon[CHI_H xHII + fHe CHI_HeI xHeII
              + fHe (CHI_HeI+CHI_HeII)xHeIII].

Therefore b(P_fraction(A))=sum_i epsilon CHI_i A_i, independently of where lambda was sampled. Summing the w residual and binding-weighted fraction residuals yields

  Delta(w+b) = sum_i B_i + dtm[W_t+b(F_t)]
               + R_w + b(R_fraction).

The zero-photo provider identity at the single shared stage is

  W_t+b(F_t) = -[escape_rate+expansion_work_rate-CMB_to_gas_rate]/nH.

MaterialOwners uses that very RHS and dtm/nHm, with cmb_reservoir=-integrated CMB_to_gas. Consequently

  Delta(w+b) + escape + work + cmb_reservoir - sum_i B_i
      = R_w+b(R_fraction),

and adding the radiation identity gives

  Delta(w+b+U_active)+U_out+Z+escape+work+cmb_reservoir-Q_E
      = R_w+b(R_fraction).

The photon number identity is independent of gas residual convergence; gas species and nonphoto event owners give complementary consistency checks:

  Delta xHII = A_HI+CI_HI-RR_HII + R_HII,
  fHe Delta xHeII = A_HeI-A_HeII+CI_HeI-CI_HeII-RR_HeII-DR+RR_HeIII+fHe R_HeII,
  fHe Delta xHeIII = A_HeII+CI_HeII-RR_HeIII+fHe R_HeIII.

Here the nonphoto event counts are per H from the same stage. H/He complements preserve nuclei algebraically. Charge is reconstructed from the fractions. The stored fHe is mathematically constant; finite-precision ratio differences must remain bounded by the original budget gates rather than normalized or repaired.

Thus conservation is algebraic at any admitted nonlinear trial, with the shown residual defect, and exact at the mathematical root. It does not prove time accuracy. With finite tolerances, the original independent energy gate may be tighter than the nominal nonlinear residual allowance and remains mandatory.

## 6. Event, source and regularity qualifications

### Why whole-step midpoint freezing is weaker on partial segments

Let smooth lambda(s)=lambda0+alpha(s-s0), f0>0, q=0, but absorption switches off at tau=s0+rho h, 0<rho<1. Freezing lambda at the whole-step midpoint gives optical depth rho h(lambda0+alpha h/2), whereas the exact active optical depth is lambda0 rho h+alpha rho^2 h^2/2. The defect is alpha rho(1-rho)h^2/2. Segment-midpoint freezing is exact for this linear prescribed lambda. A corresponding source-entry example has q(s) linear and an active interval [rho h,h]; the whole-step background midpoint can again leave O(h^2). This is why the segment-centered variant is preferred.

### A remaining fully coupled kink

At a discrete-node CUTOFF crossing, lambda_i f drops abruptly to zero for that species. Its contribution to y' has a jump proportional to that node's positive quadrature weight. y is continuous but generally only piecewise C^2. A single affine interpolation across the event can then differ from the true y by O(h), and the midpoint nonphoto rule also sees this kink. Both give O(h^2) event-step local defects. Source switching can likewise kink f'; it need not kink y' immediately when photo forcing depends on the continuous f, but the conservative general event estimate is retained.

For a fixed finite eta grid, the source and cutoff times are prescribed and finite, independent of time refinement. There are O(1) event-containing steps as h→0 for that fixed grid; smooth steps contribute O(h^3) each and event steps O(h^2) each. Under the same fixed-grid Lipschitz stability assumption, total error is O(h^2). Coincident known events count once; exact existing topology handles them. This reasoning does not yield a constant uniform in eta refinement. Establishing such a result would need control of summed jump strengths/total variation and a norm stable under quadrature refinement.

If a strict O(h^3) local statement is required at every coupled transaction, use the union of all characteristic event times as global gas-step boundaries, or introduce piecewise gas-stage unknowns at those boundaries. That is a more expensive separate variant, not a hidden requirement/change in the first bounded experiment.

The provider contains both continuous kinks and genuine jumps; they must not be conflated. Smooth-order claims require a fixed branch. A finite transverse crossing of a continuous Lipschitz rate kink can have O(h^2) local error and retain global2. In contrast, the DR onset at T/11605=0.8 switches from exact zero to a positive formula; K3/K5 switch between TINY and separate expressions, and K2 changes formula at 5500 K without enforced matching. An unresolved jump in a rate or a diagnostic owner can have O(h) local quadrature error, destroying global2 for that field even at one crossing. Diagnostic ci_floor, ce_cap and excluded_dr include on/off masks, so they may jump even when their associated physical rate is continuous. Locating and globally splitting such state-triggered events would be an additional numerical convention requiring its own contract; it is not silently included here.

The saved original B output rows span 30.000000000000004 K to at most 375.645869 K, and the saved Radau rows span 30 K to 375.653756 K. Thus the HeI CE cap diagnostic switch at 13179/69.07755278982137 K (approximately 190.785 K) is crossed. The associated physical CE coefficient is continuous with a kink, while ce_cap_HeI_E can have first-order event quadrature error. Its small magnitude does not make that order claim true. All 37 existing allowance tests remain mandatory; the order study must classify smooth physical/owner quantities separately from indicator diagnostics. Saved output endpoints alone do not certify the absence of other interior crossings in the new method; record stage/endpoint branch masks and distinguish observations from rigorous whole-interval bounds.

A direct coupled cutoff counterexample is supplied by independent review. Take f'=−k(1−x)f and x'=k(1−x)f before tau=alpha*h, q=0, then turn opacity off. Put v=k(1−x0)f0. With the global chord used at the active segment midpoint, numerical minus exact x1 is

  (1/2) k f0 v alpha^2(1-alpha) h^2 + O(h^3).

This is nonzero for interior alpha and positive stock. It verifies the remaining event-local order2 limitation even without any nonphoto term. No uniform claim at grazing, persistent, unresolved, or infinitely many provider crossings is made. Existing provider domain and floor/cap diagnostics stay active.

### Frozen-per-s kernel versus exact proper-time source

The kernel's q is held constant per unit s within each event segment. It is not an exact integration of the original constant-Q_t source through varying H and E. Midpoint q_s gives the correct source through second order; its Q_N and Q_E must stay internally shared with radiation. In particular do not overwrite Q_N with Q_t integral ds/H while retaining frozen-q radiation: that creates a ledger/state mismatch. A kernel supporting the exact varying q_s would be a separate consistent method with all owners replaced together.

Likewise dtm=h/H(sm) is midpoint quadrature for proper time, not exact Delta t. Holding H at the endpoint yields an O(h^2) defect for general proper-time processes; using different H factors for gas, opacity, source and owners gives a mismatched method. Radiation segments use their own pseg consistently, while the nonphoto integral uses its own global pm consistently.

## 7. Positivity, domain, stiffness and arithmetic

For nonnegative incoming f, q and lambda_i, exact frozen radiation is nonnegative at every interior time. Positive spectral quadrature preserves nonnegative photon and absorbed owners. With the exact support gate, E>=CUTOFF_i>CHI_i wherever lambda_i>0, hence B_i-epsilon CHI_i A_i>=0; this is checked directly by the existing code.

Admitted endpoint fractions lie in 0<=xHII<=1, xHeII>=0, xHeIII>=0, xHeII+xHeIII<=1; w>0. Their exact affine interpolants belong to the same convex physical domain. Floating point, EOS normal-intermediate requirements and provider validity still require explicit stage checks. The endpoint and segment provider domains may impose stricter requirements than convex fraction/w admission. No repair is permitted. Temperatures are derived, not extrapolated. In exact arithmetic with the constant fHe of this background, define D(theta)=1+fHe+xHII(theta)+fHe[xHeII(theta)+2 xHeIII(theta)]. Both w(theta) and positive D(theta) are affine, and T(theta)=2w(theta)/(3 kB D(theta)). Its derivative has constant-sign numerator, so T(theta) is monotone or constant and lies between the two endpoint temperatures. This bounds the accepted reconstructed stage path, not the unobserved exact continuous trajectory; explicit floating-point/provider checks still apply.

The midpoint gas method is not unconditionally positivity preserving or L-stable. For the limiting scalar gas sink u'=-k u,

  u1/u0=(1-kh/2)/(1+kh/2).

It becomes negative for kh>2 and tends to -1 as kh→infinity, so the method can oscillate or be rejected even when radiation remains positive. A-stability of scalar midpoint does not establish unconditional stability of the nonlinear mixed scheme. The full method is not automatically symplectic, time-reversible, or globally A-stable merely because one stage is midpoint. There is also a purely photo-induced loss of an admissible root. Let q=0, x'=k(1-x)f, f'=-x', u0=1-x0>0 and f0>u0, without cutoff or nonphoto terms. For one unsplit transaction the midpoint kernel gives D=x1-x0 satisfying

  D = f0 [1-exp(-kh(u0-D/2))].

The residual L(D)=D-f0[1-exp(-kh(u0-D/2))] is strictly increasing. At the physical endpoint D=u0 it is negative when kh>-(2/u0)ln(1-u0/f0), so there is no root in the physically allowed interval0<=D<=u0. The exact coupled ODE nevertheless stays physical. This is a direct shared-photo counterexample to unconditional gas positivity, beyond the scalar nonphoto sink example. Domain rejection is therefore part of the method, not merely a Newton inconvenience.

A stiffly damped alternative would require another specifically analyzed shared-owner scheme; no silent BE fallback is allowed.

Formal truncation order assumes exact roots/arithmetic. Fixed residual tolerances [1e-14,1e-14,1e-14,1e-26] can create a refinement floor; global solver defect may scale like the accumulated residuals through the stability factor. Do not loosen or secretly tighten them to manufacture observed order. Record actual residuals and certify an asymptotic window above roundoff/nonlinear/spectral errors. Underflow tails, unresolved interval midpoints, incompatible event anchors and failed line search remain explicit rejection outcomes. The new method may fail original gates, and that is a valid PARTIAL/FAIL result.

## 8. Minimal variants compared

- V0: global ym and pm for every radiation segment, with E evaluated at each segment midpoint. Smallest edit; smooth order2 and exact shared conservation. Has the demonstrated O(h^2) partial-event coefficient defect. Fixed-finite-event global2 remains possible, but local event claims must be limited.
- V1 (recommended): affine yseg, actual pseg at every segment midpoint; global ym/pm for all nonphoto terms and owners. Same four endpoint unknowns and unchanged kernel. Removes the artificial whole-step center offset, improves prescribed-smooth event integration, and retains the finite-grid coupled-kink qualification.
- V2: global union event splitting and V1 on every subinterval. Stronger smooth local-order justification on all open event-free pieces, higher solve count, and fresh resource/schedule implications. Optional future stricter experiment.
- Rejected shortcuts: old/endpoint gas opacity, initial-stock photo rate, midpoint counts paired with independently reconstructed heat, exact source ledger overwrite, endpoint work/CMB owners with midpoint w, averaged endpoint temperature, clipped midpoint/endpoints, unconstrained stiff-mode acceptance.

## 9. Sources and evidence

Local project behavior is established by the reviewed source and saved evidence in `../short-hhe-coupling/`, the V2 kernel in `../continuous-boundary-prototype-v2/`, and the baseline `../../../rust/rei_microphysics/`; no library API change is proposed. The derivations above are original algebra for those interfaces, not a theorem imported from a superficially similar exponential integrator.

For external context only: Hochbruck and Ostermann, *Exponential integrators*, Acta Numerica 19 (2010), section 2.8, describe midpoint freezing of both matrix and inhomogeneity for a non-autonomous linear system. Their later stiff-error theorems have additional hypotheses and are not asserted for this H/He scheme. Primary author/institution copy: https://publikationen.bibliothek.kit.edu/1000024914/1910360 (retrieved 2026-10-07).

The midpoint scalar stability function and A-/L-stability definitions can be checked in Innerberger and Praetorius, *Numerics of Differential Equations*, section 4.3 and Exercise 4.20, https://www.tuwien.at/index.php?eID=dumpFile&f=180707&t=f&token=b9f8c06bae2517b296a4cf40a43c26cd24d1ab06 (retrieved 2026-10-07). The positivity counterexample here is derived directly from the scalar residual.
