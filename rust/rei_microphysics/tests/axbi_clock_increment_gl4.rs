//! PR123 original AX03 source tests transported to actual legacy AX08 intervals.
#[path = "../../../research/axbi_goal_20261014/convergence/ax08_shortclock_20261015/clock_increment_gl4.rs"]
mod local_clock;
use local_clock::integrate_clock;
use rei_microphysics::axbi_background::{AxbiBackground, BackgroundFamily, Cosmology};
fn close(a: f64, b: f64, rtol: f64, atol: f64) {
    assert!(a.is_finite() && b.is_finite());
    assert!(
        (a - b).abs() <= atol + rtol * b.abs(),
        "a={a:0.16e},b={b:0.16e},diff={:0.6e}",
        a - b
    );
}
#[test]
fn real_saved_ax08_row15_to16_has_stable_clock() {
    // Immutable ZERO actual CSV accepted row15->16; independently calculated
    // GL4 source duration from current user-owned AX03 C8 source lock.
    let a0 = 0.04761904789152601;
    let a1 = 0.04761904790969124;
    let saved_source_dt = 3223208.118472241;
    let original_clock_gl4_truth = 3223206.3009491283;
    let x = integrate_clock(a0, a1, 0.0).unwrap();
    close(x.proper_seconds, original_clock_gl4_truth, 8e-15, 1e-8);
    assert_eq!(x.delta_b, 0.0);
    close(
        saved_source_dt - x.proper_seconds,
        1.8175231125205755,
        1e-7,
        1e-7,
    );
    let cosm = Cosmology {
        h0_per_s: 67.4e3 / 3.0856775814913673e22,
        omega_m: 0.315,
        omega_r: 9.2e-5,
        omega_lambda: 1.0 - 0.315 - 9.2e-5,
    };
    let bg = AxbiBackground::new(
        cosm,
        1.0 / 21.0,
        0.2,
        0.,
        0.,
        BackgroundFamily::PhysicalDensityFixed,
        4096,
    )
    .unwrap();
    let old = bg.point_at_scale(a1).unwrap().time_s - bg.point_at_scale(a0).unwrap().time_s;
    close(old, saved_source_dt, 1e-8, 1e-4);
    assert!((old - x.proper_seconds).abs() > 1.);
}
#[test]
fn signed_background_even_clock_odd_shear() {
    for i in 0..7 {
        let a0: f64 = 0.08 + i as f64 * 0.013;
        let a1 = a0 + 0.0001;
        let p = integrate_clock(a0, a1, 0.005).unwrap();
        let n = integrate_clock(a0, a1, -0.005).unwrap();
        assert_eq!(p.proper_seconds, n.proper_seconds);
        assert_eq!(p.delta_b, -n.delta_b);
        assert!(p.delta_b > 0.0);
        let z = integrate_clock(a0, a1, 0.0).unwrap();
        assert_eq!(z.delta_b, 0.0);
        assert!(z.proper_seconds > p.proper_seconds);
    }
}
#[test]
fn adjacent_float_time_increment_is_positive() {
    let a0 = 0.1_f64;
    let a1 = f64::from_bits(a0.to_bits() + 1);
    let out = integrate_clock(a0, a1, 0.01).unwrap();
    assert!(out.proper_seconds > 3.0 && out.proper_seconds < 4.0);
    assert!(out.delta_b > 0.0);
}
#[test]
fn invalid_source_or_clock_domain_rejected() {
    for q in [0.001, 0.01 + 1e-8, f64::NAN] {
        assert!(integrate_clock(0.1, 0.101, q).is_err());
    }
    for (a0, a1) in [
        (0.0, 0.1),
        (0.1, 0.1),
        (0.1, 0.09),
        (0.04, 0.1),
        (0.1, 0.201),
    ] {
        assert!(integrate_clock(a0, a1, 0.0).is_err());
    }
}
