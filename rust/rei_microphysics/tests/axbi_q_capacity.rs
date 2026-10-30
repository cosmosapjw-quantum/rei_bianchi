//! C4: direct source-constrained directional-q memory cap and evidence.
use rei_microphysics::axbi_q_capacity::{assess_merge, cap_packets, CapacityPolicy, TaggedPhoton};
use rei_microphysics::axbi_q_reference::{emit_from_axbi_source, CovariantPhoton};
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::AxisymmetricPoint;

fn geom(a: f64, b: f64) -> rei_microphysics::GeometrySnapshot {
    AxisymmetricPoint::new(a, b, 1e-16, 0.)
        .unwrap()
        .snapshot()
        .unwrap()
}
fn tag(g: &rei_microphysics::GeometrySnapshot, energy: f64, mu: f64, index: usize) -> TaggedPhoton {
    TaggedPhoton {
        angular_key: index,
        photon: CovariantPhoton::from_local(g, energy, [(1. - mu * mu).sqrt(), 0., mu], 1.)
            .unwrap(),
    }
}
fn policy(cap: usize) -> CapacityPolicy {
    CapacityPolicy {
        cap,
        max_events_per_h: [1.0; 3],
        max_heat_ev_per_h: 1e3,
        neutral_cm3: [1e-6, 1e-7, 1e-8],
        duration_s: 1e8,
    }
}
#[test]
fn same_local_direction_at_two_lrs_emission_epochs_is_not_same_k_direction() {
    let early = geom(0.05, 0.);
    let late = geom(0.08, 0.01);
    let now = geom(0.1, 0.015);
    let a = tag(&early, 35., 0.5, 3);
    let b = tag(&late, 35., 0.5, 3);
    let check = assess_merge(&a, &b, &now, &now, policy(1)).unwrap();
    assert!(!check.accepted);
    assert_eq!(check.reason, "HOLD_Q_DIRECTION");
    assert!(check.energy_deficit_now_ev_per_h > 0.);
    assert!(check.energy_deficit_now_ev_per_h < 0.01);
}
#[test]
fn flrw_same_direction_merges_preserve_number_k_and_energy() {
    let g0 = geom(0.05, 0.);
    let g1 = geom(0.050005, 0.);
    let g2 = geom(0.050010, 0.);
    let a = tag(&g0, 34.9, 0.5, 3);
    let b = tag(&g1, 35.3, 0.5, 3);
    let result = assess_merge(&a, &b, &g1, &g2, policy(1)).unwrap();
    assert!(result.accepted, "{}", result.reason);
    let merged = result.merged.unwrap();
    assert!((merged.photon.photons_per_h - 2.).abs() < 1e-14);
    for i in 0..3 {
        assert!((2. * merged.photon.k_ev[i] - a.photon.k_ev[i] - b.photon.k_ev[i]).abs() < 1e-11);
    }
    assert!(result.energy_deficit_now_ev_per_h.abs() < 1e-12);
    assert!(result.energy_deficit_future_ev_per_h.abs() < 1e-12);
}
#[test]
fn angular_labels_and_threshold_tube_are_hard_guards() {
    let g0 = geom(0.05, 0.);
    let gf = geom(0.050005, 0.);
    let a = tag(&g0, 54.1, 0.5, 2);
    let b = tag(&g0, 54.8, 0.5, 2);
    let t = assess_merge(&a, &b, &g0, &gf, policy(1)).unwrap();
    assert!(!t.accepted);
    assert_eq!(t.reason, "HOLD_THRESHOLD_TUBE");
    let c = tag(&g0, 35.0, 0.5, 9);
    let d = tag(&g0, 35.2, 0.5, 2);
    let r = assess_merge(&c, &d, &g0, &gf, policy(1)).unwrap();
    assert!(!r.accepted);
    assert_eq!(r.reason, "HOLD_DIFFERENT_ANGULAR_CELL");
}
#[test]
fn actual_source_cohort_cap_is_transactional_and_preserves_energy() {
    let source = AxbiSource::new(1.9e-7, 0.2, 16, 8).unwrap();
    let g0 = geom(0.05, 0.);
    let gf = geom(0.050001, 0.);
    let packets = emit_from_axbi_source(&source, &g0, 20., 1e8).unwrap();
    assert_eq!(packets.len(), 384);
    let tags: Vec<TaggedPhoton> = packets
        .into_iter()
        .enumerate()
        .map(|(i, p)| TaggedPhoton {
            angular_key: i / 48,
            photon: p,
        })
        .collect();
    let baseline_count: f64 = tags.iter().map(|p| p.photon.photons_per_h).sum();
    let baseline_energy: f64 = tags
        .iter()
        .map(|p| p.photon.photons_per_h * p.photon.energy_at(&g0).unwrap())
        .sum();
    let report = cap_packets(&tags, &g0, &gf, policy(256)).unwrap();
    assert_eq!(report.packets.len(), 256);
    assert_eq!(tags.len(), 384);
    let new_count: f64 = report.packets.iter().map(|p| p.photon.photons_per_h).sum();
    let new_energy: f64 = report
        .packets
        .iter()
        .map(|p| p.photon.photons_per_h * p.photon.energy_at(&g0).unwrap())
        .sum();
    assert!((baseline_count - new_count).abs() <= 1e-12 * baseline_count);
    assert!((baseline_energy - new_energy).abs() <= 1e-12 * baseline_energy);
    assert!(report.merges > 0);
}
#[test]
fn hard_cap_below_threshold_partition_returns_hold_without_mutating_source() {
    let g = geom(0.05, 0.);
    let gf = geom(0.050001, 0.);
    let initial = vec![
        tag(&g, 15., 0.5, 0),
        tag(&g, 30., 0.5, 0),
        tag(&g, 70., 0.5, 0),
    ];
    let before: Vec<_> = initial
        .iter()
        .map(|p| {
            (
                p.angular_key,
                p.photon.photons_per_h.to_bits(),
                p.photon.k_ev.map(f64::to_bits),
            )
        })
        .collect();
    let result = cap_packets(&initial, &g, &gf, policy(1));
    let hold = result.unwrap_err();
    assert_eq!(hold.reason, "HOLD_BUDGET_THRESHOLD_OR_DIRECTION");
    assert_eq!(initial.len(), before.len());
    for (packet, (angular_key, count_bits, k_bits)) in initial.iter().zip(before.iter()) {
        assert_eq!(packet.angular_key, *angular_key);
        assert_eq!(packet.photon.photons_per_h.to_bits(), *count_bits);
        assert_eq!(packet.photon.k_ev.map(f64::to_bits), *k_bits);
    }
}

