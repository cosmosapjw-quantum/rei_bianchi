# REI IGM | ORIGINAL 26-event photon source Hessian + first-interval F05 research handoff (2026-11-01)

### Verified progress, not inferred

- [Draft PR #341](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/341), original science commit `2c2a1ed750e939281c7dd06a177115ff0e850e92`, exact immutable parent [PR #332](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/332) `2e3305c8ba9bff5d00412c5d79d9c1aa1e6f6e9a`.
- **Original physical execution success:** [GitHub Actions #41281907171](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/41281907171); real original 46,080 accepted source node input, four source photon groups, original 26-event photon owner, SHA original input verified. 11/11 Python and 11/11 -O Python tests, repository `verify` SUCCESS.
- New exact source-submap derivation: `p_s=a_s exp(delta_s)/(e+Σa_t exp(delta_t))`, `J_st=p_s(delta_st-p_t)`, `H_stu=p_s[(delta_st-p_t)(delta_su-p_u)-p_t(delta_tu-p_u)]`. For the original fixed-time marginal `S_s` outer box, `|R_s|<=p_s^max ||delta||_1,max^2`. **Wolfram: all symbolic derivative identities 0.**
- Actual original source-conditional photon-share 2nd-order maximum bound: `2.9615573897068414e-06`. Original ionizations: H I `6.1042634734117385e+47` s^-1, He I `5.0743677284306637e+48` s^-1, He II `0`; source photon heat `8.227132749317622e37 erg/s` (matches PR332 source-owner reference).
- Conservatively summing absolute quadratic remainders over 3 species and 4 groups yields a *source-operator Taylor approximation* bound at the frozen epoch `<= 4.4415211940847004e+45 photon events/s` (using original total incident group current `4.9990828131189868e+50 s^-1`). This corresponds to `<= 0.07813%` of reference HI+HeI absorbed photons, **NOT** an error bar on ionization history, photon conservation or CMB observable.
- Created original nodewise physical Hessian/second-order source CSV: 46,080 unique node rows, gzip SHA256 `83082e803a348e6b5cd8a55ad4431ad99d85957629e4793b14b09075ee1f6da1`. This gzip, JSON, science figures and full original execution code are in GitHub Actions artifact #13073433105 (4,244,549 bytes, 90-day retention); this raw CSV does **not** have verified permanent secondary cloud backup.
- Original source-inclusive `.tar.gz` SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`; original state arrays `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`, kernel SHA256 `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644` unchanged.
- Source-code, tests, 20 **separately indexed** R01–R10/C01–C10 checkpoint JSONs are Git-backed (26/26 identical SHA1). Portable research ZIP 25,847 bytes, SHA256 `68335c42ca38363b19c249829b45238e09d8cd66c6fb1b50e9e8222cc5503d73`, Google Drive `1WwNzaTpfZrUkJ26if8TvSVxUnLBQtVJ-`, **raw downloaded and SHA256+CRC verified**. Remote files were published in one batch after local phase checkpoints, not a separate PR per phase.

### Scientific honesty and next actual physics

The exact second-order source-moment theorem uses a **fixed tick160 forcing/clock** and outer original accepted marginal source moment boxes. It is not a mathematically certified joint 26-event physical parent set, and the separate fixed-local-numerator node Hessian does not include local numerator/source-state derivative. Floating-point interval transcendental operations are not formally machine-certified. Most importantly, the original nonlinear 4-site MPRK22/SDIRK2 `D_h(X,Theta)` implicit J and all-X remainder remain **NOT_COMPUTED**.

Original first full canonical interval **BLOCKED** at `[160,161]`, accepted `160/131072`, old independent endpoint-box metric `2.1245050576368385e-4` > unchanged strict `2e-4`. Both source and thermochemistry are unpromoted. No main merge, force-push, production mutation. Same-author referee only; no native subagent. `cosmosapjw` Remote Desktop **OFFLINE**, Exa 402 credits exhausted. GitHub Actions and original connected source provided actual physics.

**Central DAG: 28/88 (+0), Working DAG: 33/88 (reported), Fast: 4/7 (reported).** Do not add these counters, nor treat 20 stage checkpoints as 20 new science units.

**Next minimally constructive unit:** Derive original 4-site MPRK/SDIRK implicit stage Jacobian with *shared* 3 global neutral photon moments and the thermal energy/root response. Retain exact parent/source constraints; extend verified source Hessian to full `J_D` and a true nonlinear remainder enclosing all `(y,theta)` at `[160,161]`. Only if the **same original** local error `2e-4`, width `2e-3`, all three lanes and event/ledger conditions pass may the first canonical interval run resume. Avoid more adjacent point-path or metadata PRs.

### Copy/paste next-thread packet

```text
$physmath-research-loop $scispace $exa $wolfram $chrome $remote-desktop-commander
PROJECT=cosmosapjw-quantum/rei_bianchi
CURRENT_PR=341
CURRENT_HEAD=2c2a1ed750e939281c7dd06a177115ff0e850e92
PARENT_PR=332
IMMUTABLE_PARENT_HEAD=2e3305c8ba9bff5d00412c5d79d9c1aa1e6f6e9a
LAST_OTHER_SCIENCE_PR=336
PR336_HEAD=b63c4b879c0d380780719e622ef29a4a1316c025
ORIGINAL_ACCEPTED=160/131072
ORIGINAL_ARCHIVE_SHA256=a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b
ORIGINAL_SOURCE_ARRAY_SHA256=cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01
ORIGINAL_KERNEL_SHA256=579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644
NEW_PHYSICS=ORIGINAL_PHOTON_SOURCE_3MOMENT_EXACT_HESSIAN_PLUS_OUTERBOX_QUADRATIC_BOUND
ACTUAL_ORIGINAL_NODES=46080
ORIGINAL_GROUPS=4
MAX_SOURCE_FRACTION_QUADRATIC_BOUND=2.9615573897068414e-6
PHOTON_HEAT_ERG_S=8.227132749317622e37
NODES_CSV_GZIP_SHA256=83082e803a348e6b5cd8a55ad4431ad99d85957629e4793b14b09075ee1f6da1
GITHUB_CI_SCIENCE_RUN=41281907171
GITHUB_CI_SCIENCE_STATUS=SUCCESS
GITHUB_DATA_ARTIFACT_ID=13073433105
SOURCE_ZIP_SHA256=68335c42ca38363b19c249829b45238e09d8cd66c6fb1b50e9e8222cc5503d73
SOURCE_ZIP_DRIVE_ID=1WwNzaTpfZrUkJ26if8TvSVxUnLBQtVJ-
SOURCE_ZIP_DRIVE_RESTORE=BYTE_EXACT
RAW_46080_CSV_PERMANENT_DUAL_BACKUP=NOT_VERIFIED
CENTRAL_DAG=28/88_REPORTED_DELTA0
WORKING_DAG=33/88_REPORTED
PHYSICAL_FAST_DAG=4/7_REPORTED
FIRST_CANONICAL_INTERVAL=BLOCKED_MINIMUM_STEP
ORIGINAL_REJECTED_ERROR=2.1245050576368385e-4
UNCHANGED_GATE=2e-4
FULL_26EVENT_DH_JACOBIAN_REMAINDER=NOT_COMPUTED
NATIVE_SUBAGENT=NOT_RUN
DISTINCT_AUTHOR_REVIEW=NOT_RUN
REMOTE_DESKTOP=OFFLINE
EXA=402_CREDITS_EXHAUSTED
NO_MERGE=true
NO_FORCE_PUSH=true
AUTO_NEXT_NODE=false
NEXT=SOURCE_SHARED_4SITE_MPRK_SDIRK_JACOBIAN_AND_VALIDATED_ALL_X_REMAINDER_THEN_TICK160_TO161
```
