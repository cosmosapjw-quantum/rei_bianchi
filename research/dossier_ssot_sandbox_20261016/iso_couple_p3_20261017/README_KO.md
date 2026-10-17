# REI ISO-COUPLE-P3 (2026-10-17)

P2의 H/He/D source-bound finite thermal chemistry와 PR150의 MD14/BB50k source, diagonal Bianchi-I exact Killing ray를 **샌드박스 독립 연구 crate**로 연결한다. 신규 positive source-age cohort absorber는 384개 원본 source energy/direction 셀을 각자 보존하고 원래 P2 64-bin 압축 비교기를 원형대로 함께 유지한다.

1. `docs/THEORY_ISO_P3_KO.md` : 연구 주장, Duhamel/phase-space/energy, spectral compression defects.
2. `docs/IMPLEMENTATION_HANDOFF_KO.md`: source-to-Rust binding, units and executable next action.
3. `contracts/P3_RESULTS.json`, `P3_SOURCE_CONTRACT.json`, `DAG_PROGRESS.json`, `SOURCE_IDENTITY.json`.
4. `rust/rei_iso_couple_p3`: Rust1.94.1 no-external-dependency crate, `src/positive_age.rs`, `src/source_age.rs`, all exact owner_src Rust module blobs, tests, examples.
5. `evidence/`: complete 32 row positive vs grey, historical 20 rows grey, 56 candidate group enumeration, 21 row transparent Killing comparator, longer positive time attempt partial 39/40 (not scientific PASS), Rust test and Clippy logs, plots.
6. `scripts/RUN_STAGE_P3.sh`: staged verify/compile/evidence regeneration; `scripts/analyze_results.py`: claim-scoped scientific ledger checks.

Production not changed; original PR171 age/spectral/time HOLD remains. PR 150,181 source SHA protected. No Codex/NCP/local HPC. New subagent capability was not exposed: `native_subagent=NOT_RUN` with one-owner serial fallback.
