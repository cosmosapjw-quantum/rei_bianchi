//! Same-stage HG97 HII RR and prescribed HyRec CMB exchange, FLRW local derivative.
//! Neutral He is a spectator. This component performs no time integration.
use crate::{
    axisym_coupled_derivative, cold_compton, cold_hii_rr, AxisymCoupledDerivative,
    AxisymCoupledState, AxisymLocalSources, AxisymmetricPoint, ForwardError, IsotopeSpecies,
};

#[derive(Clone, Copy, Debug)]
pub struct Stage {
    pub temperature_k: f64,
    pub n_h_m3: f64,
    pub n_he_m3: f64,
    pub xe: f64,
    pub particles_m3: f64,
    pub derivative: AxisymCoupledDerivative,
    pub recombinations_m3_s: f64,
    pub cooling_w_m3: f64,
    pub compton_w_m3: f64,
    pub cmb_bath_w_m3: f64,
    pub binding_j_m3: f64,
    pub binding_w_m3: f64,
}

fn bad() -> ForwardError {
    ForwardError::InvalidInput("COLD_STAGE_COMPOSITION_DOMAIN")
}

/// Evaluate the actual current state at a finite nonnegative gas proper-time tag.
pub fn stage(
    time_s: f64,
    geometry: AxisymmetricPoint,
    state: &AxisymCoupledState,
    tgamma_k: f64,
) -> Result<Stage, ForwardError> {
    if !time_s.is_finite() || time_s < 0.0
        || geometry.anisotropy != 0.0
        || geometry.shear_per_s != 0.0
        || state.photon_number_m3 != 0.0
        || state.photon_energy_j_m3 != 0.0
        || state.photon_delta_pressure_j_m3 != 0.0
    {
        return Err(bad());
    }
    let mut diagnostics = None;
    let derivative =
        axisym_coupled_derivative(time_s, geometry, state, cold_hii_rr::KB, |_, current| {
            for species in IsotopeSpecies::ALL {
                if ![
                    IsotopeSpecies::H1Neutral,
                    IsotopeSpecies::H1Ionized,
                    IsotopeSpecies::He4Neutral,
                ]
                .contains(&species)
                    && current.isotopes.density_m3(species) != 0.0
                {
                    return Err(bad());
                }
            }
            let nh = current.isotopes.density_m3(IsotopeSpecies::H1Neutral)
                + current.isotopes.density_m3(IsotopeSpecies::H1Ionized);
            let ne = current.isotopes.density_m3(IsotopeSpecies::H1Ionized);
            let nhe = current.isotopes.density_m3(IsotopeSpecies::He4Neutral);
            let eos = current
                .isotopes
                .try_legacy_hhe_eos(current.thermal_energy_j_m3, cold_hii_rr::KB)?;
            let temperature = 2.0 * current.thermal_energy_j_m3
                / (3.0 * cold_hii_rr::KB * eos.thermal_particle_density_m3);
            let xe = ne / nh;
            let rr = cold_hii_rr::stage(temperature, nh, nhe, xe).map_err(|_| bad())?;
            let cmb = cold_compton::stage(temperature, tgamma_k, nh, nhe, xe).map_err(|_| bad())?;
            let r = rr.recombinations_m3_s;
            let c = rr.cooling_w_m3;
            let q = cmb.d_gas_thermal_w_m3;
            let binding = cold_hii_rr::CHI_J * ne;
            diagnostics = Some((
                r,
                c,
                q,
                binding,
                temperature,
                nh,
                nhe,
                xe,
                eos.thermal_particle_density_m3,
            ));
            let mut species_m3_s = [0.0; 13];
            species_m3_s[IsotopeSpecies::H1Neutral as usize] = r;
            species_m3_s[IsotopeSpecies::H1Ionized as usize] = -r;
            Ok(AxisymLocalSources {
                species_m3_s,
                electron_m3_s: -r,
                photon_number_m3_s: 0.0,
                photon_power_j_m3_s: 0.0,
                thermal_power_j_m3_s: -c + q,
                internal_power_j_m3_s: -cold_hii_rr::CHI_J * r,
                escape_power_j_m3_s: cold_hii_rr::CHI_J * r + c,
                external_power_j_m3_s: q,
            })
        })?;
    let (r, c, q, binding, temperature, nh, nhe, xe, particles) = diagnostics.ok_or_else(bad)?;
    let binding_dot = -3.0 * geometry.mean_hubble_per_s * binding - cold_hii_rr::CHI_J * r;
    if !binding.is_finite() || !binding_dot.is_finite() {
        return Err(bad());
    }
    Ok(Stage {
        temperature_k: temperature,
        n_h_m3: nh,
        n_he_m3: nhe,
        xe,
        particles_m3: particles,
        derivative,
        recombinations_m3_s: r,
        cooling_w_m3: c,
        compton_w_m3: q,
        cmb_bath_w_m3: -q,
        binding_j_m3: binding,
        binding_w_m3: binding_dot,
    })
}
