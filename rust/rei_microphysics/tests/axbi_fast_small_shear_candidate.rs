//! New additive source-free fast radiation diagnostic, no production mutation.
#[path = "../../../research/axbi_goal_20261014/convergence/ax08_halfminus_fast_20261015/fast_moments.rs"]
mod fast_moments;
use fast_moments::fast_bianchi_i_initial_isotropic;
use rei_microphysics::axbi_background::isotropic_initial_radiation_moments;

#[test]
fn exact_rational_moments_vs_actual_production_simpson4096() {
    let a_ref: f64 = 1.0 / 21.0;
    for a in [a_ref, 0.071, 0.11, 0.2] {
        let eps_ref = 3.85176572207226835e-3;
        let iso = eps_ref * (a_ref / a).powi(4);
        for b in [
            -0.025,
            -0.01,
            -0.005892916695356844,
            -0.00294649,
            -1.0e-6,
            0.0,
            1.0e-6,
            0.00294649,
            0.005892916695356844,
            0.01,
            0.025,
        ] {
            let x = fast_bianchi_i_initial_isotropic(a, b, a_ref, 0.0, eps_ref).unwrap();
            let y = isotropic_initial_radiation_moments(a, b, a_ref, 0.0, eps_ref, 4096).unwrap();
            assert!(
                (x.energy_j_m3 - y.energy_j_m3).abs() / iso < 2e-13,
                "energy b={b:e} delta={:e}",
                (x.energy_j_m3 - y.energy_j_m3) / iso
            );
            assert!(
                (x.pressure_anisotropy_j_m3 - y.pressure_anisotropy_j_m3).abs() / iso < 2e-13,
                "quad b={b:e} delta={:e}",
                (x.pressure_anisotropy_j_m3 - y.pressure_anisotropy_j_m3) / iso
            );
            assert_eq!(x.dipole_energy_j_m3, 0.0);
            if b == 0.0 {
                assert_eq!(x.energy_ratio_minus_one, 0.0);
                assert_eq!(x.pressure_over_isotropic, 0.0);
                assert_eq!(x.signed_energy_correction_j_m3, 0.0);
                assert_eq!(x.pressure_anisotropy_j_m3, 0.0);
            } else {
                assert!(x.signed_energy_correction_j_m3 > 0.0);
                assert_eq!(x.pressure_anisotropy_j_m3.is_sign_positive(), b < 0.0);
            }
        }
    }
}
#[test]
fn rigorous_small_shear_complex_analytic_truncation_bound() {
    let (m0, m2) = fast_moments::conservative_taylor14_bounds();
    assert!(m0 > 0.0 && m0 < 6e-18, "energy theoretical truncation {m0}");
    assert!(
        m2 > 0.0 && m2 < 5e-17,
        "quadrupole theoretical truncation {m2}"
    );
}
#[test]
fn physical_domains_and_arbitrary_reference_b() {
    let err = fast_bianchi_i_initial_isotropic(0.2, 0.1, 0.04, 0.0, 2.0);
    assert!(err.is_err());
    assert!(fast_bianchi_i_initial_isotropic(0.2, 0.1, 0.04, 0.1, 2.0).is_ok());
    assert!(fast_bianchi_i_initial_isotropic(0.0, 0.0, 0.1, 0.0, 1.0).is_err());
    assert!(fast_bianchi_i_initial_isotropic(0.1, 0.0, 0.1, 0.0, -1.0).is_err());
    assert!(fast_bianchi_i_initial_isotropic(0.1, f64::NAN, 0.1, 0.0, 1.0).is_err());
    assert!(fast_bianchi_i_initial_isotropic(0.1, 0.0, 0.1, 0.0, 0.0).is_ok());
}
#[test]
fn tiny_shear_correction_without_catastrophic_cancellation() {
    let tiny = 1.0e-9;
    let x = fast_bianchi_i_initial_isotropic(0.1, tiny, 0.1, 0.0, 1.0).unwrap();
    assert!(x.energy_ratio_minus_one > 0.0);
    assert!((x.energy_ratio_minus_one / (tiny * tiny) - 8.0 / 5.0).abs() < 1e-6);
    assert!((x.pressure_over_isotropic / tiny + 8.0 / 5.0).abs() < 1e-6);
    assert_eq!(x.energy_j_m3, 1.0); // binary64 energy monopole itself rounds to one
}
