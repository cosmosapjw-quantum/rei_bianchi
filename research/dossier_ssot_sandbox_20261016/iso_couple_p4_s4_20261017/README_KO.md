# REI ISO-COUPLE-P4/S4 (2026-10-17)

**Scoped constructive theory and offline Rust 1.94.1 code**. Parent: source-locked Draft PR #185 exact `d239fc2e5e9402801f3cca2523425a9ddf2a1504`. Frozen production PR150 `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7` is read-only.

## New objective

Original P4/S3 photon GL birth-time transport and source-native chemistry remain intact. Add (1) exact bracketing of HI/HeI/HeII/D photo threshold crossings along each axisymmetric Bianchi-I Killing ray; (2) positive root-split subslab absorption; (3) bit-exact per-gas-step opacity memoization, reused geometry snapshots by birth time; (4) opt-in **exact f64-zero-only** source-age retirement. No lossful nonzero cohort compression, no production merge.

Read `docs/THEORY_NUMERICS_KO.md` for explicit conditional proof and scientific limitations. Source and claim registry in `contracts`; executed Rust/independent SciPy results and failure/repair in `evidence`.

## Reproduce

Use user's frozen Rust 1.94.1 toolchain, or install equivalent under `/mnt/data/rust-1.94.1-prefix`. Unpack and run `bash scripts/RUN_STAGE_P4_S4.sh` in this folder. Native cargo offline locked. Requires Python with SciPy for separate photo oracle. Time-seconds, energy eV, number per reference-comoving m³, species proper m^-3, SI J.

Executed: **91/91 Rust tests, strict Clippy, scoped rustfmt, 12/12 immutable original owners**, live photo-edge and H/He/D ledger, independent SciPy comparator, 12-step exact-zero state campaign and 3 rotated timing runs at N4/8/16. No original P4/S3 Rust files edited except new `src/lib.rs` appended public module declarations in isolated copy; original PR branch not edited. Previously separate source remains unchanged by byte.

**Admitted:** `P4/S4 PASS_SCOPED` only; actual full FLRW/BI EoR/Thomson, physical BASS on-shell geometry, nonzero age compression, global accuracy gates remain HOLD. Native subagents not exposed, serialized sandbox work. Dropbox write not implied without destination.
