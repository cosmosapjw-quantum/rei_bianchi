use rei_microphysics::axbi_covariant_transport::PhotonState;
use rei_microphysics::axbi_driver::{compiled_identity, Driver, DriverConfig, DriverState};
use rei_microphysics::igm_state::IgmGasState;

fn component() -> (Driver, DriverState) {
    let mut c = DriverConfig::baseline();
    c.end_zbar = 19.8;
    c.background_panels = 64;
    c.transport_cells = 32;
    Driver::new(c).unwrap()
}
fn photons(s: &DriverState) -> PhotonState {
    PhotonState {
        number: s.photons.clone(),
        energy_ref: s.photon_energy_ref.clone(),
        support_lo: s.photon_support_lo.clone(),
        support_hi: s.photon_support_hi.clone(),
    }
}
fn seed(d: &Driver, s: &mut DriverState, energy: f64, number: f64) {
    for k in 0..d.source.angular_cells.len() {
        d.seed_delta(
            s,
            k,
            energy,
            number * d.source.angular_cells[k].count_fraction,
        )
        .unwrap();
    }
    s.ledgers.source_n += number;
    s.ledgers.source_u += energy * number;
}
#[test]
fn reference_moments_do_not_remap_and_work_uses_actual_energy() {
    let (d, mut s) = component();
    seed(&d, &mut s, 54.42, 0.01);
    let initial = photons(&s);
    let a0 = s.a;
    let u0 = d.photon_inventory(&s).1;
    for j in 1..=100 {
        d.geometry_map(&mut s, a0 * (1.0 + 0.005 * j as f64 / 100.0))
            .unwrap();
    }
    assert_eq!(photons(&s), initial);
    let (n, u) = d.photon_inventory(&s);
    assert!((n - 0.01).abs() < 1e-16);
    assert!((u / u0 - a0 / s.a).abs() < 2e-15);
    assert!((s.ledgers.photon_work - (u0 - u)).abs() < 2e-15);
    d.validate(&s, 1e-8).unwrap();
}
#[test]
fn repeated_transport_cannot_create_heii_photo_events_below_threshold() {
    let (d, mut s) = component();
    let nh = d.n_h0_cm3 / s.a.powi(3);
    s.gas = IgmGasState::from_temperature([2e-4, 0.01, 0.0], nh, d.n_he0_cm3 / s.a.powi(3), 8.1)
        .unwrap();
    seed(&d, &mut s, 54.42, 1e-8);
    let a0 = s.a;
    for j in 1..=128 {
        d.geometry_map(&mut s, a0 * (1.0 + 0.005 * j as f64 / 128.0))
            .unwrap();
    }
    let g = d
        .background
        .point_at_scale(s.a)
        .unwrap()
        .geometry()
        .unwrap();
    let prepared = d.transport.prepare(&photons(&s), &g).unwrap();
    let pure = d
        .transport
        .evaluate(&prepared, [0.0, 0.0, nh * 0.01], nh, 1e7)
        .unwrap();
    assert_eq!(pure.absorbed_per_h[2], 0.0);
    assert_eq!(pure.photo.gamma_s[2], 0.0);
    let mut counter = 0;
    d.chemical_stage(&mut s, 1e3, &mut counter).unwrap();
    assert_eq!(s.ledgers.photo_events[2], 0.0);
    assert!(counter > 0);
}
#[test]
fn number_only_mutation_is_rejected_instead_of_inventing_spectrum() {
    let (d, mut s) = component();
    s.photons[0] = 1.0;
    assert!(d.validate(&s, 1e-8).is_err());
    let a = s.a * 1.001;
    assert!(d.geometry_map(&mut s, a).is_err());
    assert!(d.photon_inventory(&s).0.is_nan());
}
#[test]
fn checkpoint_v3_roundtrips_all_arrays_and_rejects_projected_v2() {
    let (d, mut s) = component();
    seed(&d, &mut s, 30.0, 1e-6);
    d.geometry_map(&mut s, 1.0 / 20.99).unwrap();
    let file = std::env::temp_dir().join(format!(
        "covariant_driver_checkpoint_{}.txt",
        std::process::id()
    ));
    d.save_checkpoint(&file, &s).unwrap();
    let text = std::fs::read_to_string(&file).unwrap();
    assert!(text.starts_with("AXBI_CHECKPOINT_V3\n"));
    let loaded = d.read_checkpoint(&file).unwrap();
    assert_eq!(photons(&loaded), photons(&s));
    assert_eq!(loaded.a, s.a);
    let legacy = text.replacen("AXBI_CHECKPOINT_V3", "AXBI_CHECKPOINT_V2", 1);
    std::fs::write(&file, legacy).unwrap();
    assert!(d.read_checkpoint(&file).is_err());
    std::fs::remove_file(file).unwrap();
    assert!(compiled_identity().contains("Fixed reference-energy photon moments"));
}
#[test]
fn output_support_and_moments_use_local_energy() {
    let (d, mut s) = component();
    seed(&d, &mut s, 30.0, 1e-5);
    let a0 = s.a;
    d.geometry_map(&mut s, a0 * 1.005).unwrap();
    let (mut h, mut a, mut p, mut l, mut f) =
        (Vec::new(), Vec::new(), Vec::new(), Vec::new(), Vec::new());
    d.output_row(&s, "COVARIANT", &mut h, &mut a, &mut p, &mut l, &mut f)
        .unwrap();
    let mut total = 0.0;
    let expected = 30.0 * a0 / s.a;
    for row in String::from_utf8(p).unwrap().lines() {
        let cols: Vec<_> = row.split(',').collect();
        let n: f64 = cols[10].parse().unwrap();
        if n > 0.0 {
            let lo: f64 = cols[6].parse().unwrap();
            let hi: f64 = cols[7].parse().unwrap();
            let u: f64 = cols[11].parse().unwrap();
            assert!((lo - expected).abs() < 1e-12 && (hi - expected).abs() < 1e-12);
            assert!((u / n - expected).abs() < 1e-12);
            total += u;
        }
    }
    assert!((total - d.moments(&s).unwrap()[0]).abs() < 1e-18);
}
#[test]
fn transport_resolution_is_separate_and_be_stage_has_one_event_owner() {
    assert_eq!(DriverConfig::baseline().transport_cells, 128);
    assert_eq!(
        DriverConfig::read("transport_cells=64\n")
            .unwrap()
            .energy_subdivisions,
        16
    );
    for x in ["0", "1025", "NaN"] {
        assert!(DriverConfig::read(&format!("transport_cells={x}\n")).is_err());
    }
    let (d, mut s) = component();
    seed(&d, &mut s, 30.0, 1e-8);
    let old = d.photon_inventory(&s);
    let mut counter = 0;
    d.chemical_stage(&mut s, 1e6, &mut counter).unwrap();
    let new = d.photon_inventory(&s);
    assert!((old.0 - new.0 - s.ledgers.absorbed_n).abs() < 1e-20);
    assert!((s.ledgers.absorbed_n - s.ledgers.photo_events.iter().sum::<f64>()).abs() < 1e-20);
    d.validate(&s, 1e-8).unwrap();
}

