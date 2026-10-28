# Frozen phenomenological external-source contract, v1

2026-10-28. Scientific authority requested: Astra; actual runtime identity is not independently observable. Selected research scope R2–R10, using previous prerequisite evidence. This is an executable prescribed-background, open-system source model and frozen-epoch n/T response, not a new trajectory or calibrated prediction. No new IVP, rate integration campaign, or alteration of old Li6 closure. Original DAG working33/88, central28/88, fast4/7 and main595.225063/600 remain unchanged. F4's **phenomenological source-model subobligation** can close after implementation and independent acceptance; historical physical F4 remains distinct.

## 1. Inputs, conventions and outputs

Read `research/rei_fast_selected_20261028/outputs/grid044_M4_nominal_all21_populations.csv` (201 rows). Use executor's already verified baseline manifest and record the actual file digest once. Reuse its per_Href columns in the exact state order

`[n, H1_0,H1_1, D_0,D_1, T_0,T_1, He3_0,He3_1,He3_2, He4_0,He4_1,He4_2, Li7_0,Li7_1,Li7_2,Li7_3]`.

Let A=`[1,1,1,2,2,3,3,3,3,3,4,4,4,7,7,7,7]`, q=`[0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3]`. The four hidden Li6 columns are copied unchanged and no new event touches them. The comoving reference satisfies dot(n_ref)=-3H n_ref; y_i=n_i/n_ref. This reference is **not** the evolving total baryon density when matter is injected. Use the matching saved `nHref` array in `research/rei_fast_selected_20261028/inputs/angtherm_selected/research/rei_angular_thermochemistry_20261023/results/grid044_M4_nominal.npz`, in cm^-3; the source code loads its physical background from `nH_ref_cm3`. Verify that its201eta values equal the CSVeta at the existing serialization precision (absolute5e-15), all nHref are positive finite, and record endpoints. Missing/mismatched data stop this path; no synthetic density fallback. This amendment supersedes the provisional illustrative density law. All event rates r are events/Href/proper-second; y is particles/Href; photon/CR flux F is angle-integrated number/(cm² s), so there is no extra 4pi or c. Energies in eV, cross sections cm², hazards s^-1. No eta-to-time conversion or cumulative event integration is performed.

Output a201-row CSV with each channel rate, 17-vector new-source derivative at baseline, fast n/T stocks, thermal n/T QSS, direct beta daughter rates, absorbed photon number and energy, escaped number and energy, heat/radiation/neutrino/fast-electron/atomic-internal ledgers and balance residuals. Produce one compact response figure vs mean z for source-family rates, n/T QSS, slowing/escape branching, and energy channels (signed energy book entries may need separate panels). Label all amplitudes **illustrative, uncalibrated** and all responses **frozen-epoch QSS; not a time-evolution solution**. Retain exact zeros.

## 2. Unified operator and external reservoirs

`dot y = f_old(y,t) + I_thermal - diag(kesc_i)y + sum_c nu_c r_c + e_n ks,n B_n + e_TII ks,T B_T`.

For this evaluation report only the new-source contribution, not a re-evaluated f_old. Old beta ownership is removed from any future assembled f_old before adding the beta columns below; no old operator is actually modified here. `B_n,B_T` are separate fast particles/Href, never counted again in thermal n/T. `dot B_j=S_fast,j-L_fast,j B_j`, `L_fast=ks+ke+lambda/gamma`. Freeze-epoch `B=S_fast/L_fast`. `S_fast` includes injected fast particles and nuclear daughters. Record branch fluxes `ks B`, `ke B`, `(lambda/gamma)B` separately. Take gamma=1 (nonrelativistic lifetime approximation), ks,n=1e-2, ke,n=1e-3, ks,T=1e-8, ke,T=2e-9. These phenomenological hazards deliberately distinguish neutral and charged transport. They approximate energy-averaged transport with finite escape, not instantaneous thermalization. No cosmological transport/redshifting or spatial gradients are solved.

External photon bins are replenished reservoirs: their absorption drain is `n_ref sum r`, and sustaining them requires external emissivity of that magnitude plus any propagation loss. The specified F below is a prescribed local field, not an emissivity already transported. Fresh photons are supplied continuously at each epoch; no new cohort is inserted into an aged initial packet. A finite-reservoir implementation would require photon transport and is outside this evaluation.

