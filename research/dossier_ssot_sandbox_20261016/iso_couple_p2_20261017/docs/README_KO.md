# REI ISO-COUPLE-P2: source-bound finite-bin H/He/D bridge

Constructive R5/R7/R9 scientific work and bounded C5–C8 coding, 2026-10-17.

- Physics: `docs/THEORY_AND_NUMERICS_KO.md`
- Machine contracts: `contracts/ISO_COUPLE_P2_CONTRACT.json`, `contracts/DAG_PROGRESS.json`, `evidence/P2_RESULTS.json`
- Code: `rust/rei_iso_couple_p2/` standalone original-modules-import plus new `src/full_network.rs`, `tests/iso_couple_p2.rs`, `examples/p2_campaign.rs`.
- Evidence: 56 actual Rust tests (20 P1 ISO-EOS + 16 P1 CX + 20 P2), clippy -D warnings PASS, original 10 Git blob matches, 45 actual convergence runs. Historical initial fail and targeted repair logs retained.
- Scope: fixed-volume manufactured 70/30 eV photon bins, Case A escaped recombination, Grackle/Verner/Savin coefficients, no cosmological injection or expansion. Native full EoR HOLD.

**Next:** ISO-COUPLE-P3 source photon births & Bianchi covariant age/time binding; `BI-SIGNED` prerequisite still HOLD. GitHub branch additive/draft only; no production source changes.
