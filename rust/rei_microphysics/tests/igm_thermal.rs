use rei_microphysics::{
    igm_rates::igm_rates,
    igm_state::IgmGasState,
    igm_thermal::{igm_point_rhs, IgmPhotoInput},
    HHeModel,
};
fn close(a: f64, b: f64) {
    assert!(
        (a - b).abs() <= 1e-12 * a.abs().max(b.abs()),
        "{a:e} != {b:e}"
    );
}
fn state(f: [f64; 3], t: f64) -> IgmGasState {
    IgmGasState::from_temperature(f, 1.0, 0.1, t).unwrap()
}
#[test]
fn zero_electrons_is_valid_and_only_expands() {
    let s = state([0.0; 3], 100.0);
    let r = igm_point_rhs(&s, 1.0, 0.1, 1e-17, 30.0, IgmPhotoInput::default()).unwrap();
    assert_eq!(r.fraction_dt, [0.0; 3]);
    assert_eq!(r.escape_erg_cm3_s, 0.0);
    assert_eq!(r.cmb_to_gas_erg_cm3_s, 0.0);
    close(r.w_dt_erg_per_h_s, -2e-17 * s.w_erg_per_h);
    close(r.temperature_dt_k_s, -2e-17 * 100.0);
}
#[test]
fn chemistry_charge_and_energy_close_with_external_photo() {
    let s = state([0.3, 0.2, 0.4], 4e4);
    let p = IgmPhotoInput {
        gamma_s: [1e-12, 2e-12, 3e-12],
        heat_erg_per_absorber_s: [2e-23, 3e-23, 4e-23],
    };
    let r = igm_point_rhs(&s, 1.0, 0.1, 1e-17, 50.0, p).unwrap();
    let d = r.species_chemical_cm3_s;
    assert!(r.escape_erg_cm3_s > 0.0);
    close(d[0], -d[1]);
    close(d[2] + d[3], -d[4]);
    close(d[5], d[1] + d[3] + 2.0 * d[4]);
    close(
        r.thermal_micro_erg_cm3_s + r.binding_micro_erg_cm3_s + r.escape_erg_cm3_s,
        r.photo_input_erg_cm3_s + r.cmb_to_gas_erg_cm3_s,
    );
    close(
        r.w_dt_erg_per_h_s + r.expansion_work_erg_cm3_s,
        r.thermal_micro_erg_cm3_s,
    );
    let kb = HHeModel::controlled_fixture().kb_erg_k;
    let eos = s.eos(1.0, 0.1).unwrap();
    let nt = 1.1 + eos.electron_density_cm3;
    close(
        r.temperature_dt_k_s,
        2.0 * r.w_dt_erg_per_h_s / (3.0 * kb * nt) - eos.temperature_k * d[5] / nt,
    );
}
#[test]
fn correct_density_powers_and_single_recombination_owners() {
    let s = state([0.3, 0.2, 0.4], 5e4);
    let a = igm_point_rhs(&s, 1.0, 0.1, 0.0, 50.0, IgmPhotoInput::default()).unwrap();
    let b = igm_point_rhs(&s, 2.0, 0.2, 0.0, 50.0, IgmPhotoInput::default()).unwrap();
    assert!(a.ce_thermal_sink_erg_cm3_s[1] > 0.0);
    close(
        b.ce_thermal_sink_erg_cm3_s[1],
        8.0 * a.ce_thermal_sink_erg_cm3_s[1],
    );
    close(
        b.ce_thermal_sink_erg_cm3_s[0],
        4.0 * a.ce_thermal_sink_erg_cm3_s[0],
    );
    let rates = igm_rates(s.eos(1.0, 0.1).unwrap().temperature_k).unwrap();
    let ne = s.eos(1.0, 0.1).unwrap().electron_density_cm3;
    close(a.rr_events_cm3_s[1], ne * 0.02 * rates.rr_cm3_s[1]);
    close(a.dr_events_cm3_s, ne * 0.02 * rates.dr_cm3_s);
    close(
        a.dr_thermal_sink_erg_cm3_s,
        ne * 0.02 * rates.dr_cooling_erg_cm3_s,
    );
    let constants = HHeModel::controlled_fixture();
    for i in 0..3 {
        close(
            a.ci_thermal_sink_erg_cm3_s[i],
            a.ci_events_cm3_s[i] * constants.threshold_ev[i] * constants.ev_erg,
        );
    }
}
#[test]
fn cmb_signed_and_low_temperature_source_artifacts_visible() {
    let s = state([0.3, 0.2, 0.4], 10.0);
    let t = s.eos(1.0, 0.1).unwrap().temperature_k;
    let at = |tcmb| igm_point_rhs(&s, 1.0, 0.1, 0.0, tcmb, IgmPhotoInput::default()).unwrap();
    assert!(at(20.0).cmb_to_gas_erg_cm3_s > 0.0);
    assert!(at(5.0).cmb_to_gas_erg_cm3_s < 0.0);
    assert_eq!(at(t).cmb_to_gas_erg_cm3_s, 0.0);
    let r = at(t);
    assert_eq!(r.dr_events_cm3_s, 0.0);
    assert_eq!(r.dr_thermal_sink_erg_cm3_s, 0.0);
    assert!(r.excluded_dr_cooling_erg_cm3_s > 0.0);
    assert!(r.ci_floor_events_cm3_s.iter().all(|x| *x > 0.0));
}
#[test]
fn invalid_inputs_fail_without_state_mutation() {
    let s = state([0.3, 0.2, 0.4], 100.0);
    let before = (s.fractions, s.w_erg_per_h);
    for (nh, nhe, h, tc) in [
        (0.0, 0.1, 0.0, 2.7),
        (1.0, -0.1, 0.0, 2.7),
        (1.0, 0.1, -1.0, 2.7),
        (1.0, 0.1, 0.0, f64::NAN),
        (1e200, 1e199, 0.0, 2.7),
        (1.0, 0.1, 0.0, 1e200),
    ] {
        assert!(igm_point_rhs(&s, nh, nhe, h, tc, IgmPhotoInput::default()).is_err());
    }
    assert!(igm_point_rhs(
        &state([0.3, 0.2, 0.4], 0.5),
        1.0,
        0.1,
        0.0,
        2.7,
        IgmPhotoInput::default()
    )
    .is_err());
    let bad = IgmPhotoInput {
        gamma_s: [0.0; 3],
        heat_erg_per_absorber_s: [1e-23; 3],
    };
    assert!(igm_point_rhs(&s, 1.0, 0.1, 0.0, 2.7, bad).is_err());
    assert_eq!((s.fractions, s.w_erg_per_h), before);
}
#[test]
fn pure_species_and_no_helium_are_valid() {
    for f in [[1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [0.0; 3]] {
        let s = IgmGasState::from_temperature(f, 1.0, 0.0, 100.0).unwrap();
        let r = igm_point_rhs(&s, 1.0, 0.0, 0.0, 2.7, IgmPhotoInput::default()).unwrap();
        assert_eq!(r.fraction_dt[1], 0.0);
        assert_eq!(r.fraction_dt[2], 0.0);
    }
}
#[test]
fn cmb_absolute_normalization_and_proper_energy_equivalence() {
    let s = state([0.3, 0.2, 0.4], 100.0);
    let e = s.eos(1.0, 0.1).unwrap();
    let r = igm_point_rhs(&s, 1.0, 0.1, 2e-17, 30.0, IgmPhotoInput::default()).unwrap();
    close(
        r.cmb_to_gas_erg_cm3_s,
        1.0178101728574782e-37
            * e.electron_density_cm3
            * 30.0_f64.powi(4)
            * (30.0 - e.temperature_k),
    );
    close(
        r.w_dt_erg_per_h_s - 3.0 * 2e-17 * e.u_erg_cm3,
        r.thermal_micro_erg_cm3_s - 5.0 * 2e-17 * e.u_erg_cm3,
    );
}
#[test]
fn eos_directional_derivative_includes_changing_particles() {
    let s = state([0.3, 0.2, 0.4], 4e4);
    let r = igm_point_rhs(&s, 1.0, 0.1, 0.0, 30.0, IgmPhotoInput::default()).unwrap();
    let eps = 1e3;
    let at = |dt: f64| {
        IgmGasState::new(
            std::array::from_fn(|i| s.fractions[i] + dt * r.fraction_dt[i]),
            s.w_erg_per_h + dt * r.w_dt_erg_per_h_s,
        )
        .unwrap()
        .eos(1.0, 0.1)
        .unwrap()
        .temperature_k
    };
    let derivative = (at(eps) - at(-eps)) / (2.0 * eps);
    assert!((derivative - r.temperature_dt_k_s).abs() / derivative.abs() < 1e-7);
}
#[test]
fn forged_states_and_nonfinite_photo_inputs_are_rejected() {
    let s = state([0.3, 0.2, 0.4], 100.0);
    for f in [[-0.01, 0.2, 0.4], [0.3, 0.6, 0.6], [f64::NAN, 0.2, 0.4]] {
        let bad = IgmGasState { fractions: f, ..s };
        assert!(igm_point_rhs(&bad, 1.0, 0.1, 0.0, 2.7, IgmPhotoInput::default()).is_err());
    }
    for value in [-1.0, f64::NAN, f64::INFINITY] {
        for p in [
            IgmPhotoInput {
                gamma_s: [value; 3],
                ..IgmPhotoInput::default()
            },
            IgmPhotoInput {
                gamma_s: [1e-10; 3],
                heat_erg_per_absorber_s: [value; 3],
            },
        ] {
            assert!(igm_point_rhs(&s, 1.0, 0.1, 0.0, 2.7, p).is_err());
        }
    }
}
#[test]
fn helium_simplex_boundary_uses_validated_sum_without_clipping() {
    let s = state([0.5, 0.8, 0.2], 100.0);
    let r = igm_point_rhs(&s, 1.0, 0.1, 0.0, 2.7, IgmPhotoInput::default()).unwrap();
    assert_eq!(r.ci_events_cm3_s[1], 0.0);
}
#[test]
fn recovered_eos_temperature_is_strictly_admitted_without_endpoint_projection() {
    // The generic foundation constructor does not promise chemistry admission.
    // These are deliberately NOT silently projected back to the requested T.
    for (f, t) in [([0.0, 0.01, 0.01], 1.0), ([0.0, 0.02, 0.02], 1e6)] {
        let s = IgmGasState::from_temperature(f, 1e-4, 1e-5, t).unwrap();
        let recovered = s.eos(1e-4, 1e-5).unwrap().temperature_k;
        assert!(!(1.0..=1e6).contains(&recovered));
        assert!(igm_point_rhs(&s, 1e-4, 1e-5, 0.0, 2.7, IgmPhotoInput::default()).is_err());
        assert_eq!(s.eos(1e-4, 1e-5).unwrap().temperature_k, recovered);
    }
    for t in [1.00000001, 999999.99] {
        let s = IgmGasState::from_temperature([0.0, 0.01, 0.01], 1e-4, 1e-5, t).unwrap();
        assert!(igm_point_rhs(&s, 1e-4, 1e-5, 0.0, 2.7, IgmPhotoInput::default()).is_ok());
    }
}
