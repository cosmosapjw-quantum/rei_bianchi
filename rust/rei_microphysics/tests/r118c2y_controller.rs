use rei_microphysics::external_controller::{accepted_step, rejected_step};
#[test]
fn controller_keeps_margin_and_bounds() {
    let target = 1.6e-4;
    let max = 8e-5;
    let du = 4e-5;
    assert!(accepted_step(du, 0.9 * target, target, max).unwrap() < du);
    assert!(accepted_step(du, 0.1 * target, target, max).unwrap() > du);
    assert!(accepted_step(du, 0., target, max).unwrap() <= 1.25 * du);
    assert!(accepted_step(max, 0., target, max).unwrap() <= max);
    assert!(accepted_step(du, target, target, max).is_err());
    assert!(accepted_step(du, f64::NAN, target, max).is_err());
    assert_eq!(rejected_step(du).unwrap(), du / 2.);
    assert!(rejected_step(1e-10).is_err());
}
