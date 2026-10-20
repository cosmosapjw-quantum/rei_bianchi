# BR06: frozen native gas and variable BASS geometry birth reference

**Revision: `BR06_RECOVERY_R1_FINAL`. Scope: one recorded gas operator.**

This add-only research unit continues the verified BR05 checkpoint at parent
commit `00e89bce3060516083d63edb857f1294ee560ea0` (Draft PR #206). Read
[`docs/REPORT_KO.md`](docs/REPORT_KO.md),
[`contracts/BR06_CONTRACT.json`](contracts/BR06_CONTRACT.json),
[`evidence/VERIFICATION.json`](evidence/VERIFICATION.json), and
[`contracts/DAG_PROGRESS.json`](contracts/DAG_PROGRESS.json) first.

The opt-in `br06_reference` executable preserves each quadrature photon's birth
time, birth geometry, Killing constants, direction, energy, age, photon weight,
and original spectral/angular labels. It uses the original MD14/BB50k source and
H/He/D atomic owners. Gas reference-comoving inventories are frozen at the
recorded BR05 corrector state; proper densities change with BASS volume. There
are **zero new nonlinear gas histories and zero new nonlinear macrosteps** in
BR06. The previous production and research branches, CX half-flow, and S10
four-corner controller are unchanged.

The parent positive exponential-fitted birth rule remains unchanged. New
positive Gauss reference controls resolve the recorded birth distribution and
its moments. A finite Gauss rule is not claimed to reproduce the exact constant
opacity source integral at every optical depth. The VigilODE integration uses
the pinned directed scalar damped-moment kernel with a positive dyadic adapter;
its verified scalar enclosures do not enclose the entire variable-opacity
operator. See [`docs/VIGILODE_REUSE_KO.md`](docs/VIGILODE_REUSE_KO.md).

## What is in Git and in the full archive

Git contains the exact source additions, tests, contracts, reports, verification
receipts, and compact numerical evidence. The full ZIP also contains all larger
CSV outputs and the 99-package locked Cargo registry archive. Their exact sizes
and hashes are listed in `contracts/GITHUB_DATA_OMISSIONS.json`.

The full ZIP contains the complete 133-file parent source/input corpus, four
exact first-step CSV subsets, ten new Rust source/build files, bootstrap config,
477 pinned VigilODE payload files, the locked dependency archive, and all nine
new execution results. It can be restored without downloading the BR05 ZIP.
The complete *historical* BR05 archive is not duplicated here. Its identity is
preserved in the recovery contract. The scientific source commit and the later
provider readback receipt are kept separate to avoid circular archive hashes.

## Reproduce in a fresh sandbox

Requirements: Linux x86_64, Rust/Cargo 1.94.1 with Clippy and rustfmt, and Python
with NumPy and SciPy. The actual reference environment was Python 3.12.14,
NumPy 2.3.5, SciPy 1.17.0. Rust registry dependencies are included and locked;
the recipe performs no network operation or software installation.

Extract the full ZIP, verify `MANIFEST_SHA256.json`, then choose a **new absolute
workspace outside the extracted unit**:

```bash
bash RUN_STAGE.sh verify /tmp/rei_br06_new_verify
```

The recipe checks 143 parent/new source hashes, bootstrap config, four canonical
CSV hashes, all 477 pinned VigilODE files, and all 99 locked registry packages.
It creates a fresh Cargo home and target, runs the parent 233 tests and new 16
tests, strict Clippy for both, an eight-template reference calculation, and the
independent full 384-label Python reference at two orders. Repeated restoration
tests are repeat evidence, not additional unique test cases. Each process gets
raw logs, a typed exit status, and a separate work budget.

To rerun the complete fixed nine-case numerical matrix in another new workspace:

```bash
bash RUN_STAGE.sh matrix /tmp/rei_br06_new_matrix
```

The recorded recovery matrix used three workers and 600 seconds per case. All
nine cases completed, with 169,616 cohort evaluations. Wall times depend on the
sandbox; a timeout is classified as `WORK_BUDGET_TIMEOUT`, not nonexistence of
a physical solution. The Rust binary reads fixture inputs relative to its build
manifest, so rebuild it in the restored layout.

The independent analysis scripts in `scripts/` expose `--help`. Their receipts
record exact command lines. The `reference_parent` directory created by the
restore recipe supplies unchanged source/donor files and exact STEP1 rows under
the historical `MONITOR_*` filenames. It is deliberately identified as a
first-step subset. Raw absolute paths in old execution receipts document where
those executions actually occurred; portable recipes use the restored layout.

For the separate inexpensive scalar harness, follow
[`PORTABLE_MOMENT_HARNESS_R1.md`](evidence/c9_r1/PORTABLE_MOMENT_HARNESS_R1.md).
Copy `evidence/vigilode_adapter_r1/` to a new root's `adapter_r1/`, and copy
`vendor/vigilode/` to the same root's `vigilode_exact_selected/`. Extract the
registry tar under that root and rename its `registry/` directory to
`vendor_r1/`. The complete 99-package registry contains all nine registry
packages in the narrow harness's final Cargo.lock; their checksums were compared in
`evidence/c9_r1/FULL_REGISTRY_CONTAINS_NARROW_LOCK.json`. Preserve the source's
relative paths and run Cargo from `adapter_r1/harness/`. This relocation recipe
does not claim an additional test execution.

## Recovery and claim boundary

An automatic workspace cleanup removed the first BR06 work before any Git blob
ACK, PR, or cloud archive existed. The parent archive, parent inputs, first-step
CSV bytes, two core Rust files, and pinned upstream payloads were recovered by
identity. Eight source/build wrappers were reconstructed as R1. All current
claims use actual post-interruption executions; deleted-run PASS results are
not inherited. Failed bootstrap attempts, the repaired duplicate-source-label
guard, and the final restore hash-guard addendum remain in the evidence.

`COMPLETE_VERIFIED_SCOPED_FROZEN_OPERATOR` means this bounded study is complete.
It includes failed age/work accuracy targets. It does not admit longspan
time/age/spectrum/angle convergence, a universal second-order H/He/D gas scheme,
full EoR initial conditions, or two-way Einstein feedback. The next bounded node
is `BR07_NATIVE_MOMENT_ENERGY_ADMISSION`; it is not executed automatically.
