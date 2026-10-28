# Fast selected-species route: theory and implementation contract

Authority: current user's image-limited abundance-history goal and subsequent explicit correction **“Li IV도 포함해줘. 그림에서 누락했어.”**; parent task 2026-10-28; repository AGENTS.md read locally. Requested role is Astra theory/contract authority; actual model identity is not inferred from this label. This scratch directory is not a Git checkout. Exact remote/source identities must come from the controller's intake. This document authorizes no execution or publication.

## 1. Decision and finite scope

The shortest route is **projection of an existing accepted time history**, preserving its original internal state and closure. It requires no new IVP, no recipient caloric branch, no new Einstein feedback, and no new stellar-emissivity adapter. ANGTHERM01's ten histories and ANGTHERM02's lithium-threshold work are the first specifically identified reuse targets in the saved `WORK_THREAD_PROMPT_KO.md`. The controller must recover the arrays, their matching source/normalization/clock, and the relevant admission before treating this route as available. An endpoint table or a screenshot does not establish a time history.

If those arrays lack the requested physics, deliver the finite-scope reused plot and identify the missing dynamics. A separate prescribed-background reduced calculation is the next route, conditional on source-qualified inputs and a separately authorized finite budget. The main ledger remains **595.225063/600 CPU s, NO_MORE_IVPs**. Closed planning/presentation reservations and other owners' allocations are not executable allowances.

The image contained 16 states. The latest explicit user correction adds Li IV, superseding the initial image-only projection contract. The current display has exactly **17 heavy-particle states**:

| Nuclide | Displayed ion states | A | Nuclear Z |
|---|---|---:|---:|
| neutron | n | 1 | 0 |
| hydrogen-1 | H I, H II | 1 | 1 |
| deuterium | D I, D II | 2 | 1 |
| tritium | T I, T II | 3 | 1 |
| helium-3 | 3He I, 3He II, 3He III | 3 | 2 |
| helium-4 | 4He I, 4He II, 4He III | 4 | 2 |
| lithium-7 | 7Li I, 7Li II, 7Li III, 7Li IV | 7 | 3 |

Current count: 1+2+2+2+3+3+4=17. Roman stage I/II/III/IV means charge q=0/1/2/3; Li IV is bare lithium. Electron density is an auxiliary observable, not an eighteenth plotted heavy species.

**Display restriction and model restriction differ.** Existing Li6, Be7 or other internally evolved states can be retained as closure while excluded from the requested curves. They must be disclosed in the model/caption. Li IV is now explicitly displayed, so there is no requested Li III truncation and no three-stage lithium renormalization. The image-only nuclear reaction list still omits the standard Be7 production/decay path, so it cannot silently replace a full BBN network for precision Li7 production.

## 2. Route A: executable specification for saved-history projection

Inputs: original raw history and admission; stored time variable and its physical mapping; complete state-column registry; abundance normalization; isotope totals or heavy-state populations; raw source/case/grid identity. Reuse the existing implementation and readers when present. Allowed new code is a small reader/selector/plotter under this unit, not a kinetic solver or general adapter.

For a stored state population `y[A,q]`, emit the matching 17 columns without changing values. If instead charge fractions `f[A,q]` are stored with constant isotope abundance `Y[A]`, recover `y[A,q]=Y[A]*f[A,q]` in the **same** reference normalization. Shared electronic fractions between isotopes are permitted only when the source contract explicitly makes that approximation. Do not equate total abundance and charge fraction.

If the source uses per-Href abundances, keep that unit, or convert only with its documented constant `n_b/n_Href`. Never substitute total hydrogen nuclei for Href where nuclear reactions change the former. If baryon-normalized, define `y_i=n_i/n_b` and `n_b=sum_i A_i*n_i` over the full internal baryonic network. BBN-like appearance does not dictate normalization: label the actual plotted number fraction. Mass fractions `X_i=A_i*y_i` are a different optional observable, not the same curves.

