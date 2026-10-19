//! Frozen scalar source-age diagnostic using original native phi and birth nodes.
use rei_iso_couple_reference::{
    positive_birth_clock::photon_slab, retarded_transport::gauss_birth_nodes,
};
fn main() {
    println!("birth_GL,tau,exact_phi,birth_gauss,relative_survivor_deficit,number_ledger");
    for q in [2, 4] {
        for tau in [1e-4, 0.01, 0.1, 1., 3., 10., 30., 100., 300., 1000.] {
            let exact = photon_slab(tau).unwrap().new_surviving;
            let approx = gauss_birth_nodes(q)
                .unwrap()
                .iter()
                .map(|(u, w)| w * (-tau * (1. - u)).exp())
                .sum::<f64>();
            println!(
                "{q},{tau:.17e},{exact:.17e},{approx:.17e},{:.17e},{:.17e}",
                1. - approx / exact,
                approx + (1. - approx) - 1.
            );
        }
    }
}
