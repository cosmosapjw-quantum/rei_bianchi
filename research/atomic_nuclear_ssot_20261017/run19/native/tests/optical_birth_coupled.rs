#[path = "../examples/common/mod.rs"]
mod common;
use rei_iso_couple_reference::{
    bass_optical_birth::{BassOpticalBirthBridge, LayerControls},
    bass_retarded::BassRetardedBridge,
    bass_source_bridge::BassSourceBridge,
    positive_spectral::SpectralMode,
    retarded_transport::RetardedControls,
};
fn make() -> (
    BassOpticalBirthBridge,
    rei_iso_couple_reference::full_network::FullState,
    rei_iso_couple_reference::full_network::NetworkConfig,
    f64,
) {
    let g = common::load("SIGNED_MINUS", 121);
    let p = g.point_at_x(0.7).unwrap();
    let end = g.point_at_x(0.70004).unwrap();
    let (full, conf, source) = common::fixture(&g, 0.7);
    let bridge = BassOpticalBirthBridge(
        BassSourceBridge::new(source, g, 2.7255).unwrap(),
        RetardedControls::new(4, 2, SpectralMode::OriginalCellMean)
            .unwrap()
            .with_threshold_events(),
        LayerControls::default(),
    );
    (bridge, full, conf, end.time_s - p.time_s)
}
#[test]
fn native_source_optical_layer_updates_one_photon_and_gas_owner() {
    let (b, full, c, dt) = make();
    let state = b.initial(full.clone(), &c, full.elapsed_s).unwrap();
    let initial = format!("{state:?}");
    let (out, diag) = b.advance_with_diagnostics(&state, &c, dt).unwrap();
    assert_eq!(initial, format!("{state:?}"));
    assert!(diag.panels > 1 && diag.tau_seed > 1.0);
    assert_eq!(diag.retarded.newborn_gl_count, 384 * 4 * diag.panels);
    assert_eq!(out.state.chemistry_accepted, 1);
    assert!(
        out.chemistry_budget
            .photo_events_m3
            .iter()
            .all(|v| *v > 0.0)
    );
    assert!(out.chemistry_budget.rr_events_m3.iter().sum::<f64>() > 0.0);
    assert!(out.chemistry_budget.freefree_integrated_j_m3 > 0.0);
    assert!(out.chemistry_budget.cmb_change_j_m3 > 0.0);
    let surv = out
        .state
        .cohorts
        .iter()
        .map(|p| p.n_comoving_m3)
        .sum::<f64>();
    assert!(
        ((surv + out.state.photon_absorbed_count_com3) / out.state.source_injected_count_com3
            - 1.0)
            .abs()
            < 2e-12
    );
    assert!(out.global_energy_relative_error < 3e-10);
    assert!(
        out.state
            .cohorts
            .iter()
            .all(|co| co.birth_time_s > state.time_s && co.birth_time_s < out.state.time_s)
    );
}
#[test]
fn cohort_budget_failure_rolls_back_entire_trial() {
    let (mut b, full, c, dt) = make();
    let state = b.initial(full.clone(), &c, full.elapsed_s).unwrap();
    let initial = format!("{state:?}");
    b.2.max_cohorts = 1;
    assert!(b.advance(&state, &c, dt).is_err());
    assert_eq!(initial, format!("{state:?}"));
}
#[test]
fn thin_birth_panel_matches_unchanged_uniform_gl4_path() {
    let (b, full, c, _) = make();
    let s = b.initial(full.clone(), &c, full.elapsed_s).unwrap();
    let dt = 1e7;
    let (a, diag) = b.advance_with_diagnostics(&s, &c, dt).unwrap();
    assert_eq!(diag.panels, 1);
    let old = BassRetardedBridge(b.0.clone(), b.1)
        .advance(&s, &c, dt)
        .unwrap();
    let na = a
        .state
        .cohorts
        .iter()
        .map(|co| co.n_comoving_m3)
        .sum::<f64>();
    let nb = old
        .state
        .cohorts
        .iter()
        .map(|co| co.n_comoving_m3)
        .sum::<f64>();
    assert!((na / nb - 1.0).abs() < 2e-12);
    assert!((a.state.full.gas.thermal_j_m3 / old.state.full.gas.thermal_j_m3 - 1.0).abs() < 2e-12);
}
#[test]
fn source_identity_and_rule_domain_rejections_are_explicit() {
    let (mut b, full, c, dt) = make();
    let s = b.initial(full.clone(), &c, full.elapsed_s).unwrap();
    let mut bad = c;
    bad.photon_source = "WRONG";
    assert!(b.advance(&s, &bad, dt).is_err());
    b.2.growth = 1.0;
    assert!(b.advance(&s, &c, dt).is_err());
    b.2.growth = 2.0;
    b.1.birth_gauss_nodes = 2;
    assert!(b.advance(&s, &c, dt).is_err());
}
