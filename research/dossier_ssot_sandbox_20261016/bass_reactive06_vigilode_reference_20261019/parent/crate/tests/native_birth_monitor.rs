//! Direct physics parity and monitor-specific failure/identity verification.
mod bass_common;

use bass_common::common::bit_parity;
use rei_iso_couple_reference::{
    ap_midpoint::{ApMidpointBridge, BirthMode},
    fitted_birth,
    full_network::NetworkError,
    mixture_coupling::CoupleError,
    monitored_midpoint::MonitoredMidpointBridge,
    native_birth_monitor::{
        MonitorControls, MonitorError, MonitorMode, population_moments, rule_panels,
    },
    native_monitor_csv::MonitorCsv,
};

fn fixture(
    case: &str,
    mode: BirthMode,
) -> (
    MonitoredMidpointBridge,
    rei_iso_couple_reference::full_network::NetworkConfig,
    rei_iso_couple_reference::full_network::FullState,
) {
    let (b, c, g) = bass_common::fixture(case, 121, 0.0, false, 8192);
    (
        MonitoredMidpointBridge::from_parent(ApMidpointBridge::from_original(b, mode)),
        c,
        g,
    )
}

#[test]
fn off_direct_dispatch_preserves_parent_fitted_and_legacy_bits() {
    for case in ["SIGNED_MINUS", "SIGNED_PLUS"] {
        for mode in [BirthMode::Off, BirthMode::Fitted { refinement: 2 }] {
            let (b, c, g) = fixture(case, mode);
            let state = b.initial(g, &c, 0.0).unwrap();
            let (parent, parent_diag) = b
                .parent()
                .advance_with_diagnostics(&state, &c, 1e9)
                .unwrap();
            let observed = b
                .advance_with_monitor(&state, &c, 1e9, MonitorMode::Off)
                .unwrap();
            bit_parity(&parent, &observed.step);
            assert_eq!(
                format!("{parent_diag:?}"),
                format!("{:?}", observed.diagnostics)
            );
            assert!(observed.monitor.is_none());
        }
    }
}

#[test]
fn actual_corrector_capture_keeps_every_physics_bit_and_append_identity() {
    for case in ["SIGNED_MINUS", "SIGNED_PLUS"] {
        let (b, c, g) = fixture(case, BirthMode::Fitted { refinement: 2 });
        let mut state = b.initial(g, &c, 0.0).unwrap();
        for step_id in 1..=2 {
            let before = format!("{state:?}");
            let (parent, parent_diag) = b
                .parent()
                .advance_with_diagnostics(&state, &c, 1e10)
                .unwrap();
            let out = b
                .advance_with_monitor(
                    &state,
                    &c,
                    1e10,
                    MonitorMode::On(MonitorControls {
                        step_id,
                        ..MonitorControls::default()
                    }),
                )
                .unwrap();
            bit_parity(&parent, &out.step);
            assert_eq!(format!("{parent_diag:?}"), format!("{:?}", out.diagnostics));
            assert_eq!(before, format!("{state:?}"));
            let captured = out.monitor.unwrap().unwrap();
            assert_eq!(captured.step_id, step_id);
            assert_eq!(captured.dt.to_bits(), 1e10_f64.to_bits());
            assert_eq!(captured.t0.to_bits(), state.time_s.to_bits());
            assert_eq!(captured.prior_cohorts, state.cohorts.len());
            assert_eq!(
                captured.births.len() + state.cohorts.len(),
                out.step.state.cohorts.len()
            );
            let birth_sum: f64 = captured.births.iter().map(|r| r.birth.n_comoving_m3).sum();
            assert_eq!(birth_sum.to_bits(), out.step.source_birth_com3.to_bits());
            // Actual midpoint evaluation gas is separately captured, not an
            // arbitrary accepted endpoint state supplied to a frozen oracle.
            assert_ne!(
                format!("{:?}", captured.rate_gas),
                format!("{:?}", out.step.state.full.gas)
            );
            for rule in &captured.rules {
                let rates = b
                    .parent()
                    .opacity_channels(rule.energy_ev, &captured.rate_gas, &c)
                    .unwrap();
                assert_eq!(rates.map(f64::to_bits), rule.rates_per_s.map(f64::to_bits));
                assert_eq!(
                    (rates.iter().sum::<f64>() * captured.dt).to_bits(),
                    rule.tau.to_bits()
                );
                assert!(rule.panels.iter().all(|p| p.width_bits_match));
            }
            for record in &captured.births {
                let actual = &out.step.state.cohorts[record.cohort_index];
                assert_eq!(
                    actual.n_comoving_m3.to_bits(),
                    record.accepted_com3.unwrap().to_bits()
                );
                assert_eq!(
                    record.after_photo_com3.map(f64::to_bits),
                    record.accepted_com3.map(f64::to_bits)
                );
                assert_eq!(
                    actual.birth_time_s.to_bits(),
                    record.birth.birth_time_s.to_bits()
                );
                let energy = record
                    .killing_ev_scale
                    .iter()
                    .zip(captured.end_geometry.scale_factors)
                    .map(|(k, a)| (k / a).powi(2))
                    .sum::<f64>()
                    .sqrt();
                assert!((energy / record.end_energy_ev.unwrap() - 1.0).abs() < 1e-13);
                assert!(record.clock_age_defect.abs() < 1e-14);
            }
            let accepted = captured.accepted.unwrap();
            assert!(
                accepted
                    .populations_m3
                    .iter()
                    .all(|v| v.is_finite() && *v >= 0.0)
            );
            assert_eq!(
                accepted.photons.positive_cohorts + accepted.photons.zero_cohorts,
                out.step.state.cohorts.len()
            );
            state = out.step.state;
        }
    }
}

