use rei_microphysics::he_rct::{
    combined_ft03_rhs, EscapingMeanPhotonEnergy, RctProvider, RctScenario, RctSelection, RctSource,
};
use rei_microphysics::{
    ft03_adaptive_step, ft03_adaptive_step_with_rct, ft03_implicit_step,
    ft03_implicit_step_with_rct, ft03_try_step_with_rct, Ft03Model, Ft03RctLedger, StepControl,
};

fn control() -> StepControl {
    StepControl {
        max_iterations: 128,
        residual_tolerance: 1e-12,
    }
}

fn selected(mean_ev: f64) -> RctSelection {
    RctSelection::Escaping {
        provider: RctProvider::new(
            RctSource::Kf96Nominal,
            RctScenario::W82GroundStateCommonTemperatureZeroDrift,
            true,
        )
        .unwrap(),
        closure: EscapingMeanPhotonEnergy::research_input_ev(mean_ev).unwrap(),
    }
}

fn same_state_bits(a: &rei_microphysics::HHeState, b: &rei_microphysics::HHeState) {
    for (x, y) in a.coordinates().iter().zip(b.coordinates()) {
        assert_eq!(x.to_bits(), y.to_bits());
    }
    assert_eq!(a.escaped_erg_cm3.to_bits(), b.escaped_erg_cm3.to_bits());
}

#[test]
fn synthetic_q_minus_zero_plus_and_actual_ft03_rhs() {
    let model = Ft03Model::controlled().unwrap();
    let old = model.initial_state();
    let q = model.gas.threshold_ev[2] - model.gas.threshold_ev[0];
    assert!((q - 40.819325400298).abs() < 1e-10);
    let means = [q - 1.0, q, q + 1.0];
    println!(
        "fixture Q_bits={:016x} means_bits={:016x},{:016x},{:016x}",
        q.to_bits(),
        means[0].to_bits(),
        means[1].to_bits(),
        means[2].to_bits()
    );
    for (idx, mean) in means.into_iter().enumerate() {
        let out = combined_ft03_rhs(&model, &old, selected(mean)).unwrap();
        let ledger = out.rct.unwrap();
        assert!(!ledger.physical_closure_admission);
        assert_eq!(
            ledger.closure_input_origin,
            "CALLER_SUPPLIED_NO_ATOMIC_MOMENT"
        );
        assert!(ledger.event.event_rate_cm3_s > 0.0);
        assert_eq!(ledger.tracked_photon_rate_cm3_s, [0.0; 3]);
        assert_eq!(out.baseline.photo_per_cm3_s, out.combined.photo_per_cm3_s);
        assert_eq!(
            out.baseline.collision_per_cm3_s,
            out.combined.collision_per_cm3_s
        );
        assert_eq!(
            out.baseline.recombination_per_cm3_s,
            out.combined.recombination_per_cm3_s
        );
        assert_eq!(out.baseline.dr_per_cm3_s, out.combined.dr_per_cm3_s);
        let heat = ledger.thermal_energy_rate_erg_cm3_s;
        if idx == 0 {
            assert!(heat > 0.0);
        }
        if idx == 1 {
            assert_eq!(heat.to_bits(), 0.0f64.to_bits());
        }
        if idx == 2 {
            assert!(heat < 0.0);
        }
        let d = out.combined.derivative;
        let g = &model.gas;
        let chemical = g.ev_erg
            * (g.n_h_cm3 * d[0] * g.threshold_ev[0]
                + g.n_he_cm3
                    * (d[1] * g.threshold_ev[1] + d[2] * (g.threshold_ev[1] + g.threshold_ev[2])));
        let photons = g.ev_erg
            * (0..3)
                .map(|k| g.photon_energy_ev[k] * d[4 + k])
                .sum::<f64>();
        let gross =
            chemical.abs() + photons.abs() + d[3].abs() + out.combined.escaped_energy_rate.abs();
        let residual = chemical + photons + d[3] + out.combined.escaped_energy_rate;
        assert!(residual.abs() <= 2e-12 * gross);
    }
}

