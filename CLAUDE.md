# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

`AGENTS.md` holds the binding repository policy (trust model, research-integrity
boundary, anti-bureaucracy/execution-transition rule, typed-identity rule for
hash mismatches, tiered delegation). Read it; it is not repeated here.

## What this repo is

Personal research repo extending homogeneous reionization (H/He thermochemistry
+ ionizing radiation) toward nonlinear, finite-tilt Bianchi cosmologies. Active
implementation is **Rust only**. Python/JAX packages were retired; old Python
commands in stage receipts and handoff docs are historical, not active
instructions. Rust binary64 behavior is canonical.

Most tracked files are evidence, not code: `stages/` (durable per-stage
directories with receipts/manifests, ~2300 files), `docs/`, `runs/`,
`artifacts/`. Failed attempts are preserved as separate `__ATTEMPT_*`
directories and are never overwritten.

The former global CUH-G harness is no longer installed. Its historical local
`.cuh/` directory was removed from this checkout on 2026-10-14 after an exact
archive comparison. The owner-local archive is
`~/.codex/backups/rei_bianchi-cuh-20261014/cuh-51c23b82.tar.zst` (SHA-256
`a7c50be6c2226e835b2a09546feaf7a6d019771e9046151e39fa75d76749749c`).
Older evidence and replay instructions that reference `.cuh/` require restoring
the needed files from that archive. This local archive is not a remote Git
publication. New work uses this checkout by default as specified in `AGENTS.md`.

## Commands

Each crate is its own standalone workspace (`[workspace]` in each
`Cargo.toml`), so always pass `--manifest-path`. CI (`.github/workflows`) runs
only fmt + test on `rei_microphysics`.

```bash
M=rust/rei_microphysics/Cargo.toml
cargo fmt   --manifest-path $M --all -- --check
cargo test  --manifest-path $M --workspace --locked
cargo clippy --manifest-path $M --workspace --all-targets --locked -- -D warnings
python scripts/verify_repo.py     # hashes artifacts/compact against artifacts/registry, checks handoff exists

# single test file / single test
cargo test --manifest-path $M --locked --test he_rct
cargo test --manifest-path $M --locked --test he_rct -- some_test_name --exact
```

Other crates (edition 2024, rust 1.94):
- `rust/rei_peebles_reference` — depends on `rec_microphysics` via git at a pinned rev of `rec_bianchi`.
- `rust/rei_rec_source_adapter` — depends on `rec_microphysics` by **path** `../../../rec_bianchi/rust/rec_microphysics`, i.e. a sibling checkout at `~/Dropbox/bianchi/rec_bianchi`. Builds fail without it.

Campaign drivers are `examples/` (run with `--release`):

```bash
cargo run --release --manifest-path $M --example first_interval -- \
  --input docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_first_interval.json \
  --output <dir> [--pilot] [--resume]
cargo run --release --manifest-path $M --example paired_history -- \
  --scenario configs/rei_fastest_v1/science_scenario_v1.json --output <dir> \
  [--pilot|--full] [--resume] [--only SPEC_GEOMETRY]   # GEOMETRY ∈ FLRW, BI, EPS_HALF
```

These drivers `include_str!` their frozen input and their own source files at
compile time, refuse to run if the input file bytes differ, and write a
`source_identity` file into the output dir; `--resume` refuses if the compiled
source differs. Consequence: **editing any source file listed in a driver's
identity list invalidates resume of existing runs under `runs/`** — start a new
output dir instead. `paired_history` also pulls `src/paired_runtime.rs` via
`#[path]` (it is not a `lib.rs` module).

## Architecture (`rust/rei_microphysics`)

Pipeline target (`docs/architecture/ARCHITECTURE_LOCK.md`):
background history → total-opacity/photon-control operator → node H/He
chemistry + thermal state → `MatterSource` → Bianchi geometry backend.
Primordial recombination is an *external* provider (`rec_bianchi`), never
reimplemented or surrogated here.

