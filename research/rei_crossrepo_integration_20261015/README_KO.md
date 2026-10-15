# REI C12: five-supplier executable integration, 2026-10-15

## Outcome, authority and main correction

This is an **additive, isolated, actually executed** cross-repository scientific bridge
on top of rei_bianchi C11 commit `10c57ed9419344d56aa9fb2d2f9feeb14b0a20a2` (itself
stacked on C10/C9). The user's original active REI checkout at
`0fcb2dddf5de6b583c2e00f150abff0b2afb6315`, user-owned private AX08
runs/checkpoints, and the sibling repository working trees were *not modified*.

An independent C11 implementation had already been committed in another research
thread while this integration was underway. We **reused** that source-locked
native Case-A stage in our new C12 branch instead of silently overwriting it.
The contemporaneous unmerged alternative Case-A experiment and its observations
were preserved as an explicit pre-isolation private archive, not conflated with the
authoritative C11 source. The integration outcome is not `GOAL_DONE` or full
reionization physics. Native subagent delegation was not available, so
`native_subagent=NOT_RUN` (actual NumPy/Rust multiprocessing is distinct).

## Actual imports, source identities, and results

`mirror_suppliers.py` captures **16 genuine Git blobs** with byte-for-byte
Git blob identities and SHA256 manifests from exactly pinned GitHub commit SHAs.
They are placed as isolated `suppliers/` read-only *inputs*, not replacement
REI production modules. `crossrepo_integration.py` invokes the **actual
supplied algorithms** and verifies scientific/output claims. No inferred API,
invented benchmark, or HTML-only source intake.

| Provider | Actual code or source used | Observed result | Adoption gate |
| --- | --- | --- | --- |
| `bass` PR157 | `Background(Family(q))`, `gauss_increment`, `photon_short_logmap` | 5 signed q × 3 increments, same original REI H(a), positive binary64-nextafter dt=3.5706700623663608 s, phase-space log residual within rounding | isolated short-step kernel parity only; original owner driver callsite is not replaced |
| `bass_cr` PR71 | `PositivePacketOracle`, `AdaptiveQGrid` and original curved moment bounds | actual C10 BB50K q0/μ0/a_emit=.2 single-ray **24 positive photon packets**; 1→8 cells, exact-dyadic N,U, all HI/HeI/HeII photon events and species heats inside supplier envelope | `HOLD_PRECISION_TARGET` until targeted six-channel budgets met, no source-age/angle mixing |
| `rec_bianchi` PR94 | original `REIConditionalIC.from_scenario`, `_state_metrics`, real HyRec FULL donor JSON | original REI source SHA matches; source x_e=.000210349192936, T=9.306042400380866 K vs baseline x_HII=.0002,T=8.098143045064857 K; instantaneous dτ/dln a +5.174596468% | `DISABLED_REQUIRES_SEPARATE_REI_SENSITIVITY_CAMPAIGN`; no physical q≠0 pre-recombination history |
| `WU088_HH` PR83 | original `read_rei_guard` with real accessible WU PHYS19 consumer contract and `ft03_manufactured_response` negative control | actual REI `coverage.rs` excludes HH_R10; source `MD14_Z002_FESC_BB50K_13P6_100_V1`; unapproved physical HH rate invocation refused | `HOLD`: no valid `k_HH(T)`, no microscopic scattering-rate source, HH production OFF |
| `BASS_HE` PR64 | real 16-row `warm_P01_cumulative_tau.csv`, exact `Decimal` bounds, source status | τ(1e11s) in [1.279983109176429360327345119834258225,1.279983109176430675377905063299454235]×10⁻⁷, collision prob ≈1.2799830272585955241×10⁻⁷ | independently conserved warm HM12/FT03 family; **never** relabeled as cold AX08 τ |

The `bass_cr` interval widths (1→8 cells) improved 38.18×/78.81×/185.63×
for HI/HeI/HeII absorption and 170.93×/85.90×/211.44× for corresponding
photoheating. They did **not** reach the predeclared numerical budget;
`HOLD_PRECISION_TARGET` is a measured legitimate failure, not an inferred
production PASS. Actual source opacity, packet energy, and proper dt were passed
without source or frame substitution.

