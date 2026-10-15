//! Independent Rust RHS against actual Python DOP853 solved source-free states.
#[path = "../../../research/axbi_goal_20261014/anisotropic_stress_20261015/sigma_pi_rhs.rs"]
mod stress;
use stress::{evaluate, initial, validate, State, StressModel, RHO_CRIT};
fn close(x: f64, y: f64, tol_rel: f64, tol_abs: f64) {
    assert!(x.is_finite() && y.is_finite(), "nonfinite");
    assert!(
        (x - y).abs() <= tol_abs + tol_rel * y.abs(),
        "x={x:.17e}, y={y:.17e}, abs_diff={:.8e}",
        (x - y).abs()
    );
}
#[test]
fn cross_language_108_real_coupled_trajectory_rhs_golden() {
    let bytes=include_str!("../../../research/axbi_goal_20261014/anisotropic_stress_20261015/results/rhs_frozen_golden.csv");
    let mut count = 0;
    for line in bytes.lines().skip(1) {
        if line.is_empty() {
            continue;
        }
        let fields: Vec<_> = line.split(',').collect();
        assert_eq!(fields.len(), 17);
        let values: Vec<f64> = fields.iter().map(|s| s.parse::<f64>().unwrap()).collect();
        let model = StressModel {
            Sigma_ref: values[0],
            orientation: values[1] as i8,
            free_radiation_fraction: values[2],
            matter_viscosity_strength: values[3],
        };
        validate(model).unwrap();
        let s = State {
            b: values[5],
            signed_s_over_HREF: values[6],
            thermal_energy_over_rhocrit: values[7],
            proper_time_times_HREF: values[8],
        };
        let r = evaluate(model, values[4], s).unwrap();
        let expected = [
            values[9], values[10], values[11], values[12], values[13], values[14], values[15],
            values[16],
        ];
        let actual = [
            r.d_b_dlog_a,
            r.d_signed_s_HREF_dlog_a,
            r.d_thermal_energy_dlog_a,
            r.d_proper_time_HREF_dlog_a,
            r.H_per_s,
            r.Sigma,
            r.radiation_pi_J_m3,
            r.matter_pi_J_m3,
        ];
        for (i, (&x, &y)) in actual.iter().zip(expected.iter()).enumerate() {
            let atol = match i {
                4 => 1e-30,
                6 | 7 => 1e-26,
                2 => 1e-15,
                _ => 1e-13,
            };
            close(x, y, 2e-12, atol)
        }
        count += 1;
    }
    assert_eq!(count, 108);
}
#[test]
fn exact_convention_sigma_stress_free_and_energy_heating_positive() {
    let sig = (3.0f64).sqrt() * 0.01 / 1.0001f64.sqrt();
    let model = StressModel {
        Sigma_ref: sig,
        orientation: 1,
        free_radiation_fraction: 1.,
        matter_viscosity_strength: 0.02,
    };
    let s = initial(model).unwrap();
    let r = evaluate(model, 0., s).unwrap();
    close(r.Sigma, sig, 1e-15, 1e-16);
    assert_eq!(r.radiation_pi_J_m3, 0.0); // initially isotropic radiation at a_ref
    assert!(r.matter_pi_J_m3 < 0.0);
    assert!(r.d_thermal_energy_dlog_a > 0.0);
    assert!(r.d_proper_time_HREF_dlog_a > 0.0);
    assert!(r.raychaudhuri_dHdt_per_s2 < 0.0);
}
#[test]
fn fluid_sign_reversal_flrw_and_valid_domain() {
    let z = StressModel {
        Sigma_ref: 0.,
        orientation: 0,
        free_radiation_fraction: 1.0,
        matter_viscosity_strength: 0.02,
    };
    let s = initial(z).unwrap();
    let r = evaluate(z, 0.7, s).unwrap();
    assert_eq!(r.Sigma, 0.0);
    assert_eq!(r.radiation_pi_J_m3, 0.0);
    assert_eq!(r.matter_pi_J_m3, 0.0);
    assert_eq!(r.d_signed_s_HREF_dlog_a, 0.0);
    let bad = StressModel {
        Sigma_ref: 0.,
        orientation: 1,
        ..z
    };
    assert!(validate(bad).is_err());
    let bad_visc = StressModel {
        matter_viscosity_strength: -0.1,
        ..z
    };
    assert!(validate(bad_visc).is_err());
    let bad_frac = StressModel {
        free_radiation_fraction: 1.01,
        ..z
    };
    assert!(validate(bad_frac).is_err());
    let nan = State { b: f64::NAN, ..s };
    assert!(evaluate(z, 0.1, nan).is_err());
    let beyond = State { b: 0.03, ..s };
    assert!(evaluate(z, 0.1, beyond).is_err());
}
#[test]
fn shear_stress_tensor_invariants_and_dimensions() {
    let s = 1.5e-17;
    let pi_rad = 1e-14;
    let pi_m = -2e-14;
    let shear = [-s, -s, 2.0 * s];
    let pi = [-pi_rad - pi_m, -pi_rad - pi_m, 2.0 * (pi_rad + pi_m)];
    let norm: f64 = shear.iter().map(|x| x * x).sum::<f64>() / 2.0;
    close(norm, 3.0 * s * s, 1e-16, 1e-42);
    let work: f64 = shear.iter().zip(pi.iter()).map(|(x, y)| x * y).sum();
    close(work, 6.0 * s * (pi_rad + pi_m), 1e-15, 1e-45);
    close(pi[2] - pi[0], 3.0 * (pi_rad + pi_m), 1e-15, 1e-26);
    assert!(RHO_CRIT > 0.0);
}
