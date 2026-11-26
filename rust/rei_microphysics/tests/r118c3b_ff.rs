use rei_microphysics::ff_balance::{absorption_ratio, gaunt};
#[test]
fn physical_table_and_balance() {
    assert!((gaunt(1e-6, 1e-16).unwrap() - 20.7575626).abs() < 1e-7);
    for mode in [1, 2] {
        for t in [10., 50., 130., 10000.] {
            assert!((absorption_ratio(t, t, 0.2, mode).unwrap() - 1.).abs() < 1e-12);
            assert!(absorption_ratio(t, t * 2., 0.2, mode).unwrap() > 1.);
            assert!(absorption_ratio(t, t / 2., 0.2, mode).unwrap() < 1.);
        }
    }
    assert!(absorption_ratio(0., 50., 0., 2).is_err());
}