#[test]
fn real_signed_background_same_local_emission_direction_only_flrw_merges() {
    use rei_microphysics::axbi_background::{AxbiBackground, BackgroundFamily, Cosmology};
    let cosmology = Cosmology {
        h0_per_s: 67.4e5 / 3.085_677_581_491_367e24,
        omega_m: 0.315,
        omega_r: 0.000092,
        omega_lambda: 0.684908,
    };
    for q in [0.0, 0.01, -0.01] {
        let b = AxbiBackground::new(
            cosmology,
            1.0 / 21.0,
            1.0 / 5.0,
            0.0,
            q,
            BackgroundFamily::PhysicalDensityFixed,
            4096,
        )
        .unwrap();
        let early = b.point_at_scale(1.0 / 21.0).unwrap().geometry().unwrap();
        let late = b.point_at_scale(1.0 / 12.0).unwrap().geometry().unwrap();
        let a = tag(&early, 100.0, 0.5, 1);
        let c = tag(&late, 100.0, 0.5, 1);
        let out = assess_merge(&a, &c, &late, &late, policy(1)).unwrap();
        if q == 0.0 {
            assert!(out.accepted, "FLRW: {}", out.reason);
        } else {
            assert!(!out.accepted);
            assert_eq!(out.reason, "HOLD_Q_DIRECTION");
            assert!(out.energy_deficit_now_ev_per_h > 0.0);
        }
    }
}

#[test]
fn a_cap_that_already_fits_must_still_validate_physical_packet_inputs() {
    let g = geom(0.05, 0.0);
    let input = [TaggedPhoton {
        angular_key: 0,
        photon: CovariantPhoton {
            k_ev: [f64::NAN, 1.0, 0.0],
            photons_per_h: 1.0,
        },
    }];
    let e = cap_packets(&input, &g, &g, policy(32)).unwrap_err();
    assert_eq!(e.reason, "INVALID_CAP_INPUT");
}
