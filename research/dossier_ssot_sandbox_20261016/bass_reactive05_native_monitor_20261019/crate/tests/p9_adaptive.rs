use rei_iso_couple_reference::adaptive_step::scaled_defect;
#[test]
fn rare_channel_cannot_hide_behind_total_photon_scale() {
    let r = scaled_defect(1e-16, 2e-16, 1e-22, 1e-3).unwrap();
    assert!(r > 100., "rare channel must reject, got {r}");
}
#[test]
fn invalid_scales_fail_closed() {
    for a in [0., -1., f64::NAN, f64::INFINITY] {
        assert!(scaled_defect(1., 2., a, 1e-3).is_err());
    }
}
mod common;
use common::{bit_parity, fixture};
use rei_iso_couple_reference::{
    adaptive_step::{
        LocalTolerances, Trial, attempt, events_comoving, next_step, photon_projection,
    },
    full_network::NetworkError,
    midpoint_coupled::{Centering, MidpointBridge},
    positive_spectral::SpectralMode,
    reflection_pool::PoolLimits,
};
fn setup() -> (
    MidpointBridge,
    rei_iso_couple_reference::full_network::NetworkConfig,
    rei_iso_couple_reference::source_age::AgeHistory,
) {
    let (b, ctl, mut c, g) = fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    c.cx_controls.rtol = 1e-12;
    c.cx_controls.atol_normalized = 1e-15;
    let b = MidpointBridge(b, ctl, PoolLimits::default(), Centering::JointCxSplit);
    let s = b.initial(g, &c, 0.).unwrap();
    (b, c, s)
}
#[test]
fn accepted_solution_is_fine_not_richardson_and_input_unchanged() {
    let (b, c, s) = setup();
    let old = format!("{s:?}");
    let h = 2e9;
    let t = LocalTolerances {
        rtol: 1.,
        ..LocalTolerances::default()
    };
    let out = match attempt(&b, &s, &c, h, &t).unwrap() {
        Trial::Accepted(x) => x,
        _ => panic!("expected acceptance"),
    };
    let a = b.advance(&s, &c, h / 2.).unwrap();
    let z = b.advance(&a.state, &c, h / 2.).unwrap();
    let mut reconstructed = z.clone();
    reconstructed.state = out.state.clone();
    bit_parity(&z, &reconstructed);
    let e1 = events_comoving(&b, &a, 0.).unwrap();
    let e2 = events_comoving(&b, &z, h / 2.).unwrap();
    for j in 0..4 {
        assert_eq!(
            out.photo_events_com3[j].to_bits(),
            (e1[j] + e2[j]).to_bits()
        );
    }
    assert_eq!(old, format!("{s:?}"));
    assert_eq!(out.state.chemistry_accepted, s.chemistry_accepted + 2);
    let co = b.advance(&s, &c, h).unwrap();
    assert_eq!(out.state.cohorts.len(), 2 * co.state.cohorts.len());
    assert!(out.report.maximum <= 1.);
}
#[test]
fn rare_event_guard_rejects_and_does_not_commit() {
    let (b, c, s) = setup();
    let before = format!("{s:?}");
    let t = LocalTolerances {
        rtol: 0.,
        nuclei_m3: [1e10; 13],
        gas_energy_j_m3: 1e10,
        photon_number_com3: 1e10,
        photon_energy_j_com3: 1e10,
        angular_p2_energy: 1e10,
        photo_events_com3: [1e10, 1e10, 1e-40, 1e10],
    };
    match attempt(&b, &s, &c, 2e10, &t).unwrap() {
        Trial::Rejected {
            report: Some(r),
            next_h_s,
            ..
        } => {
            assert_eq!(r.worst, "photo_event_2");
            assert!(r.maximum > 1.);
            assert!(next_h_s < 2e10);
        }
        _ => panic!("HeII guard must reject"),
    }
    assert_eq!(before, format!("{s:?}"));
}
#[test]
fn nonfinite_controls_and_no_progress_fail() {
    let (b, c, s) = setup();
    let t = LocalTolerances::default();
    for h in [-1., 0., f64::NAN, f64::INFINITY] {
        assert!(attempt(&b, &s, &c, h, &t).is_err());
    }
    let mut late = s.clone();
    late.time_s = 1e10;
    assert!(matches!(
        attempt(&b, &late, &c, 1e-20, &t),
        Err(NetworkError::NoForwardProgress)
    ));
    let t = LocalTolerances {
        rtol: f64::NAN,
        ..t
    };
    assert!(attempt(&b, &s, &c, 1., &t).is_err());
}
#[test]
fn provenance_and_inner_work_errors_are_not_retried_as_accuracy_failures() {
    let (b, mut c, s) = setup();
    c.photon_source = "wrong";
    assert!(matches!(
        attempt(&b, &s, &c, 1e9, &LocalTolerances::default()),
        Err(NetworkError::SourceMismatch)
    ));
    c.photon_source = rei_iso_couple_reference::axbi_sources::SOURCE_ID;
    c.cx_controls.max_attempts = 1;
    assert!(matches!(
        attempt(&b, &s, &c, 1e10, &LocalTolerances::default()),
        Err(NetworkError::Cx(_))
    ));
}
#[test]
fn rejected_trial_followed_by_acceptance_counts_births_only_once() {
    let (b, c, s) = setup();
    let h = 1e10;
    let mut tiny = LocalTolerances {
        rtol: 0.,
        ..LocalTolerances::default()
    };
    tiny.photo_events_com3 = [1e-45; 4];
    assert!(matches!(
        attempt(&b, &s, &c, h, &tiny).unwrap(),
        Trial::Rejected { .. }
    ));
    let loose = LocalTolerances {
        rtol: 1.,
        ..LocalTolerances::default()
    };
    let out = match attempt(&b, &s, &c, h / 4., &loose).unwrap() {
        Trial::Accepted(x) => x,
        _ => panic!("loose step failed"),
    };
    let p = photon_projection(&b, &out.state).unwrap();
    let n = out.state.source_injected_count_com3;
    assert!((p.count + out.state.photon_absorbed_count_com3 - n).abs() < 3e-12 * n);
    assert_eq!(out.state.time_s, h / 4.);
    assert_eq!(s.source_injected_count_com3, 0.);
}
#[test]
fn stepsize_feedback_is_bounded() {
    assert_eq!(next_step(8., 0., true), 16.);
    assert_eq!(next_step(8., 0., false), 4.);
    assert!(next_step(8., 1e30, false) >= 1.6);
    assert!(scaled_defect(f64::INFINITY, 1., 1., 1e-3).is_err());
}
