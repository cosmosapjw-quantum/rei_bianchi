# Temperature-rate coefficient and point-RHS report

C8 consolidates existing execution. No scientific build, test, benchmark or native campaign was rerun during this consolidation. Local Rust 1.85.1 results and source-matched upstream Rust 1.94.1 results are separate cohorts. Fresh independent actor C9 is **PASS_SCOPED** (`evidence/C9_INDEPENDENT_REVIEW.json`), with root admission of coefficient/prepared-point and conditional Li6/Li7 number-component scope. Upstream PR178 itself explicitly recorded `NOT_RUN_NO_NATIVE_DELEGATION`. The standalone upstream Rust opt-in policy is externally reported and advisory here; its Rust code is not independently admitted by this review.

## Implemented behavior and numerical scope

The default point path prepares the unchanged direct H/He coefficient bundle once and reuses it in the original event and energy ledger. Tables are explicit opt-in. Prepared values bind the exact EOS temperature, and D consumes the same prepared H coefficients under its existing explicit H-equality approximation. Uncertified branch, zero, subnormal and sign cells use the direct evaluator; inputs outside the provider domain reject. No derivative API, automatic driver selection or new thermal closure is introduced.

The preserved local suite passed **9 tests: 5 H/He and 4 Li**. Its 21 H/He temperature/composition fixtures are **21 fixture states, not a 21-species network**. Reused R7 H/He evidence at 65,537 nodes has sampled maximum relative error **3.8387697880837957e-7** over 421,431 queries; the initial 8,193-node failure remains recorded. Local Li uses 8,193 nodes and 1,015 independent temperatures with sampled maximum relative error **1.1733732758756332e-6**. These satisfy the unchanged 1e-5 value target on its declared positive-normal scope and establish no continuous curvature or trajectory bound.

PR177, pinned at `2f4103968cc26061a62dc7931c27c2fe86d75cd8`, independently exercised the same coefficient source: 20,510 queries, maximum relative error **3.8172670147488274e-7**, with exact zero/mask checks. PR178, pinned at `1579a5e4b0c3093bfd6942cc4914e29a00a71978`, adds 36 fixed-source RHS states (worst event-ledger normalized residual 1.2272269344036022e-16). Its finite-difference slope diagnostic reached absolute log-slope difference **0.0065711347474461945**; value accuracy does not certify derivative/Jacobian accuracy. Derivative/Newton use remains HOLD.

## Local Rust 1.85.1 cohort

All 57 timings from the original C6 stdout are retained below: each row reports the median and min/max of all three samples. Ratios are baseline median divided by method median; point baseline is legacy double-direct, coefficient baseline is serial direct. Four-worker comparisons here include work sharing as well as evaluator changes.

| Distribution | Queries | Method | Median ms | Min–max ms | Baseline ratio |
|---|---:|---|---:|---:|---:|
| ordered_logT | 256 | direct | 0.088302 | 0.088081–0.139790 | 1.000 |
| ordered_logT | 256 | table_scalar | 0.033280 | 0.033149–0.161833 | 2.653 |
| ordered_logT | 256 | table_soa | 0.044326 | 0.037416–0.064406 | 1.992 |
| ordered_logT | 256 | table_parallel4 | 0.396974 | 0.229383–0.626068 | 0.222 |
| ordered_logT | 8192 | direct | 3.345947 | 2.878182–3.409307 | 1.000 |
| ordered_logT | 8192 | table_scalar | 0.956814 | 0.932387–0.962212 | 3.497 |
| ordered_logT | 8192 | table_soa | 1.381961 | 1.062191–1.805855 | 2.421 |
| ordered_logT | 8192 | table_parallel4 | 0.809909 | 0.775121–3.347095 | 4.131 |
| random_logT | 256 | direct | 0.109304 | 0.090996–0.342704 | 1.000 |
| random_logT | 256 | table_scalar | 0.054191 | 0.054141–0.054682 | 2.017 |
| random_logT | 256 | table_soa | 0.046971 | 0.046670–0.048743 | 2.327 |
| random_logT | 256 | table_parallel4 | 0.449904 | 0.334050–1.184530 | 0.243 |
| random_logT | 8192 | direct | 3.316118 | 3.059794–3.337470 | 1.000 |
| random_logT | 8192 | table_scalar | 3.352733 | 3.152984–5.979288 | 0.989 |
| random_logT | 8192 | table_soa | 3.328917 | 2.844531–4.876075 | 0.996 |
| random_logT | 8192 | table_parallel4 | 1.583382 | 1.564389–1.706977 | 2.094 |
| point | 1024 | legacy_double_direct | 1.883331 | 1.854348–2.180677 | 1.000 |
| point | 1024 | prepared_direct_point | 1.403362 | 1.355091–1.587203 | 1.342 |
| point | 1024 | table_point | 1.419978 | 1.416031–1.480468 | 1.326 |

