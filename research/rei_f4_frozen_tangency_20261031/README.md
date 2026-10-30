# REI F4: frozen BASS193 vs hybrid21 source-tangency & chemical-energy port

Science question: At 193 original BASS21 saved states with one fixed prescribed H,T,n_b,clock, can one re-use the same trajectory after replacing the native H/He chemical source with source-qualified REI/Grackle H/He rates? If not, what is the exact source defect and *formal* energy port required before any coupled evolution may be attempted?

**Answer**: the actual source defect Delta F is nonzero at 193/193 saved epochs, with max |Delta F|/H = 1.292427529... ; the unchanged BASS path is therefore not an exact solution of the substituted field. This is a local necessary condition, **not** a proof of nonexistence of a different hybrid trajectory. No new IVP, no new opacity or CMB.

Original authority: PR #298 HEAD `914eae63681e55cf013208d3fd5357f38fc2fd69`, inherited PR296 native Rust and PR295 (Grackle), BASS21 original owner `cc602e209e7deeb511ab2a1f3b2268d55206c43c`.

Reproduce with `bash VERIFY.sh` in a clean extracted archive. Python dependencies numpy, scipy, matplotlib; `source/PR298_FULL.zip` must remain byte-exact. See `THEORY_AND_REPORT_KO.md`, `ADVERSARIAL_AUDIT_KO.md`, `HANDOFF_NEXT_THREAD_KO.md`.

Original Working DAG 33/88, Central 28/88, Physical Fast 4/7; this is one auxiliary source-compatibility calculation (1/1 scoped), canonical delta=0. Draft only, no merge, no force push, no budget reset, production HOLD; R6/C9 different author NOT_RUN.
