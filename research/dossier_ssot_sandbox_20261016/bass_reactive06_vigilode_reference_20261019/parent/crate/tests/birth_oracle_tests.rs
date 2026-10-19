#[path = "../birth_oracle.rs"]
mod birth_oracle;
use birth_oracle::{exact_phi, gauss_phi};
#[test]
fn zero_and_thin_limits() {
    assert_eq!(exact_phi(0.).unwrap(), 1.);
    for n in [2, 4] {
        assert!((gauss_phi(0., n).unwrap() - 1.).abs() < 2e-15);
        assert!((gauss_phi(1e-4, n).unwrap() - exact_phi(1e-4).unwrap()).abs() < 2e-15);
    }
}
#[test]
fn opaque_source_retains_algebraic_not_exponential_tail() {
    assert!((exact_phi(100.).unwrap() - 0.01).abs() < 1e-16);
    assert!(gauss_phi(100., 2).unwrap() / exact_phi(100.).unwrap() < 1e-6);
    assert!(gauss_phi(100., 4).unwrap() / exact_phi(100.).unwrap() < 0.02);
}
#[test]
fn scalar_event_ledger_cannot_detect_birth_bias() {
    let birth = 2.3;
    let exact = birth * exact_phi(40.).unwrap();
    let approx = birth * gauss_phi(40., 2).unwrap();
    assert!((exact - approx).abs() / exact > 0.99);
    for survivor in [exact, approx] {
        let absorbed = birth - survivor;
        assert!((survivor + absorbed - birth).abs() < 1e-15);
        assert!(survivor >= 0. && absorbed >= 0.);
    }
}
#[test]
fn gaussian_approximations_improve_in_resolved_regime() {
    let ex = exact_phi(1.).unwrap();
    let e2 = (gauss_phi(1., 2).unwrap() - ex).abs();
    let e4 = (gauss_phi(1., 4).unwrap() - ex).abs();
    assert!(e4 < e2 * 1e-4 && e4 < 1e-9);
}
#[test]
fn invalid_inputs_fail() {
    for tau in [-1., f64::NAN, f64::INFINITY] {
        assert!(exact_phi(tau).is_err());
        assert!(gauss_phi(tau, 2).is_err());
    }
    assert!(gauss_phi(1., 3).is_err());
}
