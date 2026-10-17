//! Opt-in, constant-source/frozen-opacity proper-volume photon clock.
//! No expansion, source-age reconstruction or time-dependent Bianchi admission.
use crate::full_network::NetworkError;
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct BirthPartition {
    pub surviving: f64,
    pub absorbed: f64,
}
/// Integrated births B (number / proper m^3), not emission rate.
/// The positive complement is evaluated directly to retain optically thin events.
pub fn uniform_partition(old: f64, births: f64, tau: f64) -> Result<BirthPartition, NetworkError> {
    if [old, births, tau].iter().any(|x| !x.is_finite() || *x < 0.) || !(old + births).is_finite() {
        return Err(NetworkError::InvalidInput);
    }
    let (phi, birth_absorbed) = if tau < 1e-3 {
        let factor = 0.5
            + tau
                * (-1. / 6.
                    + tau
                        * (1. / 24.
                            + tau
                                * (-1. / 120.
                                    + tau * (1. / 720. + tau * (-1. / 5040. + tau / 40320.)))));
        (1. - tau * factor, (births * tau) * factor)
    } else {
        let phi = -(-tau).exp_m1() / tau;
        (phi, births * (1. - phi))
    };
    let old_surviving = if tau > 700. && old > 0. {
        (old.ln() - tau).exp()
    } else {
        old * (-tau).exp()
    };
    let result = BirthPartition {
        surviving: old_surviving + births * phi,
        absorbed: old * (-(-tau).exp_m1()) + birth_absorbed,
    };
    if [result.surviving, result.absorbed]
        .iter()
        .any(|x| !x.is_finite() || *x < 0.)
    {
        return Err(NetworkError::NonFinite);
    }
    Ok(result)
}
