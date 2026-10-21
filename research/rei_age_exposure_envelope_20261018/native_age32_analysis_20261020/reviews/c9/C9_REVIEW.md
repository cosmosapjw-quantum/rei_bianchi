# v9 C9 independent review

**PASS_SCOPED.** Three concrete findings were repaired; open findings: **0**. The review covers the new stored-output analysis, the constant-source scalar primitive, and the explicit source-jump integration hook. It does not issue native convergence or production admission.

## Closed findings

- **C9-01 — final event binding.** The final event now verifies clock, active count, N and saved photo ledgers against the endpoint. All 33 actual crosschecks pass. Independent memory-only probes that change endpoint N or photo ledgers are rejected as INVALID. The original files remain untouched.
- **C9-02 — intermediate exponential underflow.** Scaled exponent-product branches retain the representable weighted survival and midpoint ratio. The independent Decimal150 probe gives weighted survival 5.075958897549336e-135 versus reference 5.075958897549457e-135 (relative error 2.378875921469783e-14). At x=1491 the midpoint ratio is 2.554e-321, matching the rounded reference.
- **C9-03 — root bracket classification.** Bracket endpoints are now classified by Decimal100. Independent Decimal150 evaluation verifies the signs for epsilon=1e-16,0.005,0.01,0.1,0.9. At epsilon=0.005 the corrected bracket is [0.3470181810994558,0.34701818109945587], with defect-minus-target signs -1.467536456662775e-18 and +1.265221261187155e-19.

## Evidence and scientific scope

The retained logs contain 12 focused repair tests and the unchanged 12-test integration suite, all passing. One final postprocess wrote results/attempt004; earlier attempts remain. Independent targeted rechecks passed with exact final source hashes in C9_RECEIPT.json. No native trajectory, v8 campaign or v7 benchmark was rerun.

The exact photon telescope, own-population N/U normalization, centered survivor moments, legacy age64 missing-event status, unchanged0.005 and1e-8 gates, nonempty output preservation and numbered execution receipts were inspected. The stored Fraction telescope remains separate from a numerical integration/global error certificate. Scalar limits are conditional on constant source and hazard. Native age/time remain HOLD; the nonlinear Grackle response bound remains NOT_ESTABLISHED; PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED.

All three required repairs are closed. The scoped review stops here.
