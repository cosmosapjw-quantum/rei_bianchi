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
use rei_microphysics::{Absorber, AtomicProvider, CharacteristicRay, GeometrySnapshot, HHeModel};
use std::{fmt::Write as _, sync::OnceLock, thread, time::Instant};
include!("case_a_micro.inc.rs");

const F_HE: f64 = 0.2454 / (4.0 * (1.0 - 0.2454));
const N0: f64 = 1.; // photons per H; ionization-front depletion negligible
const T0: f64 = 8.098143045064857;
const QS: [f64; 3] = [-0.005, 0., 0.005];
const STEPS: [usize; 4] = [1, 8, 32, 128];

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
    emitted_n: f64,
    emitted_u: f64,
    number_of_birth_cohorts: usize,
    source_flux_z_eV_H: f64,
    source_P2_eV_H: f64,
    remaining_flux_z_eV_H: f64,
    remaining_P2_eV_H: f64,
    below_UV_source_N_H: f64,
    below_UV_source_U_eV_H: f64,
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
        let recorded=format!("{base},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{},{:.17e}",
          m.ci[0],m.ci[1],m.ci[2],
          m.rr[0],m.rr[1],m.rr[2],m.dr,m.thermal,m.binding,m.escaped,
          m.cmb,m.energy_residual(),m.max_energy_local_residual,
          m.max_charge_local_residual,m.ce_cap,m.excluded_dr,
          m.ci_floor.iter().sum::<f64>(),m.n_substeps,self.boundary_u/p);
        format!(
            "{recorded},{:.17e},{:.17e},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            self.emitted_n,
            self.emitted_u,
            self.number_of_birth_cohorts,
            self.source_flux_z_eV_H,
            self.source_P2_eV_H,
            self.remaining_flux_z_eV_H,
            self.remaining_P2_eV_H,
            self.below_UV_source_N_H,
            self.below_UV_source_U_eV_H
        )
    }
}
fn do_case(q: f64, eta: f64, idx: usize, sub: usize) -> Result<[Summary; 2], String> {
    let start = Instant::now();
    let (d, init) = pick(q);
    let geo = steps_geo(q, sub);
    let ne = d.energies.len();
    let e0 = d
        .source
        .spectral_cells
        .iter()
        .map(|x| x.energy_ev * x.photon_fraction)
        .sum::<f64>();
    let sig = signatures();
    let ray = d.source.angular_cells.len() / 2;
    let mu = d.source.angular_cells[ray].mu;
    let dir = [(1. - mu * mu).sqrt(), 0., mu];
    let mut state = init.clone();
    // Both arms start with ZERO photons. Every photon is born from the
    // original MD14 BB50K source at its actual proper-time midpoint.
    let mut cohorts: Vec<CovariantPhoton> = Vec::new();
    let mut emitted_n = 0_f64;
    let mut emitted_u = 0_f64;
    let mut emitted_flux_z = 0_f64;
    let mut emitted_P2 = 0_f64;

    let gref = d
        .background
        .point_at_scale(1.0 / 21.0)
        .map_err(|e| format!("{e:?}"))?
        .geometry()
        .map_err(|e| format!("{e:?}"))?;
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
        // Only existing earlier-born cohorts accrue pre-emission redshift work.
        for cohort in &cohorts {
            if cohort.photons_per_h <= 0. {
                continue;
            }
            let before = cohort.energy_at(&step.g0).map_err(|e| format!("{e:?}"))?;
            let mid = cohort.energy_at(&step.gm).map_err(|e| format!("{e:?}"))?;
            exact_work += cohort.photons_per_h * (before - mid);
        }
        // PROJECTED: original native geometry map before source injection.
        d.geometry_map(&mut state, step.am)
            .map_err(|e| format!("{e:?}"))?;
        // Original MD14 BB50K total source, per-H per second; same clock
        // and angular spectrum across both lanes. 4π is already integrated.
        let zbar = 1.0 / step.am - 1.0;
        let rate = d
            .source
            .at_redshift(zbar)
            .map_err(|e| format!("{e:?}"))?
            .per_h_s;
        let rays: Vec<_> = d
            .source
            .angular_cells
            .iter()
            .map(|cell| {
                let dir = [(1. - cell.mu * cell.mu).sqrt(), 0., cell.mu];
                let ray = CharacteristicRay::new(1., dir, 0.).map_err(|e| format!("{e:?}"))?;
                let changed = ray
                    .pullback(&gref, &step.gm)
                    .map_err(|e| format!("{e:?}"))?;
                let jac = ray
                    .solid_angle_jacobian(&gref, &step.gm)
                    .map_err(|e| format!("{e:?}"))?;
                Ok::<_, String>((changed.direction, cell.count_fraction * jac))
            })
            .collect::<Result<Vec<_>, String>>()?;
        let sum_weight = rays.iter().map(|(_, w)| *w).sum::<f64>();
        if !sum_weight.is_finite() || sum_weight <= 0. {
            return Err("Invalid source angular normalization".into());
        }
        for (k, (direction, w)) in rays.iter().enumerate() {
            for spec in &d.source.spectral_cells {
                let n = rate * step.dt * spec.photon_fraction * (*w) / sum_weight;
                if n < 0. || !n.is_finite() {
                    return Err("Nonpositive source cohort".into());
                }
                let E = spec.energy_ev;
                emitted_n += n;
                emitted_u += n * E;
                let mu = direction[2];
                emitted_flux_z += n * E * mu;
                emitted_P2 += n * E * (3. * mu * mu - 1.) / 2.;

                let (bn, bu) = d
                    .deposit(&mut state.photons, k, E, n)
                    .map_err(|e| format!("{e:?}"))?;
                state.ledgers.source_n += n;
                state.ledgers.source_u += n * E;
                state.ledgers.boundary_n += bn;
                state.ledgers.boundary_u += bu;
                cohorts.push(
                    CovariantPhoton::from_local(&step.gm, E, *direction, n)
                        .map_err(|e| format!("{e:?}"))?,
                );
            }
        }
        // B: exact covariant photon energy at the same midpoint. Keep each
        // (source age, energy, angle, positive count) until the common end.
        // The density during a midpoint collision remains frozen; collect
        // species photon events before changing gas fractions.
        let mut b_events = [0.; 3];
        let mut b_heat = 0.;
        for photon in &mut cohorts {
            let prior = photon.photons_per_h;
            if prior == 0. {
                continue;
            }
            let r = absorb_frozen_gas(photon, &step.gm, neutral_b, step.dt)
                .map_err(|e| format!("{e:?}"))?;
            b_book.add(
                prior,
                r.final_packet.photons_per_h,
                r.absorbed_per_h,
                r.binding_ev_per_h,
                r.heat_ev_per_h,
            );
            for j in 0..3 {
                b_events[j] += r.absorbed_per_h[j];
            }
            b_heat += r.heat_ev_per_h;
            *photon = r.final_packet;
        }
        gas_b.photo(b_events, b_heat)?;
        for photon in &cohorts {
            if photon.photons_per_h == 0. {
                continue;
            }
            let mid = photon.energy_at(&step.gm).map_err(|e| format!("{e:?}"))?;
            let next = photon.energy_at(&step.g1).map_err(|e| format!("{e:?}"))?;
            exact_work += photon.photons_per_h * (mid - next);
        }
        // A: exact native spectral-bin energy for the Verner threshold source
        // and the identical gas/proper time midpoint.
        let mut a_events = [0.; 3];
        let mut a_heat = 0.;
        for k in 0..d.source.angular_cells.len() {
            for j in 0..ne {
                let pos = k * ne + j;
                let prior = state.photons[pos];
                if prior <= 0. {
                    continue;
                }
                let (after, event, bind, heat) =
                    absorb_grid(prior, d.energies[j], sig[j], neutral_a, step.dt);
                a_book.add(prior, after, event, bind, heat);
                for m in 0..3 {
                    a_events[m] += event[m];
                }
                a_heat += heat;
                state.photons[pos] = after;
            }
        }
        gas_a.photo(a_events, a_heat)?;
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
    let n_b = cohorts.iter().map(|x| x.photons_per_h).sum::<f64>();
    let energy_b = cohorts
        .iter()
        .map(|x| x.photons_per_h * x.energy_at(&geo.last().unwrap().g1).unwrap())
        .sum::<f64>();
    // Positive local angular radiation energy moment cone; C16's physical
    // 0/1/2-moment criterion is checked on actual independent photon stocks.
    let gend = &geo.last().unwrap().g1;
    let mut flux_a = 0_f64;
    let mut p2_a = 0_f64;
    for (k, cell) in d.source.angular_cells.iter().enumerate() {
        let direction = [(1. - cell.mu * cell.mu).sqrt(), 0., cell.mu];
        let ray = CharacteristicRay::new(1., direction, 0.).map_err(|e| format!("{e:?}"))?;
        let mu = ray
            .pullback(&gref, gend)
            .map_err(|e| format!("{e:?}"))?
            .direction[2];
        for j in 0..ne {
            let energy = state.photons[k * ne + j] * d.energies[j];
            flux_a += energy * mu;
            p2_a += energy * (3. * mu * mu - 1.) / 2.;
        }
    }
    let mut flux_b = 0_f64;
    let mut p2_b = 0_f64;
    let mut below_n_b = 0_f64;
    let mut below_u_b = 0_f64;
    for photon in &cohorts {
        if photon.photons_per_h <= 0. {
            continue;
        }
        let e = photon.energy_at(gend).map_err(|e| format!("{e:?}"))?;
        let mu = photon.direction_at(gend).map_err(|e| format!("{e:?}"))?[2];
        let u = photon.photons_per_h * e;
        flux_b += u * mu;
        p2_b += u * (3. * mu * mu - 1.) / 2.;
        if e < 13.6 {
            below_n_b += photon.photons_per_h;
            below_u_b += u;
        }
    }
    for (u, f, pi) in [(energy_a, flux_a, p2_a), (energy_b, flux_b, p2_b)] {
        let scale = (u * u).max(1e-80);
        if u < 0.
            || pi < -u / 2. - 1e-12 * u
            || pi > u + 1e-12 * u
            || 3. * f * f > u * (u + 2. * pi) + 1e-11 * scale
        {
            return Err("Photon U/F/P2 positive moment cone failed".into());
        }
    }
    if emitted_flux_z.abs() > 5e-11 * emitted_u {
        return Err(
            "Axially reflection-symmetric original stellar source has nonzero dipole".into(),
        );
    }
    let boundary_n = state.ledgers.boundary_n;
    let err_n_a = emitted_n - n_a - a_book.count() - boundary_n;
    let err_n_b = emitted_n - n_b - b_book.count();
    let err_e_a = emitted_u
        - energy_a
        - a_book.binding
        - a_book.heat
        - state.ledgers.photon_work
        - state.ledgers.boundary_u;
    let err_e_b = emitted_u - energy_b - b_book.binding - b_book.heat - exact_work;
    if (state.ledgers.source_n - emitted_n).abs() > 3e-12 * emitted_n
        || (state.ledgers.source_u - emitted_u).abs() > 3e-12 * emitted_u
    {
        return Err("Mismatch between original driver and exact source births".into());
    }
    let thermal_a =
        gas_initial_u + a_book.heat + micro_a.thermal - gas_a.u_ev_h - gas_a.adiabatic_loss;
    let thermal_b =
        gas_initial_u + b_book.heat + micro_b.thermal - gas_b.u_ev_h - gas_b.adiabatic_loss;
    for (en, ee, gt, b) in [
        (err_n_a, err_e_a, thermal_a, a_book),
        (err_n_b, err_e_b, thermal_b, b_book),
    ] {
        if en.abs() / emitted_n.max(1e-200) > 3e-9
            || ee.abs() / emitted_u.max(1e-200) > 3e-9
            || gt.abs() / gas_initial_u > 3e-9
            || b.event_residual.abs() / emitted_n.max(1e-200) > 3e-9
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
                micro: MicroBook,
                remaining_flux_z: f64,
                remaining_P2: f64,
                below_N: f64,
                below_U: f64| {
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
            emitted_n,
            emitted_u,
            number_of_birth_cohorts: cohorts.len(),
            source_flux_z_eV_H: emitted_flux_z,
            source_P2_eV_H: emitted_P2,
            remaining_flux_z_eV_H: remaining_flux_z,
            remaining_P2_eV_H: remaining_P2,
            below_UV_source_N_H: below_N,
            below_UV_source_U_eV_H: below_U,
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
            flux_a,
            p2_a,
            0.,
            0.,
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
            flux_b,
            p2_b,
            below_n_b,
            below_u_b,
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
            for idx in [16] {
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
    writeln!(&mut out,"q_ref,eta_initial,source_cells_per_segment,substeps,transport,mean_birth_energy_eV,x_HII_final,x_HeII_final,x_HeIII_final,electron_per_H_final,Tgas_final_K,u_thermal_final_eV_per_H,gas_adiabatic_loss_eV_per_H,gas_deposited_photoheat_eV_per_H,gas_max_charge_residual,surviving_photons_per_H,final_photon_energy_eV_per_H,boundary_photons_per_H,HI_absorbed_per_H,HeI_absorbed_per_H,HeII_absorbed_per_H,binding_eV_per_H,photoheat_eV_per_H,redshift_work_eV_per_H,photon_number_residual_per_H,photon_energy_residual_over_mean_birth_E,gas_thermal_residual_eV_per_H,photon_event_residual_per_H,heat_repeat_eV_per_H,thermal_repeat_eV_per_H,case_runtime_ms,CI_HI_per_H,CI_HeI_per_H,CI_HeII_per_H,RR_HII_per_H,RR_HeII_per_H,RR_HeIII_per_H,DR_HeII_per_H,micro_thermal_eV_per_H,micro_binding_eV_per_H,micro_escape_eV_per_H,micro_cmb_to_gas_eV_per_H,micro_energy_residual_eV_per_H,micro_max_local_energy_relative_error,micro_max_local_charge_error,micro_ce_cap_eV_per_H,micro_excluded_DR_eV_per_H,micro_CI_floor_events_per_H,micro_substeps,grid_boundary_energy_eV_per_H,emitted_photons_per_H,emitted_energy_eV_per_H,number_of_birth_cohorts,emitted_flux_z_eV_per_H,emitted_P2_eV_per_H,final_flux_z_eV_per_H,final_P2_eV_per_H,covariant_below_13p6_photons_per_H,covariant_below_13p6_energy_eV_per_H").unwrap();
    for record in results {
        writeln!(&mut out, "{}", record.row()).unwrap();
    }
    print!("{out}");
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn original_md14_birth_matches_independent_integral_and_both_lanes() {
        let [a, b] = do_case(0., 0., 16, 32).unwrap();
        let gl16_ref = 3.45955703510326897e-6;
        assert!((a.emitted_n - gl16_ref).abs() / gl16_ref < 2e-10);
        assert_eq!(a.emitted_n, b.emitted_n);
        assert_eq!(a.emitted_u, b.emitted_u);
        assert_eq!(a.number_of_birth_cohorts, 32 * 48 * 8);
    }
    #[test]
    fn all_original_stellar_births_are_axially_reflection_symmetric() {
        for q in QS {
            let [a, b] = do_case(q, 0., 16, 8).unwrap();
            assert!(a.source_flux_z_eV_H.abs() < 5e-11 * a.emitted_u);
            assert!(b.source_flux_z_eV_H.abs() < 5e-11 * b.emitted_u);
            assert!(a.source_P2_eV_H.abs() < 5e-11 * a.emitted_u);
            assert!(b.source_P2_eV_H.abs() < 5e-11 * b.emitted_u);
        }
    }
    #[test]
    fn projected_uv_lower_boundary_failure_without_physical_crossing() {
        let [a, b] = do_case(0., 0., 16, 8).unwrap();
        assert!(a.photon_boundary / a.emitted_n > 0.01);
        assert_eq!(b.photon_boundary, 0.);
        assert_eq!(b.below_UV_source_N_H, 0.);
        assert!(a.emitted_n > 0.);
    }
    #[test]
    fn true_grackle_case_a_recombination_changes_gas_and_remains_positive() {
        let [a, b] = do_case(0., 0., 16, 32).unwrap();
        for x in [a, b] {
            assert!(x.x_hii >= 0. && x.x_hii <= 1.);
            assert!(x.x_heii >= 0. && x.x_heiii >= 0.);
            assert!(x.x_heii + x.x_heiii <= 1. + 1e-12);
            assert!(x.micro.rr[0] > 0. && x.micro.rr[2] > 0.);
            assert!(x.micro.energy_residual().abs() < 3e-12);
            assert!(x.tgas > 1.);
        }
    }
}
