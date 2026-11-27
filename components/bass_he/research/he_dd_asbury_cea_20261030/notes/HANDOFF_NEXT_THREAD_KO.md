# BASS_HE PR129 | Next thread source-qualified independent Asbury + CEA

```makefile
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/BASS_HE
PARENT_PR=128
PARENT_IMMUTABLE_HEAD=e218b1fdccbc8c3e156d9f70805fe8a9048604f8
READ_LIVE_HEAD_FIRST=true
CURRENT_UNIT=ASBURY1965_ABSOLUTE_DA_X_CEA1966_NEUTRAL_DEUTERON_STOPPING
CURRENT_PR=TO_READ_FROM_PUBLISHED_RECEIPT
CURRENT_HEAD=TO_READ_FROM_LIVE_GITHUB
NEW_INDEPENDENT_ASBURY_EXPERIMENTS=1
ASBURY_MEASURED_ABSOLUTE_DA=2
ASBURY_MODEL_INFERRED_EVENT_TOTALS=2
CEA_AUTHOR_CALCULATED_D_H_HE=12
DERIVED_NOMINAL_BIRTH_STOPPING=4
CENTRAL_DAG=28/88
HE_PHYSICAL_DAG=14/18
NEW_SOURCE_MICRO=2/2_SCOPED
CANONICAL_PHYSICAL_DELTA=0
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
AUTO_NEXT_NODE=false
NEXT_OBJECTIVE=TARGET_EPOCH_HE_REST_150_250_MEV_GAMMA_HISTORY_PLUS_IONIZED_DFAST_DEPOSITION
```

## New actually grounded physics
Asbury & Loeffler (1965), Phys Rev 137 B1214 DOI 10.1103/PhysRev.137.B1214,
source user PDF SHA256 `954042ad95c1aab77a84b9a402ccf9dc213403723a93820d4aeebcddaa51d75c`.
Table II pB1218: E=220.5 MeV at θcm=52.4: DA=(6.3±2.2) nb/sr,
reported MODEL integrated total (22.3±7.9) nb. E=265.3 at θcm=53.2:
DA=(1.5±1.1) nb/sr, model total (5.4±3.8) nb.
DO NOT treat models as independent measurement or match Rice binned DA pointwise.

Williamson/Boujot/Picard, CEA-R3042 (1966) deuteron elemental H and He
source tables p76,p78 / supplied PDF90,92, SHA256 `e5ff9c4e9b3d635103935c0fefb3a6e11988ec9ebe90150da686666d06568652`.
Original appended erratum p388 replaces report pages223–296, not target tables.
Source 12 calculated rows at energies50,60,75,100,125,150MeV; strict interpolation.
Deuteron pair nominal K: (118.9857833,77.6677385) MeV at 220.5 and
(147.4822297,93.9712921) MeV at 265.3. Tabulated mass stopping, path
range units MeV cm²/g and g/cm²; not an ionized primordial plasma source.

Drake/Victor/Dalgarno Phys Rev180 25 (1969) uploaded:
relevant REI LiII atomic 2-photon spectral data, NOT HE MeV gamma source.

## Exact restore and validation
`bash REPRODUCE.sh` recomputes CSV/JSON, 19 targeted tests and source plots.
Expected `results/SCIENTIFIC_RESULT.json`, `results/ASBURY_MEASURED_2.csv`,
`results/CEA_ELEMENTAL_D_H_HE_12.csv`,
`results/ASBURY_DFAST_NEUTRAL_BRIDGE_4.csv`.
No fresh target-frame high-energy photon history or plasma deposition was computed.
The data is real source/derived physics, not a cosmological production event rate.

## Exact next source needs
- Actual solver-owned f_gamma(x,p,t) covering 150–250 MeV in alpha rest-frame,
  and source injection/cascade, n_alpha, U_alpha and expansion epoch.
- High-energy ionized H-He D slowing/secondary production/escape and deposition
  kernel, with target temperature, charge state, density; CEA neutral values are
  comparison benchmark only.
- Detector response and angular/E covariance in full Rice 1998 Duke thesis
  UMI 9825640 or collaboration run/acceptance files, if combining Rice and Asbury.
- Experimental 1965 Asbury full paper is ALREADY uploaded; do not request it again.
- CEA-R3042 with appended erratum is ALREADY uploaded; do not request it again.
