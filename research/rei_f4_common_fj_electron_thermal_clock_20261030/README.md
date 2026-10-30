# REI F4: source-owned BASS193 F/J × conditional electron/thermal clock bridge

- Scientific work: reproduce frozen original BASS21 F/J for 193 saved epochs and original PR287 conditional first-flight 192 arrival intervals. No original IVP recomputation, no production mutation, and no native REI17 solver claim.
- Provenance: `source/` contains three byte-locked original source ZIPs; `results/` contains original-state-derived physical CSV, NPZ and five plots; `code/bridge.py` calculates and `code/plot_science.py` plots.
- Run from clean extraction: `bash VERIFY.sh` (requires Python, numpy, scipy, matplotlib), checks source SHA/ZIP CRC, targeted tests, outputs reproduced against original bytes.
- Governance: Working 33/88; Central 28/88; fast 4/7; auxiliary 1/1 scoped; F4 partial; production HOLD; NO_MORE_IVPS, NO_MERGE, NO_FORCE_PUSH, NO_BUDGET_RESET, AUTO_NEXT_NODE false.
- Git parent: rei_bianchi PR #292 HEAD `8219c0be13093d64da1b50e75854260975bc4384`, source owner `cc602e209e7deeb511ab2a1f3b2268d55206c43c`.
- R6/C9 genuinely distinct-author audit NOT_RUN. R1–R10 and C1–C10 stage JSON are retrospective, not independent completed physical experiments.

See `REPORT_KO.md`, `ADVERSARIAL_AUDIT_KO.md`, `HANDOFF_NEXT_THREAD_KO.md`.