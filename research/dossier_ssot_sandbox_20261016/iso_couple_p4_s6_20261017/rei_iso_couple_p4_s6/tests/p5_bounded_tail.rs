use rei_iso_couple_reference::{
    HHeModel,
    age_remainder::{BudgetedAgeHistory, TailControls},
    axbi_sources::{AxbiSource, SOURCE_ID},
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground},
    deuterium_atomic::DAtomicProvider,
    full_network::{FullState, NetworkConfig},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
    positive_spectral::SpectralMode,
    retarded_transport::RetardedControls,
    retarded_transport_threshold::PositiveThresholdBridge,
    source_age::SourceAgeBridge,
};
fn fixture(
    h: f64,
    shear: f64,
    horizon: f64,
) -> (PositiveThresholdBridge, NetworkConfig, FullState) {
    let source = AxbiSource::new(1900. / (21f64.powi(3) * 1e6), 0.2, 16, 8).unwrap();
    let geo = ConstantAxisymmetricBackground::new(
        0.,
        AxisymmetricPoint::new(1. / 21., 0., h, shear).unwrap(),
        [0., horizon],
    )
    .unwrap();
    let bridge = PositiveThresholdBridge(
        SourceAgeBridge::new(source, geo).unwrap(),
        RetardedControls::new(2, 4, SpectralMode::OriginalCellMean).unwrap(),
    );
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let mut cfg = NetworkConfig::source_bound(
        DAtomicProvider::new(chi, chi + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        SOURCE_ID,
    );
    cfg.use_collisions = false;
    cfg.use_cx = false;
    cfg.use_cmb = false;
    let mut v = [0.; 13];
    v[S::H1Neutral as usize] = 1000.;
    v[S::H1Ionized as usize] = 900.;
    v[S::He4Neutral as usize] = 300.;
    v[S::He4SinglyIonized as usize] = 100.;
    v[S::He4DoublyIonized as usize] = 60.;
    v[S::DNeutral as usize] = 25.;
    v[S::DIonized as usize] = 5.;
    let nuclei = IsotopeNumberState::new(v).unwrap();
    let gas = MixtureState {
        nuclei,
        thermal_j_m3: 1.5
            * KB_J_K
            * nuclei.thermal_particle_density_all_thermal_m3().unwrap()
            * 1e4,
    };
    let state = FullState {
        gas,
        photon_bins: vec![],
        escaped_j_m3: 0.,
        cmb_reservoir_j_m3: 0.,
        elapsed_s: 0.,
    };
    (bridge, cfg, state)
}
fn controls(cut: f64, num: f64, energy: f64, horizon: f64) -> TailControls {
    TailControls {
        max_weight_per_cohort_com3: cut,
        max_cumulative_number_com3: num,
        max_cumulative_energy_j_com3: energy,
        max_direct_species_events_com3: [f64::MAX; 4],
        horizon_s: horizon,
    }
}
fn start(
    bridge: &PositiveThresholdBridge,
    cfg: &NetworkConfig,
    initial: FullState,
    ctrl: TailControls,
) -> BudgetedAgeHistory {
    let h = bridge.initial(initial, cfg, 0.).unwrap();
    bridge.with_tail_budget(h, cfg, ctrl).unwrap()
}
#[test]
fn zero_budget_is_original_native_including_chemistry() {
    let (b, c, f) = fixture(1.2e-16, 0.06 * 1.2e-16, 1.5e14);
    let mut original = b.initial(f.clone(), &c, 0.).unwrap();
    let mut current = start(&b, &c, f, controls(0., 0., 0., 1.5e14));
    for _ in 0..3 {
        let a = b.advance_with_diagnostics(&original, &c, 2e10).unwrap().0;
        let d = b.advance_budgeted(&current, &c, 2e10).unwrap();
        assert_eq!(d.new_removed_nonzero, 0);
        assert_eq!(a.state.cohorts.len(), d.state.history().cohorts.len());
        assert_eq!(
            a.state.photon_absorbed_count_com3,
            d.state.history().photon_absorbed_count_com3
        );
        assert_eq!(
            a.state.full.gas.thermal_j_m3,
            d.state.history().full.gas.thermal_j_m3
        );
        assert!(d.photon_inventory_relative_residual < 1e-11);
        current = d.state;
        original = a.state;
    }
}
#[test]
fn positive_nonzero_truncation_has_explicit_remainder_and_mass_balance() {
    let (b, c, f) = fixture(1.2e-16, 0., 1.5e14);
    let mut current = start(&b, &c, f, controls(1e-12, 1e-10, 1e-26, 1.5e14));
    for _ in 0..4 {
        let step = b.advance_budgeted(&current, &c, 2e10).unwrap();
        assert!(step.photon_inventory_relative_residual < 1e-10);
        assert!(step.state.remainder().cumulative_removed_number_com3 <= 1e-10);
        assert!(
            step.state
                .remainder()
                .cumulative_future_photo_energy_bound_j_com3
                <= 1e-26
        );
        current = step.state;
    }
    assert!(current.remainder().count_removed_nonzero > 0);
    assert!(current.remainder().cumulative_removed_number_com3 > 0.);
    assert!(
        current
            .remainder()
            .direct_species_events_upper_com3
            .iter()
            .all(|x| *x >= 0.)
    );
    assert!(
        current.history().source_injected_count_com3
            > current.remainder().cumulative_removed_number_com3
    );
}
#[test]
fn number_budget_does_not_overflow_or_reclassify_as_absorption() {
    let (b, c, f) = fixture(1.2e-16, 0., 1.5e14);
    let mut current = start(&b, &c, f, controls(1., 1e-17, 1e-20, 1.5e14));
    let mut prev = 0.;
    for _ in 0..4 {
        let r = b.advance_budgeted(&current, &c, 1e13).unwrap();
        assert!(r.state.remainder().cumulative_removed_number_com3 >= prev);
        assert!(r.state.remainder().cumulative_removed_number_com3 <= 1e-17);
        prev = r.state.remainder().cumulative_removed_number_com3;
        current = r.state;
    }
    assert!(current.remainder().count_removed_nonzero > 0);
    assert!(current.history().photon_absorbed_count_com3 > 1e-6);
}
#[test]
fn energy_budget_alone_can_prevent_nonzero_truncation() {
    let (b, c, f) = fixture(1.2e-16, 0., 1.5e14);
    let current = start(&b, &c, f, controls(1., 1., 0., 1.5e14));
    let res = b.advance_budgeted(&current, &c, 2e10).unwrap();
    assert_eq!(res.new_removed_nonzero, 0);
    assert_eq!(
        res.state
            .remainder()
            .cumulative_future_photo_energy_bound_j_com3,
        0.
    );
}
#[test]
fn contracting_direction_energy_envelope_not_assumed_monotone() {
    let (b, c, f) = fixture(1.0e-15, 2.0e-15, 8.0e14);
    let current = start(&b, &c, f, controls(1., 1., 1., 8e14));
    let res = b.advance_budgeted(&current, &c, 1e10).unwrap();
    assert!(res.state.remainder().count_removed_nonzero > 0);
    assert!(
        res.state
            .remainder()
            .cumulative_future_photo_energy_bound_j_com3
            > res
                .state
                .remainder()
                .cumulative_removed_energy_at_cut_j_com3
    );
}
#[test]
fn invalid_controls_and_future_domain_fail_closed() {
    let (b, c, f) = fixture(1.2e-16, 0., 1e11);
    for ctrl in [
        controls(f64::NAN, 1., 1., 1e11),
        controls(1., -1., 1., 1e11),
        controls(1., 1., 1., 1e12),
    ] {
        let initial = b.initial(f.clone(), &c, 0.).unwrap();
        assert!(b.with_tail_budget(initial, &c, ctrl).is_err());
    }
    let current = start(&b, &c, f, controls(1., 1., 1., 1e11));
    assert!(b.advance_budgeted(&current, &c, 2e11).is_err());
}
#[test]
fn strict_zero_cutoff_preserves_positive_tiny_cohorts() {
    let (b, c, f) = fixture(1.2e-16, 0., 1.5e14);
    let current = start(&b, &c, f, controls(0., 1., 1., 1.5e14));
    let a = b.advance_budgeted(&current, &c, 1e13).unwrap();
    assert_eq!(a.new_removed_nonzero, 0);
    assert!(
        a.state
            .history()
            .cohorts
            .iter()
            .all(|x| x.n_comoving_m3 > 0.)
    );
}

#[test]
fn species_event_zero_guard_forbids_energy_capable_removed_cohorts() {
    let (b, c, f) = fixture(1.2e-16, 0., 1.5e14);
    let mut ctrl = controls(1e-12, 1e-10, 1e-26, 1.5e14);
    ctrl.max_direct_species_events_com3[2] = 0.;
    let mut current = start(&b, &c, f, ctrl);
    for _ in 0..3 {
        current = b.advance_budgeted(&current, &c, 2e10).unwrap().state;
    }
    let s = current.remainder();
    assert!(s.count_removed_nonzero > 0);
    assert_eq!(s.direct_species_events_upper_com3[2], 0.);
    assert!(s.cumulative_removed_number_com3 <= 1e-10);
}
#[test]
fn species_event_positive_hard_cap_never_exceeded() {
    let (b, c, f) = fixture(1.2e-16, 0., 1.5e14);
    let mut ctrl = controls(1e-12, 1e-10, 1e-26, 1.5e14);
    ctrl.max_direct_species_events_com3 = [1e-10, 1e-11, 2e-14, 1e-11];
    let mut current = start(&b, &c, f, ctrl);
    for _ in 0..4 {
        current = b.advance_budgeted(&current, &c, 2e10).unwrap().state;
    }
    let r = current.remainder();
    for (upper, cap) in r
        .direct_species_events_upper_com3
        .into_iter()
        .zip(ctrl.max_direct_species_events_com3)
    {
        assert!(upper <= cap);
    }
    assert!(r.count_removed_nonzero > 0);
}
