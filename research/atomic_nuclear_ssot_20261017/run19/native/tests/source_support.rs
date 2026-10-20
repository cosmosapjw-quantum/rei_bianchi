use rei_iso_couple_reference::{
    birth_layers::graded_birth_nodes, source_support::refined_birth_nodes,
};
#[test]
fn requested_subdivision_changes_native_birth_support() {
    let base = graded_birth_nodes(359.22363635035254, 2., 128).unwrap();
    let fine = refined_birth_nodes(359.22363635035254, 2., 128, 2).unwrap();
    assert_eq!(
        fine.len(),
        2 * base.len(),
        "subdivision must refine rather than replay the parent support"
    );
}
#[test]
fn unrefined_is_bitwise_parent() {
    for tau in [0., 0.1, 1., 359.22363635035254, 1e12] {
        let a = graded_birth_nodes(tau, 2., 128).unwrap();
        let b = refined_birth_nodes(tau, 2., 128, 1).unwrap();
        for (x, y) in a.iter().zip(&b) {
            assert_eq!(
                x.remaining_fraction.to_bits(),
                y.remaining_fraction.to_bits()
            );
            assert_eq!(x.weight.to_bits(), y.weight.to_bits());
        }
    }
}
#[test]
fn child_panels_tile_parent_exactly() {
    use rei_iso_couple_reference::{birth_layers::graded_panels, source_support::refined_panels};
    let base = graded_panels(359.22363635035254, 2., 128).unwrap();
    for r in [2, 3, 4, 8] {
        let fine = refined_panels(359.22363635035254, 2., 128, r).unwrap();
        for (j, (a, b)) in base.iter().enumerate() {
            assert_eq!(fine[j * r].0, *a);
            assert_eq!(fine[j * r + r - 1].1, *b);
        }
        for pair in fine.windows(2) {
            assert_eq!(pair[0].1, pair[1].0);
        }
    }
}
#[test]
fn positive_complete_seventh_degree_moments() {
    for tau in [0., 359.22363635035254, 1e12] {
        for r in [2, 4, 8] {
            let nodes = refined_birth_nodes(tau, 2., 4096, r).unwrap();
            assert!(
                nodes.iter().all(|n| n.weight > 0.
                    && n.remaining_fraction > 0.
                    && n.remaining_fraction < 1.)
            );
            for k in 0..=7 {
                let v = nodes
                    .iter()
                    .map(|n| n.weight * n.remaining_fraction.powi(k))
                    .sum::<f64>();
                assert!((v - 1. / (k + 1) as f64).abs() < 2e-14);
            }
        }
    }
}
#[test]
fn refinement_and_total_resource_budget_reject() {
    for r in [0, 65, usize::MAX] {
        assert!(refined_birth_nodes(359., 2., 128, r).is_err());
    }
    assert!(refined_birth_nodes(359., 2., 15, 2).is_err());
    for tau in [-1., f64::NAN, f64::INFINITY] {
        assert!(refined_birth_nodes(tau, 2., 128, 2).is_err());
    }
}
#[test]
fn fixed_opacity_survival_refines_not_rescaled() {
    let tau = 1000.0_f64;
    let exact = -(-tau).exp_m1() / tau;
    let mut prior = f64::INFINITY;
    for r in [1, 2, 4] {
        let nodes = refined_birth_nodes(tau, 2., 128, r).unwrap();
        let s = nodes
            .iter()
            .map(|n| n.weight * (-tau * n.remaining_fraction).exp())
            .sum::<f64>();
        let error = (s / exact - 1.).abs();
        assert!(error < prior);
        prior = error;
    }
    assert!(prior < 1e-10);
}
