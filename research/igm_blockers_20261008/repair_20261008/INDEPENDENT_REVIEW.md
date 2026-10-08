# Independent review: paired density / heat / checkpoint repair

Verdict on the diff as first read in this review: **CHANGES REQUIRED for the direct-photoheat bound; scoped exploratory accepted states may be preserved. Full paired transport/error admission remains HOLD.** One read-only review pass; no new evolution, arithmetic probe, provider, observer, or test invocation. Root edits made in response during this review are not silently counted as a second reviewed revision.

Paths below are under `research/igm_blockers_20261008/numeric/`.

## Findings

### R1 — High, direct heat's claimed coefficient bound is not justified at cancellation (new local repair required)

`source/rei-next-nodes/short-hhe-midpoint/src/canonical_owner.rs:154–193`, especially the claim at 186–190; consumed by `material.rs:100–107`.

The implementation forms `mean_ev=energy_base_ev/count_base`, then `excess_ev=mean_ev-CHI[i]`, and assigns eight `rounding(coefficient.value)` charges to `EPS*excess_ev`. This uses the **small result's** scale to bound rounding already introduced at the **mean energy's** scale. A positive threshold gap does not remove this conditioning factor. Near the HI cutoff, mean/physical excess can differ by thousands, so a fixed eight result-ULP charge is not a general enclosure of the division/subtraction chain. `count_base` and `energy_base_ev` are also formed as bare f64 before tracking; these can themselves be subnormal and have much worse relative errors. Six final-coefficient charges for `energy_coefficient` do not enclose those inputs either.

`photoheat_owner` relies on `heat.value > heat.loss` to authorize its fallback. Consequently this is more than an unmeasured continuum-model error: the newly claimed local arithmetic/sign bound is missing necessary terms. It does not prove the observed k16 scalar result is physically wrong, but the bound must not be presented as validated.

Minimal correction: propagate an interval or magnitude bound from count/energy-base construction through division and subtraction, charge errors at each operand's scale, and only then multiply by EPS/absorbed count. Alternatively mark the fallback as exploratory with unresolved sign/error authority until such a bound exists. Keep the stored k16 evidence; do not erase failed attempts. A focused saved-operand regression is sufficient for this correction; no broad campaign is called for.

### R2 — High for full paired-loss admission, known remaining transport scope: checkpointed node uncertainty is not consumed by the next characteristic

`source/rei-next-nodes/short-hhe-midpoint/src/radiation.rs:274,314` and `canonical_owner.rs:89–133,210–217`.

`Density` now stores a `PhotonNode { number, energy }`, and gamma reads it, but both transaction functions invoke the characteristic with `old[j]`, the scalar number only. The characteristic/kernel never receives the old canonical number value or either inherited loss. The next node is re-created from new kernel output. Thus persistence/observer support does not yet implement transported canonical values and uncertainties across an advance. The same issue exists across internal segment boundaries, where `stock=o.n` is the next input.

This omission exists before N becomes scalar zero: any nonzero inherited uncertainty is dropped. When scalar N eventually becomes zero the current guard correctly refuses, as witnessed by k17. Do not describe this implementation as full paired transport or cumulative loss closure. Scope the PASS to paired storage/readout and observed scalar advances. The documented next blocker must include loss propagation while N is still representable, not solely convolution after N becomes zero.

Minimal eventual repair: pass the canonical input pair/loss into the characteristic flow, transport inherited uncertainty by the positive segment coefficient, add newly incurred arithmetic uncertainty once, and persist that output. This is a follow-up implementation boundary rather than justification for repeating completed campaigns now.

### R3 — Medium, non-active accepted-record replay remains inconsistent with canonical restoration

`source/rei-next-nodes/short-hhe-midpoint/src/record.rs:63–67`.

Replay zeroes the segment N/U canonical components before summing. It later restores only scalar `sum.n`/`sum.u` (and scalar-derived logs), then asks `owner_ledger(sum)` to compare to a node with nonzero occurrences **before** replacing `sum.canonical` with the stored node ledger. This can still produce `canonical owner/readout mismatch` for ordinary nonempty recorded nodes, while zero-projected U can also create `ln(0)`. The transport implementation separately restores `last_pair`; replay does not reproduce that step.

