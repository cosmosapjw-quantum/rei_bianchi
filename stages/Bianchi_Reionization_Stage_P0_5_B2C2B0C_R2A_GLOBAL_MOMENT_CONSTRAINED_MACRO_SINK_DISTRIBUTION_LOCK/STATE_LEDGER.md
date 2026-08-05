# R2A state ledger

1. The recovered repository base was verified at commit `12f4cd5b31bb3d45eabbc2343057fd995b15dc72`.
2. B2C2B0A, B2C2B0C, and B2C2B0C-R1 compact artifacts passed registry SHA-256, ZIP CRC, and internal compact-manifest checks.
3. The external `rec_bianchi` HEAD probe returned `REMOTE_UNAVAILABLE`; no surrogate or adapter review was started.
4. The durable pre-calculation scaffold is reproduced byte-for-byte under `state/PRECALC_SNAPSHOT/` and verified against `state/PRECALC_MANIFEST.json`.
5. `ATTEMPT_0` preserves the pre-calculation initializer self-manifest bug. `ATTEMPT_1` preserves the ZIP suffix ambiguity failure before input loading. Neither produced scientific output.
6. The final calculation produced 30 core projection cases and 540 macro rows. All core KL/KKT/moment/zero gates passed.
7. SymPy exact identities plus Decimal(80) imported-data checks and an independent validator passed.
8. Native Wolfram executables were unavailable; the `.wl` reproduction script and exact fallback are durable.
9. R2B is authorized with the tau=10 Myr all-case feasibility witness; tau=100/300 Myr failures remain open sensitivity constraints.
