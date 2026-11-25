use rei_microphysics::axbi_covariant_driver::{Driver, DriverConfig};
#[test]
fn decomposed_metric_matches_original_and_zero_on_identical_state() {
    let mut c = DriverConfig::baseline();
    c.end_zbar = 19.98;
    c.background_panels = 64;
    c.transport_cells = 16;
    c.inactive_hi_split = true;
    let (d, s) = Driver::new(c).unwrap();
    let a = d.error_components(&s, &s).unwrap();
    assert_eq!(a.legacy_metric(), 0.);
    assert_eq!(a.rate_metric(), 0.);
    let p = d.probe_step(&s, 1e-6).unwrap();
    assert!(p.components.legacy_metric().is_finite());
    assert_eq!(
        p.components.legacy_metric(),
        d.error_metric(&p.full, &p.half).unwrap()
    );
    assert!(p.rhs > 0);
}

#[test]
fn exact_frozen_opacity_birth_integral_and_energy_ledger() {
    use rei_microphysics::{Absorber, AtomicProvider, HHeModel};
    let mut c = DriverConfig::baseline();
    c.end_zbar = 19.98;
    c.background_panels = 64;
    c.transport_cells = 16;
    let (d, s) = Driver::new(c).unwrap();
    let geom = d
        .background
        .point_at_scale(s.a)
        .unwrap()
        .geometry()
        .unwrap();
    let mut old = d.transport.empty_state();
    let mut birth = old.clone();
    d.transport.add_delta(&mut old, 0, 30., 1e-5).unwrap();
    d.transport.add_delta(&mut birth, 0, 30., 2e-5).unwrap();
    let a = d.transport.prepare(&old, &geom).unwrap();
    let b = d.transport.prepare(&birth, &geom).unwrap();
    let nh = 1e-3;
    let sigma = AtomicProvider::reference()
        .cross_section(Absorber::HI, 30.)
        .unwrap();
    let lam = HHeModel::controlled_fixture().c_cm_s * nh * sigma;
    for x in [1e-10_f64, 0.01, 1., 10., 100., 1e4] {
        let v = a
            .evaluate_continuous_birth(&b, [nh, 0., 0.], nh, x / lam)
            .unwrap();
        let want = 1e-5 * (-x).exp() + 2e-5 * (-(-x).exp_m1() / x);
        let (n, u) = d.transport.inventory(&v.state, &geom).unwrap();
        assert!((n - want).abs() < 2e-13 * want);
        assert!((u - 30. * want).abs() < 2e-13 * 30. * want);
        assert!((n + v.absorbed_per_h[0] - 3e-5).abs() < 1e-18);
        assert!((u + v.binding_ev_per_h + v.heat_ev_per_h - 30. * 3e-5).abs() < 1e-16);
    }
}

#[test]
fn nonmonotone_search_never_accepts_an_unchecked_candidate() {
    let mut c = DriverConfig::baseline();
    c.end_zbar = 19.98;
    c.background_panels = 64;
    c.transport_cells = 16;
    c.inactive_hi_split = true;
    c.continuous_birth = true;
    c.nonmonotone_search = true;
    c.local_target = 1.6e-4;
    c.initial_dln_a = 1e-5;
    let (d, mut s) = Driver::new(c).unwrap();
    let old = s.clone();
    for _ in 0..30 {
        if d.adaptive_step(&mut s).unwrap_or(false) {
            break;
        }
    }
    assert!(s.accepted == 1);
    let h = ((s.a - old.a) / old.a).ln_1p();
    let probe = d.probe_step(&old, h).unwrap();
    assert!(probe.components.legacy_metric() < d.config.local_target);
    assert!(probe.components.rate_metric() < d.config.local_target);
    assert!(s.attempts >= 3 && s.rhs_evaluations > 0);
}

#[test]
fn flrw_two_ordinate_symmetry_reduction_preserves_physical_moments() {
    let mut c = DriverConfig::baseline();
    c.end_zbar = 19.98;
    c.background_panels = 64;
    c.transport_cells = 16;
    c.inactive_hi_split = true;
    c.continuous_birth = true;
    let (d, s) = Driver::new(c.clone()).unwrap();
    c.flrw_two_ordinate = true;
    let (r, t) = Driver::new(c.clone()).unwrap();
    assert_eq!(r.source.angular_cells.len(), 2);
    let a = d.probe_step(&s, 2e-5).unwrap().half;
    let b = r.probe_step(&t, 2e-5).unwrap().half;
    for i in 0..3 {
        assert!((a.gas.fractions[i] - b.gas.fractions[i]).abs() < 1e-14)
    }
    assert!((d.photon_inventory(&a).0 - r.photon_inventory(&b).0).abs() < 1e-18);
    let m = r.moments(&b).unwrap();
    assert!(m[1].abs() < 1e-14 * m[0] && m[2].abs() < 1e-14 * m[0]);
    c.q_ref = 0.01;
    assert!(Driver::new(c).is_err());
}