Open matter ledgers subtract injected baryon/charge/energy from external reservoirs and add escaped quantities to them. Supply q electrons per injected charge-q thermal/fast ion and remove q electrons with an escaped ion, preserving neutrality without inventing an unbalanced external current. Fast injected T is bare(q=1); fast n has q=0. Stable nuclear daughters thermalize promptly in this closure, while n/T use finite reservoirs. Escape of thermal species has common kesc=1e-18 s^-1 for all17states. External-off tests switch all external photon,CR,injection and escape amplitudes to0; intrinsic beta/capture may remain on for a nonzero test state.

## 3. Explicit finite photon operator

Bins `(E_eV,F_cm-2_s-1)` are `(20,1e4),(100,1e3),(5e6,1e-2),(25e6,1e-2)`. A single amplitude alpha multiplies all F and all injected/CR source amplitudes; alpha=0,1,10 are the finite sensitivity choices. Escape hazards do not scale with alpha. No continuous spectral quadrature.

For each atomic transition q→q+1, `sigma(E)=sigma0*(I/E)^3` for E>I and0 otherwise; r=F sigma y_parent. Thresholds by isotope are H,D,T:[13.6]; He3,He4:[24.6,54.4]; Li7:[5.4,75.6,122.4]eV. sigma0=6.3e-18cm² for every transition is an explicitly illustrative common normalization. Atomic event removes parent, adds next ion and one free fast electron. Allocate I to atomic internal energy, E-I to fast-electron energy; no immediate heat. Both terms sum to absorbed photon E. This hydrogenic-tail toy is not an evaluated many-electron cross section.

Photodisintegration family parameters `(parent, products,Q_eV,sigma0)`:

| parent | fully stripped products | Q (eV) | sigma0(cm²) |
|---|---|---:|---:|
| D | HII + fast n | -2.2246e6 | 1e-27 |
| He4 | HII + fast T | -19.8139e6 | 1e-27 |
| He4 | He3III + fast n | -20.5776e6 | 1e-27 |
| Li7 | He4III + fast T | -2.4670e6 | 1e-27 |

For each parent charge q, let Bstrip=sum of that parent's ionization thresholds from q onward (zero for bare parent), Ereq=-Q+Bstrip. Nuclear toy sigma=`sigma0*(1-Ereq/E)^2` for E>Ereq else0. These are heavy-target approximate energy thresholds; no exact lab recoil threshold assertion. Each event releases Z_parent-q spectator electrons by explicit full stripping. Heavy-charge gain relative to consumed target is Z_parent-q; free-electron number gain is identical. Store Bstrip in atomic internal ledger, -Q in nuclear rest/binding ledger, and K=E-Ereq as kinetic budget. Half K feeds the fast n/T kinetic reservoir and half goes to prompt heat of stable daughters. Thus E=(-Q)+Bstrip+K exactly. The fast kinetic reservoir's source power is the sum of these half-K rates (plus direct fast injection below). Its QSS mean energy is P_fast/S_fast if S_fast>0, else0; use the same hazard fractions for particle and kinetic-energy flow. Slowing deposits that kinetic fraction to heat, escape carries it outward, and fast beta sends that pre-existing kinetic fraction to heat under the prompt-retention assumption. Beta Q is a separate entry below. Released spectator electrons have zero assigned excess energy beyond stripping cost in this toy.

## 4. Ion/isotope injection and CR secondary kernels

Thermal injection perHref/s at alpha=1: HI=0,HII=1e-20; DI=7e-25,DII=3e-25; TI=2.5e-29,TII=7.5e-29; He3I=0,He3II=2e-26,He3III=8e-26; He4all=0; Li7I=0,Li7II=2e-31,Li7III=3e-31,Li7IV=5e-31; n=1e-27. These explicitly define normalized isotope charge distributions; charge probabilities are assumptions, not recovered donor data. Thermal injection has zero excess kinetic energy; account injected matter's mass/binding separately if a total energy convention is needed. Fast injection n=1e-25,TII=1e-27 perHref/s, each with K=1e6eV/particle. Fast reservoir electron supply for T injection is one per ion.