#[test]
fn monitoring_quota_and_invalid_controls_do_not_reject_physics() {
    let (b, c, g) = fixture("SIGNED_MINUS", BirthMode::Fitted { refinement: 1 });
    let state = b.initial(g, &c, 0.0).unwrap();
    let parent = b.parent().advance(&state, &c, 1e9).unwrap();
    for controls in [
        MonitorControls {
            max_newborn_records: 0,
            ..MonitorControls::default()
        },
        MonitorControls {
            step_id: 0,
            ..MonitorControls::default()
        },
    ] {
        let out = b
            .advance_with_monitor(&state, &c, 1e9, MonitorMode::On(controls))
            .unwrap();
        bit_parity(&parent, &out.step);
        let err = out.monitor.unwrap().unwrap_err();
        if controls.step_id == 0 {
            assert_eq!(err, MonitorError::InvalidControls);
        } else {
            assert!(matches!(err, MonitorError::RecordQuota { limit: 0, .. }));
        }
    }
}

#[test]
fn legacy_monitor_unsupported_is_separate_from_parent_physics() {
    let (b, c, g) = fixture("SIGNED_MINUS", BirthMode::Off);
    let state = b.initial(g, &c, 0.0).unwrap();
    let parent = b.parent().advance(&state, &c, 1e9).unwrap();
    let out = b
        .advance_with_monitor(&state, &c, 1e9, MonitorMode::On(MonitorControls::default()))
        .unwrap();
    bit_parity(&parent, &out.step);
    assert_eq!(
        out.monitor.unwrap().unwrap_err(),
        MonitorError::UnsupportedBirthMode
    );
}

#[test]
fn solver_worklimit_and_negative_population_keep_original_classification() {
    let (b, mut c, g) = fixture("SIGNED_MINUS", BirthMode::Fitted { refinement: 1 });
    let state = b.initial(g, &c, 0.0).unwrap();
    c.cx_controls.max_rate_calls = 1;
    let saved = format!("{state:?}");
    let err = b
        .advance_with_monitor(
            &state,
            &c,
            1e10,
            MonitorMode::On(MonitorControls::default()),
        )
        .unwrap_err();
    assert_eq!(err, NetworkError::Cx(CoupleError::WorkLimit));
    assert_eq!(saved, format!("{state:?}"));
    let (b, c, g) = fixture("SIGNED_MINUS", BirthMode::Fitted { refinement: 1 });
    let mut state = b.initial(g, &c, 0.0).unwrap();
    let mut co = b.0.source_births(0.0, 1.0).unwrap().remove(0);
    co.n_comoving_m3 = -1.0;
    state.cohorts.push(co);
    let saved = format!("{state:?}");
    assert_eq!(
        b.advance_with_monitor(&state, &c, 1e9, MonitorMode::On(MonitorControls::default()))
            .unwrap_err(),
        NetworkError::NegativePopulation
    );
    assert_eq!(saved, format!("{state:?}"));
}

