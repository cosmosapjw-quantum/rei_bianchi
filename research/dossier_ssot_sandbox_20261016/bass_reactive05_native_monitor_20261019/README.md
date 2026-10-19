# BR05 native birth monitor and one crossed control

Read `docs/REPORT_KO.md`, `evidence/SCIENCE_RESULTS.json`, `evidence/VERIFICATION.json`, and `contracts/DAG_PROGRESS.json` first.

This is an add-only, opt-in follow-up to PR203 at `a8e550846745fc89e79e84ad32567e3fb556c175`. All 125 parent inputs are byte-identical; eight new Rust/build inputs implement an observational monitor. The original source, physical owners, CX half-flows and four-corner controller remain unchanged. One new Nt16r8 source-native history closes the r4–8 time/birth rectangle. Longspan convergence remains unadmitted.

The full ZIP contains the complete 133-input build, all six raw monitor CSVs, native histories, independent analyses, logs, failures, audits, figures and restore contracts. The GitHub source release omits large generated data listed with exact bytes/SHA in `contracts/GITHUB_DATA_OMISSIONS.json`. Restore those from the full ZIP before running full-data analysis. Complete source verification and source compilation remain possible in the source checkout.

Run `bash RUN_STAGE.sh verify`, `test`, `light`, or `analyze`. The separate `native` mode performs the chosen longspan dynamics once into a new output directory. All reproduction output defaults to a new temporary directory. Rust/Cargo1.94.1 with Clippy/rustfmt and Python3.12 are the verified runtime; the compiler archive/build cache is not included in this scientific package.

Scientific source commit/tree, full ZIP identity, cloud upload/provider/raw-restore statuses and latest PR head are recorded in the separate final publication receipt. That receipt is added after archive creation so it does not introduce circular hashes.

The current publication captions are `docs/FIGURE_CAPTIONS.md`. `evidence/FINAL_REPORT_SCOPE_REVIEW.json` records one wording correction (121 is the donor geometry grid) while retaining the original figure-audit caption bytes. No plot or numerical value changed.
