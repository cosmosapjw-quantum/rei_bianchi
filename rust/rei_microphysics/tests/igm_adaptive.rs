use rei_microphysics::igm_adaptive::{AdaptiveControl, AdaptiveIntegrator, AdaptiveState};
use rei_microphysics::{igm_config::parse_config, igm_continuous::ContinuousHistory};
const CFG: &str = include_str!("../../../configs/igm_manufactured_v1.cfg");

// Recorded RED against the old acceptance seam before introducing this API.
#[test]
fn error_control_rejects_a_conservative_but_inaccurate_neutral_step() {
    let mut c = parse_config(CFG).unwrap();
    c.source.photons_per_h_per_s = 0.0;
    c.fractions = [0.0; 3];
    c.max_dln_a = 0.002;
    let (h, s) = ContinuousHistory::new(c, 1).unwrap();
    let end = s.ln_a + 0.002;
    let control = AdaptiveControl {
        relative: 1e-8,
        ..Default::default()
    };
    let integrator = AdaptiveIntegrator::new(h, control).unwrap();
    let result = integrator
        .advance_one(&AdaptiveState::new(s.clone()), end)
        .unwrap();
    let q = result.state;
    let exact = s.gas.w_erg_per_h * (-2.0 * (q.ln_a - s.ln_a)).exp();
    assert!(
        q.rejected_steps > 0,
        "a conservative step needs LTE rejection before acceptance"
    );
    assert!((q.gas.w_erg_per_h / exact - 1.0).abs() < 1e-7);
}

#[test]
fn retries_leave_all_accepted_state_and_ledger_fields_unchanged() {
    let mut c = parse_config(CFG).unwrap();
    c.source.photons_per_h_per_s = 0.0;
    c.fractions = [0.0; 3];
    c.max_dln_a = 0.002;
    let (h, s) = ContinuousHistory::new(c, 1).unwrap();
    let input = AdaptiveState::new(s);
    let before = format!("{input:?}");
    let i = AdaptiveIntegrator::new(
        h,
        AdaptiveControl {
            relative: 1e-8,
            ..Default::default()
        },
    )
    .unwrap();
    let q = i.advance_one(&input, input.state.ln_a + 0.002).unwrap();
    assert!(q.diagnostics.rejected_lte > 0);
    assert_eq!(before, format!("{input:?}"));
    let mut clean = input.clone();
    clean.state.next_dln_a = q.state.ln_a - input.state.ln_a;
    let r = i.advance_one(&clean, q.state.ln_a).unwrap();
    assert_eq!(format!("{:?}", q.state.gas), format!("{:?}", r.state.gas));
    assert_eq!(
        format!("{:?}", q.state.ledger),
        format!("{:?}", r.state.ledger)
    );
    assert_eq!(q.state.counts, r.state.counts);
    assert_eq!(q.state.log_counts, r.state.log_counts);
    assert_eq!(q.state.max_residual, r.state.max_residual);
}

#[test]
fn adjacent_event_is_explicitly_unestimated_and_research_guarded() {
    use rei_microphysics::{igm_adaptive::MicrostepPolicy, igm_continuous::SpectralGrid};
    let mut c = parse_config(CFG).unwrap();
    c.source.photons_per_h_per_s = 0.0;
    let (h, mut s) = ContinuousHistory::new_with_grid(c, 3, SpectralGrid::ThresholdBands).unwrap();
    let pair = h
        .events
        .windows(2)
        .find(|p| !(p[0] < p[0] + 0.5 * (p[1] - p[0]) && p[0] + 0.5 * (p[1] - p[0]) < p[1]))
        .unwrap();
    s.ln_a = pair[0];
    let end = pair[1];
    let input = AdaptiveState::new(s);
    let before = format!("{input:?}");
    let strict = AdaptiveIntegrator::new(h.clone(), Default::default()).unwrap();
    assert_eq!(
        strict.advance_one(&input, end).unwrap_err().reason,
        "ADAPTIVE_UNSPLITTABLE_EVENT"
    );
    let research = AdaptiveIntegrator::new(
        h,
        AdaptiveControl {
            microstep_policy: MicrostepPolicy::GuardedResearch,
            ..Default::default()
        },
    )
    .unwrap();
    let q = research
        .advance_one(&input, end)
        .expect("guarded research mode must retain and measure microscopic event motion");
    assert_eq!(q.state.ln_a, end);
    assert_eq!(q.diagnostics.guarded_microsteps, 1);
    assert!(q.diagnostics.last_was_guarded);
    assert_eq!(q.diagnostics.microsteps.len(), 1);
    assert!(q.diagnostics.last_guard <= 1.0);
    assert!(q.diagnostics.microsteps[0].proper_dt > 0.0);
    assert_eq!(before, format!("{input:?}"));
}

