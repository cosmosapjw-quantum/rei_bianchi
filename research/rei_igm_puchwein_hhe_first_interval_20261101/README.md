# REI IGM | First source-owned Puchwein H/He photon/thermal FLRW pilot (2026-11-01)

**Status: SOURCE-CONDITIONAL DERIVED NUMERICALLY-CHECKED, **NOT** native REI Rust RUX05, NOT Bianchi-I, NOT a new central science DAG admission.** REI central **28/88 unchanged**, REI working **33/88**, WU canonical **34/49**. Draft isolated from REI D0 governance PR #318 at exact HEAD `4e9ee7114bff272c68a85d6907f4beeb21f93bb4`; no main merge/production/force push, no budget reset. This is the first **actual new coupled H/He ionization+thermal time series** in this source-reuse unit, not another policy-only report.

### Published and source-qualified inputs

- **Original physical UVB**: Puchwein, Haardt, Haehnelt & Madau (2019), *MNRAS* 485, 47–68, DOI `10.1093/mnras/stz222`, original ancillary `https://arxiv.org/src/1801.04931v1/anc/rates_fiducial.txt`. Original **59-row** REI owner source `research/rei_physical_fast_20261028/sources/PUCHWEIN_2019_FIDUCIAL.json` Git blob `218d81f68447da438228a7b102e1cec96a8e8a1a`, in its original branch `research/rei-physical-fast-20261028`. This PR publishes only the exact original z=5.18–15.1 **21-knot subset**, [source CSV](PUCHWEIN2019_FIDUCIAL_21_EXACT_KNOTS.csv), Git blob **`148979f7fb150b3bb5fe9989e667cebcf1c9643d`**, SHA256 `faf3f87d94eefba71a781e1ae62ebf202760a56fb6c42afaceeba6ca8ffe235e`. Six fields: HI/HeI/HeII photoionization rates s^-1 and photoheating **eV per absorber per s**, plus original Compton_raw column archived but *not used* due normalization issue.
- **Microphysics**: Grackle 3.4.1 Case-A chemical/cooling source exact commit `af7939494ce65007887ada7b98d1813df6843346` as REI actual Rust `rust/rei_microphysics/src/igm_rates.rs` blob `dc3cc028a41ac852d94835372ce13545389d1c3a`, and the *point* energy/source Rust `igm_thermal.rs` blob `0648618d9822e169e9672ac3c556f86595c3b0b6`. This experiment **translates** the relevant source formulas to Python/SciPy BDF; it does not run the native Rust REI stage.
- **Model**: homogeneous flat FLRW H0=67.4, Omega_m=.315, Omega_r=9.27e-5, Omega_b=.0493, Y_He=.245 (chosen), fixed externally specified original UVB source, Case-A recombination escape; nH proper∝(1+z)^3, full non-equilibrium HI/HII/HeI/HeII/HeIII, proper n_e, gas kinetic energy, Compton and adiabatic terms, chemical binding and escaping photon-energy ledger. No ionization QV relabel, no geometry/shear or radiation field self-consistency.
- **Initial conditions are declared modeling hypotheses, NOT author data**: reset z10 with Tgas30K, xHII2e-4, xHeII1e-5, xHeIII1e-10. Prehistory starts z15.1 with synthetic same fractions and adiabatically inferred Tgas4.678654668874172K from assumed thermal decoupling at zdec150. Both follow exact original UVB source knot support (no extrapolation).

### Results with a falsifiable physical effect

| Model | xHII(z5.81) | Tgas(z5.81) | segment tau(z5.81,z10) |
|:--|--:|--:|--:|
| Puchwein UVB reset z10 | 0.999959916771 | 11606.9197 K | 0.017389415757 |
| Same IC, UVB off | 0.000198242999725 | 11.4993835 K | 0.000007680127720 |
| Same original Puchwein rate table, sourced prehistory starts z15.1 | 0.999959568922 | 11469.2357 K | 0.021246257161 |

**New physical fact *about the conditional model***: despite nearly identical late xHII, segment optical depth is **22.1792466% larger** if the high-z source prehistory is evolved instead of imposing a nearly neutral reset at z10. z10 from source-supported prehistory has xHII=0.1856732600 and Tgas=5851.21848K. Thus a late xHII endpoint alone cannot specify the Thomson depth; chronology and actual initial history matter. This is not observed cosmological tau, full CMB tau, or a proof Puchwein's original history is reproduced.

