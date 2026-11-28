//! Static opt-in HH stepper derived from the pinned FT03 block iteration.
//! The original FT03 module is unchanged. OFF delegates directly to it.
//! All ON thermal evaluations, final residuals and HH events share one selector.
use crate::{ft03_coefficients,ForwardError,Ft03Model,Ft03Events,Ft03Step,HHeState,StepControl};
use crate::hh_optin::{self,HhSelection};
#[derive(Clone,Copy,Debug,Default)]
pub struct HhIntegrated {pub events_cm3:f64,pub per_h:f64,pub heat_erg_cm3:f64}
#[derive(Clone,Copy,Debug)]
pub struct HhStep {pub state:HHeState,pub events:Ft03Events,pub hh:HhIntegrated,pub iterations:usize,pub residual_norm:f64,pub local_error:f64}
fn wrap(s:Ft03Step)->HhStep {HhStep{state:s.state,events:s.events,hh:HhIntegrated::default(),iterations:s.iterations,residual_norm:s.residual_norm,local_error:s.local_error}}
fn validate_on(model:&Ft03Model,state:&HHeState,selection:HhSelection)->Result<f64,ForwardError>{
 hh_optin::combined_ft03_rhs(model,state,selection)?;
 model.gas.temperature(state)
}
fn finite_events(e:&Ft03Events)->bool {
 e.photo_per_cm3.iter().flatten().chain(e.collision_per_cm3.iter()).chain(e.recombination_per_cm3.iter()).chain(e.dr_per_cm3.iter()).all(|v|v.is_finite() && *v>=0.)
}
fn finite_hh(e:&HhIntegrated)->bool {e.events_cm3.is_finite() && e.events_cm3>=0. && e.per_h.is_finite() && e.per_h>=0. && e.heat_erg_cm3.is_finite() && e.heat_erg_cm3<=0.}
fn checked_product(factors:&[f64])->Result<f64,ForwardError>{
 if factors.iter().any(|x|!x.is_finite()){return Err(ForwardError::InvalidInput("HH_NONFINITE"));}
 if factors.contains(&0.){return Ok(0.);}
 let v=factors.iter().product::<f64>();
 if !v.is_finite(){return Err(ForwardError::InvalidInput("HH_NONFINITE"));}
 if v==0.{return Err(ForwardError::InvalidInput("HH_PRODUCT_UNDERFLOW"));}
 Ok(v)
}
fn be_endpoint_residual(
    model: &Ft03Model,
    old: &HHeState,
    new: &HHeState,
    dt: f64,
    selection: HhSelection,
) -> Result<(f64, Ft03Events, HhIntegrated), ForwardError> {
    let ep = hh_optin::endpoint(model, old, new, dt, selection)?;
    let rhs = ep.rhs.combined;
    let scale = [
        1.0,
        1.0,
        1.0,
        old.u_erg_cm3.max(1e-30),
        old.photon_cm3[0].max(1e-30),
        old.photon_cm3[1].max(1e-30),
        old.photon_cm3[2].max(1e-30),
    ];
    let mut norm: f64 = 0.0;
    for k in 0..7 {
        norm = norm.max((ep.residual[k] / scale[k]).abs());
    }
    norm = norm.max(
        (ep.escaped_residual
            / model.gas.total_energy(old)?.max(1e-30))
        .abs(),
    );
    let mut events = Ft03Events::default();
    for a in 0..3 {
        events.collision_per_cm3[a] = dt * rhs.collision_per_cm3_s[a];
        events.recombination_per_cm3[a] = dt * rhs.recombination_per_cm3_s[a];
        for k in 0..3 {
            events.photo_per_cm3[a][k] = dt * rhs.photo_per_cm3_s[a][k];
        }
    }
    for k in 0..2 {
        events.dr_per_cm3[k] = dt * rhs.dr_per_cm3_s[k];
    }
    if !norm.is_finite() || !finite_events(&events) {
        return Err(ForwardError::InvalidInput("FT03_OVERFLOW"));
    }
    let hh=HhIntegrated{events_cm3:ep.hh_events_cm3,per_h:ep.hh_per_h,heat_erg_cm3:ep.hh_heat_erg_cm3};
    if !finite_hh(&hh){return Err(ForwardError::InvalidInput("HH_NONFINITE"));}
    Ok((norm, events, hh))
}

