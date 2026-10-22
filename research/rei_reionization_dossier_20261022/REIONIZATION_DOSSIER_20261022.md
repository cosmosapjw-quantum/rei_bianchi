# Reionization in non-tilted LRS Bianchi I

## Updated microphysics dossier and isotope–ion evolution atlas

Artifact series: 20261022. Repository: cosmosapjw-quantum/rei_bianchi, Draft PR 219. This is an updated scientific synthesis of the seven-chapter October 14 standalone dossier, with a dated computational results section and a reproducible figure atlas. It does not overwrite the private source document or certify its unexercised mechanisms. Actual creation and execution times are recorded in the accompanying receipts; the series label is not a wall-clock timestamp.

The controlling editorial sources are the user's three attached PDFs: the 73-page standalone reionization dossier, the 33-page two-chapter reionization series volume, and the 7-page nuclear-capture volume. Their exact PDF hashes, extracted-text hashes and substantive reconciliation are in `ATTACHED_DOSSIER_RECONCILIATION.json` and `.md`. The nuclear volume works through n+p <-> D+gamma; it is a specialized derivation, not a provider for the entire eighteen-family network. This new synthesis preserves the seven-chapter scope map while adding the actual pilot results; the original derivations remain in their source volumes.

### Executive result

The present sandbox experiment evolves an atomic H/D/He/Li charge network in a non-tilted, locally rotationally symmetric Bianchi I background from mean-scale-factor redshift z=20 to z=2. It resolves the requested initial shear, radiation-stress and matter-stress comparisons separately. The background density, prescribed gas-temperature function, UV prescription, atomic rates and initial abundances are held fixed across each comparison. The other two *initial* physical axes are held at zero; their subsequent histories respond dynamically.

The atomic histories and the newer nuclear calculation are distinct model layers. The former supplies H1, D, He3, He4, Li6 and Li7 ionic populations. The latter supplies conditional total tritium and neutron inventories under an all-bare, instantaneous-thermalization, passive-reservoir approximation. It does not supply tritium charge fractions. The atlas explicitly displays that missing partition instead of manufacturing neutral or ionized T curves.

The previous exact-zero tritium result was imposed by the atomic implementation, not established by a nuclear production calculation. Once the admitted nuclear creation terms are included, the conditional maximum cumulative T production is about 3.96234e-96 nuclei per baryon and the surviving inventory at z=2 is about 1.39389e-104. These are positive within the specified extrapolated rate model, extraordinarily small, and not a calibrated physical prediction for nonthermal fusion in the intergalactic medium. The two quantities differ because production is cumulative whereas T decays on a 12.312-year half-life.

The stronger shear cases visibly alter expansion and the relation between time and redshift. Matter-only atomic differences in the original cold family lie below the existing numerical-control discrepancy and are labelled unresolved. A separately matched semi-relativistic family now tests initial Pi_m up to 0.1: its maximum ionic-fraction change is 5.45518e-6, whereas the strongest-case discretization/tolerance control differs by 2.31265e-10. The earlier unresolved statement therefore does not extend to this stronger family. This is separation from an observed numerical discrepancy, not empirical validation or a rigorous error bound. The 28 base designs plus 7 stronger-matter designs are supplied in PNG and PDF; the atlas also preserves 13 earlier atomic and 5 nuclear figures with their historical scope, 53 figure designs altogether.

### Evidence and claim map

| Layer | Actually supplied | Scientific ceiling |
|---|---|---|
| Covariant dossier | Updated definitions, event accounting and seven-chapter implementation map | Theory scaffold, not a newly solved transport/observer problem |
| Atomic pilot | 82 saved quotient trajectories, including three controls; one saved full-state reference | Prescribed-temperature, prescribed-UV preliminary atomic test fluid |
| Nuclear extension | 18 reaction families on 82 saved histories; direct positive T/n stock evolution | Conditional all-bare, instant-thermalization passive calculation |
| Base controlled atlas | One additional positive matter-amplitude case; matched initial physical axes; 28 figures | Scoped comparison using the original cold-family closures |
| Stronger matter test | Four new nominal cases and one refined control; 7 figures | Separately matched semi-relativistic family; no observational cosmology claim |
| Production reionization | Thermal, nonthermal, ionic nuclear projection and source feedback still incomplete | HOLD; no complete FLRW or Bianchi I production admission |

## 1. Covariant radiation–matter problem and the updated state inventory

### 1.1 Frames, clocks and normalization

Use metric signature (-,+,+,+), physical proper time t in seconds, and dimensional c, hbar and kB. A length clock s=ct must not be substituted into a time derivative without the corresponding factor of c. Mean-scale-factor redshift is defined by 1+z proportional to a^(-1). The plotted time coordinate is each case's elapsed proper time in Myr since its z=20 initial surface, not the age of the Universe since a Big Bang. One Myr is one million Julian years of 365.25 days.

For the current non-tilted, common-rest-frame model, Y_A=n_A/n_B is the abundance per baryon and sum(A Y_A)=1. In a general tilted extension, a normal-frame density is D_A=gamma_A n_A; normal-density abundances D_A/D_B and proper-density ratios differ. The original dossier's frame distinctions remain necessary. A covariant evolution equation also does not guarantee that redshift is globally invertible in every geometry.

### 1.2 One physical event, one number and energy ledger

A nonnegative differential event rate dR_r, measured per physical volume and physical second, underlies both the stoichiometric source and four-momentum transfer. In compact notation:

```text
R_A = sum_r integral nu_Ar dR_r
Q_A^a = sum_r integral Delta p_Ar^a dR_r
nabla_a N_A^a = R_A/c ; nabla_a T_A^{ab} = Q_A^b/c
dY_A/dt = (1/n_B) sum_r nu_Ar R_r    [common frame, conserved baryons]
```

The same event must not independently heat the gas twice through a chemistry operator and an auxiliary energy source. A closed event includes photons, recoil, internal excitation, outgoing electrons and neutrinos as applicable. Nuclear beta decay changes the nuclear electric-charge tally; its emitted electron restores the full electric-charge ledger. The current nuclear output records available Q and electron counts, but it does not solve thermal deposition or the neutrino energy partition.

### 1.3 Replace the historical 17-state vector by a 21-entry census

| Nucleus | Mass number A | Nuclear charge Z | Census entries | Current numerical status |
|---|---|---|---|---|
| neutron n | 1 | 0 | n_0 | Conditional total from the nuclear lane |
| H1 | 1 | 1 | H1_0, H1_1 | Atomic ion fractions solved |
| D | 2 | 1 | D_0, D_1 | Atomic ion fractions solved |
| T | 3 | 1 | T_0, T_1 | Total solved conditionally; charge partition unresolved |
| He3 | 3 | 2 | He3_0, He3_1, He3_2 | Atomic ion fractions solved |
| He4 | 4 | 2 | He4_0, He4_1, He4_2 | Atomic ion fractions solved |
| Li6 | 6 | 3 | Li6_0 through Li6_3 | Atomic ion fractions solved; high-charge nominal zeros explicit |
| Li7 | 7 | 3 | Li7_0 through Li7_3 | Atomic ion fractions solved; high-charge nominal zeros explicit |

