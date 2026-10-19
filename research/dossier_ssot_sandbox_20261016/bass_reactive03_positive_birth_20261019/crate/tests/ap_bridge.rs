//! Bounded integration verification for the additive fitted-birth target.
mod bass_common;
use bass_common::common::bit_parity;
use rei_iso_couple_reference::{
    ap_midpoint::{ApMidpointBridge, BirthMode},
    bass_reactive::GeometryChoice,
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground},
    bound_adaptive::photon_projection,
    full_network::NetworkError,
    mixture_coupling::CoupleError,
};

fn fixture(
    case: &str,
    mode: BirthMode,
) -> (
    ApMidpointBridge,
    rei_iso_couple_reference::full_network::NetworkConfig,
    rei_iso_couple_reference::full_network::FullState,
) {
    let (b, c, g) = bass_common::fixture(case, 121, 0.0, false, 8192);
    (ApMidpointBridge::from_original(b, mode), c, g)
}

#[test]
fn off_dispatch_preserves_every_legacy_state_bit() {
    for case in ["SIGNED_MINUS", "SIGNED_PLUS"] {
        let (b, c, g) = fixture(case, BirthMode::Off);
        let old = b.original();
        let mut a = b.initial(g, &c, 0.0).unwrap();
        for _ in 0..2 {
            let x = old.advance(&a, &c, 1e9).unwrap();
            let y = b.advance(&a, &c, 1e9).unwrap();
            bit_parity(&x, &y);
            a = y.state;
        }
    }
}

#[test]
fn every_birth_retains_native_labels_geometry_and_killing_ray() {
    for case in ["SIGNED_MINUS", "SIGNED_PLUS"] {
        let (b, c, g) = fixture(case, BirthMode::Fitted { refinement: 2 });
        let t0 = 2e12;
        let dt = 2e11;
        let born = b.emit_births(t0, dt, &c, &g.gas).unwrap();
        assert!(born.len() > 768);
        let end_geometry = b.0.geometry.snapshot(t0 + dt).unwrap();
        for co in born {
            assert!(co.n_comoving_m3 > 0.0);
            assert!(co.birth_time_s > t0 && co.birth_time_s < t0 + dt);
            let original = b.0.geometry.snapshot(co.birth_time_s).unwrap();
            assert_eq!(
                co.birth_geometry.scale_factors.map(f64::to_bits),
                original.scale_factors.map(f64::to_bits)
            );
            assert_eq!(
                co.birth_geometry.hubble_per_s.map(f64::to_bits),
                original.hubble_per_s.map(f64::to_bits)
            );
            let source = b.0.source.spectral_cells[co.spectral_index];
            let angle = b.0.source.angular_cells[co.angular_index];
            assert_eq!(co.energy_at_birth_ev.to_bits(), source.energy_ev.to_bits());
            assert_eq!(co.direction_at_birth[2].to_bits(), angle.mu.to_bits());
            let squared: f64 = (0..3)
                .map(|i| {
                    (co.energy_at_birth_ev * co.direction_at_birth[i] * original.scale_factors[i]
                        / end_geometry.scale_factors[i])
                        .powi(2)
                })
                .sum();
            let propagated = co.ray_at(&end_geometry).unwrap();
            assert!((propagated.energy_ev / squared.sqrt() - 1.0).abs() < 6e-15);
        }
    }
}

#[test]
fn frozen_native_source_count_and_survival_match_analytic_integral() {
    let (mut b, c, g) = fixture("SIGNED_MINUS", BirthMode::Fitted { refinement: 1 });
    let a =
        b.0.geometry
            .snapshot(0.0)
            .unwrap()
            .volume_factor()
            .unwrap()
            .cbrt();
    b.0.geometry = GeometryChoice::constant(
        ConstantAxisymmetricBackground::new(
            0.0,
            AxisymmetricPoint::new(a, 0.0, 0.0, 0.0).unwrap(),
            [0.0, 8e12],
        )
        .unwrap(),
    );
    let dt = 8e12;
    let native = b.0.source_births(0.0, dt).unwrap();
    let exact_total: f64 = native.iter().map(|co| co.n_comoving_m3).sum();
    let exact_surviving: f64 = native
        .iter()
        .map(|co| {
            let k: f64 = b
                .opacity_channels(co.energy_at_birth_ev, &g.gas, &c)
                .unwrap()
                .iter()
                .sum();
            co.n_comoving_m3 * rei_iso_couple_reference::fitted_birth::phi(k * dt).unwrap()
        })
        .sum();
    let born = b.emit_births(0.0, dt, &c, &g.gas).unwrap();
    let emitted: f64 = born.iter().map(|co| co.n_comoving_m3).sum();
    let survivors: f64 = born
        .iter()
        .map(|co| {
            let k: f64 = b
                .opacity_channels(co.energy_at_birth_ev, &g.gas, &c)
                .unwrap()
                .iter()
                .sum();
            co.n_comoving_m3 * (-k * (dt - co.birth_time_s)).exp()
        })
        .sum();
    assert!((emitted / exact_total - 1.0).abs() < 3e-14);
    assert!((survivors / exact_surviving - 1.0).abs() < 3e-12);
}

