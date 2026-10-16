# Temperature coefficient APIs

`AxbiProvider.point` now prepares the unchanged direct bundle once and reuses it in the original event/energy ledger. `IgmRateBackend::default()` is `Direct`.

```rust
use std::sync::Arc;
use rei_microphysics::rate_table::{IgmRateTable, IgmRateBackend};
let table = Arc::new(IgmRateTable::build_default()?); // 65537 nodes, explicit setup
let backend = IgmRateBackend::Table(table.clone());
let prepared = backend.prepare(temperature_k)?;
let same_h_equality_d_rates = d_provider.rates_from_prepared(&prepared);
let point = axbi_provider.point_with_backend(&backend, &gas, nh, nhe, h, tcmb, photo)?;
let coefficient_rows = table.batch_soa(&temperatures)?;
let parallel_rows = table.batch_parallel(&temperatures, 4)?;
```

Prepared values bind one exact temperature; `igm_point_rhs_with_prepared` rejects a changed EOS temperature. There is no global mutable cache or derivative API. The table changes coefficient evaluation only; no Newton or driver path is switched automatically.

Batch outputs contain fifteen independent coefficient rows in the following order. Scalar `rates` also reconstructs selected DR cooling and source diagnostics.

| Rows | Channels | Units |
|---|---|---|
| 0–2 | H/He CI | cm³/s |
| 3–5 | H/He RR | cm³/s |
| 6 | He DR | cm³/s |
| 7–9 | HI/metastable HeI/HeII CE | erg cm³/s, erg cm⁶/s, erg cm³/s |
| 10–12 | RR cooling | erg cm³/s |
| 13 | raw DR cooling | erg cm³/s |
| 14 | free-free coefficient | erg cm³/s |

Li coefficients and separate Li6/Li7 number states live in `lithium_rates`. The caller must choose `IsotopeRatePolicy::ElementalElectronicEquality`; `IsotopeResolved` reports `MissingSource`. Individual cold RR/DR domains remain available, while complete-chain calls use their actual common domain. This component supplies number sources with explicit electron density, without a Li thermal, photon, abundance, or nuclear-decay closure.

The frozen focused source bundle builds without manual downloads once a compatible Rust compiler is available:

```sh
python3 build_focused.py --rustc /path/to/rustc --output /tmp/rate-focused
/tmp/rate-focused/rate_table_tests --test-threads=1 --nocapture
/tmp/rate-focused/lithium_rates_tests --test-threads=1 --nocapture
```

The focused harness omits only the unrelated `joint_affine` declaration/reexports because Rust 1.85.1 predates its float next-up/down API. Changed modules and needed source bytes are frozen in `focused_bundle`. Historical uncalled driver context remains only compilation context; the current external driver and full production crate were not verified by this harness.
