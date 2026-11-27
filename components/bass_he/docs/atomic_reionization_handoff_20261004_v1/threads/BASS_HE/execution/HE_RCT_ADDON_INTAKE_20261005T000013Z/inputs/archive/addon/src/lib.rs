//! Experimental static FT03/RCT add-on using an unchanged pinned dependency.
//! No production dispatcher is patched. Constant source and fixed escape closure
//! are frozen for each attempt. Counts use proper cm^-3, energies erg cm^-3.
#![forbid(unsafe_code)]
use rei_microphysics::he_rct::{
    combined_ft03_rhs, ClosedRctLedger, EscapingMeanPhotonEnergy, RctProvider, RctSelection,
};
use rei_microphysics::{
    ft03_adaptive_step, ft03_coefficients, ft03_implicit_step, ForwardError, Ft03Events, Ft03Model,
    Ft03Rhs, HHeState, StepControl,
};
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct RctIntegral {
    /// Equal emitted and escaped photon counts in the declared escape model.
    pub events: f64,
    pub heat: f64,
    pub escaped: f64,
    pub chemical: f64,
}
impl RctIntegral {
    fn valid(self) -> bool {
        self.events.is_finite()
            && self.events >= 0.
            && self.escaped.is_finite()
            && self.escaped >= 0.
            && self.heat.is_finite()
            && self.chemical.is_finite()
    }
    fn plus(self, b: Self) -> Result<Self, ForwardError> {
        if !self.valid() || !b.valid() {
            return Err(err("RCT_ACCUMULATOR_DOMAIN"));
        }
        let r = Self {
            events: self.events + b.events,
            heat: self.heat + b.heat,
            escaped: self.escaped + b.escaped,
            chemical: self.chemical + b.chemical,
        };
        if !r.valid() {
            return Err(err("RCT_OVERFLOW"));
        }
        Ok(r)
    }
}
/// Additional full/half event estimator, not a rigorous exact-flow bound.
/// No defaults: the caller must explicitly state both parts of its error budget.
#[derive(Clone, Copy, Debug)]
pub struct EventControl {
    pub absolute_per_h: f64,
    pub relative: f64,
}
impl EventControl {
    fn validate(self) -> Result<(), ForwardError> {
        if !self.absolute_per_h.is_finite()
            || self.absolute_per_h < 0.
            || !self.relative.is_finite()
            || self.relative < 0.
            || (self.absolute_per_h == 0. && self.relative == 0.)
        {
            return Err(err("RCT_EVENT_CONTROL"));
        }
        Ok(())
    }
}
#[derive(Clone, Copy, Debug)]
pub struct RctStep {
    pub state: HHeState,
    pub baseline_events: Ft03Events,
    /// None is OFF/not evaluated, not a measured physical zero.
    pub rct: Option<RctIntegral>,
    pub iterations: usize,
    pub residual_norm: f64,
    pub local_error: f64,
    pub event_error_per_h: f64,
}
fn err(code: &'static str) -> ForwardError {
    ForwardError::InvalidInput(code)
}
fn product(xs: &[f64]) -> Result<f64, ForwardError> {
    if xs.iter().any(|v| !v.is_finite()) {
        return Err(err("RCT_OVERFLOW"));
    }
    if xs.contains(&0.) {
        return Ok(0.);
    }
    let p = xs.iter().product::<f64>();
    if !p.is_finite() {
        return Err(err("RCT_OVERFLOW"));
    }
    if p == 0. {
        return Err(err("RCT_PRODUCT_UNDERFLOW"));
    }
    Ok(p)
}
/// Guard the original provider's rate/energy products without replacing them.
/// This rejects zero from nonzero factors, not every subnormal rounding loss.
pub fn checked_rct_events(
    m: &Ft03Model,
    s: &HHeState,
    p: RctProvider,
    e: EscapingMeanPhotonEnergy,
) -> Result<ClosedRctLedger, ForwardError> {
    let out = p.closed_events(&m.gas, s, e)?;
    let hi = product(&[m.gas.n_h_cm3, 1. - s.fractions[0]])?;
    let he = product(&[m.gas.n_he_cm3, s.fractions[2]])?;
    let k = p.coefficient_cm3_s(out.event.temperature_k)?;
    let r = product(&[k, hi, he])?;
    product(&[out.event.q_ev, m.gas.ev_erg, r])?;
    product(&[out.event.q_ev - e.mean_ev(), m.gas.ev_erg, r])?;
    product(&[e.mean_ev(), m.gas.ev_erg, r])?;
    if r > 0. && (out.event.fraction_rate_s[0] == 0. || out.event.fraction_rate_s[1] == 0.) {
        return Err(err("RCT_PRODUCT_UNDERFLOW"));
    }
    Ok(out)
}
fn coords(s: &HHeState) -> [f64; 7] {
    [
        s.fractions[0],
        s.fractions[1],
        s.fractions[2],
        s.u_erg_cm3,
        s.photon_cm3[0],
        s.photon_cm3[1],
        s.photon_cm3[2],
    ]
}
fn events(rhs: &Ft03Rhs, dt: f64) -> Result<Ft03Events, ForwardError> {
    let mut e = Ft03Events::default();
    for a in 0..3 {
        e.collision_per_cm3[a] = product(&[dt, rhs.collision_per_cm3_s[a]])?;
        e.recombination_per_cm3[a] = product(&[dt, rhs.recombination_per_cm3_s[a]])?;
        for g in 0..3 {
            e.photo_per_cm3[a][g] = product(&[dt, rhs.photo_per_cm3_s[a][g]])?;
        }
    }
    for j in 0..2 {
        e.dr_per_cm3[j] = product(&[dt, rhs.dr_per_cm3_s[j]])?;
    }
    Ok(e)
}
fn plus_events(a: Ft03Events, b: Ft03Events) -> Result<Ft03Events, ForwardError> {
    let mut c = a;
    for s in 0..3 {
        c.collision_per_cm3[s] += b.collision_per_cm3[s];
        c.recombination_per_cm3[s] += b.recombination_per_cm3[s];
        for g in 0..3 {
            c.photo_per_cm3[s][g] += b.photo_per_cm3[s][g];
        }
    }
    for j in 0..2 {
        c.dr_per_cm3[j] += b.dr_per_cm3[j];
    }
    if c.photo_per_cm3
        .iter()
        .flatten()
        .chain(c.collision_per_cm3.iter())
        .chain(c.recombination_per_cm3.iter())
        .chain(c.dr_per_cm3.iter())
        .any(|v| !v.is_finite() || *v < 0.)
    {
        return Err(err("RCT_OVERFLOW"));
    }
    Ok(c)
}
fn integrate_rct(r: ClosedRctLedger, dt: f64) -> Result<RctIntegral, ForwardError> {
    Ok(RctIntegral {
        events: product(&[dt, r.event.event_rate_cm3_s])?,
        heat: product(&[dt, r.thermal_energy_rate_erg_cm3_s])?,
        escaped: product(&[dt, r.escaped_energy_rate_erg_cm3_s])?,
        chemical: product(&[dt, r.event.chemical_energy_rate_erg_cm3_s])?,
    })
}
fn residual(
    m: &Ft03Model,
    old: &HHeState,
    new: &HHeState,
    dt: f64,
    sel: RctSelection,
) -> Result<(f64, Ft03Events, RctIntegral), ForwardError> {
    let (p, e) = match sel {
        RctSelection::Escaping { provider, closure } => (provider, closure),
        _ => return Err(err("RCT_INTERNAL_SELECTION")),
    };
    let rct = checked_rct_events(m, new, p, e)?;
    let q = combined_ft03_rhs(m, new, sel)?;
    let a = coords(old);
    let b = coords(new);
    let scale = [
        1.,
        1.,
        1.,
        old.u_erg_cm3.max(1e-30),
        old.photon_cm3[0].max(1e-30),
        old.photon_cm3[1].max(1e-30),
        old.photon_cm3[2].max(1e-30),
    ];
    let mut norm = 0_f64;
    for j in 0..7 {
        norm = norm.max(((b[j] - a[j] - dt * q.combined.derivative[j]) / scale[j]).abs());
    }
    norm = norm.max(
        ((new.escaped_erg_cm3 - old.escaped_erg_cm3 - dt * q.combined.escaped_energy_rate)
            / m.gas.total_energy(old)?.max(1e-30))
        .abs(),
    );
    if !norm.is_finite() {
        return Err(err("RCT_OVERFLOW"));
    }
    Ok((norm, events(&q.baseline, dt)?, integrate_rct(rct, dt)?))
}
fn invariants(
    m: &Ft03Model,
    old: &HHeState,
    new: &HHeState,
    b: &Ft03Events,
    r: RctIntegral,
    tol: f64,
) -> Result<(), ForwardError> {
    let g = &m.gas;
    let en = g.total_energy(old)?;
    let mut norm = ((g.total_energy(new)? - en) / en.max(1e-30)).abs();
    let mut j = [0.; 3];
    for (s, val) in j.iter_mut().enumerate() {
        *val = b.photo_per_cm3[s].iter().sum::<f64>() + b.collision_per_cm3[s]
            - b.recombination_per_cm3[s];
    }
    j[1] -= b.dr_per_cm3.iter().sum::<f64>();
    let dx = new.fractions[0] - old.fractions[0];
    let dy = new.fractions[1] - old.fractions[1];
    let dz = new.fractions[2] - old.fractions[2];
    norm = norm.max(((g.n_h_cm3 * dx - j[0] - r.events) / g.n_h_cm3).abs());
    norm = norm.max(((g.n_he_cm3 * dy - j[1] + j[2] - r.events) / g.n_he_cm3).abs());
    norm = norm.max(((g.n_he_cm3 * dz - j[2] + r.events) / g.n_he_cm3).abs());
    for p in 0..3 {
        norm = norm.max(
            ((old.photon_cm3[p]
                - new.photon_cm3[p]
                - (0..3).map(|a| b.photo_per_cm3[a][p]).sum::<f64>())
                / old.photon_cm3[p].max(1e-30))
            .abs(),
        );
    }
    if !norm.is_finite() || norm > tol.max(1e-13) * 8. {
        return Err(err("RCT_INVARIANT_RESIDUAL"));
    }
    Ok(())
}
/// Positive frozen-coefficient species update used by the actual iteration.
/// k*nH and k*nHe have inverse-second units; no electron factor multiplies RCT.
fn species_block(
    old: [f64; 3],
    guess: [f64; 3],
    ion: [f64; 3],
    rr: [f64; 3],
    dr: f64,
    k_nh: f64,
    k_nhe: f64,
    dt: f64,
) -> [f64; 3] {
    let ih = ion[0] + k_nhe * guess[2];
    let x = (old[0] + dt * ih) / (1. + dt * (ih + rr[0]));
    let a = dt * ion[1];
    let b = dt * (rr[1] + dr);
    let c = dt * ion[2];
    let d = dt * (rr[2] + k_nh * (1. - guess[0]));
    let y = (old[1] + (1. - (old[1] + old[2])) * (a / (1. + a)) + old[2] * (d / (1. + d)))
        / (1. + b / (1. + a) + c / (1. + d));
    let z = (old[2] + c * y) / (1. + d);
    [x, y, z]
}
/// Proposed opt-in static implicit step. The original FT03 code is unchanged.
pub fn implicit_step(
    m: &Ft03Model,
    old: &HHeState,
    dt: f64,
    c: StepControl,
    sel: RctSelection,
) -> Result<RctStep, ForwardError> {
    let (p, e) = match sel {
        RctSelection::Disabled => {
            let s = ft03_implicit_step(m, old, dt, c)?;
            return Ok(RctStep {
                state: s.state,
                baseline_events: s.events,
                rct: None,
                iterations: s.iterations,
                residual_norm: s.residual_norm,
                local_error: s.local_error,
                event_error_per_h: 0.,
            });
        }
        RctSelection::Escaping { provider, closure } => (provider, closure),
    };
    checked_rct_events(m, old, p, e)?;
    combined_ft03_rhs(m, old, sel)?;
    if !dt.is_finite()
        || dt < 0.
        || c.max_iterations == 0
        || !c.residual_tolerance.is_finite()
        || c.residual_tolerance <= 0.
    {
        return Err(err("RCT_STEP_CONTROL"));
    }
    if dt == 0. {
        return Ok(RctStep {
            state: *old,
            baseline_events: Ft03Events::default(),
            rct: Some(RctIntegral::default()),
            iterations: 0,
            residual_norm: 0.,
            local_error: 0.,
            event_error_per_h: 0.,
        });
    }
    let g = &m.gas;
    let mut guess = *old;
    for it in 1..=c.max_iterations {
        checked_rct_events(m, &guess, p, e)?;
        let ne = g.electron_density(&guess)?;
        let t = g.temperature(&guess)?;
        let rates = ft03_coefficients(t)?;
        let k = p.coefficient_cm3_s(t)?;
        let lower = [
            g.n_h_cm3 * (1. - guess.fractions[0]),
            g.n_he_cm3 * (1. - (guess.fractions[1] + guess.fractions[2])),
            g.n_he_cm3 * guess.fractions[1],
        ];
        let mut next = guess;
        for a in 0..3 {
            let opacity = (0..3).map(|s| lower[s] * g.sigma_cm2[s][a]).sum::<f64>();
            next.photon_cm3[a] = old.photon_cm3[a] / (1. + dt * g.c_cm_s * opacity);
        }
        let ion = std::array::from_fn(|a| {
            (0..3)
                .map(|j| g.c_cm_s * g.sigma_cm2[a][j] * next.photon_cm3[j])
                .sum::<f64>()
                + ne * rates.beta_ci_cm3_s[a]
        });
        let rr = std::array::from_fn(|a| ne * rates.alpha_rr_cm3_s[a]);
        let dr = ne * rates.alpha_dr_cm3_s.iter().sum::<f64>();
        next.fractions = species_block(
            old.fractions,
            guess.fractions,
            ion,
            rr,
            dr,
            product(&[k, g.n_h_cm3])?,
            product(&[k, g.n_he_cm3])?,
            dt,
        );
        checked_rct_events(m, &next, p, e)?;
        let q = combined_ft03_rhs(m, &next, sel)?;
        next.u_erg_cm3 = old.u_erg_cm3 + dt * q.combined.derivative[3];
        next.escaped_erg_cm3 = old.escaped_erg_cm3 + dt * q.combined.escaped_energy_rate;
        let (norm, bev, rev) = residual(m, old, &next, dt, sel)?;
        if norm < c.residual_tolerance {
            invariants(m, old, &next, &bev, rev, c.residual_tolerance)?;
            return Ok(RctStep {
                state: next,
                baseline_events: bev,
                rct: Some(rev),
                iterations: it,
                residual_norm: norm,
                local_error: 0.,
                event_error_per_h: 0.,
            });
        }
        guess = next;
    }
    Err(err("RCT_NONCONVERGENCE"))
}
/// Accept the two half-steps only. Full-step events are used only as an estimator.
pub fn adaptive_step(
    m: &Ft03Model,
    old: &HHeState,
    dt: f64,
    c: StepControl,
    sel: RctSelection,
    ec: EventControl,
) -> Result<RctStep, ForwardError> {
    if let RctSelection::Disabled = sel {
        let s = ft03_adaptive_step(m, old, dt, c)?;
        return Ok(RctStep {
            state: s.state,
            baseline_events: s.events,
            rct: None,
            iterations: s.iterations,
            residual_norm: s.residual_norm,
            local_error: s.local_error,
            event_error_per_h: 0.,
        });
    }
    ec.validate()?;
    if dt == 0. {
        return implicit_step(m, old, dt, c, sel);
    }
    let full = implicit_step(m, old, dt, c, sel)?;
    let a = implicit_step(m, old, dt / 2., c, sel)?;
    let b = implicit_step(m, &a.state, dt / 2., c, sel)?;
    let mut error =
        (m.gas.temperature(&full.state)?.ln() - m.gas.temperature(&b.state)?.ln()).abs();
    for j in 0..3 {
        error = error.max((full.state.fractions[j] - b.state.fractions[j]).abs());
    }
    if !error.is_finite() || error >= 2e-4 {
        return Err(err("RCT_LOCAL_ERROR"));
    }
    let re = a
        .rct
        .ok_or_else(|| err("RCT_INTERNAL_SELECTION"))?
        .plus(b.rct.ok_or_else(|| err("RCT_INTERNAL_SELECTION"))?)?;
    let fc = full
        .rct
        .ok_or_else(|| err("RCT_INTERNAL_SELECTION"))?
        .events
        / m.gas.n_h_cm3;
    let hc = re.events / m.gas.n_h_cm3;
    let error_event = (fc - hc).abs();
    let allowed = ec.absolute_per_h + ec.relative * fc.abs().max(hc.abs());
    if !allowed.is_finite() || !error_event.is_finite() {
        return Err(err("RCT_OVERFLOW"));
    }
    if error_event > allowed {
        return Err(err("RCT_EVENT_LOCAL_ERROR"));
    }
    Ok(RctStep {
        state: b.state,
        baseline_events: plus_events(a.baseline_events, b.baseline_events)?,
        rct: Some(re),
        iterations: full.iterations + a.iterations + b.iterations,
        residual_norm: a.residual_norm.max(b.residual_norm),
        local_error: error,
        event_error_per_h: error_event,
    })
}
/// Commit state and the external count/energy accumulator only after all checks.
pub fn try_adaptive_step(
    m: &Ft03Model,
    s: &mut HHeState,
    total: &mut RctIntegral,
    dt: f64,
    c: StepControl,
    sel: RctSelection,
    ec: EventControl,
) -> Result<RctStep, ForwardError> {
    let r = adaptive_step(m, s, dt, c, sel, ec)?;
    let next = if let Some(e) = r.rct {
        total.plus(e)?
    } else {
        *total
    };
    *s = r.state;
    *total = next;
    Ok(r)
}

