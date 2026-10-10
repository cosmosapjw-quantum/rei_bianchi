//! Local axisymmetric H/He derivative composition with caller-supplied source terms.
//!
//! This module owns no physical initial condition, atomic rate, source history, or
//! closure selection.  Its coupled path is deliberately a local derivative only;
//! a physical history still requires an admitted provider, transport coupling, and
//! convergence evidence.
use crate::{AxisymmetricPoint, ForwardError, IsotopeNumberState, IsotopeSpecies};
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct IsotropicExpansionTerms {
    pub nuclear_density_dot_per_s: f64,
    pub photon_number_dot_per_s: f64,
    pub photon_energy_dot_per_s: f64,
    pub temperature_dot_k_s: f64,
}
pub fn isotropic_expansion_terms(
    hubble_per_s: f64,
    nuclear_density: f64,
    photon_number: f64,
    photon_energy: f64,
    temperature_k: f64,
) -> Result<IsotropicExpansionTerms, ForwardError> {
    if ![
        hubble_per_s,
        nuclear_density,
        photon_number,
        photon_energy,
        temperature_k,
    ]
    .iter()
    .all(|x| x.is_finite())
        || nuclear_density < 0.
        || photon_number < 0.
        || photon_energy < 0.
        || temperature_k < 0.
    {
        return Err(ForwardError::InvalidInput("AXISYM_EXPANSION_DOMAIN"));
    }
    let o = IsotropicExpansionTerms {
        nuclear_density_dot_per_s: -3. * hubble_per_s * nuclear_density,
        photon_number_dot_per_s: -3. * hubble_per_s * photon_number,
        photon_energy_dot_per_s: -4. * hubble_per_s * photon_energy,
        temperature_dot_k_s: -2. * hubble_per_s * temperature_k,
    };
    if [
        o.nuclear_density_dot_per_s,
        o.photon_number_dot_per_s,
        o.photon_energy_dot_per_s,
        o.temperature_dot_k_s,
    ]
    .iter()
    .all(|x| x.is_finite())
    {
        Ok(o)
    } else {
        Err(ForwardError::InvalidInput("AXISYM_EXPANSION_OVERFLOW"))
    }
}

/// Proper local state under the explicit neutral/no-positron/all-electrons-thermal
/// one-temperature nonrelativistic closure.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct AxisymCoupledState {
    pub isotopes: IsotopeNumberState,
    pub thermal_energy_j_m3: f64,
    pub photon_number_m3: f64,
    pub photon_energy_j_m3: f64,
    /// `p_parallel - p_perpendicular`, in J m^-3.
    pub photon_delta_pressure_j_m3: f64,
}

/// Signed local ledger supplied by the selected physical provider.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct AxisymLocalSources {
    pub species_m3_s: [f64; 13],
    pub electron_m3_s: f64,
    pub photon_number_m3_s: f64,
    pub photon_power_j_m3_s: f64,
    pub thermal_power_j_m3_s: f64,
    /// Binding/excitation/rest-energy change, excluded from thermal energy.
    pub internal_power_j_m3_s: f64,
    pub escape_power_j_m3_s: f64,
    pub external_power_j_m3_s: f64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct AxisymCoupledDerivative {
    pub species_m3_s: [f64; 13],
    pub electron_m3_s: f64,
    pub thermal_particle_m3_s: f64,
    pub temperature_k: f64,
    pub temperature_k_s: f64,
    pub thermal_energy_j_m3_s: f64,
    pub photon_number_m3_s: f64,
    pub photon_energy_j_m3_s: f64,
    pub sources: AxisymLocalSources,
}

fn coupled_bad() -> ForwardError {
    ForwardError::InvalidInput("AXISYM_COUPLED_DOMAIN")
}

fn closed(sum: f64, scale: f64) -> bool {
    sum.is_finite()
        && scale.is_finite()
        && scale >= 0.
        && if scale == 0. {
            sum == 0.
        } else {
            sum.abs() <= 128. * f64::EPSILON * scale
        }
}

fn compensated_add(sum: &mut f64, correction: &mut f64, value: f64) {
    let next = *sum + value;
    if sum.abs() >= value.abs() {
        *correction += (*sum - next) + value;
    } else {
        *correction += (value - next) + *sum;
    }
    *sum = next;
}

fn compensated_sum(values: impl IntoIterator<Item = f64>) -> f64 {
    let mut sum = 0.;
    let mut correction = 0.;
    for value in values {
        compensated_add(&mut sum, &mut correction, value);
    }
    sum + correction
}

