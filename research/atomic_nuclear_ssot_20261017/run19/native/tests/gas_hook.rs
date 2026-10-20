#[path = "../examples/common/mod.rs"]
mod common;
use rei_iso_couple_reference::{
    bass_gas_reference as new, bass_optical_birth as old, bass_source_bridge::BassSourceBridge,
    full_network, positive_spectral::SpectralMode, retarded_transport::RetardedControls,
};
#[test]
fn native_callback_preserves_original_photon_and_gas_state() {
    let g = common::load("SIGNED_MINUS", 121);
    let t = g.point_at_x(0.7).unwrap().time_s;
    let (full, c, src) = common::fixture(&g, 0.7);
    let ctl = RetardedControls::new(4, 2, SpectralMode::OriginalCellMean)
        .unwrap()
        .with_threshold_events();
    let a = old::BassOpticalBirthBridge(
        BassSourceBridge::new(src.clone(), g.clone(), 2.7255).unwrap(),
        ctl,
        old::LayerControls::default(),
    );
    let b = new::BassGasReferenceBridge(
        BassSourceBridge::new(src, g, 2.7255).unwrap(),
        ctl,
        new::LayerControls::default(),
    );
    let state = a.initial(full, &c, t).unwrap();
    let dt = 1e8;
    let actual = a.advance(&state, &c, dt).unwrap();
    let mut called = 0;
    let (result, _) = b
        .advance_with_gas(&state, &c, dt, &mut |s, c, h| {
            called += 1;
            full_network::step(s, c, h)
        })
        .unwrap();
    assert_eq!(called, 1);
    assert_eq!(actual.state.full.gas.nuclei, result.state.full.gas.nuclei);
    assert_eq!(
        actual.state.full.gas.thermal_j_m3,
        result.state.full.gas.thermal_j_m3
    );
    assert_eq!(
        actual.state.source_injected_count_com3,
        result.state.source_injected_count_com3
    );
    assert_eq!(
        actual.state.full.escaped_j_m3,
        result.state.full.escaped_j_m3
    );
    assert_eq!(
        actual
            .state
            .cohorts
            .iter()
            .map(|x| x.n_comoving_m3)
            .collect::<Vec<_>>(),
        result
            .state
            .cohorts
            .iter()
            .map(|x| x.n_comoving_m3)
            .collect::<Vec<_>>()
    );
}
#[test]
fn rejected_reference_does_not_mutate_caller_state() {
    let g = common::load("SIGNED_MINUS", 121);
    let t = g.point_at_x(0.7).unwrap().time_s;
    let (full, c, src) = common::fixture(&g, 0.7);
    let ctl = RetardedControls::new(4, 2, SpectralMode::OriginalCellMean)
        .unwrap()
        .with_threshold_events();
    let b = new::BassGasReferenceBridge(
        BassSourceBridge::new(src, g, 2.7255).unwrap(),
        ctl,
        new::LayerControls::default(),
    );
    let state = b.initial(full, &c, t).unwrap();
    let gas = state.full.gas;
    let old_count = state.cohorts.len();
    let result = b.advance_with_gas(&state, &c, 1e8, &mut |_, _, _| {
        Err(full_network::NetworkError::NegativePopulation)
    });
    assert!(result.is_err());
    assert_eq!(gas.nuclei, state.full.gas.nuclei);
    assert_eq!(gas.thermal_j_m3, state.full.gas.thermal_j_m3);
    assert_eq!(old_count, state.cohorts.len());
}
