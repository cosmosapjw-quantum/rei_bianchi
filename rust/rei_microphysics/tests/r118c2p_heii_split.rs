use rei_microphysics::axbi_covariant_transport::CovariantTransport;
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::{AxisymmetricPoint, GeometrySnapshot};
fn g(a: f64) -> GeometrySnapshot {
    AxisymmetricPoint::new(a, 0., 1e-16, 0.)
        .unwrap()
        .snapshot()
        .unwrap()
}
fn core() -> CovariantTransport {
    let s = AxbiSource::new(1.9e-7, 0.2, 8, 8).unwrap();
    CovariantTransport::new(&s, g(0.05), 1, 13.6, 512.).unwrap()
}
#[test]
fn threshold_delta_and_monotone_split() {
    let c = core();
    let mut p = c.empty_state();
    c.add_delta(&mut p, 0, 54.42, 0.1).unwrap();
    let s = c.partition_heii(&p, &g(0.05)).unwrap();
    assert_eq!(s.above, p);
    assert_eq!(s.below, c.empty_state());
    let m = c.move_heii(&s, &g(0.06)).unwrap();
    assert_eq!(m.below, p);
    assert_eq!(m.above, c.empty_state());
    let mut p = c.empty_state();
    c.add_delta(&mut p, 0, 40., 0.7).unwrap();
    c.add_delta(&mut p, 0, 80., 0.3).unwrap();
    let s = c.partition_heii(&p, &g(0.05)).unwrap();
    assert!(s.below.number[0] > 0. && s.above.number[0] > 0.);
    let s2 = c.move_heii(&s, &g(0.06)).unwrap();
    assert!(s2.below.number[0] > s.below.number[0]);
    assert!((s2.below.number[0] + s2.above.number[0] - p.number[0]).abs() < 1e-13);
    assert!((s2.below.energy_ref[0] + s2.above.energy_ref[0] - p.energy_ref[0]).abs() < 1e-11);
}
#[test]
fn exact_source_partition_and_birth_absorption() {
    let c = core();
    let gg = g(0.08);
    let mut p = c.empty_state();
    let u = c.inject(&mut p, &gg, 11.5, 1e13).unwrap();
    let (s, v) = c.inject_heii(&gg, 11.5, 1e13).unwrap();
    assert!(s.above.number.iter().sum::<f64>() > 0.);
    assert!((v.added_photons_per_h / u.added_photons_per_h - 1.).abs() < 1e-13);
    assert!((v.added_energy_ev_per_h / u.added_energy_ev_per_h - 1.).abs() < 1e-13);
    let a = c
        .advance_heii(
            &c.partition_heii(&c.empty_state(), &gg).unwrap(),
            &s,
            &gg,
            [1e-5, 1e-6, 1e-7],
            1e-4,
            1e13,
        )
        .unwrap();
    let (n, w) = c.heii_inventory(&a.state, &gg).unwrap();
    assert!((n + a.absorbed_per_h.iter().sum::<f64>() - v.added_photons_per_h).abs() < 1e-12);
    assert!((w + a.binding_ev_per_h + a.heat_ev_per_h - v.added_energy_ev_per_h).abs() < 1e-11);
}
