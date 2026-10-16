//! Research transaction around unchanged native Driver::chemical_stage.
use rei_microphysics::axbi_covariant_transport::PhotonState;
use rei_microphysics::axbi_driver::{Driver, DriverConfig, DriverState};
use rei_microphysics::igm_rates::{igm_rates, IgmRates};
use rei_microphysics::igm_state::IgmGasState;
use rei_microphysics::igm_thermal::{igm_point_rhs, IgmPointRhs};
use rei_microphysics::{ForwardError, HHeModel};
use std::{
    fmt::Write as FmtWrite,
    fs::{self, File},
    io::{self, BufRead, Write},
    path::Path,
    time::Instant,
};
pub const EV: f64 = 1.602176634e-12;
pub const TOL: f64 = 1e-10;
pub fn field<T: std::fmt::Debug>(s: &mut String, k: &str, v: T) {
    if s.len() > 1 {
        s.push(',');
    }
    write!(s, "\"{}\":{:?}", k, v).unwrap();
}
fn error(s: &'static str) -> ForwardError {
    ForwardError::InvalidInput(s)
}
pub fn rhs_json(v: &IgmPointRhs) -> String {
    let mut s = String::from("{");
    field(&mut s, "fraction_dt", v.fraction_dt);
    field(&mut s, "species_chemical_cm3_s", v.species_chemical_cm3_s);
    field(&mut s, "w_dt_erg_per_h_s", v.w_dt_erg_per_h_s);
    field(&mut s, "temperature_dt_k_s", v.temperature_dt_k_s);
    field(&mut s, "photo_events_cm3_s", v.photo_events_cm3_s);
    field(&mut s, "ci_events_cm3_s", v.ci_events_cm3_s);
    field(&mut s, "rr_events_cm3_s", v.rr_events_cm3_s);
    field(&mut s, "dr_events_cm3_s", v.dr_events_cm3_s);
    field(
        &mut s,
        "ci_thermal_sink_erg_cm3_s",
        v.ci_thermal_sink_erg_cm3_s,
    );
    field(
        &mut s,
        "rr_thermal_sink_erg_cm3_s",
        v.rr_thermal_sink_erg_cm3_s,
    );
    field(
        &mut s,
        "dr_thermal_sink_erg_cm3_s",
        v.dr_thermal_sink_erg_cm3_s,
    );
    field(
        &mut s,
        "ce_thermal_sink_erg_cm3_s",
        v.ce_thermal_sink_erg_cm3_s,
    );
    field(
        &mut s,
        "freefree_thermal_sink_erg_cm3_s",
        v.freefree_thermal_sink_erg_cm3_s,
    );
    field(&mut s, "thermal_micro_erg_cm3_s", v.thermal_micro_erg_cm3_s);
    field(&mut s, "binding_micro_erg_cm3_s", v.binding_micro_erg_cm3_s);
    field(&mut s, "escape_erg_cm3_s", v.escape_erg_cm3_s);
    field(&mut s, "cmb_to_gas_erg_cm3_s", v.cmb_to_gas_erg_cm3_s);
    field(&mut s, "photo_input_erg_cm3_s", v.photo_input_erg_cm3_s);
    field(
        &mut s,
        "expansion_work_erg_cm3_s",
        v.expansion_work_erg_cm3_s,
    );
    field(&mut s, "ci_floor_events_cm3_s", v.ci_floor_events_cm3_s);
    field(
        &mut s,
        "ce_cap_cooling_erg_cm3_s",
        v.ce_cap_cooling_erg_cm3_s,
    );
    field(
        &mut s,
        "excluded_dr_cooling_erg_cm3_s",
        v.excluded_dr_cooling_erg_cm3_s,
    );
    s.push('}');
    s
}
pub fn rates_json(v: &IgmRates) -> String {
    let mut s = String::from("{");
    field(&mut s, "ci_cm3_s", v.ci_cm3_s);
    field(&mut s, "rr_cm3_s", v.rr_cm3_s);
    field(&mut s, "dr_cm3_s", v.dr_cm3_s);
    field(&mut s, "ce_erg", v.ce_erg);
    field(&mut s, "rr_cooling_erg_cm3_s", v.rr_cooling_erg_cm3_s);
    field(&mut s, "dr_cooling_erg_cm3_s", v.dr_cooling_erg_cm3_s);
    field(
        &mut s,
        "dr_raw_cooling_erg_cm3_s",
        v.dr_raw_cooling_erg_cm3_s,
    );
    field(&mut s, "freefree_erg_cm3_s", v.freefree_erg_cm3_s);
    field(&mut s, "ci_floor_cm3_s", v.diagnostics.ci_floor_cm3_s);
    field(&mut s, "ce_cap_erg", v.diagnostics.ce_cap_erg);
    field(
        &mut s,
        "dr_excluded_erg_cm3_s",
        v.diagnostics.dr_excluded_erg_cm3_s,
    );
    field(&mut s, "dr_low_branch", v.diagnostics.dr_low_branch);
    s.push('}');
    s
}

