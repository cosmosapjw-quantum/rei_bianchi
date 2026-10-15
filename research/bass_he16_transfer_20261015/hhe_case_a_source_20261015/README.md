# BASS_HE → rei_bianchi: cold AXBI original Case-A microphysics + two photon transport lanes

**Actual completed scope:** Source-coupled HII/HeII/HeIII and gas internal energy evolution in a short non-tilted LRS Bianchi I experiment using the original cold `AxbiProvider::point` with original Grackle 3.4.1 Case-A ionization/recombination/cooling, native CMB Compton operator and matched Bianchi proper-time clock. It is not a full continuous-emissivity or coupled on-the-spot reionization solver.

The authorizing parent code/source/photons are under neighboring research paths, and original live `rei_bianchi` remains untouched.

## Source entrypoints

- `case_a_source.rs`: bounded q=-0.005,0,+0.005 and 54 physical A/B cases, native original Driver geometry and Verner source. Compile directly with original Rust release rlib.
- `case_a_micro.inc.rs`: original source-driven Case-A Heun proper-time micro integration with 1e10s maximum micro substep; no arbitrary source-rate fits or clipping.
- `SOURCE_PROBE.rs`: direct native source-rate/thermal RHS readback at cold T~8 K.
- `analyze_case_a.py` and `test_case_a_source.py`: mathematical species, atomic binding, whole-energy and CMB/escape evidence checks from source results.
- `SOURCE_RATE_SURFACE_IDENTITY.json`: byte identity of seven selected rate/thermal/EOS functions between original frozen source and separately compiled rlib source records.
- `results/CASE_A_SERIAL.csv`, `CASE_A_PARALLEL.csv`, `CASE_A_HALF_MICRO.csv`: original matched source A/B outputs, serial/parallel and halved micro step.
- `CASE_A_SOURCE_RESEARCH_REPORT_KO.md`: mathematical derivation, physics assumptions, numerical result and admission scope.

## Exact build/run on the authorized Ubuntu

```bash
DEPS="$HOME/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/target/release/deps"
rustc -O --edition=2021 \
  -L dependency="$DEPS" \
  --extern "rei_microphysics=$DEPS/librei_microphysics-2db3552c92b16edc.rlib" \
  case_a_source.rs -o /tmp/axbi_case_a_source
/tmp/axbi_case_a_source --jobs 1 > /tmp/case_a_serial.csv
/tmp/axbi_case_a_source --jobs 2 > /tmp/case_a_parallel.csv
PYTHONDONTWRITEBYTECODE=1 python3 analyze_case_a.py \
  --serial /tmp/case_a_serial.csv --parallel /tmp/case_a_parallel.csv \
  --out /tmp/AXBI_CASE_A_REPORT.json
rustc --test -O --edition=2021 \
  -L dependency="$DEPS" \
  --extern "rei_microphysics=$DEPS/librei_microphysics-2db3552c92b16edc.rlib" \
  case_a_source.rs -o /tmp/axbi_case_a_tests
/tmp/axbi_case_a_tests
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s . -p 'test_*.py' -q
```

Source-specific bound: original rlib binary SHA256 44b7ea58b04b58e521a2db2686a4b248040414a733120c22689e857ed40d2a3f. Full frozen original EoR native binary source epoch differs; `SOURCE_RATE_SURFACE_IDENTITY.json` proves only seven directly tested source function bodies match.

Micro-step refinement is archived separately, as a copy of the source that changes only `MICRO_MAX_DT_S` from 1e10 to 5e9. It is **not** a certified global EoR error limit.

## Conservation tests

For each photo and micro source event: H and He nucleus abundance conservation, electron charge source, selected original opacity thresholds, photon number, radiation + binding + kinetic heat + Compton exchange + expansion work and escaping Case-A recombination radiation. The original native EOS and original `igm_point_rhs` thermal source are used without double-counting expansion (handled by exact half-step map). All inputs are physical proper densities and proper seconds.

**Exclusions**: ongoing photon emissivity, secondary recombination-photon redistribution (coupled OTS), independent global true-error or CMB observational admission, longer cosmological reionization histories. Publication-admission remains HOLD.
