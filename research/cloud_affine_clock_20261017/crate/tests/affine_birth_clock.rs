use rei_iso_couple_reference::affine_birth_clock::advance_affine;
use rei_iso_couple_reference::birth_clock::uniform_partition;
fn close(a: f64, b: f64, t: f64) {
    assert!(
        (a - b).abs() <= t * a.abs().max(b.abs()).max(1e-290),
        "{a:e} {b:e}"
    );
}
#[test]
fn zero_opacity_affine_source_exact() {
    let p = advance_affine(2., 1., 3., 0., 0., 4.).unwrap();
    assert_eq!(p.injected, 8.);
    close(p.surviving, 10., 2e-15);
    assert_eq!(p.absorbed, 0.);
}
#[test]
fn constant_limit_reuses_exact_phi() {
    for tau in [0., 1e-20, 0.1, 1., 1e3] {
        let p = advance_affine(2., 3., 3., tau, tau, 1.).unwrap();
        let q = uniform_partition(2., 3., tau).unwrap();
        assert_eq!(p.surviving, q.surviving);
        assert_eq!(p.absorbed, q.absorbed);
    }
}
#[test]
fn affine_opacity_old_inventory_is_exact() {
    let p = advance_affine(2., 0., 0., 0.2, 0.8, 1.).unwrap();
    close(p.surviving, 2. * (-0.5f64).exp(), 2e-15);
    close(p.absorbed, 2. * (-(-0.5f64).exp_m1()), 2e-15);
}
#[test]
fn count_ledger_and_positivity() {
    for j0 in [0., 0.3, 2.] {
        for j1 in [0., 0.8, 3.] {
            for l0 in [0., 0.1, 1.] {
                for l1 in [0., 0.6, 1.] {
                    let p = advance_affine(0.7, j0, j1, l0, l1, 1.).unwrap();
                    assert!(p.surviving >= 0. && p.absorbed >= 0.);
                    close(p.surviving + p.absorbed, 0.7 + p.injected, 3e-15);
                }
            }
        }
    }
}
#[test]
fn outside_quadrature_domain_is_rejected() {
    assert!(advance_affine(1., 1., 2., 10., 10., 1.).is_err());
    for x in [-1., f64::NAN, f64::INFINITY] {
        assert!(advance_affine(1., x, 1., 1., 1., 1.).is_err());
        assert!(advance_affine(1., 1., 1., x, 1., 1.).is_err());
        assert!(advance_affine(1., 1., 1., 1., 1., x).is_err());
    }
}
#[test]
fn zero_step_identity() {
    let p = advance_affine(3., 1., 2., 0.1, 0.3, 0.).unwrap();
    assert_eq!(p.surviving, 3.);
    assert_eq!(p.absorbed, 0.);
    assert_eq!(p.injected, 0.);
}
#[test]
fn optical_depth_boundary_is_explicit() {
    assert!(advance_affine(1., 1., 2., 1., 1., 1.).is_ok());
    assert!(advance_affine(1., 1., 2., 1., 1., 1. + f64::EPSILON).is_err());
    assert!(advance_affine(1., 1., 1., 10., 10., 1.).is_ok());
}
#[test]
fn overflowing_inventory_and_rates_fail_closed() {
    assert!(advance_affine(f64::MAX, f64::MAX, f64::MAX, 0., 0., 1.).is_err());
    assert!(advance_affine(0., 1., 2., f64::MAX, f64::MAX, 2.).is_err());
    assert!(advance_affine(0., f64::MAX, f64::MAX, 0., 0., 2.).is_err());
}
#[test]
fn rate_then_time_scaling_preserves_integrals() {
    let tiny = f64::from_bits(1);
    let p = advance_affine(0., tiny, tiny, 0., 0., 1e300).unwrap();
    assert_eq!(p.injected, tiny * 1e300);
    assert_eq!(p.surviving, tiny * 1e300);
    let a = advance_affine(0.7, 0.6, 0.9, 0.2, 0.8, 1.).unwrap();
    let b = advance_affine(0.7, 0.6e-200, 0.9e-200, 0.2e-200, 0.8e-200, 1e200).unwrap();
    close(a.surviving, b.surviving, 3e-15);
    close(a.absorbed, b.absorbed, 3e-15);
}
#[test]
fn unsupported_subnormal_variable_integrals_rejected() {
    assert!(advance_affine(0., f64::from_bits(1), f64::from_bits(2), 0., 0., 1.).is_err());
}
