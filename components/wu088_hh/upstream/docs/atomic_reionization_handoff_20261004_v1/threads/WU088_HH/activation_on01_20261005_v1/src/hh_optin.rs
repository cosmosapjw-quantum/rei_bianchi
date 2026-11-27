//! Experimental opt-in HH source for the typed, static FT03 consumer.
//!
//! This is a provider/RHS/residual adapter, NOT an HH time integrator. The
//! inherited source files and S0 scenario are untouched. The declared
//! 35_000..=60_000 K research window excludes the raw k57 3000 K floor.
//! Source identities and non-physical uncertainty status: ACTIVATION_CONTRACT.json.
use crate::{ft03_rhs, ForwardError, Ft03Model, Ft03Rhs, HHeState};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum HhProvider {
    /// Grackle 3.4.1 k57 analytic branch, Lenzuni et al. prescription.
    Lcs91,
    /// Glover (2015), Eq. 14, corrected Kunc-Soon prescription.
    CorrectedKs,
}
#[derive(Clone, Copy, Debug, Default)]
pub enum HhSelection {
    #[default]
    Disabled,
    Research(HhProvider),
}
#[derive(Clone, Copy, Debug)]
pub struct RateJet {
    pub k_cm3_s: f64,
    pub k_m3_s: f64,
    /// Temperature derivative in cm^3 s^-1 K^-1.
    pub d1: f64,
    /// Second temperature derivative in cm^3 s^-1 K^-2.
    pub d2: f64,
}
#[derive(Clone, Copy, Debug)]
pub struct HhLedger {
    pub rate: RateJet,
    /// q = R/nH, evaluated without division by nH or ne.
    pub per_h_s: f64,
    pub events_cm3_s: f64,
    pub thermal_erg_cm3_s: f64,
    pub binding_erg_cm3_s: f64,
}
#[derive(Clone, Copy, Debug)]
pub struct CombinedHhRhs {
    pub baseline: Ft03Rhs,
    pub combined: Ft03Rhs,
    /// HH events never overwrite the baseline electron-CI or RR counters.
    pub hh: Option<HhLedger>,
}
#[derive(Clone, Copy, Debug)]
pub struct HhEndpoint {
    pub rhs: CombinedHhRhs,
    pub residual: [f64; 7],
    pub escaped_residual: f64,
    pub hh_events_cm3: f64,
    pub hh_per_h: f64,
    pub hh_heat_erg_cm3: f64,
}

fn temperature_domain(t: f64) -> Result<(), ForwardError> {
    if !t.is_finite() || !(35_000.0..=60_000.0).contains(&t) {
        return Err(ForwardError::InvalidInput("HH_TEMPERATURE_DOMAIN"));
    }
    Ok(())
}

// A true zero factor is not an underflow. No arbitrary density floor is used.
fn product(factors: &[f64]) -> Result<f64, ForwardError> {
    if factors.iter().any(|v| !v.is_finite()) {
        return Err(ForwardError::InvalidInput("HH_NONFINITE"));
    }
    if factors.contains(&0.0) {
        return Ok(0.0);
    }
    let r = factors.iter().product::<f64>();
    if !r.is_finite() {
        return Err(ForwardError::InvalidInput("HH_NONFINITE"));
    }
    if r == 0.0 {
        return Err(ForwardError::InvalidInput("HH_PRODUCT_UNDERFLOW"));
    }
    Ok(r)
}

impl HhProvider {
    pub fn rate(self, t: f64) -> Result<RateJet, ForwardError> {
        temperature_domain(t)?;
        let (a, p) = match self {
            Self::Lcs91 => (1.2e-17, 1.2),
            Self::CorrectedKs => (4.65e-21, 1.5),
        };
        let b = 157_800.0;
        let k = product(&[a, t.powf(p), (-b / t).exp()])?;
        let inv = 1.0 / t;
        let d1 = product(&[k, p * inv + b * inv * inv])?;
        // Positive form of k'' avoids subtracting two nearly equal terms.
        let d2 = product(&[
            k,
            p * (p - 1.0) * inv.powi(2)
                + 2.0 * b * (p - 1.0) * inv.powi(3)
                + b * b * inv.powi(4),
        ])?;
        Ok(RateJet { k_cm3_s: k, k_m3_s: product(&[k, 1e-6])?, d1, d2 })
    }
}

