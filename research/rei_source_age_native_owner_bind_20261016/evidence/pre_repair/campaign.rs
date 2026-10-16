mod native_owner;
use native_owner::*;
use rei_microphysics::axbi_driver::{Driver, DriverConfig};
use rei_microphysics::igm_state::IgmGasState;
use std::{fs, io::Write, path::Path};
fn driver(
    q: f64,
    nmu: usize,
    cells: usize,
) -> Result<(Driver, Accepted), Box<dyn std::error::Error>> {
    let mut cfg = DriverConfig::baseline();
    cfg.q_ref = q;
    cfg.n_mu = nmu;
    cfg.energy_subdivisions = 2;
    cfg.transport_cells = cells;
    cfg.background_panels = 256;
    cfg.inactive_hi_split = false;
    cfg.max_rhs = 2_000_000;
    cfg.transport_threads = 1;
    cfg.parallel_jacobian_columns = false;
    let (d, mut s) = Driver::new(cfg)?;
    s.gas = IgmGasState::from_temperature(
        [0.01, 0.01, 0.001],
        d.n_h0_cm3 / s.a.powi(3),
        d.n_he0_cm3 / s.a.powi(3),
        8000.,
    )?;
    Ok((d, empty(s)))
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();
    if args.get(1).map(String::as_str) == Some("rhs") {
        return oracle_server();
    }
    let out = Path::new(args.get(1).map(String::as_str).unwrap_or("."));
    fs::create_dir_all(out)?;
    let mut checks = fs::File::create(out.join("checks.txt"))?;
    let mut count = 0;
    let (d, old) = driver(0., 8, 16)?;
    let to = old.gas_owner.a * 1.0001;
    let seeded = trial(&d, &old, to, 1, &mut count)?;
    // Single-cohort exact parity: the native aggregate equals its sole cohort.
    let mut one = seeded.clone();
    let mut native = one.gas_owner.clone();
    let p = &one.cohorts[0].surviving;
    native.photons = p.number.clone();
    native.photon_energy_ref = p.energy_ref.clone();
    native.photon_support_lo = p.support_lo.clone();
    native.photon_support_hi = p.support_hi.clone();
    let mut nc = 0;
    d.chemical_stage(&mut native, 1e9, &mut nc)?;
    one = chemistry(&d, &one, 1e9, &mut count)?;
    assert_eq!(native.gas.fractions, one.gas_owner.gas.fractions);
    assert_eq!(native.gas.w_erg_per_h, one.gas_owner.gas.w_erg_per_h);
    assert_eq!(native.photons, one.cohorts[0].surviving.number);
    writeln!(checks, "one_cohort_native_parity=PASS")?;
    let before = format!("{:?}", seeded);
    let bad = trial(&d, &seeded, seeded.gas_owner.a * 1.0001, 0, &mut count);
    assert!(bad.is_err());
    assert_eq!(before, format!("{:?}", seeded));
    writeln!(checks, "invalid_trial_atomic_rollback=PASS")?;
    let mut capped = 1;
    let mut capcfg = d.config.clone();
    capcfg.max_rhs = 1;
    let (capd, _) = Driver::new(capcfg)?;
    assert!(trial(&capd, &seeded, seeded.gas_owner.a * 1.0001, 1, &mut capped).is_err());
    assert_eq!(before, format!("{:?}", seeded));
    writeln!(checks, "rhs_failure_atomic_rollback=PASS")?;
    let two = trial(&d, &old, to, 2, &mut count)?;
    let mut reverse = two.clone();
    reverse.cohorts.reverse();
    let a = chemistry(&d, &two, 1e9, &mut count)?;
    let b = chemistry(&d, &reverse, 1e9, &mut count)?;
    for k in 0..3 {
        assert!((a.gas_owner.gas.fractions[k] - b.gas_owner.gas.fractions[k]).abs() < 1e-13);
    }
    writeln!(checks, "cohort_permutation=PASS")?;
    // Distinct monoenergetic supports sharing one grid cell must not be merged.
    let mut split = seeded.clone();
    split.cohorts.clear();
    let edges = d.transport.edges();
    let cell = edges
        .windows(2)
        .position(|w| w[0] > 30. && w[1] < 50.)
        .unwrap();
    let qlo = edges[cell] * 0.75 + edges[cell + 1] * 0.25;
    let qhi = edges[cell] * 0.25 + edges[cell + 1] * 0.75;
    for q in [qlo, qhi] {
        let mut c = seeded.cohorts[0].clone();
        c.surviving = d.transport.empty_state();
        d.transport.add_delta(&mut c.surviving, 0, q, 0.001)?;
        c.birth.original = c.surviving.clone();
        split.cohorts.push(c);
    }
    let split_out = chemistry(&d, &split, 1e10, &mut count)?;
    let k = split.cohorts[0]
        .surviving
        .number
        .iter()
        .position(|v| *v > 0.)
        .unwrap();
    assert_eq!(split_out.cohorts[0].surviving.support_lo[k], qlo);
    assert_eq!(split_out.cohorts[1].surviving.support_lo[k], qhi);
    let survival0 = split_out.cohorts[0].surviving.number[k] / 0.001;
    let survival1 = split_out.cohorts[1].surviving.number[k] / 0.001;
    assert!((survival0 - survival1).abs() > 1e-8);
    writeln!(
        checks,
        "same_cell_distinct_support_survival=PASS,{survival0},{survival1}"
    )?;
    let geometry = d.geometry_point(old.gas_owner.a)?.geometry()?;
    let ray = d.transport.ray_geometry(&geometry)?;
    let chi = rei_microphysics::HHeModel::controlled_fixture().threshold_ev;
    let ev = rei_microphysics::HHeModel::controlled_fixture().ev_erg;
    for (k, threshold) in [13.60, 24.59, 54.42].iter().enumerate() {
        assert!(*threshold > chi[k]);
        let energy = *threshold + 0.1;
        let mut p = d.transport.empty_state();
        d.transport
            .add_delta(&mut p, 0, energy / ray[0].scale, 0.001)?;
        let abs = d
            .transport
            .prepare(&p, &geometry)?
            .evaluate([1., 1., 1.], 1., 0.)?;
        assert!(
            (abs.photo.heat_erg_per_absorber_s[k] / abs.photo.gamma_s[k] / ev - (energy - chi[k]))
                .abs()
                < 1e-12
        );
    }
    writeln!(checks, "fit_activation_vs_physical_binding=PASS")?;
    for c in &two.cohorts {
        let n = c.birth.original.number.iter().sum::<f64>();
        assert!((n - c.birth.j_per_h_dln_a * c.birth.quadrature_weight_dln_a).abs() < 1e-13 * n);
        assert!(c.birth.x > c.birth.lower_x && c.birth.x < c.birth.upper_x);
    }
    writeln!(checks, "positive_birth_clock_mapping=PASS")?;
    let mut raw = fs::File::create(out.join("history.csv"))?;
    writeln!(raw,"q,nmu,cells,source_spectral,time_steps,age_panels,a,cohorts,N,U,xHII,xHeII,xHeIII,w,energy_residual,photon_residual,photoHI,photoHeI,photoHeII,rrHI,rrHeI,rrHeII,ciHI,ciHeI,ciHeII,escaped,cmb,photon_work,thermal_work,rhs")?;
    for q in [-0.1, 0., 0.1] {
        for (axis, level) in [
            (0, 1),
            (0, 2),
            (0, 4),
            (1, 1),
            (1, 2),
            (1, 4),
            (2, 1),
            (2, 2),
            (2, 4),
            (3, 1),
            (3, 2),
            (3, 4),
            (4, 1),
            (4, 2),
            (4, 4),
        ] {
            let nmu = if axis == 2 { 8 * level } else { 8 };
            let cells = if axis == 3 { 16 * level } else { 16 };
            let age = if axis == 1 { 4 * level } else { 4 };
            let steps = if axis == 0 { 4 * level } else { 4 };
            let (d0, s0) = driver(q, nmu, cells)?;
            let mut cfg = d0.config.clone();
            cfg.energy_subdivisions = if axis == 4 { 8 * level } else { 8 };
            cfg.initial_dln_a = 0.002 / steps as f64;
            let (d, _) = Driver::new(cfg)?;
            let e0 = energy(&d, &s0)?;
            let to = s0.gas_owner.a * 0.002f64.exp();
            let mut rhs = 0;
            let s = trial(&d, &s0, to, age, &mut rhs)?;
            let (n, u) = inventory(&d, &s)?;
            let l = &s.gas_owner.ledgers;
            let f = s.gas_owner.gas.fractions;
            let row = vec![
                q,
                nmu as f64,
                cells as f64,
                d.config.energy_subdivisions as f64,
                steps as f64,
                age as f64,
                s.gas_owner.a,
                s.cohorts.len() as f64,
                n,
                u,
                f[0],
                f[1],
                f[2],
                s.gas_owner.gas.w_erg_per_h,
                energy(&d, &s)? - e0,
                n + l.absorbed_n - l.source_n,
                l.photo_events[0],
                l.photo_events[1],
                l.photo_events[2],
                l.rr_events[0],
                l.rr_events[1],
                l.rr_events[2],
                l.ci_events[0],
                l.ci_events[1],
                l.ci_events[2],
                l.escaped_u,
                l.cmb_input,
                l.photon_work,
                l.thermal_work,
                rhs as f64,
            ];
            writeln!(
                raw,
                "{}",
                row.iter()
                    .map(|v| format!("{v:.17e}"))
                    .collect::<Vec<_>>()
                    .join(",")
            )?;
            // Complete accepted state permits independent replay, including surviving ages.
            fs::write(
                out.join(format!("snapshot_q{q}_axis{axis}_level{level}.txt")),
                format!("{:?}", s),
            )?;
        }
    }
    // Native nonlinear constant-geometry histories for independent Radau comparison.
    for steps in [16, 32, 64, 128] {
        let (d, s) = driver(0., 8, 16)?;
        let mut s = oracle_fixture(&d, s)?;
        let mut rhs = 0;
        let mut f = fs::File::create(out.join(format!("oracle_native_{steps}.csv")))?;
        writeln!(f, "t,x,y,z,w_ev,n0,n1,n2")?;
        for i in 0..=steps {
            let y = oracle_state(&d, &s)?;
            writeln!(
                f,
                "{},{}",
                i as f64 * 1e11 / steps as f64,
                y.iter()
                    .map(|v| format!("{v:.17e}"))
                    .collect::<Vec<_>>()
                    .join(",")
            )?;
            if i < steps {
                s = chemistry(&d, &s, 1e11 / steps as f64, &mut rhs)?;
            }
        }
    }
    writeln!(checks, "chronological_md14_signed_campaign=PASS")?;
    Ok(())
}

