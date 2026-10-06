# H/He low-temperature point provider and thermal RHS

Status: implemented and tested bounded point unit, 2026-10-06. No commit, branch, checkout/rebase, push, production history run or existing scientific claim changed. Sources frozen pending independent reviewer final checks.

## Delivered

Repository relative to rust/rei_microphysics:
- src/igm_rates.rs: independent Case-A selected Grackle phenomenological coefficients; 1..1e6 K operational guard, source floor/cap diagnostics, split RR/DR, explicit low-branch DR cooling residual.
- src/igm_thermal.rs: immutable proper-time chemistry/thermal point evaluator, species/charge and fraction derivatives, EOS temperature derivative, common event owners and separate material binding/thermal, escape, photo input, signed CMB and expansion-work power ledger.
- tests/igm_rates.rs (4 tests), tests/igm_thermal.rs (11 tests).
- tests/data/igm_grackle: original-C selected harness, exact pinned headers, license, 96-row CSV, source/body manifest, provenance/model README. Regenerates offline from delivered repository alone.
- src/lib.rs: only new igm_rates/igm_thermal exports in this unit. Existing foundation exports predate this unit.

Full source file hashes: DELIVERABLE_SHA256.json. Plan and fixed mapping: IMPLEMENTATION_PLAN.md. Detailed exact-version source audit: grackle_source_audit.md. A separate source worker fetched original source, verified constants/caller density products, mechanically isolated C bodies and generated C reference; implementer compared actual Rust output independently.

## Verification

Environment: source /workspace/shared/rei-build-feasibility/env.sh; override CARGO_TARGET_DIR=/workspace/shared/igm-thermal-work/target (separate from publisher/foundation builds).

- Recorded initial runtime-red provider tests in rates-red.log; runtime-red thermal tests in thermal-red.log. One pure-zero test initially passed stub and was retained as boundary regression, not claimed red evidence.
- Independent review found sequential helium complement arithmetic mismatch at [.5,.8,.2]. Reproduced runtime failure in simplex-red.log, then changed complement to 1-(y+z), matching validated simplex sum, no clipping. Regression passes.
- cargo test --locked --offline: exit0,166 tests pass,0 failures, final log full-tests-final.log. Includes original/foundation151 plus15 new.
- Independent literal-C parity:96 temperatures×17 outputs, exact zero checks; maximum relative discrepancy1.13800717496614643e-13; tolerance3e-13. Log parity_summary.txt. No absolute tolerance conceals tiny outputs.
- Bundled gcc reference compiled offline and output byte-matched bundled CSV (SHA25650ece50b98792c6c0210d6b11e2aec29b4caa4acd96ff9e09a31274dcdff4565).
- Scoped rustfmt --check on four new Rust files:exit0, fmt-final.log.
- cargo clippy --locked --offline --lib --tests:exit0, clippy-final.log; zero diagnostics naming new igm_rates/igm_thermal files. Existing repository warnings remain, chiefly literal fixture excessive precision and existing loop style; no blanket suppression or unrelated changes.
- low_temperature_diagnostics.csv produced by probe.rs at explicit manufactured density/composition and temperatures1.01..999999 K; contains source-floor CI event contribution, cap-active CE power, excluded raw DR power, material thermal, escape and signed CMB. This is point numerical diagnostics, not observed/calibrated cosmology.

## Scientific/numerical choices and limits

Fixed CaseA escape, C1, primary-only external rates. CI threshold energy uses existing HHe binding/eV owner; raw approximate CI cooling is not added. RR cooling uses selected Grackle kinetic fits, no FT03 derivative moments. DR k4 summand is off at/below9284 K; matching thermal channel also off, raw reHeII2 residual retained as an excluded diagnostic. Above branch DR kinetic loss plus binding is emitted once. CE middle channel uses ne²*nHeII (erg cm6/s coefficient). Freefree and signed CMB are separate. Source tiny=1e-20 and exponential caps retained explicitly; those numerical low-T artifacts are not empirical validation.

CMB prefactor from CODATA2022 and exact blackbody derivation1.0178101728574782e-37 cgs; no Grackle fixed present-day CMB normalization. Existing HHeModel owns kB/c/eV/threshold constants; historical Grackle kboltz retained only for source reHeII1 parity. Source source audit distinguishes derivation from externally verified formula quotation.

Operational admission is STRICT on actual recovered EOS T. A generic foundation constructor call requesting exactly1 or1e6 K can reconstruct just outside the range and be rejected; two minimal cases are tested and documented. No endpoint projection/clipping or foundation behavior change. Future integrator IC validation MUST evaluate actual EOS/provider admission before running and report mismatch, not silently round it away. Physical fit support is not established across the entire operational domain.

No full time integrator, coupled photon transport, source/emissivity history, Jacobian, interval enclosure/certificate, checkpoint/restart model or observational/REC claim. Externally provided Gamma and heat per absorber are point-regression inputs only; no photon population inferred. HH/RCT/CR, molecules/metals/dust and metastable CI remain excluded. Underflow/overflow/nonfinite invalid point inputs reject without mutation; exact zero electrons/species/He are valid. Future source-driven implementation must retain exclusive photo-event ownership and proper-time versus ln(a) conversion exactly once.
