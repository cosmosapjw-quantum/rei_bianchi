use rei_microphysics::{
    coupled_primary::PrimaryPacket, igm_state::IgmGasState, igm_step::*, HHeModel,
};
fn bg() -> StepBackground {
    StepBackground {
        n_h: 4e-4,
        n_he: 3.16e-5,
        hubble: 6e-17,
        tcmb: 35.0,
    }
}
fn gas(t: f64) -> IgmGasState {
    IgmGasState::from_temperature([2e-4, 0.0, 0.0], bg().n_h, bg().n_he, t).unwrap()
}
fn binding(g: &IgmGasState, b: StepBackground) -> f64 {
    let c = HHeModel::controlled_fixture();
    c.ev_erg
        * (c.threshold_ev[0] * g.fractions[0]
            + b.n_he / b.n_h
                * (c.threshold_ev[1] * g.fractions[1]
                    + (c.threshold_ev[1] + c.threshold_ev[2]) * g.fractions[2]))
}
#[test]
fn neutral_helium_growth_and_complete_energy_number_ownership() {
    let old = gas(30.0);
    let p = vec![PrimaryPacket {
        energy_ev: 80.0,
        per_h: 0.01,
    }];
    let dt = 1e11;
    let b = bg();
    let r = implicit_step(&old, &p, b, dt, StepControl::default()).unwrap();
    assert!(r.gas.fractions[1] > 0.0 && r.gas.fractions[2] > 0.0);
    assert!(r.packets[0].per_h > 0.0 && r.packets[0].per_h < p[0].per_h);
    let absorbed = r.absorbed_per_h.iter().sum::<f64>();
    assert!((p[0].per_h - r.packets[0].per_h - absorbed).abs() < 1e-10 * p[0].per_h);
    let c = HHeModel::controlled_fixture();
    let material = r.gas.w_erg_per_h + binding(&r.gas, b) - old.w_erg_per_h - binding(&old, b);
    let radiation = (r.packets[0].per_h - p[0].per_h) * 80.0 * c.ev_erg;
    let reservoirs = dt / b.n_h
        * (r.endpoint.escape_erg_cm3_s - r.endpoint.cmb_to_gas_erg_cm3_s
            + r.endpoint.expansion_work_erg_cm3_s);
    assert!((material + radiation + reservoirs).abs() < 1e-10 * (p[0].per_h * 80.0 * c.ev_erg));
    assert!(r.residual <= 1e-13);
}
#[test]
fn zero_photons_and_zero_electrons_stay_zero() {
    let b = bg();
    let old = IgmGasState::from_temperature([0.0; 3], b.n_h, b.n_he, 30.0).unwrap();
    let r = implicit_step(&old, &[], b, 1e12, StepControl::default()).unwrap();
    assert_eq!(r.gas.fractions, [0.0; 3]);
    assert!(r.packets.is_empty());
    assert!(r.gas.w_erg_per_h < old.w_erg_per_h);
}
#[test]
fn failure_is_nonmutating_and_eos_domain_is_strict() {
    let old = gas(30.0);
    let copy = old;
    assert!(implicit_step(
        &old,
        &[],
        bg(),
        1e12,
        StepControl {
            max_iterations: 0,
            ..StepControl::default()
        }
    )
    .is_err());
    assert_eq!(old.fractions, copy.fractions);
    assert_eq!(old.w_erg_per_h, copy.w_erg_per_h);
    let bad = gas(0.9);
    assert!(implicit_step(&bad, &[], bg(), 1.0, StepControl::default()).is_err());
}
#[test]
fn high_opacity_and_stiff_recombination_remain_admissible() {
    let b = StepBackground {
        n_h: 1.0,
        n_he: 0.08,
        ..bg()
    };
    let old = IgmGasState::from_temperature([0.9, 0.2, 0.7], b.n_h, b.n_he, 1e4).unwrap();
    let r = implicit_step(
        &old,
        &[PrimaryPacket {
            energy_ev: 20.0,
            per_h: 1e-3,
        }],
        b,
        1e11,
        StepControl::default(),
    )
    .unwrap();
    r.gas.eos(b.n_h, b.n_he).unwrap();
    assert!(r.packets[0].per_h > 0.0);
    assert!(r.gas.fractions[0] < old.fractions[0]);
}
#[test]
fn admitted_static_eos_roots_are_exact_fixed_points_including_endpoints() {
    let b = StepBackground {
        hubble: 0.0,
        ..bg()
    };
    for t in [1.0, 1.0 + 1e-13, 30.0, 1e6 - 1e-7, 1e6] {
        let old = IgmGasState::from_temperature([0.0; 3], b.n_h, b.n_he, t).unwrap();
        if rei_microphysics::igm_thermal::igm_point_rhs(
            &old,
            b.n_h,
            b.n_he,
            0.0,
            b.tcmb,
            Default::default(),
        )
        .is_err()
        {
            continue;
        }
        let r = implicit_step(&old, &[], b, 1.0, StepControl::default()).unwrap();
        assert_eq!(r.gas.w_erg_per_h, old.w_erg_per_h);
        assert_eq!(r.gas.fractions, old.fractions);
    }
}
#[test]
fn tiny_adiabatic_steps_keep_representable_budget_roots() {
    let b = bg();
    let old = IgmGasState::from_temperature([0.0; 3], b.n_h, b.n_he, 30.0).unwrap();
    for dt in [3.0, 10.0, 1e3, 1e6] {
        let r = implicit_step(&old, &[], b, dt, StepControl::default()).unwrap();
        let expected = old.w_erg_per_h / (1.0 + 2.0 * b.hubble * dt);
        assert!((r.gas.w_erg_per_h - expected).abs() <= 2e-30);
    }
}

