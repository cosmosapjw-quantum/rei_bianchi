use crate::{
    checked, err,
    material::{self, MaterialOwners},
    radiation::{self, Grid, Radiation},
    v2::{self, Owners},
    Fallible,
};
use rei_microphysics::{igm_background::FlrwPoint, igm_config::HistoryConfig};
pub const TOL: [f64; 4] = [1e-14, 1e-14, 1e-14, 1e-26];
#[derive(Clone, Debug, PartialEq)]
pub struct State {
    pub s: f64,
    pub y: [f64; 4],
    pub density: crate::diagnostics::Density,
    pub active: [f64; 2],
    pub radiation: Owners,
    pub material: MaterialOwners,
    pub iterations: usize,
    pub norm: f64,
    pub n_ratio: f64,
    pub e_ratio: f64,
    pub accepted_trace: crate::diagnostics::Trace,
    pub trial_trace: crate::diagnostics::Trace,
}
impl State {
    pub fn new(cfg: &HistoryConfig, grid: &Grid) -> Fallible<Self> {
        let p = cfg.background.at_ln_a(cfg.start).map_err(err)?;
        let g = rei_microphysics::igm_state::IgmGasState::from_temperature(
            cfg.fractions,
            p.n_h_cm3,
            p.n_he_cm3,
            cfg.temperature_k,
        )
        .map_err(err)?;
        Ok(Self {
            s: cfg.start,
            y: material::values(&g),
            density: crate::diagnostics::Density::new(vec![0.; grid.nodes.len()]),
            active: [0.; 2],
            radiation: Owners::default(),
            material: MaterialOwners::default(),
            iterations: 0,
            norm: 0.,
            n_ratio: 0.,
            e_ratio: 0.,
            accepted_trace: Default::default(),
            trial_trace: Default::default(),
        })
    }
}
#[derive(Debug)]
pub struct Evaluation {
    pub r: [f64; 4],
    pub radiation: Radiation,
    pub material: MaterialOwners,
    pub trace: crate::diagnostics::Trace,
}
pub fn norm(r: [f64; 4]) -> f64 {
    (0..4).map(|i| r[i].abs() / TOL[i]).fold(0., f64::max)
}
pub fn evaluate(
    cfg: &HistoryConfig,
    grid: &Grid,
    old: &State,
    s1: f64,
    p: FlrwPoint,
    y: [f64; 4],
) -> Fallible<Evaluation> {
    crate::diagnostics::reset();
    // Endpoint admission is separate from every reconstructed stage.
    material::rhs(y, p)?;
    crate::diagnostics::stage(0, y, p)?;
    let p0 = cfg.background.at_ln_a(old.s).map_err(err)?;
    material::rhs(old.y, p0)?;
    let sm = (old.s + s1) * 0.5;
    if !(old.s < sm && sm < s1) {
        return Err("unresolved midpoint".into());
    }
    let pm = cfg.background.at_ln_a(sm).map_err(err)?;
    let ym: [f64; 4] = std::array::from_fn(|i| (old.y[i] + y[i]) * 0.5);
    let r = material::rhs(ym, pm)?;
    crate::diagnostics::stage(1, ym, pm)?;
    let dt = (s1 - old.s) / pm.hubble_per_s;
    let radiation = radiation::transaction_path(cfg, grid, old.y, y, old.s, s1, &old.density)?;
    let d = material::photo_delta(
        radiation.owners.an,
        radiation.owners.be,
        p.n_he_cm3 / p.n_h_cm3,
    );
    let res = assemble_residual(old.y, y, d, r.fraction_dt, r.w_dt_erg_per_h_s, dt)?;
    Ok(Evaluation {
        r: res,
        radiation,
        material: MaterialOwners::stage(r, pm, s1 - old.s)?,
        trace: crate::diagnostics::snapshot(),
    })
}
/// Shared residual assembly, also used by explicitly labelled mathematical controls.
pub fn assemble_residual(
    old: [f64; 4],
    y: [f64; 4],
    d: [f64; 4],
    fraction_dt: [f64; 3],
    w_dt: f64,
    dt: f64,
) -> Fallible<[f64; 4]> {
    let mut res = [0.; 4];
    for i in 0..3 {
        res[i] = checked(y[i] - old[i] - d[i] - dt * fraction_dt[i])?;
    }
    res[3] = checked(y[3] - old[3] - d[3] - dt * w_dt)?;
    Ok(res)
}
pub fn linear(mut a: [[f64; 4]; 4], mut b: [f64; 4]) -> Fallible<[f64; 4]> {
    for k in 0..4 {
        let scale = (0..4).map(|i| a[i][k].abs()).fold(0., f64::max);
        let pivot = (k..4)
            .max_by(|&i, &j| a[i][k].abs().total_cmp(&a[j][k].abs()))
            .unwrap();
        let p = a[pivot][k];
        if !p.is_finite() || !scale.is_finite() || p.abs() <= 1e-14 * scale {
            return Err(format!("singular/nonfinite Jacobian column {k}"));
        }
        a.swap(k, pivot);
        b.swap(k, pivot);
        for i in k + 1..4 {
            let q = a[i][k] / a[k][k];
            for j in k..4 {
                a[i][j] -= q * a[k][j];
            }
            b[i] -= q * b[k];
        }
    }
    let mut x = [0.; 4];
    for i in (0..4).rev() {
        x[i] = checked((b[i] - (i + 1..4).map(|j| a[i][j] * x[j]).sum::<f64>()) / a[i][i])?;
    }
    Ok(x)
}
pub fn budget(cfg: &HistoryConfig, state: &State, initial_material: f64) -> Fallible<[f64; 4]> {
    let p = cfg.background.at_ln_a(state.s).map_err(err)?;
    let o = state.radiation;
    let m = state.material;
    let n = state.active[0] + o.an.iter().sum::<f64>() + o.outn - o.qn;
    let e = state.y[3] + material::binding(state.y, p.n_he_cm3 / p.n_h_cm3) + state.active[1]
        - initial_material
        + o.oute
        + o.red
        + m.escape
        + m.work
        + m.cmb
        - o.qe;
    let na = 1e-10 * o.qn.max(1e-10);
    let ea = 1e-10 * (o.qe + m.work + m.escape + m.cmb.abs()).max(1e-20);
    Ok([checked(n)?, checked(e)?, n.abs() / na, e.abs() / ea])
}
/// Private candidate assembly. The immutable input is never changed on rejection.
fn commit_candidate(
    cfg: &HistoryConfig,
    old: &State,
    s1: f64,
    y: [f64; 4],
    ev: Evaluation,
    it: usize,
    initial_material: f64,
) -> Fallible<State> {
    let mut cumulative = old.radiation;
    let mut inc = ev.radiation.owners;
    let active = [inc.n, inc.u];
    inc.n = 0.;
    inc.u = 0.;
    inc.ln_n = None;
    inc.ln_u = None;
    v2::try_add_scaled(&mut cumulative, inc, 1.).map_err(err)?;
    let mut candidate = State {
        s: s1,
        y,
        density: ev.radiation.density,
        active,
        radiation: cumulative,
        material: old.material.plus(ev.material)?,
        iterations: it,
        norm: norm(ev.r),
        n_ratio: 0.,
        e_ratio: 0.,
        accepted_trace: ev.trace,
        trial_trace: Default::default(),
    };
    let b = budget(cfg, &candidate, initial_material)?;
    candidate.n_ratio = b[2];
    candidate.e_ratio = b[3];
    if b[2] > 1. || b[3] > 1. {
        return Err(format!(
            "original budget rejects candidate: N_ratio={:.17e} E_ratio={:.17e}",
            b[2], b[3]
        ));
    }
    Ok(candidate)
}
pub fn advance(
    cfg: &HistoryConfig,
    grid: &Grid,
    old: &State,
    s1: f64,
    initial_material: f64,
) -> Fallible<State> {
    if !(s1 > old.s && s1 <= cfg.start + cfg.max_dln_a) {
        return Err("outside short interval".into());
    }
    let p = cfg.background.at_ln_a(s1).map_err(err)?;
    let mut y = old.y;
    let mut trials = crate::diagnostics::Trace::default();
    for iteration in 0..=16 {
        let base = evaluate(cfg, grid, old, s1, p, y)?;
        let n = norm(base.r);
        if n <= 1. {
            let mut committed =
                commit_candidate(cfg, old, s1, y, base, iteration, initial_material)?;
            committed.trial_trace = trials;
            return Ok(committed);
        }
        trials.merge(base.trace);
        if iteration == 16 {
            return Err(format!("Newton 16-iteration cap, norm={n:e}"));
        }
        let mut jac = [[0.; 4]; 4];
        for j in 0..4 {
            let increment = 1e-7 * y[j].abs().max(if j == 3 { 1e-15 } else { 1e-6 });
            let mut trial = y;
            trial[j] += increment;
            let mut d = increment;
            // Only gas/provider admission allows a backward finite difference.
            if material::rhs(trial, p).is_err() {
                trial = y;
                trial[j] -= increment;
                d = -increment;
                material::rhs(trial, p)?;
            }
            let pert = evaluate(cfg, grid, old, s1, p, trial)?;
            trials.merge(pert.trace);
            for i in 0..4 {
                jac[i][j] = checked((pert.r[i] - base.r[i]) / d)?;
            }
        }
        let delta = linear(jac, base.r.map(|r| -r))?;
        let mut accepted = None;
        for line in 0..12 {
            let alpha = 2f64.powi(-line);
            let trial = std::array::from_fn(|i| y[i] + alpha * delta[i]);
            if material::rhs(trial, p).is_err() {
                continue;
            }
            let test = evaluate(cfg, grid, old, s1, p, trial)?;
            trials.merge(test.trace);
            if norm(test.r) < n {
                accepted = Some(trial);
                break;
            }
        }
        y = accepted.ok_or_else(|| format!("12-trial line search failed, norm={n:e}"))?;
    }
    Err("unreachable solver cap".into())
}
