use bass_common::common::{bit_parity, fixture};
use rei_iso_couple_reference::{
    bass_reactive::{BindingBridge, BoundSourceAgeBridge, GeometryChoice},
    midpoint_coupled::{Centering, MidpointBridge},
    positive_spectral::SpectralMode,
    reflection_pool::PoolLimits,
};
#[test]
fn original_constant_map_keeps_all_state_bits() {
    let (old, ctrl, mut c, g) = fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    c.cx_controls.rtol = 1e-12;
    c.cx_controls.atol_normalized = 1e-14;
    let new = BoundSourceAgeBridge::new(old.source.clone(), GeometryChoice::constant(old.geometry))
        .unwrap();
    let legacy = MidpointBridge(old, ctrl, PoolLimits::default(), Centering::JointCxSplit);
    let bound = BindingBridge(new, ctrl, PoolLimits::default(), Centering::JointCxSplit);
    let mut a = legacy.initial(g, &c, 0.).unwrap();
    let mut b = a.clone();
    for _ in 0..3 {
        let x = legacy.advance(&a, &c, 1e9).unwrap();
        let y = bound.advance(&b, &c, 1e9).unwrap();
        bit_parity(&x, &y);
        a = x.state;
        b = y.state;
    }
}
mod bass_common;
use rei_iso_couple_reference::{
    bound_adaptive::{events_comoving, photon_projection},
    source_age::Cohort,
};
#[test]
fn mismatched_birth_geometry_rejected_without_input_mutation() {
    let (b, c, g) = bass_common::fixture("SIGNED_MINUS", 121, 0., false, 8192);
    let mut a = b.initial(g, &c, 0.).unwrap();
    let mut bg = b.0.geometry.snapshot(0.).unwrap();
    bg.scale_factors[0] *= 1.01;
    a.cohorts.push(Cohort {
        birth_time_s: 0.,
        birth_geometry: bg,
        energy_at_birth_ev: 13.7,
        direction_at_birth: [1., 0., 0.],
        n_comoving_m3: 0.,
        spectral_index: 0,
        angular_index: 0,
    });
    let saved = format!("{a:?}");
    assert!(b.advance(&a, &c, 1e9).is_err());
    assert_eq!(saved, format!("{a:?}"));
}
#[test]
fn actual_bass_full_reactions_and_one_source_transaction() {
    let (b, c, g) = bass_common::fixture("SIGNED_MINUS", 121, 0., false, 8192);
    let mut a = b.initial(g, &c, 0.).unwrap();
    for _ in 0..2 {
        let births = b.emit_births(a.time_s, 1e9, &c).unwrap();
        let born = births.iter().map(|x| x.n_comoving_m3).sum::<f64>();
        let o = b.advance(&a, &c, 1e9).unwrap();
        assert_eq!(o.state.cohorts.len(), a.cohorts.len() + births.len());
        assert_eq!(
            o.state.source_injected_count_com3.to_bits(),
            (a.source_injected_count_com3 + born).to_bits()
        );
        assert!(o.chemistry_budget.rr_events_m3.iter().sum::<f64>() > 0.);
        assert!(o.chemistry_budget.cx_signed_m3.abs() > 0.);
        assert!(o.chemistry_budget.freefree_integrated_j_m3 > 0.);
        assert!(o.chemistry_budget.cmb_change_j_m3.abs() > 0.);
        let p = photon_projection(&b, &o.state).unwrap();
        assert!(
            ((p.count + o.state.photon_absorbed_count_com3) / o.state.source_injected_count_com3
                - 1.)
                .abs()
                < 3e-12
        );
        assert!(o.global_energy_relative_error < 3e-12);
        a = o.state;
    }
}
#[test]
fn cached_and_uncached_donor_give_identical_complete_native_state() {
    let (b, c, g) = bass_common::fixture("SIGNED_PLUS", 121, 0., false, 8192);
    let (z, _, _) = bass_common::fixture("SIGNED_PLUS", 121, 0., false, 0);
    let a = b.initial(g, &c, 0.).unwrap();
    let x = b.advance(&a, &c, 1e9).unwrap();
    let y = z.advance(&a, &c, 1e9).unwrap();
    bit_parity(&x, &y);
    let (h, m, n) = b.0.geometry.cache_stats();
    assert!(h > m && n <= 8192);
    assert_eq!(z.0.geometry.cache_stats().0, 0);
}
#[test]
fn nonzero_origin_half_step_events_use_their_own_volumes() {
    let (b, c, g) = bass_common::fixture("SIGNED_MINUS", 121, 2e12, false, 8192);
    let a = b.initial(g, &c, 2e12).unwrap();
    let x = b.advance(&a, &c, 1e9).unwrap();
    let y = b.advance(&x.state, &c, 1e9).unwrap();
    let e1 = events_comoving(&b, &x, a.time_s).unwrap();
    let e2 = events_comoving(&b, &y, x.state.time_s).unwrap();
    let v1 =
        b.0.geometry
            .snapshot(a.time_s + 0.5e9)
            .unwrap()
            .volume_factor()
            .unwrap();
    let v2 =
        b.0.geometry
            .snapshot(a.time_s + 1.5e9)
            .unwrap()
            .volume_factor()
            .unwrap();
    let vm =
        b.0.geometry
            .snapshot(a.time_s + 1e9)
            .unwrap()
            .volume_factor()
            .unwrap();
    assert_ne!(v1.to_bits(), v2.to_bits());
    for i in 0..4 {
        let proper =
            x.chemistry_budget.photo_events_m3[i] * v1 + y.chemistry_budget.photo_events_m3[i] * v2;
        assert_eq!((e1[i] + e2[i]).to_bits(), proper.to_bits());
    }
    let wrong =
        (x.chemistry_budget.photo_events_m3[0] + y.chemistry_budget.photo_events_m3[0]) * vm;
    assert_ne!(wrong.to_bits(), (e1[0] + e2[0]).to_bits());
    assert_eq!(y.state.time_s.to_bits(), (a.time_s + 2e9).to_bits());
}
#[test]
fn donor_domain_rejection_is_transactional() {
    let (b, c, g) = bass_common::fixture("COLD_FLRW", 121, 0., false, 8192);
    let a = b.initial(g, &c, 0.).unwrap();
    let saved = format!("{a:?}");
    assert!(b.advance(&a, &c, b.0.geometry.domain_s()[1] * 1.1).is_err());
    assert_eq!(saved, format!("{a:?}"));
    assert!(b.0.geometry.snapshot(-1.).is_err());
}
#[test]
fn actual_d_threshold_crossing_and_no_numerical_loss() {
    let (b, c, g) = bass_common::fixture("SIGNED_MINUS", 121, 0., false, 8192);
    let mut a = b.initial(g, &c, 0.).unwrap();
    for mu in [-0.4f64, 0.4] {
        a.cohorts.push(Cohort {
            birth_time_s: 0.,
            birth_geometry: b.0.geometry.snapshot(0.).unwrap(),
            energy_at_birth_ev: 13.60214,
            direction_at_birth: [(1. - mu * mu).sqrt(), 0., mu],
            n_comoving_m3: 1e-12,
            spectral_index: 900,
            angular_index: 900,
        });
    }
    let (o, d) = b.advance_with_diagnostics(&a, &c, 1e10).unwrap();
    assert!(d.threshold_crossings > 0);
    assert_eq!(
        o.state.cohorts.len(),
        a.cohorts.len() + b.emit_births(0., 1e10, &c).unwrap().len()
    );
    assert!(o.global_energy_relative_error < 3e-12);
    assert!(o.chemistry_budget.photo_events_m3[3] > 0.);
}
#[test]
fn split_spectrum_retains_original_labels_and_birth_records() {
    let (b, c, g) = bass_common::fixture("SIGNED_PLUS", 121, 0., true, 8192);
    let a = b.initial(g, &c, 0.).unwrap();
    let births = b.emit_births(0., 1e9, &c).unwrap();
    let o = b.advance(&a, &c, 1e9).unwrap();
    assert!(births.len() > 4000);
    assert_eq!(births.len(), o.state.cohorts.len());
    for (x, y) in births.iter().zip(&o.state.cohorts) {
        assert_eq!(x.birth_time_s.to_bits(), y.birth_time_s.to_bits());
        assert_eq!(x.direction_at_birth, y.direction_at_birth);
        assert_eq!(x.spectral_index, y.spectral_index);
    }
}
#[test]
fn constant_s10_four_corner_policy_preserves_results() {
    use rei_iso_couple_reference::{adaptive_step, bound_adaptive, bound_budget, budget_native};
    let (base, ctr, mut c, g) = fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    c.cx_controls.max_attempts = 20000;
    c.cx_controls.max_rate_calls = 2500000;
    let b = BindingBridge(
        BoundSourceAgeBridge::new(base.source.clone(), GeometryChoice::constant(base.geometry))
            .unwrap(),
        ctr,
        PoolLimits::default(),
        Centering::JointCxSplit,
    );
    let o = MidpointBridge(base, ctr, PoolLimits::default(), Centering::JointCxSplit);
    let a = o.initial(g, &c, 0.).unwrap();
    let x = budget_native::attempt(
        &o,
        &a,
        &c,
        1e9,
        &adaptive_step::LocalTolerances::default(),
        &budget_native::NativeBudgetControls::default(),
    )
    .unwrap();
    let y = bound_budget::attempt(
        &b,
        &a,
        &c,
        1e9,
        &bound_adaptive::LocalTolerances::default(),
        &bound_budget::NativeBudgetControls::default(),
    )
    .unwrap();
    assert_eq!(x.action, y.action);
    assert_eq!(x.pairs_evaluated, y.pairs_evaluated);
    assert_eq!(format!("{:?}", x.scales), format!("{:?}", y.scales));
    let xa = x.accepted.unwrap();
    let ya = y.accepted.unwrap();
    assert_eq!(format!("{:?}", xa.state), format!("{:?}", ya.state));
    assert_eq!(xa.photo_events_com3, ya.photo_events_com3);
}
#[test]
fn table_knots_split_without_false_photo_edge_counts() {
    use rei_iso_couple_reference::bass_reactive::split_by_thresholds_from_energies;
    let g = bass_common::geometry("SIGNED_MINUS", 121, 8192);
    // Original donor-reconstructed first knot (roundoff in reconstructed x is retained).
    let knot = 1.0195600729585139e14;
    let ta = knot - 1e10;
    let tb = knot + 1e10;
    let co = Cohort {
        birth_time_s: ta,
        birth_geometry: g.snapshot(ta).unwrap(),
        energy_at_birth_ev: 100.,
        direction_at_birth: [1., 0., 0.],
        n_comoving_m3: 1.,
        spectral_index: 0,
        angular_index: 0,
    };
    let e0 = co.ray_at(&g.snapshot(ta).unwrap()).unwrap().energy_ev;
    let e1 = co.ray_at(&g.snapshot(tb).unwrap()).unwrap().energy_ev;
    let x = split_by_thresholds_from_energies(&g, &co, ta, tb, e0, e1, 13.602134599702).unwrap();
    assert_eq!(x.len(), 3);
    assert!((x[1] - knot).abs() < 10.);
    assert_eq!(g.edge_count(e0, e1, 13.602134599702, x.len() - 2), 0);
}
