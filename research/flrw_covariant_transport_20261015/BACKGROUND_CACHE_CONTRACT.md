# Exact background-point memoization contract

Status: implementation contract frozen; new cache measurements pending. This is a source-exact performance change for a fresh stage004 epoch. Running stage003, its source, five-case allocation and results remain untouched. Skill context: physmath-research-loop 1.3.0, parent-supplied context; the requested R1–R10 record is below.

## Selected implementation

Add a bounded **32-entry exact-key ring cache owned by each immutable AxbiBackground model context**. Retain the original point_at_scale computation as an uncached reference function. Do not change interval_increment, local GL4/GL8 proper-time increments, Simpson panel count/order, rate arithmetic, geometry validation, thresholds, source, transport, Newton or time-error criteria.

Actual source: rust/rei_microphysics/src/axbi_background.rs defines AxbiBackground with private cosmology, a_ref, a_end, b_ref, q_ref, family and panels. They are constructor-initialized and currently have no mutators. Driver.background and Driver.config are public, so a Driver-owned cache keyed only by a would be stale after background replacement. The selected cache resides in AxbiBackground itself; replacing Driver.background replaces the model/cache together. Changing Driver.config does not retroactively change the existing background, and cache identity must not be inferred from that config.

The model/cache association is constructed, not hashed from an incomplete parameter subset. An Arc<Mutex<PointCache>> may be shared by AxbiBackground clones because all calculation parameters are immutable and copied exactly. A separately constructed background gets a separate cache, even at the same scale. Future model mutators would have to replace or invalidate the cache atomically; none are introduced here. Do not freeze a private clone behind the public Driver.background field: that would change existing public replacement behavior.

The cache key is a typed validated positive finite binary64 scale represented by a.to_bits(). Preserve the existing positive(a) check and [a_ref,a_end] domain check before lookup. NaN, infinities, either signed zero, negatives and out-of-domain inputs retain their current error tags/order. Do not round, quantize, use approximate equality, interpolate, or use a neighboring key. Distinct adjacent positive f64 values are distinct keys.

Cache only successful, completely validated BackgroundPoint values. BackgroundPoint is Copy and returned by value; caller changes cannot mutate stored results. A miss performs the original uncached function with exactly its current arithmetic and geometry validation, then stores the successful value. Failed computations are not cached. A hit returns that same value. No geometry or proper-time value is reconstructed from accumulated differences.

Use safe std synchronization. Hold the mutex only for lookup/insertion, not the expensive quadrature. Duplicate concurrent misses may compute the same pure result; they are allowed and must be counted honestly. Evict by a deterministic bounded ring; eviction changes work, not results. A poisoned/unavailable cache falls back to the uncached function rather than introducing a new scientific error. The bypass/reference mode must not consult or alter a previously populated cache. Cache contents are derived transient state: they are not serialized as physical checkpoint data.

## Equivalence derivation and limits

Write the existing finite algorithm as F(M,b), where M is the complete immutable model and b=a.to_bits(). F includes input/domain checks, every 4096-panel operation at current configuration, the final rates and geometry validation. For a successful miss, the cache stores C_M[b]=F(M,b). Because M and b are unchanged, every later successful lookup returns exactly F(M,b), including all BackgroundPoint field bits. Eviction or a duplicate miss merely evaluates F again. Errors still execute the original checks/reference path. Model replacement selects another C_M. Therefore cache-on and cache-off have identical returned values and errors for every call in the supported model context.

By induction over the unchanged driver calls, the resulting gas/photon states, active/passive moments, source/event/work ledgers, local errors and adaptive accept/reject decisions are identical. This equivalence concerns the finite algorithm, not a new proof of continuum accuracy. Cosmological proper time is a physical output and remains bitwise equal. Source/build identity and elapsed wall-clock metadata necessarily differ and are verified separately against each artifact's own binding. Wall-clock-limited runs can complete different numbers of steps because performance changes; an equal accepted-step comparison is required for numerical parity.

The existing short-clock interval_increment is deliberately untouched: replacing it by subtraction of cached accumulated clocks would reintroduce the earlier cancellation problem. Background memoization does not address source-grid/refinement errors or change any physical assumption.

## Evidence and bounded discriminant

Read raw/ncp002_serial_hotpath_profile.json: point_at_scale averaged0.179824ms over20 calls; interval_increment averaged0.000724ms. This source-bound measurement used checkpoint4080 with1024 transport cells and4672 cached photon quadrature nodes. It is a repeated-call cost measurement, not a measured cache-hit fraction.

