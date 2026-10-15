//! Minimal dynamical H/He + gas-internal-energy A/B on LRS Bianchi I.
//! SOURCE-SCOPED RESEARCH: photoionization-only, no recombination, no ongoing
//! emissivity or calibrated reionization closure. Production code unchanged.
//! A uses native Driver::geometry_map with per-half-step energy-grid deposition
//! and native AtomicProvider::cross_section at exact stored grid energies.
//! B uses CovariantPhoton conserved comoving momentum and original
//! absorb_frozen_gas at the SAME midpoint, gas densities and proper time.
//! Both update xHII, xHeII, xHeIII, gas thermal internal energy per H;
//! species, photons, threshold binding, photoheat, and adiabatic work are audited.
use rei_microphysics::axbi_driver::{Driver, DriverConfig, DriverState};
use rei_microphysics::axbi_q_reference::{absorb_frozen_gas, CovariantPhoton};
use rei_microphysics::{Absorber, AtomicProvider, GeometrySnapshot, HHeModel};
use std::{fmt::Write as _, sync::OnceLock, thread, time::Instant};
include!("case_a_micro.inc.rs");

const F_HE: f64 = 0.2454 / (4.0 * (1.0 - 0.2454));
const N0: f64 = 1e-6; // photons per H; ionization-front depletion negligible
const T0: f64 = 8.098143045064857;
const QS: [f64; 3] = [-0.005, 0., 0.005];
const STEPS: [usize; 3] = [1, 16, 128];

#[derive(Clone, Copy)]
struct GeoStep {
    a0: f64,
    am: f64,
    a1: f64,
    dt: f64,
    g0: GeometrySnapshot,
    gm: GeometrySnapshot,
    g1: GeometrySnapshot,
}
static DRIVERS: OnceLock<Vec<(f64, Driver, DriverState)>> = OnceLock::new();
fn drivers() -> &'static Vec<(f64, Driver, DriverState)> {
    DRIVERS.get_or_init(|| {
        QS.iter()
            .map(|&q| {
                let mut c = DriverConfig::baseline();
                c.q_ref = q;
                c.end_zbar = 19.998;
                c.background_panels = 4096;
                c.energy_subdivisions = 16;
                c.n_mu = 8;
                let (d, s) = Driver::new(c).expect("Original native source");
                (q, d, s)
            })
            .collect()
    })
}
fn pick(q: f64) -> (&'static Driver, &'static DriverState) {
    let v = drivers().iter().find(|(x, _, _)| *x == q).unwrap();
    (&v.1, &v.2)
}
static GEO: OnceLock<Vec<(f64, usize, Vec<GeoStep>)>> = OnceLock::new();
fn steps_geo(q: f64, n: usize) -> &'static [GeoStep] {
    let store = GEO.get_or_init(|| {
        let mut result = Vec::new();
        for &case in &QS {
            let (d, s) = pick(case);
            let start = s.a;
            let end = 1.0 / 20.998;
            let span = (end / start).ln();
            for &count in &STEPS {
                let mut v = Vec::with_capacity(count);
                for i in 1..=count {
                    let a0 = if i == 1 {
                        start
                    } else {
                        start * (span * ((i - 1) as f64) / (count as f64)).exp()
                    };
                    let a1 = if i == count {
                        end
                    } else {
                        start * (span * (i as f64) / (count as f64)).exp()
                    };
                    let am = (a0 * a1).sqrt();
                    let p0 = d.background.point_at_scale(a0).unwrap();
                    let pm = d.background.point_at_scale(am).unwrap();
                    let p1 = d.background.point_at_scale(a1).unwrap();
                    let dt = p1.time_s - p0.time_s;
                    assert!(dt > 0.);
                    v.push(GeoStep {
                        a0,
                        am,
                        a1,
                        dt,
                        g0: p0.geometry().unwrap(),
                        gm: pm.geometry().unwrap(),
                        g1: p1.geometry().unwrap(),
                    });
                }
                result.push((case, count, v));
            }
        }
        result
    });
    store
        .iter()
        .find(|(case, count, _)| *case == q && *count == n)
        .unwrap()
        .2
        .as_slice()
}
static SIG: OnceLock<Vec<[f64; 3]>> = OnceLock::new();
fn signatures() -> &'static [[f64; 3]] {
    SIG.get_or_init(|| {
        let energies = &pick(0.).0.energies;
        for &q in &QS {
            assert_eq!(&pick(q).0.energies, energies);
        }
        let provider = AtomicProvider::reference();
        let species = [Absorber::HI, Absorber::HeI, Absorber::HeII];
        energies
            .iter()
            .map(|&e| std::array::from_fn(|j| provider.cross_section(species[j], e).unwrap()))
            .collect()
    })
    .as_slice()
}

