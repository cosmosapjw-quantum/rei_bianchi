# Evidence ledger — 2026-10-21 follow-up

| Evidence | Identity / location | Outcome |
|---|---|---|
| Latest PR head and task tree | PR199 `dd24a9f89e847ae7e97c017ffededd4aa53790d8`; task tree `bbe0079939ad642a4d38e443950f37926432dd70`; 2,412 files | Current baseline |
| v10 campaign receipt | `native_optimization_20261021/evidence/ncp_time_campaign_20261021/CAMPAIGN_RECEIPT.json`; SHA `d7ed2beb165aca6e44ad3c203ed75b7705a631748a15549535d4850b9ed352a5` | 3 new cases exit0, original validators PASS |
| v10 saved analysis | `.../ANALYSIS.json`; SHA `45d7b3f1fe346f90502e6062ed6b8b0a9f512d412124fef8589b7129b32f9f1f` | Both adjacent pairs fail 0.005 |
| Three raw endpoints | `native_optimization_20261021/evidence/native_time_refinement_20261021/raw/`; endpoint SHAs in `DIAGNOSTIC.json` | Hash-bound identity PASS |
| Astra bounded analysis contract | Existing reviewer `/root/review_lrs_ncp_20261021`, fresh read-only assignment | Analysis-only admissible; one mesh index repair authorized |
| Diagnostic | `native_optimization_20261021/evidence/native_time_refinement_20261021/DIAGNOSTIC.json`; SHA `9a24c3a14b2c3b9a50c69b0b4245efe30b4b415576297e49c7db6b310043d467` | Exit0, 12/12 adjacent differences decrease; finite-grid-only |
| Failed diagnostic attempt | `DIAGNOSTIC_ATTEMPT001.json`, `STDOUT.txt`, `STDERR.txt` in diagnostic evidence folder | Script indexing defect, exit1; preserved |
| Literature | `native_optimization_20261021/literature/FINITE_GRID_DIAGNOSTIC_SOURCES.md` | Context only; no model-specific theorem claimed |
| Fresh artifact search | PR199 current head/checks; first 100 branch names; Drive 138 direct files; Dropbox 36 direct files; root chat search unavailable through exposed connector | No later native return observed within listed scope; not exhaustive of all conversations/branches |
| Latest CI | PR199 runs 39523990828 / 39523997460 | Root `cargo fmt` failure; workspace tests skipped; scoped task did not modify root Rust/CI |

- Publication: result commit `96d88ae767b09f9d70e5f65f4180115f886beee0` parent `dd24a9f89e847ae7e97c017ffededd4aa53790d8`; 30 changed task paths, 0 outside task.
- Owner checkout remained branch `research/flrw-production-integration-20261015`, HEAD `fef2baf960f57f37b838004fbb8a7d37b3824852`, with its pre-existing 431 dirty entries.
