use rei_microphysics::{
    axbi_covariant_driver::{Driver, DriverConfig},
    general_history::{GeneralHistory, HistoryPoint},
};
#[test]
fn general_driver_isotropic_reduction() {
    let a = 1. / 21.;
    let b = 0.2;
    let id = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]];
    let h = GeneralHistory::new(
        vec![
            HistoryPoint { a, h: 50., f: id },
            HistoryPoint { a: b, h: 6., f: id },
        ],
        4,
        8,
    )
    .unwrap();
    let cfg=DriverConfig::read("reactive_hi=true\nhei_split=true\nheii_split=true\ncontinuous_birth=true\nnonmonotone_search=true\nq_ref=0\ntransport_cells=32\nreactive_extra_high_cells=3").unwrap();
    let (d, s) = Driver::new_general(cfg, h).unwrap();
    let p = d.general_moments(&s).unwrap();
    assert_eq!(p.energy, 0.);
    assert_eq!(d.transport.cell_count(), 32 * 35);
    let x = d.probe_step(&s, 1e-6).unwrap().half;
    let p = d.general_moments(&x).unwrap();
    assert!(p.energy > 0.);
    assert!(p.flux.iter().all(|x| x.abs() < 1e-12 * p.energy));
    assert!((p.pressure[0][0] - p.energy / 3.).abs() < 1e-12 * p.energy);
}
#[test]
fn constant_h_clock_and_checkpoint_domain() {
    let a = 1. / 21.;
    let b = 0.2;
    let id = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]];
    let h = GeneralHistory::new(
        vec![
            HistoryPoint { a, h: 50., f: id },
            HistoryPoint {
                a: b,
                h: 50.,
                f: id,
            },
        ],
        4,
        8,
    )
    .unwrap();
    let t = h.dt(a, b).unwrap();
    assert!((t / ((b / a).ln() / (50. * 2.1842852410855023e-18)) - 1.).abs() < 1e-14);
    let cfg=DriverConfig::read("reactive_hi=true\nhei_split=true\nheii_split=true\ncontinuous_birth=true\nnonmonotone_search=true\nq_ref=0").unwrap();
    let (d, s) = Driver::new_general(cfg, h).unwrap();
    assert!(d
        .save_checkpoint(std::path::Path::new("/tmp/unsupported_general_ck"), &s)
        .is_err());
}
#[test]
fn external_trial_keeps_reference_and_exact_endpoint() {
    let a = 1. / 21.;
    let b = 0.2;
    let id = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]];
    let h = GeneralHistory::new(
        vec![
            HistoryPoint { a, h: 50., f: id },
            HistoryPoint {
                a: b,
                h: 50.,
                f: id,
            },
        ],
        4,
        8,
    )
    .unwrap();
    let cfg=DriverConfig::read("reactive_hi=true\nhei_split=true\nheii_split=true\ncontinuous_birth=true\nnonmonotone_search=true\nq_ref=0").unwrap();
    let (mut d, s) = Driver::new_general(cfg, h).unwrap();
    let a1 = a * 1.000001;
    d.set_general_interval(vec![
        HistoryPoint { a, h: 50., f: id },
        HistoryPoint {
            a: a1,
            h: 50.,
            f: id,
        },
    ])
    .unwrap();
    let mut count = 0;
    let x = d.external_trial(&s, a1, &mut count).unwrap();
    assert_eq!(x.a, a1);
    assert_eq!(x.accepted, 1);
    assert!(count > 0);
    let m = d.general_moments(&x).unwrap();
    assert!(m.energy > 0.);
    let ray = d.transport.general_history().unwrap().rays(a1).unwrap().0;
    assert!((ray[0].scale - a / a1).abs() < 1e-14);
}
#[test]
fn external_interval_rejects_changed_start() {
    let a = 1. / 21.;
    let id = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]];
    let mut h = GeneralHistory::new(
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
    let f = [[2., 0., 0.], [0., 0.5, 0.], [0., 0., 1.]];
    assert!(h
        .replace_interval(vec![
            HistoryPoint { a, h: 50., f },
            HistoryPoint {
                a: a * 1.000001,
                h: 49.,
                f
            }
        ])
        .is_err());
    assert_eq!(h.point(a).unwrap().f, id);
}