#[derive(Clone, Copy, Debug)]
struct Gas {
    h_ii: f64,
    he_ii: f64,
    he_iii: f64,
    u_ev_h: f64,
    adiabatic_loss: f64,
    deposited_heat: f64,
    max_charge_residual: f64,
}
impl Gas {
    fn new(eta: f64) -> Self {
        let hii = 1.0 - eta;
        let y = eta / 2.;
        let z = 1. - eta;
        let electrons = hii + F_HE * (y + 2. * z);
        let k = HHeModel::controlled_fixture().kb_erg_k / HHeModel::controlled_fixture().ev_erg;
        let u = 1.5 * k * T0 * (1. + F_HE + electrons);
        Self {
            h_ii: hii,
            he_ii: y,
            he_iii: z,
            u_ev_h: u,
            adiabatic_loss: 0.,
            deposited_heat: 0.,
            max_charge_residual: 0.,
        }
    }
    fn electron_per_h(&self) -> f64 {
        self.h_ii + F_HE * (self.he_ii + 2. * self.he_iii)
    }
    fn temperature(&self) -> f64 {
        let k = HHeModel::controlled_fixture().kb_erg_k / HHeModel::controlled_fixture().ev_erg;
        self.u_ev_h / (1.5 * k * (1. + F_HE + self.electron_per_h()))
    }
    fn nproper(&self, nh: f64) -> [f64; 3] {
        [
            nh * (1. - self.h_ii),
            nh * F_HE * (1. - self.he_ii - self.he_iii),
            nh * F_HE * self.he_ii,
        ]
    }
    fn cool(&mut self, a0: f64, a1: f64) {
        let fac = (a0 / a1).powi(2);
        let new = self.u_ev_h * fac;
        self.adiabatic_loss += self.u_ev_h - new;
        self.u_ev_h = new;
    }
    fn photo(&mut self, ev: [f64; 3], heat: f64) -> Result<(), String> {
        let available = [
            1. - self.h_ii,
            F_HE * (1. - self.he_ii - self.he_iii),
            F_HE * self.he_ii,
        ];
        for j in 0..3 {
            if ev[j] < -1e-23 || ev[j] > available[j] + 1e-14 {
                return Err(format!(
                    "Nucleus depletion at species {j}: event {} available {}",
                    ev[j], available[j]
                ));
            }
        }
        let old_e = self.electron_per_h();
        self.h_ii += ev[0];
        self.he_ii += (ev[1] - ev[2]) / F_HE;
        self.he_iii += ev[2] / F_HE;
        let electron_delta = self.electron_per_h() - old_e;
        let physical_delta: f64 = ev.iter().sum();
        self.max_charge_residual = self
            .max_charge_residual
            .max((electron_delta - physical_delta).abs());
        if !(self.h_ii >= 0.
            && self.h_ii <= 1. + 1e-12
            && self.he_ii >= -1e-12
            && self.he_iii >= 0.
            && self.he_ii + self.he_iii <= 1. + 1e-12
            && heat >= -1e-20)
        {
            return Err("Nonphysical fraction/heat".into());
        }
        self.u_ev_h += heat;
        self.deposited_heat += heat;
        Ok(())
    }
}
#[derive(Clone, Copy, Default)]
struct PhotonBook {
    absorbed: [f64; 3],
    binding: f64,
    heat: f64,
    event_residual: f64,
}
impl PhotonBook {
    fn add(&mut self, before: f64, after: f64, events: [f64; 3], b: f64, q: f64) {
        for j in 0..3 {
            self.absorbed[j] += events[j];
        }
        self.event_residual += before - after - events.iter().sum::<f64>();
        self.binding += b;
        self.heat += q;
    }
    fn count(&self) -> f64 {
        self.absorbed.iter().sum()
    }
}
fn absorb_grid(
    n: f64,
    e: f64,
    sig: [f64; 3],
    neutral: [f64; 3],
    dt: f64,
) -> (f64, [f64; 3], f64, f64) {
    let m = HHeModel::controlled_fixture();
    let rates = std::array::from_fn::<_, 3, _>(|j| m.c_cm_s * neutral[j] * sig[j]);
    let sum: f64 = rates.iter().sum();
    let lost = if sum > 0. {
        n * -(-sum * dt).exp_m1()
    } else {
        0.
    };
    let ev = std::array::from_fn(|j| if sum > 0. { lost * rates[j] / sum } else { 0. });
    let bind = (0..3).map(|j| ev[j] * m.threshold_ev[j]).sum();
    let heat = (0..3).map(|j| ev[j] * (e - m.threshold_ev[j])).sum();
    (n - lost, ev, bind, heat)
}
#[derive(Clone, Copy)]
struct Summary {
    arm: &'static str,
    q: f64,
    eta: f64,
    idx: usize,
    steps: usize,
    e0: f64,
    x_hii: f64,
    x_heii: f64,
    x_heiii: f64,
    xe: f64,
    tgas: f64,
    u: f64,
    gas_adiabatic: f64,
    gas_heat: f64,
    gas_charge_err: f64,
    photon_survive: f64,
    photon_energy: f64,
    photon_boundary: f64,
    boundary_u: f64,
    abs: [f64; 3],
    binding: f64,
    heating: f64,
    redshift_work: f64,
    photon_n_err: f64,
    photon_e_err: f64,
    thermal_e_err: f64,
    event_err: f64,
    elapsed_ms: f64,
    micro: MicroBook,
}
impl Summary {
    fn row(&self) -> String {
        let p = N0;
        let base=format!("{:.6e},{:.6e},{},{},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.8}",
            self.q,self.eta,self.idx,self.steps,self.arm,self.e0,
            self.x_hii,self.x_heii,self.x_heiii,self.xe,self.tgas,self.u,
            self.gas_adiabatic,self.gas_heat,self.gas_charge_err,
            self.photon_survive/p,self.photon_energy/p,self.photon_boundary/p,
            self.abs[0]/p,self.abs[1]/p,self.abs[2]/p,
            self.binding/p,self.heating/p,self.redshift_work/p,
            self.photon_n_err/p,self.photon_e_err/(p*self.e0),
            self.thermal_e_err,self.event_err/p,self.gas_heat/p,self.u,
            self.elapsed_ms);
        let m = &self.micro;
        format!("{base},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{},{:.17e}",
          m.ci[0],m.ci[1],m.ci[2],
          m.rr[0],m.rr[1],m.rr[2],m.dr,m.thermal,m.binding,m.escaped,
          m.cmb,m.energy_residual(),m.max_energy_local_residual,
          m.max_charge_local_residual,m.ce_cap,m.excluded_dr,
          m.ci_floor.iter().sum::<f64>(),m.n_substeps,self.boundary_u/p)
    }
}
fn do_case(q: f64, eta: f64, idx: usize, sub: usize) -> Result<[Summary; 2], String> {
    let start = Instant::now();
    let (d, init) = pick(q);
    let geo = steps_geo(q, sub);
    let ne = d.energies.len();
    let e0 = d.energies[idx];
    let sig = signatures();
    let ray = d.source.angular_cells.len() / 2;
    let mu = d.source.angular_cells[ray].mu;
    let dir = [(1. - mu * mu).sqrt(), 0., mu];
    let mut state = init.clone();
    state.photons[ray * ne + idx] = N0;
    state.ledgers.source_n = N0;
    state.ledgers.source_u = N0 * e0;
    let mut packet = CovariantPhoton::from_local(&geo[0].g0, e0, dir, N0).unwrap();
    let mut gas_a = Gas::new(eta);
    let mut gas_b = Gas::new(eta);
    let gas_initial_u = gas_a.u_ev_h;
    let (mut a_book, mut b_book) = (PhotonBook::default(), PhotonBook::default());
    let (mut micro_a, mut micro_b) = (MicroBook::default(), MicroBook::default());
    let mut exact_work = 0.;
    for step in geo {
        let nhmid = d.n_h0_cm3 / step.am.powi(3);
        gas_a.cool(step.a0, step.am);
        gas_b.cool(step.a0, step.am);
        let neutral_a = gas_a.nproper(nhmid);
        let neutral_b = gas_b.nproper(nhmid);
        // Exact characteristic transported source, absorption at exact midpoint.
        let prev = packet.energy_at(&step.g0).unwrap();
        let mid = packet.energy_at(&step.gm).unwrap();
        let next = packet.energy_at(&step.g1).unwrap();
        let before_b = packet.photons_per_h;
        exact_work += before_b * (prev - mid);
        let ab = absorb_frozen_gas(&packet, &step.gm, neutral_b, step.dt)
            .map_err(|e| format!("{e:?}"))?;
        b_book.add(
            before_b,
            ab.final_packet.photons_per_h,
            ab.absorbed_per_h,
            ab.binding_ev_per_h,
            ab.heat_ev_per_h,
        );
        gas_b.photo(ab.absorbed_per_h, ab.heat_ev_per_h)?;
        packet = ab.final_packet;
        exact_work += packet.photons_per_h * (mid - next);
        // Canonical energy grid source at same midpoint/proper clock.
        d.geometry_map(&mut state, step.am)
            .map_err(|e| format!("{e:?}"))?;
        let mut step_events = [0.; 3];
        let mut step_heat = 0.;
        for k in 0..d.source.angular_cells.len() {
            for j in 0..ne {
                let pos = k * ne + j;
                let prior = state.photons[pos];
                if prior <= 0. {
                    continue;
                }
                let (after, ev, bind, heat) =
                    absorb_grid(prior, d.energies[j], sig[j], neutral_a, step.dt);
                a_book.add(prior, after, ev, bind, heat);
                for m in 0..3 {
                    step_events[m] += ev[m];
                }
                step_heat += heat;
                state.photons[pos] = after;
            }
        }
        gas_a.photo(step_events, step_heat)?;
        // Original Case-A Grackle 3.4.1 source, with photo input zero because
        // photon events already transferred to the gas at this midpoint.
        // Proper time input is the native Bianchi background clock in seconds.
        let tcmb = 2.7255 / step.am;
        apply_original_case_a(&mut gas_a, nhmid, tcmb, step.dt, &mut micro_a)?;
        apply_original_case_a(&mut gas_b, nhmid, tcmb, step.dt, &mut micro_b)?;
        d.geometry_map(&mut state, step.a1)
            .map_err(|e| format!("{e:?}"))?;
        gas_a.cool(step.am, step.a1);
        gas_b.cool(step.am, step.a1);
    }
    let n_a: f64 = state.photons.iter().sum();
    let energy_a: f64 = state
        .photons
        .iter()
        .enumerate()
        .map(|(i, n)| n * d.energies[i % ne])
        .sum();
    let n_b = packet.photons_per_h;
    let energy_b = n_b * packet.energy_at(&geo.last().unwrap().g1).unwrap();
    let boundary_n = state.ledgers.boundary_n;
    let err_n_a = N0 - n_a - a_book.count() - boundary_n;
    let err_n_b = N0 - n_b - b_book.count();
    let err_e_a = N0 * e0
        - energy_a
        - a_book.binding
        - a_book.heat
        - state.ledgers.photon_work
        - state.ledgers.boundary_u;
    let err_e_b = N0 * e0 - energy_b - b_book.binding - b_book.heat - exact_work;
    let thermal_a =
        gas_initial_u + a_book.heat + micro_a.thermal - gas_a.u_ev_h - gas_a.adiabatic_loss;
    let thermal_b =
        gas_initial_u + b_book.heat + micro_b.thermal - gas_b.u_ev_h - gas_b.adiabatic_loss;
    for (en, ee, gt, b) in [
        (err_n_a, err_e_a, thermal_a, a_book),
        (err_n_b, err_e_b, thermal_b, b_book),
    ] {
        if en.abs() / N0 > 3e-9
            || ee.abs() / (N0 * e0) > 3e-9
            || gt.abs() / gas_initial_u > 3e-9
            || b.event_residual.abs() / N0 > 3e-9
        {
            return Err(format!(
                "Ledger violation: n={en} e={ee} thermal={gt} event={}",
                b.event_residual
            ));
        }
    }
    for m in [micro_a, micro_b] {
        let scale = m.thermal.abs() + m.binding.abs() + m.escaped.abs() + m.cmb.abs();
        if m.energy_residual().abs() > 3e-12 * scale.max(1e-30) {
            return Err(
                "Accumulated Case-A micro thermal/binding/escape/CMB energy imbalance".into(),
            );
        }
        if m.max_charge_local_residual > 2e-14 {
            return Err("Micro chemical electron source ledger failed".into());
        }
    }
    let elapsed_ms = start.elapsed().as_secs_f64() * 1000.;
    let pack = |arm,
                g: Gas,
                n: f64,
                energy: f64,
                b: PhotonBook,
                work: f64,
                bound: f64,
                bound_u: f64,
                ne_err: f64,
                ene_err: f64,
                therm_err: f64,
                micro: MicroBook| {
        Summary {
            arm,
            q,
            eta,
            idx,
            steps: sub,
            e0,
            x_hii: g.h_ii,
            x_heii: g.he_ii,
            x_heiii: g.he_iii,
            xe: g.electron_per_h(),
            tgas: g.temperature(),
            u: g.u_ev_h,
            gas_adiabatic: g.adiabatic_loss,
            gas_heat: g.deposited_heat,
            gas_charge_err: g.max_charge_residual,
            photon_survive: n,
            photon_energy: energy,
            photon_boundary: bound,
            boundary_u: bound_u,
            abs: b.absorbed,
            binding: b.binding,
            heating: b.heat,
            redshift_work: work,
            photon_n_err: ne_err,
            photon_e_err: ene_err,
            thermal_e_err: therm_err,
            event_err: b.event_residual,
            elapsed_ms,
            micro,
        }
    };
    Ok([
        pack(
            "PROJECTED",
            gas_a,
            n_a,
            energy_a,
            a_book,
            state.ledgers.photon_work,
            boundary_n,
            state.ledgers.boundary_u,
            err_n_a,
            err_e_a,
            thermal_a,
            micro_a,
        ),
        pack(
            "COVARIANT",
            gas_b,
            n_b,
            energy_b,
            b_book,
            exact_work,
            0.,
            0.,
            err_n_b,
            err_e_b,
            thermal_b,
            micro_b,
        ),
    ])
}
fn main() {
    let args: Vec<String> = std::env::args().collect();
    let jobs = if args.len() == 3 && args[1] == "--jobs" {
        args[2].parse::<usize>().expect("jobs")
    } else if args.len() == 1 {
        1
    } else {
        panic!("usage [--jobs 1|2]")
    };
    assert!(jobs == 1 || jobs == 2);
    let mut cases = Vec::new();
    for &q in &QS {
        for eta in [0., 1e-5] {
            for idx in [5, 32, 33] {
                for &n in &STEPS {
                    cases.push((q, eta, idx, n));
                }
            }
        }
    }
    // Precompute all original, identical background time/geometry histories
    // once, so independent cases do not repeat 4096-panel quadrature loops.
    let _ = drivers();
    let _ = signatures();
    let _ = steps_geo(0., 1);
    let mut results = Vec::new();
    if jobs == 1 {
        for &(q, e, idx, n) in &cases {
            results.extend_from_slice(&do_case(q, e, idx, n).unwrap());
        }
    } else {
        for chunk in cases.chunks(2) {
            let mut rows = Vec::new();
            thread::scope(|scope| {
                let tasks = chunk
                    .iter()
                    .map(|&(q, e, idx, n)| scope.spawn(move || do_case(q, e, idx, n)))
                    .collect::<Vec<_>>();
                for task in tasks {
                    rows.push(task.join().unwrap().unwrap());
                }
            });
            for r in rows {
                results.extend_from_slice(&r);
            }
        }
    }
    let mut out = String::new();
    writeln!(&mut out,"q_ref,eta_initial,energy_index,substeps,transport,initial_energy_eV,x_HII_final,x_HeII_final,x_HeIII_final,electron_per_H_final,Tgas_final_K,u_thermal_final_eV_per_H,gas_adiabatic_loss_eV_per_H,gas_deposited_photoheat_eV_per_H,gas_max_charge_residual,photon_survive_fraction,photon_final_energy_eV_per_initial,photon_boundary_fraction,HI_absorbed_fraction,HeI_absorbed_fraction,HeII_absorbed_fraction,binding_eV_per_initial,photoheat_eV_per_initial,redshift_work_eV_per_initial,photon_number_residual_relative,photon_energy_residual_relative,gas_thermal_residual_eV_per_H,photon_event_residual_relative,heat_repeat_eV_per_initial,thermal_repeat_eV_per_H,case_runtime_ms,CI_HI_per_H,CI_HeI_per_H,CI_HeII_per_H,RR_HII_per_H,RR_HeII_per_H,RR_HeIII_per_H,DR_HeII_per_H,micro_thermal_eV_per_H,micro_binding_eV_per_H,micro_escape_eV_per_H,micro_cmb_to_gas_eV_per_H,micro_energy_residual_eV_per_H,micro_max_local_energy_relative_error,micro_max_local_charge_error,micro_ce_cap_eV_per_H,micro_excluded_DR_eV_per_H,micro_CI_floor_events_per_H,micro_substeps,grid_boundary_energy_eV_per_initial").unwrap();
    for record in results {
        writeln!(&mut out, "{}", record.row()).unwrap();
    }
    print!("{out}");
}