A UVB amplitude model variation 0.5,1,2 with the same z10 reset yields segment tau 0.0124690193,0.0173894158,0.0228358741. The scale factors are selected sensitivity hypotheses, **not source uncertainty or measured posterior**. Representative [11 physically computed epoch rows](EOR_HHE_11_SCIENCE_EPOCHS.csv) are Git blob byte-exact with the actual numerical results: `aaf60834dcc095025ad6261515fa5535d5b30894`.

### Exact scope of code, verification, and storage

This PR is a thin, source-qualified public research checkpoint; it publishes **source knots, representative scientific data, reproducible mathematical/physical contract, and 20-stage checksum ledger**. The **complete executable Python source and 5,027 derived physics rows**, 8 PNG+8 SVG scientific plots, scripts, tests, original failed-test provenance and 20 R/C stage ZIPs +4 phase ZIPs are inside an accompanying ChatGPT user-downloadable source master, **not automatically present in this GitHub subtree**. Nothing in this PR implies upload of those binaries to Library/Drive/Dropbox.

- Source-inclusive executable-model ZIP `REI_IGM_PUCHWEIN_HHE_FIRST_INTERVAL_SOURCE_MASTER_20261101.zip` SHA256 **`f335e3abcae8f83efb4e3c11db1f8d8942d750f03960aa69c27544b5685202f6`**; 1,212,615 bytes, 66 archive members, CRC PASS.
- Stage/phase aggregate `REI_IGM_PUCHWEIN_HHE_FIRST_INTERVAL_ALL_STAGES_20261101.zip` SHA256 **`fc1d73f857865ec3d4e6babe202552c833b7f567c395d7946e2e1b3e25c6c40d`**; 1,431,829 bytes, 46 archive members, CRC PASS. 20/20 stage ZIP CRC PASS, 4/4 phase ZIP CRC PASS. **Only local backups verified; external binary backup NOT_DONE.**
- Generated physics model rows: trajectory **802**, H/He event **2406**, initial-T **603**, UVB amplitude **603**, prehistory **601**, prehistory-vs-reset **12**, total **5027** new **model outputs**, not measurements. Source UVB input rows 21 counted separately.
- Actual tests source-code run `OPENBLAS_NUM_THREADS=1 python -m unittest -q test_rei_first_interval` 24/24 PASS normal, same with `python -O` 24/24 PASS, `py_compile` PASS. BDF vs Radau one-author method comparison max ≈5.36e-8 relative in final selected chemistry+tau; energy identity max ≈1.31e−46 erg cm−3 s−1; charge-source residual ≈3e−36 cm−3 s−1. Wolfram symbolic check 3 identities (0, `-xSref/nref`,0). Distinct-author R6/C9 **NOT_RUN**. Initial 2/21 tests failed (wrong assumed source z support and degenerate He=0 BDF finite-difference Jacobian) and were repaired without concealing narrower He=0 RHS claim.

**Model equation:** `d x_HII/dt=(n_HI Γ_HI + n_e n_HI k_CI - n_e n_HII k_RR)/n_H` and analogous two-stage He system, thermal `dw/dt = Qth/n_H - 2 H w`. Define `Qphoto = sum(n_abs*(chi Gamma + h_eV * eV_erg))`, `Qbound = Qphoto_binding+Qcollision_ion−Qrecomb_binding`, `Qescape=Qrecomb_binding+Qkin_cooling`, `Qth=Qphoto_heat−Qcollision_ion−Qkin_cooling+Qcmb`. Then exact point identity `Qth+Qbound+Qescape−Qcmb−Qphoto=0`. Segment `tau=integral_{5.81}^{10} c*sigmaT*n_e/[H(z)(1+z)] dz`; the UVB is an external prescribed photon reservoir, not transported. Angular Bianchi transfer, EoR spatial patchiness, measured tau posterior, and owner-native REI solver are outside claimed results.

### DAG progress and next executable science

**Original** REI central **28/88**, working **33/88**, WU **34/49**, delta **0**. The RUX-P0 source/consumer seam is now better supported by a first physical **conditional model numerical witness**, but RUX02/03/04/05 native accepted completion is **NOT claimed**. The latest REI governance PR #318 remains Draft; this scientific sibling PR adds under its head without modifying its science or source history.

Next user-authorized work: bind the actual original Rust `IgmPointRhs` to the published UVB knots with **same physical nH/nHe/clock/IC** and original source/energy ownership, then execute one native RUX05 first interval if execution permit and budget. Only after matching source with BASS Bianchi geometry and photon transport can RUX07/RUX09 and an actual directional observable be certified. Do not start a new meta-audit or another atomic source atlas as the default.

**NO_MAIN_MERGE, AUTO_NEXT_NODE=false, REI_L4=HOLD, PRODUCTION=NOT_ISSUED.**