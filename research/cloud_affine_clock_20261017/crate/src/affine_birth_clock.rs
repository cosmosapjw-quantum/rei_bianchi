//! Supporting scalar Duhamel gate for EXTERNALLY PRESCRIBED affine rates.
//! Fixed photon energy and proper volume; no species event allocation, no gas
//! evolution or Bianchi coupling. tau<=1 is a domain bound, NOT an error bound.
use crate::birth_clock::uniform_partition;
use crate::full_network::NetworkError;
#[derive(Clone, Copy, Debug)]
pub struct AffinePartition {
    pub surviving: f64,
    pub absorbed: f64,
    pub injected: f64,
}
pub fn advance_affine(
    old: f64,
    j0: f64,
    j1: f64,
    l0: f64,
    l1: f64,
    h: f64,
) -> Result<AffinePartition, NetworkError> {
    if [old, j0, j1, l0, l1, h]
        .iter()
        .any(|x| !x.is_finite() || *x < 0.)
    {
        return Err(NetworkError::InvalidInput);
    }
    if h == 0. {
        return Ok(AffinePartition {
            surviving: old,
            absorbed: 0.,
            injected: 0.,
        });
    }
    // Scale first: halving a subnormal rate before multiplying by h loses
    // a representable integral. Reject overflow/unrepresentable products.
    let js = [h * j0, h * j1];
    let ls = [h * l0, h * l1];
    for (rate, integral) in [j0, j1, l0, l1].iter().zip([js[0], js[1], ls[0], ls[1]]) {
        if !integral.is_finite() || (*rate > 0. && integral == 0.) {
            return Err(NetworkError::InputOutsideDomain);
        }
    }
    let mean = |a: f64, b: f64| a.min(b) + (a.max(b) - a.min(b)) * 0.5;
    let born = mean(js[0], js[1]);
    let tau = mean(ls[0], ls[1]);
    if !born.is_finite() || !tau.is_finite() || !(old + born).is_finite() {
        return Err(NetworkError::NonFinite);
    }
    if j0 == j1 && l0 == l1 {
        let p = uniform_partition(old, born, tau)?;
        return Ok(AffinePartition {
            surviving: p.surviving,
            absorbed: p.absorbed,
            injected: born,
        });
    }
    // Variable quadrature has no subnormal-integral accuracy contract.
    if js
        .iter()
        .chain(ls.iter())
        .any(|x| *x > 0. && *x < f64::MIN_POSITIVE)
    {
        return Err(NetworkError::InputOutsideDomain);
    }
    if tau > 1. {
        return Err(NetworkError::InputOutsideDomain);
    }
    let p = uniform_partition(old, 0., tau)?;
    let mut surviving = p.surviving;
    let mut absorbed = p.absorbed;
    let d = 0.5 / 3f64.sqrt();
    for x in [0.5 - d, 0.5 + d] {
        let j = (1. - x) * js[0] + x * js[1];
        let l = (1. - x) * ls[0] + x * ls[1];
        let w = 0.5 * j;
        let tail = (1. - x) * mean(l, ls[1]);
        if !w.is_finite() || !tail.is_finite() {
            return Err(NetworkError::NonFinite);
        }
        surviving += w * (-tail).exp();
        absorbed += w * (-(-tail).exp_m1());
    }
    if [surviving, absorbed]
        .iter()
        .any(|x| !x.is_finite() || *x < 0.)
    {
        return Err(NetworkError::NonFinite);
    }
    let residual = (surviving + absorbed) - (old + born);
    if residual.abs() > 8. * f64::EPSILON * (old + born).max(f64::MIN_POSITIVE) {
        return Err(NetworkError::PhysicsLedger);
    }
    Ok(AffinePartition {
        surviving,
        absorbed,
        injected: born,
    })
}