Default prepared point evaluation is 1.342x the historical double-direct median. Table point evaluation is slightly slower than prepared direct in this cohort (1.419978 versus 1.403362 ms/1,024). At 8,192 ordered queries scalar lookup is 3.497x serial direct; at random temperatures it is 0.989x. Four-worker random lookup is 2.094x serial direct, while four-worker batches of 256 are slower. The data support conditional selection, with distribution and batch size kept explicit.

The reused R7 prototype construction cost is **0.109192622 s**; it is not a fresh C6 build measurement. The scalar grid payload is **8,913,016 B**, the complete table payload **9,109,624 B** (8.69 MiB), and the C6 process peak RSS is **18,724 KiB** (18.29 MiB). Process RSS is not incremental table memory. Indicative local break-even values are preserved per row in `coding_evidence/C8_LOCAL_TIMINGS.json`, using C/(direct seconds/query − method seconds/query); nonpositive savings have no break-even. Setup occurs explicitly once and can be shared with `Arc`.

## Upstream Rust 1.94.1 cohorts

PR177 reports three-sample medians separately: at 32,768 ordered queries scalar is 3.437x serial direct and four-worker table is 5.303x serial direct; random scalar is 0.842x, random SoA 1.005x, and four-worker table 2.505x serial direct. Its benchmark construction is 0.10438279 s; its independent accuracy construction is 0.119123867 s. These are separate measurements from the local R7 construction. PR177 JSON retains medians, but its raw inner timing samples are not part of this bounded intake, so no min/max is invented. The inherited hardcoded 1.85 compiler label is not treated as actual upstream compiler identity.

PR178 supplies the fair **four workers versus four workers** comparator. Each row below aggregates all three preserved run-level results; each run contains an internal median. This does not pool hosts, toolchains, sample sizes or distributions. Raw files are `evidence/intake/upstream_pr178/C9_RUN1.stdout` through `C9_RUN3.stdout`.

| Distribution | Queries | Speedup median | Min–max | Break-even queries median |
|---|---:|---:|---:|---:|
| ordered | 32768 | 2.124553 | 1.928861–2.160741 | 1,620,123.02 |
| ordered | 262144 | 1.607568 | 1.450020–2.053808 | 1,844,093.84 |
| random | 32768 | 1.066370 | 1.059831–1.138644 | 14,602,490.51 |
| random | 262144 | 1.370923 | 1.267570–1.374531 | 3,155,998.14 |

Per-run construction spans 0.132711501–0.149328278 s. At 262,144 queries, matched-worker gains are 1.608x ordered and 1.371x random, with median break-even approximately 1.84 million and 3.16 million queries. These support an advisory opt-in policy calibrated to the actual source, worker count, temperature distribution and workload. PR178 `OPTIN_POLICY.json` remains a tested standalone reference, without production binding. Its setup margin 1.5 and forecast net-speedup floor 1.1 are advisory policy choices, not new scientific tolerances.

## Lithium, dossier inventory and future integration

