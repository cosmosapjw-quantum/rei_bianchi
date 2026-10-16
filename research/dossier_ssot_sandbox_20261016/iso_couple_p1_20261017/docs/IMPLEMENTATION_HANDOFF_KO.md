# ISO-COUPLE 실행 인계 및 후속 R/C 작업

## 실제 실행 단위

- Source: `rust/rei_iso_couple_reference/` standalone, Rust edition 2024; no dependencies downloaded. PR150 frozen original modules under `owner_src/` in **unchanged bytes**. `src/mixture_eos.rs` inherits PR179 EOS reference; `src/mixture_coupling.rs` contains the new Heun CX-only integrator and ownership gate.
- Primitive reference `DAtomicProvider::new(chi_H_ev, chi_D_ev, source).defect()` is compiled from original PR150 code, never made-up DAtomicProvider substitute. `Savin2002::rates` is also original source. `HHeModel::controlled_fixture()` two constants are reproduced identically in a minimal link shim to avoid importing unrelated production runtime.
- New `MixtureCxComponent::atomic_rhs()` calls original `ThermalCxComponent::rhs()` with bound provider/owner/photo. `advance_cx_only()` rejects `AtomicRhs`, and requires `ThermalSubstep` for finite time. Trial rejects are atomic errors; no partial state is committed.
- `examples/campaign.rs`: 4 He loads × 3 time horizons × 3 tolerances with 12 separately integrated strict references; `examples/savin_balance_scan.rs` distinguishes alternative conditional detailed balance from frozen rate source. Values in both files are explicitly MANUFACTURED-input, not fitted cosmological histories.

## Bounded commands

```
source '/mnt/data/rust_1_94_1_env(6).sh'
export CARGO_BUILD_JOBS=1 CARGO_INCREMENTAL=0
bash scripts/RUN_STAGE.sh
```

`RUN_STAGE.sh` checks actual Git blob hashes, runs Rust unit/integration (36/36), `cargo clippy --all-targets -- -D warnings`, and replays the offline release examples. Rustfmt only targets new code files, not the #[path]-included frozen owner modules. Numeric tests do not adjust the original source's Savin domain. Work budget: one Cargo worker, < 1 GiB expected RAM, finite number of 36 scenarios; no NCP/local/Codex.

## Acceptance and HOLD

PASS_SCOPED for exact H/He/D mixture EOS connection, native source-bound defect, CX-only finite-time solver, atomic/substep XOR, 36 regression tests and strict deterministic 36-row time/tolerance probes. No full coupled H/He/D production step. The original 26-node DAG `ISO-COUPLE` depends on `BI-SIGNED`, currently HOLD, and remains `PARTIAL_CX_ONLY` rather than globally PASS.

New next task `ISO-COUPLE-P2`: pair `DAtomicRhs` PI/CI/RR/CE rates with H/He gas RHS on one **shared EOS/event clock**, then one photon absorber owner per physical photon and a single ff/CMB heat/charge owner. Requires source-matched actual spectra and certified time splitting, independent timing convergence. Continue separate `SA-01`, `SA-02`, `FLRW-CONV`, `BI-SIGNED` without replaying previous full campaigns. Distinguish optional conditional detailed-balance rate law from original Savin fits as model alternatives.
