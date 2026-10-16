# Temperature coefficient acceleration

## Active scope override before R6

The user's latest instruction is: “선행 PR을 확인하면 우선 scope는 Li와 그 이온까지만 포함해.” The follow-up “(Li isotope 포함)” explicitly includes lithium isotopes. Added-species work is therefore restricted to 6Li and 7Li, each Li I–Li IV, after checking the preceding PR and source authority. This supersedes the root's earlier carbon selection. Existing H/He/D optimization and all generic interpolation, closure, cache, and cost derivations remain in scope. The immutable R1–R5 carbon exploration is retained as historical evidence; carbon is excluded from active production exports and added-species admission. The execution budget is unchanged. The active lithium source/domain/isotope mapping is appended at R6; no generic derivation or existing-provider validation is restarted.

## R1 — research contract

This unit constructs reusable temperature-only coefficient evaluation, measures scalar and batch costs, and admits an additional species coefficient only after checking its actual primary provider. The baseline is `4583ed342b8476e86e42b023d6de1d0f50820adb`; the repository policy blob is `429a5a13ee75b1222bc50627f8d5973d01dd21c4`. `CONTRACT.json` records quantitative acceptance and bounded local execution. Existing external native runs and their checkpoints remain under their existing contracts.

The stored object is a gas-rest-frame coefficient k(T), with each channel's original units and provenance. Proper densities, radiation spectrum, expansion rate, abundances, and thermal closure remain inputs to their existing consumers. This separates reusable atomic computation from evolving background state while keeping the same physical equation.

Completion requires a derived interpolation/error contract, primary-source species decision, implemented opt-in evaluator, independent numerical comparisons, measured construction/query costs, and independent scientific review. The direct provider remains the reference and fallback. Local coefficient and point-RHS evidence establishes that scope; cosmological trajectory accuracy requires its own matched trajectory evidence.

R1 outcome: the next dependency is the exact source/provider and branch map, followed by interpolation derivation. No new no-go claim is proposed.

## R2 — source and reusable evidence

The existing `rust/rei_microphysics/src/igm_rates.rs` evaluates the selected Grackle 3.4.1 Case-A implementation at source commit `af7939494ce65007887ada7b98d1813df6843346`. Its operational domain is 1–10^6 K. This domain describes the existing numerical model; source empirical accuracy remains the provider's separate claim. Its sixteen stored scalars are CI[3], RR[3], DR, CE[3], RR cooling[3], DR cooling, raw DR cooling, and free-free. The CE metastable HeI channel has erg cm^6 s^-1 units; the other listed cooling channels have erg cm^3 s^-1. Its density factor is n_e^2 n_HeII, so treating every channel as binary would change the physical model.

`igm_thermal.rs::igm_point_rhs` computes temperature from the ideal-gas state and calls this bundle. `axbi_rates.rs::AxbiProvider::point` separately evaluates the same bundle again for its returned diagnostic object. A prepared-rate adapter can remove this duplicate evaluation without approximating a coefficient. `deuterium_atomic.rs::DAtomicProvider::rates` selects four H channels and converts cm^3/s to m^3/s by 10^-6 and erg cm^3/s to J m^3/s by 10^-13; its explicit H-equality D approximation retains its present status.

The piecewise-source map includes T=5500 K; T=0.8×11605=9284 K; CE exponent caps at 118348/ln(10^30), 13179/ln(10^30), 473638/ln(10^30) K; raw DR-cooling caps at 470000/ln(10^30), 94000/ln(10^30) K; and the CI-H floor-selection boundary. Crossing cells use direct evaluation. Low-branch DR reaction and selected DR cooling are identically zero, so these channels may return exact zero without logging zero. Diagnostics encode exact source predicates, not interpolated boolean masks.

Savin2002's D/H exchange coefficient pair in `deuterium_charge_exchange.rs` is temperature-only with 2.7–2×10^5 K guard and m^3/s units. Its existing thermal-CX construction and verified implementation at `research/flrw_thermal_charge_exchange_20261016` are reusable background evidence. This unit does not repeat that derivation or silently import its standalone implementation into the Rust solver. `he_rct.rs` supplies no new source-admitted species extension; its existing source conflict remains visible.

