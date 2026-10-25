# REI-CHEM-LEDGER-01 frozen scientific contract

Date 2026-10-25. Scientific authority role requested Astra; runtime model UNOBSERVED. Central source snapshot c5050305f84a051cb797cd84c84768c76bcb18b9, fixed historical authority 0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17, AGENTS blob429a5a13ee75b1222bc50627f8d5973d01dd21c4. Root selects this separate new bounded unit. No source fitting, IVP, physical chemistry prediction, donor recomputation, NCP, ANGTHERM mutation, or completed 83-case replay.

## Objective and exact novelty

Construct an isotope-resolved reaction interface with molecule composition, signed ionic charge, explicit thermal/fast electrons, conservative energy basis, and event ownership. Existing C23C exact CI/PI/RR and L0 energy cancellation are reused background. New functionality is arbitrary finite composition vectors, negative ions, molecular signatures, separate electron pools, duplicate-equivalence diagnostics, and proof-backed change of energy-reference invariance. Atomic authority inspected current C23C implementation: single nuclide species and charge0..Z, fixed CI/PI/RR rungs; none of this molecule/interface functionality is present there. This is scoped novelty relative to inspected sources, not a literature novelty claim.

## Allowed files and execution

Only `research/rei_chem_ledger_20261025/**` in the root-supplied staging sandbox; no existing checkout is available and no clone is requested. Publication later adds this owned leaf to the current central tree. Files: `chem_ledger.py`, `fixtures.json`, `run_checks.py`, `run_bounded.py`, `README.md`, `plot_saved.py`, `figures/**`, and `raw/**`. Copy this contract and `THEORY.md` unchanged into `authority/`. Implementation may use Python standard library only (`fractions`, `json`, `dataclasses`, `math`, `resource`, `subprocess`, etc.). No rate libraries or numerical integration. Root publishes only after independent review.

One scientific child; one worker, one thread. New separate-unit cumulative scientific CPU cap30s, wall120s, memory512MiB. These are maximum limits, not an instruction to spend them. A preparatory import/syntax check is allowed and separately measured; include all fixture/test computation in the child debit. The runner must record actual child user+system CPU, wall, exit, peak RSS and counts. Timeout terminates this task child only. Preserve first raw output/failure. No automatic retries or historical budget resets. After a substantive ambiguity/failure return to authority with exact row; do not invent tolerances, input values, model choices, or repair. Root may authorize one targeted repair separately; it must fit the same cumulative cap. Historical L0 known partial11.449628s, whole debit UNKNOWN_NOT_ZERO, old10.110448/10s overrun preserved; unrelated ANGTHERM/GRID044 allowances do not transfer.

Commands from repo root, after source creation:

```
python3 -m py_compile research/rei_chem_ledger_20261025/chem_ledger.py research/rei_chem_ledger_20261025/run_checks.py research/rei_chem_ledger_20261025/run_bounded.py
python3 research/rei_chem_ledger_20261025/run_bounded.py --cpu-seconds 30 --wall-seconds 120 --output research/rei_chem_ledger_20261025/raw
```

Existing `raw/attempt.json` makes the runner return `ALREADY_ATTEMPTED` without computing fixtures. Code/source manifest, contract and fixture input SHA are recorded before child execution. After that child, a single standard-library SVG render from saved exact residuals is allowed as postprocessing within the same cumulative30CPU/120wall budget, with separate timing; panels show isotope-count, charge and energy residuals separately, and labels distinguish intended rejected cases from passing cases. The renderer must not recompute scientific fixtures. Actual SVG inspection/rendered preview by independent review is required. This is proportional reproducibility bookkeeping, not a new custody gate.

## Definitions and conventions

Metric (-,+,+,+); c,hbar,kB retained conceptually. This local scalar unit does not evaluate metric dynamics. Nucleus key is `(Z,A,isomer)` with nonnegative integer Z, positive integer A>=Z, and nonempty explicit isomer token (`ground` default only when supplied). Neutron `(0,1,ground)` is a nucleus label. A species is `(composition,charge,state,pool)`: composition is sorted positive integer multiplicities of nucleus keys; ionic charge q is signed integer in units of elementary positive charge; state is an explicit token; pool is `material`, `electron_thermal`, or `electron_fast`. The two electron species have empty composition, q=-1, and distinct pool. Material species require nonempty composition and q<=sum Z_i a_is; negative q is accepted as formal bookkeeping. Admitting that schema never establishes a physical bound state or rate. Photons are separate radiation energy/count reservoirs, not negative-charge material species. State/isomer/pool cannot be dropped in identity.

Actual baseline catalog: n; H1,D,T at q0,1; He3,He4 at q0,1,2; Li6,Li7 at q0,1,2,3:21 populations. Electron pools are two extra material-ledger rows, not extra nuclear population claims. Add synthetic species H1−, H1H1, H1D, Li7H1, He4H1+ for fixtures. Core supports finite supplied catalogs of arbitrary (Z,A,isomer), not a hardcoded8-nucleus universe. A held synthetic C12/13 molecule example verifies extensibility without claiming actual carbon inputs. Physical target catalog extension remains owner-supplied.

