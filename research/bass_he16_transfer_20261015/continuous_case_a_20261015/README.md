# Original cold MD14 source + Case-A H/He photon transport comparison

Native research-only implementation. **Non-tilted LRS Bianchi I, zbar=20 to19.998.** This package uses the original cold `rei_microphysics` Rust source and **does not** change the production solver. It is not a fully calibrated long reionization history and does not close stellar/recombination radiation `Q^a`.

## Source/physics

Original `AxbiSource.at_redshift` emitted number rate per H per proper second, original 48 BB50K source spectral modes split at 13.6/24.59/54.42/100eV, eight angular Gauss directions. Birth cohorts weighted at each proper midpoint with original normal-frame solid-angle Jacobian. 4π photon source already integrated. `PROJECTED` uses original `Driver::deposit` and twice-per-step `geometry_map`. `COVARIANT` stores conserved Killing spatial covector with `CovariantPhoton`, born at the SAME energy/clock/angular direction; no intermediate grid reprojection. Original `AxbiProvider.point` Grackle3.4.1 Case-A H/He ionization/recombination/collisional/thermal/Compton source; escape photons are accounted as energy but have no invented angular/spectral moment or re-emission. Gas, photon, binding/heat/escape/CMB, expansion, boundary and source-emitter energy ledgers verified.

## Files

- `continuous_casea.rs` executable source with 4 native Rust tests, outputs all birth/emissivity, gas/photoheat, photon positive U/F/Pi moment/conservation data.
- `case_a_micro.inc.rs`: matching original cold Grackle Case-A micro source Heun operator, proper s.
- `source_gl16.rs`: independent 16-point Gauss source birth integral using native H(a) and original `AxbiSource`.
- `source_support.rs`: original source 48x8-mode minimal true endpoint energy proof at selected finite background.
- `source_only_boundary.rs`: independent native source-only no-absorption demonstration of persistent lower boundary loss for 1/8/32/128/512 steps.
- `analyze_continuous.py`, `test_continuous_casea.py`: inspect 48 A/B rows, check real nuclei, gas, charge, total source/gas/radiation energy and angular positivity cone, GL16 source quadrature and negative fixtures.
- `plot_continuous.py`: white SVG of actual projected photon boundary error and evolving HeIII numerical response.
- `SOURCE_METHOD_IDENTITY.json`: two actual original `AxbiSource` methods byte-equal between separately compiled rlib source and frozen native source; full binary/source epochs are DIFFERENT.
- `results/`: 48 real Rust rows at four physical source step levels; GL16, support and source-only independent native references; SVG, JSON and performance measurements.
- `RESEARCH_LOOP_KO.md` detailed physics and scientific claim/admission, `NEXT_DAG.json` future tasks.

## Reproduce directly on authorized Ubuntu, no local Codex

```bash
DEPS="$HOME/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/target/release/deps"
rustc -O --edition=2021 \
  -L dependency="$DEPS" \
  --extern "rei_microphysics=$DEPS/librei_microphysics-2db3552c92b16edc.rlib" \
  continuous_casea.rs -o /tmp/rei_original_md14_casea
/tmp/rei_original_md14_casea --jobs 1 > /tmp/md14_serial.csv
/tmp/rei_original_md14_casea --jobs 2 > /tmp/md14_parallel.csv
PYTHONDONTWRITEBYTECODE=1 python3 analyze_continuous.py \
  --serial /tmp/md14_serial.csv --parallel /tmp/md14_parallel.csv \
  --gl16 results/SOURCE_GL16_REFERENCE.csv \
  --support results/SOURCE_SUPPORT.csv --out /tmp/casea_analysis.json
rustc --test -O --edition=2021 -L dependency="$DEPS" \
  --extern "rei_microphysics=$DEPS/librei_microphysics-2db3552c92b16edc.rlib" \
  continuous_casea.rs -o /tmp/rei_original_md14_casea_tests
/tmp/rei_original_md14_casea_tests
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python3 -m unittest discover -s . -p 'test_*.py' -q
```

Original scientific reference: [Friedrich et al. (2012)](https://academic.oup.com/mnras/article/421/3/2232/1077406), photon-conserving He/H RT and explicit Case-A vs coupled OTS distinctions. Relevant sibling science: C13 native source, C16 positive photon moment cone/stellar emitter recoil. See RESEARCH_LOOP_KO.md for evidence and boundaries.

## C8 새 결과: energy × time source-only 수렴성

원래 MD14 광자 방출원에 대해 원래 에너지 문턱 구간당 4,8,16,32,64개 셀과 시간분할 1,8,32,128개를 독립적으로 바꾸는 source-only 실험을 실제 Rust에서 실행했다. 20개 케이스의 유출 원본은 `source_boundary_2d.rs`, `results/SOURCE_BOUNDARY_2D.csv`, `results/BOUNDARY_2D_ANALYSIS.json`, `C8_SOURCE_GRID_2D_KO.md`에 있다. 독립 테스트 `test_boundary_2d.py`는 10/10 PASS이고 원래 16셀 source-only 계산에 대한 회귀 테스트를 포함한다. Fixed-grid time refinement alone does not cure the spurious lower boundary; energy grid doubling reduces the measured source-only artifact by about 1/2 within tested range. Photo-chemistry grid convergence and full continuum-spectrum UV leakage have NOT been certified. Scientific admission stays source-scoped.