#[test]
fn panel_geometry_preserves_zero_opacity_thick_widths_and_clock_rounding() {
    for tau in [0.0, 1e-12, 1.0, 93.0, 1e12] {
        for refinement in [1, 4, 16] {
            let nodes = fitted_birth::rule(tau, refinement).unwrap();
            let panels = rule_panels(tau, refinement, &nodes, 1e15, 1e9).unwrap();
            assert_eq!(panels.len() * 2, nodes.len());
            assert_eq!(panels.first().unwrap().left, 0.0);
            assert_eq!(panels.last().unwrap().right, 1.0);
            for panel in panels {
                assert!(panel.width_bits_match);
                assert!(panel.nominal_width_s <= (1e9 / refinement as f64) * (1.0 + 2e-14));
                assert!(panel.optical_bound_excess <= 1e-13 * (1.0 + panel.optical_width));
                assert!(panel.represented_width_s >= 0.0);
                assert_eq!(
                    (panel.represented_width_s - panel.nominal_width_s).to_bits(),
                    panel.represented_width_defect_s.to_bits()
                );
                assert!(panel.local_reference.survivors.shape.is_some());
            }
        }
    }
}

#[test]
fn altered_weights_and_incomplete_panel_cover_are_rejected() {
    let mut nodes = fitted_birth::rule(93.0, 2).unwrap();
    nodes[0].1 *= 1.001;
    assert!(rule_panels(93.0, 2, &nodes, 0.0, 1.0).is_err());
    let nodes = fitted_birth::rule(93.0, 2).unwrap();
    assert!(rule_panels(93.0, 2, &nodes[..nodes.len() - 2], 0.0, 1.0).is_err());
    assert!(rule_panels(f64::NAN, 2, &nodes, 0.0, 1.0).is_err());
}

#[test]
fn empty_zero_subnormal_and_invalid_native_measures_are_explicit() {
    let empty = population_moments([]).unwrap();
    assert_eq!(empty.count, 0.0);
    assert_eq!(empty.positive_cohorts, 0);
    let zero = population_moments([(0.0, 1.0), (0.0, 2.0)]).unwrap();
    assert_eq!(zero.zero_cohorts, 2);
    assert_eq!(zero.age_sum_s, 0.0);
    let tiny = population_moments([(f64::from_bits(1), 1.0)]).unwrap();
    assert_eq!(tiny.count.to_bits(), 1);
    assert_eq!(tiny.positive_cohorts, 1);
    let underflow = population_moments([(f64::from_bits(1), 0.25)]).unwrap();
    assert_eq!(underflow.first_moment_underflows, 1);
    assert_eq!(underflow.second_moment_underflows, 1);
    assert_eq!(
        population_moments([(-1.0, 1.0)]).unwrap_err(),
        MonitorError::NegativePopulation
    );
    assert!(population_moments([(1.0, f64::NAN)]).is_err());
    assert!(population_moments([(1.0, -1.0)]).is_err());
    assert!(population_moments([(f64::MAX, f64::MAX)]).is_err());
}

#[test]
fn accepted_export_streams_joinable_rows_and_refuses_overwrite() {
    let (b, c, g) = fixture("SIGNED_MINUS", BirthMode::Fitted { refinement: 1 });
    let state = b.initial(g, &c, 0.0).unwrap();
    let out = b
        .advance_with_monitor(&state, &c, 1e9, MonitorMode::On(MonitorControls::default()))
        .unwrap();
    let data = out.monitor.unwrap().unwrap();
    let unique = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    let dir =
        std::env::temp_dir().join(format!("br05-monitor-test-{}-{unique}", std::process::id()));
    let mut writer = MonitorCsv::create(&dir).unwrap();
    writer.write_step(&data).unwrap();
    writer
        .write_final(&out.step.state, &data.end_geometry)
        .unwrap();
    assert_eq!(writer.steps_written, 1);
    assert_eq!(writer.births_written, out.step.state.cohorts.len());
    assert!(MonitorCsv::create(&dir).is_err());
    for name in [
        "MONITOR_STEPS.csv",
        "MONITOR_RULES.csv",
        "MONITOR_PANELS.csv",
        "MONITOR_TEMPLATES.csv",
        "MONITOR_BIRTHS.csv",
        "MONITOR_FINAL_COHORTS.csv",
    ] {
        let csv = std::fs::read_to_string(dir.join(name)).unwrap();
        let columns = csv.lines().next().unwrap().split(',').count();
        assert!(
            csv.lines()
                .skip(1)
                .all(|line| line.split(',').count() == columns)
        );
        assert!(!csv.contains("NaN"));
    }
    drop(writer);
    std::fs::remove_dir_all(dir).unwrap();
}
