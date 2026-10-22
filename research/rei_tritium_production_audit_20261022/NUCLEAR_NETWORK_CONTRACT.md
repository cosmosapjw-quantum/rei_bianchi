# Complete dossier nuclear source accounting with declared Li closure

This extension implements all sixteen nuclear/capture/decay labels in the supplied nineteen-reaction drawing. The drawing has three duplicate forward/inverse descriptions, so its sixteen labels map to thirteen physical families. Five declared closure families make eighteen. The exact coefficients, identifiers, units, source selection and acceptance values are in `NUCLEAR_NETWORK_CONTRACT.json`. The preceding DD-only contract and its completed artifacts remain unchanged.

## R1 — Finite problem and executable result

Compute source and sink fluxes for every admitted family, including physical thermal inverse two-body reactions, while reusing the 82 saved cosmological histories. The selected model is a conditional **instantaneously thermalized all-bare nuclear sensitivity**. All isotope nuclei enter bare-nucleus reaction kernels regardless of their saved electronic charge states. This mode is deliberately different from the preceding DII-only DD calculation; it is not an inferred ionization history.

The finite inventory is n, H1, D, T, He3, He4, Li6 and Li7, with baryon-normalized abundance `Y_i=n_i/n_B`. The selected reaction list is closed under products. It is not a claim to include every possible physical reaction involving these nuclei: pp weak fusion, Be7 production/decay and other listed exclusions remain outside this finite model. All dossier obligations are retained as aliases; aliases never double-count an event.

## R2 — Evidence and source applicability

Reuse the pinned drawing transcription, the old isotope inventories and saved histories. `nuclear_intake/RUN19_target_network.json` was fetched at the frozen PR219 head. `RUN19_full_network.rs` was inspected: despite its name, it implements atomic photo/collisional/charge-exchange physics, not these nuclear channels. `R5_DONOR_BBN.json` is a BBN abundance output at 1 keV, not a cross-section provider at 100–10000 K. The separate `../rei_full_nuclear_source_intake_20261022/PROVIDER_CODE_INTAKE.md` records additional donor inspection.

The forward charged kernels use primary/evaluated low-energy S-factor constants. They are explicit constant-S continuations; the literature's tabulated BBN/stellar temperature fits are not evaluated outside their stated ranges. The Maxwellian Gamow window here is below available charged-particle laboratory data. Thermal neutron coefficients use explicitly assumed 1/v continuation. Energetic DD neutrons and tritons are placed instantaneously into this thermal population by the selected closure, not by an inferred stopping calculation. `NUCLEAR_PROVIDER_INVENTORY.md` records values and unresolved physical refinements.

## R3 — Canonical event ownership

| Physical family | Dossier labels | Extra closure role |
|---|---|---|
| He3(n,gamma)He4 | 4 | — |
| T(p,gamma)He4 | 5 | — |
| D(D,gamma)He4 | 6 | — |
| D(p,gamma)He3 | 7, 13 | — |
| p(n,gamma)D | 8, 12 | — |
| T beta decay | 9 | — |
| n beta decay | 10 | — |
| T(alpha,gamma)Li7 | 11, 19 | — |
| D(D,p)T | 14 | — |
| D(D,n)He3 | 15 | — |
| T(D,n)He4 | 16 | — |
| He3(D,p)He4 | 17 | — |
| He3(n,p)T | 18 | — |
| D(alpha,gamma)Li6 | — | Li6 formation |
| Li6(p,alpha)He3 | — | Li6 loss to represented nuclei |
| Li6(n,alpha)T | — | Li6 loss and additional T source |
| Li7(p,alpha)He4 | — | Li7 loss to two alpha particles |
| D(n,gamma)T | — | Additional neutron-fed T source |

Each capture's reverse photodisintegration is represented. Each binary-transfer family's reverse is included by the thermal detailed-balance prescription below. The two beta decays are one-way because this model supplies no inverse weak bath.

## R4 — Rates, masses and inverse factors

For reactant multiplicities `a_ir` and product multiplicities `b_ir`, define `nu_ir=b_ir-a_ir` and `sym_r=product_i factorial(a_ir)`. A two-body forward event rate per baryon is

