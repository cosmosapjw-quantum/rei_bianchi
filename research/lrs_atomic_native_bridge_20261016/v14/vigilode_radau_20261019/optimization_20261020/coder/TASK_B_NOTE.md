# Task B implementation and observed evidence

The root-authored `../OPTIMIZATION_CONTRACT.md` was read in full. Work stayed in the task-owned source/build tree. No Git mutation, network dependency fetch, publication, scientific criterion change, original native-byte change or VigilODE-byte change occurred.

## Implementation

The additive native module adds a transport-borrowing NativeCellCache whose own base photon snapshot, per-cell prepared nodes and frozen ray scales live for one Jacobian. Its prepare operation validates native shape/domain, exact support identity, and exact unchanged-cell number/energy. It reconstructs only the explicitly changed cell and replays cell/node order into unchanged native_rates arithmetic. Context caches frozen ray scales. Budget supplies explicit Legacy/CellCache mode and profile-gated timings/counters. The CLI supports --native-eval legacy|cell-cache (default legacy) and --profile. Original FD epsilon/formula/fallback classification, attempt charging, caps and transactional mutation are retained.

The separate src/bin/lrs_batch.rs reuses existing pinned ParallelExecution::rayon/map_ordered for independent process slots with distinct CPUs, child timeout and honest failure capture. Native event loops and the solver pin were not parallelized or changed. Three batch jobs imply useful width <=3 even with four worker slots.

## Verification outcomes

- Preserved immutable original executable and adapter/addition/native-parent source under immutable_baseline before editing.
- First candidate build: exit0, 10.0601s. First focused pass: exit101, one newly written support fixture violated its cell bin. This is preserved at experiments/focused; no numerical mismatch occurred.
- Concrete repair kept the fixture within the actual native bin straddling HeI threshold, with a steep base and changed-cell reconstruction. Repair build exit0,1.9758s; focused repair exit0,1.8763s. Four unit tests and six integration tests passed, including the unchanged seven prior tests.
- Seeded native full/cached Jacobians equal exactly: d=84,40 occupied cells,169 charged calls in each;6760 vs200 occupied-cell preparations. Empty d4 and delta d5 comparisons also equal; delta11 vs3 preparations. Native threshold/steep preparations equal after changed-cell recomputation; stale support/state, wrong shape/index rejected. Cached resource failure preserves state/ledgers while charging attempts; fatal/domain distinctions checked.
- All19 existing settings completed with cached native evaluation, compared recursively against original same-setting raw data. No scientific-field mismatch, nonfinite value or dropped original channel. FixedN4's real reference is final_source_n4. N16 references are the three actual unchanged-binary outputs produced in this session.
- Native baseline152 files and pinned VigilODE477 files remain byte-identical, with only the authorized additive native-parent hook appended. See experiments/SOURCE_IDENTITIES.json.

## Serial timing (all five pairs retained)

CPU0 affinity; no competing build. One warm-up per variant/setting, then five interleaved AB/BA pairs, all profile off. Every measured output matches the unchanged original N16 physical data/ledgers. Native wall medians legacy/cache: fixed0.550993/0.122657s;birth1.792522/0.361862s;disabled1.936270/0.397404s. Process-wall medians legacy/cache: fixed0.666076/0.214912s;birth2.073549/0.666494s;disabled2.272976/0.720854s. Ranges,IQR and every paired ratio are retained; these are different clocks and must not be conflated.

FixedN16 profile attribution: both2992 charged RHS attempts and1,914,880 node visits. Occupied preparations119,680 legacy vs14,720 cache. Exclusive preparation timing0.495075 vs0.078447s; inclusive Jacobian0.474229 vs0.051619s. Inclusive Jacobian overlaps evaluation timing and must not be added to exclusive totals. Fine profile clocks are disabled in timing samples.

## Batch and memory observations

After serial completion: one warm plus3measured batches for each width1/2/4,36successful child histories, all numerically matching original N16 data. Batch pool preserves original output order. Median whole batch walls2.77677/0.907515/0.757882s respectively; width1 sample1.52965..2.86474s is noisy, and width4 useful concurrency is at most3. No universal throughput scaling claim.

Two initial batch harness failures are retained: omitted CASE_BINARY (usage exit1), then absent /usr/bin/time (child127). Corrected argument binding and optional RSS fallback produced all successful batches. No physics failure was inferred. RSS in successful batch children is null because time is absent.

Earlier Python fork/exec/wait4 observations (legacy9344KiB,cache15464KiB) are potentially contaminated by pre-exec parent RSS after JSON parsing; they are preserved as diagnostic evidence and NOT_ADMITTED for either memory increase or reduction. Root identified this concrete measurement defect. A small C parent helper repaired it: four alternating fixedN16 observations legacy/cache/cache/legacy yielded6400/6552/6456/6396KiB actual wait4 ru_maxrss, all exit0 with identical physics. Helper/source/child binary identities, CPU and raw receipts are preserved in MEMORY_HELPER_IDENTITY.json and memory_c_* folders. These are descriptive observations and support no memory-reduction claim. The serial runner's earlier resource field is explicitly named peak_children_rss_kb_cumulative and is not per-child RSS.

## Artifacts and stop boundary

Canonical normal files are under patch_files/ relative to vigilode_radau_20261019. Actual candidate source/build under baseline/, original executable under immutable_baseline/, raw evidence under experiments/. Main binary SHA25624f9d38e56d3380e830478b8afe7760b2f44fff7ab60167ed14aa668ae7f4ac0. Original binary SHA25628dfc8dbfe627acd7c7d2f77c08746db6d5f67f620b6e6a38a1b658c52eebc2d.

Root scientific admission and independent review remain pending. No publication/upload was attempted. All earlier held claims and PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED persist. Stopped after the finite authorized evidence; await root review or a bounded repair request.

## Final delivery runner repair

prepare_and_run.py now accepts --native-eval legacy|cell-cache (default legacy) and --profile, forwarding them through an additive optional case_args argument on run_cases. Existing four Python runner regression tests passed unchanged. Actual fixed Radau N2 cache+profile smoke exited0; argv/mode/profile were asserted and physical JSON matched the original N2 output exactly. Native source and candidate binary were unchanged. See delivery_fix/FINAL.json and delivery_fix/native_smoke.
