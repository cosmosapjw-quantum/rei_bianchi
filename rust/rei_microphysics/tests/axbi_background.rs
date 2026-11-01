use rei_microphysics::axbi_background::*;
use rei_microphysics::{CharacteristicRay, GeometryBackground};
fn toy(q: f64, family: BackgroundFamily, n: usize) -> AxbiBackground {
    AxbiBackground::new(
        Cosmology {
            h0_per_s: 2e-18,
            omega_m: 1.0,
            omega_r: 0.0,
            omega_lambda: 0.0,
        },
        1.0 / 21.0,
        1.0 / 5.0,
        0.0,
        q,
        family,
        n,
    )
    .unwrap()
}
#[test]
fn matter_clock_and_flrw_limit() {
    let bg = toy(0.0, BackgroundFamily::PhysicalDensityFixed, 4096);
    let a = 1.0 / 5.0;
    let p = bg.point_at_scale(a).unwrap();
    let exact = 2.0 / (3.0 * 2e-18) * (a.powf(1.5) - (1.0_f64 / 21.0).powf(1.5));
    assert!((p.time_s / exact - 1.0).abs() < 1e-12);
    assert_eq!(p.b, 0.0);
    assert_eq!(p.sigma, 0.0);
    let inverse = bg.point_at_time(p.time_s * 0.5).unwrap();
    assert!((inverse.time_s / (p.time_s * 0.5) - 1.0).abs() < 1e-12);
    assert!(bg.snapshot(-1.0).is_err());
}
#[test]
fn density_constraint_signed_shear_and_refinement() {
    let plus = toy(0.01, BackgroundFamily::PhysicalDensityFixed, 4096);
    let minus = toy(-0.01, BackgroundFamily::PhysicalDensityFixed, 4096);
    let refined = toy(0.01, BackgroundFamily::PhysicalDensityFixed, 8192);
    let p = plus.point_at_scale(0.2).unwrap();
    let m = minus.point_at_scale(0.2).unwrap();
    let r = refined.point_at_scale(0.2).unwrap();
    assert!((p.h_per_s.powi(2) / (p.h_flrw_per_s.powi(2) + p.s_per_s.powi(2)) - 1.0).abs() < 1e-12);
    let initial = plus.point_at_scale(1.0 / 21.0).unwrap();
    assert!((p.s_per_s * p.a.powi(3) / (initial.s_per_s * initial.a.powi(3)) - 1.0).abs() < 1e-12);
    assert_eq!(p.h_per_s, m.h_per_s);
    assert_eq!(p.b, -m.b);
    assert!((p.time_s / r.time_s - 1.0).abs() < 1e-7);
    assert!((p.b - r.b).abs() < 1e-9);
    assert!((initial.sigma - 0.01 / (1.0001_f64).sqrt()).abs() < 1e-15);
    let same = toy(0.01, BackgroundFamily::SameHDiagnostic, 4096)
        .point_at_scale(0.2)
        .unwrap();
    assert_eq!(same.h_per_s, same.h_flrw_per_s);
    assert!(p.h_per_s > same.h_per_s);
    let g = p.geometry().unwrap();
    assert!((g.volume_factor().unwrap() / p.a.powi(3) - 1.0).abs() < 1e-12);
}
#[test]
fn reflection_even_ray_transport_preserves_parity() {
    let bg = toy(0.01, BackgroundFamily::PhysicalDensityFixed, 64);
    let g0 = bg.point_at_scale(1.0 / 21.0).unwrap().geometry().unwrap();
    let g1 = bg.point_at_scale(0.2).unwrap().geometry().unwrap();
    let a = CharacteristicRay::new(30.0, [0.8, 0.0, 0.6], 1.0)
        .unwrap()
        .pullback(&g0, &g1)
        .unwrap();
    let b = CharacteristicRay::new(30.0, [0.8, 0.0, -0.6], 1.0)
        .unwrap()
        .pullback(&g0, &g1)
        .unwrap();
    assert_eq!(a.energy_ev, b.energy_ev);
    assert_eq!(a.direction[2], -b.direction[2]);
    assert!(
        (a.energy_ev * a.direction[2] + b.energy_ev * b.direction[2]).abs() / a.energy_ev < 1e-12
    );
}
#[test]
fn feedback_zero_nonzero_and_missing_history() {
    let bg = toy(0.0, BackgroundFamily::PhysicalDensityFixed, 64);
    let p = bg.point_at_scale(0.2).unwrap();
    let first = FeedbackSample {
        a: 1.0 / 21.0,
        time_s: 0.0,
        pressure_anisotropy_j_m3: 0.0,
        extra_energy_j_m3: 0.0,
    };
    let mut last = FeedbackSample {
        a: 0.2,
        time_s: p.time_s,
        ..first
    };
    let zero = omitted_feedback(&bg, &[first, last], 6.67430e-11, 299792458.0).unwrap();
    assert_eq!(zero.max_abs_delta_s_over_h, 0.0);
    last.pressure_anisotropy_j_m3 = 1e-20;
    last.extra_energy_j_m3 = 1e-20;
    let nonzero = omitted_feedback(&bg, &[first, last], 6.67430e-11, 299792458.0).unwrap();
    assert!(nonzero.max_abs_delta_s_over_h > 0.0);
    assert!(nonzero.max_extra_energy_over_background > 0.0);
    assert!(omitted_feedback(&bg, &[], 6.67430e-11, 299792458.0).is_err());
}
#[test]
fn invalid_input_rejected() {
    assert!(AxbiBackground::new(
        Cosmology {
            h0_per_s: f64::NAN,
            omega_m: 1.0,
            omega_r: 0.0,
            omega_lambda: 0.0
        },
        0.1,
        0.2,
        0.0,
        0.0,
        BackgroundFamily::PhysicalDensityFixed,
        64
    )
    .is_err());
    assert!(toy(0.0, BackgroundFamily::PhysicalDensityFixed, 64)
        .point_at_scale(0.3)
        .is_err());
}

#[test]
fn initially_isotropic_radiation_stress_small_b_limit() {
    let zero = isotropic_initial_radiation_moments(0.1, 0.0, 0.05, 0.0, 16.0, 4096).unwrap();
    assert_eq!(zero.energy_j_m3, 1.0);
    assert!(zero.pressure_anisotropy_j_m3.abs() < 1e-12);
    let b = 1e-6;
    let plus = isotropic_initial_radiation_moments(0.1, b, 0.05, 0.0, 16.0, 4096).unwrap();
    let minus = isotropic_initial_radiation_moments(0.1, -b, 0.05, 0.0, 16.0, 4096).unwrap();
    assert!((plus.pressure_anisotropy_j_m3 / (-8.0 * b / 5.0) - 1.0).abs() < 1e-5);
    assert!(plus.pressure_anisotropy_j_m3 < 0.0);
    assert!(minus.pressure_anisotropy_j_m3 > 0.0);
    assert!(plus.energy_j_m3 > 0.0);
    assert_eq!(plus.dipole_energy_j_m3, 0.0);
    assert_eq!(plus.signed_energy_correction_j_m3, plus.energy_j_m3 - 1.0);
}
