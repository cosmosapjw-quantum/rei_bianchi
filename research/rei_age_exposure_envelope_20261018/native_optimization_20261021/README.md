# V10 optimized native unfinished campaign

This lane prepares and runs **only time8, time16, time32** with the frozen native physics and original gates. No completed age/reference/spectral/fixed-study case is launched. Scientific/production admission remains NOT_ISSUED.

## One campaign entrypoint

First inspect the actual host plan. These arguments are explicit upper grants; the plan also obeys detected affinity, CPU quota, physical available memory and remaining cgroup memory.

```bash
python3 campaign.py --runtime /task/v10_runtime --out /task/v10_results \
  --available-cpus 64 --available-memory-gib 128 --plan-only
```

On an idle verified64core128GB host the default plan uses3cases,20persistent transport workers percase and1main lane percase, totaling63slots. It gives each case at most24GiB and reserves at least16GiB. Smaller grants reduce workers/concurrency and increase the elapsed allowance to `min(5600,ceil(3/jobs)*1800+200)` seconds, while retaining5400aggregate child wall seconds and1800percase. No claim of64core speedup follows from local measurements.

Run the same entrypoint with an installed Rust1.94.1 prefix and the v9 offline C10 archive:

```bash
python3 campaign.py --runtime /task/v10_runtime --out /task/v10_results \
  --rust-prefix /task/rust-1.94.1-prefix \
  --c10 /task/REI_AGE_ENVELOPE_EXECUTION_READY_20261020_v9.zip \
  --available-cpus 64 --available-memory-gib 128
```

`--repo /path/to/repo` can instead read locally available frozen native Git objects. No source user moves/unzips are required. Archive restoration verifies all153 frozen file hashes/sizes before writes. Immutable donors are never edited. The C10 option additionally restores the already completed original positive-DOP853 age32 reference automatically, verifies its raw archive hash, and writes its exact path/operator classification to RAW_INPUTS.json.

The entrypoint prepares the task overlay, checks source freshness and all prepared output hashes, compiles offline under a separate300s campaign build cap, and runs the small original-core preflight before heavy cases. It writes timestamped host manifests, persistent CAMPAIGN.json, percase raw stdout/stderr/data/receipts, actual child CPU/RSS and output hashes. Every launched attempt counts against persistent budgets. Completed matching own outputs are reused after hashes. Failed/interrupted/mismatched attempts are never automatically replayed. Independent remaining cases continue. Resource termination targets only owned process groups. No other job is stopped or killed.

## Native changes

`prepare.py` generates an opt-in overlay from manifest-verified immutable owner/donor sources. `accessors.rs` exposes the existing persistent worker pool for independent prepared-cohort evaluation; Arc owns the prepared list. All floating-point photo reductions occur afterward in original cohort order. Width1 keeps the original order. No nested pool map and no new dependency are introduced.

`subnormal-barycenter` is enabled only through REI_SUBNORMAL_REPAIR and only after the original count/energy gate has failed. It accepts only a finite positive subnormal population and valid support. It checks u/n, support-clamped/adjacent candidates with both original compensated count/energy expressions and original tolerances. Normal populations and originally passing quadrature are unchanged. Failure retains the original error. First success reports inputs/candidate bits and old/new defects/gates; a main-exit guard reports total repairs and maximum repaired mass bits. This relaxes subnormal fixed-support representation, without a global nonlinear response bound.

Compact native tracing retains only common8 observation states consumed by output. REI_FULL_TRACE selects the original full-snapshot control. Physical stepping, source/birth records and final state remain unchanged.

## Accepted BE observer and offline analysis

REI_BE_TRACE activates compact accepted-chemistry JSONL records after Newton convergence and the original local accepted ledger gate. The observer uses the final accepted gas, frozen prepared nodes and the exact original denominator association `1.0 + dt_s * model.c_cm_s * opacity`, with the original compensated opacity sum. It records separate lambda diagnostics, denominator extrema, outward Q/S accumulations, active node count, rounded before/after masses, reconstruction difference, and identifying bits.

