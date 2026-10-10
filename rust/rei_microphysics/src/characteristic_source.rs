//! Opt-in fixed-covector continuous source stage. No chemistry/closure admission.
//!
//! Coefficients are frozen at a declared stage, not endpoint photon births. A
//! caller supplies actual characteristic energy/opacity and owns time refinement.
use crate::ForwardError;

#[derive(Clone, Copy, Debug)]
pub struct ContinuousPhotonStage {
    pub number: f64,
    pub source_per_s: f64,
    pub opacity_per_s: [f64; 3],
}

#[derive(Clone, Copy, Debug)]
pub struct ContinuousPhotonStep {
    pub number: f64,
    pub absorbed_by_species: [f64; 3],
    pub source_added: f64,
    pub integrated_number_s: f64,
}

pub fn continuous_photon_step(
    stage: ContinuousPhotonStage,
    dt_s: f64,
) -> Result<ContinuousPhotonStep, ForwardError> {
    if ![stage.number, stage.source_per_s, dt_s]
        .into_iter().chain(stage.opacity_per_s)
        .all(|v| v.is_finite() && v >= 0.) {
        return Err(ForwardError::InvalidInput("CONTINUOUS_PHOTON_DOMAIN"));
    }
    let x = stage.opacity_per_s.iter().sum::<f64>() * dt_s;
    if !x.is_finite() {
        return Err(ForwardError::InvalidInput("CONTINUOUS_PHOTON_OVERFLOW"));
    }
    let (phi1, phi2) = if x < 1e-3 {
        (1. + x*(-0.5 + x*(1./6. + x*(-1./24. + x*(1./120. - x/720.)))),
         0.5 + x*(-1./6. + x*(1./24. + x*(-1./120. + x*(1./720. - x/5040.)))))
    } else {
        let phi1 = -(-x).exp_m1()/x;
        (phi1, (1.-phi1)/x)
    };
    let source_added = stage.source_per_s * dt_s;
    let number = (-x).exp()*stage.number + source_added*phi1;
    let integrated_number_s = dt_s*(stage.number*phi1 + source_added*phi2);
    let absorbed_by_species = stage.opacity_per_s.map(|k| k*integrated_number_s);
    if ![number, source_added, integrated_number_s]
        .into_iter().chain(absorbed_by_species)
        .all(|v| v.is_finite() && v >= 0.) {
        return Err(ForwardError::InvalidInput("CONTINUOUS_PHOTON_RESULT"));
    }
    Ok(ContinuousPhotonStep {number, absorbed_by_species, source_added, integrated_number_s})
}