#[test]
fn native_positive_and_negative_bass_reactions_keep_ledgers() {
    for case in ["SIGNED_MINUS", "SIGNED_PLUS"] {
        let (b, c, g) = fixture(case, BirthMode::Fitted { refinement: 1 });
        let original = b.original();
        let mut a = b.initial(g, &c, 0.0).unwrap();
        for _ in 0..2 {
            let out = b.advance(&a, &c, 1e10).unwrap();
            assert!(
                out.chemistry_budget
                    .photo_events_m3
                    .iter()
                    .all(|x| *x > 0.0)
            );
            assert!(out.chemistry_budget.rr_events_m3.iter().sum::<f64>() > 0.0);
            assert!(out.chemistry_budget.cx_signed_m3.abs() > 0.0);
            assert!(out.chemistry_budget.freefree_integrated_j_m3 > 0.0);
            assert!(out.chemistry_budget.cmb_change_j_m3.abs() > 0.0);
            assert!(out.state.cohorts.iter().all(|co| co.n_comoving_m3 >= 0.0));
            assert!(out.global_energy_relative_error < 3e-12);
            let photons = photon_projection(&original, &out.state).unwrap().count;
            let relative = (photons + out.state.photon_absorbed_count_com3)
                / out.state.source_injected_count_com3
                - 1.0;
            assert!(relative.abs() < 3e-12);
            a = out.state;
        }
    }
}

#[test]
fn fitted_birth_rejects_bad_source_and_resolution() {
    for bad in [f64::NAN, -1.0, 0.0] {
        let (mut b, c, g) = fixture("SIGNED_MINUS", BirthMode::Fitted { refinement: 1 });
        b.0.source.spectral_cells[0].photon_fraction = bad;
        assert_eq!(
            b.emit_births(0.0, 1e9, &c, &g.gas).unwrap_err(),
            NetworkError::InvalidInput
        );
    }
    let (b, c, g) = fixture("SIGNED_MINUS", BirthMode::Fitted { refinement: 0 });
    assert_eq!(
        b.emit_births(0.0, 1e9, &c, &g.gas).unwrap_err(),
        NetworkError::InvalidInput
    );
    let (b, mut c, g) = fixture("SIGNED_MINUS", BirthMode::Fitted { refinement: 1 });
    c.photon_source = "not-the-native-source";
    assert_eq!(
        b.emit_births(0.0, 1e9, &c, &g.gas).unwrap_err(),
        NetworkError::InvalidInput
    );
}

#[test]
fn negative_cohort_rejection_does_not_change_the_input() {
    let (b, c, g) = fixture("SIGNED_MINUS", BirthMode::Fitted { refinement: 1 });
    let mut state = b.initial(g, &c, 0.0).unwrap();
    let mut cohort = b.0.source_births(0.0, 1.0).unwrap().remove(0);
    cohort.n_comoving_m3 = -1.0;
    state.cohorts.push(cohort);
    let saved = format!("{state:?}");
    assert_eq!(
        b.advance(&state, &c, 1e9).unwrap_err(),
        NetworkError::NegativePopulation
    );
    assert_eq!(format!("{state:?}"), saved);
}

#[test]
fn cx_work_limit_is_reported_as_work_limit() {
    let (b, mut c, g) = fixture("SIGNED_MINUS", BirthMode::Fitted { refinement: 1 });
    c.cx_controls.max_rate_calls = 1;
    let state = b.initial(g, &c, 0.0).unwrap();
    let saved = format!("{state:?}");
    assert_eq!(
        b.advance(&state, &c, 1e10).unwrap_err(),
        NetworkError::Cx(CoupleError::WorkLimit)
    );
    assert_eq!(format!("{state:?}"), saved);
}

