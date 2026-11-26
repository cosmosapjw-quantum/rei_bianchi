use rei_microphysics::spectral_ff::SpectralFf;
#[test]
fn balance_and_positivity() {
    let mut s = SpectralFf::new(1e-10, 60., 256).unwrap();
    let r = s.advance(50., 50., 0., 1e-4, 3e4, false).unwrap();
    assert_eq!(r.net, 0.);
    assert!(s.distortion().iter().all(|v| *v == 0.));
    let r = s.advance(10., 50., 0., 1e-4, 3e4, false).unwrap();
    assert!(r.net < 0. && r.max_tau > 1.);
    assert!(s
        .distortion()
        .iter()
        .zip(s.nodes())
        .all(|(v, x)| v + 1. / x.exp_m1() >= 0.));
    assert!((s.energy(3e4).unwrap() - r.net).abs() < 1e-14);
    let old = s.energy(3e4).unwrap();
    let r = s.advance(100., 50., 0., 1e-4, 3e4, false).unwrap();
    assert!((s.energy(3e4).unwrap() - old - r.net).abs() < 1e-14);
}

#[test]
fn validated_distortion_restore() {
    let mut s = SpectralFf::new(1e-10, 60., 128).unwrap();
    s.advance(10., 50., 0.2, 1e-5, 3e4, false).unwrap();
    let a = s.distortion().to_vec();
    let mut t = SpectralFf::new(1e-10, 60., 128).unwrap();
    t.restore_distortion(&a).unwrap();
    assert_eq!(s.energy(3e4).unwrap(), t.energy(3e4).unwrap());
    assert!(t.restore_distortion(&vec![-1e30; 128]).is_err());
    assert_eq!(t.distortion(), a);
    assert!(t.restore_distortion(&vec![f64::NAN; 128]).is_err());
    s.advance(100., 50., 0.2, 1e-5, 3e4, false).unwrap();
    t.advance(100., 50., 0.2, 1e-5, 3e4, false).unwrap();
    assert_eq!(s.distortion(), t.distortion());
}