#[test]
fn invalid_controls_and_attempt_limits_fail_without_mutation() {
    let mut c = parse_config(CFG).unwrap();
    c.source.photons_per_h_per_s = 0.0;
    c.fractions = [0.0; 3];
    c.max_dln_a = 0.002;
    let (h, s) = ContinuousHistory::new(c, 1).unwrap();
    assert!(AdaptiveIntegrator::new(
        h.clone(),
        AdaptiveControl {
            relative: f64::NAN,
            ..Default::default()
        }
    )
    .is_err());
    let i = AdaptiveIntegrator::new(
        h,
        AdaptiveControl {
            relative: 1e-10,
            max_attempts: 1,
            ..Default::default()
        },
    )
    .unwrap();
    let input = AdaptiveState::new(s);
    let before = format!("{input:?}");
    let e = i.advance_one(&input, input.state.ln_a + 0.002).unwrap_err();
    assert_eq!(e.reason, "ADAPTIVE_MAX_ATTEMPTS");
    assert_eq!(e.diagnostics.rejected_lte, 1);
    assert_eq!(before, format!("{input:?}"));
}

#[test]
fn tighter_local_control_reduces_global_neutral_error() {
    let mut errors = Vec::new();
    for relative in [1e-3, 1e-4] {
        let mut c = parse_config(CFG).unwrap();
        c.source.photons_per_h_per_s = 0.0;
        c.fractions = [0.0; 3];
        c.max_dln_a = 0.01;
        let (h, s) = ContinuousHistory::new(c, 1).unwrap();
        let end = s.ln_a + 0.02;
        let exact = s.gas.w_erg_per_h * (-0.04_f64).exp();
        let i = AdaptiveIntegrator::new(
            h,
            AdaptiveControl {
                relative,
                ..Default::default()
            },
        )
        .unwrap();
        let q = i.advance_to(&AdaptiveState::new(s), end).unwrap();
        errors.push((q.state.gas.w_erg_per_h / exact - 1.0).abs());
    }
    assert!(errors[1] < 0.7 * errors[0], "{errors:?}");
}

#[test]
fn physical_trial_failure_is_retried_from_the_original_state() {
    let mut c = parse_config(CFG).unwrap();
    c.source.photons_per_h_per_s = 1e-12;
    c.max_dln_a = 0.002;
    let (h, s) = ContinuousHistory::new(c, 1).unwrap();
    let input = AdaptiveState::new(s);
    let before = format!("{input:?}");
    let i = AdaptiveIntegrator::new(
        h,
        AdaptiveControl {
            relative: 1e-2,
            max_attempts: 64,
            ..Default::default()
        },
    )
    .unwrap();
    let q = i.advance_one(&input, input.state.ln_a + 0.002).unwrap();
    assert!(q.diagnostics.rejected_physical > 0, "{:?}", q.diagnostics);
    assert_eq!(before, format!("{input:?}"));
    assert!(q.state.ln_a > input.state.ln_a);
    assert!(q.diagnostics.last_error <= 1.0);
}

