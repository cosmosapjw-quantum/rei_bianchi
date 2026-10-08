#[path="../../shared-log-spectral-primitives/src/primitives.rs"] mod primitives;
use primitives::*;
fn close(a: f64, b: f64, t: f64) {
    assert!((a - b).abs() <= t, "{a:e} != {b:e}");
}

fn zero_readout_is_positive_and_attenuates_exponentially() {
    let a = Wide::from_log(-750.0).unwrap();
    assert!(!a.is_empty());
    assert_eq!(a.readout().unwrap().0, 0.0);
    close(a.log(), -750.0, 2e-12);
    let o = segment(
        Tracked::exact(a),
        Tracked::empty(),
        [2.0, 0.0, 0.0],
        0.5,
        100.0,
    )
    .unwrap();
    close(o.n.value.log(), -751.0, 2e-12);
    assert!(!o.a[0].value.is_empty());
}

fn shared_pair_retains_shape_after_common_logs_cancel() {
    let n = 0.5;
    let m = n * (2.0f64).exp() * (1.0 + 0.4 * (1e-7f64).exp_m1());
    let p = MomentPair::new(2.0, (2.0f64 + 1e-7).next_up(), -1000000, n, m, false).unwrap();
    assert!(p.normalized_mean().unwrap() > 0.39 && p.normalized_mean().unwrap() < 0.41);
    assert_eq!(p.readout().unwrap().n, 0.0);
    assert!(MomentPair::new(2.0, (2.0f64 + 1e-7).next_up(), 0, 0.5, 100.0, false).is_err());
}

fn normal_aggregate_charges_lost_weighted_addend() {
    let small = Tracked::exact(Wide::from_log(-750.0).unwrap())
        .mul(Tracked::from_f64(1e308).unwrap())
        .unwrap();
    let big = Tracked::from_f64(1.0).unwrap();
    let total = big.add(small).unwrap();
    assert!(!total.loss.is_empty());
    assert!(total.loss.log() >= small.value.log());
    assert!(!admit(0.0, total.loss, 1e-20, 1e-20).unwrap());
}

fn source_restart_and_export_preserve_authority() {
    let o = segment(
        Tracked::exact(Wide::from_log(-750.0).unwrap()),
        Tracked::from_f64(0.3).unwrap(),
        [0.0; 3],
        0.1,
        100.0,
    )
    .unwrap();
    close(o.n.value.readout().unwrap().0, 0.03, 1e-15);
    let mut tail = segment(
        Tracked::exact(Wide::from_log(-750.0).unwrap()),
        Tracked::empty(),
        [0.0; 3],
        0.1,
        100.0,
    )
    .unwrap();
    let ln = tail.n.value.log();
    tail.export().unwrap();
    assert!(tail.n.value.is_empty());
    close(tail.outn.value.log(), ln, 1e-13);
}

fn strengthened_budget_rejects_bound_even_at_zero_residual() {
    assert!(!admit(0.0, Wide::from_f64(1.1e-20).unwrap(), 1e-20, 1e-20).unwrap());
    assert!(!admit(0.75e-20, Wide::from_f64(0.5e-20).unwrap(), 1e-20, 1e-20).unwrap());
    assert!(admit(0.25e-20, Wide::from_f64(0.5e-20).unwrap(), 1e-20, 1e-20).unwrap());
}

fn front_restriction_is_positive_and_empty_geometry_exact() {
    let c = ClosureInput {
        l: 0.0,
        r: 1.0,
        beta: 0.0,
        front: true,
        n: Tracked::from_f64(1.0).unwrap(),
    };
    let (n, m) = restrict(c, 0.0, 0.5).unwrap();
    close(n.value.readout().unwrap().0, 0.75, 3e-14);
    assert!(m.value.log() > n.value.log());
    let (n, m) = restrict(c, 2.0, 3.0).unwrap();
    assert!(n.value.is_empty() && m.value.is_empty());
}

fn validated_commit_rejects_overflow_and_caps_atomically() {
    let mut ledger = Owners::empty();
    let normal = segment(
        Tracked::from_f64(1.0).unwrap(),
        Tracked::empty(),
        [0.0; 3],
        0.0,
        100.0,
    )
    .unwrap();
    ledger
        .checked_add(
            normal,
            Tracked::from_f64(1.0).unwrap(),
            0.0,
            0.0,
            1e-20,
            1e-30,
        )
        .unwrap();
    let before = ledger;
    let too_large = Tracked::exact(Wide::from_parts(1.0, 1024).unwrap());
    assert!(ledger
        .checked_add(normal, too_large, 0.0, 0.0, 1e-20, 1e-30)
        .is_err());
    assert_eq!(ledger, before);
    let small = Tracked::from_f64(2e-18).unwrap();
    assert!(ledger
        .checked_add(normal, small, 0.0, 0.0, 1e-20, 1e-30)
        .is_err());
    assert_eq!(ledger, before);
}

