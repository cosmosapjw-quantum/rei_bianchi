use rei_microphysics::axbi_covariant_driver::ErrorComponents;
#[test]
fn error_vector_contract() {
    let c = ErrorComponents {
        gas: [1., 2., 3., 4.],
        shape_n: 5.,
        shape_u: 6.,
        pool_n: 7.,
        pool_u: 8.,
        gamma: [9., 10., 11.],
        heat: [12., 13., 14.],
    };
    let v = c.ordered_values();
    assert_eq!(
        v,
        [1., 2., 3., 4., 5., 6., 7., 8., 9., 10., 11., 12., 13., 14.]
    );
    assert_eq!(
        v.into_iter().fold(0., f64::max),
        c.legacy_metric().max(c.rate_metric())
    );
}
