# BASS_HE PR129: 1965 Asbury observed gamma+He4->dd and 1966 neutral elemental D stopping

New independent measured experiment (Asbury-Loeffler 1965): 1 experiment, 2 absolute measured DA.
Original CEA-R3042 deuteron H/He elemental-target calculated stopping and ranges: 12 published table rows.
Derived at Asbury representative mean-E, effective CM-theta: 4 fast deuteron K_birth + neutral elemental range/stopping by strict in-table linear interpolation.

- CEA is NOT a measured primordial plasma deposition/thermalization kernel.
- Asbury published total SIG is NOT a second direct measurement: angular shape sin²(theta)cos²(theta) model.
- Rice 1998/2000 counts as one different experiment, and angle/E broad bins are not pointwise comparable.
- Drake1969 is helium-like atomic two-photon eV-physics source relevant to REI, NOT 150-250 MeV photons.
- No source original PDF is in this code/data Git/public archive. The originals may be privately backed up.

Run `bash REPRODUCE.sh` in package root. This uses Python stdlib and matplotlib.
`results/ASBURY_MEASURED_2.csv` contains measured source columns, inferred event totals explicitly typed.
`results/CEA_ELEMENTAL_D_H_HE_12.csv` are original author calculated values.
`results/ASBURY_DFAST_NEUTRAL_BRIDGE_4.csv` are new derived nominal K and interpolated
neutral-material source values with exact source energy brackets.
`results/SCIENTIFIC_RESULT.json` contains identities, limitations and progress.
`notes/THEORY_KO.md` is a derivation and finite blind-referee note.
`stages/R01.md...R10.md,C01.md...C10.md` record stage-specific deliverables and fixed DAG.

Scope progress: Central28/88, HE Physical14/18, source micro2/2; no canonical physical delta.
Distinct-author R06/C09 and native subagent NOT_RUN; production HOLD.

Evidence status is based on executed Python 19 targeted tests and independent Wolfram numerical check;
no production cosmological IVP has been run.