Reaction r stores separate nonnegative integer reactant and product multiplicities, direction, physical-process tag, event normalization, provider identity/domain, and an ownership slot. Stoichiometric column nu_sr=products-reactants. Do not divide integer coefficients by their gcd: two identical events per row is a different event normalization. Preserve catalysts appearing on both sides in canonical reactant/product signatures even when nu=0. Net nu alone is not a full physical reaction identity.

For chemical channels, isotope count matrix A_is and charge row q_s obey A nu=0 and q^T nu=0 exactly. Nuclear channels are explicitly typed `nuclear`; they require baryon row b_s=sum_i A_i a_is conserved and charge conserved, but isotope rows may change. This compiler reports nuclear isotope delta without treating it as chemical conservation. Physical nuclear Q/branches/energy remain unsupported unless a future provider supplies them. The present nucleus-conversion fixture is an algebra control only.

Species abundance x_s=N_s/N_ref is dimensionless; event rate r_j is events per reference nucleus per proper second. Then dx/dt=nu r, units s^-1. If a supplier rate is per target per second, an explicit target x_s multiplier is required; if per volume per second, divide by n_ref in m^-3 with explicit conversion. This unit accepts already normalized rates and must reject missing normalization labels, not infer them.

Energy epsilon_s is eV per particle, internal energy relative to free constituent nuclei and free electrons; synthetic values below are exact rationals and never physical threshold data. Electron internal energy is0; each electron pool has a distinct kinetic reservoir. Material stored internal energy per reference nucleus is I=epsilon^T x. For channel j, DeltaI_j=epsilon^T nu_j and Q_j=-DeltaI_j. Kinetic/radiation/source reservoir increments dE_Aj (eV/event) obey epsilon^T nu_j+sum_A dE_Aj=0. Positive increment means energy enters that reservoir. The ledger explicitly lists thermal gas, fast electrons, radiation, and external source; absent contributions must be declared zero. Nothing maps fast electron energy into heat implicitly. A diagnostic bolometric tally is not an additional physical energy owner.

Charge: track electrons explicitly once. A separate neutralizing reconstruction is a diagnostic `sum_material q*x - x_e_th - x_e_fast`; do not add an electron source once explicitly and again via reconstruction. For signed JVPs the same matrix identities apply, without requiring tangent entries to be nonnegative. A reaction's forward physical rate remains nonnegative; zero rate is an explicit supported zero and not missing provider data.

## Derived results to implement

(1) For exact rational r, A dx/dt=(A nu)r=0 and q^T dx/dt=0. For finite normalized physical state/rates, source positivity is not guaranteed by stoichiometry alone; no integrator positivity claim is made.

(2) Energy cancellation is a column identity. Sum the material internal source and independently supplied reservoir increments, never define a final reservoir as a residual in the tested path. Each fixture supplies all increments independently.

(3) For any matrix C of actually conserved rows, changing reference energies epsilon'=epsilon+C^T lambda preserves DeltaI because DeltaI'-DeltaI=lambda^T C nu=0. For chemical reactions C stacks isotope counts and charge. The charge-reference shift includes explicit electron rows. Nuclear channels can use baryon/charge references only; isotope-reference invariance is not claimed there. This also explains why inconsistent ion versus neutral atomic-mass conventions can generate false Q: a missing explicit electron violates charge cancellation. Tests use two distinct exact rational lambda vectors, including nonzero charge coefficient.

(4) Reversing both sides maps nu->-nu, Q->-Q and every reservoir increment->its negative. It does not assign a reverse rate or detailed balance law. A `reversible_pair_key` sorts the two complete side signatures but returns orientation separately. A `directed_event_key` retains side order, process, normalization, frame/domain, and declared state resolution. Same unordered pair with different process/energy partitions is not duplicate physical ownership.

(5) Two providers registered to the same physical ownership slot and same directed event definition are a conflict unless one is explicitly `alternative_inactive`. Slots are per physical event inclusion, not per repository. Distinct electron thermalization/PI or forward/reverse channels remain distinct slots. Different branches or isotope labels are distinct. Unresolved overlap yields `OWNER_OVERLAP_UNRESOLVED`; do not silently sum them. This is scientific event deduplication only, no authentication/locking/lease system.

## Frozen synthetic fixtures

Use isotope H1=(1,1), D=(1,2), Li7=(3,7), He4=(2,4), ground isomer everywhere. Internal energies eV: H1=-10,D=-11,H1+=0,D+=0,H1−=-12,H1H1=-25,H1D=-26,Li7=-30,Li7H1=-45,He4=-40,He4H1+=-48,e_th=0,e_fast=0,n=0. Omitted core-ion epsilon is `UNQUALIFIED`, not0. These values manufacture ledger witnesses; they do not approximate physical molecular data.