An output census of 21 entries is not a claim of 21 independent evolved populations. Under fixed isotope totals, equal electronic rate operators within an element and equal conditional initial populations, the existing quotient evolves nine charge fractions: two H, three He and four Li. H1/D, He3/He4 and Li6/Li7 share their respective conditional electronic vectors. The reduced and unreduced implementations were already compared. That proof does not authorize assigning a newly produced T population the H vector: nuclear conversion and daughter charge injection invalidate its original premises.

### 1.4 Non-tilted LRS geometry and separate matter/radiation stress

Let a_perp=a exp(-b), a_parallel=a exp(2b), and s=dot(b). In an orthonormal frame, shear is diag(-s,-s,2s), and each anisotropic stress is diag(-p_X,-p_X,2p_X). With energy density in J/m^3, K=8 pi G/c^2. The implemented conventions are:

```text
H^2 = K epsilon/3 + Lambda c^2/3 + s^2
dot(s) + 3 H s = K (p_m + p_gamma + p_nu)
S = sqrt(6) s/H ; Sigma = |S|
P_X = sqrt(6) K p_X/H^2 ; Pi_X = |P_X|
P_r = P_gamma + P_nu ; Pi_r = |P_r|
Pi_total = |P_m + P_r|
```

This uses the full Frobenius contraction; a half-contraction convention differs by sqrt(2). Radiation components are summed with sign before taking a norm. Equal norms can represent different orientations, and a small total stress can conceal cancellation between two nonzero sectors. The matter anisotropic stress in this pilot belongs to its collisionless massive nonbaryonic component, not an imposed anisotropic baryon gas. The atomic baryons are isotropic by closure.

## 2. Atomic processes and energy transfer

### 2.1 Active rate model

The active atomic model includes photoionization and radiative recombination. It uses a prescribed E^(-2) external UV spectrum with support 5–60 eV. Its amplitude corresponds to Gamma_HI=5e-14 f(z) s^(-1), where f(z)=[1+tanh((7.5-z)/1.25)]/2. The prescribed gas temperature is Tgas=100+9900 f(z) K. Geometry affects expansion, proper time and the radiation/matter moments; it does not change intrinsic local atomic or nuclear constants.

In each charge block, write G=P+n_e R, with photoionization matrix P and recombination matrix R. Off-diagonal transition entries are nonnegative and each column sums to zero. Electron density couples the charge blocks. The implemented analytical atomic Jacobian includes the derivative of that electron closure:

```text
n_e = w^T f
df/dx = (P+n_e R) f/H
J_ff = [P+n_e R + outer(R f,w)]/H
```

Dropping the outer product would discard the physical electron-mediated coupling. The background block uses the inherited hybrid derivative treatment. No clipping or renormalization is used to conceal an accepted-state failure. Completed operator, conservation and reduced/full comparison checks are reused here.

### 2.2 Status of additional microphysics

| Mechanism | Dossier role | Status of this atlas |
|---|---|---|
| Photoionization and radiative recombination | Charge-transfer kinetics | Active under the declared source/rate model |
| Isotope-dependent spectroscopy | Reduced masses and electronic operators | Equal-element approximation; no resolved isotope shift claim |
| Collisional ionization, dielectronic recombination and charge exchange | Additional thermal/electronic pathways | Not activated in this pilot |
| Molecules, dust and stellar source calibration | Astrophysical closure | Absent |
| Nuclear injection into charge states | Stoichiometric ionic source | Not yet coupled |
| Gas heating/cooling from all events | Shared energy conservation | Prescribed T; no solved thermal history |

Reduced-mass and charged-ion dipole corrections from the original theory remain available for a future isotope-specific provider. They are not inferred merely from a nucleus label. The equality quotient must be disabled or re-derived when those effects or nuclear injection become active.

Nominal Li III and Li IV are zero because the retained UV lacks the necessary photons and the corresponding initial populations vanish; the recombination operator itself is not deleted. Separate positive-population controls exercised those transitions. T's old zero had a different origin: both output charge slots were filled with zero and nuclear production was absent.

## 3. Neutral-hydrogen impact ionization and positive spectral moments

The original dossier treats an impact-ionization construction with a specified one-centre Coulomb model, spectator 1s state and classical projectile trajectory. Its thresholds and spectral-moment representations are conditional on those approximations. They are not universal measured cross sections or a substitute for a calibrated nonthermal-electron provider.

The useful numerical principle is to retain nonnegative spectral/event measures and to integrate regular threshold coordinates rather than subtract large nearly equal energies. For any future rate-table adapter, the interpolation contract must specify temperature or projectile-energy domain, units, thresholds, extrapolation and derivative behavior. A table entry below machine range needs a log value and a status; it must not silently become a physical zero.

This chapter supplies a donor methodology, not an activated channel in the present histories. The UV-driven atomic curves therefore do not include secondary electron ionization. No figure is interpreted as evidence for the unimplemented impact-ionization model. A future implementation must couple its outgoing-electron distribution and heat partition through the common event ledger of Chapter 1.

## 4. Nuclear capture, photodisintegration and tritium production

### 4.1 Preserve the distinctions in the original capture theory

For a neutral capture, K(E)=sigma(E) v(E) is the regular low-energy kernel. Maxwell averaging that kernel is preferable to manipulating a divergent 1/v cross section alone. The attached nuclear volume gives a regular integration coordinate with weight y^2 exp(-y^2) K(kB T y^2), and a low-temperature moment expansion K0+(3/2)K1 kB T+(15/8)K2(kB T)^2+... under its Taylor-coefficient convention. A truncated integration interval needs a bound on the remaining integrand before its tail can be certified. These neutral-capture results do not establish charged-particle constant-S behavior.

The original n+p to D+gamma example gave K(0)=7.3524012e-26 m^3/s for its chosen effective-theory amplitude and masses. The present evaluated thermal anchor, 0.3326 barn at 2200 m/s, gives 7.3172e-26 m^3/s under a 1/v continuation. These are distinct provider choices; their difference is not an empirical error bar. The nuclear volume's illustrative equal-mass parameters M=938.92 MeV and Q=2.224575 MeV give a stationary-target threshold shift about 1.31923 keV. Smallness relative to rest energy does not make that shift small relative to kB T.

Microscopic reciprocity, stationary-target photon absorption and thermal-equilibrium inverse rates are different ensemble statements. The unpolarized n+p/D+gamma cross-section reciprocity contains a 2/3 degeneracy factor including the two incoming photon polarizations. The leading thermal equilibrium relation contains 4/3 and the Maxwell translational factor. A recoil-shifted stationary-target photon threshold cannot simply replace Q in an otherwise recoil-free equilibrium formula.

