# SOURCE MAP

## Binding and method

- Target repository: `/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rei_bianchi`
- Git HEAD: `111b6ace750e36e218df7fc9626c6bad2ec19971`
- Audit date: 2026-08-23
- Scope rule: the preceding physics remedies are discovery seeds only. A seed becomes a premise only after current-source applicability and primary-source support are independently audited.
- Execution rule: source inspection and small isolated counterexamples only; no production trajectory, history driver, parity driver, packager, or BDF replay was executed.

## Repository path aliases

All aliases are repository-relative stage directories.

- `A`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY`
- `P`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK`
- `V`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_VALIDATED_CONTINUOUS_BRANCH_DIFFERENTIAL_INCLUSION_ENCLOSURE_LOCK`
- `C`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_EVALUATION_SITE_SPARSE_GENERATOR_VALIDATED_MPRK22_SDIRK2_DISCRETE_MAP_ENCLOSURE_LOCK`
- `R1`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R1_POSITIVITY_CONSERVATIVE_SECOND_ORDER_THERMOCHEMISTRY_PREFLIGHT`
- `R2A`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_ADAPTIVE_INTERNAL_MICROSTEP_ACCEPTANCE_AND_GLOBALIZATION_LOCK`
- `S`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_SPARSE_LOCAL_GENERATOR_AFFINE_TAYLOR_MODEL_ENCLOSURE_LOCK`
- `U`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_FOUR_CORNER_BRANCH_AND_UNRESOLVED_OTS_ENERGY_PROPAGATION_PREFLIGHT`
- `B`: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R1_CANONICAL_TIME_RESOLVED_GROUP_BOUNDARY_FLUX_DYNAMIC_OPACITY_AND_HEATING_MOMENT_EXTRACTION_LOCK_RERUN_V2`

## Active numerical and admission chain

The mechanically traced active chain is:

`A/run_adaptive_history.py` → `A/attempt_worker.py` → `P/interval_discrete_map.py` → `V/reduced_interval_rhs.py`, `C/implicit_certificates.py`, `U/uncertainty_trial.py`, and ultimately the `R1` MPRK22/SDIRK2 primitives.

The following are present but disconnected from that active chain:

- monotone table-event localization and its synthetic restart audit: `P/analysis/cross_site_discrete_map.py:42-130`, `P/analysis/table_event_restart_audit.py:26-82`;
- low-rank normalization/JVP machinery: `S/analysis/global_coupling.py:1-10,52-76,128-156,163-250`;
- an older fixed-point defect: `R2A/analysis/globalized_picard.py:108,259-295`;
- guide-invoked attempt parity: `A/analysis/validate_one_attempt.py:13-34`, with no controller/launcher caller found.

That distinction is decisive: static presence is not production effectiveness.

## Current-source evidence matrix

| Topic | Exact current source | Observed fact | Epistemic status |
|---|---|---|---|
| Active acceptance | `A/analysis/attempt_worker.py:98-133`; `P/analysis/interval_discrete_map.py:343-390` | One full step and two dependent half steps are compared by set distance; the result is named/used as local error. | Direct code evidence; it is a discrepancy, not by itself a proven LTE/global error. |
| No active defect/QoI/global estimator | Active caller inventory plus the paths above | No active LTE theorem, continuous defect, global propagation, adjoint, dual-weight, or QoI estimator was found. | Mechanical negative result within the inventoried chain. |
| Strict charts/exact zeros | `V/analysis/reduced_interval_rhs.py:316-384,505-523,573-589`; `R1/analysis/mprk22.py:30-48`; `R2A/analysis/tensorized_inputs.py:135-152` | Log/logit-like transforms and divisions require strict positivity while owner support includes exact zero structure. | Direct conflict between representable chart interior and physical closed faces. |
| He II normalization | `R2A/analysis/array_owner_kernel.py:203-235,320-362`; `V/analysis/reduced_interval_rhs.py:405-435,471-503` | `c_heii` already carries `YHE`, then `sum_nheii/n_h_total` contributes another helium abundance in the pure-He II limit. | Direct code plus limiting-case counterexample. |
| He II limiting probe | Isolated evaluation of the displayed formula | Pure-He II coefficient per H is `YHE^2 = 0.006241` for `YHE=0.079`; number-density opacity requires `YHE = 0.079`; ratio `0.079`. | Reproducible algebraic counterexample, not a production run. |
| Interval signed sum | `V/analysis/interval_arithmetic.py:1-7,212-217` | Long-double accumulation, cast to binary64, and one `nextafter` excludes the exact sum for `[1e20,1,-1e20]`: returned hull is about zero while exact rational sum is 1. | Reproducible exact counterexample; fatal to a general containment claim. |
| Interval transcendental scope | `V/analysis/interval_arithmetic.py:1-7`; `V/analysis/reduced_interval_rhs.py:573-589` | The module disclaims MPFI/MPFR rigor and uses heuristic inflation. | Direct code evidence; not a verified elementary-function layer. |
| Certificate scope | `C/analysis/implicit_certificates.py:1-6,41-119`; `P/analysis/interval_discrete_map.py:171-197,202-341` | Certificates cover local linear/scalar blocks; they are not a proof of the entire nonlinear discrete map. | Direct code limitation. |
| 54 eV shares | `P/analysis/interval_discrete_map.py:104-156`; corresponding point operator `U/analysis/event_uncertainty_operator.py:139-165` | H share is obtained by `1-y2a-y2b`; unresolved energy is defined algebraically from the other terms. | Direct evidence of cancellation exposure and ledger dependence. |
| Photon ledger | `P/analysis/interval_discrete_map.py:104-156,370-381`; `A/analysis/attempt_worker.py:121-126`; `A/analysis/adaptive_policy.py:235-285` | Assigned photons are reconstructed from the same total and the checked residual self-cancels. | Direct same-path tautology; not independent conservation evidence. |
| Energy ledger | Same paths | `unresolved` is constructed so the later energy sum closes by definition. | Direct same-path tautology; not independent energy validation. |
| Event handling | `P/analysis/interval_discrete_map.py:297-341`; `A/analysis/adaptive_policy.py:426-427`; disconnected localization noted above | Active path detects/stops on a table event but does not call production localization or restart/rebuild. | Direct call-graph evidence. Endpoint/topological logic does not establish all-root coverage. |
| Jacobian structure | `P/analysis/interval_discrete_map.py:171-281`; `V/analysis/reduced_interval_rhs.py:405-435`; disconnected `S/global_coupling.py` paths above | Active implicit work uses small dense population blocks and a scalar thermal derivative; existing global low-rank machinery is unused. On a fixed smooth branch, four groupwise outer products have right factors that factor through the three global sums `(sum_nhi,sum_nhei,sum_nheii)`. | Direct call-graph plus symbolic factorization. The nonlocal photo-feedback rank is therefore at most three; conditioning, interval behavior, and performance remain hypotheses. |
| Legacy BDF | `B/inputs/canonical_b2c2a_r1_src/gamma_conditioned_reconciliation.py:647-689`; `B/inputs/canonical_b2c2a_r1_src/absorption_decomposition.py:438-480`; `B/analysis/replay_canonical_bdf_dense.py:111-141,161-281` | Legacy solves visibly rely mainly on `.success`, without `jac`, `jac_sparsity`, or event functions in those calls. | Direct historical-source evidence. |
| Legacy product use now | `R2A/analysis/array_forcing.py:49-103`; `V/analysis/reduced_interval_rhs.py:240-249` | The active interval run consumes immutable BDF-derived interpolation/calibration; it does not execute legacy BDF. | Direct call-graph evidence; fixes require a new upstream/reference lane, not an in-place current solver switch. |
| Runtime identity | `A/analysis/runtime_contract.py:18-51,71-107,153-220` and live read-only version probe | Pinned NumPy/pandas versions (`2.3.5`/`2.2.3`) differ from live (`2.4.2`/`3.0.0`); SciPy matches `1.17.0`; JAX is absent/excluded. | Direct current blocker to scientifically admitted execution. |
| Resume | `A/analysis/run_adaptive_history.py:1517-1584,2056-2118` | Loaded state is restored, but no separate entry branch for an already-terminal status was found. | Direct control-flow gap; exact behavioral exploit was not executed. |
| Worker buffering | `A/analysis/run_adaptive_history.py:1630-1776` | `subprocess.run(..., capture_output=True)` buffers before later size checks. | Direct resource-bound gap. |
| Candidate semantics | `A/analysis/run_adaptive_history.py:1697-1728`; `A/analysis/adaptive_policy.py:235-374` | Schema/finite/metadata checks do not provide an independent physical oracle. | Direct limitation. |
| Packaging | `A/analysis/package_local_results.py:47-110` | Broad JSON/history/receipt selection and in-memory `read_bytes`/`BytesIO` materialization are used. | Direct containment/resource concern; packaging was not run. |
| Resource preflight | `A/analysis/preflight.py:38-43`; `A/analysis/run_adaptive_history.py:421-463,2125-2147` | Memory and worker/optional attempt caps exist; disk, inode, wall-time, and package-size forecasts were not found. | Mechanical negative result within inventoried code. |

## Primary-source map

| Source | Primary contribution | What it does **not** establish here |
|---|---|---|
| Friedrich et al., *Radiative transfer of energetic photons: X-rays and helium ionization in C2-RAY*, MNRAS (2012), arXiv:1201.0602, https://arxiv.org/html/1201.0602v1, §3.1.2, §3.3, Appendix D (eqs. 35, 36, 84) | H/He population equations, helium simplex, coupled opacity shares, and the single `n_He/n_H` conversion when fraction equations are written per species inventory. | It does not certify this repository's discrete map, interval layer, timestep estimator, or event controller. |
| Burchard, Deleersnijder & Meister, *A high-order conservative Patankar-type discretisation for stiff systems of production-destruction equations*, Appl. Numer. Math. 47 (2003), DOI `10.1016/S0168-9274(03)00101-6` | Original conservative/positive Patankar construction for production–destruction systems. | Applicability requires an actual nonnegative PDS decomposition; it does not validate arbitrary transformed thermal/radiative coupling or exact-zero chart behavior. |
| Kopecz & Meister, *On order conditions for modified Patankar–Runge–Kutta schemes*, Appl. Numer. Math. 123 (2018), DOI `10.1016/j.apnum.2017.09.004` | Formal order conditions and constraints for MPRK methods. | Positivity/conservation do not imply accurate QoIs, interval containment, or global error control. |
| Martín-Vaquero et al., nonautonomous modified Patankar methods (2021), DOI `10.1016/j.cam.2020.113350` | Separate positivity, conservation, and second-order conditions for nonautonomous PDS, closer to the time-dependent forcing here. | It does not prove the current stage-time sampling or branch-changing map meets those conditions. |
| Torlo, Öffner & Ranocha, *Issues with positivity-preserving Patankar-type schemes* (2022), DOI `10.1016/j.apnum.2022.07.014` | Counterexamples near zero: oscillation, sticking/spurious behavior, and order reduction; standard theory relies on strictly positive states. | It does not rule out a separately proved active-face/reduced-system construction. It does rule out treating positivity/conservation as zero-safety. |
| Radtke & Burchard (2015) plus corrigendum, DOI `10.1016/j.ocemod.2014.11.002`, `10.1016/j.ocemod.2017.10.003` | Content/process-matrix constructions for multiple nonnegative inventories. | The corrected tests replaced nominal zeros by `10^-10`; they are not evidence for literal exact-zero handling, and signed charge needs separate treatment. |
| Mahdi et al. (2018), DOI `10.1137/17M1138418` | Stoichiometric left-nullspace invariants: `l^T Γ=0` implies conserved `l^T x`. | A numerical null vector is not automatically physical H, He, or charge provenance. |
| Angeli & Sontag (2003), DOI `10.1109/TAC.2003.817920`; Fiedler & Pták (1962), DOI `10.21136/CMJ.1962.100526` | Metzler characterization of positive linear systems and classical nonsingular M-matrix equivalences/inverse nonnegativity. | A nonlinear species Jacobian is not automatically Metzler; the result applies only to a qualifying frozen transfer generator. |
| Henderson & Searle (1981), DOI `10.1137/1023004`; Hager (1989), DOI `10.1137/1031049` | Woodbury reduction identities under nonsingularity of the base block and reduced system. | They provide no conditioning, positivity, or interval-enclosure guarantee; table events break smooth fixed-branch structure. |
| Krawczyk (1969), DOI `10.1007/BF02234767`; Rump (2010), DOI `10.1017/S096249291000005X` | Interval root enclosure requires outward-rounded operations, a Jacobian enclosing all derivatives on the box, and strict inclusion; success yields an enclosure/uniqueness result under hypotheses. | An algebraic root certificate does not enclose the continuous trajectory or truncation error; failure is inconclusive. |
| Estep, *A posteriori error bounds and global error control for approximation of ordinary differential equations*, SIAM J. Numer. Anal. 32 (1995), https://epubs.siam.org/doi/10.1137/0732001 | Residual/duality-based a posteriori and global ODE error control, including stiff dissipative settings under stated assumptions. | A full/two-half endpoint distance is not automatically this estimator; stability/adjoint assumptions must be established for the current hybrid map. |
| Enright & Hayes (2007), DOI `10.1145/1206040.1206041` | Defines continuous defect `δ=ỹ'-f(t,ỹ)` for a reconstruction and warns that full/half or method comparisons can agree while both are inaccurate. | Their explicit-RK construction does not automatically transfer to MPRK–SDIRK; branch-correct reconstruction and stability analysis are required. |
| Cao & Petzold (2004), DOI `10.1137/S1064827503420969` | Adjoint-weighted global/scalar-QoI error estimation from perturbations and conditioning. | It is not an interval bound; valid differentiability, accurate primal/adjoint solves, and hybrid jump/saltation treatment are required. |
| Mellema et al. (2006), DOI `10.1016/j.newast.2005.09.004` | Photon conservation: depletion of ionizing photons equals caused photoionizations, supporting a separately accumulated source–absorption–escape ledger. | It does not validate this repository's OTS cascade or energy partition. |
| Shampine & Thompson (2000), DOI `10.1016/S0898-1221(00)00045-6` | Convergence-rate preservation for accurately located simple, isolated, well-separated events with continuous restart; documents missed double crossings/re-detection issues. | Does not cover grazing, repeated, or simultaneous roots without additional machinery. |
| Park & Barton (1996), DOI `10.1145/232807.232809`; Biscani & Izzo (2022), DOI `10.1093/mnras/stac1092` | Whole-interpolant/polynomial real-root isolation can order multiple simple roots. | Guarantee is relative to the interpolation polynomial; true-solution enclosure needs dense-output error, and multiplicity greater than one can still defeat isolation. |
| Donde & Hiskens (2006), DOI `10.1142/S0218127406015040` | Grazing is tangency to an event hypersurface and can be sought by shooting/continuation. | This is a falsifier/offline analysis, not a complete online locator. |
| Modelica 3.7 event semantics, https://specification.modelica.org/maint/3.7/equations.html; SciPy `solve_ivp` docs, https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html | Authoritative semantics for event iteration/priority and official warning that sign-change detection may miss multiple crossings. | Neither source proves the current custom controller correct. |
| Roache (2002), DOI `10.1115/1.1436090`; Trucano, Pilch & Oberkampf (2003), DOI `10.2172/918244`; Oberkampf et al. (2004), DOI `10.1115/1.1767847` | Manufactured/exact solutions and refinement support code verification; code comparison/reproduction is distinct from physical validation. | Same-code parity or expected historical output cannot substitute for an independent oracle or validation data. |
| Nedialkov, Jackson & Corliss (1999), DOI `10.1016/S0096-3003(98)10083-8` | Validated-IVP success means a uniqueness guarantee and enclosure of the true solution. | Point references, step refinement, and local algebraic certificates do not meet that stronger standard. |
| IEEE Std 1788-2015, *IEEE Standard for Interval Arithmetic*, https://standards.ieee.org/ieee/1788/4431/ | Standardized interval operations, formats, and exception semantics; authoritative benchmark for enclosure semantics. | The standard page does not certify the local heuristic, nor select/qualify a verified elementary-function implementation. The standard was inactivated in 2026 and version applicability must be stated. |