#[test]
fn four_corner_off_keeps_raw_corners_scales_and_accepted_state() {
    use rei_iso_couple_reference::{ap_budget, bound_adaptive, bound_budget};
    let (b, c, g) = fixture("SIGNED_MINUS", BirthMode::Off);
    let state = b.initial(g, &c, 0.0).unwrap();
    let tolerances = bound_adaptive::LocalTolerances::default();
    let controls = bound_budget::NativeBudgetControls::default();
    let original =
        bound_budget::attempt(&b.original(), &state, &c, 1e9, &tolerances, &controls).unwrap();
    let fitted = ap_budget::attempt(&b, &state, &c, 1e9, &tolerances, &controls).unwrap();
    assert_eq!(original.action, fitted.action);
    assert_eq!(original.pairs_evaluated, fitted.pairs_evaluated);
    assert_eq!(
        format!("{:?}", original.scales),
        format!("{:?}", fitted.scales)
    );
    assert_eq!(
        format!("{:?}", original.comparisons),
        format!("{:?}", fitted.comparisons)
    );
    assert_eq!(
        format!("{:?}", original.accepted),
        format!("{:?}", fitted.accepted)
    );
}

#[test]
fn fitted_four_corner_attempt_uses_same_policy_and_retains_input() {
    use rei_iso_couple_reference::{
        ap_budget, bound_adaptive, bound_budget, budget_kernel::Action,
    };
    let (b, c, g) = fixture("SIGNED_MINUS", BirthMode::Fitted { refinement: 1 });
    let state = b.initial(g, &c, 0.0).unwrap();
    let saved = format!("{state:?}");
    let controls = bound_budget::NativeBudgetControls::default();
    let result = ap_budget::attempt(
        &b,
        &state,
        &c,
        1e9,
        &bound_adaptive::LocalTolerances::default(),
        &controls,
    )
    .unwrap();
    assert_eq!(result.action, Action::CommitTightFine);
    assert!(result.pairs_evaluated <= controls.pair_budget);
    assert!(!result.comparisons.is_empty());
    for comparison in &result.comparisons {
        assert!(
            comparison
                .four
                .iter()
                .all(|v| v.len() == result.scales.len())
        );
        assert!(
            comparison
                .four
                .iter()
                .flatten()
                .all(|x| x.value.is_finite())
        );
    }
    let accepted = result.accepted.unwrap();
    assert_eq!(accepted.state.time_s.to_bits(), 1e9f64.to_bits());
    assert!(accepted.max_energy_ledger < 3e-12);
    assert_eq!(format!("{state:?}"), saved);
}

#[test]
fn zero_opacity_reduces_to_positive_transparent_births() {
    use rei_iso_couple_reference::isotope_state::{IsotopeNumberState, IsotopeSpecies as S};
    let (mut b, c, mut g) = fixture("SIGNED_MINUS", BirthMode::Fitted { refinement: 4 });
    let a =
        b.0.geometry
            .snapshot(0.0)
            .unwrap()
            .volume_factor()
            .unwrap()
            .cbrt();
    b.0.geometry = GeometryChoice::constant(
        ConstantAxisymmetricBackground::new(
            0.0,
            AxisymmetricPoint::new(a, 0.0, 0.0, 0.0).unwrap(),
            [0.0, 8e12],
        )
        .unwrap(),
    );
    let mut populations = [0.0; 13];
    populations[S::H1Ionized as usize] = 1900.0;
    populations[S::He4DoublyIonized as usize] = 460.0;
    populations[S::DIonized as usize] = 30.0;
    g.gas.nuclei = IsotopeNumberState::new(populations).unwrap();
    let dt = 8e12;
    let native = b.0.source_births(0.0, dt).unwrap();
    let expected: f64 = native.iter().map(|co| co.n_comoving_m3).sum();
    let born = b.emit_births(0.0, dt, &c, &g.gas).unwrap();
    let count: f64 = born.iter().map(|co| co.n_comoving_m3).sum();
    let mean_age: f64 = born
        .iter()
        .map(|co| co.n_comoving_m3 * (1.0 - co.birth_time_s / dt))
        .sum::<f64>()
        / count;
    assert_eq!(born.len(), 8 * native.len());
    assert!((count / expected - 1.0).abs() < 3e-14);
    assert!((mean_age - 0.5).abs() < 3e-14);
    for co in born {
        assert_eq!(
            b.opacity_channels(co.energy_at_birth_ev, &g.gas, &c)
                .unwrap(),
            [0.0; 4]
        );
        assert!(co.n_comoving_m3 > 0.0);
    }
}

#[test]
fn unrepresentable_birth_time_is_a_resolution_error() {
    let (b, c, g) = fixture("SIGNED_MINUS", BirthMode::Fitted { refinement: 1 });
    assert_eq!(
        b.emit_births(2e12, 1e-9, &c, &g.gas).unwrap_err(),
        NetworkError::NoForwardProgress
    );
}
