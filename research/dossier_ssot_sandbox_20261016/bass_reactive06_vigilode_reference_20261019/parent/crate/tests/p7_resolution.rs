mod common;
use common::{bit_parity, fixture};
use rei_iso_couple_reference::{
    axbi_sources::AxbiSource,
    positive_spectral::SpectralMode,
    reflection_pool::{PoolLimits, ReflectionPooledBridge},
    resolution_study::PositiveStudyBridge,
    source_age::SourceAgeBridge,
};
fn nh0() -> f64 {
    1900. / (21_f64.powi(3) * 1e6)
}
#[test]
fn positive_gl32_must_not_inherit_grey_projection_64_bin_cap() {
    let (base, ctr, conf, gas) = fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    let bridge = PositiveStudyBridge::new(nh0(), 0.2, 16, 32, base.geometry, ctr)
        .expect("positive rays are not64 grey bins");
    let a = bridge.initial(gas, &conf, 0.).unwrap();
    let (r, _) = bridge.advance(&a, &conf, 1e8).unwrap();
    assert_eq!(r.state.cohorts.len(), 48 * 32 * 2);
    assert!(r.state.full.photon_bins.is_empty());
    assert!(r.state.cohorts.iter().all(|x| x.n_comoving_m3 >= 0.));
    assert!(r.global_energy_relative_error < 3e-10);
}
#[test]
fn old_grey_guard_stays_rejected_for32_angles() {
    let (base, _, _, _) = fixture(0., false, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    let source = AxbiSource::new(nh0(), 0.2, 16, 32).unwrap();
    assert!(SourceAgeBridge::with_groups(source, base.geometry, [1, 1, 1]).is_err());
}
#[test]
fn gl8_factory_keeps_p6_complete_step_bits() {
    let (base, ctr, conf, gas) = fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    let old = ReflectionPooledBridge(base.clone(), ctr, PoolLimits::default());
    let new = PositiveStudyBridge::new(nh0(), 0.2, 16, 8, base.geometry, ctr).unwrap();
    let a = old.initial(gas, &conf, 0.).unwrap();
    let b = old.advance(&a, &conf, 2e9).unwrap();
    let (c, _) = new.advance(&a, &conf, 2e9).unwrap();
    bit_parity(&b, &c);
}
#[test]
fn all_owner_angular_resolutions_keep_positive_normalized_source() {
    let (base, ctr, _, _) = fixture(0., false, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    for angle in [8, 16, 32] {
        let b = PositiveStudyBridge::new(nh0(), 0.2, 16, angle, base.geometry, ctr).unwrap();
        let sum: f64 = b
            .source()
            .angular_cells
            .iter()
            .map(|x| x.count_fraction)
            .sum();
        assert!((sum - 1.).abs() < 3e-14);
        assert!(
            b.source()
                .angular_cells
                .iter()
                .all(|x| x.count_fraction > 0.)
        );
        assert!(b.source().normalization_relative_residual < 1e-7);
    }
}
#[test]
fn rejected_inputs_do_not_silently_select_another_resolution() {
    let (base, ctr, _, _) = fixture(0., false, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    for (n, e) in [(12, 16), (8, 0), (64, 16)] {
        assert!(PositiveStudyBridge::new(nh0(), 0.2, e, n, base.geometry, ctr).is_err());
    }
    let mut bad = ctr;
    bad.opacity_substeps = 3;
    assert!(PositiveStudyBridge::new(nh0(), 0.2, 16, 8, base.geometry, bad).is_err());
}
#[test]
fn frozen_spectral_number_energy_and_thermal_binding_ledgers() {
    let (base, ctr, conf, gas) = fixture(0., false, 0.2, SpectralMode::SplitPositiveGauss3, 2, 4);
    for e in [16, 32, 64] {
        let b = PositiveStudyBridge::new(nh0(), 0.2, e, 8, base.geometry, ctr).unwrap();
        let r = b.frozen_spectrum(&gas.gas, &conf, 8e10).unwrap();
        assert!(
            (r.surviving_fraction + r.events_per_injected_photon.iter().sum::<f64>() - 1.).abs()
                < 2e-13
        );
        assert!(
            (r.surviving_energy_ev + r.absorbed_energy_ev - r.injected_mean_energy_ev).abs()
                < 3e-12
        );
        assert!((r.heat_ev + r.binding_ev - r.absorbed_energy_ev).abs() < 3e-12);
        assert!(r.events_per_injected_photon.iter().all(|x| *x > 0.));
    }
}
#[test]
fn observer_flrw_quadrupole_and_birth_age_limits() {
    use rei_iso_couple_reference::resolution_study::observer_moments;
    let (base, ctr, conf, gas) = fixture(0., true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    let b = PositiveStudyBridge::new(nh0(), 0.2, 16, 32, base.geometry, ctr).unwrap();
    let a = b.initial(gas, &conf, 0.).unwrap();
    let (r, _) = b.advance(&a, &conf, 1e8).unwrap();
    let m = observer_moments(&r.state, b.geometry()).unwrap();
    assert!((m.energy_p2_j_com3 / m.energy_j_com3).abs() < 3e-14);
    assert!(m.mean_age_s >= 0. && m.mean_age_s <= 1e8);
    let sum: f64 = r.state.cohorts.iter().map(|c| c.n_comoving_m3).sum();
    assert_eq!(sum.to_bits(), m.photons_com3.to_bits());
}
