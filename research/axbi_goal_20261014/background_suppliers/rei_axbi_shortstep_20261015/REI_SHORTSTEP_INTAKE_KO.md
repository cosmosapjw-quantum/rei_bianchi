# REI AX03 C8 short-step intake (opt-in research code, production driver unchanged)

This is an additive, source-frozen cancellation-resistant Bianchi-I proper-time supply, stacked directly on original REI BASS AX03 background supplier PR121. It does NOT change Rust AX03 production source, q-reference campaign, native chemistry, or the actual AX08 science solver. Original source clock is elapsed SI proper time from mean redshift20 to4.

- New shortstep.py exposes physical local Gauss4 proper interval (Delta t, Delta b), 501-node positive-derivative Hermite *factored increments*, cached Gauss weights, vectorized multiple interval physical integration (default 1 worker), optional 2/4-thread experimental path, exact Killing photon delta-log energy and angle. The supplied actual Rust stdlib-only GL4 physical reference is rust_shortstep.rs.
- Source family and units are unchanged: five density-fixed q0,+/-0.005,+/-0.01 and a separate +0.01 SAME_H counterfactual; source lock SHA 46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0.
- Independent MP80 oracle for 90 exact binary64 endpoint intervals (6 families x3 points x5 requested widths) gives physical Gauss4 max time relative error2.29e-16, Hermite501 max5.79e-10, original cumulative time subtraction worst124% error. Actual Rust source-identical standard library GL4 max time rel2.29e-16 and db rel5.10e-16 on all90. Wrong q rejected exit3. One ULP above a=.1 at q=.01 yields dt3.57067006236636s vs cumulative subtraction4s.
- Actual same-input 90 interval benchmark medians (background setup excluded): Hermite0.466ms, grouped vector GL4 one worker0.636ms, sequential naive accumulated subtraction29.11ms. 2/4 worker threads slower. These timings are for short source intervals, NOT whole native REI numerical solver.
- Original REI performance/background_table_001 reported 356 actual SHORT_STEP_SUBTRACTION_HOLD records in driver-style accumulated subtraction. Its own tested stable Rust Table.increment already achieved2.38e-11 sampled relative accuracy. This C8 does NOT supersede the original stable Rust table or close the actual driver integration hold simply by shipping a separate source module.
- Read REPORT_KO.md, evidence/MP80_SHORTSTEP.json, evidence/RUST_GL4_90.json, evidence/BENCHMARK_VECTOR.json, evidence/CLOCK_SHIFT.json, evidence/REI_OLD_CLOCK_HOLD.json, source-bound parent supplier PR121 and NEXT_C9.json. No outside observable ionization claim, no native N-body/global H/He error certification.

Actual independent REI worktree (not owner checkout) reproducibility:
python3 -m unittest discover -s research/axbi_goal_20261014/background_suppliers/rei_axbi_shortstep_20261015 -p test_shortstep.py -v
python3 -m unittest discover -s research/axbi_goal_20261014/background_suppliers/bass_20261015 -p test_axbi_supplier.py -v
cd rust/rei_microphysics && CARGO_TARGET_DIR=/tmp/reix_ax03_new cargo test --release --offline --test axbi_background

Extra native Rust positive and negative parity was executed against the 90 source intervals, not merely imported logs. Evidence RELOCATED_NATIVE_RUST_90.log and REI_SOURCE_NATIVE_AX03_6.log.

Future C9 or a separately approved controller-specific patch must locate the actual driver callsite t(a2)-t(a1) and redirect to an explicit positive dt operation with physical time-clock/error acceptance. Do not promote a standalone table or wrapper into native scientific admission by writing a PR description.
