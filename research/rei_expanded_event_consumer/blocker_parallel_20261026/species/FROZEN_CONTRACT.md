# Frozen species projection contract — 2026-10-26

Authority: Astra framing authority26 under root, physmath workflow1.0.0 and unchanged AGENTS blob429a5a13ee75b1222bc50627f8d5973d01dd21c4. Implementation: lower-tier implementation26. Review: independent review26. Unit: REI-WU-SPECIES-CONSUMER-PROJECTION-01.

## Actual canonical gates and ownership

- HE-EXP-SPECIES (lead WU088_HH, consumer BASS_HE): all7targets explicitly listed; unsupportedpair tagged INPUT_PENDING.
- REC-EXP-SPECIES (lead WU088_HH, consumer rec_bianchi): historical21 states reproduced exactly; extensions explicitly UNADMITTED and source-referenced; no silent isotope rate equality.

This unit supplies executable WU-to-consumer identity projections and support queries for those existing nodes. It must not close WU_ALL_TARGET_SPECIES_REACTION_REGISTRY, HE-EXCHANGE, HE-EXP-STOPPING, REC-EXP-SPECTRAL or parent L1/L4. WU remains the species/event authority. There is no rate/cross-section/mass/differential-provider admission.

Inputs are exact bytes listed in INPUT_MANIFEST.json. Their four Git blobs and SHA256 have been checked. Preserve copied inputs. No source retrieval, parser builder or old suite replay is needed during execution.

## Source interpretation

1. WU_SPECIES historical_view supplies exactly21 ordered label/species_id links and rows keyed by canonical WU IDs. Canonical compiler_record includes isotope composition (Z,A,isomer,count), charge, electronic state and electron/material pool.
2. Seven atomic isotope targets are H1=(1,1), D=(1,2), T=(1,3), He3=(2,3), He4=(2,4), Li6=(3,6), Li7=(3,7). Charges0..Z yield20 states; neutron(Z0,A1,q0) adds one material state. Neutron is separately named, not an eighth atomic target.
3. Expected WU historical ordered labels: n:0,H1:0,H1:1,D:0,D:1,T:0,T:1,He3:0,He3:1,He3:2,He4:0,He4:1,He4:2,Li6:0,Li6:1,Li6:2,Li6:3,Li7:0,Li7:1,Li7:2,Li7:3.
4. HE consumer registry supplies21 material identities, e_th/e_fast and9 synthetic extension witnesses. Its rec_population_crosswalk gives exact REC labels/indices. Bind the21 through isotope composition+charge+material pool and cross-check every index and label against REC_ATOMIC_MODEL.species_order. Require a bijection; reject missing/duplicate/unknown target or ambiguous composition. Canonical WU isotope/state remains authoritative.
5. **State semantics are not equal:** historical WU bound-charge records are population_aggregate_unresolved, fully stripped species/neutron bare_nucleus. HE's bookkeeping fixtures label ground. Retain both states with relation NUCLEUS_CHARGE_PROJECTION_ONLY; state_equivalence=false and physical_state_partition=null. Do not silently relabel aggregate as ground or evolve aggregate and resolved extensions together.
6. REC input declares Y_i=n_i/n_b, A·Y=1, thermal electron count n_b q·Y. REI endpoint declares x_i=n_i/n_ref. This implementation only reorders labels or caller data associated with the same explicitly supplied normalization; it must reject/decline automatic Y↔x normalization conversion. e_fast and e_th are distinct pools and neither is a material row. Never identify e_fast with REC's derived thermal electron count.
7. WU has92 canonical species identities;21 are historical,71 are nonhistorical source-state/particle/molecular extensions. Each extension output must retain canonical compiler_record, source_labels, qualification and immutable source reference to INPUT_MANIFEST WU commit/path plus JSON pointer /rows/<ID>. Mark extension consumer_admission=UNADMITTED, active=false, rate=null. SOURCE_EXPLICIT identity qualification is not consumer admission.
8. HE has no source-qualified full differential provider (summary value0; physical_provider_admitted=false). Expose a pair_support(left,right) query over the23 non-synthetic HE records, plus separate9 synthetic witnesses. Preserve original per-row differential_exchange_status and return INPUT_PENDING with rate=null for selected unsupported full joint-law pairs. Scalar PI/RR/CI provider IDs may be returned as candidate metadata, never as a joint-law or numeric rate. Synthetic pairs return UNADMITTED_SYNTHETIC_WITNESS and never a physical support value. Reject unknown IDs. There is no need to enumerate a large cross-product; query functionality plus selected targeted pairs is the useful deliverable.

