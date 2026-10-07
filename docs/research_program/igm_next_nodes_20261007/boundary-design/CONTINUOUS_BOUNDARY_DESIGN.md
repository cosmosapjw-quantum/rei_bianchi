# Continuous lower-boundary radiation design

Research/design only · 2026-10-07 UTC

## Verdict and scope

The minimal credible next representation is a **positive two-moment spectral panel state with an event-local, continuously cut active interval**, or its equivalent two-moment finite-volume formulation in physical log energy. A panel owns photon number and comoving photon energy, not whole stocks attached to Gauss nodes. The lower boundary removes a continuously swept measure. All absorption, emitted source, gas heating, redshift, and outflow are computed from that same measure and committed together.

A one-moment partial-node weighting fix is insufficient: the number sink and energy sink have different spectral averages. Even a perfectly smooth outflow curve cannot fix independently mis-evolved radiation, gas, or owner ledgers. No implementation or convergence claim is made here. Fixed physical inputs, original 37 fields, original thresholds, no source renormalization, no state clipping, no error-budget relaxation, immutable baseline, and existing negative results remain binding.

## 1. Source evidence

- `tools/igm_continuous_reference.py`, especially `spectral_grid`, `source_derivative`, `solve_history`, `make_row`, and lines 247–253: whole surviving node stock enters out_N/out_E at its HI crossing, then its log stock becomes -infinity. This source is byte-identical to the pilot baseline (SHA-256 `3fa6a91a3239238bef49f183d906dfcfc9034b60e079f7fd14c144c02293f429`).
- `tools/igm_reference.py`: photon owners are constructed once in `evaluate`; each owner feeds photon loss, gas ionization, binding energy and excess heat. CHI = [13.598434599702, 24.587389011, 54.41776] eV differs deliberately from fit CUTOFF = [13.60, 24.59, 54.42] eV. These must not be conflated.
- `rust/rei_microphysics/src/igm_continuous.rs:459–490`: the native method has the same whole-node export, with redshift before/after the midpoint gas/source stage. This existing split transaction cannot simply receive smoothed reporting fields.
- `../long-flrw/FIELD_SUMMARY.csv`: 8/37 failures in p64 versus p128: out_E 1362.1124, out_N 335.1653, Gamma_heii 2.2769, Gamma_hei 1.8621, Gamma_hi 1.8389, Eactive 1.7831, x_heii 1.2292, Nactive 1.2025 times the original allowance.
- `../long-flrw/OUTFLOW_DIAGNOSTICS.json`: out_E = 13.6 EV × out_N to roundoff. An isolated p128 exit at row 187 contains 1.917476835e-6 photons/H; its energy jump is 771.724 current allowances. Source leaves at 13.7 eV, ln(13.7/13.6)=0.007326040092... earlier in s. Case-A escape_E is a different channel.
- the independently reviewed pilot assessment: both complete 273-row references admitted individually; original accepted-state number/energy ratios p64 0.03624596/0.01155373, p128 0.08552141/0.02731410. Internal conservation does not establish grid convergence.

At row 188 the pilot source-number difference is approximately 4.04e-8/H versus an outflow difference of -1.304e-5/H; at row 271 approximately 3.09e-8/H versus -9.562e-4/H, while the active stock nearly cancels the outflow difference. At the energy-onset worst row 185 the upstream source difference is not negligible. These pilot diagnostics help localize the bookkeeping mode but do not isolate the causal contribution of each upstream discretization.

This establishes the discrete export mechanism and large observed jumps. It does not causally isolate source, absorption or thermal errors, and does not prove every spectral error will disappear after this change.

## 2. Continuum definition and boundary law

Let s = ln(a), eta = s + ln(E/eV), E(eta,s) = exp(eta-s) in eV, and f(eta,s) >= 0 be photons per H per d eta. Write epsilon = 1.602176634e-12 erg/eV and Ec = 13.6 eV. The tracked interval is D(s) = [b(s), eta_max], intersected with the existing finite eta domain, where b(s)=s+ln(Ec). The lower trace is from the active/high-energy side. Before b reaches the domain, its boundary flux is zero.

For species i,

    lambda_i(eta,s) = c nH(s) a_i(gas) sigma_i(E) / H(s),
    a_i = (1-xHII, fHe*(1-xHeII-xHeIII), fHe*xHeII),
    lambda = sum_i lambda_i,
    partial_s f = q - lambda*f,
    q = j_total*exp(s-eta)/(C*H(s)) * 1[Emin < E < Emax],
    C = 1/Emin - 1/Emax.