The matched source provider already integrated in the **parent C11** is
`rei_microphysics::igm_rates` (Grackle 3.4.1 Case-A coefficients). It tracks
H/He photoionization and Case-A RR/DR recombination/cooling with exact event
owner identities, not the unadmitted WU collision or BASS_HE warm source.
That parent has its own 129-node rate table, numerical accuracy contracts and
second-order source-scoped photo+recomb test. C12 does not duplicate or supplant
its implementation.

## Reproducibility and computational evidence

From the *isolated C12 root*:
```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
# Verify that five Git commit-pinned blob snapshots are identical (network):
python3 research/rei_crossrepo_integration_20261015/mirror_suppliers.py
# Original WU088_HH repo required for actual previous-provider contract gate:
export WU088_HH_LOCAL_REPO="$HOME/chat_research/WU088_HH"
# Only for an extracted archive without its own .git metadata, bind a live
# REI source checkout with byte-identical coverage/source/FT03/scenario files:
# export REI_NATIVE_CONSUMER_ROOT="$HOME/Dropbox/bianchi/rei_bianchi"
python3 research/rei_crossrepo_integration_20261015/crossrepo_integration.py
python3 -m unittest discover -s research/rei_crossrepo_integration_20261015 -p 'test_*.py' -v
python3 -m unittest discover -s research/source07_c11_casea_20261015 -p 'test_*.py' -v
CARGO_TARGET_DIR=/tmp/rei_c11_rates_target cargo test --offline \
  --manifest-path rust/rei_microphysics/Cargo.toml --test igm_rates
CARGO_TARGET_DIR=/tmp/rei_c11_rates_target cargo test --offline \
  --manifest-path rust/rei_microphysics/Cargo.toml --test igm_thermal
CARGO_TARGET_DIR=/tmp/rei_c11_rates_target cargo test --offline \
  --manifest-path rust/rei_microphysics/Cargo.toml --test axbi_background
```

Ubuntu actual re-execution: C12 Python **6/6 PASS**, C11 Python **8/8 PASS**,
original Rust `igm_rates` **4/4**, `igm_thermal` **11/11**,
`axbi_background` **6/6**. The scientific input and rate-source identity
were also checked with real original Grackle-owner source on the *parent*
`10c57ed`. No local Codex was used. `CROSSREPO_CONSUMER_RESULTS.json`,
`validation/RUN.stdout`, `validation/TESTS.log`,
`validation/ORIGINAL_C11_TESTS.log`, and the three native Cargo test logs
provide replay evidence.

**Units and scientific scope:** default signature (-,+,+,+), proper time in
seconds, real energy in eV, H/He proper number densities in cm⁻³; angular
packet source mu is one reference ray per source age. The independent BASS
clock comparison resolves binary64 proper-time increments rather than
subtracting accumulated cosmological time. C12 is a verified integration
*boundary*, not a fully joint `z=20→4` rate/RT reconstruction or an
observer optical-depth/polarized sky solution.

## Constructive next executable physics

1. Make a source-backed *short interval* with the live AXBI MD14 emissivity
   and actual BASS positive proper-clock/gradient increment at the same
   execution owner (already independent source-proved).
2. Couple a source-provided true child N/U packet grid from `bass_cr` to
   actual evolved gas/chemistry; test 6 reaction envelopes against owner
   source and maintain positive photon/binding/heat ledger. Do not infer
   child distributions from parent N,U.
3. Enable source-identified HyRec q0 z20 IC **only as a separate original
   source sensitivity** from a fresh native zero-photon start. Preserve the
   existing approximate baseline.
4. Keep `WU088_HH` OFF until an admitted thermal `k_HH(T)` and identical
   pair convention exist. Keep BASS_HE P01 separate unless the entire warm
   source/time/opacity contract is explicitly selected and recomputed.
5. Perform AX11/AX12 native dt/dE/dμ coupled convergence before a global
   reionization or observational claim. Results in this bridge alone are
   not numerical bounds on full cosmic reionization.

## Backup and release

The verified source+tests+receipts commit identity, ZIP SHA256, both external
cloud paths, remote file sizes and independent remote hashes belong in
`BACKUP_RECEIPT.json` **after** both uploads have succeeded. This README
by itself does not assert remote preservation before that verification.
