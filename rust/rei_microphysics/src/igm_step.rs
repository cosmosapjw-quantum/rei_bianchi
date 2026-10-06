//! Conservative frozen-background backward Euler gas/packet transaction.
use crate::{
    coupled_primary::PrimaryPacket, igm_state::IgmGasState, igm_thermal::IgmPointRhs, ForwardError,
};
#[derive(Clone, Copy, Debug)]
pub struct StepBackground {
    pub n_h: f64,
    pub n_he: f64,
    pub hubble: f64,
    pub tcmb: f64,
}
#[derive(Clone, Copy, Debug)]
pub struct StepControl {
    pub max_iterations: usize,
    pub relative_residual: f64,
    pub cumulative_count_scale: f64,
    pub cumulative_energy_scale: f64,
}
impl Default for StepControl {
    fn default() -> Self {
        Self {
            max_iterations: 160,
            relative_residual: 1e-15,
            cumulative_count_scale: 1e-10,
            cumulative_energy_scale: 1e-20,
        }
    }
}
#[derive(Clone, Debug)]
pub struct StepResult {
    pub gas: IgmGasState,
    pub packets: Vec<PrimaryPacket>,
    pub endpoint: IgmPointRhs,
    pub iterations: usize,
    pub residual: f64,
    pub absorbed_per_h: [f64; 3],
    pub underflow_n_bound: f64,
    pub underflow_e_bound: f64,
}

use crate::{
    igm_photo::{igm_photo_rates, packet_opacity},
    igm_rates::igm_rates,
    igm_thermal::igm_point_rhs,
};
fn invalid() -> ForwardError {
    ForwardError::InvalidInput("IGM_STEP_REJECTED")
}
fn endpoint(
    gas: &IgmGasState,
    old_packets: &[PrimaryPacket],
    b: StepBackground,
    dt: f64,
) -> Result<
    (
        Vec<PrimaryPacket>,
        crate::igm_photo::IgmPhotoRates,
        IgmPointRhs,
    ),
    ForwardError,