There is no extra a^3 dilution in this per-H density. All rates here are per unit s; the matching proper-time boundary flux is H times the displayed flux.

Define N = integral_D f d eta and U = epsilon integral_D E f d eta. Reynolds transport at b'(s)=1 gives

    F_N(s) = f(b(s)+,s),
    F_E(s) = epsilon*Ec*F_N(s),
    N' = Q_N(active) - sum_i A_Ni - F_N,
    U' = Q_E(active) - sum_i B_i - U - F_E,
    A_Ni = integral_D lambda_i*f d eta,
    B_i = epsilon integral_D E*lambda_i*f d eta.

The -U term is cosmological redshift: redshift_E' = U. Binding deposition is epsilon*sum_i CHI_i*A_Ni; photoheat is sum_i(B_i-epsilon*CHI_i*A_Ni). Ec governs outflow; CHI governs material binding and heat. At the present Emin=13.7>Ec, direct source outflow is zero. If an already-supported fixture places source below Ec, emitted ledgers include the full source and those below-band source photons go directly to outflow at their actual emission energies; then out_E=epsilon*Ec*out_N no longer holds for the combined channel.

With zero initial radiation, the existing global identities remain

    N + sum_i abs_i + out_N - emitted_N = 0,
    (w-w0)+(binding-binding0)+U+escape_E+work_E
      +cmb_reservoir_E+redshift_E+out_E-emitted_E = 0.

For an analytic control with nonzero initial photons, subtract N0 and U0 respectively. Such controls have a separately labeled initial-inventory identity and high-precision reference; report their binary64 residuals, but do not silently amend or claim the production comparator, which is frozen for the initially empty fixture. Zero-initial source controls use its original budgets unchanged. These are independent audits of one shared evolution, never definitions used to repair an owner.

## 3. Preferred panel moments and exact source integrals

For a fixed comoving panel [etaL,etaR], define its surviving occupied support I(s)=[L(s),R(s)]. In a fully illuminated panel L=max(etaL,b(s)) and R=etaR. In this initially empty, constant finite-source fixture, the occupied high-eta front is r_source(s)=s+ln(Emax), so R=min(etaR,r_source(s)); no photons may be reconstructed ahead of that front. More general analytic controls retain the union of their declared initial and source-reachable supports rather than applying this fixture-specific cap. Store

    N_j = integral_I f d eta,
    M_j = integral_I exp(eta)*f d eta,
    U_j = epsilon*exp(-s)*M_j.

M_j is a comoving energy moment. It avoids the unavoidable time-dependent energy weight in the state and exposes redshift analytically. For fully illuminated support,

    N_j' = Q_Nj - sum_i A_Nij - delta_j*F_N,
    M_j' = Q_Mj - sum_i A_Mij - delta_j*exp(b)*F_N,
    A_Mij = integral_I exp(eta)*lambda_i*f d eta.

Here delta_j selects the unique cut panel; at a panel endpoint choose the right/high-energy panel trace. For fixed internal eta faces there is no transport, and only the lower moving face contributes. Empty support has exactly zero moments by geometry, not by an extinction threshold. In a source-front panel the general Reynolds formula also has +R'(s)*f(R-,s) in N' and +R'(s)*exp(R)*f(R-,s) in M'. The exact newly born front has zero trace, so these terms vanish. A reconstruction that imposes a nonzero trace there is invalid: either it creates a fictitious incoming flux, or it no longer realizes the displayed moving-support evolution.

The source support intersection is [Lq,Rq]=I intersect [s+ln(Emin),s+ln(Emax)]. For nonempty overlap,

    Q_Nj = j_total*exp(s)/(C*H) * (exp(-Lq)-exp(-Rq)),
    Q_Mj = j_total*exp(s)/(C*H) * (Rq-Lq),
    Q_Ej = epsilon*exp(-s)*Q_Mj.

These are the actual panel source integrals. The source used by the state and the emitted ledgers is identical. They are not an analytic total substituted for an independently discretized source, and no finite sum of weights is renormalized.

Two moments require two radiation degrees of freedom per panel, the same count as existing Gauss2. For a fully illuminated panel, an explicit positive closure example is

    f_j(eta) = N_j * exp(beta_j*(eta-L)) / Z(beta_j),
    Z(beta) = integral_L^R exp(beta*(eta-L)) d eta,
    M_j/N_j = integral_L^R exp(eta)*exp(beta*(eta-L)) d eta / Z(beta).

