//! Transactional ln(a) source-driven FLRW point histories, first-order split BE.
use crate::{
    igm_config::HistoryConfig,
    igm_source::{build_birth_schedule, Birth},
    igm_state::IgmGasState,
    ForwardError,
};
#[derive(Clone, Debug, Default)]
pub struct Ledger {
    pub emitted_n: f64,
    pub emitted_e: f64,
    pub absorption: [f64; 3],
    pub out_n: f64,
    pub out_e: f64,
    pub redshift_e: f64,
    pub escape_e: f64,
    pub work_e: f64,
    pub cmb_e: f64,
    pub cmb_abs_e: f64,
    pub ci: [f64; 3],
    pub rr: [f64; 3],
    pub dr: f64,
    pub floor: [f64; 3],
    pub cap_e: [f64; 3],
    pub excluded_dr_e: f64,
    pub underflow_n_bound: f64,
    pub underflow_e_bound: f64,
}
#[derive(Clone, Debug)]
pub struct ActivePacket {
    pub birth_index: usize,
    pub per_h: f64,
    pub log_per_h: f64,
}
#[derive(Clone, Debug)]
pub struct HistoryState {
    pub ln_a: f64,
    pub gas: IgmGasState,
    pub packets: Vec<ActivePacket>,
    pub birth_cursor: usize,
    pub output_cursor: usize,
    pub ledger: Ledger,
    pub next_dln_a: f64,
    pub accepted_steps: usize,
    pub rejected_steps: usize,
    pub max_residual: f64,
}
#[derive(Clone, Debug)]
pub struct History {
    pub config: HistoryConfig,
    pub births: Vec<Birth>,
    pub initial_material: f64,
}