This is not the running progressive driver's k17 blocker because recording is disabled. It limits the broader V1–V3 accepted-record API compatibility claim. Restore/replay the actual final segment pair and its logs before comparison, or explicitly exclude that API from this repair's accepted scope. No fresh replay was run in this review.

## Checkpoint and accounting observations

- V3 serializes per-node tracked N/E, active loss, 13 owner terms, and the new heat ledger. Explicit V1 and V2 readers exist. The V3 write path roundtrips and compares state bytes before replacing HEAD.
- V1 migration reconstructs energy from stored N and current node/epoch geometry rather than recovering historically measured energy uncertainty. Its legacy/historical-error limitation must remain explicit. `pair_legacy_density` also computes its new energy coefficient/product without a fresh rounding charge; this belongs in R2's unclosed uncertainty scope.
- No evidence was found that the examined V3 serializer drops its newly added heat ledger. The old 13-term trailer preserves heat from the main state record.
- The current thermal residual adds A/B-owner uncertainty to the direct heat bound even if the fallback is selected. Some shared input uncertainty may therefore be conservatively counted through both paths. This does not create a false PASS, and the reviewed diff does not document a unique decomposition that would support a no-double-count claim. Resolve the bound authority once when R1 is fixed rather than subtracting arbitrary terms.

## Existing execution evidence and claim ceiling

- `repair-coarse-suffix-v3f.log` records accepted k15, observer sigma 9624, original gates `[0.6463509202763655,0.0013558191017777456,0.0074689617368987465]`.
- `repair-coarse-suffix-v3i.log` records accepted k16, observer sigma 9624, gates `[0.6485470105119698,0.0015511531159999056,0.007448008134352242]`.
- `repair_20261008/runs/coarse-suffix-v3i/FAILURE_17.json` preserves the actual next failure: finite `lnN=-748.5203313766382`, `lnU=-773.0631346468055`, scalar N/U zero, `authoritative tail is not empty`, last_step 16, attempted_step 17, counts `[4,3,1]`, `state_unchanged=true`. This is appropriate fail-closed behavior; no silent tail deletion is evident.
- `comparison_14.json` explicitly limits its PASS to the common k14/28/14 epoch. That does not certify k15/k16 temporal/tail refinement or the whole suffix.
- The TASK_RETURN read during review retains full-z12→10 and continuum NOT_REACHED and physical HOLD. These ceilings are appropriate. Rename/qualify `PAIRED_PATH_AND_K16_PASS` and `paired_common_and_k16=PASS_SCOPED` if they could be read as admission of the currently unclosed R1/R2 bounds; runner acceptance and error enclosure are different evidence.

Review performed only with `git status`, `git diff`, source reads and existing logs/JSON. Several exploratory source/log variants are retained and should remain historical. No repository file was modified by this reviewer; only this `/tmp` review artifact was written. This pass ends here.

## Targeted correction verification within this review (one repair response)

The root implemented a targeted response to R1. I read only the changed coefficient-bound block and the existing `repair-coarse-review-fix-v3j.log`; no new computation was run by this reviewer.

- The coefficient now additionally includes `64 * rounding(mean_ev) * EPS` before the excess-scale operation charges. This corrects the specific mistake of bounding division/subtraction only at the small excess scale **when the stored count_base and energy_base_ev are treated as the given rounded inputs**.
- The comments now explicitly limit this to representation arithmetic and leave wider kernel/provider authority unresolved. Formation error of count_base/energy_base_ev, including their subnormal rounding and incoming-state uncertainty, remains outside this local bound. The 64-ULP allowance does not certify those earlier operations. This is the already documented upstream scope, not a request for another expanded review cycle.
- The existing rerun log records k15→k16 accepted at the same displayed three gate maxima, exit reported successful by the root. It records one new advance, provider/observer/RHS costs, and physical HOLD. The earlier k17 failure artifact remains untouched.

**Final disposition:** the specific local R1 scale error is corrected for the declared rounded-input arithmetic scope. Accept publication as a scoped exploratory paired-storage/observer/restart and k16 execution result, with R2 (full transported value/loss handoff), upstream kernel enclosure, R3 (inactive accepted-record replay compatibility), and full evolution/continuum admission remaining HOLD. Do not describe this correction as a full kernel or cumulative representation-error proof. One review plus this one targeted correction verification is complete.
