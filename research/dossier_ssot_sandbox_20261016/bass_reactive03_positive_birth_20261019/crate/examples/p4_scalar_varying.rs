use rei_iso_couple_reference::retarded_transport::scalar_duhamel;
fn main() {
    println!("case,steps,birth_gl,opacity_substeps,emitted,survivors,absorbed,number_residual");
    for case in ["linear_kappa", "smooth_kappa_j", "constant", "zero"] {
        for n in [2usize, 4, 8, 16, 32, 64] {
            for (bq, kq) in [(2, 1), (4, 1), (4, 4), (4, 8)] {
                let source = |t: f64| match case {
                    "smooth_kappa_j" => 1.7 * (1. + 0.25 * t * t),
                    _ => 1.7,
                };
                let opacity = |t: f64| match case {
                    "linear_kappa" => 0.3 + 1.1 * t,
                    "smooth_kappa_j" => 0.3 + 1.1 * t + 0.7 * t * t,
                    "constant" => 0.3,
                    _ => 0.,
                };
                let mut s = 2.3_f64;
                let mut e = 0.;
                let mut a = 0.;
                for i in 0..n {
                    let t = i as f64 / n as f64;
                    let out = scalar_duhamel(t, 1. / n as f64, s, bq, kq, source, opacity).unwrap();
                    s = out.survivors;
                    e += out.emitted;
                    a += out.absorbed;
                }
                println!(
                    "{case},{n},{bq},{kq},{e:.16e},{s:.16e},{a:.16e},{:.16e}",
                    ((e + 2.3) - (s + a)).abs() / (e + 2.3)
                );
            }
        }
    }
}
