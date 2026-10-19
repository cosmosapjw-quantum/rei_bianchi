use rei_iso_couple_reference::birth_layers::graded_birth_nodes;
#[test]
fn terminal_optical_layer_survives_at_tau_1000() {
    let tau = 1000.;
    let nodes = graded_birth_nodes(tau, 2., 128).unwrap();
    let survival = nodes
        .iter()
        .map(|n| n.weight * (-tau * n.remaining_fraction).exp())
        .sum::<f64>();
    let exact = if tau == 0.0 {
        1.0
    } else {
        -(-tau).exp_m1() / tau
    };
    let relative = (survival / exact - 1.).abs();
    assert!(
        relative < 2e-6,
        "terminal survivor relative error = {relative:.17e}, got {survival:.17e}, exact {exact:.17e}"
    );
}

#[test]
fn positive_complete_weights_and_birth_age_moments() {
    for tau in [0.0, 1e-12, 0.1, 1.0, 10.0, 1e3, 1e8, 1e12] {
        let nodes = graded_birth_nodes(tau, 1.5, 128).unwrap();
        assert!(
            nodes.iter().all(|n| n.weight > 0.0
                && n.remaining_fraction > 0.0
                && n.remaining_fraction < 1.0)
        );
        for m in 0_i32..=7 {
            let v = nodes
                .iter()
                .map(|n| n.weight * n.remaining_fraction.powi(m))
                .sum::<f64>();
            assert!(
                (v - 1.0 / (m as f64 + 1.0)).abs() < 2e-14,
                "tau={tau} m={m}"
            );
        }
    }
}
#[test]
fn constant_remainder_controls_different_channel_opacities() {
    use rei_iso_couple_reference::birth_layers::constant_survival_error_bound;
    for seed in [1e-3, 1.0, 10.0, 1e3, 1e6, 1e10] {
        for ratio in [0.0, 1e-8, 1e-4, 0.01, 0.3, 1.0] {
            let tau = seed * ratio;
            for growth in [2.0, 1.5, 1.25] {
                let nodes = graded_birth_nodes(seed, growth, 128).unwrap();
                let s = nodes
                    .iter()
                    .map(|n| n.weight * (-tau * n.remaining_fraction).exp())
                    .sum::<f64>();
                let exact = if tau == 0.0 {
                    1.0
                } else {
                    -(-tau).exp_m1() / tau
                };
                let bound = constant_survival_error_bound(tau, seed, growth, 128).unwrap();
                assert!(
                    (s - exact).abs() <= bound + 3e-14 * exact,
                    "seed={seed} ratio={ratio} g={growth} err={} bound={bound}",
                    (s - exact).abs()
                );
                assert!((s / exact - 1.0).abs() < 2e-6);
            }
        }
    }
}
#[test]
fn panel_budget_invalid_scale_and_invalid_growth_reject() {
    for tau in [-1.0, f64::NAN, f64::INFINITY] {
        assert!(graded_birth_nodes(tau, 2.0, 128).is_err());
    }
    for g in [0.0, 1.0, 2.1, f64::NAN] {
        assert!(graded_birth_nodes(1e3, g, 128).is_err());
    }
    assert!(graded_birth_nodes(1e3, 2.0, 2).is_err());
    assert!(graded_birth_nodes(1e3, 2.0, 0).is_err());
}
#[test]
fn very_opaque_cases_use_logarithmically_many_panels() {
    assert_eq!(graded_birth_nodes(1e3, 2.0, 128).unwrap().len(), 44);
    assert_eq!(graded_birth_nodes(1e6, 2.0, 128).unwrap().len(), 84);
    assert_eq!(graded_birth_nodes(1e12, 2.0, 128).unwrap().len(), 164);
}

#[test]
fn thick_slab_survivor_does_not_cancel_against_unity() {
    use rei_iso_couple_reference::birth_layers::stable_new_survival;
    for tau in [1e8, 1e12, 1e16, 1e18] {
        assert!(
            (stable_new_survival(tau).unwrap() * tau - 1.0).abs() < 2e-15,
            "tau={tau}"
        );
    }
}