fn malformed_inputs_reject_and_energy_underflows_first() {
    assert!(Wide::from_log(f64::NEG_INFINITY).is_err());
    assert!(Wide::from_log(f64::NAN).is_err());
    assert!(Wide::from_parts(1.0, 1024).unwrap().readout().is_err());
    let n = 0.5;
    let m = n * 0.5f64.exp();
    assert!(MomentPair::with_logs(0.0, 1.0, 0, n, m, false, 0.0, 0.0).is_err());
    let o = segment(
        Tracked::from_f64(1e-310).unwrap(),
        Tracked::empty(),
        [0.0; 3],
        0.0,
        100.0,
    )
    .unwrap();
    assert!(o.n.value.readout().unwrap().0 > 0.0);
    assert!(!o.u.value.is_empty());
    assert!(!o.u.readout().unwrap().1.is_empty());
}

fn pair_readouts_have_dimensional_bounds() {
    let p = MomentPair::new(0.0, 1.0, -1200, 1.0, 0.5f64.exp(), false).unwrap();
    let r = p.readout().unwrap();
    assert_eq!(r.n, 0.0);
    assert_eq!(r.m, 0.0);
    assert!(!r.n_bound.is_empty());
    assert!(!r.m_bound.is_empty());
    assert_eq!(
        r.n_bound,
        Wide::from_parts(p.components().1, p.components().0).unwrap()
    );
}

fn long_dark_continuation_does_not_use_be_or_log_roundtrip() {
    let start = Tracked::exact(Wide::from_parts(1.3, -1000000).unwrap());
    let mut state = start;
    for _ in 0..10 {
        state = segment(state, Tracked::empty(), [2.0, 0.0, 0.0], 0.5, 100.0)
            .unwrap()
            .n;
    }
    let ratio = state.value.mantissa() / start.value.mantissa()
        * 2.0f64.powi(state.value.exponent() - start.value.exponent());
    close(ratio, (-10.0f64).exp(), 1e-16);
    assert_ne!(state.value.log(), f64::NEG_INFINITY);
}

fn physical_opacity_tail_and_weight_unit_controls() {
    let f = Tracked::from_f64(1.0).unwrap();
    let q = Tracked::from_f64(0.3).unwrap();
    let rates = [1.3663e6, 0.0, 0.0];
    let h = 5.5e-4;
    let dark = segment(f, Tracked::empty(), rates, h, 100.0).unwrap();
    assert_eq!(dark.n.value.readout().unwrap().0, 0.0);
    close(dark.n.value.log(), -rates[0] * h, 2e-12);
    let initial = segment(f, Tracked::empty(), [2.0, 1.0, 0.0], 0.1, 100.0).unwrap();
    let source = segment(Tracked::empty(), q, [2.0, 1.0, 0.0], 0.1, 100.0).unwrap();
    let joint = segment(f, q, [2.0, 1.0, 0.0], 0.1, 100.0).unwrap();
    let split = initial.add(source).unwrap();
    for (a, b) in [
        (joint.n, split.n),
        (joint.u, split.u),
        (joint.a[0], split.a[0]),
        (joint.b[1], split.b[1]),
        (joint.red, split.red),
    ] {
        close(
            a.value.readout().unwrap().0,
            b.value.readout().unwrap().0,
            3e-15,
        );
    }
    let weighted = initial.weighted(Tracked::from_f64(0.2).unwrap()).unwrap();
    close(
        weighted.a[0].value.readout().unwrap().0,
        0.2 * initial.a[0].value.readout().unwrap().0,
        1e-16,
    );
}

fn endpoint_moment_uses_carried_energy_and_keeps_tail_scale() {
    let k = -1200;
    let n = Tracked::exact(Wide::from_parts(1.3, k).unwrap());
    let mut o = Owners::empty();
    o.n = n;
    o.u = n.scale(EPS).unwrap().scale(0.4f64.exp()).unwrap();
    let endpoint = endpoint_pair(0.0, 1.0, 0.0, o, false).unwrap();
    let p = endpoint.pair.unwrap();
    let (e, ns, ms) = p.components();
    assert_eq!(e, k);
    close(ms / ns, 0.4f64.exp(), 1e-15);
    assert_eq!(endpoint.carried_u, o.u);
    assert!(endpoint_pair(0.0, 1.0, 0.0, Owners::empty(), false)
        .unwrap()
        .pair
        .is_none());
    let mut invalid = o;
    invalid.u = Tracked::empty();
    assert!(endpoint_pair(0.0, 1.0, 0.0, invalid, false).is_err());
}

fn restrictions_add_moments_without_final_child_residual() {
    for front in [false, true] {
        for beta in [-128.0, -1.0, 0.0, 128.0] {
            let c = ClosureInput {
                l: 0.0,
                r: 1.0,
                beta,
                front,
                n: Tracked::exact(Wide::from_parts(1.3, -1200).unwrap()),
            };
            let full = restrict(c, 0.0, 1.0).unwrap();
            let left = restrict(c, 0.0, 0.37).unwrap();
            let right = restrict(c, 0.37, 1.0).unwrap();
            for (total, a, b) in [(full.0, left.0, right.0), (full.1, left.1, right.1)] {
                let sum = a.add(b).unwrap();
                let rel = sum.value.mantissa() / total.value.mantissa()
                    * 2.0f64.powi(sum.value.exponent() - total.value.exponent())
                    - 1.0;
                assert!(rel.abs() < 5e-12);
            }
            let eta = (left.1.value.mantissa() / left.0.value.mantissa()).ln()
                + ((left.1.value.exponent() - left.0.value.exponent()) as f64)
                    * std::f64::consts::LN_2;
            let scaled_m = left.0.value.mantissa()
                * eta.exp()
                * 2.0f64.powi(left.0.value.exponent() - left.1.value.exponent());
            assert!((scaled_m / left.1.value.mantissa() - 1.0).abs() < 3e-12);
        }
    }
}

