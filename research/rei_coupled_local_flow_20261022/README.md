# Coupled local flows for REI

Decision: **PASS_SCOPED_LOCAL_THERMAL_AND_BETA_FLOWS**, independently
recommended and adopted by the controller for the declared finite models.

This self-contained CPU unit implements two finite local models with the
preserved hydrogen RR fit and evaluated neutron lifetime:

* Dark pure-H Case-A recombination with evolving temperature, an exact
  composition–temperature first integral and independently tested escaped
  energy balance.
* Prescribed-temperature neutron beta decay plus H recombination, exact
  positive subflows, second-order Strang composition and a Bessel reference.

Read [REPORT_KO.md](REPORT_KO.md) for results and interpretation,
[THEORY.md](THEORY.md) for derivation,
[INDEPENDENT_REVIEW.md](INDEPENDENT_REVIEW.md) for the independent assessment,
and [IMPLEMENTATION.md](IMPLEMENTATION.md) for actual execution commands.

## Run offline

Requirements observed in the execution environment: Python3.12.14,
NumPy2.3.5, SciPy1.17.0 and Matplotlib3.10.8. Installed dependencies suffice;
the code makes no network request. From the repository root:

```bash
bash research/rei_coupled_local_flow_20261022/run_fresh.sh
```

From inside an extracted unit directory:

```bash
bash run_fresh.sh
```

The helper prints a new `/tmp/rei-coupled-local-flow.*` directory and runs
there. Delivered observations remain intact. Its default command executes
the baseline diagnostic; the separate paired-timing driver documents a
targeted performance follow-up and is not automatically replayed.

For an input/import check without integrations:

```bash
bash run_fresh.sh --prepare-only
```

This preparation path was actually executed after the standalone repair.
The numerical equations are unchanged from the successful first run.

## Observed results

The first scientific invocation completed **103/103 checks, exit0** with
82 retained arrays and three figures. Body clocks after library imports were
40.260782s wall/38.323069s CPU; process peakRSS113576KiB. The one authorized
paired-timing follow-up completed separately, with 96 repeated output checks,
12 representative output arrays and a fourth figure. It used body
4.362195s wall/4.358365s CPU. These counts are separate invocation records.

Maximum reduced thermal x scaled error3.12413e-10, T relative error2.57759e-11,
independently evolved total-energy residual2.14210e-15. Bessel/Radau agreement
is4.21885e-14; observed final Strang orders remain near2. Trace onset
1e-104 is resolved componentwise to1.28786e-14 relative error.

Paired timing favors the direct two-state thermal solve in all three observed
medians, with overlapping ranges. No universal speedup is admitted. The
chosen precision baseline is direct DOP853 for both thermal and beta cases;
retain the exact orbit as a reusable physical constraint/reference, and
Strang as the verified positive conservative stage construction.

## Evidence layout

| Path | Purpose |
|---|---|
| `code/local_flows.py` | Scientific formulas and exact flows; unchanged after first run |
| `code/run_diagnostic.py` | Frozen finite checks, references, timing and figures |
| `code/run_paired_timing.py` | One targeted timing clarification with saved references |
| `inputs/` | Three byte-preserved small JSON inputs and copy manifest |
| `results/results.json`, `raw_arrays.npz` | First-run numbers and arrays |
| `results/execution.json`, `checks.json` | Original execution/check record |
| `results/first_run_source.zip` | Exact first-run source snapshot |
| `results/packaging_patch.diff` | Narrow postrun delivery correction |
| `results/paired_timing.json` | Paired CPU/wall samples and accuracy observations |
| `figures/` | Four inspected PNGs |
| `SOURCES.md`, `WOLFRAM_CHECK.md` | Actual literature and symbolic-check scope |
| `RESUME.md` | Scope, adopted path and next physical dependency |

The RR thermal moment is a same-fit conditional closure. Beta energy
partition/stopping is a future input dependency; the beta calculation here
has prescribed temperature. All conventions are stated once in the contract
and theory. No old C1/C2 or cosmological integration was invoked.