#[test]
fn photon_defect_sees_spectral_cancellation_and_preserves_log_tails() {
    let c = parse_config(CFG).unwrap();
    let (h, mut a) = ContinuousHistory::new(c, 4).unwrap();
    let i = AdaptiveIntegrator::new(h, Default::default()).unwrap();
    a.counts[0] = 1e-4;
    a.counts[1] = 2e-4;
    a.log_counts[0] = a.counts[0].ln();
    a.log_counts[1] = a.counts[1].ln();
    let mut b = a.clone();
    b.counts.swap(0, 1);
    b.log_counts.swap(0, 1);
    let e = i.state_defect(&a, &b).unwrap();
    assert!(e.max_ratio > 1.0, "{e:?}");
    a.counts.fill(0.0);
    a.log_counts.fill(f64::NEG_INFINITY);
    b = a.clone();
    a.log_counts[0] = -750.0;
    b.log_counts[0] = -760.0;
    let before = format!("{a:?}{b:?}");
    let tail = i.state_defect(&a, &b).unwrap();
    assert!(tail.max_ratio > 0.0 && tail.max_ratio < 1.0, "{tail:?}");
    assert_eq!(before, format!("{a:?}{b:?}"));
}

#[test]
fn unsplittable_motion_guard_rejects_large_relative_radiation_creation() {
    use rei_microphysics::{igm_adaptive::MicrostepPolicy, igm_continuous::SpectralGrid};
    let c = parse_config(CFG).unwrap();
    let (h, mut s) = ContinuousHistory::new_with_grid(c, 3, SpectralGrid::ThresholdBands).unwrap();
    let pair = h
        .events
        .windows(2)
        .find(|p| p[0] + 0.5 * (p[1] - p[0]) == p[0] || p[0] + 0.5 * (p[1] - p[0]) == p[1])
        .unwrap();
    s.ln_a = pair[0];
    let end = pair[1];
    let input = AdaptiveState::new(s);
    let before = format!("{input:?}");
    let i = AdaptiveIntegrator::new(
        h,
        AdaptiveControl {
            microstep_policy: MicrostepPolicy::GuardedResearch,
            ..Default::default()
        },
    )
    .unwrap();
    let e = i.advance_one(&input, end).unwrap_err();
    assert_eq!(e.reason, "ADAPTIVE_MICROSTEP_GUARD");
    assert!(e.diagnostics.last_guard > 1.0);
    assert_eq!(before, format!("{input:?}"));
}

#[test]
fn representable_two_and_three_ulp_pairs_use_actual_widths() {
    let mut c = parse_config(CFG).unwrap();
    c.source.photons_per_h_per_s = 0.0;
    c.fractions = [0.0; 3];
    let (h, s) = ContinuousHistory::new(c, 1).unwrap();
    let input = AdaptiveState::new(s);
    let i = AdaptiveIntegrator::new(h, Default::default()).unwrap();
    for (ulps, factor) in [(2_u64, 1.0), (3, 1.25)] {
        let end = f64::from_bits(input.state.ln_a.to_bits() - ulps);
        let q = i.advance_one(&input, end).unwrap();
        assert_eq!(q.state.ln_a, end);
        assert_eq!(q.diagnostics.last_error_factor, factor);
        assert!(!q.diagnostics.last_was_guarded);
        assert_eq!(q.state.accepted_steps, 2);
        assert_eq!(q.state.endpoint_stage_steps, if ulps == 2 { 2 } else { 1 });
    }
}

#[test]
fn minimum_step_and_work_limits_report_accepted_state_unchanged() {
    let mut c = parse_config(CFG).unwrap();
    c.source.photons_per_h_per_s = 0.0;
    c.fractions = [0.0; 3];
    c.max_dln_a = 0.002;
    c.min_dln_a = 0.002;
    let (h, s) = ContinuousHistory::new(c, 1).unwrap();
    let input = AdaptiveState::new(s);
    let before = format!("{input:?}");
    let i = AdaptiveIntegrator::new(
        h.clone(),
        AdaptiveControl {
            relative: 1e-10,
            ..Default::default()
        },
    )
    .unwrap();
    assert_eq!(
        i.advance_one(&input, input.state.ln_a + 0.002)
            .unwrap_err()
            .reason,
        "ADAPTIVE_MIN_STEP"
    );
    let i = AdaptiveIntegrator::new(
        h,
        AdaptiveControl {
            max_trial_evaluations: 2,
            ..Default::default()
        },
    )
    .unwrap();
    let e = i.advance_one(&input, input.state.ln_a + 0.002).unwrap_err();
    assert_eq!(e.reason, "ADAPTIVE_MAX_WORK");
    assert_eq!(e.diagnostics.trial_evaluations, 2);
    assert_eq!(before, format!("{input:?}"));
}

