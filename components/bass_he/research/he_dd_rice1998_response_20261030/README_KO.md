# BASS_HE PR130 Rice1998 source-owned detector-to-physics reconstruction
**2026-10-30**. Parent immutable Draft PR129 at `6251fa523e3002d4a618964287a6bfe34ca59c34`.

This add-only scoped research uses the uploaded 1998 Rice Duke dissertation and previously source-locked 2000 Table I to reconstruct physical laboratory Jacobians, absolute SAL differential cross sections from original yields, and separately preserve 1993 LEGS raw polarization counts. It computes the original source Schiff laboratory photon spectrum *with an unreconciled high-bin normalization finding*. Source thesis PDF and historical Table5.2 image are NOT in public Git.

## Direct outcomes
- SAL 1998 original preliminary 12 rows: `Y × J_lab_to_CM × f_bin/1000`, 12 exact CM kinematic transformations, 12 source-measured and published same-campaign comparisons. Independent Wolfram confirms Jacobian 12/12.
- 1998 Tables 4.2–4.4 LEGS distinct low-statistics experiment: **10 lab-angle rows with 395 raw coincidence candidates**, flux/accidental characterization and strictly *instrumental* polarization ratio (not corrected dd nuclear analyzing power).
- Source original Appendix A.1 Schiff model low/tag 1.1162284 (author 1.117); high/tag 1.2575051 vs author 1.546 under literal 190-250 MeV integration; 190-270 yields 1.5525891 as **diagnostic only**. Independent Wolfram check matched.
- Another printed source anomaly: 1998 Table5.1 last low-bin source `Y=827±136` gives `dσ` stat SD 0.14042136 while printed 0.122 nb/sr. Retain raw and reconstructed separately.
- 5 actual scientific plots PNG+SVG. `bash REPRODUCE.sh` runs source science, plots and 28 reproducible targeted tests. Source PDF SHA256 and 2000 source Git blob identity recorded.

Status: **Central 28/88; HE physical 14/18; new source micro 2/2 scoped; physical delta 0**. No new independent SAL measurement, no true cosmic 150–250MeV photon field, no plasma-D heating. `kappa/R_event/heat_rate=null;L4=false;PRODUCTION=HOLD;NO_MERGE=true;NO_FORCE_PUSH=true;AUTO_NEXT_NODE=false`.

### Reproduce
Extract the code/data ZIP, then `bash REPRODUCE.sh` from its root. The source input files are shipped; `inputs/create_inputs.py` reprints the manually read source table numbers and checks protected 2000 blob, for audit but it does not read a PDF. Runtime: Python3, matplotlib (plot only); standard library scientific computation and unittest. Python tests should pass without matplotlib when invoking `python -m unittest discover -s tests`.

See `notes/THEORY_AND_SOURCE_KO.md` for equations, author original page/figure citations and limitations; `notes/NEXT_THREAD_HANDOFF_KO.md` for exact next objective. Do not interpret 2000/1998 cross-version data as two independent experiments or make source-normalization repairs without provenance.
