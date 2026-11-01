use rei_microphysics::{HHeModel, IsotopeNumberState, IsotopeSpecies};
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
#[test]
fn legacy_hhe_bridge_recovers_existing_electron_and_temperature_coordinates() {
    let isotope =
        IsotopeNumberState::new([0., 2e6, 3e6, 0., 0., 0., 0., 0., 0., 0., 4e6, 5e6, 6e6]).unwrap();
    let eos = isotope.try_legacy_hhe_eos(6.0e-13, 1.380_649e-23).unwrap();
    let mut model = HHeModel::controlled_fixture();
    model.n_h_cm3 = eos.projection.n_h_cm3;
    model.n_he_cm3 = eos.projection.n_he_cm3;
    let state = rei_microphysics::HHeState {
        fractions: eos.projection.fractions,
        u_erg_cm3: eos.u_erg_cm3,
        photon_cm3: [0.; 3],
        escaped_erg_cm3: 0.,
    };
    assert_eq!(
        model.electron_density(&state).unwrap(),
        eos.electron_density_m3 / 1e6
    );
    assert!((model.temperature(&state).unwrap() - eos.temperature_k).abs() < 1e-12);
    assert_eq!(eos.thermal_particle_density_m3, 40e6);
    assert_eq!(
        isotope
            .try_legacy_hhe_eos(0., 1.380_649e-23)
            .unwrap()
            .temperature_k,
        0.
    );
    assert!(isotope.try_legacy_hhe_eos(-1., 1.380_649e-23).is_err());
    assert!(isotope.try_legacy_hhe_eos(0., 0.).is_err());
    assert!(IsotopeNumberState::new([0.; 13])
        .unwrap()
        .try_legacy_hhe_eos(0., 1.380_649e-23)
        .is_err());
}
#[test]
fn eos_rejects_erased_ion_fraction_and_subnormal_denominator() {
    let mut erased_fraction = [0.; 13];
    erased_fraction[IsotopeSpecies::H1Neutral as usize] = 1e100;
    erased_fraction[IsotopeSpecies::H1Ionized as usize] = 1e-250;
    assert!(IsotopeNumberState::new(erased_fraction)
        .unwrap()
        .try_legacy_hhe_eos(1., 1.)
        .is_err());

    let mut subnormal_density = [0.; 13];
    subnormal_density[IsotopeSpecies::H1Neutral as usize] = 2_f64.powi(-1020);
    assert!(IsotopeNumberState::new(subnormal_density)
        .unwrap()
        .try_legacy_hhe_eos(f64::from_bits(1), 2_f64.powi(-56))
        .is_err());
}
