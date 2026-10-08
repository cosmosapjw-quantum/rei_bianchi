//! Opt-in first-order step-doubling control for the fixed continuous spectrum.
//! Local estimates are not global error certificates. The fixed driver is unchanged.
use crate::{
    igm_continuous::{ContinuousHistory, ContinuousState, ContinuousTrial},
    igm_history::Ledger,
    ForwardError, HHeModel,
};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum MicrostepPolicy {
    Strict,
    GuardedResearch,
}
#[derive(Clone, Debug)]
pub struct AdaptiveControl {
    pub relative: f64,
    pub fraction_atol: f64,
    pub temperature_atol: f64,
    pub energy_atol: f64,
    pub count_atol: f64,
    pub gamma_atol: f64,
    pub heat_atol: f64,
    pub safety: f64,
    pub min_factor: f64,
    pub max_factor: f64,
    pub max_attempts: usize,
    pub max_trial_evaluations: usize,
    pub microstep_policy: MicrostepPolicy,
    pub microstep_motion_limit: f64,
}
impl Default for AdaptiveControl {
    fn default() -> Self {
        Self {
            relative: 1e-6,
            fraction_atol: 1e-10,
            temperature_atol: 1e-8,
            energy_atol: 1e-24,
            count_atol: 1e-12,
            gamma_atol: 1e-26,
            heat_atol: 1e-36,
            safety: 0.9,
            min_factor: 0.1,
            max_factor: 2.0,
            max_attempts: 32,
            max_trial_evaluations: 10_000_000,
            microstep_policy: MicrostepPolicy::Strict,
            microstep_motion_limit: 1.0,
        }
    }
}
impl AdaptiveControl {
    fn valid(&self) -> bool {
        [
            self.relative,
            self.fraction_atol,
            self.temperature_atol,
            self.energy_atol,
            self.count_atol,
            self.gamma_atol,
            self.heat_atol,
            self.microstep_motion_limit,
        ]
        .iter()
        .all(|x| x.is_normal() && *x > 0.0)
            && self.safety > 0.0
            && self.safety < 1.0
            && self.min_factor > 0.0
            && self.min_factor < 1.0
            && self.max_factor.is_finite()
            && self.max_factor >= 1.0
            && self.max_attempts > 0
            && self.max_trial_evaluations > 0
            && self.microstep_motion_limit <= 1.0
    }
}
#[derive(Clone, Debug, Default)]
pub struct AdaptiveDiagnostics {
    pub accepted_macros: usize,
    pub rejected_lte: usize,
    pub rejected_physical: usize,
    pub trial_evaluations: usize,
    pub guarded_microsteps: usize,
    pub last_error: f64,
    pub max_error: f64,
    pub last_guard: f64,
    pub max_guard: f64,
    pub last_was_guarded: bool,
    pub last_error_factor: f64,
    pub last_attempt_error: Option<f64>,
    pub last_attempt_component: &'static str,
    pub last_attempt_width: f64,
    pub last_failure_code: &'static str,
    pub last_trial_phase: &'static str,
    pub worst_component: &'static str,
    pub microsteps: Vec<MicrostepRecord>,
}
#[derive(Clone, Debug)]
pub struct MicrostepRecord {
    pub boundary_kind: &'static str,
    pub events: Vec<EventIdentity>,
    pub field_motion: Vec<(&'static str, f64, f64)>,
    pub fraction_equation_defect: [f64; 3],
    pub energy_equation_defect: f64,
    /// Rates exclude the exactly applied support/export event map.
    pub post_event_rate_guard: bool,
    pub start: f64,
    pub end: f64,
    pub proper_dt: f64,
    pub max_motion_ratio: f64,
    pub worst_component: &'static str,
}
#[derive(Clone, Debug)]
pub struct EventIdentity {
    pub node: usize,
    pub kind: &'static str,
    pub at: f64,
    pub energy_ev: f64,
}
#[derive(Clone, Debug)]
pub struct AdaptiveState {
    pub state: ContinuousState,
    pub diagnostics: AdaptiveDiagnostics,
}
impl AdaptiveState {
    pub fn new(state: ContinuousState) -> Self {
        Self {
            state,
            diagnostics: AdaptiveDiagnostics::default(),
        }
    }
}
#[derive(Clone, Debug)]
pub struct AdaptiveFailure {
    pub reason: &'static str,
    pub diagnostics: Box<AdaptiveDiagnostics>,
}
impl std::fmt::Display for AdaptiveFailure {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(self.reason)
    }
}
impl std::error::Error for AdaptiveFailure {}
#[derive(Clone, Debug, Default)]
pub struct ErrorEstimate {
    pub max_ratio: f64,
    pub worst_component: &'static str,
}
impl ErrorEstimate {
    fn include(&mut self, name: &'static str, ratio: f64) -> Result<(), ForwardError> {
        if !ratio.is_finite() || ratio < 0.0 {
            return Err(ForwardError::InvalidInput("ADAPTIVE_NONFINITE_ERROR"));
        }
        if ratio > self.max_ratio {
            self.max_ratio = ratio;
            self.worst_component = name;
        }
        Ok(())
    }
}
#[derive(Clone, Debug)]
pub struct AdaptiveIntegrator {
    pub history: ContinuousHistory,
    pub control: AdaptiveControl,
}
fn ratio(a: f64, b: f64, atol: f64, rtol: f64) -> f64 {
    let scale = atol + rtol * a.abs().max(b.abs());
    if !a.is_finite() || !b.is_finite() || !scale.is_finite() || scale <= 0.0 {
        f64::NAN
    } else {
        (a - b).abs() / scale
    }
}
fn log_add(a: f64, b: f64) -> f64 {
    let hi = a.max(b);
    if hi == f64::NEG_INFINITY {
        hi
    } else {
        hi + (a.min(b) - hi).exp().ln_1p()
    }
}
fn log_difference(a: f64, b: f64) -> f64 {
    if a == b {
        return f64::NEG_INFINITY;
    }
    let hi = a.max(b);
    let lo = a.min(b);
    hi + (-(lo - hi).exp_m1()).ln()
}
fn ledger_values(l: &Ledger) -> [(&'static str, f64, bool); 30] {
    [
        ("emitted_N", l.emitted_n, false),
        ("emitted_E", l.emitted_e, true),
        ("abs_HI", l.absorption[0], false),
        ("abs_HeI", l.absorption[1], false),
        ("abs_HeII", l.absorption[2], false),
        ("out_N", l.out_n, false),
        ("out_E", l.out_e, true),
        ("redshift_E", l.redshift_e, true),
        ("escape_E", l.escape_e, true),
        ("work_E", l.work_e, true),
        ("cmb_reservoir_E", l.cmb_e, true),
        ("cmb_absolute_exchange_E", l.cmb_abs_e, true),
        ("ci_HI", l.ci[0], false),
        ("ci_HeI", l.ci[1], false),
        ("ci_HeII", l.ci[2], false),
        ("rr_HII", l.rr[0], false),
        ("rr_HeII", l.rr[1], false),
        ("rr_HeIII", l.rr[2], false),
        ("dr_HeII", l.dr, false),
        ("ci_floor_HI", l.floor[0], false),
        ("ci_floor_HeI", l.floor[1], false),
        ("ci_floor_HeII", l.floor[2], false),
        ("ce_cap_HI_E", l.cap_e[0], true),
        ("ce_cap_HeI_E", l.cap_e[1], true),
        ("ce_cap_HeII_E", l.cap_e[2], true),
        ("excluded_dr_E", l.excluded_dr_e, true),
        ("underflow_N", l.underflow_n_bound, false),
        ("underflow_E", l.underflow_e_bound, true),
        ("absorbed_N", l.absorption.iter().sum(), false),
        (
            "chemical_N",
            l.ci.iter().chain(l.rr.iter()).sum::<f64>() + l.dr,
            false,
        ),
    ]
}
impl AdaptiveIntegrator {
    pub fn new(
        history: ContinuousHistory,
        control: AdaptiveControl,
    ) -> Result<Self, AdaptiveFailure> {
        if !control.valid() {
            return Err(AdaptiveFailure {
                reason: "ADAPTIVE_INVALID_CONTROL",
                diagnostics: Default::default(),
            });
        }
        Ok(Self { history, control })
    }
    fn failure(&self, reason: &'static str, diagnostics: &AdaptiveDiagnostics) -> AdaptiveFailure {
        AdaptiveFailure {
            reason,
            diagnostics: Box::new(diagnostics.clone()),
        }
    }
    fn state_valid(&self, s: &ContinuousState) -> bool {
        let h = &self.history;
        let gas_valid = h
            .config
            .background
            .at_ln_a(s.ln_a)
            .and_then(|p| s.gas.eos(p.n_h_cm3, p.n_he_cm3))
            .is_ok_and(|eos| {
                eos.temperature_k.is_finite() && (1.0..=1e6).contains(&eos.temperature_k)
            });
        gas_valid
            && ledger_values(&s.ledger)
                .iter()
                .all(|(_, value, _)| value.is_finite())
            && s.max_residual.is_finite()
            && s.max_residual >= 0.0
            && s.ln_a.is_finite()
            && s.ln_a >= h.config.start
            && s.ln_a <= h.config.end
            && s.next_dln_a.is_normal()
            && s.next_dln_a > 0.0
            && s.counts.len() == h.nodes.len()
            && s.log_counts.len() == h.nodes.len()
            && s.counts.iter().zip(&s.log_counts).all(|(n, l)| {
                n.is_finite()
                    && *n >= 0.0
                    && if n.is_normal() {
                        l.is_finite() && *l == n.ln()
                    } else if *n == 0.0 && *l == f64::NEG_INFINITY {
                        true
                    } else {
                        // Subnormal/zero readouts may round while the authoritative
                        // tail keeps attenuating; only underflow-scale logs belong here.
                        l.is_finite() && *l <= f64::MIN_POSITIVE.ln()
                    }
            })
    }
    fn diagnostics_valid(&self, s: &AdaptiveState) -> bool {
        let d = &s.diagnostics;
        let finite_nonnegative = |x: f64| x.is_finite() && x >= 0.0;
        [
            d.last_error,
            d.max_error,
            d.last_guard,
            d.max_guard,
            d.last_error_factor,
            d.last_attempt_width,
        ]
        .into_iter()
        .all(finite_nonnegative)
            && d.last_attempt_error.is_none_or(finite_nonnegative)
            && d.accepted_macros <= s.state.accepted_steps
            && d.trial_evaluations <= self.control.max_trial_evaluations
            && d.guarded_microsteps == d.microsteps.len()
            && d.microsteps.iter().all(|r| {
                r.start.is_finite()
                    && r.end.is_finite()
                    && r.start < r.end
                    && r.proper_dt.is_normal()
                    && r.proper_dt > 0.0
                    && finite_nonnegative(r.max_motion_ratio)
                    && finite_nonnegative(r.energy_equation_defect)
                    && r.fraction_equation_defect
                        .into_iter()
                        .all(finite_nonnegative)
                    && r.field_motion.iter().all(|(_, bound, ratio)| {
                        finite_nonnegative(*bound) && finite_nonnegative(*ratio)
                    })
                    && r.events.iter().all(|e| {
                        e.node < self.history.nodes.len()
                            && e.at.is_finite()
                            && (e.at == r.start || e.at == r.end)
                            && e.energy_ev.is_normal()
                            && e.energy_ev > 0.0
                    })
            })
    }
    fn trial(
        &self,
        s: &ContinuousState,
        t: f64,
        d: &mut AdaptiveDiagnostics,
    ) -> Result<(ContinuousTrial, usize), ForwardError> {
        if d.trial_evaluations >= self.control.max_trial_evaluations {
            return Err(ForwardError::InvalidInput("ADAPTIVE_MAX_WORK"));
        }
        d.trial_evaluations += 1;
        let middle = s.ln_a + 0.5 * (t - s.ln_a);
        let endpoint = !(s.ln_a < middle && middle < t);
        self.history
            .trial_with_increment(s, t, if endpoint { t } else { middle })
            .map(|v| (v, usize::from(endpoint)))
    }
    /// Max-norm physical endpoint defect, including cancellation-free photon L1 defects.
    /// This is a diagnostic between two same-time states, not an acceptance certificate.
    pub fn state_defect(
        &self,
        a: &ContinuousState,
        b: &ContinuousState,
    ) -> Result<ErrorEstimate, ForwardError> {
        if a.ln_a != b.ln_a || !self.state_valid(a) || !self.state_valid(b) {
            return Err(ForwardError::InvalidInput("ADAPTIVE_INVALID_STATE"));
        }
        let c = &self.control;
        let h = &self.history;
        let mut e = ErrorEstimate::default();
        let p = h.config.background.at_ln_a(a.ln_a)?;
        let ea = a.gas.eos(p.n_h_cm3, p.n_he_cm3)?;
        let eb = b.gas.eos(p.n_h_cm3, p.n_he_cm3)?;
        for (i, name) in ["x_hii", "x_heii", "x_heiii"].iter().enumerate() {
            e.include(
                name,
                ratio(
                    a.gas.fractions[i],
                    b.gas.fractions[i],
                    c.fraction_atol,
                    c.relative,
                ),
            )?;
        }
        e.include(
            "T",
            ratio(
                ea.temperature_k,
                eb.temperature_k,
                c.temperature_atol,
                c.relative,
            ),
        )?;
        e.include(
            "ne_per_h",
            ratio(
                ea.electron_density_cm3 / p.n_h_cm3,
                eb.electron_density_cm3 / p.n_h_cm3,
                c.fraction_atol,
                c.relative,
            ),
        )?;
        e.include(
            "w",
            ratio(
                a.gas.w_erg_per_h,
                b.gas.w_erg_per_h,
                c.energy_atol,
                c.relative,
            ),
        )?;
        let ra = h.radiation(a);
        let rb = h.radiation(b);
        e.include("Nactive", ratio(ra[0], rb[0], c.count_atol, c.relative))?;
        e.include("Eactive", ratio(ra[1], rb[1], c.energy_atol, c.relative))?;
        let mut ln = f64::NEG_INFINITY;
        let mut le = f64::NEG_INFINITY;
        for (i, (la, lb)) in a.log_counts.iter().zip(&b.log_counts).enumerate() {
            let defect = log_difference(*la, *lb);
            ln = log_add(ln, defect);
            le = log_add(
                le,
                defect + (h.energy(i, a.ln_a) * HHeModel::controlled_fixture().ev_erg).ln(),
            );
        }
        e.include(
            "photon_L1",
            (ln - (c.count_atol + c.relative * ra[0].max(rb[0])).ln()).exp(),
        )?;
        e.include(
            "photon_energy_L1",
            (le - (c.energy_atol + c.relative * ra[1].max(rb[1])).ln()).exp(),
        )?;
        let pa = h.endpoint_photo(a)?;
        let pb = h.endpoint_photo(b)?;
        for i in 0..3 {
            e.include(
                ["Gamma_hi", "Gamma_hei", "Gamma_heii"][i],
                ratio(
                    pa.input.gamma_s[i],
                    pb.input.gamma_s[i],
                    c.gamma_atol,
                    c.relative,
                ),
            )?;
            e.include(
                ["heat_hi", "heat_hei", "heat_heii"][i],
                ratio(
                    pa.input.heat_erg_per_absorber_s[i],
                    pb.input.heat_erg_per_absorber_s[i],
                    c.heat_atol,
                    c.relative,
                ),
            )?;
        }
        Ok(e)
    }
    fn pair_defect(
        &self,
        coarse: &ContinuousTrial,
        half1: &ContinuousTrial,
        half2: &ContinuousTrial,
    ) -> Result<ErrorEstimate, ForwardError> {
        let mut e = self.state_defect(&coarse.state, &half2.state)?;
        let c = &self.control;
        for (((name, a, energy), (_, b, _)), (_, d, _)) in ledger_values(&coarse.delta)
            .into_iter()
            .zip(ledger_values(&half1.delta))
            .zip(ledger_values(&half2.delta))
        {
            e.include(
                name,
                ratio(
                    a,
                    b + d,
                    if energy { c.energy_atol } else { c.count_atol },
                    c.relative,
                ),
            )?;
        }
        e.include(
            "photo_absorbed_energy",
            ratio(
                coarse.photo_energy,
                half1.photo_energy + half2.photo_energy,
                c.energy_atol,
                c.relative,
            ),
        )?;
        Ok(e)
    }
    fn motion_guard(
        &self,
        old: &ContinuousState,
        trial: &ContinuousTrial,
    ) -> Result<MicrostepRecord, ForwardError> {
        use crate::{igm_photo::packet_opacity_masked, verner_cutoff_ev, Absorber};
        let h = &self.history;
        let c = &self.control;
        let q = &trial.state;
        if !self.state_valid(q) {
            return Err(ForwardError::InvalidInput("ADAPTIVE_INVALID_STATE"));
        }
        let l = &trial.delta;
        let bg = h.config.background.at_ln_a(trial.stage)?;
        let r = bg.n_he_cm3 / bg.n_h_cm3;
        let model = HHeModel::controlled_fixture();
        let eo = old.gas.eos(bg.n_h_cm3, bg.n_he_cm3)?;
        let en = q.gas.eos(bg.n_h_cm3, bg.n_he_cm3)?;
        let xe0 = eo.electron_density_cm3 / bg.n_h_cm3;
        let xe1 = en.electron_density_cm3 / bg.n_h_cm3;
        let p0 = l.absorption[0] + l.ci[0] + l.rr[0];
        let p1 = l.absorption[1] + l.ci[1] + l.rr[1] + l.dr;
        let p2 = l.absorption[2] + l.ci[2] + l.rr[2];
        let raw = [
            p0,
            if r > 0.0 { (p1 + p2) / r } else { 0.0 },
            if r > 0.0 { p2 / r } else { 0.0 },
        ];
        let be = p0
            + p1
            + p2
            + trial.fraction_defect[0]
            + r * trial.fraction_defect[1]
            + 2.0 * r * trial.fraction_defect[2];
        let bw = trial.photo_energy
            + model.ev_erg * (0..3).map(|i| model.threshold_ev[i] * l.ci[i]).sum::<f64>()
            + l.escape_e
            + l.work_e
            + l.cmb_abs_e
            + trial.energy_defect;
        let bt = (2.0 * bw / (3.0 * model.kb_erg_k) + eo.temperature_k * be)
            / (1.0 + r).max(1.0 + r + xe0 - be);
        let mut estimate = ErrorEstimate::default();
        let mut fields = Vec::new();
        let mut include = |name: &'static str,
                           bound: f64,
                           a: f64,
                           b: f64,
                           atol: f64|
         -> Result<(), ForwardError> {
            if !bound.is_finite() || bound < 0.0 {
                return Err(ForwardError::InvalidInput("ADAPTIVE_NONFINITE_MOTION"));
            }
            // Enclose measured arithmetic motion too, without modifying the state.
            let bound = bound.max((b - a).abs()) * (1.0 + 64.0 * f64::EPSILON);
            let scale = atol + c.relative * a.abs().max(b.abs());
            if !a.is_finite() || !b.is_finite() || !scale.is_finite() || scale <= 0.0 {
                return Err(ForwardError::InvalidInput("ADAPTIVE_NONFINITE_MOTION"));
            }
            let v = bound / scale;
            estimate.include(name, v)?;
            fields.push((name, bound, v));
            Ok(())
        };
        for (i, name) in ["x_hii", "x_heii", "x_heiii"].iter().enumerate() {
            include(
                name,
                raw[i] + trial.fraction_defect[i],
                old.gas.fractions[i],
                q.gas.fractions[i],
                c.fraction_atol,
            )?;
        }
        include("ne_per_h", be, xe0, xe1, c.fraction_atol)?;
        include(
            "w",
            bw,
            old.gas.w_erg_per_h,
            q.gas.w_erg_per_h,
            c.energy_atol,
        )?;
        include(
            "T",
            bt,
            eo.temperature_k,
            en.temperature_k,
            c.temperature_atol,
        )?;
        let ro = h.radiation(old);
        let rn = h.radiation(q);
        include(
            "Nactive",
            l.emitted_n + l.absorption.iter().sum::<f64>() + l.out_n,
            ro[0],
            rn[0],
            c.count_atol,
        )?;
        include(
            "Eactive",
            l.emitted_e + trial.photo_energy + l.out_e + l.redshift_e.abs(),
            ro[1],
            rn[1],
            c.energy_atol,
        )?;
        for (name, value, energy) in ledger_values(l) {
            include(
                name,
                value.abs(),
                0.0,
                value,
                if energy { c.energy_atol } else { c.count_atol },
            )?;
        }
        // Bound reaction-induced rate motion at the same post-event endpoint.
        // Exact support/export jumps are deterministic event maps, not LTE.
        let mut stock = q.clone();
        stock.counts.clone_from(&old.counts);
        stock.log_counts.clone_from(&old.log_counts);
        let mut motion = q.clone();
        let absorbers = [Absorber::HI, Absorber::HeI, Absorber::HeII];
        for i in 0..h.nodes.len() {
            let masks = std::array::from_fn(|k| {
                h.nodes[i].eta - verner_cutoff_ev(absorbers[k]).ln() > old.ln_a
            });
            let k = packet_opacity_masked(
                &q.gas,
                h.energy(i, trial.stage),
                masks,
                bg.n_h_cm3,
                bg.n_he_cm3,
            )?
            .iter()
            .sum::<f64>();
            let injected = trial.proper_dt * trial.source_rates[i];
            let survivor = (old.counts[i] + injected) / (1.0 + trial.proper_dt * k);
            let gross = injected + trial.proper_dt * k * survivor;
            motion.counts[i] = gross;
            motion.log_counts[i] = if gross > 0.0 {
                gross.ln()
            } else {
                f64::NEG_INFINITY
            };
            if q.ln_a >= h.nodes[i].eta - verner_cutoff_ev(Absorber::HI).ln() {
                stock.counts[i] = 0.0;
                stock.log_counts[i] = f64::NEG_INFINITY;
                motion.counts[i] = 0.0;
                motion.log_counts[i] = f64::NEG_INFINITY;
            }
        }
        let po = h.endpoint_photo(&stock)?;
        let pn = h.endpoint_photo(q)?;
        let pm = h.endpoint_photo(&motion)?;
        for i in 0..3 {
            include(
                ["Gamma_hi", "Gamma_hei", "Gamma_heii"][i],
                pm.input.gamma_s[i],
                po.input.gamma_s[i],
                pn.input.gamma_s[i],
                c.gamma_atol,
            )?;
            include(
                ["heat_hi", "heat_hei", "heat_heii"][i],
                pm.input.heat_erg_per_absorber_s[i],
                po.input.heat_erg_per_absorber_s[i],
                pn.input.heat_erg_per_absorber_s[i],
                c.heat_atol,
            )?;
        }
        let mut events = Vec::new();
        for (node, n) in h.nodes.iter().enumerate() {
            for (kind, energy) in [
                ("source_entry", h.config.source.energy_max_ev),
                ("source_exit", h.config.source.energy_min_ev),
                ("HI_cutoff", verner_cutoff_ev(Absorber::HI)),
                ("HeI_cutoff", verner_cutoff_ev(Absorber::HeI)),
                ("HeII_cutoff", verner_cutoff_ev(Absorber::HeII)),
            ] {
                let at = n.eta - energy.ln();
                if at == old.ln_a || at == q.ln_a {
                    events.push(EventIdentity {
                        node,
                        kind,
                        at,
                        energy_ev: energy,
                    });
                }
            }
        }
        let boundary_kind = if h.events.binary_search_by(|x| x.total_cmp(&q.ln_a)).is_ok() {
            "physical_event"
        } else if q.ln_a == h.config.end {
            "final_endpoint"
        } else {
            "requested_endpoint"
        };
        Ok(MicrostepRecord {
            boundary_kind,
            events,
            start: old.ln_a,
            end: q.ln_a,
            proper_dt: trial.proper_dt,
            max_motion_ratio: estimate.max_ratio,
            worst_component: estimate.worst_component,
            field_motion: fields,
            fraction_equation_defect: trial.fraction_defect,
            energy_equation_defect: trial.energy_defect,
            post_event_rate_guard: true,
        })
    }
    pub fn advance_to(
        &self,
        s: &AdaptiveState,
        end: f64,
    ) -> Result<AdaptiveState, AdaptiveFailure> {
        if !self.control.valid()
            || !end.is_finite()
            || end < s.state.ln_a
            || end > self.history.config.end
            || !self.state_valid(&s.state)
            || !self.diagnostics_valid(s)
        {
            return Err(self.failure("ADAPTIVE_INVALID_INPUT", &s.diagnostics));
        }
        let mut q = s.clone();
        while q.state.ln_a < end {
            q = self.advance_one(&q, end)?;
        }
        Ok(q)
    }
    pub fn advance_one(
        &self,
        s: &AdaptiveState,
        end: f64,
    ) -> Result<AdaptiveState, AdaptiveFailure> {
        let h = &self.history;
        let c = &self.control;
        let old = &s.state;
        let mut d = s.diagnostics.clone();
        if !c.valid()
            || !self.state_valid(old)
            || !self.diagnostics_valid(s)
            || !end.is_finite()
            || end <= old.ln_a
            || end > h.config.end
        {
            return Err(self.failure("ADAPTIVE_INVALID_INPUT", &d));
        }
        if old.accepted_steps >= h.config.max_steps {
            return Err(self.failure("ADAPTIVE_MAX_STEPS", &d));
        }
        let ei = h.events.partition_point(|v| *v <= old.ln_a);
        let limit = h.events.get(ei).copied().unwrap_or(end).min(end);
        let proposed = old.next_dln_a.min(h.config.max_dln_a);
        let mut dx = proposed.min(limit - old.ln_a);
        for attempt in 0..c.max_attempts {
            let t = if dx >= limit - old.ln_a {
                limit
            } else {
                old.ln_a + dx
            };
            dx = t - old.ln_a;
            if !t.is_finite() || t <= old.ln_a {
                return Err(self.failure("ADAPTIVE_NO_PROGRESS", &d));
            }
            d.last_attempt_width = dx;
            d.last_attempt_error = None;
            let mid = old.ln_a + 0.5 * dx;
            if !(old.ln_a < mid && mid < t) {
                if c.microstep_policy == MicrostepPolicy::Strict || t != limit {
                    return Err(self.failure("ADAPTIVE_UNSPLITTABLE_EVENT", &d));
                }
                d.last_trial_phase = "unsplittable";
                let (trial, nstage) = self
                    .trial(old, t, &mut d)
                    .map_err(|e| self.failure(e.code(), &d))?;
                let record = self
                    .motion_guard(old, &trial)
                    .map_err(|e| self.failure(e.code(), &d))?;
                d.last_guard = record.max_motion_ratio;
                d.max_guard = d.max_guard.max(record.max_motion_ratio);
                d.worst_component = record.worst_component;
                if record.max_motion_ratio > c.microstep_motion_limit {
                    d.microsteps.push(record);
                    return Err(self.failure("ADAPTIVE_MICROSTEP_GUARD", &d));
                }
                let mut state = trial.state;
                state.accepted_steps = old.accepted_steps + 1;
                state.endpoint_stage_steps = old.endpoint_stage_steps + nstage;
                state.next_dln_a = proposed;
                d.accepted_macros += 1;
                d.guarded_microsteps += 1;
                d.last_was_guarded = true;
                d.microsteps.push(record);
                return Ok(AdaptiveState {
                    state,
                    diagnostics: d,
                });
            }
            if old
                .accepted_steps
                .checked_add(2)
                .is_none_or(|v| v > h.config.max_steps)
            {
                return Err(self.failure("ADAPTIVE_MAX_STEPS", &d));
            }
            let attempt_result = (|| {
                d.last_trial_phase = "coarse";
                let (coarse, _) = self.trial(old, t, &mut d)?;
                d.last_trial_phase = "first_half";
                let (half1, n1) = self.trial(old, mid, &mut d)?;
                d.last_trial_phase = "second_half";
                let (mut half2, n2) = self.trial(&half1.state, t, &mut d)?;
                let mut estimate = self.pair_defect(&coarse, &half1, &half2)?;
                let h1 = mid - old.ln_a;
                let h2 = t - mid;
                let split_ratio = h1 / h2;
                estimate.max_ratio *= 0.5 * (split_ratio + 1.0 / split_ratio);
                half2.state.endpoint_stage_steps = old.endpoint_stage_steps + n1 + n2;
                Ok::<_, ForwardError>((
                    half2.state,
                    estimate,
                    0.5 * (split_ratio + 1.0 / split_ratio),
                ))
            })();
            let factor = match attempt_result {
                Ok((mut state, estimate, error_factor)) => {
                    let err = estimate.max_ratio;
                    d.last_attempt_error = Some(err);
                    d.last_attempt_component = estimate.worst_component;
                    let factor = if err == 0.0 {
                        c.max_factor
                    } else {
                        (c.safety * err.powf(-0.5)).clamp(c.min_factor, c.max_factor)
                    };
                    if err <= 1.0 {
                        state.accepted_steps = old.accepted_steps + 2;
                        state.rejected_steps = old.rejected_steps
                            + (d.rejected_lte - s.diagnostics.rejected_lte)
                            + (d.rejected_physical - s.diagnostics.rejected_physical);
                        state.next_dln_a = if attempt == 0 && t == limit && dx < proposed {
                            proposed
                        } else {
                            (dx * factor).min(h.config.max_dln_a)
                        };
                        d.accepted_macros += 1;
                        d.last_error = err;
                        d.last_error_factor = error_factor;
                        d.max_error = d.max_error.max(err);
                        d.last_was_guarded = false;
                        d.worst_component = estimate.worst_component;
                        return Ok(AdaptiveState {
                            state,
                            diagnostics: d,
                        });
                    }
                    d.rejected_lte += 1;
                    factor.min(0.9)
                }
                Err(e) => {
                    d.last_failure_code = e.code();
                    if e.code() == "ADAPTIVE_MAX_WORK" {
                        return Err(self.failure("ADAPTIVE_MAX_WORK", &d));
                    }
                    d.rejected_physical += 1;
                    0.5
                }
            };
            dx *= factor;
            if dx < h.config.min_dln_a {
                return Err(self.failure("ADAPTIVE_MIN_STEP", &d));
            }
        }
        Err(self.failure("ADAPTIVE_MAX_ATTEMPTS", &d))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn neutral_pair_has_first_order_be_error_divisor_one() {
        let mut c = crate::igm_config::parse_config(include_str!(
            "../../../configs/igm_manufactured_v1.cfg"
        ))
        .unwrap();
        c.source.photons_per_h_per_s = 0.0;
        c.fractions = [0.0; 3];
        let (h, s) = ContinuousHistory::new(c, 1).unwrap();
        let mut defects = Vec::new();
        for width in [1e-3, 5e-4] {
            let t = s.ln_a + width;
            let m = s.ln_a + 0.5 * (t - s.ln_a);
            let coarse = h.trial_with_increment(&s, t, m).unwrap();
            let first = h
                .trial_with_increment(&s, m, s.ln_a + 0.5 * (m - s.ln_a))
                .unwrap();
            let fine = h
                .trial_with_increment(&first.state, t, m + 0.5 * (t - m))
                .unwrap();
            let exact = s.gas.w_erg_per_h * (-2.0 * (t - s.ln_a)).exp();
            let defect = (fine.state.gas.w_erg_per_h - coarse.state.gas.w_erg_per_h).abs();
            let quotient = (fine.state.gas.w_erg_per_h - exact).abs() / defect;
            assert!((0.99..1.01).contains(&quotient), "{quotient}");
            defects.push(defect);
        }
        assert!((3.9..4.1).contains(&(defects[0] / defects[1])));
    }
    #[test]
    fn nonfinite_motion_envelope_cannot_fall_back_to_measured_change() {
        let c = crate::igm_config::parse_config(include_str!(
            "../../../configs/igm_manufactured_v1.cfg"
        ))
        .unwrap();
        let (h, s) = ContinuousHistory::new(c, 1).unwrap();
        let i = AdaptiveIntegrator::new(h, Default::default()).unwrap();
        let mut q = s.clone();
        q.ln_a = f64::from_bits(s.ln_a.to_bits() - 1);
        let trial = ContinuousTrial {
            state: q.clone(),
            delta: Default::default(),
            proper_dt: 1.0,
            stage: q.ln_a,
            source_rates: vec![0.0; s.counts.len()],
            photo_energy: 0.0,
            fraction_defect: [0.0; 3],
            energy_defect: f64::NAN,
        };
        assert!(
            i.motion_guard(&s, &trial).is_err(),
            "NaN gross bound must not become a finite measured-only guard"
        );
    }
}
