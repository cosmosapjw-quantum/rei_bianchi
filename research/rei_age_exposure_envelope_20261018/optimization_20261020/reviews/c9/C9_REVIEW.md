# C9 independent review: age-exposure optimization

## Decision

**PASS for the scoped optimization and its reproducible launch path.** No numerical or mathematical defect remains open in the reviewed A/B/C kernel. One concrete launcher verification defect was found, repaired by the executor, and closed through a targeted positive/negative regression. This decision covers the existing fixed-source, fixed-opacity endpoint model and its frozen 57,344-node input. Production scientific admission remains `NOT_ISSUED`; no nonlinear solver, cosmological history, age32 acceptance reference, owner policy, PR150/R9, LRS, or BASS claim is changed.

The review used actual `results/AGENTS.md` and the supplied physmath research loop 1.3.0 `SKILL.md`, `POLICY_INTEGRATION.md`, `SUBAGENT_MODE.md`, and selected C9 contract. It was one fresh, read-only implementation review. Source repair went through the parent to the executor. The reviewer wrote only files in `reviews/c9`; no recursive review or historical scientific campaign was run.

## Reviewed identity and evidence

The reviewed current `rust/src/main.rs` SHA-256 is `81bd489a71a8813408033f2c77a184f17a9c9446b52b5cb511e4d64d582959e5`; `certified.rs` is `ab53e08371489094e51af310bdfb58936453c87d244a7addfc567d758e5f0bf3`. Both were checked at entry and after the launcher repair. Frozen original `main.rs` and `certified.rs` were checked against the initial baseline receipt. Model input, node input, and Cargo.lock match that receipt. Exact current identities for all reviewed helpers and vendor modules are recorded in `C9_RECEIPT.json`.

The authority supplied by the parent is immutable baseline HEAD `58dc257d1402daa3d0f64786279e13cd72bfb0c7` and restored task tree `1360944eb7e94743c1d5a668e7458f5b4f902d7a`. The local tree is a materialized snapshot, not an operational Git checkout; no unsupported claim of a local `git diff HEAD` comparison is made. Source comparisons used `baseline_source/src`, original A/B snapshots, and the actual files. Current affine and directed module hashes equal the preserved vendor provenance and prior implementation identities.

## Arithmetic and ordered execution

### A: integer denominator lift

For reduced input x=p/q with q>0, initialize D0=N0=P0=1. At step j use Dj=j q D(j-1), Pj=(-p) P(j-1), and Nj=j q N(j-1)+Pj. Division gives Nj/Dj=N(j-1)/D(j-1)+(-p)^j/(j! q^j), so induction establishes exactly the original rational Taylor partial sum. The implementation snapshots j=18 and j=19, constructs the same normalized rationals, and calls unchanged outward rational conversion and directed squaring. BigInt arithmetic avoids fixed-width integer overflow.

The original range reduction, zero return, and tau>=752 subnormal enclosure are retained. For 0<=x<=1/2, alternating terms decrease in magnitude, so S19<=exp(-x)<=S18. The cutoff retains [0,eta], eta the minimum positive binary64 value; the unchanged proof uses 1074 ln(2)<751.8<752. These observations apply to general nonnegative rational arguments, not only binary64 denominators, subject to finite resources for their BigInts.

Evidence: `rust/src/certified.rs:33-122`, the original snapshot, and the focused unit test sources at `certified.rs:129-181`. The reviewer actually executed the existing test binary's four `certified::tests`; all passed in approximately 0.11 s. They cover exact general-rational S18/S19 equality, endpoints around 0.5, range-reduction transitions and 752, the minimum subnormal, conversion midpoints, underflow positive upper bounds, and prefix recurrence/thread parity. Command, binary identity, stdout, stderr, and exit code are preserved in `focused_tests.*`. This was an existing test executable with the same certified.rs as C, without recompilation.

### B: indexed preload and age cache

`Cache::preload` builds a Vec in request order, uses HashSet only for membership deduplication, and uses indexed slice `par_iter().map(...).collect()` to preserve the correspondence between every miss key and computed interval. Hash iteration order is never used to order numerical sums. Each worker reads immutable rate data and constructs the identical exact tau from the same rate and binary64 time bits. It fills the same cache keys used by `survival`; fallback cache misses still execute the original computation.

