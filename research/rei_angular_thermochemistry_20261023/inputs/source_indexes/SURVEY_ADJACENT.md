# Adjacent source survey for the 2026-10-23 reionization synthesis

## Decision and scope

The most useful next calculation is a **source-bounded, prescribed-background extension** of the existing depleted-photon/common-temperature C22A scheme, combined with the directional Bianchi photon characteristics already found by the parent survey in rei_bianchi C13/C15/C16. This is a synthesis of existing components. It should not be described as the first directional UV model or a new full Einstein–matter closure.

The current adjacent source survey found a complete, reusable H/He/Li atomic provider, the C22A energy and photon accounting, later C22B/C/D additions, exact chemical reductions, and saved anisotropic and FLRW backgrounds. It did **not** find directional depleted UV evolution in the inspected C22A/B/C/D chain. C22E evaluates directional line-admission conditions on stored C22D fields and explicitly makes no RHS, provider, or ODE calls. The separately maintained rei_bianchi survey is authoritative for its directional models.

This survey used the built-in physmath research loop 1.0.0 evidence-reuse policy, the local AGENTS.md and the preceding RESUME.md. It ran no cosmological or chemical solver, imported no research model, replayed no completed solution, created no clone/worktree, and changed no remote object. Binary saved arrays were decoded, hash-checked, and read as data with pickle disabled; small CSV exports contain selected existing columns.

### Coverage actually completed

