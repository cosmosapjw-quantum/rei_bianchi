use bass_he_rct_step_addon::*;
use rei_microphysics::he_rct::*;
use rei_microphysics::*;
fn selected(m: &Ft03Model, offset: f64) -> RctSelection {
    RctSelection::Escaping {
        provider: RctProvider::new(
            RctSource::Kf96Nominal,
            RctScenario::W82GroundStateCommonTemperatureZeroDrift,
            true,
        )
        .unwrap(),
        closure: EscapingMeanPhotonEnergy::research_input_ev(
            m.gas.threshold_ev[2] - m.gas.threshold_ev[0] + offset,
        )
        .unwrap(),
    }
}
fn budget() -> EventControl {
    EventControl {
        absolute_per_h: 1e-14,
        relative: 2e-4,
    }
}
fn same(a: f64, b: f64, scale: f64) {
    assert!(
        (a - b).abs() <= 3e-13 * scale.max(1e-300),
        "{a:e} != {b:e}, scale {scale:e}"
    );
}
#[test]
fn off_exact_delegation() {
    let m = Ft03Model::controlled().unwrap();
    let s = m.initial_state();
    let c = StepControl::default();
    for dt in [0., 1e9] {
        let b = ft03_implicit_step(&m, &s, dt, c).unwrap();
        let r = implicit_step(&m, &s, dt, c, RctSelection::Disabled);
        assert!(r.is_ok(), "{:?}", r);
        let r = r.unwrap();
        assert_eq!(r.state, b.state);
        assert_eq!(r.iterations, b.iterations);
        assert_eq!(r.residual_norm, b.residual_norm);
        assert!(r.rct.is_none());
        let b = ft03_adaptive_step(&m, &s, dt, c).unwrap();
        let r = adaptive_step(&m, &s, dt, c, RctSelection::Disabled, budget()).unwrap();
        assert_eq!(r.state, b.state);
        assert_eq!(r.local_error, b.local_error);
    }
    let b = ft03_implicit_step(&m, &s, -1., c).unwrap_err();
    let r = implicit_step(&m, &s, -1., c, RctSelection::Disabled).unwrap_err();
    assert_eq!(r.code(), b.code());
}
#[test]
fn enabled_endpoint_uses_actual_combined_rhs() {
    let m = Ft03Model::controlled().unwrap();
    let s = m.initial_state();
    let dt = 1e10;
    for offset in [-1., 0., 1.] {
        let sel = selected(&m, offset);
        let r = implicit_step(&m, &s, dt, StepControl::default(), sel);
        assert!(r.is_ok(), "{:?}", r);
        let r = r.unwrap();
        let q = combined_ft03_rhs(&m, &r.state, sel).unwrap();
        let ev = r.rct.unwrap();
        assert!(ev.events > 0.);
        same(
            ev.events,
            dt * q.rct.unwrap().event.event_rate_cm3_s,
            ev.events,
        );
        for a in 0..3 {
            same(
                r.state.fractions[a] - s.fractions[a],
                dt * q.combined.derivative[a],
                1.,
            );
            same(
                r.baseline_events.collision_per_cm3[a],
                dt * q.baseline.collision_per_cm3_s[a],
                dt * q.baseline.collision_per_cm3_s[a],
            );
        }
        same(
            m.gas.total_energy(&r.state).unwrap(),
            m.gas.total_energy(&s).unwrap(),
            m.gas.total_energy(&s).unwrap(),
        );
        same(
            ev.chemical + ev.heat + ev.escaped,
            0.,
            ev.escaped.abs() + ev.chemical.abs(),
        );
        assert!(r.residual_norm < 1e-14);
    }
}
#[test]
fn accepted_halves_use_sum_not_last_endpoint() {
    let m = Ft03Model::controlled().unwrap();
    let s = m.initial_state();
    let c = StepControl::default();
    let sel = selected(&m, 1.);
    let dt = 1e9;
    let h1 = implicit_step(&m, &s, dt / 2., c, sel);
    assert!(h1.is_ok(), "{:?}", h1);
    let h1 = h1.unwrap();
    let h2 = implicit_step(&m, &h1.state, dt / 2., c, sel).unwrap();
    let r = adaptive_step(&m, &s, dt, c, sel, budget()).unwrap();
    assert_eq!(r.state, h2.state);
    assert_eq!(
        r.rct.unwrap().events,
        h1.rct.unwrap().events + h2.rct.unwrap().events
    );
    let last = dt
        * combined_ft03_rhs(&m, &h2.state, sel)
            .unwrap()
            .rct
            .unwrap()
            .event
            .event_rate_cm3_s;
    assert_ne!(r.rct.unwrap().events, last);
}
#[test]
fn event_budget_rejects_and_rolls_back() {
    let m = Ft03Model::controlled().unwrap();
    let mut s = m.initial_state();
    let old = s;
    let mut sum = RctIntegral::default();
    let prev = sum;
    let e = try_adaptive_step(
        &m,
        &mut s,
        &mut sum,
        1e10,
        StepControl::default(),
        selected(&m, 0.),
        EventControl {
            absolute_per_h: 1e-40,
            relative: 0.,
        },
    )
    .unwrap_err();
    assert_eq!(e.code(), "RCT_EVENT_LOCAL_ERROR");
    assert_eq!(s, old);
    assert_eq!(sum, prev);
}
#[test]
fn domain_and_nonconvergence_do_not_commit() {
    let m = Ft03Model::controlled().unwrap();
    let mut s = m.initial_state();
    let old = s;
    let mut sum = RctIntegral::default();
    let gm = RctSelection::Escaping {
        provider: RctProvider::new(
            RctSource::Gm25Constant,
            RctScenario::W82GroundStateCommonTemperatureZeroDrift,
            true,
        )
        .unwrap(),
        closure: EscapingMeanPhotonEnergy::research_input_ev(40.).unwrap(),
    };
    let e = try_adaptive_step(
        &m,
        &mut s,
        &mut sum,
        1e9,
        StepControl::default(),
        gm,
        budget(),
    )
    .unwrap_err();
    assert_eq!(e.code(), "RCT_TEMPERATURE_DOMAIN");
    assert_eq!(s, old);
    assert_eq!(sum, RctIntegral::default());
    let e = try_adaptive_step(
        &m,
        &mut s,
        &mut sum,
        1e10,
        StepControl {
            max_iterations: 1,
            residual_tolerance: 1e-14,
        },
        selected(&m, 0.),
        budget(),
    )
    .unwrap_err();
    assert_eq!(e.code(), "RCT_NONCONVERGENCE");
    assert_eq!(s, old);
    assert_eq!(sum, RctIntegral::default());
}
#[test]
fn strict_product_boundary_distinguishes_absent_and_underflow() {
    let mut m = Ft03Model::controlled().unwrap();
    let mut s = m.initial_state();
    let sel = selected(&m, 0.);
    let (p, e) = match sel {
        RctSelection::Escaping { provider, closure } => (provider, closure),
        _ => unreachable!(),
    };
    s.fractions = [1., 0., 1.];
    s.u_erg_cm3 = 1.5
        * m.gas.kb_erg_k
        * 50000.
        * (m.gas.n_h_cm3 + m.gas.n_he_cm3 + m.gas.electron_density(&s).unwrap());
    let out = checked_rct_events(&m, &s, p, e);
    assert!(out.is_ok(), "{:?}", out);
    assert_eq!(out.unwrap().event.event_rate_cm3_s, 0.);
    m.gas.n_h_cm3 = 1e-180;
    m.gas.n_he_cm3 = 8.3e-182;
    s.fractions = [0.9, 0.3, 0.6];
    s.photon_cm3 = [0.; 3];
    s.u_erg_cm3 = 1.5
        * m.gas.kb_erg_k
        * 50000.
        * (m.gas.n_h_cm3 + m.gas.n_he_cm3 + m.gas.electron_density(&s).unwrap());
    assert_eq!(
        checked_rct_events(&m, &s, p, e).unwrap_err().code(),
        "RCT_PRODUCT_UNDERFLOW"
    );
}
#[test]
fn successful_transaction_commits_both() {
    let m = Ft03Model::controlled().unwrap();
    let mut s = m.initial_state();
    let mut sum = RctIntegral::default();
    let result = try_adaptive_step(
        &m,
        &mut s,
        &mut sum,
        1e9,
        StepControl::default(),
        selected(&m, 0.),
        budget(),
    );
    assert!(result.is_ok(), "{:?}", result);
    let r = result.unwrap();
    assert_eq!(r.state, s);
    assert_eq!(sum, r.rct.unwrap());
    assert!(sum.events > 0.);
}
#[test]
fn bad_event_control_explicitly_rejected() {
    let m = Ft03Model::controlled().unwrap();
    let s = m.initial_state();
    let e = adaptive_step(
        &m,
        &s,
        1e9,
        StepControl::default(),
        selected(&m, 0.),
        EventControl {
            absolute_per_h: 0.,
            relative: 0.,
        },
    )
    .unwrap_err();
    assert_eq!(e.code(), "RCT_EVENT_CONTROL");
}
#[test]
fn default_event_budget_rejects_state_admissible_large_step() {
    let m = Ft03Model::controlled().unwrap();
    let s = m.initial_state();
    let c = StepControl::default();
    let sel = selected(&m, 0.);
    let dt = 1e10;
    let full = implicit_step(&m, &s, dt, c, sel).unwrap();
    let a = implicit_step(&m, &s, dt / 2., c, sel).unwrap();
    let b = implicit_step(&m, &a.state, dt / 2., c, sel).unwrap();
    let mut state_error = (m.gas.temperature(&full.state).unwrap().ln()
        - m.gas.temperature(&b.state).unwrap().ln())
    .abs();
    for j in 0..3 {
        state_error = state_error.max((full.state.fractions[j] - b.state.fractions[j]).abs());
    }
    assert!(state_error < 2e-4);
    assert_eq!(
        adaptive_step(&m, &s, dt, c, sel, budget())
            .unwrap_err()
            .code(),
        "RCT_EVENT_LOCAL_ERROR"
    );
}
#[test]
fn zero_step_has_no_events_and_bad_dt_is_rejected() {
    let m = Ft03Model::controlled().unwrap();
    let s = m.initial_state();
    let sel = selected(&m, 0.);
    let r = implicit_step(&m, &s, 0., StepControl::default(), sel).unwrap();
    assert_eq!(r.state, s);
    assert_eq!(r.rct, Some(RctIntegral::default()));
    for dt in [-1., f64::NAN, f64::INFINITY] {
        assert_eq!(
            implicit_step(&m, &s, dt, StepControl::default(), sel)
                .unwrap_err()
                .code(),
            "RCT_STEP_CONTROL"
        );
    }
}
#[test]
fn invalid_accumulator_is_transactional() {
    let m = Ft03Model::controlled().unwrap();
    let mut s = m.initial_state();
    let prev = s;
    let mut sum = RctIntegral {
        events: f64::INFINITY,
        ..RctIntegral::default()
    };
    let e = try_adaptive_step(
        &m,
        &mut s,
        &mut sum,
        1e9,
        StepControl::default(),
        selected(&m, 0.),
        budget(),
    )
    .unwrap_err();
    assert_eq!(e.code(), "RCT_ACCUMULATOR_DOMAIN");
    assert_eq!(s, prev);
    assert!(sum.events.is_infinite());
}
#[test]
fn out_of_domain_temperature_does_not_commit() {
    let m = Ft03Model::controlled().unwrap();
    let mut s = m.initial_state();
    s.u_erg_cm3 *= 0.1;
    let prev = s;
    let mut sum = RctIntegral::default();
    assert_eq!(
        try_adaptive_step(
            &m,
            &mut s,
            &mut sum,
            1e9,
            StepControl::default(),
            selected(&m, 0.),
            budget()
        )
        .unwrap_err()
        .code(),
        "FT03_TEMPERATURE_DOMAIN"
    );
    assert_eq!(s, prev);
    assert_eq!(sum, RctIntegral::default());
}
#[test]
fn fractional_boundaries_and_dark_photons_remain_valid() {
    let m = Ft03Model::controlled().unwrap();
    for frac in [[0., 0., 0.], [1., 0., 1.], [0.5, 1., 0.], [0.9, 0.3, 0.6]] {
        let mut s = m.initial_state();
        s.fractions = frac;
        s.photon_cm3 = [0.; 3];
        s.u_erg_cm3 = 1.5
            * m.gas.kb_erg_k
            * 50000.
            * (m.gas.n_h_cm3 + m.gas.n_he_cm3 + m.gas.electron_density(&s).unwrap());
        let r = implicit_step(&m, &s, 1e8, StepControl::default(), selected(&m, 0.)).unwrap();
        assert!((0.0..=1.0).contains(&r.state.fractions[0]));
        assert!(
            r.state.fractions[1] >= 0.
                && r.state.fractions[2] >= 0.
                && r.state.fractions[1] + r.state.fractions[2] <= 1.
        );
        assert_eq!(r.state.photon_cm3, [0.; 3]);
    }
}
