# CLOSEOUT RECEIPTS

All commands were read-only with respect to the target repository. Python used `-B`; no production/history/parity/package/BDF driver ran.

## Harness identity

- Archive: `/home/cosmosapjw/Dropbox/physmath-research-harness-gpt56.zip`
- SHA-256: `9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934`
- Harness version: `3.1.0`
- Archive safety inspection: 59 members; no absolute path, traversal, backslash path, or symlink member.

## Harness structure check

Command: `python3 tools/validate_workspace.py`

Result before final contract removal: `Research harness validation passed.`

## Active-stage unit tests

Command: `python3 -B -m unittest discover -s <active-adaptive-history-stage>/tests -p 'test_*.py'`

Result:

```text
.................................................
----------------------------------------------------------------------
Ran 49 tests in 8.501s

OK
```

Claim ceiling: diagnostic regression evidence only. These tests do not negate the exact counterexamples or supply production/scientific authority.

## Independent exact probes

Current helpers were loaded directly from bound HEAD without running the history driver.

```text
SIGNED_SUM -5e-324 5e-324 CONTAINS_EXACT_1 False
KRAWCZYK_CERTIFIED [True]
KRAWCZYK_PUBLISHED [3.9999999999999933, 6.9999999999999885] [3.9999999999999996, 6.999999999999999]
KRAWCZYK_EXACT [4, 7] CONTAINS [False, False]
PURE_HEII_CURRENT_PER_H 0.006241 EXPECTED_PER_H 0.079 RATIO 0.079
```

The first probe attempt printed the signed-sum and Krawczyk bounds but failed only in the reporting expression because a two-element NumPy array was coerced to `bool`. One corrected reporting retry produced the complete output above; no scientific computation changed.

## Target repository custody

Command: `git rev-parse HEAD && git diff --no-ext-diff --exit-code -- . && git status --short --untracked-files=all`

Result:

```text
111b6ace750e36e218df7fc9626c6bad2ec19971
?? rei_bianchi_0cf932378225e4b14c36d1c80597b76cda2b7088_self_contained.bundle
?? rei_bianchi_agent-precalc-adaptive-history-parallel-runtime_from-ae340271.bundle
```

Tracked diff is empty. The two pre-existing bundles were not opened, hashed, moved, or modified.

## Bounded-work closeout

Command before ephemeral-contract deletion: `python3 ~/.codex/bounded-work-harness/bounded_work.py check WORK_CONTRACT.json`

Result: `PASS WORK_CONTRACT.json`

Recorded maxima: one metacognitive pass, one independent review round, one repair-closeout round (schema-only correction: completed work requires `finding: null`), one reporting-only same-failure retry, and peak four active agents. All are at or below frozen limits.

## Runtime admission ceiling

- Live: Python `3.12.3`, NumPy `2.4.2`, SciPy `1.17.0`, pandas `3.0.0`; JAX absent.
- Pins include NumPy `2.3.5`, SciPy `1.17.0`, pandas `2.2.3`.
- Therefore production/scientific execution remained blocked and was not attempted.