For L<R, the ratio is strictly increasing in beta and spans (exp(L),exp(R)). This follows because its derivative is Cov(exp(eta),eta)>0. Thus an interior realizable moment pair has a unique positive power-law-in-energy reconstruction. Solve in stable log/expm1 forms, including beta=0 and beta=-1 limits. For an authoritative exactly empty panel, N=0 requires M=0; an IEEE-underflowed readout is not authoritative emptiness and retains its log-scale moments and tail bounds. Endpoint-mean limits are atomic measures, not finite beta values; preserve an explicitly declared limiting representation or reject/refine, never replace the mean by a clipped interior value. The solver for this closure remains an implementation task.

At an advancing source-created front, use a declared positive base weight that vanishes at that front, for example f=N*w(eta)*exp(beta*(eta-L))/Z_w with w(eta)=(R-eta)/(R-L). This is a shape constraint on every interior point approaching R, not reassignment of a single endpoint value: f(R-)=0 for every finite beta. Under the probability density proportional to w*exp(beta*eta), d(M/N)/d beta=Cov(exp(eta),eta)>0 because w>0 throughout the open interval and both functions are strictly increasing. As beta tends to minus/plus infinity the distribution concentrates at L/R respectively, despite the finite-order zero of w at R; the mean therefore spans exactly (exp(L),exp(R)). Thus every interior realizable pair has one finite-beta positive front-vanishing reconstruction. In scaled coordinates y=(eta-L)/(R-L), evaluate the base factor as 1-y, with stable integrals and endpoint limits. The atomic limiting means remain a separate representation/admission case, not a reason to violate the zero-trace constraint. The support and zero-trace constraint are physical/numerical state metadata, not inferred from two moments alone. Its integrated positive kernel and moment projection must agree on that metadata. A source-off period or nonzero initial support must not be handled by blindly applying the constant-source front formula.

Amplitude is fixed by the stored physical N moment; this is an explicit conservative reconstruction, not source-spectrum renormalization. A new representation/version must record that closure. It is a numerical approximation to spectral shape, not new physics.

Moment realizability requires N>=0 and exp(L)*N <= M <= exp(R)*N. Positivity of the reconstructed density does not make arbitrary Radau/BDF moment updates positivity preserving. Every accepted update must pass realizability, all gas-domain checks, original conservation budgets, and quadrature admission; otherwise reject/refine. No projection or clipping is permitted. Near vanishing cut-cell width, do not divide a residual stock by a tiny width and hope it remains stable; use the integrated sweep below, or an equivalent coordinate-regularized method with a proved empty-cell limit.

## 4. Event-local swept-panel update

This is a constructive way to obtain positive moments and continuous outflow while retaining stiff, positive characteristic solves. Given a positive reconstructed f0(eta) at s0, define the local characteristic solution until its exact cutoff time tau(eta)=eta-ln(Ec):

    f*(eta,u) = f0(eta)*exp(-integral_s0^u lambda dv)
               + integral_s0^u q(eta,v)*exp(-integral_v^u lambda dw) dv.

It is evaluated only while active; photons not initially present have f0=0. Split each characteristic in time at its true source entry/leave and each channel crossing. End-of-step state integrates f*(eta,s1) over eta>b(s1). The cutoff export is

    Delta out_N = integral_[b(s0),b(s1)] f*(eta,tau(eta)-) d eta,
    Delta out_E = epsilon*Ec*Delta out_N.

Intersect all intervals with actual domain/panel supports. The export integrates a swept strip, not an entire numerical node. Source photons born and exported within one step are included automatically through f*. The corresponding absorption and redshift integrals use the very same characteristic history, truncated at min(s1,tau):

    Delta A_Ni = double_integral lambda_i*f* du d eta,
    Delta B_i = epsilon*double_integral exp(eta-u)*lambda_i*f* du d eta,
    Delta R = epsilon*double_integral exp(eta-u)*f* du d eta.

Compute emitted source moments with the same local time/source approximation. The identities are

    N1 + sum_i Delta A_Ni + Delta out_N = N0 + Delta Q_N,
    U1 + sum_i Delta B_i + Delta R + Delta out_E = U0 + Delta Q_E.