#[test]
fn source_step_emits_immediately_and_obeys_backward_euler_ownership() {
    let old = gas(30.0);
    let b = bg();
    let packets = [PrimaryPacket {
        energy_ev: 80.0,
        per_h: 0.0,
    }];
    let source = [1e-14];
    let dt = 1e11;
    let r =
        implicit_step_with_source(&old, &packets, &source, b, dt, StepControl::default()).unwrap();
    let emitted = dt * source[0];
    let k = rei_microphysics::igm_photo::packet_opacity(&r.gas, 80.0, b.n_h, b.n_he).unwrap();
    let expected = emitted / (1.0 + dt * k.iter().sum::<f64>());
    assert!(
        r.packets[0].per_h > 0.0,
        "a continuous source must contribute in the first BE step"
    );
    assert_eq!(r.packets[0].energy_ev, packets[0].energy_ev);
    assert!((r.packets[0].per_h - expected).abs() < 2e-15 * emitted);
    for (i, opacity) in k.iter().enumerate() {
        assert!((r.absorbed_per_h[i] - dt * opacity * r.packets[0].per_h).abs() < 2e-15 * emitted);
    }
    assert!(
        (emitted - r.packets[0].per_h - r.absorbed_per_h.iter().sum::<f64>()).abs()
            < 1e-10 * emitted
    );
    let ev_erg = HHeModel::controlled_fixture().ev_erg;
    let material = r.gas.w_erg_per_h + binding(&r.gas, b) - old.w_erg_per_h - binding(&old, b);
    let radiation = (r.packets[0].per_h - packets[0].per_h) * packets[0].energy_ev * ev_erg;
    let reservoirs = dt / b.n_h
        * (r.endpoint.escape_erg_cm3_s - r.endpoint.cmb_to_gas_erg_cm3_s
            + r.endpoint.expansion_work_erg_cm3_s);
    let source_energy = emitted * packets[0].energy_ev * ev_erg;
    assert!((material + radiation + reservoirs - source_energy).abs() < 1e-10 * source_energy);
}

