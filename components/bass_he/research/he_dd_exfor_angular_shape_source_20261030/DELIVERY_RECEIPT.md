# BASS_HE PR120 · 2026-10-30 | Source-derived EXFOR angular-shape science delivery

## Actual authority
Draft PR https://github.com/cosmosapjw-quantum/BASS_HE/pull/120, add-only descendant of PR119 frozen head `62b925b739656f01131e152ace05624d0f102850`. Exact final Git HEAD of this document must be read from the PR after this commit. No merge, force push, main or parent mutation.

## Source and scientific data
- Exact original IAEA-NDS/exfor_master@`939a14d7bba1ddce51975cb5e8711ce96b3b0871`, path `exforall/M04/M0475.x4`, 3349 bytes, SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`, Git blob `c49433293921dbb012d7f1b0387745732a598efa`. Byte-identical at PR120 `sources/M0475.x4` and clean ZIP.
- Original experimental M0475002 DA: 12 measured energy-angle points, (213,258,330)MeV × (46,61,73,87)° CM, with source ERR-S nb/sr_CM. No original measured total SIG at 330 MeV; no angle-efficiency calibration or covariance imported.
- Actually generated 30 exact contrast functions from only 12 source measurements (18 within-energy angular pairs, 12 cross-energy fixed-angle pairs), each with exact coordinatewise source ERR-S box, conditional delta variance unknown-correlation lower and upper, and independent-error linearized SD. Thirty are NOT new independent experiments.
- Actual 9 conditional source-model WLS fits (three energies × constant/sin²/even-quartic), χ²,dof,nominal p and fitted values at measured angles. Source ERR-S assumed independent Gaussian ONLY for conditional χ²; missing detector acceptance/covariance prohibits experiment-calibrated evidence for a multipole transition. Rice 2000 original numeric data NOT_ACQUIRED, no fake Rice points.
- Three normalization-invariant 46°→87° contrasts E213=8/19 box [9/35,23/41], E258=17/33 box [7/29,27/37], E330=5/33 box [-3/31,13/35]. Source boxes NOT joint statistical CI. 330 sin² p~0.10, not a 5% rejection.

## Actual technical verification
- Python targeted 15/15 unittest PASS (raw source tamper fail-closed, real fractions, box extremizers, statistical models, output reproduction), compileall PASS, original source SHA/Git blob PASS.
- Independent Wolfram Language exact fractions and three-energy × three-model least squares χ² PASS. Initial Wolfram attempt contained unresolved weight name; corrected in later stateless call. Native independent-subagent author R6 and C9 NOT_RUN, no GitHub CI/old full production suite status claimed.
- Git R01–R10 and C01–C10: twenty distinct commits and exact remote file blob checks, full 40-digit Git stage SHAs in `STAGE_LEDGER.json`.
- Google Drive stage log https://docs.google.com/document/d/147wUtWd41GZh8NYQJaw9oNdOHHBDGB3g5JSGsO7fOcQ/edit : 20/20 SHA text rows read back; Dropbox Paper https://www.dropbox.com/scl/fi/654uuvsqd3bzep9qwfgas/BASS_HE-PR120-EXFOR-source-angular-shape-stage-Git-receipts-20261030.paper?rlkey=zeeebbloeakfhmn32d7uma1ue&dl=0 : 20/20 text rows read back. Those stage rows were written in two grouped batches, not 20 independent cloud operations.
- Original complete local research ZIP `BASS_HE_PR120_EXFOR_SOURCE_SHAPE_20261030.zip`, **31869 bytes**, SHA256 `703bcef62463d794bd60f0902d1db829084907808fd8bea6e29133a2b5cf4b9f`. 26 ZIP entries =25 payload files plus SHA256 payload manifest, CRC PASS. Clean separate extraction with Python 15/15 + compileall + byte-identical regeneration of JSON and both CSV results PASS.
- ChatGPT Library upload ACK `/BASS_HE_PR120_EXFOR_ANGULAR_SHAPE_20261030/BASS_HE_PR120_EXFOR_SOURCE_SHAPE_20261030.zip`; Google Drive raw ZIP upload ACK file ID `190rGy9htuGjPGh8wj5XkIJBHHunRZKQl` and raw 31869-byte download to model container. Compared actual full bytes with `cmp`, SHA256 same `703bcef6...4b9f`, and ZIP CRC PASS. Google Drive: https://drive.google.com/file/d/190rGy9htuGjPGh8wj5XkIJBHHunRZKQl/view . Dropbox **binary ZIP** upload/readback NOT_RUN (Paper stage text receipts are separate).

## Science gate and DAG
- Existing Central 28/88, HE physical 14/18, parent PR119 Angular 2/3 all unchanged; physical delta 0.
- New finite *source-measured angular shape micro-unit*: S1 exact 30 contrasts/box and S2 conditional 9 model fits = **2/2 scoped**. No new canonical gate or extra stalled-DAG node.
- `kappa=null;R_event=null;heat_rate=null;physical_activation=false;L4=false;production=HOLD`.
- Next actionable science: validate angle-dependent Arends experimental detector acceptance, original ERR-S covariance and single-D vs exclusive-event counting; source original Rice numeric tables, and actual high-energy f_gamma(t,x,E,Ω) in He rest frame before physical rate, correlated fast-D stopping, escape, secondary energy and C_V. No 4501 LP, new IVP, false 330 SIG, UVB substitution, automatic merge/force push.
