# BASS_HE | measured EXFOR kinetic cross-section atlas | next-thread handoff

```ini
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/BASS_HE
PARENT_PR=112
PARENT_HEAD=a03c1eee365c9b796fef137b81a4347ad44008d1
BRANCH=research/he-dd-exfor-measured-kinetic-atlas-20261029
CURRENT_PR=READ_LATEST_REMOTE
CURRENT_HEAD=READ_LATEST_REMOTE
ROOT=research/he_dd_exfor_measured_kinetic_atlas_20261029

CENTRAL_DAG=28/88
HE_DAG=14/18
NEW_MEASURED_DATA_DAG=2/2_SCOPED
PHYSICAL_DELTA=0
THEORY=9/10
CODING=9/10
STAGE_PUBLICATION=20/20
INDEPENDENT_R6_C9=NOT_RUN
NATIVE_SUBAGENT=NOT_RUN

kappa=null
R_event=null
heat_rate=null
physical_activation=false
L4=false
production=HOLD
```

## Exact source / execution
The immutable true experiment source is `IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871:exforall/M04/M0475.x4`, 3349 bytes SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`, Git blob `c49433293921dbb012d7f1b0387745732a598efa`. New branch contains byte-identical copy at ROOT/sources/M0475.x4, byte-verified Python source and test, alternate C++ source and measured coordinates in `results/MEASURED_KINETIC_COORDINATES.json`. Local downloadable archive also contains full 90-digit ATLAS.json, DA/SIG CSV and three generated source-marker plots.

Read ROOT/{THEORY_KO.md,REPORT_KO.md,RESULTS.json if present,IMPLEMENTATION_CONTRACT.json,STAGE_LEDGER.json,DELIVERY_RECEIPT.md,src/exfor_kinematic_atlas.py,tests/test_exfor_physical_atlas.py,tests/independent_cpp_exfor.cpp,results/MEASURED_KINETIC_COORDINATES.json}. No original IVP/full suite/4501-node LP replay.

Run only new targeted paths in ROOT:
```bash
python -m unittest discover -s tests -p 'test_*.py' -q
python -m compileall -q src tests
python src/exfor_kinematic_atlas.py --source sources/M0475.x4 --out results
g++ -std=c++20 -O2 -Wall -Wextra -Werror -pedantic tests/independent_cpp_exfor.cpp -o /tmp/he_exfor_cxx
/tmp/he_exfor_cxx sources/M0475.x4
python src/make_figures.py
```
Current-session evidence: Python 23/23 targeted PASS, C++20 original 18 rows max shell residual 5.5856e-103 MeV², Wolfram independent shell and threshold, plots directly inspected. The C++ oracle is an independent *algorithm*, not an independent research agent; R6/C9 nonauthor NOT_RUN.

## Actual new physical-data facts (source-valued, not extrapolated)
M0475002: 12 original DA measurements [nb/sr] at 213/258/330 MeV and theta_CM 46/61/73/87 deg; M0475003: six original SIG [nb] at E_gamma 201,225,253,285,320,359 MeV (NO measured 330 MeV total). Frozen PR104 masses M_alpha c²=3727.3794118, m_d c²=1875.61294500 MeV. Q=(2m−M)=23.84647820 MeV. True photon threshold =Q+Q²/(2M)=23.9227589403967 MeV. Fixed-target event pair total kinetic=E_gamma−Q. Derived source-valued A_K=DA_reported*(E_gamma−Q) [nb MeV/sr], S_K=SIG_reported*(E_gamma−Q) [nb MeV] with original ERR-S propagated as coordinatewise statistical error. At E_gamma330, each of the four measured angle rows provides two correlated daughter Kpm, and each pair totals 306.1535218 MeV. This is reported experimental cross-section weighted by produced daughter kinetic energy, NOT a new measurement, event rate, ionization or thermal heat.

The lab daughter gamma boost (parent PR108 reuse): s=M²+2ME, q*=sqrt(s/4−m²), Kpm=(M+E)/2−m±E q* cos(theta_CM)/sqrt(s). Photon rest frame and unspecified detector ±-arm convention must not be silently interchanged. If original total SIG already corresponds to a different counting convention, `S_K` inherits that convention, not a newly qualified exclusive event sigma.

## Scope, blockers and what to do next
Next physics goal: acquire original Arends1976 DOI 10.1016/0370-2693(76)90671-7 and Silverman1984 DOI 10.1103/PhysRevC.29.35 full detector efficiency, coincidence, polarization and DA/SIG event-vs-particle convention. Obtain a measured true exclusive event SIG at E_gamma330 MeV or a separately qualified interpolation/inference including uncertainty (do not call it measured). Source-qualify incident MeV-photon phase space and He target proper frame, then named D_fast stopping/redistribution/deposition and C_V. Only then consider physical L4 or HE DAG promotion. Remain `production=HOLD`, original Central28/88 and HE14/18. Source archive Git and dual text log 20/20 ACK exist; **do not call them dual full binary restored backup**. No auto merge, force push or fake native reviewers.