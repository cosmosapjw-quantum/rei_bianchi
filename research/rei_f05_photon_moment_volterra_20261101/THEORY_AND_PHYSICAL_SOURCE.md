# REI F05: original four-group / three-moment continuum source theory

Original source family: `cosmosapjw-quantum/rei_bianchi`, new research cycle 2026-11-01. This document records **one R1–R10 mathematical-physics research unit**, not ten canonical nodes.

## R1 | Original physics question and locked scope

Current highest relevant original F05 evidence is Draft PR #354 HEAD `6574db945a1b96fa5e0b55923e36781b5db0b03b`, with actual source-native 46,080-cell H/He/thermal V2 shadow gate, 14 original ledger checks, and official accepted tick **160/131072** unchanged. Prior theory PR #353 HEAD `2e04037fbc174e71ed1bee313f2b554257ede4b9` established a discrete-map defect enclosure but expressly did **not** bound the error against the exact continuous initial-value problem. This cycle moves to the **physical continuous source operator**, not another correlated-increment local estimator, point-source atlas, approval-protocol debate, or production IVP run.

**Target physical result:** use the exact original four photon groups and three global H/He absorbing populations to derive (i) finite-amplitude photon allocation/shielding stability and gas-heating response, (ii) the exact low-rank global source Jacobian, (iii) a mathematically reproducible reduced Volterra equation for nonautonomous chemical+thermal continuous-flow error. If actual original source data permit, compute only a compact four-group native opacity-fraction witness on the accepted tick160 parent, rather than another 46,080-row atlas. Do not claim the resulting Volterra bound is a certified original continuum solution unless actual trajectory tubes, continuous residual, and stability bounds are evaluated.

**Physical state** per spatial node (i\): particle numbers (p_i=(N_{HI},N_{HII},N_{HeI},N_{HeII},N_{HeIII})), gas (T_i>0) kelvin, (z_i=\ln(T_i/K)), local thermal (U_i=\tfrac32 k_B(N_{H,i}+N_{He,i}+n_{e,i})T_i) erg, (n_e=N_{HII}+N_{HeII}+2N_{HeIII}). Conserved (N_{H,i}=N_{HI}+N_{HII}), (N_{He,i}=N_{HeI}+N_{HeII}+N_{HeIII}). Proper time (t) seconds. Local OTS, electron-density and cooling terms are retained, not replaced by a 3-channel toy.

