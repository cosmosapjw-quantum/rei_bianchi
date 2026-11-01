//! Source-bound covariant momentum packet reference (no chemistry ODE).
use rei_microphysics::axbi_q_reference::{
    absorb_frozen_gas, emit_from_axbi_source, CovariantPhoton,
};
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::{AxisymmetricPoint, CharacteristicRay};

fn geo(a: f64, b: f64) -> rei_microphysics::GeometrySnapshot {
    AxisymmetricPoint::new(a, b, 1e-17, 0.0)
        .unwrap()
        .snapshot()
        .unwrap()
}
fn approx(a: f64, b: f64, tol: f64) {
    assert!(
        (a - b).abs() <= tol * a.abs().max(b.abs()).max(1.0),
        "{a} vs {b}"
    );
}
#[test]
fn q_packet_exact_freeflight_matches_original_characteristic() {
    let g0 = geo(1. / 21., 0.);
    for direction in [[1., 0., 0.], [0., 0., 1.], [0.6, 0., 0.8]] {
        let ray = CharacteristicRay::new(67.0, direction, 0.).unwrap();
        let p = CovariantPhoton::from_local(&g0, 67., direction, 1.).unwrap();
        for (a, b) in [(1. / 20., 0.001), (1. / 12., -0.01), (0.2, 0.02)] {
            let gt = geo(a, b);
            let transported = ray.pullback(&g0, &gt).unwrap();
            approx(p.energy_at(&gt).unwrap(), transported.energy_ev, 2e-13);
            let n = p.direction_at(&gt).unwrap();
            for j in 0..3 {
                approx(n[j], transported.direction[j], 2e-13);
            }
        }
    }
}
#[test]
fn native_md14_source_packets_preserve_photon_count_and_energy() {
    let g = geo(1. / 21., 0.);
    let source = AxbiSource::new(1.9e-7, 0.2, 16, 8).unwrap();
    let dt = 1e11_f64;
    let packets = emit_from_axbi_source(&source, &g, 20., dt).unwrap();
    assert_eq!(packets.len(), 48 * 8);
    let count: f64 = packets.iter().map(|p| p.photons_per_h).sum();
    let expected = source.at_redshift(20.).unwrap().per_h_s * dt;
    assert!(
        (count - expected).abs() <= 1e-12 * expected,
        "count={count} expected={expected}"
    );
    let energy: f64 = packets
        .iter()
        .map(|p| p.photons_per_h * p.energy_at(&g).unwrap())
        .sum();
    let shape_e: f64 = source
        .spectral_cells
        .iter()
        .map(|c| c.photon_fraction * c.energy_ev)
        .sum();
    assert!((energy - expected * shape_e).abs() <= 1e-12 * expected * shape_e);
}
#[test]
fn crossing_heii_threshold_has_no_freeflight_leakage() {
    let g0 = geo(1., 0.);
    let g1 = geo(56.52930276087527 / 53.8758, 0.);
    let p = CovariantPhoton::from_local(&g0, 56.52930276087527, [1., 0., 0.], 1.).unwrap();
    assert!(p.energy_at(&g1).unwrap() < 54.42);
    let loss = absorb_frozen_gas(&p, &g1, [0., 0., 1e-2], 1e9).unwrap();
    approx(loss.final_packet.photons_per_h, 1., 2e-13);
    assert_eq!(loss.absorbed_per_h[2], 0.);
}
#[test]
fn frozen_gas_absorption_owns_photons_binding_and_heat_once() {
    let g = geo(0.1, 0.003);
    let p = CovariantPhoton::from_local(&g, 70., [0.6, 0., 0.8], 3.).unwrap();
    let r = absorb_frozen_gas(&p, &g, [0.015, 0.001, 0.0001], 1e9).unwrap();
    assert!(r.final_packet.photons_per_h >= 0.);
    assert!(r.final_packet.photons_per_h < 3.);
    let total: f64 = r.absorbed_per_h.iter().sum();
    approx(r.final_packet.photons_per_h + total, 3., 4e-13);
    let lost_e = 70. * total;
    approx(lost_e, r.binding_ev_per_h + r.heat_ev_per_h, 4e-13);
    assert!(r.absorbed_per_h.iter().all(|x| *x >= 0.));
    assert!(r.heat_ev_per_h >= 0.);
}
#[test]
fn physical_invalid_inputs_are_rejected() {
    let g = geo(0.1, 0.);
    assert!(CovariantPhoton::from_local(&g, 10., [1., 0., 0.], -1.).is_err());
    let p = CovariantPhoton::from_local(&g, 70., [1., 0., 0.], 1.).unwrap();
    assert!(absorb_frozen_gas(&p, &g, [-1., 0., 0.], 1e8).is_err());
    assert!(absorb_frozen_gas(&p, &g, [1., 0., 0.], -1.).is_err());
    assert!(
        emit_from_axbi_source(&AxbiSource::new(1.9e-7, 0.2, 16, 8).unwrap(), &g, 21., 1e6).is_err()
    );
}
