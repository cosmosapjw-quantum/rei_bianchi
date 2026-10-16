# Actual failures retained

1. First run `cargo check --offline --locked` failed because newly created crate had no `Cargo.lock`; generated lock with `cargo generate-lockfile --offline`; subsequent check PASS.
2. First 18 regression tests: 16/18 PASS. One expected free-electron count was hand-calculated as 10 rather than 11 in 13-state all-ones model. Another expected a negative temperature when it had exactly 0 thermal energy. Corrected both. **Actual physics improvement**: new event map rejects Savin rate-domain crossings at both nonzero-event endpoints, and refuses wrong rate-source identity.
3. First `eos_probe` exited with RateSourceMismatch after previous source-id guard was strengthened; changed probe to carry `Savin2002::SOURCE` automatically.
4. `rustfmt` on lib.rs followed `#[path]` and changed frozen `deuterium_thermal_charge_exchange.rs` formatting (20618→24556 bytes). Restored from original Dropbox byte snapshot, after which all four original owner blob hashes matched. Final code format commands target only new files. Source identity validated AGAIN after cargo test, clippy and formatting.
5. Unmodified original source's one preexisting Clippy `needless_range_loop` is suppressed **at the imported module declaration only**, not edited in owner snapshot; final `cargo clippy --all-targets -- -D warnings` PASS for the standalone reference crate.

No full network native owner files altered. No outer CMB/FF/RCT/EoR claims admitted. No blind retries after unchanged input.
