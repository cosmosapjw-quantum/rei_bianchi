# rei_brperf01_rates

Opt-in positive compact temperature-coefficient receiver for the immutable BR06
H/He/D `igm_rates` source. The default backend remains Direct.

```rust
use rei_brperf01_rates::{CompactRateTable, RateBackend, DEFAULT_NODES};
use std::sync::Arc;

let direct = RateBackend::default();
let table = Arc::new(CompactRateTable::build(DEFAULT_NODES)?); // 8193 nodes
let selected = RateBackend::CompactScalar(table.clone());
let coefficients = selected.rates(10_000.0)?;

// Optional immutable transport; validates source and payload SHA-256 on read.
let bytes = table.to_bytes();
let restored = CompactRateTable::from_bytes(&bytes)?;
assert_eq!(restored.source_evaluations(), 0);
```

Native integration uses the separately owned `rei_brperf01_native_rates`
`step_strang_with_evaluator` API with a closure `|t| table.rates(t)`.
The table does not own populations, density products, radiation, geometry,
charge exchange, integration control or energy ledgers.

Run `bash RUN_STAGE.sh` within the restored full BRPERF01 layout. Run
`bash RUN_STAGE.sh --bench` only when other timing workloads are idle.
`prepare_restore.py` snapshots this source plus the exact parent crate and
checks every restored payload hash; shared pinned registry/toolchain are
reused, with a separate empty target for compilation.

See `REPORT_RATES_KO.md` for derivation and actual results,
`SOURCE_CONTRACT.json` for channel units and source identity,
`DAG_RATES.json` for admission limits, and `evidence/` for all raw measurements.

The selected 8193-node scalar receiver met the **sampled** 1e-4 coefficient error
target (measured maximum 1.300166e-5). 4097 nodes missed that target. The old
65537-node log-linear table is more accurate on the measured sample set. No
universal error bound or full-trajectory acceleration is claimed here.

`wide=1.7.1` is actually applied to the optional scalar-bit-equivalent SIMD
receiver. It provided no additional speedup on the tested SSE2/no-AVX target;
scalar remains recommended. `sha2=0.10.9` implements source/cache integrity.
Exact dependencies and license metadata are in `Cargo.lock` and the shared
offline registry. All original source notices remain with the parent crate.
