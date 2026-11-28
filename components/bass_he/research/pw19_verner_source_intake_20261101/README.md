# BASS_HE → REI: original PW19 spectral source intake (2026-11-01)

**STATUS: SOURCE-CONDITIONAL / DRAFT / HOLD.** This is one physically sourced spectral supplier unit, not an accepted REI RUX04 source, 4-group photon current, cosmological IVP, or observational datum. No source model or original REI accepted state was changed. REI central **28/88 REPORTED**, working **33/88**, physical fast **4/7**, BASS_HE physical **14/18**, all **delta 0**. No new canonical admission.

## Source and model authority

* Original UVB data: Taira, Kopenhafer & O'Shea (2025) [DOI:10.5281/zenodo.15367103](https://doi.org/10.5281/zenodo.15367103), reformatted PW19 source; pinned v1.0.0 source ZIP SHA256 `afd470b9fd934234e7f6e815d6887814a2ff8767e61f0d2a8e6187efde8d0d55`, Zenodo MD5 `2c8790767866ca446d13660043224d67`. Exact original z=5.807 and 6.141 CSVs, 626 energies each; SHA256 `475a6e943e135902bfbf5c249a3aa84a1dbee768a2fa781ff25582a151dd9065` and `f896dd5b5d664bbe273c89a7ce2a5141e698c2d56a298d5a3ab570ff044a9980`.
* Original frequency-dependent photoionization cross-section formula: Verner et al. (1996), ApJ 465 487, DOI:10.1086/177435, Table 1 H I, He I, He II. Fit support E=threshold to 50 keV; no extrapolation >50 keV.
* Source meaning: `I(E)=4πνJν` (angle-integrated intensity times frequency), with units erg/s/cm² **per d ln E**. The script integrates `Γ_s=∫I(E)σ_s(E)/(E ε_eV) dlnE` and `H_s=∫I(E)σ_s(E)(1−χ_s/E) dlnE` (erg/s/neutral). The Taira CSV is **not** `J_nu` itself and must not be multiplied by `4πν` again.
* z=5.95 is an explicitly chosen interpolation between the **source knots**, with log-intensity and linear-intensity alternatives. Exact original intensity zero at **48.355849560166504 eV** is preserved as zero, never floor-replaced. Fit threshold energy and physical ionization potential are separately defined.

## Numerical scientific result at z=5.95 (log intensity in z)

| Species | Source-derived Γ [s^-1/neutral] | Excess heating [eV/s/neutral] | Excess energy per event [eV] | Ratio to existing Puchwein19 Table D1 effective Γ |
|---|---:|---:|---:|---:|
| H I | 6.563816010575724e-13 | 2.5104549999523157e-12 | 3.8246882543743315 | 10.112115817111373 |
| He I | 3.264700888771998e-13 | 1.8488237711337598e-12 | 5.663072465512105 | 7.008525973380063 |
| He II | 1.1316533742685503e-17 | 4.846325794601765e-16 | 42.82517867040526 | 1.2641625462213724 |

The PW19 *radiation spectrum* rates and published/previously pinned **neutral-weighted effective D1 rates are not interchangeable**. Large H/He discrepancies are a **source-operator mismatch**, not an assertion that the literature UVB is numerically wrong. The original REI photon owner remains separate. BASS_HE can contribute the conditionally calculated spectral input plus provenance, **not** invent local 4-group source currents.

Hard photon exposure from 54.42 eV to 50 keV is nonzero (224.647308695533 photons/cm²/s), which does **not** cure native REI G3 near-zero source current. Any future import must bind actual local emissivity, attenuation, source time, spectral group mapping and energy/ionization ledger.

## Run and validation

Run `python3 fetch_source.py` (writes only a verified local source ZIP), then `python3 spectral_physics.py` and `python3 independent_audit.py`. Both scripts use only Python standard library. Results are source-conditional and no new IVP is run. The main algorithm checks 8 vs 16 Simpson log-energy subdivision for 4 spectral scenarios; the same-author independent auditor computes uniformly spaced midpoint integration over 120,000 bins per species, verifying actual energy absorption and heating consistency. **Distinct-author referee NOT_RUN**. This independent audit does not certify astrophysical source equivalence.

**Hostile findings:** First run failed on a real zero-intensity CSV row, repaired with zero-preserving interpolation. Initial He I quadrature had 0.1964% false edge contribution because two adjacent bands both included the threshold endpoint, fixed by species-eligible band masks rather than relaxing tolerance. Material physics uncertainties include spectral redshift interpolation, Verner fit domain/uncertainty, homogeneous vs neutral-weighted UVB, and unbound REI group/local source. No further support-only atlas before central owner action.

**STOP / next decisive science:** REI owner must accept/reject its original F05 [160,161] V2 shadow discrete certificate, or admit a causal H/He local frequency/time/emissivity/absorption and thermal source RUX04 and then run first matched FLRW/finite-shear BI physical intervals. NO_MERGE, NO_FORCE_PUSH, NO_PRODUCTION, NO_NEW_IVP, AUTO_NEXT=false.

Parent is immutable BASS_HE PR #146 HEAD `b3b4d95e93999e86a26a3c9719adb739d5865ce4`; REI owner PR #353 theory HEAD `2e04037fbc174e71ed1bee313f2b554257ede4b9` (V2 still SHADOW).