#[test]
fn disabled_step_is_bit_identical_to_original_ft03() {
    let model = Ft03Model::controlled().unwrap();
    let old = model.initial_state();
    let ordinary = ft03_implicit_step(&model, &old, 1e4, control()).unwrap();
    let conditional =
        ft03_implicit_step_with_rct(&model, &old, 1e4, control(), RctSelection::Disabled).unwrap();
    same_state_bits(&ordinary.state, &conditional.step.state);
    assert_eq!(
        ordinary.events.photo_per_cm3,
        conditional.step.events.photo_per_cm3
    );
    assert_eq!(
        ordinary.events.collision_per_cm3,
        conditional.step.events.collision_per_cm3
    );
    assert_eq!(
        ordinary.events.recombination_per_cm3,
        conditional.step.events.recombination_per_cm3
    );
    assert_eq!(
        ordinary.events.dr_per_cm3,
        conditional.step.events.dr_per_cm3
    );
    assert_eq!(
        ordinary.residual_norm.to_bits(),
        conditional.step.residual_norm.to_bits()
    );
    assert_eq!(conditional.rct, Ft03RctLedger::default());
    let ordinary = ft03_adaptive_step(&model, &old, 1e4, control()).unwrap();
    let conditional =
        ft03_adaptive_step_with_rct(&model, &old, 1e4, control(), RctSelection::Disabled).unwrap();
    same_state_bits(&ordinary.state, &conditional.step.state);
    assert_eq!(
        ordinary.events.photo_per_cm3,
        conditional.step.events.photo_per_cm3
    );
    assert_eq!(
        ordinary.events.collision_per_cm3,
        conditional.step.events.collision_per_cm3
    );
    assert_eq!(
        ordinary.events.recombination_per_cm3,
        conditional.step.events.recombination_per_cm3
    );
    assert_eq!(
        ordinary.events.dr_per_cm3,
        conditional.step.events.dr_per_cm3
    );
    assert_eq!(
        ordinary.local_error.to_bits(),
        conditional.step.local_error.to_bits()
    );
    assert_eq!(conditional.rct, Ft03RctLedger::default());
}

#[test]
fn selected_endpoint_rate_residual_and_ledger() {
    let model = Ft03Model::controlled().unwrap();
    let old = model.initial_state();
    let q = model.gas.threshold_ev[2] - model.gas.threshold_ev[0];
    let dt = 1e8;
    let out = ft03_implicit_step_with_rct(&model, &old, dt, control(), selected(q + 1.0)).unwrap();
    assert!(out.step.residual_norm < control().residual_tolerance);
    assert!(out.rct.events_per_cm3 > 0.0);
    assert_eq!(
        out.rct.events_per_cm3.to_bits(),
        out.rct.escaped_photons_per_cm3.to_bits()
    );
    let endpoint = combined_ft03_rhs(&model, &out.step.state, selected(q + 1.0)).unwrap();
    let event_rate = endpoint.rct.unwrap().event.event_rate_cm3_s;
    assert!(
        (out.rct.events_per_cm3 - dt * event_rate).abs()
            <= 8.0 * f64::EPSILON * (dt * event_rate).abs()
    );
    let before = old.coordinates();
    let after = out.step.state.coordinates();
    let scale = [
        1.0,
        1.0,
        1.0,
        old.u_erg_cm3,
        old.photon_cm3[0],
        old.photon_cm3[1],
        old.photon_cm3[2],
    ];
    for k in 0..7 {
        assert!(
            (after[k] - before[k] - dt * endpoint.combined.derivative[k]).abs() / scale[k]
                < control().residual_tolerance
        );
    }
    let energy0 = model.gas.total_energy(&old).unwrap();
    let energy1 = model.gas.total_energy(&out.step.state).unwrap();
    assert!(((energy1 - energy0) / energy0).abs() <= 8e-12);
}

