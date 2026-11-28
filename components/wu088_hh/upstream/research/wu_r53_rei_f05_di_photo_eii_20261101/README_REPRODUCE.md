# WU R53 | Real original REI F05 H/D photoionization, recombination, charge-exchange, electron-impact source stress

**Owner:** cosmosapjw-quantum/WU088_HH. **Immutable parent** WU Draft PR #192 HEAD `0f45a3a13c8bbf277804eacc3a80e822a39a0b18`. **Original source:** REI original 26-event F05 frozen accepted tick160/131072; physical NONAUTHORITATIVE tick161 preview PR #352 HEAD `ea8d6bf94197392c69f939f03c1673ed3afe349c`. No native REI history or four-group photon owner has been altered.

**Main paper:** Daniel Wolf Savin (2002), [DOI 10.1086/324218](https://doi.org/10.1086/324218), original Table1 47 paired charge-exchange rates and Eq11–13 isotopic HI/DI approximate equality for photoionization, electron impact ionization and radiative recombination. All source files SHA256 pinned in `SOURCE_CONTRACT.json` and `EII_SOURCE_CONTRACT.json`.

Primary full source-inclusive 11 source files:
- Original WU R52 46,080-cell proper nH/clock CX-only physical output and exact original REI 46,080-cell H/He/T/electron physical state.
- Original material W_j NPZ, 85-row original native first 5-interval photon forcing, original REI F05 thermal energy, Savin original 47 source rates and fit receipt.
- Original REI H alphaA and alphaB source-code snapshots, native 17-node forcing PCHIP implementation, original H EII beta code.

## Run code (Python >=3.11, numpy, scipy; matplotlib optional for plots)

From the directory that contains `sources/`:

```bash
python3 r53_photo_chemistry.py --out results
python3 r53_photon_budget.py
python3 r53_eii_sensitivity.py
python3 -m unittest test_r53 test_r53_eii -q
python3 -O -m unittest test_r53 test_r53_eii -q
python3 audit_r53.py
python3 audit_r53_eii.py
python3 plot_r53.py
```

Original 46k source physics outputs:
- `results/R53_ORIGINAL_REI_F05_D_PHOTO_CX_46080.csv.gz` original-REI 46k×44 source-case A/B H-cloned DI photon/ RR + Savin CX time-dependent source data.
- `results/R53_OWNER_PHOTON_BUDGET_46080.csv.gz` original-REI 46k per-cell HI/DI photon reaction counts and local source demand comparison.
- `results/R53_REI_F05_EII_SOURCE_SENSITIVITY_46080.csv.gz` original-REI 46k EII-ON five-state DI transport and collisional-ionization threshold energy ledger.
- `results/R53_RESULTS.json`, `R53_PHOTON_BUDGET.json`, `R53_EII_RESULTS.json`: original-source scientific quantitative receipts.
- `results/R53_ADVERSARIAL_AUDIT.json`, `results/R53_EII_ADVERSARIAL_AUDIT.json`: same-author source-native original row and independent DOP853 audit.
- original source-real 24-row witnesses and two diagnostic figures retained in complete original archive.

**Physical limitations:** \(\eta_D=2.5e-5\) is an explicit assumed conditional D/H. The DI PI rate clones original source HI gamma using Savin near-isotope equality, not original DI spectral cross section. DI alphaA/alphaB clones native H RR, and DI EII clones native H beta via Savin Eq12, no validated isotope-specific quantum correction. The original source HII and log T are linearly/log-linearly interpolated across tick160 and **UNAPPROVED preview tick161**; source electron density is linearly interpolated. Original native group photons and gas enthalpy are NOT rerun or debited. Original H→D charge compensation holds exact source relative; total photon/electron/latent/thermal conservation requires new original source-owner coupled calculation.

**F53 scientific finding:** DI photon budget under *initially all-neutral D*, cloned HI field, gross photo demand ≈4.95% of original emitted photons and 7.57% original G1 absorption over that same original first F05 tick; initial all-ionized D demand far lower. Source H EII at high-T hot dense regions has threshold cooling potential >1% native F05 thermal change for 7,062/46,080 cells. These are **stress criteria**, not actual native photon allocation or a strong no-go.

Original owner central canonical REI 28/88; WU canonical 34/49; working REI 33/88; Δcanonical0, original tick160/131072 accepted, tick161 NOT_ACCEPTED. Draft/unmerged/production HOLD; no main merge or auto-next.
