# BASS_HE | next-thread handoff, measured EXFOR shape physical-data unit

$physmath-research-loop $scispace $exa $wolfram

PROJECT=cosmosapjw-quantum/BASS_HE
PARENT_PR=119
PARENT_HEAD=62b925b739656f01131e152ace05624d0f102850
NEW_PR=LOOKUP_REMOTE_AFTER_PUBLICATION
NEW_HEAD=LOOKUP_REMOTE_AFTER_PUBLICATION
BRANCH=research/he-dd-exfor-angular-shape-source-20261030
ROOT=research/he_dd_exfor_angular_shape_source_20261030
CENTRAL_DAG=28/88_UNCHANGED
HE_PHYSICAL_DAG=14/18_UNCHANGED
PR119_ANGULAR_DAG=2/3_UNCHANGED
NEW_MEASURED_SHAPE_MICRO_UNIT=2/2_SCOPED
PHYSICAL_DELTA=0
R6_DISTINCT_AUTHOR=NOT_RUN
C9_DISTINCT_AUTHOR=NOT_RUN
NATIVE_SUBAGENT=NOT_RUN
R_event=null
heat_rate=null
kappa=null
L4=false
production=HOLD
AUTO_NEXT_NODE=false

## Restore
Read root `notes/THEORY_KO.md`, `notes/REPORT_KO.md`, `STAGE_LEDGER.json`, `DELIVERY_RECEIPT.md`, original `sources/M0475.x4`, `src/experimental_shape_atlas.py`, `tests/test_experimental_shape_atlas.py` and 3 results files. Verify raw input SHA256 b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f, Git blob c49433293921dbb012d7f1b0387745732a598efa. Confirm PR119 parent unchanged; inspect actual PR120 head and raw Git blobs.

Compute by `python src/experimental_shape_atlas.py --root .` then `python -m unittest discover -s tests -v`. Results: 30 derived pointwise source contrasts (18 angular, 12 energy) as exact rationals, individual ERR-S axis box endpoints (NOT CI), 9 conditional WLS fits including χ²/dof/p and original 12 measurements. Python 15/15 and independent Wolfram 9 χ² verified on 2026-10-30.

## Science priority
The 46°–87° contrast is E213 8/19, E258 17/33, E330 5/33; source ERR-S Cartesian boxes overlap. Source full-sky nuclear event normalization and angular detector efficiency UNKNOWN. No total SIG measured at 330 MeV. Rice et al 2000 actually measured 150–250 MeV two γ bins, six angles each, but no source-qualified table digitization; do not copy made-up data.

Next physics: acquire original full Arends 1976/Rice 1998 detector acceptance, coincidence efficiency, source-owned covariance; only then consider source-qualified angular observable deconvolution. In parallel obtain physically appropriate observer/He-rest 150-400 MeV photon phase space and genuine fast-D thermal/escape operator; no substitutions with UVB. Do not merge, force push, activate production or repeat old IVPs/4501 LP.

## Backup
Download ZIP from the current conversation and provider links once published. Distinguish Git upload, text Drive/Dropbox logs, cloud binary upload and full byte restoration; preserve actual ACK SHA instead of inferring. Native independent R6/C9 remain NOT_RUN.