#[derive(Clone, Debug)]
pub struct Cohort {
    pub t0: f64,
    pub t1: f64,
    pub birth: f64,
    pub number: f64,
    pub energy: f64,
    pub identity: &'static str,
}
#[derive(Clone, Debug)]
pub struct Accepted {
    pub state: DriverState,
    pub time: f64,
    pub cursor: usize,
    pub cohorts: Vec<Cohort>,
    pub transaction_checks: Vec<[f64; 3]>,
    pub construction: Vec<f64>,
    pub emission_roundoff: Vec<[f64; 4]>,
}
#[derive(Clone, Copy, Debug)]
pub enum Source {
    None,
    Pulse { on: f64, off: f64, rate: f64 },
    Md14,
}
#[derive(Clone, Debug)]
pub struct Fixture {
    pub name: &'static str,
    pub temperature: f64,
    pub fractions: [f64; 3],
    pub photons: [f64; 3],
    pub horizon: f64,
    pub q_ref: f64,
    pub helium: bool,
    pub source: Source,
}
pub struct Model {
    pub d: Driver,
    pub initial: Accepted,
    pub initial_energy: f64,
    pub initial_number: f64,
    pub initial_charge: f64,
    pub initial_fractions: [f64; 3],
    pub start: Instant,
}
pub fn photons(s: &DriverState) -> PhotonState {
    PhotonState {
        number: s.photons.clone(),
        energy_ref: s.photon_energy_ref.clone(),
        support_lo: s.photon_support_lo.clone(),
        support_hi: s.photon_support_hi.clone(),
    }
}
fn set_photons(s: &mut DriverState, p: PhotonState) {
    s.photons = p.number;
    s.photon_energy_ref = p.energy_ref;
    s.photon_support_lo = p.support_lo;
    s.photon_support_hi = p.support_hi;
}
pub fn make_driver(
    qref: f64,
    threads: usize,
    subdivisions: usize,
    nmu: usize,
    cells: usize,
    helium: bool,
) -> Result<(Driver, DriverState), ForwardError> {
    let mut cfg = DriverConfig::baseline();
    cfg.q_ref = qref;
    cfg.background_panels = 256;
    cfg.transport_threads = threads;
    cfg.energy_subdivisions = subdivisions;
    cfg.n_mu = nmu;
    cfg.transport_cells = cells;
    cfg.max_rhs = 4_000_000;
    cfg.max_wall_s = 300.0;
    let (mut d, mut s) = Driver::new(cfg)?;
    s.a = 0.1;
    if !helium {
        d.n_he0_cm3 = 0.0;
    }
    Ok((d, s))
}
pub fn setup(
    f: &Fixture,
    threads: usize,
    subdivisions: usize,
    nmu: usize,
    cells: usize,
) -> Result<Model, ForwardError> {
    let (d, mut s) = make_driver(f.q_ref, threads, subdivisions, nmu, cells, f.helium)?;
    let mut construction = vec![];
    if f.name == "md14_birth_cohort" {
        s.a = 1.0 / 21.0;
        let birth_geometry = d.background.point_at_scale(s.a)?.geometry()?;
        let mut p = photons(&s);
        let injected = d.transport.inject(&mut p, &birth_geometry, 20.0, 1e14)?;
        set_photons(&mut s, p);
        d.geometry_map(&mut s, 0.1)?;
        let inventory = d.photon_inventory(&s);
        construction = vec![
            1.0 / 21.0,
            0.1,
            20.0,
            1e14,
            injected.added_photons_per_h,
            injected.added_energy_ev_per_h,
            s.ledgers.photon_work,
            s.ledgers.thermal_work,
            inventory.0,
            inventory.1,
        ];
        // Reset the local physical-ledger origin after initial-condition
        // construction, retaining the construction work separately above.
        s.ledgers = rei_microphysics::axbi_driver::Ledgers::default();
    }

    let nh = d.n_h0_cm3 / s.a.powi(3);
    let nhe = d.n_he0_cm3 / s.a.powi(3);
    s.gas = IgmGasState::from_temperature(f.fractions, nh, nhe, f.temperature)?;
    // Each occupied ray/cell contains one reference-energy delta.
    let geometry = d.background.point_at_scale(s.a)?.geometry()?;
    let rays = d.transport.ray_geometry(&geometry)?;
    for (i, e) in [20.0, 40.0, 80.0].iter().enumerate() {
        d.seed_delta(&mut s, i, *e / rays[i].scale, f.photons[i])?;
    }
    let initial_energy = d.total_energy(&s)?;
    let initial_number = d.photon_inventory(&s).0;
    let y = d.n_he0_cm3 / d.n_h0_cm3;
    let initial_charge = f.fractions[0] + y * (f.fractions[1] + 2.0 * f.fractions[2]);
    Ok(Model {
        d,
        initial: Accepted {
            state: s,
            time: 0.0,
            cursor: 0,
            cohorts: vec![],
            transaction_checks: vec![],
            construction,
            emission_roundoff: vec![],
        },
        initial_energy,
        initial_number,
        initial_charge,
        initial_fractions: f.fractions,
        start: Instant::now(),
    })
}
#[derive(Clone, Debug)]
pub struct Invariants {
    pub energy_residual: f64,
    pub energy_scale: f64,
    pub number_residual: f64,
    pub number_scale: f64,
    pub charge_residual: f64,
    pub charge_scale: f64,
    pub species_residual: [f64; 3],
    pub species_scale: [f64; 3],
    pub source_number_residual: f64,
    pub source_energy_residual: f64,
    pub max_normalized: f64,
}
fn ratio(r: f64, scale: f64) -> f64 {
    if scale == 0.0 {
        if r == 0.0 {
            0.0
        } else {
            f64::INFINITY
        }
    } else {
        r.abs() / (TOL * scale)
    }
}
impl Model {
    pub fn validate(&self, a: &Accepted) -> Result<Invariants, ForwardError> {
        let s = &a.state;
        let [x, y, z] = s.gas.fractions;
        let nh = self.d.n_h0_cm3 / s.a.powi(3);
        let nhe = self.d.n_he0_cm3 / s.a.powi(3);
        let eos = s.gas.eos(nh, nhe)?;
        if !(0.0..=1.0).contains(&x)
            || y < 0.0
            || z < 0.0
            || y + z > 1.0
            || s.gas.w_erg_per_h <= 0.0
            || !(1.0..=1e6).contains(&eos.temperature_k)
        {
            return Err(error("RESEARCH_ADMISSIBILITY"));
        }
        self.d.transport.validate_state(&photons(s))?;
        if !s.photons.iter().all(|v| v.is_finite() && *v >= 0.0) {
            return Err(error("RESEARCH_PHOTONS"));
        }
        let l = &s.ledgers;
        let (n, u) = self.d.photon_inventory(s);
        let yy = self.d.n_he0_cm3 / self.d.n_h0_cm3;
        let chi = HHeModel::controlled_fixture().threshold_ev;
        let binding = chi[0] * x + yy * (chi[1] * y + (chi[1] + chi[2]) * z);
        let energy = self.d.total_energy(s)?;
        let er = energy - self.initial_energy;
        let escale = self.initial_energy.abs()
            + u.abs()
            + (s.gas.w_erg_per_h / EV).abs()
            + binding.abs()
            + l.escaped_u.abs()
            + l.cmb_input.abs()
            + l.source_u.abs()
            + l.boundary_u.abs();
        let nr = n + l.absorbed_n + l.boundary_n - l.source_n - self.initial_number;
        let nscale = self.initial_number.abs()
            + n.abs()
            + l.absorbed_n.abs()
            + l.source_n.abs()
            + l.boundary_n.abs();
        let charge = x + yy * (y + 2.0 * z);
        let forward: [f64; 3] =
            std::array::from_fn(|i| l.photo_events[i] + l.ci_events[i] - l.rr_events[i]);
        let cr = charge - self.initial_charge - forward.iter().sum::<f64>() + l.dr_events;
        let cscale = charge.abs()
            + self.initial_charge.abs()
            + l.photo_events.iter().map(|v| v.abs()).sum::<f64>()
            + l.ci_events.iter().map(|v| v.abs()).sum::<f64>()
            + l.rr_events.iter().map(|v| v.abs()).sum::<f64>()
            + l.dr_events.abs();
        let net = [
            forward[0],
            forward[1] - l.dr_events - forward[2],
            forward[2],
        ];
        let stocks = [x, yy * y, yy * z];
        let stocks0 = [
            self.initial_fractions[0],
            yy * self.initial_fractions[1],
            yy * self.initial_fractions[2],
        ];
        let species_residual = std::array::from_fn(|i| stocks[i] - stocks0[i] - net[i]);
        let species_scale = std::array::from_fn(|i| {
            stocks[i].abs()
                + stocks0[i].abs()
                + l.photo_events.iter().map(|v| v.abs()).sum::<f64>()
                + l.ci_events.iter().map(|v| v.abs()).sum::<f64>()
                + l.rr_events.iter().map(|v| v.abs()).sum::<f64>()
                + l.dr_events.abs()
        });
        let sn = a.cohorts.iter().map(|c| c.number).sum::<f64>();
        let su = a.cohorts.iter().map(|c| c.energy).sum::<f64>();
        let snr = sn - l.source_n;
        let sur = su - l.source_u;
        let max_normalized = [
            ratio(er, escale),
            ratio(nr, nscale),
            ratio(cr, cscale),
            ratio(snr, sn.abs() + l.source_n.abs()),
            ratio(sur, su.abs() + l.source_u.abs()),
        ]
        .into_iter()
        .chain((0..3).map(|i| ratio(species_residual[i], species_scale[i])))
        .fold(0.0, f64::max);
        let v = Invariants {
            energy_residual: er,
            energy_scale: escale,
            number_residual: nr,
            number_scale: nscale,
            charge_residual: cr,
            charge_scale: cscale,
            species_residual,
            species_scale,
            source_number_residual: snr,
            source_energy_residual: sur,
            max_normalized,
        };
        if !max_normalized.is_finite() || max_normalized > 1.0 {
            eprintln!("RESEARCH_CUMULATIVE_LEDGER {}", inv_json(&v));
            return Err(error("RESEARCH_LEDGER"));
        }
        Ok(v)
    }
    pub fn emit(&self, old: &Accepted, t1: f64, source: Source) -> Result<Accepted, ForwardError> {
        let mut a = old.clone();
        let dt = t1 - old.time;
        if !dt.is_finite() || dt <= 0.0 {
            return Err(error("RESEARCH_DT"));
        }
        let (number, energy, identity) = match source {
            Source::None => (0.0, 0.0, "NONE"),
            Source::Pulse { on, off, rate } => {
                let active = (t1.min(off) - old.time.max(on)).max(0.0);
                let count = rate * active;
                let before = self.d.photon_inventory(&a.state);
                let geom = self.d.background.point_at_scale(a.state.a)?.geometry()?;
                let rays = self.d.transport.ray_geometry(&geom)?;
                let old_photons = photons(&a.state);
                if a.state.photon_inactive_number.iter().any(|v| *v != 0.0)
                    || a.state.photon_inactive_energy_ref.iter().any(|v| *v != 0.0)
                {
                    return Err(error("PULSE_UNSUPPORTED_PASSIVE_STOCK"));
                }
                let mut stocks = [0.0; 3];
                let mut occupied = [0usize; 3];
                for k in 0..old_photons.number.len() {
                    if old_photons.number[k] == 0.0 {
                        continue;
                    }
                    let ray = k / self.d.transport.n_energy();
                    if ray >= 3 {
                        return Err(error("PULSE_UNRELATED_RAY"));
                    }
                    let q = [20.0, 40.0, 80.0][ray] / rays[ray].scale;
                    occupied[ray] += 1;
                    if occupied[ray] > 1
                        || old_photons.support_lo[k] != q
                        || old_photons.support_hi[k] != q
                        || old_photons.energy_ref[k] != q * old_photons.number[k]
                    {
                        return Err(error("PULSE_UNSUPPORTED_DELTA_LAYOUT"));
                    }
                    stocks[ray] = old_photons.number[k];
                }
                let mut fresh = self.d.transport.empty_state();
                let mut intended_energy = 0.0;
                for (i, (e, w)) in [(20.0, 0.5), (40.0, 0.3), (80.0, 0.2)].iter().enumerate() {
                    let q = e / rays[i].scale;
                    let birth = count * w;
                    self.d
                        .transport
                        .add_delta(&mut fresh, i, q, stocks[i] + birth)?;
                    intended_energy += birth * q * rays[i].scale;
                }
                set_photons(&mut a.state, fresh);
                let after = self.d.photon_inventory(&a.state);
                let represented = after.0 - before.0;
                let energy = after.1 - before.1;
                let number_scale = before.0.abs() + after.0.abs() + count.abs();
                let energy_scale = before.1.abs() + after.1.abs() + intended_energy.abs();
                let number_roundoff = count - represented;
                let energy_roundoff = intended_energy - energy;
                if number_roundoff.abs() > 128.0 * f64::EPSILON * number_scale
                    || energy_roundoff.abs() > 128.0 * f64::EPSILON * energy_scale
                {
                    return Err(error("PULSE_REPRESENTATION_ROUNDOFF"));
                }
                a.emission_roundoff.push([
                    number_roundoff,
                    number_scale,
                    energy_roundoff,
                    energy_scale,
                ]);
                a.state.ledgers.source_n += represented;
                a.state.ledgers.source_u += energy;
                (represented, energy, "FINITE_DURATION_DELTA_PULSE")
            }
            Source::Md14 => {
                let geometry = self.d.background.point_at_scale(a.state.a)?.geometry()?;
                let mut p = photons(&a.state);
                let l = self
                    .d
                    .transport
                    .inject(&mut p, &geometry, 1.0 / a.state.a - 1.0, dt)?;
                set_photons(&mut a.state, p);
                a.state.ledgers.source_n += l.added_photons_per_h;
                a.state.ledgers.source_u += l.added_energy_ev_per_h;
                (
                    l.added_photons_per_h,
                    l.added_energy_ev_per_h,
                    "NATIVE_MD14_EMISSIVITY",
                )
            }
        };
        if number > 0.0 {
            let (t0, tb) = match source {
                Source::Pulse { on, off, .. } => (old.time.max(on), t1.min(off)),
                _ => (old.time, t1),
            };
            a.cohorts.push(Cohort {
                t0,
                t1: tb,
                birth: 0.5 * (t0 + tb),
                number,
                energy,
                identity,
            });
            a.cursor += 1;
        }
        Ok(a)
    }
    pub fn trial(
        &self,
        old: &Accepted,
        dt: f64,
        source: Source,
        counter: &mut usize,
    ) -> Result<(Accepted, Invariants), ForwardError> {
        if !dt.is_finite() || dt <= 0.0 {
            return Err(error("RESEARCH_DT"));
        }
        let mut a = self.emit(old, old.time + dt, source)?;
        self.d.chemical_stage(&mut a.state, dt, counter)?;
        a.time = old.time + dt;
        a.state.accepted = old.state.accepted + 1;
        let inv = self.validate(&a)?;
        let old_s = &old.state;
        let new_s = &a.state;
        let lo = &old_s.ledgers;
        let ln = &new_s.ledgers;
        let (no, uo) = self.d.photon_inventory(old_s);
        let (nn, un) = self.d.photon_inventory(new_s);
        let yy = self.d.n_he0_cm3 / self.d.n_h0_cm3;
        let chi = HHeModel::controlled_fixture().threshold_ev;
        let reservoir = |st: &DriverState, u: f64| {
            let [x, y, z] = st.gas.fractions;
            u.abs()
                + (st.gas.w_erg_per_h / EV).abs()
                + (chi[0] * x + yy * (chi[1] * y + (chi[1] + chi[2]) * z)).abs()
        };
        let energy_r = self.d.total_energy(new_s)? - self.d.total_energy(old_s)?;
        let energy_scale = reservoir(old_s, uo)
            + reservoir(new_s, un)
            + (ln.escaped_u - lo.escaped_u).abs()
            + (ln.cmb_input - lo.cmb_input).abs()
            + (ln.source_u - lo.source_u).abs();
        let number_r = nn - no + (ln.absorbed_n - lo.absorbed_n) - (ln.source_n - lo.source_n);
        let number_scale = nn.abs()
            + no.abs()
            + (ln.absorbed_n - lo.absorbed_n).abs()
            + (ln.source_n - lo.source_n).abs();
        let event: [f64; 3] = std::array::from_fn(|i| {
            (ln.photo_events[i] - lo.photo_events[i]) + (ln.ci_events[i] - lo.ci_events[i])
                - (ln.rr_events[i] - lo.rr_events[i])
        });
        let dr = ln.dr_events - lo.dr_events;
        let stocks = |st: &DriverState| {
            [
                st.gas.fractions[0],
                yy * st.gas.fractions[1],
                yy * st.gas.fractions[2],
            ]
        };
        let so = stocks(old_s);
        let sn = stocks(new_s);
        let qo = so[0] + so[1] + 2.0 * so[2];
        let qn = sn[0] + sn[1] + 2.0 * sn[2];
        let event_scale = (0..3)
            .map(|i| {
                (ln.photo_events[i] - lo.photo_events[i]).abs()
                    + (ln.ci_events[i] - lo.ci_events[i]).abs()
                    + (ln.rr_events[i] - lo.rr_events[i]).abs()
            })
            .sum::<f64>()
            + dr.abs();
        let charge_r = qn - qo - event.iter().sum::<f64>() + dr;
        let charge_scale = qn.abs() + qo.abs() + event_scale;
        a.transaction_checks = vec![
            [energy_r, energy_scale, ratio(energy_r, energy_scale)],
            [number_r, number_scale, ratio(number_r, number_scale)],
            [charge_r, charge_scale, ratio(charge_r, charge_scale)],
        ];
        let net = [event[0], event[1] - dr - event[2], event[2]];
        for i in 0..3 {
            let r = sn[i] - so[i] - net[i];
            let scale = sn[i].abs() + so[i].abs() + event_scale;
            a.transaction_checks.push([r, scale, ratio(r, scale)]);
        }
        if a.transaction_checks
            .iter()
            .any(|v| !v[2].is_finite() || v[2] > 1.0)
        {
            eprintln!("RESEARCH_TRANSACTION_LEDGER {:?}", a.transaction_checks);
            return Err(error("RESEARCH_TRANSACTION_LEDGER"));
        }
        Ok((a, inv))
    }
}
pub fn inv_json(v: &Invariants) -> String {
    let mut s = String::from("{");
    field(&mut s, "energy_residual_ev_per_h", v.energy_residual);
    field(&mut s, "energy_scale_ev_per_h", v.energy_scale);
    field(&mut s, "number_residual_per_h", v.number_residual);
    field(&mut s, "number_scale_per_h", v.number_scale);
    field(&mut s, "charge_residual_per_h", v.charge_residual);
    field(&mut s, "charge_scale_per_h", v.charge_scale);
    field(&mut s, "species_residual_per_h", v.species_residual);
    field(&mut s, "species_scale_per_h", v.species_scale);
    field(
        &mut s,
        "source_number_residual_per_h",
        v.source_number_residual,
    );
    field(
        &mut s,
        "source_energy_residual_ev_per_h",
        v.source_energy_residual,
    );
    field(&mut s, "max_normalized", v.max_normalized);
    s.push('}');
    s
}
pub fn state_json(m: &Model, a: &Accepted) -> String {
    let d = &m.d;
    let s = &a.state;
    let l = &s.ledgers;
    let nh = d.n_h0_cm3 / s.a.powi(3);
    let nhe = d.n_he0_cm3 / s.a.powi(3);
    let eos = s.gas.eos(nh, nhe).unwrap();
    let (n, u) = d.photon_inventory(s);
    let g = d.background.point_at_scale(s.a).unwrap();
    let geometry = g.geometry().unwrap();
    let rays = d.transport.ray_geometry(&geometry).unwrap();
    let (mut p1, mut p2) = (0.0, 0.0);
    for (i, v) in s.photon_energy_ref.iter().enumerate() {
        let ray = rays[i / d.transport.n_energy()];
        p1 += v * ray.scale * ray.mu;
        p2 += v * ray.scale * ray.mu * ray.mu;
    }
    let mut out = String::from("{");
    field(&mut out, "time_s", a.time);
    field(&mut out, "transaction_checks", &a.transaction_checks);
    field(&mut out, "construction", &a.construction);
    field(&mut out, "emission_roundoff", &a.emission_roundoff);
    field(&mut out, "a", s.a);
    field(&mut out, "q_ref", d.config.q_ref);
    field(&mut out, "b", g.b);
    field(&mut out, "nh", nh);
    field(&mut out, "nhe", nhe);
    field(&mut out, "tcmb", 2.7255 / s.a);
    field(&mut out, "temperature", eos.temperature_k);
    field(&mut out, "fractions", s.gas.fractions);
    field(&mut out, "w", s.gas.w_erg_per_h);
    field(&mut out, "photon_number", n);
    field(&mut out, "photon_energy_ev_per_h", u);
    field(&mut out, "angular_energy_moments", [u, p1, p2]);
    field(&mut out, "photons", &s.photons);
    field(&mut out, "energy_ref", &s.photon_energy_ref);
    field(&mut out, "support_lo", &s.photon_support_lo);
    field(&mut out, "support_hi", &s.photon_support_hi);
    field(&mut out, "source_n", l.source_n);
    field(&mut out, "source_u", l.source_u);
    field(&mut out, "absorbed_n", l.absorbed_n);
    field(&mut out, "escape_ev_per_h", l.escaped_u);
    field(&mut out, "cmb_ev_per_h", l.cmb_input);
    field(&mut out, "photo_events", l.photo_events);
    field(&mut out, "rr_events", l.rr_events);
    field(&mut out, "ci_events", l.ci_events);
    field(&mut out, "dr_events", l.dr_events);
    field(&mut out, "ci_floor_events", l.ci_floor_events);
    field(&mut out, "ce_cap_ev", l.ce_cap_ev);
    field(&mut out, "excluded_dr_ev", l.excluded_dr_ev);
    field(&mut out, "accepted_steps", s.accepted);
    field(&mut out, "source_cursor", a.cursor);
    field(
        &mut out,
        "max_native_newton_residual",
        s.max_newton_residual,
    );
    field(&mut out, "transport_cells", d.transport.n_energy());
    field(
        &mut out,
        "transport_workers",
        d.transport.transport_threads(),
    );
    field(
        &mut out,
        "source_subdivisions",
        d.config.energy_subdivisions,
    );
    field(&mut out, "native_angles", d.config.n_mu);
    field(
        &mut out,
        "actual_ray_mu0",
        d.source
            .angular_cells
            .iter()
            .map(|v| v.mu)
            .collect::<Vec<_>>(),
    );
    field(
        &mut out,
        "delta_reference_q_ev",
        [
            20.0 / rays[0].scale,
            40.0 / rays[1].scale,
            80.0 / rays[2].scale,
        ],
    );
    field(&mut out, "actual_delta_energies_ev", [20.0, 40.0, 80.0]);
    write!(out, ",\"invariants\":{}", inv_json(&m.validate(a).unwrap())).unwrap();
    out.push('}');
    out
}
pub fn fixtures() -> Result<Vec<Fixture>, ForwardError> {
    let (d, s) = make_driver(0.0, 1, 16, 8, 64, true)?;
    let nh = d.n_h0_cm3 / s.a.powi(3);
    let nhe = d.n_he0_cm3 / s.a.powi(3);
    let f = [0.31, 0.23, 0.17];
    let ne = nh * f[0] + nhe * (f[1] + 2.0 * f[2]);
    let tr = 0.03 / (ne * igm_rates(8000.0)?.rr_cm3_s[0]);
    let th = 0.08 / (ne * igm_rates(1e5)?.ci_cm3_s[0]);
    let mut out = vec![
        Fixture {
            name: "recomb8000",
            temperature: 8000.0,
            fractions: f,
            photons: [0.0; 3],
            horizon: tr,
            q_ref: 0.0,
            helium: true,
            source: Source::None,
        },
        Fixture {
            name: "collision1e5",
            temperature: 1e5,
            fractions: f,
            photons: [0.0; 3],
            horizon: th,
            q_ref: 0.0,
            helium: true,
            source: Source::None,
        },
        Fixture {
            name: "mixed1e4",
            temperature: 1e4,
            fractions: f,
            photons: [0.013, 0.007, 0.003],
            horizon: 3e12,
            q_ref: 0.0,
            helium: true,
            source: Source::None,
        },
    ];
    for (name, t, helium, frac, count, horizon, q, source) in [
        ("cold100", 100.0, true, f, [0.0; 3], 1e12, 0.0, Source::None),
        (
            "cmb_heating10",
            10.0,
            true,
            f,
            [0.0; 3],
            1e13,
            0.0,
            Source::None,
        ),
        (
            "no_helium",
            1e4,
            false,
            f,
            [0.013, 0.007, 0.003],
            3e12,
            0.0,
            Source::None,
        ),
        (
            "tiny_ions",
            100.0,
            true,
            [1e-10, 2e-10, 1e-10],
            [0.0; 3],
            1e12,
            0.0,
            Source::None,
        ),
        (
            "strong_absorption",
            1e4,
            true,
            f,
            [0.3, 0.2, 0.1],
            1e13,
            0.0,
            Source::None,
        ),
        (
            "pulse_early",
            1e4,
            true,
            f,
            [0.0; 3],
            3e12,
            0.0,
            Source::Pulse {
                on: 0.0,
                off: 1.5e12,
                rate: 0.02 / 1.5e12,
            },
        ),
        (
            "pulse_delayed",
            1e4,
            true,
            f,
            [0.0; 3],
            3e12,
            0.0,
            Source::Pulse {
                on: 1.5e12,
                off: 3e12,
                rate: 0.02 / 1.5e12,
            },
        ),
        (
            "md14_smoke",
            1e4,
            true,
            f,
            [0.0; 3],
            1e12,
            0.0,
            Source::Md14,
        ),
        (
            "signed_plus",
            1e4,
            true,
            f,
            [0.013, 0.007, 0.003],
            3e12,
            0.1,
            Source::None,
        ),
        (
            "signed_minus",
            1e4,
            true,
            f,
            [0.013, 0.007, 0.003],
            3e12,
            -0.1,
            Source::None,
        ),
    ] {
        out.push(Fixture {
            name,
            temperature: t,
            fractions: frac,
            photons: count,
            horizon,
            q_ref: q,
            helium,
            source,
        });
    }
    Ok(out)
}
pub fn fixture_json(f: &Fixture) -> String {
    let mut s = String::from("{");
    field(&mut s, "name", f.name);
    field(&mut s, "temperature", f.temperature);
    field(&mut s, "fractions", f.fractions);
    field(&mut s, "initial_counts", f.photons);
    field(&mut s, "horizon_s", f.horizon);
    field(&mut s, "a", 0.1);
    field(&mut s, "q_ref", f.q_ref);
    field(&mut s, "helium", f.helium);
    field(&mut s, "source", format!("{:?}", f.source));
    s.push('}');
    s
}
pub fn run_one(
    f: &Fixture,
    n: usize,
    threads: usize,
    sub: usize,
    nmu: usize,
    cells: usize,
    out: &Path,
) -> Result<(), Box<dyn std::error::Error>> {
    let m = setup(f, threads, sub, nmu, cells)?;
    let mut a = m.initial.clone();
    let mut file = File::create(out)?;
    writeln!(file, "{}", state_json(&m, &a))?;
    let mut reject = File::create(out.with_extension("rejects.jsonl"))?;
    let mut count = 0usize;
    let mut attempts = 0usize;
    let base = f.horizon / n as f64;
    let mut max_inv = 0.0f64;
    for k in 0..n {
        let target = if k + 1 == n {
            f.horizon
        } else {
            (k + 1) as f64 * base
        };
        while a.time < target {
            let mut dt = target - a.time;
            if let Source::Pulse { on, off, .. } = f.source {
                for edge in [on, off] {
                    if edge > a.time && edge < a.time + dt {
                        dt = edge - a.time;
                    }
                }
            }
            let mut halves = 0;
            loop {
                attempts += 1;
                if attempts > 40000
                    || a.state.accepted >= 20000
                    || count > 4_000_000
                    || m.start.elapsed().as_secs_f64() > 290.0
                {
                    return Err("research execution cap".into());
                }
                match m.trial(&a, dt, f.source, &mut count) {
                    Ok((next, inv)) => {
                        max_inv = max_inv.max(inv.max_normalized);
                        a = next;
                        break;
                    }
                    Err(e) => {
                        writeln!(
                            reject,
                            "{{\"time\":{},\"dt\":{},\"error\":{:?},\"rollback_verified\":true}}",
                            a.time,
                            dt,
                            format!("{:?}", e)
                        )?;
                        halves += 1;
                        if halves > 20 {
                            return Err(format!("20halvings: {:?}", e).into());
                        }
                        dt *= 0.5;
                    }
                }
            }
        }
        writeln!(file, "{}", state_json(&m, &a))?;
    }
    let mut cohorts = File::create(out.with_extension("cohorts.jsonl"))?;
    for c in &a.cohorts {
        writeln!(cohorts,"{{\"t0\":{},\"t1\":{},\"birth_time\":{},\"emission_age_at_observation\":{},\"number\":{},\"energy_ev\":{},\"identity\":{:?}}}",c.t0,c.t1,c.birth,a.time-c.birth,c.number,c.energy,c.identity)?;
    }
    let mut summary = String::from("{");
    field(&mut summary, "fixture", f.name);
    field(&mut summary, "n", n);
    field(&mut summary, "threads", threads);
    field(&mut summary, "source_subdivisions", sub);
    field(&mut summary, "n_mu", nmu);
    field(&mut summary, "transport_cells", cells);
    field(&mut summary, "attempts", attempts);
    field(&mut summary, "accepted", a.state.accepted);
    field(&mut summary, "rhs_evaluations", count);
    field(&mut summary, "elapsed_s", m.start.elapsed().as_secs_f64());
    field(&mut summary, "max_invariant_normalized", max_inv);
    write!(summary, ",\"endpoint\":{}", state_json(&m, &a)).unwrap();
    summary.push('}');
    fs::write(out.with_extension("summary.json"), summary)?;
    Ok(())
}
pub fn rollback_tests(out: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let f = fixtures()?
        .into_iter()
        .find(|v| v.name == "pulse_early")
        .unwrap();
    let mut m = setup(&f, 1, 16, 8, 64)?;
    let old = m.initial.clone();
    let snapshot = format!("{:?}", old);
    let mut counter = 0;
    let invalid = m.trial(&old, -1.0, f.source, &mut counter).is_err();
    let invalid_no_rhs = counter == 0;
    m.d.config.max_rhs = 1;
    let source_trial = m.emit(&old, 1e10, f.source)?;
    let injected_before_failure = source_trial.cursor > old.cursor
        && source_trial.state.ledgers.source_n > old.state.ledgers.source_n;
    let fail = m.trial(&old, 1e10, f.source, &mut counter).is_err();
    let exact = snapshot == format!("{:?}", old);
    if !(invalid && invalid_no_rhs && fail && exact && injected_before_failure) {
        return Err("rollback test failed".into());
    }
    fs::write(out,format!("{{\"invalid_dt_rejected\":{},\"invalid_no_rhs\":{},\"native_failure_after_source\":{},\"accepted_state_bitwise_unchanged\":{},\"diagnostic_rhs_charged\":{}}}",invalid,invalid_no_rhs,fail,exact,counter))?;
    Ok(())
}
pub fn rhs_server(a: f64, qref: f64, helium: bool) -> Result<(), Box<dyn std::error::Error>> {
    let (d, _) = make_driver(qref, 1, 16, 8, 64, helium)?;
    let geometry = d.background.point_at_scale(a)?.geometry()?;
    let nh = d.n_h0_cm3 / a.powi(3);
    let nhe = d.n_he0_cm3 / a.powi(3);
    let rays = d.transport.ray_geometry(&geometry)?;
    let stdin = io::stdin();
    let mut stdout = io::BufWriter::new(io::stdout());
    for line in stdin.lock().lines() {
        let line = line?;
        let parts = line
            .split_whitespace()
            .map(str::parse::<f64>)
            .collect::<Result<Vec<_>, _>>()?;
        if parts.len() != 7 {
            return Err("expected7floats".into());
        }
        let eval = (|| -> Result<String, ForwardError> {
            let gas = IgmGasState::new([parts[0], parts[1], parts[2]], parts[3])?;
            let mut p = d.transport.empty_state();
            for i in 0..3 {
                d.transport.add_delta(
                    &mut p,
                    i,
                    [20.0, 40.0, 80.0][i] / rays[i].scale,
                    parts[4 + i],
                )?;
            }
            let abs = [
                nh * (1.0 - parts[0]),
                nhe * (1.0 - parts[1] - parts[2]),
                nhe * parts[1],
            ];
            let prep = d.transport.prepare(&p, &geometry)?;
            let absorption = prep.evaluate(abs, nh, 0.0)?;
            let rhs = igm_point_rhs(&gas, nh, nhe, 0.0, 2.7255 / a, absorption.photo)?;
            let eos = gas.eos(nh, nhe)?;
            let rates = igm_rates(eos.temperature_k)?;
            let mut deriv = vec![
                rhs.fraction_dt[0],
                rhs.fraction_dt[1],
                rhs.fraction_dt[2],
                rhs.w_dt_erg_per_h_s,
            ];
            let species = [
                rei_microphysics::Absorber::HI,
                rei_microphysics::Absorber::HeI,
                rei_microphysics::Absorber::HeII,
            ];
            let provider = rei_microphysics::AtomicProvider::reference();
            let mut energies = vec![];
            let mut sigmas = vec![];
            for i in 0..3 {
                let e = [20.0, 40.0, 80.0][i] / rays[i].scale * rays[i].scale;
                energies.push(e);
                let sigma: [f64; 3] =
                    std::array::from_fn(|j| provider.cross_section(species[j], e).unwrap());
                deriv.push(
                    -parts[4 + i]
                        * HHeModel::controlled_fixture().c_cm_s
                        * (0..3).map(|j| abs[j] * sigma[j]).sum::<f64>(),
                );
                sigmas.push(sigma);
            }
            let mut s = String::from("{");
            field(&mut s, "d", deriv);
            field(&mut s, "temperature", eos.temperature_k);
            field(&mut s, "nh", nh);
            field(&mut s, "nhe", nhe);
            field(&mut s, "tcmb", 2.7255 / a);
            field(&mut s, "actual_energy_ev", energies);
            field(&mut s, "sigma_cm2", sigmas);
            field(&mut s, "gamma_s", absorption.photo.gamma_s);
            field(
                &mut s,
                "heat_erg_per_absorber_s",
                absorption.photo.heat_erg_per_absorber_s,
            );
            write!(
                s,
                ",\"rhs\":{},\"rates\":{}",
                rhs_json(&rhs),
                rates_json(&rates)
            )
            .unwrap();
            s.push('}');
            Ok(s)
        })();
        match eval {
            Ok(s) => writeln!(stdout, "{}", s)?,
            Err(e) => writeln!(stdout, "{{\"error\":{:?}}}", format!("{:?}", e))?,
        };
        stdout.flush()?;
    }
    Ok(())
}

