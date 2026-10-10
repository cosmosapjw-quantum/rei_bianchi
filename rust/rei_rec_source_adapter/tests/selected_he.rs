use rec_microphysics::frame::MaterialVelocity;
use rec_microphysics::ledger::{assemble_he_event_ledger, ChannelRates, HeEnergies};
use rei_microphysics::IsotopeSpecies;
use rei_rec_source_adapter::{project_selected_he4_non_tilted, SourceConvention};

fn rates(column: usize, sign: f64) -> ChannelRates {
    let mut r = ChannelRates {
        r584: 0.,
        rir: 0.,
        rp: 0.,
        rs: 0.,
        r2g: 0.,
    };
    match column {
        0 => r.r584 = sign,
        1 => r.rir = sign,
        2 => r.rp = sign,
        3 => r.rs = sign,
        4 => r.r2g = sign,
        _ => unreachable!(),
    }
    r
}

#[test]
fn projects_all_signed_basis_channels_without_reinterpreting_energy() {
    for column in 0..5 {
        for sign in [-1., 1.] {
            let energies = HeEnergies::canonical_si();
            let bf_photon_power = match column {
                2 => sign * energies.chi_p,
                3 => sign * energies.chi_s,
                _ => 0.,
            };
            let ledger =
                assemble_he_event_ledger(rates(column, sign), energies, bf_photon_power, 0.)
                    .unwrap();
            let out = project_selected_he4_non_tilted(
                &ledger,
                SourceConvention::SelectedHe4ProperSiGasSeconds,
            )
            .unwrap();
            assert_eq!(
                out.species_dot_m3_s[IsotopeSpecies::He4Neutral as usize],
                ledger.species_source[0] + ledger.species_source[1] + ledger.species_source[2]
            );
            assert_eq!(
                out.species_dot_m3_s[IsotopeSpecies::He4SinglyIonized as usize],
                ledger.species_source[3]
            );
            assert_eq!(out.electron_dot_m3_s, ledger.species_source[4]);
            assert_eq!(out.photon_number_dot_m3_s, ledger.photon_number_source);
            assert_eq!(out.photon_power_j_m3_s, ledger.p_gamma);
            assert!(out.species_dot_m3_s.iter().enumerate().all(|(i, x)| {
                i == IsotopeSpecies::He4Neutral as usize
                    || i == IsotopeSpecies::He4SinglyIonized as usize
                    || *x == 0.
            }));
        }
    }
}

#[test]
fn rejects_nonconservative_or_nonfinite_ledgers() {
    let mut ledger =
        assemble_he_event_ledger(rates(4, 1.), HeEnergies::canonical_si(), 0., 0.).unwrap();
    ledger.he_nuclei_residual = 1.;
    assert!(project_selected_he4_non_tilted(
        &ledger,
        SourceConvention::SelectedHe4ProperSiGasSeconds
    )
    .is_err());
    ledger.he_nuclei_residual = 0.;
    ledger.p_gamma = f64::NAN;
    assert!(project_selected_he4_non_tilted(
        &ledger,
        SourceConvention::SelectedHe4ProperSiGasSeconds
    )
    .is_err());
    for rate in [1., 1e-20] {
        let unclosed =
            assemble_he_event_ledger(rates(2, rate), HeEnergies::canonical_si(), 0., 0.).unwrap();
        assert!(project_selected_he4_non_tilted(
            &unclosed,
            SourceConvention::SelectedHe4ProperSiGasSeconds
        )
        .is_err());
    }
}

#[test]
fn recomputes_current_closure_instead_of_trusting_cached_residuals() {
    let baseline =
        assemble_he_event_ledger(rates(4, 1.), HeEnergies::canonical_si(), 0., 0.).unwrap();

    let mut stale_nuclei = baseline;
    stale_nuclei.species_source[0] += 1.;
    assert_eq!(stale_nuclei.he_nuclei_residual, baseline.he_nuclei_residual);
    assert!(
        project_selected_he4_non_tilted(
            &stale_nuclei,
            SourceConvention::SelectedHe4ProperSiGasSeconds
        )
        .is_err()
    );

    let mut stale_charge = baseline;
    stale_charge.species_source[4] += 1.;
    assert_eq!(
        stale_charge.charge_minus_e_residual,
        baseline.charge_minus_e_residual
    );
    assert!(
        project_selected_he4_non_tilted(
            &stale_charge,
            SourceConvention::SelectedHe4ProperSiGasSeconds
        )
        .is_err()
    );

    let mut stale_energy = baseline;
    stale_energy.p_internal += 1.;
    assert_eq!(stale_energy.energy_residual, baseline.energy_residual);
    assert!(
        project_selected_he4_non_tilted(
            &stale_energy,
            SourceConvention::SelectedHe4ProperSiGasSeconds
        )
        .is_err()
    );
}

#[test]
fn declared_zero_tilt_preserves_the_rec_scalar_clock() {
    let velocity = MaterialVelocity::new([0.; 3]).unwrap();
    assert_eq!(velocity.gamma(), 1.);
    assert_eq!(velocity.scalar_source_normal_time(7., 0., 3.).unwrap(), 7.);
}