The additional provider candidate is the full elemental carbon charge chain C^0…C^6+: six Voronov electron-impact ionization coefficients and ground-parent Badnell RR/DR coefficients. Primary table extraction and per-stage validity mapping are being performed independently by `rate_sources`; adoption waits for those exact bytes and formulas. Isotope-specific accuracy does not follow from elemental charge-stage data.

R2 outcome: the existing temperature coefficient and branch map is established by source inspection; exact new-provider data is a tracked dependency for R5/R9. Remote active driver differs from the local historical driver, so the driver is outside allowed edits. Fresh stage publications use the current remote parent while preserving the frozen source baseline.

## R3 — claims, assumptions, and admission scope

For a source coefficient k, set x=ln(T/T_*), y(x)=ln(k(T)/k_*), where fixed positive references make the logarithms dimensionless. Changing the fixed references changes no interpolation slope or reconstructed coefficient. On each eligible cell [x_i,x_(i+1)], assume k>0, normal finite binary64 endpoint values, no source-branch boundary, and y twice continuously differentiable. Piecewise source rules and structural zero regions are handled separately.

The construction claims are: (A) log-linear interpolation preserves positivity; (B) a supplied bound M_i≥sup|y''| yields relative error at most exp(M_i h_i²/8)-1 in exact arithmetic; (C) its derivative is k_hat s_i/T inside a cell, s_i=(y_(i+1)-y_i)/h_i; (D) inserting the same coefficient in forward event fluxes and stoichiometric updates preserves reaction conservation identities. A measured off-grid maximum tests selected temperatures and is recorded as numerical evidence, without converting the sampled maximum into a continuous supremum proof.

The empirical target is relative coefficient error ≤10^-5, with direct evaluation for structural branch-crossing or numerically unsuitable cells. If a derivative API is provided, its target is |s_table-s_reference|/max(1,|s_reference|)≤10^-3 on smooth interiors. The current implementation may omit derivatives: callers then retain direct-provider Jacobians or differentiate the selected evaluator by an explicitly supported method. A direct analytic derivative paired with a table residual is not an exact Jacobian of that residual and must be labeled as an approximate Newton matrix.

For F_r=k_r(T) product_j n_j^(ν_jr), the same nonnegative density prefactor gives |F_hat_r-F_r|≤ε F_r. For a signed net source S_a=sum_r N_ar F_r, the correct bound is |S_hat_a-S_a|≤ε sum_r |N_ar|F_r. Cancellation can make relative error in S_a arbitrarily large even while each event flux is accurate. Therefore point-RHS comparisons use event-scale absolute normalization, and a coefficient tolerance alone is not a trajectory tolerance.

The elemental carbon extension can supply a charge-stage number RHS with prescribed electron density once its coefficients are admitted. Thermal closure requires channel-resolved energy data; ionization thresholds alone do not determine the kinetic energy of recombining electrons or all emitted photons. Source fit/domain uncertainty and table interpolation error are separate quantities.

R3 outcome: positivity, interpolation error, event conservation, sampled accuracy, and speed are separate claims with explicit assumptions. The unresolved new-provider data affects carbon adoption only; it does not block the existing H/He table derivation.

## R4 — representation choice and discriminating experiment

The selected representation uses a uniform grid in x=ln T, initially 8193 nodes across the H/He operational domain and at most 65537 if a concrete accuracy failure requires refinement. Positive normal channels store log coefficients in structure-of-arrays form. Fifteen independent H/He channels are sufficient because selected DR cooling is exactly either zero or the raw DR-cooling channel. This reduces storage and preserves that source relation algebraically. A structural-zero mask certifies a source-defined zero interval; equal zero endpoints alone cannot certify that an interior rate vanishes.

Uniform spacing gives one logarithm, one affine index calculation, and one shared interpolation coordinate per temperature for all channels. It avoids a per-channel binary search. The batch layout puts each channel in contiguous storage and permits an implementation to loop over temperatures while reusing grid coordinates; this is a vectorization opportunity whose actual machine-vector execution requires compiler or disassembly evidence. Independent temperature queries can be chunked between at most four workers without shared mutable coefficient state.

