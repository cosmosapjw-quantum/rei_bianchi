//! Scoped CPU comparison: original cumulative Simpson vs new physical local GL4,
//! with optional real std::thread splits. Not a complete H/He solver benchmark.
use rei_microphysics::axbi_background::{AxbiBackground, BackgroundFamily, Cosmology};
use std::hint::black_box;
use std::time::Instant;

#[derive(Clone, Copy)]
struct Row {
    case: usize,
    a0: f64,
    a1: f64,
    dt80: f64,
}
fn cosmo() -> Cosmology {
    Cosmology {
        h0_per_s: 2.1842852410855026e-18,
        omega_m: 0.315,
        omega_r: 9.2e-5,
        omega_lambda: 0.6849080000000001,
    }
}
fn setup() -> (Vec<AxbiBackground>, Vec<Row>) {
    let candidates = [
        (0.0, BackgroundFamily::PhysicalDensityFixed),
        (0.005, BackgroundFamily::PhysicalDensityFixed),
        (-0.005, BackgroundFamily::PhysicalDensityFixed),
        (0.01, BackgroundFamily::PhysicalDensityFixed),
        (-0.01, BackgroundFamily::PhysicalDensityFixed),
        (0.01, BackgroundFamily::SameHDiagnostic),
    ];
    let backgrounds: Vec<_> = candidates
        .iter()
        .map(|&(q, f)| AxbiBackground::new(cosmo(), 1.0 / 21.0, 0.2, 0.0, q, f, 4096).unwrap())
        .collect();
    let fixture = include_str!("../tests/fixtures/axbi_c9_clock_mp80_90.csv");
    let mut rows = Vec::new();
    for line in fixture.lines().skip(1) {
        let c: Vec<&str> = line.split(',').collect();
        assert_eq!(c.len(), 6);
        let family = match c[0] {
            "PhysicalDensityFixed" => BackgroundFamily::PhysicalDensityFixed,
            "SameHDiagnostic" => BackgroundFamily::SameHDiagnostic,
            _ => panic!("invalid"),
        };
        let q: c64 = c[1].parse().unwrap();
        let idx = candidates
            .iter()
            .position(|&(a, b)| a == q && b == family)
            .unwrap();
        rows.push(Row {
            case: idx,
            a0: c[2].parse().unwrap(),
            a1: c[3].parse().unwrap(),
            dt80: c[4].parse().unwrap(),
        });
    }
    assert_eq!(rows.len(), 90);
    (backgrounds, rows)
}
type c64 = f64;
fn calc(rows: &[Row], backgrounds: &[AxbiBackground], old: bool) -> Vec<f64> {
    rows.iter()
        .map(|r| {
            let b = &backgrounds[r.case];
            let dt = if old {
                b.point_at_scale(r.a1).unwrap().time_s - b.point_at_scale(r.a0).unwrap().time_s
            } else {
                b.proper_time_increment(r.a0, r.a1).unwrap()
            };
            black_box(dt)
        })
        .collect()
}
fn threaded(rows: &[Row], backgrounds: &[AxbiBackground], n: usize) -> Vec<f64> {
    let chunk = rows.len().div_ceil(n);
    std::thread::scope(|scope| {
        let mut tasks = Vec::new();
        for piece in rows.chunks(chunk) {
            tasks.push(scope.spawn(move || calc(piece, backgrounds, false)));
        }
        tasks
            .into_iter()
            .flat_map(|x| x.join().unwrap())
            .collect::<Vec<f64>>()
    })
}
fn median(mut samples: Vec<f64>) -> f64 {
    samples.sort_by(|x, y| x.total_cmp(y));
    samples[samples.len() / 2]
}
fn measure<F: Fn() -> Vec<f64>>(name: &str, call: F, n: usize) -> f64 {
    let origin = call();
    assert_eq!(origin.len(), 90);
    let mut measures = Vec::new();
    let mut checksum = 0.;
    for _ in 0..n {
        let t = Instant::now();
        let v = call();
        let ms = t.elapsed().as_secs_f64();
        checksum += black_box(v.iter().sum::<f64>() * 1e-16);
        measures.push(ms);
    }
    let m = median(measures);
    println!("{{\"mode\":\"{name}\",\"median_s\":{m:.17e},\"repetitions\":{n},\"checksum\":{checksum:.17e}}}");
    m
}
fn main() {
    let (background, rows) = setup();
    let reference = calc(&rows, &background, false);
    let old = calc(&rows, &background, true);
    let worst_old = old
        .iter()
        .zip(&rows)
        .map(|(&x, r)| (x / r.dt80 - 1.).abs())
        .fold(0.0_f64, f64::max);
    let worst_new = reference
        .iter()
        .zip(&rows)
        .map(|(&x, r)| (x / r.dt80 - 1.).abs())
        .fold(0.0_f64, f64::max);
    let bad_old = old
        .iter()
        .zip(&rows)
        .filter(|(x, r)| ((*x / r.dt80) - 1.).abs() > 1e-8)
        .count();
    assert!(worst_new < 4e-13);
    assert!(worst_old > 0.1);
    assert!(bad_old > 20);
    for n in [2, 4] {
        let parallel = threaded(&rows, &background, n);
        assert_eq!(
            reference, parallel,
            "parallel must preserve numerical identity"
        );
    }
    println!("{{\"schema\":\"rei.axbi.c9.native_source_clock_benchmark.v1\",\"n_intervals\":90,\"max_naive_relative_error\":{worst_old:.17e},\"max_new_relative_error\":{worst_new:.17e},\"n_naive_gt1e_8\":{bad_old}}}");
    measure(
        "original_two_Simpson4096_point_subtraction",
        || calc(&rows, &background, true),
        3,
    );
    measure(
        "local_Gauss4_serial",
        || calc(&rows, &background, false),
        21,
    );
    measure(
        "local_Gauss4_thread2",
        || threaded(&rows, &background, 2),
        21,
    );
    measure(
        "local_Gauss4_thread4",
        || threaded(&rows, &background, 4),
        21,
    );
}