fn check_invariants(
    model: &Ft03Model,
    old: &HHeState,
    new: &HHeState,
    events: &Ft03Events,
    hh: &HhIntegrated,
    tolerance: f64,
) -> Result<(), ForwardError> {
    let g = &model.gas;
    let energy0 = g.total_energy(old)?;
    let energy1 = g.total_energy(new)?;
    let mut norm = ((energy1 - energy0) / energy0.max(1e-30)).abs();
    let mut j = [0.0; 3];
    for (a, value) in j.iter_mut().enumerate() {
        *value = events.photo_per_cm3[a].iter().sum::<f64>() + events.collision_per_cm3[a]
            - events.recombination_per_cm3[a];
    }
    j[0] += hh.events_cm3;
    j[1] -= events.dr_per_cm3.iter().sum::<f64>();
    norm = norm.max(((g.n_h_cm3 * (new.fractions[0] - old.fractions[0]) - j[0]) / g.n_h_cm3).abs());
    norm = norm.max(
        ((g.n_he_cm3 * (new.fractions[1] - old.fractions[1]) - j[1] + j[2]) / g.n_he_cm3).abs(),
    );
    norm =
        norm.max(((g.n_he_cm3 * (new.fractions[2] - old.fractions[2]) - j[2]) / g.n_he_cm3).abs());
    for k in 0..3 {
        let absorbed = (0..3).map(|a| events.photo_per_cm3[a][k]).sum::<f64>();
        norm = norm.max(
            ((old.photon_cm3[k] - new.photon_cm3[k] - absorbed) / old.photon_cm3[k].max(1e-30))
                .abs(),
        );
    }
    if !norm.is_finite() || norm > tolerance.max(1e-13) * 8.0 {
        return Err(ForwardError::InvalidInput("FT03_INVARIANT_RESIDUAL"));
    }
    Ok(())
}

pub fn implicit(
    model: &Ft03Model,
    old: &HHeState,
    dt: f64,
    control: StepControl,
    selection: HhSelection,
) -> Result<HhStep, ForwardError> {
    let provider=match selection {
      HhSelection::Disabled=>return Ok(wrap(crate::ft03_implicit_step(model,old,dt,control)?)),
      HhSelection::Research(p)=>p,
    };
    validate_on(model,old,selection)?;
    if !dt.is_finite()
        || dt < 0.0
        || control.max_iterations == 0
        || !control.residual_tolerance.is_finite()
        || control.residual_tolerance <= 0.0
    {
        return Err(ForwardError::InvalidInput("FT03_STEP_CONTROL"));
    }
    if dt == 0.0 {
        return Ok(HhStep {
            state: *old,
            events: Ft03Events::default(),
            hh:HhIntegrated::default(),
            iterations: 0,
            residual_norm: 0.0,
            local_error: 0.0,
        });
    }
    let g = &model.gas;
    let mut guess = *old;
    for iteration in 1..=control.max_iterations {
        let ne = g.electron_density(&guess)?;
        let t=validate_on(model,&guess,selection)?;
        let c = ft03_coefficients(t)?;
        let hh_rate=provider.rate(t)?;
        let [h, he1, he2] = guess.fractions;
        let lower = [
            g.n_h_cm3 * (1.0 - h),
            g.n_he_cm3 * (1.0 - (he1 + he2)),
            g.n_he_cm3 * he1,
        ];
        let mut next = guess;
        for k in 0..3 {
            let opacity = (0..3).map(|a| lower[a] * g.sigma_cm2[a][k]).sum::<f64>();
            next.photon_cm3[k] = old.photon_cm3[k] / (1.0 + dt * g.c_cm_s * opacity);
        }
        let mut ion = std::array::from_fn::<_, 3, _>(|a| {
            (0..3)
                .map(|k| g.c_cm_s * g.sigma_cm2[a][k] * next.photon_cm3[k])
                .sum::<f64>()
                + ne * c.beta_ci_cm3_s[a]
        });
        // Frequency per remaining neutral: fixed point gives nH*(1-h)^2*k.
        ion[0] += checked_product(&[g.n_h_cm3, 1.0-h, hh_rate.k_cm3_s])?;
        let rr = std::array::from_fn::<_, 3, _>(|a| ne * c.alpha_rr_cm3_s[a]);
        let dr = ne * c.alpha_dr_cm3_s.iter().sum::<f64>();
        next.fractions[0] = (old.fractions[0] + dt * ion[0]) / (1.0 + dt * (ion[0] + rr[0]));
        let he0_old = 1.0 - (old.fractions[1] + old.fractions[2]);
        let a = dt * ion[1];
        let b = dt * (rr[1] + dr);
        let c2 = dt * ion[2];
        let d = dt * rr[2];
        // All production terms are nonnegative at a helium boundary.
        let he1_next =
            (old.fractions[1] + he0_old * (a / (1.0 + a)) + old.fractions[2] * (d / (1.0 + d)))
                / (1.0 + b / (1.0 + a) + c2 / (1.0 + d));
        next.fractions[1] = he1_next;
        next.fractions[2] = (old.fractions[2] + c2 * he1_next) / (1.0 + d);
        // Use the candidate's fractions and photons with the current thermal
        // guess; the final RHS and residual are reevaluated at the actual T.
        let rates = hh_optin::combined_ft03_rhs(model, &next, selection)?.combined;
        next.u_erg_cm3 = old.u_erg_cm3 + dt * rates.derivative[3];
        next.escaped_erg_cm3 = old.escaped_erg_cm3 + dt * rates.escaped_energy_rate;
        validate_on(model,&next,selection)?;
        let (norm, events, hh) = be_endpoint_residual(model, old, &next, dt, selection)?;
        if norm < control.residual_tolerance {
            check_invariants(model, old, &next, &events, &hh, control.residual_tolerance)?;
            return Ok(HhStep {
                state: next,
                events,
                hh,
                iterations: iteration,
                residual_norm: norm,
                local_error: 0.0,
            });
        }
        guess = next;
    }
    Err(ForwardError::InvalidInput("FT03_NONCONVERGENCE"))
}

