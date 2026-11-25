//! Focused tests of a diagnostic-only HI active/passive restriction utility.
use rei_microphysics::axbi_covariant_transport::{CovariantTransport, PhotonState};
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::{AxisymmetricPoint, GeometrySnapshot};
fn g(a: f64) -> GeometrySnapshot {
    AxisymmetricPoint::new(a, 0.0, 1e-16, 0.0)
        .unwrap()
        .snapshot()
        .unwrap()
}
fn core() -> CovariantTransport {
    let s = AxbiSource::new(1.9e-7, 0.2, 16, 8).unwrap();
    CovariantTransport::new(&s, g(0.05), 1, 1.0, 512.0).unwrap()
}
fn cell(c: &CovariantTransport, lo: f64, hi: f64, mean: f64) -> PhotonState {
    let mut p = c.empty_state();
    p.number[0] = 1.0;
    p.energy_ref[0] = mean;
    p.support_lo[0] = lo;
    p.support_hi[0] = hi;
    c.validate_state(&p).unwrap();
    p
}
fn close(a: f64, b: f64, tol: f64) {
    assert!((a - b).abs() <= tol * a.abs().max(b.abs()), "{a} != {b}");
}
#[test]
fn partition_empty_below_above_and_exact_threshold_delta() {
    let c = core();
    let empty = c.empty_state();
    let e = c.partition_below_hi(&empty, &g(0.05)).unwrap();
    assert_eq!(e.active, empty);
    let below = cell(&c, 5.0, 10.0, 7.0);
    let frozen = below.clone();
    let p = c.partition_below_hi(&below, &g(0.05)).unwrap();
    assert_eq!(p.inactive_number, below.number);
    assert_eq!(p.inactive_energy_ref, below.energy_ref);
    assert_eq!(p.active, empty);
    assert_eq!(below, frozen);
    assert_eq!(p.quadrature_nodes, 0);
    let above = cell(&c, 20.0, 30.0, 25.0);
    let p = c.partition_below_hi(&above, &g(0.05)).unwrap();
    assert_eq!(p.active, above);
    assert_eq!(p.inactive_number, empty.number);
    let mut delta = c.empty_state();
    c.add_delta(&mut delta, 0, 27.2, 0.7).unwrap();
    let p = c.partition_below_hi(&delta, &g(0.1)).unwrap();
    assert_eq!(p.active, delta);
    let mut just_below = c.empty_state();
    c.add_delta(
        &mut just_below,
        0,
        f64::from_bits(27.2_f64.to_bits() - 1),
        0.7,
    )
    .unwrap();
    let p = c.partition_below_hi(&just_below, &g(0.1)).unwrap();
    assert_eq!(p.active, empty);
    assert_eq!(p.inactive_number, just_below.number);
}
#[test]
fn merge_inactive_preserves_edge_moments_and_rejects_transactionally() {
    let c = core();
    // Repeated endpoint pools retain realizability even for nonexact counts.
    let mut n = c.empty_state().number;
    let mut u = n.clone();
    let mut an = n.clone();
    let mut au = n.clone();
    an[0] = 0.7;
    au[0] = c.edges()[0] * an[0];
    for _ in 0..1000 {
        c.merge_inactive(&mut n, &mut u, &an, &au).unwrap();
        assert_eq!(u[0], c.edges()[0] * n[0]);
    }
    let before_n = n.clone();
    let before_u = u.clone();
    au[0] = 0.0;
    assert!(c.merge_inactive(&mut n, &mut u, &an, &au).is_err());
    assert_eq!(n, before_n);
    assert_eq!(u, before_u);
    let empty = c.empty_state().number;
    c.merge_inactive(&mut n, &mut u, &empty, &empty).unwrap();
    assert_eq!(n, before_n);
    assert_eq!(u, before_u);
}
#[test]
fn mixed_partition_matches_moments_is_idempotent_and_preserves_photo_rates() {
    let c = core();
    let p = cell(&c, 10.0, 80.0, 30.0);
    let frozen = p.clone();
    let split = c.partition_below_hi(&p, &g(0.05)).unwrap();
    assert_eq!(p, frozen);
    assert!(split.active.number[0] > 0.0 && split.inactive_number[0] > 0.0);
    assert_eq!(split.active.support_lo[0], 13.6);
    assert_eq!(split.active.support_hi[0], 80.0);
    close(
        split.active.number[0] + split.inactive_number[0],
        1.0,
        64.0 * f64::EPSILON,
    );
    close(
        split.active.energy_ref[0] + split.inactive_energy_ref[0],
        30.0,
        128.0 * f64::EPSILON,
    );
    let again = c.partition_below_hi(&split.active, &g(0.05)).unwrap();
    assert_eq!(again.active, split.active);
    assert_eq!(again.inactive_number, c.empty_state().number);
    let old = c
        .prepare(&p, &g(0.05))
        .unwrap()
        .evaluate([1e-4, 1e-5, 1e-6], 1e-4, 0.0)
        .unwrap();
    let active = c
        .prepare(&split.active, &g(0.05))
        .unwrap()
        .evaluate([1e-4, 1e-5, 1e-6], 1e-4, 0.0)
        .unwrap();
    for j in 0..3 {
        close(old.photo.gamma_s[j], active.photo.gamma_s[j], 1e-9);
        close(
            old.photo.heat_erg_per_absorber_s[j],
            active.photo.heat_erg_per_absorber_s[j],
            1e-9,
        );
    }
}
#[test]
fn monotone_two_cut_transfers_keep_total_count_energy_and_redshift_work() {
    let c = core();
    let initial = cell(&c, 10.0, 80.0, 30.0);
    let first = c.partition_below_hi(&initial, &g(0.05)).unwrap();
    let mut active = first.active;
    let mut pn = first.inactive_number;
    let mut pu = first.inactive_energy_ref;
    let mut work = 0.0;
    let mut prior_r = 1.0;
    for a in [0.06, 0.08] {
        let r = 0.05 / a;
        let prior_q = active.energy_ref.iter().sum::<f64>() + pu.iter().sum::<f64>();
        work += (prior_r - r) * prior_q;
        let split = c.partition_below_hi(&active, &g(a)).unwrap();
        for k in 0..pn.len() {
            pn[k] += split.inactive_number[k];
            pu[k] += split.inactive_energy_ref[k];
        }
        active = split.active;
        c.validate_state(&active).unwrap();
        close(
            active.number.iter().sum::<f64>() + pn.iter().sum::<f64>(),
            1.0,
            64.0 * f64::EPSILON,
        );
        let u = r * (active.energy_ref.iter().sum::<f64>() + pu.iter().sum::<f64>());
        close(u + work, 30.0, 128.0 * f64::EPSILON);
        prior_r = r;
    }
}
