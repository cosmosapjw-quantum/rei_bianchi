# Native BASS, REC and REI evolution

The R118 BASS Rust core and REC microphysics crate build inside this checkout. The BASS manifest resolves both research dependencies by relative path. REI remains at the project’s existing `rust/rei_microphysics` path. The public registry dependencies and checksums retain the upstream BASS lock.

From the repository root, run the two physical smoke intervals in a fresh output directory:

```bash
python3 components/bass_rec/run_smoke.py run/bass-rec-rei
```

The first run transports the homogeneous Bianchi I sky from an emission redshift of 1100 over eight steps in log scale factor. The transported radiation and the checked-in HYREC reference table drive REC’s implicit matched recombination correction. The second run takes the independently produced REC HMLA boundary at redshift 20 and advances ionizing packets and H/He/thermal abundances on BASS geometry down to 19.999. These intervals exercise different physical eras. The late interval evolves its own gas and photon state, with one-way geometry on this native entry. Output includes the computed histories, UV energy and momentum ledgers, and a compact summary.

To use the native entry points directly:

```bash
cargo run --locked --manifest-path components/bass_rec/bass/_rustcore/Cargo.toml --example homogeneous_sky -- --help
cargo test --locked --manifest-path components/bass_rec/bass/_rustcore/Cargo.toml --lib --tests
cargo test --locked --manifest-path components/bass_rec/rec/rust/rec_microphysics/Cargo.toml --lib --tests
```

Rust 1.94.1 was used for the integration checks. A populated Cargo cache supports `--offline`. For a fresh offline host, extract only `vendor/` from the original BASS offline bundle pinned in `SOURCE_PROVENANCE.json`, then set `CARGO_HOME/config.toml` as follows using the absolute path on that host:

```toml
[source.crates-io]
replace-with = "vendored-sources"
[source.vendored-sources]
directory = "/absolute/path/to/vendor"
```

Run `python3 components/bass_rec/run_smoke.py --offline run/bass-rec-rei`. Cargo uses the checked-in local crates for the scientific operators and the external vendor directory for the 177 registry package records. A standard full checkout provides the existing REI compile-time scenario, coefficients and contract fixtures.

`SOURCE_PROVENANCE.json` identifies the original crate trees, attached data, licenses, binding changes and the previous dependency revisions. The upstream REC crate at the earlier BASS pin has identical bytes to the imported REC crate. The owner REI crate has 46 changed, added or removed paths. The results in `validation/` document exactly which comparisons sampled this change. Each upstream crate retains its examples, unit tests and integration tests.

## Accepted native material accounting

The final optional flag `--material-trace` on `rei_live_characteristics` evaluates passive charge exchange in each accepted proper-time interval with arithmetic endpoint means of temperature, H density and HII fraction. The initial DII fraction equals the REC HII boundary. The same callback records HI, HeI and HeII absorption counts, threshold work and photoelectron heat from the actual accepted packets. The owner’s H/He solver already applies these events. The tracer contributes zero additional gas, photon or CR source terms.

Run the three matched shear cases at five time resolutions from the repository root:

```bash
python3 components/bass_rec/run_material_trace.py --offline run/bass-rec-material
```

The driver compares each accepted row with a separate Python integration from serialized history, compares species-resolved heat and binding with the host’s original photon ledger, and checks that the default native run and the online observer produce byte-identical default scientific files. The extension keeps the original public evolve functions and positional CLI arguments available. The finite redshift window, fixed spectral and angular quadratures, initialization and absent dynamical D feedback bound interpretation.

Two extra runs at 32 and 64 steps compare equal elapsed proper time by moving the final redshift of the positive-shear case. At 64 steps the fixed-redshift DII difference relative to FLRW is +8.99251e−10. The elapsed time differs by −5.02928e6 s. At a matched elapsed time (1.39 s residual in 4.024e11 s), the DII difference is +4.76831e−14. This control attributes most of the fixed-redshift contrast to the available reaction time. The residual also includes the small change in endpoint redshift. Per-case states and per-absorber energies are recorded in `validation/ACCEPTED_MATERIAL_TRACE.json`.