#[test]
fn state_and_safety_controls_are_strictly_finite_without_floors() {
    let c = parse_config(CFG).unwrap();
    let (h, s) = ContinuousHistory::new(c, 1).unwrap();
    assert!(AdaptiveIntegrator::new(
        h.clone(),
        AdaptiveControl {
            microstep_motion_limit: 1.01,
            ..Default::default()
        }
    )
    .is_err());
    assert!(AdaptiveIntegrator::new(
        h.clone(),
        AdaptiveControl {
            count_atol: 0.0,
            ..Default::default()
        }
    )
    .is_err());
    let i = AdaptiveIntegrator::new(h, Default::default()).unwrap();
    let mut input = AdaptiveState::new(s);
    input.state.counts[0] = f64::NAN;
    assert_eq!(
        i.advance_one(&input, input.state.ln_a + 1e-4)
            .unwrap_err()
            .reason,
        "ADAPTIVE_INVALID_INPUT"
    );
}

#[test]
fn both_half_branch_resource_failures_roll_back_the_entire_input() {
    let mut c = parse_config(CFG).unwrap();
    c.source.photons_per_h_per_s = 0.0;
    c.fractions = [0.0; 3];
    let (h, s) = ContinuousHistory::new(c, 1).unwrap();
    let input = AdaptiveState::new(s);
    let before = format!("{input:?}");
    for (work, phase) in [(1, "first_half"), (2, "second_half")] {
        let i = AdaptiveIntegrator::new(
            h.clone(),
            AdaptiveControl {
                max_trial_evaluations: work,
                ..Default::default()
            },
        )
        .unwrap();
        let e = i.advance_one(&input, input.state.ln_a + 1e-7).unwrap_err();
        assert_eq!(e.reason, "ADAPTIVE_MAX_WORK");
        assert_eq!(e.diagnostics.last_trial_phase, phase);
        assert_eq!(e.diagnostics.trial_evaluations, work);
        assert_eq!(before, format!("{input:?}"));
    }
}

#[test]
fn source_free_zero_readout_tail_remains_finite_and_attenuates() {
    let mut c = parse_config(CFG).unwrap();
    c.source.photons_per_h_per_s = 0.0;
    let (h, mut s) = ContinuousHistory::new(c, 4).unwrap();
    s.log_counts[0] = -750.0;
    let input = AdaptiveState::new(s);
    let i = AdaptiveIntegrator::new(h, Default::default()).unwrap();
    let q = i.advance_one(&input, input.state.ln_a + 1e-7).unwrap();
    assert_eq!(q.state.counts[0], 0.0);
    assert!(q.state.log_counts[0].is_finite());
    assert!(q.state.log_counts[0] < input.state.log_counts[0]);
    assert!(q.state.ledger.underflow_n_bound <= 1e-20);
    assert!(q.state.ledger.underflow_e_bound <= 1e-30);
}

#[test]
fn splitting_each_characteristic_preserves_the_photon_error_budget() {
    let c = parse_config(CFG).unwrap();
    let (h, mut a) = ContinuousHistory::new(c, 1).unwrap();
    a.counts = vec![1e-4, 2e-4];
    a.log_counts = a.counts.iter().map(|x| x.ln()).collect();
    let mut b = a.clone();
    b.counts = vec![1.1e-4, 1.9e-4];
    b.log_counts = b.counts.iter().map(|x| x.ln()).collect();
    let i = AdaptiveIntegrator::new(h.clone(), Default::default()).unwrap();
    let original = i.state_defect(&a, &b).unwrap();
    let mut split = h;
    split.nodes = split
        .nodes
        .iter()
        .flat_map(|n| {
            [rei_microphysics::igm_continuous::CharacteristicNode {
                eta: n.eta,
                weight: 0.5 * n.weight,
            }; 2]
        })
        .collect();
    for s in [&mut a, &mut b] {
        s.counts = s.counts.iter().flat_map(|n| [0.5 * n; 2]).collect();
        s.log_counts = s.counts.iter().map(|x| x.ln()).collect();
    }
    let i = AdaptiveIntegrator::new(split, Default::default()).unwrap();
    let duplicate = i.state_defect(&a, &b).unwrap();
    assert!(
        (duplicate.max_ratio / original.max_ratio - 1.0).abs() < 1e-12,
        "{original:?} {duplicate:?}"
    );
    assert_eq!(duplicate.worst_component, original.worst_component);
}