#[test]
fn actual_run_resume_rejects_changed_config_and_source_before_stepping() {
    use rei_microphysics::axbi_driver::run;
    let config="end_zbar=19.8\nbackground_panels=64\ntransport_cells=32\nq_ref=0.0\n";
    let (driver,state)=Driver::new(DriverConfig::read(config).unwrap()).unwrap();
    let out=std::env::temp_dir().join(format!("covariant_resume_binding_{}",std::process::id()));
    assert!(!out.exists());
    std::fs::create_dir(&out).unwrap();
    std::fs::write(out.join("config.cfg"),config).unwrap();
    std::fs::write(out.join("source_identity.txt"),compiled_identity()).unwrap();
    std::fs::write(out.join("case_id.txt"),"RESUME_BINDING").unwrap();
    driver.save_checkpoint(&out.join("checkpoint.txt"),&state).unwrap();
    let original=std::fs::read(out.join("checkpoint.txt")).unwrap();
    for changed in [config.replace("transport_cells=32","transport_cells=64"),config.replace("q_ref=0.0","q_ref=0.005")] {
        let err=run(&changed,&out,"RESUME_BINDING",true).unwrap_err();
        assert!(format!("{err:?}").contains("AXBI_RESUME_IDENTITY"));
        assert_eq!(std::fs::read(out.join("checkpoint.txt")).unwrap(),original);
        assert!(!out.join("history.csv").exists());
        assert!(!out.join("raw/rejections.csv").exists());
    }
    std::fs::write(out.join("source_identity.txt"),"changed source bytes").unwrap();
    let err=run(config,&out,"RESUME_BINDING",true).unwrap_err();
    assert!(format!("{err:?}").contains("AXBI_RESUME_IDENTITY"));
    assert_eq!(std::fs::read(out.join("checkpoint.txt")).unwrap(),original);
    assert!(!out.join("history.csv").exists());
    std::fs::remove_dir_all(out).unwrap();
}
