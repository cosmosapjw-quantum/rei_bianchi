# Independent review of the long-term plan assembly

Date: 2026-10-23. Reviewer: numerics_survey agent, assigned independently to the atomic, thermal and REI author contracts and global assembly. My BASS/VigilODE scientific contracts are excluded from this independent scientific review; their review belongs to the REI reviewer. This review checks the plan's source fidelity, executable next actions, dependency/ownership visibility and claim accounting. It does not approve future physics, execute campaigns or replace leaf-source reviews.

**Verdict: PASS_SCOPED for additive plan publication after the single renderer correction below.** Future nodes remain proposed and input-dependent as authored. Publication is not production activation or scientific completion.

## Inputs actually read

- `atomic/LONGTERM_CONTRACTS.json`: all12 WU088_HH/BASS_CR contracts, ownership restrictions, unknown budget fields and selected-unit statement.
- `thermal/BASS_HE_LONGTERM_CONTRACTS.json`: all6 nodes and protected holds.
- `thermal/rec_bianchi_LONGTERM_CONTRACTS.json`: all5 nodes, active LINE02 reservation and C3 cumulative debit.
- `rei/CONTRACTS.json`: all6 nodes, conditional dependencies, ANGTHERM02 reservation and historical budgets.
- `assembly/DAG.json`, `authorities.json`, `PR_PLANS_KO.md`, REI handoff and source coverage. Read-only fidelity comparison found6 embedded author documents equal to their source JSON and SHA256,39 unique node IDs and no missing local dependency IDs. Reviewed DAG SHA256: `fdbc1816e5d0782eb17f21f8517dfb91b0cd25bdf5166460df0e7f3552052a5c`.

## One finding and its closure

**G1 — prerequisite/owner visibility in compact views.** The initial PR table displayed “no prerequisites” for REI-L0/L2/L3 despite mandatory external providers. REI-L4 conditional dependencies and the document-level ANGTHERM02 reservation were preserved in the raw contract but not exposed in the compact scheduling view. A reader using that view could begin work before consulting the owner/provider requirements.

Requested minimal correction: display external and condition-tagged dependencies alongside internal dependencies; carry author-level reservations and historical-budget policy into handoff preambles. Do not turn conditional prerequisites into unconditional blockers, and do not rewrite scientific contracts.

Assembler applied the correction. Readback confirms the REI handoff preamble contains `external:ANGTHERM02_OWNER_ADMISSION`, its active owner branch/head, read-only reuse/no repair/no execution restriction, and historical budgets. PR tables now display internal/external/conditional dependencies. REI-L4 retains three separately conditioned obligations: nonzero n/T→L2, anisotropic baryons→L3, and an ANGTHERM02 accuracy claim→owner admission. **G1 closed.**

## Scientific and scheduling checks

1. **Owner reservations preserved.** WU PHYS83 is owner completion/intake rather than duplicate execution. REC-LINE02 retains the already consumed primary run and asks the owner to finish remaining review/delivery. ANGTHERM02 is reserved for its active owner; the central plan grants zero new cases. These reservations are neither reset nor overridden by a proposed-node status.
2. **Positive next actions are explicit.** HE-X1 PASS permits progression to source/frame/event-correlation checks; HE-ANG can replace the angular model only after source admission. REC-C3 admits exact saved-diagnostic primitive sharing before paired timing. CR cutoff binding proceeds as a source-to-existing-theorem connector, with stopping physics a separate next node. REI-L0 constructs exact balanced source columns; L1 binds a qualified provider pair. These are useful bounded actions, not indefinite re-audits.
3. **Scope remains conditional where needed.** The necessary moment cone is distinct from empirical differential-source calibration and full event realizability. Same-event energy/charge/particle ownership is required for atomic and beta integration. Planck bath/actual spectrum and total species stress/injection rate remain distinct. REI-L4's isotropic zero-n/T route is available without requiring optional L2/L3 branches; nonzero or anisotropic claims acquire their respective prerequisites.
4. **Budgets are cumulative.** Atomic unknown debit is not zero. REC-C3 retains600s cap,81.3665s recorded spend and518.6335s upper remainder subject to later receipts. REC-LINE02's180s primary allocation is already consumed. HE-X1's small fresh algebra allowance does not replenish HE38. REI completed ANGTHERM01 allowance is nontransferable; D10 unknown initial debit remains unknown. Future unfrozen limits do not authorize a numerical campaign.
5. **Status axes remain separate.** Global DAG scope states mechanical provenance assembly with no implied execution or admission. `plan_status=PROPOSED` does not overwrite author scientific status. Saved194checks, old129T/394 cases and completed donor cohorts are reused historical evidence, not fresh plan executions. The current X1 execution may be reported only through its own actual result/review records; central publication cannot complete future nodes.
6. **Coverage limits are honest.** Source coverage separates enumerated metadata, selected file reads and scientific admission; incomplete Drive coverage and unavailable conversation/runtime evidence remain explicit. Exhaustive branch-name enumeration does not imply reading every branch's science.

