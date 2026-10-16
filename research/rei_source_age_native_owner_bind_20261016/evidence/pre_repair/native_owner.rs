//! Opt-in tagged-cohort owner. No production files are modified.
use rei_microphysics::axbi_covariant_transport::{PhotonState, PreparedAbsorption};
use rei_microphysics::axbi_driver::{Driver, DriverState};
use rei_microphysics::axbi_rates::AxbiProvider;
use rei_microphysics::igm_state::{w_erg_per_h_to_ev, w_ev_per_h_to_erg, IgmGasState};
use rei_microphysics::igm_thermal::{IgmPhotoInput, IgmPointRhs};
use rei_microphysics::{ForwardError, HHeModel};
fn err(s: &'static str) -> ForwardError {
    ForwardError::InvalidInput(s)
}
#[derive(Clone, Debug)]
pub struct Birth {
    pub lower_x: f64,
    pub upper_x: f64,
    pub x: f64,
    pub proper_time_s: f64,
    pub rate_per_h_s: f64,
    pub j_per_h_dln_a: f64,
    pub quadrature_weight_dln_a: f64,
    pub physical_energy_bounds_ev: Vec<[f64; 2]>,
    pub mu_birth: Vec<f64>,
    /// Canonical spatial Killing momenta of a unit reference-energy ray.
    /// Each node's canonical p_i is this vector times its native reference q.
    pub killing_per_q: Vec<[f64; 3]>,
    pub original: PhotonState,
}
#[derive(Clone, Debug)]
pub struct Cohort {
    pub birth: Birth,
    pub surviving: PhotonState,
}
#[derive(Clone, Debug)]
pub struct Accepted {
    pub gas_owner: DriverState,
    pub cohorts: Vec<Cohort>,
    pub cursor: usize,
}
pub fn photon_state(s: &DriverState) -> PhotonState {
    PhotonState {
        number: s.photons.clone(),
        energy_ref: s.photon_energy_ref.clone(),
        support_lo: s.photon_support_lo.clone(),
        support_hi: s.photon_support_hi.clone(),
    }
}
pub fn inventory(d: &Driver, s: &Accepted) -> Result<(f64, f64), ForwardError> {
    let g = d.geometry_point(s.gas_owner.a)?.geometry()?;
    let mut n = 0.;
    let mut u = 0.;
    for c in &s.cohorts {
        let v = d.transport.inventory(&c.surviving, &g)?;
        n += v.0;
        u += v.1;
    }
    Ok((n, u))
}
pub fn energy(d: &Driver, s: &Accepted) -> Result<f64, ForwardError> {
    let c = HHeModel::controlled_fixture();
    let [x, y, z] = s.gas_owner.gas.fractions;
    let binding = c.threshold_ev[0] * x
        + d.n_he0_cm3 / d.n_h0_cm3
            * (c.threshold_ev[1] * y + (c.threshold_ev[1] + c.threshold_ev[2]) * z);
    let l = &s.gas_owner.ledgers;
    Ok(inventory(d, s)?.1
        + w_erg_per_h_to_ev(s.gas_owner.gas.w_erg_per_h)?
        + binding
        + l.escaped_u
        + l.photon_work
        + l.thermal_work
        - l.source_u
        - l.cmb_input)
}
pub fn empty(s: DriverState) -> Accepted {
    Accepted {
        gas_owner: s,
        cohorts: vec![],
        cursor: 0,
    }
}
fn norm(r: [f64; 4], ow: f64, nw: f64) -> f64 {
    r[0].abs()
        .max(r[1].abs())
        .max(r[2].abs())
        .max(r[3].abs() / ow.abs().max(nw.abs()).max(1e-6))
}
struct Context<'a> {
    d: &'a Driver,
    old: &'a Accepted,
    prepared: Vec<PreparedAbsorption>,
}
impl Context<'_> {
    fn evaluate(
        &self,
        x: [f64; 4],
        dt: f64,
        count: &mut usize,
    ) -> Result<([f64; 4], Vec<PhotonState>, IgmPointRhs), ForwardError> {
        if *count >= self.d.config.max_rhs {
            return Err(err("AXBI_RHS_CAP"));
        }
        *count += 1;
        let gas = IgmGasState::new([x[0], x[1], x[2]], w_ev_per_h_to_erg(x[3])?)?;
        let a = self.old.gas_owner.a;
        let nh = self.d.n_h0_cm3 / a.powi(3);
        let nhe = self.d.n_he0_cm3 / a.powi(3);
        let absorbers = [nh * (1. - x[0]), nhe * (1. - x[1] - x[2]), nhe * x[1]];
        let mut photo = IgmPhotoInput::default();
        let mut states = vec![];
        for p in &self.prepared {
            let r = p.evaluate(absorbers, nh, dt)?;
            states.push(r.state);
            for k in 0..3 {
                photo.gamma_s[k] += r.photo.gamma_s[k];
                photo.heat_erg_per_absorber_s[k] += r.photo.heat_erg_per_absorber_s[k];
            }
        }
        // ONE native point RHS for the shared gas, after summing the tagged-node inputs.
        let rhs = AxbiProvider
            .point(&gas, nh, nhe, 0., 2.7255 / a, photo)?
            .rhs;
        let mut r = [0.; 4];
        for i in 0..3 {
            r[i] = x[i] - self.old.gas_owner.gas.fractions[i] - dt * rhs.fraction_dt[i];
        }
        r[3] = x[3]
            - w_erg_per_h_to_ev(self.old.gas_owner.gas.w_erg_per_h)?
            - dt * rhs.w_dt_erg_per_h_s / HHeModel::controlled_fixture().ev_erg;
        if r.iter().any(|v| !v.is_finite()) {
            return Err(err("AXBI_DRIVER_NONFINITE"));
        }
        Ok((r, states, rhs))
    }
}
/// Native backward Euler/Newton policy, with a tagged prepared list replacing
/// only the single aggregate prepared object. No gas sub-solves per cohort.
pub fn chemistry(
    d: &Driver,
    old: &Accepted,
    dt: f64,
    count: &mut usize,
) -> Result<Accepted, ForwardError> {
    if !dt.is_finite() || dt <= 0. || d.config.inactive_hi_split {
        return Err(err("COHORT_DT_OR_PASSIVE_MODE"));
    }
    let geometry = d.geometry_point(old.gas_owner.a)?.geometry()?;
    let prepared = old
        .cohorts
        .iter()
        .map(|c| d.transport.prepare(&c.surviving, &geometry))
        .collect::<Result<Vec<_>, _>>()?;
    let context = Context { d, old, prepared };
    let ow = w_erg_per_h_to_ev(old.gas_owner.gas.w_erg_per_h)?;
    let mut x = [
        old.gas_owner.gas.fractions[0],
        old.gas_owner.gas.fractions[1],
        old.gas_owner.gas.fractions[2],
        ow,
    ];
    for _ in 0..50 {
        let (r, stocks, rhs) = context.evaluate(x, dt, count)?;
        let n = norm(r, ow, x[3]);
        if n <= 1e-11 {
            let mut next = old.clone();
            next.gas_owner.gas = IgmGasState::new([x[0], x[1], x[2]], w_ev_per_h_to_erg(x[3])?)?;
            for (c, p) in next.cohorts.iter_mut().zip(stocks) {
                c.surviving = p;
            }
            let nh = d.n_h0_cm3 / old.gas_owner.a.powi(3);
            let ev = HHeModel::controlled_fixture().ev_erg;
            let events = rhs.photo_events_cm3_s.map(|v| v * dt / nh);
            let absorbed = events.iter().sum::<f64>();
            let ni = inventory(d, old)?.0;
            let nf = inventory(d, &next)?.0;
            if (ni - nf - absorbed).abs() > 1e-10 * old.gas_owner.ledgers.source_n.max(1.) {
                return Err(err("AXBI_ABSORPTION_LEDGER"));
            }
            let l = &mut next.gas_owner.ledgers;
            l.absorbed_n += absorbed;
            for k in 0..3 {
                l.photo_events[k] += events[k];
                l.rr_events[k] += rhs.rr_events_cm3_s[k] * dt / nh;
                l.ci_events[k] += rhs.ci_events_cm3_s[k] * dt / nh;
                l.ci_floor_events[k] += rhs.ci_floor_events_cm3_s[k] * dt / nh;
            }
            l.dr_events += rhs.dr_events_cm3_s * dt / nh;
            l.ce_cap_ev += rhs.ce_cap_cooling_erg_cm3_s.iter().sum::<f64>() * dt / (nh * ev);
            l.excluded_dr_ev += rhs.excluded_dr_cooling_erg_cm3_s * dt / (nh * ev);
            l.escaped_u += rhs.escape_erg_cm3_s * dt / (nh * ev);
            l.cmb_input += rhs.cmb_to_gas_erg_cm3_s * dt / (nh * ev);
            next.gas_owner.max_newton_residual = next.gas_owner.max_newton_residual.max(n);
            return Ok(next);
        }
        let mut jac = [[0.; 4]; 4];
        for j in 0..4 {
            let delta = 1e-7 * x[j].abs().max(if j == 3 { 1e-6 } else { 1e-4 });
            let mut xp = x;
            xp[j] += delta;
            let (rp, sign) = match context.evaluate(xp, dt, count) {
                Ok((r, _, _)) => (r, 1.),
                Err(_) => {
                    xp = x;
                    xp[j] -= delta;
                    (context.evaluate(xp, dt, count)?.0, -1.)
                }
            };
            for i in 0..4 {
                jac[i][j] = (rp[i] - r[i]) / (sign * delta);
            }
        }
        let direction = solve4(jac, r.map(|v| -v))?;
        let mut alpha = 1.;
        let mut accepted = None;
        for _ in 0..40 {
            let xp = std::array::from_fn(|i| x[i] + alpha * direction[i]);
            if let Ok((rp, _, _)) = context.evaluate(xp, dt, count) {
                if norm(rp, ow, xp[3]) < n {
                    accepted = Some(xp);
                    break;
                }
            }
            alpha *= 0.5;
        }
        x = accepted.ok_or(err("AXBI_NEWTON_LINESEARCH"))?;
    }
    Err(err("AXBI_NEWTON_ITERATIONS"))
}
fn solve4(mut a: [[f64; 4]; 4], mut b: [f64; 4]) -> Result<[f64; 4], ForwardError> {
    for k in 0..4 {
        let pivot = (k..4)
            .max_by(|&i, &j| a[i][k].abs().total_cmp(&a[j][k].abs()))
            .unwrap();
        if a[pivot][k].abs() < 1e-30 || !a[pivot][k].is_finite() {
            return Err(err("AXBI_SINGULAR_JACOBIAN"));
        }
        a.swap(k, pivot);
        b.swap(k, pivot);
        for i in k + 1..4 {
            let factor = a[i][k] / a[k][k];
            for j in k..4 {
                a[i][j] -= factor * a[k][j];
            }
            b[i] -= factor * b[k];
        }
    }
    let mut x = [0.0; 4];
    for i in (0..4).rev() {
        x[i] = f((b[i] - (i + 1..4).map(|j| a[i][j] * x[j]).sum::<f64>()) / a[i][i])?;
    }
    Ok(x)
}