#[test]
fn overflowing_mixed_tolerance_scale_is_not_a_zero_defect() {
    let c = parse_config(CFG).unwrap();
    let (h, s) = ContinuousHistory::new(c, 1).unwrap();
    let i = AdaptiveIntegrator::new(
        h,
        AdaptiveControl {
            relative: f64::MAX,
            ..Default::default()
        },
    )
    .unwrap();
    assert!(
        i.state_defect(&s, &s).is_err(),
        "a nonfinite denominator must fail rather than return a zero norm"
    );
}

#[test]
fn invalid_gas_and_cumulative_ledgers_cannot_be_admitted_even_at_zero_duration() {
    let c = parse_config(CFG).unwrap();
    let (h, s) = ContinuousHistory::new(c, 1).unwrap();
    let i = AdaptiveIntegrator::new(h, Default::default()).unwrap();
    let mut gas = AdaptiveState::new(s.clone());
    gas.state.gas.w_erg_per_h = f64::NAN;
    assert!(
        i.advance_to(&gas, gas.state.ln_a).is_err(),
        "zero-duration call must validate gas"
    );
    let mut ledger = AdaptiveState::new(s);
    ledger.state.ledger.emitted_n = f64::NAN;
    assert!(
        i.advance_to(&ledger, ledger.state.ln_a).is_err(),
        "zero-duration call must validate all cumulative ledger fields"
    );
    assert!(
        i.advance_one(&ledger, ledger.state.ln_a + 1e-7).is_err(),
        "fresh delta error control must not hide an invalid cumulative ledger"
    );
}

#[test]
fn diagnostic_nan_and_contradictory_normal_count_logs_are_rejected() {
    let c = parse_config(CFG).unwrap();
    let (h, s) = ContinuousHistory::new(c, 1).unwrap();
    let i = AdaptiveIntegrator::new(h, Default::default()).unwrap();
    let mut input = AdaptiveState::new(s.clone());
    input.diagnostics.max_error = f64::NAN;
    assert!(
        i.advance_to(&input, input.state.ln_a).is_err(),
        "diagnostic NaN must not be admitted on identity advances"
    );
    let mut input = AdaptiveState::new(s);
    input.state.counts[0] = 1.0;
    input.state.log_counts[0] = -750.0;
    assert!(
        i.advance_one(&input, input.state.ln_a + 1e-7).is_err(),
        "normal count and authoritative logarithm must agree"
    );
}

#[test]
fn nonfinite_middle_ledger_channels_reject_but_signed_cmb_is_legal() {
    let c = parse_config(CFG).unwrap();
    let (h, s) = ContinuousHistory::new(c, 1).unwrap();
    let i = AdaptiveIntegrator::new(h, Default::default()).unwrap();
    for poison in [0, 1, 2, 3] {
        let mut input = AdaptiveState::new(s.clone());
        match poison {
            0 => input.state.ledger.absorption[1] = f64::NAN,
            1 => input.state.ledger.cmb_e = f64::INFINITY,
            2 => input.state.ledger.cap_e[1] = f64::NAN,
            _ => input.state.ledger.underflow_e_bound = f64::NAN,
        }
        assert!(i.advance_to(&input, input.state.ln_a).is_err());
    }
    let mut input = AdaptiveState::new(s);
    input.state.ledger.cmb_e = -1e-30;
    assert!(i.advance_to(&input, input.state.ln_a).is_ok());
}
