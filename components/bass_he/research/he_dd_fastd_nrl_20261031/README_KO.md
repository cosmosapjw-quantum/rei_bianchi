# BASS_HE PR139 - NRL 2023 fully ionized H/He fast-D stopping Green-function extension

This is an **add-only, exploratory physical extension** of frozen PR138 HEAD `07f2f0beb36cc54c8a4df0b7c0c5728ca8b2de51`; no production code is modified. Mathematical derivation: `notes/THEORY_KO.md`. Adversarial scope/defects: `notes/BLIND_REFEREE_KO.md`. Reproduction: `bash REPRODUCE.sh` (Python scipy/numpy/matplotlib needed; no proprietary code).

Physical outputs computed and saved in `data/`: 5 sourced FLRW background rows, 50 integrated D energy transfer/characteristic times and nuclear-target columns, 40 pointwise NRL rate rows, 4050 energy-profile rows, 50 quadrature and Coulomb-log model sensitivity comparisons = **4195 derived/model rows**, ZERO newly measured rows, four PNG/SVG science plots. D birth inputs: nominal Asbury 1965 pair kinematics from PR129 plus 0.1, 1, 10, 30, 50, 100 MeV model probes.

Main example K0=1 MeV, z=1e5, K_end=0.001 MeV: Q_e=0.99720503244, Q_p=0.001658897123, Q_alpha=0.000136070438 MeV; t_characteristic=430.081052 s; L_characteristic=2.62038555e9 m; tH=9.16834822e-8. Energy ledger Qsum=0.999 MeV, not `heat_rate`. 160 versus 320 quadrature maximum relative change 9.25e-7; fixed lnΛ20 is separate physics sensitivity (time ratios across all 50 conditions 0.88–1.20 of dynamic static-Debye model). Source/approximation caveats remain.

`CENTRAL_DAG=28/88`, `HE_PHYSICAL_DAG=14/18`, `CANONICAL_PHYSICAL_DELTA=0`, `PRODUCTION=HOLD`; `kappa=null; R_event=null; heat_rate=null; L4=false; NO_MERGE=true; NO_FORCE_PUSH=true; AUTO_NEXT_NODE=false`.

Bibliography: A. Beresnyak (ed.), *2023 NRL Plasma Formulary*, NRL (Oct 2023), section Collisions and Transport p31, https://www.nrl.navy.mil/Portals/38/PDF%20Files/NRL_Plasma_Formulary_2023.pdf ; K. Jedamzik, PRD 74 103509 (2006) Appendix D1a DOI https://doi.org/10.1103/PhysRevD.74.103509 ; J.G. Asbury & F.J. Loeffler, Phys Rev 137 B1214 (1965) DOI https://doi.org/10.1103/PhysRev.137.B1214 ; prior BASS_HE PR129 & PR131 as frozen provenance. Previous CEA-R3042 (1966) neutral stopping tables **are not a substitute** for plasma stopping.
