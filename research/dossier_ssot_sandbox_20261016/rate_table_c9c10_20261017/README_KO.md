# rei_bianchi RT-C9/C10 source-locked sandbox continuation

Status (2026-10-17): measured and tested C9 bounded method review; C10 standalone advisory policy implemented (not production integrated). Parent PR #177 / C8 report and source identity in `contracts/C9_RESULTS.json`.

Read `docs/C9_C10_REPORT_KO.md` → `docs/THEORY_C9_KO.md` → `contracts/C9_RESULTS.json` → `docs/C10_HANDOFF_KO.md`.

Only standalone C9 test file, policy code/test/manifest, and reports should be published to the public GitHub draft branch. The original Grackle-owner source and full C07 source archive belong to a separate full recovery ZIP. No original production code or full EoR outputs changed.

Replay full archive: `bash scripts/REPLAY_C9_C10.sh`. No Codex/local Ubuntu/NCP required. Source note: `rustc 1.94.1`, `cargo --offline --locked`, 5 vCPU and 5.9GB sandbox, tests 4/4 plus 9/9, independent fresh actor NOT_RUN.
