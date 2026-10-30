# REI F4 | PR286 verified source-cone delivery, 2026-10-30

**Read GitHub PR286 live HEAD before any continuation.** This handoff is intentionally committed after the immutable science ZIP and uses PRE_DELIVERY_HEAD rather than guessing its own commit SHA. Original PR284 and sibling PR285 remain unchanged.

```text
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/rei_bianchi
CURRENT_PR=286
CURRENT_BRANCH=research/rei-f4-lii-2e1-ocr-free-source-cone-20261030
READ_LIVE_HEAD_FIRST=true
PRE_DELIVERY_HEAD=5d22085ac8a0de938a5b6d6a264bfc0fb339a5bf
SOURCE_PARENT_PR=284
IMMUTABLE_SOURCE_PARENT_HEAD=661f34c5216aa52402be6f9db5c16ab2e55ecfb3
OVERLAPPING_SIBLING_PR=285
SAME_SCIENTIFIC_NODE_AS_PR285=true
SOURCE_PR284_ZIP_SHA256=fa3e5f2a5cc0eaaa458372dbd2d926ad6829451a16a04b1bd220b3abb26747c9
UNIT=REI_F4_LII_2E1_OCR_FREE_SHARP_CONE_20261030

MASTER_ZIP=REI_F4_LII_2E1_OCR_FREE_CONE_20261030_FULL.zip
MASTER_BYTES=12125019
MASTER_SHA256=98b99f762fc63e83030279dd72f9aa871388bafe80a44ba9b3d9f8de5486ed3b
GDRIVE_ID=1gLYRwE3sXV4PjkJyImqswagfQMsG4C5H
GDRIVE_RAW_SHA256=PASS
LIBRARY_MASTER=UPLOADED
DROPBOX_BINARY=NOT_UPLOADED

TARGET_TESTS=14/14_PASS
MANIFEST=41/41_PASS
ZIP_CRC=PASS
CLEAN_RESTORE=PASS
DETERMINISTIC_RESULTS=4/4_SHA_PASS
GIT_FROZEN_FILES=39/39_EXACT_BLOB
STAGE_GIT=20/20_INDIVIDUAL_COMMITS
STAGE_DRIVE=20/20_INDIVIDUAL_UPLOADS
STAGE_SCIENCE_SCOPE=18/20_RETROSPECTIVE
R6_C9_DISTINCT_AUTHOR=NOT_RUN
NATIVE_SUBAGENT=NOT_RUN
ADVERSARIAL_SAME_AUTHOR_REVIEW=RECORDED
DRAKE_1969_LI_II_TABLE_VISUAL=NOT_VERIFIED
CHIANTI_DERIVED_SOURCE_RAW=NOT_DOWNLOADED

SOURCE_EPOCHS=193
BOUNDED_CHANNEL_ROWS=4825
SOURCE_GENERATOR_ROWS=7720
PROVEN_HAT_GENERATORS=20
CONDITIONAL_MONOTONE_GENERATORS=20
NEW_IVPS=0
ORIGINAL_WORKING_DAG=33/88
ORIGINAL_CENTRAL_DAG=28/88
ORIGINAL_PHYSICAL_FAST=4/7
CANONICAL_DELTA=0
NEW_AUXILIARY=1/1_SAME_NODE_AS_PR285
F4=PARTIAL
L4_READY=false
PRODUCTION=HOLD
NO_MORE_IVPS=true
NO_MERGE=true
NO_FORCE_PUSH=true
NO_BUDGET_RESET=true
AUTO_NEXT_NODE=false
STOP_AFTER_ONE_BOUNDED_NODE=true

NEXT_UNIT=VISUALLY_CERTIFIED_DRAKE1969_LI_II_2E1_OR_REAL_LI1S_SINGLET_TRIPLET_BRANCHING
NEXT_ACTION=Obtain original physically printed Table II Li II ordinates on p29 of Drake et al 1969, or source-owned CHIANTI heseq_2photon.dat with clear secondary provenance; state-resolved Li 1s spin/charge partial cross-sections; or full common REI17/BASS21 F/J + thermal/electron/radiation+H,K,nHref/nb clock. Do not equate conditional frozen first absorption with actual heat/ionization or CMB optical depth.
```

