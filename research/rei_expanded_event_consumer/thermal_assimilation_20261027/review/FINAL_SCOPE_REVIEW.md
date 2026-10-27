# Final scientific scope and DAG preservation review

Date: 2026-10-27. Reviewer: `/root/normalization_review`.

**Decision: `PASS_FINAL_SCIENTIFIC_SCOPE_AND_DAG_PRESERVATION`. Remaining blocking findings: 0.** The report, admission and requested stage records preserve the closed C9 result: a conditional local native thermal source and one frozen directional derivative. They do not promote the selected relaxation rate to a qualified physical stopping law. `REC-COUPLED` remains partial, original completion delta is 0, working count is 32/88, central count is 27/88, L4 is false and global physical completion is null.

## Review scope and identities

The reviewer read `REPORT_KO.md`, `ADMISSION.json`, stages R7–R10/C9/C10, `STAGE_LEDGER.json`, `DAG_UPDATE_RECEIPT.json`, the actual DAG/current view and four selected contract wrappers. Direct saved-data comparisons used the working baseline at `ee94bef85b56d879dc38f184856a5c613575e9e1` and the incoming central originals at `12f6007a83a40d76f80574e41a5402676e81fc7a`. The DAG metadata author was `/root/supplier_intake`; this reviewer performed its own comparison rather than using the root's comparison receipt as proof.

Closed source, numerical and visual C9 reviews were reused. No scientific import, source evaluation, FD, solver, provider replay or render was performed. No implementation file or DAG was edited by this reviewer. Full hash bindings and individual preservation checks are in `FINAL_SCOPE_REVIEW.json`.

| Reviewed artifact | SHA256 |
|---|---|
| Final scientific `REPORT_KO.md` wording | `b17b898f8ff7d535beecc5788ca16697eb6b7032458bea14743db55b11191699` |
| `ADMISSION.json` | `cf85a4828296bd1600cb6c854331fdf1ec5ca02bd0c413847b9b6876a9b31b26` |
| Stage ledger at this review | `939091b884ed8d0c25e08c96e1927142bdcacfd58951cdccbda4e5d232c5524a` |
| Actual `orchestration_expansion_20261025/DAG.json` | `031e078a6dc3478bb87479093aaf2742582d4d1df040651770ece41d05fad5c4` |
| Actual `status/CURRENT_STATUS.json` | `77728e2fd64e4cc89f3fbce47a20aa5ff5667496ade29f3643102dc7d256f36b` |

## Two documentation findings resolved

The initial report wrote the alternative reference as `dot r=Rr` while the adopted derivation and source convention use continuity production. Root corrected the report and admission to **`dot r+3Hr=Rr`**, **`dot n+3Hn=S`**, and **`x=n/r`**, explicitly explaining the common dilution cancellation and **Rr=0 for the fixed comoving reference**. The existing quotient and full differential remain unchanged. This closes the normalization-definition finding without any code change or rerun.

The admission initially named `[0,23]` as `density_like_rows`, which could be read as two row IDs. Root renamed the field to **`density_like_row_range_inclusive:[0,23]`** and retained logT row 24 separately. The machine-readable scope now agrees unambiguously with the report and the reviewed first-24-row maps.

## Scientific scope, signs and ownership

The approved decision, 118 checks, residual maxima and scientific code/checker identities agree between admission and C9. The report retains the actual saved background versus manufactured fast-pool distinction, independent conditional nu, native coefficient domains and model qualifications, and the selected Planck reference. Source/JVP equations preserve the common thermal-electron subset and the particle-count contribution to the caloric equation.

Photo primary energy enters the fast reservoir once; assimilation transfers fast number and energy together to the bath. RR/DR kinetic cooling, binding changes and escaping radiation retain their named partners, while the external radiation-transfer ledger remains distinct from an independently evolved radiation energy density. The report's numerical power signs and values agree with the already approved saved output. The general-reference control is not presented as an additional expansion/pressure-work or Bianchi trajectory calculation. One local direction is not relabeled a full Jacobian or a new V6 certificate.

## Direct DAG preservation result

All **88 IDs and their order**, all **17 integration edges**, and all non-node top-level data are unchanged. The latter include authorities, historical scope, dependency interpretation and the global gates. **84 nodes are exactly unchanged.** Every original nested contract, dependency, conditional dependency, external prerequisite, claim gate, PR plan, budget, execution guard, selected runtime contract and original source pointer remains equal, including key presence.

Only the following four wrappers change:

| Node | Scoped change |
|---|---|
| `REC-COUPLED` | Current partial observation plus separate `thermalAssimilationContract`; original photo observation is preserved exactly in `prior_observation`. |
| `B3g-actual-cohort-binding` | Incoming central partial reconstructed-transport observation and next action. |
| `B3i-calibrated-geometry` | Incoming central saved-model geometry observation; physical calibration remains open. |
| `B2-G1C-error-transport` | Incoming central finite reconstruction-bound observation; physical/continuous bounds remain open. |

All four contract files equal their DAG nodes. The three BASS nodes equal the exact central nodes, and their wrapper and plan bytes equal the central originals. The current-status view changes only the same four rows; its other 84 rows are exactly unchanged. REC's current observation equals its DAG observation directly. BASS current observations intentionally store the DAG wrapper's `value` payload; those payloads match and the three whole current-view rows exactly equal the central originals. The schema difference is not a scope inconsistency.

The previous five working finite admissions remain unchanged. The 20 R/C stage entries all record working 32/88, central 27/88 and original-node delta 0. Completing scoped loop stages is consistently distinguished from completing original network gates.

## Late CR owner result remains separate

The final report correctly incorporates the bounded CR observation at `1c88ba4b0f258c6ce83bcb197e4e2c3446915bbb`. `FINAL_CR_DELTA.json/md` and selected exact original contract/result/preparation records were read. The producer has 16/20 loop stages and 36/36 C6 controls; its actual-source primary 224 RHS and C9 admission remain pending at this boundary. This review does not independently rerun or certify that producer's numerical work.

The source-qualified capture hazard lambda(E) is distinct from irreversible thermal assimilation nu. The selected event reduces ion charge and fast-electron count together, leaves thermal count and selected thermal heat unchanged, and owns its retained photon in a separate integrated port rather than native w_ext. Its actual exports have null nb, exposure, event rate and instantaneous RHS. The separate T=10000 K producer is not assigned the REI saved donor's temperature/density. Consequently this return does not qualify the REI physical nu, alter the frozen code or add an original completion. Its observed **0.701900185/30 CPU s** is an owner-unit ledger and is not transferred into REI's allowance.

## Delivery boundary and review cost

The explicitly pending final publication/delivery links are not scientific blockers. Final ACK, budget and handoff assembly remains root-owned; this review does not self-certify a future commit, archive or upload. Subsequent actual publication/ACK metadata can resolve those pending references without changing the reviewed scientific claim.

The three measured metadata phases used **0.210295974 process CPU seconds before serialization**, separately from prior C9 numerical/visual review metadata and the owners' edits or execution. Individual phases are in `FINAL_SCOPE_REVIEW.json`. Unmeasured tool, initialization and serialization tail costs remain `UNKNOWN_NOT_ZERO`.
