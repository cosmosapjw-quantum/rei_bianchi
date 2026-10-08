# Independent scoped diff/source review — 2026-10-08

Reviewer: separate Codex review agent; implementation not edited by reviewer. One review round, one permitted targeted repair closeout. Scope: followup adapter/replay, BASS/REC schema fixtures, unchanged PR87/PR88 dependencies; no native science or campaign execution.

## Finding requiring targeted repair

**R1, P2, current C1 blocker:** `adapter.py:readout` delegates packet metadata validation to unchanged PR88 `packet.check`, which validates context, six moments, family kind and absent generators but does not bind original `schema` or `family_id`. The followup then returns a new typed family identity without preserving the original producer family label. Probe: load the actual public packet, set `family_id='wrong-family'`, call `readout`; observed `PASS_CONDITIONAL_OBSERVED_POINT_ONLY`, typed ID `observed-fixed-binary64-point:1623af1f...`, no original producer family ID field. Consequence: source/moment numerical identity remains valid, but the requested family metadata identity can silently change. This is a metadata preservation/refusal defect, not scientific-integrity failure or evidence of invalid six moments. Minimal repair: validate the pinned producer schema and family ID in the new wrapper, preserve original schema/family metadata separately from the typed zero-generator point ID, add one focused mutation regression. Do not alter imported PR88 bytes or create another provenance layer.

Repair closeout: **PASS_SCOPED_SOURCE_AND_STORED_POINT_ONLY**; R1 closed by the single targeted repair below.

## Verification performed

- Read scientific contract, validation matrix, wrapper/replay/tests, consumer schema/tests, unchanged packet checker and typed adapter, native observer source, actual exported packet, accounting and previous output receipts.
- Independent preservation probe: all **143** imported PR88 file bytes equal `git show origin/research/igm-rate-export01-20261008:<path>` and recorded SHA256 values; zero failures. `git diff --exit-code 17f43b84ee49bada32d6efe84c3377e7d645f230 -- research/igm_handoff_20261008` exit **0**.
- `python3 research/igm_rate_export01_20261008/reproduce.py --output /tmp/igm-independent-review-20261008` exit **0**: 6 adapter tests, 7 consumer tests, 2440 stored rows, six ordered binary64 reductions match, previous typed output exact parity. Primary profile/audit: one conditional receiver, one project, zero observe/cross_section/spectral_moments/RHS/advance/native child calls. Tests are separate pure Python children before audit; review made no provider/observer/history calls.
- R1 probe was run in a short inline Python process, exit **0**; the accepted mutation output above is the retained first finding.

## Correctness and claim boundary

Actual PR88 moment producer uses the same node/species/provider sigma and term for Gamma and incident Ecal, with Ecal equal to term times the same incident eV. It does not derive rates from integrated A/B, opacity or nonphoto RHS zeros. Context binds exact binary64 gas/photon ln(a), h/y/z/w, reconstructed background proper nH/nHe/H, constants, provider source, binding thresholds separately from provider support cutoffs, grid and accepted committed-2 source/build. Receiver converts floats to exact rational point values; zero generators enclose that observed rounded point only. Source/provider/gas/epoch expectations are refused through the actual typed receiver. Missing Gamma/Ecal returns MISSING_INSTANTANEOUS_JOINT_MOMENTS with producer fields and forbidden substitutes.

BASS formula is dimensionally c[m/s]*sigma[m2]*ne[m-3]*D → normal-time s-1, density conversion 10^6 once, D once; no new time mapping or optical integration. Explicit constants authority handles distinct historical Thomson values. REC enforces nuclei denominators, exact electrons, positive gas/radiation temperatures and independent radiation authority/model. Both accept synthetic schema fixtures only and reject actual-history admission. They do not generate histories from one endpoint.

This is source review and stored-point reproducibility evidence, **not physical admission**. Provider and continuum errors remain UNKNOWN; physical/full-Wide/coupled-history HOLD. Background is the explicitly labeled pinned recipe reconstruction, not separately saved original endpoint background. Zero-width typed output is not an enclosure of the exact finite spectral sum or continuum. Actual BASS history/frame/tail and REC radiation/matched initial-state payloads remain NOT_PROVIDED. Native exporter science and historical all-attempts costs are inherited PR88 evidence; they were not rerun or reset. PR85 log-tail and PR86 canonical Wide authorities remain separate. No reservation-owner computation was duplicated.

After R1 targeted closeout, no other current-task blocking defect identified within this finite scope. The review does not inspect arbitrary new producer families, consumer solvers or authoritative histories.

## Single targeted repair closeout

Inspected the new-wrapper-only repair and regression. `readout` now refuses a substituted/missing original producer schema or family ID with `PINNED_PRODUCER_SCHEMA_FAMILY_ID_REQUIRED`. It returns unchanged producer schema, family ID/kind, null generator metadata, uncertainty widths, units, context ID and observation ID under `producer_moment_identity`, separate from the PR87 typed observed-point identity. No imported PR88 code was edited.

Reviewer commands: `python3 -m unittest discover -s research/igm_rate_export01_20261008/tests -v` exit **0**, **7/7**. Inline focused probe loads the actual public packet, checks returned original metadata, then substitutes each of schema/family_id; both refused with the expected typed reason, process exit **0**. Repair replay receipt `/tmp/igm-rate-export-followup-repair-20261008/RESULTS.json` reports 7 adapter + 7 consumer tests exit0, six bit matches and typed parity, zero observer/provider/RHS/history/native calls; reviewer inspected that receipt. Recorded imported PR88 SHA values were rechecked after repair, **143/143 unchanged**.

Final decision: **PASS_SCOPED_SOURCE_AND_STORED_POINT_ONLY**. No unresolved current C1/C2 source-review blocker. Physical admission, continuum/provider uncertainty, authoritative history/consumer data remain exactly the HOLD/UNKNOWN/NOT_PROVIDED boundaries above. Review loop stops here; no additional optional review surfaces or native computation requested.
