# Bounded bootstrap fixture repair

Existing checkout: `/workspace/scratch/d5baa30c266d/rei_isotope`.
Observed branch: `research/rei-coupled-isotope-contract-20261022`.
Observed HEAD before repair: `3e56bbd3d939ab235df2d47f9d012c95674d00fc`; initial tracked/untracked status was clean.
Publication base supplied by controller: `a7bff87` (not independently inspected here).

Requested execution identity: lower-tier coding agent under the frozen Astra contract.
Observed execution metadata: delegated agent task `/root/bootstrap_contract/fixture_implementer`; runtime model identity not exposed or asserted. Python 3.12.14.

Before mutation, all eight `SOURCE_IDENTITY.json/current_files` entries matched the pinned isotope source by SHA256 and byte count. The task directory was absent. Restored its five recovered files; recovered bootstrap/test hashes matched the supplied 04ab417bf497ecf2b83f8597b72f2ec14f631f61155d6e294d6226425e83d1cf / 5d8c8c6ce53805695c24454caf0440e65190f1a0d0eaca9ef738061d9cef2077.

Only `test_bootstrap.py` differs from recovery: normalize omitted fixture rtol/atol defaults on both lookup input and stored lookup cases. Explicit nondefault tolerances and ellmax remain identifying fields. Added a regression test for implicit/explicit nominal-default equivalence and retained control/tolerance/ellmax distinctions. Production `bootstrap.py`, identity manifest, requirements and historical `TEST_STDOUT.txt` remain byte-identical.

Fresh raw logs are separate stdout/stderr pairs:
- `FIXTURE_BEFORE_*`: `PYTHONDONTWRITEBYTECODE=1 python -m unittest test_bootstrap.SummaryTests -v`; exit 1, 3 tests, 3 reproduced ValueError failures at bootstrap.py:337 / original test_bootstrap.py:216.
- `FIXTURE_SUMMARY_*`: same command after repair; exit 0, 4 tests PASS, 0.618 seconds.
- `FIXTURE_FULL_*`: `PYTHONDONTWRITEBYTECODE=1 python -m unittest test_bootstrap -v`; exit 0, 14 tests PASS, 30.463 seconds (the existing 13 plus one regression).

The full suite exercised source-only empty preparation, stdlib plan/clean import with no results; original complete-inventory reuse with compute forbidden and unchanged protected outputs; fixture complete no-work without state rewrite; missing-only resume/inherited budgets; retained failure/partial/interruption; cumulative 90 attempts / 2400 CPU seconds / 900 wall seconds and worker bounds; raw/receipt-derived summary and all three control comparisons; no overwrite; missing/corrupt failure; pending independent review. Limits remain unchanged: maximum 4 workers, actual bootstrap execution serial 1. Case definitions remain 79 nominal + 3 controls + 1 reference.

No actual point checks, ODE solving, rendering or full83 integration was launched. Full fresh83 remains NOT_RUN. Scientific admission remains PENDING_INDEPENDENT_REVIEW. No commit, branch switch, worktree, push, source/physics/solver/contract changes or NCP-policy changes were made. Final source identity recheck passed; tracked diff outside the restored unit is empty.
