//! Optional source-free radiation + viscous matter LRS Bianchi-I Einstein RHS.
//! Standalone std-only; do not silently alter frozen AX07/AX08 Rust binary.
//! Sigma=sqrt(sigma_ij sigma^ij/2)/H=sqrt3*abs(s)/H. Orientation separate.
//! Energy and pressure units J/m^3; eta units J*s/m^3; time proper seconds.
#[path = "../convergence/ax08_halfminus_fast_20261015/fast_moments.rs"]
mod radiation;
use radiation::fast_bianchi_i_initial_isotropic;

pub const H0: f64 = 67.4e3 / 3.0856775814913673e22;
pub const OM: f64 = 0.315;
pub const OR: f64 = 9.2e-5;
pub const OL: f64 = 1.0 - OM - OR;
pub const AREF: f64 = 1.0 / 21.0;
pub const AEND: f64 = 0.2;
pub const XEND: f64 = 1.4350845252893227; // ln((1/5)/(1/21))=ln(4.2)
pub const HREF: f64 = 1.1835101980340536e-16;
pub const GAMMA_M: f64 = 5.0 / 3.0;
pub const K_SI: f64 = 8.0 * std::f64::consts::PI * 6.67430e-11 / (299792458.0 * 299792458.0);
pub const RHO_CRIT: f64 = 3.0 * H0 * H0 / K_SI;
#[derive(Clone, Copy, Debug)]
pub struct StressModel {
    pub Sigma_ref: f64,
    pub orientation: i8,
    pub free_radiation_fraction: f64,
    pub matter_viscosity_strength: f64,
}
#[derive(Clone, Copy, Debug)]
pub struct State {
    pub b: f64,
    pub signed_s_over_HREF: f64,
    pub thermal_energy_over_rhocrit: f64,
    pub proper_time_times_HREF: f64,
}
#[derive(Clone, Copy, Debug)]
pub struct Rates {
    pub d_b_dlog_a: f64,
    pub d_signed_s_HREF_dlog_a: f64,
    pub d_thermal_energy_dlog_a: f64,
    pub d_proper_time_HREF_dlog_a: f64,
    pub H_per_s: f64,
    pub Sigma: f64,
    pub radiation_pi_J_m3: f64,
    pub matter_pi_J_m3: f64,
    pub hamiltonian_rhs_per_s2: f64,
    pub raychaudhuri_dHdt_per_s2: f64,
}
pub fn validate(model: StressModel) -> Result<(), &'static str> {
    let s = model.Sigma_ref;
    if !s.is_finite()
        || s < 0.0
        || s >= 3.0_f64.sqrt()
        || !model.free_radiation_fraction.is_finite()
        || !(0.0..=1.0).contains(&model.free_radiation_fraction)
        || !model.matter_viscosity_strength.is_finite()
        || !(0.0..=0.1).contains(&model.matter_viscosity_strength)
        || (s == 0.0 && model.orientation != 0)
        || (s > 0.0 && model.orientation != 1 && model.orientation != -1)
    {
        return Err("INVALID_SIGMA_OR_PI_MODEL");
    }
    Ok(())
}
pub fn initial(model: StressModel) -> Result<State, &'static str> {
    validate(model)?;
    let q = if model.Sigma_ref == 0.0 {
        0.0
    } else {
        model.orientation as f64 * model.Sigma_ref
            / (3.0 - model.Sigma_ref * model.Sigma_ref).sqrt()
    };
    Ok(State {
        b: 0.0,
        signed_s_over_HREF: q,
        thermal_energy_over_rhocrit: 0.0,
        proper_time_times_HREF: 0.0,
    })
}
pub fn evaluate(model: StressModel, x: f64, state: State) -> Result<Rates, &'static str> {
    validate(model)?;
    if !x.is_finite()
        || x < 0.0
        || x > XEND + 1e-11
        || !state.b.is_finite()
        || !state.signed_s_over_HREF.is_finite()
        || !state.thermal_energy_over_rhocrit.is_finite()
        || state.thermal_energy_over_rhocrit < -1e-11
        || !state.proper_time_times_HREF.is_finite()
    {
        return Err("UNPHYSICAL_LRS_STATE");
    }
    let a = AREF * x.exp();
    let energy_mom = fast_bianchi_i_initial_isotropic(1.0, state.b, 1.0, 0.0, 1.0)
        .map_err(|_| "OUT_OF_SMALL_SHEAR_RADIATION_DOMAIN")?;
    let monopole = energy_mom.energy_j_m3;
    let quadrupole = energy_mom.pressure_over_isotropic;
    let dust = OM / a.powi(3);
    let thermal = state.thermal_energy_over_rhocrit;
    let rad_iso = OR / a.powi(4);
    let rad_total = rad_iso * (1.0 + model.free_radiation_fraction * (monopole - 1.0));
    let pi_r_norm = rad_iso * model.free_radiation_fraction * quadrupole / 3.0;
    let s = HREF * state.signed_s_over_HREF;
    let h2 = H0 * H0 * (dust + thermal + rad_total + OL) + s * s;
    if !(h2 > 0.0) || !h2.is_finite() {
        return Err("NONPOSITIVE_HAMILTONIAN_CONSTRAINT");
    }
    let h = h2.sqrt();
    let frac = s / h;
    // eta=nu*rho_dust/H; Pi_m = -2*eta*s, consistent instantaneous
    // first-order Navier-Stokes toy (NOT Israel-Stewart causal thermodynamics).
    let pi_m_norm = -2.0 * model.matter_viscosity_strength * dust * frac;
    let pi_total = pi_r_norm + pi_m_norm;
    let derivative_s = -3.0 * state.signed_s_over_HREF + (3.0 * H0 * H0 / (HREF * h)) * pi_total;
    let dy_th = -3.0 * GAMMA_M * thermal - 6.0 * frac * pi_m_norm;
    let ray = -1.5 * H0 * H0 * (dust + GAMMA_M * thermal + 4.0 * rad_total / 3.0) - 3.0 * s * s;
    Ok(Rates {
        d_b_dlog_a: frac,
        d_signed_s_HREF_dlog_a: derivative_s,
        d_thermal_energy_dlog_a: dy_th,
        d_proper_time_HREF_dlog_a: HREF / h,
        H_per_s: h,
        Sigma: 3.0_f64.sqrt() * frac.abs(),
        radiation_pi_J_m3: pi_r_norm * RHO_CRIT,
        matter_pi_J_m3: pi_m_norm * RHO_CRIT,
        hamiltonian_rhs_per_s2: h2,
        raychaudhuri_dHdt_per_s2: ray,
    })
}
