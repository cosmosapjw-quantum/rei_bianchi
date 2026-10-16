# Unit8 A: reusable thermal atomic rates and early Li charge history

Frozen 2026-10-16. Requested authority Astra; observed model UNKNOWN. This extends the completed Unit7 source/opacity bridge with thermal rates and a donor-specific early charge trajectory. No old output or product runner is modified. Source discovery used primary Verner tables/code and paper, with Exa corroboration and SciSpace discovery recorded separately. The calculation is a declared reduced atomic model, not a complete multilevel cosmological recombination calculation.

## 1. Exact providers, charge convention, and two distinct closures

Reuse the original `phfit2.f` Version 2 from Unit7 and new `rrfit.f` Version 4 (June 29, 1999). Parse their actual block data, crosscheck the six H/He/Li entries against the author's tabulations, and record the effective rows. q is ionic charge; N=Z-q is the electron count in the photoionizing or recombined ion. RR table labels name the **product**, so LiIII,N=1 is LiIV+electron→LiIII, not LiIII→LiII.

The six ready element channels are H I, He I, He II, Li I, Li II, Li III. Provider thresholds are H I 13.60, He I 24.59, He II 54.42, Li I 5.392, Li II 75.64, Li III 122.5 eV. Preserve these fitted thresholds; do not replace them with newer spectroscopic energies while keeping provider cross sections.

Ground-state photon channels are H/He/Li occupied outer-shell photoionization. For Li I invert **only 2s**, with the exact PH2→PH1 switch at64.39eV; the 1s partial is retained as a separate blackbody opacity/energy diagnostic. A LiI K hole is not the LiII ground state, so the K partial cannot be inserted into a ground-to-ground Milne relation. For H I, He I, He II, Li II, Li III the selected shell is1s. The provider uses PH2 for the N=1,2 species on the finite energy range here.

Main closure `ground_Milne`: one ground state per Li charge q=0,1,2,3, plus continuum electrons and prescribed blackbody; use ground-channel photoionization and its spontaneous+stimulated inverse computed below. Nuclear spin degeneracy cancels for the same isotope; electronic g=[2,1,2,1], hence d_q=2*g_(q+1)/g_q=[1,4,1]. H has d=1; He channels d=[4,1]. This is microscopically reversible within the selected smooth channel model, while omitted excited-state kinetics remain explicit.

Comparison closure `total_RR_sensitivity`: same ground photoionization, but spontaneous total RR from rrfit, without an invented stimulated all-level correction. It tests replacing direct-ground capture by the published all-bound-level rate; it is not an LTE closure and its difference is model sensitivity, not a statistical uncertainty or a complete error bracket. Do not add ground Milne RR to total RR (which already contains ground capture). Neither model includes electron-impact ionization, dielectronic recombination, charge exchange, multilevel trapping, nonthermal radiation, or a self-consistent electron/temperature solution.

The author paper explicitly distinguishes total from partial photo cross sections for Milne inversion, and total RR from ground and excited contributions. Numerical precision here does not certify physical accuracy of the near-threshold smooth fits or omitted processes.

## 2. Blackbody and Milne derivation with units

Let epsilon be photon energy in joules, chi the channel threshold in joules, sigma(epsilon) in m^2, and C=8*pi/(h^3*c^2). In an isotropic blackbody the collision rate is c times photon number density, not the one-sided c/4 surface flux. Thus

    beta(Tg)=C integral_chi^infty sigma(epsilon)*epsilon^2
                         /expm1(epsilon/(kB*Tg)) d epsilon  [s^-1].

The corresponding absorbed and primary-kinetic rates per target are

    W=C integral sigma*epsilon^3*n_gamma d epsilon            [J/s],
    K=C integral sigma*epsilon^2*(epsilon-chi)*n_gamma d epsilon [J/s],
    Q=chi*beta,  W=K+Q.

For LiI1s use chi=64.39eV; sum2s+1s only for total opacity diagnostics, with shell energy bookkeeping as in Unit7. These are rates in the specified unattenuated blackbody, not predicted deposited heat.

