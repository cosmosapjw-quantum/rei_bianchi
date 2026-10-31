# Source-linked REI F4 causal Li II 2E1 photon memory

One frozen original-BASS193 physical source experiment (not an IVP). Run `python code/build_memory.py`, `python code/test_memory.py`, `python code/plot_science.py` from the extracted root. Python 3 with numpy, pandas, matplotlib. Contains the prior original PR302/303/305 source-minimal CSV and FS2010 14×258 raw data from the user-provided author TAR (private archive only). `source_bass/trajectory.npz` and `PR293_SOURCE_FJ21_193.npz` are immutable original BASS/REI arrays. All input identities enforced by SHA-256.

Results: `CAUSAL_EMISSION_ARRIVAL_18528.csv` (18,528 source-kernel response rows), `CAUSAL_ARRIVAL_CLOCK_SOURCE_192.csv` (192 proper-clock and FS conditional heat source rows), `CAUSAL_EMISSION_SURVIVAL_193.csv` (193 source photon budget rows), `RESULTS.json`. Figures: 5 PNG + 5 SVG. `REPORT_KO.md`, `ADVERSARIAL_AUDIT_KO.md`, `HANDOFF_NEXT_THREAD_KO.txt`, evidence and 20 retrospective R/C stage checkpoints.

Do not add new source to baseline BASS radiation or chemistry. This computation is a source-replacement *candidate* and nonlocal operator, not a native completed REI17 F/J. FS2010 is a hypothetical x_i=xHII projection on original multi-ion BASS193 and not actual gas heating. All PRs remain draft/unmerged; no force push or new IVP.
