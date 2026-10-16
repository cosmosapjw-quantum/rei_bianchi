# Compact Thomson pair observable

This unit evaluates the frozen Thomson contract against the saved compact
`ne_cm3` norms, without loading histories or running a solver. The observed
implementation checks and all six synthetic fixtures passed. Fresh independent
Astra review remains pending; solver convergence and continuum accuracy are HOLD.

The nominal binary64 calculation selected `B_L2 = 8.749468843353422e-8`, giving
`q = 8.749468460587409e-8` for the common-interval absolute transmission and
last-scattering total-variation envelope, including the distinct no-scatter
state. This is a conditional numerical evaluation of the exact derived bound.
The published norm summaries and float upper sums lack outward rounding
enclosures. Nonnegative electron densities remain an explicit theorem assumption.
Background applicability is supported by source-lineage and configuration
evidence; the compiled aggregate was not reassembled in this work.

Run from this directory with Python 3 and its standard library:

```sh
python3 code/run_bounded.py
```

The runner executes the exact two commands prescribed by the contract, each
with a 30-second timeout, and preserves wall time, child user/system CPU time,
exit status, stdout, and stderr in `results/EXECUTION_RECEIPT.json`. The evaluator
uses 8192 panels following `spec/CONTRACT_AMENDMENT.json`; the initial 4096-panel
probe exceeded the unchanged raw second-moment relative-width gate. Independent
50-digit Decimal arithmetic checks the background endpoints, moments, three
bound components, selected bound, and probability formula at frozen tolerances.

The six fixtures cover constant-hazard sharpness, signed cancellation,
localized visibility, zero differences and cgs/SI conversion, shared-background
mismatch, and analytic matter-only quadrature. Their inputs, expected values,
observed values and check outcomes are in `results/TEST_RESULTS.json`.

Only `code/`, `tests/`, `results/`, and this README were created by the coding
worker. No raw-history read, PL analyzer replay, solver/renderer launch, remote
run, canonical DAG edit, or publication was performed. Historical FULL005 debit
`156.5376037069618 / 300 seconds` and absolute deadline `1792122617.77407` remain
unchanged archival provenance; new NCP allocation is zero. The source commit
and repository anchor are input provenance; this sandbox unit is not a git
checkout, so no local branch or diff against those commits is asserted.

The executor requested model was `gpt-6.1-sol`; runtime identity was not
independently observed. The next action is the frozen fresh read-only Astra
review of the code and actual outputs.