> {
    let mut photons = Vec::with_capacity(old_packets.len());
    for p in old_packets {
        if !p.per_h.is_finite() || p.per_h < 0.0 {
            return Err(invalid());
        }
        let k = packet_opacity(gas, p.energy_ev, b.n_h, b.n_he)?
            .iter()
            .sum::<f64>();
        let n = p.per_h / (1.0 + dt * k);
        if !n.is_finite() {
            return Err(invalid());
        }
        photons.push(PrimaryPacket {
            energy_ev: p.energy_ev,
            per_h: n,
        });
    }
    let photo = igm_photo_rates(gas, &photons, b.n_h, b.n_he)?;
    let rhs = igm_point_rhs(gas, b.n_h, b.n_he, b.hubble, b.tcmb, photo.input)?;
    Ok((photons, photo, rhs))
}
fn thermal(
    old: &IgmGasState,
    f: [f64; 3],
    photo: crate::igm_thermal::IgmPhotoInput,
    b: StepBackground,
    dt: f64,
) -> Result<IgmGasState, ForwardError> {
    // Evaluate the original energy first: a genuine fixed point is returned
    // exactly, including admitted provider endpoints. This is not projection.
    let evaluate = |g: IgmGasState| -> Result<(IgmGasState, f64), ForwardError> {
        let r = igm_point_rhs(&g, b.n_h, b.n_he, b.hubble, b.tcmb, photo)?;
        Ok((g, g.w_erg_per_h - old.w_erg_per_h - dt * r.w_dt_erg_per_h_s))
    };
    let same = IgmGasState::new(f, old.w_erg_per_h)?;
    if let Ok((g, 0.0)) = evaluate(same) {
        return Ok(g);
    }
    // Construct legal bracket endpoints in energy space. Roundoff may put a
    // requested endpoint temperature outside the actual EOS domain; move the
    // bracket inward by representable energy ulps, never an input or root.
    let bound = |t: f64, lower: bool| -> Result<(IgmGasState, f64), ForwardError> {
        let mut g = IgmGasState::from_temperature(f, b.n_h, b.n_he, t)?;
        for _ in 0..16 {
            let actual = g.eos(b.n_h, b.n_he)?.temperature_k;
            if (1.0..=1e6).contains(&actual) {
                return evaluate(g);
            }
            g.w_erg_per_h = f64::from_bits(if lower {
                g.w_erg_per_h.to_bits() + 1
            } else {
                g.w_erg_per_h.to_bits() - 1
            });
        }
        Err(invalid())
    };
    let (mut lo, fl) = bound(1.0, true)?;
    let (mut hi, fh) = bound(1e6, false)?;
    if fl == 0.0 {
        return Ok(lo);
    }
    if fh == 0.0 {
        return Ok(hi);
    }
    if fl > 0.0 || fh < 0.0 {
        return Err(invalid());
    }
    let mut w = old.w_erg_per_h;
    if w <= lo.w_erg_per_h || w >= hi.w_erg_per_h {
        w = 0.5 * (lo.w_erg_per_h + hi.w_erg_per_h);
    }
    for _ in 0..100 {
        let (g, residual) = evaluate(IgmGasState::new(f, w)?)?;
        if residual == 0.0 {
            return Ok(g);
        }
        // At floating precision, explicitly choose the closest neighboring
        // representable residual rather than a loose temperature tolerance.
        if residual.abs() <= 8.0 * f64::EPSILON * w {
            let mut best = g;
            let mut error = residual.abs();
            for _ in 0..64 {
                let before = best.w_erg_per_h;
                for bits in [before.to_bits() - 1, before.to_bits() + 1] {
                    let v = f64::from_bits(bits);
                    if v >= lo.w_erg_per_h && v <= hi.w_erg_per_h {
                        if let Ok((candidate, r)) = evaluate(IgmGasState::new(f, v)?) {
                            if r.abs() < error {
                                best = candidate;
                                error = r.abs();
                            }
                        }
                    }
                }
                if best.w_erg_per_h == before {
                    return Ok(best);
                }
            }
            // Rare nonlocal case: preserve the root bracket and continue.
            w = best.w_erg_per_h;
            continue;
        }
        if w == lo.w_erg_per_h || w == hi.w_erg_per_h {
            let (_, rl) = evaluate(lo)?;
            let (_, rh) = evaluate(hi)?;
            return Ok(if rl.abs() <= rh.abs() { lo } else { hi });
        }
        if residual < 0.0 {
            lo = g;
        } else {
            hi = g;
        }
        let wp = (w * (1.0 + 1e-5)).min(hi.w_erg_per_h);
        let wm = (w * (1.0 - 1e-5)).max(lo.w_erg_per_h);
        let (_, fp) = evaluate(IgmGasState::new(f, wp)?)?;
        let (_, fm) = evaluate(IgmGasState::new(f, wm)?)?;
        let derivative = (fp - fm) / (wp - wm);
        let newton = w - residual / derivative;
        w = if newton.is_finite() && newton > lo.w_erg_per_h && newton < hi.w_erg_per_h {
            newton
        } else {
            0.5 * (lo.w_erg_per_h + hi.w_erg_per_h)
        };
    }
    Err(ForwardError::InvalidInput("IGM_STEP_ITERATION_LIMIT"))
}
pub fn implicit_step(
    old: &IgmGasState,
    packets: &[PrimaryPacket],
    b: StepBackground,
    dt: f64,
    control: StepControl,
) -> Result<StepResult, ForwardError> {
    if !dt.is_normal()
        || dt <= 0.0
        || control.max_iterations == 0
        || !control.relative_residual.is_normal()
        || control.relative_residual <= 0.0
        || control.relative_residual > 1e-10
        || !control.cumulative_count_scale.is_normal()
        || control.cumulative_count_scale < 1e-10
        || !control.cumulative_energy_scale.is_normal()
        || control.cumulative_energy_scale < 1e-20
    {
        return Err(invalid());
    }
    // Preflight actual EOS and incoming packet values before candidate updates.
    igm_point_rhs(old, b.n_h, b.n_he, b.hubble, b.tcmb, Default::default())?;
    igm_photo_rates(old, packets, b.n_h, b.n_he)?;
    let mut gas = *old;
    for iteration in 0..control.max_iterations {
        let (_, photo, _) = endpoint(&gas, packets, b, dt)?;
        let eos = gas.eos(b.n_h, b.n_he)?;
        let rates = igm_rates(eos.temperature_k)?;
        let ne = eos.electron_density_cm3;
        let a: [f64; 3] =
            std::array::from_fn(|i| dt * (photo.input.gamma_s[i] + ne * rates.ci_cm3_s[i]));
        let r = [
            dt * ne * rates.rr_cm3_s[0],
            dt * ne * (rates.rr_cm3_s[1] + rates.dr_cm3_s),
            dt * ne * rates.rr_cm3_s[2],
        ];
        let [x0, y0, z0] = old.fractions;
        let mut f = [(x0 + a[0]) / (1.0 + a[0] + r[0]), y0, z0];
        if b.n_he > 0.0 {
            let den = 1.0 + r[2];
            f[1] = (y0 + a[1] * ((1.0 - y0 - z0) + y0 + z0 * r[2] / den) + r[2] * z0 / den)
                / (1.0 + a[1] + r[1] + a[2] * (1.0 + a[1]) / den);
            f[2] = (z0 + a[2] * f[1]) / den;
        }
        // Convex damping preserves the closed species simplex, including exact zeros.
        for i in 0..3 {
            f[i] = if iteration < 20 {
                f[i]
            } else {
                0.5 * gas.fractions[i] + 0.5 * f[i]
            };
        }
        let trial = IgmGasState::new(f, gas.w_erg_per_h)?;
        let (_, new_photo, _) = endpoint(&trial, packets, b, dt)?;
        gas = thermal(old, f, new_photo.input, b, dt)?;
        let (photons, owners, rhs) = endpoint(&gas, packets, b, dt)?;
        let mut residual: f64 = 0.0;
        for i in 0..3 {
            let scale = 1e-6_f64
                .max(old.fractions[i])
                .max(gas.fractions[i])
                .max((dt * rhs.fraction_dt[i]).abs());
            residual = residual
                .max((gas.fractions[i] - old.fractions[i] - dt * rhs.fraction_dt[i]).abs() / scale);
        }
        let scale = 1e-16_f64
            .max(old.w_erg_per_h)
            .max(gas.w_erg_per_h)
            .max((dt * rhs.w_dt_erg_per_h_s).abs());
        residual = residual
            .max((gas.w_erg_per_h - old.w_erg_per_h - dt * rhs.w_dt_erg_per_h_s).abs() / scale);
        if residual <= control.relative_residual {
            let absorbed = std::array::from_fn(|i| dt * owners.owner_per_h_s[i]);
            for i in 0..3 {
                let same = dt * rhs.photo_events_cm3_s[i] / b.n_h;
                if (same - absorbed[i]).abs()
                    > 1e-10 * same.abs().max(control.cumulative_count_scale)
                {
                    return Err(invalid());
                }
            }
            for (j, (p, q)) in packets.iter().zip(photons.iter()).enumerate() {
                let loss = dt * owners.packet_owner_per_h_s[j].iter().sum::<f64>();
                if (p.per_h - q.per_h - loss).abs()
                    > 1e-10 * p.per_h.max(control.cumulative_count_scale)
                {
                    return Err(invalid());
                }
            }
            let c = crate::HHeModel::controlled_fixture();
            let df: [f64; 3] = std::array::from_fn(|i| gas.fractions[i] - old.fractions[i]);
            let delta_binding = c.ev_erg
                * (c.threshold_ev[0] * df[0]
                    + b.n_he / b.n_h
                        * (c.threshold_ev[1] * df[1]
                            + (c.threshold_ev[1] + c.threshold_ev[2]) * df[2]));
            let delta_material = gas.w_erg_per_h - old.w_erg_per_h + delta_binding;
            let radiation_loss = dt * owners.absorbed_erg_per_h_s;
            let reservoirs = dt / b.n_h
                * (rhs.escape_erg_cm3_s - rhs.cmb_to_gas_erg_cm3_s + rhs.expansion_work_erg_cm3_s);
            let throughput = radiation_loss.abs()
                + delta_material.abs()
                + dt / b.n_h
                    * (rhs.escape_erg_cm3_s
                        + rhs.cmb_to_gas_erg_cm3_s.abs()
                        + rhs.expansion_work_erg_cm3_s);
            if (delta_material - radiation_loss + reservoirs).abs()
                > 1e-10 * throughput.max(control.cumulative_energy_scale)
            {
                return Err(ForwardError::InvalidInput("IGM_STEP_ENERGY_LEDGER"));
            }
            let mut underflow_n_bound = dt * owners.underflow_count_per_h_s;
            let mut underflow_e_bound = dt * owners.underflow_energy_erg_per_h_s;
            for (p, q) in packets.iter().zip(photons.iter()) {
                if p.per_h > 0.0 && !q.per_h.is_normal() {
                    underflow_n_bound += f64::MIN_POSITIVE;
                    underflow_e_bound += f64::MIN_POSITIVE * p.energy_ev * c.ev_erg;
                }
            }
            if underflow_n_bound > 1e-20 || underflow_e_bound > 1e-30 {
                return Err(ForwardError::InvalidInput(
                    "IGM_UNDERFLOW_BOUND_EXCEEDS_BUDGET",
                ));
            }
            return Ok(StepResult {
                gas,
                packets: photons,
                endpoint: rhs,
                iterations: iteration + 1,
                residual,
                absorbed_per_h: absorbed,
                underflow_n_bound,
                underflow_e_bound,
            });
        }
    }
    Err(ForwardError::InvalidInput("IGM_STEP_ITERATION_LIMIT"))
}
