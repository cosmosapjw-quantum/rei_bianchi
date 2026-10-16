// Isolated V10 research stage: four Grackle Case-A capture channels.
// Every energy below is erg per total H nucleus until booked in eV/H.
const V10_ORDER: [usize; 8] = [0, 1, 2, 3, 3, 2, 1, 0];
const V10_ION: [usize; 4] = [1, 3, 4, 3];
const V10_PRODUCT: [usize; 4] = [0, 2, 3, 2];

fn v10_pair(ion: f64, electron: f64, k: f64) -> Result<f64, ForwardError> {
    if !ion.is_finite() || !electron.is_finite() || !k.is_finite()
        || ion < 0.0 || electron < 0.0 || k < 0.0 {
        return Err(err("V10_PAIR_DOMAIN"));
    }
    if ion == 0.0 || electron == 0.0 || k == 0.0 { return Ok(0.0); }
    let small = ion.min(electron);
    let large = ion.max(electron);
    let diff = large - small;
    let event = if diff == 0.0 {
        small * small * k / (1.0 + small * k)
    } else {
        let u = -(-diff * k).exp_m1();
        small * large * u / (diff + small * u)
    };
    Ok(event.max(0.0).min(small))
}

fn v10_electron(species: &[f64; 5]) -> f64 {
    species[1] + species[3] + 2.0 * species[4]
}

#[derive(Clone, Copy)]
struct V10Probe {
    species: [f64; 5],
    events: [f64; 4],
    cooling: [f64; 4],
    t_mid: f64,
    w_after: f64,
}

fn v10_probe(t: f64, before: [f64; 5], w_before: f64, strength: f64,
    y_he: f64, kb: f64) -> Result<V10Probe, ForwardError> {
    let rates = crate::igm_rates::igm_rates(t)?;
    let alpha = [rates.rr_cm3_s[0], rates.rr_cm3_s[1], rates.rr_cm3_s[2], rates.dr_cm3_s];
    let cool = [rates.rr_cooling_erg_cm3_s[0], rates.rr_cooling_erg_cm3_s[1],
        rates.rr_cooling_erg_cm3_s[2], rates.dr_cooling_erg_cm3_s];
    let mut species = before;
    let mut events = [0.0; 4];
    let mut cooling = [0.0; 4];
    for channel in V10_ORDER {
        if alpha[channel] <= 0.0 {
            if cool[channel] != 0.0 { return Err(err("V10_RR_ZERO_RATE_COOLING")); }
            continue;
        }
        let amount = v10_pair(species[V10_ION[channel]], v10_electron(&species),
            0.5 * strength * alpha[channel])?;
        species[V10_ION[channel]] -= amount;
        species[V10_PRODUCT[channel]] += amount;
        events[channel] += amount;
        cooling[channel] += amount * cool[channel] / alpha[channel];
    }
    let total_cooling = cooling.iter().sum::<f64>();
    let w_after = w_before - total_cooling;
    let w_mid = w_before - 0.5 * total_cooling;
    let particles_mid = 1.0 + y_he
        + 0.5 * (v10_electron(&before) + v10_electron(&species));
    if !(w_after >= 0.0 && w_mid > 0.0 && particles_mid > 0.0)
        || species.iter().any(|&v| !v.is_finite() || v < -1e-12) {
        return Err(err("V10_RR_THERMAL_SPECIES_DOMAIN"));
    }
    Ok(V10Probe { species, events, cooling,
        t_mid: w_mid / (1.5 * kb * particles_mid), w_after })
}

