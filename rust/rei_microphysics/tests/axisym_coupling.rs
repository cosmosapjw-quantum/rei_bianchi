use rei_microphysics::{
    axisym_coupled_derivative, isotropic_expansion_terms, AxisymCoupledState, AxisymLocalSources,
    AxisymmetricPoint, ForwardError, IsotopeNumberState, IsotopeSpecies,
};

fn state(
    densities: [f64; 13],
    u: f64,
    photon_n: f64,
    photon_u: f64,
    delta_p: f64,
) -> AxisymCoupledState {
    AxisymCoupledState {
        isotopes: IsotopeNumberState::new(densities).unwrap(),
        thermal_energy_j_m3: u,
        photon_number_m3: photon_n,
        photon_energy_j_m3: photon_u,
        photon_delta_pressure_j_m3: delta_p,
    }
}
fn zero_sources() -> AxisymLocalSources {
    AxisymLocalSources {
        species_m3_s: [0.; 13],
        electron_m3_s: 0.,
        photon_number_m3_s: 0.,
        photon_power_j_m3_s: 0.,
        thermal_power_j_m3_s: 0.,
        internal_power_j_m3_s: 0.,
        escape_power_j_m3_s: 0.,
        external_power_j_m3_s: 0.,
    }
}
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

#[test]
fn coupled_scalar_expansion_keeps_photon_number_and_adds_shear_work() {
    let mut n = [0.; 13];
    n[IsotopeSpecies::H1Neutral as usize] = 2.;
    n[IsotopeSpecies::H1Ionized as usize] = 1.;
    let s = state(n, 60., 7., 22., 4.);
    let g = AxisymmetricPoint::new(1., 0., 0.2, 0.05).unwrap();
    let d = axisym_coupled_derivative(0., g, &s, 1., |_, _| Ok(zero_sources())).unwrap();
    assert_eq!(d.temperature_k, 10.);
    assert_eq!(d.temperature_k_s, -4.);
    assert!((d.photon_number_m3_s + 4.2).abs() < 1e-14);
    assert_eq!(d.photon_energy_j_m3_s, -18.);
    assert!((d.species_m3_s[IsotopeSpecies::H1Neutral as usize] + 1.2).abs() < 1e-14);
}