#[test]
fn source_step_without_absorption_accumulates_emission_at_fixed_energy() {
    let b = StepBackground {
        hubble: 0.0,
        ..bg()
    };
    let old = IgmGasState::from_temperature([0.0; 3], b.n_h, b.n_he, 30.0).unwrap();
    let packets = [PrimaryPacket {
        energy_ev: 10.0,
        per_h: 0.125,
    }];
    let source = [2e-15];
    let dt = 1e11;
    let r =
        implicit_step_with_source(&old, &packets, &source, b, dt, StepControl::default()).unwrap();
    assert_eq!(r.packets[0].per_h, packets[0].per_h + dt * source[0]);
    assert_eq!(r.packets[0].energy_ev, packets[0].energy_ev);
    assert_eq!(r.gas.fractions, old.fractions);
    assert_eq!(r.gas.w_erg_per_h, old.w_erg_per_h);
    assert_eq!(r.absorbed_per_h, [0.0; 3]);
}

#[test]
fn zero_source_step_is_bitwise_legacy_equivalent() {
    let packets = [
        PrimaryPacket {
            energy_ev: 20.0,
            per_h: 0.001,
        },
        PrimaryPacket {
            energy_ev: 80.0,
            per_h: 0.002,
        },
    ];
    let old = gas(30.0);
    let legacy = implicit_step(&old, &packets, bg(), 1e11, StepControl::default()).unwrap();
    let sourced = implicit_step_with_source(
        &old,
        &packets,
        &[0.0, 0.0],
        bg(),
        1e11,
        StepControl::default(),
    )
    .unwrap();
    assert_eq!(format!("{legacy:?}"), format!("{sourced:?}"));
}

#[test]
fn source_step_rejects_invalid_rates_shapes_and_overflow_without_mutation() {
    let old = gas(30.0);
    let packets = [PrimaryPacket {
        energy_ev: 80.0,
        per_h: 0.0,
    }];
    let before = format!("{old:?} {packets:?}");
    for source in [
        vec![],
        vec![0.0, 0.0],
        vec![-1.0],
        vec![f64::NAN],
        vec![f64::INFINITY],
        vec![f64::MIN_POSITIVE / 2.0],
        vec![f64::MAX],
    ] {
        assert!(
            implicit_step_with_source(&old, &packets, &source, bg(), 1e11, StepControl::default())
                .is_err(),
            "invalid source admitted: {source:?}"
        );
    }
    let negative_old = [PrimaryPacket {
        energy_ev: 80.0,
        per_h: -0.001,
    }];
    assert!(
        implicit_step_with_source(
            &old,
            &negative_old,
            &[1e-13],
            bg(),
            1e11,
            StepControl::default()
        )
        .is_err(),
        "emission must not conceal an invalid incoming packet"
    );
    assert_eq!(before, format!("{old:?} {packets:?}"));
}

#[test]
fn source_step_retains_subnormal_emission_and_bounds_arithmetic_underflow() {
    let b = StepBackground {
        hubble: 0.0,
        ..bg()
    };
    let old = IgmGasState::from_temperature([0.0; 3], b.n_h, b.n_he, 30.0).unwrap();
    let packets = [PrimaryPacket {
        energy_ev: 10.0,
        per_h: 0.0,
    }];
    for dt in [0.25, f64::MIN_POSITIVE] {
        let r = implicit_step_with_source(
            &old,
            &packets,
            &[f64::MIN_POSITIVE],
            b,
            dt,
            StepControl::default(),
        )
        .unwrap();
        assert_eq!(r.packets[0].per_h, dt * f64::MIN_POSITIVE);
        assert!(r.underflow_n_bound > 0.0 && r.underflow_n_bound <= 1e-20);
        assert!(r.underflow_e_bound > 0.0 && r.underflow_e_bound <= 1e-30);
    }
}

