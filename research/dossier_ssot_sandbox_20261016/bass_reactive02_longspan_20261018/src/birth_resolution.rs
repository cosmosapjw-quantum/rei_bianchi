//! Frozen-coefficient diagnostics for the inherited positive birth quadrature.
//! No change to native photon/chemistry steps. Passing is not a coupled error bound.
use crate::bound_source_age::SourceAgeBridge;
use crate::full_network::{NetworkConfig, NetworkError};
use crate::mixture_eos::MixtureState;
use crate::positive_spectral::{SpectralMode, expand_births};
use crate::retarded_transport::gauss_birth_nodes;
#[derive(Debug)]
pub struct BirthAudit {
    pub exact: f64,
    pub sampled: f64,
    pub relative_defect: f64,
    pub youngest_optical_age: f64,
    pub within_tolerance: bool,
}
/// Dimensionless tau=kappa[s^-1]*dt[s]. Exact constant-source newborn fraction.
/// Unlike 1-(1-phi), direct expm1/tau does not cancel its optically thick tail.
pub fn frozen_birth(tau: f64, nodes: usize, rtol: f64) -> Result<BirthAudit, NetworkError> {
    if !tau.is_finite() || tau < 0. || !rtol.is_finite() || rtol <= 0. || rtol >= 1. {
        return Err(NetworkError::InvalidInput);
    }
    let gl = gauss_birth_nodes(nodes)?;
    let exact = if tau == 0. {
        1.
    } else {
        -(-tau).exp_m1() / tau
    };
    let sampled = gl
        .iter()
        .map(|(u, w)| w * (-tau * (1. - u)).exp())
        .sum::<f64>();
    let relative_defect = (sampled / exact - 1.).abs();
    let youngest_optical_age = gl
        .iter()
        .map(|(u, _)| tau * (1. - u))
        .fold(f64::INFINITY, f64::min);
    if ![exact, sampled, relative_defect, youngest_optical_age]
        .iter()
        .all(|x| x.is_finite())
        || exact <= 0.
    {
        return Err(NetworkError::NonFinite);
    }
    Ok(BirthAudit {
        exact,
        sampled,
        relative_defect,
        youngest_optical_age,
        within_tolerance: relative_defect <= rtol,
    })
}
#[derive(Debug, Default)]
pub struct FrozenNative {
    pub emitted: f64,
    pub exact_survivors: f64,
    pub sampled_survivors: f64,
    pub exact_events: [f64; 4],
    pub sampled_events: [f64; 4],
    pub max_tau: f64,
    pub min_positive_tau: f64,
}
/// Static photon-only oracle: initial source and absorber densities held fixed;
/// no redshift, no chemistry, no thermal feedback. Original atomic owners called.
/// Birth/survival are integrated analytically over repeated equal time intervals.
pub fn native_frozen(
    bridge: &SourceAgeBridge,
    conf: &NetworkConfig,
    gas: &MixtureState,
    duration: f64,
    steps: usize,
    birth_nodes: usize,
    spectrum: SpectralMode,
) -> Result<FrozenNative, NetworkError> {
    if !duration.is_finite() || duration <= 0. || steps == 0 || steps > 1_000_000 {
        return Err(NetworkError::InvalidInput);
    }
    let raw = bridge.source_births(0., 1.)?;
    let cells = expand_births(&bridge.source, &raw, conf.deuterium.chi_d_ev(), spectrum)?;
    let dt = duration / steps as f64;
    let mut out = FrozenNative {
        min_positive_tau: f64::INFINITY,
        ..FrozenNative::default()
    };
    for co in cells {
        let rates = bridge.opacity_channels(co.energy_at_birth_ev, gas, conf)?;
        let k = rates.iter().sum::<f64>();
        let tau = k * dt;
        let a = frozen_birth(tau, birth_nodes, 0.001)?;
        let whole = frozen_birth(k * duration, birth_nodes, 0.001)?;
        let emitted = co.n_comoving_m3 * duration;
        let exact = emitted * whole.exact;
        // Geometric accumulation of each step's sampled births. Equivalent to
        // repeated N<-exp(-tau)*N+j*dt*Q; ratio Q/phi cancels the same old decay.
        let sampled = exact * (a.sampled / a.exact);
        out.emitted += emitted;
        out.exact_survivors += exact;
        out.sampled_survivors += sampled;
        out.max_tau = out.max_tau.max(tau);
        if k > 0. {
            out.min_positive_tau = out.min_positive_tau.min(tau);
            for (i, rate) in rates.iter().enumerate() {
                out.exact_events[i] += (emitted - exact) * rate / k;
                out.sampled_events[i] += (emitted - sampled) * rate / k;
            }
        }
    }
    Ok(out)
}
