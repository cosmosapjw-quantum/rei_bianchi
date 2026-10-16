# One authorized endpoint repair

Initial nine-test PASS and the independent HOLD are retained. Before editing, the two changed Python files and all original frozen identities/receipts/return/report/selection/manifest were copied into pre_repair/. Original raw outputs, WRAPPER_RECEIPT and CODE_FREEZE at the preparation root are unchanged.

Only stage coordinates changed: integrate computes one transaction endpoint, using the exact mesh target when capped; transaction computes one midpoint and passes explicit coordinates to coarse and fine Heun stages. Coarse F1 and second fine F1 use the same endpoint. Nonprogressing endpoint/midpoint raises STEP_UNDERFLOW_HOLD before callbacks. State arithmetic, step h values, Heun coefficients, CFL, tolerances, constraints, fine acceptance and birth ownership remain unchanged. No algebraic-B RHS was introduced.

One supplemental synthetic invocation: **11/11 PASS**, exit0, process wall0.1901098609669134s, user0.142507s, system0.019203s, peakRSS16072704B. Total **2 invocations / 0.33612156996969134s**, under original30s cumulative allocation. Strict supplied hex coordinates reproduce the old one-ULP overshoot and now verify every callback lies within the exact target, including a capped birth boundary. A one-ULP interval regression verifies no callback occurs when the midpoint cannot progress.

The supplemental raw receipt has a metadata defect: cwd serialized as "0" after the launcher reused a variable for exit status. Actual subprocess cwd was set correctly and is recorded in both prelaunch REPAIRED_CODE_FREEZE and raw/STARTED. RECEIPT_CLARIFICATION records the actual cwd and cause; the original receipt is preserved, and no rerun occurred.

Runtime helper remains UNBUILT_UNRUN; no Rust builds/helper/native/setup/physical RHS/reference calls. Actual ELF/setup/Gamma/heat/prepared-node observations remain null/HOLD. Old campaign costs/cutoffs and all broader scientific HOLDs remain unchanged. Next: fresh narrow independent Astra endpoint-repair review; root sole publication owner.

## Final independent closure

INDEPENDENT_REVIEW_AFTER_REPAIR.json records SCOPED_CODE_PREPARATION_PASS/publication approved, no findings or repair. Preparation only; helper UNBUILT_UNRUN/physical HOLD. Next BUILD_ONLY_AUTHORITY_PENDING, no build/run authorized. Original HOLD/costs/raw remain preserved.