/// HI+HI -> HI+HII+e, with R=k*nHI^2 in the inherited network convention.
/// Chi is a positive binding energy supplied by the consumer, not kB*157800.
/// Computational zero-density support is not additional physical admission.
pub fn events(p: HhProvider, t: f64, nh: f64, h: f64, chi: f64)
    -> Result<HhLedger, ForwardError>
{
    if !nh.is_finite() || nh < 0.0 || !h.is_finite() || !(0.0..=1.0).contains(&h)
        || !chi.is_finite() || chi <= 0.0
    {
        return Err(ForwardError::InvalidInput("HH_EVENT_DOMAIN"));
    }
    let rate = p.rate(t)?;
    let w = 1.0 - h;
    let q = product(&[nh, w, w, rate.k_cm3_s])?;
    let r = product(&[nh, q])?;
    let binding = product(&[chi, r])?;
    Ok(HhLedger { rate, per_h_s: q, events_cm3_s: r,
        thermal_erg_cm3_s: -binding, binding_erg_cm3_s: binding })
}

/// Preserve the actual FT03 RR/CI/DR/PI and escape inventories.
/// Disabled does not evaluate an HH rate or apply the HH temperature guard.
/// No provider loading/dispatch claim is made about an unconnected full history.
pub fn combined_ft03_rhs(model: &Ft03Model, state: &HHeState, selection: HhSelection)
    -> Result<CombinedHhRhs, ForwardError>
{
    let baseline = ft03_rhs(model, state)?;
    let p = match selection {
        HhSelection::Disabled => return Ok(CombinedHhRhs {
            baseline, combined: baseline, hh: None }),
        HhSelection::Research(p) => p,
    };
    let g = &model.gas;
    let chi = product(&[g.threshold_ev[0], g.ev_erg])?;
    let hh = events(p, g.temperature(state)?, g.n_h_cm3, state.fractions[0], chi)?;
    let mut combined = baseline;
    combined.derivative[0] += hh.per_h_s;
    combined.derivative[3] += hh.thermal_erg_cm3_s;
    if combined.derivative.iter().any(|v| !v.is_finite()) {
        return Err(ForwardError::InvalidInput("HH_NONFINITE"));
    }
    Ok(CombinedHhRhs { baseline, combined, hh: Some(hh) })
}

/// Assemble a BE residual at a SUPPLIED endpoint, with that endpoint's events.
/// This does not solve for, accept, or advance a state; all arguments are borrowed.
/// Different half endpoints require separate calls; no final-endpoint shortcut.
pub fn endpoint(model: &Ft03Model, old: &HHeState, new: &HHeState,
                dt: f64, selection: HhSelection) -> Result<HhEndpoint, ForwardError>
{
    if !dt.is_finite() || dt < 0.0 {
        return Err(ForwardError::InvalidInput("HH_STEP_DOMAIN"));
    }
    let old_t = model.gas.temperature(old)?;
    if let HhSelection::Research(_) = selection { temperature_domain(old_t)?; }
    let rhs = combined_ft03_rhs(model, new, selection)?;
    let x0 = old.coordinates();
    let x1 = new.coordinates();
    let mut residual = [0.0; 7];
    for i in 0..7 {
        residual[i] = x1[i] - x0[i] - product(&[dt, rhs.combined.derivative[i]])?;
    }
    let escaped_residual = new.escaped_erg_cm3 - old.escaped_erg_cm3
        - product(&[dt, rhs.combined.escaped_energy_rate])?;
    if residual.iter().any(|v| !v.is_finite()) || !escaped_residual.is_finite() {
        return Err(ForwardError::InvalidInput("HH_NONFINITE"));
    }
    let (r,q,heat) = match rhs.hh {
        Some(hh) => (product(&[dt,hh.events_cm3_s])?, product(&[dt,hh.per_h_s])?,
                     product(&[dt,hh.thermal_erg_cm3_s])?),
        None => (0.0,0.0,0.0),
    };
    Ok(HhEndpoint { rhs, residual, escaped_residual,
        hh_events_cm3:r, hh_per_h:q, hh_heat_erg_cm3:heat })
}
