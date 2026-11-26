use rei_microphysics::spectral_ff::SpectralFf;
#[test]
fn balance_and_positivity() {
    let mut s = SpectralFf::new(1e-10, 60., 256).unwrap();
    let r = s.advance(50., 50., 0., 1e-4, 3e4, false).unwrap();
    assert_eq!(r.net, 0.);
    assert!(s.delta.iter().all(|v| *v == 0.));
    let r = s.advance(10., 50., 0., 1e-4, 3e4, false).unwrap();
    assert!(r.net < 0. && r.max_tau > 1.);
    assert!(s
        .delta
        .iter()
        .zip(&s.x)
        .all(|(v, x)| v + 1. / x.exp_m1() >= 0.));
    assert!((s.energy(3e4).unwrap() - r.net).abs() < 1e-14);
    let old = s.energy(3e4).unwrap();
    let r = s.advance(100., 50., 0., 1e-4, 3e4, false).unwrap();
    assert!((s.energy(3e4).unwrap() - old - r.net).abs() < 1e-14);
}