The original Planck-photon integral remains a theoretical branch. Its exponentially small positive tail must not be confused with an exact zero caused by compact external spectral support. The current nuclear photo entries are zero only for the specified external 5–60 eV source under the declared target approximation. This does not zero the CMB tail, all photons in nature, or internally emitted capture photons in a future reprocessing model. Capture photons currently escape.

### 4.2 Finite nuclear inventory and sources

The supplied drawing has three atomic labels and sixteen nuclear/capture/decay labels. Duplicate forward/inverse labels reduce the nuclear part to thirteen event families. Five explicit closure families are added, giving eighteen families and thirty-four physical directions. This is the complete declared dossier-plus-closure inventory, not every possible light-element reaction.

| Family | Forward process | Provider/model used |
|---|---|---|
| 1 | n + p -> D + gamma | Evaluated thermal anchor, 1/v |
| 2 | D + p -> He3 + gamma | Low-energy constant S continuation |
| 3 | D + D -> T + p | Low-energy constant S continuation |
| 4 | D + D -> He3 + n | Low-energy constant S continuation |
| 5 | D + D -> He4 + gamma | Low-energy constant S continuation |
| 6 | D + T -> He4 + n | Low-energy constant S continuation |
| 7 | D + He3 -> He4 + p | Low-energy constant S continuation |
| 8 | T + p -> He4 + gamma | Selected radiative-capture model; E1 gap retained |
| 9 | He3 + n -> He4 + gamma | Evaluated thermal anchor, 1/v |
| 10 | He3 + n -> T + p | Evaluated thermal anchor, 1/v |
| 11 | T + He4 -> Li7 + gamma | Low-energy constant S continuation |
| 12 | T -> He3 + electron + antineutrino | Evaluated T half-life |
| 13 | n -> p + electron + antineutrino | Evaluated neutron lifetime |
| 14 | D + He4 -> Li6 + gamma | Explicit Li6 closure, constant S |
| 15 | Li6 + p -> He3 + He4 | Explicit destruction closure, constant S |
| 16 | Li6 + n -> T + He4 | Thermal total-absorption anchor assigned to dominant branch |
| 17 | Li7 + p -> He4 + He4 | Explicit destruction closure, constant S |
| 18 | D + n -> T + gamma | Thermal capture closure, 1/v |

Forward binary event rates include identical-reactant factorials. Reverse two-body rates include spin, symmetry and Boltzmann factors and the thermodynamic product-of-nuclear-masses factor from the common mass table, (m_i m_j / m_k m_l)^(3/2). Eight external photon inverse directions have zero support; twenty-six directions have finite populated log rates. Finite logarithms far below floating-point range are retained. Constants, citations, units, Q values, branch assumptions and exclusions are in the frozen nuclear provider inventory and coefficient registry accompanying the restoration package.

Important omissions include weak p+p production, Be7 and its electron capture, some Li neutron/proton channels, screening, neutral-atom reaction dynamics, nonthermal stopping and internally generated hard-photon reprocessing. The user-requested nuclear creation terms have been implemented for the declared finite scope; these omissions remain explicit development dependencies.

### 4.3 What the tritium audit establishes

The inherited `lift()` function filled both T entries with zero. No nuclear fusion source appeared in that atomic RHS. A production line in a diagram alone could not make the old output positive. The separate direct DD calculation first demonstrated positive T creation; the full finite network then retained all its declared creation and destruction directions.

| Quantity | Admitted conditional result |
|---|---|
| Maximum cumulative T births per baryon | 3.9623422053e-96 |
| Maximum surviving T at z=2 per baryon | 1.3938915088e-104 |
| Maximum surviving n at z=2 per baryon | 2.1929560189e-110 |
| Largest bulk-reservoir gross relative change | 1.4388714811e-80 |
| Largest finite-channel 1x-to-2x cumulative difference | 0.0048439812 dex; original limit 0.02 dex |
| Endpoint T spread across the old 82 cases | 5.92e-13 dex; roundoff-scale, no physical ranking |

Direct D+D production dominates. He3(n,p)T, D(n,gamma)T and Li6(n,alpha)T are included and positive within the model, with maximum cumulative log10 yields approximately -117.101, -123.715 and -126.855 respectively. The thermally activated inverse of D+T also has a finite but vastly smaller log yield. New trace inventories are extremely small, so bulk feedback is negligible *within this conditional model*, not by a model-independent bound.

NACRE II tabulated thermonuclear rates concern much higher temperatures than this pilot's 100–10000 K gas. The constant-S extension here is an explicit low-energy extrapolation, not direct empirical validation at the sampled few-eV Gamow energies. DD products are born energetic; using thermal neutron coefficients immediately is the stated instantaneous-thermalization assumption. A physical nonthermal source calculation must treat slowing and competing reactions before using these yields observationally.

### 4.4 Positive stock versus subtraction of large event totals

The authoritative inventories are the directly propagated `log_T_n` values. Subtracting nearly equal cumulative production and destruction totals loses the tiny remaining stock; the earlier event reconstruction even produced negative or zero neutron net values. Those values are retained as numerical diagnostics, not used as physical neutron abundances. A small gross-normalized event residual is not a small stock-relative error.

The first full-network trapezoidal treatment failed its original refinement criterion for an extremely narrow reverse-rate interval. Its failed outputs are preserved. A single targeted repair integrated a log-linear event rate analytically in proper time. The revised 1x-to-2x comparison passed the unchanged 0.02-dex criterion. No old background IVP, failed-run deletion or acceptance-threshold relaxation was needed. The independent decision is PASS_SCOPED for this conditional implementation.

## 5. Nonthermal electrons, thermalization and gas temperature

An ionizing electron can create additional active electrons before joining the thermal population. Its slowing, ionization and thermalization rates must therefore be distinguished. A consistent event partition separates daughter kinetic energy, ionization threshold and deposited heat; it cannot assign the threshold cost to both an internal-energy variable and gas heating.

For nonrelativistic species sharing one thermal temperature, the original dossier's thermal energy has the structure U=(3/2) kB (N_nuc+N_th) T. Active nonthermal electrons belong to a separate distribution. Changing the number of thermal particles changes heat capacity, even when the total available energy is unchanged. Spectator nuclei and electrons must be included in the EOS and thermal CX composition contract.

The present atlas uses the actual stored `T_K`, but that temperature was prescribed rather than solved. Thus it is meaningful to plot an abundance against this model gas temperature; it is not a prediction of self-consistent reionization heating. Different cases share T(z) while their T(t) mappings differ because elapsed time differs. The paired secondary axis consequently shows the explicitly labelled matched reference case's mapping only, never a universal clock for every curve.

The next coupled solver must add daughter charge injection, nonthermal stopping, a shared EOS and one energy owner for each reaction. The T total cannot be silently pasted into old ionic states or used to modify electron density without that contract. The old nuclear Q ledger remains available-energy accounting until the deposition operator is admitted.

