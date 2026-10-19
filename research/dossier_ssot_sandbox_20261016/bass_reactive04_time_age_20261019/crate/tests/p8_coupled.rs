mod common;
use common::fixture;
use rei_iso_couple_reference::{
    bianchi_i::GeometryBackground,
    deuterium_thermal_coupling::CxOwnership,
    midpoint_coupled::{Centering, MidpointBridge},
    positive_spectral::SpectralMode,
    reflection_pool::PoolLimits,
};
#[test]
fn native_joint_macrostep_converges_quadratically_in_di_events() {
    let mut values = Vec::new();
    for n in [8, 16, 32] {
        let (base, ctl, mut cfg, gas) =
            fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
        cfg.owner = CxOwnership::AtomicRhs;
        let bridge = MidpointBridge(base, ctl, PoolLimits::default(), Centering::Joint);
        let mut state = bridge.initial(gas, &cfg, 0.).unwrap();
        let h = 8e10 / n as f64;
        let mut count = 0.;
        for _ in 0..n {
            let vm = bridge
                .0
                .geometry
                .snapshot(state.time_s + h / 2.)
                .unwrap()
                .volume_factor()
                .unwrap();
            let out = bridge.advance(&state, &cfg, h).unwrap();
            count += out.chemistry_budget.photo_events_m3[3] * vm;
            state = out.state;
        }
        values.push(count);
    }
    let ratio = (values[0] - values[1]) / (values[1] - values[2]);
    let p = ratio.log2();
    assert!(p > 1.8 && p < 2.25, "joint order {p}; DI={values:?}");
}
#[test]
fn legacy_switch_is_exact_parent_map() {
    use common::bit_parity;
    use rei_iso_couple_reference::reflection_pool::ReflectionPooledBridge;
    let (base, ctl, cfg, gas) = fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    let parent = ReflectionPooledBridge(base.clone(), ctl, PoolLimits::default());
    let new = MidpointBridge(base, ctl, PoolLimits::default(), Centering::Legacy);
    let a = parent.initial(gas, &cfg, 0.).unwrap();
    bit_parity(
        &parent.advance(&a, &cfg, 2e9).unwrap(),
        &new.advance(&a, &cfg, 2e9).unwrap(),
    );
}
#[test]
fn joint_predictor_births_and_ledgers_are_not_committed_twice() {
    use rei_iso_couple_reference::reflection_pool::ReflectionPooledBridge;
    let (base, ctl, mut cfg, gas) = fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    let old = ReflectionPooledBridge(base.clone(), ctl, PoolLimits::default());
    let a = old.initial(gas, &cfg, 0.).unwrap();
    let r = old.advance(&a, &cfg, 2e10).unwrap();
    cfg.owner = CxOwnership::AtomicRhs;
    let new = MidpointBridge(base, ctl, PoolLimits::default(), Centering::Joint);
    let (s, d) = new.advance_with_diagnostics(&a, &cfg, 2e10).unwrap();
    assert_eq!(r.source_birth_com3.to_bits(), s.source_birth_com3.to_bits());
    assert_eq!(
        r.state.source_injected_energy_j_com3.to_bits(),
        s.state.source_injected_energy_j_com3.to_bits()
    );
    assert_eq!(r.state.cohorts.len(), s.state.cohorts.len());
    assert_eq!(s.state.chemistry_accepted, 1);
    assert_eq!(s.state.full.elapsed_s, 2e10);
    assert_eq!(d.computed_paths, d.reused_paths);
    let photons = s.state.cohorts.iter().map(|q| q.n_comoving_m3).sum::<f64>();
    assert!(
        (photons + s.state.photon_absorbed_count_com3 - s.state.source_injected_count_com3).abs()
            < 1e-12 * s.state.source_injected_count_com3
    );
    assert!(s.global_energy_relative_error < 3e-10);
}
#[test]
fn all_centering_controls_run_with_actual_channels() {
    for mode in [
        Centering::Legacy,
        Centering::GasOnly,
        Centering::OpacityOnly,
        Centering::Joint,
    ] {
        let (base, ctl, mut cfg, gas) =
            fixture(-0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
        cfg.owner = CxOwnership::AtomicRhs;
        let bridge = MidpointBridge(base, ctl, PoolLimits::default(), mode);
        let a = bridge.initial(gas, &cfg, 0.).unwrap();
        let s = bridge.advance(&a, &cfg, 2e10).unwrap();
        let b = s.chemistry_budget;
        assert!(b.rr_events_m3.iter().sum::<f64>() > 0.);
        assert!(b.cx_signed_m3.abs() > 0.);
        assert!(b.freefree_integrated_j_m3 > 0.);
        assert!(b.cmb_change_j_m3.abs() > 0.);
    }
}
#[test]
fn joint_transaction_rejects_wrong_cx_owner_and_invalid_dt() {
    let (base, ctl, mut cfg, gas) = fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    let bridge = MidpointBridge(base, ctl, PoolLimits::default(), Centering::Joint);
    let a = bridge.initial(gas, &cfg, 0.).unwrap();
    let before = format!("{a:?}");
    assert!(bridge.advance(&a, &cfg, 1e9).is_err());
    cfg.owner = CxOwnership::AtomicRhs;
    for h in [0., -1., f64::NAN, 1e20] {
        assert!(bridge.advance(&a, &cfg, h).is_err());
    }
    assert_eq!(before, format!("{a:?}"));
}
#[test]
fn joint_native_cx_has_second_order_di_events_and_single_clock() {
    let mut vals = Vec::new();
    for n in [8, 16, 32] {
        let (base, ctl, mut cfg, gas) =
            fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
        cfg.cx_controls.rtol = 1e-12;
        cfg.cx_controls.atol_normalized = 1e-15;
        let bridge = MidpointBridge(base, ctl, PoolLimits::default(), Centering::JointCxSplit);
        let mut state = bridge.initial(gas, &cfg, 0.).unwrap();
        let h = 8e10 / n as f64;
        let mut a = 0.;
        for _ in 0..n {
            let vm = bridge
                .0
                .geometry
                .snapshot(state.time_s + h / 2.)
                .unwrap()
                .volume_factor()
                .unwrap();
            let s = bridge.advance(&state, &cfg, h).unwrap();
            a += s.chemistry_budget.photo_events_m3[3] * vm;
            state = s.state;
        }
        assert_eq!(state.full.elapsed_s, 8e10);
        assert_eq!(state.time_s, 8e10);
        vals.push(a);
    }
    let p = ((vals[0] - vals[1]) / (vals[1] - vals[2])).log2();
    assert!(p > 1.8 && p < 2.25, "order={p}; DI={vals:?}");
}
