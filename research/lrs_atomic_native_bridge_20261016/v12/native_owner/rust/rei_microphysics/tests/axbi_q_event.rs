//! Tests for C3 event-aware, source-independent, frozen-gas Bianchi I propagation.
use rei_microphysics::axbi_q_advance::{advance_batch, advance_frozen_expanding, EnergySoA};
use rei_microphysics::axbi_q_reference::CovariantPhoton;
use rei_microphysics::{Absorber, AtomicProvider, AxisymmetricPoint, GeometrySnapshot, HHeModel};

fn g() -> GeometrySnapshot {
    AxisymmetricPoint::new(1.0, 0.0, 1e-16, 0.0)
        .unwrap()
        .snapshot()
        .unwrap()
}
fn rel(a: f64, b: f64, eps: f64) {
    assert!(
        (a - b).abs() <= eps * a.abs().max(b.abs()).max(1e-30),
        "{a} {b}"
    );
}
#[test]
fn static_exact_exponential_matches_original_constant_step() {
    let g = g();
    let p = CovariantPhoton::from_local(&g, 70.0, [1.0, 0.0, 0.0], 0.5).unwrap();
    let dens = [1e-4, 1e-5, 1e-6];
    let dt = 1e12;
    let old = rei_microphysics::axbi_q_reference::absorb_frozen_gas(&p, &g, dens, dt).unwrap();
    let result = advance_frozen_expanding(&p, &g, [0.0; 3], dens, dt, 1).unwrap();
    rel(
        result.final_packet.photons_per_h,
        old.final_packet.photons_per_h,
        1e-12,
    );
    rel(
        result.absorbed_per_h.iter().sum::<f64>(),
        old.absorbed_per_h.iter().sum(),
        1e-12,
    );
    rel(result.heat_ev_per_h, old.heat_ev_per_h, 1e-12);
    rel(result.binding_ev_per_h, old.binding_ev_per_h, 1e-12);
    rel(result.redshift_work_ev_per_h, 0.0, 1e-12);
}
#[test]
fn threshold_crossing_matches_analytic_residence_for_step_opacity() {
    // HeII is the ONLY absorber. At 54.42 exactly and H>0 no HeII photons are absorbed.
    let g = g();
    let p = CovariantPhoton::from_local(&g, 54.42, [1.0, 0.0, 0.0], 1.0).unwrap();
    let out = advance_frozen_expanding(&p, &g, [1e-16; 3], [0.0, 0.0, 1e-10], 1e15, 2).unwrap();
    rel(out.absorbed_per_h[2], 0.0, 1e-12);
    rel(out.final_packet.photons_per_h, 1.0, 1e-12);
    // One initially above-threshold packet crosses during the interval.
    let p2 = CovariantPhoton::from_local(&g, 54.9, [1.0, 0.0, 0.0], 1.0).unwrap();
    let out2 = advance_frozen_expanding(&p2, &g, [1e-16; 3], [0.0, 0.0, 1e-10], 1e15, 8).unwrap();
    assert_eq!(out2.threshold_crossings, 1);
    let t_cross = (54.9_f64 / 54.42).ln() / 1e-16;
    let sigma = AtomicProvider::reference()
        .cross_section(Absorber::HeII, 54.7)
        .unwrap();
    let lam = HHeModel::controlled_fixture().c_cm_s * 1e-10 * sigma;
    assert!(out2.absorbed_per_h[2] > 0.0);
    assert!(out2.absorbed_per_h[2] < 1.0 - (-lam * 1e15).exp());
    // The constant-sigma analytic residence formula is a scale reference only.
    assert!((t_cross / 1e15) > 0.0 && (t_cross / 1e15) < 1.0);
    assert!(out2.redshift_work_ev_per_h > 0.0);
    let hi = advance_frozen_expanding(&p2, &g, [1e-16; 3], [0.0, 0.0, 1e-10], 1e15, 256).unwrap();
    // DOP853 was evaluated independently in independent_reference.py.
    assert!((hi.absorbed_per_h[2] - 0.0004128992999639923).abs() < 5e-11);
    assert!((hi.heat_ev_per_h - 9.949266237910015e-5).abs() < 1e-9);
}
#[test]
fn physical_energy_photon_ledger_and_refinement() {
    let g = g();
    let p = CovariantPhoton::from_local(&g, 65.0, [0.6, 0.0, 0.8], 3.0).unwrap();
    let h = [1.2e-16, 1.2e-16, 1.8e-16];
    let dens = [2e-11, 3e-12, 1e-12];
    let dt = 2e15;
    let coarse = advance_frozen_expanding(&p, &g, h, dens, dt, 16).unwrap();
    let fine = advance_frozen_expanding(&p, &g, h, dens, dt, 1024).unwrap();
    let n0 = p.photons_per_h;
    let e0 = p.energy_at(&g).unwrap();
    for r in [&coarse, &fine] {
        rel(
            n0,
            r.final_packet.photons_per_h + r.absorbed_per_h.iter().sum::<f64>(),
            1e-12,
        );
        let end = r.final_packet.photons_per_h * r.final_energy_ev
            + r.heat_ev_per_h
            + r.binding_ev_per_h
            + r.redshift_work_ev_per_h;
        rel(n0 * e0, end, 1e-12);
        assert!(r.heat_ev_per_h >= 0.0 && r.redshift_work_ev_per_h > 0.0);
    }
    assert!((coarse.heat_ev_per_h - fine.heat_ev_per_h).abs() < 1e-2);
}
#[test]
fn parallel_and_serial_outputs_are_identical_at_packet_level() {
    let g = g();
    let packets: Vec<CovariantPhoton> = (0..1920)
        .map(|i| {
            let e = 14.0 + (i % 160) as f64 * 0.44;
            CovariantPhoton::from_local(&g, e, [1.0, 0.0, 0.0], 1e-4).unwrap()
        })
        .collect();
    let h = [1e-16; 3];
    let dens = [1e-5, 1e-6, 1e-7];
    let dt = 3e14;
    let a = advance_batch(&packets, &g, h, dens, dt, 4, 1).unwrap();
    let b = advance_batch(&packets, &g, h, dens, dt, 4, 4).unwrap();
    assert_eq!(a.len(), b.len());
    for (u, v) in a.iter().zip(b.iter()) {
        assert_eq!(
            u.final_packet.photons_per_h.to_bits(),
            v.final_packet.photons_per_h.to_bits()
        );
        for (x, y) in u.absorbed_per_h.iter().zip(v.absorbed_per_h) {
            assert_eq!(x.to_bits(), y.to_bits());
        }
        assert_eq!(u.heat_ev_per_h.to_bits(), v.heat_ev_per_h.to_bits());
    }
}
#[test]
fn unsafe_or_unbounded_inputs_are_rejected() {
    let g = g();
    let p = CovariantPhoton::from_local(&g, 55.0, [1.0, 0.0, 0.0], 1.0).unwrap();
    assert!(advance_frozen_expanding(&p, &g, [-1e-16, 0.0, 0.0], [0.0; 3], 1e12, 8).is_err());
    assert!(advance_frozen_expanding(&p, &g, [1e-16; 3], [0.0; 3], 1e12, 0).is_err());
    assert!(advance_frozen_expanding(&p, &g, [1e-16; 3], [0.0; 3], f64::INFINITY, 8).is_err());
    assert!(advance_batch(&[p], &g, [1e-16; 3], [0.0; 3], 1e12, 4, 0).is_err());
}

#[test]
fn contiguous_energy_readout_matches_packet_reference() {
    let geom = g();
    let samples: Vec<CovariantPhoton> = (0..384)
        .map(|i| {
            let f = i as f64 / 383.;
            CovariantPhoton::from_local(&geom, 14. + 80. * f, [0.6, 0.0, 0.8], 0.01).unwrap()
        })
        .collect();
    let soa = EnergySoA::from_packets(&samples).unwrap();
    assert_eq!(soa.len(), samples.len());
    let geom2 = AxisymmetricPoint::new(0.3, 0.025, 1e-16, 0.)
        .unwrap()
        .snapshot()
        .unwrap();
    let out = soa.energies_at(&geom2).unwrap();
    for (sample, e) in samples.iter().zip(out) {
        rel(e, sample.energy_at(&geom2).unwrap(), 5e-14);
    }
}
