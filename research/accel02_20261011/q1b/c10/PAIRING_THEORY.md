# C10 split-step pairing contract

Status: derived from the frozen Q1B moment and native ABI definitions; numerical and implementation claims require the separate evidence files. No external physical provider or new approximation is introduced beyond the declared first-order time splitting and existing power-law re-compression.

Let each stored cell have reference-volume number N and current energy moment U in eV cm^-3. E=R(t)q, Q=U/R. The non-tilted expanding background and all source values are the pinned providers. Href=nH(t)V(t), Heref=nHe(t)V(t) are constant reference nuclear densities, V=a_rel^3. Angular weights already enter N,U and are never multiplied a second time.

## Source and geometric work

On an event-split interval [t0,t1], use the same positive quadrature nodes for dN=integral SN dt, dQ=integral SQ dt, injected energy Is=integral R SQ dt and source work Ws=integral (R-R1)SQ dt. Set N*=N0+dN and U*=R1(U0/R0+dQ). Radiation work WA=(R0-R1)U0/R0+Ws is evaluated from this physical expansion integral. It is not an energy-ledger correction. Thus U*-U0+WA-Is=0 algebraically up to independently measured quadrature and roundoff errors. Geometry differences at very short times remain a precision risk, not permission to alter the source.

## Absorption and chemical heat

For positive incident weights Pi matching sum Pi=N* and sum qi Pi=Q*, set kappa_i=c sum_alpha n_alpha sigma_alpha(R1 qi), Pi+=Pi/(1+h kappa_i), and A_alpha_i=h n_alpha c sigma_alpha Pi+. All are nonnegative in the gas domain. Pointwise Pi=Pi+ + sum_alpha A_alpha_i. The same qi weights yield surviving U+, number absorbed per species, absorbed energy and photoheat. No independent counter repair is allowed. Moment matching must be checked before attenuation; a quadrature that closes around an inaccurate incident first moment does not conserve the authoritative state.

The native input moments are K0_alpha=c sum_i sigma_alpha Pi+ and KE_alpha=c sum_i (R1 qi) sigma_alpha Pi+. Proper Gamma=sum_cells K0/V and heat per absorber=EV_ERG sum_cells(KE-chi K0)/V. The chemical thresholds chi=[13.598434599702,24.587389011,54.41776] eV are distinct from sigma turn-ons [13.60,24.59,54.42] eV and remain so.

## Four-variable native gas solve

The unknown is y=(xHII,xHeII,xHeIII,w_eV_H). Fix the source-integrated incident distribution during a trial, and solve y1-y0-h f_native(t1,y1,K(y1))=0. Trial gas states must be finite, have fractions in the physical simplex, and temperature in [1,10^6] K before native evaluation. A rejected trial is neither a projected state nor an accepted trajectory point. The native owner supplies all original recombination, collision, cooling, escape and prescribed CMB terms.

Reference gas energy in eV cm^-3 is G(y)=Href*w+Href*chiHI*xHII+Heref*[chiHeI*xHeII+(chiHeI+chiHeII)*xHeIII]. This is linear in y with fixed nuclear reference densities. Therefore a gas-equation residual r produces exactly the energy defect grad(G).r, before floating-point summation error. This relation is an independent diagnostic of both the solve and the ledger; a small unweighted residual alone does not prove the fixed-initial-energy criterion.

The native combined expansion-work output includes radiation work. The split step has already accumulated WA, so only thermal work Wth_rate=2 H1 Href*w1*EV_ERG is integrated in the gas substep. Native combined minus explicit radiation work, or a same-state dark native call, checks this decomposition. Escape and signed CMB powers use the converged native state.

The total reference-volume ledger is

    EV_ERG * [sum(U1-U0)+G(y1)-G(y0)+sum(WA)-sum(Is)]
      + h * (Wth_rate + Escape_rate - CMB_rate) = 0.

The photon-number ledger is sum(N1-N0-dN)+sum_alpha,cells A_alpha=0. Nuclear conservation and charge consistency remain native gas-owner obligations. These identities are necessary local consistency tests and do not establish the first-order time-discretization error.

## Acceptance limits

A common-final-time h/h2/h4 comparison must use resolved entry supports in every substep. First-order convergence, strict accepted domains and actual measured local/global ledgers are separate checks. A precision failure is retained as ENTRY_PRECISION_TIME_BUDGET_CONFLICT when physically allowed refinement cannot satisfy the existing coordinate guard; no large-step workaround is admitted.

C3 versus saved C2/direct initial opacity is an initial-epoch spatial check only. The full 15.9 to 4 interval, nine-field temporal 2e-6 test, full 24-field spectral/angular 1e-3 test on separately normalized 65/129 epoch sets, fixed-initial energy/number 1e-9 ledgers and geometry1e-11 remain unaltered. BASS adoption requires the new accepted history and an actual receiver call.
