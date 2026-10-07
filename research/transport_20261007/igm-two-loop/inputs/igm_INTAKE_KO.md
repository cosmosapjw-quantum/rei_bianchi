# IGM branch fresh intake — 2026-10-07

## Source identity and scope

- Repository: cosmosapjw-quantum/rei_bianchi; branch `forward/rem-hhe-igm-20261006`.
- Fresh branch and PR84 head: `39c39eab1cc2f1a215723680accc123e67ef13b6`; actual commit tree `a281ad11d25c8a298d1a0e7f59ca596da0a1b4a4`.
- Latest commit at 2026-10-07 11:38:32 UTC is the additive SYNC03 return. Scientific implementation remains parent `a9aea514e086fec6d50cdf14496ff46054cc895e`.
- PR84 remains open/draft with base `forward/rust-reion-kernels-20260922`. A new change intended **for** this IGM branch should use this branch as the new PR base; PR84 itself targets the parent kernel branch.
- Full recursive tree is non-truncated. No applicable root/research/production AGENTS.md exists; the sole AGENTS.md is an archived BASS_HE source copy under docs/fastest_track_chat.
- Seventeen exact remote source/document blobs are saved in source/ and checked against Git blob IDs; SOURCE_MANIFEST.json binds bytes and SHA256. No implementation or remote mutation was performed by this intake.

## Current scientific blockers

1. Long FLRW z=12→10 remains failed: p64/p128 independent Radau histories pass their own budgets but fail 8/37 protected field comparisons. Worst out_E allowance ratio 1362.1124, out_N 335.1653. Whole-node lower-boundary transfers cause spectral grid-phase staircases. No later branch commit fixes this.
2. Continuous-boundary V2 only admits the selected bounded pure-radiation control matrix. It does not constitute projected/coupled multistep transport. Its 512-subdivision opacity control passes 1e-6; 64/128/256 are retained failed candidates.
3. Short coupled midpoint resolves the selected tiny-interval temporal comparison at m16→32 and m32→64, all37 fields. It does not fix long history: scope is Δln(a)=2e-4 only. Original m4→8 and m8→16 work_E failures persist as history. Exact Radau peak-array accounting remains unverified but address-space limit was enforced; this resource-accounting gap is separate from numerical reference admission.
4. Projected two-moment panel transport is mathematically designed, not implemented. V2 lacks closure restriction moments for all front/ordinary closures, shared-scale authoritative tail evolution, and moment-preserving projected multistep wiring.
5. Source-off tails are an immediate blocker, not a distant edge case. With the unchanged actual initial gas/source, λ_HI≈1.366273e6 per ln(a). An interior wake has log f≈−817.21 by Δs=6e-4 and −1090.46 by 8e-4. V2 characteristic explicitly rejects authoritative zero-readout tails. Ordinary β±128 shape coverage can also fail across a wake of width8e-4.
6. Physical export begins only beyond Δs=ln(13.7/13.6)≈0.00732604 for this fixture. A four-base-interval run to8e-4 necessarily has exact zero outflow and cannot demonstrate physical export-onset correction.
7. Source-free hot/strong/cold controls and physical REC→REI handoff remain separate unresolved paths. They need not block a bounded transport primitive advance; replacing current physical fixture to evade tail rejection would change the problem.

## Production versus research implementation

The live production crate is rust/rei_microphysics. The released implementation delta at the preceding numerical checkpoint is exact transaction-local sigma caching in igm_photo.rs and igm_step.rs, with atomic_provider test counters. The 250-file transport_20261007 checkpoint is an isolated research tree and adds no production source/default changes.

`short-hhe-midpoint/Cargo.toml` uses the production crate as path dependency, while src/lib.rs imports the unchanged V2 primitives by relative path. Its persistent Grid is characteristic sampling over one tiny interval, not the intended two-moment panel bridge. Its normal-only product helper and V2 try_add_scaled reject unsupported nonnormal owners. Inventory::LogTail is a classification, not operational tail evolution.

## Recommended ordered loop

**Loop1:** additive reusable panel restriction + authoritative tail primitives, with actual source-off witness and moment-exact positive stock quadrature. Preserve V2 as the negative control. This implements explicit gates P1–P4 in projected-radiation-bridge-theory/TEST_FIRST_AND_RESOURCES.md and closes a real prerequisite of the long-history replacement. Minimum acceptance: exact-input moment/mean checks, physical empty versus positive tail, exponential (not BE) attenuation, source restart, weighted owners and dimensional underflow bounds, rollback on rejection; no posthoc weight repair, floor, or residual-assigned owner.

**Loop2, dependent on loop1 evidence:** prescribed-gas projected panel integration with splits/merges and continuous swept boundary, comparing against fresh-point unprojected replay under the same source/rate/time partition. This isolates accumulated closure bias from quadrature and time error. A left-front family y exp(βy) is a concrete mathematical/physical extension for the actual initially empty lower trace before export onset; it requires its own exact-input tests. If scope/resources permit, one→four physical frozen-stage intervals provide a source-bound bridge. Do not automatically claim nonlinear coupled four-step or full z12→10 accuracy from these controls.

Keep ongoing coupled/history ownership separate, and publish the scoped implementation plus ready-to-run next gate rather than altering production boundary defaults before 37-field validation.

## Frozen acceptance and executable paths

- Full original field allowances: fractions1e-6+1e-3|ref|; Γ1e-22+1e-3|ref|; energy1e-20+1e-3|ref|; photons1e-8+1e-3|ref|; temperatures1e-6+1e-3|ref|. Retightening factor0.1.
- Number ledger allowance1e-10 max(emitted_N,1e-10). Energy allowance1e-10 max(emitted_E+work_E+escape_E+|cmb_reservoir_E|,1e-20).
- V2 exact-input normalized mean5e-13 in admitted support/domain; component quadrature1e-6; characteristic kernel oracle3e-12. New tail readouts require |residual|+underflow_bound≤original allowance, with cumulative caps1e-20 photons/H and1e-30erg/H.
- No generic gas positivity, all-field order2, continuum/global certificate, production/observational EoR claim follows.

From a complete disposable repository tree: `python research/transport_20261007/replay_saved.py`; `cargo test --manifest-path research/transport_20261007/short-hhe-midpoint/Cargo.toml --offline --release -j1 --lib --tests -- --test-threads=1`. Standalone V2: rustc --edition=2021 -D warnings -O src/tests.rs, run inside disposable experiment directory. Historical wrapper `.py.txt` is not a supported runnable publication entry point.

Historical (not predictive) total numeric costs: V2 CPU37.0622s/wall37.3432s including its attempts; midpoint CPU67.5611s/wall67.9466s including its attempts. Proposed new primitive envelope120CPU/180wall,512MiB address space,32MiB output including builds, one numerical process/thread; compilation separately measured. New coupled4-interval feasibility needs its own envelope, not extrapolation from these totals. Resource cap4096 denotes simultaneous distinct integration sites in the proposed bridge, never total scalar buffers.

No new scientific test was executed during this read-only intake. All reported scientific results above are source-admitted prior results.
