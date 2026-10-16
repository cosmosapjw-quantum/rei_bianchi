# Temperature-rate acceleration intake

Frozen REI base: `4583ed342b8476e86e42b023d6de1d0f50820adb`, branch `research/flrw-production-integration-20261015`. Read-only intake on 2026-10-16; no science execution, tests, production change, or external-process control. Exact GitHub source/blob pins and delta PR identities are in FRONTIER.json.

## Concrete source finding

The actual Newton residual calls `PreparedAbsorption::evaluate_for_cell_count`, then `AxbiProvider::point`. The latter calls `igm_point_rhs`, which evaluates the full `igm_rates(T)` bundle, then evaluates that same full bundle again via `self.rates(T)`. This is duplicate formula work established from source, not a measured bottleneck or speedup. `DAtomicProvider::rates` also evaluates the whole bundle just to select H CI, RR, RR kinetic cooling, CE and their diagnostics for its existing conditional D=H model.

An immutable prepared bundle can therefore be reused within the H/He point call and by D projections. An opt-in table can approximate only the temperature-dependent coefficients, retaining the direct source evaluator as oracle/fallback. The Newton trial temperature changes with both energy and composition; caching one temperature for an entire nonlinear stage would be wrong.

## Existing providers and limits

| Provider | Eligible channels | Domain | Scope |
|---|---|---|---|
| Grackle `igm_rates` | H/He CI, RR, DR, CE, radiative cooling, freefree | 1..1e6 K | Existing Case-A operational model; not empirical fit certification |
| `DAtomicProvider` | H CI/RR/RR-cooling/CE mapped to D | 1..1e6 K | Existing explicit D=H approximation; no isotope-specific fit |
| Savin2002 | D0+H+ forward/reverse CX | 2.7..200000 K | Existing DOI 10.1086/324218 Eq6/Table2 fit, m3/s |
| `RctProvider` | HeIII+HI radiative transfer constants | Source-specific | Already constant, no table benefit; 17-fold source conflict remains explicit |

Source knots include T=5500 K and the actual predicate T/11605<=0.8 (nominally 9284 K). CI floor and CE exponent-cap boundaries also matter. Exact-zero DR, source branch identity, and diagnostic flags must not be blended across a branch. Table error is separate from source uncertainty.

Photoionization Gamma and photoheat are functions of the live radiation field and transport; volumetric reaction/cooling events multiply live density factors. Metastable HeI CE uses ne² nHeII. CMB exchange and expansion also depend on variables beyond gas T. None belong in a T-only table.

The isotope state has T and He3 slots but supplies no corresponding thermal atomic rates. Completed `research/flrw_thermal_charge_exchange_20261016/thermal_cx.py` has independent C9 scoped PASS and is reusable; it is standalone research code, not a newly integrated Rust solver. Do not repeat it.

## Existing acceleration already present

PreparedAbsorption stores quadrature cross sections/excess energies for frozen spectrum/geometry. AxbiBackground already has exact point memoization. OrderedWorkerPool already supports persistent cell preparation and optional independent Jacobian columns. These are existing mechanisms, not missing work to reproduce. A rate bundle/table should remain immutable and shareable; batch independent temperatures without adding nested pools or changing time/Newton order.

## Source identity detail

Eleven of twelve fetched Rust/policy source files matched the local snapshot exactly. Local `axbi_driver.rs` is blob `02c6e82c2265f238e5ff77abab1909028e3aa3c2`; the frozen remote source is `23f0d9a40b8fb8b595d0f73dd6b279067ccadf88`. The remote callgraph was read directly and confirms the finding. This immutable-source byte mismatch requires using the remote source for driver claims; no stale driver edit or execution is authorized by this intake. It does not block an additive rate-only research seam.

## Donor delta since preceding thermal-CX intake

| Lane | Current observed head | Delta and ownership boundary |
|---|---|---|
| REI166 | 553ce556d9f8 | Unchanged source-age/native reference owner; HOLD remains |
| REI167 | 1e6a3dd60d69 | Reports 84 A/B and 20 FullExp histories; common-limit/true-error HOLD; do not duplicate |
| REI168 | c02fb3492b99 | Unchanged source-free RR/DR midpoint/Radau scoped PASS |
| HE74 | bba6c0db991c | Source-cut gate; native pilot reported running, dynamic evidence pending |
| CR77 | a176504a141b | Physical exposure vs endpoint-BE rate oracle; photo-only, no new collisional provider |
| HH103 | 789bd912e61a | Positive-energy finite-L Jost theory; sigma(E), kHH(T) still OPEN and HH_R10 OFF |
| BASS168 | 03a01d21ed21 | Non-LRS FD96 tensor/Hessian and source-only Einstein; no chemistry rates |
| REC99 | e6596cf6083c | U8 original-grid z0 complete; U5 spectral HOLD, refinement NOT_RUN, REI candidate off |

No additional ready physical species-rate provider was identified within this bounded delta. H/He and conditional D reuse are constructive now. CR77's physical-exposure Gamma must not be passed into an unchanged native backward-Euler endpoint owner.

Coverage was the latest two updated open PRs per five donor repositories plus named REI166/167/168, compared with the preceding intake. Donor numerical outcomes are PR-reported and were not rerun; cloud backup claims were not independently verified here. PR branches establish research lanes, not live process ownership. This is not an exhaustive novelty audit.

## Proposed safe execution seam

Add an explicit immutable prepared-rate/table adapter in owned research/new rate files, with exact provider identity and domain checks, branch-aware handling, source oracle/fallback, deterministic batch evaluation, and unchanged production defaults. Validate coefficient errors and point-RHS/ledger errors separately; measure build cost, memory, lookup cost, and amortization. A bounded coefficient benchmark supports no full-driver speedup or cosmological accuracy claim. Root owns the frozen implementation contract and final selection.