## Implementation outputs and APIs

Implementation writes code/tests under implementation/ per root's explicit ownership assignment; outputs may be under species/ or the root-selected run directory. Do not modify species/inputs, INPUT_MANIFEST or this contract. This path clarification changes no scientific dependency or acceptance criterion.
- projection.py: load validated sources, construct historical21 projection and WU extension records, expose forward/reverse label/index reorder and pair_support. Pure stdlib, no NumPy/SciPy, no external services.
- SPECIES_PROJECTION.json: exact ordered21 rows with WU ID, nuclide, charge, source-native states, HE label, REC label/index, identity relation and source references;7target summary+neutron;71 UNADMITTED extensions; pool/normalization restrictions.
- test_projection.py or callable run_checks: narrow changed-contract controls, callable from root's combined bounded runner. Do not spawn own runner or execute on import.
- RESULTS.json and executor handoff after authorized combined execution only. Prior input inspection is not scientific result.

The reorder operation must preserve arbitrary supplied21 component values under forward+inverse permutation, retaining exact ints/rationals or caller data without floating arithmetic. Reject duplicate input labels; error rather than fill missing entries with zero. No abundance positivity or physical applicability is inferred from this label operation.

## Acceptance and negative controls

Integer/string/source identity comparisons exact; no tolerance is necessary. All of the following must pass:
1. Manifest byte identities, WU independent admission species hash and preserved qualification agree.
2. Seven isotope targets,20 atomic charge states+neutron exactly21, exact source labels and bijective REC index coverage0..20.
3. Source-label permutations round-trip exactly on distinct signed integer markers; charge/baryon count rows agree by explicit Z,A,q, with neutron separate.
4. WU/HE electronic-state differences are recorded and never asserted equivalent. Unknown state-identity requests require a partition map rather than being accepted by composition alone.
5. All71 nonhistorical WU IDs retain source qualifiers and immutable source-row reference, UNADMITTED,active=false,rate=null. Keep molecular constituents and isomer labels verbatim.
6. Selected pair queries cover H1/e_th,He4+/e_fast,Li6/e_th,T/e_fast plus a material-material pair; all full joint-law states INPUT_PENDING, rate=null. A scalar provider candidate cannot change that.
7. e_fast↔e_th substitution, changing n_b to n_ref without supplied density map, missing/duplicate labels, Li6→Li7 mutation, synthetic-extension physical admission and unknown source ID are rejected by the relevant API/validation.
8. Preserve original ElementalElectronicEquality policy as an explicit source model string; no copied rate or isotope equality is activated.

These are inventory/identity/projection gates already declared by the two canonical nodes, not empirical physical provider gates. Scientific admission and numerator change require independent reviewer approval of code+actual output.

## Execution and stopping

Root has reserved a **single combined stdlib validation across parallel lanes**, no more than0.15 CPU s, inside the previous source campaign's conservative remaining0.310169663 CPU s. This is not a new allocation or reset. Other wall/memory/command limits and cumulative accounting are root-owned; implementation must wait for the combined frozen command and run authorization. No standalone test process, profiling, broad suite or scientific runtime is authorized by this file. Return preparation to root first. On substantive mapping/source ambiguity, stop the affected projection and ask authority26/root; never invent a state equivalence, source or budget.

