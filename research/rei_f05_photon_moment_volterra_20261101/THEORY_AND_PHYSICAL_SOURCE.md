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
## R5 | Derived original photon-allocation, low-rank Jacobian and continuum error theorem

### Theorem I: exact four-group absorption allocation, finite log shielding and heating

For each active original photon group \(g\in\{0,1,2,3\}\), define \(u_{sg}=a_{sg}S_s\ge0\), \(D_g=E_g+\sum_s u_{sg}>0\), \(q_{sg}=u_{sg}/D_g\), \(q_{0g}=E_g/D_g\). All \(q\)'s are dimensionless, \(\sum_s q_{sg}+q_{0g}=1\). Source photoionization rate of cell \(i\), species \(s\), group \(g\) is \(r_{isg}=J_g a_{sg}p_{is}/D_g\) [events/s]. Exact summation over all physical cells and species gives

\[
 R_g^{\mathrm{resolved}}=\sum_{i,s}r_{isg}=J_g\sum_s q_{sg}=J_g(1-q_{0g}),\quad
 R_g^{\mathrm{external}}=J_gq_{0g},\quad
 R_g^{\mathrm{resolved}}+R_g^{\mathrm{external}}=J_g.
\]

This identity is an **original model photon-allocation identity**, not a solution of a retarded Boltzmann/radiative transfer equation. The grouped original primary gas heating is \(H_g=\sum_{i,s}\epsilon_{sg}r_{isg}=J_g\bar\epsilon_g\), \(\bar\epsilon_g=\sum_s\epsilon_{sg}q_{sg}\), units erg/s.

Let \(\ell_k=\ln S_k\) for positive three source moments, and keep original group clock and forcing fixed. Derivatives are exactly

\[
 \frac{\partial\ln D_g}{\partial \ell_k}=q_{kg},\qquad
 \frac{\partial q_{sg}}{\partial\ell_k}
 =q_{sg}(\delta_{sk}-q_{kg}),\qquad
 \nabla^2_{\ell}\ln D_g=\operatorname{diag}(q_g)-q_gq_g^{\mathsf T}\succeq0.
\]

Proof of PSD: for arbitrary real \(v\in\mathbb R^3\), augment with \(v_0=0\); its quadratic form is the variance \(\sum_{s=0}^3q_{sg}v_s^2-(\sum_{s=0}^3q_{sg}v_s)^2\ge0\). Thus group log-denominator is convex; at fixed positive local numerator the log photo rate is concave in the **three independent log source moments**. If \(E_g=0\), the Hessian has the all-ones null vector, since a common rescaling of all global opacity moments does not change the **relative allocation**.

Further,

\[
 \frac{\partial R_g^{\mathrm{resolved}}}{\partial\ell_k}
 =J_g q_{0g}q_{kg}\ge0,\qquad
 \frac{\partial H_g}{\partial\ell_k}
 =J_g q_{kg}(\epsilon_{kg}-\bar\epsilon_g).
\]

The first is a positive monotonic source-total response when external sink \(E_g>0\). For \(E_g=0\), \(R_g^{\mathrm{resolved}}=J_g\) is strictly independent of the moment composition: opacity reallocates an unchanged **resolved total** among HI, HeI and HeII. The **thermal heating generally changes** as the species' excess energies \(\epsilon_{kg}\) differ; common scaling leaves it invariant only for \(E_g=0\) at fixed \(J_g\). No assumption of exact cosmic total energy conservation is introduced.

