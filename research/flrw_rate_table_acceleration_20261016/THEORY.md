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
