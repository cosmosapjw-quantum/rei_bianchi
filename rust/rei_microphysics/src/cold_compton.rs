//! Instantaneous Thomson Compton exchange with a prescribed CMB bath, proper SI.
//! Original October-2012 HyRec coefficient, fsR=meR=1. No history admission.
pub const A_K4_S: f64 = 4.91466895548409e-22;
pub const KB_J_K: f64 = 1.380649e-23;
pub const SOURCE_SHA256: &str = "8ffe38f0431fcd1ae04b55f855f36e8643b1c5eb33a947f581f95d628611f976";

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ComponentError {
    TemperatureDomain,
    DensityDomain,
    NonFiniteOutput,
}

#[derive(Debug, Clone, Copy)]
pub struct Stage {
    pub d_temperature_k_s: f64,
    pub d_gas_thermal_w_m3: f64,
    pub d_cmb_bath_w_m3: f64,
    pub dn_hi_m3_s: f64,
    pub dn_hii_m3_s: f64,
    pub dn_hei_m3_s: f64,
    pub dn_heii_m3_s: f64,
    pub dn_heiii_m3_s: f64,
    pub dn_e_m3_s: f64,
    pub d_binding_w_m3: f64,
}

/// Same-stage densities with neutral helium: ne=nH*xe and fHe=nHe/nH.
/// The bath remains prescribed; its energy ledger is distinct from RR escape.
pub fn stage(
    tm_k: f64,
    tgamma_k: f64,
    nh_m3: f64,
    nhe_m3: f64,
    xe: f64,
) -> Result<Stage, ComponentError> {
    if !tm_k.is_finite() || !tgamma_k.is_finite() || tm_k <= 0.0 || tgamma_k <= 0.0 {
        return Err(ComponentError::TemperatureDomain);
    }
    if !nh_m3.is_finite()
        || !nhe_m3.is_finite()
        || !xe.is_finite()
        || nh_m3 <= 0.0
        || nhe_m3 < 0.0
        || !(0.0..=1.0).contains(&xe)
    {
        return Err(ComponentError::DensityDomain);
    }
    let ne = nh_m3 * xe;
    let rate = A_K4_S * tgamma_k * tgamma_k * tgamma_k * tgamma_k;
    let delta = tgamma_k - tm_k;
    let tdot = rate * xe / (1.0 + xe + nhe_m3 / nh_m3) * delta;
    let q = 1.5 * KB_J_K * ne * rate * delta;
    if ![ne, rate, tdot, q].iter().all(|v| v.is_finite()) {
        return Err(ComponentError::NonFiniteOutput);
    }
    Ok(Stage {
        d_temperature_k_s: tdot,
        d_gas_thermal_w_m3: q,
        d_cmb_bath_w_m3: -q,
        dn_hi_m3_s: 0.0,
        dn_hii_m3_s: 0.0,
        dn_hei_m3_s: 0.0,
        dn_heii_m3_s: 0.0,
        dn_heiii_m3_s: 0.0,
        dn_e_m3_s: 0.0,
        d_binding_w_m3: 0.0,
    })
}
