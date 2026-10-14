use rei_microphysics::axbi_driver::*;
use rei_microphysics::igm_state::w_erg_per_h_to_ev;
fn component() -> (Driver, DriverState) {
    let mut c = DriverConfig::baseline();
    c.end_zbar = 19.8;
    c.background_panels = 64;
    Driver::new(c).unwrap()
}
#[test]
fn reaction_free_geometry_conserves_count_energy_and_temperature_dilution() {
    let (d, mut s) = component();
    let initial = s.a;
    let old_w = s.gas.w_erg_per_h;
    let offset = d.energies.len() * 3;
    s.photons[offset + 5] = 0.5;
    s.photons[offset + d.energies.len() + 5] = 0.5;
    s.ledgers.source_n = 1.0;
    s.ledgers.source_u = d.energies[5];
    let to = 1.0 / 20.9;
    d.geometry_map(&mut s, to).unwrap();
    assert!((s.gas.w_erg_per_h / old_w - (initial / to).powi(2)).abs() < 1e-14);
    assert_eq!(s.gas.fractions, [2e-4, 0.0, 0.0]);
    let (n, u) = d.residuals(&s).unwrap();
    assert!(n.abs() < 1e-12);
    assert!(u.abs() < 1e-12);
    let m = d.moments(&s).unwrap();
    assert!(m[1].abs() < 1e-12);
}
#[test]
fn conservative_deposit_exact_number_and_energy() {
    let (d, s) = component();
    let mut stocks = s.photons.clone();
    let e = 20.0;
    d.deposit(&mut stocks, 0, e, 2.0).unwrap();
    let mut v = s;
    v.photons = stocks;
    let (n, u) = d.photon_inventory(&v);
    assert!((n - 2.0).abs() < 1e-14);
    assert!((u - 40.0).abs() < 1e-12);
    assert_eq!(
        d.deposit(&mut v.photons, 0, 10.0, 3.0).unwrap(),
        (3.0, 30.0)
    );
    assert!(d.deposit(&mut v.photons, 0, 101.0, 1.0).is_err());
}
#[test]
fn cold_absorption_uses_one_event_owner() {
    let (d, mut s) = component();
    let eindex = 10;
    let e = d.energies[eindex];
    for k in 0..d.source.angular_cells.len() {
        s.photons[k * d.energies.len() + eindex] = 0.01 * d.source.angular_cells[k].count_fraction;
    }
    s.ledgers.source_n = 0.01;
    s.ledgers.source_u = 0.01 * e;
    let before = s.gas.fractions[0];
    let mut counter = 0;
    d.chemical_stage(&mut s, 1e7, &mut counter).unwrap();
    let (n, _) = d.photon_inventory(&s);
    assert!((0.01 - n - s.ledgers.absorbed_n).abs() < 1e-12);
    assert!((s.ledgers.absorbed_n - s.ledgers.photo_events.iter().sum::<f64>()).abs() < 1e-12);
    assert!(s.gas.fractions[0] > before);
    d.validate(&s, 1e-8).unwrap();
}
#[test]
fn checkpoint_roundtrip_and_registry_normalization() {
    let (d, mut s) = component();
    s.attempts = 3;
    s.rejects = 1;
    s.rhs_evaluations = 7;
    let path = std::env::temp_dir().join(format!(
        "axbi_component_checkpoint_{}.txt",
        std::process::id()
    ));
    d.save_checkpoint(&path, &s).unwrap();
    let loaded = d.read_checkpoint(&path).unwrap();
    assert_eq!(loaded.gas.fractions, s.gas.fractions);
    assert_eq!(loaded.gas.w_erg_per_h, s.gas.w_erg_per_h);
    assert_eq!(loaded.photons, s.photons);
    assert_eq!(loaded.rhs_evaluations, 7);
    std::fs::remove_file(path).unwrap();
    let (mut h, mut a, mut p, mut l, mut f) =
        (Vec::new(), Vec::new(), Vec::new(), Vec::new(), Vec::new());
    d.output_row(&s, "TEST", &mut h, &mut a, &mut p, &mut l, &mut f)
        .unwrap();
    assert_eq!(String::from_utf8(h).unwrap().trim().split(',').count(), 25);
    let text = String::from_utf8(a).unwrap();
    let mut masssum = 0.0;
    for line in text.lines() {
        let row = line.split(',').collect::<Vec<_>>();
        let mass: f64 = row[6].parse().unwrap();
        let y: f64 = row[11].trim().parse().unwrap();
        masssum += mass * y;
    }
    assert!((masssum - 1.0).abs() < 1e-12);
    assert!(text.contains("H_I"));
    assert!(text.contains("He_I"));
    assert!(text.contains("electron"));
    assert!(w_erg_per_h_to_ev(s.gas.w_erg_per_h).unwrap() > 0.0);
}
#[test]
fn component_step_doubling_and_state_array_metric() {
    let (d, mut s) = component();
    let mut done = false;
    for _ in 0..20 {
        if d.adaptive_step(&mut s).unwrap() {
            done = true;
            break;
        }
    }
    assert!(
        done,
        "bounded component step must resolve its numerical local-error target"
    );
    assert_eq!(s.accepted, 1);
    assert!(s.last_error < 1e-5);
    d.validate(&s, 1e-8).unwrap();
    let mut other = s.clone();
    other.photons[0] += 1e-6;
    other.photons[1] -= 1e-6;
    assert!(d.error_metric(&other, &s).unwrap() > 0.0);
}

