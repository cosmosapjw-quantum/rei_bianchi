//! Continuous proper emissivity on fixed comoving log-energy characteristics.
//!
//! Additive research path. Spectral quadrature and first-order coupled BE errors
//! require independent refinement; conservation is not an accuracy certificate.
use crate::{
    coupled_primary::PrimaryPacket,
    igm_config::HistoryConfig,
    igm_history::Ledger,
    igm_photo::{igm_photo_rates, packet_opacity_masked},
    igm_state::IgmGasState,
    igm_step::{implicit_step_with_source_masked, StepBackground, StepControl},
    verner_cutoff_ev, Absorber, ForwardError, HHeModel,
};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum SpectralGrid {
    Uniform,
    ThresholdBands,
}
impl SpectralGrid {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Uniform => "uniform",
            Self::ThresholdBands => "threshold-bands",
        }
    }
}
#[derive(Clone, Copy, Debug)]
pub struct CharacteristicNode {
    pub eta: f64,
    pub weight: f64,
}
#[derive(Clone, Debug)]
pub struct ContinuousState {
    pub ln_a: f64,
    pub gas: IgmGasState,
    /// One count per fixed characteristic, including zero and extinct nodes.
    pub counts: Vec<f64>,
    /// Authoritative tail bookkeeping. -infinity means never populated or exported.
    pub log_counts: Vec<f64>,
    pub ledger: Ledger,
    pub next_dln_a: f64,
    pub accepted_steps: usize,
    pub endpoint_stage_steps: usize,
    pub rejected_steps: usize,
    pub max_residual: f64,
}
/// Private-trial diagnostics computed before cumulative-ledger addition.
/// The fixed driver discards these; its arithmetic/acceptance is unchanged.
#[derive(Clone, Debug)]
pub(crate) struct ContinuousTrial {
    pub state: ContinuousState,
    pub delta: Ledger,
    pub proper_dt: f64,
    pub stage: f64,
    pub source_rates: Vec<f64>,
    pub photo_energy: f64,
    pub fraction_defect: [f64; 3],
    pub energy_defect: f64,
}
#[derive(Clone, Debug)]
pub struct ContinuousHistory {
    pub config: HistoryConfig,
    pub nodes: Vec<CharacteristicNode>,
    pub spectral_panels: usize,
    pub spectral_grid: SpectralGrid,
    pub events: Vec<f64>,
    pub initial_material: f64,
}
fn invalid() -> ForwardError {
    ForwardError::InvalidInput("IGM_CONTINUOUS_REJECTED")
}
fn binding(g: &IgmGasState, ratio: f64) -> f64 {
    let c = HHeModel::controlled_fixture();
    c.ev_erg
        * (c.threshold_ev[0] * g.fractions[0]
            + ratio
                * (c.threshold_ev[1] * g.fractions[1]
                    + (c.threshold_ev[1] + c.threshold_ev[2]) * g.fractions[2]))
}
impl ContinuousHistory {
    pub fn new(
        config: HistoryConfig,
        spectral_panels: usize,
    ) -> Result<(Self, ContinuousState), ForwardError> {
        Self::new_with_grid(config, spectral_panels, SpectralGrid::Uniform)
    }
    pub fn new_with_grid(
        config: HistoryConfig,
        spectral_panels: usize,
        spectral_grid: SpectralGrid,
    ) -> Result<(Self, ContinuousState), ForwardError> {
        if spectral_panels == 0
            || spectral_panels > config.max_packets / 2
            || config.start >= config.end
            || !config.max_dln_a.is_normal()
            || config.max_dln_a <= 0.0
            || !config.min_dln_a.is_normal()
            || config.min_dln_a <= 0.0
            || config.min_dln_a > config.max_dln_a
        {
            return Err(invalid());
        }
        // Validate the unchanged analytic SED/provider domain; never normalize a
        // finite quadrature to conceal source-moment error.
        config.source.energy_quadrature(1)?;
        let lo = config.source.energy_min_ev.ln() + config.start;
        let hi = config.source.energy_max_ev.ln() + config.end;
        let mut edges = vec![lo, hi];
        if spectral_grid == SpectralGrid::ThresholdBands {
            for energy in [
                config.source.energy_min_ev,
                config.source.energy_max_ev,
                verner_cutoff_ev(Absorber::HI),
                verner_cutoff_ev(Absorber::HeI),
                verner_cutoff_ev(Absorber::HeII),
            ] {
                for epoch in [config.start, config.end] {
                    let edge = epoch + energy.ln();
                    if lo < edge && edge < hi {
                        edges.push(edge);
                    }
                }
            }
            edges.sort_by(f64::total_cmp);
            edges.dedup();
        }
        let count = spectral_panels
            .checked_mul(2)
            .and_then(|n| n.checked_mul(edges.len() - 1))
            .ok_or_else(invalid)?;
        if count > config.max_packets {
            return Err(invalid());
        }
        let mut nodes = Vec::new();
        nodes.try_reserve_exact(count).map_err(|_| invalid())?;
        for edge in edges.windows(2) {
            for panel in 0..spectral_panels {
                let left = edge[0] + (edge[1] - edge[0]) * panel as f64 / spectral_panels as f64;
                let right = if panel + 1 == spectral_panels {
                    edge[1]
                } else {
                    edge[0] + (edge[1] - edge[0]) * (panel + 1) as f64 / spectral_panels as f64
                };
                let half = 0.5 * (right - left);
                for side in [-1.0, 1.0] {
                    let eta = left + half * (1.0 + side / 3.0_f64.sqrt());
                    if !(left < eta && eta < right && half.is_normal()) {
                        return Err(invalid());
                    }
                    nodes.push(CharacteristicNode { eta, weight: half });
                }
            }
        }
        let mut events = Vec::new();
        for n in &nodes {
            for energy in [
                config.source.energy_min_ev,
                config.source.energy_max_ev,
                verner_cutoff_ev(Absorber::HI),
                verner_cutoff_ev(Absorber::HeI),
                verner_cutoff_ev(Absorber::HeII),
            ] {
                let event = n.eta - energy.ln();
                if config.start < event && event <= config.end {
                    events.push(event);
                }
            }
        }
        events.sort_by(f64::total_cmp);
        events.dedup();
        let p = config.background.at_ln_a(config.start)?;
        let gas = IgmGasState::from_temperature(
            config.fractions,
            p.n_h_cm3,
            p.n_he_cm3,
            config.temperature_k,
        )?;
        crate::igm_thermal::igm_point_rhs(
            &gas,
            p.n_h_cm3,
            p.n_he_cm3,
            p.hubble_per_s,
            p.tcmb_k,
            Default::default(),
        )?;
        let initial_material = gas.w_erg_per_h + binding(&gas, p.n_he_cm3 / p.n_h_cm3);
        let s = ContinuousState {
            ln_a: config.start,
            gas,
            counts: vec![0.0; nodes.len()],
            log_counts: vec![f64::NEG_INFINITY; nodes.len()],
            ledger: Ledger::default(),
            next_dln_a: config.max_dln_a,
            accepted_steps: 0,
            endpoint_stage_steps: 0,
            rejected_steps: 0,
            max_residual: 0.0,
        };
        Ok((
            Self {
                config,
                nodes,
                spectral_panels,
                spectral_grid,
                events,
                initial_material,
            },
            s,
        ))
    }
    pub fn energy(&self, index: usize, s: f64) -> f64 {
        let eta = self.nodes[index].eta;
        for a in [Absorber::HI, Absorber::HeI, Absorber::HeII] {
            let e = verner_cutoff_ev(a);
            if s == eta - e.ln() {
                return e;
            }
        }
        (eta - s).exp()
    }
    /// Proper source rate, before the single dln(a)/H clock conversion.
    /// On event-bounded intervals callers use an interior point.
    pub fn source_rate(&self, index: usize, s: f64) -> f64 {
        let n = self.nodes[index];
        let c = &self.config.source;
        let entry = n.eta - c.energy_max_ev.ln();
        let exit = n.eta - c.energy_min_ev.ln();
        if s <= entry || s >= exit {
            return 0.0;
        }
        c.photons_per_h_per_s * n.weight
            / ((1.0 / c.energy_min_ev - 1.0 / c.energy_max_ev) * self.energy(index, s))
    }
    pub fn packets(&self, s: &ContinuousState) -> Vec<PrimaryPacket> {
        s.counts
            .iter()
            .enumerate()
            .map(|(i, n)| PrimaryPacket {
                energy_ev: self.energy(i, s.ln_a),
                per_h: *n,
            })
            .collect()
    }
    pub fn radiation(&self, s: &ContinuousState) -> [f64; 2] {
        let ev = HHeModel::controlled_fixture().ev_erg;
        [
            s.counts.iter().sum(),
            s.counts
                .iter()
                .enumerate()
                .map(|(i, n)| n * self.energy(i, s.ln_a) * ev)
                .sum(),
        ]
    }
    pub fn balances(&self, s: &ContinuousState) -> Result<[f64; 2], ForwardError> {
        let p = self.config.background.at_ln_a(s.ln_a)?;
        let r = self.radiation(s);
        let l = &s.ledger;
        Ok([
            r[0] + l.absorption.iter().sum::<f64>() + l.out_n - l.emitted_n,
            s.gas.w_erg_per_h + binding(&s.gas, p.n_he_cm3 / p.n_h_cm3) + r[1]
                - self.initial_material
                + l.out_e
                + l.redshift_e
                + l.escape_e
                + l.work_e
                + l.cmb_e
                - l.emitted_e,
        ])
    }
    pub fn advance_to(
        &self,
        s: &ContinuousState,
        end: f64,
    ) -> Result<ContinuousState, ForwardError> {
        if !s.ln_a.is_finite()
            || s.ln_a < self.config.start
            || s.ln_a > self.config.end
            || !end.is_finite()
            || end < s.ln_a
            || end > self.config.end
        {
            return Err(invalid());
        }
        let mut q = s.clone();
        while q.ln_a < end {
            q = self.advance_one(&q, end)?;
        }
        Ok(q)
    }
    pub fn advance_one(
        &self,
        s: &ContinuousState,
        end: f64,
    ) -> Result<ContinuousState, ForwardError> {
        if !s.ln_a.is_finite()
            || s.ln_a < self.config.start
            || s.ln_a > self.config.end
            || !end.is_finite()
            || end <= s.ln_a
            || end > self.config.end
            || s.accepted_steps >= self.config.max_steps
            || s.counts.len() != self.nodes.len()
            || s.log_counts.len() != self.nodes.len()
        {
            return Err(invalid());
        }
        let event_index = self.events.partition_point(|v| *v <= s.ln_a);
        let limit = self
            .events
            .get(event_index)
            .copied()
            .unwrap_or(end)
            .min(end);
        let mut dx = s.next_dln_a.min(self.config.max_dln_a).min(limit - s.ln_a);
        let mut rejected = 0;
        loop {
            let t = if dx >= limit - s.ln_a {
                limit
            } else {
                s.ln_a + dx
            };
            dx = t - s.ln_a;
            if t <= s.ln_a {
                return Err(invalid());
            }
            let middle = s.ln_a + 0.5 * dx;
            // Adjacent representable events have no representable midpoint.
            // Integrate their positive width at the right endpoint; explicit
            // interval masks keep source/cross-section support one-sided.
            let endpoint_stage = !(s.ln_a < middle && middle < t);
            let mid = if endpoint_stage { t } else { middle };
            let result = self.trial(s, t, mid);
            match result {
                Ok(mut q) => {
                    q.accepted_steps = s.accepted_steps + 1;
                    q.endpoint_stage_steps = s.endpoint_stage_steps + usize::from(endpoint_stage);
                    q.rejected_steps = s.rejected_steps + rejected;
                    q.next_dln_a = if rejected == 0 && t == limit {
                        s.next_dln_a.min(self.config.max_dln_a)
                    } else {
                        (1.5 * dx).min(self.config.max_dln_a)
                    };
                    return Ok(q);
                }
                Err(e) => {
                    if std::env::var_os("IGM_TRACE_REJECT").is_some() {
                        eprintln!("continuous reject t={t} dx={dx}: {e}");
                    }
                }
            }
            rejected += 1;
            dx *= 0.5;
            if dx < self.config.min_dln_a {
                return Err(invalid());
            }
        }
    }
    fn trial(
        &self,
        s: &ContinuousState,
        t: f64,
        mid: f64,
    ) -> Result<ContinuousState, ForwardError> {
        self.trial_with_increment(s, t, mid)
            .map(|trial| trial.state)
    }
    pub(crate) fn trial_with_increment(
        &self,
        s: &ContinuousState,
        t: f64,
        mid: f64,
    ) -> Result<ContinuousTrial, ForwardError> {
        let p = self.config.background.at_ln_a(mid)?;
        let dt = (t - s.ln_a) / p.hubble_per_s;
        let photons: Vec<_> = s
            .counts
            .iter()
            .enumerate()
            .map(|(i, n)| PrimaryPacket {
                energy_ev: self.energy(i, mid),
                per_h: *n,
            })
            .collect();
        let src = &self.config.source;
        let normalization = 1.0 / src.energy_min_ev - 1.0 / src.energy_max_ev;
        let all_rates: Vec<_> = self
            .nodes
            .iter()
            .enumerate()
            .map(|(i, n)| {
                let entry = n.eta - src.energy_max_ev.ln();
                let exit = n.eta - src.energy_min_ev.ln();
                // No physical event lies strictly inside this segment. These
                // inequalities describe its open interior even when no floating
                // midpoint exists.
                if entry < t && exit > s.ln_a {
                    src.photons_per_h_per_s * n.weight / (normalization * photons[i].energy_ev)
                } else {
                    0.0
                }
            })
            .collect();
        for (i, rate) in all_rates.iter().enumerate() {
            let n = self.nodes[i];
            let active =
                n.eta - src.energy_max_ev.ln() < t && n.eta - src.energy_min_ev.ln() > s.ln_a;
            if !rate.is_finite()
                || *rate < 0.0
                || (active
                    && src.photons_per_h_per_s > 0.0
                    && (!rate.is_normal() || !(dt * rate).is_normal()))
            {
                return Err(invalid());
            }
        }
        let absorbers = [Absorber::HI, Absorber::HeI, Absorber::HeII];
        let masks: Vec<[bool; 3]> = self
            .nodes
            .iter()
            .map(|n| std::array::from_fn(|i| n.eta - verner_cutoff_ev(absorbers[i]).ln() > s.ln_a))
            .collect();
        let cutoff = verner_cutoff_ev(Absorber::HI);
        let rates: Vec<_> = all_rates
            .iter()
            .enumerate()
            .map(|(i, v)| if masks[i][0] { *v } else { 0.0 })
            .collect();
        let step = implicit_step_with_source_masked(
            &s.gas,
            &photons,
            &rates,
            &masks,
            StepBackground {
                n_h: p.n_h_cm3,
                n_he: p.n_he_cm3,
                hubble: p.hubble_per_s,
                tcmb: p.tcmb_k,
            },
            dt,
            StepControl {
                cumulative_count_scale: s.ledger.emitted_n.max(1e-10),
                cumulative_energy_scale: (s.ledger.emitted_e
                    + s.ledger.escape_e
                    + s.ledger.work_e
                    + s.ledger.cmb_abs_e
                    + s.ledger.redshift_e
                    + s.ledger.out_e)
                    .max(1e-20),
                ..StepControl::default()
            },
        )?;
        let mut q = s.clone();
        let mut delta = Ledger::default();
        q.ln_a = t;
        q.gas = step.gas;
        q.max_residual = q.max_residual.max(step.residual);
        let ev = HHeModel::controlled_fixture().ev_erg;
        let mut source_n = 0.0;
        let mut source_e = 0.0;
        for i in 0..self.nodes.len() {
            let e0 = self.energy(i, s.ln_a);
            let em = photons[i].energy_ev;
            let e1 = self.energy(i, t);
            let injected = dt * rates[i];
            let all_injected = dt * all_rates[i];
            let n = step.packets[i].per_h;
            source_n += injected;
            source_e += injected * em * ev;
            q.ledger.emitted_n += all_injected;
            delta.emitted_n += all_injected;
            q.ledger.emitted_e += all_injected * em * ev;
            delta.emitted_e += all_injected * em * ev;
            if rates[i] == 0.0 && all_rates[i] > 0.0 {
                q.ledger.out_n += all_injected;
                delta.out_n += all_injected;
                q.ledger.out_e += all_injected * em * ev;
                delta.out_e += all_injected * em * ev;
            }
            q.ledger.redshift_e += (s.counts[i] * (e0 - em) + n * (em - e1)) * ev;
            delta.redshift_e += (s.counts[i] * (e0 - em) + n * (em - e1)) * ev;
            let cross = self.nodes[i].eta - cutoff.ln();
            if t == cross {
                q.ledger.out_n += n;
                delta.out_n += n;
                q.ledger.out_e += n * e1 * ev;
                delta.out_e += n * e1 * ev;
                q.counts[i] = 0.0;
                q.log_counts[i] = f64::NEG_INFINITY;
            } else {
                q.counts[i] = n;
                q.log_counts[i] = if n.is_normal() {
                    n.ln()
                } else {
                    let log_added = if injected > 0.0 {
                        injected.ln()
                    } else {
                        f64::NEG_INFINITY
                    };
                    let a = s.log_counts[i];
                    let high = a.max(log_added);
                    let low = a.min(log_added);
                    let numerator = if high == f64::NEG_INFINITY {
                        high
                    } else {
                        high + (low - high).exp().ln_1p()
                    };
                    numerator
                        - (dt
                            * packet_opacity_masked(&q.gas, em, masks[i], p.n_h_cm3, p.n_he_cm3)?
                                .iter()
                                .sum::<f64>())
                        .ln_1p()
                };
            }
        }
        let r = step.endpoint;
        let vol = dt / p.n_h_cm3;
        for i in 0..3 {
            q.ledger.absorption[i] += step.absorbed_per_h[i];
            delta.absorption[i] += step.absorbed_per_h[i];
            q.ledger.ci[i] += vol * r.ci_events_cm3_s[i];
            delta.ci[i] += vol * r.ci_events_cm3_s[i];
            q.ledger.rr[i] += vol * r.rr_events_cm3_s[i];
            delta.rr[i] += vol * r.rr_events_cm3_s[i];
            q.ledger.floor[i] += vol * r.ci_floor_events_cm3_s[i];
            delta.floor[i] += vol * r.ci_floor_events_cm3_s[i];
            q.ledger.cap_e[i] += vol * r.ce_cap_cooling_erg_cm3_s[i];
            delta.cap_e[i] += vol * r.ce_cap_cooling_erg_cm3_s[i];
        }
        q.ledger.dr += vol * r.dr_events_cm3_s;
        delta.dr += vol * r.dr_events_cm3_s;
        q.ledger.escape_e += vol * r.escape_erg_cm3_s;
        delta.escape_e += vol * r.escape_erg_cm3_s;
        q.ledger.work_e += vol * r.expansion_work_erg_cm3_s;
        delta.work_e += vol * r.expansion_work_erg_cm3_s;
        q.ledger.cmb_e -= vol * r.cmb_to_gas_erg_cm3_s;
        delta.cmb_e -= vol * r.cmb_to_gas_erg_cm3_s;
        q.ledger.cmb_abs_e += vol * r.cmb_to_gas_erg_cm3_s.abs();
        delta.cmb_abs_e += vol * r.cmb_to_gas_erg_cm3_s.abs();
        q.ledger.excluded_dr_e += vol * r.excluded_dr_cooling_erg_cm3_s;
        delta.excluded_dr_e += vol * r.excluded_dr_cooling_erg_cm3_s;
        q.ledger.underflow_n_bound += step.underflow_n_bound;
        delta.underflow_n_bound += step.underflow_n_bound;
        q.ledger.underflow_e_bound += step.underflow_e_bound;
        delta.underflow_e_bound += step.underflow_e_bound;
        if q.ledger.underflow_n_bound > 1e-20 || q.ledger.underflow_e_bound > 1e-30 {
            return Err(invalid());
        }
        let nres = step
            .packets
            .iter()
            .zip(&photons)
            .map(|(new, old)| new.per_h - old.per_h)
            .sum::<f64>()
            + step.absorbed_per_h.iter().sum::<f64>()
            - source_n;
        let radiation_change = step
            .packets
            .iter()
            .zip(&photons)
            .map(|(new, old)| (new.per_h - old.per_h) * old.energy_ev * ev)
            .sum::<f64>();
        let material = q.gas.w_erg_per_h - s.gas.w_erg_per_h
            + binding(&q.gas, p.n_he_cm3 / p.n_h_cm3)
            - binding(&s.gas, p.n_he_cm3 / p.n_h_cm3);
        let eres = material
            + radiation_change
            + vol * (r.escape_erg_cm3_s + r.expansion_work_erg_cm3_s - r.cmb_to_gas_erg_cm3_s)
            - source_e;
        let total = self.balances(&q)?;
        if nres.abs() > 1e-10 * q.ledger.emitted_n.max(1e-10)
            || eres.abs()
                > 1e-10
                    * (q.ledger.emitted_e
                        + q.ledger.work_e
                        + q.ledger.escape_e
                        + q.ledger.cmb_abs_e)
                        .max(1e-20)
            || total[0].abs() > 1e-10 * q.ledger.emitted_n.max(1e-10)
            || total[1].abs()
                > 1e-10
                    * (q.ledger.emitted_e
                        + q.ledger.work_e
                        + q.ledger.escape_e
                        + q.ledger.cmb_abs_e)
                        .max(1e-20)
        {
            return Err(invalid());
        }
        let fraction_defect = std::array::from_fn(|i| {
            ((q.gas.fractions[i] - s.gas.fractions[i]) - dt * r.fraction_dt[i]).abs()
        });
        let energy_defect =
            ((q.gas.w_erg_per_h - s.gas.w_erg_per_h) - dt * r.w_dt_erg_per_h_s).abs();
        Ok(ContinuousTrial {
            state: q,
            delta,
            proper_dt: dt,
            stage: mid,
            source_rates: rates,
            photo_energy: vol * r.photo_input_erg_cm3_s,
            fraction_defect,
            energy_defect,
        })
    }
    /// Physical endpoint rates, distinct from interval-average gas ownership.
    pub fn endpoint_photo(
        &self,
        s: &ContinuousState,
    ) -> Result<crate::igm_photo::IgmPhotoRates, ForwardError> {
        let p = self.config.background.at_ln_a(s.ln_a)?;
        let packets = self.packets(s);
        let absorbers = [Absorber::HI, Absorber::HeI, Absorber::HeII];
        // Ordinary points preserve the original batched provider's underflow
        // boundary. Exact event outputs use the documented right-hand limit.
        if !self.nodes.iter().any(|n| {
            absorbers
                .iter()
                .any(|a| s.ln_a == n.eta - verner_cutoff_ev(*a).ln())
        }) {
            return igm_photo_rates(&s.gas, &packets, p.n_h_cm3, p.n_he_cm3);
        }
        let mut total = crate::igm_photo::IgmPhotoRates::default();
        for (j, packet) in packets.iter().enumerate() {
            let one = igm_photo_rates(&s.gas, std::slice::from_ref(packet), p.n_h_cm3, p.n_he_cm3)?;
            let mut owners = [0.0; 3];
            for (i, a) in absorbers.iter().enumerate() {
                if s.ln_a >= self.nodes[j].eta - verner_cutoff_ev(*a).ln() {
                    continue;
                }
                total.input.gamma_s[i] += one.input.gamma_s[i];
                total.input.heat_erg_per_absorber_s[i] += one.input.heat_erg_per_absorber_s[i];
                owners[i] = one.owner_per_h_s[i];
                total.owner_per_h_s[i] += owners[i];
                total.absorbed_erg_per_h_s +=
                    owners[i] * packet.energy_ev * HHeModel::controlled_fixture().ev_erg;
            }
            total.packet_owner_per_h_s.push(owners);
            // Retaining even the inactive-channel bounds is conservative.
            total.underflow_count_per_h_s += one.underflow_count_per_h_s;
            total.underflow_energy_erg_per_h_s += one.underflow_energy_erg_per_h_s;
        }
        Ok(total)
    }
}
