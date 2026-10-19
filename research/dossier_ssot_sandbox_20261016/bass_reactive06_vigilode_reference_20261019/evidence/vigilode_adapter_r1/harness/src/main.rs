use br06_recovery_moment_kernel::{
    adapter::{MomentWork, positive_moment_table},
    damped_moments::compute_normalized_damped_moment,
    directed::{Interval, sub_up},
};

fn row(kind: &str, tau: f64, j: usize, k: usize, result: Result<Interval, String>) {
    match result {
        Ok(v) => println!(
            "{kind},{tau:.17e},{j},{k},{:.17e},{:.17e},{:.17e},ok",
            v.lo,
            v.hi,
            sub_up(v.hi, v.lo).expect("finite interval width")
        ),
        Err(error) => println!(
            "{kind},{tau:.17e},{j},{k},0,0,0,\"{}\"",
            error.replace('"', "\"\"")
        ),
    }
}

fn main() {
    let taus = [
        0.0, 1e-12, 1e-8, 0.03, 0.5, 1.0, 1.000001, 2.0, 10.0, 32.0, 93.0, 156.0, 1e3, 1e12,
    ];
    println!("kind,tau,j,k,lo,hi,width,status");
    for tau in taus {
        let mut work = MomentWork::default();
        let table = positive_moment_table(tau, 1e-10, 0.0, &mut work);
        eprintln!(
            "tau={tau:.17e},validation={},kernel={},exp={},dyadic={},interval_ops={},width={}",
            work.validation_attempts,
            work.kernel_calls,
            work.exponential_calls,
            work.dyadic_steps,
            work.interval_operations,
            work.width_checks
        );
        for j in 0..=2 {
            for k in 0..=2 {
                row(
                    "dyadic",
                    tau,
                    j,
                    k,
                    table
                        .as_ref()
                        .map(|t| t.get(j, k))
                        .map_err(ToString::to_string),
                );
                row(
                    "direct",
                    tau,
                    j,
                    k,
                    compute_normalized_damped_moment(tau, 1.0, j, k).map_err(|e| e.to_string()),
                );
            }
        }
    }
}
