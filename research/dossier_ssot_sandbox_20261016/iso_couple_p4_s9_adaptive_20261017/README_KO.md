# rei_bianchi P4/S9: observable local-defect control / inner-CX precision

2026-10-17. Parent PR189 exact HEAD `6d9057aa03e62d309f397354f37d6faa1d5c52ee`. Original P8 archive SHA256 `63618bb44cea7832273cefe3cd07053a3272d0b664a7efc797a100897f680a45` restored and182payload hashes checked. Original production PR150 `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7`, previous branches and physical owner12files unchanged. This directory only is add-only. No Codex/local user host/NCP, no merge.

## New code

`adaptive_step.rs` wraps unchanged JointCxSplit with coarse one-step vs fine two-half-step comparisons. Accepted state is the fine history, never Richardson extrapolation. Rejected/coarse/midpoint predictors have no physical source/photon/event ownership. Rare HI/HeI/HeII/DI step photo events are compared separately in comoving units, not hidden inside a total photon norm. Different birth-age grids are compared through conserved source-label photon projections, not by zipping newborn arrays. Original fine cohort records are retained; nonzero pruning=0.

The dimensional test is max_i |Qc_i-Qf_i|/(atol_i+rtol max(|Qc_i|,|Qf_i|))<=1. No /3 calibration is assumed. Gas densities/thermal/reservoirs, photon count/energy/P2, source inventory,4photo channels and spectral/angular-label stocks are monitored. The photon-age distribution norm and all continuum error axes are NOT certified.

## Executed results

- Rust1.94.1 release offline locked all-target140/140tests PASS; Python6/6analysis tests PASS; strictClippy/newsource rustfmt PASS. Parent native66files unchanged plus exact additive lib export; original physical owners12unchanged.
-5 complete adaptive full-chemistry histories,101accepted intervals/16rejected trials/117trials/202accepted native halfsteps. All reach8e10s. Maximum accepted projected defect0.9104006036.
- Same inner1e-12: outerrtol1e-2/1e-3/3e-4/1e-4 accepts7/16/25/37, rejects1/3/4/5. Final DI photo events9.770703560969e-10/9.769621821673e-10/9.769596047209e-10/9.769594372927e-10com^-3. Finest is a finite numerical comparator, NOT truth/global error bound.
-32 gas-only precision rows and4new independent DOP853 time-integrator references using same native RHS. Cold N512 inner1e-12->1e-14 reduces DII absolute error2.679470867406e-9->1.355733303399e-10m^-3,19.764x; rate calls4.309x. Reference refinement difference2.54019e-13m^-3. InnerCX error significantly contributes to prior floor; residual not fully classified.
- Hot coarse gas has signed-error cancellation: tighter inner tolerance need not monotonically improve final finite-grid accuracy.
-4fixed accepted-grid native replays (same16intervals/32halfsteps) isolate CX tolerance from adaptive-grid changes. DII final11.485802364356509,11.485803546829862,11.485803608589233,11.485803611481574m^-3 for1e-8/1e-10/1e-12/1e-14. Sameinner1e-12 endpoints exactly reproduce adaptive history. HeII photo total unchanged in these4cases.
-Photon ledger max5.064195208e-15;accepted halfstep energy ledger5.786274187e-16. These are arithmetic ledgers, not accuracy estimates.
-Initial inner1e-14 hit original work allowance2000attempts after3rows. Preserved partial/log. Research work allowance20000attempts/2500000ratecalls, unchanged tolerances, completed32rows. Inner work/source/ledger errors are fatal to the outer controller, not endlessly retried as accuracy failures.
-Clean restore:140Rust/6Python,lints/build PASS; fresh1adaptive,32gas,4same-grid,4DOP853controls reproduce scientific fields exactly; timing excluded. All5adaptive histories were NOT rerun. Separate check/replay times22.36s/11.00s, not one invented total run.

## Scope

PASS_SCOPED_OBSERVABLE_LOCAL_DEFECT_AND_INNER_CX_SEPARATION. FullP4 PARTIAL;SA01/02,FLRW-CONV,BI-SIGNED,FULL_EOR HOLD. Local projected defect is not a global bound or automatic inner-CX certification. No unconditional positivity/stiff stability, adjoint theorem, continuum spectral/angular/age convergence or on-shell BASS admission. Original regression abundances,D defect.0037eV,CMB bath20K,prescribed H=1.2e-16s^-1/shear.06H and same source resolution remain. Timings are descriptive, no speedup claim.

## GitHub source reconstruction

Complete72native source files are preserved as the fixed P8base67files plus exact delta6files (lib replacement +5newfiles). The script validates compressed SHA,decoded JSON SHA,complete source-tree hash and safe paths, and refuses overwrite. Local reconstruction actually verified72/72file SHA256. This is source transfer compression, not photon compression.

Repository checkout root:

```bash
ROOT=research/dossier_ssot_sandbox_20261016
python "$ROOT/iso_couple_p4_s8_recovery_20261017/RESTORE_SOURCE.py" --base "$ROOT/iso_couple_p4_s6_20261017/rei_iso_couple_p4_s6" --out /tmp/rei_p8_base
python "$ROOT/iso_couple_p4_s9_adaptive_20261017/RESTORE_SOURCE.py" --base /tmp/rei_p8_base --out /tmp/rei_p9
# Configure supplied Rust1.94.1 PATH/LD_LIBRARY_PATH, then:
cd /tmp/rei_p9
cargo test --release --offline --locked --all-targets
cargo clippy --offline --locked --all-targets -- -D warnings
cargo run --release --offline --locked --example p9_adaptive_campaign -- 1e-3 1e-12 8e10 2e10 /tmp/p9_trial_trace.csv
```

## Full evidence backup

FULL ZIP275727bytes,137entries,136payload hashes. SHA256 `024fcc02b15d53c7816c9d888f98b5ec637fdcb875456028cf9f342c5f696446`. All72Rust files,fulltheory,CSV/JSON,failures,logs,repro scripts are in this archive. The binary FULL ZIP is not duplicated in Git; Git has losslessly reconstructible source plus compact evidence.

Drive: https://drive.google.com/file/d/1cRNQqA9hcylG_MXp7uEc0gtyIboMWGEY/view
Dropbox: `/bianchi/rei_bianchi/research/REI_BASS_HIERARCHY_BACKUPS/REI_ISO_COUPLE_P4_S9_20261017_FULL.zip`,id `id:BSpOijBcT10AAAAAAD-oBA`. Upload/readback levels are sealed separately after verification.

Next bounded P4/S10: explicit inner/outer error budget allocation or actual source-matched BASS intake, retaining separate unclosed EoR/continuum gates.
