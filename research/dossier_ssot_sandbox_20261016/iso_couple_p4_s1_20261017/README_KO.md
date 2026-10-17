# ISO-COUPLE P4/S1: independent positive photon birth-clock and D-edge spectral oracle

**Date:** 2026-10-17 KST. **Parent:** [PR #182](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/182) at exact head `3a2721e58fc8bd68cdbbc92ca4669bd57609695b`; original native PR #150 owner `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7` read-only. This branch is add-only, stacked on PR #182, NOT a production code change.

## Complete executable source and evidence

`REI_ISO_P4_S1_CLOCK_SPECTRAL_20261017.zip` contains Python source `src/p4_clock.py`, **40 locally executed PASS tests**, source/identity registry, original-native-fit frozen-gas numerical experiments, DOP853 independent ODE reference, CSV/JSON evidence, failure chronology, shell execution contract, and all member SHA-256 checksums.

**ZIP SHA-256:** `2e7551c5c042a1bb7df8434be2f37f2e5a50b9059332317c87d0b0a08c801d52`.
**Git blob SHA-1:** `039b9bb727d4349ebf0a34ddd4d7a82ff341fe3a` (not the ZIP SHA-256).
The same archive was independently fetched from Google Drive and verified to this exact SHA-256, 23,927 bytes. [Immutable create-only Drive backup](https://drive.google.com/file/d/1f2emzKXoPcebuKBPkmHawirys7LhlmrX/view).

## Constructive theory and bounded measured result

For a fixed-opacity step `tau = dt * sum_i kappa_i`, the proper positive newborn photon solution is `N_new = j dt Phi(tau)`, `Phi(tau)=-expm1(-tau)/tau`, with small-tau series. Species absorber events receive `[N_old(1-exp(-tau))+j dt (1-Phi)] * kappa_i/sum kappa`, preserving positive photon ownership, photon number, thermal plus binding energy accounting.

The previous P3 midpoint birth followed by *full* dt absorption gives `N_new=j dt exp(-tau)`; unlike Phi birth it has global first-order exposure error for smooth manufactured `j,kappa`.

- **Clock diagnostic** (manufactured smooth source/opacity, same 48 original spectral means and GL8, independent SciPy DOP853 reference): at 64 steps, relative surviving-photon error old `0.062483674` versus Phi `0.000029760513`; maximum individual species-event error old `0.01378562` versus Phi `0.00002055497`. Measured order old `0.96–0.99`, corrected `1.998–1.9999`.
- **Spectrum diagnostic** (source-native Verner photo fits, frozen gas): original 48 cell-mean versus threshold-aware log-Gauss q32 has max species-event relative gap `0.000371433`. Unsplit q8 retains `0.000350694` due manufactured D threshold **inside the first H source cell**. Explicit D-edge-split q4 compared to split q32 gives `5.63e-14` maximum species-event gap, within this fixed-spectrum numerical oracle.
- **Source identity audit:** HHeModel fixture binding `chi_H=13.598434599702` eV, manufactured P3 `chi_D=13.602134599702` eV (not 13.6037 eV); Verner H fit edge `13.60` eV. Binding energies, photo-fit thresholds, and source spectral segmentation have separate owners. Initial conflation caused **two failing regression tests** and was repaired without relaxing acceptance.
- **Angle diagnostic**: prescribed off-shell Bianchi-I **initial pulse only**. GL8/16 species-event residuals against GL32 are nonmonotone; angle convergence **NOT ADMITTED**. Multibirth/redshifting source age is expressly fail-closed.

Photon and energy ledgers in these independent controlled experiments remain below `3e-15` relative. This does not check native Rust P3 total EoR source-on results.

## Reproduce

Download/extract ZIP and run `./scripts_run.sh`. Python 3.13, NumPy 2.3, SciPy 1.17, pytest; offline. No Rust, Codex, NCP, or local computer used. Full ZIP includes `contracts/RELEASE_STATUS.json`, `SOURCE_PROVENANCE.json`, `DAG_PROGRESS.json`, `docs/P4_THEORY_AND_SCOPE_KO.md`, `evidence/p4_error_axes.csv`.

**Admission:** `P4/S1 = PASS_SCOPED_PYTHON_CLOCK_AND_FROZEN_SPECTRUM`. Parent `ISO-COUPLE-P4 = PARTIAL`, `SA-01/02`, `FLRW-CONV`, `BI-SIGNED`, `FULL_EOR = HOLD`. Native production not modified, no merged claim. Next gate: source-age-specific birth + opacity clock in opt-in original-source Rust, one-owner transaction with actual evolving H/He/D gas, matching BASS geometry, independent time/angle/spectral grids.

See upstream exact P3 [source](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/182), Verner et al. 1996 DOI:10.1086/177435, and Norman et al. 2015 DOI:10.1088/0067-0049/216/1/16.
