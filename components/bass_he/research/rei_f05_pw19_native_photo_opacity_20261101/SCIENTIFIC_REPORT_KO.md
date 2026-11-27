# BASS_HE → REI Bianchi IGM F05 | Original accepted 46,080-cell H/He proper photo-opacity

2026-11-01 | Draft/HOLD | One substantive source-native physics unit, not a new original IVP or canonical DAG admission.

## Scientific target and immutable source
Source-owner PR #147 immutable HEAD `c7ea4b30c25e177014d59a755621760323578cd9`. Previous BASS_HE PW19 18-row source-donor is preserved, not recomputed as a new physical data set. The original accepted REI F05 **tick160/131072** contains 46,080 genuine H/He species-state intervals in the REIADP1 binary archive, source array SHA256 `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`.

Original-source-inclusive REC #191 ZIP SHA256 `3f6772f54822274bf6228dac1ec629a9d0b0cde9d2a0adbaa08d59a1ac352d0e` includes:
- Immutable original REI 26-event source TAR SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`; accepted `LOCAL_NEUTRAL_HAZARD_PRIMARY.state` SHA256 `74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6`.
- Original 46,080 positive native `W_node` initial values SHA256 `7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d`.
- Original 17 time nodes all at z_mid=5.95, forcing CSV SHA256 `9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268`.
- Hydrogen/helium nuclei conservation: 46,080/46,080 original initial nuclear inventories enclosed by accepted species-state intervals.

PW19 input is original source Taira et al. 2025 CC0 Zenodo https://doi.org/10.5281/zenodo.15367103, unchanged ZIP SHA256 `afd470b9fd934234e7f6e815d6887814a2ff8767e61f0d2a8e6187efde8d0d55` and Verner et al. 1996 13.60/24.59/54.42 eV photo-cross sections. PR147 18-row physical donor SHA256 `080fb36c9bf4a161f58dcf23c11765bf6eeeaeb537c2fab3fd2b51304d09240b`. This is **metagalactic isotropic PW19 reference intensity**, not admitted local REI `Jnu(t,x,n)`; the three threshold bands are not the original four photon groups.

## Constructive theory and actual science
In `(-,+,+,+)`, comoving-gas proper tetrad, original cell volume `V_j=W_j (Mpc in cm)^3/(1+5.95)^3`; `n_{s,j}^proper=N_{s,j}/V_j`. At fixed frequency-source donor:
`Phi_g = ∫_g I(E)/(E ε_eV) dln E` [photons cm^-2 s^-1],
`μ_{s,g}=Phi_g^-1∫_g [I(E)/(E ε_eV)]σ_s(E)dln E` [cm²],
`κ_{g,j}=Σ_s n_{s,j} μ_{s,g}` [cm^-1]; `λ=κ^-1` [cm].
The associated photo-rate density is `c nγ,g κ_g=Σ_s n_s Γ_s,g` [cm^-3 s^-1], with `nγ,g=Phi_g/c`. Thermal excess heat `Σ_s n_s H_s,g` plus `Σ_s χ_s ε_eV n_s Γ_s,g` equals absorbed photon energy in this fixed external spectrum, before original OTS, collisional, recombination, cooling or cosmological redshifting. Do not claim this as the actual native REI energy ledger.

For frozen homogeneous material of proper length `L`, exact spectral transmissivity `T(L)=〈exp(-κ(E)L)〉` and fixed-grey `Tgrey(L)=exp(-〈κ〉L)`. Jensen guarantees `T≥Tgrey`, and `d²ln T/dL²=Var_survivors(κ)≥0`. Wolfram algebraically verified the two derivative identities; no claim of end-to-end formal proof of the imported numerics.

## Executed original-source numerical physics
Original-source **46,080 native proper volumes**, total `8.751796724989945e70 cm³`, all original accepted 5-species lower/upper state arrays and positive nuclei. New 46,080-row 3-band physics CSV at `results/ORIGINAL_REI_T160_PW19_LOCAL_PHOTO_OPACITY_46080.csv.gz`, SHA256 **`fa574b50930f7b7157ead6e988a0bf50ddbb01fd0c253cc53912636358c3a79a`**; summary `results/SCIENCE_RESULT.json`, SHA256 **`dc8ba2eb688113b62dadbe3abb974779563ad3960354804d8090bc977c1c384f`**.

Absolute original tick160 neutral-population interval gives total **conditional** PW19 photo-events/sec `[4.644030187806854e50,4.645900150482617e50]`, enclosing previous original frozen point `4.6449651691447255e50`. The 54.42 eV–50 keV band's proper-volume-weighted H/He material photo-opacity contribution from HeII is **0.9997761023196687**, with original 46k cellwise min/median/max `[0.983775480204227,0.9998792327409174,0.9999919225421396]`.

At **one chosen original local mean free path** `L=1/κ_g` for representative real native cells (a diagnostic, **not** actual Bianchi observer light cone): grey `e^-1=0.36787944117144233`, full spectral HI-only `≈0.400922`, HI+HeI `≈0.394–0.400`, hard HeII-containing band `≈0.82777`. The strong hard-band spectral-hardening gap is a real conditional matter/spectral functional. Original REI G3 hard photon current is effectively zero: **the 99.98% helium photo-opacity contribution does not imply actual HeII ionizations or heating by native REI photons**.

## Targeted verification and hostile audit
Original ZIP/TAR/state/initial NPZ/forcing exact SHA guards, original population and charge/nuclei/volume checks, source-directed *conditional* spectral weights. `tests/test_native_source.py` full native input: **16/16 normal, 16/16 Python -O PASS**; includes altered-original-hash negative test and byte-exact cold rerun. Original initial test expected positive absorbed energy even for zero event channels, causing a **test oracle FAIL**; fixed zero-event branch expectation without adjusting physical source or numerical tolerance. Source-free `verify_published_receipt.py` also **PASS_PUBLISHED_RECEIPT_ONLY**, reads all 46,080 derived rows but does NOT verify original REC ZIP. GitHub CI runs source-free receipt check only.

Independent second algorithm `audit_independent.py` (same author, NO different-author referee) reconstructed original source, 46k×3 κ and wavelength-independent donor σ with max full-cell relative disagreement **5.549732530578375e-16**; re-evaluated nine spectral transmissions with independently integrated **40,000 per-band** log-frequency samples, max absolute discrepancy ≈`8.592e-7`. Output `results/INDEPENDENT_AUDIT.json`, SHA256 `50f32d31ce23f506741d0c1e73d33312c9b4197902859edaabf912c99649d235`. No raw MPFR/CRlibm end-to-end directed-rounding theorem. Native subagents NOT_RUN.

## Drift watchdog and actual central owner return
One scientifically useful material-source opacity unit; **STOP** new auxiliary PW19/static-opacity atlases and repetitive estimator PRs. Source-owner RUX03 has one properly evaluated original-material photo-opacity dependency; still lacks original local causal incident spectral/angular/emission history, external/OTS photon + thermal transport match, and Einstein-compatible FLRW/Bianchi clocks. RUX04 NOT_ADMITTED. Next central action belongs to original REI owner: versioned first tick161 F05 original worker acceptance/early exact parity, or original-source matched FLRW/Bianchi ray+ionization integration, preserving original photon remapping spectral-support error documented by BASS PR321. No source replacement, no new native IVP or observed CMB optical depth.

Counts at every bounded stage: REI CENTRAL **28/88_REPORTED**, WORKING **33/88_REPORTED**, FAST **4/7_REPORTED**, BASS_HE PHYSICAL **14/18_REPORTED**, canonical delta **0**. `PRODUCTION=HOLD; NO_MERGE; NO_FORCE_PUSH; NO_TOLERANCE_RELAXATION; AUTO_NEXT_NODE=false`.

Reproduce: `OPENBLAS_NUM_THREADS=1 python3 native_photo_opacity.py --rec-zip /home/cosmosapjw/research_backups/rec_bianchi/REC191_ORIGINAL_F05_NATIVE_THOMSON_MEDIUM_SOURCE_FULL_20261101.zip --out results`, `REC191_FULL_SOURCE_ZIP=... OPENBLAS_NUM_THREADS=1 python3 tests/test_native_source.py`, `python3 -O tests/test_native_source.py`, `OPENBLAS_NUM_THREADS=1 python3 audit_independent.py --rec-zip ...`, `python3 verify_published_receipt.py`.

References: Friedrich et al. 2012 https://doi.org/10.1111/j.1365-2966.2012.20449.x ; Pawlik & Schaye 2011 https://doi.org/10.1111/j.1365-2966.2010.18032.x ; Puchwein et al. 2019 https://doi.org/10.1093/mnras/stz222 ; Verner et al. 1996 https://www.pa.uky.edu/~verner/photo.html ; Taira et al. 2025 https://doi.org/10.5281/zenodo.15367103.
