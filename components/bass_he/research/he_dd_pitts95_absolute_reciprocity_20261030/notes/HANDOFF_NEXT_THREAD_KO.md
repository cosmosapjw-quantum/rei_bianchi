# BASS_HE PR124 신규 24개 EXFOR 절대 포획자료 / 방향 교정 인계

$physmath-research-loop $scispace $exa $wolfram

PROJECT=cosmosapjw-quantum/BASS_HE
CURRENT_PR=124
READ_LIVE_HEAD_FIRST=true
CURRENT_HEAD=QUERY_LIVE_PR124_HEAD_FIRST
IMMUTABLE_PARENT_PR=123
IMMUTABLE_PARENT_HEAD=df061ecb581188539fb028897adb92ee0a3700d4
BRANCH=research/he-dd-pitts95-absolute-reciprocity-20261030
ROOT=research/he_dd_pitts95_absolute_reciprocity_20261030
UNIT=HE_DD_PITTS95_ABSOLUTE_SOURCE_RECIPROCITY_20261030
NEXT_UNIT=SOURCE_OWNED_RICE_1998_2000_12_ABSOLUTE_DD_COINCIDENCE_DA
AUTO_NEXT_NODE=false
CENTRAL_DAG=28/88
HE_PHYSICAL_DAG=14/18
NEW_SCOPED=2/2
PHYSICAL_DELTA=0
STAGE_GIT=20/20
STAGE_COMMITS=21_R01_ONE_CORRECTION
STAGE_LIBRARY_UPLOAD=BLOCKED_CONTAINER_SESSION_EXPIRED
INDEPENDENT_R6=NOT_RUN
INDEPENDENT_C9=NOT_RUN
NATIVE_SUBAGENT=NOT_RUN
kappa=null
R_event=null
heat_rate=null
L4=false
PRODUCTION=HOLD
NO_MERGE=true
NO_FORCE_PUSH=true

## Key physics and original source
EXFOR IAEA-NDS/exfor_master commit 939a14d7bba1ddce51975cb5e8711ce96b3b0871, C0621.x4 SHA256 9c3b49e979e9bb389b2e046e33dec3eb95ebbbed9772a3a47391d5529aaac2ea Git blob ddeb728a59905ca669b3408e9338b8d300d5c96e. Pitts et al PRC39 1679 (1989): 8 measured absolute unpolarized capture DA, 8 vector Ay, 8 tensor Ayy, ONE experimental campaign. Quoted DA DATA-ERR excludes correlated 4% normalization. Full residual covariance and detector efficiency unknown. No Rice measured cross-section values available.

Incident laboratory T_d=95 MeV corresponds E_gamma(alpha-rest)=71.72664743398931181 MeV. Exact corrected photonuclear/capture ratio for ordered D final state is (9/2)(q/k)^2 =80.92618747566492416; for identical D full-sphere event density half this, 40.46309373783246208. Ancestor BASS_HE PR107 inverted the label (2/9)(k/q)^2 as inverse/forward, whereas it is capture/photonuclear under its own definitions. No modification to protected ancestor. Eight conditional photo DA and source-owned rank-one 4% covariance component generated, not measured photo DA or rates.

## Reproduce from ZIP
python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests
python3 src/build_pitts95.py --root .
Check raw C0621 .x4 hash and Git blob, checked source JSON, result CSV byte identity and STAGE_LEDGER, parent PR123 immutable ZIP, clean archive manifest/CRC.

## Next physical source
Rice et al 2000 DOI 10.1103/PhysRevC.61.064612: original 12 direct absolute 4He(gamma,dd) DA at 150–190/190–250 MeV × six angles, coincidence/acceptance and covariance. 1998 Rice PhD scanned PDF at https://nucldata.tunl.duke.edu/nucldata/Theses/PhD/Rice_1998.pdf (numeric row extraction not confirmed). Pitts at E_gamma=71.7266MeV cannot be used as a same-s Rice source. Next actually connect source-owned He proper-frame MeV photon distribution, alpha target density/U, exclusive event normalization and nonthermal fast-D transport/deposition to unlock physical nodes. No IVP/4501-node LP/optimization churn. Production HOLD.