Three alternatives remain measurable: direct analytic evaluation; prepared direct evaluation reused within one point call; and the immutable interpolation table. Constants use direct stored values because a table adds work. A cheap single analytic channel may cost less than index/log/exp and memory traffic; the sixteen-channel bundle has a different break-even. Full direct fallback of a branch-crossing cell keeps source semantics simple at a small localized lookup cost.

The R7 experiment evaluates source/table disagreement at deterministic off-grid temperatures, nonuniform fixed-seed temperatures, each grid knot and its floating neighbors, source branch neighbors, invalid inputs, and domain endpoints. It reports errors by channel, exact structural-zero and diagnostic-mask agreement, and construction plus repeated-query costs. C-stage benchmarks compare identical temperature arrays through scalar, batch, and bounded-thread APIs, with output checksums and repeated samples. The active cosmological binary is outside this experiment.

Root selected the concrete scope: H/He prepared evaluation and opt-in table; D prepared reuse; elemental carbon Voronov CI plus Badnell ground-parent RR/DR, with row-specific domain handling and an actual table-backed provider. Individual low-temperature recombination rows remain callable within their domains; a complete chain call requires the intersection of all needed rows. Isotope-native 12C and 13C are an explicit unresolved source dependency. Numeric source rows are retained with attribution and source licensing status; provider source code and whole papers are not copied.

The scientific execution allowance is aggregate 90 s wall, 180 s CPU, 2 GiB RAM, and four workers for this new local unit; build/toolchain commands are separately bounded at 120 s each and recorded. No derivative API is added and no Newton path is switched to the table, so derivative admission remains an explicit future interface obligation rather than an untested implicit feature.

R4 outcome: log-linear shared-grid interpolation, exact branch fallback, and exact prepared reuse are selected for implementation. The discriminating experiment can admit accuracy and identify which query sizes actually benefit.

## R5 — constructive derivation

### Positive interpolation and its error

Let h=x_(i+1)-x_i>0 and θ=(x-x_i)/h. Linear interpolation of y gives y_hat=(1-θ)y_i+θ y_(i+1), hence

    k_hat = k_i^(1-θ) k_(i+1)^θ = k_* exp(y_hat) > 0.

For y in C² on the closed cell, the interpolation remainder is y(x)-y_hat(x)=y''(ξ)(x-x_i)(x-x_(i+1))/2 for some interior ξ. Since |(x-x_i)(x-x_(i+1))|≤h²/4, |y-y_hat|≤M h²/8. Therefore exp(-δ)≤k_hat/k≤exp(δ), δ=M h²/8, and |k_hat/k-1|≤expm1(δ). A sufficient exact-arithmetic mesh condition for relative target ε is h≤sqrt(8 ln(1+ε)/M). Rounding adds the logarithmic error from endpoint log, affine interpolation, and exp; it must fit inside the total tolerance margin. The sampled validation includes these operations.

As a small exact case, k=A T^p gives y affine, y''=0, and log-linear interpolation recovers the analytic power law in exact arithmetic on every grid. For k=A T^p exp(-B/T), y'=p+B/T and y''=-B/T. On [T_i,T_(i+1)], M=B/T_i; a grid adequate at high temperature can fail at low temperature. This provides a concrete curvature mechanism and motivates per-cell checking/fallback instead of assuming a universal table resolution.

Differentiating the actual interpolant gives d k_hat/dT=k_hat s_i/T. Since s_i is the cell average of y', |s_i-y'(x)|≤M h/2 for any cell point (integrate M|u-x|/h over the cell and maximize at an endpoint). Thus |T(k_hat'-k')|/k≤exp(δ) M h/2+expm1(δ)|y'|. Coefficient error is second order in h whereas slope error is first order. At an interior knot the left and right slopes need not agree; source discontinuities may have no derivative. Any future Jacobian interface must define these cases and differentiate the actual fallback choice. This unit exports coefficients without a derivative API and changes no Newton evaluator.

### Zero, sign, branch, and domain handling

Exact zero is a source property only when a source predicate certifies the whole interval. The low-branch IGM DR channels and bare-carbon DR are such cases. A binary64 zero caused by exp underflow is numerical and must retain that distinction. Positive subnormal values, underflow-transition cells, negative values, and unresolved sign-changing cells use direct evaluation; never replace them with an invented positive floor. Generic signed observables can be represented on fixed-sign cells by sign×exp(interpolated ln|k|), but all admitted physical rate totals in this unit must be nonnegative. A signed fit coefficient inside a positive sum is not a signed physical channel.

