// Runtime capability smoke only: PHYS72 exact Python remains authoritative.
fn main() {
    let q: f64 = 553311.0 / 1.0e26;
    let delta: f64 = 3.0e-23;
    let tail: f64 = 5929.0 * delta / 2.0 * q * q * q / (1.0 - q);
    let expected: f64 = 1.5065398437838842e-80;
    let relative_error = (tail / expected - 1.0).abs();
    assert!(q.is_finite() && q > 0.0 && q < 1.0);
    assert!(relative_error < 1.0e-14);
    let workers = std::thread::available_parallelism().map(|n| n.get()).unwrap_or(1);
    println!("{{\"q_f64\":{:.17e},\"tail_f64\":{:.17e},\"relative_error\":{:.17e},\"available_parallelism\":{},\"certified\":false}}", q, tail, relative_error, workers);
}
