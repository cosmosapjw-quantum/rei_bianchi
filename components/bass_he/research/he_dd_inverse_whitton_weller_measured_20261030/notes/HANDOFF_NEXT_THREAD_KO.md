# BASS_HE PR121 | 새 대화 연구 인계

$physmath-research-loop $scispace $exa $wolfram

PROJECT=cosmosapjw-quantum/BASS_HE
PARENT_PR=120
PARENT_HEAD=83596b913a08dd31496b7abbb7d5a9972fff5cc1
NEW_PR=READ_LATEST_GITHUB_PR
NEW_HEAD=READ_LATEST_GITHUB_SHA
BRANCH=research/he-dd-inverse-whitton-weller-measured-20261030
ROOT=research/he_dd_inverse_whitton_weller_measured_20261030
CENTRAL_DAG=28/88_UNCHANGED
HE_PHYSICAL_DAG=14/18_UNCHANGED
PR114_LOWE_DATA=3/4_SCOPED_UNCHANGED
PR119_ANGULAR=2/3_SCOPED_UNCHANGED
PR120_SHAPE=2/2_SCOPED_UNCHANGED
NEW_INVERSE_SOURCE=2/2_SCOPED
PHYSICAL_DELTA=0
R6_INDEPENDENT=NOT_RUN
C9_INDEPENDENT=NOT_RUN
R_event=null
heat_rate=null
kappa=null
physical_activation=false
L4=false
production=HOLD
AUTO_NEXT_NODE=false

## Restore

Read `DELIVERY_RECEIPT.md`, `STAGE_LEDGER.json`, `SOURCE_IDENTITY.json`, `notes/THEORY_KO.md`, `notes/REPORT_KO.md`, `src/build_inverse_dd_atlas.py`, `tests/test_source_inverse.py`, all 4 `sources/*.x4`, and generated source 41-row atlas JSON/CSV. The ZIP may contain nested PR120 archive as predecessor; check its SHA against `703bcef62463d794bd60f0902d1db829084907808fd8bea6e29133a2b5cf4b9f`.

Run `python src/build_inverse_dd_atlas.py --root .` and `python -m unittest discover -s tests -v`, `python -m compileall -q src tests`, check generated JSON/CSV byte identities.

Original source owner: IAEA-NDS/exfor_master commit 939a14d7bba1ddce51975cb5e8711ce96b3b0871. C0122 Whitton 1993 29 EXFOR measurement rows: 14 REL DA and 15 polarization rows with two pointer components; A1256 Weller 1984 12 rows: 6 partial capture DA and 6 TAP. 4 pinned source Git blobs in report. M0011/M0826 already PR114 original lowE sources, included only for energy support crosswalk.

T_d_lab [9.7,20,30,50] MeV -> equivalent He4-rest gamma E [28.8037875550,33.9867354654,39.0187237278,49.0827002528] MeV. 1993 REL DA near90/shoulder source ratio [0.02606383,0.0375]; no absolute conversion.

## Next physical research

Use Rice 1995 masters and Rice 1998 PhD/2000 PRC (source TUNL PDF but scanned pages not authenticated) and original Whitton 1993/1984 detector methods to resolve captured REL normalization vs PARTIAL/DA and polarized components. Obtain original absolute differential and covariance for physical reciprocity mapping and the identical daughter convention. Avoid treating this low-E inverse source as high-E MeV photon history.

Only after source-owned gamma phase-space at He target and fast-D stopping, secondary deposition and heat capacity are real and consistent can R_event/heat/L4 be considered. Preserve parents, no auto merge, force push, source substitution or old IVP/LP reruns. Stage Git commits and GoogleDrive/Dropbox Paper logs need actual readback; Dropbox binary receipt requires real binary provider support, never infer from Paper text.