#[test]
fn adaptive_accepts_only_two_half_ledgers() {
    let model = Ft03Model::controlled().unwrap();
    let old = model.initial_state();
    let q = model.gas.threshold_ev[2] - model.gas.threshold_ev[0];
    let choice = selected(q - 1.0);
    let dt = 1e8;
    let half1 = ft03_implicit_step_with_rct(&model, &old, dt / 2.0, control(), choice).unwrap();
    let half2 = ft03_implicit_step_with_rct(&model, &half1.step.state, dt / 2.0, control(), choice)
        .unwrap();
    let full = ft03_implicit_step_with_rct(&model, &old, dt, control(), choice).unwrap();
    let accepted = ft03_adaptive_step_with_rct(&model, &old, dt, control(), choice).unwrap();
    assert!(accepted.step.local_error < 2e-4);
    same_state_bits(&accepted.step.state, &half2.step.state);
    assert_eq!(
        accepted.rct.events_per_cm3.to_bits(),
        (half1.rct.events_per_cm3 + half2.rct.events_per_cm3).to_bits()
    );
    assert_eq!(
        accepted.rct.escaped_photons_per_cm3.to_bits(),
        (half1.rct.escaped_photons_per_cm3 + half2.rct.escaped_photons_per_cm3).to_bits()
    );
    assert_eq!(
        accepted.rct.escaped_energy_erg_cm3.to_bits(),
        (half1.rct.escaped_energy_erg_cm3 + half2.rct.escaped_energy_erg_cm3).to_bits()
    );
    assert!(accepted.rct.events_per_cm3 < accepted.rct.events_per_cm3 + full.rct.events_per_cm3);
}

#[test]
fn zero_inputs_domain_underflow_and_rejected_trial_rollback() {
    let model = Ft03Model::controlled().unwrap();
    let old = model.initial_state();
    let q = model.gas.threshold_ev[2] - model.gas.threshold_ev[0];
    let zero = ft03_implicit_step_with_rct(&model, &old, 0.0, control(), selected(q)).unwrap();
    same_state_bits(&old, &zero.step.state);
    assert_eq!(zero.rct, Ft03RctLedger::default());
    let mut no_heiii = old;
    no_heiii.fractions[2] = 0.0;
    let rhs = combined_ft03_rhs(&model, &no_heiii, selected(q)).unwrap();
    assert_eq!(rhs.rct.unwrap().event.event_rate_cm3_s, 0.0);
    let gm25 = RctSelection::Escaping {
        provider: RctProvider::new(
            RctSource::Gm25Constant,
            RctScenario::W82GroundStateCommonTemperatureZeroDrift,
            true,
        )
        .unwrap(),
        closure: EscapingMeanPhotonEnergy::research_input_ev(q).unwrap(),
    };
    assert_eq!(
        ft03_implicit_step_with_rct(&model, &old, 1.0, control(), gm25)
            .unwrap_err()
            .code(),
        "RCT_TEMPERATURE_DOMAIN"
    );
    assert_eq!(
        ft03_implicit_step_with_rct(&model, &old, f64::from_bits(1), control(), selected(q))
            .unwrap_err()
            .code(),
        "FT03_PRODUCT_UNDERFLOW"
    );
    let mut state = old;
    let mut ledger = Ft03RctLedger {
        events_per_cm3: 1.0,
        escaped_photons_per_cm3: 1.0,
        escaped_energy_erg_cm3: 2.0,
    };
    let prior = ledger;
    let bad = StepControl {
        max_iterations: 0,
        residual_tolerance: 1e-12,
    };
    assert_eq!(
        ft03_try_step_with_rct(&model, &mut state, &mut ledger, 1e4, bad, selected(q))
            .unwrap_err()
            .code(),
        "FT03_STEP_CONTROL"
    );
    same_state_bits(&state, &old);
    assert_eq!(ledger, prior);
}
