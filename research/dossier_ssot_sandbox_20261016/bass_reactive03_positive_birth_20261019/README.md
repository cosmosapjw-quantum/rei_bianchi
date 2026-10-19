# BASS-REACTIVE-03: positive optically thick photon births

**Scientific status: COMPLETE_VERIFIED_SCOPED. Long-span solution: NOT_ADMITTED.**

This add-only research package continues PR #201 at parent commit
5a2ae6313ad8ea7b5fdc9b0b2a58009778764b6e. It contains the complete inherited
97-file receiver crate, eight additive Rust files, the AP build manifest,
original donor data, theory, raw results, independent reviews and fresh-build
reproduction evidence.

The new positive two-node exponential fit preserves emitted mass and first
birth-age moment while reproducing the constant-source, constant-opacity survivor integral
exactly. Each node remains a distinct physical birth cohort with its own
geometry, Killing constants, energy, direction and labels.

- 209/209 current Rust tests; strict Clippy and scoped rustfmt.
- 16 original-source frozen cases: maximum survivor relative difference
  2.22e-16 from the analytic convolution.
- 12 completed evolving histories, 496 macrosteps; one expected CX work-budget
  failure with zero accepted rows.
- Independent primitive number/energy ledgers and final CSV/receipt audit.
- Fresh source and build target: 209/209 again; four frozen CSV byte matches;
  five native histories, 160 rows and 8,000 exact scientific-field matches.

The mean-age and energy-weighted directional quadrupole do not show a
contracting temporal sequence at fixed birth refinement. Full age, time,
spectral and angular convergence, universal second order and two-way Einstein
feedback remain unproved or unimplemented. Counts and conservation alone do
not establish these claims.

## Read and reproduce

- [Korean results and scope](docs/REPORT_KO.md)
- [Constructive theory and method comparison](docs/THEORY_REPORT.md)
- [Machine-readable results](evidence/SCIENCE_RESULTS.json)
- [Final endpoint table](evidence/NATIVE_FINALS.csv)
- [Verification](evidence/VERIFICATION.json)
- [Next DAG](contracts/DAG_PROGRESS.json)
- [Restore and exact commands](README_RESTORE.md)
- [Scientific figure](figures/BIRTH_INTEGRATION_VALIDATION.png)

Use ap/Cargo.toml for the opt-in implementation. The untouched crate/Cargo.toml
builds the inherited baseline.

    REI_RUST_PREFIX=/absolute/path/to/rust-1.94.1-prefix \
    REI_RUN_OUTPUT=/absolute/path/to/new-reproduction \
      bash RUN_STAGE.sh all ap_n32_r2

MANIFEST.sha256 binds the frozen scientific release. Runtime component binaries,
build targets, Python caches and orphan working streams are excluded. The
orphan streams that were inspected are preserved separately under sample_v0
with their failure inventory.

Full ZIP publication adds an outer ARCHIVE_MANIFEST.sha256 and a publication
directory containing the exact source commit, applicable Git patch and Git
bundle. The separate final publication receipt records the Draft PR, ZIP hash,
Drive/Dropbox acknowledgements, provider hash checks and actual raw readback.
That receipt follows the frozen scientific release and is not a self-reference
inside its ZIP.
