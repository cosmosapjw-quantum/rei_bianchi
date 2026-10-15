# REI AX03 C9: real native physical-clock repair, unmerged

Actual Rust source changes live in this **isolated REI branch**, not in the original owner checkout:

- rust/rei_microphysics/src/axbi_background.rs: local_increments(from_a,to_a), proper_time_increment; source-exact mean H and shear, log1p physical interval, normalized positive 4-node Gauss-Legendre, <=0.0028 x panels, compensated scalar reductions, no dynamic buffers.
- rust/rei_microphysics/src/axbi_driver.rs: Driver::tentative now uses new physical proper-time-increment API, not absolute time subtraction. Explicit new background numerical method label in new-run metadata.
- rust/rei_microphysics/tests/axbi_c9_native_interval.rs: real binary64 input MP80 90-fixture, positivity, signed q, SAME_H counterfactual, old native catastrophic cancellation witness, invalid input, full-interval reference and actual incompatible old-source run() negative guard. Rust tests/fixtures/axbi_c9_clock_mp80_90.csv is source-fixed.
- rust/rei_microphysics/examples/axbi_c9_clock_benchmark.rs: 90-interval actual release compiler benchmark of original two-Simpson4096 cumulative subtraction vs local Gauss4, plus actual 2/4 std::thread parallel paths. Model and source formulas matched; old method demonstrably inaccurate at tiny endpoints.
- research/axbi_goal_20261014/native_clock_c9_20261015/evidence/: commands, original vs changed source identity, actual tests and local runtime; report and C10 next-stage scientific gate.

Real source AX03 source lock SHA: 46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0. Parent REI PR123 original source commit 602f9726858b8a183c259ac7eae9fc11d1d7fb99. Original owner checkout kept unchanged.

All native release tests verified with external CARGO_TARGET_DIR, scientific solver NOT launched:

    cd rust/rei_microphysics
    CARGO_TARGET_DIR=/tmp/axbi_c9_native_target cargo test --release --offline --test axbi_c9_native_interval -- --nocapture
    CARGO_TARGET_DIR=/tmp/axbi_c9_native_target cargo test --release --offline --test axbi_driver --test axbi_background --test axbi_resource_continuation --test axbi_q_event --test axbi_q_closure --test axbi_q_reference
    CARGO_TARGET_DIR=/tmp/axbi_c9_native_target cargo run --release --offline --example axbi_c9_clock_benchmark

New Rust method real MP80 90 input max dt error 2.22e-16; native old cumulative endpoint clock worst 124% on90 vs MP80, 70 bad >1e-8, and at q=+.01, a=.1 nextfloat physical dt3.570670062366s vs original Rust6s. Median90 input component latency in source-matched release benchmark ~10.2us new local method vs 19.95ms original two uncached cumulative Simpson4096, not whole native solver speedup and not a comparison with existing REI stable Rust table. 2/4 Rust threads are slower and produce bitwise identical results. Keep serial.

The original full AX08 signed science checkpoint CANNOT be resumed under this changed numerical source: normal run() checks compiled source_identity.txt before read_checkpoint. The low-level Driver::read_checkpoint() itself is not a full source authority gate. Original H/He chemistry, cosmology, q family, energy/opacities, and exact source provenance were not modified; this branch still requires independent new science allocation, complete signed history and AX11/AX12 errors before observational or publication admission. No automatic merge or current-run launcher start.

The detailed science derivations, evidence limitations and next action are in REPORT_KO.md / NEXT_C10.json.
