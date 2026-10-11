# Whole-history continuation from PILOT02 generation 3

Status: **DESIGN_ONLY; production implementation and launch not admitted by this file.** The independent local verdict can admit the tested r=0 map/controller/cold restart; it cannot supply the missing whole-history driver or its output evidence.

## Scientific target and exact reuse

Continue the existing C2 r=0 positive split map from accepted `../evidence/PILOT02/CHECKPOINTS/gen-00000003`, at4539815858.150909s, to the existing provider endpoint40119269418002330s (z15.9→4). The endpoint is copied from the pinned Q0 saved epoch list and must equal `HistoryProvider.end_time_s` at implementation binding. Original fields, physical providers, binaries, cell grid, source precision, native coordinate certificate, gas solve, local quadrature/fit tolerances and controller numerical scales remain unchanged. No new higher-order method is proposed.

Load generation3 under its ORIGINAL six-slot identity and manifest first. Preserve its initial condition, seven accepted-prefix states (initial+six half-steps), all counter origins/extrema, support/R histories and cursor: attempts5, accepted macros3, rejected macros2, accepted boundaries6, next step1708897821.8075385s. The successful C11 cold-process gen1→2 proof is reused. No initial transient or completed pilot family is rerun.

The old checkpoint binds an end of1e10s, an empty hard-event list and effective pilot budgets. Those bytes MUST NOT be edited or reinterpreted as an existing full-history checkpoint. Create a new child run with an explicit, hashed `IDENTITY_TRANSITION.json`: old manifest/identity and full input prefix hashes; unchanged physics/numerical-file pins; new runtime-only control/end/event/output schedules; preserved current state/cursor. Publish a child generation with identical physical arrays and the new run binding before its first map. This is a declared run extension, not bit-identical control-file continuation.

## Output and event schedules

`OUTPUT_EPOCHS.json` copies the129 **exact existing time values** from `recovery/Q0_SOURCE_ATTRIBUTION.json#/exact_source_history/*/time_s`; the65 subset is indices0,2,...128. Reuse these values rather than reconstructing them with another floating operation. Every future output time is a mandatory accepted macro endpoint, so no new dense-output interpolant is needed. The existing prefix lies before epoch1; epoch0 diagnostics still need the cell-method output adapter described below.

Use three explicitly separate schedules:

1. **Hard source/gas integration boundaries:** source-band10eV/50000eV crossings of fixed cell edges, especially empty-cell births, and emissivity redshift-table knots. Add the129 output epochs as OUTPUT boundaries, labelled separately. Endpoints are exact event values; do not use `nextafter` or shift a threshold.
2. **Internal source quadrature breakpoints:** all HM12 emissivity energy-knot/cell-edge crossings. `source_precision.provider_event_times` already delegates to the frozen source routine that finds these plus band/z events. Continue passing its complete per-map list to `integrate_source`. Do NOT feed every HM12 energy knot into the controller's global hard-stop list merely because the provider returns it.
3. **Opacity integration cuts:** HI/HeI/HeII thresholds within a cell are handled by the existing per-cell quadrature splits. These are not automatically extra global time jumps. The native-only smooth-support certificate still rejects threshold-crossing support; the ordinary resolved generic quadrature handles its usual split case. An actual unresolved threshold/support failure remains failclosed and must be localized.

A small new schedule builder must therefore select band/z hard events explicitly. It may reuse the existing root-finding formulas on just band edges and z knots, but must retain source-internal event handling unchanged. Materialize, hash and validate the full lists once per new run; no unbounded source-event recalculation as a separate science campaign.

## Runtime allocation and durable chunks

Proposed first full-target runtime allocation: total attempt cap105 and total accepted-macro cap103, counting the existing cursor5/3. Thus the newly allocated allowance is100 attempts/100 accepted macros. This allocation does **not** predict that100 attempts finish the universe history. Exhaustion is `ALLOCATION_EXHAUSTED`, with a truthful accepted checkpoint; any later allocation receives a new explicit version while counters continue increasing.

For the first worker chunk, allow at most3 new attempts and a45s **cooperative** wall budget checked before starting another trial. The worker always targets the full endpoint, not a new narrow-redshift test interval. Checkpoint after each accepted macro with both accepted half-step states and the next-step cursor. Rejected temporal attempts update an append-only durable attempt/cursor journal without becoming accepted physical history. Source/native/domain/ledger exceptions preserve the first failure and stop. An interrupted in-flight trial is not accepted; resume the last committed prefix and the most recent valid trial cursor, recording the interruption rather than resetting counts.

Measured PILOT02 cost:40.22730653599865s for12 physical maps=3.35228s/map, approximately10.0568s/three-map temporal trial. Three new attempts therefore suggest roughly30s **at the tested early-epoch workload**, plus packaging/checkpoint overhead. This is not an upper bound or a whole-run ETA: more source breakpoints, more Newton evaluations, growing accepted-prefix serialization and changed opacities can increase cost. A cooperative wall bound cannot interrupt one in-flight synchronous map. The surrounding executor may terminate an unresponsive worker; no partial map may then be promoted.