Continuous outflow follows by integrating a locally integrable density over a continuously moving strip; panel-edge trace jumps can create derivative kinks but not stock jumps. A truly atomic physical initial spectrum is an exception and legitimately yields an exit jump; this fixture's continuous source does not require pretending atoms are smooth.

After computing positive endpoint moments, reconstruct f1 from those moments. The projection must preserve causal occupied support and the zero trace of any newly born moving source front. This moment-preserving projection must be explicit and measured; it changes higher spectral moments and therefore requires spectral refinement. It must not change N, M, any ledger, or the physical source normalization. Split/merge operations likewise preserve both moments and maintain positivity, or fail admission.

## 5. Analytic positive local kernel for a first prototype

For one characteristic subinterval of width h with nonnegative frozen per-s rates r_i, lambda=sum r_i, and nonnegative frozen q, let E(u)=E0*exp(-u), f(0)=f0. This is a defined local temporal approximation, not a replacement of the changing physical opacity/source by an exact model. Use J(k)=integral_0^h exp(-k*u)du = h*phi(k*h), phi(z)=(1-exp(-z))/z.

    f1 = f0*exp(-lambda*h)+q*J(lambda),
    A_i = r_i*(f0*J(lambda)+q*(h-J(lambda))/lambda),
    D = (J(1)-J(lambda+1))/lambda,
    B_i = epsilon*E0*r_i*(f0*J(lambda+1)+q*D),
    R = epsilon*E0*(f0*J(lambda+1)+q*D),
    Q_N = q*h,
    Q_E = epsilon*E0*q*J(1),
    U1 = epsilon*E0*exp(-h)*f1.

At lambda=0 use (h-J(lambda))/lambda -> h^2/2 and D -> 1-(1+h)*exp(-h); stable series/divided differences are required near cancellation. All integrals are nonnegative. In exact arithmetic,

    f1 + sum_i A_i = f0 + Q_N,
    U1 + sum_i B_i + R = epsilon*E0*f0 + Q_E.

At exit export f1 with E=Ec, and stop subsequent absorption/redshift. A common implicit gas stage can consume the integrated A_i/B_i, while gas cooling/recombination/work/CMB retains its original owner contract. Integrating q exactly in time or using a higher-order stage is an upgrade requiring the corresponding same-owner identity; do not mix an exact emitted ledger with frozen-q injection. This kernel differs from the existing helper fixed_rate_moments, whose U formula represents a different source-energy convention; do not reuse it without a definition check.

Eta quadrature must split at panel edges and eta=s0+ln(Ek), s1+ln(Ek) for source edges and all cutoff energies, with further adaptive refinement as required. Use positive quadrature weights and the same quadrature atoms for all components of a local transaction. Independent quadrature for sink, heat and exit loses the strongest identity guarantee. However, shared quadrature alone does not prove exact equality to stored N0/M0: explicitly control the integration error of the reconstructed initial moments, or construct a positive moment-exact quadrature on each subinterval. Do not rescale weights after the fact. Admit the full unchanged budgets, including quadrature error, before committing.

## 6. Why the tempting smaller fixes fail

1. Posthoc smoothing only out_N/out_E changes the global residual by the smoothing increment. Smoothing stock as compensation still does not change the spectrum used in opacity, Gamma, heat, redshift or the gas trajectory. Smoothed budgets are no longer independent evidence of the solved equations.
2. Replacing each node's Heaviside survival by a fractional weight alpha_j(s) gives the extra physical terms alpha_j' n_j and alpha_j' E_j n_j. Depositing its loss at Ec leaves an energy discrepancy proportional to (E_j-Ec)*(-alpha_j')*n_j unless a consistent spectral shape supplies the true boundary trace and active energy moment. The omitted terms cannot be charged to redshift after the fact.
3. A single density/count per panel with an assumed mean Ebar can conserve count but generally misses energy. Physical absorption is integral E*lambda*f, not Ebar*integral lambda*f; their difference is a covariance term. The same problem affects a spectrally varying source. One must evolve a second energy moment or retain a richer positive representation with equivalent information.
4. Increasing temporal precision does not remove fixed-grid exit jumps. Uniform refinement can shrink their amplitude but the supplied diagnostic already shows unfavorable cost; extrapolated required panel counts are heuristics, not a lower-bound theorem for the 273 output phases.
5. Source-edge continuity and HeI/HeII cutoff integration still matter. Fixing only the 13.6 eV export does not certify the three failing Gamma fields or x_heii.

