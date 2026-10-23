# REI coupled isotope contract — C1

Read `REPORT_KO.md` for results and `CONTRACT.md` for exact definitions,
assumptions, finite acceptance and future interface obligations.

The 21-state event bookkeeping is a mathematical contract. `check_contract.py`
is a finite, self-contained diagnostic; it is not a coupled cosmological
solver or a physical daughter-yield provider. It does not run the old sweeps.

## Reproduce the diagnostic

Use Python 3.12 on Linux; the actual run used 3.12.14. There are no nonstandard
Python dependencies. Reproduce in a separate extracted copy if preserving the
supplied run receipts byte-for-byte: the diagnostic writes its own JSON evidence.

```bash
python research/rei_coupled_isotope_contract_20261022/check_contract.py
```

From a source-only ZIP, enter the extracted root containing the `research/`
directory first. An absolute script path also works. The small fixtures suffice;
the historical Git checkouts are not required. A missing original local source
is reported `SOURCE_NOT_LOCAL`, not a fresh original-source byte match. Copied
fixture hashes remain checked. Actual source copies were available and matched
in the recorded producer run.

Expected finite result: 191 named checks, zero failed checks, exit0. Negative
controls deliberately produce rejected ledgers or unresolved-input exceptions
and record them as successful rejection tests. No physical probability or
energy partition is inferred from a manufactured test value.

`evidence/EXECUTION.json` identifies the actual run. `evidence/ALGEBRA_CHECKS.json`
holds all numerical inputs, outputs and residuals. Independent scoped review
is recorded in `REVIEW.md` and `evidence/INDEPENDENT_REVIEW.json`.
`DAG.json` and `RESUME.md` define the remaining work. Delivery receipts are
post-checkpoint records; they do not rewrite the immutable source ZIP.