Branch crossing is tested using the source predicates, including `T/11605.0 <= 0.8`, not merely the decimal value 9284. A grid cell intersecting a branch or cap boundary is direct. The CI floor mask and all diagnostic booleans follow the exact source semantics. Cell endpoints and each branch's floating neighbors are checked because rounding can move an apparent algebraic boundary by an ulp. Outside a table's range but inside a provider's valid range, the provider evaluates directly; outside the provider domain, its typed error is retained. Invalid T is never clamped to an endpoint.

### Rate coefficients, closures, and prepared state

For binary event r, F_r=k_r(T)n_a n_b has units volume^-1 time^-1. Three-body or metastable effective channels retain their stated higher density power. In the number RHS dot(n)=N F, any conserved row vector ℓ satisfying ℓᵀN=0 obeys ℓᵀdot(n)=0 for direct and table coefficients because the same event flux multiplies the same stoichiometric column. This algebraic identity does not require k_hat=k. A process's forward/reverse detailed-balance ratio, if part of its physical contract, needs a paired representation or a bound on that ratio; independent interpolation alone only guarantees a ratio error ≤exp(δ_forward+δ_reverse)-1.

Photoionization Γ=∫4πJ_ν σ(ν)/(hν)dν depends on J_ν. Photoheating includes the additional excess-energy factor, and Compton exchange depends on radiation temperature and electron density. Neither is a reusable T-only coefficient unless those external inputs are explicitly frozen and included in identity. The table contains neither these radiation functionals nor density products. It also contains no expansion-rate factor.

A prepared direct rate bundle is valid for its exact T and provider identity. If T is recovered from u=(3/2)k_B T n_tot, then dT/du=T/u and dT/dn_j=-(T/n_tot)∂n_tot/∂n_j at fixed u. Composition changes can therefore change T inside a nonlinear iteration even when u is fixed. Prepared values must be reconstructed whenever that exact T changes. They may be reused for the duplicated evaluation at one already evaluated state, yielding an exact arithmetic-path optimization. A prepared object with private temperature/rate fields and a consumer temperature-identity check prevents accidental reuse at another state without introducing a global mutable cache.

### Carbon source construction

The selected numeric rows are `data/carbon_coefficients.json`. Voronov uses U=E_ion/(k_B^source T), k_B^source=8.617385×10^-5 eV/K, and

    C_q(T)=A (1+P sqrt(U))/(X+U) U^K exp(-U)  [cm³/s].

For q=0…5, the source lower electron temperatures are [1,1,2,3,20,20] eV and the upper temperature is 20 keV. This source conversion constant is identity-bearing; replacing it silently with a newer CODATA value changes reproduction. Its logarithmic slope is s_C=U-K+U/(X+U)-P sqrt(U)/(2(1+P sqrt(U))).

Badnell RR uses a=sqrt(T/T0), d=sqrt(T/T1), b=B+C exp(-T2/T), and

    α_RR(T)=A/[a(1+a)^(1-b)(1+d)^(1+b)]  [cm³/s].

Its logarithmic slope is -1/2-(1-b)a/[2(1+a)]-(1+b)d/[2(1+d)]+b_x ln[(1+a)/(1+d)], with b_x=C exp(-T2/T) T2/T. Badnell DR uses

    α_DR(T)=T^(-3/2) sum_j c_j exp(-E_j/T),

where E_j is in K and c_j in cm³ s^-1 K^(3/2). Its slope is -3/2+[sum_j c_j exp(-E_j/T)(E_j/T)]/[sum_j c_j exp(-E_j/T)]. The standard source tabulation range is 10 q²≤T/K≤10^7 q² for initial target charge q=1…6; this is labeled as a tabulation interval rather than a newly proved accuracy bound. DR for bare q=6 is structurally zero.

The q=4 DR row has one negative fit amplitude. Its two relevant terms obey

    0.002646 exp(-2804000/T) - 0.0007843 exp(-4324000/T)
    > (0.002646-0.0007843) exp(-2804000/T) > 0

