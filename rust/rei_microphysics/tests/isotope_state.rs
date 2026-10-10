use rei_microphysics::{IsotopeNumberState, IsotopeSpecies};
#[test]
fn moments_and_strict_projection() {
    let s = IsotopeNumberState::new([1., 2., 3., 5., 7., 11., 13., 17., 19., 23., 29., 31., 37.])
        .unwrap();
    let m = s.moments().unwrap();
    assert_eq!(m.heavy_particle_density_m3, 198.);
    assert_eq!(m.baryon_density_m3, 667.);
    assert_eq!(m.neutral_free_electron_density_m3, 193.);
    assert_eq!(s.thermal_particle_density_all_thermal_m3().unwrap(), 391.);
    assert!(s.try_legacy_hhe_projection().is_err());
}
#[test]
fn metadata_and_domain() {
    assert_eq!(IsotopeSpecies::He4DoublyIonized.baryon_number(), 4);
    assert_eq!(IsotopeSpecies::He4DoublyIonized.charge(), 2);
    assert_eq!(IsotopeSpecies::He4DoublyIonized.nuclear_charge(), 2);
    assert!(IsotopeNumberState::new([f64::NAN; 13]).is_err());
    assert!(IsotopeNumberState::new([-1.; 13]).is_err());
    let s = IsotopeNumberState::new([0.; 13]).unwrap();
    assert!(s.abundances_per_baryon().is_err());
    let mut tiny = [0.; 13];
    tiny[IsotopeSpecies::H1Ionized as usize] = f64::from_bits(1);
    assert!(IsotopeNumberState::new(tiny)
        .unwrap()
        .try_legacy_hhe_projection()
        .is_err());
}
#[test]
fn legacy_hhe_is_explicit_si() {
    let s =
        IsotopeNumberState::new([0., 2e6, 3e6, 0., 0., 0., 0., 0., 0., 0., 4e6, 5e6, 6e6]).unwrap();
    let p = s.try_legacy_hhe_projection().unwrap();
    assert_eq!(p.n_h_cm3, 5.);
    assert_eq!(p.n_he_cm3, 15.);
    assert_eq!(p.fractions, [0.6, 1.0 / 3.0, 0.4]);
}