pub fn adaptive(
    model: &Ft03Model,
    old: &HHeState,
    dt: f64,
    control: StepControl,
    selection: HhSelection,
) -> Result<HhStep, ForwardError> {
    if let HhSelection::Disabled=selection{return Ok(wrap(crate::ft03_adaptive_step(model,old,dt,control)?));}
    if dt == 0.0 {
        return implicit(model, old, dt, control, selection);
    }
    let full = implicit(model, old, dt, control, selection)?;
    let half1 = implicit(model, old, dt / 2.0, control, selection)?;
    let half2 = implicit(model, &half1.state, dt / 2.0, control, selection)?;
    let tf = model.gas.temperature(&full.state)?;
    let th = model.gas.temperature(&half2.state)?;
    let mut error = (tf.ln() - th.ln()).abs();
    for a in 0..3 {
        error = error.max((full.state.fractions[a] - half2.state.fractions[a]).abs());
    }
    if !error.is_finite() || error >= 2e-4 {
        return Err(ForwardError::InvalidInput("FT03_LOCAL_ERROR"));
    }
    let events = half1.events.plus(half2.events);
    if !finite_events(&events) {
        return Err(ForwardError::InvalidInput("FT03_OVERFLOW"));
    }
    let hh=HhIntegrated{
      events_cm3:half1.hh.events_cm3+half2.hh.events_cm3,
      per_h:half1.hh.per_h+half2.hh.per_h,
      heat_erg_cm3:half1.hh.heat_erg_cm3+half2.hh.heat_erg_cm3,
    };
    if !finite_hh(&hh){return Err(ForwardError::InvalidInput("HH_NONFINITE"));}
    check_invariants(model,old,&half2.state,&events,&hh,control.residual_tolerance)?;
    Ok(HhStep {
        state: half2.state,
        events,
        hh,
        iterations: full.iterations + half1.iterations + half2.iterations,
        residual_norm: half1.residual_norm.max(half2.residual_norm),
        local_error: error,
    })
}

/// Commit only after every full/half solve, local-error and event check succeeds.
pub fn try_adaptive(model:&Ft03Model,state:&mut HHeState,dt:f64,control:StepControl,selection:HhSelection)->Result<HhStep,ForwardError>{
 let result=adaptive(model,state,dt,control,selection)?;
 *state=result.state;
 Ok(result)
}