for every finite T>0, and the remaining amplitude 0.01762 is positive. Thus the total analytic DR is positive despite a negative fitted term. Keep that negative amplitude exactly; clipping it would change the source. The other selected rows have nonnegative amplitudes. At cold temperatures a total may still underflow in binary64, requiring direct evaluation/underflow semantics.

For carbon populations n_0…n_6 and externally specified n_e≥0, define I_q=n_e n_q C_q for q=0…5 and R_q=n_e n_q(α_RR,q+α_DR,q) for q=1…6. Set absent boundary fluxes to zero. Then dot(n_q)=I_(q-1)+R_(q+1)-I_q-R_q, so summing telescopes to zero, and sum_q q dot(n_q)=sum I_q-sum R_q. If electrons are evolved, dot(n_e)=sum I_q-sum R_q conserves total electric charge e(sum q n_q-n_e). With external n_e the output records this electron source rather than asserting a closed electron evolution.

Single-channel APIs retain their own cold/hot domain. The complete chain is defined on [20/k_B^source,10^7] K, the actual intersection of needed CI/RR/DR domains. It is ground-parent, low-density Maxwellian elemental carbon. There are no isotope-native 12C/13C rows; those requests receive explicit unsupported status. The source numerical rows have attribution and retained retrieval identity; source licensing is reported as unspecified where the provider does not state a license. No carbon thermal or photon ledger is introduced.

### Cache identity and cost

An immutable table identity includes source provider/version and numeric-row digest, process/charge/parent, recombination case and physical mode, source constants and units, operational domain, precision, interpolation/grid specification, zero/branch/fallback policy, and approximation tolerance. A mutable provider revision or precision change requires reconstruction. Background parameters absent from k(T) are absent from its key; any actually used density/radiation parameter belongs in the key of a different object. The private prepared bundle additionally carries exact temperature.

Let B be table construction time, c_d direct time per query, and c_l lookup time per query for the same bundle. A repeated-query table pays off at N>B/(c_d-c_l) only if c_d>c_l. When c_l≥c_d there is no positive crossover for that measured workload; this is a cost result, not a general impossibility claim. If rate evaluation occupies fraction f of total runtime and achieves speedup s, Amdahl gives S_total=1/(1-f+f/s). No f measurement is available from the active external run, so its end-to-end speedup is not inferred from a local rate benchmark.

For m independent temperature queries with scalar-batch per-item cost c, p workers, startup L, and extra per-item scheduling/copy cost b, T_parallel≈L+mc/p+mb. Parallelism beats the serial batch only when c(1-1/p)>b and m>L/[c(1-1/p)-b]. Small batches may correctly remain serial. Outputs retain input ordering, and workers share immutable grid rows. Benchmark results must state threads, query distribution, construction inclusion, and actual break-even rather than assume that more threads or a SoA layout produces speedup.

R5 outcome: the interpolation/error proof, branch construction, conservation mapping, carbon formulas and positivity, cache identity, and amortization equations are complete. R6 reviews these transitions independently; R7 measures the implementation-dependent accuracy and cost.

## R6 — lithium and isotope delta under independent review

The generic R5 interpolation/slope proof, closure separation, cache construction, and amortization were independently reviewed by `rate_frontier` as mathematically sound under their stated hypotheses. Its initial carbon-source comparison is retained as historical exploration. Active added-species admission uses lithium only.

Preceding PR151 at head `9f455d98` has `inventory17.json` blob `69354d1065` with Li7; its Li6 abundance entry 6.035916255350921×10^-15 was omitted with no charge mapping. The existing native thirteen-species state has no Li. The prior `ISOTOPE_PROVIDER_THEORY.md` blob `7d83af0666` explicitly distinguishes elemental Verner Z,N data from isotope A and provides a declared element-equality precedent for 3He. These observations establish that the current request adds 6Li and 7Li charge stages rather than inheriting a completed isotope-native Li implementation. The old trace-inventory omission does not restrict the user's new explicit Li6 scope. No default abundance or automatic network activation is adopted from that inventory.

The actual selected source rows are `data/lithium_coefficients.json`: Z=3, ground-parent M=1, CI q=0,1,2; RR q=1,2,3; DR q=1,2; structurally zero DR q=3. They use the same verified Voronov and Badnell formulas and units from R5, with lithium numeric rows. CI lower k_B T values are [1,4,5] eV and the upper value is 20 keV. RR/DR per-channel domains are [10q²,10^7q²] K; the complete CI/RR/DR chain intersects on [5/(8.617385×10^-5),10^7] K. Independent RR remains available as cold as 10 K for q=1. The standard-tabulation interpretation and low-density Maxwellian/ground-parent assumptions remain explicit.