Li6 and Li7 each carry q=0…3 identities with separately conserved isotope nuclei. Their CI/RR/DR coefficients are elemental Voronov/Badnell source rows and require explicit `ElementalElectronicEquality`; `IsotopeResolved` returns typed `MissingSource`. Caller populations remain explicit. No isotope-native accuracy, default abundance, Li photothermal closure, nuclear evolution or cold CI extrapolation is claimed. Source-fit uncertainty and isotope-model error remain separate from interpolation error.

The dossier Eq. 1.15 has 17 entries; the current union appends four Li6 charges to reach 21. The exact map is `data/dossier_species_registry.json`; per-entry rate/primitive notes describe the Oct16 integration snapshot, and its Oct17 source-pinned overlay records later branches without changing indices:

| Zero-based indices | States | Implementation status |
|---|---|---|
| 0 | n | Existing bookkeeping |
| 1–2 | H1 q=0,1 | Existing point provider |
| 3–4 | D q=0,1 | Existing H-equality atomic model and separately scoped CX |
| 5–6 | T q=0,1 | Bookkeeping; no new atomic/decay provider |
| 7–9 | He3 q=0,1,2 | Bookkeeping; no new isotope thermal-rate admission |
| 10–12 | He4 q=0,1,2 | Existing point provider |
| 13–16 | Li7 q=0,1,2,3 | Typed conditional Li component |
| 17–20 | Li6 q=0,1,2,3 | User isotope extension, typed conditional Li component |

This inventory is not an activated coupled 21-state solver. Electrons, photons, molecules/negative ions, nonthermal injection, and Be/Li radioactive reservoirs retain their separate owners. The former pure-H/D CX receipt at `0a3bec74b4de61c9e95bf6727636c39cc970695b` is historical scoped evidence. It does not define the current frontier: newer PR179 mixture EOS and PR180 finite-time He-spectator CX evidence must be reused, with their production guards preserved. `evidence/intake/RESUME_GITHUB_20261017.json` records the immutable refs. Current RUN09 source-support evidence advances dynamic H/He/D reference work to positive spectral refinement at H/D edges; Li/Be nuclear T1–T8 and full 21-state coupling remain HOLD. Exact immutable intake records govern these distinct scopes.

Future Li photothermal integration still needs source-supported omitted CI bounds, RR/DR kinetic/emitted-energy moments, explicit BBN/time-origin/charge-state mapping and preserved omitted reservoirs. The low-temperature proposal and dossier reconciliation remain useful dependency records, with completed upstream EOS stages not repeated.

## Reproduction and resource boundary

`API_USAGE.md`, `build_focused.py` and the 67-file `focused_bundle` preserve the actual local verification context. Rust 1.85.1 focused compilation excluded only unrelated `joint_affine` declarations/reexports requiring later float APIs. All changed modules were built; a full local production crate build was not verified. Historical uncalled local driver context is not the current remote active driver. Upstream Rust 1.94.1 restored the source-pinned `joint_affine` donor; its original-crate strict Clippy warnings are inherited and do not make the local focused build a full-crate test.

Original local cumulative science usage remains **0.7098421649934608 wall s / 0.633306 CPU s** in `evidence/RUN_LEDGER.json`. Imported external executions are read-only reuse under their own historical budgets; they are not charged as new local runs or pooled with the local resource ledger. No NCP deadline, budget, observer, checkpoint, source run or production switch was changed. No SIMD, end-to-end speedup, full EoR, NCP64, global convergence or new cosmological history is admitted.

Requested roles are Astra high for contract/independent review and Sol high for mechanical implementation; observed runtime model identity is not exposed. The prior usage-quota interruption is a runtime interruption, not a numerical failure.

## Final handoff

R1–R10 and C1–C10 are complete within this scoped admission. C9 published at `bf492b3095fe78e9a7baff4bc2003129c52fe6e5`; `FINAL_PUBLICATION.json` carries the final C10 commit, archive identity and actual backup receipts. `RESTORE.md` and `CODEX_HANDOFF_PROMPT.md` provide automated source acquisition into the existing workspace and the next-lineage handoff. Review snapshot hashes are retained as the historical reviewed state; later factual status/receipt updates do not change the reviewed production bytes or numerical outputs.