## 6. Finite-aperture polarized observations

The original observer theory specifies an observer tetrad, screen basis, aperture and analyzer. A positive polarization coherency matrix yields the Stokes constraint Q^2+U^2+V^2 <= I^2. Positive transport and correctly transformed event measures are needed to preserve that constraint. A Jacobi-map flux conversion must not also be inserted as an extra intensity multiplier.

These results remain useful for later light-cone observables, but the current homogeneous time histories do not implement an observing aperture or synthetic polarized sky. A radiation quadrupole or a stress curve is not by itself a measured polarization map. The earlier illustrative Kasner/observer constructions are not empirical validation of this Bianchi I pilot.

An observational extension needs calibrated astrophysical sources, line-of-sight transport, frequency-dependent opacity, an observer specification and a comparison dataset. This dossier therefore reports dynamical and abundance histories, not a fit to reionization optical depth, 21-cm data, CMB polarization or primordial abundance observations.

## 7. Conservative approximation, optimization and error interpretation

### 7.1 Preserve the physical event structure when optimizing

Rate tables should depend on local state variables and provider domain, not be regenerated for every background trajectory. The inherited pilot already separates fixed photo integrals and electronic generators from the geometry. Its quotient reduces eighteen populated isotope fractions to nine only under explicitly checked equality assumptions. Nuclear rates are evaluated in log space and the fast T/n subsystem uses an exact frozen linear propagator on each interval.

Safe future table keys include provider/version, units, temperature coordinate, composition dependence and radiation-shape identity. Interpolation must preserve nonnegativity, thresholds and detailed-balance relationships where those relationships apply. A temperature table alone is insufficient for a rate depending on a nonthermal spectrum, target charge state or radiation distribution. Parallelism across cases is independent; shared mutable state must not mix their clocks or event ledgers.

### 7.2 Numerical, closure and empirical errors are different

The saved L16/L24 and tighter-tolerance checks found a maximum conditional-charge discrepancy 3.3929270504e-9 over three selected controls. That observed discrepancy is neither a rigorous global error bound nor a statistical uncertainty interval. It is nevertheless an important warning scale for interpreting a matter-only response of order 4.16e-10. The atlas marks that response unresolved at the saved accuracy and does not subtract numerical noise to manufacture a signal.

Model uncertainty from a prescribed UV field, constant-S continuation or instant thermalization is not estimated by increasing angular order. Conversely, a valid local reaction identity does not establish trajectory convergence or observational validity. The original dossier's full variation of event weights and outcomes, shared covariance and observable-adjoint ideas remain the intended framework for future uncertainty work; they are not newly evaluated confidence intervals here.

### 7.3 Reuse and durable execution

The original 83 IVPs comprise 82 quotient histories and one populated-isotope reference. The existing nuclear postprocessor already used all 82 quotient histories. The base atlas reuses those histories and completed controls, and adds exactly one missing S=0, Am=0.8, Ar=0, L16 case. Its new nuclear postprocess is joined by exact case name and time grid. The user's subsequent larger-Pi_m request adds a separate five-IVP contract: four nominal histories and one refined control, with nuclear postprocessing of only the four new nominal histories. Thus this dossier unit has six new IVPs in total. No old 82-case sweep or NCP run is repeated, and no expired NCP deadline or budget is reset.

The missing cold case used 1.9918 CPU seconds. The separate strong-family calculation used 128.4184 CPU seconds and 22.7350 wall seconds, within its 180-CPU-second cap; CPU and wall cost differ because numerical libraries can use multiple threads. Rendering and PDF composition have separate costs and do not count as solver trajectories. The final receipts preserve the measured distinction.

The new-case receipt, plot manifest and initial-axis CSV record the actual case, sources, hashes, runtimes and fixed-axis checks. Rendering is presentation work, not another solver run. Independent review checks the changed dependencies and plot claims; it does not reopen every completed historical validation.

## 8. Controlled parameter experiment and figure atlas

### 8.1 Three required independent comparisons

| Comparison | Varied physical initial axis | Other fixed physical initial axes | Selected control inputs |
|---|---|---|---|
| Shear | Sigma_0, positive orientation | Pi_r,0=Pi_m,0=0 | S_0=0, 0.01, 0.05, 0.2, 0.6 |
| Radiation | Pi_r,0, positive orientation | Sigma_0=Pi_m,0=0 | Ar=0, 0.4, 1.6; Am=0 |
| Matter | Pi_m,0, positive orientation | Sigma_0=Pi_r,0=0 | Am=0, 0.8, 1.6; Ar=0 |

Am and Ar are distribution-shape inputs, not the physical Pi values. The figure legends and `CASE_TABLE.csv` use diagnostic physical norms and retain signed components. Tiny numerical residuals around zero are checked against the frozen absolute tolerance 1e-15. Positive varied axes must be strictly ordered. All comparisons preserve the same n_B(z), T(z), UV closure, rate model and initial isotope populations. H(z), elapsed time and subsequent stresses are allowed to respond.

Each comparison supplies six figure designs: isotope totals versus redshift and proper elapsed time; ionic populations versus both axes; conditional-ion differences from the zero-axis reference at common redshift; and signed shear/stress, photon/neutrino, expansion and elapsed-time context. Difference curves are not equal-time comparisons. The redshift panels run from 20 to 2 from left to right.

All 35 new figure designs follow the user's revised display convention. Abundances use a logarithmic ordinate labelled with powers of ten. Log-domain T/n values below the representable linear floating-point range retain their exact stored log coordinates; a second logarithm is never applied. Signed changes, signed stresses and signed control residuals use a symmetric logarithmic scale with an explicitly stated linear region around zero. That display threshold is not a detection threshold or error bar. Exact zeros are retained or annotated, not replaced by a positive floor.

The lower redshift axis is paired with upper elapsed time in Myr from the matched reference trajectory. On the separate time plots, each curve uses its own actual elapsed Myr, and the upper axis gives redshift for the reference trajectory only. Both mappings use the saved monotonic samples without extrapolation. The reference identity is stated on the figures: the original zero case for base comparisons, the new semi-relativistic zero case for the strong-matter comparison. Linear horizontal scales retain the initial t=0 point and give a clear z=20 to2 interval; a logarithmic time axis would omit that origin. The 18 historical figures are preserved as an explicitly archived appendix in their original presentation, rather than silently rewritten as new results.

The absolute abundance is Y=n/n_B, not a fraction of its element. This preserves visibility of the Li6/Li7 and He3/He4 abundance differences even when conditional electronic histories coincide. Zero high-charge populations are annotated instead of placed at an arbitrary log floor. Initial T/n zeros are excluded from log ordinates and identified as such. T/n lines are conditional total nuclei only, never T I/T II predictions.

### 8.2 Physically interesting additional cases