fn f(x: f64) -> Result<f64, ForwardError> {
    if x.is_finite() {
        Ok(x)
    } else {
        Err(err("AXBI_DRIVER_NONFINITE"))
    }
}
fn geometry(d: &Driver, s: &Accepted, to: f64) -> Result<Accepted, ForwardError> {
    let mut next = s.clone();
    let before = inventory(d, s)?.1;
    let ow = w_erg_per_h_to_ev(s.gas_owner.gas.w_erg_per_h)?;
    next.gas_owner.a = to;
    let after = inventory(d, &next)?.1;
    next.gas_owner.gas = s.gas_owner.gas.adiabatic_to(s.gas_owner.a, to)?;
    next.gas_owner.ledgers.photon_work += before - after;
    next.gas_owner.ledgers.thermal_work += ow - w_erg_per_h_to_ev(next.gas_owner.gas.w_erg_per_h)?;
    Ok(next)
}
fn advance_one(
    d: &Driver,
    s: &Accepted,
    to: f64,
    count: &mut usize,
) -> Result<Accepted, ForwardError> {
    if to == s.gas_owner.a {
        return Ok(s.clone());
    }
    if to < s.gas_owner.a {
        return Err(err("COHORT_REVERSE_TIME"));
    }
    let dt = d.geometry_increment(s.gas_owner.a, to)?.proper_time_s;
    let mid = (s.gas_owner.a * to).sqrt();
    let a = geometry(d, s, mid)?;
    let b = chemistry(d, &a, dt, count)?;
    geometry(d, &b, to)
}
fn advance(d: &Driver, s: &Accepted, to: f64, count: &mut usize) -> Result<Accepted, ForwardError> {
    if to <= s.gas_owner.a {
        return advance_one(d, s, to, count);
    }
    let x = s.gas_owner.a.ln();
    let width = to.ln() - x;
    let panels = (width / d.config.initial_dln_a).ceil().max(1.) as usize;
    let mut next = s.clone();
    for i in 0..panels {
        next = advance_one(
            d,
            &next,
            (x + width * (i + 1) as f64 / panels as f64).exp(),
            count,
        )?;
    }
    Ok(next)
}
/// Positive midpoint quadrature in x=ln(a). Births are chronologically split.
/// j(x)=per_h_s/H; transport.inject uses dt_equiv=weight/H at birth geometry.
/// This is an explicit first-order source/operator quadrature, refined separately.
pub fn trial(
    d: &Driver,
    old: &Accepted,
    to: f64,
    birth_panels: usize,
    count: &mut usize,
) -> Result<Accepted, ForwardError> {
    if birth_panels == 0 || !to.is_finite() || to <= old.gas_owner.a || d.config.inactive_hi_split {
        return Err(err("COHORT_TRIAL_DOMAIN"));
    }
    let x0 = old.gas_owner.a.ln();
    let dx = (to.ln() - x0) / birth_panels as f64;
    let mut s = old.clone();
    let reference = d.geometry_point(1. / 21.)?.geometry()?;
    for i in 0..birth_panels {
        let lo = x0 + i as f64 * dx;
        let hi = lo + dx;
        let x = 0.5 * (lo + hi);
        let a = x.exp();
        s = advance(d, &s, a, count)?;
        let point = d.geometry_point(a)?;
        let g = point.geometry()?;
        let rays = d.transport.ray_geometry(&g)?;
        let rate = d.source.at_redshift(1. / a - 1.)?.per_h_s;
        let mut p = d.transport.empty_state();
        let emitted = d
            .transport
            .inject(&mut p, &g, 1. / a - 1., dx / point.h_per_s)?;
        let bounds = p
            .support_lo
            .iter()
            .zip(&p.support_hi)
            .enumerate()
            .map(|(k, (&l, &h))| {
                [
                    l * rays[k / d.transport.n_energy()].scale,
                    h * rays[k / d.transport.n_energy()].scale,
                ]
            })
            .collect();
        let killing = d
            .source
            .angular_cells
            .iter()
            .map(|c| {
                [
                    reference.scale_factors[0] * (1. - c.mu * c.mu).sqrt(),
                    0.,
                    reference.scale_factors[2] * c.mu,
                ]
            })
            .collect();
        let birth = Birth {
            lower_x: lo,
            upper_x: hi,
            x,
            proper_time_s: point.time_s,
            rate_per_h_s: rate,
            j_per_h_dln_a: rate / point.h_per_s,
            quadrature_weight_dln_a: dx,
            physical_energy_bounds_ev: bounds,
            mu_birth: rays.iter().map(|r| r.mu).collect(),
            killing_per_q: killing,
            original: p.clone(),
        };
        s.cohorts.push(Cohort {
            birth,
            surviving: p,
        });
        s.cursor += 1;
        s.gas_owner.ledgers.source_n += emitted.added_photons_per_h;
        s.gas_owner.ledgers.source_u += emitted.added_energy_ev_per_h;
    }
    s = advance(d, &s, to, count)?;
    s.gas_owner.accepted = old.gas_owner.accepted + 1;
    let ni = inventory(d, old)?.0;
    let nf = inventory(d, &s)?.0;
    let l0 = &old.gas_owner.ledgers;
    let l = &s.gas_owner.ledgers;
    let nr = nf - ni + l.absorbed_n - l0.absorbed_n - l.source_n + l0.source_n;
    if nr.abs()
        > 1e-10
            * (ni.abs()
                + nf.abs()
                + (l.source_n - l0.source_n).abs()
                + (l.absorbed_n - l0.absorbed_n).abs())
    {
        return Err(err("COHORT_NUMBER_LEDGER"));
    }
    let ei = energy(d, old)?;
    let ef = energy(d, &s)?;
    let gross = inventory(d, old)?.1.abs()
        + inventory(d, &s)?.1.abs()
        + w_erg_per_h_to_ev(old.gas_owner.gas.w_erg_per_h)?.abs()
        + w_erg_per_h_to_ev(s.gas_owner.gas.w_erg_per_h)?.abs()
        + l.source_u.abs()
        + l.escaped_u.abs()
        + l.cmb_input.abs()
        + ei.abs()
        + ef.abs();
    if (ef - ei).abs() > 1e-10 * gross {
        return Err(err("COHORT_ENERGY_LEDGER"));
    }
    Ok(s)
}