The owner inventory returned **51 accessible repositories**. A second offset-100 page was empty. All advertised branch pages were enumerated for the 13 selected adjacent repositories below: **1,374 current heads**. The exact names and SHAs are in adjacent_remote/*_branches.json. PR coverage is the latest updated, all-state sample of at most 30 per repository, **236 metadata rows** in total. This is not a complete open-PR or historical-PR census. Only scientifically selected head/source trees and files were deeply read; enumerating a branch is not a source review.

| Repository | Advertised heads | Recent PR rows | Main assessment |
|---|---:|---:|---|
| rec_bianchi | 145 | 30 | Thermal RR/DR moments, common-T chemistry, Compton accounting, anisotropic escape bounds |
| bass | 266 | 30 | Full-to-compact chemistry and exact affine reduction |
| bass_cr | 175 | 30 | Complete C22A–D source chain, C22E diagnostics, atomic provider, saved backgrounds |
| vigilode | 191 | 30 | Lifted adaptive error norm; bounded explicit DOPRI5 implementation |
| BASS_HE | 94 | 30 | Baryon pressure evolution, positive LRS propagator, reactive moment bridges |
| WU088_HH | 146 | 30 | Finite source CI and cold nuclear photon/recoil contracts |
| htt_base | 296 | 30 | Latest open-input theory, not an adopted atomic/IGM provider |
| RABBIT_v1.0.5_PRODUCTION | 55 | 26 | BBN transport; no reionization import selected |
| ISM | 1 | 0 | Molecular fitting package, not primordial IGM microphysics |
| toy_bbn | 2 | 0 | Educational BBN model |
| bianchi_phase_r | 1 | 0 | Branch inventory only; README lookup failed |
| MOSAIC-ODE | 1 | 0 | Solver bootstrap, not a broadly admitted production solver |
| CLASSIER | 1 | 0 | CLASS/ncdm work, not a new atomic provider |

The owner inventory, branch/PR JSON, selected tree listings, file manifest, and byte verification are under adjacent_remote/. There are **85 byte-verified text source/evidence files**, plus the two separately verified binary histories and their donor receipts. One explicit lookup failed: C22A/CONTRACT.json at the selective ba39 source publication; the existing contract was recovered from 15fd instead. Whole-repository recursive tree requests for large repositories exceeded the connector transport limit, so the survey read nonrecursive roots and specific subtrees. Completeness therefore applies to the advertised branch inventory, not to every file in every repository.

No claim is made to complete chat visibility, unshared local branches, inaccessible repositories, or archive contents. The parent task separately owns rei_bianchi, personal context, Drive/Dropbox, backups, and the proposed new theory contract.

## Exact source pins

| Label | Repository / exact commit | Adoptable paths or role |
|---|---|---|
| CR-C22 | bass_cr / ba39fc75521aa18705ec832d789e50dd5c6565bc | research/cr_c22a_thermochemical_20261022; cr_c22b_compton_bath_20261022; cr_c22c_h1_excitation_20261022; cr_c22d_cold_ci_20261022 |
| CR-recovery | bass_cr / 15fd250ab91574bd4f3348e91d739a15a6ed6005 | C22A/B contracts, acceptance records, C21O atomic provenance and saved histories |
| REC-moments | rec_bianchi / 12068893fab749ae1efb513563d0a86cc1cf649f | research/rec_thermal_moments_20261022/code/{recombination_moments,thermal_sources,thermal_system}.py |
| REC-THERM02 | rec_bianchi / b28b387fecd6cc71fddb98e95f336eba5f8a647f | research/rec_rei_thermal_compton_20261022/code/coupled_thermal.py |
| REC-angular | rec_bianchi / 5185c396b7e07076565ca2f5044a5ccd193e6ee1 | research/rec_bianchi_escape_moments_20261022/code/escape_moments.py |
| BASS-compact | bass / 574c3af93810122af0a7977e00e34195e5251a09 | research/rei_hheli_compact_pilot_20261022/code/compact_system.py |
| BASS-affine | bass / 797d66580448dad7fc41f2c2db31fe0eb37908bf | research/sandbox_affine_chemistry_20261022/code/affine_system.py |
| HE33/36 | BASS_HE / 6403055c3d574ec0bd1ece80147f9711315902e7 | HE33 pressure propagator; HE36 event_bridge/{event_bridge,source_lift,finite_bridge}.py |
| HH81 | WU088_HH / b3ec271a96cb67e583bffa9b61533802838236f9 | research/hh_phys81_atomic_nuclear_source_contract_20261023/source/{finite_ci,nuclear_recoil}.py |
| VIG | vigilode / fbc3c272fa06b443de148631ea78bfa6a34f1b2b | crates/rodas5p-integrators/src/dopri5.rs; crates/vigilode/src/explicit.rs; research/lifted_error_norm_20261022 |

Every downloaded file has its own exact commit, Git blob, remote URL, and local path in [source_manifest.json](adjacent_remote/source_manifest.json). The table identifies the source revision; it does not imply all historical acceptance runs executed at that same documentation head.

The most consequential discovery is a **stale advertised head**. bass_cr PR96 advertises 7643af28c671a7473754a3c2cd0c6e523bd61aac, but its updated body links reachable source publication ba39fc75521aa18705ec832d789e50dd5c6565bc and source-closure commit 9496f159a0387713d9135398e1f1a3b3e4dcbee0. The latter publication contains C22D/E source that the older branch-tip view misses. The PR metadata/body is preserved as adjacent_remote/bass_cr_pr96_latest_full.json. The recovery-pointer-only branch 5750489be6ad80b4e142f5712c656c33ae07f097 is therefore not the scientific source of record.

## Immediate provider import

The byte-verified atomic root is:

/workspace/scratch/d5baa30c266d/intake_reionization_20261023/adjacent_remote/files/bass_cr/ba39fc75521a/research/cr_c21o_hheli_z2_20261021/

It contains atomic_network.py, coupled_model.py, and vendor/atomic with the seven required provider/input files, ATTRIBUTION.md, and REI_LICENSE. C22A model.py and rr_energy_moment.py are in the neighboring cr_c22a_thermochemical_20261022 directory.

The following files are byte-identical between the recovery 15fd and later ba39 snapshots:

| File | SHA256 |
|---|---|
| atomic_network.py | 6730e3091de918f693e02e40b0bdf1fefc543a5dcc4de23efd885ca098e2ed5f |
| C22A/model.py | 8e8a8afce20670ef762cc4060e09011f850191ae38efb31f548720a89cc2886f |
| C22A/rr_energy_moment.py | 59bc1620600d51a1f6b1b703272c4d92a7b38f3d32637de2acf2a04af2c6d2a4 |

| Provider/input file | SHA256 |
|---|---|
| r9_li_thermal_rates.py | 74b2a8c30c62f4a50e7c5c4bcf92cb159549ffcb904a3e423a793169c2f2bb27 |
| phfit2.f | 8df982535a4a2b952e33ca2ffb6d81600e156d7373fbf547a0c0170c1cecc296 |
| photo_table.dat | a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389 |
| partial_table.dat | fd0a315f100a78f8edb6b3fb12c0022246309cbc834394cbd0e8e5305d00b393 |
| rrfit.f | 81ff692a44622665d4d216e8f66445bfaa6699701f80ec9c02c80ebe8fd42cf9 |
| rr_table.dat | 2382f6896fe58ee1da58c9bd563fd7d02c0d94410dbd4150767eed26a54f5091 |
| rr_description.txt | fa24b34f734f8d346163df77f6c277af848b799daa693387251c892f86c14ca4 |

Use the unchanged Provider.sigma and Provider.rr interface and the explicit 21-population abundance/charge mapping. The provider's other thermal/Milne methods are not part of this adopted C22A closure. The model has neutron; H1/D/T charge pairs; He3/He4 charge triples; Li6/Li7 charge quadruples. Initial neutron and tritium totals are exactly zero, and C22A rejects a nonzero beta parent because decay-energy closure is absent.

The six electronic channels are HI, HeI, HeII, LiI, LiII, LiIII. Photo cross sections are returned in **Mb**, with 1 Mb = 10^-18 cm² = 10^-22 m². RR coefficients are **cm³/s**. The selected H/He thresholds are 13.6, 24.59, 54.42 eV; Li thresholds are 5.392, 75.64, 122.5 eV. These are the fit/source conventions, not a precision isotope-resolved energy table. H/He PH2 tabulated upper bounds are 50,000 eV, but the actual pilot adopts six initial cohort energies 10, 20, 40, 60, 100, 150 eV and redshifts downward. Neutral Li uses PH2 below 64.39 eV and the outer-2s PH1 partial above; Li core photoionization and Auger outcomes are absent. Do not turn a selected 150 eV pilot into an unbounded full-ion model.

The adopted total-RR fit range is 3–10^9 K. C22A initial T is strictly interior; its evolving-state guard admits the endpoints. C22D uses the tighter lower-strict range 3 < T <= 20,000 K. The numerical fit range is not a demonstrated physical accuracy range for differentiated heat moments.

The donor wrapper came unchanged from rei_bianchi commit 8a4f5df46f6e3058f5e685b85cc1cf3c20926368. Its repository MIT notice is preserved. The six original Verner numerical files retain author headers and source attribution; no separate SPDX/license statement was found in those files. The MIT repository notice is **not** represented as a new license grant for the original author files. This precise distinction is already stated by the donor ATTRIBUTION.md.

## Normalization and C22A equations

Let x_i be the stored scaled coordinate, Y_i = scales_i x_i = n_i/n_Href, and g_b be photons per H-reference nucleus. Eta is ln(a/a_initial), with a_initial = 1/21 and eta_end = ln 7. The initial nuclear totals per H-reference are H1 = 1, D = 2.5e-5, He3 = 1e-5, He4 = 0.082, Li7 = 5e-10, Li6 = 1e-14; n and T vanish. Therefore

\[
B=\sum_i A_iY_i=1.32808000350006,\qquad
n_B=B\,n_{\rm Href},\qquad
Y_i^{(B)}=Y_i/B.
\]

Photon counts and energies expressed per H-reference must also be divided by B when converted to per-baryon quantities. The physical electron density is n_e = n_Href sum_i q_i Y_i. The donor normalizes

\[
n_{\rm Href,0}[{\rm cm}^{-3}]
=\frac{\Omega_b\rho_{\rm crit}[{\rm J\,m}^{-3}]}
 {c^2m_u B\,10^6},\qquad
n_{\rm Href}=n_{\rm Href,0}/a^3,
\]

with Omega_b = 0.049309230511847414.

Thermal energy u is eV per H-reference nucleus. The common temperature is recovered from

\[
u=\frac32 k_B T\,N,\qquad N=\sum_i(1+q_i)Y_i.
\]

This avoids adding the particle-creation temperature term twice: the change of N is already included when T is recovered from u and the evolving charge inventory.

For an ionization edge e with lower/upper states l/u and threshold chi_e, C22A evaluates, per unit eta,

\[
P_{eb}=\frac{c_{\rm cm}\,n_{\rm Href}}{H}
Y_l\,\sigma_e(E_b)\,g_b,\qquad
R_e=\frac{n_e}{H}Y_u\alpha_e(T).
\]

The same P is used to remove photons and ionize atoms:

\[
g_b'=-\sum_eP_{eb},\qquad
Y_l'=-\sum_bP_{eb}+R_e,\qquad
Y_u'=\sum_bP_{eb}-R_e .
\]

There is no continuing external source in this C22A cohort experiment. Its initial photons per H-reference are [0.05, 0.25, 0.003, 0.0002, 0.00001, 0.000001], scaled by the case input. C22A uses **E_b = E_b0 exp(-eta)**, an isotropic mean-redshift closure. Threshold crossings are segmented at eta = ln(E_b0/chi_e).

The source-preserving energy accounting is

\[
u'=-2u+\sum_{eb}(E_b-\chi_e)P_{eb}
       -\sum_eK_{{\rm cap},e}R_e,
\]
\[
E_{\rm esc}'=\sum_e(\chi_e+K_{{\rm cap},e})R_e,\quad
W_{\rm gas}'=2u,\quad W_\gamma'=\sum_bE_bg_b.
\]

The total u + binding·Y + E·g + E_esc + W_gas + W_gamma is constant within the declared closure. The photon-number and charge/event ledgers provide separate checks. A directional extension must replace the photon drift and work consistently; preserving only the total energy ledger would not establish state accuracy.

### Conditional RR heat

C22A uses the unchanged Verner–Ferland RR fit

\[
\alpha(T)=\frac{a}{u_0(1+u_0)^{1-b}(1+u_1)^{1+b}},
\quad u_j=\sqrt{T/T_j}.
\]

The stable positive capture factor is

\[
f(T)=\frac{1-b}{2(1+u_0)}
     +\frac{1+b}{2(1+u_1)},\qquad
K_{\rm cap}=k_BT f(T).
\]

The exact Maxwellian moment identity for a temperature-independent underlying cross section is L = k_BT [3 alpha/2 + d alpha/d ln T]. Applying that identity to an empirical total-rate fit defines a **conditional heat closure**. It does not turn the fit derivative into a separately verified energy-loss cross section. The positive form requires a,T0,T1 > 0 and -1 <= b <= 1.

REC-moments independently supplies the general differentiated RR form and signed-coefficient DR energy moments, including explicit structural absence versus numerical underflow. Its Mao-2017 correction combined with an unchanged donor number rate is explicitly a **hybrid**. This resolves a mathematical moment-construction dependency; it does not resolve provider-consistent physical heat accuracy for every adopted isotope/channel.

## Later C22 and adjacent physical inputs

### C22B–E

C22B adds Thomson Compton exchange against a prescribed blackbody bath T_gamma = 2.7255/a K, with the opposite energy debit in a separate bath ledger:

\[
Q_{\rm C}/n_{\rm Href}=
\frac{4\sigma_T c\,a_RT_\gamma^4}{m_ec^2}
\left(\frac{n_e}{n_{\rm Href}}\right)k_B(T_\gamma-T).
\]

Its nonrelativistic selector requires k_B max(T,T_gamma)/(m_e c²) <= 0.01. It does not add a duplicate CMB energy density to Einstein's source. The C22B acceptance record reports 3 BDF cases plus one Radau reference, 804 saved and 6,670 accepted states; maximum relative energy residual 1.4171373335946987e-11 and reference-scaled discrepancy 9.511332883578116e-9. Reuse this record; do not recount those old runs as new work.

C22C adds finite-source H1 n=2 excitation with separate 2s/2p event counters. C22D adds finite CCC H1 collisional ionization. Its source convention aligns the H-family binding increment to **13.6058 eV**, preserves the original photo-fit incident-energy axis/shape, and sets HI sigma to zero below the new support. It does not claim Milne consistency or a complete LTE atom. C22D guards T > 3 K, T <= 20,000 K and n_Href <= 0.01 cm^-3. CI transfers chi times the event rate from thermal to binding energy and adds no escaped CI reservoir. Since CI is H1-only, the old shared H1/D ionization-fraction quotient is invalid when it is active. Copying its CI term while retaining the earlier isotope reduction would change the model.

The C22D optimized RHS calls the unchanged C22A event routine and retains W_gamma' = E·g. Thus the inspected C22D source still has mean-redshift cohort evolution. C22E reads stored H and s, derives directional H_gamma = H + s(3 mu² - 1), and checks extrema. Its source-coverage record leaves line/geometry/cascade/mixing/secondary inputs unresolved and reports REGIME_NOT_ESTABLISHED. This is a line-admission diagnostic, not directional depleted-UV dynamics.

### REC common temperature and angular escape

REC-THERM02 contains a common-temperature full63/compact34 model, z=20 to 2, 193 saved nodes, initial T=1000 K and a 5–60 eV quadrature. Its eight new runs are five nominal compact cases, two tighter compact references and one full63 oracle. The reported scoped energy residual is 3.767e-7, below its 3e-6 gate. Do not pool these with the separate full63 z≈7.9637 to 2, 5–200 eV study or with BASS's aliased compact-pilot records.

It distinguishes an actual-grey hot-electron cooling branch from a Planck-reference exchange branch and retains a separate UV energy moment. Remaining inputs include exact Li charge-state/energy yields and actual spectral recoil/induced terms with radiation and Einstein matching. Its frozen-coefficient positive thermal update is a useful scalar fixture, not proof of positivity of the full nonlinear stiff integration.

REC-angular provides a constructive angular Sobolev escape bound. With S = sigma/H, q(n)=1+S_nn>0 and t=C_S/H, B=<beta(t/q)> and Q=<STF(nn) beta(t/q)>. Q is an escape-probability moment, not a radiation stress tensor. It proves B<=beta(t) and the thick approximation B0=1/t, Q0=2S/(15t), with errors bounded by exp(-t/qmax)/t and sqrt(2/3) times that bound. At epsilon=1e-8 the sufficient threshold is t/qmax>=18.42068075. Its evidence is finite angular tests and saved predicate checks, with zero cosmological IVPs. Resolved line populations, Einstein coefficients, degeneracies, source number/energy and ownership of compressed feedback remain necessary inputs.

### Matter pressure, CR stopping, and nuclear energy

HE33 supplies an actual small positive LRS pressure propagator in src/lrs_baryon_moments.js. Its SI API uses pressures J/m³, H/s/nu in s^-1, and dt in seconds. It solves a fixed-coefficient Metzler 2×2 system for P_perp and P_parallel, using positive logarithmic sums and expm1 to avoid cancellation/underflow. Negative initial pressures, negative nu and nonrepresentable results are rejected. Time-dependent coefficients use midpoint sampling. This is useful if anisotropic baryon stress is added, but the **physical pressure-anisotropy relaxation rate nu is still an input**, not automatically a photoionization/RR rate.

The underlying homogeneous nonrelativistic moment equations include

\[
\dot e+3H(e+p)+\sigma:\pi=Q,\qquad
\dot T=-2HT-\frac{T R_{\rm part}}{n_{\rm part}}
-\frac{2\sigma:\pi}{3k_B n_{\rm part}}
+\frac{2Q}{3k_B n_{\rm part}}.
\]

HE36 supplies reusable source-lift/centralization and finite-mass incoming-loss moment algebra. The actual CCC H source is fixed-heavy-target and finite in energy; it cannot be reinterpreted as a finite-target-mass differential provider. Outgoing daughter gains, fast-particle counts, stopping/deposition, and closure coefficients remain physical inputs. Its fixture/moment evidence is not a completed cosmological transport calculation.

HH81 supplies finite H/He/Li CI and cold-COM nuclear photon/recoil contracts. The adopted source windows are H 13.6058–968.61 eV, He 24.6–60 eV, and Li 6–15 eV; zero outside is a declared finite model, not a physical all-energy cross section. The Li threshold-to-6 eV gap remains relevant at low T. Its 7-to-3 reduction is exact continuous-coordinate elimination, not equilibrium chemistry. Three new IVPs and raw seven-state comparison passed within the selected model, with maximum state discrepancies 3.27e-10 and 7.29e-11 for the cited comparisons. Cold photon/recoil partition closes an event ledger, while nuclear rates, finite-T event averages, normal-frame emission and stopping remain open. It does **not** supply missing beta-electron/neutrino energy deposition.

## Numerical reuse and reduction

BASS's earlier 62-to-33 compact system uses reflection-even moment structure, exact zero n/T totals and the declared isotope equality. The 33-to-30 affine extension removes three redundant neutral populations using fixed H/He/Li totals:

\[
v=d+Lu,\qquad u'=R F(x,d+Lu),\qquad J_u=R J_v L.
\]

It preserves the actual floating initial H total 0.9999999999999999. It is exact elimination within that model, not QSS. Its evidence consists of algebraic/source comparison at actual and synthetic positive points and finite-difference directions, with **zero new IVPs**. The wrapper still evaluates larger donor machinery, so the reduction itself proves no wall-time gain.

Vigilode's lifted-error kernel addresses a concrete pitfall: reducing coordinates changes the adaptive norm unless embedded error is lifted back to the physical/full representation. Its inspected chemical example uses

\[
\|e\|^2=\frac1{33}\sum_i [(Le)_i/s_i]^2.
\]

The denominator, scales and constrained neutral errors must all correspond to the original 33-state problem. A new thermal/directional model needs its own full-space mapping and dimension; do not copy the numeral 33. The C kernel uses compensated long-double reconstruction and robust hypot accumulation, rejecting bad scales/nonfinite values and explicitly reporting platforms without extra long-double range.

The newest explicit vigilode DOPRI5 source is real code with FSAL adaptive integration, per-component tolerances, robust weighted norms, typed failures and partial results. Its executed-source pin is 45037fc24e8f8101605f309e1fdb3a9a4e3df56d, distinct from the fbc report head. It has no automatic stiff switching, dense events or nonidentity mass support in this interface. This is not a reason to replace a qualified stiff BDF/Radau baseline for the proposed chemistry. Choose an integrator on the new model's demonstrated stiffness/error cost; preserve independent oracle coverage and do not infer positivity from a successful generic solve.

## Saved background recovered without a rerun

Two exact C21O histories at CR-recovery are now local in adjacent_remote/background/. They contain eta, a, H, s, b and nH_ref_cm3 at 201 nodes, along with donor chemistry, radiation and stress diagnostics. Both carry PASS_SCOPED receipts, no global-error certificate, and no claim that 1,025 angular samples prove continuum positivity.

| Case | Original path beneath C21O | Initial signed full-Frobenius axes | SHA256 |
|---|---|---|---|
| grid044 | runs/c21o_grid45_v1/cases/grid044/history.npz | Sigma=0.6, Pi_m=0.0005, Pi_r=0.0012 | ae20c278239787c020e45028a6d6804cb9f056b75076a1d5ab045c0a7389733b |
| grid022 | runs/c21o_grid45_v1/cases/grid022/history.npz | Sigma=Pi_m=Pi_r=0 | 5d0ef6ee7adadf3a3acf148a930136cf406fab2b3eb484682e2a93de7119b7c0 |

The anisotropic file is 299,956 bytes; the FLRW file is 262,312 bytes. Their Git blob SHA1s and donor COMPLETE SHA256 values both match. The selected-column CSVs contain only existing eta,a,H,s,b,nH_ref_cm3 values. The FLRW b contains a residual up to about 4.86e-21, which was preserved.

For a new **prescribed-background** experiment, adopting these stored a/H/b fields and using Hermite b interpolation with nodal slopes s/H is a concrete route that avoids an invented geometry and avoids old-solver replay. The interpolant itself becomes a new, explicitly frozen background contract; its derivative must own the directional work. Using independently interpolated s/H for that work would generally break exact consistency with interpolated b. The new trace model must compute its own electron density from its own populations. Donor Thomson/background evolution used the donor chemistry; it is not updated by new trace chemistry. No full Einstein-backreaction claim follows from this reuse.

## What is resolved, and what remains a physical input

| Dependency | Current assessment | Recommended action |
|---|---|---|
| H/He/Li selected photo/RR provider | Source and units recovered, seven files byte-verified | Import unchanged selected provider with attribution and declared fit domains |
| Photon-conserving absorption | Already implemented in C22A | Reuse the same event flux for photons, charge and energy |
| Common-T particle census | Already implemented in C22A and REC | Evolve thermal energy and recover T using current electron/ion count |
| RR/DR energy-moment algebra | Derived/source-implemented | Retain conditional-fit status; do not call it universal atomic heat accuracy |
| Directional photon drift/work | Parent found rei_bianchi prior implementation | Combine with C22A provider; cite the prior directional model |
| Actual anisotropic/FLRW backgrounds | Stored donor trajectories recovered | Freeze/interpolate as prescribed geometry; reuse donor evidence |
| Exact reduced coordinates/error metric | Existing BASS/vigilode derivations | Derive mapping for new state; lift adaptive errors consistently |
| Full nonlinear positivity/stiff efficiency | Not established by the above algebra alone | Measure on the new scope, with an independent unreduced reference |
| External ionizing source spectrum/history | C22A only initializes finite cohorts | New emissivity is a declared scenario or independently sourced physical input |
| Li core charge/energy yields and cascades | Unresolved for general full-photo model | Keep outside adopted provider, or require final-state data |
| Resolved line transfer/reemission | Escape bounds exist; source closure incomplete | Do not equate C22E admission checks with a line solver |
| Beta energy and CR stopping/deposition | Still missing | Require spectra, daughters and transport/deposition law before activating |
| Anisotropic baryon relaxation | Moment equation/progagator available | Supply a justified transport coefficient and reaction tensors |
| Radiation/Einstein backreaction of new trace | Not supplied by prescribed-background reuse | State the trace scope explicitly |

## Concrete import recommendation

Start from the already byte-frozen atomic provider, C22A conditional RR capture moment, and the two verified saved backgrounds. Reuse the parent's pinned rei_bianchi characteristic geometry and derive one internally consistent directional energy/stress/work contract. Keep the initial-cohort scenario distinct from an observed cosmological emissivity history. Compare symmetry-folded photon channels against an unreduced independent oracle while preserving the physical event source, isotope conventions, charge census and full-space error metric.

Do not add C22D H1-only CI automatically: it changes the H/D reduction and the H-family energy registry and narrows the active temperature selector. Do not add HE36/HH81 recoil or line inputs solely because ledger interfaces now exist. Those interfaces make the unresolved physical data requirements precise; they do not supply stopping, differential daughter distributions or resolved line populations.

No old solved node needs to be rerun to justify this starting point. The new scientific claim should concern the scoped composition, directional depletion/work consistency and the demonstrated reduction/integration result, with every additional physical process admitted through an explicit source contract.