Keep accepted generation numbers/cursor counts monotonic. Derive each chunk allowance from BOTH the remaining allocation and the chunk cap; never call the remaining-budget helper twice against an already reduced dictionary. Store original total controls, actual effective controls, counts and both canonical hashes. Every external publication uses an explicit completed/failed chunk receipt. The current complete-prefix checkpoint format is correct for an initial chunk; writing every historical prefix into every generation has quadratic storage/serialization growth and is a concrete later throughput concern, not a reason to discard history silently.

## Full24 output adapter: exact existing definitions, new cell binding

Reuse field names, cgs definitions and comparison normalization from:

- `research/accel02_20261011/q1a/compare.py`: `FIELDS`9 and `MOMENTS`15, `metric` and separate65/129 subsets.
- `research/accel02_20261011/q1a/postprocess.py`: volume conversion, photoheat definitions and moment row layout.
- `research/accel02_20261011/n2/postprocess_moments_recovered.py`: identical physical field semantics and provenance structure.

These old packet exporters are NOT directly callable on C2 cell states: they expect a fixed packet-energy state and contain an old shifted-energy convention. Reuse definitions, **not** their `nextafter` path or packet-to-N conversion.

Add a versioned cell-output adapter and a diagnostic-only native-step extension. At an actual accepted output boundary, retain the summed K0/KE and direct heat from the same attenuated positive measure already used by the gas solve. Export native Gamma=ΣK0/a_rel^3; per-absorber primary heat=EV*(ΣKE−chi*ΣK0)/a_rel^3; proper species heat multiplies the actual neutral/singly ionized absorber density. Keep own-scale direct/ABI heat comparisons; do not recompute evolved Gamma from a newly projected power-law spectrum and assume it equals the just-used gas kernel. Source instantaneous N/U comes from the same StableCellSource formula; cumulative source fields use the existing paired counters. Radiation energy is EV*ΣU, divided by a_rel^3 for proper units. The remaining nine fields retain the native driver definitions.

At epoch0 no previous attenuated map diagnostics exist. Bind a new output-only evaluation of the original saved C2 moments with the admitted positive-measure operator at h=0, retaining its actual identity and distinguishing it from a repeated IC acceptance campaign. Do not invent or interpolate initial Gamma/heat. If an existing saved result is shown byte/semantics-equivalent, reuse it instead; equivalence is currently NOT_ESTABLISHED.

Append-only output records must bind epoch index/exact time, accepted generation/state hash, full24 fields, original-IC ledger values and geometry identities. Preserve native output kernels alongside N/U because the map's attenuated spectrum is not generally the next cell power-law reconstruction. Existing PILOT02 Gamma already came from the actual attenuated measure; no retrospective24field claim is made for its intermediate boundaries.

## Gates and implementation blockers

| Item | Present evidence | Needed before first full-target chunk |
|---|---|---|
| Same-map FLRW local dynamics | PILOT02 three macros; original local gates | Reuse exact source/controller/absorption/gas pins |
| Cold adaptive restart | C11 fresh-process gen1→2 bitwise | Reuse proof; new identity-transition load must be checked without a trajectory replay |
| Old→new end/control binding | Not implemented | New declared identity-transition tool, identical physical-prefix comparison, child atomic snapshot |
| Global hard/output schedules | Pilot had none | Separate band/z/output and source-internal energy-knot schedules; pin all exact values |
| Chunk wall/attempt journal | Pilot budget only | Cooperative driver and cumulative rejected-cursor journal; strict transactional accepted prefix |
| Full24 cell outputs | Only9 actual pilot fields saved | New cell adapter/native-kernel diagnostic binding, exact epoch0 handling |
| Whole-history geometry checks | Old geometry tests retained; no C11 full run | Record abs(R*a_rel−1), direction invariance and angular volume identity at actual accepted/output boundaries, same1e-11 |
| Growing checkpoint prefix | Correct local complete format | Initial chunks may retain format; measure size/cost; no silent history truncation |
| C2/C3 full histories/time refinement | Not evaluated | Subsequent actual matched runs and frozen comparisons; no old IC/source-gate replay |
| Nonzero shear/BASS | C11 source arithmetic explicitly r=0 | Separate existing later nodes; no scope transfer |

The whole-history gate remains time9fields2e-6, spectral/full24fields1e-3, energy/original energy1e-9, photon number/original nH1e-9, geometry1e-11, strict domains. For each65/129 selection, each field uses that fine subset's own maximum; exact-zero fine fields require exact-zero differences. The unchanged controller local target2e-7 is an integration heuristic, not that global acceptance denominator.

## Smallest next executable unit

Implement and check a **zero-native-map transition + schedule + chunk-driver packet** first; publish its child initial checkpoint with the inherited accepted prefix. Add only new tests for allowed runtime binding changes versus forbidden numerical/physics changes, output schedule/event classification and interrupted/rejected-cursor resume. Then complete the full24 cell binding, or explicitly freeze its required raw native kernels and output-state capture before the first full-target map so it can be evaluated without replaying dynamics. An independent review must confirm these concrete implementation gaps are closed. Only then execute one3-attempt/45s full-target continuation chunk from generation3. No new pilot restart at t0 and no higher-order solver development is requested.
