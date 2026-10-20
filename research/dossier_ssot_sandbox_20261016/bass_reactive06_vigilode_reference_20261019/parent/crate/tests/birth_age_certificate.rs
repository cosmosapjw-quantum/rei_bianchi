use rei_iso_couple_reference::birth_age_certificate::{compare_fitted, compare_nodes};
use rei_iso_couple_reference::fitted_birth;
use rei_iso_couple_reference::full_network::NetworkError;

fn close(actual: f64, expected: f64, tolerance: f64) {
    assert!(
        (actual - expected).abs() <= tolerance,
        "actual={actual:.17e}, expected={expected:.17e}, tolerance={tolerance:.4e}"
    );
}

#[test]
fn uniform_single_atom_has_exact_cdf_w1_and_moment_defects() {
    let result = compare_nodes(0.0, 7.0, &[(0.5, 1.0)]).unwrap();
    let shape = result.emitted.shape.unwrap();
    close(result.emitted.discrete_mass, 7.0, 0.0);
    close(result.emitted.exact_mass, 7.0, 0.0);
    close(shape.cdf_sup, 0.5, 0.0);
    close(shape.w1, 0.25, 0.0);
    close(shape.signed_moment_defects[0], 0.0, 0.0);
    close(shape.signed_moment_defects[1], -1.0 / 12.0, 6e-17);
}

#[test]
fn transparent_gl2_exact_moments_do_not_remove_distribution_error() {
    let shape = compare_fitted(0.0, 1.0, 1).unwrap().emitted.shape.unwrap();
    close(shape.signed_moment_defects[0], 0.0, 2e-16);
    close(shape.signed_moment_defects[1], 0.0, 2e-16);
    close(shape.cdf_sup, 1.0 / (2.0 * 3.0_f64.sqrt()), 2e-16);
    close(shape.w1, 5.0 / 12.0 - 1.0 / (2.0 * 3.0_f64.sqrt()), 2e-16);
}

#[test]
fn transparent_panel_refinement_has_analytic_inverse_length_scaling() {
    let ks_one = 1.0 / (2.0 * 3.0_f64.sqrt());
    let w1_one = 5.0 / 12.0 - ks_one;
    for refinement in [1, 2, 4, 8, 16] {
        let result = compare_fitted(0.0, 1.0, refinement).unwrap();
        let shape = result.survivors.shape.unwrap();
        close(shape.cdf_sup, ks_one / refinement as f64, 3e-16);
        close(shape.w1, w1_one / refinement as f64, 3e-16);
    }
}

#[test]
fn global_timestep_age_mapping_preserves_the_uniform_reference_contract() {
    for nsteps in [1, 4, 16] {
        for refinement in [1, 4, 16] {
            let local = fitted_birth::rule(0.0, refinement).unwrap();
            let nodes: Vec<_> = (0..nsteps)
                .flat_map(|step| {
                    local
                        .iter()
                        .map(move |(x, w)| ((step as f64 + x) / nsteps as f64, w / nsteps as f64))
                })
                .collect();
            let shape = compare_nodes(0.0, 1.0, &nodes)
                .unwrap()
                .emitted
                .shape
                .unwrap();
            let ks = 1.0 / (2.0 * 3.0_f64.sqrt());
            close(shape.cdf_sup, ks / (nsteps * refinement) as f64, 4e-16);
            close(
                shape.w1,
                (5.0 / 12.0 - ks) / (nsteps * refinement) as f64,
                4e-16,
            );
        }
    }
}

#[test]
fn changing_mass_does_not_hide_or_change_the_normalized_shape() {
    let nodes = fitted_birth::rule(17.0, 4).unwrap();
    let twice: Vec<_> = nodes.iter().map(|(x, w)| (*x, 2.0 * w)).collect();
    let reference = compare_nodes(17.0, 3.0, &nodes).unwrap();
    let rescaled = compare_nodes(17.0, 3.0, &twice).unwrap();
    close(rescaled.emitted.relative_mass_defect.unwrap(), 1.0, 2e-15);
    close(rescaled.survivors.relative_mass_defect.unwrap(), 1.0, 2e-14);
    let a = reference.survivors.shape.unwrap();
    let b = rescaled.survivors.shape.unwrap();
    close(a.cdf_sup, b.cdf_sup, 2e-15);
    close(a.w1, b.w1, 2e-15);
    close(a.discrete_moments[0], b.discrete_moments[0], 2e-15);
}

#[test]
fn unordered_and_repeated_atoms_are_only_sorted_for_diagnostics() {
    let input = [(0.8, 0.1), (0.2, 0.3), (0.8, 0.3), (0.2, 0.3)];
    let copy = input;
    let a = compare_nodes(3.0, 1.0, &input).unwrap();
    let b = compare_nodes(3.0, 1.0, &[(0.2, 0.6), (0.8, 0.4)]).unwrap();
    assert_eq!(input, copy);
    let a = a.survivors.shape.unwrap();
    let b = b.survivors.shape.unwrap();
    close(a.cdf_sup, b.cdf_sup, 3e-15);
    close(a.w1, b.w1, 3e-15);
    close(a.discrete_moments[1], b.discrete_moments[1], 3e-15);
}

