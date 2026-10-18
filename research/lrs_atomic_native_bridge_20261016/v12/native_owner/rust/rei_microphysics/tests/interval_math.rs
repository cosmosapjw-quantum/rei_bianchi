use rei_microphysics::{Interval, Jet};
fn i(a: f64, b: f64) -> Interval {
    Interval::new(a, b).unwrap()
}
fn has(x: Interval, y: f64) {
    assert!(x.lo.is_finite() && x.hi.is_finite() && x.lo <= y && y <= x.hi);
}
#[test]
fn outward_basics() {
    has(i(1., 2.).add(&i(3., 4.)).unwrap(), 4.);
    has(i(1., 2.).add(&i(3., 4.)).unwrap(), 6.);
    has(i(-2., 3.).mul(&i(-4., 5.)).unwrap(), -12.);
    has(i(-2., 3.).mul(&i(-4., 5.)).unwrap(), 15.);
    has(i(2., 4.).div(&i(1., 2.)).unwrap(), 1.);
    has(i(2., 4.).div(&i(1., 2.)).unwrap(), 4.);
}
#[test]
fn elementary_limits() {
    has(i(0., 0.).exp().unwrap(), 1.);
    has(i(1., 1.).ln().unwrap(), 0.);
    has(i(4., 4.).powf(0.5).unwrap(), 2.);
    has(i(2., 2.).powf(-1.).unwrap(), 0.5);
}
#[test]
fn domain_rejections() {
    assert!(Interval::new(2., 1.).is_err());
    assert!(Interval::new(f64::NAN, 1.).is_err());
    assert!(i(-1., 1.).ln().is_err());
    assert!(i(1., 2.).div(&i(-1., 1.)).is_err());
    assert!(i(1000., 1001.).exp().is_err());
    assert!(Jet::variable(i(1., 1.), 7).is_err());
}
#[test]
fn mixed_partial_product() {
    let x = Jet::variable(i(2., 2.), 0).unwrap();
    let y = Jet::variable(i(3., 3.), 1).unwrap();
    let xy = x.mul(&y).unwrap();
    has(xy.value, 6.);
    has(xy.gradient[0], 3.);
    has(xy.gradient[1], 2.);
    has(xy.hessian[0][1], 1.);
    has(xy.hessian[1][0], 1.);
    has(xy.hessian[0][0], 0.);
    has(xy.hessian[1][1], 0.);
}
#[test]
fn nonlinear_chain_and_constants() {
    let x = Jet::variable(i(2., 2.), 0).unwrap();
    let f = x.powf(3.).unwrap();
    has(f.value, 8.);
    has(f.gradient[0], 12.);
    has(f.hessian[0][0], 12.);
    let c = Jet::constant(i(7., 7.)).unwrap();
    has(c.gradient[3], 0.);
    has(c.hessian[2][5], 0.);
    let identity = x.ln().unwrap().exp().unwrap();
    has(identity.value, 2.);
    has(identity.gradient[0], 1.);
    has(identity.hessian[0][0], 0.);
}
