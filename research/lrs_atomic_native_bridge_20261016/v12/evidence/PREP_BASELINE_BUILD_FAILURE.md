# Initial frozen-owner build failure

Command: `cargo test --manifest-path research/lrs_atomic_native_bridge_20261016/v12/native_owner/rust/rei_microphysics/Cargo.toml --test axbi_driver`

Exit: 101.

Cause: the first source snapshot included `rust/rei_microphysics` but not source-boundary `include_str!` contracts. Rust reported missing files under `research/flrw_jacobian_columns_20261016`, `research/bass_source008_20261016`, `research/bass_source007_20261016`, `docs/fastest_track_chat/REI-AXBI-GOAL-20261014`, `research/axbi_goal_20261014`, and `research/flrw_covariant_transport_20261015`.

Repair: archived those exact contract paths from frozen PR150 commit `6ea2b1b4b3875c9163cafc45efe720afded43fc4` into the isolated native owner snapshot.

Identical command rerun: exit 0; `tests/axbi_driver.rs` passed 13/13. Existing Rust 1.99 warning: `AtomicUsize::fetch_update` is deprecated in favor of `try_update`.
