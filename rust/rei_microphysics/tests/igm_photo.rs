use rei_microphysics::{
    coupled_primary::PrimaryPacket, igm_photo::igm_photo_rates, igm_state::IgmGasState,
    igm_thermal::igm_point_rhs, HHeModel,
};
#[test]
fn all_three_absorbers_own_high_energy_and_binding_heat_closes() {
    let gas = IgmGasState::from_temperature([0.2, 0.3, 0.1], 1e-3, 8e-5, 100.0).unwrap();
    let packets = vec![PrimaryPacket {
        energy_ev: 80.0,
        per_h: 0.01,
    }];
    let p = igm_photo_rates(&gas, &packets, 1e-3, 8e-5).unwrap();
    assert!(p.owner_per_h_s.iter().all(|x| *x > 0.0));
    let rhs = igm_point_rhs(&gas, 1e-3, 8e-5, 0.0, 30.0, p.input).unwrap();
    for i in 0..3 {
        assert!(
            (rhs.photo_events_cm3_s[i] / 1e-3 - p.owner_per_h_s[i]).abs()
                < 1e-14 * p.owner_per_h_s[i]
        );
    }
    let expected =
        p.owner_per_h_s.iter().sum::<f64>() * 80.0 * HHeModel::controlled_fixture().ev_erg;
    assert!((p.absorbed_erg_per_h_s - expected).abs() < 1e-14 * expected);
    assert!((rhs.photo_input_erg_cm3_s / 1e-3 - expected).abs() < 1e-14 * expected);
}
#[test]
fn absent_helium_has_finite_per_absorber_rate_but_zero_events() {
    let gas = IgmGasState::from_temperature([0.2, 0.0, 0.0], 1e-3, 0.0, 100.0).unwrap();
    let p = igm_photo_rates(
        &gas,
        &[PrimaryPacket {
            energy_ev: 80.0,
            per_h: 0.01,
        }],
        1e-3,
        0.0,
    )
    .unwrap();
    assert!(p.input.gamma_s.iter().all(|x| *x > 0.0));
    assert_eq!(p.owner_per_h_s[1], 0.0);
    assert_eq!(p.owner_per_h_s[2], 0.0);
}
#[test]
fn empty_photons_and_zero_opacity_are_exact_boundaries() {
    let gas = IgmGasState::from_temperature([1.0, 0.0, 1.0], 1e-3, 8e-5, 100.0).unwrap();
    let empty = igm_photo_rates(&gas, &[], 1e-3, 8e-5).unwrap();
    assert_eq!(empty.input.gamma_s, [0.0; 3]);
    let p = igm_photo_rates(
        &gas,
        &[PrimaryPacket {
            energy_ev: 80.0,
            per_h: 0.01,
        }],
        1e-3,
        8e-5,
    )
    .unwrap();
    assert_eq!(p.owner_per_h_s, [0.0; 3]);
}
#[test]
fn exact_cutoffs_and_invalid_packets() {
    use rei_microphysics::{verner_cutoff_ev, Absorber};
    let gas = IgmGasState::from_temperature([0.2, 0.3, 0.1], 1e-3, 8e-5, 100.0).unwrap();
    for (i, a) in [Absorber::HI, Absorber::HeI, Absorber::HeII]
        .iter()
        .enumerate()
    {
        let e = verner_cutoff_ev(*a);
        let below = f64::from_bits(e.to_bits() - 1);
        let q = |energy_ev| {
            igm_photo_rates(
                &gas,
                &[PrimaryPacket {
                    energy_ev,
                    per_h: 0.01,
                }],
                1e-3,
                8e-5,
            )
            .unwrap()
        };
        assert_eq!(q(below).input.gamma_s[i], 0.0);
        assert!(q(e).input.gamma_s[i] > 0.0);
    }
    assert!(igm_photo_rates(
        &gas,
        &[PrimaryPacket {
            energy_ev: 80.0,
            per_h: -1.0
        }],
        1e-3,
        8e-5
    )
    .is_err());
}
#[test]
fn positive_underflow_is_explicitly_bounded_without_photon_floor() {
    let gas = IgmGasState::from_temperature([0.2, 0.3, 0.1], 1e-3, 8e-5, 100.0).unwrap();
    let p = igm_photo_rates(
        &gas,
        &[PrimaryPacket {
            energy_ev: 80.0,
            per_h: 1e-300,
        }],
        1e-3,
        8e-5,
    )
    .unwrap();
    assert!(p.underflow_energy_erg_per_h_s > 0.0);
    assert!(p.underflow_energy_erg_per_h_s < 1e-290);
    let rhs = igm_point_rhs(&gas, 1e-3, 8e-5, 0.0, 30.0, p.input).unwrap();
    assert!(rhs.photo_input_erg_cm3_s.is_finite());
}
