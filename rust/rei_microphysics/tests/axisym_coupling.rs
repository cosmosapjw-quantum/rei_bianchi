use rei_microphysics::isotropic_expansion_terms;
#[test]
fn scalar_expansion_has_distinct_conservation_owners() {
    let x = isotropic_expansion_terms(0.2, 5., 7., 11., 13.).unwrap();
    for (got, expected) in [
        (x.nuclear_density_dot_per_s, -3.0),
        (x.photon_number_dot_per_s, -4.2),
        (x.photon_energy_dot_per_s, -8.8),
        (x.temperature_dot_k_s, -5.2),
    ] {
        assert!((got - expected).abs() <= 16.0 * f64::EPSILON * expected.abs());
    }
    let z = isotropic_expansion_terms(0., 5., 7., 11., 13.).unwrap();
    assert_eq!(z.nuclear_density_dot_per_s, 0.);
    assert_eq!(z.photon_number_dot_per_s, 0.);
    assert!(isotropic_expansion_terms(f64::NAN, 1., 1., 1., 1.).is_err());
}
