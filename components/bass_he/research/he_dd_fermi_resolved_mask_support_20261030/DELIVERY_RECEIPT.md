# BASS_HE PR118 | Fermi high-latitude resolved photons × EXFOR physical-data closeout

Date: 2026-10-30 KST. Current Draft PR118, add-only child of frozen PR117 HEAD `621fee964e6847f4e8c948c7ac7c193e46db5698`. **Read the actual PR118 final HEAD after this document commits; do not predict its own commit.** No merge/force push/parent or production code mutations.

## New science (empirical input versus mathematical model)
Fermi-LAT Ackermann et al 2015 ApJ799:86 source table3 original 78-record published-data **third-party Git mirror**, SHA256 `a78ced8234a7eb104a5f5b406a6bc609591ec2c323a26008625b239b5dccc0e5`, Git blob `794cb6fcbef243be950613475c4254d6ab3877a4`. This is not verified byte-for-byte original CDS `table3.dat`. The previously unused source-resolved high-latitude `fsrc` component is measured above |b|>20° in 200–282.8 and 282.8–400 MeV windows: `4.092e-7`, `3.026e-7` cm^-2 s^-1 sr^-1. It is a single source value repeated in A/B/C, **not three independent observations**; unlike full-sky IGRB, no full 4π normalization.

EXFOR M0475003 original six experimentally reported SIG knots at Eγ=201/225/253/285/320/359 MeV and reported σ=(2.41,1.29,.92,1.04,.61,.55) nb, original IAEA Git blob `c49433293921dbb012d7f1b0387745732a598efa`. No measured 330-MeV total SIG. Define `g(E) = sigma_lin(E) 1_[201,359](E)` as a **restricted diagnostic**; the indicator is NOT a claim σphysical vanishes elsewhere. Given measured energy-integrated photon intensity and an otherwise arbitrary nonnegative within-bin source distribution, derive sharp support-restricted interval `0 <= Gamma_like_mask <= Omega_H*1e-33*(2.41*I1+1.04*I2)` with `Omega_H=4*pi*(1-sin(20deg))=8.268418735752577 sr`, upper `1.075618749129087e-38 s^-1 per He`. Conditional additional flat within-bin shape `5.41491699924193e-39 s^-1 per He`. Born pair kinetic-weighted separate upper `2.12407326900785e-36 MeV s^-1 per He`, conditional flat `1.23812256990148e-36 MeV s^-1 per He`. This is neither actual event rate nor thermal heat, and not upper bound of FULL physical event rate.

Literature: Rice et al Phys Rev C61 064612 (2000) original absolute 4He(gamma,dd) dσ/dΩ at six angles and two energy bins 150–190,190–250 MeV, and Asbury/Loeffler 1965 mean E221/265MeV, original numeric rows NOT acquired, DO NOT invent. Arends/Silverman detector event-vs-inclusive normalization and target-rest physical MeV gamma history plus D-fast stopping and Cv still OPEN.

## Executed code, data, and checks
Remote Git add-only `src/mask_bounds_min.py` blob `3cf3023bf80745b6c1bf2398b80edd9fcbe243bf`; focused `tests/test_mask_bounds_min.py` blob `81e49ff68a9c8a1675913f062461cef946bf3099`, byte-equal to local tested files. Original Fermi source and EXFOR source copied byte-exact from PR117. Git `results/RESOLVED_MASK_CONCISE_ATLAS.json` and `results/BORN_PAIR_KINETIC_POSITIVE_ENVELOPE.json` are the compact seven-row physical data results. Full source `src/resolved_source_bound.py` and companion 13 tests + detailed JSON/CSV reside in portable local full ZIP; **not separately posted as those same exact full-file Git paths**, so do not claim entire source ZIP equals Git tree.
- Local new focused Python 7/7 PASS, full local 13/13 PASS, combined 20/20 PASS, compileall PASS.
- Independent **algorithm** Wolfram exact rational flat-bin integrals and mask geometry support numbers; distinct-author native R6/C9 **NOT_RUN**; Git commit status CI not assumed.
- No old IVPs, 4501 node LP or full production suite.

## Actual checkpoint and provider acknowledgments
- R01–R10 C01–C10 = 20 **real distinct Git stage commits**; full stage ID/40char SHA, DAG at each and two-provider text ACK/readback in `STAGE_LEDGER.json`.
- Google Drive stage doc: https://docs.google.com/document/d/14DlO6wO5NhfpKrdezJaLt0Fwnvr8Trdn6a9Ax2TU-vY/edit , **20/20 stage text rows read back**.
- Dropbox Paper stage doc: https://www.dropbox.com/scl/fi/9n0ri1xxzxj8zfdftmwsk/BASS_HE-DD-Fermi-resolved-high-latitude-mask-20261030-stage-log.paper?rlkey=ql5mwfeg7fek1bdwjqtasdrpm&dl=0 , **20/20 stage text rows read back**.
- Portable local ZIP `BASS_HE_FERMI_RESOLVED_MASK_20261030_FULL.zip` **118809 bytes** SHA256 `e8e5b0794ebe54a0f0133f399d54174ede3b85af36602c46a99de4067ef15d58`, 34 entries including 33 hashed payloads, ZIP CRC + payload SHA all PASS, nested PR117 ZIP original checksum PASS. **Fresh isolated extract** executed `bash REPRODUCE.sh`: Python20/20, compileall PASS, regenerated source-based JSON+CSV byte-identical. 
- Library upload ACK: `/BASS_HE_HE_DD_RESOLVED_20261030/BASS_HE_FERMI_RESOLVED_MASK_20261030_FULL.zip` Library file `libfile_c906494590708191b3bc6ce115f19a70`.
- Google Drive full ZIP upload ACK file `1vTo8K5j3COZ42VN-baw12fwARo5QUDeK` (https://drive.google.com/file/d/1vTo8K5j3COZ42VN-baw12fwARo5QUDeK/view). **Google Drive raw binary restored** to container, 118809 bytes, `cmp` original and readback = equal, both exact SHA256 above, restored ZIP CRC PASS.
- Dropbox binary full ZIP upload/readback **NOT_RUN**. Dropbox Paper text ACK is **not** binary dual restoration.
- Internal ZIP's ledger snapshot was written BEFORE cloud upload and truthfully says Drive ZIP backup NOT_RUN at that moment. This FINAL Git receipt plus current `STAGE_LEDGER.json` are authoritative LATER cloud readback.

## Physics and DAG final
Central **28/88**, HE physical **14/18**, parent Fermi ABC auxiliary **3/4 scoped**, NEW resolved-mask auxiliary **2/3 scoped** (S1 actual source and mask, S2 reported-SIG conditional positive response, S3 physical event+deposition source still missing), physical_delta=0.
`kappa=null; R_event=null; heat_rate=null; physical_activation=false; L4=false; production=HOLD.`
Distinct-author R6/C9 NOT_RUN. No merging, no force push. Next physically meaningful target is the original Rice numerical DA or Arends detector counting, true proper-He-frame MeV photon phase-space and its cosmic history, then nonthermal D_fast slowing/escape/deposition. 