use crate::{
    coupled_primary::PrimaryPacket,
    igm_step::{implicit_step, StepBackground, StepControl},
    verner_cutoff_ev, Absorber, HHeModel,
};
fn invalid() -> ForwardError {
    ForwardError::InvalidInput("IGM_HISTORY_REJECTED")
}
fn binding(g: &IgmGasState, ratio: f64) -> f64 {
    let c = HHeModel::controlled_fixture();
    c.ev_erg
        * (c.threshold_ev[0] * g.fractions[0]
            + ratio
                * (c.threshold_ev[1] * g.fractions[1]
                    + (c.threshold_ev[1] + c.threshold_ev[2]) * g.fractions[2]))
}
impl History {
    pub fn new(config: HistoryConfig) -> Result<(Self, HistoryState), ForwardError> {
        if config.energy_panels > config.max_packets / 2
            || config.birth_panels > config.max_packets / 2
        {
            return Err(invalid());
        }
        let nodes = config.source.energy_quadrature(config.energy_panels)?;
        if config
            .birth_panels
            .checked_mul(2)
            .and_then(|n| n.checked_mul(nodes.len()))
            .ok_or_else(invalid)?
            > config.max_packets
        {
            return Err(invalid());
        }
        let births = build_birth_schedule(
            &config.background,
            &config.source,
            config.start,
            config.end,
            config.birth_panels,
            config.energy_panels,
        )?;
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
        let state = HistoryState {
            ln_a: config.start,
            gas,
            packets: Vec::new(),
            birth_cursor: 0,
            output_cursor: 0,
            ledger: Ledger::default(),
            next_dln_a: config.max_dln_a,
            accepted_steps: 0,
            rejected_steps: 0,
            max_residual: 0.0,
        };
        Ok((
            Self {
                config,
                births,
                initial_material,
            },
            state,
        ))
    }
    pub fn energy(&self, p: &ActivePacket, t: f64) -> f64 {
        let b = self.births[p.birth_index];
        for a in [Absorber::HI, Absorber::HeI, Absorber::HeII] {
            let cutoff = verner_cutoff_ev(a);
            let crossing = b.ln_a + (b.energy_ev / cutoff).ln();
            if t == crossing {
                return cutoff;
            }
        }
        b.energy_ev * (b.ln_a - t).exp()
    }
    pub fn radiation(&self, s: &HistoryState) -> [f64; 2] {
        let ev = HHeModel::controlled_fixture().ev_erg;
        [
            s.packets.iter().map(|p| p.per_h).sum(),
            s.packets
                .iter()
                .map(|p| p.per_h * self.energy(p, s.ln_a) * ev)
                .sum(),
        ]
    }
    pub fn balances(&self, s: &HistoryState) -> Result<[f64; 2], ForwardError> {
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
    /// One accepted transaction, stopping no later than requested output/event.
    /// Rejects are retried on private candidate data; caller state never mutates.
    pub fn advance_one(&self, s: &HistoryState, end: f64) -> Result<HistoryState, ForwardError> {
        if !end.is_finite()
            || end <= s.ln_a
            || end > self.config.end
            || s.accepted_steps >= self.config.max_steps
        {
            return Err(invalid());
        }
        let mut limit = end;
        if let Some(b) = self.births.get(s.birth_cursor) {
            if b.ln_a > s.ln_a {
                limit = limit.min(b.ln_a);
            } else {
                return Err(invalid());
            }
        }
        for p in &s.packets {
            let b = self.births[p.birth_index];
            for a in [Absorber::HI, Absorber::HeI, Absorber::HeII] {
                let cross = b.ln_a + (b.energy_ev / verner_cutoff_ev(a)).ln();
                if cross > s.ln_a {
                    limit = limit.min(cross);
                }
            }
        }
        let mut dx = s.next_dln_a.min(self.config.max_dln_a).min(limit - s.ln_a);
        let mut rejects = 0;
        loop {
            // Use exact event/output coordinate whenever this trial reaches its limit.
            let t = if dx >= limit - s.ln_a {
                limit
            } else {
                s.ln_a + dx
            };
            if t <= s.ln_a {
                return Err(invalid());
            }
            dx = t - s.ln_a;
            let point = self.config.background.at_ln_a(t)?;
            let dt = dx / point.hubble_per_s;
            let photons: Vec<_> = s
                .packets
                .iter()
                .map(|p| PrimaryPacket {
                    energy_ev: self.energy(p, t),
                    per_h: p.per_h,
                })
                .collect();
            let result = implicit_step(
                &s.gas,
                &photons,
                StepBackground {
                    n_h: point.n_h_cm3,
                    n_he: point.n_he_cm3,
                    hubble: point.hubble_per_s,
                    tcmb: point.tcmb_k,
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
            );
            if std::env::var_os("IGM_TRACE_REJECT").is_some() && result.is_err() {
                eprintln!("step reject t={t} dx={dx}: {:?}", result);
            }
            if let Ok(step) = result {
                let mut q = s.clone();
                q.ln_a = t;
                q.gas = step.gas;
                q.accepted_steps += 1;
                q.rejected_steps += rejects;
                q.max_residual = q.max_residual.max(step.residual);
                q.next_dln_a = if rejects == 0 && t == limit {
                    s.next_dln_a.min(self.config.max_dln_a)
                } else {
                    (dx * 1.5).min(self.config.max_dln_a)
                };
                let ev = HHeModel::controlled_fixture().ev_erg;
                q.ledger.redshift_e += s
                    .packets
                    .iter()
                    .map(|p| p.per_h * (self.energy(p, s.ln_a) - self.energy(p, t)) * ev)
                    .sum::<f64>();
                q.packets.clear();
                for (p, np) in s.packets.iter().zip(step.packets.iter()) {
                    let b = self.births[p.birth_index];
                    let crossing = b.ln_a + (b.energy_ev / verner_cutoff_ev(Absorber::HI)).ln();
                    if t == crossing {
                        q.ledger.out_n += np.per_h;
                        q.ledger.out_e += np.per_h * np.energy_ev * ev;
                    } else {
                        q.packets.push(ActivePacket {
                            birth_index: p.birth_index,
                            per_h: np.per_h,
                            log_per_h: if np.per_h.is_normal() {
                                np.per_h.ln()
                            } else {
                                p.log_per_h
                                    - (dt
                                        * crate::igm_photo::packet_opacity(
                                            &q.gas,
                                            np.energy_ev,
                                            point.n_h_cm3,
                                            point.n_he_cm3,
                                        )?
                                        .iter()
                                        .sum::<f64>())
                                    .ln_1p()
                            },
                        });
                    }
                }
                let r = step.endpoint;
                let vol = dt / point.n_h_cm3;
                for i in 0..3 {
                    q.ledger.absorption[i] += step.absorbed_per_h[i];
                    q.ledger.ci[i] += vol * r.ci_events_cm3_s[i];
                    q.ledger.rr[i] += vol * r.rr_events_cm3_s[i];
                    q.ledger.floor[i] += vol * r.ci_floor_events_cm3_s[i];
                    q.ledger.cap_e[i] += vol * r.ce_cap_cooling_erg_cm3_s[i];
                }
                q.ledger.underflow_n_bound += step.underflow_n_bound;
                q.ledger.underflow_e_bound += step.underflow_e_bound;
                if q.ledger.underflow_n_bound > 1e-20 || q.ledger.underflow_e_bound > 1e-30 {
                    return Err(invalid());
                }
                q.ledger.dr += vol * r.dr_events_cm3_s;
                q.ledger.escape_e += vol * r.escape_erg_cm3_s;
                q.ledger.work_e += vol * r.expansion_work_erg_cm3_s;
                q.ledger.cmb_e -= vol * r.cmb_to_gas_erg_cm3_s;
                q.ledger.cmb_abs_e += vol * r.cmb_to_gas_erg_cm3_s.abs();
                q.ledger.excluded_dr_e += vol * r.excluded_dr_cooling_erg_cm3_s;
                while let Some(b) = self.births.get(q.birth_cursor) {
                    if b.ln_a != t {
                        break;
                    }
                    q.ledger.emitted_n += b.per_h;
                    q.ledger.emitted_e += b.per_h * b.energy_ev * ev;
                    if b.energy_ev < verner_cutoff_ev(Absorber::HI) {
                        q.ledger.out_n += b.per_h;
                        q.ledger.out_e += b.per_h * b.energy_ev * ev;
                    } else {
                        q.packets.push(ActivePacket {
                            birth_index: q.birth_cursor,
                            per_h: b.per_h,
                            log_per_h: b.per_h.ln(),
                        });
                    }
                    q.birth_cursor += 1;
                }
                if q.packets.len() > self.config.max_packets {
                    return Err(invalid());
                }
                // Audit local changes directly. Subtracting two cumulative residuals
                // would compare tiny current absorption against roundoff of all past births.
                let nres = s
                    .packets
                    .iter()
                    .zip(step.packets.iter())
                    .map(|(p, np)| np.per_h - p.per_h)
                    .sum::<f64>()
                    + step.absorbed_per_h.iter().sum::<f64>();
                let local_radiation = photons
                    .iter()
                    .zip(step.packets.iter())
                    .map(|(p, np)| (np.per_h - p.per_h) * p.energy_ev * ev)
                    .sum::<f64>();
                let ratio = point.n_he_cm3 / point.n_h_cm3;
                let eres = (q.gas.w_erg_per_h - s.gas.w_erg_per_h)
                    + {
                        let c = HHeModel::controlled_fixture();
                        let df: [f64; 3] =
                            std::array::from_fn(|i| q.gas.fractions[i] - s.gas.fractions[i]);
                        c.ev_erg
                            * (c.threshold_ev[0] * df[0]
                                + ratio
                                    * (c.threshold_ev[1] * df[1]
                                        + (c.threshold_ev[1] + c.threshold_ev[2]) * df[2]))
                    }
                    + local_radiation
                    + vol
                        * (r.escape_erg_cm3_s + r.expansion_work_erg_cm3_s
                            - r.cmb_to_gas_erg_cm3_s);
                let nscale = step
                    .absorbed_per_h
                    .iter()
                    .sum::<f64>()
                    .max(s.ledger.emitted_n);
                let escale = vol
                    * (r.escape_erg_cm3_s
                        + r.expansion_work_erg_cm3_s
                        + r.cmb_to_gas_erg_cm3_s.abs()
                        + r.photo_input_erg_cm3_s);
                let total = self.balances(&q)?;
                if nres.abs() <= 1e-10 * nscale.max(1e-10)
                    && eres.abs()
                        <= 1e-10
                            * escale
                                .max(
                                    s.ledger.emitted_e
                                        + s.ledger.escape_e
                                        + s.ledger.work_e
                                        + s.ledger.cmb_abs_e
                                        + s.ledger.redshift_e
                                        + s.ledger.out_e,
                                )
                                .max(1e-20)
                    && total[0].abs() <= 1e-10 * q.ledger.emitted_n.max(1e-10)
                    && total[1].abs()
                        <= 1e-10
                            * (q.ledger.emitted_e
                                + q.ledger.work_e
                                + q.ledger.escape_e
                                + q.ledger.cmb_abs_e)
                                .max(1e-20)
                {
                    return Ok(q);
                }
                if std::env::var_os("IGM_TRACE_REJECT").is_some() {
                    eprintln!("ledger reject t={t} dx={dx} local={nres},{eres} total={total:?} scales={nscale},{escale}");
                }
            }
            rejects += 1;
            dx *= 0.5;
            if dx < self.config.min_dln_a {
                return Err(invalid());
            }
        }
    }
    pub fn advance_to(&self, state: &HistoryState, end: f64) -> Result<HistoryState, ForwardError> {
        let mut s = state.clone();
        if end < s.ln_a || end > self.config.end {
            return Err(invalid());
        }
        while s.ln_a < end {
            s = self.advance_one(&s, end)?;
        }
        Ok(s)
    }
}