Define D_q(Te)=d_q*(2*pi*me*kB*Te/h^2)^(3/2) [m^-3] and S_q(Te)=D_q*exp[-chi/(kB*Te)]. The level-resolved Milne relation, averaged over Maxwellian free electrons, gives

    alpha_g_sp(Te) = (C/D_q) integral_chi^infty
          sigma*epsilon^2*exp[-(epsilon-chi)/(kB*Te)] d epsilon [m^3/s],
    alpha_g_stim(Te,Tg) = (C/D_q) integral_chi^infty
          sigma*epsilon^2*exp[-(epsilon-chi)/(kB*Te)]
          *[1+n_gamma(epsilon,Tg)] d epsilon                  [m^3/s].

Convert these to cm^3/s by multiplying by 1e6. At Tg=0 use n_gamma=0. The label `alpha_g_stim` means spontaneous plus stimulated, not stimulated alone. The photon epsilon^2 factor, free-electron spin factor2 in D, and electron thermal phase space are all retained.

At Te=Tg=T, exp[-(epsilon-chi)/kT]*(1+n)=exp(chi/kT)*n pointwise. Therefore independently integrated rates obey

    beta(T)/alpha_g_stim_cm3_s(T,T)=S_q(T)/1e6 [cm^-3].

This identity is an actual check only if alpha is integrated independently, not set to beta/S. Also export alpha_g_sp, alpha_total_RR, their ratio, stimulated enhancement, Saha ratio and detailed-balance residual. Never impose this equality on alpha_total_RR.

The published fit is

    alpha_total_RR_cm3_s(Te)=a/[sqrt(Te/Ta)
          *(1+sqrt(Te/Ta))^(1-b)*(1+sqrt(Te/Tb))^(1+b)].

Li product rows (a,b,Ta,Tb) are LiI=(1.036e-11,0.3880,107.7,1.177e7), LiII=(1.112e-10,0.6926,24.37,8.323e6), LiIII=(3.039e-10,0.7539,18.71,6.209e6). Parse all six requested rows from rrfit. For HeI use the **b** table entry because that is what the public rrfit code actually selects; do not silently use the alternative low-temperature fit. The author gives3..1e9K for low-Z RR applicability; this unit uses100..1e6K only.

## 3. Reusable grids, finite tails, and stable computation

Export six-channel blackbody beta,W,K,Q and same-T ground spontaneous/stimulated RR, total RR and Saha diagnostics on 81 logarithmically spaced temperatures100..1e6K. Distinct variables Te and Tg must remain named explicitly; an equal-temperature table does not license their equality elsewhere. Additionally export Li ground alpha_g_stim on Te=[300,1000,3000,1e4,3e4,1e5,3e5,1e6]K and Tg/Te=[0,0.5,1,2], a 96-row reusable two-temperature sample. No late-epoch history is attached to those table rows.

Use shifted electron/photon variable t=(epsilon-chi)/(kB*Tscale). For beta, Tscale=Tg, x0=chi/(kB*Tg), and

    beta=C*(kB*Tg)^3*exp(-x0)*Ibeta,
    Ibeta=integral_0^80 sigma(chi+kB*Tg*t)*(x0+t)^2
                 *exp(-t)/[-expm1(-(x0+t))] dt.

Compute log_beta=log(C)+3log(kB*Tg)-x0+log(Ibeta) before exponentiating. At underflow retain the finite log_beta and mark the floating rate as underflowed, not physically zero. For alpha use Tscale=Te and prefactor C*(kB*Te)^3/D_q; its integrand is sigma*(x0e+t)^2*exp(-t), multiplied for stimulation by1/[-expm1(-epsilon/(kB*Tg))]. No exp(+chi/kT) is evaluated. Below threshold sigma=0 by provider convention.

Gauss–Legendre64/128 nodes on each interval with boundaries0,1,4,16,40,60,80 and every applicable LiI64.39eV branch converted to t. Final=128; compare64/128 at all reusable table rows. Compare integration through 60 versus80 and require relative tail difference<=1e-12 for rates/moments after their scaled integrals are formed. This is a controlled finite-window approximation, not evaluation of an unknown physical spectrum to arbitrary energies. The largest sampled energy is below14keV for the declared grids and below the provider's100keV partial-fit range. Export the actual maxima. Do not extrapolate this table or add a ratefloor that changes a stiff transition.