## 7. Minimal options, tradeoffs, and recommended order

A. Two-moment cut panels in eta, with integrated sweep: recommended first design. Same number of state unknowns as Gauss2; analytic redshift and unchanged characteristics; exact E^-2 panel-source integrals possible; requires positive reconstruction, paired number/energy absorption quadrature, moment-preserving remap and cut-cell handling. Owner evaluation and Jacobian costs rise; event count may fall when node events are replaced by panel topology. No speedup is yet established.

B. Fixed physical log-energy x=ln(E) finite volume with two moments: larger code change but fixed source and threshold edges. Density g(x,s)=f(x+s,s) satisfies g_s-g_x=q-lambda*g. Number face flux is -g; energy density u=epsilon*exp(x)*g satisfies u_s-u_x=epsilon*exp(x)*(q-lambda*g)-u. Thus for cell [xL,xR], N'=gR-gL+Q_N-A_N and U'=epsilon*(exp(xR)*gR-exp(xL)*gL)+Q_E-B-U. Use the identical trace in adjacent cells and F_E=epsilon*Eface*F_N. Positivity-preserving upwind/implicit or conservative semi-Lagrangian transport is needed; explicit transport introduces a CFL restriction, while low-order transport adds spectral diffusion. This avoids the shrinking cut cell but moves redshift transport throughout the grid.

C. Event-local high-order density/dense characteristic representation: smallest conceptual physics change and useful independent oracle. Retain positive f(eta) or an integral representation, integrate moving supports directly, and defer projection. Greater representation/history/quadrature cost, potential exponential-polynomial complexity growth, and separate positivity certification. Nodal interpolation alone is not a conservative implementation of this option.

D. Nonuniform adaptive fixed-node refinement: useful diagnostic or fallback; target swept boundary, source edges and all species kernels instead of uniform p. Whole-node exports remain discontinuous, so this is not the preferred final representation. Adaptive splitting of a positive panel preserves its inherited N and M; merging must also preserve both, with a spectral-shape error indicator. An estimator must include outflow number/energy, all three Gamma, heat, stock and source moments, not just total photons. Node/step/resource caps stay explicit. The future implementation must define separately the counts of stored moments, panel reconstruction degrees of freedom, simultaneous quadrature samples and solver unknowns; changing their relation does not silently reinterpret max_packets or grant more resources.

Recommended staged work: analytic/source-free test implementation first; independently review a conservative two-moment or dense-integral reference; then short source+absorption coupled controls; only then run a bounded z12→10 spectral pilot with a separate work budget. Do not promote either existing p64/p128 reference to a continuum oracle for this new representation.

## 8. Proposed interfaces and ownership contract

- SpectralPanelState: fixed eta bounds; active and causally occupied supports at s; source-front/zero-trace metadata; N and comoving-energy M; positive reconstruction parameters or declared limiting measure; log-scale/tail representation where needed; immutable identity.
- CutTopology(s0,s1,panel): source/cutoff partitions, swept interval, exact half-open conventions, no silently merged adjacent-float events.
- SourceMoments(s,interval): q number and comoving-energy moments for the actual supported source, plus separately identified direct below-band emission.
- PanelOwners(s,gas,reconstruction,topology): A_N[3], A_M[3], Gamma kernels[3], boundary trace; identical support/sigma in all channels. Gamma is evaluated directly, never by division by a vanishing neutral fraction.
- PanelTransaction(s0,s1,gas_stage,panel): positive end N/M, Delta source_N/E, absorption_N[3]/E[3], redshift_E, out_N/E, quadrature residuals and explicit tail bounds; no mutation.
- MaterialTransaction: consumes those exact absorption owners for ionization, CHI binding and excess heat; existing collision/recombination/escape/work/CMB ownership retained.
- CommitIfAdmissible: accepted state and all ledgers change together; rejected candidates leave state unchanged; all original gas/simplex/provider/radiation/budget/resource conditions apply.
- Observe: integrate the same admitted representation for Nactive/Eactive and endpoint Gamma; reconstruct independent residuals; preserve all 37 comparison fields and exact output epochs.

## 9. Test-first contract (no acceptance criteria relaxed)