`analyze.py` uses Fraction arithmetic from stored binary64 values for `Q_lo/d_max .. Q_hi/d_min` and the separately outward node-division sum. The enclosure concerns the exact rational stored-weight/stored-denominator discrete BE kernel. It does not enclose unrounded physical coefficients, continuous-time history, or nonlinear gas response. Before/after plain sums are rounded observations; their comparison residual is kept separate. Empty node populations are explicit. Failed native attempts yield INCOMPLETE_ACCEPTED_PREFIX. Perrow exact evidence is streamed into separate JSONL files and summarized in ANALYSIS.json.

Automatic analysis preserves the original0.005 finite-neighbor target and uses existing endpoint_metrics/match_observations for time8vs16,16vs32 and each available time result vs stored age32. It enriches missing endpoint birth times from setup.json, as the original comparator does. Missing/invalid channels remain MISSING_PAIR/INVALID_PAIR and are never filled with zeros. Source equivalence is limited to common frozen native/config/B1 lineage and explicit numerical representation choices; the positive DOP853 reference and native BE operator remain distinct. All comparisons are finite differences, without convergence or production admission.

## Local verification and measured kernel result

See IMPLEMENTATION_RECEIPT.json and verification/. Core/benchmark build wall time is separately accumulated below120s; all changed-risk controls and the bounded kernel measurement are accumulated below240s. Full time8/time16/time32 were not run locally.

The actual compiled original core repaired captured N2,N3,N4 failed cells with unchanged gates, preserved a normal passing result, rejected malformed/out-of-support/normal repair candidates, and gave identical synthetic scientific fields at1/2/4workers. The four tiny integration variants used the controller-approved minimum-valid configuration2birth/nmu8/source8/transport8 and11mesh steps (89RHS each). Serial/off, parallel/off, parallel/observer, and fulltrace/observer endpoint/observations/native_return bytes were identical. Three earlier inputs were rejected before stepping by original minimum/normalization guards; their logs remain preserved.

Ten Python changed-risk tests cover resource allocation, independent failures/resume/no-duplicate behavior, persistent aggregate budget, exact BE zero/threshold populations, setup birth-time enrichment and missing-channel rejection.

The absorption-only kernel benchmark uses one actual source8/nmu8/transport16 prepared fixture,32cohort jobs,20evaluations/sample and5samples/mode. It runs no gas RHS or history. All scientific fields match original serial bitwise. Median sample times were0.009680326s original serial,0.009681998s pool1,0.006849993s pool2 and0.004608712s pool4: measured local ratios approximately1.000,1.413 and2.100 for pool1/2/4. Raw samples, fixed absorber/dt values, separate fixture preparation time and parity flags are in verification/MICROBENCH.json. This short local kernel workload is not a64core campaign speedup estimate.

## Targeted C9 corrections

The independent C9 batch led to four Python-only corrections. TimeoutExpired now preserves available stdout/stderr, exit124 and budget debit for both light checks and build checks. Launch PID/PGID/start identity is persisted; resume refuses live own orphan groups or an uncertain launch boundary without launching another case, and conservatively debits confirmed exited prefixes. The existing own-child preexec hook writes its own namespace-local/procfs PID, PGID, start ticks and namespace to a sidecar; resume reads only that saved concrete procfs identity. No host process scan is used. Launch exceptions and uncertain handoffs preserve typed attempts, raw files and conservative budget debits. Analysis requires current campaign identity plus output hashes before treating a completed result as eligible; cached age32 reference restoration verifies stored payload hashes. The original B1 receipt/binary/prepared identities are separately bound as a baseline reference; the optimized BE binary is explicitly distinct. The ten targeted Python checks pass; both failed namespace-mapping regression receipts are preserved. Existing Rust/tiny/kernel evidence is reused; no additional native trajectory, build or timing measurement was performed for these corrections.