External CR protons: E_CR=1e8 eV, F_CR=1e-2 cm^-2 s^-1. Two channels on every He4 charge state:

`p_ext + He4_q -> HII + He3III + fast n + (2-q)e_free`

`p_ext + He4_q -> 2HII + fast T + (2-q)e_free`.

Each has sigma=`1e-26*(1-3e7/E_CR)^2` for E_CR>3e7 else0, and r=F_CR sigma y_He4q. This30MeV cutoff is a phenomenological support cutoff, not an exact threshold. Q=-20.5776MeV for n-channel, -19.8139MeV for T-channel. Ereq=-Q+Bstrip, K=E_CR-Ereq; reject an admitted event if K<0. As above halfK enters fast daughter reservoir, half prompt heat; -Q nuclear ledger and Bstrip atomic ledger. The projectile contributes exactly +1 net baryon and +1 net heavy charge to the matter system per event; subtract one proton from the external CR reservoir. Inject one compensating electron per consumed external CR proton. The additional 2-q electrons come from stripping the target. Thus Δq_heavy−Δelectron=0 including external compensation. The outgoing HII includes the retained projectile and is not also added as an independent injection. This finite two-channel kernel is an explicit inclusive-yield model, not a CR energy-density-to-rate shortcut.

## 5. Weak decays, capture and thermal QSS

Use lambda_n=1/878.4s; lambda_T=ln2/[12.312*365.24219878*86400s]. Thermal beta columns: `n->HII+e_fast+antinu`, `TI->He3II+e_fast+antinu`, `TII->He3III+e_fast+antinu`. Each preserves A, increases heavy charge by1 and electron count by1. Fast n/T beta creates HII/He3III respectively with the same electron/antineutrino counts. There is no HI directly from n beta. Atomic spectator electrons of TI are retained. Adopt beta Q_n=782333eV,Q_T=18590eV, partition electron fraction1/3 and antineutrino fraction2/3, zero recoil at this approximation. These fractions are illustrative, not beta-spectrum integration. Debit nuclear rest energy by Q and credit electron/neutrino energy; do not call all Q heat. T bound-state/ionization shifts of beta Q are neglected explicitly at eV/keV order.

Neutron capture: `n+HI->DI+gamma`, `n+HII->DII+gamma`. r_q=n_ref*y_n*y_Hq*C, C=0.3326e-24*2.2e5 cm³/s; fixed2200m/s1/v continuation; no newly integrated rate. Qcap=2.2246e6eV all to escaping radiation; debit nuclear rest byQcap. Ignore atomic isotope binding shifts. kcap=n_ref*(y_HI+y_HII)*C. No D-to-T capture or T-burning channel is included in this finite model; previous18-family conditional network is not silently merged.

For thermal n QSS, `S_n=I_n+ks,n B_n`, `L_n=lambda_n+kcap+kesc`, `y_n*=S_n/L_n`. For T define `S0=I_TI`, `S1=I_TII+ks,T B_T`, L=lambda_T+kesc, Gamma=sum F sigma_T, rrec=1e-14s^-1 illustrative. Define T recombination `TII+e->TI+gamma`, energy13.6eV escaping radiation with corresponding atomic-internal debit (electron kinetic energy neglected). Then

`D=L*(L+Gamma+rrec)`;

`TI*=((L+rrec)*S0+rrec*S1)/D`;

`TII*=(Gamma*S0+(L+Gamma)*S1)/D`;

`TI*+TII*=(S0+S1)/L`.

Report new-source derivatives twice if useful: at original baseline (n=T=0), and at a coefficient-frozen state replacing only n,TI,TII with these QSS values. The latter does not modify saved baseline and its stable daughter growth is a derivative, not an evolved abundance. No QSS equilibrium claim for stable species. Parent targets outside n/T remain frozen, and their depletion is still reported in event derivatives. Capture and T recombination are internal terms with their own switches for external-only off test. No inverse weak bath is specified; inverseweak NOT_INCLUDED_BY_MODEL, not physically forbidden or measured zero.

