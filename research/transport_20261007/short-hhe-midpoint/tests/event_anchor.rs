use rei_microphysics::{verner_cutoff_ev, Absorber};
use short_hhe_control::{event_anchor::start_energy, v2};
#[test]
fn exact_event_anchor_identity_and_neighbors() {
    let s0 = -13f64.ln();
    for (i, atom) in [Absorber::HI, Absorber::HeI, Absorber::HeII]
        .into_iter()
        .enumerate()
    {
        let c = verner_cutoff_ev(atom);
        let eta = c.ln() + s0 + 1.4905626121828326e-5;
        let b = eta - c.ln();
        let (e, special) = start_energy(eta, s0, b).unwrap();
        assert!(special, "exact event must use its stored identity");
        assert_eq!(e * (-(b - s0)).exp(), c);
        for bits in [b.to_bits() - 1, b.to_bits() + 1] {
            let near = f64::from_bits(bits);
            let (e, special) = start_energy(eta, s0, near).unwrap();
            assert!(!special, "neighbor acquired event status");
            assert_eq!(e, (eta - s0).exp());
        }
        let (next, special) = start_energy(eta, b, b + 1e-5).unwrap();
        assert!(special);
        assert_eq!(next, c);
        let mut r = [0.; 3];
        r[i] = 0.7;
        let o = v2::kernel(0.02, 0.4, r, b - s0, e).unwrap();
        assert_eq!(o.u, v2::EPS * c * o.n);
        let n = o.n + o.an.iter().sum::<f64>();
        let en = o.u + o.be.iter().sum::<f64>() + o.red;
        assert!((n - (0.02 + o.qn)).abs() < 2e-12 * n);
        assert!((en - (v2::EPS * e * 0.02 + o.qe)).abs() < 2e-12 * en);
        let first = o.u;
        let begin = v2::EPS * next * o.n;
        assert_eq!(first, begin, "event energy continuity");
        assert!(
            v2::kernel(o.n, 0., r, 1e-5, next).is_err(),
            "absorption extends below cutoff"
        );
    }
}
#[test]
fn anchored_photo_material_identity() {
    use short_hhe_control::material::{binding, photo_delta};
    let cutoff = 24.59f64;
    let eta = 0.6374054043926861;
    let b = eta - cutoff.ln();
    let a = -13f64.ln();
    let (e, _) = start_energy(eta, a, b).unwrap();
    let o = v2::kernel(0.001, 2., [0.7, 0.4, 0.], b - a, e).unwrap();
    let fhe = 0.07894736842105263;
    let old = [0.0002, 0., 0., 1e-14];
    let d = photo_delta(o.an, o.be, fhe);
    let new = std::array::from_fn(|i| old[i] + d[i]);
    let absorbed = o.be.iter().sum::<f64>();
    let material = new[3] - old[3] + binding(new, fhe) - binding(old, fhe);
    assert!((material - absorbed).abs() <= 2e-12 * absorbed);
    let total = material + o.u + o.red;
    let input = v2::EPS * e * 0.001 + o.qe;
    assert!((total - input).abs() < 2e-12 * input);
}
