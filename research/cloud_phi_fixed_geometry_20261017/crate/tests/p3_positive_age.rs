use rei_iso_couple_reference::{
    HHeModel,
    axbi_sources::{AxbiSource, SOURCE_ID},
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground, GeometryBackground},
    deuterium_atomic::DAtomicProvider,
    full_network::{FullState, NetworkConfig},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
    positive_age::PositiveAgeBridge,
    source_age::SourceAgeBridge,
};
fn data() -> (PositiveAgeBridge, NetworkConfig, FullState) {
    let h = 1.2e-16;
    let s = h * 0.06;
    let a = 1.0 / 21.0;
    let bg = ConstantAxisymmetricBackground::new(
        0.0,
        AxisymmetricPoint::new(a, 0.0, h, s).unwrap(),
        [0., 1.5e14],
    )
    .unwrap();
    let src = AxbiSource::new(1900.0 / (21.0f64.powi(3) * 1e6), 0.2, 16, 8).unwrap();
    let positive = PositiveAgeBridge(SourceAgeBridge::new(src, bg).unwrap());
    let c = HHeModel::controlled_fixture().threshold_ev[0];
    let conf = NetworkConfig::source_bound(
        DAtomicProvider::new(c, c + 0.0037, "MANUFACTURED_D_H").unwrap(),
        SOURCE_ID,
    );
    let mut n = [0.0; 13];
    n[S::H1Neutral as usize] = 1000.;
    n[S::H1Ionized as usize] = 900.;
    n[S::He4Neutral as usize] = 300.;
    n[S::He4SinglyIonized as usize] = 100.;
    n[S::He4DoublyIonized as usize] = 60.;
    n[S::DNeutral as usize] = 25.;
    n[S::DIonized as usize] = 5.;
    let ni = IsotopeNumberState::new(n).unwrap();
    let nth = ni.thermal_particle_density_all_thermal_m3().unwrap();
    let gas = MixtureState {
        nuclei: ni,
        thermal_j_m3: 1.5 * KB_J_K * nth * 10000.,
    };
    (
        positive,
        conf,
        FullState {
            gas,
            photon_bins: vec![],
            escaped_j_m3: 0.,
            cmb_reservoir_j_m3: 0.,
            elapsed_s: 0.,
        },
    )
}
fn rel(a: f64, b: f64) -> f64 {
    (a - b).abs() / a.abs().max(b.abs()).max(1e-50)
}
#[test]
fn positive_source_age_first_event_structural_close() {
    let (b, conf, initial) = data();
    let state = b.initial(initial, &conf, 0.).unwrap();
    let after = b.advance(&state, &conf, 1e10).unwrap();
    assert!(after.global_energy_relative_error < 3e-10);
    assert_eq!(after.state.cohorts.len(), 384);
    assert!(after.chemistry_budget.photo_events_m3.iter().sum::<f64>() > 0.);
    let n = after
        .state
        .cohorts
        .iter()
        .map(|v| v.n_comoving_m3)
        .sum::<f64>();
    assert!(
        rel(
            after.state.source_injected_count_com3,
            n + after.state.photon_absorbed_count_com3
        ) < 4e-11
    );
}
#[test]
fn positive_cohort_events_equal_unprojected_opacity_benchmark() {
    let (b, conf, initial) = data();
    let state = b.initial(initial, &conf, 0.).unwrap();
    let tau = 1e10;
    let gm = b.0.geometry.snapshot(0.5 * tau).unwrap();
    let co = b.0.source_births(0.5 * tau, tau).unwrap();
    let g0 = b.0.geometry.snapshot(0.).unwrap();
    let rat = g0.volume_factor().unwrap() / gm.volume_factor().unwrap();
    let mut density = [0.; 13];
    for sp in S::ALL {
        density[sp as usize] = state.full.gas.nuclei.density_m3(sp) * rat;
    }
    let gm_gas = MixtureState {
        nuclei: IsotopeNumberState::new(density).unwrap(),
        thermal_j_m3: state.full.gas.thermal_j_m3 * rat.powf(5. / 3.),
    };
    let x =
        b.0.grey_absorption_error(&co, &gm, &gm_gas, &conf, tau)
            .unwrap();
    let actual = b.advance(&state, &conf, tau).unwrap();
    let event_sum = actual.chemistry_budget.photo_events_m3.iter().sum::<f64>();
    let expected = x.cohort_photo_events_m3.iter().sum::<f64>();
    assert!(
        rel(event_sum, expected) < 8e-13,
        "actual {event_sum} ref {expected}"
    );
    for j in 0..4 {
        assert!(
            rel(
                actual.chemistry_budget.photo_events_m3[j],
                x.cohort_photo_events_m3[j]
            ) < 8e-13
        );
    }
    assert!(x.total_relative_error > 3e-3); // P2 grey is *not* exact.
}
#[test]
fn source_age_positive_two_ages_savin_cx_once() {
    let (b, conf, initial) = data();
    let state = b.initial(initial, &conf, 0.).unwrap();
    let a = b.advance(&state, &conf, 3e10).unwrap();
    let r = b.advance(&a.state, &conf, 3e10).unwrap();
    assert_eq!(r.state.cohorts.len(), 768);
    assert!(r.chemistry_budget.cx_signed_m3.is_finite());
    assert!(r.global_energy_relative_error < 3e-10);
    let n = r.state.cohorts.iter().map(|v| v.n_comoving_m3).sum::<f64>();
    assert!(
        rel(
            r.state.source_injected_count_com3,
            n + r.state.photon_absorbed_count_com3
        ) < 1e-10
    );
}
#[test]
fn rejected_step_preserves_original_state() {
    let (b, conf, initial) = data();
    let state = b.initial(initial, &conf, 0.).unwrap();
    let before = state.full.gas.nuclei.density_m3(S::H1Neutral);
    assert!(b.advance(&state, &conf, -1.0).is_err());
    assert!(b.advance(&state, &conf, 1.0e15).is_err());
    assert_eq!(before, state.full.gas.nuclei.density_m3(S::H1Neutral));
    assert_eq!(state.cohorts.len(), 0);
}
