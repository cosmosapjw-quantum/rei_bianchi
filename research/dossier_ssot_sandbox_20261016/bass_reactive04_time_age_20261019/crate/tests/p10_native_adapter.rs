mod common;
use common::{bit_parity, fixture};
use rei_iso_couple_reference::{
    adaptive_step::{LocalTolerances, events_comoving, photon_projection},
    budget_kernel::Action,
    budget_native::{AdapterError, NativeBudgetControls, attempt},
    full_network::{NetworkConfig, NetworkError},
    midpoint_coupled::{Centering, MidpointBridge},
    positive_spectral::SpectralMode,
    reflection_pool::PoolLimits,
    source_age::AgeHistory,
};
fn setup() -> (MidpointBridge, NetworkConfig, AgeHistory) {
    let (b, ctl, mut c, g) = fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    c.cx_controls.max_attempts = 20000;
    c.cx_controls.max_rate_calls = 2500000;
    let b = MidpointBridge(b, ctl, PoolLimits::default(), Centering::JointCxSplit);
    let s = b.initial(g, &c, 0.).unwrap();
    (b, c, s)
}
fn broad() -> LocalTolerances {
    LocalTolerances {
        rtol: 0.,
        nuclei_m3: [1e10; 13],
        gas_energy_j_m3: 1e10,
        photon_number_com3: 1e10,
        photon_energy_j_com3: 1e10,
        photo_events_com3: [1e10; 4],
        angular_p2_energy: 1e10,
    }
}
#[test]
fn returns_exact_tight_fine_and_only_two_committed_steps() {
    let (b, c, s) = setup();
    let before = format!("{s:?}");
    let h = 2e9;
    let x = attempt(
        &b,
        &s,
        &c,
        h,
        &LocalTolerances {
            rtol: 1.,
            ..Default::default()
        },
        &Default::default(),
    )
    .unwrap();
    assert_eq!(x.action, Action::CommitTightFine);
    assert_eq!(x.pairs_evaluated, 2);
    let v = x.accepted.unwrap();
    let mut cc = c;
    cc.cx_controls.rtol = v.precision.relative;
    cc.cx_controls.atol_normalized = v.precision.absolute;
    let f = b.advance(&s, &cc, h / 2.).unwrap();
    let z = b.advance(&f.state, &cc, h - f.state.time_s).unwrap();
    let mut zz = z.clone();
    zz.state = v.state.clone();
    bit_parity(&z, &zz);
    let e1 = events_comoving(&b, &f, 0.).unwrap();
    let e2 = events_comoving(&b, &z, f.state.time_s).unwrap();
    for j in 0..4 {
        assert_eq!(v.photo_events_com3[j].to_bits(), (e1[j] + e2[j]).to_bits());
    }
    assert_eq!(v.state.chemistry_accepted, s.chemistry_accepted + 2);
    assert_eq!(format!("{s:?}"), before);
    assert!(x.comparisons[0].report.outer_max <= 0.75);
    assert!(x.comparisons[0].report.inner_max <= 0.25);
}
#[test]
fn rare_heii_outer_rejection_is_transactional() {
    let (b, c, s) = setup();
    let before = format!("{s:?}");
    let mut t = broad();
    t.photo_events_com3[2] = 1e-30;
    let x = attempt(&b, &s, &c, 2e10, &t, &Default::default()).unwrap();
    assert_eq!(x.action, Action::RetrySmallerOuterInterval);
    assert!(x.accepted.is_none());
    assert!(x.next_h_s < 2e10);
    assert_eq!(format!("{s:?}"), before);
}
#[test]
fn native_inner_exhaustion_stops_without_shrinking_h() {
    let (b, c, s) = setup();
    let mut t = broad(); // Use named DII, not a hard-coded nucleus index.
    t.nuclei_m3[rei_iso_couple_reference::isotope_state::IsotopeSpecies::DIonized as usize] = 1e-30;
    let mut controls = NativeBudgetControls::default();
    controls.ladder.truncate(2);
    let x = attempt(&b, &s, &c, 1e10, &t, &controls).unwrap();
    assert_eq!(x.action, Action::StopInnerUnresolved);
    assert!(x.accepted.is_none());
    assert_eq!(x.next_h_s, 1e10);
    assert!(x.comparisons.last().unwrap().report.inner_max > controls.beta);
}
#[test]
fn pair_budget_exhaustion_distinct_from_inner_ladder_exhaustion() {
    let (b, c, s) = setup();
    let mut t = broad();
    t.nuclei_m3[rei_iso_couple_reference::isotope_state::IsotopeSpecies::DIonized as usize] = 1e-30;
    let controls = NativeBudgetControls {
        pair_budget: 2,
        ..Default::default()
    };
    let x = attempt(&b, &s, &c, 1e10, &t, &controls).unwrap();
    assert_eq!(x.action, Action::StopWorkLimit);
    assert_eq!(x.pairs_evaluated, 2);
    assert!(x.accepted.is_none());
}
#[test]
fn frozen_scale_matches_loose_pair_and_does_not_grow_with_ladder() {
    let (b, c, s) = setup();
    let t = LocalTolerances {
        rtol: 1e-3,
        ..Default::default()
    };
    let controls = NativeBudgetControls::default();
    let x = attempt(&b, &s, &c, 2e9, &t, &controls).unwrap();
    let mut cc = c;
    cc.cx_controls.rtol = controls.ladder[0].relative;
    cc.cx_controls.atol_normalized = controls.ladder[0].absolute;
    let a = b.advance(&s, &cc, 2e9).unwrap();
    let f = b.advance(&s, &cc, 1e9).unwrap();
    let z = b.advance(&f.state, &cc, 1e9).unwrap();
    let pa = photon_projection(&b, &a.state).unwrap();
    let pz = photon_projection(&b, &z.state).unwrap();
    let ss = x.scales.iter().find(|v| v.key == "photons").unwrap();
    assert_eq!(
        ss.value.to_bits(),
        (t.photon_number_com3 + t.rtol * pa.count.abs().max(pz.count.abs())).to_bits()
    );
}
#[test]
fn source_and_inner_work_errors_are_not_accuracy_retries() {
    let (b, mut c, s) = setup();
    c.photon_source = "WRONG";
    assert!(matches!(
        attempt(&b, &s, &c, 1e9, &Default::default(), &Default::default()),
        Err(AdapterError::Network(NetworkError::SourceMismatch))
    ));
    c.photon_source = rei_iso_couple_reference::axbi_sources::SOURCE_ID;
    c.cx_controls.max_attempts = 1;
    assert!(matches!(
        attempt(&b, &s, &c, 1e10, &Default::default(), &Default::default()),
        Err(AdapterError::Network(NetworkError::Cx(_)))
    ));
}
#[test]
fn invalid_controls_and_time_fail_before_any_commit() {
    let (b, c, s) = setup();
    for h in [0., -1., f64::NAN] {
        assert!(attempt(&b, &s, &c, h, &Default::default(), &Default::default()).is_err());
    }
    let mut v = NativeBudgetControls::default();
    v.ladder[1] = v.ladder[0];
    assert!(attempt(&b, &s, &c, 1., &Default::default(), &v).is_err());
}
#[test]
fn advancing_from_nonzero_time_uses_each_halfstep_volume() {
    let (b, c, s) = setup();
    let s = b.advance(&s, &c, 1e9).unwrap().state;
    let x = attempt(&b, &s, &c, 2e9, &broad(), &Default::default()).unwrap();
    let a = x.accepted.unwrap();
    assert_eq!(a.state.time_s, 3e9);
    assert_eq!(a.state.full.elapsed_s, s.full.elapsed_s + 2e9);
    let p = photon_projection(&b, &a.state).unwrap();
    let n = a.state.source_injected_count_com3;
    assert!((p.count + a.state.photon_absorbed_count_com3 - n).abs() < 1e-12 * n);
}

#[test]
fn real_inner_refinement_reuses_the_previous_pair_on_frozen_scales() {
    let (b, c, s) = setup();
    let mut tol = broad();
    tol.nuclei_m3[rei_iso_couple_reference::isotope_state::IsotopeSpecies::DIonized as usize] =
        1e-7;
    let x = attempt(&b, &s, &c, 1e9, &tol, &Default::default()).unwrap();
    assert_eq!(x.action, Action::CommitTightFine);
    assert_eq!(x.pairs_evaluated, 3);
    assert_eq!(x.comparisons.len(), 2);
    assert_eq!(
        x.comparisons[0].report.decision,
        rei_iso_couple_reference::budget_kernel::Decision::TightenInner
    );
    let a = &x.comparisons[0];
    let z = &x.comparisons[1];
    for (prior, next) in [(&a.four[2], &z.four[0]), (&a.four[3], &z.four[1])] {
        assert_eq!(prior.len(), next.len());
        for (u, v) in prior.iter().zip(next) {
            assert_eq!(u.key, v.key);
            assert_eq!(u.value.to_bits(), v.value.to_bits());
        }
    }
    assert_eq!(
        x.accepted.as_ref().unwrap().precision.relative.to_bits(),
        (1e-12f64).to_bits()
    );
}
