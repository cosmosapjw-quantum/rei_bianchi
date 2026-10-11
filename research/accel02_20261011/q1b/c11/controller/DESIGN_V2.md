# Additive runtime-budget continuation correction

The C11 first actual adaptive pilot rejected one temporal trial and persisted `attempts=1`, `accepted_macros=0`, `rejected_macros=1`. V1's `run_bounded` limits attempts per invocation. Calling it again with the original6-attempt cap would permit7 total attempts. This is a runtime-budget ownership issue, not a physical/numerical acceptance failure.

`adaptive_controller_v2.py` retains V1 and `CONTROL_V1.json` unchanged. Its pure `effective_budget_controls(original_controls,cursor)` returns a copy with remaining attempts and accepted-macro allowances only. All numerical controls, scales, source/local/scientific tolerances and step logic are unchanged. A negative remaining allowance rejects the already-overbudget cursor. Zero allowance is an exhausted budget and executes no map. Inputs are never overwritten.

`budget_lineage(original,effective,cursor)` records prior counts, original/effective limits and canonical JSON hashes of both control dictionaries. These hashes describe dictionaries and are explicitly distinct from the exact `CONTROL_V1.json` file hash retained in dependency closure. The effective controls must be persisted alongside this lineage. Computation always starts from original total controls, never from a previously effective dictionary; callers must not subtract twice.

Two integration choices are supported:

1. Call `effective_budget_controls` once, persist original/effective controls and `budget_lineage`, and call immutable V1 `run_bounded` with the effective controls. This is the integration runner's selected path.
2. Call V2 `run_bounded` with original controls. It performs the translation, enriches callbacks/results with lineage, and calls V1. Do not combine this wrapper with already translated controls.

Four new targeted tests cover cumulative resumed rejection budget, cumulative accepted-macro budget, zero-map exhausted cursor, and failclosed overbudget cursor. They do not rerun the earlier8 controller tests or any native science run. RED and green logs are preserved. No scientific or source accuracy claim follows from this runtime correction.
