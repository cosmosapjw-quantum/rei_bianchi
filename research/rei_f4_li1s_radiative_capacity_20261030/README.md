# REI/BASS193 Li I 1s measured vacuum radiative capacity (2026-10-30)

This is a **source-bound scoped physics atlas**, not complete F4 or accepted REI heating.

Reproduce: `bash VERIFY.sh`. Uses original immutable PR279 source-inclusive archive in `source/PR279_FULL.zip` (SHA256 fixed in `CONTRACT.json`). Read `THEORY_KO.md`, `REPORT_KO.md`, `results/RESULT.json`, `HANDOFF_NEXT_THREAD_KO.md`.

New data: 8,492 original Li I K-shell source-grid events with M1/2E1 radiative branch photon-count bounds, 193 epoch photon count/radiative energy histories, 3 × 8,492 threshold-capacity cells, two cumulative plots. 28 targeted regression checks, no new IVP.

The lifetime measured for the Li II 1s2s singlet is 503±26 μs, triplet 52.2±5.0 s. No measured spin yield or photon escape probability has been inserted. Actual thermal port remains UNBOUND. Source-model Li I 1s 64.39 eV effective core threshold is NOT silently changed to an atomic-level NIST rate.

Frozen REI DAG 33/88 working, 28/88 central, F4 4/7, canonical Δ0. Historical PR279 and PR278 remain unmodified; branch is isolated and draft-only.