For kinetics compute a distinct 513-node uniform-u rate table over the actual early window, with Te=Tg=T0(1+z). Use shape-preserving interpolation of log positive rates against u (PCHIP); direct RR may be evaluated analytically instead. Reuse every other node for a257-node interpolation comparison. No quadrature inside the ODE right-hand side. Record maximum rate-interpolation discrepancy at the 256 off-grid midpoints via direct evaluation; the limit is2e-5 relative. It is acceptable to use the same 513 rate table for both atomic closures, since their physical distinction is in alpha, not quadrature.

## 4. Actual early window, independent origins, and kinetic equations

Use the existing donor, Unit7 BE_KINETICS_CONTRACT constants/cosmology, BE_KINETICS_RESULT and the actual 32769-row `be_kinetics_history.csv`. Keep its z=100000→10000 ionized thermal bath: T0=2.7255K, Tm=Tgamma, nb0=2.47920954940649e-7cm^-3, Ye=0.8765521883879055. Compute ne(z)=Ye*nb0*(1+z)^3 and the same donor H(z). Be history is a prescribed source; do not rerun or modify it. Use raw Fdecay, not normalized p_z. Interpolate F with monotone PCHIP in ascending u=ln[(1+zstart)/(1+z)]. No extrapolation outside the donor history interval.

Let l^d_q be the probability distribution of the pre-existing direct donor Li7, sum l^d=1. Let l^b_q be Li7 produced by EC per initial Be7 donor, sum l^b=F(u). Actual abundances are Y_Li,q=YLi7_direct*l^d_q+YBe7*l^b_q. Initial direct Li is bare, l^d=(0,0,0,1), and l^b=0, consistent with the early-ionized preparation. This starts the atomic evolution at zstart; the source table does not establish a resolved Li trajectory between the BBN endpoint and zstart. Report the stationary initial bound fraction as an initialization diagnostic and inherit Unit7's nonzero omitted Be-source bound; do not assert an uncomputed interval was exactly zero.

For q=0,1,2 define b_q=beta_q and r_q=ne*alpha_(q+1→q). With zero out-of-range terms,

    d l_q/dt = b_(q-1) l_(q-1) + r_q l_(q+1)
               - (b_q+r_(q-1)) l_q + delta_(q,3)*dF/dt,
    d l/du = (atomic generator/H)*l + delta_(q,3)*dF/du.

The direct-origin equation has no source. The generator has nonnegative off-diagonal entries and zero column sums. Nuclear Li number is conserved separately except EC source addition. Evolve only q=0,1,2 and recover q3=1-sum lower for direct, q3=F-sum lower for EC. The lower equations use the actual interpolated F and need no numerical differentiation. This avoids a large cancellation in the nearly bare total and enforces source normalization without clipping or rescaling. Recovering a materially negative q3 is a failure, not permission to repair populations.

Use scipy solve_ivp Radau with analytic6x6 block-diagonal Jacobian for the two origins, rtol1e-8, atol1e-13 on normalized states; output 1025 uniform-u points plus exact endpoints. A BDF solve at rtol3e-9,atol3e-14 is the independent solver check for the ground model. A Radau run using 257 rate nodes is the interpolation comparison. One ground-model run with every second Be-history row checks coupling resolution; no alternate physics is introduced. For the total-RR comparison use the same 513 interpolation settings and production solver only. Report component-origin and charge differences between models as sensitivity, without requiring them small.

## 5. Conditional equilibrium and diagnostics

For either frozen local generator, positive stationary probabilities obey pi_(q+1)/pi_q=b_q/r_q. Construct normalized weights using log ratios to avoid overflow; no solver inversion is needed. For the ground model at equal T these equal S_q/ne by detailed balance. Export pi, dynamic-minus-pi, mean charge, bound-electron count, ne*alpha/H and beta/H at selected z=100000,50000,30000,20000,15000,10000. Do not substitute pi for the evolved trajectory or call the total-RR stationary solution Saha equilibrium.

Separate direct and EC-origin histories matter because daughter Li is injected bare at the actual Be decay time. Report their normalized charge distributions only when the corresponding total is positive; an absent EC component has null conditional fractions. The actual per-baryon abundance sum remains YLi_direct+YBe*F.