/// Test-only decomposition of native event owners. Integrated trajectories keep
/// every process active; these identities do not define altered providers.
pub fn isolated_event_tests(out: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let mut file = File::create(out)?;
    for t in [100.0, 8000.0, 1e4, 1e5] {
        let f = Fixture {
            name: "isolated_event",
            temperature: t,
            fractions: [0.31, 0.23, 0.17],
            photons: [0.013, 0.007, 0.003],
            horizon: 1.0,
            q_ref: 0.0,
            helium: true,
            source: Source::None,
        };
        let m = setup(&f, 1, 16, 8, 64)?;
        let s = &m.initial.state;
        let nh = m.d.n_h0_cm3 / s.a.powi(3);
        let nhe = m.d.n_he0_cm3 / s.a.powi(3);
        let geometry = m.d.background.point_at_scale(s.a)?.geometry()?;
        let abs = [
            nh * (1.0 - s.gas.fractions[0]),
            nhe * (1.0 - s.gas.fractions[1] - s.gas.fractions[2]),
            nhe * s.gas.fractions[1],
        ];
        let prepared = m.d.transport.prepare(&photons(s), &geometry)?;
        let photo = prepared.evaluate(abs, nh, 0.0)?.photo;
        let rhs = igm_point_rhs(&s.gas, nh, nhe, 0.0, 2.7255 / s.a, photo)?;
        let chi = HHeModel::controlled_fixture().threshold_ev;
        for process in [
            "photo_only_event_control",
            "CI_only_event_control",
            "RR_only_event_control",
        ] {
            let events = match process {
                "photo_only_event_control" => rhs.photo_events_cm3_s,
                "CI_only_event_control" => rhs.ci_events_cm3_s,
                _ => rhs.rr_events_cm3_s,
            };
            let sign = if process == "RR_only_event_control" {
                -1.0
            } else {
                1.0
            };
            let net = events.map(|v| sign * v);
            let species = [
                -net[0],
                net[0],
                -net[1],
                net[1] - net[2],
                net[2],
                net.iter().sum(),
            ];
            let binding = events
                .iter()
                .zip(chi)
                .map(|(e, c)| sign * e * c * EV)
                .sum::<f64>();
            let thermal = match process {
                "photo_only_event_control" => (0..3)
                    .map(|i| abs[i] * photo.heat_erg_per_absorber_s[i])
                    .sum(),
                "CI_only_event_control" => -rhs.ci_thermal_sink_erg_cm3_s.iter().sum::<f64>(),
                _ => -rhs.rr_thermal_sink_erg_cm3_s.iter().sum::<f64>(),
            };
            let escape = if process == "RR_only_event_control" {
                -binding - thermal
            } else {
                0.0
            };
            let input = if process == "photo_only_event_control" {
                binding + thermal
            } else {
                0.0
            };
            let residual = thermal + binding + escape - input;
            let scale = thermal.abs() + binding.abs() + escape.abs() + input.abs();
            let h = species[0] + species[1];
            let he = species[2] + species[3] + species[4];
            let charge = species[5] - species[1] - species[3] - 2.0 * species[4];
            let cscale = species.iter().map(|v| v.abs()).sum::<f64>();
            let reconstructed = EV
                * (chi[0] * species[1] + chi[1] * (species[3] + species[4]) + chi[2] * species[4]);
            if ratio(residual, scale) > 1.0
                || ratio(h, cscale) > 1.0
                || ratio(he, cscale) > 1.0
                || ratio(charge, cscale) > 1.0
                || ratio(reconstructed - binding, reconstructed.abs() + binding.abs()) > 1.0
            {
                return Err("isolated native event identity".into());
            }
            let mut row = String::from("{");
            field(&mut row, "temperature", t);
            field(&mut row, "test_only_control", process);
            field(&mut row, "events_cm3_s", events);
            field(&mut row, "species_cm3_s", species);
            field(&mut row, "thermal_erg_cm3_s", thermal);
            field(&mut row, "binding_erg_cm3_s", binding);
            field(&mut row, "escape_erg_cm3_s", escape);
            field(&mut row, "photo_input_erg_cm3_s", input);
            field(&mut row, "energy_residual_erg_cm3_s", residual);
            field(&mut row, "energy_scale_erg_cm3_s", scale);
            field(&mut row, "energy_normalized", ratio(residual, scale));
            field(&mut row, "hydrogen_residual", h);
            field(&mut row, "helium_residual", he);
            field(&mut row, "charge_residual", charge);
            field(
                &mut row,
                "binding_reconstruction_residual",
                reconstructed - binding,
            );
            row.push('}');
            writeln!(file, "{}", row)?;
        }
    }
    Ok(())
}
/// Three accepted original-driver steps only; dynamic native background/source
/// and both native expansion work owners are exercised without a history claim.
pub fn dynamic_smoke(out: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let mut file = File::create(out)?;
    for q in [0.0, 0.1, -0.1] {
        let mut cfg = DriverConfig::baseline();
        cfg.q_ref = q;
        cfg.background_panels = 256;
        cfg.transport_cells = 64;
        cfg.energy_subdivisions = 16;
        cfg.n_mu = 8;
        cfg.max_attempts = 1000;
        cfg.max_rhs = 30000;
        cfg.max_steps = 5;
        cfg.max_wall_s = 30.0;
        let (d, mut state) = Driver::new(cfg)?;
        let a0 = state.a;
        let start = Instant::now();
        let initial = d.total_energy(&state)?;
        while state.accepted < 3 {
            if start.elapsed().as_secs_f64() > 30.0 {
                return Err("dynamic smoke wall cap".into());
            }
            d.adaptive_step(&mut state)?;
        }
        d.validate(&state, 1e-10)?;
        let bg = d.background.point_at_scale(state.a)?;
        let geometry = bg.geometry()?;
        let nh = d.n_h0_cm3 / state.a.powi(3);
        let nhe = d.n_he0_cm3 / state.a.powi(3);
        let eos = state.gas.eos(nh, nhe)?;
        let (n, u) = d.photon_inventory(&state);
        let (nr, er) = d.residuals(&state)?;
        let mut row = String::from("{");
        field(&mut row, "q_ref", q);
        field(&mut row, "initial_a", a0);
        field(&mut row, "a", state.a);
        field(&mut row, "b", bg.b);
        field(&mut row, "s_per_s", bg.s_per_s);
        field(&mut row, "h_per_s", bg.h_per_s);
        field(&mut row, "sigma_s_over_h", bg.sigma);
        field(&mut row, "scale_factors", geometry.scale_factors);
        field(
            &mut row,
            "elapsed_proper_s",
            d.background.interval_increment(a0, state.a)?.proper_time_s,
        );
        field(&mut row, "temperature", eos.temperature_k);
        field(&mut row, "fractions", state.gas.fractions);
        field(&mut row, "photons_per_h", n);
        field(&mut row, "photon_energy_ev_per_h", u);
        field(&mut row, "source_n", state.ledgers.source_n);
        field(&mut row, "source_u", state.ledgers.source_u);
        field(
            &mut row,
            "thermal_work_ev_per_h",
            state.ledgers.thermal_work,
        );
        field(&mut row, "photon_work_ev_per_h", state.ledgers.photon_work);
        field(&mut row, "escape_ev_per_h", state.ledgers.escaped_u);
        field(&mut row, "cmb_ev_per_h", state.ledgers.cmb_input);
        field(&mut row, "number_residual", nr);
        field(&mut row, "energy_residual", er);
        field(&mut row, "initial_total_energy", initial);
        field(&mut row, "accepted", state.accepted);
        field(&mut row, "attempts", state.attempts);
        field(&mut row, "rejects", state.rejects);
        field(&mut row, "rhs_evaluations", state.rhs_evaluations);
        field(&mut row, "elapsed_wall_s", start.elapsed().as_secs_f64());
        row.push('}');
        writeln!(file, "{}", row)?;
    }
    Ok(())
}

