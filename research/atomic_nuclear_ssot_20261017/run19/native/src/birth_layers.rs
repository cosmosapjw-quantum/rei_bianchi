//! Positive composite GL4 quadrature in remaining birth age v=(t1-t_birth)/dt.
//! A finite optical seed fixes the first panel; later panels grow geometrically.
//! The seed used with evolving gas is a scale estimate, not a certified opacity bound.
use crate::full_network::NetworkError;
use crate::retarded_transport::gauss_birth_nodes;

#[derive(Clone, Copy, Debug)]
pub struct BirthNode {
    pub remaining_fraction: f64,
    pub weight: f64,
}

/// Complete partition of [0,1], retaining the opaque tail rather than discarding it.
pub fn graded_panels(
    tau: f64,
    growth: f64,
    max_panels: usize,
) -> Result<Vec<(f64, f64)>, NetworkError> {
    if !tau.is_finite()
        || tau < 0.0
        || !growth.is_finite()
        || !(1.0..=2.0).contains(&growth)
        || growth == 1.0
        || !(1..=4096).contains(&max_panels)
    {
        return Err(NetworkError::InvalidInput);
    }
    let mut panels = Vec::new();
    let mut left = 0.0;
    let mut right = if tau <= 1.0 { 1.0 } else { 1.0 / tau };
    while left < 1.0 {
        if panels.len() == max_panels {
            return Err(NetworkError::InputOutsideDomain);
        }
        if !right.is_finite() || right <= left {
            return Err(NetworkError::NoForwardProgress);
        }
        panels.push((left, right));
        left = right;
        right = if left >= 1.0 / growth {
            1.0
        } else {
            left * growth
        };
    }
    Ok(panels)
}

pub fn graded_birth_nodes(
    tau: f64,
    growth: f64,
    max_panels: usize,
) -> Result<Vec<BirthNode>, NetworkError> {
    let panels = graded_panels(tau, growth, max_panels)?;
    let gl = gauss_birth_nodes(4)?;
    let mut nodes = Vec::with_capacity(4 * panels.len());
    for (a, b) in panels {
        for &(u, w) in &gl {
            let v = a + (b - a) * u;
            let weight = (b - a) * w;
            if !v.is_finite() || v <= a || v >= b || !weight.is_finite() || weight <= 0.0 {
                return Err(NetworkError::NoForwardProgress);
            }
            nodes.push(BirthNode {
                remaining_fraction: v,
                weight,
            });
        }
    }
    Ok(nodes)
}

/// Analytic GL4 Peano bound for the *constant* extinction integrand exp(-tau*v).
/// Exact-arithmetic inequality; this binary64 evaluation is not outward-rounded.
/// Independent of any assumption that actual_tau equals the grid's optical seed.
pub fn constant_survival_error_bound(
    actual_tau: f64,
    seed_tau: f64,
    growth: f64,
    max_panels: usize,
) -> Result<f64, NetworkError> {
    if !actual_tau.is_finite() || actual_tau < 0.0 {
        return Err(NetworkError::InvalidInput);
    }
    let panels = graded_panels(seed_tau, growth, max_panels)?;
    if actual_tau == 0.0 {
        return Ok(0.0);
    }
    let log_c = -(1_778_112_000.0_f64).ln();
    let mut bound = 0.0;
    for (a, b) in panels {
        let h = b - a;
        let log_term = log_c + h.ln() + 8.0 * (actual_tau.ln() + h.ln()) - actual_tau * a;
        bound += log_term.exp();
    }
    if !bound.is_finite() {
        return Err(NetworkError::NonFinite);
    }
    Ok(bound)
}

/// Stable constant-source survivor fraction.
pub fn stable_new_survival(tau: f64) -> Result<f64, NetworkError> {
    if !tau.is_finite() || tau < 0.0 {
        return Err(NetworkError::InvalidInput);
    }
    if tau == 0.0 {
        return Ok(1.0);
    }
    Ok(-(-tau).exp_m1() / tau)
}
