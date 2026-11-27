# BASS_HE PR126 Rice measured birth kinematic bridge | handoff

```makefile
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/BASS_HE
PARENT_PR=125
PARENT_HEAD=b7a3f7e7f3eb2461ff75039797c085296e575acb
GRANDPARENT_PR=124
GRANDPARENT_HEAD=9696297205c2560bd8bdfc8d72b8b80b86fae8d3
CURRENT_UNIT=SOURCE_QUALIFIED_RICE_2000_ABSOLUTE_SPECTRUM_X_HE_PHOTON_HISTORY
EXECUTED_SUBSCOPE=RICE2000_EXACT_BIRTH_KINEMATIC_12_MEASURED_ANGLES
NEXT_CANDIDATE_ONLY=ACTUAL_HE_REST_PHOTON_FIELD_AND_EXCLUSIVE_EVENT_FOLD
AUTO_NEXT_NODE=false
CENTRAL_DAG=28/88
HE_PHYSICAL_DAG=14/18
AUXILIARY_RICE_BIRTH_MICRO=1/2
CANONICAL_PHYSICAL_DELTA=0
R06_SAME_AUTHOR_ADVERSARIAL=PERFORMED
R06_DISTINCT_AUTHOR=NOT_RUN
C09_DISTINCT_AUTHOR=NOT_RUN
NATIVE_SUBAGENT=NOT_RUN
kappa=null
R_event=null
heat_rate=null
L4=false
PRODUCTION=HOLD
NO_MERGE=true
NO_FORCE_PUSH=true
```

## Exact previous source lock and newly generated science

- Rice 2000 original Table I **exact** Git blob `9cdec4449b22bdba2797bbdfb815e98901b85636`, SHA256 `dd29c7b492162b257b6b9674792c2db5cf65c98921cbea088a9283ea641bc03a`. Source original 12 DA observations, 1 campaign, two broad E bins, NOT 12 individual photon energies.
- 12 new source-conditional high-energy daughter pair phase-space support records: `results/RICE2000_BIRTH_KINEMATICS.json` and `.csv`, new code `src/build_rice_birth.py`, tests `tests/test_rice_birth.py`; source copy `inputs/RICE2000_TABLE_I_AUTHORITATIVE.json` byte-identical to parent.
- Kinematics at any E and fixed effective angle: K±=(E-Q)/2±(E/2)sqrt(1-4m²/s)cosθ, Q=23.84647820 MeV. Pair variance Delta²cos²θ. Strict endpoint envelopes analytically certified for E≥150 MeV given frozen masses; 12 rows × 2 endpoints, no fake midpoint measurements.
- Under **same** nonnegative experimental E-weight and angle/acceptance only, binned source-reported DA×(E−Q) lies between DA×(Emin−Q) and DA×(Emax−Q) in nb MeV/sr. Systematics reported 7.1/13%, unknown covariance. Distinct Rice Table II fit anomaly unchanged in parent.
- Actual He-rest high-energy 150–250 MeV photon field, alpha target number density/U^mu and D_fast stopping/heat absent; existing Fermi-LAT IGRB/EGEB observations in HE PR119 are not astrophysical local target histories. No event rate or thermal heating computed.
- Relevant nonthermal literature: Protheroe, Stanev, Berezinsky PRD51 4134 (1995); Poulin, Serpico PRD91 103007 (2015); Acharya, Khatri PRD99 043520 (2019). For D-fast plasma stopping check Casas, Barriga-Carrasco, Rubio PRE88 033102 (2013), but plasma mixture and 50–150 MeV particle range must match; NIST PSTAR/ASTAR is **not** deuteron data.

## Restore and gates

Run `bash REPRODUCE.sh` from package root. Validate original source byte hash, Python 11 targeted tests, source to CSV/JSON reproduction, independent Wolfram 220 MeV 63.6° Kplus=113.08029523781035, Kminus=83.07322656218965, variance=225.10604262585437.

This is a bounded auxiliary physical-data bridge, not the full next node. It must not increment Central 28/88 or HE Physical 14/18. Physical production HOLD and no merge/force-push. Actual publication/backups and HEAD must be read from the separate delivery receipt; do not infer unperformed remote write/readback.