The Li+ DR row has the signed amplitudes [2.941×10^-5,6.068×10^-5,-7.753×10^-7] and energies [634500,702400,827100] K. For every T>0,

    2.941e-5 exp(-634500/T) - 7.753e-7 exp(-827100/T)
    > (2.941e-5-7.753e-7) exp(-634500/T) > 0.

The remaining amplitude is positive, so the analytic total is positive. The negative amplitude is preserved. Cold binary64 underflow retains its numerical meaning and direct fallback; it is not a new structural-zero channel.

Root explicitly adopted the opt-in isotope model `IsotopeRatePolicy::ElementalElectronicEquality`: for A∈{6,7}, set k_(A,q,p)(T)=k_(Li,q,p)(T) for each process p while retaining separate species identity (Z,A,q). The policy is a required constructor argument, with no implicit default. This is a declared shared-electronic coefficient approximation, not an isotope-native source or a reduced-mass scaling prescription. The source table carries no mass-number dependence, and no bound on neglected isotope shifts, mass effects, or hyperfine/population effects is asserted. An isotope-native/IsotopeResolved policy request must return typed missing-source status until such a provider exists. This model decision follows the preceding declared 3He element-equality precedent and is distinct from source-row evidence.

Under that model, keep n_(A,q), q=0…3, separately for both A. Define I_(A,q)=n_e n_(A,q) C_q and R_(A,q)=n_e n_(A,q)(α_RR,q+α_DR,q), with boundary fluxes zero. Then

    dot(n_(A,q)) = I_(A,q-1)+R_(A,q+1)-I_(A,q)-R_(A,q),
    sum_q dot(n_(A,q)) = 0  for each A,
    electron_source = sum_(A,q) I_(A,q) - sum_(A,q) R_(A,q).

The charge identity is sum_(A,q) q dot(n_(A,q))=electron_source. Thus the source conserves nuclei independently for Li6 and Li7 and changes neither label; weighting those two identities by A=6,7 also proves conservation of their baryon count. For the same T,n_e and proportional initial charge populations n_(7,q)=c n_(6,q), both isotope derivatives have that same proportionality; this is a useful implementation check of the selected approximation. Electron density is an explicit external input, with its source returned for optional correct coupling. No isotope masses, binding-energy defect, nuclear reactions, thermal or radiation ledger are invented. The prior Li8/Li9 omitted reservoirs remain explicitly pending nuclear-decay and daughter-product closure; they are neither aliased into Li7 nor represented as stable in this bounded Li6/Li7 collisional component.

The coefficient table may share elemental rows between A=6 and A=7 only under this named policy, while outputs and cache identity retain the policy and isotope labels. The conditional approximation and native-source status must remain visible at construction and in returned provider metadata.

Primary isotope spectroscopy found by the source owner provides a concrete limitation: Bushaw et al., Physical Review A 75, 052503 (2007), DOI 10.1103/PhysRevA.75.052503, reports a neutral Li7–Li6 ionization-threshold shift of 18067.54(21) MHz. This confirms a real isotope dependence. It does not determine the isotope shifts of all electron-ion rates or DR resonances, so it supplies neither a full correction nor a rigorous error bound for `ElementalElectronicEquality`. The active implementation does not apply a threshold patch from this datum.

R6 outcome: `evidence/R6_INDEPENDENT_REVIEW.json` records `PASS_SCOPED_LI6_LI7_CONDITIONAL_COEFFICIENT_IMPLEMENTATION`, with no blocking findings, independent inspection of all ten selected Li source lines, and reuse of the unchanged generic mathematical review. Its positive transition is bounded implementation and targeted tests; C9 will review the actual changed implementation and observed results. The source/domain and conditional-isotope-model obligations are now resolved at the design level. Numerical accuracy of the Li implementation and integrated adapters remains for C6–C8.

## R7 — actual discriminating computation

