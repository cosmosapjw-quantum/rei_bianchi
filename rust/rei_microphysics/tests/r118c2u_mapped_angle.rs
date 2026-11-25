use rei_microphysics::axbi_covariant_driver::{Driver, DriverConfig};
#[test]
fn mapped_fixed_reference_angles_reduce_false_birth_quadrupole() {
    let base="reactive_hi=true\nhei_split=true\nheii_split=true\ncontinuous_birth=true\nnonmonotone_search=true\nq_ref=-1\nn_mu=16\ntransport_cells=32\nreactive_extra_high_cells=3\nbackground_panels=64";
    let (a, _) = Driver::new(DriverConfig::read(base).unwrap()).unwrap();
    let (b, _) =
        Driver::new(DriverConfig::read(&format!("{base}\nangular_map_ratio=0.5")).unwrap())
            .unwrap();
    let f = |d: &Driver, scale: f64| {
        let g = d
            .background
            .point_at_scale(scale)
            .unwrap()
            .geometry()
            .unwrap();
        let r = d.transport.ray_geometry(&g).unwrap();
        r.iter()
            .map(|x| x.angular_weight * (3. * x.mu * x.mu - 1.) / 2.)
            .sum::<f64>()
    };
    assert!(f(&a, 0.2).abs() > 0.01);
    for i in 0..=32 {
        let s = (1. / 21.) * (21_f64 / 5.).powf(i as f64 / 32.);
        let s = s.min(0.2);
        assert!(f(&b, s).abs() < 3e-5)
    }
    assert!(b.source.angular_cells[0].mu < 0. && b.source.angular_cells[15].mu > 0.);
}
