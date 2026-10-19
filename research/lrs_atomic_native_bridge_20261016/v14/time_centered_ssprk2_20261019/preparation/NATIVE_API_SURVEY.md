# Native API survey for pending V15 contract

Source root: `/workspace/scratch/6af5e9e6c737/v15_work/native_owner/rust/rei_microphysics`.

## Existing public transport APIs

`src/axbi_covariant_transport.rs` owns `PhotonState { number, energy_ref, support_lo, support_hi }` (ray-major fixed reference-energy cells), `RayGeometry { scale, mu, angular_weight }`, and `CovariantTransport`.

- `CovariantTransport::{cell_count,n_energy,edges,empty_state,validate_state}` expose shape, fixed reference edges, and exact physical-envelope checks.
- `CovariantTransport::ray_geometry(&GeometrySnapshot)` supplies current physical-energy scale and angular source weights for each reference ray.
- `CovariantTransport::inventory(&PhotonState,&GeometrySnapshot)` returns total number and physical energy.
- `CovariantTransport::inject(&mut PhotonState,&GeometrySnapshot,zbar,dt_s)` is the existing source deposition owner. It returns `SourceLedger { added_photons_per_h, added_energy_ev_per_h }`, evaluates the same source spectrum and extends physical support by union.
- `CovariantTransport::prepare(&PhotonState,&GeometrySnapshot)` reconstructs threshold-cut positive spectral quadrature into `PreparedAbsorption` with public diagnostics; `prepare_legacy_serial` preserves the serial path.
- `PreparedAbsorption::{evaluate,evaluate_with_rule}` take absorber densities `[f64;3]`, hydrogen density, and proper dt. They produce `AbsorptionResult { state, photo, absorbed_per_h, binding_ev_per_h, heat_ev_per_h }`. `PhotonAttenuation` selects BE or exponential frozen-reconstruction maps. `attenuation_factors` exposes their scalar identity.
- `CovariantTransport::{partition_below_hi,merge_inactive}` own the optional inactive pool partition.

There is currently **no public instantaneous closed-moment absorption derivative**. `AbsorptionNode { cell,q,number,sigma,excess_ev }`, `PreparedAbsorption::{template,nodes}`, `cell_quadrature`, and compensated accumulation helpers are private in this module. An exact derivative API using the native reconstruction requires an additive implementation in this owner or an explicitly authorized visibility/interface change. Inferring derivatives by subtracting nearby finite-step maps is not an existing contract.

## Existing gas point RHS

`src/igm_thermal.rs` exports `igm_point_rhs(&IgmGasState,nh,nhe,h,tcmb,IgmPhotoInput) -> IgmPointRhs`. `IgmPhotoInput` holds per-absorber photoionization rates and heat powers; `IgmPointRhs` holds proper-time fraction/thermal derivatives and every event/cooling/escape/CMB channel. Point evaluation performs no integration or hidden coordinate conversion. `h` is nonnegative expansion; EOS temperature domain is 1..=1e6 K with strict validation.

`src/igm_state.rs` exports `IgmGasState { fractions:[HII,HeII,HeIII], w_erg_per_h }`, `new`, `from_temperature`, `eos`, and `adiabatic_to`; the latter is the exact fixed-fraction a^-2 thermal map. `w_erg_per_h_to_ev` and `w_ev_per_h_to_erg` own unit conversions.

## Existing driver interfaces and visibility

`src/axbi_driver.rs` publicly exposes `Driver::{config,background,source,energies,n_h0_cm3,n_he0_cm3,transport}`, `DriverState`, `Ledgers`, `Driver::geometry_point`, `geometry_increment`, `geometry_map`, `validate`, `residuals`, `photon_inventory`, `photon_pool_inventory`, `total_energy`, `seed_delta`, `moments`, `fixed_step`, `set_source_clocks`, and `last_clock_rhs`.

`DriverState` exposes gas, active N/U/support arrays, inactive N/U arrays, all ledgers, a and counters. The public `geometry_point` returns `src/axbi_background.rs::BackgroundPoint` with a,b,h_flrw_per_s,h_per_s,s_per_s,sigma and public `geometry()` conversion.

`Driver::{photon_state,set_photon_state,inject,tentative,partition_inactive}` and its clock fields are private. `ResidualContext` is private; its evaluation combines a finite-step attenuation map with an implicit gas residual. `chemical_stage` is public but is a finite-step nonlinear solve, not a point RHS.

`src/axbi_physical_birth.rs` is included as a private **child module** `axbi_driver::physical_birth`, with its public types re-exported by `axbi_driver`, via a path attribute at the end of `axbi_driver.rs`; this child can access the private driver helpers. It exposes `PhysicalBirthRule`, `BirthSample`, `BirthMicroSegment`, `BirthStepReport`, and `Driver::fixed_step_physical_birth`. It remains the V14 chronological birth/finite-map experiment, not the pending derivative integrator.

## Preparation limits

No native compilation, tests, toy cases, refinement histories, projection diagnostics or model changes performed. Offline cargo metadata confirms a dependency-free crate. All four required frozen V14 output hashes verified after restoration and after metadata checks. Await the root-owned algorithm, validation and admission contract before editing native code.
