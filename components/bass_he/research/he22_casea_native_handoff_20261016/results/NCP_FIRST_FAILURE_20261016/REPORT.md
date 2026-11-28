# HE22 NCP native execution: HOLD at first density gate

Actual execution on 2026-10-16 KST, isolated from `/root/BASS_HE` and active rei jobs.

## Immutable inputs

HE21 `579ffbce28f988aadb51c377b15f348e4c0359af`; delivered HE22 `0514b6bbb97902b29abe939b270394397354ba00` (tree `132dc2b5af157f352957623be458b24afa508444`). Original rei_bianchi `f7830e2f55e7a1938bc3c98f61b60651f8dae474` (tree `c4b499b95f510910f673f386e3986bd4f8159a69`). C19 reference fetched separately at `e91ffe368c4e6db64c4b6c5962566302a33402b6`.

Owner-provided `/root/BASS_HE_HE22_NCP_HANDOFF_20261016.tar.gz` and authenticated Drive download have SHA256 `a5ee858a9343ce9d892b5577c92c550229c3ec2a02d97439078fa2a8ff85fb89` (63042 bytes). All 20 internal SHA checks passed. All 17 shared public Git/archive files match exactly. HE21 photo source matches the pinned parent SHA256 `3df86063f12e238ec41219343a016b3a5086d18ce973015c335ec8118d9a5b66`.

## Measured execution

NAVERCloud x86_64 Xeon Gold 5220, 64 vCPU, 125 GiB RAM, 1 NUMA node. Rust 1.99.0; opt-level=2, edition=2021, no fast-math; OpenBLAS/OMP/MKL threads=1. Isolated Python 3.12 venv; full versions in logs/environment.txt. No performance speedup claim.

Command: `HE22_WORK_ROOT=/root/HE22_NCP_20261016 bash research/he22_casea_native_handoff_20261016/ncp/NCP_BOOTSTRAP_AND_TEST.sh` from the isolated clone. Exit 1. Original rlib and HE22 wrapper compiled successfully. Delivered focused tests: 24 passed in 3.66 s. These include constructed test doubles; they are not native scientific acceptance.

Native binary SHA256 `16ab38349995dd9ace5796e83ee14d298509f9d5e3c66641a3872db47fcaca58`. Source files and rlib identities are separately recorded.

Pilot q=0,m=4,n=2: first failure `HE22_NATIVE_DENSITY_OR_HELIUM_SOURCE_MISMATCH`, runtime 0.083673627 s, all_pass=false. No completed chemical step, no final gas state. Matrix 0/12; convergence NOT_RUN because pilot failed. No unchanged historical scientific suites rerun.

## Root-cause evidence (IMPLEMENTATION / scientific-input contract)

A single diagnostic first-point capture used the unchanged coupler's exact first input, stopped immediately after one original Rust evaluation, and saved argv, returncode, raw stdout/stderr. It is not another pilot or acceptance result.

At a=0.047620181473387826: HE21 expected nH=0.0017574444586802788 cm^-3; native nH=0.0017577960178838546 cm^-3. Relative mismatch=0.0002000400080011122 versus fixed 1e-9 tolerance. Both helium/H ratios=0.08130135170951498. This is a density failure, not helium or a native process crash.

C19 commit's `research/cr_c10_source_subcells_20261015/README_KO.md` and `REI_SOURCE07_C6_HANDOFF_KO.md` explicitly call 0.0017575700008892194 the proper *neutral HI* density. HE21 uses it as total N_H_Z20 and then multiplies by the evolving neutral fraction. The native baseline instead derives total hydrogen nuclei from omega_b, critical density and proton mass. Expected/native density ratio is approximately 0.9998. This is evidence of neutral-density versus total-nuclei ownership confusion; it does not by itself authorize a changed model.

No physical inputs, source budgets, initial fractions, normalization, tolerances or library code were changed. AGENTS.md chat-first policy requires returning scientific-input changes to the research thread. Next prerequisite is an authored density/per-H/source normalization contract and affected regression evidence, preserving the existing HE21 reference. Merely relaxing density validation is invalid.

## Bounded physics evidence

Original Rust point returned T=8.097757410023563 K, positive finite photo/CI/RR fields and zero DR for this cold first state. Its instantaneous thermal+binding+escape-CMB-photo identity residual is 0 in binary64 evaluation. Raw values and units are in diagnostic/POINT_LEDGER.json. This point uses the incompatible native density, so it cannot certify coupled photon/event ownership.

Integrated photon number/energy, binding, photoheating, photon/gas work, escaped energy and CMB balances: NOT_VERIFIED; pilot stopped before acceptance. Time/frequency/angular convergence: NOT_RUN. No astrophysical EoR or observational CMB admission.

Pinned igm_rates.rs documents a Rust port of selected Grackle 3.4.1 rate functions at af7939494ce65007887ada7b98d1813df6843346, with documented CI floors/CE caps and DR treatment. It explicitly says no raw-provider call. igm_thermal.rs uses separate CODATA Thomson/blackbody Compton exchange, not Grackle's rounded comp_rate. Thus this build is actual original rei_microphysics execution, NOT direct linking/execution of upstream Grackle. Upstream Grackle runtime equivalence, active DR behavior and full chemistry remain unresolved. C19 CLI source was inspected; matched-checkpoint numerical comparison was not run after density failure.

## Preservation and claim boundary

First bootstrap log and pilot JSON are preserved unchanged. Private archive includes raw diagnostic bytes, input archive, build binaries and source-content hashes; public PR contains no private handoff connection instructions or attached PDFs. Backup receipts are separate immutable artifacts so the archive does not recursively contain its own hash. Existing worktree, production jobs and existing PRs were not modified.

Status: BUILD_PASS; PYTHON_TESTS_24_PASS; NATIVE_PILOT_HOLD_FIRST_FAILURE; MATRIX_NOT_RUN; FULL_EOR_AND_OBSERVER_CMB_HOLD. Independent scientific review remains separate and is not claimed here.
