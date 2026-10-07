# Bounded continuous-boundary and short H/He transport research

This opt-in research directory is separate from the production crate's targets and defaults. It adds no production source changes. The published repository's existing Rust crate, comparison tools and exact manufactured config are reused through relative paths.

## Results and limits

- Continuous boundary V1: **PARTIAL**. The 64-subdivision initial-opacity target and narrow-support normalization/admission limitations remain visible. Source, rejected snapshots, test records and high-precision oracle results are retained.
- Continuous boundary V2: **PASS only for the selected bounded pure-radiation control matrix**. The 512-subdivision candidate passes; 64/128/256 failures remain. Exact-input normalization, near-empty rejection and owner checks do not establish a joined projected/coupled history. Log-tail evolution is unsupported and rejects.
- Short H/He backward Euler: **PARTIAL**. The 120 declared transactions pass physical/nonlinear and original conservation gates; spectral comparison passes. Temporal retightening fails in seven finest-pair fields, including work_E (ratio 238.517). Its first event-endpoint rejection, setup failures and unsuccessful first reference attempt remain.
- Short H/He midpoint: **selected finest-pair accuracy PASS; overall PARTIAL**. Both Gauss orders pass 16→32 and 32→64 for all 37 fields; the original 4→8 and added 8→16 work_E gates still fail (Gauss4 ratios 9.70189 and 2.66101). The independent reference pair is numerically admitted. Its exact peak concurrent-array count remains **UNVERIFIED**: observed samples are lower bounds, not a complete peak certificate. The earlier asserted array bound is withdrawn. All physical, nonlinear, number and energy gates retain their original thresholds.
- Mathematical/PDE notes describe reviewed methods, conditional designs and limitations. They are not implementation or production acceptance. The separate collisionless energy-transport benchmark is included after final independent review: 26 cases / 234 rows and nine tests. Its P0 FV energy defect, unlimited-DG negative states, limited-DG energy changes and initial projection errors remain explicit. The original oracle exceeded its site cap (4369 > 4096); a byte-identical bounded replay peaks at 2157 and does not erase the original failure. See transport-method-benchmark/REPORT.md.

The short experiments cover only the original 2e-4 interval in ln(a). They do not admit long histories, a projected multistep coupled method, physical export onset, production changes, or a general order-two claim for every diagnostic.

## Layout and source boundary

Each experiment retains its final source/tests, scientific contract, result tables, historical failure record and separate review. Small table files preserve their original numerical bytes. Large historical branch traces and full-tree run guards are represented by reviewed summaries rather than duplicated. HISTORICAL_TEST_LOGS.json preserves nonempty failure/RED/final logs with archived original hashes. RESOURCE_SUMMARY.json retains attempt exit codes and measured resource data; its totals describe the original experiment, not publication validation.

PROVENANCE.json distinguishes archived original byte hashes from the relocated publication bytes. Hashes quoted in older reviews/contracts refer to original archived artifacts unless explicitly marked as published. Source relocation changes only Cargo/provider and config references. Reference-generation wrappers ending in .py.txt are historical evidence: their input guards bind the original archive and are not runnable publication entry points. The existing repository reference implementation remains available under tools/.

The exact config is reused from [the previously published long-FLRW fixture](../../docs/research_program/igm_next_nodes_20261007/long-flrw/radau-p128-o2/config.cfg). The underlying mathematical boundary design is [already published](../../docs/research_program/igm_next_nodes_20261007/boundary-design/CONTINUOUS_BOUNDARY_DESIGN.md). Backward Euler and midpoint depend on ../../rust/rei_microphysics from this directory; their own Cargo files specify the correct crate-relative path.

## Lightweight replay

From the repository root, with Python 3.12 and Rust 1.94.1 available:

    python research/transport_20261007/replay_saved.py
    cargo test --manifest-path research/transport_20261007/short-hhe-coupling/Cargo.toml --offline --release -j1 --lib --tests -- --test-threads=1
    cargo test --manifest-path research/transport_20261007/short-hhe-midpoint/Cargo.toml --offline --release -j1 --lib --tests -- --test-threads=1

The saved-table replay reads the existing comparator, recomputes all 62 retained comparisons and step-budget maxima, and preserves every failed scientific verdict. It does not integrate histories or change the saved tables. The midpoint baseline-reference file reuses the backward-Euler reference_tighter.csv rather than duplicating it.

For standalone V1/V2 controls, compile src/tests.rs with rustc --edition=2021 -D warnings -O, place the executable outside this directory, and run from a disposable copy of the experiment directory. These harnesses write results/. The V1 executable deliberately exits 1 for its retained failed quadrature gate; V2 exits 0. The short-H/He Decimal kernel oracle can likewise be run in a disposable copy; it checks 121 exact-input components. The full 80-digit boundary oracle requires mpmath 1.3.0 and is not part of the lightweight publication replay.

Run any full history/reference experiment separately with fresh, explicit resource accounting. Do not interpret archived resource totals or altered path guards as a new historical replay certificate. Publication validation is summarized in PUBLICATION_VALIDATION.json.
