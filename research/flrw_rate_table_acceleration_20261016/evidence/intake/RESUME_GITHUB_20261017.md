# Resume intake — 2026-10-17 UTC

Current integration PR150 is still `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7`; default main is `ae3402713c4b6530ab2b27f008f5f5d5c6a999ed`. All eight task-owned runtime/test files were fetched at the current integration commit and equal local Git blobs. No production edit or scientific rerun occurred.

## Rate-table continuation already published

PR177 `2f4103968cc26061a62dc7931c27c2fe86d75cd8` and PR178 `1579a5e4b0c3093bfd6942cc4914e29a00a71978` restore our exact C07 archive and preserve the same H/He source blobs. Their changes are additive research files, with no overlap in the eight owned paths. These research branches diverge from the integration branch; use their evidence without replacing the integration source.

PR177 reports 20,510 samples, maximum individual coefficient error 3.8172670147488274e-7 under 1e-5, exact-zero/mask checks, and Rust1.94.1 results. PR178 corrects the serial-versus-parallel comparison: at N262144, matched four-worker median speedups are 1.607568396 ordered and 1.370923361 random; median build break-even is about1.844m/3.156m queries. Keep this new runtime separate from original C6 measurements and do not infer whole-solver gain.

PR178's 36-state RHS and sampled coefficient decisions are reusable. Its derivative scan max absolute log-slope difference0.0065711347474461945 keeps derivative/Jacobian use HOLD; no derivative API was part of our unit, and this statistic is not the proposed scaled derivative metric. The standalone C10 policy is tested advisory code, not deployed. Its `REVIEW_DECISION.json` explicitly says independent actor NOT_RUN_NO_NATIVE_DELEGATION, so fresh independent admission is still missing.

Exact imported artifacts are in `upstream_pr177/` and `upstream_pr178/`, including all three C9 raw benchmark logs. Their Git blob identities and original URLs are in the JSON companion. A serialization-only extra final newline was removed, and10/10 imported documents now match their exact source Git blobs. No upstream test was rerun.

## Scientific frontier and handoff

The old instruction to derive mixture EOS from scratch is stale: PR179 already supplies a13-state mixture EOS; PR180 supplies finite-time He-spectator thermal-CX reference; PR181–192 continue coupled H/He/D source-age transport and controls. These remain scoped research results. Original pure-H/D production spectator rejection remains intact; local dossier17/native13/Li8/union21 distinctions still hold, and no full21-state Li network is admitted.

PR192 `14837d300d7845bbe50bc7068f058e1591c581e6` has79source files and `nested_budget.rs`. PR193 `267b6e0d7baa416d94e15560e1e61e60132af5b4` instead targets a distinct78-file `budget_native.rs` receiver and adds an uncompiled BASS whole-cell guard. They must not be conflated. PR193's local next action is to compile its10authored tests, then qualify the full donor and bind geometry.

A separate non-PR atomic lineage is further ahead on actual BASS121 H/He/D joint references: RUN09 branch `research/rei-atomic-run09-source-support-20261017`, commit `86ffbea52e3a786ef360cf1434b8e3504e2dfdbf`. Its exact README and DAG are preserved in `upstream_run09/`. It reports completed40/80/160/240birth support comparisons and scoped PASS without a continuum bound. Its next node is positive spectral refinement of the first H/D-edge source cell, using r4birth support as a bounded input while keeping BASS121/atomic/IC/GL8 fixed. Li/Be nuclear T1–T8, full isotope coupling, spectral/angular convergence and Einstein feedback remain HOLD. Neither branch's successor should be started automatically during this rate closeout.

## Bounded donor intake

- BASS_HE74: source-cut pilot metadata still lists native A/B pending; no change to our rate source.
- WU088_HH108: finite-P/Q first Born Abel result; physical HH rate remains HOLD/OFF.
- bass_cr79: manufactured photo-only midpoint-exposure improvement; not native full Grackle/PreparedAbsorption integration.
- BASS169: first-order massive-FD shear response; do not double-add stress to an already prescribed sourced history.
- rec_bianchi100: original-C h/h2/h4 sensitivity; no automatic REI initial-condition adoption.

Finish this unit by consolidating reused evidence, independently reviewing the scoped claim, and closing its handoff. Preserve historical NCP deadlines and costs; no replay or allocation reset. Remote backup completion is a separate parent task; this intake does not convert PR backup claims into new readback verification.

