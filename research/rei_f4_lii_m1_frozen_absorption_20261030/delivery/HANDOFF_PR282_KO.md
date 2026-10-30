# REI F4 · PR282 source-owned Li II M1 국소 광흡수 handoff (2026-10-30)

**반드시 GitHub PR282의 실제 최신 HEAD를 먼저 읽어라.** 문서 본문 HEAD는 최종 보고서 작성 전 pre-delivery checkpoint이며 자기 SHA를 사전 생성하지 않는다. 신규 IVP/merge/force-push/예산 초기화/자동 다음 노드 불허.

```text
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/rei_bianchi
CURRENT_PR=282
BRANCH=research/rei-f4-lii-m1-native-frozen-absorption-20261030
PRE_DELIVERY_HEAD=8e6f93367745cf105abe1ef5e280c26a75c2609a
READ_LIVE_HEAD_FIRST=true
PARENT_PR=281
IMMUTABLE_PARENT_HEAD=e64dd58859c38d1d2040757f32c512221c4ca236
READ_ONLY_RELATED_PR=279;280
UNIT=LI_II_M1_SOURCE_MATCHED_FROZEN_ABSORPTION
SOURCE_OWNER_BASS_COMMIT=cc602e209e7deeb511ab2a1f3b2268d55206c43c
PR278_SOURCE_SHA256=df871a18f297da15d05a5dadbad55e2aa29571217ad9136d9c4826921d1a11db
PR280_SOURCE_SHA256=fd9b8343ed2ea48b6caa9eff8aa5592d34a75fb77cfe223c81af3afbd8a21a91
MASTER_ZIP=REI_F4_LII_M1_FROZEN_ABSORPTION_20261030_FULL.zip
MASTER_BYTES=10533802
MASTER_SHA256=a0f15cab2a283c1cfdf5c2a1fa8d2bc1fe9e232c1754cdaf4625ca0ff65107c0
GDRIVE_ID=1APTfDHd-RnXjz0fWz6_lYTdd2OyyOp7a
GDRIVE_RAW_SHA256=PASS
LIBRARY_MASTER=UPLOADED
DROPBOX_BINARY=NOT_UPLOADED
CLEAN_RESTORE=PASS
TESTS=16/16_PASS
MANIFEST=45/45_PASS
REGENERATED_DATA_SHA=3/3_PASS
GIT_CORE_STAGE=39/39_EXACT_BLOB
STAGE_GIT_ACK=20/20
STAGE_DRIVE_ACK=20/20
STAGE_EXECUTION=18/20_SCOPED
R6_C9_DISTINCT_AUTHOR=NOT_RUN
NATIVE_SUBAGENT=NOT_RUN
NEW_IVPS=0
WORKING_DAG=33/88
CENTRAL_DAG=28/88
PHYSICAL_FAST=4/7
CANONICAL_DELTA=0
F4=PARTIAL
L4_READY=false
NO_MORE_IVPS=true
NO_MERGE=true
NO_FORCE_PUSH=true
AUTO_NEXT_NODE=false
NO_BUDGET_RESET=true
PRODUCTION=HOLD
NEXT_UNIT=PHYSICAL_LINE_BRANCHING_OR_FULL_REI17_BASS21_OWNER
STOP_AFTER_ONE_NODE=true
```

## 실제 물리 데이터

원본 BASS21 저장 epoch 193개 × 원본 ion 21개: 4053 source-native photon-opacity/first absorption 행. Li II M1 Eγ=59.020723673eV, BASS native Verner σ. 고정 현시점 κ=nb ΣYiσi, p_i=Yiσi/ΣYjσj, λ=κ^-1, τH=cκ/H, 초기 광전자 에너지 평균 Σp_i(Eγ−Ei). z20→z2: κ 3.74711085585e-20→2.00503547827e-26 m^-1, λ 864.874→1.6163e9 proper pc, τH 94917.27→0.907697, HeII 조건부 첫 흡수 비율 0→0.994507659, 광전자 초기 에너지 39.4460→4.82487 eV. HeII 비율 1/2 교차 저장격자 z∈(9.122960,9.226078); τH=1 교차 z∈(2.061430,2.092615). 모두 원본 동결점 데이터이며 연속 RT·actual optical depth가 아님.

## 입력·검증·저장

- Git source path: `research/rei_f4_lii_m1_frozen_absorption_20261030/`. `code/m1_absorption.py`, tests, two raw CSV, `results/RESULTS.json`, reports, 20 stages and delivery receipts posted; 39 science+stage blob identities exact vs local frozen files.
- Full source archived including PR278 and PR280 original ZIPs and plot PNGs: 10,533,802 byte SHA256 a0f15cab2a283c1cfdf5c2a1fa8d2bc1fe9e232c1754cdaf4625ca0ff65107c0.
- Clean extraction `bash VERIFY.sh` exit0, 16/16 targeted Python, independent mpmath80 H/He σ, Wolfram three exact residual zeros, manifest 45/45, regenerated data 3/3.
- Drive https://drive.google.com/file/d/1APTfDHd-RnXjz0fWz6_lYTdd2OyyOp7a/view complete raw readback full SHA/size; Library `/REI_F4_LII_M1_FROZEN_ABSORPTION_20261030/` ACK, Dropbox binary NOT_UPLOADED.
- Every R1–R10/C1–C10 has a distinct retrospective Git commit and Google Drive upload; actual IDs in `delivery/STAGE_UPLOAD_ACKS.json`. This is NOT 20 independent live jobs; R6/C9 author-independent NOT_RUN.

## Remaining physical owners

Separate PR279/280 unresolved singlet/triplet yields, Li II 2E1 differential dA/dE, anisotropic/finite-time photon transport, secondary electron energy deposition, source-matched REI17↔BASS21 full F/J with Li6/T/nuclear/CR/fast and electron/thermal/radiation and nHref/nb,H,K, common proper clock. Source-owned M1 emission *capacity*, not actual emissivity. Photon photoabsorption point data, not actual heat or Δτ/CMB. No new IVP until separate approval; do not promote F4/L4 or canonical DAG.

Stop after one bounded next node if separately authorized. Do not run or schedule it from this handoff.
