# PR282 daughter, original Li II 2E1 differential emitted spectral data

Read `THEORY_KO.md` then `REPORT_KO.md`, `results/RESULT.json` and `HANDOFF_NEXT_THREAD_KO.md`.

`bash VERIFY.sh` checks original nested source SHA and source-derived 193/8492/4053 output structure, executes targeted unit/science tests and checks the manifest. The file `source/PR282_FULL.zip` is an immutable binary original source (10,533,802 bytes), includes earlier PR278/PR280 ZIPs; original raw CSV and graphics remain in the source-inclusive archive, not transformed through spreadsheet parsing.

Important: the conditional `1-exp(-c*kappa/H)` is a **frozen local Hubble-length trial absorption**, not a cosmological time-integrated opacity, actual H/He ionization or heat. A true `IgmPhotoInput::heat_erg_per_absorber_s` source is UNBOUND.

Progress: working `33/88`, central `28/88`, F4-fast `4/7`, canonical delta `0`, auxiliary `1/1_SCOPED`. All R1–R10/C1–C10 stage entries published retrospectively, `R6` & `C9` different-author NOT_RUN.
