use rei_microphysics::axbi_covariant_driver::{Driver, DriverConfig};
#[test]
fn high_grid_extension_preserves_old_cells() {
    let cfg="reactive_hi=true\nhei_split=true\nheii_split=true\ncontinuous_birth=true\nnonmonotone_search=true\nq_ref=-1\ntransport_cells=32\nbackground_panels=64";
    let (a, _) = Driver::new(DriverConfig::read(cfg).unwrap()).unwrap();
    let (b, _) =
        Driver::new(DriverConfig::read(&format!("{cfg}\nreactive_extra_high_cells=3")).unwrap())
            .unwrap();
    assert_eq!(a.transport.edges(), &b.transport.edges()[..=32]);
    assert_eq!(b.transport.n_energy(), 35);
    assert!(b.transport.edges()[35] > 512.);
    let bounds = b.required_source_q_bounds().unwrap();
    eprintln!("bounds={bounds:?} top={}", b.transport.edges()[35]);
    assert!(bounds[0] > 6.8 && bounds[1] > 512. && bounds[1] < b.transport.edges()[35]);
}
