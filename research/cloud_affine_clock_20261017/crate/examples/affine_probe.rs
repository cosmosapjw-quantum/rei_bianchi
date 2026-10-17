use rei_iso_couple_reference::affine_birth_clock::advance_affine;
fn main() {
    println!("case,steps,j0,j1,l0,l1,old,surviving,absorbed,injected");
    for (case, j0, j1, l0, l1) in [
        ("increasing", 0.6, 0.9, 0.2, 0.8),
        ("decreasing", 1.2, 0.3, 0.9, 0.1),
        ("crossed", 0.1, 1.4, 0.8, 0.2),
        ("constant", 0.8, 0.8, 0.5, 0.5),
    ] {
        for n in [1, 2, 4, 8, 16, 32] {
            let mut current = 0.7;
            let mut absorb = 0.;
            let mut inject = 0.;
            let h = 1. / n as f64;
            for i in 0..n {
                let a = i as f64 * h;
                let b = (i + 1) as f64 * h;
                let r = advance_affine(
                    current,
                    (1. - a) * j0 + a * j1,
                    (1. - b) * j0 + b * j1,
                    (1. - a) * l0 + a * l1,
                    (1. - b) * l0 + b * l1,
                    h,
                )
                .unwrap();
                current = r.surviving;
                absorb += r.absorbed;
                inject += r.injected;
            }
            println!(
                "{case},{n},{j0:.17e},{j1:.17e},{l0:.17e},{l1:.17e},7e-1,{current:.17e},{absorb:.17e},{inject:.17e}"
            );
        }
    }
}