`F_r = n_B k_r(T) product_i Y_i^a_ir / sym_r`,

and a one-body decay event rate is `F_r=lambda_r Y_parent`. Thus `dY_i/dt=sum_r nu_ir F_r`; `dY_i/dx=(1/H)dY_i/dt`. The event rate, source/sink inventory, nuclear charge and Q ledgers have a single owner.

For charged bare nuclei, use the generalized constant-S shifted Maxwell integral in the preceding `PHYSICS_CONTRACT.md` with `mu=m_i m_j/(m_i+m_j)` and `E_G=2 mu c^2 (pi alpha Z_i Z_j)^2`. Internal units are SI. The saved output includes log rates and log event fluxes even when corresponding linear values underflow. Thermal 1/v neutron models have constant `k=sigma_2200 * 1e-28 * 2200 m^3/s`.

For a binary reaction `i+j -> k+l` releasing Q>0, Maxwell-Boltzmann ground-state reciprocity gives

`k_reverse/k_forward = (sym_products/sym_reactants) * (g_i g_j)/(g_k g_l) * (m_i m_j/(m_k m_l))^(3/2) * exp[-Q/(kB T)]`.

This follows by equating forward and reverse event rates at chemical equilibrium, including pair-count factors. It assumes a common thermal temperature, nondegenerate nuclear populations, time-reversal-invariant nuclear dynamics and no excited-state partition contribution. `g=2J+1` is fixed in the JSON. The thermodynamic mass-product ratio uses the same nuclear mass table as Q; using a reduced-mass ratio with inconsistent total-mass approximations is not an identical convention. Forward and reverse event rates each retain their own symmetry divisor. Compare the log relation with an ULP-scale floor when `Q/(kBT)` is very large.

Use precise neutron/proton/deuteron/triton/helion/alpha masses from the available SciPy physical-constant table and serialize their values. Lithium masses are NIST neutral atomic masses minus three electron masses, neglecting atomic binding energy. This declared small mass approximation affects lithium Q values; it is not precision nuclear mass evaluation. The common mass table makes reaction-cycle energy accounting algebraically consistent. Q is computed from rest-mass differences, subtracting a beta electron rest mass for weak decays.

## R5 — Radiation and energy closure

The external spectrum has support 5–60 eV. All admitted photodisintegration thresholds exceed that support, so their **external-spectrum** integrals are exactly zero. This is a structural support result and receives a distinct zero-reason flag. Endothermic thermal inverse two-body rates have finite negative logarithms; floating-point underflow does not turn them into structural zeros.

Nuclear capture photons are assigned to an escaping radiation ledger. They do not re-enter the external UV spectrum or trigger secondary photodisintegration in this mode. Gas temperature is prescribed, not solved. The signed event Q ledger therefore reports available nuclear energy, not instantaneous gas heating. Beta electrons and antineutrinos are counted; missing kinetic/neutrino/atomic-shell partition is marked unresolved. There is no duplicate addition to the existing atomic heating or Einstein background equations.

## R6 — Constructive fast subsystem and passive bulk

The six nonzero background isotope reservoirs H1, D, He3, He4, Li6, Li7 are fixed for coefficient evaluation. T and n are evolved together from zero. All selected terms involving them are linear at fixed bulk reservoirs:

`dot n = b_n - a_n n + c_Tn T`,

`dot T = b_T + c_nT n - a_T T`.

`b_n` contains DDn; `b_T` contains DDp. Each capture/decay/inverse supplies its actual loss hazard. `c_Tn` contains DT fusion and the thermal inverse of He3(n,p)T and Li6(n,alpha)T. `c_nT` contains He3(n,p)T, Li6(n,alpha)T, D(n,gamma)T and the thermal inverse of DT fusion. Remaining T/n captures and inverse DD reactions are sinks. The JSON reaction registry, rather than a manually incomplete list, must generate these contributions.

