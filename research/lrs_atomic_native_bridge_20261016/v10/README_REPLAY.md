# V10 isolated native source-clock experiment

The frozen PR #150 input is commit `6ea2b1b4b3875c9163cafc45efe720afded43fc4`.
`prepare_owner_v10.sh REPO NEW_EMPTY_DIR` creates an independent source copy,
checks the original driver and Grackle rate hashes, applies the uniform-birth
attenuation and research-driver patches from PR #167 at
`1e6a3dd60d69b22483d07a30541736018a69dea8`, then applies the V10
opt-in seed, half-opacity, diagnostic ledger, four-channel RR/DR stage and
Newton diagnostic patches. PR #150 production files and checkpoints are not
changed. The PR #167 driver patch contains other experimental driver changes;
all V10 lanes use this derivative except the retained original-owner baseline
smoke in the raw archive. The patched `legacy_be` N8 CSV's original 41 columns
matched the original-owner N8 baseline byte for byte.

Build and run from the new copy:

```bash
CARGO_BUILD_JOBS=2 /root/.cargo/bin/cargo build --release \
  --manifest-path rust/rei_microphysics/Cargo.toml --example native_v10
rust/rei_microphysics/target/release/examples/native_v10 legacy_be 8
```

The study uses `X=ln(a/a0)` on `[0,1e-5]`, `a0=1/21`, total H nuclei density
from the frozen FLRW owner, HII/HeII/HeIII fractions `(0.075,0.12,0.03)`,
`T0=15000 K`, empty initial photons, owner source, 64 transport energy cells,
16 source-energy subdivisions, 8 angular cells, and one transport thread.
`Driver::fixed_step` obtains proper `dt` from `geometry_increment`. The CSV
has cumulative photon/source/chemical/thermal/radiative and geometry ledgers.

Primary modes: `legacy_be`, `no_radiation_be`, `no_radiation_rrmp`, `split_be`,
`uniform_birth`, `full_exp`, `full_exp_half`, `full_exp_half_rrmp`. The first
five resolutions are 8, 16, 32, 64, 128 steps. Selected same-lane references
use 512, 1024 and one targeted 2048 steps. Diagnostic `legacy_tight` and
`best_tight` run only at 128 steps with Newton threshold `1e-13` rather than
`1e-11`. The source-off and photon-off controls coincide because initial
photons are empty; no seed was introduced.

`full_exp_half` evaluates opacity at the arithmetic mean of old and Newton
trial absorber densities at the same midpoint geometry. It rescales
`IgmPhotoInput` by midpoint/end absorber density before `igm_point_rhs` so
photo event and heat counts remain consistent; a positive midpoint event with
zero endpoint absorber fails explicitly. `full_exp_half_rrmp` adds V8's
palindromic four-channel Grackle Case-A exact-pair reaction half stages around
the remaining BE chemistry stage; RR/DR species, cooling and escaped radiation
are removed from that BE RHS once. CI, CE, free-free and CMB remain at the
owner endpoint evaluation. The uniform-birth kernel uses frozen midpoint
geometry and is not a GL2 proper-time source-age cohort calculation. These
are numerical controls, not production changes or a source-on second-order
claim.

The NCP archive `V10_NATIVE_RAW_20261016.tar.gz` contains source identities,
patches, build/test logs (including the first failed diagnostic-ledger build),
original-owner baseline, all controls, stdout/stderr, and `/usr/bin/time -v`
measurements. `NCP_RUN_RECEIPT.json` lists SHA-256 and terminal observables.
