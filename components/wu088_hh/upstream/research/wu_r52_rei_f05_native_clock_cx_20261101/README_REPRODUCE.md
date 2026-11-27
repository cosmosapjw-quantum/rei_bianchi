# WU R52 | Reproducible original REI F05 physical-clock D/H charge-exchange transient

Parent WU Draft PR #190 HEAD a42fa9113573a588ef2033ef6bbad2d9b3f87f94. Source REI F05 PR #352 HEAD ea8d6bf94197392c69f939f03c1673ed3afe349c and geometry source REC→REI PR #191 original NPZ plus forcing. Original accepted REI tick160/131072; tick161 native H/He preview is NEVER accepted by this consumer.

## Requirements
Python >=3.11, numpy for physical vectorized computation, scipy for *separate same-author* independent DOP853 audit, optional matplotlib for scientific plots. No natural-units convention: source clock is proper seconds, W*Mpc_cm^3/(1+z)^3 is cm^3, Savin k [cm^3 s^-1], n_H in cm^-3, photon/thermal energies in erg.

## Source data
The full source-inclusive archive preserves exactly these six files inside `source_inputs/`. Every input's exact original SHA256 is enforced by `r52_rei_native_clock_kinetics.py` and `SOURCE_CONTRACT.json`:
- `initial_material_state_z6.npz` SHA256 7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d
- `canonical_time_resolved_forcing_nodes.csv` SHA256 9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268
- `ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz` SHA256 713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d
- `REI_F05_ORIGINAL26_NATIVE_DISCRETE_ENERGY_46080.csv.gz` SHA256 024e1d1bbef95d3e254b8c54b3d1134de54eebce7b82d082401c522f813637c5
- `SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv` SHA256 ba98ec463903f3589c6c68cd7d9e3b3bc637188bb5d25616addb2fb71ab689e8
- `SAVIN2002_ORIGINAL_TABLE2_FITS.json` SHA256 b178d89b858ae58ed1fe873fe831e02b737532a2f1fc20a82c920e76d2c3b1bc

The **Savin original rate file** SHA-256 in the frozen program and contract is ba98ec463903f3589c6c68cd7d9e3b3bc637188bb5d25616addb2fb71ab689e8 (do not trust a transcribed shortened hash). Original Savin (2002): https://doi.org/10.1086/324218. Source rate table represents rounded original Table1, not unprovided ab-initio exact data.

## Run all physics and tests from the archive root

```bash
python3 r52_rei_native_clock_kinetics.py --out results
python3 -m unittest test_r52 -q
python3 -O -m unittest test_r52 -q
python3 audit_r52.py
python3 r52_rei_native_clock_kinetics.py --out replay
cmp results/R52_ORIGINAL_REI_F05_REAL_PROPER_D_CX_46080.csv.gz replay/R52_ORIGINAL_REI_F05_REAL_PROPER_D_CX_46080.csv.gz
cmp results/R52_RESULT.json replay/R52_RESULT.json
```

`results/R52_ORIGINAL_REI_F05_REAL_PROPER_D_CX_46080.csv.gz` contains all 46,080 original physical-source nodes and signed chemistry state/energy rows. `results/R52_RESULT.json` contains population/clock/source metadata and model summaries. `results/R52_ADVERSARIAL_AUDIT.json` is an independent numerical algorithm check. `results/R52_SUMMARY.json` and 23 real source witnesses are thin public Git evidence. The Git subset includes code, tests and summary but **does not** carry original REI NPZ/large data; restore only exact original source bytes from full archive. No fake GitHub CI claim: external CI NOT_RUN unless actual original source is restored and tested.

## Admission and assumptions

F05 original source first interval has 17 z_mid=5.95 nodes, so original source cell volumes are fixed within the first tick. Source n_H is computed as H nuclei count / physical volume, not by interpreting counts as density. The source H/He thermochemistry at both tick endpoints is real original native data (tick161 nonauthoritative preview). Between endpoints original continuous trajectory not supplied: this model **declares** x_HII linearly interpolated and log(T) linearly interpolated; alternative frozen-endpoint controls test local dependence but not all possible original trajectories. D initial ionization is unknown, so run y0=0,1,and stationary-at-t160 as three scenarios. Model only includes ground-state H/D charge exchange, with H+ compensation and exact charge bookkeeping relative to original H+ baseline, not D photoionization/recombination or full original Einstein–Boltzmann source owner. Results are conditional, not observed reionization or accepted production. Official REI tick160/131072, WU 34/49 and central REI 28/88 unchanged.
