# Source history and finite prescribed-bath coupling contract

2026-10-28. Author role: requested Astra scientific authority; actual runtime model unobserved. This is the next bounded unit after PR245. It uses the completed external operator rather than repeating its 201-epoch evaluation. The old original33/88, central28/88, fast4/7 remain unchanged until an authority explicitly admits a scoped node. Physical F4 is not replaced by phenomenological calibration claims.

## A. Selected terminal nodes and authority

H1: bind a definite illustrative source history and matched clock; H2: evaluate a constructive QSS error bound including initial transient; H3: implement and test a runnable finite 17-visible-state prescribed-bath coupling; H4: execute the frozen finite pilot only if explicit IVP authority exists. Completion of H1–H3 is useful scientific progress even if H4 is awaiting permission. No unresolved astrophysical calibration is imposed as a prerequisite to this explicitly phenomenological pilot.

The user previously approved cumulative planning30/presentation65 CPU seconds. Prior closeout reports planning19.204540885/presentation56.217331494, with old attempts and allocations closed. A fresh, non-IVP diagnostic allocation may use the continuing user authorization without resetting debits or transferring closed reservations; record its exact new command, caps and measured debit before/after execution. Author's recommended new maximum: tests4 child CPU seconds +0.5 observer/tail; diagnostics3+0.5; one plot3+0.5, one worker,3GiB, no automatic retries. Parent owns the precise allocation and must fit it under cumulative ceilings. Restore original policy caps10/30 afterward, retaining the over-baseline debits and UNKNOWN_NOT_ZERO costs.

The main campaign remains595.225063/600 and NO_MORE_IVPs. This is an explicit execution restriction, distinct from physical claim admission. The broad continuation request does not expressly revoke it. A new pilot IVP requires a concrete separate authorization; it must not be relabeled algebra or funded by a foreign ledger. Prepare all code and a reviewable maximum-three-case run before asking. Old30/65 approvals expressly covered no-IVP work. No new scientific local run is performed by this contract author.

## B. Immutable inputs and exact meaning of history

Reuse `rei_external_sources_20261028/implementation/{model.py,config.json}` and its frozen event/energy conventions. Preserve source hashes at execution. Baseline is `rei_fast_selected_20261028/outputs/grid044_M4_nominal_all21_populations.csv`, SHA256 `68b316ae614db15f5765cf97c8f634fb57b3efc8f6a597236a27ec6bcdc3c539`; matched NPZ is `rei_fast_selected_20261028/inputs/angtherm_selected/research/rei_angular_thermochemistry_20261023/results/grid044_M4_nominal.npz`, SHA256 `ac035e9bdc6427dd66cbc3a39db92769ffc23f2ae8de7a2c1200b83fb9f20619`.

Read the NPZ's own H,nHref,eta. Require shape201, finite positive H and nHref, increasing eta, eta agreement with CSV at absolute5e-15. Do not invent H from density or a different cosmology. Coordinates: eta=ln(a/a_initial), z=21exp(-eta)-1, eta∈[0,ln7], proper-time elapsed t(0)=0 and dt/deta=1/H. t is elapsed proper time on this source background, not an absolute universe age.

For the finite diagnostic history define H(eta)=exp(PCHIP(eta_k,log H_k)) on the saved knots. This reproduces the source interpolation convention but uses saved output knots; it is an explicitly specified finite reconstruction, not proof of unresolved donor-clock accuracy. Compute t increments with fixed Gauss-Legendre8 quadrature, compare16 once, and require total elapsed-time relative difference≤1e-8 and every interval≤1e-7. Failure gives CLOCK_QUADRATURE_HOLD, not a fabricated time axis.

All external photon bins, CR fluxes, injection amplitudes and escape hazards are exactly the earlier constants at alpha=1, turned on at t=0 and continuously replenished thereafter. Thus the actual chosen local source history is constant external forcing on this finite interval. No stellar/IGM astrophysical fit or transported emissivity is inferred. Source rates still vary because target abundances vary. At each saved knot obtain S_fast,n,S_fast,T and kcap from the already frozen formulas and baseline populations; define these three coefficient functions by linear interpolation in reconstructed proper time. This interpolation is the declared model, not a claim to resolve any faster initial atomic transient between saved knots. Preserve exact zero amplitudes and never insert plotting floors into data.

## C. Five-stock dynamical object and QSS bound

Let x=(B_n,B_T,n,T0,T1), all particles/Href. The first two are distinct fast reservoirs, not thermal abundance. Set x(0)=0. This finite source turn-on choice is deliberate; QSS at t=0 generally fails. With previously frozen constants:

    Bn' = Sfn(t) - Lfn Bn
    BT' = SfT(t) - LfT BT
    n'  = In + ksn Bn - Ln(t) n
    T0' = I0 - (LT+Gamma)T0 + r T1
    T1' = I1 + ksT BT + Gamma T0 - (LT+r)T1