fn oracle_fixture(d: &Driver, mut s: Accepted) -> Result<Accepted, Box<dyn std::error::Error>> {
    let born = trial(d, &s, s.gas_owner.a * 1.000001, 1, &mut 0)?;
    let g = d.geometry_point(s.gas_owner.a)?.geometry()?;
    let ray = d.transport.ray_geometry(&g)?;
    for e in [20., 40., 80.] {
        let mut c = born.cohorts[0].clone();
        c.surviving = d.transport.empty_state();
        d.transport
            .add_delta(&mut c.surviving, 0, e / ray[0].scale, 0.002)?;
        c.birth.original = c.surviving.clone();
        s.cohorts.push(c);
    }
    Ok(s)
}
fn oracle_state(_d: &Driver, s: &Accepted) -> Result<Vec<f64>, Box<dyn std::error::Error>> {
    let g = &s.gas_owner.gas;
    let mut v = vec![
        g.fractions[0],
        g.fractions[1],
        g.fractions[2],
        rei_microphysics::igm_state::w_erg_per_h_to_ev(g.w_erg_per_h)?,
    ];
    for c in &s.cohorts {
        v.push(c.surviving.number.iter().sum());
    }
    Ok(v)
}
fn oracle_server() -> Result<(), Box<dyn std::error::Error>> {
    use rei_microphysics::axbi_rates::AxbiProvider;
    use rei_microphysics::igm_thermal::IgmPhotoInput;
    use std::io::{self, BufRead};
    let (d, s0) = driver(0., 8, 16)?;
    let fixture = oracle_fixture(&d, s0)?;
    let a = fixture.gas_owner.a;
    let nh = d.n_h0_cm3 / a.powi(3);
    let nhe = d.n_he0_cm3 / a.powi(3);
    let geometry = d.geometry_point(a)?.geometry()?;
    let prepared = fixture
        .cohorts
        .iter()
        .map(|c| d.transport.prepare(&c.surviving, &geometry))
        .collect::<Result<Vec<_>, _>>()?;
    for line in io::stdin().lock().lines() {
        let x = line?
            .split_whitespace()
            .map(str::parse::<f64>)
            .collect::<Result<Vec<_>, _>>()?;
        if x.len() != 7 {
            return Err("oracle expects seven state variables".into());
        }
        let gas = IgmGasState::new(
            [x[0], x[1], x[2]],
            rei_microphysics::igm_state::w_ev_per_h_to_erg(x[3])?,
        )?;
        let ab = [nh * (1. - x[0]), nhe * (1. - x[1] - x[2]), nhe * x[1]];
        let mut photo = IgmPhotoInput::default();
        let mut dn = vec![];
        for (j, p) in prepared.iter().enumerate() {
            let r = p.evaluate(ab, nh, 0.)?;
            let scale = x[4 + j] / 0.002;
            for k in 0..3 {
                photo.gamma_s[k] += r.photo.gamma_s[k] * scale;
                photo.heat_erg_per_absorber_s[k] += r.photo.heat_erg_per_absorber_s[k] * scale;
            }
            dn.push(
                -(0..3)
                    .map(|k| ab[k] / nh * r.photo.gamma_s[k] * scale)
                    .sum::<f64>(),
            );
        }
        let rhs = AxbiProvider
            .point(&gas, nh, nhe, 0., 2.7255 / a, photo)?
            .rhs;
        let mut v = rhs.fraction_dt.to_vec();
        v.push(rhs.w_dt_erg_per_h_s / rei_microphysics::HHeModel::controlled_fixture().ev_erg);
        v.extend(dn);
        println!(
            "{}",
            v.iter()
                .map(|v| format!("{v:.17e}"))
                .collect::<Vec<_>>()
                .join(" ")
        );
    }
    Ok(())
}
