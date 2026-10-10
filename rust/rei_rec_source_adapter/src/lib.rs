//! Fixed-input REC-to-REI selected-He ledger binding.
//!
//! This projects a supplied REC proper-SI, gas-proper-seconds material ledger
//! into REI's isotope slots. It does not select a physical source, map a
//! screen, evolve radiation packets, or inject a source into the H/He RHS.
use rec_microphysics::ledger::HeEventLedger;
use rei_microphysics::IsotopeSpecies;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum SourceConvention {
    SelectedHe4ProperSiGasSeconds,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct SelectedHeIsotopeSource {
    pub species_dot_m3_s: [f64; 13],
    pub electron_dot_m3_s: f64,
    pub photon_number_dot_m3_s: f64,
    pub internal_power_j_m3_s: f64,
    pub photon_power_j_m3_s: f64,
    pub kinetic_power_j_m3_s: f64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum AdapterError {
    NonFiniteLedger,
    ConservationMismatch,
}

fn residual_is_closed(value: f64, terms: &[f64]) -> Result<bool, AdapterError> {
    let scale = terms.iter().map(|x| x.abs()).sum::<f64>();
    if !scale.is_finite() {
        return Err(AdapterError::NonFiniteLedger);
    }
    if scale == 0.0 {
        return Ok(value == 0.0);
    }
    let normalized = value / scale;
    if !normalized.is_finite() {
        return Err(AdapterError::NonFiniteLedger);
    }
    Ok(normalized.abs() <= 64.0 * f64::EPSILON)
}

/// Preserves the REC selected-He bookkeeping: ground, S and P populations
/// become the REI He4-neutral slot; ionized He becomes He4:q1. This is valid
/// only at declared zero tilt, where REC's material and normal clocks coincide.
pub fn project_selected_he4_non_tilted(
    ledger: &HeEventLedger,
    convention: SourceConvention,
) -> Result<SelectedHeIsotopeSource, AdapterError> {
    match convention {
        SourceConvention::SelectedHe4ProperSiGasSeconds => {}
    }
    let values = [
        ledger.species_source[0],
        ledger.species_source[1],
        ledger.species_source[2],
        ledger.species_source[3],
        ledger.species_source[4],
        ledger.species_source[5],
        ledger.he_nuclei_residual,
        ledger.charge_minus_e_residual,
        ledger.photon_number_source,
        ledger.p_internal,
        ledger.p_gamma,
        ledger.h_kin,
        ledger.energy_residual,
    ];
    if values.iter().any(|x| !x.is_finite()) {
        return Err(AdapterError::NonFiniteLedger);
    }
    if !residual_is_closed(ledger.he_nuclei_residual, &ledger.species_source[..4])?
        || !residual_is_closed(
            ledger.charge_minus_e_residual,
            &[ledger.species_source[3], ledger.species_source[4]],
        )?
        || !residual_is_closed(
            ledger.energy_residual,
            &[ledger.p_internal, ledger.p_gamma, ledger.h_kin],
        )?
    {
        return Err(AdapterError::ConservationMismatch);
    }
    let mut species_dot_m3_s = [0.0; 13];
    species_dot_m3_s[IsotopeSpecies::He4Neutral as usize] =
        ledger.species_source[0] + ledger.species_source[1] + ledger.species_source[2];
    species_dot_m3_s[IsotopeSpecies::He4SinglyIonized as usize] = ledger.species_source[3];
    Ok(SelectedHeIsotopeSource {
        species_dot_m3_s,
        electron_dot_m3_s: ledger.species_source[4],
        photon_number_dot_m3_s: ledger.photon_number_source,
        internal_power_j_m3_s: ledger.p_internal,
        photon_power_j_m3_s: ledger.p_gamma,
        kinetic_power_j_m3_s: ledger.h_kin,
    })
}
