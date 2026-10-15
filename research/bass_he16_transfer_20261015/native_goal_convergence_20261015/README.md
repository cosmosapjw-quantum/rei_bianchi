# Native AXBI short-prefix convergence and collisionless projection

This isolated scientific research lane does not modify the original rei_bianchi live solver. It reuses a pinned original binary and tests a separate linked Rust crate for the geometry remap counterexample. Scientific admission is NOT_ISSUED.

## Inputs

- The original native release binary must hash to `32d11e733155d355a1fa748597b48ea1c8196adba3c871722a7a598f0b6cbfca`.
- The original native source compiled epoch hash in each run is `d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185`.
- The experimental remap probe links a *separate* `librei_microphysics` artifact. Its entire compiled source identity is different. Its ten geometrical/remap functions are matched byte-for-byte in `results/RUST_SOURCE_SURFACE_IDENTITY.json`.
- Original raw results are stored in two experiments under the backed-up `HE18_AXBI_NATIVE_GOAL_20261015` data folder, not under the repository Git tree.

## Reproduce tests

From a repository containing this research directory, run each suite separately:

    export OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
    python3 -m unittest discover -s research/bass_he16_transfer_20261015 -p 'test_*.py' -q
    python3 -m unittest discover -s research/bass_he16_transfer_20261015/directional_tau_20261015 -p 'test_*.py' -q
    python3 -m unittest discover -s research/bass_he16_transfer_20261015/native_goal_convergence_20261015 -p 'test_*.py' -q

Observed on the user's Ubuntu host: 33+19+28 = 80 passing tests. The Python tests use committed scientific result summaries and manufactured fixtures; they do not rerun the entire native cosmological source ODE.

## Native data and optical-depth goal outputs

- `native_probe.py` prepares six one-time isolated frozen configs and can run all three q cases at local_target=1e-5 and 3e-6. Explicit `--execute` is required after creating the plan; it refuses repeating a completed plan.
- `native_third_level.py` similarly prepares/executes three q cases at local_target=1e-6 in a second independent directory.
- `native_goal_analysis.py` reads nine individual native run SHA-bound histories and computes common observer redshift tau0 and tau2 plus level1/level2 differences.
- `third_level_analysis.py` provides level1/level2/level3 source-scope Cauchy differences, not a certified global error or asymptotic convergence order.
- `signed_error_correlation.py` computes a frozen-geometry gas-error counterfactual, not source causal attribution.
- `evidence_manifest.py` verifies all nine raw native histories, binary/source/config bindings and raw evidence hashes. Its generated raw SHA manifest is committed in results.

## Independent Rust freeflight probes

- `axbi_geometry_remap_probe.rs` executes 48 original `Driver::geometry_map` tests with photon-number/energy residuals. Results in `results/REMAP_SEMIGROUP_LEDGER.csv`.
- `axbi_exact_characteristic_vs_remap.rs` compares original `CovariantPhoton::energy_at` to one versus 4096 projected maps across q=-0.005/0/+0.005. Results in `results/REMAP_VS_COVARIANT_CHARACTERISTIC.csv`.
- `remap_semigroup_identity.py` independently proves the two-neighbor projector variance counterexample using exact rational arithmetic.
- `verify_function_surfaces.py` extracts function bodies to prove only the ten selected surfaces are source-byte identical between two DIFFERENT original Rust epochs.

Only the stored source-specific short-prefix calculations and the documented isolated transport functions are verified. Original coupled-ODE global accuracy, recombination/radiation closure, and any present-day CMB-observable claims remain unresolved.
