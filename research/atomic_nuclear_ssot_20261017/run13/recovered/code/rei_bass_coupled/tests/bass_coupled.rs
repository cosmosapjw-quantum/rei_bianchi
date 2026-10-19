#[path = "../examples/common/mod.rs"]
mod common;
use rei_iso_couple_reference::{
    bass_retarded::BassRetardedBridge, bass_source_bridge::BassSourceBridge,
    positive_spectral::SpectralMode, retarded_transport::RetardedControls,
};
#[test]
fn source_on_actual_bass_geometry_evolves_gas_and_shared_photons() {
    let g = common::load("SIGNED_MINUS", 121);
    let p = g.point_at_x(0.7).unwrap();
    let end = g.point_at_x(0.70004).unwrap();
    let (full, conf, source) = common::fixture(&g, 0.7);
    let ini = full.gas.nuclei.moments().unwrap().baryon_density_m3 * p.a.powi(3);
    let bridge = BassRetardedBridge(
        BassSourceBridge::new(source, g, 2.7255).unwrap(),
        RetardedControls::new(2, 2, SpectralMode::OriginalCellMean)
            .unwrap()
            .with_threshold_events(),
    );
    let state = bridge.initial(full, &conf, p.time_s).unwrap();
    let snapshot = format!("{state:?}");
    let (out, d) = bridge
        .advance_with_diagnostics(&state, &conf, end.time_s - p.time_s)
        .unwrap();
    assert_eq!(snapshot, format!("{state:?}"));
    assert_eq!(out.state.chemistry_accepted, 1);
    assert!(out.state.full.gas.eos().unwrap().temperature_k != 1.0e4);
    assert!(out.chemistry_budget.rr_events_m3.iter().sum::<f64>() > 0.);
    assert!(out.chemistry_budget.photo_events_m3.iter().all(|x| *x > 0.));
    assert!(out.chemistry_budget.cmb_change_j_m3 > 0.);
    assert!(out.chemistry_budget.freefree_integrated_j_m3 > 0.);
    let total = out
        .state
        .cohorts
        .iter()
        .map(|c| c.n_comoving_m3)
        .sum::<f64>()
        + out.state.photon_absorbed_count_com3;
    assert!((total / out.state.source_injected_count_com3 - 1.).abs() < 2e-12);
    let finalb = out
        .state
        .full
        .gas
        .nuclei
        .moments()
        .unwrap()
        .baryon_density_m3
        * end.a.powi(3);
    assert!((finalb / ini - 1.).abs() < 2e-12);
    assert!(out.global_energy_relative_error < 3e-10);
    assert_eq!(d.newborn_gl_count, 768);
}
#[test]
fn rejected_transaction_does_not_mutate_input() {
    let g = common::load("COLD_FLRW", 121);
    let p = g.point_at_x(0.7).unwrap();
    let (full, conf, source) = common::fixture(&g, 0.7);
    let bridge = BassRetardedBridge(
        BassSourceBridge::new(source, g, 2.7255).unwrap(),
        RetardedControls::new(2, 2, SpectralMode::OriginalCellMean)
            .unwrap()
            .with_threshold_events(),
    );
    let state = bridge.initial(full, &conf, p.time_s).unwrap();
    let snapshot = format!("{state:?}");
    assert!(bridge.advance(&state, &conf, -1.).is_err());
    assert!(bridge.advance(&state, &conf, f64::NAN).is_err());
    let mut bad = conf;
    bad.photon_source = "WRONG_SOURCE";
    assert!(bridge.advance(&state, &bad, 100.).is_err());
    assert_eq!(snapshot, format!("{state:?}"));
}

#[test]
fn explicit_cosmic_cmb_owner_ignores_legacy_fixture_temperature() {
    let g = common::load("COLD_FLRW", 121);
    let p = g.point_at_x(0.7).unwrap();
    let (full, conf, source) = common::fixture(&g, 0.7);
    let bridge = BassRetardedBridge(
        BassSourceBridge::new(source, g, 2.7255).unwrap(),
        RetardedControls::new(2, 2, SpectralMode::OriginalCellMean)
            .unwrap()
            .with_threshold_events(),
    );
    let state = bridge.initial(full, &conf, p.time_s).unwrap();
    let first = bridge.advance(&state, &conf, 1.0e8).unwrap();
    let mut alternate = conf;
    alternate.cmb_temperature_k = 1.0e5;
    let second = bridge.advance(&state, &alternate, 1.0e8).unwrap();
    assert_eq!(
        first.state.full.gas.thermal_j_m3.to_bits(),
        second.state.full.gas.thermal_j_m3.to_bits()
    );
    assert_eq!(
        first.chemistry_budget.cmb_change_j_m3.to_bits(),
        second.chemistry_budget.cmb_change_j_m3.to_bits()
    );
    let mut off = conf;
    off.use_cmb = false;
    let third = bridge.advance(&state, &off, 1.0e8).unwrap();
    assert_eq!(third.chemistry_budget.cmb_change_j_m3, 0.0);
    assert!(first.chemistry_budget.cmb_change_j_m3 > 0.0);
}
