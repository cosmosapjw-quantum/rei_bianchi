//! Source-free initially isotropic Bianchi-I radiation, exact Taylor 14 candidate.
//!
//! Derived from S=(1-mu0²)exp(2 db)+mu0²exp(-4 db) for (-,+,+,+).
//! Energy: ∫ sqrt(S) dmu0; P2: ∫ sqrt(S)*P2(mu_local) dmu0.
//! All f64 Taylor coefficients are exact rational values verified by Wolfram15.
//! This intentionally does NOT replace the frozen production 4096-panel Simpson.
//! Restricted |db|<=0.025; outside requires original exact-direction quadrature.
//! No Thomson/ionizing radiation or self-consistent Einstein feedback included.
#[derive(Clone, Copy, Debug)]
pub struct FastMoments {
    pub energy_j_m3: f64,
    pub signed_energy_correction_j_m3: f64,
    pub pressure_anisotropy_j_m3: f64,
    pub dipole_energy_j_m3: f64,
    pub energy_ratio_minus_one: f64,
    pub pressure_over_isotropic: f64,
}

const C_ENERGY: [f64; 13] = [
    8.0 / 5.0,
    -16.0 / 21.0,
    8.0 / 35.0,
    16.0 / 231.0,
    4528.0 / 32175.0,
    -2656.0 / 15015.0,
    -254248.0 / 3828825.0,
    25107568.0 / 183324141.0,
    10458544.0 / 195859125.0,
    -644335456.0 / 5547967425.0,
    -732698224.0 / 17375502375.0,
    4574816.0 / 46334673.0,
    1570056394912.0 / 45853950767625.0,
];
const C_QUAD: [f64; 14] = [
    -8.0 / 5.0,
    8.0 / 7.0,
    -16.0 / 35.0,
    -40.0 / 231.0,
    -4528.0 / 10725.0,
    1328.0 / 2145.0,
    1016992.0 / 3828825.0,
    -12553784.0 / 20369349.0,
    -10458544.0 / 39171825.0,
    322167728.0 / 504360675.0,
    1465396448.0 / 5791834125.0,
    -29736304.0 / 46334673.0,
    -1570056394912.0 / 6550564395375.0,
    13886441783391392.0 / 21890676096464175.0,
];
/// Rigorous *analytic Taylor truncation* bounds for |db|<=0.025, not a bound
/// on binary64 arithmetic, spectral sources or on the full evolution solver.
/// On complex |db|=R=0.4, z=exp(-6 db), the radicand
/// (1-mu²)+mu² z has modulus >=cos(3R)*exp(-6R)>0.
/// Cauchy bounds: |m0|<=exp(4R), |m2|<=exp(R)/2 * (exp(9R)/sqrt(cos(3R))+exp(3R)).
pub fn conservative_taylor14_bounds() -> (f64, f64) {
    let r: f64 = 0.4;
    let rho: f64 = 0.025 / r;
    let tail = rho.powi(15) / (1.0 - rho);
    let energy_max = (4.0 * r).exp();
    let quadrupole_max =
        r.exp() * 0.5 * ((9.0 * r).exp() / (3.0 * r).cos().sqrt() + (3.0 * r).exp());
    (energy_max * tail, quadrupole_max * tail)
}
#[inline(always)]
fn horner(x: f64, coeffs: &[f64]) -> f64 {
    let mut result = 0.0_f64;
    for &v in coeffs.iter().rev() {
        result = result.mul_add(x, v);
    }
    result
}
#[inline]
pub fn fast_bianchi_i_initial_isotropic(
    a: f64,
    b: f64,
    a_ref: f64,
    b_ref: f64,
    eps_ref_j_m3: f64,
) -> Result<FastMoments, &'static str> {
    if !(a.is_finite()
        && a > 0.0
        && a_ref.is_finite()
        && a_ref > 0.0
        && b.is_finite()
        && b_ref.is_finite()
        && eps_ref_j_m3.is_finite()
        && eps_ref_j_m3 >= 0.0)
    {
        return Err("INVALID_PHYSICAL_INPUT");
    }
    let db = b - b_ref;
    if !db.is_finite() || db.abs() > 0.025 {
        return Err("OUTSIDE_VERIFIED_SMALL_SHEAR_DOMAIN");
    }
    let iso = eps_ref_j_m3 * (a_ref / a).powi(4);
    if !iso.is_finite() {
        return Err("NONFINITE_RADIATION_ENERGY_SCALE");
    }
    // In the FLRW limit b=b_ref, both corrections vanish as true exact zeros.
    let delta_ratio = db * db * horner(db, &C_ENERGY);
    let pressure_ratio = db * horner(db, &C_QUAD);
    let energy_ratio = 1.0 + delta_ratio;
    if !energy_ratio.is_finite() || energy_ratio <= 0.0 {
        return Err("NONPHYSICAL_RADIATION_ENERGY_RATIO");
    }
    Ok(FastMoments {
        energy_j_m3: iso * energy_ratio,
        signed_energy_correction_j_m3: iso * delta_ratio,
        pressure_anisotropy_j_m3: iso * pressure_ratio,
        dipole_energy_j_m3: 0.0,
        energy_ratio_minus_one: delta_ratio,
        pressure_over_isotropic: pressure_ratio,
    })
}
