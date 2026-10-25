# Scientific interfaces and PR sequence

## Shared physical contract

Use signature(-,+,+,+), preserve c,hbar,k_B, and declare coordinate time convention. With x^0=ct and four-momentum p^0=E/c, define per-sector energy-density stress in a declared orthonormal frame:
T_s^{mu nu}=(rho_s+p_s)u_s^mu u_s^nu/c^2+p_s g^{mu nu}+(u_s^mu q_s^nu+q_s^mu u_s^nu)/c^2+pi_s^{mu nu},
where u.u=-c^2, u.q=0, u_mu pi^{mu nu}=0, pi symmetric tracefree. rho is energy density, q energy flux. Give full tensor or explicit rho,q,p,pi plus frame; scalar temperature alone cannot specify anisotropic stress.

Every event channel r exports isotope/nucleusA,Z/ioniccharge/state/reactants/products, stoichiometric columnS_ir, gross nonnegative event rateGamma_r, selected domain/normalization, and event-weighted four-momentum changes. In a common volume/time convention Q_s^nu=sum_r Gamma_r<Delta p_s^nu>_event, so cQ_s^0 has unitsenergy/(volume*time). Boost event momentum and transform rate/clock/volume consistently. An event rate is not transformed with the same density weight as a stored occupation packet.

For an internally closed channel sum_s Q_s^nu=0 after including binding/internal energy, recoil, photons, thermal/nonthermal particles and escaped channels as explicitly tracked reservoirs. External photon/baryon injection or escape instead gives sum_internal Q_s^nu=Q_external^nu, with the external reservoir declared once. Never silently force an open-system balance to zero or count the external donor twice. Nuclear abundance incidence conserves nuclei for atomic channels; nuclear reactions use the specified nuclear/baryon/charge ledger and decay products, with neutrino escape explicit.

Use one event measure for number and energy/momentum; <rate*DeltaE> cannot be replaced by <rate><DeltaE> without a derivation. Arbitrary all-target kernels require a coverage matrix keyed by isotope,charge,state,process,T/E/angular/spectral domain and qualified source. Existing H/He/Li rows establish their scoped coverage only. BASS consumes this matrix; atomic repos expand it. Requirements are AND within a selected model; broad all-target ambitions do not block one fully bound channel.

## BASS sequence and finite error relation

Existing B1/B2 close at PR184. Existing B3a–f supply clock/state/finite-count/quadrature/error components. Their composition has not supplied actual finite incident occupation or calibrated history uncertainty.

B3f uses W=E_b n detR, angular boundA0 and positive energy lowerL0. A sufficient total relative Frobenius budget is (A0+sqrt(2)U+epsilon_fp B0)/(L0-U), requiringL0>U. epsilon_fp=2e-12 is empirical binary64reserve, not interval rounding proof. Original target2e-8 remains. Missing eR/eS/en staysnull. The Euclidean Frobenius bound is tied to the declared frame; Lorentz-invariant certification is not implied.

1. B3g consumer binding: copy no upstream implementation; consume exact sourcePin/cohort labels/birthhistory/R,S,n,E_b/error radii and check finite supplied endpoints using existing code. Retiming/pullback belongs to REC owner. A scalar K_s is not a general3x3transport map.
2. B3h physical absorption: freeze one native receiver cell/face trace, finite donor and exclusive reaction owner. Bind angular/spectral/time support and recoil/internal energy. Positive gross counts and finite depletion precede conservative transfer.
3. B3i one-channel geometry coupling: consume the above complete T,Q record in fixed-scale Einstein dynamics. Separate angular/time/radial/tail/source error and retain original constraint+kinetic+ledger monitors.
4. G1C can proceed independently from stored G1B histories: establish d||delta z||/dt<=L(t)||delta z||+eta(t) on a declared tube. A computable Gronwall bound requires a domain-valid L and tube closure. A sampled maximum alone gives a conditional estimate, not a global bound. This work supplies eR/history uncertainty to B3g where justified.
5. B4 selected-client restart; B5 expanded domain: preserve source/grid/frame/clock/accepted history/cumulative debit. One appropriate new comparison only after actual source and resource receipt.

## VigilODE sequence

Existing native AffineErrorNorm already constructs physical endpoint scales and divides by physical dimension. Its finite-row representability refusals differ from research exact integer gate's support. Preserve typed support and default behavior. Native actual BASS port must use full33 state errors,not compact30 diagonal norm; offsets lift states,not embedded differences.

D1–D5 are reusable components, with scopes kept separate. D1 endpoint positivity does not certify internal stage domain. D2 checks beforeRHS; scalar-linear[0,2] certificate is not nonlinear universal safety. D3 has a manufactured whole-curve result. D4 journal ACK is not durable external exactly-once. D5 complete finite pair does not prove J=dF/dy.

V6 actual-model derivative binding is the useful next numerical contract after native owner input. For a fixed affine map y=b+Lz and restrictionR, F_red=R F_full and J_red=R J_full L. If maps/time/source depend onstate, derive the additional terms rather than reuse the fixed formula. Preserve chemical nuclei/charge and energy ledger under restriction. Use analytic/exact or source-qualified derivative where available; directional differences need domain-valid step sequences and separate truncation/roundoff, never a loose universal tolerance.

V2 native driver then composes persistent Session/Transaction/output hooks; sticky fatal, recoverable attempts and provider/method epochs preserve every spent cost and accepted prefix. V7 restart only covers scientific recovery actually needed by that client. Full Session/Driver state matters; recreatingSession::new from accepted(t,y) loses h,attemptcap,counters,pendingACK and can silently reset resources.

V8 whole-domain provider must bind original vector field, Jacobian/residual and tube. Existing privateVerifiedModelProvider and prepare/commit output paths are reused. Point tests or callbacks cannot issue a wholeintervalcertificate.

V3 regression alreadyPASS is reused. V4 structural algorithms alreadyopt-in are reused; source-informed bounds and actual matched-error work decide value. V5 accepted-only remap must conserve joint photon number/energy on actual spectral grid; diffusion mass conservation alone is insufficient.

## Concrete implementation handoff fields

Every future coding child receives exact base/source/input SHA,allowedpaths,equations,units,alloriginaltolerances,requiredpositive/negativecontrols,rawoutputschema,exactcommand,environment,per-run and cumulative debit,stopcondition and reviewrecipient. Command lines are frozen when the actual runnable consumer is selected; this audit does not invent executable CLI flags for unimplemented lanes.

At first substantive failure, retain raw and return to scientific authority. One bounded repair may change only the diagnosed binding/implementation; physics/domain/tolerance changes require an explicit scientific decision. The next PASS action is in every JSONnode. Source/execution/admission/delivery remain separate. No repeated provenance audit when existing exact inputs remain unchanged.

