//! HG97 Case-A HII recombination and thermal cooling component, proper SI.
//! A separate component, with no history, helium reactions or photon spectrum.
pub const SOURCE_SHA256: &str = "6ea0b803b554c91d598705f96416e1a8b67549fb02cb567944eaacdba5d148b0";
pub const KB: f64 = 1.380649e-23;
pub const CHI_J: f64 = 13.598434599702 * 1.602176634e-19;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ComponentError {
    TemperatureDomain,
    DensityDomain,
    NonFiniteOutput,
}

#[derive(Debug, Clone, Copy)]
pub struct Coefficients {
    pub alpha_m3_s: f64,
    pub cooling_j_m3_s: f64,
}

#[derive(Debug, Clone, Copy)]
pub struct Stage {
    pub coefficients: Coefficients,
    pub recombinations_m3_s: f64,
    pub cooling_w_m3: f64,
    pub dn_hi_m3_s: f64,
    pub dn_hii_m3_s: f64,
    pub dn_e_m3_s: f64,
    pub d_thermal_w_m3: f64,
    pub d_binding_w_m3: f64,
    pub d_escape_w_m3: f64,
    pub d_temperature_k_s: f64,
}

pub fn coefficients(temperature_k: f64) -> Result<Coefficients, ComponentError> {
    if !temperature_k.is_finite() || !(3.0..=1e9).contains(&temperature_k) {
        return Err(ComponentError::TemperatureDomain);
    }
    let lambda = 315614.0 / temperature_k;
    let alpha = 1.269e-13 * lambda.powf(1.503) / (1.0 + (lambda / 0.522).powf(0.470)).powf(1.923);
    let cooling = 1.778e-29 * temperature_k * lambda.powf(1.965)
        / (1.0 + (lambda / 0.541).powf(0.502)).powf(2.697);
    let result = Coefficients {
        alpha_m3_s: alpha * 1e-6,
        cooling_j_m3_s: cooling * 1e-13,
    };
    if !result.alpha_m3_s.is_finite()
        || !result.cooling_j_m3_s.is_finite()
        || result.alpha_m3_s <= 0.0
        || result.cooling_j_m3_s <= 0.0
    {
        return Err(ComponentError::NonFiniteOutput);
    }
    Ok(result)
}

/// Charge-neutral HII-only stage: ne = nHII = nH*xe; neutral helium spectator.
pub fn stage(
    temperature_k: f64,
    n_h_m3: f64,
    n_he_m3: f64,
    xe: f64,
) -> Result<Stage, ComponentError> {
    let coefficients = coefficients(temperature_k)?;
    if !n_h_m3.is_finite()
        || !n_he_m3.is_finite()
        || !xe.is_finite()
        || n_h_m3 < 0.0
        || n_he_m3 < 0.0
        || !(0.0..=1.0).contains(&xe)
        || n_h_m3 + n_he_m3 <= 0.0
    {
        return Err(ComponentError::DensityDomain);
    }
    let ne = n_h_m3 * xe;
    let r = coefficients.alpha_m3_s * ne * ne;
    let cooling = coefficients.cooling_j_m3_s * ne * ne;
    let binding = CHI_J * r;
    let temperature_dot =
        (-cooling + 1.5 * KB * temperature_k * r) / (1.5 * KB * (n_h_m3 + n_he_m3 + ne));
    if ![ne, r, cooling, binding, binding + cooling, temperature_dot]
        .iter()
        .all(|x| x.is_finite())
    {
        return Err(ComponentError::NonFiniteOutput);
    }
    Ok(Stage {
        coefficients,
        recombinations_m3_s: r,
        cooling_w_m3: cooling,
        dn_hi_m3_s: r,
        dn_hii_m3_s: -r,
        dn_e_m3_s: -r,
        d_thermal_w_m3: -cooling,
        d_binding_w_m3: -binding,
        d_escape_w_m3: binding + cooling,
        d_temperature_k_s: temperature_dot,
    })
}