The lower-tier code owner compiled a standalone Rust prototype that includes the unchanged production `igm_rates.rs` as its direct source reference and the new generic/table implementation. Rust 1.94.1 failed at tool startup with SIGBUS; the separately recorded Rust 1.85.1 toolchain executed successfully. This is an environment repair, not a change in source coefficients or scientific tolerance. `evidence/R7_RESULTS.json`, per-run stdout/resources, and `evidence/RUN_LEDGER.json` preserve commands and outputs.

The initial 8193-node table completed execution with exit code zero but failed the fixed numerical target: 77,367 temperature queries gave maximum relative coefficient error 2.453727547795756×10^-5 versus the required 10^-5. Zero, diagnostic-mask, and invalid-input mismatches were all zero. The largest errors occurred in the steep exponential cooling channels near cap regions, consistent with the curvature mechanism in R5. The failure is classified as numerical resolution, with its original raw record retained.

Root authorized the already allowed 65537-node refinement without changing tolerance or physical assumptions. The refined run tested 421,431 queries across all sixteen output fields, including deterministic log off-grid and fixed-seed nonuniform samples, refined grid knots and floating neighbors, cell-quarter probes, explicit branch neighbors, endpoints and invalid inputs. Its maximum relative error was 3.8387697880837957×10^-7, with zero mask/zero/invalid mismatches and eight direct-fallback cells. Fixed off-grid controls were retained between resolutions. The exact CI floor-crossing bracket will receive a targeted C6 predicate-neighbor check; the R7 grid/fallback coverage is not represented as that unperformed exact-boundary test.

Two independently interpretable construction controls also ran: a power law had relative error 3.1086244689504383×10^-15; a curved exponential example had error 0.0018986301621563006 below its analytic bound 0.0020245602827097826. These verify the chosen examples and the implemented interpolation formula. The H/He sample maximum is empirical, not a certified continuous curvature supremum.

The refined generic grid payload was 8,913,016 bytes, took 0.109192622 s to construct, and the complete refined probe consumed 0.365005623 s wall and 0.333695 s CPU with peak RSS 18,244 KiB. The IGM floor masks add 196,608 bytes, so the full coefficient/mask payload is 9,109,624 bytes; the initial probe's `storage_bytes` reports the generic grid only. Initial plus refined scientific execution totals were 0.429108927 s wall and 0.390437 s CPU. Construction and probe costs are recorded separately; no direct-versus-table speedup is inferred from these accuracy runs. Scalar/batch/parallel comparative benchmarks and Li-specific execution remain C-stage obligations under the unchanged aggregate budget.

R7 outcome: actual compiled H/He prototype accuracy passes the frozen coefficient target on the stated sample after one diagnosed refinement. No derivative API, new Newton/table residual path, continuous error certificate, or trajectory claim is admitted by this result.

## R8 — scoped result decision

Adopt the 65537-node H/He table as the opt-in implementation candidate supported by R7 sampled coefficient accuracy. Preserve direct evaluation as default/reference/fallback and the 8193-node failed target result. The factor-eight grid refinement reduced the observed worst error by approximately a factor of 64, consistent with the smooth log-linear second-order coefficient estimate; this observed comparison does not replace the cellwise curvature hypothesis.

Adopt exact prepared direct-rate reuse within a point evaluation and its D projection for implementation: it removes duplicate source work without changing coefficients. Its actual integrated point outputs and temperature-identity enforcement must pass C6–C7. Adopt the source-backed Li6/Li7 state-and-number-rate component under required `ElementalElectronicEquality`, retaining per-channel domains and typed missing-source behavior for native isotope coefficients. Source and model acceptance at R6 does not substitute for the forthcoming Li numerical tests.

Performance remains an empirical comparison to be completed in C8: the table's construction cost and memory are already known, but a speedup decision requires direct/prepared/lookup/batch/parallel timing on identical inputs. No full-driver timing fraction or trajectory result is available. The new table remains opt-in so its observed workload economics can guide use.

No strong no-go result is proposed or admitted. The missing isotope-native dataset, unsupported Li8/Li9 nuclear closure, and a failed coarse mesh are specific source/model/numerical obligations with constructive next actions, not impossibility theorems. NG1–NG7 therefore have no new exclusion claim to evaluate. The watchdog requirement is met by the actual compiled R7 calculation and the executable C-stage handoff; further unchanged-source audits are unnecessary.

