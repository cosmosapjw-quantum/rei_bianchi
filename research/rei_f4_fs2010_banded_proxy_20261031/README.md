# REI F4 FS2010 × BASS193: band-enclosed single-xi deposition proxies (2026-10-31)

**Scope: conditional source, off-manifold single-xi FS2010 model comparison, no new IVP.** The accurate data product is `BASS193_FS2010_BAND_DEPOSITION_ENVELOPE_192.csv` with 192 original arrival bins. It is *not* native species-resolved energy deposition or an evolved temperature.

Scientific formulation, provenance, results, citations and same-author adversarial audit are in `SCIENTIFIC_REPORT_KO.md`. Computation is `python build_envelope.py`, figures `python plot_physics.py`, scoped regressions `python -m unittest discover -s tests -v`. `bash VERIFY.sh` checks immutable output hashes **in the full standalone ZIP**; the public Git subtree reuses its two exact original source CSVs from ancestor PR302/PR303 and can run `python -m unittest discover -s tests -v` and `python build_envelope.py`. In a public Git checkout, earlier PR302 and PR303 data files are used via parent paths; in the compact privately backed-up ZIP they are included in `inputs/` for standalone replay.

Inputs: FS2010 author-linked original archive NOT acquired; exact 21cmFAST Git mirror `2a51aa316e216a1eb60650f9e7fbe35fe9e62040`, 14 xi × 258 energy grid rows; 336 original-table-derived outward-rounded energy-band extrema rechecked. Source is the original BASS193 full192 PR302 data with PR303 frozen state match. No publisher PDFs, raw FS tables or large source master ZIP republished.

Working 33/88, Central 28/88, F4-fast 4/7, canonical delta 0, auxiliary 1/1 scoped, production HOLD, no merge, no force push, auto-next false.