## 6. Acceptance and finite execution

Allowed: implement this contract in new unit only, one bounded test run (root allocation4CPU s), one201-row evaluation (3CPU s), one plot (3CPU s); actual root wrapper and cumulative ceilings control. No auto reruns or IVP. Tests:

1. Exact integer A/q stoichiometry for each event including fast species, spectator electrons, CR/projectile and injection/escape boundary entries. A residual exactly0 for closed columns; CR internal ΔA=+1 balanced by external−1. Beta heavyΔq=+1 with electron+1. Li6 mapping unchanged byte/content as appropriate.
2. Per-event scalar energy identity at all admitted energies and target charges; numerical tolerance1e-12 relative to max(1,total incoming eV), absolute1e-12eV. Includes beta/capture/recombination nuclear or atomic internal entries, so no claim is based on kinetic terms alone.
3. Strict zero cross sections at/below each threshold; positivity for nonnegative state and source; generator off-diagonal coefficients nonnegative at frozen targets. Use boundary-component test `y_i=0 -> dot y_i>=0` with its own sinks absent. No claim of arbitrary explicit-Euler positivity.
4. Fast branching fractions sum1 within1e-14; limiting ks→0 and ke→0 checks against formulas; positive QSS and nonzero sink denominators. Solve3-component frozen QSS residuals with relative scale=max source and sink rates, tolerance1e-12 (zero case exact). Ttotal identity within1e-12. Alpha0 gives zero n/T QSS and external rates, even if baseline capture/decay operators are retained; intrinsic QSS starts source-zero.
5. Independent direct rate spotchecks at first/middle/last epoch; all201rows finite; source17mapping with LiIV present and Li6 absent from new coupling. Off means all external powers0, and escape disabled for the complete new-external derivative-off test. External photon amplitudes scale Gamma and photorates linearly; QSS total T scales linearly while ion fraction need not. Record alpha0,1,10 curves or table, not a fitted uncertainty band.

The fixed-epoch QSS assumption requires reservoir/thermal relaxation times shorter than coefficient-variation times. Report tau_fast=1/Lfast, tau_n=1/Ln, tau_T=1/L; a real validity assessment needs the background timescale and source history, which this pointwise demonstration does not infer. No continuum convergence claim is required for algebraic formulas.

## 7. Scientific axes and evidence status

Symmetry/gauge: populations and event rates are local scalar quantities in the existing comoving tetrad and proper time; isotropic prescribed angle-integrated flux is an added closure. No gauge-dependent potential or observed directional redshift enters. Mean z labels saved epochs. A future anisotropic radiation extension must retain angular transfer rather than interpret this scalar bath as directional data.

Balance laws: closed nuclear events preserve baryon number; beta changes charge only with explicit emitted electron; atomic stages exchange free/bound electrons; open injection/escape obey source-sink balance rather than fixed total normalization. Photon/CR absorption and weak/capture/recombination energy have explicit owners and signs. Binding/rest bookkeeping is an effective Q-value convention, with recoil and isotope binding refinements deliberately omitted.

Observables: model outputs are abundances perHref, source/event rates and allocated powers. Photon absorption is a local drain/emissivity requirement; no optical depth, luminosity distance, line intensity or observed spectrum is inferred without forward transport. A meaningful new result is evaluated external-source rates and finite-survival n/T response under stated knobs.

Symbolic check actually executed through Wolfram Language evaluator: eight bare nuclear/weak/capture columns returned baryon residuals all0 and heavy-charge residuals `{0,0,0,0,1,1,1,0}`; inverse two-species loss matrix returned `{(d*s+b*t)/(a*d-b*c),(c*s+a*t)/(a*d-b*c)}`; fast fractions simplified to1. Wolfram context lookup errored internally; evaluator succeeded, no retry needed. This is tool-assisted algebra, not independent physical calibration. Literature intake and independent implementation review are separate evidence. Remaining scientific obligations after scoped pass: calibrate spectra/yields/cross sections and charge probabilities; solve transport or justify fitted effective hazards; validate source history/QSS timescale; then separately authorize dynamics if wanted. Those obligations do not block completion of this explicitly phenomenological pilot.