The case loop remains in node order; each interval row, node total, passive sum, event aggregation, rate-group sort, map ordering, and final directed sum remains ordered as before. The age cache repeats the identical rational conversion once per frozen clock entry. The earlier observation-time insertion into a group's BTreeMap uses the same zero entry and changes no defect or iteration order. Current successful B and C outputs show 53,408 preloads and 53,408 cache evaluations, demonstrating full requested-key coverage on this input without reducing the cache work count.

Evidence: `main.rs:16-42,81-121,124-198`; B snapshots; all raw study comparisons in `independent_raw_check.json`.

### C: reusable exact oracle and outer group parallelism

Grouped map vectors are immutable after construction. At the canonical 1-thread prefix execution, every leaf recurrence r(k+1)=gk rk+dk is evaluated in exact rationals from initial zero and compared with its prefix upper bound. At 2 and 4 prefix threads, group counts, prefix lengths, and every prefix bit are compared against the canonical vectors, including initial zero. Thus every already-checked rational inequality transfers to each corresponding thread execution; merely comparing final values would not have established that transfer.

Indexed outer group collection retains group order. The original VigilODE tree, fixed split points, outward arithmetic, and final sorted directed fold remain in place. Source inspection confirms the unchanged prefix implementation returns exactly one initial value plus one value per input leaf. The old full-oracle branch is still available with `REI_REUSE_ORACLE` unset.

Across the four age cases, the observed counts reconcile exactly: 4,448 group recurrences, 27,552 leaf inequalities, and 2*(27,552+4,448)=64,000 prefix bit comparisons. The global, ungrouped prefix checks remain unchanged as well. Evidence: `main.rs:200-280`; `src/vendor/affine_transport.rs:103-207`; raw C study instrumentation and `independent_raw_check.json`.

C reduces repeated exact-rational audit work while retaining the relevant guarantees and adding full grouped-prefix bit comparisons. It must not be described as running the identical original audit workload.

## Independent raw result assessment

The reviewer parsed all 22 successful study files then available, including `WRAPPER_CHECK`, without importing the benchmark comparator or summary. Complete recursive output comparison excluded only wall time and the new optimization instrumentation. Every other field, key, type, list order, and binary64 endpoint matched the baseline. The binary64 comparison packs each parsed float into its 64-bit representation. This is a numerical output identity claim for the stored values, not byte identity of pretty-printed JSON.

The B8 reference run has 53,628 successful exponential endpoint comparisons, exactly 53,408 cached evaluations plus 220 direct global-prefix evaluations. Its complete numerical output also matches the baseline. This is stronger than the small fixture check for the actual frozen data. It does not exhaust arbitrary rational inputs; their exact partial-sum identity follows from the induction above. The grouped intermediate prefix vectors are checked by live assertions but are not all serialized, so the review does not claim to have independently reconstructed every internal grouped prefix from JSON alone.

Raw evidence: `results/B8_REFERENCE_RUN.json`, `B8_REFERENCE_STUDY.json`, `B8_REFERENCE.stderr`, each A/B/C `*_RUN.json` and `*_STUDY.json`, and `reviews/c9/independent_raw_check.json`.

## Performance claim and limits

| Configuration | Samples | Median wall time (s) | Baseline / median |
|---|---:|---:|---:|
| Original baseline, global Rayon setting 2 | 3 | 47.413248701 | 1.0000 |
| A, global Rayon setting 2 | 3 | 10.461018704 | 4.5324 |
| B, global Rayon setting 2 | 3 | 6.618587983 | 7.1637 |
| C, global Rayon setting 2 | 3 | 3.531862843 | 13.4244 |
| C, global Rayon setting 8 | 3 | 1.560498093 | 30.3834 |