#[test]
fn empty_quadrature_reports_mass_loss_and_undefined_shape() {
    let result = compare_nodes(2.0, 3.0, &[]).unwrap();
    assert_eq!(result.positive_nodes, 0);
    assert_eq!(result.emitted.relative_mass_defect, Some(-1.0));
    assert_eq!(result.survivors.relative_mass_defect, Some(-1.0));
    assert_eq!(result.survivors.discrete_mass, 0.0);
    assert!(result.survivors.exact_mass > 0.0);
    assert!(result.emitted.shape.is_none());
    assert!(result.survivors.shape.is_none());
    let zero = compare_nodes(2.0, 3.0, &[(0.25, 0.0)]).unwrap();
    assert_eq!(zero.positive_nodes, 0);
    assert!(zero.survivors.shape.is_none());
}

#[test]
fn zero_source_has_zero_mass_and_no_normalized_shape() {
    for nodes in [vec![], vec![(0.25, 1.0)]] {
        let result = compare_nodes(1e12, 0.0, &nodes).unwrap();
        for measure in [result.emitted, result.survivors] {
            assert_eq!(measure.discrete_mass, 0.0);
            assert_eq!(measure.exact_mass, 0.0);
            assert!(measure.relative_mass_defect.is_none());
            assert!(measure.log_mass_ratio.is_none());
            assert!(measure.shape.is_none());
        }
    }
}

#[test]
fn zero_opacity_and_subnormal_opacity_reproduce_uniform_diagnostics() {
    let nodes = [(0.1, 0.3), (0.7, 0.7)];
    let uniform = compare_nodes(0.0, 1.0, &nodes).unwrap();
    let transparent = uniform.survivors.shape.unwrap();
    close(uniform.emitted.shape.unwrap().w1, transparent.w1, 0.0);
    let small = compare_nodes(f64::from_bits(1), 1.0, &nodes)
        .unwrap()
        .survivors
        .shape
        .unwrap();
    close(small.cdf_sup, transparent.cdf_sup, 1e-15);
    close(small.w1, transparent.w1, 1e-15);
    close(small.exact_moments[0], 0.5, 1e-15);
}

#[test]
fn an_endpoint_atom_tests_the_exact_exponential_mean() {
    for tau in [1e-10, 0.1, 1.0, 3.0, 100.0, 1e12] {
        let result = compare_nodes(tau, 1.0, &[(0.0, 1.0)]).unwrap();
        let shape = result.survivors.shape.unwrap();
        close(shape.w1, shape.exact_moments[0], 2e-14);
        close(shape.cdf_sup, 1.0, 0.0);
    }
}

#[test]
fn huge_opacity_keeps_representable_w1_positive() {
    let tau = 1e300;
    let endpoint = compare_nodes(tau, 1.0, &[(0.0, 1.0)]).unwrap();
    let shape = endpoint.survivors.shape.unwrap();
    close(shape.w1 / (1.0 / tau), 1.0, 1e-14);
    let mean_atom = compare_nodes(tau, 1.0, &[(1.0 / tau, 1.0)]).unwrap();
    let expected = (2.0 / std::f64::consts::E) / tau;
    close(mean_atom.survivors.shape.unwrap().w1 / expected, 1.0, 1e-14);
}

#[test]
fn absolute_survivor_underflow_does_not_fabricate_an_empty_shape() {
    let result = compare_nodes(1000.0, 1.0, &[(1.0, 1.0)]).unwrap();
    assert_eq!(result.survivors.discrete_mass, 0.0);
    assert!(result.survivors.absolute_mass_underflow);
    assert!(result.survivors.log_mass_ratio.unwrap() < -900.0);
    let shape = result.survivors.shape.unwrap();
    close(shape.w1, 0.999, 3e-15);
    close(shape.discrete_moments[0], 1.0, 0.0);
}

#[test]
fn negative_and_nonfinite_inputs_are_rejected_without_clipping() {
    for (tau, born, nodes) in [
        (-1.0, 1.0, vec![]),
        (f64::INFINITY, 1.0, vec![]),
        (f64::NAN, 1.0, vec![]),
        (1.0, -1.0, vec![]),
        (1.0, f64::NAN, vec![]),
        (1.0, 1.0, vec![(-0.1, 1.0)]),
        (1.0, 1.0, vec![(1.1, 1.0)]),
        (1.0, 1.0, vec![(f64::NAN, 1.0)]),
        (1.0, 1.0, vec![(0.5, -1.0)]),
        (1.0, 1.0, vec![(0.5, f64::INFINITY)]),
    ] {
        assert!(matches!(
            compare_nodes(tau, born, &nodes),
            Err(NetworkError::InvalidInput)
        ));
    }
    assert!(matches!(
        compare_fitted(1.0, 1.0, 3),
        Err(NetworkError::InvalidInput)
    ));
}

#[test]
fn fitted_representation_limit_propagates_as_numerical_resolution() {
    assert!(matches!(
        compare_fitted(1e300, 1.0, 1),
        Err(NetworkError::NoForwardProgress)
    ));
}

#[test]
fn lipschitz_moment_bounds_and_mass_witness_hold_across_opacity_scales() {
    for tau in [0.0, 1e-12, 0.1, 1.0, 10.0, 1e4, 1e12] {
        for refinement in [1, 2, 4, 8, 16] {
            let result = compare_fitted(tau, 1.0, refinement).unwrap();
            assert!(result.survivors.relative_mass_defect.unwrap().abs() < 2e-12);
            for measure in [result.emitted, result.survivors] {
                let shape = measure.shape.unwrap();
                assert!(shape.w1 <= shape.cdf_sup + 2e-14);
                assert!(shape.signed_moment_defects[0].abs() <= shape.w1 + 2e-14);
                assert!(shape.signed_moment_defects[1].abs() <= 2.0 * shape.w1 + 2e-14);
                assert!(shape.cdf_sup > 0.0);
                assert!(shape.w1 > 0.0);
            }
        }
    }
}
