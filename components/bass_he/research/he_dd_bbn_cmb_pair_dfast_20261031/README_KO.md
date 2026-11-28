# BASS_HE / PR131 - CMB Breit-Wheeler attenuation x fast-D electron drag (2026-10-31)

Source/model-scoped **physical data** generated directly in this package. This is not a cosmological 150-250 MeV injected-photon history and **not** a completed heat-deposition solver.

## Research result

For a standard fully ionized, homogeneous Planck/PDG reference cosmology, calculate the exact leading QED `gamma + gamma_CMB -> e+ + e-` absorption hazard of an injected test photon at 150-250 MeV. Couple Rice (2000) constrained integrated **bin fit** (8.29 nb and 4.34 nb, not monochromatic measured sigma) to the same redshift-local He4 density to compare the direct *first interaction* hazards. Separately calculate Maxwellian-electron, leading-Coulomb-log fast-deuteron electron energy transfer for 50-150 MeV D. These are meaningful *physical coefficients*, not normalized astrophysical event rates or thermal heating fractions.

Sources: Gould & Schreder, Phys. Rev. 155, 1404 (1967), DOI https://doi.org/10.1103/PhysRev.155.1404 ; Planck Collaboration, A&A 641 A6 (2020), DOI https://doi.org/10.1051/0004-6361/201833910 ; PDG Astrophysical Constants, https://pdg.lbl.gov/2025/reviews/rpp2024-rev-astrophysical-constants.pdf ; Rice et al., Phys. Rev. C 61, 064612 (2000), DOI https://doi.org/10.1103/PhysRevC.61.064612 ; Brown, Preston & Singleton, Phys. Rep. 410, 237 (2005), arXiv https://arxiv.org/abs/physics/0501084 ; Jedamzik, Phys. Rev. D 74, 103509 (2006), https://arxiv.org/abs/hep-ph/0604251 .

The reuploaded source `Rice_1998(2).pdf` is SHA-256 `87fe939659151b09a1653467f1ac2098d971048fa4cf3611b447fce8cc976336`, 139-page incomplete reproduction, **identical** to source used in PR130; does not contain the thesis Table 5.2 or later chapter. That table was independently supplied in PR127. Do NOT put copyrighted original PDF in public Git. PDF's Table 5.1 original stat error and Schiff high-bin ratio anomalies remain source CONCERN (see PR130), no source-value edits.

## Reproduce

```bash
python -m pip install -r requirements.txt
bash REPRODUCE.sh
```

This generates six CSV tables (164 model-predicted rows), one JSON summary, and four scientific PNG/SVG figures. Targeted self-contained Python test suite has 23 cases, including independent adaptive quadrature, numerical convergence, external Wolfram BW normalization and D birth kinematics, charge conservation, and scientific non-promotion guards. The optional user PDF hash check is skipped when the original PDF is unavailable; it is not distributed with this public code archive.

### Actual outputs

`data/SOURCE_FLRW_IONIZED_STATES_11.csv`: 11 real-parameter model states (Planck background not BASS-native); source field units per CSV.

`data/PHYSICAL_CMB_GAMMAGAMMA_PAIR_OPACITY_55.csv`: 55 energy/redshift points, gamma-gamma Breit-Wheeler absorption frequency and Hubble ratio.

`data/PHYSICAL_FASTD_PLASMA_ELECTRON_DRAG_55.csv`: 55 fast-D energy/redshift points, electron friction and timescale; static vs dynamic Debye-screening variants. **Not** BPS next-to-leading-order, not nuclear slowing/heat.

`data/RICE_BINMODEL_DD_VS_CMB_PAIR_HAZARDS_22.csv`: 22 energy/redshift first-interaction hazards for **only** He-dd and gamma-gamma pair creation. The two-channel fraction is not a global dd production probability or upper bound on all cascading interactions. Uses Rice bin-averaged cross section as a constant-in-bin *model* with the printed one-sigma normalization systematic range only.

`data/PHYSICAL_GAMMA_TRANSPARENCY_TRANSITION_15.csv`: 15 computed local `Gamma_gg/H=0.1,1,10` transitions for five gamma energies. Not an observed spectrum cutoff.

`data/MODEL_CONDITIONAL_SOURCE_BIN_BIRTH_6.csv`: six nominal two-body D birth-energy pairs, obeying exact `K_+ + K_- = E_gamma - Q`. Models, not new measured daughters.

For precise interpretation, scientific derivations, explicit missing inputs, and blind referee, see `notes/THEORY_AND_SCIENCE_KO.md`, `notes/BLIND_REFEREE_KO.md`. The complete copied handoff is in `notes/HANDOFF_NEXT_THREAD_KO.md`.

### Governance

Frozen parent `cosmosapjw-quantum/BASS_HE` PR130 `39177b446df601e3103cdb1e4d39ac51ad31086a`; open separate Draft only; do not merge/force-push. Canonical Central `28/88`, HE physical `14/18`, physical delta **0**, scoped new opacity/drag microtasks `2/2`. `kappa=null`, `R_event=null`, `heat_rate=null`, `L4=false`, `PRODUCTION=HOLD`. Distinct-author R06/C09 `NOT_RUN`. Native subagent tool absent in this host (`NOT_RUN`).