Each source above remains subject to the independent claim–source audit; no citation is treated as current-code applicability by title alone.

## Genealogy, conflicts, and negative/null findings

1. The repository already contains MPRK22/SDIRK2 and local certificates. Therefore “use a positive method” is not novel or sufficient; the live conflict is exact-boundary representability, normalization, global coupling, enclosure rigor, and admission.
2. The physical absorber-share equations support one helium-abundance conversion. They conflict with the pure-He II `YHE^2` limiting behavior in the current interval forcing.
3. Classical interval/Krawczyk theory requires inclusion operations. It conflicts with the explicit heuristic interval layer, the exact signed-sum exclusion counterexample, and an exact 2×2 M-matrix helper/consumer witness whose published bounds exclude both exact coordinates. The witness does not prove occurrence on the active trajectory because the active matrix constructor widens intervals.
4. A posteriori/global error theory separates defect, stability/adjoint weighting, and target error. It limits any claim that the current dependent full/two-half endpoint distance alone establishes LTE, global trajectory error, or QoI error.
5. Event-localization code and low-rank/JVP code are historical/static assets only until the active caller graph consumes them. Static receipts are not runtime evidence. Four groupwise outer products factor through three global species sums, so fixed-branch nonlocal photo feedback has rank at most three; this does not establish conditioning, enclosure, or speedup.
6. Standard MPRK positivity/conservation theory assumes strict positivity and qualifying PDS/denominator/order conditions. Published near-zero pathologies and a corrigendum that replaced zeros with `10^-10` directly prevent using it as evidence for exact structural-zero safety.
7. The current live runtime is inadmissible under its own pinned contract, so no new scientific execution was attempted.
8. Physics-specific reasoning cannot cure runtime identity, symlink/package custody, terminal resume, unbounded pipes, or ancestry complexity. Those are retained blockers, not omitted inconveniences.

## Evidence gaps that survive Phase 2

- A source- and implementation-qualified verified interval elementary-function backend for the exact deployment environment.
- A derivation proving that the proposed active-face PDS decomposition remains nonnegative and second order across all current radiative/thermal branches.
- A stability/adjoint model and owner-approved quantitative budgets for the actual scientific QoIs.
- An event strategy combining all-simple-root isolation with an explicit grazing/repeated-root falsifier, true-solution dense-output error, and simultaneous-event priority semantics. No single checked source supplies all of these guarantees.
- An independent reference implementation assembled from primitive fluxes and limiting regimes.
- Verified factorization, measured numerical rank, conditioning, interval behavior, and performance of the block-plus-rank-`<=3` solve on admissible states, including Woodbury/Schur denominator failure criteria.
- Exact vacuum/trace conventions and table-knot ownership, which are model-authority decisions rather than numerical defaults.
