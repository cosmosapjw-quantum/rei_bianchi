# rei_bianchi | ISO-COUPLE P4/S5: bounded nonzero source-age photon tail (2026-10-17)

Sandbox-only exact-source additive research. Parent immutable Draft PR #186 SHA `88b0efea3f033ceb5663c1ae2ccd724a3a7c6375`; original production PR #150 frozen `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7` (12/12 byte-identical original modules).

## Exact result

New **opt-in** `rei_iso_couple_p4_s5/src/age_remainder.rs`: source-age photon cohort with positive but tiny weight may be skipped under explicit cumulative number, energy, **four species channel** direct-event budgets, with accounting of numerical omitted photons separate from photoabsorption. The model-independent direct omitted absorption-count bound per photon holds for any nonnegative opacity history; finite-horizon photon energy uses original axisymmetric Bianchi I Killing geodesic. This **does not certify nonlinear H/He/D gas-feedback errors, threshold-frequency inference, or native full-EOR observables**.

Contains original Rust 1.94.1 no-external-dependency crate, 9 new Rust tests + 91 inherited tests, deterministic source-native three-scenario comparison (`36 CSV rows`), four independent DOP853 fixed-opacity scalar controls, science validator, failure/repair chronology and execution contract. Strict all-target Clippy, changed-files rustfmt, complete clean restore test planned and receipts stored in evidence.

## Run

Install the exact Rust 1.94.1 in an isolated prefix, then 

`RUST_ROOT=/mnt/data/rust-1.94.1-prefix bash scripts/RUN_STAGE_P4_S5.sh`

Python SciPy for independent scalar check; no external NCP, local, Codex or internet needed. Reference-comoving photon number [m^-3], gas proper m^-3, time s, photon energy eV and J conversion. No energy/unit convention changed. The benchmark is short and all timings are sandbox-specific.

Claim: `P4/S5 PASS_SCOPED_DIRECT_REMAINDER_AND_GUARDED_RUST_COMPARATOR`. Full P4, SA-01/02, FLRW-CONV, BI-SIGNED, FULL-EOR HOLD. See `docs/THEORY_P4_S5_KO.md` and `contracts/DAG_PROGRESS.json`. **A speedup with mass-only budget can silently destroy minority HeII relative accuracy: the species guard is required for any scoped physical consideration.**
