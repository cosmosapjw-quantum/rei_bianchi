//! AX08 signed Bianchi I phase-volume and photon-number invariant.
//! This tests existing source functions without changing the historical AX08 driver.
use rei_microphysics::axbi_background::{
    isotropic_initial_radiation_moments, AxbiBackground, BackgroundFamily, Cosmology,
};
use rei_microphysics::CharacteristicRay;

const GL8_X: [f64; 8] = [
    -0.9602898564975363,
    -0.7966664774136267,
    -0.5255324099163290,
    -0.1834346424956498,
    0.1834346424956498,
    0.5255324099163290,
    0.7966664774136267,
    0.9602898564975363,
];
const GL8_W: [f64; 8] = [
    0.1012285362903763,
    0.2223810344533745,
    0.3137066458778873,
    0.3626837833783619,
    0.3626837833783619,
    0.3137066458778873,
    0.2223810344533745,
    0.1012285362903763,
];

fn close(a: f64, b: f64, tol: f64) {
    assert!(a.is_finite() && b.is_finite(), "nonfinite {a} {b}");
    assert!((a - b).abs() < tol, "{a:.18e} != {b:.18e}, tol={tol:.2e}");
}

#[test]
fn actual_ax08_signed_phase_volume_and_energy_parity() {
    let a_ref = 1.0 / 21.0;
    let bg_cosmology = Cosmology {
        h0_per_s: 67.4 * 1e5 / 3.0856775814913673e24,
        omega_m: 0.315,
        omega_r: 9.2e-5,
        omega_lambda: 1. - 0.315 - 9.2e-5,
    };
    for q in [-0.01, -0.005, 0.0, 0.005, 0.01] {
        let bg = AxbiBackground::new(
            bg_cosmology,
            a_ref,
            0.2,
            0.0,
            q,
            BackgroundFamily::PhysicalDensityFixed,
            256,
        )
        .unwrap();
        let g0 = bg.point_at_scale(a_ref).unwrap().geometry().unwrap();
        for a in [a_ref, 0.08, 0.12, 0.2] {
            let point = bg.point_at_scale(a).unwrap();
            let g1 = point.geometry().unwrap();
            let mut number = 0.;
            let mut energy = 0.;
            let shift = a_ref / a;
            let b = point.b;
            for (&mu0, &w) in GL8_X.iter().zip(GL8_W.iter()) {
                let ray = CharacteristicRay::new(20.0, [(1.0 - mu0 * mu0).sqrt(), 0.0, mu0], 1.0)
                    .unwrap();
                let transported = ray.pullback(&g0, &g1).unwrap();
                let jac = ray.solid_angle_jacobian(&g0, &g1).unwrap();
                let s = (1. - mu0 * mu0) * (2. * b).exp() + mu0 * mu0 * (-4. * b).exp();
                let local_mu = mu0 * (-2. * b).exp() / s.sqrt();
                close(transported.energy_ev / (20. * shift), s.sqrt(), 8e-15);
                close(transported.direction[2], local_mu, 8e-15);
                close(jac, s.powf(-1.5), 8e-15);
                let reverse = transported.pullback(&g1, &g0).unwrap();
                close(reverse.energy_ev, ray.energy_ev, 1e-12);
                close(reverse.direction[2], ray.direction[2], 1e-12);
                let jac_inv = transported.solid_angle_jacobian(&g1, &g0).unwrap();
                close(jac * jac_inv, 1.0, 1e-12);
                number += 0.5 * w * jac;
                energy += 0.5 * w * transported.energy_ev / (20. * shift);
            }
            // Exactly normalized phase-volume: free-streamed photon number ∝a^-3.
            close(number, 1., 1e-12);
            // Independent initial-angular measure, compared to owner's Simpson4096.
            let m = isotropic_initial_radiation_moments(a, b, a_ref, 0.0, 13.0, 4096).unwrap();
            let expected = m.energy_j_m3 / (13.0 * shift.powi(4));
            close(energy, expected, 1e-12);
            // Isotropic limit of energy and stress.
            if q == 0.0 {
                close(b, 0., 0.5e-15);
                close(number, 1., 1e-15);
                close(energy, 1., 1e-15);
            }
        }
    }
}
