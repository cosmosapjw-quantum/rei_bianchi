// Real frozen AX08 source b(t), source-free 4096-panel Simpson vs Taylor10.
// Standalone std-only benchmark, not full ODE runtime.
#[path = "fast_moments.rs"]
mod fast_moments;
use std::env;
use std::fs::File;
use std::hint::black_box;
use std::io::{BufRead, BufReader};
use std::time::Instant;

fn simpson_saved_model(b: f64) -> (f64, f64) {
    let ep = (2.0 * b).exp();
    let ez = (-4.0 * b).exp();
    let panels = 4096usize;
    let mut monopole = 0f64;
    let mut quad = 0f64;
    for i in 0..=panels {
        let mu = i as f64 / panels as f64;
        let r = ((1.0 - mu * mu) * ep + mu * mu * ez).sqrt();
        let local_mu = mu * ez.sqrt() / r;
        let w = if i == 0 || i == panels {
            1.0
        } else if i % 2 == 0 {
            2.0
        } else {
            4.0
        };
        monopole += w * r;
        quad += w * r * (3.0 * local_mu * local_mu - 1.0) / 2.0;
    }
    (
        monopole / (3.0 * panels as f64),
        quad / (3.0 * panels as f64),
    )
}
fn percentile_median(v: &mut [f64]) -> f64 {
    v.sort_by(|a, b| a.total_cmp(b));
    v[v.len() / 2]
}
fn read_b(path: &str, maxsamples: usize) -> Result<Vec<f64>, String> {
    let file = File::open(path).map_err(|x| x.to_string())?;
    let mut r = BufReader::with_capacity(1 << 20, file);
    let mut line = String::new();
    r.read_line(&mut line).map_err(|x| x.to_string())?;
    let header: Vec<_> = line.trim_end().split(',').collect();
    if header.get(6) != Some(&"b") || header.get(0) != Some(&"case_id") {
        return Err("NOT_ORIGINAL_AX08_B_REGISTRY".into());
    }
    let mut b = Vec::new();
    let mut rows = 0usize;
    loop {
        line.clear();
        if r.read_line(&mut line).map_err(|x| x.to_string())? == 0 {
            break;
        }
        if rows % 39 == 0 {
            let columns: Vec<_> = line.trim_end().split(',').collect();
            if columns.len() != 25 || columns[0] != "SHEAR_MINUS" {
                return Err("NOT_FROZEN_COMPLETED_SHEAR_MINUS".into());
            }
            let v: f64 = columns[6].parse().map_err(|x| format!("{x}"))?;
            if !v.is_finite() || v.abs() > 0.025 {
                return Err("B_OUTSIDE_FAST_CONTRACT".into());
            }
            b.push(v);
            if b.len() >= maxsamples {
                break;
            }
        }
        rows += 1;
    }
    if b.len() < 500 {
        return Err(format!("INSUFFICIENT_REAL_SAMPLES:{}", b.len()));
    }
    Ok(b)
}
fn main() -> Result<(), String> {
    let args: Vec<_> = env::args().collect();
    if args.len() != 2 {
        return Err("Usage: bench_fast_moments ABSOLUTE_FROZEN_HISTORY_CSV".into());
    }
    let b = read_b(&args[1], 8192)?;
    let mut max_e = 0f64;
    let mut max_p = 0f64;
    let mut l1_err_e = 0f64;
    let mut l1_err_p = 0f64;
    for &v in &b {
        let a = simpson_saved_model(v);
        let exact = fast_moments::fast_bianchi_i_initial_isotropic(1.0, v, 1.0, 0.0, 1.0)
            .map_err(|x| x.to_string())?;
        let e = (a.0 - exact.energy_j_m3).abs();
        let p = (a.1 - exact.pressure_over_isotropic).abs();
        max_e = max_e.max(e);
        max_p = max_p.max(p);
        l1_err_e += e;
        l1_err_p += p;
        if e > 2e-13 || p > 2e-13 {
            return Err(format!("MATCHED_SCIENCE_ERROR_HOLD:b={v}:err={e},{p}"));
        }
    }
    let mut r_s = Vec::new();
    let mut f_s = Vec::new();
    let mut sinks = [0f64; 2];
    for _ in 0..7 {
        let t = Instant::now();
        let mut acc = 0f64;
        for &v in &b {
            let r = simpson_saved_model(black_box(v));
            acc += black_box(r.0 + r.1);
        }
        r_s.push(t.elapsed().as_secs_f64());
        sinks[0] = black_box(acc);
        let t = Instant::now();
        let mut acc = 0f64;
        for &v in &b {
            let r =
                fast_moments::fast_bianchi_i_initial_isotropic(1.0, black_box(v), 1.0, 0.0, 1.0)
                    .map_err(|x| x.to_string())?;
            acc += black_box(r.energy_j_m3 + r.pressure_over_isotropic);
        }
        f_s.push(t.elapsed().as_secs_f64());
        sinks[1] = black_box(acc);
    }
    let ref_m = percentile_median(&mut r_s);
    let fast_m = percentile_median(&mut f_s);
    let count = b.len();
    if !sinks[0].is_finite() || !sinks[1].is_finite() {
        return Err("NONFINITE_BENCHMARK".into());
    }
    println!("{{\"schema\":\"rei.axbi.fast_small_shear_kernel.v1\",\"status\":\"MATCHED_REAL_B_PHYSICS_PASS\",\"n_samples\":{},\"max_abs_b\":{:.17e},\"mean_abs_energy_ratio_difference\":{:.17e},\"mean_abs_quadrupole_ratio_difference\":{:.17e},\"max_abs_energy_ratio_difference\":{:.17e},\"max_abs_quadrupole_ratio_difference\":{:.17e},\"legacy_simpson4096_median_s\":{:.9},\"fast_taylor14_median_s\":{:.9},\"kernel_speedup\":{:.5},\"sink_reference\":{:.17e},\"sink_fast\":{:.17e},\"not_full_ode_speedup\":true}}",
        count,b.iter().fold(0f64,|s,x|s.max(x.abs())),l1_err_e/count as f64,l1_err_p/count as f64,
        max_e,max_p,ref_m,fast_m,ref_m/fast_m,sinks[0],sinks[1]);
    Ok(())
}