T1. Transparent source-free constant density on one panel, initially with b(s0)<=L. Analytic N(s)=f0*(R-max(L,b))+, M(s)=f0*(exp(R)-exp(max(L,b)))+, and out_N=f0*clamp(b-L,0,R-L). For b(s0)>L, first replace L by the initial active lower edge max(L,b(s0)); no initial outflow is fabricated. Verify continuous cumulative exit, right-hand traces, empty-cell limit, N and U+redshift+out_E identities, panel-split invariance and arbitrary off-phase outputs.

T2. Smooth exponential density and one analytic atomic control. The smooth density must have no stock jumps at quadrature abscissae; a deliberately atomic spectrum must retain its true physical exit event. Distinguish representation error from real singular data.

T3. Frozen competing absorbers/source. Check the analytic kernel above over h, lambda*h from zero through strong extinction, source=0 and f0=0, source start/stop and cutoff inside one step. Verify every A_i>=0 and B_i-epsilon*CHI_i*A_i>=0 on its physical support; identities hold without owner reassignment. Test stable small-lambda limits and compare to high-precision quadrature.

T4. Source-only expanding spectrum, including a source front entering an initially empty panel. Integrate the actual E^-2 source over time and active/swept supports. Verify no photons ahead of the causal front, zero trace/no incoming Reynolds flux at the newly born front, proper-time conversion, exact panel-source totals, injection-and-exit within a step, and direct below-band source only in an explicitly separate supported control. Never renormalize node or panel weights.

T5. Positivity/realizability. Empty/near-empty spectrum, extreme means, vanishing cut width, no representable midpoint, neutral species=0, strong absorption/IEEE tails. Reject invalid states without projection; preserve authoritative log information and conservative underflow bounds. Nonnegative source/owners do not waive endpoint checks.

T6. Conservation negative controls. Intentionally smooth only outflow, omit boundary energy, substitute CHI for Ec, use Ebar*A_N instead of A_E, use inconsistent source totals, or remap preserving only N. Each must fail an independent invariant/owner test. Preserve the old fixed-node fixture as a regression exposing staircase behavior.

T7. Local quadrature and reconstruction. Verify both moments before/after each split, merge and remap; shared quadrature identity and initial-moment integration residual; nesting/order refinement; source/threshold split correctness. A no-negative-sample test alone is insufficient to certify a positive polynomial between samples.

T8. Coupled short history. Same immutable cosmology/provider/closure/initial state/source. All 37 fields, all original accepted/output budgets, independent time retightening at 0.1 allowance, separate spectral refinement and independently rerun output schedules. Spectral convergence must measure reconstruction bias as well as quadrature order.

T9. Bounded full z12→10, then separately reviewed z12→6. Exact 273-row schedule, complete histories only, native-versus-same-grid temporal comparison separated from refined continuum-reference spectral comparison. Include early near-zero outflow floors; no late-time-only or endpoint-only pass. No automatic p256/native release or max_packets/max_steps increase follows from this design.

Original comparator allowances are unchanged: fraction 1e-6+1e-3*abs(ref); Gamma 1e-22+1e-3*abs(ref); energy 1e-20+1e-3*abs(ref); photons 1e-8+1e-3*abs(ref); T/Tcmb 1e-6+1e-3*abs(ref). Number residual allowance 1e-10*max(emitted_N,1e-10); energy allowance 1e-10*max(emitted_E+work_E+escape_E+abs(cmb_reservoir_E),1e-20).

## 10. External context and limits

The equations above are derived for the inspected local per-H model, rather than copied from an external code. External primary sources corroborate the general conservative finite-volume approach only:

- Vaytet et al. (2011), https://arxiv.org/abs/1101.4955: frequency-domain finite-volume exchange between radiation groups in a multigroup radiation-hydrodynamics scheme.
- Jiang (2022), https://arxiv.org/html/2209.06240v1: a finite-volume frequency-space formulation, time-dependent gas/radiation coupling and the limitations of frequency-integrated spectral representation.
- LeVeque/Clawpack advection chapter, https://www.clawpack.org/riemann_book/html/Advection.html: integrated conservation, boundary fluxes and exact characteristic translation.

Retrieved 2026-10-07. No external package/API is being installed or used; these are mathematical background, not version-dependent implementation authority. They do not prove this closure's accuracy or positivity under the chosen time integrator.

Unresolved implementation choices: robust positive closure at extreme moments; exactly moment-consistent quadrature or certified residual allocation; safe near-empty cut-cell representation; coupled implicit Jacobian; projected spectral-shape error; practical runtime. These are explicit gates for a bounded prototype, not reasons to change the scientific model or soften acceptance.
