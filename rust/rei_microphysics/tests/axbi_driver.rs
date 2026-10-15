use rei_microphysics::axbi_driver::*;
use rei_microphysics::igm_state::w_erg_per_h_to_ev;
fn component() -> (Driver, DriverState) {
    let mut c = DriverConfig::baseline();
    c.end_zbar = 19.8;
    c.background_panels = 64;
    Driver::new(c).unwrap()
}

#[test]
fn explicit_initial_hydrogen_fraction_is_opt_in_and_validated() {
    assert_eq!(DriverConfig::baseline().initial_x_hii, 2e-4);
    assert_eq!(DriverConfig::read("").unwrap().initial_x_hii, 2e-4);
    for value in ["NaN", "inf", "-0.0001", "1.0001", "invalid"] {
        assert!(DriverConfig::read(&format!("initial_x_hii={value}\n")).is_err());
    }
    for value in [0.0, 1.0] {
        assert_eq!(
            DriverConfig::read(&format!("initial_x_hii={value}\n"))
                .unwrap()
                .initial_x_hii,
            value
        );
    }
    let mut config = DriverConfig::baseline();
    config.initial_x_hii = f64::NAN;
    assert!(Driver::new(config).is_err());
}

#[test]
fn donor_initial_eos_one_step_ledgers_and_checkpoint_roundtrip() {
    let x = 0.000210349192936;
    let temperature = 9.306042400380866;
    let config = DriverConfig::read(&format!(
        "end_zbar=19.8\nbackground_panels=64\ninitial_x_hii={x}\ninitial_temperature_k={temperature}\n"
    ))
    .unwrap();
    let (d, mut s) = Driver::new(config).unwrap();
    let (baseline, _) = component();
    assert_eq!(d.n_h0_cm3, baseline.n_h0_cm3);
    assert_eq!(d.n_he0_cm3, baseline.n_he0_cm3);
    assert_eq!(s.gas.fractions, [x, 0.0, 0.0]);
    let nh = d.n_h0_cm3 / s.a.powi(3);
    let eos = s.gas.eos(nh, d.n_he0_cm3 / s.a.powi(3)).unwrap();
    assert!((eos.temperature_k / temperature - 1.0).abs() < 1e-14);
    assert!((eos.electron_density_cm3 / (nh * x) - 1.0).abs() < 1e-14);
    assert!(s.gas.w_erg_per_h.is_finite() && s.gas.w_erg_per_h > 0.0);
    let mut accepted = false;
    for _ in 0..20 {
        if d.adaptive_step(&mut s).unwrap() {
            accepted = true;
            break;
        }
    }
    assert!(
        accepted,
        "bounded donor step must meet the existing local target"
    );
    assert_eq!(s.accepted, 1);
    assert!(s.last_error < d.config.local_target);
    let (n, u) = d.residuals(&s).unwrap();
    assert!(n.is_finite() && u.is_finite());
    d.validate(&s, 1e-8).unwrap();
    let path =
        std::env::temp_dir().join(format!("axbi_donor_checkpoint_{}.txt", std::process::id()));
    d.save_checkpoint(&path, &s).unwrap();
    let restored = d.read_checkpoint(&path).unwrap();
    assert_eq!(restored.a, s.a);
    assert_eq!(restored.gas.fractions, s.gas.fractions);
    assert_eq!(restored.gas.w_erg_per_h, s.gas.w_erg_per_h);
    assert_eq!(restored.photons, s.photons);
    assert_eq!(restored.accepted, s.accepted);
    assert_eq!(restored.rhs_evaluations, s.rhs_evaluations);
    std::fs::remove_file(path).unwrap();
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

#[test]
fn sparse_full_spectra_keep_each_abundance_and_align_terminal_resume_and_cap() {
    use std::io::{BufWriter, Write};
    let root = std::env::temp_dir().join(format!("axbi_sparse_output_{}", std::process::id()));
    std::fs::create_dir(&root).unwrap();
    let (d, mut s) = component();
    let mut h = BufWriter::new(std::fs::File::create(root.join("history.csv")).unwrap());
    let mut a = BufWriter::new(std::fs::File::create(root.join("abundances.csv")).unwrap());
    let mut p = BufWriter::new(std::fs::File::create(root.join("spectra.csv")).unwrap());
    let mut l = BufWriter::new(std::fs::File::create(root.join("ledgers.csv")).unwrap());
    let mut f = BufWriter::new(std::fs::File::create(root.join("feedback.csv")).unwrap());
    writeln!(p,"case_id,q_ref,Sigma,time_s,a,zbar,energy_low_eV,energy_high_eV,mu_center,solid_angle_weight_sr,photon_n_per_H,photon_u_eV_per_H").unwrap();
    let mut last = None;
    for i in 0..=61 {
        if i > 0 {
            let next = s.a * (1e-6_f64).exp();
            d.geometry_map(&mut s, next).unwrap();
        }
        s.accepted = i;
        let seconds = if i == 17 { 30.0 } else { 0.0 };
        let snapshot = d.spectrum_due(i, seconds, i == 61);
        assert_eq!(snapshot, [0, 17, 60, 61].contains(&i));
        d.output_batch(
            &s, "TEST", &root, snapshot, &mut h, &mut a, &mut p, &mut l, &mut f,
        )
        .unwrap();
        if snapshot {
            last = Some(d.background.point_at_scale(s.a).unwrap().time_s);
        }
    }
    for w in [&mut h, &mut a, &mut p, &mut l, &mut f] {
        w.flush().unwrap();
    }
    let full_rows = d.energies.len() * d.source.angular_cells.len();
    assert_eq!(
        std::fs::read_to_string(root.join("spectra.csv"))
            .unwrap()
            .lines()
            .count(),
        1 + 4 * full_rows
    );
    assert_eq!(
        std::fs::read_to_string(root.join("history.csv"))
            .unwrap()
            .lines()
            .count(),
        62
    );
    assert_eq!(
        std::fs::read_to_string(root.join("abundances.csv"))
            .unwrap()
            .lines()
            .count(),
        62 * 6
    );
    assert_eq!(
        std::fs::read_to_string(root.join("feedback.csv"))
            .unwrap()
            .lines()
            .count(),
        62
    );
    assert_eq!(d.saved_spectrum_time(&root).unwrap(), last);
    assert!(!d
        .ensure_spectrum_snapshot(&s, "TEST", &root, &mut last, &mut p)
        .unwrap());
    // Manufacture one accepted state with no scheduled spectrum, then resume
    // that exact checkpoint. Adding its missing snapshot must be idempotent.
    let next = s.a * (1e-6_f64).exp();
    d.geometry_map(&mut s, next).unwrap();
    s.accepted = 62;
    d.output_batch(
        &s, "TEST", &root, false, &mut h, &mut a, &mut p, &mut l, &mut f,
    )
    .unwrap();
    for w in [&mut h, &mut a, &mut p, &mut l, &mut f] {
        w.flush().unwrap();
    }
    d.save_checkpoint_budget(&root, &root.join("checkpoint.txt"), &s)
        .unwrap();
    let resumed = d.read_checkpoint(&root.join("checkpoint.txt")).unwrap();
    last = d.saved_spectrum_time(&root).unwrap();
    assert!(d
        .ensure_spectrum_snapshot(&resumed, "TEST", &root, &mut last, &mut p)
        .unwrap());
    p.flush().unwrap();
    assert!(!d
        .ensure_spectrum_snapshot(&resumed, "TEST", &root, &mut last, &mut p)
        .unwrap());
    assert_eq!(
        d.saved_spectrum_time(&root).unwrap(),
        Some(d.background.point_at_scale(resumed.a).unwrap().time_s)
    );
    assert_eq!(
        std::fs::read_to_string(root.join("spectra.csv"))
            .unwrap()
            .lines()
            .count(),
        1 + 5 * full_rows
    );
    assert_eq!(
        std::fs::read_to_string(root.join("abundances.csv"))
            .unwrap()
            .lines()
            .count(),
        63 * 6
    );
    // A guard failure must happen before either primary rows or spectrum grow.
    let old_h = std::fs::metadata(root.join("history.csv")).unwrap().len();
    let old_p = std::fs::metadata(root.join("spectra.csv")).unwrap().len();
    let bytes = std::fs::read_dir(&root)
        .unwrap()
        .map(|e| e.unwrap().metadata().unwrap().len())
        .sum::<u64>();
    let sparse = std::fs::File::create(root.join("budget_reservation")).unwrap();
    sparse
        .set_len(SCIENCE_OUTPUT_BUDGET_BYTES - bytes - 100)
        .unwrap();
    assert!(d
        .output_batch(&resumed, "TEST", &root, false, &mut h, &mut a, &mut p, &mut l, &mut f)
        .is_err());
    assert_eq!(
        std::fs::metadata(root.join("history.csv")).unwrap().len(),
        old_h
    );
    assert_eq!(
        std::fs::metadata(root.join("spectra.csv")).unwrap().len(),
        old_p
    );
    drop(sparse);
    drop(h);
    drop(a);
    drop(p);
    drop(l);
    drop(f);
    std::fs::remove_dir_all(root).unwrap();
}

#[test]
fn full_resource_allocation_preserves_pilot_default_and_exact_guard() {
    let legacy = DriverConfig::read("end_zbar=19.8\nbackground_panels=64\n").unwrap();
    assert_eq!(legacy.output_budget_mib, 256);
    assert_eq!(
        legacy.scientific_output_budget_bytes().unwrap(),
        224 * 1024 * 1024
    );
    assert_eq!(legacy.launcher_reserve_bytes().unwrap(), 32 * 1024 * 1024);
    let full = DriverConfig::read("end_zbar=19.8\nbackground_panels=64\noutput_budget_mib=2048\n")
        .unwrap();
    assert_eq!(
        full.scientific_output_budget_bytes().unwrap(),
        1920 * 1024 * 1024
    );
    assert_eq!(full.launcher_reserve_bytes().unwrap(), 128 * 1024 * 1024);
    assert_eq!(
        full.scientific_output_budget_bytes().unwrap() + full.launcher_reserve_bytes().unwrap(),
        2048 * 1024 * 1024
    );
    assert!(DriverConfig::read("output_budget_mib=512\n").is_err());
    let (old, oldstate) = Driver::new(legacy).unwrap();
    let (new, newstate) = Driver::new(full.clone()).unwrap();
    assert_eq!(oldstate.gas.fractions, newstate.gas.fractions);
    assert_eq!(oldstate.gas.w_erg_per_h, newstate.gas.w_erg_per_h);
    assert_eq!(old.energies, new.energies);
    assert_eq!(oldstate.photons, newstate.photons);
    assert_eq!(
        old.background.point_at_scale(oldstate.a).unwrap(),
        new.background.point_at_scale(newstate.a).unwrap()
    );
    let root =
        std::env::temp_dir().join(format!("axbi_full_output_resource_{}", std::process::id()));
    std::fs::create_dir(&root).unwrap();
    let file = std::fs::File::create(root.join("sparse_resource_bytes")).unwrap();
    file.set_len(SCIENCE_OUTPUT_BUDGET_BYTES + 1).unwrap();
    assert!(guard_output_bytes(&root, 0).is_err());
    assert!(guard_output_bytes_with_limit(
        &root,
        0,
        full.scientific_output_budget_bytes().unwrap()
    )
    .is_ok());
    assert!(old
        .save_checkpoint_budget(&root, &root.join("checkpoint.txt"), &oldstate)
        .is_err());
    new.save_checkpoint_budget(&root, &root.join("checkpoint.txt"), &newstate)
        .unwrap();
    std::fs::remove_file(root.join("checkpoint.txt")).unwrap();
    let limit = full.scientific_output_budget_bytes().unwrap();
    file.set_len(limit - 100).unwrap();
    assert!(guard_output_bytes_with_limit(&root, 100, limit).is_ok());
    assert!(guard_output_bytes_with_limit(&root, 101, limit).is_err());
    assert!(new
        .save_checkpoint_budget(&root, &root.join("checkpoint.txt"), &newstate)
        .is_err());
    assert!(!root.join("checkpoint.txt").exists());
    assert!(!root.join("checkpoint.tmp").exists());
    drop(file);
    std::fs::remove_file(root.join("sparse_resource_bytes")).unwrap();
    std::fs::remove_dir(root).unwrap();
}

#[test]
fn refinement_output_allocation_4096_preserves_existing_budgets_and_exact_guard() {
    for (total, science, reserve) in [
        (256u64, 224u64, 32u64),
        (2048, 1920, 128),
        (4096, 3968, 128),
    ] {
        let config = DriverConfig::read(&format!("output_budget_mib={total}\n")).unwrap();
        assert_eq!(
            config.scientific_output_budget_bytes().unwrap(),
            science * 1024 * 1024
        );
        assert_eq!(
            config.launcher_reserve_bytes().unwrap(),
            reserve * 1024 * 1024
        );
        assert_eq!(
            config.scientific_output_budget_bytes().unwrap()
                + config.launcher_reserve_bytes().unwrap(),
            total * 1024 * 1024
        );
    }
    assert!(DriverConfig::read("output_budget_mib=4095\n").is_err());
    assert!(DriverConfig::read("output_budget_mib=4097\n").is_err());
    let root = std::env::temp_dir().join(format!(
        "axbi_refinement_output_resource_{}",
        std::process::id()
    ));
    std::fs::create_dir(&root).unwrap();
    let file = std::fs::File::create(root.join("sparse_resource_bytes")).unwrap();
    let config = DriverConfig::read("output_budget_mib=4096\n").unwrap();
    let limit = config.scientific_output_budget_bytes().unwrap();
    file.set_len(limit - 100).unwrap();
    assert!(guard_output_bytes_with_limit(&root, 100, limit).is_ok());
    assert!(guard_output_bytes_with_limit(&root, 101, limit).is_err());
    drop(file);
    std::fs::remove_file(root.join("sparse_resource_bytes")).unwrap();
    std::fs::remove_dir(root).unwrap();
}