Read raw/ncp003_benchmark001/summary.json and measurement_interpretation.json: prepare parallelism passed bitwise parity at widths1/8/32/64, but32-step wall was0.718848497/0.562208340/0.558850855/0.591987827s. Mean useful CPU activity was about1.00/1.42/1.63/2.59 cores. No64-busy-core claim follows. Removing repeated serial background work is a concrete next opportunity rather than adding idle workers.

Static call-graph accounting for a successful adaptive_step gives approximately47 point_at_scale calls across three tentative solves and the final metric, but only about6 exact scales: old, geometric quarter, mid, geometric three-quarter, endpoint and a_ref. Output/checkpoint calls add more repeated scales. These47/6 counts are a source-derived prediction, **not measured hit/miss telemetry**. Rejections and exact floating endpoint arithmetic may change the distinct-key count; instrument actual calls before interpreting a speedup.

After the current global allocation releases8 cores, run one actual NCP comparison pair at transport_threads=8 on the same populated V4 fixture: cache-off versus cache-on,32 accepted steps per arm. Total bound≤60s and≤10000 actual RHS; no additional thread/grid factorial cases. Use the same scalar function and source build in both arms, changing only cache bypass. Preserve each final physics state, metrics, decisions, counters and source/config hashes. Record calls, hits, misses, actual uncached executions, distinct requested exact keys, capacity/evictions, wall and CPU time. Counters must not alter arithmetic or physical state. A duplicate concurrent miss may make uncached executions exceed unique keys; report that instead of forcing a false identity.

Compare complete BackgroundPoint bits, returned errors and complete driver physical output bitwise. Keep existing physics tolerances unchanged. Report the measured same-work wall ratio and call-cost reduction; do not claim full-history or64-core efficiency from this small fixture. If no useful speedup is observed, retain the result and diagnose the measured fraction; do not expand benchmark combinations automatically.

Focused changed tests: at most2 attempts, each≤180s. Cover exact cached/uncached field bits for repeated/adjacent keys and model endpoints; invalid-input/error parity; eviction; independent backgrounds at the same a; clone behavior; Driver.background replacement after cache warming; public config mutation not masquerading as background mutation; concurrent calls and bounded capacity. A complete same-fixture adaptive parity pair covers state/event/decision propagation. Existing historical checks are reused; no broad historical rerun is requested.

## Evidence reuse and executable next step

After the finite function equivalence and focused regression/parity tests pass, stage003 scientific screening remains evidence for the same numerical function. Record a semantic-equivalence edge from its source identity to stage004; do not relabel an old checkpoint as an exact-source resume or claim that old resource/performance measurements apply to the faster build. A different wall cap may cover more history, and new full histories must actually execute. Existing source-bound resume guards remain intact. The next lower-worker action is the32-entry background-owned cache/reference implementation, followed by the bounded pair when8 cores are free.

## Compact R1–R10 record

| Step | Actual completion/status |
|---|---|
| R1 | Target fixed: reduce repeated background work without changing the FLRW finite function or scientific screen. |
| R2 | Read actual AxbiBackground/Driver APIs, serial hotpath receipt and NCP003 parity/scaling outputs. |
| R3 | Identified complete private model context, public Driver replacement hazard and exact positive-f64 domain. |
| R4 | Chose background-owned32-entry ring over Driver-only a-key caching, private model snapshots or interpolation. |
| R5 | Derived F(M,b) memoization and driver-call induction; interval clock unchanged. |
| R6 | Independent source-grounded review requested from integration_science_review; its completed signoff is recorded in the separate handoff message rather than modifying this frozen contract. |
| R7 | Existing actual timings read; one8-thread cache-on/off32-step pair specified. New cache benchmark not run. |
| R8 | No implementation/performance PASS or continuum/no-go claim before its actual evidence. |
| R9 | Root accepted the exact32-entry background-owned scope and bounded pair; lower-worker handoff is executable. |
| R10 | Implement after Unit3 snapshot; focused tests and free-core bounded pair; reuse old science only through explicit finite-function equivalence; stage004 fresh source binding. |

This contract is frozen for implementation. Future measurements and independent-review receipts belong in separate result artifacts; do not mutate the compiled contract merely to append later outcomes.
