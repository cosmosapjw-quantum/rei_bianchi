use rei_microphysics::{
    axbi_covariant_driver::{Driver, DriverConfig},
    GeometrySnapshot,
};
#[test]
fn reactivation_and_checkpoint() {
    let c=DriverConfig::read("reactive_hi=true\nhei_split=true\nheii_split=true\ncontinuous_birth=true\nnonmonotone_search=true\nq_ref=-1\ntransport_cells=64\nbackground_panels=64\nend_zbar=19.8").unwrap();
    let (d, mut s) = Driver::new(c.clone()).unwrap();
    let ray = d
        .source
        .angular_cells
        .iter()
        .enumerate()
        .max_by(|a, b| a.1.mu.total_cmp(&b.1.mu))
        .unwrap()
        .0;
    let z = d
        .background
        .point_at_scale(1. / 20.8)
        .unwrap()
        .geometry()
        .unwrap();
    let scale = d.transport.ray_geometry(&z).unwrap()[ray].scale;
    assert!(scale > 1.);
    let e = 13.6 / (1. + (scale - 1.) / 2.);
    // Use symmetric rays to satisfy parity constraint.
    let n = d.source.angular_cells.len();
    for k in [ray, n - 1 - ray] {
        d.seed_delta(&mut s, k, e, 1e-6).unwrap();
    }
    s.ledgers.source_n = 2e-6;
    s.ledgers.source_u = 2e-6 * e;
    assert_eq!(
        s.hi_below.as_ref().unwrap().number.iter().sum::<f64>(),
        2e-6
    );
    assert_eq!(d.endpoint_photo(&s).unwrap().gamma_s[0], 0.);
    d.validate(&s, 1e-8).unwrap();
    d.geometry_map(&mut s, 1. / 20.8).unwrap();
    assert_eq!(s.hi_below.as_ref().unwrap().number.iter().sum::<f64>(), 0.);
    assert!(d.endpoint_photo(&s).unwrap().gamma_s[0] > 0.);
    // Positive optical rate alone is not enough: exercise the actual gas owner
    // after reactivation, with a physical event ledger and no new births.
    let mut trial = s.clone();
    let mut rhs = 0;
    d.chemical_stage(&mut trial, 1e7, &mut rhs).unwrap();
    assert!(trial.ledgers.photo_events[0] > 0.);
    assert!(trial.photons.iter().sum::<f64>() < s.photons.iter().sum::<f64>());
    d.validate(&trial, 1e-8).unwrap();
    eprintln!(
        "reactivated gamma={:e}, absorbed={:e}, scale={scale:e}",
        d.endpoint_photo(&s).unwrap().gamma_s[0],
        trial.ledgers.photo_events[0]
    );
    d.validate(&s, 1e-8).unwrap();
    let file = std::env::temp_dir().join(format!("c2s_v7_{}.txt", std::process::id()));
    d.save_checkpoint(&file, &s).unwrap();
    let t = d.read_checkpoint(&file).unwrap();
    assert_eq!(s.hi_below, t.hi_below);
    assert_eq!(s.photons, t.photons);
    assert!(std::fs::read_to_string(&file)
        .unwrap()
        .starts_with("AXBI_CHECKPOINT_V7\n"));
    std::fs::remove_file(file).unwrap();
}
#[test]
fn bidirectional_all_edges() {
    let c=DriverConfig::read("reactive_hi=true\nhei_split=true\nheii_split=true\ncontinuous_birth=true\nnonmonotone_search=true\ntransport_cells=64\nbackground_panels=64\nend_zbar=19.8").unwrap();
    let (d, _) = Driver::new(c).unwrap();
    let tr = &d.transport;
    let a = 1. / 21.;
    let refg = GeometrySnapshot::new([a; 3], [0.; 3]).unwrap();
    let blue = GeometrySnapshot::new([2. * a, 2. * a, 0.5 * a], [0.; 3]).unwrap();
    let red = GeometrySnapshot::new([a * 2.; 3], [0.; 3]).unwrap();
    let ray = d
        .source
        .angular_cells
        .iter()
        .enumerate()
        .max_by(|a, b| a.1.mu.total_cmp(&b.1.mu))
        .unwrap()
        .0;
    let mut p = tr.empty_state();
    for q in [12., 23., 52.] {
        tr.add_delta(&mut p, ray, q, 1e-6).unwrap();
    }
    let b = tr.partition_four(&p, &refg).unwrap();
    let n =
        |x: &rei_microphysics::axbi_covariant_transport::PhotonState| x.number.iter().sum::<f64>();
    assert_eq!(n(&b.below), 1e-6);
    assert_eq!(n(&b.low), 1e-6);
    assert_eq!(n(&b.middle), 1e-6);
    let v = tr.move_four(&b, &blue).unwrap();
    assert_eq!(n(&v.below), 0.);
    assert!(n(&v.high) > 0.);
    let w = tr.move_four(&v, &red).unwrap();
    let x = tr.move_four(&w, &refg).unwrap();
    assert_eq!(b, x);
}
