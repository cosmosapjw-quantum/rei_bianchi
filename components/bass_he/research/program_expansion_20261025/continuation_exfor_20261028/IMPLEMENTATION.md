# EXFOR11 implementation handoff

The new scientific module is inert on import except for loading unchanged inherited definitions. No production case, inherited suite, CAS, or plot was executed during implementation. Static syntax uses Python `compile(source, filename, 'exec')`; it does not import modules or write bytecode.

`src/exfor_aperture.py` maps the frozen contract to literal EXFOR source parsing, exact decimal sensitivity windows, even Bernstein basis powers/integrals, rational cosine-derived row intervals, inner/outer inequalities, exhaustive exact active-basis enumeration, per-energy geometry strips, and certified linear-fractional extrema with coefficient witnesses. Every basis is attempted; singular and feasible-basis counts are retained. Each inverse is reused across the three energy right-hand sides. Exact results and human-readable float summaries occupy separate fields. The six total rows remain an independent table.

`tests/test_exfor_aperture.py` provides the independent Decimal trigonometric oracle, basis/integral/endpoint controls, small polytopes, empty and degenerate cases, common-scale ratio controls, source/type failures, and a separate saved exact certificate reader. The reader verifies every stored vertex inequality and denominator, inner vertices against outer constraints, exact objective extrema and witness membership, FULL acceptance and all twelve case identities.

`validate_once.py` runs all new controls and actual cases in one primary invocation, saves data even if a control fails, and then rereads the saved certificates. `run_bounded.py` enforces the publication manifest and input checksum instead of claiming that this restored partial mirror has a complete local Git checkout. `measure_execution.py` measures the entire inner runner lifetime, preserves separate outer orchestration timing, and enforces cumulative initial-plus-one-targeted-repair resource accounting. Source commit supplied by parent must be the actual published S05 commit.

Before execution parent writes a pin JSON containing `source_commit`, `source_sha256` (the exact dictionary returned by `run_bounded.manifest()`), and `input_sha256`. Manifest reads can be performed without science imports. Exact command:

```
python -B scripts/measure_execution.py --mode validate --source-commit ACTUAL_S05_COMMIT --pin ABSOLUTE_PIN_JSON --source ABSOLUTE_M0475_X4 --output ABSOLUTE_NEW_INITIAL_DIR --receipt ABSOLUTE_EXTERNAL_RESOURCE_JSON
```

Validation cap is 60 CPU seconds/180 wall seconds/768 MiB, one thread. Plot cap is 10 CPU seconds/30 wall seconds/768 MiB, one thread. `plot_saved.py` imports JSON/Fraction and plotting libraries only; it plots literal observations and already saved family bounds. No fitter, geometry, basis, or scientific campaign is imported by plotter. Parent reviews the actual PNG.

Algorithm cost is 3,984 exact small-matrix inversions across all inner/outer family configurations and 11,952 RHS candidate solves, before singular exclusions. Maximum dimension is five. Nine inherited geometry calls are reused across degrees/endpoints. This is a cost estimate, not an observed runtime.

Requested executor was gpt-6.1-sol. Actual runtime model identity is not observable from the coding worker and remains null.