The signed-stress gallery compares negative single-sector orientations, positive/negative matter–radiation combinations, and two initially cancelling configurations. Cancellation concerns the sum P_m+P_r, not the separate positive norms. It need not persist as the components redshift and exchange momentum differently. Rounded amplitude tokens in filenames are never used to decide whether cancellation is exact.

The shear-orientation gallery compares S=+0.6 and S=-0.6 with equal norm, the isotropic reference and mixed-stress cases. Opposite signs represent different axis orientations; their difference is not a derivative with respect to the nonnegative Sigma norm. The stronger combined cases are selected to make real dynamical effects visible while preserving the inherited positive-distribution domain. Enlarging Pi arbitrarily would leave that domain and is not used as a plotting trick.

Each additional gallery supplies totals, ions and signed dynamics, with both time/redshift population views. Photon and neutrino stresses are displayed separately inside every context figure. The primary and additional figures together cover the full frozen 28-design manifest. Historical atomic and nuclear figures appear in a clearly marked appendix; they retain their original scope and are not counted as new controlled comparisons.

### 8.3 Reading overlapping curves

Fixed bulk isotope totals overlap because this is the passive-reservoir approximation, not evidence that all nuclear reactions were omitted. Same-element ionic curves can overlap by the proven equality quotient. Trace T/n endpoint curves nearly coincide because their decay/thermal source balance is local and the old-case spread is roundoff-scale. Neither overlap nor a visually magnified difference alone establishes an effect. Read the signed difference panels alongside the observed control discrepancy and the model-status captions.

The strongest visually apparent contrasts arise in shear, elapsed time and the timing of ionization, while the original weak matter-only charge response remains unresolved. Results measured by the renderer are recorded without rounding in `GROUP_METRICS.json`; the full case identities and source joins are in the machine-readable manifests. The requested extension to larger matter stress is a separately declared experiment, with its own matched background and numerical control; the original weak-range statement is not extrapolated to it.

| Original controlled slice | Largest absolute conditional-ion change at common z | Location |
|---|---|---|
| Sigma | 2.5419269658e-3 | Li II; Sigma_0=0.6; z=10.87496 |
| Pi_r | 2.1083219726e-8 | Li II; Ar=1.6; z=10.607 |
| Pi_m | 4.1617853608e-10 | He II; Am=1.6; z=6.877 |

The last value is below the observed 3.3929270504e-9 control discrepancy. The original Pi_m,0 values are approximately 0, 5.46887435e-4 and 1.09377487e-3. This small range cannot answer whether a substantially larger admissible matter stress produces a resolved response.

### 8.4 Requested stronger-Pi_m test: a measurable response within a declared family

The angular distribution is proportional to W(mu)=1+A_m P2(mu). Nonnegativity requires -1 <= A_m <= 2. In the original massive component, m/Tref=30 and its initial fraction of the matter energy is 0.1; the realized Pi_m,0 per unit positive A_m is 0.000683609293. Therefore this angular family cannot reach Pi_m,0 above 0.001367218586. Simply setting its A_m to achieve 0.01 or 0.1 would make the distribution negative. This is a bound on this family, not on all possible matter models.

The new family instead has m/Tref=3 and an initial massive-component fraction 0.3. Tref is its nonbaryonic momentum scale, not the gas temperature. Its initial equation-of-state ratio is pbar/rho=0.1748400251 and the initial energy-weighted squared speed is 0.5245200754 c^2. Reflection symmetry keeps bulk velocity zero, so the family remains non-tilted despite its larger dispersion. This is a hypothetical semi-relativistic comparison, not an observationally allowed dark-matter fit.

Within this family, initial total energy, component energy, isotropic pressure, particle number, Hubble rate, baryon density, gas temperature, radiation monopoles and atomic populations are matched. Only the positive angular quadrupole is changed, giving actual Pi_m,0=0,0.01,0.05,0.1 while Sigma_0=Pi_r,0=0. The corresponding amplitudes are approximately 0,0.1305473,0.6527365,1.305473, all strictly inside the positive domain. Nominal initial energy, pressure and number matching residuals are at most 4.44e-16 relative, and the H matching residual is zero at printed precision. Initial fixed axes and actual target norms pass their frozen gates.

| Actual initial Pi_m | Maximum absolute conditional-ion change from the matched new zero case | Change / reference discrepancy |
|---|---|---|
| 0.01 | 5.4664637039e-8 | 16.11 |
| 0.05 | 1.3657043808e-6 | 402.52 |
| 0.10 | 5.4551782906e-6 | 1607.81 |

The maxima occur in the complementary Li I/Li II fractions near z=10.69579. At Pi_m,0=0.1, the largest H charge change is 2.43345e-6, the largest He change is 3.20300e-6, and the largest electron-per-baryon change is 1.98264e-6. These are conditional charge-fraction differences, not relative errors or absolute Li abundances. Isotope-specific absolute populations remain in the ion panels. The model's optical-depth accumulator changes by 2.04403e-6 at the endpoint; this is an internal model output, not an observed optical-depth constraint.

The strongest case was compared with L24 radiation moments, 48x24 momentum cells, fourth-order Gauss quadrature and tighter Radau tolerances, instead of the nominal L16/24x12/third-order settings. The maximum conditional-fraction discrepancy is 2.3126511817e-10; relative H and elapsed-time differences are 1.82e-11 and 1.43e-10. The nominal and refined Li II effect at the peak have the same sign and differ by 1.01e-10. The initial pressure changes by only 2.53e-10 relative under this quadrature refinement, within the frozen gate.

The table uses the conservative reference scale max(2.31265e-10,3.39293e-9), where the second number is the earlier cold-family control discrepancy. The stronger effects exceed ten times that observed scale under the predeclared classification. This supports a response separated from the observed numerical-control discrepancy in this conditional family. One refined high-case control does not certify a global error bound for all cases, a statistical confidence level, or the empirical validity of the prescribed UV/temperature model.

The correct conclusion is therefore two-part: the tested original cold-family response is unresolved at its saved accuracy; the new stronger-stress family shows a response distinguishable from the retained numerical-control scales. A comparison between a hot case and the old cold zero case would also change pressure/composition and is not used as a Pi-only experiment. Seven additional figures display the strong-family totals, ions, signed response, dynamics and control comparison, preserving all 28 original figures.

### 8.5 Why the scalar atomic response is small and approximately quadratic

The measured maximum changes divided by Pi_m,0 squared are approximately 5.46646e-4, 5.46282e-4 and 5.45518e-4 for the three nonzero cases, a spread about 0.21%. The actual equations give a physical explanation around the matched isotropic anchor. An angular quadrupole induces shear and stress at first order in A_m. The scalar matter energy-work term contains the contraction 6 s p_m, while the radiation monopole couples to its quadrupole through a product proportional to (s/H) E2. These contributions are second order; the Friedmann equation also contains s squared. Angular averaging removes the initial first-order scalar-density change.