**Original continuum source authority:** `stages/*VALIDATED_CONTINUOUS_BRANCH_DIFFERENTIAL_INCLUSION_ENCLOSURE_LOCK/analysis/reduced_interval_rhs.py`, SHA256 `b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36`, method `ReducedIntervalModel._explicit_photo_fields`. Actual original source TAR SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`, accepted parent arrays SHA256 `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`; original 26-event discrete native kernel SHA256 `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`. Distinguish *continuous reduced RHS* authority from *discrete native map* authority, though both use the source-owner photon allocation definitions.

**Invariants:** original [160,161] remains unapproved; V1 original worker, source, stage policies, source archive, accepted histories, main, production, budget, strict local threshold `2e-4`, width `2e-3`, owner table/OTS/14 ledgers unchanged. No merge, force push, tolerance relaxation, automatic next node, tick162 or history restart. Native subagent unavailable in this Chat runtime; use same-author hostile review once, no fabricated distinct-author referee.

**Success** is an exact source-matched theorem with assumptions and one independently checkable physical four-group witness; **stop** if the work becomes duplicate source derivative maps or protocol changes. CENTRAL=**28/88_REPORTED**; WORKING=**33/88_REPORTED**; PHYSICAL_FAST=**4/7_REPORTED**; CANONICAL_DELTA=**0**.

**R1 backup and drift watchdog:** isolated Git worktree and one Draft PR, stage commit and remote push; mission-specific physical continuous source mathematics rather than meta-work.
## R2 | Primary literature and original source crosswalk

**Original source read, not inferred:** `ReducedIntervalModel._explicit_photo_fields` in the SHA-locked `reduced_interval_rhs.py` above (approx. source lines 405–438) defines all four group photoionization/primary-photoheat allocations. It constructs exactly three interval totals `sum_nhi`, `sum_nhei`, `sum_nheii` and a per-group denominator `raw_total=external_subgrid+raw_hi+raw_hei+raw_heii`. Each species' nodewise photo rate is `forcing.current[g] * c_s * p_is /(N_s * raw_total)` when `owner_support[s,g]` is true. The helium I divisor is the GLOBAL helium nuclei total; the helium II divisor in this original code is the GLOBAL hydrogen total, an easily missed asymmetric convention. The code exposes `excess_eV[s,g]` for energy accounting. These are the exact original physical owner definitions, with zero coefficients for unsupported group/species pairs.

The same source's `rhs_details` constructs non-photo local electron-dependent collisional ionizations, H/He recombinations, local OTS branches, local energy cooling and cosmological expansion. Its exact continuous gas variable satisfies `d_logt=thermal_rhs/energy-particle_rhs/particles` with `energy=(3/2)k_B particles*T`, so thermal feedback enters the local 4×4 block and the derivative of primary heating enters the global 3-moment coupling. The proper-time `forcing_bounds` is an external nonautonomous forcing interpolation, not another endogenous cell-coupled state variable.

**Literature (claims constrained to original sources):** Arnold Neumaier, *Global, rigorous and realistic bounds for the solution of dissipative differential equations, Part I: Theory*, primary manuscript https://arnold-neumaier.at/ms/ode.pdf, Theorems 2.6–2.8 and logarithmic-norm analysis, develops validated ODE error propagation based on one-sided Lipschitz conditions. This supports the *form* of the proposed continuum residual inequality, not any numerical value for REI.

Julien Alexandre dit Sandretto and Alexandre Chapoutot, *Validated Explicit and Implicit Runge-Kutta Methods*, Reliable Computing **22** (2016), 78–103, https://interval.louisiana.edu/reliable-computing-journal/volume-22/reliable-computing-22-pp-078-103.pdf, require a priori exact-flow enclosure and validated truncation-error bounds to claim continuum IVP inclusion. It was already used in prior R1–R10; reused rather than redone.

Ka-Hou Leong, Avery Meiksin, Althea Lai et al., *A comparison of numerical methods for computing the reionization of intergalactic hydrogen and helium by a central radiating source*, MNRAS (2023), DOI https://doi.org/10.1093/mnras/stac3828, discusses photon competition between H I, He I and He II and effects on heating/ionization. It does NOT verify this REI homogeneous global denominator prescription, which is a model assumption, and spatially retarded radiative transfer is not implicitly achieved by an instantaneous 3-moment source.

**Reuse boundary:** original accepted source array and PR354 V2 source/ledger data are previously observed implementation-level evidence. This theory creates neither a new astrophysical photon transport provider nor a validated continuous H/He trajectory. Original-source `c_s`, denominators and `excess_eV` are authoritative model data; a general theorem about that reduced source must not be conflated with full time-retarded radiative transfer.

**R2 backup/publish:** R2 commit pushed to ONE Draft PR #355. DAG 28/88 central, 33/88 working, 4/7 fast, canonical delta 0. Drift watchdog: original physics source/literature directly mapped, no adjacent atlas.
## R3 | Exact definitions, dimensions and nonlocal dependence

At fixed proper time `t` and spatial node `i=1,…,46080`, define `S_s(t)=Σ_i p_{is}(t)` for absorbing `s∈{HI,HeI,HeII}`, with the nuclei-conserving species counts `p_is` in particles. Let `N_H^Σ=Σ_i N_H,i` and `N_He^Σ=Σ_i N_He,i`. The source coefficients are EXACTLY
`a_Hg=c_Hg/N_H^Σ, a_HeIg=c_HeIg/N_He^Σ, a_HeIIg=c_HeIIg/N_H^Σ`,
where `c_Hg=NH0_CM3*(1+zcos)^2*MPC_CM*σ_Hg`, `c_HeIg=YHE*c'_g`, `c_HeIIg=YHE*c''_g`, and `σ` is the original species/group photoionization cross section when owner support is present (else zero). `NH0_CM3 [cm^-3]*MPC_CM [cm]*σ [cm^2]` is dimensionless, so `a_sg` is per-particle, `a_sg S_s` dimensionless, and `D_g=E_g+Σ_s a_sg S_s` dimensionless with `E_g=external_subgrid[g]≥0`.