## 6. Ready17 adapter and complete residual ledger

Export the existing17 ordering n,H1_0,H1_1,D_0,D_1,T_0,T_1,He3_0,He3_1,He3_2,He4_0,He4_1,He4_2,Li7_0,Li7_1,Li7_2,Li7_3 for the ground model. The first 13 are the **frozen fully ionized early-bath spectators**: n is unchanged, H/D/T in q1, He3/He4 in q2. Only the last 4 contain newly evolved Li populations. This is a standalone numerical adapter, not native product integration or a late H/He recombination history.

Retain every excluded donor nuclide unchanged except Be7, which is removed from that frozen residual once and represented separately by YBe*x_Be4 and YBe*x_Be3. Li receives YBe*F once. Check full baryon sum against the donor's original (possibly nonunit) baryon sum, not against a renormalized1. Full nuclear charge changes by -YBe*F.

Let Ebound_Li=sum_q(3-q)*Y_Li,q and Ebound_Be=YBe*x_Be3. Relative to the initially bare donor, the explicit ledger is

    delta_nuclear_charge=-YBe*F,
    bound_electrons=Ebound_Li+Ebound_Be,
    delta_free_electrons=delta_nuclear_charge-bound_electrons,
    delta_ionic_charge=delta_free_electrons,
    delta_total_electrons=-YBe*F.

Report these trace deltas separately from the frozen ne used for rates and their maximum fraction of Ye. The17-only free+bound electron sum equals its instantaneous tracked nuclear charge; the complete ledger additionally includes surviving Be and unchanged excluded nuclei. Bound-electron capture consumes one electron and transfers it to the weak channel; recombination redistributes free to bound electrons. No electron normalization repair is used.

The reusable rate-availability map lists the six actual provider channels and their17 isotope consumers: H I→H1,D,T; He I/II→He3,He4; Li I/II/III→Li7. Reusing element fits for isotopes carries no resolved isotope/recoil accuracy. n has no atomic channel. Missing multilevel/DR/collisional/charge-exchange processes and missing later ne(z),Tm(z),H/He/nonthermal history are explicit dependency fields, not zeros. No native code activation is asserted.

## 7. Acceptance, budget and next action

Require source constants/rows agree semantically with the author tables; immutable source hashes match. Ground-channel and independent Decimal RR/formula evaluations at100,1e4,1e6K agree1e-11 relative. If gfortran is present, use unchanged public rrfit/phfit2 native REAL oracles with 1e-5 relative; otherwise record NOT_RUN_compiler_unavailable and do not install a compiler.

Numerical rate acceptance:64/128 comparison<=1e-8 relative; independent scipy quad spot checks on the six channels at300,1e4,1e6K<=2e-8; beta=alpha*S and W=K+chi*beta<=2e-8, using scaled/log forms where rates underflow. Finite alpha and finite log_beta are required. Zero/underflow cases are represented explicitly, never accepted by a loose SI absolute floor. Independent integration covers alpha and beta separately; do not make a check tautological. RR-model disagreement has no numerical PASS limit.

Kinetics: normalized populations>=-2e-11; per-origin sum residual<=2e-11; full Li source sum residual<=2e-11 normalized to max(YLi_direct,YBe*F,1e-30); Radau/BDF,513/257 and full/half Be-grid maximum absolute charge-population differences<=5e-6 (each normalized origin separately, EC values per initial Be). Report relative differences for populations>=1e-8, but do not claim accurate tiny neutral fractions from an absolute ODE tolerance. No clipping or renormalization. Mass/charge/electron ledger residual<=1e-12 relative with 1e-25 per-baryon absolute floor; original donor normalization is a reported value.

All new numerical work combined <=30 seconds, one thread, one finite production/validation pass. If an unexpectedly expensive check threatens the budget, stop and return observed timings and the completed output; no silent unchecked admission. One targeted repair is permitted only after authority interpretation. PASS advances to independent review and publication of the reduced early radiative model, reusable rates and adapter. A full late charge/recombination history remains dependent on actual late electron, temperature and radiation histories and additional atomic closure; do not fabricate them to fill a plot.