## Publication boundary

The reviewed plans may be published additively with their source contracts, handoffs and this receipt. Any subsequently added author-approved cross-repository alias or edge belongs to its own source/fidelity delta; this review does not certify unseen additions. Existing explicit external prerequisites remain binding until the named provider delivers its source-qualified artifact. No extra scientific gate, campaign replay or recursive review cycle is requested by this review.

Author delta checked within this review: HE-EXCHANGE now explicitly reuses the completed HE35 supplied-kappa pseudo-Maxwell finite-mass pair and its scoped oracle/conservation/C–Python5e-13 evidence. Empirical kappa/source uncertainty remains open. The change removes duplicate derivation without granting physical transport admission. All six embedded author documents and their hashes still match after assembly.

Final cross-repository delta read: all7 embedded author documents/hash identities match after adding rei/INTEGRATION_EDGES.json;17 author-authorized integration edges retain explicit conditions and claim limits. The source-provider list is a menu for selected channels; required dependencies are AND within the selected model. Isotropic/zero-n/T and validated alternative solver routes remain available. LINE02 owner delivery and single beta ownership are retained. This closes the cross-repository visibility portion of G1 without new physics admission. Scientific content of numerics leaf kernels remains excluded from this review; only their conditional consumer-interface mapping is reviewed here.

## Final REC129 / REC-HISTORY delta review

This final review is confined to the refreshed REC contract and its rendered assembly. Thermal authority reports current PR129 source `a7c46fd8338971e2cefa776f5dd7b25a46974990`, with its scoped science/review complete and final delivery receipt pending. This review does not reexecute or independently recount those scientific checks.

Readback of the40-node assembly confirms exact author-contract equality for REC-LINE02, REC-HISTORY and REC-COUPLED. LINE02's central plan status is `OWNER_DELIVERY_PENDING`, preserving the separate author science-complete-scoped status. REC-HISTORY remains `selected_next_not_run` in its contract and `PROPOSED` in the plan; it depends on REC-LINE02. REC-COUPLED now depends on REC-LI, REC-FIELD and REC-HISTORY. The PR table and REC handoff both expose the new history node and pending delivery distinction.

The new history gate requires actual native boundary/interpolation ownership, exclusive causal photon number/energy bookkeeping, and separately calibrated finite history/interpolation error. It does not promote the frozen LINE02 JVP into a full history derivative. Its positive next step is read-only source/theory binding, followed by a frozen bounded finite-case contract; no prior primary/review allowance is replenished and no new IVP is authorized. Existing17 cross-repository conditional edges are unchanged and do not acquire a new science-complete status.

**Delta verdict: PASS_SCOPED; no finding.** Final reviewed assembly SHA256: `bdddc18f700a23dbcc429100111866ee3a88cf35b9e33eef387acba3434dabe6`. This final identity supersedes the earlier39-node identity solely for this documented REC delta; all earlier bounded review exclusions remain.
