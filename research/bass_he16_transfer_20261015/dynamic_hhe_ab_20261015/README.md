# Dynamic photo-only H/He A/B: source-scoped Rust experiment

This repository directory contains a complete runnable source-scoped Rust experiment. It is distinct from the original full coupled `rei_bianchi` reionization solver. Previous frozen-gas experiments are located in the neighboring `frozen_collision_ab_20261015` research directory.

## Model

Normal-comoving LRS Bianchi I, zbar 20 to 19.8; two experimental photon transport paths (canonical-energy fixed grid versus exact covariant photon momentum). Original Verner HI, HeI, HeII photo cross sections and HHeModel binding/heat ledger, matched fixed midpoint absorption. Gas HII, HeII, HeIII and thermal internal energy per H actually evolve with photon ionizations/photoheat and adiabatic expansion. **Excluded:** recombination, collisional ionization, thermal cooling, ongoing photon source emissivity, production ODE solver. The temperature is computed from ideal-gas u but is not fed back into photo cross sections.

## Files

- `dynamic_hhe_ab.rs`: isolated optimized Rust binary + seven native Rust controls, source-bound immutable Driver/geometry/signature caches, bounded 1- or 2-worker runner.
- `analyze_dynamic.py`: validates all gas nucleon/charge/thermal and photon event/energy ledgers, checks 81 paired cases and exact serial/parallel data parity.
- `test_dynamic_hhe.py`: fourteen Python quantitative controls with manufactured positivity, zero-opacity, species electron and temperature accounting.
- `plot_dynamic.py`: dependency-free white-background SVG for source-scoped HeIII numerical excess.
- `results/FINAL_SERIAL.csv` and `FINAL_PARALLEL2.csv`: 162 native transport-lane rows, identical physical columns; `DYNAMIC_HHE_ANALYSIS.json`: 81 paired case summaries and photo-only limitations.
- `DYNAMIC_HHE_RESEARCH_REPORT_KO.md`: derivation, model assumptions, actual outputs, optimization evidence and claims.
- `NEXT_SCIENCE_DAG.json`: exact next constructive code task to extend beyond photo-only chemistry.

## Compile and run on authorized local Ubuntu

```bash
DEPS="$HOME/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/target/release/deps"
rustc -O --edition=2021 -L dependency="$DEPS" \
  --extern "rei_microphysics=$DEPS/librei_microphysics-2db3552c92b16edc.rlib" \
  dynamic_hhe_ab.rs -o /tmp/dynamic_hhe_ab
/tmp/dynamic_hhe_ab --jobs 1 > /tmp/dynamic_serial.csv
/tmp/dynamic_hhe_ab --jobs 2 > /tmp/dynamic_parallel.csv
python3 analyze_dynamic.py --serial /tmp/dynamic_serial.csv \
  --parallel /tmp/dynamic_parallel.csv --out /tmp/dynamic_analysis.json
rustc --test -O --edition=2021 -L dependency="$DEPS" \
  --extern "rei_microphysics=$DEPS/librei_microphysics-2db3552c92b16edc.rlib" \
  dynamic_hhe_ab.rs -o /tmp/dynamic_hhe_tests
/tmp/dynamic_hhe_tests
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s . -p 'test_*.py' -q
```

Source-specific compiled rlib SHA256: 44b7ea58b04b58e521a2db2686a4b248040414a733120c22689e857ed40d2a3f. This source epoch differs from the production-native original binary epoch. Original original production solver and case history files stay unchanged.

## Scientific admission

`IMPLEMENTATION_VERIFIED / PHOTO_ONLY_DYNAMICAL_SOURCE_SCOPED`; global full EoR physical, thermal and CMB optical-depth error admission is **HOLD**. The fact that ghost HeII photoionizations propagate into gas charge/temperature has been executed here, not yet proven to dominate errors in full production ionization history.