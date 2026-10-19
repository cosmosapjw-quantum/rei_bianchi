use rei_iso_couple_reference::{
    birth_layers::{constant_survival_error_bound, graded_birth_nodes},
    retarded_transport::gauss_birth_nodes,
};
fn main() {
    println!(
        "seed_tau,actual_tau,method,node_count,weight_sum,survivor,absorbed,constant_GL4_bound"
    );
    for seed in [
        0.0, 1e-12, 1e-6, 1e-3, 1.0, 10.0, 100.0, 1e3, 1e6, 1e10, 1e12,
    ] {
        for ratio in [0.001, 0.1, 1.0] {
            let tau = seed * ratio;
            for growth in [0.0, 1.0, 2.0, 1.5, 1.25] {
                let (method, points, bound) = if growth <= 1.0 {
                    let ng = if growth == 0.0 { 2 } else { 4 };
                    (
                        format!("uniform{ng}"),
                        gauss_birth_nodes(ng).unwrap(),
                        f64::NAN,
                    )
                } else {
                    (
                        format!("graded{growth}"),
                        graded_birth_nodes(seed, growth, 128)
                            .unwrap()
                            .into_iter()
                            .map(|n| (n.remaining_fraction, n.weight))
                            .collect(),
                        constant_survival_error_bound(tau, seed, growth, 128).unwrap(),
                    )
                };
                let sum = points.iter().map(|n| n.1).sum::<f64>();
                let surv = points.iter().map(|n| n.1 * (-tau * n.0).exp()).sum::<f64>();
                let abs = points
                    .iter()
                    .map(|n| n.1 * (-(-tau * n.0).exp_m1()))
                    .sum::<f64>();
                println!(
                    "{seed:.17e},{tau:.17e},{method},{},{sum:.17e},{surv:.17e},{abs:.17e},{bound:.17e}",
                    points.len()
                );
            }
        }
    }
}