Finite variation is also exact, not only Taylor-local. If \(S_s'=S_s e^{\delta_s}\) while \(E_g,a_{sg},J_g\) are fixed, then

\[
 \frac{D_g'}{D_g}=q_{0g}+\sum_s q_{sg}e^{\delta_s},
 \qquad e^{-M}\le D_g'/D_g\le e^M,\quad
 M=\|\delta\|_\infty.
\]

Hence \(|\ln(D_g'/D_g)|\le M\) on the whole positive moment cone, independent of 46,080 spatial nodes. At a supported positive local rate \(r_{isg}>0\), its finite response is \(\ln(r'_{isg}/r_{isg})=\ln(p'_{is}/p_{is})-\ln(D'_g/D_g)\); external clock variation requires another term and is **not** included in this fixed-time identity. If a group current or species channel is zero, use the allocation identity rather than taking an undefined logarithm.

### Theorem II: exact rank-three nonlocal continuous H/He/thermal Jacobian

Use conserved per-cell nuclei \(N_{H,i},N_{He,i}>0\) and dimensionless physical state
\(y_i=(x_{HII,i},x_{HeII,i},x_{HeIII,i},z_i)\), \(z_i=\ln(T_i/\mathrm K)\). The exact original continuous source can be expressed \(f_i(t,y_i,S(y))\), where all locally resolved photo, 26-event OTS, electron-density, recombination, cooling and expansion terms remain in \(f_i\), and

\[
 S(y)=S_*+V y,\qquad V_i=
 \begin{pmatrix}
 -N_{H,i}&0&0&0\\
 0&-N_{He,i}&-N_{He,i}&0\\
 0&N_{He,i}&0&0
 \end{pmatrix}.
\]

Here \(V\in\mathbb R^{3\times4N}\) has particle-count coefficients. For differentiable source branches with \(D_g>0\),

\[
 D_yf(t,y)=A(t,y)+U(t,y)V,\quad
 A=\operatorname{blockdiag}_{i=1}^N\bigl[\partial_{y_i}f_i\bigr]_{S\;\mathrm{fixed}},
 \quad U_{ik}=\left[\frac{\partial f_i}{\partial S_k}\right]_{y_i\;\mathrm{fixed}},
\]

with \(U\in\mathbb R^{4N\times3}\). Thus the **entire intercell Jacobian contribution** has rank \(\le3\), not \(\le4\) despite four photon groups, and not \(O(N)\). This is a structural theorem for the original REI instantaneous source and its local 26-event physics, not an assumption of weak coupling. The full Jacobian \(A+UV\) need not have rank three or be stable.

Explicit photon derivatives are \(\partial_{S_k}r_{isg}=-r_{isg}a_{kg}/D_g\) [events/(s·particle)] for fixed local populations. Their contribution to the log-temperature RHS is

\[
 U_{z_i,k}=\frac{1}{U_i^{\rm gas}}\partial_{S_k}R_i
 -\frac{1}{N_{{\rm part},i}}\partial_{S_k}\dot N_{{\rm part},i},
 \quad
 \partial_{S_k}R_i=
 -\sum_{s,g} \epsilon_{sg}r_{isg}\frac{a_{kg}}{D_g},
\]

where the original OTS/cooling/expansion terms depend only locally at fixed \(S\). The particle derivative includes ionization electron creation, so omitting it would incorrectly reduce the thermal nonlocal coupling to direct photoheating alone. \(U_{z_i,k}\) has units \(1/(\mathrm{s}\cdot\mathrm{particle})\); multiplying by \(V\) yields \(1/\mathrm{s}\). Hydrogen and helium nuclear-conservation left-null vectors also annihilate the population rows of each source-coupling column.

### Theorem III: exact three-moment Volterra reduction of continuum error

Let \(y\) be an exact original continuous solution over \([t_0,t_1]\), and \(\hat y\) a piecewise \(C^1\), physically admissible approximate history with residual \(r(t)=\dot{\hat y}(t)-f(t,\hat y(t))\). Assume the segment between \(y(t)\) and \(\hat y(t)\) lies in a smooth single-table-branch physical tube with positive original group denominators; let \(e=y-\hat y\). By the mean-value identity and constant \(V\),

\[
 \dot e=A(t)e+U(t)Ve-r(t)
\]

for path-averaged **local block-diagonal** \(A(t)\) and **three-column** \(U(t)\). Let \(\Phi_A(t,s)\) be the fundamental propagator of the unknown local-block \(A(t)\). Define the exact three-vector \(m(t)=Ve(t)\) [particle count]. Variation of constants yields

\[
 e(t)=\Phi_A(t,t_0)e_0-\int_{t_0}^t\Phi_A(t,s)r(s)\,ds
       +\int_{t_0}^t\Phi_A(t,s)U(s)m(s)\,ds,
\]

\[
 \boxed{m(t)=g(t)+\int_{t_0}^t K(t,s)m(s)\,ds},\quad
 g(t)=V\Phi_A(t,t_0)e_0-\int_{t_0}^t V\Phi_A(t,s)r(s)\,ds,\quad
 K(t,s)=V\Phi_A(t,s)U(s)\in\mathbb R^{3\times3}.
\]

This is exact for the full nonlinear **error dynamics** along the unknown segment, not a closed 3-ODE approximation of the original chemistry. It retains all 46k local 4×4 propagators, yet reduces the only intercell memory kernel to **3×3**. A nonlocal Hessian or a separate global photon IVP is not required to state it.

For a computable error bound, one must actually construct a physically valid tube and outward bounds \(\|r(t)\|\le\rho(t)\), \(\|\Phi_A(t,s)\|\le M_A(t,s)\), \(\|U(s)\|\le u(s)\), and the matching \(V\). Then
\[
 \|m(t)\|\le G(t)+\int_{t_0}^t \|V\|M_A(t,s)u(s)\|m(s)\|\,ds,
\]
\[
 G(t)=\|V\|M_A(t,t_0)\|e_0\|+\int_{t_0}^t\|V\|M_A(t,s)\rho(s)\,ds.
\]
A logarithmic norm \(\mu_W(A(t))\) can provide \(M_A(t,s)=\exp(\int_s^t\mu_W(A(\tau))\,d\tau)\), with consistent dimensionless weighted population/thermal norm. For any interval where \(G(t)\le G_*\) and kernel norm \(\le\kappa\) (units \(1/\mathrm s\)), the Volterra/Gronwall estimate gives \(\|m(t)\|\le G_*e^{\kappa(t-t_0)}\). An additional small-gain sufficient bound is \(G_* /(1-\kappa h)\) when \(\kappa h<1\); small-gain is *not* required for existence of the Volterra solution.

For numerical conditioning one may use positive fixed reference moment values \(D_*=\operatorname{diag}(S_{*,HI},S_{*,HeI},S_{*,HeII})\) and define \(\tilde m=D_*^{-1}m\), \(\tilde V=D_*^{-1}V\), \(\tilde U=UD_*\), yielding a dimensionless 3×3 kernel \(\tilde V\Phi_A\tilde U\) with the same physical spectrum under fixed similarity. This scaling is **not** a change to the source model or its opacity coefficients.

**Admission boundary:** finite photon allocation and rank-three factorization are **derived exact source theorems**, conditional smooth-branch. The Volterra identity is **derived exact given an exact trajectory and approximate history**, but **no original 46k time-continuous residual, tube, logarithmic norm or continuum error numerical certificate has been run** in this R5 stage. Original tick161 V2 discrete candidate is not a continuum solution certificate.

**R5 backup/publish:** an actual new low-rank physical theorem and conditional continuum validation route, not a new owner gate. CENTRAL=28/88, WORKING=33/88, FAST=4/7, canonical delta0; drift watchdog PASS.
## R6 | Same-author blind-referee adversarial assessment of original physics

**F1 / SOURCE VALIDITY:** Original coefficient *asymmetry* is essential. He I uses \(N_{He}^\Sigma\) while He II uses \(N_H^\Sigma\), as checked directly in original \`_explicit_photo_fields\`. Using a symmetric helium denominator would change the original physical source. Minimal correction: bind all \(a_{sg}\) to the unmodified source, as in R3. CLASSIFICATION=BLOCK_NOW for any such substitution.

**F2 / GROUP SUPPORT AND ZERO-CURRENT LIMIT:** If an original group has \(J_g=0\) (including binary64 subnormal original group4 currents) or \(a_{sg}=0\) from \`owner_support\`, logarithms of the individual photo rates are undefined. \(\sum r=J(1-q_0)\), positivity and \(\ln D\) convexity stay valid provided \(D_g>0\). Never claim a log derivative at a zero rate. Use signed/additive rate or group-allocation identities for that case. CLASSIFICATION=FIX_SOON in any future rate-sensitivity implementation; the proved group identities survive.

**F3 / PHYSICAL PARENT CORRELATION:** The three moments \(S(y)\) are not independently selectable sources when testing a particular true H/He history; \(V\) is the physically nuclei-conserving differential of the source moment map. Conditional derivatives with respect to \(\ln S\) at frozen local population may be counterfactual, so for actual perturbations the full \(A+UV\) must include local-numerator, electron and OTS paths. This is an exact modeling obligation, not a demand to compute another source Hessian. CLASSIFICATION=BLOCK_NOW for any interpretation that omits \(A\).

**F4 / TEMPERATURE FEEDBACK INVALIDATES NAIVE CHEMICAL CONTRACTIVITY:** A frozen-rate conservative continuous production-destruction generator has nonnegative off-diagonals, zero column sum and \(\mu_1(Q)=0\), but the original \(\partial_{y_i}f_i\) includes nonlinear local electron rates, cooling and gas-temperature/ionization cross couplings. An elementary two-variable feedback block \(A=[[-1,2],[2,-1]]\) has a positive eigenvalue \(+1\) despite both diagonal losses being negative; it is a mathematical counterexample to inferring full thermo-chemical contraction from the M-matrix property of a *discrete linear population corrector*. This block is NOT an identified REI original Jacobian; to certify stability one must evaluate an original source-aware interval log norm or another validated bound. CLASSIFICATION=BLOCK_NOW for an unqualified contraction claim, not a strong no-go theorem about the original system.

**F5 / VOLTERRA IS CONDITIONAL, NOT AN AUTOMATIC REDUCED SOLVER:** The path-averaged \(A,U\) depend on the unknown true exact trajectory; the 3×3 Volterra equation is an exact error representation but cannot be evaluated from PR354's one-tick discrete source output alone. Need a certified continuous trajectory tube, differentiable branch handling, residual of a selected interpolant, and original data-aware \(\mu_W(A)\), \(\|U\|\) bounds. Without those inputs, report \`CONTINUUM_ERROR=UNRESOLVED\`, not a new numerical PASS or canonical admission. This is the smallest real bridge to the original F05 continuum physics objective, not optional gate proliferation.

**F6 / FALSE ENERGY CONCLUSION:** Source group total resolved ionizations are exactly constant under all \((S_1,S_2,S_3)\) variations only for \`E_g=0\` at fixed \(J_g\). Gas photoheating is NOT generally constant because \(\epsilon_{sg}\) differ. Exact OTS chemical/escaped/unresolved energy remains local source-owned and is not included in the photon group primary excess heating identity. Do not upgrade photon allocation to cosmological total energy conservation. CLASSIFICATION=BLOCK_NOW for this overclaim.

**F7 / MODEL VS REALITY:** The exact rank-three theorem belongs to the original REI instantaneous photon-sharing source, not to arbitrary retarded 3D radiative transfer. Real propagation would add radiation phase-space degrees of freedom. The absence of Bianchi Einstein self-consistency/observational likelihood remains a separate existing REI DAG obligation. CLASSIFICATION=OUT_OF_SCOPE for this bounded F05 theorem, not a new process blocker.

**F8 / COORDINATE AND BRANCH CAUTION:** Original continuous code represents He with triangular variables \((x_{HI},x_{HeI},r_{HeIII},\log T)\). The 4-fraction coordinate transform used in the derivation is smooth and locally invertible only inside strict helium physical simplex, \(1-x_{HeI}>0\), and valid table interpolation branches. V remains constant in the *fraction* coordinates; using triangular variables makes V state dependent and the pathwise rank factorization needs the chain rule. An identical theorem may be expressed in triangular coordinates with \(V(y)=D_yS\), but then path-averaged \(V\) cannot be pulled unchanged through the mean-value integral. Use the fraction representation for the exact three-moment Volterra identity. CLASSIFICATION=FIX_SOON only if a production implementation changes coordinates without the required transform.

**One-pass hostile verdict:** exact photon partition, rank \(\le3\) and conditional Volterra reduction survive. Uncertified original continuum tube/residual remains a real \`INPUT_MISSING/NUMERICAL_UNRESOLVED\` obligation. No strong new no-go, no separate reviewer recursive pass, no false continuous solution admission. Distinct-author referee NOT_RUN, native subagent NOT_RUN (host unavailable).

**R6 backup/publish:** branch one commit on Draft PR #355; central 28/88, working 33/88, fast 4/7, canonical Δ0, source/production unchanged; drift watchdog PASS: actual falsifiable source and stability challenges, no meta loop.
## R7 | Exact CAS derivation and genuine 46,080-cell four-group original-source witness

**Wolfram exact symbolic checks, not a native REI execution.** For symbolic nonnegative \(E,a,b,c,S_1,S_2,S_3\) and positive denominator, Wolfram evaluated \(\partial_{\ell_k}q_s=q_s(\delta_{sk}-q_k)\) and returned an identically **zero** 3×3 difference between its symbolic Jacobian and \(\operatorname{diag}(q)-q q^\mathsf T\). It returned \(\sum_s q_s+q_0=1\) exactly, \(\det(\operatorname{diag}(q)-q q^\mathsf T)=a b c E S_1 S_2 S_3/(E+a S_1+b S_2+c S_3)^4\). Consequently the opacity log-Hessian is PSD and is strictly positive definite when all three active channels and \(E\) are positive. The four independently tested symbolic residuals were all zero: group total rate response \(\partial_{\ell_k}R_g-J_g q_0q_k\), heating response \(\partial_{\ell_k}H_g-J_g q_k(\epsilon_k-\bar\epsilon)\), exact finite group denominator ratio, and common-opacity scaling heating response at \(E=0\). Wolfram also verified \(R_g+J_gq_0=J_g\). These are **new direct model-specific formula checks**; no numerical continuous-flow certificate is inferred.

**Original source-native four-group physical witness (actual execution).** Using only original accepted checkpoint \`g-00000003-tick-000160\` from the source tar, original 46,080 spatial H/He node **intervals**, original three-moment denominators, and original \`ReducedIntervalModel._explicit_photo_fields\`, the bounded aggregate diagnostic \`original_group_witness.py\` executed on the connected Linux source host. Source archive, accepted state, 26-event kernel and continuous RHS SHA-256 are verified before evaluation. It directly forms \(D_g,q_{sg},q_{0g}\) with original owner-support and the exact original HeI/HeII normalization. It evaluates only **four aggregate group records**, not another spatial atlas, no fake three independent datasets and no new 26-event IVP.

- Original accepted proper time \(t_{160}=779495799866.9248\) s. Global moment intervals [physical particle counts]: \(S_{HI}=[6.7966152322008365,6.798828287895977]\times10^{62}\), \(S_{HeI}=[4.092953249688367,4.1057366588935733]\times10^{61}\), \(S_{HeII}=[4.350710201123768,4.35071147975618]\times10^{65}\).
- Group 0: original \`owner_support=[false,false,false]\`. \(J_0\simeq4.2522110\times10^{50}\) source current units/s, all resolved ionizing species channels exactly zero by original support; external share encloses 1. Tiny signed interval artifacts from outward expansion around structural zero do **not** represent physical negative photon counts.
- Group 1: only \`HeI\` supported; \(q_{HeI,1}=[0.0630294878,0.0632387952]\), external \(q_{0,1}=[0.9367736539,0.9369581019]\), \(J_1\simeq7.3652364\times10^{49}\); original resolved photoionization \([4.6422707759,4.6576867577]\times10^{48}\) events/s and primary photon heating \([3.7620753158,3.7745683580]\times10^{37}\) erg/s.
- Group 2: \`HI\` and \`HeI\` supported; \(q_{HI,2}=[0.5893592646,0.5904189967]\), \(q_{HeI,2}=[0.4091708810,0.4110530213]\), external opacity upper about \(7.945\times10^{-321}\) from the original outward zero, \(J_2\simeq1.0348161\times10^{48}\). Resolved events \([1.0332950388,1.0363393356]\times10^{48}\)/s; primary photoheat \([4.4528538932,4.4647779313]\times10^{37}\) erg/s.
- Group 3: all three species supported, \(q_{HeII,3}=[0.9971651655,0.9971705164]\), but the original \(J_3\in[0,10^{-323}]\) is binary64-subnormal; thus its opacity **allocation fraction** cannot be misrepresented as a physically significant HeII ionization current at this tick.

**Actual integrated primary photoionization:** all 4 groups combined \([5.67556581469568,5.694026093361244]\times10^{48}\) native ionizations/s (event count rate). **Actual integrated primary photoheat:** \([8.214929208940955,8.239346289239531]\times10^{37}\) erg/s. Recomputing the genuine original 46,080-node \`_explicit_photo_fields\` and directly summing its HI+HeI+HeII photon rate and its primary heat yields enclosing intervals \([5.67556581469568,5.694026093361243]\times10^{48}\) /s and \([8.214929208940955,8.23934628923953]\times10^{37}\) erg/s, **both overlap** the independently aggregated group expression. They differ only in final displayed endpoint ulps, not exact byte identity of distinct formulas. This is a source/operator **numerical consistency check**, not a proof of continuum ODE truncation error.

**Physically important contrast:** within these conservative interval sums group 1 contributes about \(81.5\)–\(82.1\)% of resolved ionizations but \(45.7\)–\(45.9\)% of primary photoheat, while group 2 contributes about \(18.1\)–\(18.3\)% of resolved ionizations and \(54.0\)–\(54.3\)% of photoheat. A much smaller photon number in the harder group can dominate heating due its original excess energy. These percentages are conservative ratios of separately enclosed totals, not measurements of real sky/IGM observations. OTS/cooling/expansion are not included in the primary heating column.

**Verification and provenance:** actual source diagnostic replayed once after code change with \`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1\`; both source-output JSON files were **byte exact** SHA256 \`5f050d6c57cfc06a80af5e02c2c64f2cba25776f618dd2b3890cbfa4dcb57fd9\`. Separate Python stdlib readback checked exactly 4 owner-support patterns, original source/archive state/kernel locks, 4/4 positive original denominators, each 4-owner partition interval containing 1, direct and native total photoionization/heat overlap, and zero canonical delta. The Python runtime printed NumPy 1.x optional compiled-extension compatibility warnings but the source call exited 0; no runtime repair, source mutation or false error-classification promotion.

**R7 backup/publish:** source-derived four-group JSON + executable standalone aggregate check + all mathematical calculations on one Draft PR. Source tool invocation is original-physics numeric verification, not an approved tick161 state or a full entire-interval run. CENTRAL=28/88, WORKING=33/88, PHYSICAL_FAST=4/7, canonical delta0. Drift watchdog PASS: physical photon allocation+heating consequence advances actual original IGM source understanding.
