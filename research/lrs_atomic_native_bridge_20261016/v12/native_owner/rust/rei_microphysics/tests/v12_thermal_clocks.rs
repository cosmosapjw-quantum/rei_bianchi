use rei_microphysics::{
    axbi_driver::{Driver, DriverConfig, NativeClockMode},
    axbi_rates::AxbiProvider,
    igm_state::IgmGasState,
    igm_thermal::IgmPhotoInput,
};

const FRACTIONS: [f64; 3] = [0.075, 0.12, 0.03];
const TEMPERATURE_K: f64 = 15_000.0;

fn assert_rate_close(actual: &[f64], expected: &[f64]) {
    for (&a, &b) in actual.iter().zip(expected) {
        assert!(
            (a - b).abs() <= 1e-12 * b.abs().max(1e-100),
            "{a:e} != {b:e}"
        );
    }
}

fn source_free_step(
    mode: NativeClockMode,
) -> (
    Driver,
    rei_microphysics::axbi_driver::DriverState,
    IgmGasState,
) {
    let mut config = DriverConfig::baseline();
    config.transport_cells = 8;
    config.background_panels = 128;
    config.initial_x_hii = FRACTIONS[0];
    config.initial_temperature_k = TEMPERATURE_K;
    let (mut driver, mut state) = Driver::new(config).unwrap();
    let nh = driver.n_h0_cm3 / state.a.powi(3);
    let nhe = driver.n_he0_cm3 / state.a.powi(3);
    state.gas = IgmGasState::from_temperature(FRACTIONS, nh, nhe, TEMPERATURE_K).unwrap();
    let initial_gas = state.gas;
    driver.set_source_free_clock(&state, mode).unwrap();
    driver.fixed_step(&mut state, 1e-5 / 8.0).unwrap();
    (driver, state, initial_gas)
}

#[test]
fn source_free_clock_modes_run_the_original_fixed_step_path_and_keep_ledgers_finite() {
    for mode in [
        NativeClockMode::OwnerBe,
        NativeClockMode::CeMid,
        NativeClockMode::ChemicalMid,
        NativeClockMode::AllMid,
    ] {
        let (driver, state, _) = source_free_step(mode);
        let rhs = driver.last_clock_rhs().unwrap().unwrap();
        let (photon_count, energy) = driver.residuals(&state).unwrap();
        assert_eq!(photon_count, 0.0, "{}", mode.as_str());
        assert!(energy.abs() < 1e-10, "{} energy={energy:e}", mode.as_str());
        assert_eq!(state.ledgers.source_n, 0.0);
        assert_eq!(state.ledgers.source_u, 0.0);
        assert!(state.photons.iter().all(|&v| v == 0.0));
        assert!(state.gas.fractions[0] > 0.0 && state.gas.fractions[0] < 1.0);
        assert!(state.gas.fractions[1] >= 0.0);
        assert!(state.gas.fractions[2] >= 0.0);
        assert!(state.gas.fractions[1] + state.gas.fractions[2] <= 1.0);
        assert!(rhs
            .ci_events_cm3_s
            .iter()
            .all(|&v| v >= 0.0 && v.is_finite()));
        assert!(rhs
            .rr_events_cm3_s
            .iter()
            .all(|&v| v >= 0.0 && v.is_finite()));
        assert!(rhs.dr_events_cm3_s >= 0.0 && rhs.dr_events_cm3_s.is_finite());
        assert!(state.max_newton_residual <= 1e-11);
    }
}

#[test]
fn ce_midpoint_changes_only_the_ce_clock_while_chemical_midpoint_keeps_ce_endpoint() {
    let (be_driver, be_state, be_initial) = source_free_step(NativeClockMode::OwnerBe);
    let (ce_driver, ce_state, ce_initial) = source_free_step(NativeClockMode::CeMid);
    let (chem_driver, chem_state, chem_initial) = source_free_step(NativeClockMode::ChemicalMid);
    let be = be_driver.last_clock_rhs().unwrap().unwrap();
    let ce = ce_driver.last_clock_rhs().unwrap().unwrap();
    let chem = chem_driver.last_clock_rhs().unwrap().unwrap();
    for (driver, state, initial, observed, mode) in [
        (
            &be_driver,
            &be_state,
            be_initial,
            be,
            NativeClockMode::OwnerBe,
        ),
        (
            &ce_driver,
            &ce_state,
            ce_initial,
            ce,
            NativeClockMode::CeMid,
        ),
        (
            &chem_driver,
            &chem_state,
            chem_initial,
            chem,
            NativeClockMode::ChemicalMid,
        ),
    ] {
        let a0 = 1.0 / 21.0;
        let a1 = state.a;
        let amid = (a0 * a1).sqrt();
        let old_mid = initial.adiabatic_to(a0, amid).unwrap();
        let new_mid = state.gas.adiabatic_to(a1, amid).unwrap();
        let average = IgmGasState::new(
            std::array::from_fn(|i| 0.5 * (old_mid.fractions[i] + new_mid.fractions[i])),
            0.5 * (old_mid.w_erg_per_h + new_mid.w_erg_per_h),
        )
        .unwrap();
        let nh = driver.n_h0_cm3 / amid.powi(3);
        let nhe = driver.n_he0_cm3 / amid.powi(3);
        let endpoint = AxbiProvider
            .point(
                &new_mid,
                nh,
                nhe,
                0.0,
                2.7255 / amid,
                IgmPhotoInput::default(),
            )
            .unwrap()
            .rhs;
        let midpoint = AxbiProvider
            .point(
                &average,
                nh,
                nhe,
                0.0,
                2.7255 / amid,
                IgmPhotoInput::default(),
            )
            .unwrap()
            .rhs;
        assert_rate_close(
            &observed.ci_events_cm3_s,
            if mode == NativeClockMode::ChemicalMid {
                &midpoint.ci_events_cm3_s
            } else {
                &endpoint.ci_events_cm3_s
            },
        );
        assert_rate_close(
            &observed.rr_events_cm3_s,
            if mode == NativeClockMode::ChemicalMid {
                &midpoint.rr_events_cm3_s
            } else {
                &endpoint.rr_events_cm3_s
            },
        );
        assert_rate_close(
            &observed.ce_thermal_sink_erg_cm3_s,
            if mode == NativeClockMode::CeMid {
                &midpoint.ce_thermal_sink_erg_cm3_s
            } else {
                &endpoint.ce_thermal_sink_erg_cm3_s
            },
        );
    }
    assert_ne!(be.ce_thermal_sink_erg_cm3_s, ce.ce_thermal_sink_erg_cm3_s);
    assert_ne!(be.ci_events_cm3_s, chem.ci_events_cm3_s);
}
