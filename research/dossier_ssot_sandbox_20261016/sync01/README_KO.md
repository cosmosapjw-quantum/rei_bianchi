# REI sandbox continuation: SYNC-01 + bounded FT-B1A

Date: 2026-10-16 KST. Stacked add-only on [PR175](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/175), no owner native production edits.

## What was done

1. GitHub source/current branch readback for main, PR104/150/171/173/174/175 and four PR150 native Rust files.
2. Source-qualified 3-point projections of **two actual saved PR104 RUN002 preview CSVs** at line positions 1, 129, 257. Underlying full 16,384-step calculations are retained, not reexecuted.
3. New Rust code that consumes those sample rows and the previously tested PR175 `DiagonalGeometry` Killing map. It computes finite-shear **directional geometric redshift**, not a spectral radiation transfer solution.
4. 12 bounded Rust unit tests, fmt and Clippy passed after one diagnosed repair episode. Independent mpmath integral checks the new a2 coefficient.

## Exact result

- PR104 counterfactual signed initial shear parameter r=s/H=+0.1, Δb=0.0590521274906396 between mean z=20 and4.
- Exact equator/pole δln(E_emit/E_obs): -0.0590521274906396, 0.118104254981279.
- P2 coefficient of log redshift a2 = 0.120727326454519. The small-b expression 2Δb = 0.118104254981279; finite-b correction = 0.00262307147323967.
- N1024 Simpson vs independently high-precision integral |Δa2| = 1.393e-12 < 2e-11. The N512 attempt exceeded this same criterion (2.23e-11); increased resolution, did not widen tolerance.
- Existing PR104 **segment-only** tau(z=20→4) = 0.037415709019 Bianchi, 0.037441821269 FLRW. Not a new tau computation.

## Interpretation

Metric signature (-,+,+,+), a_perp=a e^(-b), a_parallel=a e^(2b). Same x=ln(a/a_i) means same mean redshift, **not equal proper time**. This comparison isolates angular redshift from the scalar shear-energy effect in H. It is an isotropized transport diagnostic, not a physically separate Einstein solution.

PR104 uses Robertson2015 integrated ionizing emissivity and Hui-Gnedin1997 Case B. Q denotes a **volume filling factor**. Neither Q nor the source gives an ionizing spectrum: `ionizing_spectrum=null`, `directional_intensity=null`, `total_cmb_tau=null`. No claims about native source-on EoR, Thomson visibility or polarization.

## Replay

```bash
export PATH=/mnt/data/rust-1.94.1-prefix/bin:$PATH
M=research/dossier_ssot_sandbox_20261016/sync01/rust/rei_pr104_geom/Cargo.toml
CARGO_BUILD_JOBS=1 cargo test --offline --locked --manifest-path "$M"
cargo fmt --manifest-path "$M" --all -- --check
CARGO_BUILD_JOBS=1 cargo clippy --offline --locked --manifest-path "$M" --all-targets -- -D warnings
CARGO_BUILD_JOBS=1 cargo run --offline --locked --quiet --manifest-path "$M"
```

For an extracted backup, execute these commands from the extraction root; the archive includes the baseline V2 reference Rust crate. On GitHub the baseline already exists at PR175 and is not republished in this branch.

See `contracts/SYNC01_SOURCE_LEDGER.json` and `contracts/DAG_PROGRESS.json`. Original 26-node SSOT remains unchanged.
