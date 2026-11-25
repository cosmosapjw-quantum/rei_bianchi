use rei_microphysics::axbi_driver::{Driver, DriverConfig};
#[test]
fn independent_donor_initial_state_is_explicit_and_conservative() {
    let c=DriverConfig::read("end_zbar=19.999\ninitial_temperature_k=9.3\ninitial_x_hii=0.00021\ninitial_x_heii=0\ninitial_x_heiii=0\ninitial_state_id=REC_HMLA_BOUNDARY\n").unwrap();
    let (d, s) = Driver::new(c).unwrap();
    assert_eq!(s.gas.fractions, [0.00021, 0., 0.]);
    assert_eq!(s.photons.iter().sum::<f64>(), 0.);
    let (n, e) = d.residuals(&s).unwrap();
    assert_eq!(n, 0.);
    assert_eq!(e, 0.);
    let k = d.thomson_material_knot(&s, [0.; 3]).unwrap();
    assert!((k.electrons_per_reference / 0.00021 - 1.).abs() < 2e-14);
}
#[test]
fn default_initial_census_retained_and_bad_donor_rejected() {
    let (_, s) = Driver::new(DriverConfig::baseline()).unwrap();
    assert_eq!(s.gas.fractions, [2e-4, 0., 0.]);
    assert!(DriverConfig::read("initial_x_heii=0.8\ninitial_x_heiii=0.3").is_err());
    assert!(DriverConfig::read("initial_x_hii=nan").is_err());
}
