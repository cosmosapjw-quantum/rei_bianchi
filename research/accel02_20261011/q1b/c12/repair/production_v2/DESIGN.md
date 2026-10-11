# Explicit source-failure resume lane

C2_FULL001 accepted generation39 remains authoritative. Its failed attempt42 remains a failed transaction; no journal files are rewritten or resolved by this lane. The new source identity begins a separate run whose first completed-controller attempt number is42 but whose physical attempt ordinal is43. This explicitly repeats an uncompleted interval with a different source implementation, never a completed accepted trajectory.

The failed exception consumed one runtime attempt. The controller invariant attempts=accepted+rejected is preserved with cursor41/39/2. The externally debited failure reduces the remaining cap105→104 completed attempts; remaining budget is63, macrocap103 unchanged. Numerical controls, scales, end time, hard events, physical state and all original criteria are unchanged.

prepare_failure_transition(repo,output_root,extra_dependency_paths=()) verifies exact parent manifest,53-dependency closure, failedbegin/failure/request/zero-native-result, then writes a new generation39 child. All9arrays and all physical metadata including full79-stateprefix, kernels and cumulative outputrecords remain exact. Its sourceidentity points explicitly to source_candidate/source_precision_v2.py; the oldsource and53 dependencies remain pinned. Source-candidate physics/arithmetic acceptance is an independent root/reviewer decision.

The migration copies original output0 and its BEGIN/DONE receipt exactly. No h0/source/native diagnostic is recomputed. The versioned driver requires this migrated receipt and contains no initialh0 execution branch. Later outputs use the new source API and retain current checkpoint/journal/24-field provenance rules.

Only three new cheap migration cases were run: actualsaved-array preservation with mutation rejection; correctfailedattemptdebit withoutcursorchange; exactoutputreceipt reuse and mismatch rejection. No operational child, source integration, native maps or old tests were executed by this owner.

After root review/materialization:

```bash
python -u research/accel02_20261011/q1b/c12/repair/production_v2/run_full_history_chunk_v2.py --transition-bundle research/accel02_20261011/q1b/c12/evidence/C2_FULL002/TRANSITION_RESULT.json --run-directory research/accel02_20261011/q1b/c12/evidence/C2_FULL002/RUN --new-attempt-cap 3 --wall-s 45
```

The C2_FULL002 name is a proposed root-owned destination. No preparation/launch has occurred here.
