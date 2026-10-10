pub fn one_minus_phi1(t: f64) -> f64 {
    if t == 0.0 { return 0.0; }
    const SMALL_T: f64 = 0.01;
    if t < SMALL_T {
        let mut sum: f64 = t / 2.0;
        let mut term: f64 = t / 2.0;
        let mut n: i32 = 1;
        loop {
            term *= -t / (n as f64 + 2.0);
            sum += term;
            n += 1;
            if n > 6 || term.abs() < sum.abs() * 1e-16 { break; }
        }
        sum
    } else {
        1.0 - (-(-t).exp_m1()) / t
    }
}