The atomic fractions are forced by geometry through G(f,z) f/H, while gas temperature, baryon density and the external UV prescription are unchanged functions of z. Their leading scalar response is therefore second order about this isotropic anchor. This is consistent with the measured nearly quadratic trend and explains why the old small-Pi range was difficult to resolve. It is not an exact global power law, a proof of equality under A_m sign reversal at all orders, or a detection threshold extrapolated below the smallest tested Pi_m=0.01. The derivation and finite-range checks are recorded in `STRONG_PI_M_PHYSICS_INTERPRETATION.md`.

## 9. Implementation status and the next scientific dependency

The immediate deliverable is a reproducible preliminary isotope/ion atlas, not final production reionization. To reach the latter, the next finite unit should freeze a coupled isotope-native source contract with daughter charge distributions, electron accounting, spectator heat capacity and one thermal energy owner. It should then connect source-backed nonthermal stopping and spectral support before a new production run is admitted. An independent review must distinguish local implementation checks, time/angular convergence and empirical source validation.

The exact nine-variable isotope quotient must not be retained after its equality assumptions fail. A native species operator should use stoichiometric event columns and a common conservation ledger. Every added nuclear pathway needs a provider with domain, units, branching and uncertainty status; an arrow in a diagram is insufficient. Rates at background-independent local conditions can be tabulated once, while spectrum-dependent photo terms retain their actual spectrum dependence.

The next DAG preserves existing FLRW production, Bianchi I science and NCP holds. It does not relabel a dossier update, a restored ZIP, a scoped nuclear pass or a successful plot render as completion of those tasks. All earlier failed attempts and limited-scope admissions remain accessible in the restoration bundle.

## 10. Reading the equations as nuclear-astrophysical processes

This companion explains the equations used in the updated dossier and its plots. It covers the nine groups below, not every formula in the three original source volumes. The distinction throughout is between changing a nucleus, changing its electrons, and changing the time available for either process. A reionization curve can change strongly while the underlying nuclear inventory hardly changes at all.

### 10.1. Abundance, charge fractions and the cosmological clock

`Y_A=n_A/n_B` counts nuclei of species A per baryon. The identity `sum_A A*Y_A=1` weights each nucleus by its baryon number: one helium-4 nucleus contains four baryons, whereas one proton contains one. It is a conservation statement, not a claim that the numbers of different nuclei add to one. `Y_Aq=Y_A*f_Aq` then separates how many nuclei exist from what fraction carries charge q. Changing f can move a population between neutral and ionized states without changing Y_A.

Hydrogen-1 supplies most nuclei and electrons. Deuterium is a rare hydrogen isotope and a nuclear fuel for DD reactions. Helium-4 carries a substantial baryon inventory; helium-3 is much rarer and is a target for neutron-induced tritium production. Lithium-6 and lithium-7 have very small imposed inventories but distinct nuclear creation/destruction routes. Tritium and free neutrons are unstable and start at zero in this experiment. Their new trace inventories should not be confused with the much larger pre-existing stable reservoirs.

The supplied initial abundances are finite-time inputs, motivated by primordial composition; this calculation does not rerun Big Bang nucleosynthesis or solve the primordial lithium problem. Equal electronic operators make H1 and D share a conditional charge history here, likewise the two helium and two lithium isotopes. Their absolute abundances remain different. Newly produced T has no solved charge partition and cannot inherit the hydrogen fractions by assumption.

The coordinate `x=ln(a/a_ref)` obeys `dx/dt=H`, while `1+z` is inversely proportional to a. Therefore `dt/dx=1/H`: at a given state, doubling H halves the proper time available per unit x. At fixed baryon number in the common comoving volume, `n_B` is proportional to `(1+z)^3`; doubling 1+z raises that density by a factor of eight. These relations explain why equal redshift intervals are not equal time intervals. Time axes start at z=20 and measure elapsed Myr, not the age since the Big Bang. Auxiliary axes use the labelled reference trajectory, because different cases have different clocks.

### 10.2. Event counts, stoichiometry and binary collision rates

`R_A=sum_r nu_Ar*R_r` says that every reaction event changes each species by its signed multiplicity. DD producing T+p removes two D nuclei and adds one T and one proton. The corresponding source per baryon is `dY_A/dt=sum_r nu_Ar*R_r/n_B`. Cosmic dilution cancels in this ratio when the baryon current is conserved; it still affects the collision frequency through n_B.

For a binary reaction i+j, the implemented event rate per volume is

`R_ij = n_B^2 * Y_i * Y_j * <sigma v>_ij / (1+delta_ij)`.

Its rate per baryon is `R_ij/n_B`. Doubling density at fixed temperature and fractions quadruples the events per physical volume and doubles the events per baryon. Doubling only one distinct reactant fraction doubles the rate. For DD, doubling the available D fraction quadruples its source. The factor one-half for identical reactants counts each unordered DD pair once; it is not an extra factor applied separately to each product. Stoichiometry then removes two D nuclei per event.

The appropriate reactant fraction depends on the declared model. The first DD audit used the saved ionized-deuterium fraction; the later all-bare conditional network treats the whole retained nuclear reservoir as available. Their difference is a physical availability assumption, not a change in a measured nuclear constant.

`Q_A^a=sum_r integral Delta p_A^a dR_r` uses the same events to count momentum and energy transfer. More events proportionally increase both inventories, but reaction energy is not automatically deposited as gas heat. Recoil nuclei, photons, electrons and escaping neutrinos carry separate shares. The covariant divergence equations encode local particle and energy-momentum balance; their factors of c depend on the declared coordinate convention. They do not permit a second copy of the same reaction energy in a separate heating routine.

### 10.3. Shear, signed stress and expansion

`H^2=K*epsilon/3+Lambda*c^2/3+s^2` relates mean expansion to material/radiation energy, the cosmological constant and shear. At fixed energy density, increasing the shear magnitude increases H through s squared. Its sign does not appear in that single term, but sign still matters in the coupled stress evolution. The shear equation `dot(s)+3Hs=K*(p_m+p_gamma+p_nu)` balances expansion damping against signed anisotropic stress. Without a source, the dimensional shear decreases in proportion to a to the power minus three. With a source, aligned stresses reinforce one another and opposite stresses can cancel temporarily.

`S=sqrt(6)*s/H` measures signed shear relative to expansion; `Sigma=abs(S)` discards its orientation. Similarly, `P_X=sqrt(6)*K*p_X/H^2` compares a dimensional stress with the expansion scale. Holding p_X fixed while doubling H divides P_X by four. This is why fixed raw angular amplitudes need not imply fixed physical initial Pi when another background parameter changes.

Radiation stress is added before taking its magnitude: `Pi_r=abs(P_gamma+P_nu)`. The total magnitude is `abs(P_m+P_r)`, not the sum of magnitudes. Small total stress can hide large opposed contributions. Photons scatter on the computed electrons whereas the retained neutrinos free-stream, so their initial cancellation need not persist.

