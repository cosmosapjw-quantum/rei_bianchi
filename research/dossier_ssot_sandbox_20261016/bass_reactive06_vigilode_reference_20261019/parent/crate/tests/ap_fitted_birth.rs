use rei_iso_couple_reference::{
    fitted_birth::{frozen_inventory, phi, rule},
    full_network::NetworkError,
};

#[test]
fn constant_opacity_survival_is_exact_across_thin_and_thick_scales() {
    for tau in [
        0.0, 1e-12, 1e-6, 0.1, 1.0, 3.0, 20.0, 93.0, 1000.0, 1e6, 1e12,
    ] {
        for refinement in [1, 2, 4, 8, 16] {
            let out = frozen_inventory(0.7, 2.0, [tau, 0.0, 0.0, 0.0], 1.0, refinement).unwrap();
            let exact = 0.7 * (-tau).exp() + 2.0 * phi(tau).unwrap();
            assert!(
                (out.survivor / exact - 1.0).abs() < 8e-14,
                "tau={tau} r={refinement}"
            );
            assert!(out.number_residual.abs() < 1e-14);
            assert!(out.survivor > 0.0);
        }
    }
}

#[test]
fn every_node_preserves_positive_birth_record_and_emission_mean() {
    for tau in [0.0, 1e-4, 0.99, 1.01, 93.0, 1e6, 1e12] {
        for refinement in [1, 2, 4, 8, 16] {
            let nodes = rule(tau, refinement).unwrap();
            assert!(nodes.iter().all(|(x, w)| *x > 0.0 && *x < 1.0 && *w > 0.0));
            assert!(nodes.windows(2).all(|p| p[0].0 < p[1].0));
            let mass: f64 = nodes.iter().map(|n| n.1).sum();
            let mean: f64 = nodes.iter().map(|n| n.0 * n.1).sum();
            assert!((mass - 1.0).abs() < 4e-15);
            assert!((mean - 0.5).abs() < 4e-15);
        }
    }
}

#[test]
fn transparent_rule_has_gauss_nodes_and_fourth_order_moment_refinement() {
    let nodes = rule(0.0, 1).unwrap();
    assert!((nodes[0].0 - 0.5 * (1.0 - 1.0 / 3.0_f64.sqrt())).abs() < 2e-16);
    assert_eq!(nodes[0].1, 0.5);
    let error = |r| {
        let v: f64 = rule(0.0, r)
            .unwrap()
            .iter()
            .map(|(x, w)| w * x.powi(4))
            .sum();
        (v - 0.2).abs()
    };
    assert!((error(1) / error(2) - 16.0).abs() < 1e-9);
    assert!((error(2) / error(4) - 16.0).abs() < 1e-8);
}

#[test]
fn transparent_photons_and_zero_source_are_both_admitted() {
    let a = frozen_inventory(3.0, 2.0, [0.0; 4], 7.0, 4).unwrap();
    assert!((a.survivor - 5.0).abs() < 1e-15);
    assert_eq!(a.species_absorbed, [0.0; 4]);
    let b = frozen_inventory(3.0, 0.0, [0.1, 0.2, 0.3, 0.4], 2.0, 4).unwrap();
    assert_eq!(b.born_survivor, 0.0);
    assert_eq!(b.born_age_moments, [0.0; 3]);
    assert!((b.survivor - 3.0 * (-2.0_f64).exp()).abs() < 1e-15);
    assert_eq!(
        frozen_inventory(0.0, 0.0, [0.0; 4], 1.0, 1)
            .unwrap()
            .survivor,
        0.0
    );
}

#[test]
fn competitive_absorption_is_nonnegative_and_owns_each_photon_once() {
    for scale in [1e-10, 1.0, 1e4] {
        let rates = [scale, 2.0 * scale, 0.0, 7.0 * scale];
        let o = frozen_inventory(1.0, 2.0, rates, 4.0, 2).unwrap();
        let a: f64 = o.species_absorbed.iter().sum();
        assert!(o.species_absorbed.iter().all(|v| *v >= 0.0));
        assert_eq!(o.species_absorbed[2], 0.0);
        assert!((o.species_absorbed[0] / a - 0.1).abs() < 1e-15);
        assert!((o.species_absorbed[3] / a - 0.7).abs() < 1e-15);
        assert!((o.survivor + a - 3.0).abs() < 1e-14);
    }
}

#[test]
fn thick_survivor_age_moments_converge_without_collapsing_birth_times() {
    let tau: f64 = 93.0;
    let exact_mean = 1.0 / tau - 1.0 / (tau.exp() - 1.0);
    let exact_second = 2.0 / (tau * tau) - (1.0 + 2.0 / tau) / (tau.exp() - 1.0);
    let mut previous = [f64::INFINITY; 2];
    for r in [1, 2, 4, 8, 16] {
        let a = frozen_inventory(0.0, 1.0, [tau, 0.0, 0.0, 0.0], 1.0, r).unwrap();
        let errors = [
            (a.born_age_moments[1] / a.born_survivor / exact_mean - 1.0).abs(),
            (a.born_age_moments[2] / a.born_survivor / exact_second - 1.0).abs(),
        ];
        assert!(errors.iter().zip(previous).all(|(e, p)| *e < p));
        previous = errors;
    }
    assert!(previous[0] < 5e-7);
    assert!(previous[1] < 2e-6);
}

#[test]
fn node_cost_grows_with_log_optical_depth_and_not_optical_depth() {
    let n = rule(1e12, 4).unwrap().len();
    assert!(n > 100 && n < 1200, "{n}");
}

#[test]
fn malformed_inputs_and_negative_populations_are_rejected() {
    for x in [-1.0, f64::NAN, f64::INFINITY] {
        assert!(rule(x, 1).is_err());
        assert!(phi(x).is_err());
        assert!(frozen_inventory(x, 1.0, [1.0; 4], 1.0, 1).is_err());
        assert!(frozen_inventory(0.0, x, [1.0; 4], 1.0, 1).is_err());
        assert!(frozen_inventory(0.0, 1.0, [x, 0.0, 0.0, 0.0], 1.0, 1).is_err());
    }
    for r in [0, 3, 32, usize::MAX] {
        assert!(rule(1.0, r).is_err());
    }
    for dt in [0.0, -1.0, f64::NAN] {
        assert!(frozen_inventory(0.0, 1.0, [1.0; 4], dt, 1).is_err());
    }
    assert_eq!(
        rule(f64::MAX, 16).unwrap_err(),
        NetworkError::NoForwardProgress
    );
}