The matrix is Metzler: off-diagonal rates are nonnegative. Beta decay provides true loss in both populations; capture cannot create two fast parents from one within this list. The frozen matrix exponential is positive. An exact piecewise-frozen matrix/source propagator or quantified fast-asymptotic method avoids resolving seconds/years by cosmological IVP steps. Preserve the initial zero inventory and check the turn-on transient. At constant coefficients, with determinant `D=a_n a_T-c_Tn c_nT>0`, the nonnegative stationary solution is

`n_eq=(a_T b_n+c_Tn b_T)/D`,

`T_eq=(c_nT b_n+a_n b_T)/D`.

This supplies a useful log-domain check, not permission to erase transient history. Count secondary births through the coupled system: the earlier first-generation neutron envelope is not a bound on this recycling network.

All bulk changes are obtained from the same signed event ledger. Tiny changes must be preserved as separate production and destruction extents, because adding them to an order-unity float may round them away. Before admitting passive-reservoir results, require gross production and gross destruction of **each** nonzero bulk isotope, divided by that isotope's initial abundance, to remain below 1e-6. Checking only baryon normalization or net cancellation is insufficient. If the criterion fails, the passive approximation is not admitted; upgrading to a fully coupled bulk solve requires a separate numerical contract.

## R7 — Finite discriminating checks

Check all sixteen dossier IDs exactly once after aliases; eighteen families; integer A and lepton-completed Z conservation; exact identical-pair factors; source units; rates and their structural-zero status; old DD kernel parity at 100/1000/10000 K with the same deuteron mass; independently tightened quadrature; detailed-balance statistical factors including DD and identical-alpha controls; zero-parent and positive-parent controls; isolated one-parent decay and constant two-parent hazard solution; passive bulk turnover; and event-ledger conservation.

Run all 82 immutable histories once and one reconstruction refinement. The acceptance threshold is 0.02 dex for cumulative events, with exactly zero/absent-parent channels tested by zero status instead of an undefined relative error. If needed, allow one 4x refinement, not a background rerun. A finite positive log for a populated channel satisfies positivity even when its linear value is below the representable range. Numerical rates, source uncertainty and uncomputed physical mechanisms remain separate.

For cumulative event flux use analytic log-linear interpolation in proper time. With endpoint logs `a,b` and `d=abs(b-a)`, an interval contributes `log(dt)+max(a,b)+log(1-exp(-d))-log(d)`, with equal-log limit `log(dt)+a` and explicit zero-endpoint handling. This resolves the extremely narrow endothermic endpoint layer that a linear-flux trapezoid would repeatedly miss. It does not relax the all-finite-channel 0.02 dex criterion. The event reconstruction and fast-system source reconstruction must be named separately; their endpoint inventory/count difference is a reconstruction diagnostic, not an exact identity at 1e-10 when their interpolants differ. Exact event-wise A/Z identities still apply.

## R8 — Claim admission

The intended result is a numerical conditional sensitivity for all dossier families plus the declared five closure families. It answers whether the original exact-zero T statement survives explicit nuclear source terms in this stated model, and which pathways dominate its formation and loss. It does not establish a confidence interval, an empirical low-temperature prediction, every light-nuclear reaction, or a production-default model. Every numeric result must carry the all-bare/instant-thermalization/passive-reservoir scope.

## R9 — Implementation handoff

The machine JSON is sufficient to execute: coefficients, reactions, masses/spins, Q convention, inverse prescription, input paths, limits and tolerances are frozen. `nuclear_network.py` is the lower-tier implementation owner. Its report must contain a per-family ledger, T and neutron surviving inventories, cumulative births/decays/captures, bulk turnover, Q and beta-electron ledgers, numerical convergence checks, zero reasons and provider identifiers. Compare DD contributions with the preceding DII-selected result as a change of reactant-population assumption, not a solver disagreement. Do not use the old isotope `lift()` for new T.

## R10 — Stopping and continuation

Zero new cosmological IVPs; one nominal sweep plus one refinement, one conditional extra refinement only for a failed resolution check, at most six new figures and one targeted repair. Preserve outputs and pass them to the fresh independent reviewer. Missing fast transport, screening, minor radiative branches and reactions beyond the declared closure do not become fabricated zeros; they are separate provider/model obligations. This completes the finite executable contract; scientific admission awaits actual implementation outcomes and review.
