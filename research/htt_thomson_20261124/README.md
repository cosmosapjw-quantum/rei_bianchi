# Thomson exposure on a native REI history

The AX08 density-fixed H/He calculation admits five homogeneous, non-tilted histories over mean redshifts 20 to 4. This transport evaluates the native electron charge along a ray whose receiver lies at the terminal time. The resulting depth is conditional on that receiver. A supplied velocity changes ray transport while holding the archived chemistry fixed. A coupled tilted material solution would also evolve the four-current, radiation field and reaction rates in their proper frames.

## Material and ray

The implementation uses signature `(-,+,+,+)`. A normal observer sees the future-directed photon direction **e** and the electron velocity **β** = **v**/c. In that tetrad the electron-to-normal photon energy ratio is D = γ(1 − **β**·**e**). On a segment of elapsed normal proper time dt, the positive exposure is dτ = c σ_T n_e,rest D dt. The implementation reuses the existing CODATA 2022 Thomson cross section in cm² and REI speed of light in cm/s. The public material table uses m⁻³, dimensionless velocity and seconds. This cold, elastic Thomson loss applies when photon energies in the electron frame are small compared to m_e c². Angular redistribution and polarized gain require a collision operator. The invariant path-element derivation follows [Younsi, Wu & Fuerst (2012)](https://doi.org/10.1051/0004-6361/201219599).

The original chemistry driver exposes its `IgmGasState::eos` result via `Driver::thomson_material_knot`. In the sampled archive the authoritative total is `ne_proper_cm3`, independently interpolated from native output. Dividing by `nH_proper_cm3` gives electrons per H nucleus. A separate comparison uses the published HII, HeII and HeIII fractions and Y_He = 0.2454. The maximum relative difference is 1.87 × 10⁻⁹. The exporter rejects differences above 10⁻⁷ for this specific archive/composition.

Two counterfactual density conventions are available.

- `rest` retains the supplied proper H-nucleus density.
- `normal-inventory` retains the original normal-frame inventory. Since the time component of the baryon four-current is c γ n_rest, the exported rest density is n_normal/γ. A receiver consuming it still applies D once. At fixed inventory the net exposure is proportional to 1 − **β**·**e**.

The original diagonal Bianchi I characteristic transports the terminal direction to each knot using conserved covariant spatial momenta and scale factors (a exp(−b), a exp(−b), a exp(2b)). The independent replay uses the closed-form normalized direction proportional to (e_x exp(Δb), e_y exp(Δb), e_z exp(−2Δb)), with Δb = b(t) − b(receiver). The given terminal direction follows photon propagation. Incoming apparent sky directions have the opposite sign.

Each REI cell integrates the linearly interpolated normal-clock scattering rate. Traversing cells from the receiver gives the probability mass exp(−τ_near)[−expm1(−Δτ)]. The sum plus the no-scatter probability is unity. The optional REC comparison instead integrates its declared log-linear reference density and linear charge-times-D. The replay checks each discretization with an independent numerical integral. At fixed rest density, β=(0.1,0,0) and terminal **e**=(0.6,0,0.8), the SHEAR_PLUS depths are 0.030204095050556018 (REI) and 0.030204131327360117 (REC). The baseline ZERO REI depth is 0.031968167175476965, compared to the archived full native-time result 0.031968182708871438. Four historical native integrals are available. The five-case baseline includes SHEAR_PLUS without that particular native-time archive comparison.

## Reproduction

From the repository root run:

```sh
manifest=rust/rei_microphysics/Cargo.toml
cargo test --offline --manifest-path "$manifest" --test thomson_history
cargo build --release --offline --manifest-path "$manifest" --example thomson_history
rei=rust/rei_microphysics/target/release/examples/thomson_history
python3 research/htt_thomson_20261124/verify.py --rei-binary "$rei" --output /tmp/rei-thomson.json
```

For the cross-repository receipt add `--rec-binary /path/to/rec_ray_thomson`. The committed receipt records the actual REC binary hash. It covers five archival baselines and four tilt scenarios on SHEAR_PLUS, including two spatial-velocity components that vary linearly with normal time and a third independent component. All 267 tests in the native crate's `--tests` run passed. A full default Cargo run also passed with the two legacy example inputs from commit `fef2baf960f57f37b838004fbb8a7d37b3824852` temporarily restored. Their paths are `docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_first_interval.json` and `configs/rei_fastest_v1/science_scenario_v1.json`. The example above builds with the tracked REI source and AX08 data.

```sh
src=research/rei_igm_sync_20261116/approximation_validity/incremental_fifth/results_five/five_case_abundances.csv.gz
gzip -dc "$src" > /tmp/ax08.csv
"$rei" /tmp/ax08.csv SHEAR_PLUS rest 0.1 0 0 0.6 0 0.8 > /tmp/rei-ray.tsv 2>/tmp/rei-ray.json
```

To prescribe a time-dependent velocity, replace the three velocity arguments with `--beta-series FILE.tsv`. Its header is `normal_t_s beta_x beta_y beta_z` separated by tabs, with one row on each selected case's exact normal-time knot. Constant zero recovers the archived non-tilted material frame.

The output table's first nine fields are normal_t_s, n_reference_rest_m3, electrons_per_reference, beta_x, beta_y, beta_z, dir_x, dir_y, dir_z. The trailing columns are N = ln(a) and b. The scalar density and charge have no directional factor applied. For one physical cell select one total charge owner from REC or REI. A consumer processing this raw table multiplies by D once. The separate depth in the JSON diagnostic already incorporates D and is suitable for direct optical-depth comparison. No data in this slice constrain the absent receiver segment below mean redshift 4.
