# Native LRS optimization contract — 2026-10-20

Owner: root (Astra). Implementation: delegated lower-tier coder. This is a new, bounded optimization cycle requested by the user, separate from the completed recovery and from the production v3/rux DAG.

## C1. Frozen baseline and actual evidence

- Repository: `cosmosapjw-quantum/rei_bianchi`, PR 198, branch `research/rei-lrs-v14-physical-birth-20261018`.
- Intake delivery HEAD: `5cccbcfb28a2cec57997493160b49b79954fe8f3`; scientific source: `d87ba9ca25acb8a2a032154fa23057b45acd6207`.
- VigilODE remains pinned to `8a8bd409b1d96c7b7421f496d229e119fd3d284e`; the existing Radau IIA3 and faer 0.24.4 remain the numerical solver.
- The existing 19 settings and 7 tests have earlier native sandbox/NCP evidence. New repeats are optimization experiments, not new unique physical histories or an extension of order/positivity claims.
- Latest Drive/Dropbox metadata intake found no items modified after 2026-10-20T05:29Z. Existing unchanged archives were not recounted as new executions.
- This session actually restored and compiled unchanged source with local Rust 1.94.1, locked/offline/release/jobs=2. Build exit 0, 150.893435552 s; executable SHA256 `28dfc8dbfe627acd7c7d2f77c08746db6d5f67f620b6e6a38a1b658c52eebc2d`. That build alone is not a native history run.

## C2–C3. Selected mathematical seam

In one chemical segment, geometry, scale factor, densities, CMB temperature, support, and coordinate scales are frozen. A reconstructed photon cell depends on its own number and energy-offset coordinates, and on the frozen ray geometry. Its instantaneous absorption derivative depends additionally on the three gas fractions; it does not depend on gas thermal energy or other photon cells. Gas photo-input sums depend on all photon cells. Thus the Jacobian has a 4-dimensional gas border and independent photon diagonal blocks of dimension at most 2.

The chosen change is exact reuse of prepared reconstructed nodes within ONE finite-difference Jacobian:

1. Prepare all base photon cells once using the existing `prepare_cell` / `cell_quadrature` / native atomic provider.
2. For the eight gas-coordinate perturbations, reuse all base photon preparations.
3. For either perturbation of a photon coordinate, prepare only that cell afresh.
4. Replay every native-rate node in the original cell and node order. Keep compensated photon sums and all species/event/energy operations in the original order. Do not replace a global sum by `base - old + new`.
5. Cache ray geometry/scales only for the immutable segment context. Rebuild all Jacobian-local state at every new Jacobian, and every segment after a geometry map or birth.

For m=40 occupied two-coordinate photon cells, d=84, full replay prepares (1+2d)m=6760 occupied cells per Jacobian; exact reuse prepares m+2(2m)=200. The ratio 33.8 is a preparation-operation ratio, not an elapsed-time prediction. Moving nodes, beta-dependent panel counts, steep tails, and threshold splits remain state-dependent and are recomputed for every changed cell.

## C4. Implementation and resource boundaries

- Modify only this research adapter, its additive native module/hook, tests, runner, and research delivery artifacts. Preserve every original native baseline byte and all VigilODE source bytes.
- Preserve current default invocation and public API behavior. Add explicit `--native-eval legacy|cell-cache` selection; default `legacy`. Optimization is actually usable via `cell-cache` without editing physics code. A research options constructor on Budget or equivalent additive API is acceptable.
- Optional `--profile` may collect charged RHS attempts, occupied-cell preparations, node visits, and exclusive preparation/rates/provider/other durations plus inclusive Jacobian time. Profile-off measurements must not execute fine-grained clocks. Do not confuse inclusive and exclusive times or library RHS counters with FD replay attempts.
- Cache APIs must reject wrong shape, stale unchanged-cell state/support, wrong changed-cell identity, or inadmissible perturbations. Cache lifetime/geometry provenance should be enforced by construction; no unsafe global cache.
- Keep the exact FD epsilon, central/one-sided formula, fatal-vs-domain classification, immediate fatal stop, charged attempts, resource caps, transactional rollback, solver coefficients/tolerances, GL2 births, native rates, EOS, and event ledger unchanged.
- No new general solver, analytic Jacobian, approximate rate table, fast math, reassociated reduction, or whole-pin upgrade in this implementation. Structured Schur, SIMD, and threaded LU remain comparative design candidates until their own correctness/performance evidence exists.
- Host is AMD EPYC 9V74, 8-CPU quota, 8 GiB RAM. Reuse the single local toolchain/cache/build target; preserve the immutable baseline executable separately before rebuilding the task-owned candidate tree. No clone/worktree, system/profile change, network dependency fetch, or expensive unrelated campaign.

