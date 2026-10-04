//! Pure-H, one-temperature REI consumer of the pinned REC Peebles reference.
//!
//! This separate research crate does not alter REI's Case-A H/He solver.
//! Proper densities use SI and all time derivatives are per proper second.
//! Standard collapsed and actual-ground retained source assemblies are distinct.
//! No thermal/photon-spectrum coupling or physical-history admission is implied.

use rec_microphysics::hydrogen_peebles as rec;
pub use rec::{ClosureDefect, HydrogenError, RetainedRhs, RetainedState};

pub const MODE_ID: &str = "PEEBLES_HYREC2_TLA_FUDGE1_ONE_T_SOURCE_V1";
pub const RETAINED_MODE_ID: &str = "PURE_H_RETAINED_N2_RESEARCH_V1";
pub const REC_COMMIT: &str = "cd68764aacfeae9fe794d7966604ac6fbb80ba7f";
pub const SOURCE_PROFILE: &str = rec::SOURCE_PROFILE;
pub const UPSTREAM_COMMIT: &str = rec::SOURCE_COMMIT;

fn positive(value: f64) -> Result<f64, HydrogenError> {
    if !value.is_finite() { return Err(HydrogenError::NonFinite); }
    if value <= 0.0 { return Err(HydrogenError::Domain); }
    Ok(value)
}

fn finite_output(value: f64) -> Result<f64, HydrogenError> {
    if value.is_finite() { Ok(value) } else { Err(HydrogenError::Overflow) }
}

/// Proper hydrogen-nuclei number density, never a comoving density.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct ProperHydrogenDensity(f64);
impl ProperHydrogenDensity {
    pub fn from_m3(value: f64) -> Result<Self, HydrogenError> {
        Ok(Self(positive(value)?))
    }
    /// Calls the source's cm^-3 -> m^-3 conversion exactly once.
    pub fn from_cm3(value: f64) -> Result<Self, HydrogenError> {
        Self::from_m3(rec::cm3_density_to_si(value)?)
    }
    pub fn m3(self) -> f64 { self.0 }
}

/// The adopted source requires exact equality of matter and radiation T.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct OneTemperature(f64);
impl OneTemperature {
    pub fn new(t_m_k: f64, t_r_k: f64) -> Result<Self, HydrogenError> {
        positive(t_m_k)?;
        positive(t_r_k)?;
        if t_m_k != t_r_k { return Err(HydrogenError::UnequalTemperatures); }
        Ok(Self(t_m_k))
    }
    pub fn kelvin(self) -> f64 { self.0 }
}

/// Positive H in inverse proper seconds; H=0 has no fallback source.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct ExpansionRate(f64);
impl ExpansionRate {
    pub fn per_second(value: f64) -> Result<Self, HydrogenError> {
        Ok(Self(positive(value)?))
    }
    pub fn value(self) -> f64 { self.0 }
}

#[derive(Debug, Clone, Copy)]
pub struct ReferenceInput {
    density: ProperHydrogenDensity,
    temperature: OneTemperature,
    expansion: ExpansionRate,
    state: RetainedState,
}
impl ReferenceInput {
    pub fn new(density: ProperHydrogenDensity, temperature: OneTemperature,
               expansion: ExpansionRate, state: RetainedState)
        -> Result<Self, HydrogenError> {
        if state.ground()? == 0.0 { return Err(HydrogenError::ZeroGroundSobolev); }
        Ok(Self { density, temperature, expansion, state })
    }
    pub fn from_si(t_m_k: f64, t_r_k: f64, n_h_m3: f64, hubble_s: f64,
                   xp: f64, x2: f64) -> Result<Self, HydrogenError> {
        Self::new(ProperHydrogenDensity::from_m3(n_h_m3)?,
                  OneTemperature::new(t_m_k, t_r_k)?,
                  ExpansionRate::per_second(hubble_s)?, RetainedState { xp, x2 })
    }
    pub fn from_cgs(t_m_k: f64, t_r_k: f64, n_h_cm3: f64, hubble_s: f64,
                    xp: f64, x2: f64) -> Result<Self, HydrogenError> {
        Self::new(ProperHydrogenDensity::from_cm3(n_h_cm3)?,
                  OneTemperature::new(t_m_k, t_r_k)?,
                  ExpansionRate::per_second(hubble_s)?, RetainedState { xp, x2 })
    }
    pub fn n_h_m3(self) -> f64 { self.density.m3() }
    pub fn temperature_k(self) -> f64 { self.temperature.kelvin() }
    pub fn hubble_s(self) -> f64 { self.expansion.value() }
    pub fn state(self) -> RetainedState { self.state }
}

