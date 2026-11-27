# BASS_HE E13C7: local science complete, heavy parallel batch prepared

This is the complete execution package for
`HE_E13C7_PARALLEL_FINITE_REFINEMENT01` on the fixed captured OFF target.

Start with [REPORT_KO.md](REPORT_KO.md), [CURRENT_STATE.json](CURRENT_STATE.json),
and the [independent decision](review/INDEPENDENT_DECISION.json).
The [NCP handoff](NCP_HANDOFF_INTERNAL_KO.md) runs only the remaining **2,331
ordinary paths at N1024/P60**. Source data, full OFF prior path bytes, exact
budgets, unchanged kernels, all local outputs and review evidence are included.

All declared short science is complete:24path work items,56segment enclosures,
38,656coefficient evaluations. Local admission selects four N1024 and four
N512 paths.95exact-zero paths need no numerical work; six prior paths are reused.
Actual new heavy computation and64-rank scaling are **NOT_RUN**.

The execution lock is10,078bytes with SHA-256:

```text
c04cfde1838563d95389e499de9bcbe505a7d67f6bda1fff4476af953c8cc4f4
```

It pins60files, including all10runtime Python files, actual scientific input
closure, sealed work plan and selected local evidence. The earlier pilot lock
is preserved separately. Moving Git branches are not an execution identity.

The outer ZIP hash and cloud locators are supplied in the external user handoff
and delivery receipt. `PACKAGE_MANIFEST.json` enumerates every other payload
member with actual bytes/SHA. Verify the outer ZIP identity before fresh safe
extraction, then verify every manifest entry. Do not infer bytes from a download
filename or discard a returned suffix.

NCP collects durable path results and returns them. Exact global Fraction
reduction and final independent finite admission continue in ChatGPT after
return. Physical, continuum, production and receiver remain HOLD.

The Git publication is a compact review projection; large raw inputs and full
local evidence are archive-only. Use this complete ZIP for execution.

## This Git projection

This directory is a compact publication of the complete execution archive.
Runtime inputs such as OFF_OLD_PATHS.jsonl, original source CSV and WORK_PLAN.json,
plus full local raw output are archive-only. The complete archive identity and
verified Drive/Dropbox locators are in BACKUP_RECEIPT.json. Use the external
NCP handoff here to retrieve that archive; do not run this projection as a package.
The earlier README description of complete inputs refers to the ZIP root.