#[test]
fn hard_caps_charge_started_trials_and_resume_without_off_by_one() {
    let mut config = DriverConfig::baseline();
    config.end_zbar = 19.8;
    config.background_panels = 64;
    config.max_attempts = 1;
    let (d, mut s) = Driver::new(config).unwrap();
    assert!(d.adaptive_step(&mut s).is_err());
    assert_eq!(s.attempts, 1);
    assert_eq!(s.comparisons, 1);
    assert_eq!(s.rejects, 1);
    let rhs_before = s.rhs_evaluations;
    assert!(d.adaptive_step(&mut s).is_err());
    assert_eq!(s.attempts, 1);
    assert_eq!(s.rhs_evaluations, rhs_before);
    let path = std::env::temp_dir().join(format!("axbi_cap_checkpoint_{}.txt", std::process::id()));
    d.save_checkpoint(&path, &s).unwrap();
    let loaded = d.read_checkpoint(&path).unwrap();
    assert_eq!(loaded.attempts, 1);
    assert_eq!(loaded.comparisons, 1);
    assert_eq!(loaded.rejects, 1);
    std::fs::remove_file(path).unwrap();
    let (mut d, mut s) = component();
    d.config.max_rhs = 1;
    let mut count = 1;
    assert!(d.chemical_stage(&mut s, 1e7, &mut count).is_err());
    assert_eq!(count, 1);
    count = 0;
    assert!(d.chemical_stage(&mut s, 1e7, &mut count).is_err());
    assert_eq!(count, 1);
}
#[test]
fn geometry_map_rejects_cold_endpoint_outside_provider_domain() {
    let (d, mut s) = component();
    s.gas = rei_microphysics::igm_state::IgmGasState::from_temperature(
        s.gas.fractions,
        d.n_h0_cm3 / s.a.powi(3),
        d.n_he0_cm3 / s.a.powi(3),
        1.0001,
    )
    .unwrap();
    assert!(d.geometry_map(&mut s, 1.0 / 20.8).is_err());
}

#[test]
fn aggregate_output_guard_counts_nested_bytes_and_atomic_checkpoint_peak() {
    let root = std::env::temp_dir().join(format!("axbi_output_guard_{}", std::process::id()));
    std::fs::create_dir(&root).unwrap();
    std::fs::create_dir(root.join("raw")).unwrap();
    let file = std::fs::File::create(root.join("raw/sparse_bytes")).unwrap();
    file.set_len(SCIENCE_OUTPUT_BUDGET_BYTES - 100).unwrap();
    assert!(guard_output_bytes(&root, 100).is_ok());
    assert!(guard_output_bytes(&root, 101).is_err());
    let (d, s) = component();
    let path = root.join("checkpoint.txt");
    assert!(d.save_checkpoint_budget(&root, &path, &s).is_err());
    assert!(!path.exists());
    assert!(!path.with_extension("tmp").exists());
    drop(file);
    std::fs::remove_file(root.join("raw/sparse_bytes")).unwrap();
    d.save_checkpoint_budget(&root, &path, &s).unwrap();
    assert_eq!(d.read_checkpoint(&path).unwrap().photons, s.photons);
    std::fs::remove_file(path).unwrap();
    std::fs::remove_dir(root.join("raw")).unwrap();
    std::fs::remove_dir(root).unwrap();
}
