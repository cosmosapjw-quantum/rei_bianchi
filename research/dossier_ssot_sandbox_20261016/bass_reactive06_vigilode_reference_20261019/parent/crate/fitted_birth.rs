//! Positive two-node exponential fitting on geometric birth-age panels.
//!
//! Ages x are (t_end - t_birth)/dt, weights integrate emitted photons, and
//! tau = kappa * dt. Each panel integrates 1, x and exp(-tau*x) exactly in
//! real arithmetic. The remaining age-distribution error is refined explicitly.
//! No photon is reassigned to a common birth geometry or spectral label.
use crate::full_network::NetworkError;

/// Stable (1-exp(-tau))/tau for a finite, nonnegative optical depth.
pub fn phi(tau: f64) -> Result<f64, NetworkError> {
    if !tau.is_finite() || tau < 0.0 {
        return Err(NetworkError::InvalidInput);
    }
    Ok(if tau == 0.0 {
        1.0
    } else {
        -(-tau).exp_m1() / tau
    })
}

/// Distance from either panel endpoint divided by panel width.
/// If z=tau*width/2, the symmetric offsets are +/- acosh(sinh(z)/z)/tau.
fn endpoint_fraction(z: f64) -> f64 {
    if z < 1e-3 {
        let z2 = z * z;
        let ratio =
            (1.0 + z2 * (1.0 / 90.0 + z2 * (-1.0 / 4200.0 + z2 / 378000.0))) / 3.0_f64.sqrt();
        return 0.5 * (1.0 - ratio);
    }
    if z < 20.0 {
        let excess = if z < 0.5 {
            let z2 = z * z;
            z2 * (1.0 / 6.0
                + z2 * (1.0 / 120.0
                    + z2 * (1.0 / 5040.0
                        + z2 * (1.0 / 362880.0 + z2 * (1.0 / 39916800.0 + z2 / 6227020800.0)))))
        } else {
            z.sinh() / z - 1.0
        };
        let q = (excess + (excess * (excess + 2.0)).sqrt()).ln_1p();
        return 0.5 * (1.0 - q / z);
    }
    // Avoid overflow in sinh and cancellation in z-acosh(sinh(z)/z).
    let log_one_minus = (-(-2.0 * z).exp()).ln_1p();
    let log_sinhc = z + log_one_minus - (2.0_f64.ln() + z.ln());
    let extra = (-(-2.0 * log_sinhc).exp_m1()).sqrt().ln_1p();
    let z_minus_q = 2.0_f64.ln() + z.ln() - log_one_minus - extra;
    0.5 * z_minus_q / z
}

/// Return distinct (age fraction, emitted weight) pairs in youngest-first order.
/// `refinement` fixes eta=1/refinement, independently of macrostep/spectrum.
/// Optical panel widths obey dy <= eta*(1+y), physical widths dx <= eta.
/// For tau<=1 this is uniform composite GL2 in the transparent limit.
pub fn rule(tau: f64, refinement: usize) -> Result<Vec<(f64, f64)>, NetworkError> {
    if !tau.is_finite() || tau < 0.0 || ![1, 2, 4, 8, 16].contains(&refinement) {
        return Err(NetworkError::InvalidInput);
    }
    let r = refinement as f64;
    let mut result = Vec::new();
    let mut left = 0.0;
    while left < 1.0 {
        let width_target = if tau <= 1.0 {
            1.0 / r
        } else {
            (1.0 / tau + left).min(1.0) / r
        };
        let right = (left + width_target).min(1.0);
        if right <= left || result.len() > 100_000 {
            return Err(NetworkError::NoForwardProgress);
        }
        let width = right - left;
        let z = (tau * width) * 0.5;
        let f = endpoint_fraction(z);
        let offset = width * f;
        let young = left + offset;
        let old = right - offset;
        let weight = width * 0.5;
        if ![young, old, weight].iter().all(|x| x.is_finite())
            || young <= left
            || old >= right
            || young >= old
            || weight <= 0.0
        {
            // A representational age collapse is a numerical resolution limit.
            // Never repair it by moving photons to an arbitrary time.
            return Err(NetworkError::NoForwardProgress);
        }
        result.push((young, weight));
        result.push((old, weight));
        left = right;
    }
    Ok(result)
}

#[derive(Clone, Copy, Debug, Default)]
pub struct FrozenInventory {
    pub survivor: f64,
    pub species_absorbed: [f64; 4],
    pub born_survivor: f64,
    pub born_age_moments: [f64; 3],
    pub emitted_age_moments: [f64; 3],
    pub number_residual: f64,
}

/// Independently callable frozen source/competition transaction. Rates are s^-1,
/// old and born are photon counts in a common volume, and dt is seconds.
/// Zero source and transparent gas are admitted without fabricated source data.
pub fn frozen_inventory(
    old: f64,
    born: f64,
    rates: [f64; 4],
    dt: f64,
    refinement: usize,
) -> Result<FrozenInventory, NetworkError> {
    if ![old, born, dt].iter().all(|v| v.is_finite())
        || old < 0.0
        || born < 0.0
        || dt <= 0.0
        || rates.iter().any(|v| !v.is_finite() || *v < 0.0)
    {
        return Err(NetworkError::InvalidInput);
    }
    let kappa: f64 = rates.iter().sum();
    let tau = kappa * dt;
    let nodes = rule(tau, refinement)?;
    let mut out = FrozenInventory::default();
    let mut absorption = old * -(-tau).exp_m1();
    for (age, weight) in nodes {
        let emitted = born * weight;
        let survivor = emitted * (-tau * age).exp();
        absorption += emitted * -(-tau * age).exp_m1();
        out.born_survivor += survivor;
        for p in 0..3 {
            let ap = age.powi(p as i32);
            out.born_age_moments[p] += survivor * ap;
            out.emitted_age_moments[p] += emitted * ap;
        }
    }
    out.survivor = old * (-tau).exp() + out.born_survivor;
    if kappa > 0.0 {
        for (a, k) in out.species_absorbed.iter_mut().zip(rates) {
            *a = absorption * (k / kappa);
        }
    }
    out.number_residual = out.survivor + out.species_absorbed.iter().sum::<f64>() - (old + born);
    if ![out.survivor, out.number_residual, absorption]
        .iter()
        .all(|x| x.is_finite())
    {
        return Err(NetworkError::NonFinite);
    }
    Ok(out)
}
