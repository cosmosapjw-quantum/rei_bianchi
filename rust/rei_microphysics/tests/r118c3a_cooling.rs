use rei_microphysics::{
    axbi_covariant_driver::{Driver, DriverConfig},
    general_history::{GeneralHistory, HistoryPoint},
    igm_state::IgmGasState,
    igm_thermal::{igm_point_rhs, IgmPhotoInput},
};
#[test]
fn source_partition() {
    let s = IgmGasState::from_temperature([0.1, 0.2, 0.03], 1e-3, 8e-5, 200.).unwrap();
    let r = igm_point_rhs(&s, 1e-3, 8e-5, 1e-16, 50., IgmPhotoInput::default()).unwrap();
    let c = r.cooling_channels().unwrap();
    assert!(c.iter().all(|x| *x >= 0.));
    assert!((c.iter().sum::<f64>() / r.escape_erg_cm3_s - 1.).abs() < 1e-14);
    assert_eq!(c[7], r.freefree_thermal_sink_erg_cm3_s);
}
#[test]
fn accepted_cooling_ledger_roundtrip() {
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
    let (mut d, s) = Driver::new_general(cfg.clone(), h.clone()).unwrap();
    let b = a * 1.000001;
    let q = d.transport.general_history().unwrap();
    let l = q.point(a).unwrap();
    let r = q.point(b).unwrap();
    d.set_general_interval(vec![l, r]).unwrap();
    let mut count = 0;
    let x = d.external_trial(&s, b, &mut count).unwrap();
    assert!(x.cooling_ev[7] > 0.);
    assert!((x.cooling_ev.iter().sum::<f64>() / x.ledgers.escaped_u - 1.).abs() < 1e-12);
    assert!(x.ff_temp_ev_k / x.cooling_ev[7] > 0.);
    let path = std::env::temp_dir().join(format!("rei-c3a-{}.txt", std::process::id()));
    d.save_checkpoint(&path, &x).unwrap();
    let (mut fresh, _) = Driver::new_general(cfg, h).unwrap();
    let y = fresh.restore_general_checkpoint(&path).unwrap();
    assert_eq!(x.cooling_ev, y.cooling_ev);
    assert_eq!(x.ff_temp_ev_k, y.ff_temp_ev_k);
    assert!(std::fs::read_to_string(&path)
        .unwrap()
        .starts_with("AXBI_CHECKPOINT_V10_GENERAL"));
    std::fs::remove_file(path).unwrap();
}