#[test]
fn signed_absorption_ledger_changes_particle_temperature_without_double_counting() {
    let mut n = [0.; 13];
    n[IsotopeSpecies::H1Neutral as usize] = 8.;
    n[IsotopeSpecies::H1Ionized as usize] = 2.;
    let s = state(n, 180., 9., 10., 0.);
    let g = AxisymmetricPoint::new(1., 0., 0., 0.).unwrap();
    let event = AxisymLocalSources {
        species_m3_s: [0., -2., 2., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        electron_m3_s: 2.,
        photon_number_m3_s: -2.,
        photon_power_j_m3_s: -10.,
        thermal_power_j_m3_s: 4.,
        internal_power_j_m3_s: 6.,
        escape_power_j_m3_s: 0.,
        external_power_j_m3_s: 0.,
    };
    let d = axisym_coupled_derivative(0., g, &s, 1., |_, _| Ok(event)).unwrap();
    assert_eq!(d.temperature_k, 10.);
    assert!((d.temperature_k_s + 13. / 9.).abs() < 1e-14);
    assert_eq!(d.electron_m3_s, 2.);
    let reverse = AxisymLocalSources {
        species_m3_s: event.species_m3_s.map(|x| -x),
        electron_m3_s: -event.electron_m3_s,
        photon_number_m3_s: -event.photon_number_m3_s,
        photon_power_j_m3_s: -event.photon_power_j_m3_s,
        thermal_power_j_m3_s: -event.thermal_power_j_m3_s,
        internal_power_j_m3_s: -event.internal_power_j_m3_s,
        escape_power_j_m3_s: 0.,
        external_power_j_m3_s: 0.,
    };
    let reverse_d = axisym_coupled_derivative(0., g, &s, 1., |_, _| Ok(reverse)).unwrap();
    assert!((reverse_d.temperature_k_s - 13. / 9.).abs() < 1e-14);

    let mut cancelling = event;
    cancelling.species_m3_s[IsotopeSpecies::DNeutral as usize] = 1e20;
    cancelling.species_m3_s[IsotopeSpecies::DIonized as usize] = -1e20;
    cancelling.species_m3_s[IsotopeSpecies::He3Neutral as usize] = -1e20;
    cancelling.species_m3_s[IsotopeSpecies::He3SinglyIonized as usize] = 1e20;
    let cancelling_d = axisym_coupled_derivative(0., g, &s, 1., |_, _| Ok(cancelling)).unwrap();
    assert!((cancelling_d.temperature_k_s + 13. / 9.).abs() < 1e-14);
}

#[test]
fn nonlegacy_charge_exchange_preserves_baryons_electrons_and_temperature_source() {
    let mut n = [0.; 13];
    n[IsotopeSpecies::DIonized as usize] = 1.;
    n[IsotopeSpecies::He3Neutral as usize] = 1.;
    let s = state(n, 9., 0., 0., 0.);
    let g = AxisymmetricPoint::new(1., 0., 0., 0.).unwrap();
    let mut q = zero_sources();
    q.species_m3_s[IsotopeSpecies::DNeutral as usize] = 0.25;
    q.species_m3_s[IsotopeSpecies::DIonized as usize] = -0.25;
    q.species_m3_s[IsotopeSpecies::He3Neutral as usize] = -0.25;
    q.species_m3_s[IsotopeSpecies::He3SinglyIonized as usize] = 0.25;
    let d = axisym_coupled_derivative(0., g, &s, 1., |_, _| Ok(q)).unwrap();
    assert_eq!(d.electron_m3_s, 0.);
    assert_eq!(d.thermal_particle_m3_s, 0.);
    assert_eq!(d.temperature_k_s, 0.);
}

#[test]
fn rejects_open_ledgers_at_small_scales_and_calls_provider_once() {
    let mut n = [0.; 13];
    n[IsotopeSpecies::H1Neutral as usize] = 1.;
    let s = state(n, 1.5, 1., 1., 0.);
    let g = AxisymmetricPoint::new(1., 0., 0., 0.).unwrap();
    for scale in [1., 1e-20] {
        let mut bad = zero_sources();
        bad.species_m3_s[IsotopeSpecies::H1Neutral as usize] = scale;
        assert!(axisym_coupled_derivative(0., g, &s, 1., |_, _| Ok(bad)).is_err());
    }
    for scale in [1., 1e-20] {
        let mut bad = zero_sources();
        bad.electron_m3_s = scale;
        assert!(axisym_coupled_derivative(0., g, &s, 1., |_, _| Ok(bad)).is_err());
        let mut bad = zero_sources();
        bad.thermal_power_j_m3_s = scale;
        assert!(axisym_coupled_derivative(0., g, &s, 1., |_, _| Ok(bad)).is_err());
    }
    let calls = std::cell::Cell::new(0);
    let err = axisym_coupled_derivative(0., g, &s, 1., |_, _| {
        calls.set(calls.get() + 1);
        Err(ForwardError::MissingAuthority("fixture"))
    });
    assert_eq!(calls.get(), 1);
    assert!(matches!(
        err,
        Err(ForwardError::MissingAuthority("fixture"))
    ));
    let invalid_pressure = state(n, 1.5, 1., 1., 2.);
    assert!(
        axisym_coupled_derivative(0., g, &invalid_pressure, 1., |_, _| Ok(zero_sources())).is_err()
    );
    let mut enormous = [0.; 13];
    enormous[IsotopeSpecies::H1Neutral as usize] = 1e308;
    let overflowed_temperature = state(enormous, 1e100, 1., 1., 0.);
    assert!(
        axisym_coupled_derivative(
            0.,
            g,
            &overflowed_temperature,
            1.,
            |_, _| Ok(zero_sources())
        )
        .is_err()
    );
    let mut subnormal = [0.; 13];
    subnormal[IsotopeSpecies::H1Neutral as usize] = 0.5;
    let subnormal_temperature = state(subnormal, f64::from_bits(1), 1., 1., 0.);
    assert!(axisym_coupled_derivative(
        0.,
        g,
        &subnormal_temperature,
        f64::from_bits(1),
        |_, _| Ok(zero_sources())
    )
    .is_err());
}
