# Proposed bounded DAG update — CR integrated diagnostic consumer

Status: **PROPOSED_ONLY; root applies after actual C9 acceptance**. This file does not modify the working DAG or declare a completed scientific result.

## Fixed inputs

- Working scientific/delivery baseline: `ee6746ab172f862dddfdec63b59e5e3707b59eaa`, original declared working progress **32/88**.
- Previous central: `12f6007a83a40d76f80574e41a5402676e81fc7a`.
- Fixed central CR owner return: `5abe0d19df95db730e3e33bae0373c81ba37ce89`, declared central progress **27/88**, one commit ahead/zero behind and exactly five changed paths.
- Exact central source files are in `intake/central/`; `intake/SUPPLIER_COPY_CENTRAL_RECEIPT.json` records five actual local Git blob matches and the comparison with the recovered working DAG.
- Central source S/D: `4e72c89b714431eb4c6ae07def777bbf72a5ae4c` / `ec463db0c7e5c7fb5070796071c926caa4db6445`.

The actual semantic comparison found 88 nodes in the same order, 17 integration edges on each side and no differing top-level field outside `nodes`. Seven node wrappers differ: CR_N5's new owner-return pointer; the five prior finite completed working admissions; and REC-COUPLED's prior working runtime/thermal observations. This is the reason to apply only the CR delta to the working DAG.

## 1. Incorporate the exact central CR owner delta

Use `research/orchestration_expansion_20261025/` as the destination prefix. Preserve the working DAG as the base.

1. In `DAG.json`, node `CR_N5_ATOMIC_ISOTOPE_COVERAGE`, add the central `owner_return_heiii_20261027` object exactly. Its existing `current_status`, dependencies, native source contract, `pr_plan` and all other fields stay as they are.
2. Apply the same single added `owner_return_heiii_20261027` object in `contracts/CR_N5_ATOMIC_ISOTOPE_COVERAGE.json`. If the pre-existing wrapper is identical to the central predecessor, its exact new central file can be copied.
3. Append the exact central HeIII owner-return section to `node_plans/CR_N5_ATOMIC_ISOTOPE_COVERAGE.md`, retaining the preceding source-derived plan. The already fetched central file is the reference.
4. Add `returns/CR_HEIII_GROUND_RR_20261027.json` as the exact central bytes (Git blob `8ecaa3d4823cabc4731b7d4c61ddff93c7f086dc`). This is the supplier owner return, not a new REI scientific decision.
5. In `status/CURRENT_STATUS.json`, copy only the central CR_N5 row's `observation` object. Its parent status remains partial. Preserve every other working status row, especially the five finite admissions giving32/88 and the previous REC-COUPLED thermal source result.

The original central delta does not mark CR_N5 complete. It adds one scoped child result while N4/N5 remain PARTIAL_OPEN and N6/N7 remain PREDECESSOR_GATED. Its original88 count effect is0.

## 2. Record the new REI consumer only after C9

If the frozen integrated-diagnostic consumer passes its actual changed-code, numerical and independent criteria, add a separate observation/contract pointer to `REC-COUPLED`. A candidate field name is `crIntegratedReturnContract`; root chooses the final schema in the actual admission. Bind exact local code/input identities, raw result path, independent decision and source science S.

The new observation must distinguish:

- Actual CR integrated per-proper-volume event count/energy and fixed source qualification.
- A diagnostic normalization/JVP with an explicitly supplied reference density, versus missing physical recipient n_b.
- The separate retained-photon count/energy port and unchanged external-transfer ledger.
- Species charge minus fast-electron count conservation and zero selected thermal count/heat for this capture event.
- Existing native25 state/time conventions and unchanged physical-rate/history gates.
- The 24 producer case/source alternatives, with a selected scenario or separate records rather than an additive population/time series.

Keep `selectedRuntimeContract` and `thermalAssimilationContract` exactly intact. Do not replace the existing photo/thermal `status_observation` without retaining it as a named prior observation. A new consumer return can be added under `returns/`, with corresponding additive text in the REC-COUPLED wrapper/node plan. The current parent remains constructive partial; the root's actual C9 result determines the scoped wording.

Do not infer event rate from integrated count, conditional mean capture time as exposure, a monoenergetic spectrum from mean energy, CR bath/REI donor identity, or physical nu from the RR capture hazard. Actual producer n_b/rate/exposure/instantaneous RHS/emission history remain null. A finite coupled composition update is not supplied by these integrated exports.

## Preservation and acceptance for the metadata delta

After the authorized root edit, compare the actual bounded changed objects once: retain all88 original IDs/order, all17 integration edges, every non-node top-level value, all untouched node objects/status rows, nested contracts, dependencies, conditional arrays, pr_plan, owner budgets and source identities. Check the new CR owner object and return against the exact fetched central bytes. Check only the new REC consumer pointers against the final local admission and independent review. This is metadata verification; no science replay is required.

Working declared progress remains **32/88**, central declared progress **27/88**, this new child's original88 effect **0**. Literal COMPLETE-prefix18/88 in the central return is a separate classification; it does not rewrite either declared scoped count. L4 remains false and global physical completion/error bounds remain null.

## Supplemental parallel return

The selected VigilODE Git expansion HEAD remained `72836e0290b66d33f4ca1771284b1c8070669a74` during this supplier Git survey. Root separately found a new V8 archive and a domain-only delivery JSON recording650 assertions. That root intake is a supplemental non-Git source, currently pending exact independent binding in this proposal. Unchanged Git cannot be used to claim absence of V8 work. V8's actual scope must be taken from its bound artifacts, independently of the closed V6 lease and this CR diagnostic consumer.

## Current actions performed

Only source reading, exact local intake copying, remote source-backup metadata queries and this proposal were performed. The actual root DAG and status files are unmodified by this subtask. No provider run, numerical test, IVP, push, upload or budget transfer occurred. Publication and acceptance remain root-owned.
