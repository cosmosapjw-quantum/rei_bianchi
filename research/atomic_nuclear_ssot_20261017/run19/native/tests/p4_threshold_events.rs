//! P4/S4a event-root regression and mathematical independent controls.
//! Manufactured constant-H Bianchi-I geometry. No cosmological background claim.
use rei_iso_couple_reference::bianchi_i::{ConstantHubbleBackground, GeometryBackground};
use rei_iso_couple_reference::full_network::NetworkError;
use rei_iso_couple_reference::source_age::Cohort;
use rei_iso_couple_reference::threshold_events::{
    VERNER_FIT_EDGES_EV, partition_at_photo_events, threshold_cut_times,
};

fn make_co(e: f64, dir: [f64; 3], bg: &ConstantHubbleBackground) -> Cohort {
    Cohort {
        birth_time_s: 0.,
        birth_geometry: bg.snapshot(0.).unwrap(),
        energy_at_birth_ev: e,
        direction_at_birth: dir,
        n_comoving_m3: 1.,
        spectral_index: 0,
        angular_index: 0,
    }
}
fn approx(a: f64, b: f64, eps: f64) {
    assert!(
        (a - b).abs() <= eps,
        "a={a:.16e}, b={b:.16e}, diff={:.16e}",
        (a - b).abs()
    );
}
#[test]
fn native_fitted_thresholds_are_not_chemical_binding_energies() {
    assert_eq!(VERNER_FIT_EDGES_EV, [13.60, 24.59, 54.42]);
    let h_binding = rei_iso_couple_reference::HHeModel::controlled_fixture().threshold_ev[0];
    assert!((h_binding - VERNER_FIT_EDGES_EV[0]).abs() > 1e-6);
    let a = rei_iso_couple_reference::AtomicProvider::reference();
    use rei_iso_couple_reference::Absorber;
    assert_eq!(a.cross_section(Absorber::HI, 13.599999999).unwrap(), 0.);
    assert!(a.cross_section(Absorber::HI, 13.600000001).unwrap() > 0.);
}
#[test]
fn exact_flrw_two_separate_h_and_d_crossings_and_photon_conservation() {
    let h = 1e-12;
    let bg = ConstantHubbleBackground::new([1., 1., 1.], [h, h, h]).unwrap();
    let e0 = 13.604;
    let d = 13.602134599702;
    let co = make_co(e0, [0., 0., 1.], &bg);
    let t1 = 0.5e9;
    let cut = threshold_cut_times(&co, &bg, 0., t1, d).unwrap();
    assert_eq!(cut.len(), 2);
    let t_d = (e0 / d).ln() / h;
    let t_h = (e0 / 13.60).ln() / h;
    approx(cut[0], t_d, 2e-4);
    approx(cut[1], t_h, 2e-4);
    assert!(cut[0] < cut[1]);
    let p = partition_at_photo_events(&co, &bg, 0., t1, d).unwrap();
    assert_eq!(p.len(), 3);
    approx(p.iter().map(|(a, b)| b - a).sum::<f64>(), t1, 1e-7);
    // Constant active D opacity until the D edge: exact optical path length.
    let k = 1e-9;
    let n0 = 3.2;
    let mut n = n0;
    let mut absorbed = 0.;
    for (a, b) in p {
        let tm = 0.5 * (a + b);
        let en = co.ray_at(&bg.snapshot(tm).unwrap()).unwrap().energy_ev;
        let kr = if en >= d { k } else { 0. };
        let frac = -(-kr * (b - a)).exp_m1();
        let ev = n * frac;
        absorbed += ev;
        n -= ev;
    }
    let exact = n0 * (-k * t_d).exp();
    approx(n, exact, 2e-12);
    approx(n + absorbed, n0, 1e-15);
    let midpoint_energy = co.ray_at(&bg.snapshot(t1 / 2.).unwrap()).unwrap().energy_ev;
    let midpoint_old = n0 * (-if midpoint_energy >= d { k * t1 } else { 0. }).exp();
    assert!((midpoint_old - exact).abs() / exact > 0.05);
}
#[test]
fn bidirectional_threshold_crossing_when_one_axis_contracts() {
    let h = 1e-12;
    let bg = ConstantHubbleBackground::new([1., 1., 1.], [-h, -h, h]).unwrap();
    let co = make_co(
        27.,
        [(0.1f64).sqrt(), (0.1f64).sqrt(), (0.8f64).sqrt()],
        &bg,
    );
    let t1 = 8e11;
    let cut = threshold_cut_times(&co, &bg, 0., t1, 13.602134599702).unwrap();
    assert_eq!(cut.len(), 2, "cut times {cut:?}");
    let chi = 24.59;
    let q = (chi / 27f64).powi(2);
    let root_a = (q - (q * q - 4. * 0.2 * 0.8).sqrt()) / (2. * 0.2);
    let root_b = (q + (q * q - 4. * 0.2 * 0.8).sqrt()) / (2. * 0.2);
    let t_a = root_a.ln() / (2. * h);
    let t_b = root_b.ln() / (2. * h);
    approx(cut[0], t_a, 2e-3);
    approx(cut[1], t_b, 2e-3);
    assert!(t_a > 0. && t_b < t1);
    let periods = partition_at_photo_events(&co, &bg, 0., t1, 13.602134599702).unwrap();
    assert_eq!(periods.len(), 3);
    for &(start, end) in &periods {
        assert!(end > start)
    }
}
#[test]
fn zero_expansion_no_cut_and_strict_source_guard() {
    let bg = ConstantHubbleBackground::new([1., 1., 1.], [0., 0., 0.]).unwrap();
    let c = make_co(30., [1., 0., 0.], &bg);
    assert!(
        threshold_cut_times(&c, &bg, 0., 12., 13.602134599702)
            .unwrap()
            .is_empty()
    );
    assert_eq!(
        threshold_cut_times(&c, &bg, 0., 0., 13.602134599702),
        Err(NetworkError::InvalidInput)
    );
    assert_eq!(
        threshold_cut_times(&c, &bg, 0., 1., f64::NAN),
        Err(NetworkError::InvalidInput)
    );
}
#[test]
fn unsupported_domain_rejected_by_typed_event_locator() {
    let bg = ConstantHubbleBackground::new([1., 1., 1.], [0.01, 0.01, 0.01]).unwrap();
    let co = make_co(25., [0., 0., 1.], &bg);
    assert_eq!(
        threshold_cut_times(&co, &bg, -1., -1., 13.602134599702),
        Err(NetworkError::InvalidInput)
    );
    assert_eq!(
        threshold_cut_times(&co, &bg, 0., 1., 13.60),
        Err(NetworkError::InvalidInput)
    );
}
