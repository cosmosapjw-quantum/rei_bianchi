//! Optional immutable IGM + RCT point composition. No dispatcher or integrator.
//!
//! The baseline owns EOS, photo, RR/DR/CI/CE, free-free, CMB and expansion.
//! The existing RCT provider owns its rate, domain, scenario and explicit
//! escaped-photon mean. Uncomputed atomic spectral moments remain uncomputed.
use rei_microphysics::{
    he_rct::{ClosedRctLedger, RctSelection},
    igm_state::IgmGasState,
    igm_thermal::{igm_point_rhs, IgmPhotoInput, IgmPointRhs},
    ForwardError, HHeModel, HHeState,
};

#[derive(Clone, Copy, Debug)]
pub struct ComposedPoint {
    pub baseline: IgmPointRhs,
    pub combined: IgmPointRhs,
    /// Separate ledger. Never stored in electron-recombination or photo events.
    pub rct: Option<ClosedRctLedger>,
    /// Keep small corrections explicit rather than recover them by subtraction.
    pub delta_w_dt_erg_per_h_s: f64,
    pub delta_temperature_dt_k_s: f64,
}
fn arithmetic() -> ForwardError {
    ForwardError::InvalidInput("IGM_RCT_COMPOSITION_ARITHMETIC")
}
fn finite(x: f64) -> Result<f64, ForwardError> {
    if x == 0.0 || x.is_normal() {
        Ok(x)
    } else {
        Err(arithmetic())
    }
}
fn product(xs: &[f64]) -> Result<f64, ForwardError> {
    for &x in xs {
        finite(x)?;
        if x < 0.0 {
            return Err(arithmetic());
        }
    }
    if xs.contains(&0.0) {
        return Ok(0.0);
    }
    let mut p = 1.0;
    for &x in xs {
        p *= x;
        if !p.is_normal() {
            return Err(arithmetic());
        }
    }
    Ok(p)
}
fn divide(x: f64, y: f64) -> Result<f64, ForwardError> {
    finite(x)?;
    if !y.is_normal() || y <= 0.0 {
        return Err(arithmetic());
    }
    let out = finite(x / y)?;
    if x != 0.0 && out == 0.0 {
        return Err(arithmetic());
    }
    Ok(out)
}

/// Compose a point, not a step. `h` is the baseline expansion rate in s^-1.
/// OFF delegates exactly, without evaluating any RCT coefficient or closure.
/// Temperature admission uses the actual recovered EOS, not a requested T.
/// All input references are immutable. Positive subnormal/underflowing RCT
/// products are rejected to preserve the IGM point evaluator's arithmetic policy.
#[allow(clippy::too_many_arguments)]
pub fn point(
    state: &IgmGasState,
    nh: f64,
    nhe: f64,
    h: f64,
    tcmb: f64,
    photo: IgmPhotoInput,
    selection: RctSelection,
) -> Result<ComposedPoint, ForwardError> {
    let baseline = igm_point_rhs(state, nh, nhe, h, tcmb, photo)?;
    let (provider, closure) = match selection {
        RctSelection::Disabled => {
            return Ok(ComposedPoint {
                baseline,
                combined: baseline,
                rct: None,
                delta_w_dt_erg_per_h_s: 0.0,
                delta_temperature_dt_k_s: 0.0,
            })
        }
        RctSelection::Escaping { provider, closure } => (provider, closure),
    };
    let eos = state.eos(nh, nhe)?;
    let mut model = HHeModel::controlled_fixture();
    model.n_h_cm3 = nh;
    model.n_he_cm3 = nhe;
    let hhe = HHeState {
        fractions: state.fractions,
        u_erg_cm3: eos.u_erg_cm3,
        photon_cm3: [0.0; 3],
        escaped_erg_cm3: 0.0,
    };
    // No synthetic HHe rates are evaluated here. Only the existing RCT
    // provider's coefficient + ledger and the common HHe EOS/constants are used.
    let k = provider.coefficient_cm3_s(eos.temperature_k)?;
    let hi = product(&[nh, 1.0 - state.fractions[0]])?;
    let heiii = product(&[nhe, state.fractions[2]])?;
    let rate = product(&[k, hi, heiii])?;
    let q = finite(model.threshold_ev[2] - model.threshold_ev[0])?;
    let g = finite(q - closure.mean_ev())?;
    product(&[q, model.ev_erg, rate])?;
    product(&[g.abs(), model.ev_erg, rate])?;
    product(&[closure.mean_ev(), model.ev_erg, rate])?;
    let rct = provider.closed_events(&model, &hhe, closure)?;
    if rct.event.temperature_k.to_bits() != eos.temperature_k.to_bits()
        || rct.event.event_rate_cm3_s.to_bits() != rate.to_bits()
    {
        return Err(ForwardError::InvalidInput("IGM_RCT_EOS_OR_EVENT_IDENTITY"));
    }
    for value in rct.event.fraction_rate_s {
        finite(value)?;
    }
    let dw = divide(rct.thermal_energy_rate_erg_cm3_s, nh)?;
    // Direct RCT creates no electron and conserves total particle number.
    // The existing baseline variable-particle term is therefore unchanged.
    let particles = finite(nh + nhe + eos.electron_density_cm3)?;
    let denominator = product(&[3.0, model.kb_erg_k, particles])?;
    let dt = divide(2.0 * rct.thermal_energy_rate_erg_cm3_s, denominator)?;
    let mut combined = baseline;
    for i in 0..3 {
        combined.fraction_dt[i] = finite(combined.fraction_dt[i] + rct.event.fraction_rate_s[i])?;
    }
    // Direct electron rate is zero. Preserve its exact baseline bit pattern.
    for i in 0..5 {
        combined.species_chemical_cm3_s[i] =
            finite(combined.species_chemical_cm3_s[i] + rct.event.species_rate_cm3_s[i])?;
    }
    combined.thermal_micro_erg_cm3_s =
        finite(combined.thermal_micro_erg_cm3_s + rct.thermal_energy_rate_erg_cm3_s)?;
    combined.binding_micro_erg_cm3_s =
        finite(combined.binding_micro_erg_cm3_s + rct.event.chemical_energy_rate_erg_cm3_s)?;
    combined.escape_erg_cm3_s =
        finite(combined.escape_erg_cm3_s + rct.escaped_energy_rate_erg_cm3_s)?;
    combined.w_dt_erg_per_h_s = finite(combined.w_dt_erg_per_h_s + dw)?;
    combined.temperature_dt_k_s = finite(combined.temperature_dt_k_s + dt)?;
    Ok(ComposedPoint {
        baseline,
        combined,
        rct: Some(rct),
        delta_w_dt_erg_per_h_s: dw,
        delta_temperature_dt_k_s: dt,
    })
}

#[cfg(test)]
mod arithmetic_tests {
    use super::*;
    #[test]
    fn product_rejects_underflow_and_subnormal() {
        assert!(product(&[1e-200, 1e-200]).is_err());
        assert!(product(&[f64::MIN_POSITIVE, 0.5]).is_err());
        assert!(product(&[f64::INFINITY, 0.0]).is_err());
        assert_eq!(product(&[1e-200, 0.0]).unwrap(), 0.0);
    }
    #[test]
    fn division_rejects_unrepresentable_nonzero() {
        assert!(divide(f64::MIN_POSITIVE, 2.0).is_err());
        assert!(divide(1.0, 0.0).is_err());
        assert_eq!(divide(0.0, 2.0).unwrap(), 0.0);
    }
}