Use saved physical proper time in seconds where available. For stored `s=ln(a)`, time conversion requires its matched Hubble history: `dt/ds=1/H`. Redshift in an anisotropic model must use the source's mean-scale-factor convention; a direction-dependent observed photon redshift is not a unique background clock. If the mapping is missing, plot the native clock, label it, and leave physical-time conversion unresolved.

Output: one isotope-grouped abundance figure with only the 17 states, a matching table, caption containing case/domain/grid and model scope, and a compact availability table. Positive populations may use a logarithmic ordinate. Exact zero is represented in an annotation/zero legend or linear inset; missing is missing. No epsilon floors, fabricated n/T curves, endpoint interpolation, hidden smoothing, or borrowed rates to fill missing columns.

Acceptance for the projection: selected columns equal their source arrays (exact copy; multiplication/normalization checked against the stated operation); source clock order and domain preserved; no negative or nonfinite data hidden; all 17 entries accounted for as present, source-zero, or missing. Source-zero n/T may be plotted/annotated as zero **only when source IC and channels enforce it**; this does not establish physical absence in the expanded network. A display operation adds zero original DAG completions.

## 3. Corrected kinetic equations for the optional next calculation

For homogeneous comoving baryons on a prescribed background, `dn_b/dt+3H*n_b=0`. With `y_i=n_i/n_b`, dilution cancels:

`dy_i/dt = sum_r S[i,r] R_r/n_b`,

where S is the stoichiometric matrix and R is a proper-volume event rate [m^-3 s^-1]. Unary photoreaction/decay: `R_r=n_b*y_a*Gamma_r`. Binary collision/capture: `R_r=n_b^2*k_r*y_a*y_b/(1+delta_ab)` when k is a per-pair reactivity [m^3 s^-1]; supplier conventions may absorb the identical-pair factor and must be inspected before use. Nuclear rates tabulated as `N_A<sigma v>` require their documented unit conversion, not direct insertion as k.

For photon number density per proper volume, energy and solid angle `N_E(E,Omega,t)`, the stationary isotropic-target photo-rate is `Gamma_r=c*integral dOmega integral dE N_E*sigma_r(E)`. For specific intensity per frequency `I_nu`, it is `integral dOmega integral dnu I_nu*sigma_r/(h*nu)`. Do not mix the two measures or add an extra 4pi after angular integration. Threshold, support and frame follow the source. Directional transport affects the local spectrum; a scalar nuclear cross section can use its angular integral on the specified isotropic-target closure.

Adjacent atomic stages contribute

`dy[A,q]/dt = I[A,q-1]*y[A,q-1] + D[A,q+1]*y[A,q+1] - (I[A,q]+D[A,q])*y[A,q]`,

with `I=Gamma+n_e*C` and `D=n_e*alpha`, plus any separately sourced charge exchange. Nonnegative rates and the complete boundary stages preserve each isotope total in the atomic-only block. The electron relation for a quasineutral plasma without other charged components is `y_e=sum_i q_i*y_i`; its sum includes displayed Li IV and any hidden charged closure species. On a fixed externally supplied n_e history, report the charge residual against the evolved populations rather than claiming self-consistent neutrality.

The image's written nuclear reactions, after correcting charge handling, can define a reduced network. Atomic arrows and nuclear arrows are different processes. Drawn horizontal edges are not charge-resolved product prescriptions. A nuclear event specification needs the nuclear daughters and their bound-electron/fast-electron disposition before it can be inserted into the 17 heavy-particle states.

Beta decay corrections (continuum beta, spectator bound-electron idealization):

`n -> H II + e^- + anti-nu_e`;

`T I -> 3He II + e^- + anti-nu_e`;

`T II -> 3He III + e^- + anti-nu_e`.

For T charge q=0 or1, the initial bound-electron count is `1-q`; the daughter nuclear charge is2, giving daughter charge `2-(1-q)=q+1`. Baryon number and total electric charge balance in each equation. Shake-off/excitation and bound-state beta branches need an explicit source/model when relevant; these corrections are not a lifetime calculation. Recombination can later produce H I or He I. The diagram's n→H I arrow cannot be used as the immediate beta-decay stoichiometry.