/// Test-only reject-once after a successful native evaluation; compare recovered
/// half steps to clean half steps. No default transaction path is altered.
pub fn retry_recovery_test(out: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let f = fixtures()?
        .into_iter()
        .find(|v| v.name == "pulse_early")
        .unwrap();
    let m = setup(&f, 1, 16, 8, 64)?;
    let old = m.initial.clone();
    let before = format!("{:?}", old);
    let mut attempted_rhs = 0;
    let discarded = m.trial(&old, 1e10, f.source, &mut attempted_rhs)?;
    let source_in_discarded = discarded.0.state.ledgers.source_n;
    drop(discarded);
    let first = m.trial(&old, 5e9, f.source, &mut attempted_rhs)?.0;
    let recovered = m.trial(&first, 5e9, f.source, &mut attempted_rhs)?.0;
    let mut clean_rhs = 0;
    let clean_first = m.trial(&old, 5e9, f.source, &mut clean_rhs)?.0;
    let clean = m.trial(&clean_first, 5e9, f.source, &mut clean_rhs)?.0;
    let equal = format!("{:?}", recovered) == format!("{:?}", clean);
    let unchanged = before == format!("{:?}", old);
    let expected = 0.02 / 1.5e12 * 1e10;
    let no_duplicate = (recovered.state.ledgers.source_n - expected).abs() <= 1e-12 * expected
        && recovered.cursor == 2
        && recovered.cohorts.len() == 2;
    if !(equal && unchanged && no_duplicate) {
        return Err("rejected trial recovery mismatch".into());
    }
    fs::write(out,format!("{{\"test_only_reject_after_native_success\":true,\"old_state_bitwise_unchanged\":{},\"recovered_equal_clean_half_steps\":{},\"no_duplicate_source\":{},\"discarded_source_count\":{},\"committed_source_count\":{},\"committed_cursor\":{},\"diagnostic_rhs_includes_discarded\":{},\"clean_rhs\":{}}}",unchanged,equal,no_duplicate,source_in_discarded,recovered.state.ledgers.source_n,recovered.cursor,attempted_rhs,clean_rhs))?;
    Ok(())
}