impl Driver {
    fn v10_rrdr_stage(&self, state: &mut DriverState, dt: f64) -> Result<(), ForwardError> {
        if !dt.is_finite() || dt <= 0.0 { return Err(err("V10_RR_DT")); }
        let nh = self.n_h0_cm3 / state.a.powi(3);
        let nhe = self.n_he0_cm3 / state.a.powi(3);
        let y_he = nhe / nh;
        let [x, y, z] = state.gas.fractions;
        let before = [1.0 - x, x, y_he * (1.0 - y - z), y_he * y, y_he * z];
        let model = HHeModel::controlled_fixture();
        let kb = model.kb_erg_k;
        let strength = dt * nh;
        let w_before = state.gas.w_erg_per_h;
        let lo = 10000.0;
        let hi = 24000.0;
        let f_lo = lo - v10_probe(lo, before, w_before, strength, y_he, kb)?.t_mid;
        let f_hi = hi - v10_probe(hi, before, w_before, strength, y_he, kb)?.t_mid;
        if f_lo * f_hi > 0.0 { return Err(err("V10_RR_ROOT_UNBRACKETED")); }
        let (mut left, mut right) = (lo, hi);
        let mut t_mid = lo;
        for _ in 0..75 {
            t_mid = 0.5 * (left + right);
            let f_mid = t_mid - v10_probe(t_mid, before, w_before, strength, y_he, kb)?.t_mid;
            if f_mid.abs() <= 2e-10 || right - left <= 2e-10 { break; }
            if f_mid * f_lo > 0.0 { left = t_mid; } else { right = t_mid; }
        }
        let result = v10_probe(t_mid, before, w_before, strength, y_he, kb)?;
        if (t_mid - result.t_mid).abs() > 3e-7 { return Err(err("V10_RR_ROOT_RESIDUAL")); }
        let s = result.species;
        state.gas = IgmGasState::new([s[1], s[3] / y_he, s[4] / y_he], result.w_after)?;
        let final_t = state.gas.eos(nh, nhe)?.temperature_k;
        if !(10000.0..=24000.0).contains(&final_t) { return Err(err("V10_RR_FINAL_T_DOMAIN")); }
        for i in 0..3 {
            state.ledgers.rr_events[i] += result.events[i];
            state.ledgers.v10_rr_cooling_ev[i] += result.cooling[i] / model.ev_erg;
        }
        state.ledgers.dr_events += result.events[3];
        state.ledgers.v10_dr_cooling_ev += result.cooling[3] / model.ev_erg;
        let binding = result.events[0] * model.threshold_ev[0]
            + (result.events[1] + result.events[3]) * model.threshold_ev[1]
            + result.events[2] * model.threshold_ev[2];
        state.ledgers.escaped_u += binding
            + result.cooling.iter().sum::<f64>() / model.ev_erg;
        Ok(())
    }
}

fn v10_strip_recomb(rhs: &mut IgmPointRhs, nh: f64, nhe: f64) {
    let rr = rhs.rr_events_cm3_s;
    let dr = rhs.dr_events_cm3_s;
    let cooling = rhs.rr_thermal_sink_erg_cm3_s.iter().sum::<f64>()
        + rhs.dr_thermal_sink_erg_cm3_s;
    let model = HHeModel::controlled_fixture();
    let binding = (0..3).map(|i| model.threshold_ev[i] * model.ev_erg * rr[i]).sum::<f64>()
        + model.threshold_ev[1] * model.ev_erg * dr;
    rhs.fraction_dt[0] += rr[0] / nh;
    rhs.species_chemical_cm3_s[0] -= rr[0];
    rhs.species_chemical_cm3_s[1] += rr[0];
    rhs.species_chemical_cm3_s[2] -= rr[1] + dr;
    rhs.species_chemical_cm3_s[3] += rr[1] + dr - rr[2];
    rhs.species_chemical_cm3_s[4] += rr[2];
    rhs.species_chemical_cm3_s[5] += rr[0] + rr[1] + rr[2] + dr;
    if nhe > 0.0 {
        rhs.fraction_dt[1] += (rr[1] + dr - rr[2]) / nhe;
        rhs.fraction_dt[2] += rr[2] / nhe;
    }
    rhs.w_dt_erg_per_h_s += cooling / nh;
    rhs.thermal_micro_erg_cm3_s += cooling;
    rhs.binding_micro_erg_cm3_s += binding;
    rhs.escape_erg_cm3_s -= binding + cooling;
    rhs.rr_events_cm3_s = [0.0; 3];
    rhs.dr_events_cm3_s = 0.0;
    rhs.rr_thermal_sink_erg_cm3_s = [0.0; 3];
    rhs.dr_thermal_sink_erg_cm3_s = 0.0;
}