fn malformed_extreme_exponent_and_underflowing_front_sliver() {
    assert!(Wide::from_parts(1.0, i32::MIN).is_err());
    let c = ClosureInput {
        l: 0.0,
        r: 1.0,
        beta: 0.0,
        front: false,
        n: Tracked::from_f64(1.0).unwrap(),
    };
    let (n, m) = restrict(c, 0.0, f64::from_bits(1)).unwrap();
    assert!(!n.value.is_empty() && !m.value.is_empty());
    let front = ClosureInput { front: true, ..c };
    let (n, m) = restrict(front, 0.0, f64::from_bits(1)).unwrap();
    assert!(!n.value.is_empty() && !m.value.is_empty());
}

fn reviewer_readout_boundary_and_local_width_regressions() {
    let x = Wide::from_parts(2.0f64.next_down(), -1023).unwrap();
    let (value, bound) = x.readout().unwrap();
    assert_eq!(value, f64::MIN_POSITIVE);
    assert!(Wide::from_parts(1.0, -1075).unwrap().le(bound));
    for front in [false, true] {
        let c = ClosureInput {
            l: 0.0,
            r: 3.0,
            beta: 0.0,
            front,
            n: Tracked::from_f64(1.0).unwrap(),
        };
        let a = 3.0f64.next_down();
        let (n, _) = restrict(c, a, 3.0).unwrap();
        let d = (3.0 - a) / 3.0;
        let expected = if front { d * d } else { d };
        assert!((n.value.readout().unwrap().0 / expected - 1.0).abs() < 3e-12);
    }
}

fn reviewer_invalid_empty_inputs_reject() {
    assert!(endpoint_pair(f64::NAN, f64::INFINITY, 0.0, Owners::empty(), false).is_err());
    assert!(endpoint_pair(1.0, 0.0, 0.0, Owners::empty(), false).is_err());
    let c = ClosureInput {
        l: 0.0,
        r: 1.0,
        beta: 0.0,
        front: false,
        n: Tracked {
            value: Wide::ZERO,
            loss: Wide::from_f64(1e-25).unwrap(),
        },
    };
    assert!(restrict(c, 0.0, 1.0).is_err());
}

fn main(){
zero_readout_is_positive_and_attenuates_exponentially(); println!("INHERITED_PASS zero_readout_is_positive_and_attenuates_exponentially");
shared_pair_retains_shape_after_common_logs_cancel(); println!("INHERITED_PASS shared_pair_retains_shape_after_common_logs_cancel");
normal_aggregate_charges_lost_weighted_addend(); println!("INHERITED_PASS normal_aggregate_charges_lost_weighted_addend");
source_restart_and_export_preserve_authority(); println!("INHERITED_PASS source_restart_and_export_preserve_authority");
strengthened_budget_rejects_bound_even_at_zero_residual(); println!("INHERITED_PASS strengthened_budget_rejects_bound_even_at_zero_residual");
front_restriction_is_positive_and_empty_geometry_exact(); println!("INHERITED_PASS front_restriction_is_positive_and_empty_geometry_exact");
validated_commit_rejects_overflow_and_caps_atomically(); println!("INHERITED_PASS validated_commit_rejects_overflow_and_caps_atomically");
malformed_inputs_reject_and_energy_underflows_first(); println!("INHERITED_PASS malformed_inputs_reject_and_energy_underflows_first");
pair_readouts_have_dimensional_bounds(); println!("INHERITED_PASS pair_readouts_have_dimensional_bounds");
long_dark_continuation_does_not_use_be_or_log_roundtrip(); println!("INHERITED_PASS long_dark_continuation_does_not_use_be_or_log_roundtrip");
physical_opacity_tail_and_weight_unit_controls(); println!("INHERITED_PASS physical_opacity_tail_and_weight_unit_controls");
endpoint_moment_uses_carried_energy_and_keeps_tail_scale(); println!("INHERITED_PASS endpoint_moment_uses_carried_energy_and_keeps_tail_scale");
restrictions_add_moments_without_final_child_residual(); println!("INHERITED_PASS restrictions_add_moments_without_final_child_residual");
malformed_extreme_exponent_and_underflowing_front_sliver(); println!("INHERITED_PASS malformed_extreme_exponent_and_underflowing_front_sliver");
reviewer_readout_boundary_and_local_width_regressions(); println!("INHERITED_PASS reviewer_readout_boundary_and_local_width_regressions");
reviewer_invalid_empty_inputs_reject(); println!("INHERITED_PASS reviewer_invalid_empty_inputs_reject");
}