Lfj=ksj+kej+lambda_j/gamma_j; Ln=lambda_n+kcap+kesc; LT=lambda_T+kesc. Gamma and r are the original external-only T rates; no old-bath atomic terms are included in this QSS comparison. The frozen fixed point x*(t) is exactly the prior reservoir/QSS formula. This diagnostic does not integrate a new IVP.

Partition into neutron-family u_n=(Bn,n) and tritium-family u_T=(BT,T0,T1). Their matrices are Metzler. Column sums for n are -(ken+lambda_n/gamma_n),-Ln; for T they are -(keT+lambda_T/gamma_T),-LT,-LT. Transfers ksj, Gamma and r cancel in their respective column sums. Therefore each ordinary l1 norm contracts at rate c_n=min(ken+lambda_n/gamma_n,Ln)>0 and c_T=min(keT+lambda_T/gamma_T,LT)>0. Separate family norms avoid masking tiny T by the larger n scale.

Proof: for an absolutely continuous difference v, the upper right derivative of ||v||1 is at most mu1(A)||v||1, where mu1(A)=max column sum for Metzler A. For e=u-u*, e'=Ae-(u*)'. Multiplication by the scalar integrating factor and integration gives

    ||e(t)||1 ≤ exp(-∫0^t c) ||u*(0)||1
                 + ∫0^t exp(-∫s^t c) ||(u*)'(s)||1 ds.

No QSS claim follows merely from tau<<H^-1. The source derivative and the initial mismatch are both required. The same proof applies interval by interval at the finite interpolation knots (derivatives exist almost everywhere; fixed points are continuous).

On interval k, let c_k=min all endpoint losses and M_k bound ||(u*)'||1. Propagate the computable upper bound

    E_{k+1}=exp(-c_k Δt) E_k + [-expm1(-c_k Δt)] M_k/c_k,
    E_0=||u*(0)||1.

For any offset δ in that interval the same formula with δ is a within-interval upper envelope. This bound is an algebraic recurrence derived from a comparison inequality, not a numerical integration of the physical five-stock system.

Analytic M: B*=Sf/Lf, so |B*'|=|Sf'|/Lf. For neutron n*=N/D with N=In+ksn Sfn/Lfn and D=Ln, both affine in t. Thus n*'=(N'D-ND')/D²; its constant numerator and minimum endpoint D give a rigorous supremum. Add this to |Bn*'|. For T, the constant inverse2x2 loss matrix maps (I0,I1+ksT SfT/LfT); each T fixed point is affine, so M_T is the sum of absolute exact constant slopes for BT*,T0*,T1*. No finite difference at a knot substitutes for this envelope.

Discrimination criterion frozen before seeing output: per family, a saved epoch is QSS_CERTIFIED_1_PERCENT when E_k≤0.01||u*_k||1, with a zero-denominator case certified only when both sides are exactly0. Otherwise label QSS_NOT_CERTIFIED, not QSS_REFUTED. Report separate initial-transient and forcing-variation contributions by propagating their E recurrences independently; also report last uncertified saved epoch and first subsequently all-certified saved epoch. A sample-only certificate is not an entire-interval certificate. For an interval-wide certificate compare the maximum bound on the interval with0.01 times a rigorous minimum of the nonnegative fixed-point family sum (compute rational neutron extrema including derivative roots; T affine endpoints). If not implemented label interval certification NOT_RUN.

## D. Executable finite 17-state coupling, ready for explicit IVP authority

The minimal new pilot evolves 17 visible heavy states plus Bn,BT and their kinetic energies Un,UT. Hidden Li6's four saved histories remain prescribed baseline quantities and enter plotted baryon normalization/electron accounting, with no new source events on Li6. This is a prescribed atomic/photon/electron/temperature bath experiment. It is not the larger continuous-emissivity photon-transport pilot from the original work-thread prompt, and does not close that prompt's N5–N8 wholesale.

Reuse old atomic transition rates for H,D,He3,He4,Li7 reconstructed from the actual saved M4 photon and temperature history. Source `angular_model.py` defines proper photo hazard Gamma_ch=C*nHref*sum_j(sigma_ch(E_j)*g_j), and recombination hazard R_ch=nHref*v_saved*alpha_ch(T_saved). Obtain g,temperature,v from saved raw fields with their documented normalization and state mapping; no source IVP is rerun. For visible isotopes assemble the adjacent-stage generator using existing `ATOM.edges`, excluding n/T and old beta ownership; use existing isotope-equality assumption only where the old model already adopted it. Interpolate nonnegative proper hazards linearly in t on201knots. Missing saved photon/T schema is a concrete implementation hold, not permission to replace it by an invented fitted generator. Hidden Li6 stays prescribed; its isotope total is constant and its saved charge change is included in any electron-stock ledger.

