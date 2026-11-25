use rei_microphysics::axbi_covariant_driver::{Driver, DriverConfig};
#[test]
fn three_bands_and_v6_roundtrip() {
    let c=DriverConfig::read("heii_split=true\nhei_split=true\ncontinuous_birth=true\nnonmonotone_search=true\ninactive_hi_split=true\nflrw_two_ordinate=true\ntransport_cells=64\nbackground_panels=64\nend_zbar=19.8").unwrap();
    let (d, mut s) = Driver::new(c.clone()).unwrap();
    for (e, n) in [
        (20., 1e-6),
        (24.59, 1e-6),
        (40., 1e-6),
        (54.42, 1e-6),
        (80., 1e-7),
    ] {
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
    assert!((s.photons.iter().sum::<f64>() - 1e-6).abs() < 1e-18);
    assert!((s.hei_middle.as_ref().unwrap().number.iter().sum::<f64>() - 2e-6).abs() < 1e-18);
    assert!((s.heii_above.as_ref().unwrap().number.iter().sum::<f64>() - 1.1e-6).abs() < 1e-18);
    d.validate(&s, 1e-8).unwrap();
    let p = d.probe_step(&s, 1e-5).unwrap();
    let mut u = p.half;
    assert!(u.ledgers.absorbed_n > 0. && u.ledgers.source_n > s.ledgers.source_n);
    d.validate(&u, 1e-8).unwrap();
    let f = std::env::temp_dir().join(format!("c2r_v6_{}.txt", std::process::id()));
    d.save_checkpoint(&f, &u).unwrap();
    let mut v = d.read_checkpoint(&f).unwrap();
    assert!(std::fs::read_to_string(&f)
        .unwrap()
        .starts_with("AXBI_CHECKPOINT_V6\n"));
    assert_eq!(u.hei_middle, v.hei_middle);
    assert_eq!(u.heii_above, v.heii_above);
    assert_eq!(u.photons, v.photons);
    let a = d.adaptive_step(&mut u);
    let b = d.adaptive_step(&mut v);
    assert_eq!(a.is_ok(), b.is_ok());
    assert_eq!(u.a, v.a);
    assert_eq!(u.hei_middle, v.hei_middle);
    assert_eq!(u.gas.fractions, v.gas.fractions);
    let mut c0 = c;
    c0.hei_split = false;
    let (d0, _) = Driver::new(c0).unwrap();
    assert!(d0.read_checkpoint(&f).is_err());
    std::fs::remove_file(f).unwrap();
}
#[test]
fn rejects_incomplete_mode() {
    assert!(DriverConfig::read("hei_split=true").is_err());
}
#[test]
fn three_edges_transfer_and_birth_conserve() {
    let c=DriverConfig::read("heii_split=true\nhei_split=true\ncontinuous_birth=true\nnonmonotone_search=true\ninactive_hi_split=true\nflrw_two_ordinate=true\ntransport_cells=64\nbackground_panels=64").unwrap();
    let (d, mut s) = Driver::new(c).unwrap();
    for (e, n) in [(20., 1e-6), (30., 2e-6), (55., 3e-6)] {
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
    d.geometry_map(&mut s, 2. / 21.).unwrap();
    assert!((s.photon_inactive_number.iter().sum::<f64>() - 1e-6).abs() < 1e-18);
    assert!((s.photons.iter().sum::<f64>() - 2e-6).abs() < 1e-18);
    assert!((s.hei_middle.as_ref().unwrap().number.iter().sum::<f64>() - 3e-6).abs() < 1e-18);
    assert_eq!(
        s.heii_above.as_ref().unwrap().number.iter().sum::<f64>(),
        0.
    );
    d.validate(&s, 1e-8).unwrap();
    let g = d
        .background
        .point_at_scale(s.a)
        .unwrap()
        .geometry()
        .unwrap();
    let (bands, ledger) = d.transport.inject_bands(&g, 1. / s.a - 1., 1e13).unwrap();
    let mut p = d.transport.empty_state();
    let ordinary = d.transport.inject(&mut p, &g, 1. / s.a - 1., 1e13).unwrap();
    let nh = d.n_h0_cm3 / s.a.powi(3);
    assert!((ledger.added_photons_per_h / ordinary.added_photons_per_h - 1.).abs() < 1e-13);
    assert!((ledger.added_energy_ev_per_h / ordinary.added_energy_ev_per_h - 1.).abs() < 1e-13);
    let lo = d
        .transport
        .prepare(&bands.low, &g)
        .unwrap()
        .evaluate([0.; 3], nh, 0.)
        .unwrap();
    let mid = d
        .transport
        .prepare(&bands.middle, &g)
        .unwrap()
        .evaluate([0.; 3], nh, 0.)
        .unwrap();
    assert_eq!(lo.photo.gamma_s[1], 0.);
    assert_eq!(lo.photo.gamma_s[2], 0.);
    assert_eq!(mid.photo.gamma_s[2], 0.);
}
