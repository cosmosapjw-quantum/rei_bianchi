pub fn one_minus_phi1(t: f64) -> f64 {
    const SMALL_T: f64 = 0.01;
    if t < SMALL_T {
        let mut sum: f64 = 0.0;
        let mut term: f64 = t;
        let mut n: i32 = 1;
        loop {
            sum += term;
            term *= -t / (n + 1) as f64;
            n += 1;
            if term.abs() < sum.abs() * 1e-16 { break; }
        }
        sum
    } else {
        1.0 - (-(-t).exp_m1()) / t
    }
}