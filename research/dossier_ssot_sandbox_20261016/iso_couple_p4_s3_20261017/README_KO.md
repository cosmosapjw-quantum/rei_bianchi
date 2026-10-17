# rei_bianchi ISO-COUPLE P4/S3 (2026-10-17)

**Standalone opt-in Rust source-native reference**, staged from the verified P4/S2 archive and [upstream PR #184](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/184) source HEAD `4e82783f560d26589a646f64473359299ed9f977`. PR150 original Rust owner code and P3/P4/S2 reference sources remain byte unchanged.

## Actual objective

The P4/S2 photon birth-time slab assumes constant `j` and `κ`; P4/S3 resolves photons' **real emission times** via GL2/4, Bianchi-I Killing redshift trajectories and positive competing opacity microstep events. `positive_spectral.rs` adds opt-in positive D-threshold-split GL3 nodes within each original MD14/BB50k spectral owner cell. This retains exactly the original per-cell photon number but not an exact continuum spectrum or full chemistry-order claim.

See `docs/THEORY_AND_NUMERICAL_KO.md` and `contracts/DAG_PROGRESS.json` for derivation, units and claim gates. Production/PR150, active NCP, and historical checkpoints unchanged.

## Files and reproduction

`rei_iso_couple_p4_s3/` no-network Cargo.lock crate with frozen owner modules, P3/P4S2 retained paths and new `src/retarded_transport.rs`, `src/positive_spectral.rs`, `tests/p4_retarded.rs`, `examples/p4_{retarded_campaign,scalar_varying}.rs`. `scripts/RUN_STAGE_P4_S3.sh` verifies frozen source hashes and regenerates 30 actual native rows + 96 manufactured scalar rows **byte-identically**, then scientific analyzers. `evidence/` holds native and independent Python results, successful tests/clippy, errors, retained partial refinement and resource outcomes.

Default Rust installed by user-supplied archive under `/mnt/data/rust-1.94.1-prefix`; can point `RUST_ROOT` to an alternate offline Rust 1.94.1 prefix. Run `bash scripts/RUN_STAGE_P4_S3.sh`; execution is confined to an isolated crate. S1/P3 source, source SHA and frozen original owner are not modified by the script.

## Completion

New P4/S3 9 tests plus inherited 75 => **84/84 Rust tests PASS**, strict Clippy PASS and scoped rustfmt PASS. 30 native 2 cases×3 macro-step grids×5 modes; 6 additionally matched same-opacity comparisons; 5 completed higher-step rows (sixth timed out): total **41 unique fully completed Rust numeric rows**. Native number ledger max 5.348e-15, total-step energy max 5.786e-16. Scalar manufactured time-dependent reference final N64 GL4/m8 1.45675e-7 relative, observed p≈1.995, not full EoR solver order. Full P4 PARTIAL; FLRW-CONV, SA-01/02, BI-SIGNED, FULL_EOR HOLD. Never merge as full production.