The matter stress here belongs to a collisionless nonbaryonic component. It does not directly squeeze the atomic gas, heat nuclear reactants or alter nuclear cross sections. Its effect on the retained atomic and nuclear histories is mediated by geometry and elapsed time under the prescribed gas closure.

### 10.4. Photoionization, recombination and electron feedback

The electron closure `n_e=w^T f` counts how many free electrons each populated charge state contributes. The weights contain baryon density, isotope abundance and ionic charge. A doubly ionized helium nucleus contributes two electrons; neutral helium contributes none. Thus increasing ionization can increase the supply of electrons available for recombination elsewhere.

The atomic generator is `G=P+n_e R`, and `df/dx=Gf/H`. P contains one-body photoionization hazards for the imposed radiation field. R contains radiative-recombination coefficients; multiplying by electron density converts them to a hazard per ion. If the external radiation field is unchanged, doubling gas density does not double the photoionization rate per atom. It does double the recombination rate per ion at fixed fractions and temperature. Per physical volume, photoionization is then proportional to density, whereas recombination is proportional to density squared.

For an isotropic photon number spectrum, a photoionization hazard has the form `Gamma=c*integral n_gamma(E)*sigma(E) dE`. Doubling its normalization doubles Gamma if the spectral shape is unchanged. The retained recombination coefficients decrease with temperature across the specified gas-temperature interval; hotter electrons are less readily captured in these coefficients. Temperature and UV amplitude are prescribed functions of redshift, so their simultaneous rise is an input, not a heating history predicted by the solver. Geometry changes the proper-time exposure through the factor one over H, while electron feedback can modify the later response.

The Jacobian term `outer(Rf,w)` is the change in recombination caused by the perturbed electron supply. Omitting it would treat electrons as fixed while varying the charge states that produce them. Column sums of G vanish because ionization and recombination transfer nuclei between charge states rather than destroy those nuclei.

The 5-60 eV source crosses the approximate H I, He I and He II thresholds of 13.6, 24.59 and 54.42 eV. It crosses Li I at 5.392 eV but not Li II at 75.64 eV or Li III at 122.5 eV. Therefore helium can reach its doubly ionized state, whereas initially empty Li III/IV remain empty in this restricted model. This is a spectral-support statement with the selected initial conditions and channels. Adding energetic collisions or harder photons would change it. A very small absolute lithium abundance can nevertheless have a visibly changing conditional fraction.

### 10.5. Charged nuclear reactions and the Gamow window

For the admitted bare charged-particle continuation, `sigma(E)=S0*exp[-sqrt(E_G/E)]/E`. S0 fixes the overall strength; the exponential represents Coulomb tunnelling. Larger nuclear charge product raises E_G and suppresses penetration. A higher relative kinetic energy reduces that barrier penalty, but high energies are rare in a cold Maxwell distribution.

The implemented Maxwell average integrates both penalties:

`<sigma v> = sqrt[8/(pi*mu)]*(k_B*T)^(-3/2) * integral sigma(E)*E*exp[-E/(k_B*T)] dE`.

The reacting particles are drawn from a tail, not simply from the mean thermal energy. With constant S and a well-separated Gamow peak, a saddle-point interpretation gives `E0=[E_G*(k_B*T)^2/4]^(1/3)` and an approximate temperature dependence `T^(-2/3)*exp[-3*(E_G/(4*k_B*T))^(1/3)]`. These last expressions explain the numerical integral; they are not a new rate fit substituted into the implementation. Raising T shifts the preferred reaction energy upward in proportion to T to the power two-thirds and greatly reduces the exponential suppression. In this low-temperature regime that exponential change dominates the decreasing algebraic prefactor. There is no single temperature-independent power law for the rate.

At fixed T, doubling S0 doubles the calculated coefficient and source. At fixed density, changing abundance or ion availability changes the source independently of this coefficient. The 100-10000 K gas remains far colder than a conventional thermonuclear-burning environment, so even positive DD tunnelling gives extraordinarily tiny yields. The positive logarithmically stored source refutes an exact mathematical zero in this conditional model; it does not imply astrophysically important synthesis. Constant S down to these energies is a declared extrapolation without direct empirical validation throughout the range.

### 10.6. Neutron capture, inverse reactions and photon support

Neutrons lack the electric Coulomb barrier of charged projectiles. In the retained low-energy `sigma proportional to 1/v` approximation, multiplying by v gives a nearly constant capture coefficient K0. Slower neutrons have a larger cross section, but they also sweep through targets more slowly; those two effects cancel in sigma*v. A Maxwell average of a strictly constant K remains constant. Consequently temperature has a much weaker role in these adopted neutral coefficients than in the charged Gamow factors, while density and target abundance still control collision rates.

For example, the selected proton-capture anchor is 0.3326 barn times 2200 m/s, giving 7.3172e-26 cubic metres per second. He3(n,p)T has a much larger thermal coefficient, but its tritium source is still limited by the exceedingly small neutron inventory. A large coefficient alone does not guarantee a large yield. Applying thermal anchors to fast DD neutrons requires the explicitly assumed instantaneous thermalization; their actual stopping and transport were not solved.

Detailed balance for a reversible two-body reaction relates reverse and forward coefficients through masses, spin multiplicities, identical-particle factors and `exp[-Q/(k_B*T)]`. For an endothermic inverse with positive forward Q, colder temperatures exponentially reduce the reverse rate. A very negative finite log rate is not an exact zero. The spin factor two-thirds for microscopic n+p/D+photon reciprocity and four-thirds for the leading thermal equilibrium relation describe different incoming ensembles and should not be interchanged.

A photon inverse instead depends on the actual photon distribution above threshold. The imposed 60 eV upper cutoff lies far below the nuclear thresholds, so its external nuclear photodisintegration source is exactly zero under the declared target approximation. A Planck spectrum has no such hard upper cutoff and would give a positive, exponentially small high-energy tail. The original Planck inverse formula is theory for that different radiation ensemble; the present code does not set the photon bath temperature equal to the gas temperature or reprocess its escaping capture photons.

### 10.7. Radioactive survival, cumulative births and rapid balance

The loss law `dY/dt=-lambda*Y` has `lambda=ln(2)/t_half` and survival proportional to `exp(-lambda*t)`. After one half-life half survives; after two, one quarter. This dependence is independent of density for the retained free beta-decay approximation. Tritium's pinned half-life is 12.312 years, vastly shorter than a Myr-scale reionization history. The retained neutron mean lifetime is also short, about 878 seconds.

With production, `dY_T/dt=s_T-lambda_T*Y_T` illustrates the distinction between births and surviving stock. Cumulative births add every newly formed nucleus; they never subtract an earlier birth when that nucleus decays. Surviving stock does subtract decay and other destruction. If the source varies slowly compared with the loss time and decay dominates, `Y_T approximately s_T/lambda_T`. Doubling a slowly varying source doubles this stock. Doubling the half-life approximately doubles it by allowing nuclei to survive longer. This local balance is an interpretation, not an identity at the initial switch-on or during rapid source changes.