Module layers in `src/`:
- **Verified arithmetic**: `interval_math` (`Interval`, outward rounding), `interval_ad` (`Jet` Taylor AD), `joint_affine` (shared-parent affine differences).
- **Rate/opacity kernels**: `group_rates` (PCHIP tables, photon rates), `homogeneous_rates`, `ft03_rates`, `atomic_provider` (raw coefficient records with units/temperature domains), `he_rct`.
- **State + steppers**: `hhe_events`/`microstep` (synthetic 3-group static H/He, implicit BE with full vs two-half local-error control, transactional reject + bisection), `ft03_controlled`/`ft03_interval`/`adaptive_history` (temperature-dependent FT03 successor, certified trials), `hydrogen_step`, `thermal`, `isotope_state`, `lift` (signed/positive transfer lifts).
- **Radiation & geometry**: `angular_photons` (photon grid/packets), `bianchi_i` (constant-H and axisymmetric Bianchi I backgrounds, characteristic rays), `axisym_*` (run contract, coupling, radiation ledger, source routing), `flrw_three_equations`, `coupled_primary`.
- `lib.rs` re-exports the public surface and defines the original four-group `State`/`GroupParams`/`ForwardError`. `#![forbid(unsafe_code)]`.

Unit conventions (from `lib.rs`): four-group `N` is comoving count per cMpc³;
atomic densities and three-group H/He photons are proper cm⁻³. Physics
conventions: metric `(-,+,+,+)`, `ε_123=+1`, explicit `c`, `ħ`, `k_B`.

Numerical invariants the code and tests enforce (do not relax silently): no
clipping, no table extrapolation (`OutsideTableDomain` error instead), strict
local error `< 2e-4`, public width `< 2e-3`, structural conservation ledgers
(stoichiometry, photon ownership, augmented energy) close exactly. Changing
tolerances, fixtures (`tests/fixtures/`), or frozen inputs changes the
scientific claim and needs owner/Astra decision per `AGENTS.md`.

## Scientific state and handoff

Read order for current state: `handoff/CURRENT_HANDOFF_PROMPT.md` →
`PROJECT_STATE.json` → `docs/science/current_00_READ_FIRST.md` →
`docs/provenance/DURABLE_STAGE_LEDGER.csv`. Historical admitted claim boundary: one certified FLRW thermochemistry
microstep. The latest 2026-10-15 owner instruction authorizes production Rust
edits, controlled runs, and source-native cross-repository integration.
Scientific admission remains evidence- and scope-bound: this authorization
does not itself certify production node chemistry, `R2C-R2`, `B2C2B`,
recombination splice, CAMB transfer, or Bianchi feedback. Read
`research/flrw_production_integration_20261015/HANDOFF.json` for current
execution and unresolved representation limits; historical receipts are unchanged.

Active "fastest-track" work (FLRW/Bianchi-I paired histories, task cards
`REI-F0x`) lives in `docs/atomic_reionization_handoff_20261004_v1/`
(`GLOBAL_DAG.json`, `TASK_CARDS.jsonl`, `runtime_inputs/`, `runtime_returns/`)
with research↔Codex sync notes in `docs/fastest_track_chat/` (mostly Korean).
For current planning, read `docs/fastest_track_chat/CURRENT_PLAN.json` before
using the historical `REI-F0x` task packet. The 2026-10-12 plan names `RUX-P0`
and `docs/fastest_track_chat/REI-ATOMIC-REUSE-RESET-20261012/CODEX_START_KO.md`
as the next task and document; refresh that plan before execution.
Run outputs: `runs/rei_fastest_v1/{first_interval,map_certificate,paired}`.

## External dependency

`rec_bianchi` is pinned in `external/rec_bianchi.lock.json`. Before a new
science stage run `./scripts/update_rec_bianchi_lock.sh` and follow
`external/REC_BIANCHI_MONITORING_POLICY.md`; a changed upstream SHA needs
deliberate adapter review. A weekly GitHub workflow fails when upstream HEAD
diverges from the lock.

## Branches / remote

`main`: source, compact artifacts, manifests, handoff. `archive/full-history`:
historical bundles. Claim a remote write only after `git ls-remote`, push, and a
post-push SHA comparison all succeed. Large untracked `*.zip`/`*.bundle`/
`*.tar.xz` files at repo root are local transport packages; leave them alone.
