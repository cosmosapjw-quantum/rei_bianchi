# REI ISO-COUPLE P1: source-native H/He/D spectator CX finite-time

Standalone bounded theory + Rust implementation checkpoint (2026-10-17 KST). `physmath-research-loop` R1–R10/C1–C10의 구조에서 이번에 필요한 local derivative, construction, tests, sample convergence and handoff만 수행; 다른 단계들의 전역 과학 입장은 변경하지 않음.

Start:
1. `docs/THEORY_ISO_COUPLE_KO.md`, `docs/IMPLEMENTATION_HANDOFF_KO.md` and `docs/REVIEW_AND_NEXT_KO.md`
2. `rust/rei_iso_couple_reference/src/mixture_coupling.rs`, `src/mixture_eos.rs`, `owner_src/`
3. `contracts/ISO_COUPLE_CONTRACT.json`, `contracts/DAG_PROGRESS.json`, `evidence/convergence_campaign.csv`
4. `scripts/RUN_STAGE.sh` with offline Rust 1.94.1; no local Codex/NCP required.

The 8 imported `owner_src/*.rs` files are byte-identical Git blobs to PR150 `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7` and were recovered from the user's previously saved C07 archive. Minimal HHeModel constants in src/lib.rs are the exact two values selected from the original source and do not implement a substitute atomic model. Fixed H/D rate functions, DAtomicProvider, Verner cross sections and Savin fits are the actual source code. The finite-time path integrates **CX only**, not photoionization or competing H/He thermochemistry. Private physical thresholds are never invented; all demonstration values are clearly manufactured.

Publishing branch is additive and does not alter original production owner source. Remaining blocker: `ISO-COUPLE` full original DAG depends on `BI-SIGNED`, which is HOLD.
