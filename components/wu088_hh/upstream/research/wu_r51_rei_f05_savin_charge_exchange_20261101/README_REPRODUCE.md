# WU R51 | Reproduce Savin D/H charge exchange on original REI F05 real source

Origin: WU Draft PR #189 immutable parent `b711a6a7f6bfae257f0bcbcea44cad52b8086fc0`.
REI read-only original Draft PR #352 immutable source HEAD `ea8d6bf94197392c69f939f03c1673ed3afe349c`.
Scientific unit: original REI F05 46,080 tick160 accepted H/He/T centers and 46,080 tick161 NONAUTHORITATIVE preview centers versus published original Savin(2002) atomic D(1s)+H+⇌D++H(1s) rate Table1.

Requires Python 3.11+ standard library for science and verification, and optional matplotlib for plots. Run from directory containing `sources/`:

```bash
python3 r51_savin_f05.py --out results
python3 -m unittest test_r51 -q
python3 -O -m unittest test_r51 -q
python3 audit_r51.py
python3 plot_r51.py
```

Exact source file identities **hardcoded** in `r51_savin_f05.py`:
- `SAVIN2002_AR5IV_ORIGINAL_HTML.html` SHA256 `8d22b670d2225de7a1e81ac1440e06188318cb7703b19e3b9ad214d12cb85d29`
- `SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv` SHA256 `ba98ec463903f3589c6c68cd7d9e3b3bc637188bb5d25616addb2fb71ab689e8`
- `SAVIN2002_ORIGINAL_TABLE2_FITS.json` SHA256 `b178d89b858ae58ed1fe873fe831e02b737532a2f1fc20a82c920e76d2c3b1bc`
- `ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz` SHA256 `713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d`
- `REI_F05_ORIGINAL26_NATIVE_DISCRETE_ENERGY_46080.csv.gz` SHA256 `024e1d1bbef95d3e254b8c54b3d1134de54eebce7b82d082401c522f813637c5`

The *full* zip in Google Drive/Dropbox has all source bytes, all 46,080 real-source data rows, code, audit, tests and plots. The *thin* Git research subtree is source-free (except original published Savin 47-row table/fit and source identity), and requires restoring two actual REI source gzip files **from same immutable SHA sources**, not rebuilding synthetic ones. No independent GitHub CI source data regeneration without a verified source restore.

Outputs:
- `results/R51_REI_F05_SAVIN_H_D_CX_46080.csv.gz` full physical 46k×42 conditional rate/partition/energy/charge state rows
- `results/R51_RESULTS.json`, `results/R51_SOURCE_PHYSICS_SUMMARY.json` quantitative original-source witnesses/status
- `results/R51_ADVERSARIAL_AUDIT.json` same-author independent check (not distinct scientist)
- `plots/R51_NEUTRAL_D_H_ORIGINAL_VS_FIT.png` and `.svg` (optional).

Warning: original source `source_H_nuclei_N` is a particle count, not proper cm^-3. No real D ionization IVP, free-electron generation by pure charge exchange, 26-event energy owner insertion, REI acceptance, or observational cosmological signal is claimed.

WU canonical 34/49, REI central 28/88, working 33/88, fast 4/7, +0. Original source tick160 accepted, first tick161 NOT ACCEPTED. Parent branches read-only, no main merge, no production.