Implementation schema amendment: observed NPZ fields are `photon_groups`(24×201), `temperature_K`, `electron_per_Href`; photon energies require the matched saved geometry. Recover them through no-run `angular_model.Reduced(M=4).coefficients(eta)` and existing `inputs/background/grid044_history.npz`, recording both additional source hashes. Use saved NPZ H/nHref in the actual hazard/clock; require recovered geometry provider H/nref at knots to agree within relative1e-10 before reusing its energies/sigma. `AtomicNetwork21.rhs` is explicitly not selected: it supplies a different prescribed UV/T scenario and historical beta constants. No donor IVP or photon propagation is rerun by this coefficient reconstruction.

Then in proper time:

    y17' = G_old(t)y17 + f_new(y17,B,U,nref(t));
    Bj' = Sf,j(y17) - Lfj Bj;
    Uj' = Pf,j(y17) - Lfj Uj.

Use original nref at knots, log-linear interpolation (consistent with its monotone positive density) for this finite reconstruction. All f_new events, capture nonlinearity, beta daughters, atomic threshold and CR conventions are those frozen in PR245. Supply actual B and U to transport events: slow kinetic power=ks U, escape=ke U, fast-beta retained kinetic power=(lambda/gamma)U. Do not substitute P/S for U/B after the initial transient. Zero B,U yields zero transport power without0/0; any inconsistent nonzero U with zero B is a diagnosed numerical error. Thermal n/T continue to use only the explicitly selected new atomic/T closure; do not duplicate T recombination or beta.

Initial y17 is the first baseline row; B=U=0. Two source modes: OFF disables external photon/CR/injection/escape amplitudes, retains intrinsic decay/capture; ON uses alpha=1 and frozen escapes. Old bath is identical in both. OFF is a finite prescribed-bath control, not claimed to reproduce the nonlinear self-consistent donor trajectory exactly; interpolation and fixed electron bath are material differences. The saved baseline remains a reference curve with this distinction in captions.

Integrate scaled variables to protect trace species, with scale_i=max(initial isotope total,1e-25) for stable heavy species; n/T and fast stock scales=max(the largest predicted frozen QSS stock over knots,1e-30); energy scales=1e6 times corresponding fast stock scales. Use a stiff solver with analytic or sparse finite-difference Jacobian and positive physical reaction structure; a solver name alone is not a positivity proof. Base rtol=1e-7, scaled atol=1e-11; refinement rtol=2e-8, scaled atol=2e-12. Three fixed cases only: OFF base, ON base, ON refined. Use the same201output times plus dense samples near initial relaxation times; no parameter sweep. Root must choose bounded CPU/wall from implementation cost evidence before authorization; recommended proposal ceiling≤30 child CPU seconds/case,≤120wall/case,1worker,3GiB,zero retries, total reserve≤100 CPU seconds. This is an unmeasured proposal, not performance evidence or an active allocation.

Acceptance: all actual stocks finite; no negative stock below1e-9 of its scale (report minimum and do not clip silently); ON base/refined per-isotope normalized maximum difference≤1e-5 including sampled transients; exact event A/q balance tests as prior; accumulated open-baryon and heavy/free-electron balance residual≤1e-8 times max(total initial stock,total absolute boundary throughput,1e-30). Include Bn+3BT in baryon stock and BT in charge. Use the same quadrature/solver augmented ledger for event extents rather than endpoint-only trapezoids that miss transients. Photon/CR external fields and old prescribed bath have explicit reservoir energy owners; no closed total-temperature conservation or self-consistent photon feedback is claimed. Report new-source power identity separately from any old-bath thermal ledger. All 17 plotted states include LiIV, and normalization includes hidden Li6 plus fast species where total baryon fraction is displayed. Stable abundances perHref require no total-baryon renormalization.

## E. Deliverables and finite stop

H1/H2 outputs: one201row CSV of clock, source rates, losses, fixed points, initial/variation/total family error bounds and certificates; a compact diagnostic figure; raw validation/process results. H3: complete runnable module and targeted tests, including exact affine-reservoir update, zero-input transient, family error-bound logic, source/clock mapping, dynamic B/U usage and baryon/charge events. Do not rerun the old seven-test suite for reassurance. H4: either the three authorized raw pilot cases plus visible17population plot and one fresh independent scoped review, or READY_NOT_RUN with a concrete command and finite permission request. No indefinite review tree or forced calibration prerequisite.

The author actually called Wolfram Language evaluator to check the affine-source scalar reservoir formula B(t)=e^-Lt B0+S0(1-e^-Lt)/L+S1[t/L-(1-e^-Lt)/L²]. Returned ODE residual0, IC B0, zero-loss limit B0+S0t+S1t²/2 and triangular2x2 fixed-point residual{0,0}. The zero-loss Limit emitted intermediate singularity warnings; result is independently established by Taylor expansion and is used only as a limiting identity. Tool algebra is not an independent physical review.