#[test]
fn masked_cutoff_photo_support_has_one_common_owner_without_energy_shift() {
    use rei_microphysics::igm_photo::{
        igm_photo_rates, igm_photo_rates_masked, packet_opacity_masked,
    };
    let b = bg();
    let old = IgmGasState::from_temperature([0.2, 0.3, 0.1], b.n_h, b.n_he, 100.0).unwrap();
    let energy = rei_microphysics::verner_cutoff_ev(rei_microphysics::Absorber::HeII);
    let packets = [PrimaryPacket {
        energy_ev: energy,
        per_h: 0.001,
    }];
    let masks = [[true, true, false]];
    let unmasked = igm_photo_rates(&old, &packets, b.n_h, b.n_he).unwrap();
    let masked = igm_photo_rates_masked(&old, &packets, &masks, b.n_h, b.n_he).unwrap();
    assert!(unmasked.input.gamma_s[2] > 0.0);
    assert_eq!(masked.input.gamma_s[2], 0.0);
    assert_eq!(masked.input.heat_erg_per_absorber_s[2], 0.0);
    assert_eq!(masked.packet_owner_per_h_s[0][2], 0.0);
    assert_eq!(&masked.input.gamma_s[..2], &unmasked.input.gamma_s[..2]);
    for source in [0.0, 1e-14] {
        let dt = 1e10;
        let r = implicit_step_with_source_masked(
            &old,
            &packets,
            &[source],
            &masks,
            b,
            dt,
            StepControl::default(),
        )
        .unwrap();
        let opacity = packet_opacity_masked(&r.gas, energy, masks[0], b.n_h, b.n_he).unwrap();
        assert_eq!(opacity[2], 0.0);
        assert_eq!(r.absorbed_per_h[2], 0.0);
        assert_eq!(r.endpoint.photo_events_cm3_s[2], 0.0);
        assert_eq!(r.packets[0].energy_ev.to_bits(), energy.to_bits());
        let available = packets[0].per_h + dt * source;
        let expected = available / (1.0 + dt * opacity.iter().sum::<f64>());
        assert_eq!(r.packets[0].per_h, expected);
        assert!(
            (available - r.packets[0].per_h - r.absorbed_per_h.iter().sum::<f64>()).abs()
                < 1e-10 * available
        );
        let ev_erg = HHeModel::controlled_fixture().ev_erg;
        let material = r.gas.w_erg_per_h + binding(&r.gas, b) - old.w_erg_per_h - binding(&old, b);
        let radiation = (r.packets[0].per_h - available) * energy * ev_erg;
        let reservoirs = dt / b.n_h
            * (r.endpoint.escape_erg_cm3_s - r.endpoint.cmb_to_gas_erg_cm3_s
                + r.endpoint.expansion_work_erg_cm3_s);
        assert!((material + radiation + reservoirs).abs() < 1e-10 * available * energy * ev_erg);
    }
}

#[test]
fn masked_source_step_rejects_bad_mask_shape_and_preserves_all_active_legacy() {
    let old = gas(30.0);
    let packets = [PrimaryPacket {
        energy_ev: 80.0,
        per_h: 0.001,
    }];
    for source in [0.0, 1e-14] {
        assert!(implicit_step_with_source_masked(
            &old,
            &packets,
            &[source],
            &[],
            bg(),
            1e10,
            StepControl::default()
        )
        .is_err());
        let baseline = implicit_step_with_source(
            &old,
            &packets,
            &[source],
            bg(),
            1e10,
            StepControl::default(),
        )
        .unwrap();
        let masked = implicit_step_with_source_masked(
            &old,
            &packets,
            &[source],
            &[[true; 3]],
            bg(),
            1e10,
            StepControl::default(),
        )
        .unwrap();
        assert_eq!(format!("{baseline:?}"), format!("{masked:?}"));
    }
}

#[test]
fn masked_source_step_preserves_underflow_photons_with_no_active_channels() {
    let b = StepBackground {
        hubble: 0.0,
        ..bg()
    };
    let old = IgmGasState::from_temperature([0.0; 3], b.n_h, b.n_he, 30.0).unwrap();
    let packets = [PrimaryPacket {
        energy_ev: 80.0,
        per_h: 1e-300,
    }];
    let r = implicit_step_with_source_masked(
        &old,
        &packets,
        &[0.0],
        &[[false; 3]],
        b,
        1.0,
        StepControl::default(),
    )
    .unwrap();
    assert_eq!(r.packets[0].per_h.to_bits(), packets[0].per_h.to_bits());
    assert_eq!(r.absorbed_per_h, [0.0; 3]);
    assert_eq!(r.endpoint.photo_events_cm3_s, [0.0; 3]);
    assert_eq!(r.underflow_n_bound, 0.0);
    assert_eq!(r.underflow_e_bound, 0.0);
}