fn validate_sources(s: AxisymLocalSources) -> Result<(), ForwardError> {
    if !s.species_m3_s.iter().all(|x| x.is_finite())
        || ![
            s.electron_m3_s,
            s.photon_number_m3_s,
            s.photon_power_j_m3_s,
            s.thermal_power_j_m3_s,
            s.internal_power_j_m3_s,
            s.escape_power_j_m3_s,
            s.external_power_j_m3_s,
        ]
        .iter()
        .all(|x| x.is_finite())
    {
        return Err(coupled_bad());
    }
    let mut baryons = 0.;
    let mut baryon_correction = 0.;
    let mut charge = 0.;
    let mut charge_correction = 0.;
    let mut baryon_scale = 0.;
    let mut charge_scale = s.electron_m3_s.abs();
    for species in IsotopeSpecies::ALL {
        let value = s.species_m3_s[species as usize];
        let a = f64::from(species.baryon_number());
        let q = f64::from(species.charge());
        compensated_add(&mut baryons, &mut baryon_correction, a * value);
        compensated_add(&mut charge, &mut charge_correction, q * value);
        baryon_scale += (a * value).abs();
        charge_scale += (q * value).abs();
    }
    let powers = [
        s.photon_power_j_m3_s,
        s.thermal_power_j_m3_s,
        s.internal_power_j_m3_s,
        s.escape_power_j_m3_s,
        -s.external_power_j_m3_s,
    ];
    let baryons = baryons + baryon_correction;
    let charge = charge + charge_correction;
    let power_sum = compensated_sum(powers);
    let power_scale = powers.iter().map(|x| x.abs()).sum::<f64>();
    if !closed(baryons, baryon_scale)
        || !closed(charge - s.electron_m3_s, charge_scale)
        || !closed(power_sum, power_scale)
    {
        return Err(ForwardError::InvalidInput("AXISYM_COUPLED_LEDGER"));
    }
    Ok(())
}

/// Compose geometry dilution/shear work with one caller-supplied local source ledger.
pub fn axisym_coupled_derivative<F>(
    time_s: f64,
    geometry: AxisymmetricPoint,
    state: &AxisymCoupledState,
    kb_j_k: f64,
    provider: F,
) -> Result<AxisymCoupledDerivative, ForwardError>
where
    F: FnOnce(f64, &AxisymCoupledState) -> Result<AxisymLocalSources, ForwardError>,
{
    if !time_s.is_finite()
        || !kb_j_k.is_finite()
        || kb_j_k <= 0.
        || ![
            state.thermal_energy_j_m3,
            state.photon_number_m3,
            state.photon_energy_j_m3,
            state.photon_delta_pressure_j_m3,
        ]
        .iter()
        .all(|x| x.is_finite())
        || state.thermal_energy_j_m3 < 0.
        || state.photon_number_m3 < 0.
        || state.photon_energy_j_m3 < 0.
        || state.photon_delta_pressure_j_m3 < -state.photon_energy_j_m3 / 2.
        || state.photon_delta_pressure_j_m3 > state.photon_energy_j_m3
    {
        return Err(coupled_bad());
    }
    geometry.snapshot()?;
    let moments = state.isotopes.moments()?;
    let particles = state.isotopes.thermal_particle_density_all_thermal_m3()?;
    if particles <= 0. {
        return Err(coupled_bad());
    }
    let thermal_denominator = 3. * kb_j_k * particles;
    if !thermal_denominator.is_finite()
        || thermal_denominator <= 0.
        || thermal_denominator.is_subnormal()
    {
        return Err(coupled_bad());
    }
    let temperature = 2. * state.thermal_energy_j_m3 / thermal_denominator;
    if !temperature.is_finite() {
        return Err(coupled_bad());
    }
    let sources = provider(time_s, state)?;
    validate_sources(sources)?;
    let h = geometry.mean_hubble_per_s;
    let shear = geometry.shear_per_s;
    let mut species_m3_s = [0.; 13];
    let mut heavy_source = 0.;
    let mut heavy_source_correction = 0.;
    for species in IsotopeSpecies::ALL {
        let i = species as usize;
        species_m3_s[i] = -3. * h * state.isotopes.density_m3(species) + sources.species_m3_s[i];
        compensated_add(
            &mut heavy_source,
            &mut heavy_source_correction,
            sources.species_m3_s[i],
        );
    }
    let thermal_source = heavy_source + heavy_source_correction + sources.electron_m3_s;
    let electron_m3_s = -3. * h * moments.neutral_free_electron_density_m3 + sources.electron_m3_s;
    let thermal_particle_m3_s = -3. * h * particles + thermal_source;
    let thermal_energy_j_m3_s = -5. * h * state.thermal_energy_j_m3 + sources.thermal_power_j_m3_s;
    let temperature_k_s = -2. * h * temperature
        + 2. * sources.thermal_power_j_m3_s / thermal_denominator
        - temperature * thermal_source / particles;
    let photon_number_m3_s = -3. * h * state.photon_number_m3 + sources.photon_number_m3_s;
    let photon_energy_j_m3_s = -4. * h * state.photon_energy_j_m3
        - 2. * shear * state.photon_delta_pressure_j_m3
        + sources.photon_power_j_m3_s;
    if !species_m3_s.iter().all(|x| x.is_finite())
        || ![
            electron_m3_s,
            thermal_particle_m3_s,
            thermal_energy_j_m3_s,
            temperature_k_s,
            photon_number_m3_s,
            photon_energy_j_m3_s,
        ]
        .iter()
        .all(|x| x.is_finite())
    {
        return Err(ForwardError::InvalidInput("AXISYM_COUPLED_OVERFLOW"));
    }
    Ok(AxisymCoupledDerivative {
        species_m3_s,
        electron_m3_s,
        thermal_particle_m3_s,
        temperature_k: temperature,
        temperature_k_s,
        thermal_energy_j_m3_s,
        photon_number_m3_s,
        photon_energy_j_m3_s,
        sources,
    })
}
