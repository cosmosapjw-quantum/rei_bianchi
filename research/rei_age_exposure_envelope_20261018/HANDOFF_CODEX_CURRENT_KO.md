# Codex 현재 인계 — age exposure native BE 진단

## 기준과 보존

- Repository: `cosmosapjw-quantum/rei_bianchi`
- PR199: open draft, branch `research/rei-age-exposure-envelope-20261018`
- 현재 원격 HEAD at intake: `dd24a9f89e847ae7e97c017ffededd4aa53790d8`; task tree `bbe0079939ad642a4d38e443950f37926432dd70` (2,412 files)
- v10 배송 HEAD: `652a7e03b844a145d6c6cbb401ab81f4a8429aff`; actual v10 parent/source `4f13648985e417028c530892ea02be4f56018a31`
- Owner checkout branch/dirty state was preserved; task snapshot and edits are isolated under `/tmp/rei_age_followup_20261021/research/rei_age_exposure_envelope_20261018` until expected-head publication.
- No new NCP case remains. Do not invoke `campaign.py` for time8/16/32 or rerun completed age32/64, spectral128, benchmark, fixed-model.

## Completed v10 execution

NCP `time8`, `time16`, `time32`: each one new attempt, exit0, original output validation PASS. Resource receipt records host `s1a0e5abed09`, affinity64, CPU quota unlimited, available memory131,366,031,360 bytes; 3 jobs×20 workers + 3 main slots =63, per-case address space24GiB, reserve16GiB, BLAS/OMP1. Build12.7937s. V10 BE binary SHA `2d5d95371df4c4cf882a4563edc4becdf965c76fdbbf9b9dfaa97fe083fd57fd`, prepared SHA `ca09947a4a460d3643430547688da8f7c8e0d8bd2e7f4b79e66d3fd0bc17cb1c`; original positive B1 SHA `89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4` is a distinct binary.

## New bounded analysis

`FINITE_GRID_ONLY_THREE_LEVEL_DIFFERENCE_DIAGNOSTIC` reads only saved NCP outputs. Its identity/commands/raw/stdout/stderr/exit codes are in `native_optimization_20261021/evidence/native_time_refinement_20261021/`. Attempt001's wrong mesh parity check and exit1 are preserved. An independent read-only Astra reviewer authorized the single mechanical correction; attempt002 used the correct `fine[1::2] == coarse` relation and exited0 in 0.0343s. No solver was run.

The existing 0.005 result remains FAIL for both adjacent pairs. Raw-difference finite-grid slopes do not change that criterion. Age32 is positive DOP853 and stays a cross-operator reference. `native_age_time_convergence=HOLD`; `nonlinear_Grackle_response_bound=NOT_ESTABLISHED`; `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.

## Latest intake and checks

PR199 latest head was checked directly. The selected first 100 GitHub branch entries, Drive folder (138 direct entries), Dropbox folder (36 direct entries), latest PR commits/checks, and v10 campaign return showed no later native execution. Current exposed connectors do not provide root conversation search, so other-conversation results are unverified; do not describe the intake as exhaustive. Latest CI runs `39523990828` and `39523997460` fail the root `cargo fmt --manifest-path rust/rei_microphysics/Cargo.toml --all -- --check`; workspace tests are skipped. Root Rust/CI was not changed.

SciSpace, Exa, and Wolfram were used for literature search and independent arithmetic cross-check. The literature sources and limits are in `native_optimization_20261021/literature/FINITE_GRID_DIAGNOSTIC_SOURCES.md`.

## Publication controls

Continue with expected-head fast-forward only after reviewing the exact current remote parent. Preserve task-owned evidence and existing dirty owner checkout. Keep PR199 draft, do not merge, do not force-push. Archive the result/source package to Drive folder `1phclg92jkhC5KgvnXhks8GbOFlya4qGe` and Dropbox `/bianchi/rei_bianchi/research/REI_POSITIVE_AGE_REFERENCE_BACKUPS/`; verify full object byte counts/SHA before recording ACK. Do not overwrite existing provider files.

## Next research action

No NCP prompt is needed for this lane. A new solver case, model edit, tolerance change, or production claim requires a new frozen Astra contract and separate review. Until then close this diagnostic with the current claim ceilings.