The A/B comparison retains the original audit work. The C comparison combines an equivalent-audit algorithmic change with group parallelization. The 13.42x result uses the same global worker setting; the 30.38x result compares baseline setting 2 with C setting 8 and therefore includes additional worker resources. The internal prefix validation still uses explicit pools at 1, 2, and 4 threads in every configuration: the labels indicate the global pool setting, not an assurance that the whole process never has a larger explicit validation pool. `C8_RUN` means variant C at global thread setting 8, not coding stage C8.

Runs were sequential. The first baseline measurement used a separate Python subprocess launcher; baseline repetitions and candidate runs used `bench.py`. Both time the same binary process boundary and inputs, and the three baseline times span only about 47.185-47.731 s. Measurements are a small local experiment, not an isolated cross-platform benchmark or an error bar for other hardware.

Peak RSS should be reported only as observed process high-water marks. Same-helper baseline repetitions reported 27,648 KiB and C typically 27,776 KiB; the first differently launched baseline reported 20,616 KiB. The helper's fork/launcher high-water contribution can limit such comparisons. These data support neither a memory-reduction claim nor a precise allocator-level memory cost claim; do not infer an approximately 33% C increase from the unmatched first baseline sample.

## Launcher, reproducibility, and one closed finding

**C9-01 — requested modes were not checked against observed modes — CLOSED.** The original benchmark comparator excluded optimization instrumentation and accepted matching scientific output even if a supplied executable had not activated preload, shared-oracle, or feature-gated reference parity. Consequently, a feature-free executable could complete a requested reference-parity run with zero comparisons and still be treated as successful. This was a current reproducibility/failure-reporting defect, not a failure of the already observed numerical or reference results.

The parent authorized the smallest repair and the executor added `mode_activation_failures` in `bench.py:16-41`, preserving numerical parity as a separate result. The helper now checks requested preload/reuse activation, full preload count, per-group recurrence/inequality/parity counters, and the exact reference-comparison total. It saves failure details and exits nonzero for inactive requested modes. Four fixture-based regressions cover actual baseline, C, feature-free C, and reference-enabled B outputs. A real feature-free C invocation requesting reference parity completed its numerical kernel but was rejected by the benchmark: binary exit 0, numerical parity true, expected reference checks 53,628, actual 0, `mode_activation_pass=false`, `failure_category=MODE_NOT_ACTIVATED`, benchmark exit 1. That distinction is correct. The kernel source hashes remained unchanged.

Evidence: `test_mode_activation.py`, `results/MODE_ACTIVATION_TEST.{json,stderr}`, `NEGATIVE_REFERENCE_FEATURE_FREE_RUN.json`, `NEGATIVE_REFERENCE_FEATURE_FREE_STUDY.json`, and `MODE_NEGATIVE_EXPECTED_EXIT.json`. No further source repair is required by this review.

`run_optimized.py` validates the frozen input hashes, activates both C flags, chooses a positive default bounded by affinity, visible CPU quota, and eight workers, and supports an explicit thread setting. Its existing-binary path has an actual successful numerical smoke run. `build_variant.py` stages fresh source and offline locked dependencies in scratch, preserves frozen A/B variants, and supports the reference-check feature. `REPRO_WRAPPER_CHECKS.json` records a successful fresh frozen-B offline rebuild and wrapper help/invalid-thread checks. The wrapper's fresh-C branch was inspected but was not separately exercised end to end in this review; the supplied clean-build helper and successful feature-free C build are the supporting execution evidence. Reference parity requires a binary built with `--features reference-check`; the repaired helper now reports a clear failure if that requirement is missed. Core flags use environment-variable presence, so unset a flag to disable it; setting it to the string 0 still enables it. The wrapper clears inherited mode flags before selecting its modes.

`summarize.py` reads fixed sample groups, retains exit/parity observations, distinguishes B and C audit scope, and does not rerun scientific work. The expected negative test is outside the fixed performance sample groups.

## Positive next action

The scoped C9 gate is satisfied. The parent may finish the existing report, launch instructions, and authorized publication/backup steps without starting another audit cycle. This review makes no claim about completion of remote push or either backup; those are parent-owned execution steps. Preserve the stated model scope, original age32 reference, and the measured-workload/thread distinctions when presenting the result.
