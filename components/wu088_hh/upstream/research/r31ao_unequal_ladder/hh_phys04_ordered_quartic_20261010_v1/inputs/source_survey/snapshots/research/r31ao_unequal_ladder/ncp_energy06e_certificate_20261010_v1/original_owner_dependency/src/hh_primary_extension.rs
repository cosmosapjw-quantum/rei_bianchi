
// Source-consistent HH opt-in. Fixed stage only, no history or physical-fit claim.
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum HhMode { Off, Lcs91 }
impl HhMode {
    pub fn model_id(self)->&'static str {match self {
        Self::Off=>"REI_FT03_PRIMARY_OFF_V1",
        Self::Lcs91=>"HH_ON06_FT03_LCS_BINARY64_REAL_V1"
    }}
}
#[derive(Clone,Debug)]
pub struct HhStep {
    pub base:PrimaryStep, pub hh_events_per_h:f64,
    pub hh_heat_ev_per_h:f64, pub mode:HhMode,
}
#[derive(Clone,Debug)]
pub struct HhRoot {
    pub root:PrimaryRoot, pub mode:HhMode,
    pub image:[Interval;4], pub scales:[f64;4],
    pub identity:HhIdentity,
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct HhIdentity {mode:HhMode,bits:Vec<u64>}
impl HhIdentity {
    pub fn new(g:&PrimaryStage,s:&PrimaryState,p:&PrimaryBox,dt:f64,c:StepControl,m:HhMode)->Self {
        let mut bits=vec![g.n_h_cm3.to_bits(),g.f_he.to_bits(),g.h_mean_per_s.to_bits(),dt.to_bits(),
            c.residual_tolerance.to_bits(),c.max_iterations as u64,s.escape_ev_per_h.to_bits(),
            s.w_ev_per_h.to_bits(), s.packets.len() as u64];
        bits.extend(s.fractions.map(f64::to_bits));
        for x in &s.packets {bits.extend([x.energy_ev.to_bits(),x.per_h.to_bits()]);}
        for x in p.gas.iter().chain(&p.photons) {bits.extend([x.lo.to_bits(),x.hi.to_bits()]);}
        Self{mode:m,bits}
    }
}
pub fn hh_root_matches(r:&HhRoot,g:&PrimaryStage,s:&PrimaryState,p:&PrimaryBox,dt:f64,c:StepControl,m:HhMode)->bool {
    r.mode==m && r.identity==HhIdentity::new(g,s,p,dt,c,m)
}
fn hh_rate_point(t:f64)->Result<f64,ForwardError>{
    if !t.is_finite() || !(35000.0..=60000.0).contains(&t){return Err(fail("HH_ON06_TEMPERATURE_DOMAIN"));}
    positive_product(&[1.2e-17,t.powf(1.2),(-157800.0/t).exp()])
}
fn hh_q_point(g:&PrimaryStage,m:&Ft03Model,s:&PrimaryState)->Result<f64,ForwardError>{
    let t=valid(m,s)?;
    positive_product(&[g.n_h_cm3,1.0-s.fractions[0],1.0-s.fractions[0],hh_rate_point(t)?])
}
/// q, dq and d2q in (h,HeII,HeIII,w[eV/H]), other derivative slots zero.
/// At h=1, q=dq=0 but d2q/dh2=2*nH*k: no division by ne or neutral fraction.
pub fn hh_rate_jet(g:&PrimaryStage,gas:&[Interval;4])->Result<Jet,ForwardError>{
    let m=model(g)?;
    if gas.iter().any(|x|x.valid().is_err()) || gas[0].lo<0.0 || gas[0].hi>1.0 ||
        gas[1].lo<0.0 || gas[2].lo<0.0 || gas[1].hi+gas[2].hi>1.0 || gas[3].lo<=0.0 {
        return Err(fail("HH_ON06_GAS_BOX_DOMAIN"));
    }
    let y:[Jet;4]=std::array::from_fn(|i|Jet::variable(gas[i],i).unwrap());
    let one=ic(1.0)?;
    let fhe=jdiv(&ic(m.gas.n_he_cm3)?,&ic(m.gas.n_h_cm3)?)?;
    let parts=jadd(&jadd(&jadd(&one,&fhe)?,&y[0])?,&jmul(&fhe,&jadd(&y[1],&jmul(&ic(2.0)?,&y[2])?)?)?)?;
    let t=jdiv(&jprod(&[ic(2.0)?,ic(m.gas.ev_erg)?,y[3].clone()])?,&jprod(&[ic(3.0)?,ic(m.gas.kb_erg_k)?,parts])?)?;
    if t.value.lo<35000.0 || t.value.hi>60000.0 {return Err(fail("HH_ON06_TEMPERATURE_DOMAIN"));}
    let power=t.powf(1.2).map_err(ie)?;
    let exponential=jdiv(&ic(-157800.0)?,&t)?.exp().map_err(ie)?;
    let neutral=jsub(&one,&y[0])?;
    jprod(&[ic(g.n_h_cm3)?,neutral.clone(),neutral,ic(1.2e-17)?,power,exponential])
}
/// Same reduced photon elimination and FT03 baseline as owner code, with HH jets.
pub fn hh_interval_source(g:&PrimaryStage,s:&PrimaryState,gas:&[Interval;4],photons:&[Interval],dt:f64,mode:HhMode)
 ->Result<([Jet;4],Vec<Interval>),ForwardError>{
    let m=model(g)?; let sigma=signatures(s)?;
    hh_interval_rhs(g,&m,s,gas,photons,&sigma,dt,mode)
}
fn hh_interval_rhs(g:&PrimaryStage,m:&Ft03Model,s:&PrimaryState,gas:&[Interval;4],pi:&[Interval],sigma:&[[f64;3]],dt:f64,mode:HhMode)
 ->Result<([Jet;4],Vec<Interval>),ForwardError>{
    if !dt.is_finite() || dt<0.0 || pi.len()!=s.packets.len() || sigma.len()!=pi.len() ||
        pi.iter().any(|x|x.valid().is_err()||x.lo<0.0) {return Err(fail("HH_ON06_INTERVAL_INPUT"));}
    let (mut f,ph)=interval_rhs(g,m,s,gas,pi,sigma,dt)?;
    if mode==HhMode::Lcs91 {
        let q=hh_rate_jet(g,gas)?;
        f[0]=jadd(&f[0],&q)?;
        f[3]=jsub(&f[3],&jmul(&ic(CHI[0])?,&q)?)?;
    }
    Ok((f,ph))
}

fn hh_endpoint(
    stage: &PrimaryStage,
    m: &Ft03Model,
    old: &PrimaryState,
    s: &PrimaryState,
    sigma: &[[f64; 3]],
    dt: f64,
) -> Result<(f64, PrimaryEvents, f64), ForwardError> {
    let r = raw(m, s)?;
    let nh = stage.n_h_cm3;
    let ev = m.gas.ev_erg;
    let rates = photo_rates(stage, s, sigma, m.gas.c_cm_s)?;
    let mut d = [
        r.derivative[0],
        r.derivative[1],
        r.derivative[2],
        r.derivative[3] / (nh * ev) - 2.0 * stage.h_mean_per_s * s.w_ev_per_h,
    ];
    for (k, pr) in rates.iter().enumerate() {
        d[0] += pr[0];
        d[1] += (pr[1] - pr[2]) / stage.f_he;
        d[2] += pr[2] / stage.f_he;
        let _ = k;
    }
    d[3] += photo_heat(&rates, &s.packets)?;
    let q=hh_q_point(stage,m,s)?;
    d[0]+=q;
    d[3]-=CHI[0]*q;
    let mut norm = 0.0_f64;
    let x0 = [
        old.fractions[0],
        old.fractions[1],
        old.fractions[2],
        old.w_ev_per_h,
    ];
    let x1 = [s.fractions[0], s.fractions[1], s.fractions[2], s.w_ev_per_h];
    for i in 0..4 {
        norm = norm
            .max(((x1[i] - x0[i] - dt * d[i]) / if i == 3 { old.w_ev_per_h } else { 1.0 }).abs());
    }
    for (k, p) in s.packets.iter().enumerate() {
        let loss = rates[k].iter().sum::<f64>();
        norm = norm.max(
            ((p.per_h - old.packets[k].per_h + dt * loss)
                / if old.packets[k].per_h > 0.0 {
                    old.packets[k].per_h
                } else {
                    1.0
                })
            .abs(),
        );
    }
    let escape_rate = r.escaped_energy_rate / (nh * ev);
    norm = norm.max(
        ((s.escape_ev_per_h - old.escape_ev_per_h - dt * escape_rate)
            / energy(stage, old).max(1e-30))
        .abs(),
    );
    let events = PrimaryEvents {
        photo_per_h: rates
            .into_iter()
            .map(|p| {
                let mut result = [0.0; 3];
                for a in 0..3 {
                    result[a] = positive_product(&[dt, p[a]])?;
                }
                Ok(result)
            })
            .collect::<Result<Vec<_>, ForwardError>>()?,
        collision_per_h: r.collision_per_cm3_s.map(|v| dt * v / nh),
        recombination_per_h: r.recombination_per_cm3_s.map(|v| dt * v / nh),
        dr_per_h: r.dr_per_cm3_s.map(|v| dt * v / nh),
        thermal_work_ev_per_h: positive_product(&[2.0, stage.h_mean_per_s, dt, s.w_ev_per_h])?,
    };
    if !norm.is_finite()
        || events
            .photo_per_h
            .iter()
            .flatten()
            .chain(events.collision_per_h.iter())
            .chain(events.recombination_per_h.iter())
            .chain(events.dr_per_h.iter())
            .any(|v| !v.is_finite() || *v < 0.0)
        || !events.thermal_work_ev_per_h.is_finite()
    {
        return Err(fail("PRIMARY_ENDPOINT_OVERFLOW"));
    }
    Ok((norm, events, positive_product(&[dt,q])?))
}


fn hh_point_inner(
    stage: &PrimaryStage,
    old: &PrimaryState,
    dt: f64,
    control: StepControl,
) -> Result<HhStep, ForwardError> {
    let m = model(stage)?;
    signatures(old)?;
    hh_rate_point(valid(&m, old)?)?;
    if !dt.is_finite()
        || dt < 0.0
        || control.max_iterations == 0
        || !control.residual_tolerance.is_finite()
        || control.residual_tolerance <= 0.0
    {
        return Err(fail("PRIMARY_STEP_CONTROL"));
    }
    if dt == 0.0 {
        return Ok(HhStep {base:PrimaryStep {
            state: old.clone(),
            events: PrimaryEvents {
                photo_per_h: vec![[0.0; 3]; old.packets.len()],
                collision_per_h: [0.0; 3],
                recombination_per_h: [0.0; 3],
                dr_per_h: [0.0; 2],
                thermal_work_ev_per_h: 0.0,
            },
            iterations: 0,
            residual: 0.0,
        },hh_events_per_h:0.0,hh_heat_ev_per_h:0.0,mode:HhMode::Lcs91});
    }
    let sigma = signatures(old)?;
    let mut guess = old.clone();
    for iteration in 1..=control.max_iterations {
        let temperature = valid(&m, &guess)?;
        let coeff = ft03_coefficients(temperature)?;
        let ne = stage.n_h_cm3
            * (guess.fractions[0] + stage.f_he * (guess.fractions[1] + 2.0 * guess.fractions[2]));
        let pn = photons(stage, old, &guess, &sigma, dt, m.gas.c_cm_s)?;
        let mut next = guess.clone();
        for (p, v) in next.packets.iter_mut().zip(pn) {
            p.per_h = v;
        }
        let mut ion = std::array::from_fn::<_, 3, _>(|a| {
            ne * coeff.beta_ci_cm3_s[a]
                + next
                    .packets
                    .iter()
                    .zip(&sigma)
                    .map(|(p, z)| m.gas.c_cm_s * stage.n_h_cm3 * z[a] * p.per_h)
                    .sum::<f64>()
        });
        ion[0] += positive_product(&[stage.n_h_cm3,1.0-guess.fractions[0],hh_rate_point(temperature)?])?;
        let rr = coeff.alpha_rr_cm3_s.map(|v| ne * v);
        let dr = ne * coeff.alpha_dr_cm3_s.iter().sum::<f64>();
        next.fractions[0] = (old.fractions[0] + dt * ion[0]) / (1.0 + dt * (ion[0] + rr[0]));
        let (a, b, c, d) = (dt * ion[1], dt * (rr[1] + dr), dt * ion[2], dt * rr[2]);
        let he0 = 1.0 - old.fractions[1] - old.fractions[2];
        next.fractions[1] =
            (old.fractions[1] + he0 * a / (1.0 + a) + old.fractions[2] * d / (1.0 + d))
                / (1.0 + b / (1.0 + a) + c / (1.0 + d));
        next.fractions[2] = (old.fractions[2] + c * next.fractions[1]) / (1.0 + d);
        let r = raw(&m, &next)?;
        let rates = photo_rates(stage, &next, &sigma, m.gas.c_cm_s)?;
        let heat = photo_heat(&rates, &next.packets)?;
        next.w_ev_per_h = (old.w_ev_per_h
            + dt * (r.derivative[3] / (stage.n_h_cm3 * m.gas.ev_erg) + heat - CHI[0]*hh_q_point(stage,&m,&next)?))
            / (1.0 + 2.0 * dt * stage.h_mean_per_s);
        next.escape_ev_per_h =
            old.escape_ev_per_h + dt * r.escaped_energy_rate / (stage.n_h_cm3 * m.gas.ev_erg);
        valid(&m, &next)?;
        let (norm, events, hh_events_per_h) = hh_endpoint(stage, &m, old, &next, &sigma, dt)?;
        if norm <= control.residual_tolerance {
            let e0 = energy(stage, old);
            let e1 = energy(stage, &next) + events.thermal_work_ev_per_h;
            if !e0.is_finite() || !e1.is_finite() || e0 <= 0.0 {
                return Err(fail("PRIMARY_ENERGY_INVARIANT"));
            }
            let packets_ok = next
                .packets
                .iter()
                .zip(&old.packets)
                .zip(&events.photo_per_h)
                .all(|((p, previous), loss)| {
                    let denom = if previous.per_h > 0.0 {
                        previous.per_h
                    } else {
                        1.0
                    };
                    (previous.per_h - p.per_h - loss.iter().sum::<f64>()).abs() / denom <= 1e-12
                });
            if (e1 - e0).abs() / e0 > 1e-12 || !packets_ok {
                guess = next;
                continue;
            }
            return Ok(HhStep {base:PrimaryStep {
                state: next,
                events,
                iterations: iteration,
                residual: norm,
            },hh_events_per_h,hh_heat_ev_per_h:-CHI[0]*hh_events_per_h,mode:HhMode::Lcs91});
        }
        guess = next;
    }
    Err(fail("PRIMARY_NONCONVERGENCE"))
}
fn hh_conservative_inner(
    stage: &PrimaryStage,
    old: &PrimaryState,
    dt: f64,
    control: StepControl,
    incoming_w_comp: f64,
) -> Result<(HhStep, f64), ForwardError> {
    if !incoming_w_comp.is_finite() { return Err(fail("PRIMARY_ENERGY_COMPENSATION")); }
    let m = model(stage)?;
    signatures(old)?;
    hh_rate_point(valid(&m, old)?)?;
    if !dt.is_finite()
        || dt < 0.0
        || control.max_iterations == 0
        || !control.residual_tolerance.is_finite()
        || control.residual_tolerance <= 0.0
    {
        return Err(fail("PRIMARY_STEP_CONTROL"));
    }
    if dt == 0.0 {
        return Ok((HhStep {base:PrimaryStep {
            state: old.clone(),
            events: PrimaryEvents {
                photo_per_h: vec![[0.0; 3]; old.packets.len()],
                collision_per_h: [0.0; 3],
                recombination_per_h: [0.0; 3],
                dr_per_h: [0.0; 2],
                thermal_work_ev_per_h: 0.0,
            },
            iterations: 0,
            residual: 0.0,
        },hh_events_per_h:0.0,hh_heat_ev_per_h:0.0,mode:HhMode::Lcs91}, incoming_w_comp));
    }
    let sigma = signatures(old)?;
    let mut guess = old.clone();
    for iteration in 1..=control.max_iterations {
        let temperature = valid(&m, &guess)?;
        let coeff = ft03_coefficients(temperature)?;
        let ne = stage.n_h_cm3
            * (guess.fractions[0] + stage.f_he * (guess.fractions[1] + 2.0 * guess.fractions[2]));
        let pn = photons(stage, old, &guess, &sigma, dt, m.gas.c_cm_s)?;
        let mut next = guess.clone();
        for (p, v) in next.packets.iter_mut().zip(pn) {
            p.per_h = v;
        }
        let mut ion = std::array::from_fn::<_, 3, _>(|a| {
            ne * coeff.beta_ci_cm3_s[a]
                + next
                    .packets
                    .iter()
                    .zip(&sigma)
                    .map(|(p, z)| m.gas.c_cm_s * stage.n_h_cm3 * z[a] * p.per_h)
                    .sum::<f64>()
        });
        ion[0] += positive_product(&[stage.n_h_cm3,1.0-guess.fractions[0],hh_rate_point(temperature)?])?;
        let rr = coeff.alpha_rr_cm3_s.map(|v| ne * v);
        let dr = ne * coeff.alpha_dr_cm3_s.iter().sum::<f64>();
        next.fractions[0] = (old.fractions[0] + dt * ion[0]) / (1.0 + dt * (ion[0] + rr[0]));
        let (a, b, c, d) = (dt * ion[1], dt * (rr[1] + dr), dt * ion[2], dt * rr[2]);
        let he0 = 1.0 - old.fractions[1] - old.fractions[2];
        next.fractions[1] =
            (old.fractions[1] + he0 * a / (1.0 + a) + old.fractions[2] * d / (1.0 + d))
                / (1.0 + b / (1.0 + a) + c / (1.0 + d));
        next.fractions[2] = (old.fractions[2] + c * next.fractions[1]) / (1.0 + d);
        let r = raw(&m, &next)?;
        let rates = photo_rates(stage, &next, &sigma, m.gas.c_cm_s)?;
        let _heat = photo_heat(&rates, &next.packets)?;
        // Cancellation-safe conservative form of the same backward-Euler energy equation.
        let binding_change = CHI[0] * (next.fractions[0] - old.fractions[0])
            + stage.f_he * (CHI[1] * (next.fractions[1] - old.fractions[1])
            + (CHI[1] + CHI[2]) * (next.fractions[2] - old.fractions[2]));
        let packet_change = next.packets.iter().zip(&old.packets)
            .map(|(a,b)|a.energy_ev * (a.per_h-b.per_h)).sum::<f64>();
        let escape_change = dt*r.escaped_energy_rate/(stage.n_h_cm3*m.gas.ev_erg);
        let dilation = 2.0*dt*stage.h_mean_per_s;
        let thermal_change = (-binding_change-packet_change-escape_change-dilation*old.w_ev_per_h)/(1.0+dilation);
        let compensated_change = thermal_change - incoming_w_comp;
        next.w_ev_per_h = old.w_ev_per_h + compensated_change;
        let outgoing_w_comp = (next.w_ev_per_h - old.w_ev_per_h) - compensated_change;
        next.escape_ev_per_h =
            old.escape_ev_per_h + dt * r.escaped_energy_rate / (stage.n_h_cm3 * m.gas.ev_erg);
        valid(&m, &next)?;
        let (norm, events, hh_events_per_h) = hh_endpoint(stage, &m, old, &next, &sigma, dt)?;
        if norm <= control.residual_tolerance {
            let e0 = energy(stage, old);
            let e1 = energy(stage, &next) + events.thermal_work_ev_per_h;
            if !e0.is_finite() || !e1.is_finite() || e0 <= 0.0 {
                return Err(fail("PRIMARY_ENERGY_INVARIANT"));
            }
            let packets_ok = next
                .packets
                .iter()
                .zip(&old.packets)
                .zip(&events.photo_per_h)
                .all(|((p, previous), loss)| {
                    let denom = if previous.per_h > 0.0 {
                        previous.per_h
                    } else {
                        1.0
                    };
                    (previous.per_h - p.per_h - loss.iter().sum::<f64>()).abs() / denom <= 1e-12
                });
            if (e1 - e0).abs() / e0 > 1e-12 || !packets_ok {
                guess = next;
                continue;
            }
            return Ok((HhStep {base:PrimaryStep {
                state: next,
                events,
                iterations: iteration,
                residual: norm,
            },hh_events_per_h,hh_heat_ev_per_h:-CHI[0]*hh_events_per_h,mode:HhMode::Lcs91}, outgoing_w_comp));
        }
        guess = next;
    }
    Err(fail("PRIMARY_NONCONVERGENCE"))
}

pub fn hh_stage_step(g:&PrimaryStage,s:&PrimaryState,dt:f64,c:StepControl,mode:HhMode)->Result<HhStep,ForwardError>{
    match mode {
        HhMode::Off=>Ok(HhStep{base:primary_stage_step(g,s,dt,c)?,hh_events_per_h:0.0,hh_heat_ev_per_h:0.0,mode}),
        HhMode::Lcs91=>hh_point_inner(g,s,dt,c),
    }
}
pub fn hh_stage_step_conservative(g:&PrimaryStage,s:&PrimaryState,dt:f64,c:StepControl,comp:f64,mode:HhMode)->Result<(HhStep,f64),ForwardError>{
    match mode {
        HhMode::Off=>{let(r,b)=primary_stage_step_conservative(g,s,dt,c,comp)?;Ok((HhStep{base:r,hh_events_per_h:0.0,hh_heat_ev_per_h:0.0,mode},b))},
        HhMode::Lcs91=>hh_conservative_inner(g,s,dt,c,comp),
    }
}
pub fn try_hh_stage_step(g:&PrimaryStage,s:&mut PrimaryState,dt:f64,c:StepControl,m:HhMode)->Result<HhStep,ForwardError>{
    let r=hh_stage_step(g,s,dt,c,m)?; *s=r.base.state.clone(); Ok(r)
}

fn hh_krawczyk(
    centre: &[f64; 4],
    parent: &PrimaryBox,
    y: &[Interval; 4],
    f0: &[Jet; 4],
    fy: &[Jet; 4],
    dt: f64,
    c: &[[f64; 4]; 4],
    scales: &[f64;4],
) -> Result<([Interval; 4], f64), ForwardError> {
    let mut b = [[ip(0.0)?; 4]; 4];
    let mut q = 0.0_f64;
    for i in 0..4 {
        let mut row = ip(0.0)?;
        for j in 0..4 {
            let mut v = ip(if i == j { 1.0 } else { 0.0 })?;
            for k in 0..4 {
                let ak = is(
                    &ip(if k == j { 1.0 } else { 0.0 })?,
                    &im(&ip(dt)?, &fy[k].gradient[j])?,
                )?;
                v = is(&v, &im(&ip(c[i][k])?, &ak)?)?;
            }
            row = ia(&row, &im(&ip(v.lo.abs().max(v.hi.abs()))?, &ip(scales[j])?.div(&ip(scales[i])?).map_err(ie)?)?)?;
            b[i][j] = v;
        }
        q = q.max(row.hi);
    }
    let mut k = [ip(0.0)?; 4];
    for i in 0..4 {
        let mut v = ip(centre[i])?;
        for j in 0..4 {
            let resid = is(
                &is(&ip(centre[j])?, &parent.gas[j])?,
                &im(&ip(dt)?, &f0[j].value)?,
            )?;
            v = is(&v, &im(&ip(c[i][j])?, &resid)?)?;
            v = ia(&v, &im(&b[i][j], &is(&y[j], &ip(centre[j])?)?)?)?;
        }
        k[i] = v;
    }
    Ok((k, q))
}


pub fn hh_stage_root(
    stage: &PrimaryStage,
    old: &PrimaryState,
    parent: &PrimaryBox,
    dt: f64,
    control: StepControl,
    mode:HhMode,
) -> Result<HhRoot, ForwardError> {
    let m = model(stage)?;
    let sigma = signatures(old)?;
    valid(&m, old)?;
    if !dt.is_finite() || dt <= 0.0 || parent.photons.len() != old.packets.len() {
        return Err(fail("PRIMARY_ROOT_INPUT"));
    }
    let oldgas = [
        old.fractions[0],
        old.fractions[1],
        old.fractions[2],
        old.w_ev_per_h,
    ];
    for i in 0..4 {
        if !parent.gas[i].lo.is_finite()
            || !parent.gas[i].hi.is_finite()
            || parent.gas[i].lo > parent.gas[i].hi
            || !contains(&parent.gas[i], oldgas[i])
        {
            return Err(fail("PRIMARY_PARENT_GAS"));
        }
    }
    for (b, p) in parent.photons.iter().zip(&old.packets) {
        if !b.lo.is_finite()
            || !b.hi.is_finite()
            || b.lo < 0.0
            || b.lo > b.hi
            || !contains(b, p.per_h)
        {
            return Err(fail("PRIMARY_PARENT_PHOTON"));
        }
    }
    // Qualification covers the entire incoming gas box, including its
    // temperature domain, rather than only the actual incoming point.
    hh_interval_rhs(stage, &m, old, &parent.gas, &parent.photons, &sigma, dt, mode)?;
    let point = hh_stage_step(stage, old, dt, control, mode)?.base;
    let scales=[1.0,1.0,1.0,old.w_ev_per_h];
    let identity=HhIdentity::new(stage,old,parent,dt,control,mode);
    let centre = [
        point.state.fractions[0],
        point.state.fractions[1],
        point.state.fractions[2],
        point.state.w_ev_per_h,
    ];
    let centre_box = centre.map(ip).into_iter().collect::<Result<Vec<_>, _>>()?;
    let cb = [centre_box[0], centre_box[1], centre_box[2], centre_box[3]];
    let (f0, _) = hh_interval_rhs(stage, &m, old, &cb, &parent.photons, &sigma, dt, mode)?;
    let jac: [[f64; 4]; 4] = std::array::from_fn(|i| {
        std::array::from_fn(|j| {
            let z = f0[i].gradient[j];
            (z.lo + z.hi) * 0.5
        })
    });
    let a = std::array::from_fn(|i| {
        std::array::from_fn(|j| (if i == j { 1.0 } else { 0.0 }) - dt * jac[i][j])
    });
    let c = inverse4(a)?;
    let mut radius: [f64; 4] = std::array::from_fn(|i| {
        let p = &parent.gas[i];
        (p.hi - p.lo).abs() * 2.0 + centre[i].abs() * 1e-12 + 1e-13
    });
    let mut accepted: Option<HhRoot> = None;
    for attempt in 0..24 {
        let y = [
            box_about(centre[0], radius[0])?,
            box_about(centre[1], radius[1])?,
            box_about(centre[2], radius[2])?,
            box_about(centre[3], radius[3])?,
        ];
        let (fy, photons) = hh_interval_rhs(stage, &m, old, &y, &parent.photons, &sigma, dt, mode)?;
        let (k, q) = hh_krawczyk(&centre, parent, &y, &f0, &fy, dt, &c, &scales)?;
        if q < 1.0
            && (0..4).all(|i| y[i].lo < k[i].lo && k[i].hi < y[i].hi)
            && point
                .state
                .packets
                .iter()
                .zip(&photons)
                .all(|(p, b)| contains(b, p.per_h))
        {
            accepted = Some(HhRoot {root:PrimaryRoot {
                centre,
                gas: y,
                photons,
                preconditioner: c,
                q,
            },mode,image:k,scales,identity:identity.clone()});
            let refined: [f64; 4] = std::array::from_fn(|i| {
                let r = (k[i].lo - centre[i]).abs().max((k[i].hi - centre[i]).abs());
                r * 1.00001 + 32.0 * f64::EPSILON * centre[i].abs().max(1.0)
            });
            if attempt >= 8 || (0..4).all(|i| refined[i] >= radius[i] * 0.999) {
                return Ok(accepted.unwrap());
            }
            radius = refined;
            continue;
        }
        for i in 0..4 {
            let want = (k[i].lo - centre[i]).abs().max((k[i].hi - centre[i]).abs());
            radius[i] = (radius[i] * 1.5).max(want * 1.5);
        }
    }
    accepted.ok_or_else(|| fail("PRIMARY_ROOT_NONCONVERGENCE"))
}