Let `J_g=forcing.current[g]≥0` denote original resolved+subgrid group current with physical photo-count flux units (particle ionization events/s in original code), and `ε_sg=excess_eV[s,g]*EV_ERG` in erg/absorbed photon. The native source defines
`r_isg=J_g a_sg p_is/D_g` (particle counts/s) and `Q_i^primary=Σ_{s,g} ε_sg r_isg` (erg/s).
Here `E_g` is a denominator allocation to an external/subgrid owner, **not** an actual additional independent resolved H/He species. Require `D_g>0` for all active groups; group4 may have extremely small `J_4`, but it is still a syntactically existing group and must not be silently deleted.

The global photon coupling has exactly three input moments `S_s` even though the 4 groups produce different `D_g`. The right-hand side for original reduced physical per-cell variables `y_i=(x_HII,x_HeII,x_HeIII,ln(T_i/K))` can be written `dy_i/dt=f_i(t,y_i,S(y))` with all local electron, OTS, photoheat and cooling physics retained. For fixed H and He nuclei,
`S_HI=Σ_i N_H,i(1-x_HII,i)`,
`S_HeI=Σ_i N_He,i(1-x_HeII,i-x_HeIII,i)`,
`S_HeII=Σ_i N_He,i x_HeII,i`.
Thus `S(y)=S_*+V y` is an affine **constant 3×(4N)** population moment map, V coefficients in particles. Temperature coordinates do not enter V directly. The temporal source is nonautonomous through `J_g(t), E_g(t), σ_g(t), zcos(t), H(t)` but these are externally prescribed by the original forcing, not extra dynamical global moments. The individual `f_i` has units s^-1 in all dimensionless coordinates.

**Regularity:** exact derivatives require strictly positive active `D_g,S_s,p_is,T_i`, fixed table/branch cell, and differentiability of local collision/OTS functions. Across a branch kink a smooth-Jacobian theorem is inapplicable without a separate piecewise/one-sided bound; the algebraic finite photon allocation identities below remain valid wherever denominators remain positive. Do not infer the original full nonlinear 26-event flow is differentiable across every accepted parent interval merely because one tick has zero detected table events.

**R3 backup/publish:** exact original coefficient asymmetry and physical state conventions fixed; DAG 28/88 · 33/88 · 4/7, canonical 0. Drift watchdog PASS.
## R4 | Constructive alternative representations

**Candidate A, all-cell dense continuous Jacobian:** directly differentiate the 4N nonlinear source coordinates (\(N=46080\)). This is mathematically valid but obscures the exact original global photon competition and gives a \(184320\times184320\) nominal matrix; constructing it explicitly adds no physics to the first-tick continuum-obligation question.

**Candidate B, isolate all four photon groups as four global independent state moments:** generally wrong. There are four photon **external currents**, but the endogenous original full-volume denominators depend only on **three** scalar neutral-species sums. Treating \(D_g\) independently as state variables without their 3-moment constraints introduces unphysical tangent directions and can distort cross-group source correlations.

**Candidate C, exact owner-based three-moment factorization:** retain all 26 original event reactions and local electron/OTS/thermal nonlinearities; represent each cell's source as \(f_i(t,y_i,S(y))\) with exactly three source moments. Prove finite-amplitude allocation identities, bound log-opacity changes, derive Jacobian \(A+UV\) and the continuum residual Volterra reduction. **Selected construction.** This is new continuum physics analysis, not a fourth numerical step-doubling estimator.

**Candidate D, full retarded time-dependent radiative transfer:** physically relevant as a separate higher-fidelity model, but not the REI original reduced source owner; substituting it here would violate the current source identity. Leong et al. 2023 shows time-dependent RT can differ materially from an instantaneous approximation in quasar ionization fronts; such model discrepancy is left an explicit separate scientific question, not silently included.

**Minimal proof/work criterion:** exact 3-moment algebra and one 4-group original-source acceptance-tick witness. No physical spectrum synthesis, photon atlas, original worker mutation, further V2 process review or full 131072-step replay.

**R4 backup/publish:** same Draft PR #355; CENTRAL=28/88, WORKING=33/88, FAST=4/7, canonical delta=0. Drift watchdog PASS: choose source-faithful exact physics, not representation bureaucracy.
