# BASS_HE / rei_bianchi: frozen H/He photon transport A/B

**Scope:** This isolated research lane compares original Rust two-neighbor fixed-energy-bin projection against exact covariant-momentum photon flight under the same prescribed non-evolving gas H/He absorption and cosmological Bianchi I geometry. It is not the fully coupled reionization solver and is not the warm HE18 16-cell model.

## Files

- `frozen_collision_ab.rs`: verified optimized Rust source; readonly original crate Driver states and 49 source-grid Verner signatures are hoisted with OnceLock; at most 2 workers. Direct canonical energy-grid `sigma(E_i)` in projected arm; original `CovariantPhoton` and `absorb_frozen_gas` in the unprojected arm.
- `frozen_collision_ab_canonical_uncached.rs`: identical canonical-grid H/He transport without immutable signature cache for performance/parity reference.
- `frozen_collision_ab_reference.rs`: earlier frame-roundtrip projected reference demonstrating one-ULP threshold opacity switching. Not the authoritative fixed-grid projected lane.
- `audit_threshold_roundoff.rs`, `verify_heii_threshold.rs`, `debug_midpoint_projection.rs`: native provider and source-ray narrow audits.
- `analyze_ab.py`, `test_frozen_collision_ab.py`, `plot_heii_ab.py`: science acceptance, source-bound regression, white SVG figure.
- `results/CANONICAL_CACHED_SERIAL.csv`, `CANONICAL_CACHED_PARALLEL2.csv`, `CANONICAL_UNCACHED.csv`: full 108 cases x 2 lane native evidence, identical physics columns (only timing differs).
- `results/FRAME_ROUNDTRIP_*.csv` and `results/FRAME_ROUNDOFF_THRESHOLD.csv`: previous deliberately problematic energy re-reconstruction and source-ULP effects.
- `results/ATOMIC_SOURCE_SURFACE_IDENTITY.json`: 12 tested original Rust atomic/geometry/transport function bodies compared across distinct original source epochs. The optional `absorb_frozen_gas` reference belongs to the separately compiled rlib, not the original frozen production binary.
- `FROZEN_HHE_AB_RESEARCH_REPORT_KO.md`: physical derivation, source/units, quantitative false HeII events and limitations.
- `NEXT_SCIENCE_DAG.json`: durable next code and physical acceptance requirements.

## Native source setup and reproducibility

Inputs: user original Ubuntu `rei_bianchi/rust/rei_microphysics/target/release/deps/librei_microphysics-2db3552c92b16edc.rlib` (SHA256 `44b7ea58b04b58e521a2db2686a4b248040414a733120c22689e857ed40d2a3f`). The original compiled source epoch for this reference rlib differs from the frozen original full AXBI execution binary; do not claim whole-binary identity.

Example from this directory:

```bash
RUST_DEPS="$HOME/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/target/release/deps"
rustc -O --edition=2021 -L dependency="$RUST_DEPS" \
  --extern "rei_microphysics=$RUST_DEPS/librei_microphysics-2db3552c92b16edc.rlib" \
  frozen_collision_ab.rs -o /tmp/axbi_frozen_ab
/tmp/axbi_frozen_ab --jobs 1 > /tmp/FROZEN_AB_SERIAL.csv
/tmp/axbi_frozen_ab --jobs 2 > /tmp/FROZEN_AB_PARALLEL2.csv
python3 analyze_ab.py --serial /tmp/FROZEN_AB_SERIAL.csv \
  --parallel /tmp/FROZEN_AB_PARALLEL2.csv --out /tmp/FROZEN_AB_ANALYSIS.json
rustc --test --edition=2021 -O -L dependency="$RUST_DEPS" \
  --extern "rei_microphysics=$RUST_DEPS/librei_microphysics-2db3552c92b16edc.rlib" \
  frozen_collision_ab.rs -o /tmp/axbi_frozen_ab_tests
/tmp/axbi_frozen_ab_tests
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s . -p 'test_*.py' -q
```

Working directory contains precomputed source-bound CSV test fixtures, so Python tests do not need to rerun Rust.

## Admission

Original cold AXBI EoR H/He fractions are not evolved. Frozen HI/HeI/HeII occupancies are intentionally prescribed; photon trace stocks avoid exhausting absorber nuclei. Positive fake HeII photoevents at a 54.42 eV grid threshold demonstrate a numerical source/transport mismatch under this hypothesis, not a measured astrophysical ionization signal. Admission remains `IMPLEMENTATION_VERIFIED / FROZEN_SOURCE_SCOPED` and full coupled global error remains HOLD.

Next: use `NEXT_SCIENCE_DAG.json` task `HHE_AB5` for an isolated dynamically updated HII/HeII/HeIII/thermal A/B subject to original gas, photon and source event ledgers before attempting production replacement.
