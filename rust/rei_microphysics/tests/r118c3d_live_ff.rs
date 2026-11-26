use rei_microphysics::{
    axbi_covariant_driver::{Driver, DriverConfig},
    general_history::{GeneralHistory, HistoryPoint},
};
#[test]
fn actual_candidate_spectrum_roundtrip() {
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
    let cfg=DriverConfig::read("reactive_hi=true\nhei_split=true\nheii_split=true\ncontinuous_birth=true\nnonmonotone_search=true\nq_ref=0\nff_balance_mode=3").unwrap();
    let (mut d, s) = Driver::new_general(cfg.clone(), h.clone()).unwrap();
    let b = a * 1.000001;
    let q = d.transport.general_history().unwrap();
    let l = q.point(a).unwrap();
    let r = q.point(b).unwrap();
    d.set_general_interval(vec![l, r]).unwrap();
    let mut count = 0;
    let x = d.external_trial(&s, b, &mut count).unwrap();
    assert!(s
        .ff_spectrum
        .as_ref()
        .unwrap()
        .distortion()
        .iter()
        .all(|v| *v == 0.));
    assert!(x
        .ff_spectrum
        .as_ref()
        .unwrap()
        .distortion()
        .iter()
        .any(|v| *v != 0.));
    assert!(x.ff_abs_ev > 0.);
    assert!(d.residuals(&x).unwrap().1.abs() < 1e-8);
    let path = std::env::temp_dir().join(format!("rei-c3d-{}.txt", std::process::id()));
    d.save_checkpoint(&path, &x).unwrap();
    let (mut f, _) = Driver::new_general(cfg, h).unwrap();
    let y = f.restore_general_checkpoint(&path).unwrap();
    assert_eq!(
        x.ff_spectrum.as_ref().unwrap().distortion(),
        y.ff_spectrum.as_ref().unwrap().distortion()
    );
    assert_eq!(x.ff_abs_ev, y.ff_abs_ev);
    std::fs::remove_file(path).unwrap();
}

#[test]
fn reject_tampered_v11_distortion() {
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
    let cfg=DriverConfig::read("reactive_hi=true\nhei_split=true\nheii_split=true\ncontinuous_birth=true\nnonmonotone_search=true\nq_ref=0\nff_balance_mode=3").unwrap();
    let (mut d, s) = Driver::new_general(cfg.clone(), h.clone()).unwrap();
    let b = a * 1.000001;
    let q = d.transport.general_history().unwrap();
    let l = q.point(a).unwrap();
    let r = q.point(b).unwrap();
    d.set_general_interval(vec![l, r]).unwrap();
    let mut count = 0;
    let x = d.external_trial(&s, b, &mut count).unwrap();
    let path = std::env::temp_dir().join(format!("rei-c3d-tamper-{}.txt", std::process::id()));
    d.save_checkpoint(&path, &x).unwrap();
    let orig = std::fs::read_to_string(&path).unwrap();
    let old = orig.lines().nth(27).unwrap();
    let mut v = old
        .split_whitespace()
        .map(str::to_owned)
        .collect::<Vec<_>>();
    assert_eq!(v.len(), 128);
    v[0] = format!("{:016x}", (-1e30_f64).to_bits());
    std::fs::write(&path, orig.replacen(old, &v.join(" "), 1)).unwrap();
    let (mut f, _) = Driver::new_general(cfg, h).unwrap();
    assert!(f.restore_general_checkpoint(&path).is_err());
    assert_eq!(f.transport.general_history().unwrap().interval()[0], a);
    std::fs::write(&path, &orig).unwrap();
    assert!(f.restore_general_checkpoint(&path).is_ok());
    std::fs::remove_file(path).unwrap();
}