The reverse of neutron beta decay is not a single unqualified nuclear rate. At BBN temperatures a source must supply the full relevant weak channels and lepton distributions; late-time inverse weak effects cannot be inferred merely by reversing the drawing. A nonthermal photodisintegration spectrum likewise does not justify obtaining its reverse capture rate by thermal detailed balance.

## 4. Smallest optional calculation and stopping rule

Priority is a **stored-history observable**, then a **one-way diagnostic**, then a new IVP only if separately approved. A one-way diagnostic can compute prescribed parent event exposures `F_r=integral Gamma_r dt` and first-order abundance changes `delta y_i=sum_r S[i,r]*integral R_r[y_saved]/n_b dt`. This is a perturbative response, with rates/parents/background frozen. It is not the nonlinear coupled solution and does not supply reliable large-depletion curves. If the response becomes negative, is large relative to a participating positive parent abundance, or violates the frozen-background premise, retain the diagnostic and stop; do not clamp or present it as kinetics. A numerical applicability tolerance must be fixed before this calculation, not invented after seeing its result.

A true reduced solve requires named arrays/functions for `H(t), n_b(t), T(t), J(E,Omega,t)` and, if prescribed, `n_e(t)`; named rates with valid ranges; initial isotope totals/ion fractions; explicit Li closure; nuclear daughter charge routing; and finite time domain. Missing source arrays remain missing. Source-off and zero-rate analytic limits plus conservation/positivity are the minimum targeted checks. Numerical accuracy tolerances belong to the original reused source, or must be specified for the new problem before execution. No new accuracy PASS is asserted here.

Frozen-background evolution avoids the new physical EOS obligation because T is an input. It cannot claim a newly self-consistent thermal/Einstein solution. A MeV nuclear source needs its own high-energy photon/cascade data; the earlier UV-only stored history cannot be relabeled as a photonuclear history. Existing CR113/BASS reservations and unfinished supplier work remain with their owners.

## 5. Three physical axes and current status

| Axis | Check and observable connection |
|---|---|
| Symmetry/gauge | Use scalar abundances in the source normal tetrad and its proper-time/volume convention; preserve mean-scale-factor clock and angular weights. Relabeling time with its exact Jacobian cannot change populations at the same event. Frozen anisotropic DM/H/shear are reused only with matching donor identity. No new gauge, tilt or Einstein feedback is introduced. |
| Invariants | Atomic columns have zero isotope-total sum. Nuclear columns satisfy `A^T S=0`. Including emitted electrons gives `Q^T S=0` for charge. Hidden internal stages remain in sums. With injection/escape, energy follows the source ledger; do not impose a closed-system energy constant. Positivity and baryon conservation are necessary, not a continuum-error proof. |
| Observables | Main output is `y[A,q](t)` in an explicitly named normalization. Atomic-only evolution changes charge partitions, not isotope totals. A BBN abundance plot changes nuclear totals; a reionization plot can have similar graphics with different dynamics. Interval optical depth, electron fraction and temperature are auxiliary only when their matched history exists. |

Current result: **derived contract; literature-supported route selection; numeric/plot execution NOT_RUN by this theory agent**. Saved-history recovery/admission is pending controller intake. Wolfram context was called but its automatic tritium numerical interpretation was rejected; no CAS validation is claimed. R1–R5 and R9 scope are covered by this contract/source analysis; R6 independent review and R7 actual projection/diagnostic checks are pending. R8 decision is adopt projection-first preparation, not physical admission; R10 handoff is this contract. The global working/central counts are the inherited **33/88 and 28/88**, with **0 new completions**. No strong no-go theorem or new novelty claim is made.

Theory input references: image `upload/원시 광핵반응 및 재이온화 네트워크(10).png`; prior `research/rei_next_loop_20261028/intake/WORK_THREAD_PROMPT_KO.md`, `HANDOFF_KO.md`, `REPORT_KO.md`, `FINAL_DELIVERY_RECEIPT.json`; source comparison and owner caveats in prior `intake/synthesis.md`. Their original evidence remains unmodified.
