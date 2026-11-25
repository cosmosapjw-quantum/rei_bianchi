use rei_microphysics::axbi_covariant_driver::{Driver, DriverConfig};
#[test]
fn split_checkpoint_and_gas_coupling() {
    let c=DriverConfig::read("heii_split=true\ncontinuous_birth=true\nnonmonotone_search=true\ninactive_hi_split=true\nflrw_two_ordinate=true\ntransport_cells=64\nbackground_panels=64\nend_zbar=19.8").unwrap();
    let (d, s) = Driver::new(c.clone()).unwrap();
    let p = d.probe_step(&s, 1e-5).unwrap();
    let u = p.half;
    assert!(u.ledgers.source_n > 0. && u.ledgers.absorbed_n > 0.);
    assert!(u.heii_above.as_ref().unwrap().number.iter().sum::<f64>() > 0.);
    assert!(u.gas.fractions != s.gas.fractions);
    d.validate(&u, 1e-8).unwrap();
    let file = std::env::temp_dir().join(format!("c2q_split_{}.txt", std::process::id()));
    d.save_checkpoint(&file, &u).unwrap();
    let t = d.read_checkpoint(&file).unwrap();
    assert_eq!(u.heii_above, t.heii_above);
    assert_eq!(u.photons, t.photons);
    assert!(std::fs::read_to_string(&file)
        .unwrap()
        .starts_with("AXBI_CHECKPOINT_V5\n"));
    let mut c0 = c;
    c0.heii_split = false;
    let (d0, _) = Driver::new(c0).unwrap();
    assert!(d0.read_checkpoint(&file).is_err());
    std::fs::remove_file(file).unwrap();
}
#[test]
fn invalid_split_mode_rejected() {
    assert!(DriverConfig::read("heii_split=true").is_err());
}
#[test]
fn split_v5_restart_keeps_two_distinct_active_pools() {
    let c=DriverConfig::read("heii_split=true\ncontinuous_birth=true\nnonmonotone_search=true\ninactive_hi_split=true\nflrw_two_ordinate=true\ntransport_cells=64\nbackground_panels=64\nend_zbar=19.8").unwrap();
    let (d, mut s) = Driver::new(c.clone()).unwrap();
    for (e, n) in [(40., 1e-6), (54.42, 1e-6), (80., 1e-7)] {
        for ray in 0..d.source.angular_cells.len() {
            d.seed_delta(
                &mut s,
                ray,
                e,
                n * d.source.angular_cells[ray].count_fraction,
            )
            .unwrap();
        }
        s.ledgers.source_n += n;
        s.ledgers.source_u += e * n;
    }
    assert!(s.heii_above.as_ref().unwrap().number.iter().sum::<f64>() > 0.);
    d.validate(&s, 1e-8).unwrap();
    let mut ok = false;
    for _ in 0..30 {
        if d.adaptive_step(&mut s).unwrap_or(false) {
            ok = true;
            break;
        }
    }
    assert!(ok && s.accepted == 1);
    let p = std::env::temp_dir().join(format!("c2q_split_restart_{}.txt", std::process::id()));
    d.save_checkpoint(&p, &s).unwrap();
    let mut t = d.read_checkpoint(&p).unwrap();
    assert_eq!(s.heii_above, t.heii_above);
    assert_eq!(s.photons, t.photons);
    let a = d.adaptive_step(&mut s);
    let b = d.adaptive_step(&mut t);
    assert_eq!(a.is_ok(), b.is_ok());
    assert_eq!(s.a, t.a);
    assert_eq!(s.accepted, t.accepted);
    assert_eq!(s.gas.fractions, t.gas.fractions);
    assert_eq!(s.photons, t.photons);
    assert_eq!(s.heii_above, t.heii_above);
    assert_eq!(d.residuals(&s).unwrap(), d.residuals(&t).unwrap());
    std::fs::remove_file(p).unwrap();
    // Legacy V4 cannot silently acquire split state.
    let mut c0 = c;
    c0.heii_split = false;
    let (d0, u) = Driver::new(c0).unwrap();
    let p = std::env::temp_dir().join(format!("c2q_legacy_restart_{}.txt", std::process::id()));
    d0.save_checkpoint(&p, &u).unwrap();
    assert!(d.read_checkpoint(&p).is_err());
    std::fs::remove_file(p).unwrap();
}
