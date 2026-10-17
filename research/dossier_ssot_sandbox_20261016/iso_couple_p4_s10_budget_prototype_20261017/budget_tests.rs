// P4/S10 policy regressions. AUTHORED, NOT EXECUTED: sandbox ServerError.
// Run after runtime recovery: rustc --edition=2021 --test budget_tests.rs -o budget_tests && ./budget_tests
#[path = "budget_kernel.rs"]
mod budget_kernel;
use budget_kernel::*;

fn datum(key: &str, value: f64) -> Datum {
    Datum { key: key.into(), unit: "comoving_m^-3".into(), value }
}
fn scales() -> Vec<Scale> {
    vec![Scale { key: "DI_events".into(), unit: "comoving_m^-3".into(), value: 1.0 }]
}
fn pair(coarse: f64, fine: f64, tighter: bool) -> Pair {
    Pair {
        context: Context {
            initial_identity: "same-immutable-initial-state".into(),
            physics_identity: "P9-locked-physics-and-quadrature".into(),
            projection_identity: "P9-labels-units-v1".into(),
            start_s: 0.0,
            end_s: 2.0,
        },
        precision: if tighter {
            Precision { relative: 1e-10, absolute: 1e-13 }
        } else {
            Precision { relative: 1e-8, absolute: 1e-11 }
        },
        coarse: vec![datum("DI_events", coarse)],
        fine: vec![datum("DI_events", fine)],
    }
}
#[test]
fn cancellation_is_not_a_zero_inner_error() {
    let r = assess(&pair(2.0, 2.0, false), &pair(1.3, 1.1, true), &scales(), 0.25).unwrap();
    assert_eq!(r.decision, Decision::TightenInner);
    assert_eq!(r.loose_defect_max, 0.0);
    assert!(r.inner_max > 1.59);
}
#[test]
fn separate_budgets_admit_tight_fine_only() {
    let r = assess(&pair(0.60, 0.20, false), &pair(0.55, 0.15, true), &scales(), 0.25).unwrap();
    assert_eq!(r.decision, Decision::AcceptTightFine);
    assert!((r.outer_max - 0.4).abs() < 1e-14);
    assert!((r.inner_max - 0.1).abs() < 1e-14);
}
#[test]
fn outer_failure_requests_smaller_h_after_inner_passes() {
    let r = assess(&pair(2.0, 1.0, false), &pair(2.0, 1.0, true), &scales(), 0.25).unwrap();
    assert_eq!(r.decision, Decision::ReduceOuter);
}
#[test]
fn common_bias_is_explicitly_not_certified() {
    let r = assess(&pair(100.0, 100.0, false), &pair(100.0, 100.0, true), &scales(), 0.25).unwrap();
    assert_eq!(r.decision, Decision::AcceptTightFine);
    assert_eq!(r.outer_max + r.inner_max, 0.0);
    // An external exact reference of zero would still have error 100.
    // Acceptance controls tested differences, NOT error against an exact solution.
}
#[test]
fn reordering_labels_is_safe() {
    let mut lo = pair(0.5, 0.2, false);
    let mut hi = pair(0.5, 0.2, true);
    lo.coarse.push(datum("HeII_events", 1e-20));
    lo.fine.push(datum("HeII_events", 1e-20));
    hi.coarse.insert(0, datum("HeII_events", 1e-20));
    hi.fine.insert(0, datum("HeII_events", 1e-20));
    let mut s = scales();
    s.push(Scale { key: "HeII_events".into(), unit: "comoving_m^-3".into(), value: 1e-28 });
    let r = assess(&lo, &hi, &s, 0.25).unwrap();
    assert_eq!(r.decision, Decision::AcceptTightFine);
    assert_eq!(r.components.len(), 2);
}
#[test]
fn missing_channel_is_rejected() {
    let mut hi = pair(0.5, 0.2, true);
    hi.fine.clear();
    assert!(assess(&pair(0.5, 0.2, false), &hi, &scales(), 0.25).is_err());
}
#[test]
fn duplicate_channel_is_rejected() {
    let mut hi = pair(0.5, 0.2, true);
    hi.fine.push(datum("DI_events", 0.2));
    assert_eq!(assess(&pair(0.5, 0.2, false), &hi, &scales(), 0.25).unwrap_err(), BudgetError::DuplicateLabel);
}
#[test]
fn units_are_not_inferred_or_silently_converted() {
    let mut hi = pair(0.5, 0.2, true);
    hi.fine[0].unit = "proper_m^-3".into();
    assert_eq!(assess(&pair(0.5, 0.2, false), &hi, &scales(), 0.25).unwrap_err(), BudgetError::UnitMismatch);
}
#[test]
fn invalid_scales_are_rejected() {
    for x in [0.0, -1.0, f64::NAN, f64::INFINITY] {
        let mut s = scales(); s[0].value = x;
        assert!(assess(&pair(0.5, 0.2, false), &pair(0.5, 0.2, true), &s, 0.25).is_err());
    }
}
#[test]
fn context_change_cannot_be_called_an_inner_refinement() {
    let lo = pair(0.5, 0.2, false);
    for k in 0..4 {
        let mut hi = pair(0.5, 0.2, true);
        match k {
            0 => hi.context.initial_identity.push('x'),
            1 => hi.context.physics_identity.push('x'),
            2 => hi.context.projection_identity.push('x'),
            _ => hi.context.end_s = 3.0,
        }
        assert_eq!(assess(&lo, &hi, &scales(), 0.25).unwrap_err(), BudgetError::ContextMismatch);
    }
}
#[test]
fn both_inner_tolerances_must_tighten() {
    let lo = pair(0.5, 0.2, false);
    let hi = pair(0.5, 0.2, false);
    assert_eq!(assess(&lo, &hi, &scales(), 0.25).unwrap_err(), BudgetError::PrecisionNotTighter);
}
#[test]
fn nonfinite_observations_are_fatal_input_errors() {
    let mut hi = pair(0.5, 0.2, true);
    hi.fine[0].value = f64::NAN;
    assert_eq!(assess(&pair(0.5, 0.2, false), &hi, &scales(), 0.25).unwrap_err(), BudgetError::NonFinite);
}
#[test]
fn rare_channel_is_not_hidden_in_total_photon_scale() {
    let mut lo = pair(0.0, 0.0, false);
    let mut hi = pair(0.0, 0.0, true);
    for p in [&mut lo, &mut hi] {
        p.coarse.push(datum("HeII_events", 1e-20));
        p.fine.push(datum("HeII_events", 1e-20));
    }
    hi.fine[1].value += 1e-27;
    let mut s = scales();
    s.push(Scale { key: "HeII_events".into(), unit: "comoving_m^-3".into(), value: 1e-28 });
    assert_eq!(assess(&lo, &hi, &s, 0.25).unwrap().decision, Decision::TightenInner);
}
#[test]
fn exhausted_inner_ladder_does_not_accept_or_shrink_h() {
    let r = assess(&pair(2.0, 2.0, false), &pair(1.3, 1.1, true), &scales(), 0.25).unwrap();
    assert_eq!(plan_next(&r, false, 2, 8).unwrap(), Action::StopInnerUnresolved);
}
#[test]
fn pair_work_budget_is_distinct_from_accuracy() {
    let r = assess(&pair(2.0, 2.0, false), &pair(1.3, 1.1, true), &scales(), 0.25).unwrap();
    assert_eq!(plan_next(&r, true, 4, 4).unwrap(), Action::StopWorkLimit);
    assert_eq!(plan_next(&r, true, 2, 4).unwrap(), Action::RefineAtSameInterval);
}
#[test]
fn invalid_budget_fraction_is_rejected() {
    for b in [0.0, 1.0, -0.5, f64::NAN] {
        assert!(assess(&pair(0.5, 0.2, false), &pair(0.5, 0.2, true), &scales(), b).is_err());
    }
}
#[test]
fn zero_duration_is_not_a_successful_trial() {
    let mut lo = pair(0.5, 0.2, false); lo.context.end_s = 0.0;
    assert_eq!(assess(&lo, &pair(0.5, 0.2, true), &scales(), 0.25).unwrap_err(), BudgetError::InvalidContext);
}
#[test]
fn overflowing_differences_fail_closed() {
    let lo = pair(f64::MAX, 0.0, false);
    let hi = pair(-f64::MAX, 0.0, true);
    assert_eq!(assess(&lo, &hi, &scales(), 0.25).unwrap_err(), BudgetError::NonFiniteArithmetic);
}
#[test]
fn normalized_underflow_is_not_silently_zero() {
    let lo = pair(1e-300, 0.0, false);
    let hi = pair(0.0, 0.0, true);
    let mut s = scales(); s[0].value = 1e300;
    assert_eq!(assess(&lo, &hi, &s, 0.25).unwrap_err(), BudgetError::NormalizedUnderflow);
}
#[test]
fn exact_binary_grid_obeys_triangle_and_admission_implication() {
    for a in -4..=4 { for b in -4..=4 { for c in -4..=4 { for d in -4..=4 {
        let r = assess(&pair(a as f64/4.0, b as f64/4.0, false),
                       &pair(c as f64/4.0, d as f64/4.0, true), &scales(), 0.25).unwrap();
        assert!(r.loose_defect_max <= r.triangle_upper_max);
        assert!(r.mixed_change_max <= r.inner_max);
        if r.decision == Decision::AcceptTightFine { assert!(r.loose_defect_max <= 1.0); }
    }}}}
}
