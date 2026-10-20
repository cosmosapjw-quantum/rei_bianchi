# Native age32 analysis — v9

The new native return at Git HEAD `93aca4cc483080b802fa85c9c44e43b9c85db5b7` completes the previously READY age32 run. The original endpoint target0.005 fails: N relative difference0.8248861211419689 and U0.7916059535400799 against completed age64.

Read [the research update](../RESEARCH_UPDATE_20261020_NATIVE_AGE32_KO.md), [THEORY_KO.md](THEORY_KO.md), [IMPLEMENTATION.md](IMPLEMENTATION.md), [final ANALYSIS.json](results/attempt004/ANALYSIS.json), [R6](reviews/r6/R6_RECEIPT.json), and [C9](reviews/c9/C9_RECEIPT.json).

## Results and scope

- Exact stored photon history has33 verified state links, including the final endpoint, and exactly zero telescoping residual.
- Native survivor age moments and source/absorption differences use each population's own mass. Frozen all/sensitive/passive outputs remain separate.
- Constant-scalar midpoint/source-step formulas and exposure limits are implemented. Continuum root signs are independently Decimal150-checked.
- Source-event jump changes do not account for the endpoint photon residual; interval history includes several numerical contributions and is not a certified truncation/roundoff split.
- Native age/time remain HOLD, actual nonlinear Grackle response bound NOT_ESTABLISHED, PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED.

Authoritative output is attempt004. Attempts001–003 preserve earlier incomplete/uncorrected implementation outputs, including the initial floating root brackets; do not select them as current evidence.

## Reproduction

Use explicit paths with `run_bounded.py --data32 ... --data64 ... --out <new-empty-directory> --receipts <new-receipt-directory>`. Add `--postprocess-only` only when deliberately reproducing the analysis using already reviewed tests. Inputs and provider identities are in [RAW_INPUTS.json](RAW_INPUTS.json). The complete C10 snapshot contains the original native32 archive under `archive_only/native_age32/` and the existing age64 evidence in the task tree. The next assistant performs extraction automatically when needed.

No new native trajectory or v8/v7 campaign is needed to read or reproduce these stored-data results. The120s aggregate local scientific cap is enforced by the wrapper; existing receipts count toward it. Actual implementation wall is10.235522128990851s and separate independent C9 process wall0.562281198s.

## Review and delivery

R6 PASS_SCOPED(open0), C9 PASS_SCOPED(open0,3 concrete code findings closed). The implementation's reviewed source hashes are in the C9 receipt. Source publication and dual-provider archive identities are recorded in the parent CURRENT5/delivery receipts. R6 reviewed THEORY bytes must retain SHA256 `d390e40721113ba83b1e078a6ca290d9cb4e051946b2acd7882536639f1e484c`.