#[cfg(test)]
mod source_tests {
    use super::*;
    #[test]
    fn native_case_a_provider_rates_are_used_at_cold_temperature() {
        let (d, initial) = pick(0.);
        let nh = d.n_h0_cm3 / initial.a.powi(3);
        let g = Gas::new(1e-5);
        let rhs = cold_original_case_a_point(&g, nh, 2.7255 / initial.a).unwrap();
        assert!(rhs.rr_events_cm3_s[0] > 0.);
        assert!(rhs.rr_events_cm3_s[2] > 0.);
        assert_eq!(rhs.dr_events_cm3_s, 0.);
        assert!(rhs.ci_events_cm3_s.iter().all(|&v| v >= 0.));
        let er = rhs.thermal_micro_erg_cm3_s + rhs.binding_micro_erg_cm3_s + rhs.escape_erg_cm3_s
            - rhs.cmb_to_gas_erg_cm3_s;
        assert!(er.abs() < 1e-38);
    }
    #[test]
    fn source_case_a_micro_records_recombination_charge_and_escape() {
        let (d, initial) = pick(0.);
        let nh = d.n_h0_cm3 / initial.a.powi(3);
        let mut gas = Gas::new(0.);
        let e_before = gas.electron_per_h();
        let mut book = MicroBook::default();
        apply_original_case_a(&mut gas, nh, 2.7255 / initial.a, 1.0e10, &mut book).unwrap();
        assert!(book.rr[0] > 0. && book.rr[2] > 0.);
        assert!(book.escaped > 0.);
        assert!(book.binding < 0.);
        assert!(book.max_energy_local_residual < 1e-12);
        let edelta = gas.electron_per_h() - e_before;
        let rhs_e = book.ci.iter().sum::<f64>() - book.rr.iter().sum::<f64>() - book.dr;
        assert!((edelta - rhs_e).abs() < 3e-14);
    }
    #[test]
    fn no_helium_source_at_first_midpoint_but_recombination_creates_heii() {
        let [a, b] = do_case(0., 0., 32, 1).unwrap();
        assert_eq!(a.abs[2], 0.);
        assert_eq!(b.abs[2], 0.);
        assert!(a.micro.rr[2] > 0. && b.micro.rr[2] > 0.);
        assert!(a.x_heii > 0. && b.x_heii > 0.);
    }
    #[test]
    fn grid_ghost_photoionizes_newly_recombined_helium() {
        let [a, b] = do_case(0., 0., 32, 16).unwrap();
        assert!(a.abs[2] > 0.5 * N0);
        assert_eq!(b.abs[2], 0.);
        assert!(a.x_heiii < b.x_heiii - 1e-6);
        assert!(a.micro.energy_residual().abs() < 2e-12);
        assert!(b.micro.energy_residual().abs() < 2e-12);
    }
    #[test]
    fn three_signed_cases_obey_species_positivity_and_full_source_energy() {
        for &q in &QS {
            let rows = do_case(q, 1e-5, 32, 16).unwrap();
            for r in rows {
                assert!(r.tgas > 1. && r.tgas < 1e6);
                assert!(r.x_hii >= 0. && r.x_hii <= 1.);
                assert!(r.x_heii >= 0. && r.x_heiii >= 0.);
                assert!(r.x_heii + r.x_heiii <= 1. + 1e-12);
                assert!(r.micro.energy_residual().abs() < 2e-12);
                assert!(r.thermal_e_err.abs() < 2e-14);
                assert!(r.photon_e_err.abs() / (N0 * r.e0) < 2e-12);
            }
        }
    }
}