R8 outcome: approve bounded production implementation and scientific tests of the selected candidates, keeping accuracy, source fit scope, isotope approximation, and performance as distinct claims. The original tolerance and aggregate execution budget remain fixed.

## R9 — formal implementation handoff

The active computational statement is: source-faithful direct coefficients and an explicitly selected positive log-linear approximation provide temperature-only H/He and conditional Li6/Li7 event coefficients within the stated provider domains; live state/radiation factors remain in their consumers. H/He R7 sampled error is below 10^-5 after selection of 65537 nodes. Li isotope identity and conservation are exact properties of the selected number-state model, while its shared electronic coefficient equality is an explicit approximation with unquantified isotope-model error.

The code handoff is:

| Component | Input and output contract | Required verification |
|---|---|---|
| `LogRateGrid<N>` | Immutable uniform-log grid, positive logs and source-certified structural zeros; direct callback for blocked/outside-table cells | Power law, curved bound example, degenerate grid guard, domain/zero/sign/underflow behavior |
| `IgmRateTable` | 65537-node default, fifteen independent stored fields, sixteen reconstructed output fields and exact diagnostic predicates | Reuse R7 valid-input evidence; targeted actual CI floor predicate neighbors; scalar/SoA/parallel equivalence |
| `IgmRateBackend` and `PreparedIgmRates` | Default Direct or explicit table; private exact-temperature binding and evaluator identity | Mismatched prepared temperature rejects; direct prepared values reproduce original source |
| H/He point and D reuse | Reuse one prepared bundle at the same EOS temperature; retain original density and energy factors and SI/cgs conversions | Original point/RHS and D projection agreement; table event-scale error ≤10^-5; unchanged direct default |
| Li elemental provider | Actual Voronov/Badnell selected rows, exact source constants, per-process/per-charge domains | Independently substituted primary-row checkpoints; boundary neighbors and signed-DR total positivity |
| Li6/Li7 wrapper | Required `ElementalElectronicEquality`, separate A/q metadata; isotope-resolved request returns MissingSource | Separate nuclei, baryon-weighted count, charge/electron source, proportionality, zero density; Li8/Li9 pending status |
| Li table backend | Same source coefficients on the complete-chain common domain; individual cold RR calls remain direct and available | Per-channel sampled relative error ≤10^-5; typed errors and exact structural zeros |

For a conservation residual, normalize by the sum of magnitudes of contributing event terms, not a cancellation-prone net source; a floating-arithmetic target of 64 ε_machine times that scale is appropriate for this small fixed chain. Zero-event cases must be exactly zero. For point-RHS approximation use the R3 absolute event-scale bound. Preserve any stricter existing source test rather than relax it to the table tolerance. No new Jacobian or derivative API is in this handoff.

Timing compares identical independent-temperature arrays after output agreement checks. Report repeated direct, prepared, scalar lookup, SoA batch, and bounded parallel measurements; include construction amortization, full payload 9,109,624 bytes for H/He, and measured RSS separately. Read-only shared tables and sufficiently large chunks reduce duplication. Worker count is selected from measured crossover, with at most four workers in this unit. No SIMD assertion follows merely from the data layout, and no memory-filling goal justifies replicating tables on a large host.

The bounded changed-module harness is valid for module-level scientific/API checks if unrelated full-crate toolchain features are unavailable; its exact included production files must be recorded. Such a harness does not establish a full-crate build or complete driver integration. The independent C9 review must inspect actual production diffs, source rows, raw numerical outputs, and the scope of that harness before admission.

After this unit, the constructive dependency path is: retain the explicit Li6/Li7 charge-state identities → bind a separately sourced Li photo functional to the existing radiation owner → add channel-consistent thermal and emitted-energy moments → reconcile caller-supplied BBN inventory and native state integration → execute matched trajectory/error-budget tests. Li8/Li9 require nuclear-decay and daughter-product accounting before joining that path. These are later scientific dependencies, not new work authorized inside this coefficient unit. The currently running external binary and checkpoints remain unchanged.

R9 outcome: formulas, units, source identity, acceptance criteria, executable module contracts, and remaining full-network dependencies are handed to the code owners. The lower-tier owners perform C1–C10 and return actual evidence for independent C9.
