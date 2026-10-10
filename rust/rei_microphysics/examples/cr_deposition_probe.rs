//! One actual source-pinned cold local derivative; no time integration.
use rei_microphysics::axisym_cr_deposition::{
    cr_deposition_derivative, pinned_cr_deposition_geometry, pinned_cr_deposition_packet,
};
use rei_microphysics::{AxisymCoupledState, IsotopeNumberState, IsotopeSpecies};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let p = pinned_cr_deposition_packet()?;
    let g = p.gas;
    let mut n = [0.; 13];
    n[IsotopeSpecies::H1Neutral as usize] = g.n_h_m3 * (1. - g.xi);
    n[IsotopeSpecies::H1Ionized as usize] = g.n_h_m3 * g.xi;
    n[IsotopeSpecies::He4Neutral as usize] = g.n_he_m3 * (1. - g.xi);
    n[IsotopeSpecies::He4SinglyIonized as usize] = g.n_he_m3 * g.xi;
    let isotopes = IsotopeNumberState::new(n)?;
    let kb = 1.380_649e-23;
    let state = AxisymCoupledState {
        thermal_energy_j_m3: 1.5
            * kb
            * isotopes.thermal_particle_density_all_thermal_m3()?
            * g.temperature_k,
        isotopes,
        photon_number_m3: 0.,
        photon_energy_j_m3: 0.,
        photon_delta_pressure_j_m3: 0.,
    };
    let geometry = pinned_cr_deposition_geometry()?;
    let result = cr_deposition_derivative(true, g.time_s, geometry, &state, kb, || Ok(p))?;
    let off = cr_deposition_derivative(false, g.time_s, geometry, &state, kb, || {
        panic!("OFF evaluated provider")
    })?;
    let a = result.audit.ok_or("missing ON audit")?;
    let d = result.derivative;
    // Algebraic source contribution from the returned ledger. No public ON
    // evaluation on a different background is used to isolate this quantity.
    let np = state.isotopes.thermal_particle_density_all_thermal_m3()?;
    let source_temperature = 2. * d.sources.thermal_power_j_m3_s / (3. * kb * np)
        - d.temperature_k * d.sources.electron_m3_s / np;
    let on_minus_off_temperature = d.temperature_k_s - off.derivative.temperature_k_s;
    println!(
        concat!(
        "{{\"provider_id\":\"{}\",\"manifest_sha256\":\"{}\",\"packet_sha256\":\"{}\",",
        "\"closure\":\"{}\",\"temperature_k\":{:.17e},\"temperature_k_s\":{:.17e},",
        "\"species_source_m3_s\":{:?},\"electron_source_m3_s\":{:.17e},",
        "\"thermal_power_j_m3_s\":{:.17e},\"internal_power_j_m3_s\":{:.17e},",
        "\"escape_power_j_m3_s\":{:.17e},\"modelled_ionization_loss_power_j_m3_s\":{:.17e},",
        "\"full_injection_power_j_m3_s\":{:.17e},\"table_raw_residual_j_m3_s\":{:.17e},",
        "\"heat_correction_j_m3_s\":{:.17e},\"table_correction_bound_j_m3_s\":{:.17e},",
        "\"corrected_energy_residual_j_m3_s\":{:.17e},\"off_provider_calls\":0,",
        "\"off_audit_present\":{},\"background_H_s\":{:.17e},\"background_s_s\":{:.17e},",
        "\"source_temperature_k_s\":{:.17e},\"on_minus_off_temperature_k_s\":{:.17e},",
        "\"matched_geometry\":{},\"solver_intervals\":0,",
        "\"scientific_scope\":\"PINNED_LOCAL_DEPOSITION_COMPONENT_NOT_CAUSAL_TURNON_HISTORY\"}}"
    ),
        p.provider_id,
        p.manifest_sha256,
        p.packet_sha256,
        p.closure,
        d.temperature_k,
        d.temperature_k_s,
        d.sources.species_m3_s,
        d.sources.electron_m3_s,
        d.sources.thermal_power_j_m3_s,
        d.sources.internal_power_j_m3_s,
        d.sources.escape_power_j_m3_s,
        a.modelled_ionization_loss_power_j_m3_s,
        a.full_injection_power_j_m3_s,
        a.table_raw_residual_j_m3_s,
        a.heat_correction_j_m3_s,
        a.table_correction_bound_j_m3_s,
        a.corrected_energy_residual_j_m3_s,
        off.audit.is_some(),
        geometry.mean_hubble_per_s,
        geometry.shear_per_s,
        source_temperature,
        on_minus_off_temperature,
        true
    );
    Ok(())
}