Required positive cases (all exact):

1. H1 -> H1+ + e_fast, radiation -15, fast +5, DeltaI+10; heat0. One ionization event removes one photon with independently specified15eV. Charge and nuclei zero.
2. H1+ + e_fast -> H1, radiation+15, fast-5, DeltaI-10; exact reverse ledger; no detailed-balance claim.
3. H1 + e_th -> H1−, radiation+2, DeltaI-2; attachment.
4. H1 + H1 -> H1H1, radiation+5, DeltaI-5; multiplicity2 retained.
5. H1H1 -> H1 + H1, radiation-5, DeltaI+5; absorption/dissociation.
6. D + H1H1 -> H1D + H1, all reservoir0, DeltaI0; isotope exchange.
7. D + H1+ -> D+ + H1, thermal-1, DeltaI+1; electron/charge-exchange bookkeeping, finite energy not rate.
8. Li7 + H1 -> Li7H1, radiation+5, DeltaI-5.
9. He4 + H1+ -> He4H1+, radiation+8, DeltaI-8.
10. e_fast -> e_th, fast-3, thermal+3, DeltaI0; total charge preserved, pools distinct.
11. n -> H1+ + e_fast, typed nuclear, nuclear/beta process tag, baryon/charge conserved, isotope delta reported, energy qualification `UNQUALIFIED` (not a physical beta result).
12. Synthetic C12=(6,12,ground), C13=(6,13,ground), both q0, and their neutral C12C13 molecule. Set epsilon(C12)=-4, epsilon(C13)=-5, epsilon(C12C13)=-12 eV exactly: formation receives radiation+3 and DeltaI=-3; dissociation radiation-3 and DeltaI=+3. Add the distinct formal nucleus C12m=(6,12,synthetic_m1) and its neutral atomic species with the same synthetic epsilon=-4 solely for identity checks; switching ground to synthetic_m1 changes signatures and is not a chemical reaction. These labels/energies are manufactured, not actual carbon/isomer data.

Independent expected dictionaries for each case are literal fixture data. Never generate expected stoichiometry/energy from the implementation under test. Use test exact rates 0,1,1/7,10^-100 and signed tangents -2,3/5. Source/JVP, energy invariance under two reference shifts and reverse relation are exact Fraction checks for all energy-qualified cases. Baseline 21-population catalog cardinality/composition/charge and both electron rows have explicit expected checks.

Required negative/ambiguity cases:

- Isotope swap H1->D tagged chemical must fail even though Z/charge agree.
- H1->H1+ without electron must fail charge.
- Electron produced in both pools for one PI must fail charge; duplicate source reconstruction is diagnosed.
- Add an unpaired bolometric physical energy owner to case1: energy fails; diagnostic-only tally is accepted and omitted from physical sum.
- Missing epsilon/provider normalization returns `UNQUALIFIED`, not zero energy/rate.
- Negative physical rate rejected; signed JVP accepted; missing provider differs from zero support.
- Same directed event + same ownership slot active twice gives conflict; inactive alternative accepted; different direction/process or actual isotope is distinct.
- Catalyzed H1+H1+e_th -> H1H1+e_th and uncatalyzed formation share net nu but distinct event signatures.
- Doubled stoichiometry retains multiplicity2 and differs from single-event normalization.
- Species permutation and reactant enumeration permutation leave canonical key unchanged; pool/state/isomer changes alter it.
- Formal q>sumZ invalid; q<0 passes schema with physical qualification still synthetic.
- Applying isotope-reference invariance to nuclear n decay must be refused or reported not-applicable; baryon+charge reference invariance remains valid when energies supplied algebraically.

## Acceptance and output

Exact rational identities and literal expected dictionaries are the primary acceptance; no floating tolerance is substituted. Optional binary64 display sums must be classified using exact represented operands and a displayed rounding bound, not used to overwrite the exact result. No clipping, renormalization, tolerance relaxation, empirical rate or new physics choice. Do not copy L0's2e-12 tolerance into unrelated exact integer tests.

`raw/results.json` records every fixture/control name, inputs, exact residual numerator/denominator, expected result and observed result, rejected-input reason, catalog coverage and explicit physical qualification. `raw/resource_receipt.json` records actual usage. `README.md` reports counts by category (positive chemistry, algebraic nuclear, guards, source/tangent identities), no inflated global total or physical completion percentage. Claim ceiling: `IMPLEMENTATION_CHECKED_FINITE_ISOTOPE_MOLECULAR_EVENT_INTERFACE` after independent source/raw review; global physical completion null; L4 readiness false. A passing compiler enables atomic owners to deliver species/channel-qualified inputs and REI to reject double-owned channels before later physical binding. It does not authorize another run or close molecular/atomic rate coverage.
