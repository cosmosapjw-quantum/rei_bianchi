use rei_microphysics::{
    axbi_covariant_driver::{Driver, DriverConfig},
    general_history::{GeneralHistory, HistoryPoint},
};
fn make() -> (Driver, rei_microphysics::axbi_covariant_driver::DriverState) {
    let a = 1. / 21.;
    let id = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]];
    let h = GeneralHistory::new(
        vec![
            HistoryPoint { a, h: 50., f: id },
            HistoryPoint {
                a: 0.2,
                h: 6.,
                f: id,
            },
        ],
        4,
        8,
    )
    .unwrap();
    let cfg=DriverConfig::read("reactive_hi=true\nhei_split=true\nheii_split=true\ncontinuous_birth=true\nnonmonotone_search=true\nq_ref=0").unwrap();
    Driver::new_general(cfg, h).unwrap()
}
#[test]
fn general_restart_exact() {
    let (mut d, s) = make();
    let a = s.a;
    let b = a * 1.000001;
    let h = d.transport.general_history().unwrap().point(a).unwrap();
    let e = d.transport.general_history().unwrap().point(b).unwrap();
    d.set_general_interval(vec![h, e]).unwrap();
    let mut count = 0;
    let x = d.external_trial(&s, b, &mut count).unwrap();
    let path = std::env::temp_dir().join(format!("rei-c2x-{}.txt", std::process::id()));
    d.save_checkpoint(&path, &x).unwrap();
    let (mut fresh, _) = make();
    let y = fresh.restore_general_checkpoint(&path).unwrap();
    assert_eq!(x.a, y.a);
    assert_eq!(x.photons, y.photons);
    assert_eq!(x.heii_above, y.heii_above);
    assert_eq!(x.ledgers.source_u, y.ledgers.source_u);
    let path2 = path.with_extension("second");
    fresh.save_checkpoint(&path2, &y).unwrap();
    assert_eq!(
        std::fs::read(&path).unwrap(),
        std::fs::read(&path2).unwrap()
    );
    std::fs::remove_file(path).unwrap();
    std::fs::remove_file(path2).unwrap();
}
#[test]
fn reject_wrong_registry_config_and_source() {
    let (mut d, s) = make();
    let a = s.a;
    let b = a * 1.000001;
    let h = d.transport.general_history().unwrap().point(a).unwrap();
    let e = d.transport.general_history().unwrap().point(b).unwrap();
    d.set_general_interval(vec![h, e]).unwrap();
    let mut count = 0;
    let x = d.external_trial(&s, b, &mut count).unwrap();
    let path = std::env::temp_dir().join(format!("rei-c2x-bad-{}.txt", std::process::id()));
    d.save_checkpoint(&path, &x).unwrap();
    let orig = std::fs::read_to_string(&path).unwrap();
    let (mut fresh, _) = make();
    assert!(fresh.read_checkpoint(&path).is_err());
    // Wrong registry: one bit changed in the serialized direction/weight data.
    let old = orig.lines().nth(24).unwrap();
    let line = old.replacen('0', "1", 1);
    std::fs::write(&path, orig.replacen(old, &line, 1)).unwrap();
    assert!(fresh.restore_general_checkpoint(&path).is_err());
    assert_eq!(fresh.transport.general_history().unwrap().interval()[0], a);
    // Source mismatch (preserve layout).
    std::fs::write(&path, format!("{orig}changed")).unwrap();
    assert!(fresh.restore_general_checkpoint(&path).is_err());
    std::fs::write(&path, &orig).unwrap();
    let mut other = make().0;
    other.config.local_target *= 0.5;
    assert!(other.restore_general_checkpoint(&path).is_err());
    let y = fresh.restore_general_checkpoint(&path).unwrap();
    assert_eq!(y.a, b);
    std::fs::remove_file(path).unwrap();
}