#[cfg(test)]
mod isolated_tests {
    use super::*;
    #[test]
    fn species_iteration_matches_existing_isolated_be_oracle() {
        let cases: [[f64; 8]; 6] = [
            [1.0, 1.0, 0.5, 0.0, 0.5, 1.0, 0.1, 0.022774424948338867],
            [1.0, 1.0, 0.5, 0.0, 0.5, 1.0, 1.0, 0.13397459621556135],
            [1.0, 0.1, 0.9, 0.2, 0.3, 1.0, 0.2, 0.0005848620006939289],
            [
                0.0001,
                8.3e-06,
                0.9,
                0.3,
                0.6,
                1e-14,
                1000000000000.0,
                4.979999253996135e-13,
            ],
            [1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0],
            [1.0, 1.0, 0.5, 1.0, 0.0, 1.0, 1.0, 0.0],
        ];
        for [nh, nhe, x, y, z, k, dt, exact] in cases {
            let old = [x, y, z];
            let mut guess = old;
            let mut converged = false;
            for _ in 0..1000 {
                let next = species_block(old, guess, [0.; 3], [0.; 3], 0., k * nh, k * nhe, dt);
                let diff = (0..3)
                    .map(|i| (next[i] - guess[i]).abs())
                    .fold(0_f64, f64::max);
                guess = next;
                if diff < 1e-15 {
                    converged = true;
                    break;
                }
            }
            assert!(converged);
            let jh = nh * (guess[0] - x);
            let jhe = nhe * (z - guess[2]);
            assert!((jh - exact).abs() < 1e-13 * nh);
            assert!((jhe - exact).abs() < 1e-13 * nhe);
            assert!((guess[1] + guess[2] - y - z).abs() < 1e-13);
        }
    }
    #[test]
    fn primitive_nonzero_product_rejects_underflow_and_overflow() {
        assert_eq!(
            product(&[1e-300, 1e-100]).unwrap_err().code(),
            "RCT_PRODUCT_UNDERFLOW"
        );
        assert_eq!(product(&[1e300, 1e100]).unwrap_err().code(), "RCT_OVERFLOW");
        assert_eq!(product(&[0., 1e-300]).unwrap(), 0.);
    }
}
