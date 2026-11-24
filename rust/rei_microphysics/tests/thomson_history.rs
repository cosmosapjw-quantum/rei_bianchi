use rei_microphysics::axbi_driver::{Driver, DriverConfig};
use rei_microphysics::thomson::{thomson_history, DensityConstraint::*, MaterialKnot};
const C_SIGMA: f64 = 299_792_458.0 * 6.6524587051e-29;
fn knots(beta: [f64; 3]) -> [MaterialKnot; 3] {
    [0.0, 1.0, 3.0].map(|t| MaterialKnot {
        normal_t_s: t,
        a: 0.1 + 0.05 * t,
        b: 0.0,
        n_reference_m3: 1.0 / C_SIGMA,
        electrons_per_reference: 1.0,
        beta,
    })
}
fn close(a: f64, b: f64, tol: f64) {
    assert!(
        (a - b).abs() <= tol,
        "{a} != {b} (absolute tolerance {tol})"
    )
}

#[test]
fn probability_integrates_to_one_with_transmission_and_preserves_tiny_cells() {
    let mut k = knots([0.; 3]);
    let s = thomson_history(&k, FixedRest, [1., 0., 0.]).unwrap();
    close(s[0].tau_to_receiver, 3.0, 2e-15);
    close(s[1].next_cell_mass, 1.0 - (-2.0_f64).exp(), 1e-15);
    close(
        s.iter().map(|s| s.next_cell_mass).sum::<f64>() + (-3.0_f64).exp(),
        1.,
        2e-15,
    );
    for row in &mut k {
        row.electrons_per_reference = 1e-22
    }
    let s = thomson_history(&k, FixedRest, [1., 0., 0.]).unwrap();
    close(s[0].next_cell_mass, 1e-22, 4e-38);
    for row in &mut k {
        row.electrons_per_reference = 0.0
    }
    assert_eq!(
        thomson_history(&k, FixedRest, [0., 0., 1.]).unwrap()[0].tau_to_receiver,
        0.0
    );
}
#[test]
fn boosts_keep_distinct_density_conventions_and_counterpropagation() {
    let k = knots([0.6, 0., 0.]);
    for (direction, expected) in [
        ([1., 0., 0.], 0.5),
        ([-1., 0., 0.], 2.0),
        ([0., 1., 0.], 1.25),
    ] {
        let s = thomson_history(&k, FixedRest, direction).unwrap();
        close(s[0].rate_per_s, expected, 1e-15);
        let s = thomson_history(&k, FixedNormalInventory, direction).unwrap();
        close(s[0].rate_per_s, 0.8 * expected, 1e-15);
        close(s[0].n_reference_rest_m3 / k[0].n_reference_m3, 0.8, 2e-16);
    }
    let beta = f64::from_bits(1.0_f64.to_bits() - 1);
    let s = thomson_history(&knots([beta, 0., 0.]), FixedRest, [1., 0., 0.]).unwrap();
    close(s[0].rate_per_s, ((1. - beta) / (1. + beta)).sqrt(), 2e-23);
}
#[test]
fn geometry_pulls_direction_from_terminal_and_velocity_can_vary() {
    let mut k = knots([0.; 3]);
    k[0].b = 0.1;
    k[0].beta = [0.2, 0.0, 0.0];
    k[2].beta = [0.0, 0.0, -0.3];
    let x = 1.0_f64 / 2.0_f64.sqrt();
    let s = thomson_history(&k, FixedRest, [x, 0., x]).unwrap();
    close(s[0].direction[0] / s[0].direction[2], 0.3_f64.exp(), 1e-14);
    close(
        s[0].rate_per_s,
        (1. - 0.2 * s[0].direction[0]) / (1. - 0.2_f64.powi(2)).sqrt(),
        1e-15,
    );
    close(
        s[2].rate_per_s,
        (1. + 0.3 * x) / (1. - 0.3_f64.powi(2)).sqrt(),
        1e-15,
    );
    close(
        s[0].tau_to_receiver,
        0.5 * s[0].rate_per_s + 1.5 * s[1].rate_per_s + s[2].rate_per_s,
        2e-15,
    );
}
#[test]
fn nonphysical_beta_density_geometry_and_time_fail() {
    let k = knots([0.; 3]);
    for (i, value) in [(0, f64::NAN), (1, f64::INFINITY), (2, 1.0)] {
        let mut q = k;
        q[1].beta[i] = value;
        assert!(thomson_history(&q, FixedRest, [0., 0., 1.]).is_err());
    }
    let mut q = k;
    q[1].normal_t_s = q[0].normal_t_s;
    assert!(thomson_history(&q, FixedRest, [0., 0., 1.]).is_err());
    let mut q = k;
    q[1].n_reference_m3 = -1.;
    assert!(thomson_history(&q, FixedRest, [0., 0., 1.]).is_err());
    let mut q = k;
    q[1].a = 0.;
    assert!(thomson_history(&q, FixedRest, [0., 0., 1.]).is_err());
    assert!(thomson_history(&k, FixedRest, [0., 0., 0.]).is_err());
    assert!(thomson_history(&k[..1], FixedRest, [0., 0., 1.]).is_err());
}
#[test]
fn original_chemistry_driver_exposes_eos_charge_once() {
    let (driver, state) = Driver::new(DriverConfig::baseline()).unwrap();
    let p = driver.thomson_material_knot(&state, [0.; 3]).unwrap();
    let nh = driver.n_h0_cm3 / state.a.powi(3);
    let nhe = driver.n_he0_cm3 / state.a.powi(3);
    let [h, he1, he2] = state.gas.fractions;
    close(p.n_reference_m3 * 1e-6, nh, 1e-18);
    close(
        p.electrons_per_reference,
        h + nhe / nh * (he1 + 2. * he2),
        1e-17,
    );
}