The implemented T/neutron calculation includes coupled creation and capture hazards, so its general fast balance is a small coupled system, not always the isolated formula above. Direct positive-stock propagation remains authoritative. Subtracting two nearly equal, much larger cumulative event totals can destroy all digits of the surviving stock. This numerical cancellation has no physical relation to a negative abundance.

The roughly 3.96e-96 cumulative T births per baryon and 1.39e-104 late surviving T inventory therefore answer different questions. Their large ratio is consistent with short-lived nuclei being produced and lost throughout a long epoch. Neither number changes the inherited stable-isotope composition appreciably in this conditional experiment.

### 10.8. Thermal energy, optical depth and observational limits

For a nonrelativistic thermal mixture, `U=(3/2)*k_B*N_particles*T` means that energy is proportional to both particle number and temperature. At fixed particle number, doubling T doubles thermal energy. At fixed available thermal energy, adding particles lowers the temperature that the energy can support. Ionization also consumes binding energy, and new electrons change heat capacity. These relationships motivate one consistent energy ledger rather than separate, duplicated heating estimates.

The present temperature is prescribed. The required-heating and photon-energy plots diagnose what exchange would be needed to maintain that history; they do not demonstrate that the specified radiation self-consistently supplies all of it. Nuclear Q values are available energy per event, not automatically deposited thermal energy. Fast recoil, nonthermal electrons and escaping photons/neutrinos require their own deposition rules.

The homogeneous Thomson diagnostic obeys `d tau/dt=c*sigma_T*n_e`, or `d tau/dx=c*sigma_T*n_e/H`. More free electrons or more time increases scattering depth. At fixed electron history versus x, doubling H halves the depth accumulated over that interval. If the electrons change too, their response must be included. This diagnostic alone is not a fitted observed optical depth or a synthetic sky.

The original polarization condition `Q_Stokes^2+U_Stokes^2+V_Stokes^2<=I^2` states that the polarized part cannot exceed the total intensity for a positive coherency matrix. These Stokes symbols are distinct from reaction energy Q and thermal energy U. No polarized light-cone calculation is performed in this atlas, so a radiation-stress curve must not be read as a polarization measurement.

### 10.9. Positive angular distributions and the near-quadratic stress response

`W(mu)=1+A_m*P2(mu)` is nonnegative only for -1<=A_m<=2. Increasing A_m shifts relative weight toward the symmetry axis without changing its isotropic angular average. At the initial isotropic metric, `pi_s=A_m*pbar/5`, while density and mean pressure are fixed. The original cold family consequently cannot reach arbitrarily large Pi by enlarging A_m: it reaches its positivity ceiling first.

The stronger family changes the nonbaryonic dispersion and fraction, then holds that new family's density and mean pressure fixed while varying its quadrupole. Its zero-stress member is the correct reference. Near that isotropic reference, stress induces shear and directional distortion at first order in A_m. The scalar anisotropic-work term `6*s*pi_s`, the shear contribution s squared, and the radiation monopole source `E0'=-2*(s/H)*E2` are second order because each multiplies two first-order quantities. The massive monopole also has no first-order directional average. Thus H and the retained atomic fractions first change at quadratic order under these particular matched conditions.

The measured maximum fraction shifts at Pi=.01,.05,.1 are close to `5.46e-4*Pi^2`. Doubling a sufficiently small Pi would therefore suggest about four times the leading response within this local interpretation, not a guaranteed law across arbitrary matter models. The observed finite-range values support that interpretation; they do not prove exact sign symmetry or exclude higher-order terms. All three tested nonzero stresses exceed the frozen observed-discrepancy comparison rule, whereas the old cold-family response did not. This modifies the expansion history, not nuclear constants or the prescribed gas temperature.

In the new plots, abundance tick marks represent powers of ten. Signed differences and stresses use symmetric logarithmic axes so that zero and negative values remain visible. The stated linear region is a display choice, not an error bar or a physical detection boundary. Read the numerical controls and model limits alongside the enlarged visual differences.


## References and reproducibility

1. User's October 14 attached standalone dossier, *Reionization: Microphysics, Transport and Observation* (73 PDF pages); *Reionization and Nonthermal Matter* (33 pages); and *Nuclear Capture and Photodisintegration: Thresholds, reciprocity and thermal ensembles* (7 pages). Source identities and chapter relationships: `ATTACHED_DOSSIER_RECONCILIATION.json`; prior backup mapping: `DOSSIER_SOURCE_INTAKE.json`. Original source bytes are not republished.
2. Verner and Ferland (1996), radiative recombination rates, DOI: 10.1086/192284. Author data page: https://www.pa.uky.edu/~verner/rec.html . See the pinned atomic provider records for the rows and units actually used.
3. Xu et al. (2013), NACRE II, DOI: 10.1016/j.nuclphysa.2013.09.007, https://arxiv.org/abs/1310.7099 . Tabulated high-temperature applicability must not be confused with the explicit low-temperature constant-S extrapolation here.
4. NIST neutron scattering/absorption table: https://ncnr.nist.gov/resources/n-lengths/list.html . The stated dominant-branch approximation for Li6 is retained.
5. JENDL-5 He3 evaluated table: https://wwwndc.jaea.go.jp/jendl/j5/elm/Table/z002/T3.html . Radiative capture and (n,p) channels are distinct entries.
6. LNHB tritium evaluation: https://www.lnhb.fr/nuclides/H-3_tables.pdf ; IAEA recommended decay data: https://nds.iaea.org/sgnucdat/d1.htm . Evaluated half-life and year convention are pinned in `EVALUATED_DECAY_INPUTS.json`.
7. PDG neutron listing: https://pdg.lbl.gov/2025/listings/rpp2025-list-n.pdf . The selected lifetime is recorded separately from an uncertainty analysis.
8. Viviani et al. (2023), DD reaction discussion, DOI: 10.1088/1742-6596/2586/1/012076. The distinct p+T radiative-capture input is Dubovichenko et al., DOI: 10.1142/S0218301319300042, https://arxiv.org/abs/1811.04779 ; its selected model and E1 multipole limitation remain explicit.
9. Repository evidence: `../rei_isotope_quotient_pilot_20261022/`, `../rei_tritium_production_audit_20261022/`, their frozen contracts, canonical NPZ histories, reviews and delivery receipts. Nuclear payload commit e3563ae9d562bca0537cf2c2d3fca8426413b9f6; completed delivery metadata commit 79244fe24f444ed441ddc24e7518adc8a0aa45f0. The new dossier's publication commit is recorded in its delivery receipt.

The manifest and receipts, rather than mutable branch prose, identify the exact evidence used. The HTML gallery supplies directly viewable PNGs and downloadable vector PDFs. The compiled dossier includes the full figure appendix. No newly created T ionic partition, empirical abundance constraint or full production admission is implied by those artifacts.