#[derive(Debug, Clone, Copy)]
pub struct SourceValues {
    pub x1: f64,
    pub alpha_b_m3_s: f64,
    pub beta_p_s: f64,
    pub beta_shell_s: f64,
    pub r_alpha_s: f64,
    pub d_ground_s: f64,
    pub boltzmann_lya: f64,
    pub c_factor: f64,
}
fn source_values(point: rec::SourceBoundPoint, state: RetainedState)
    -> Result<SourceValues, HydrogenError> {
    Ok(SourceValues {
        x1: state.ground()?, alpha_b_m3_s: point.alpha_b_m3_s,
        beta_p_s: point.rates.beta_p_s(), beta_shell_s: point.rates.beta_shell_s(),
        r_alpha_s: point.r_alpha_s, d_ground_s: point.rates.d_ground_s(),
        boltzmann_lya: point.rates.boltzmann_lya(), c_factor: point.rates.c_factor(),
    })
}
fn assemble(input: ReferenceInput, state: RetainedState)
    -> Result<rec::SourceBoundPoint, HydrogenError> {
    rec::hyrec2_one_temperature_source(input.temperature_k(), input.temperature_k(),
        input.n_h_m3(), input.hubble_s(), state)
}

#[derive(Debug, Clone, Copy)]
pub struct CollapsedPoint {
    pub source: SourceValues,
    pub dxp_dt: f64,
}
/// The standard collapsed Peebles mode always assembles escape with x2=0.
/// Supplied x2 is validated by ReferenceInput but is excluded from this model.
pub fn evaluate_collapsed(input: ReferenceInput) -> Result<CollapsedPoint, HydrogenError> {
    let state = RetainedState { xp: input.state.xp, x2: 0.0 };
    let point = assemble(input, state)?;
    Ok(CollapsedPoint {
        source: source_values(point, state)?,
        dxp_dt: rec::peebles_rhs(input.n_h_m3(), point.alpha_b_m3_s,
                                 point.rates, state.xp)?,
    })
}

#[derive(Debug, Clone, Copy)]
pub struct RetainedPoint {
    pub source: SourceValues,
    pub rhs: RetainedRhs,
    /// Peebles RHS using the retained state's SAME instantaneous rates.
    pub same_rates_peebles_dt: f64,
    pub same_rates_closure_defect: ClosureDefect,
    /// Instantaneous target at the actual fixed x1, not a nonlinear root.
    pub qss_at_actual_fixed_ground: f64,
}
pub fn evaluate_retained(input: ReferenceInput) -> Result<RetainedPoint, HydrogenError> {
    let point = assemble(input, input.state)?;
    let x1 = input.state.ground()?;
    Ok(RetainedPoint {
        source: source_values(point, input.state)?,
        rhs: rec::retained_rhs(input.n_h_m3(), point.alpha_b_m3_s,
                              point.rates, input.state)?,
        same_rates_peebles_dt: rec::peebles_rhs(input.n_h_m3(), point.alpha_b_m3_s,
                                               point.rates, input.state.xp)?,
        same_rates_closure_defect: rec::closure_defect(input.n_h_m3(),
            point.alpha_b_m3_s, point.rates, input.state)?,
        qss_at_actual_fixed_ground: rec::qss_at_fixed_ground(input.n_h_m3(),
            point.alpha_b_m3_s, point.rates, input.state.xp, x1)?,
    })
}

#[derive(Debug, Clone, Copy)]
pub struct ReferencePoint {
    pub collapsed: CollapsedPoint,
    pub retained: RetainedPoint,
    /// Peebles(retained-source rates) - Peebles(collapsed-source rates).
    pub source_assembly_contribution: f64,
    /// Actual retained dxp/dt - standard collapsed Peebles dxp/dt.
    pub retained_minus_standard_collapsed: f64,
}
pub fn evaluate_reference(input: ReferenceInput) -> Result<ReferencePoint, HydrogenError> {
    let collapsed = evaluate_collapsed(input)?;
    let retained = evaluate_retained(input)?;
    Ok(ReferencePoint {
        source_assembly_contribution: finite_output(retained.same_rates_peebles_dt
                                                    - collapsed.dxp_dt)?,
        retained_minus_standard_collapsed: finite_output(retained.rhs.dxp_dt
                                                          - collapsed.dxp_dt)?,
        collapsed, retained,
    })
}

/// dx/dz=-dx/dt/[(1+z)H]; this is not d/dln(a).
pub fn collapsed_redshift_rhs(input: ReferenceInput, z: f64) -> Result<f64, HydrogenError> {
    rec::to_redshift_rhs(evaluate_collapsed(input)?.dxp_dt, z, input.hubble_s())
}
