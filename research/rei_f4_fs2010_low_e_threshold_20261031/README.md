# REI F4 FS2010 threshold-resolved BASS193 source

1. This is a **private source-inclusive** frozen-science reanalysis from original GitHub Draft PR297, exact source ZIP and three user-supplied publisher PDFs. Do not redistribute publisher PDFs on public GitHub.
2. `python -m unittest discover -s tests -v` validates saved physical data against source identities and explicit conservation checks.
3. `python code/combine.py` re-combines six bounded 5-emission-epoch calculations into the 192-interval energy/absorption data and conditional energy bounds.
4. `python code/plot_science.py` recreates six scientific PNGs.
5. The full 193-epoch source replay is **not** claimed; 30 source epochs cover 99.48064% of the original conditional source. Remaining contribution is bounded using immutable PR297 energy and photon totals.
6. `code/thresholds.py` is the original-source reexecution code. To redo a chunk: `python code/run_chunk.py 0` through `5` after restoring the source ZIP. The original exact PR287 source is read from immutable nesting, not modified.
7. Scientific provenance and caveats: `THEORY_KO.md`, `REPORT_KO.md`, `ADVERSARIAL_AUDIT_KO.md`, `STAGE_LEDGER.json`, `results/RESULT.json`.

GitHub publication should contain only code/docs/tests/derived CSV and stage ledger; original source ZIPs and attached paper PDFs remain **private backup only**. No merge or production.
