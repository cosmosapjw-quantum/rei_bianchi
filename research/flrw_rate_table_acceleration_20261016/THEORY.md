# Temperature coefficient acceleration

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