## Scientific claim / scope

For 21 equally spaced nodes y=j/40 (j=0..20), A(0)=0, 21-node piecewise-linear nonnegative density, any normalized linear response is a convex mixture of 20 normalized positive hats and thus min/max over these is mathematically sharp *within this finite interpolation family*. If monotonicity of 1969 ordinates is separately assumed, a different normalized set of 20 cumulative-step generators supplies another sharp interval. Neither mathematical family proves an actual continuous Li II 2E1 source or that monotonicity holds. Original PR284 Drake Table II amplitudes are used for a parent witness only, not to produce the cone boundaries.

Original BASS21 frozen 193 points provide 193 epoch rows, 4,825 5×5 channel bounds and 7,720 generator responses. At z2, P2 lies in positive [0, 0.0022824618114819333] or optional monotone [0.0008934561285468938, 0.0015216821922610583], parent witness .001115920147. Source-integrated all-singlet *conditional* two-absorption events per baryon positive [0, 3.0150735281263275e-11], optional monotone [1.711724978952485e-11, 3.0150735281263275e-11], original parent witness 2.1745145060967717e-11. Across 193 epochs one common spectrum is fixed before integration. Formal interval bounds for finite quadrature were NOT_RUN; error between Gauss 8/16 about 9e-16. Nonlinear covariance and total variation are not covered by the simple convex linear extremum theorem.

## Adversarial review and unresolved source

Same-author hostile review recorded a concrete counterexample: isolated nonmonotone positive hat at y=.025 has z20 P2=0 whereas *conditional monotone* lower bound is 0.567724678. It also prevents falsely integrating epochwise minimum and calling it globally sharp, misapplying linear bounds to nonlinear covariance, declaring OCR values visually verified, or treating initial photoelectrons as deposited heat. Real distinct-author independent R6/C9 remain NOT_RUN.

The source file reference needed is **Drake, G. W. F.; Victor, G. A.; Dalgarno, A.**, “Two-Photon Decay of the Singlet and Triplet Metastable States of Helium-like Ions,” *Physical Review* **180**, 25–32 (1969), **page 29, Table II, Li II column**, DOI https://doi.org/10.1103/PhysRev.180.25. Repository original PDF candidate https://uwindsor.scholaris.ca/bitstreams/0cd0ebf7-0164-4c22-9aaa-71af11cfea5f/download (previous HTTP403, printed digits NOT_VERIFIED). Secondary **CHIANTI** continuum file `heseq_2photon.dat` at https://soho.nascom.nasa.gov/solarsoft/packages/chianti/dbase/continuum/heseq_2photon.dat (not yet raw-verified). For physically source-owned Li I 1s singlet/triplet partial cross-sections, inspect Ferrett et al., *Phys. Rev. A* **36**, 3172 (1987), DOI 10.1103/PhysRevA.36.3172; Langer et al., *Phys. Rev. A* **43**, 1652 (1991), DOI 10.1103/PhysRevA.43.1652; Vo Ky et al., *Phys. Rev. A* **57**, 1045 (1998), DOI 10.1103/PhysRevA.57.1045. Publication/energy range must be verified prior to using any numerical branching.

## Recovery

Immutable complete science ZIP https://drive.google.com/file/d/1gLYRwE3sXV4PjkJyImqswagfQMsG4C5H/view ; run `bash VERIFY.sh` from clean ZIP extraction (Python NumPy/SciPy/Matplotlib). The ZIP contains PR284 original source ZIP byte-for-byte, scripts, tests, all data rows, plots, and 20 retrospective stage JSONs. Git PR286 `research/rei_f4_lii_2e1_ocr_free_cone_20261030/` has exact 39/39 original text/CSV Git blobs, plus extra post-freeze delivery/FINAL_ACK.json and delivery/STAGE_ACKS.json. All source and backup scopes distinguish immutable master from handoff. Since sibling PR285 has same physical node and archive identity, never count a second 1/1 auxiliary or modify original DAG totals when evaluating these two PRs. Draft PRs remain unmerged.
