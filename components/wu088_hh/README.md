# Hydrogen and deuterium microphysics in REI

The supported REI entry point is `rei_bianchi.microphysics.hh`. It reads the packaged Savin Table 1 and returns forward/reverse rate coefficients, proper-volume sources for each ion and neutral, and the gas/internal energy transfer. The default AXBI H/He calculation retains its published source configuration. The conditional deuterium study supplies its own ground-state and initial-state assumptions.

```python
from rei_bianchi.microphysics.hh import charge_exchange_source
s = charge_exchange_source(T_K=100.0, n_HI_cm3=1.e-3, n_HII_cm3=1.e-4,
                           n_DI_cm3=2.5e-8, n_DII_cm3=2.5e-9)
print(s.net_events_cm3_s, s.gas_power_erg_cm3_s, s.electron_rate_cm3_s)
```

The upstream authority is WU088_HH PR199 at commit `6e04dcaf448269216330a75f1364b831c41e6c1e`. Its root tree is `cadfc675918e1c843fa57e6b27e8071e30cf8011`. The branch includes 1,365 commits beyond donor main and incorporates R51–R59. The separately reported WU 34/49 is a historical WU project metric. [Original WU snapshot](https://github.com/cosmosapjw-quantum/WU088_HH/tree/6e04dcaf448269216330a75f1364b831c41e6c1e)

The tree `upstream/` supplies 3,849 original files, including the WU Python and native implementations, tests, original tables and runtime input fixtures. The archive `HISTORICAL_EVIDENCE.tar.gz` carries 12,478 additional original results, documents, figures and evidence files. The per-path inventory in `UPSTREAM_INVENTORY.csv.gz` includes all 16,460 donor blobs, Git modes, byte counts, Git blob IDs and storage dispositions. The remaining 133 entries include old nested source archives, binaries, fonts, externally sourced publications and previously generated encodings. `UPSTREAM_COVERAGE.json` binds the inventory and archive. Original notices are preserved in their relative locations.

To run a historical calculation that reads saved results, use an isolated working copy. Legacy paths and scientific inputs that only existed in a previous private run require their original data. Examples include the original 46,080-row F05 compressed source arrays expected by R51 and the external R56/R57 F05 paths hard-coded by R58. The new REI D/H API and the five-case calculation below operate entirely on repository sources.

```sh
cp -a components/wu088_hh/upstream /tmp/rei-wu-work
python components/wu088_hh/restore_historical_evidence.py /tmp/rei-wu-work
# Hosts exposing Linux CPU topology through /proc rather than sysfs can apply this patch.
(cd /tmp/rei-wu-work && git apply /absolute/path/to/components/wu088_hh/validation/linux_topology.patch)
```

To recompute the study and run its integration tests, run from the REI repository root with NumPy and SciPy installed. The new package's runtime rate and conservation API uses the Python standard library.

```sh
PYTHONPATH=src python components/wu088_hh/analysis/trace_original_axbi.py \
  research/rei_igm_sync_20261116/approximation_validity/incremental_fifth/results_five/five_case_abundances.csv.gz \
  /tmp/rei-five-case-trace
PYTHONPATH=src python -m unittest discover -s components/wu088_hh/validation -v
```

For scientific results and limits, see [the isotope analysis](analysis/SCIENCE.md) and [the five-case numerical summary](analysis/results/FIVE_CASE_TRACE.json). The archive retains upstream package metadata to reconstruct historical builds and tests. New development in this component uses the REI package and integration contracts.

The [validation receipt](validation/RESULTS.json) records the native compiler and product hashes, 143 original tests covering six certificate/promotion modules, hardware/orchestration, both native libraries and the coupled-source/moment calculations, and four REI integration tests. All 1,271 tests of the preserved original core were collected. Historical test paths are relative to the hydrated donor root. On a host that disallows Unix-domain sockets, the two PHYS33 modules can run their own supported spawn implementation through ordinary multiprocessing pipes.

```sh
cd /tmp/rei-wu-work
PYTHONPATH=src python scripts/build_native.py
PYTHONPATH=src python -m pytest -q tests/test_native.py tests/test_hardware.py tests/test_orchestrator.py
PYTHONPATH=src python -m pytest -q tests/test_phys44_boundary.py tests/test_phys44_rei_guard.py \
  tests/test_phys55_hybrid_outgoing.py tests/test_phys56_screened_exterior.py tests/test_promotion.py tests/test_r31r.py
PYTHONPATH=src python -c 'import sys,pytest; from wu088_hh import phys33_coupled_source as c,phys33_moments as m; c.get_all_start_methods=m.get_all_start_methods=lambda:["spawn"]; sys.exit(pytest.main(sys.argv[1:]))' \
  -q tests/test_phys33_coupled_source.py tests/test_phys33_moments.py
```
