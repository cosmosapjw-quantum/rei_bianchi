use rei_microphysics::axbi_driver::{compiled_identity, run, Driver, DriverConfig, DriverState};
fn component(split: bool) -> (Driver, DriverState) {
    let mut c = DriverConfig::baseline();
    c.end_zbar = 19.8;
    c.background_panels = 64;
    c.transport_cells = 32;
    c.inactive_hi_split = split;
    Driver::new(c).unwrap()
}
fn seed(d: &Driver, s: &mut DriverState, q: f64, n: f64) {
    for k in 0..d.source.angular_cells.len() {
        d.seed_delta(s, k, q, n * d.source.angular_cells[k].count_fraction)
            .unwrap();
    }
    s.ledgers.source_n += n;
    s.ledgers.source_u += n * q;
}
#[test]
fn explicit_variant_defaults_false_and_rejects_nonflrw_activation() {
    assert!(!DriverConfig::baseline().inactive_hi_split);
    assert!(!DriverConfig::read("").unwrap().inactive_hi_split);
    assert!(
        DriverConfig::read("inactive_hi_split=true\nq_ref=0\n")
            .unwrap()
            .inactive_hi_split
    );
    for q in [-0.01, 0.005] {
        assert!(DriverConfig::read(&format!("inactive_hi_split=true\nq_ref={q}\n")).is_err());
    }
    assert!(DriverConfig::read("inactive_hi_split=invalid\n").is_err());
}
#[test]
fn below_hi_pool_redshifts_without_reactivation_or_boundary_loss() {
    let (d, mut s) = component(true);
    seed(&d, &mut s, 13.6, 0.01);
    let a0 = s.a;
    d.geometry_map(&mut s, a0 * 1.001).unwrap();
    let pools = d.photon_pool_inventory(&s).unwrap();
    assert_eq!(pools[0], 0.0);
    assert!((pools[2] - 0.01).abs() < 1e-16);
    let passive_n = s.photon_inactive_number.clone();
    let passive_u = s.photon_inactive_energy_ref.clone();
    let mut rhs = 0;
    d.chemical_stage(&mut s, 1e5, &mut rhs).unwrap();
    assert_eq!(s.ledgers.photo_events, [0.0; 3]);
    d.geometry_map(&mut s, a0 * 1.005).unwrap();
    assert_eq!(s.photon_inactive_number, passive_n);
    assert_eq!(s.photon_inactive_energy_ref, passive_u);
    let (n, u) = d.photon_inventory(&s);
    assert!((n - 0.01).abs() < 1e-16);
    assert!((u - 0.136 * a0 / s.a).abs() < 1e-15);
    assert!((s.ledgers.photon_work - (0.136 - u)).abs() < 1e-15);
    assert_eq!((s.ledgers.boundary_n, s.ledgers.boundary_u), (0.0, 0.0));
    d.validate(&s, 1e-8).unwrap();
    let before = format!("{s:?}");
    assert!(d.geometry_map(&mut s, a0 * 1.004).is_err());
    assert_eq!(format!("{s:?}"), before);
}
#[test]
fn coupled_stage_only_absorbs_active_pool_and_keeps_total_ledger() {
    let (d, mut s) = component(true);
    seed(&d, &mut s, 13.6, 1e-5);
    seed(&d, &mut s, 30.0, 1e-8);
    let to = s.a * 1.001;
    d.geometry_map(&mut s, to).unwrap();
    let before = d.photon_inventory(&s).0;
    let pn = s.photon_inactive_number.clone();
    let pu = s.photon_inactive_energy_ref.clone();
    let mut rhs = 0;
    d.chemical_stage(&mut s, 1e6, &mut rhs).unwrap();
    let after = d.photon_inventory(&s).0;
    assert!(s.ledgers.absorbed_n > 0.0);
    assert!((before - after - s.ledgers.absorbed_n).abs() < 1e-20);
    assert_eq!(s.photon_inactive_number, pn);
    assert_eq!(s.photon_inactive_energy_ref, pu);
    assert!((s.ledgers.absorbed_n - s.ledgers.photo_events.iter().sum::<f64>()).abs() < 1e-20);
    d.validate(&s, 1e-8).unwrap();
}
#[test]
fn split_pool_norm_detects_equal_total_moment_cancellation() {
    // Algebraic negative control at the common cutoff: these different labels
    // have identical total cell moments; production delta equality stays active.
    let (d, mut half) = component(true);
    d.seed_delta(&mut half, 0, 13.6, 0.5).unwrap();
    let j = half.photons.iter().position(|&n| n > 0.0).unwrap();
    half.photon_inactive_number[j] = 0.5;
    half.photon_inactive_energy_ref[j] = 6.8;
    let mut full = half.clone();
    full.photons[j] = 0.75;
    full.photon_energy_ref[j] = 10.2;
    full.photon_inactive_number[j] = 0.25;
    full.photon_inactive_energy_ref[j] = 3.4;
    let a = d.photon_inventory(&full);
    let b = d.photon_inventory(&half);
    assert!((a.0 - b.0).abs() < 1e-15 && (a.1 - b.1).abs() < 1e-14);
    assert!((d.error_metric(&full, &half).unwrap() - 0.5).abs() < 1e-14);
}
#[test]
fn v4_six_arrays_and_outer_variant_identity_binding() {
    for mode in [false, true] {
        let (d, mut s) = component(mode);
        seed(&d, &mut s, 13.6, 1e-6);
        let to = s.a * 1.001;
        d.geometry_map(&mut s, to).unwrap();
        let path =
            std::env::temp_dir().join(format!("inactive_v4_{}_{}.txt", std::process::id(), mode));
        d.save_checkpoint(&path, &s).unwrap();
        let text = std::fs::read_to_string(&path).unwrap();
        assert!(text.starts_with("AXBI_CHECKPOINT_V4\n"));
        assert_eq!(text.lines().count(), 11);
        let loaded = d.read_checkpoint(&path).unwrap();
        assert_eq!(loaded.photons, s.photons);
        assert_eq!(loaded.photon_energy_ref, s.photon_energy_ref);
        assert_eq!(loaded.photon_support_lo, s.photon_support_lo);
        assert_eq!(loaded.photon_support_hi, s.photon_support_hi);
        assert_eq!(loaded.photon_inactive_number, s.photon_inactive_number);
        assert_eq!(
            loaded.photon_inactive_energy_ref,
            s.photon_inactive_energy_ref
        );
        std::fs::write(&path, text.replacen("V4", "V3", 1)).unwrap();
        assert!(d.read_checkpoint(&path).is_err());
        std::fs::remove_file(path).unwrap();
    }
    let base = "end_zbar=19.8\nbackground_panels=64\ntransport_cells=32\ninactive_hi_split=false\n";
    let (d, s) = Driver::new(DriverConfig::read(base).unwrap()).unwrap();
    let out = std::env::temp_dir().join(format!("inactive_binding_{}", std::process::id()));
    assert!(!out.exists());
    std::fs::create_dir(&out).unwrap();
    std::fs::write(out.join("config.cfg"), base).unwrap();
    std::fs::write(out.join("source_identity.txt"), compiled_identity()).unwrap();
    std::fs::write(out.join("case_id.txt"), "INACTIVE_BINDING").unwrap();
    d.save_checkpoint(&out.join("checkpoint.txt"), &s).unwrap();
    let err = run(
        &base.replace("inactive_hi_split=false", "inactive_hi_split=true"),
        &out,
        "INACTIVE_BINDING",
        true,
    )
    .unwrap_err();
    assert!(format!("{err:?}").contains("AXBI_RESUME_IDENTITY"));
    assert!(!out.join("history.csv").exists());
    std::fs::remove_dir_all(out).unwrap();
}
#[test]
fn total_spectrum_envelope_and_pool_ledgers_preserve_output_schema() {
    let (d, mut s) = component(true);
    seed(&d, &mut s, 13.6, 1e-5);
    seed(&d, &mut s, 20.0, 2e-5);
    let to = s.a * 1.001;
    d.geometry_map(&mut s, to).unwrap();
    let (mut h, mut a, mut p, mut l, mut fb) =
        (Vec::new(), Vec::new(), Vec::new(), Vec::new(), Vec::new());
    d.output_row(&s, "INACTIVE", &mut h, &mut a, &mut p, &mut l, &mut fb)
        .unwrap();
    assert_eq!(String::from_utf8(h).unwrap().trim().split(',').count(), 25);
    let mut nsum = 0.0;
    let mut usum = 0.0;
    for row in String::from_utf8(p).unwrap().lines() {
        let v: Vec<_> = row.split(',').collect();
        assert_eq!(v.len(), 12);
        let n: f64 = v[10].parse().unwrap();
        let u: f64 = v[11].parse().unwrap();
        if n > 0.0 {
            let lo: f64 = v[6].parse().unwrap();
            let hi: f64 = v[7].parse().unwrap();
            assert!(u / n >= lo - 1e-13 && u / n <= hi + 1e-13);
        }
        nsum += n;
        usum += u;
    }
    let total = d.photon_inventory(&s);
    assert!((nsum - total.0).abs() < 1e-18);
    assert!((usum - total.1).abs() < 1e-16);
    assert!((d.moments(&s).unwrap()[0] - total.1).abs() < 1e-16);
    let text = String::from_utf8(l).unwrap();
    for name in [
        "active_photon_N_per_H",
        "active_photon_U_eV_per_H",
        "inactive_photon_N_per_H",
        "inactive_photon_U_eV_per_H",
    ] {
        assert_eq!(
            text.lines()
                .filter(|x| x.split(',').nth(2) == Some(name) && x.ends_with("VALUE"))
                .count(),
            1
        );
    }
}
#[test]
fn false_mode_keeps_retained_inert_baseline_and_rejects_nonzero_passive_state() {
    let (d, mut s) = component(false);
    seed(&d, &mut s, 13.6, 1e-5);
    let to = s.a * 1.001;
    d.geometry_map(&mut s, to).unwrap();
    let pools = d.photon_pool_inventory(&s).unwrap();
    assert!((pools[0] - 1e-5).abs() < 1e-18);
    assert_eq!(pools[2], 0.0);
    assert_eq!(pools[3], 0.0);
    s.photon_inactive_number[0] = 1e-5;
    s.photon_inactive_energy_ref[0] = 13.6e-5;
    assert!(d.validate(&s, 1e-8).is_err());
}
