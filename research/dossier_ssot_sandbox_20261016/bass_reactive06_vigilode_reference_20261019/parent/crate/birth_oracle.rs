//! Diagnostic scalar source convolution only; not a production integrator.
//! tau=kappa[s^-1] * step[s]. Existing Gauss nodes/weights remain unchanged.
use rei_iso_couple_reference::{full_network::NetworkError, retarded_transport::gauss_birth_nodes};
pub fn exact_phi(tau: f64) -> Result<f64, NetworkError> {
    if !tau.is_finite() || tau < 0. {
        return Err(NetworkError::InvalidInput);
    }
    Ok(if tau == 0. {
        1.
    } else {
        -(-tau).exp_m1() / tau
    })
}
pub fn gauss_phi(tau: f64, nodes: usize) -> Result<f64, NetworkError> {
    if !tau.is_finite() || tau < 0. {
        return Err(NetworkError::InvalidInput);
    }
    Ok(gauss_birth_nodes(nodes)?
        .into_iter()
        .map(|(u, w)| w * (-tau * (1. - u)).exp())
        .sum())
}