## C5–C7. Finite verification and acceptance

Implement the cache plus an explicit comparison route. Preserve the old seven focused tests and add tests tied to the actual remaining risks:

- Full vs cached RHS/Jacobian at the real seeded native state, including gas perturbations and every photon coordinate; include empty support and a delta cell to exercise 4D/5D coordinates.
- Actual threshold-spanning / steep-support or near-boundary native preparations to show changed-cell nodes are recomputed; reject a deliberately stale unrelated cell or support change.
- Domain-only FD fallback and fatal resource/native errors remain distinguishable. Verify a failed cached chemical candidate leaves physical state and ledgers unchanged while charging attempts.
- Counters distinguish expected preparation savings from unchanged FD call count. Tests must not substitute a manufactured ODE for the native callbacks.

One focused release test pass (up to 120 s) and one cached native correctness matrix covering all 19 existing settings (total budget 120 s, per case 30 s) are authorized after build. Compare against original baseline/archived raw at identical settings with a finite-aware recursive comparator. Identity of scientific floats is a strong diagnostic expected from preserved operation order, not a general scientific acceptance rule. Any mismatch must be reported with actual path/max absolute and scaled error and interpreted against the existing atols, native stage residuals, endpoint closure, electron and energy/event identities. Never silently widen a tolerance or drop a channel. If meaningful differences occur, stop and return evidence to root for a concrete repair decision.

## C8. Matched-accuracy performance experiment

Use `fixed radau 16`, `birth radau 16`, and `disabled radau 16`, 8 energy cells, 8 angular cells, one transport thread, unchanged Newton atol=1e-13/rtol=0 and all other CLI settings. No physics-resolution enlargement is needed for this optimization claim.

1. Preserve one unchanged-binary native output for each of the three settings and source/binary/command/stdout/stderr/exit receipts.
2. With the candidate binary, run profile-on legacy and cell-cache once each on `fixed radau 16`. These are attribution observations, not the speedup samples.
3. With profiling OFF, one warm-up for each variant then five interleaved measured pairs for each setting. Alternate order AB/BA. Pin the entire case process to one actually allowed CPU. Do not run simultaneous competing builds/benchmarks on that CPU. Record native wall, process wall, peak RSS if available, binary SHA, affinity and counters. Stop family on failure; preserve every sample, do not cherry-pick.
4. Report median and range/IQR, all paired ratios, actual work counts, and code/binary identity. Require same completed physical results and ledgers before calling a speedup scientifically admitted for these settings. If timing is noisy or slower, publish that outcome honestly; do not infer a universal speed theorem.
5. Coarse parallelism: after serial correctness succeeds, a bounded runner may execute the independent three-setting batch with workers=1,2,4 (each task remains single-threaded, distinct assigned CPU, no nested worker pools). Use one warm-up batch and three measured batches per width. This measures batch throughput, not acceleration of a single history. Max live children 4, per-case 30 s, total 90 s. Stop/preserve failed children and record whole batch wall and child receipts. This is optional only if it fits the finite overall task budget; it must not delay publication of the verified cache.

Implementation/build/serial evidence budget: 15 minutes after Task B starts, with early diff/status within 5 minutes. One concrete compile or regression repair is allowed; substantive criteria changes return to root. No open-ended profiling or repeated optional testing.

## C9–C10. Admission and delivery

An independent Astra agent that did not implement the change will inspect the actual diff and raw outcomes once. Root retains scientific admission. Publish usable source and runner as normal GitHub files, update PR 198 without merging, and save a stage checkpoint and final evidence to both established Drive and Dropbox locations with whole-file readback hashes. Record each C-stage status and actual backup/publication identifiers. No successful upload, compile, NCP run, or performance result may be inferred from a listing or intended command.

All earlier scientific HOLD claims persist: no source-on all-channel order, uniform-stiffness, general positivity, CaseB/fullEoR/signed-Bianchi, positive-CMB/nonzero-boundary, or continuous/global certificate promotion. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`. This optimization may be admitted only for its actual finite equivalence and measured cost evidence.
