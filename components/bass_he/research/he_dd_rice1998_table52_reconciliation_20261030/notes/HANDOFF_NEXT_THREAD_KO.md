# BASS_HE PR127 | Rice 1998 Table5.2 closed source gap | thread handoff

```makefile
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/BASS_HE
PARENT_PR=126
PARENT_HEAD=3305c4579221edde36c14f941b3530375aca4f7a
CURRENT_PR=FILL_AFTER_REAL_REMOTE_PUBLICATION
CURRENT_HEAD=FILL_AFTER_REMOTE_REF_VERIFICATION
READ_LIVE_HEAD_FIRST=true
BRANCH=research/he-dd-rice1998-table52-reconcile-20261030
ROOT=research/he_dd_rice1998_table52_reconciliation_20261030
UNIT=RICE1998_TABLE52_SOURCE_RECONCILIATION_AND_FASTD_MULTIPLICITY
NEXT_CANDIDATE=SOURCE_QUALIFIED_HE_REST_PHOTON_HISTORY_X_RICE_ABSOLUTE_RESPONSE
AUTO_NEXT_NODE=false
CENTRAL_DAG=28/88
HE_PHYSICAL_DAG=14/18
RICE_BIRTH_AUXILIARY=1/2
RICE_1998_TABLE52_SOURCE_MICRO=2/2
CANONICAL_PHYSICAL_DELTA=0
kappa=null
R_event=null
heat_rate=null
L4=false
PRODUCTION=HOLD
NO_MERGE=true
NO_FORCE_PUSH=true
NATIVE_DISTINCT_AUTHOR_R6_C9=NOT_RUN
```

Source gap: user-provided image of Bryan Joseph Rice 1998 Duke thesis Table 5.2, Eγ 190–250MeV, 6 rows, original screenshot SHA `103022f4d890519ee9273e8ddc5d7a632a93ada30ab4a5259216f600b2e10de2`. 1998 preliminary high values `(0.118,0.486,1.170,0.921,0.566,0.594)` nb/sr; original yields `(249,951,1977,1394,771,735)`; errors in SOURCE JSON. Compare to Rice 2000 published `(0.14,0.59,1.42,1.11,0.68,0.43)` nb/sr, SAME experiment. 12 row paired comparison uses original 1998 low Table5.1 and published 2000 TableI byte-locked source. Eleven ratios near 1.207 but high/139.7 ratio 0.724; do not suppress the discrepancy or promote an erratum/significance. No independent experimental rows invented.

Derived exact source operator: for ordered Rice dσ/dΩ, `σ_event = 0.5∫dΩ dσ_ordered/dΩ`, and D_fast birth kernel normalized `∫dK K_D = 2 σ_event` (2 daughters/event), first moment `(Eγ-Q)*σ_event`; cf. Protheroe, Stanev, Berezinsky PRD51 4134 (1995) Eq21. Unknown local He-frame `nγ`, target state, detector energy response and nonthermal D stopping remain. Source-restricted DA×(E−Q) intervals are NOT heat, rate or production.

Run `bash REPRODUCE.sh`; source original git blobs `266859bb62ef0929b098928b686f945aca600cb9` (Rice1998 Table5.1) and `9cdec4449b22bdba2797bbdfb815e98901b85636` (Rice2000 Table I). Stage notes R01..R10 and C01..C10 published individually if verified in current repository, then final code/data ZIP readback as available. No original image/PDF in Git. Full user screenshot and uploaded publication PDF bytes are private only. See `notes/THEORY_AND_SOURCE_KO.md`, `notes/BLIND_REFEREE_KO.md`, `sources/SOURCE_IDENTITY.json`, `STATUS.json`, `results/RICE1998_2000_MATCHED_12.json`.

NEXT SAFE ACTION: Identify physical photon injection/source history for the same BASS_HE target epoch, propagate energy-angle spectrum in alpha rest frame, identify Rice per-E exclusive response and valid high-energy D slowing in target medium; only then compute R_event or heat. Protect old IVPs/4501-LP and frozen parents.
