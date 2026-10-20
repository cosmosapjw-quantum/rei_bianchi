use parent::deuterium_atomic::DAtomicProvider;
use parent::deuterium_thermal_coupling::CxOwnership;
use parent::full_network::{EventBudget, FullState, NetworkConfig, NetworkError, NetworkResult};
use parent::igm_rates::igm_rates;
use parent::isotope_state::{IsotopeNumberState, IsotopeSpecies as S};
use parent::midpoint_gas::{self, GasRhs};
use parent::mixture_coupling::CoupleError;
use parent::mixture_eos::{KB_J_K, MixtureState};
use parent::{ForwardError, HHeModel};
use rei_brperf01_native_rates::{
    rhs_with_evaluator, rhs_with_rates, step_strang_with_evaluator, step_with_evaluator,
};

fn fixture(t: f64, scale: f64, spectators: bool) -> (FullState, NetworkConfig) {
    let mut n = [0.0; 13];
    for (sp, value) in [
        (S::H1Neutral, 1000.0),
        (S::H1Ionized, 900.0),
        (S::DNeutral, 25.0),
        (S::DIonized, 5.0),
        (S::He4Neutral, 300.0),
        (S::He4SinglyIonized, 100.0),
        (S::He4DoublyIonized, 60.0),
    ] {
        n[sp as usize] = scale * value;
    }
    if spectators {
        for sp in [
            S::Neutron,
            S::TNeutral,
            S::TIonized,
            S::He3Neutral,
            S::He3SinglyIonized,
            S::He3DoublyIonized,
        ] {
            n[sp as usize] = scale * (sp as usize + 1) as f64;
        }
    }
    let nuclei = IsotopeNumberState::new(n).unwrap();
    let s = FullState {
        gas: MixtureState {
            nuclei,
            thermal_j_m3: 1.5
                * KB_J_K
                * nuclei.thermal_particle_density_all_thermal_m3().unwrap()
                * t,
        },
        photon_bins: Vec::new(),
        escaped_j_m3: 0.0,
        cmb_reservoir_j_m3: 0.0,
        elapsed_s: 0.0,
    };
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let mut c = NetworkConfig::source_bound(
        DAtomicProvider::new(chi, chi + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        "BRPERF01_CONTROLLED_GAS_PARITY",
    );
    c.use_photo = false;
    c.owner = CxOwnership::AtomicRhs;
    (s, c)
}

fn budget_bits(b: EventBudget) -> Vec<u64> {
    b.photo_events_m3
        .into_iter()
        .chain(b.ci_events_m3)
        .chain(b.rr_events_m3)
        .chain([
            b.dr_hei_m3,
            b.cx_signed_m3,
            b.photo_energy_j_m3,
            b.thermal_change_j_m3,
            b.chemical_change_j_m3,
            b.escape_change_j_m3,
            b.cmb_change_j_m3,
            b.freefree_integrated_j_m3,
            b.d_electron_integrated_m3,
        ])
        .map(f64::to_bits)
        .collect()
}

fn rhs_bits(r: &GasRhs) -> Vec<u64> {
    r.nuclei_per_s
        .into_iter()
        .map(f64::to_bits)
        .chain(budget_bits(r.budget_per_s))
        .collect()
}

fn state_bits(s: &FullState) -> Vec<u64> {
    let mut bits: Vec<u64> = S::ALL
        .into_iter()
        .map(|sp| s.gas.nuclei.density_m3(sp).to_bits())
        .chain(
            [
                s.gas.thermal_j_m3,
                s.escaped_j_m3,
                s.cmb_reservoir_j_m3,
                s.elapsed_s,
            ]
            .map(f64::to_bits),
        )
        .collect();
    bits.push(s.photon_bins.len() as u64);
    for b in &s.photon_bins {
        bits.extend([b.energy_ev.to_bits(), b.number_m3.to_bits()]);
    }
    bits
}

fn result_bits(r: &NetworkResult) -> Vec<u64> {
    state_bits(&r.state)
        .into_iter()
        .chain(budget_bits(r.budget))
        .chain([r.attempts as u64, r.accepted as u64, r.rejected as u64])
        .collect()
}

fn assert_same_rhs(a: Result<GasRhs, NetworkError>, b: Result<GasRhs, NetworkError>) {
    match (a, b) {
        (Ok(a), Ok(b)) => assert_eq!(rhs_bits(&a), rhs_bits(&b)),
        (Err(a), Err(b)) => assert_eq!(a, b),
        (a, b) => panic!("RHS acceptance differs: {a:?} versus {b:?}"),
    }
}

fn assert_same_result(
    a: Result<NetworkResult, NetworkError>,
    b: Result<NetworkResult, NetworkError>,
) {
    match (a, b) {
        (Ok(a), Ok(b)) => assert_eq!(result_bits(&a), result_bits(&b)),
        (Err(a), Err(b)) => assert_eq!(a, b),
        (a, b) => panic!("Step acceptance differs: {a:?} versus {b:?}"),
    }
}

#[test]
fn direct_rhs_bitwise_parity_including_piecewise_boundaries_and_spectators() {
    let temperatures = [
        2.8,
        20.0,
        100.0,
        190.0,
        1713.0,
        3000.0,
        5500.0_f64.next_down(),
        5500.0,
        5500.0_f64.next_up(),
        6856.0,
        9284.0_f64.next_down(),
        9284.0,
        9284.0_f64.next_up(),
        10000.0,
        60000.0,
        199999.0,
    ];
    for t in temperatures {
        for scale in [1e-120, 1e-6, 1.0, 1e8] {
            for spectators in [false, true] {
                let (s, mut c) = fixture(t, scale, spectators);
                let actual_t = s.gas.eos().unwrap().temperature_k;
                let r = igm_rates(actual_t).unwrap();
                for mask in 0..8 {
                    c.use_collisions = mask & 1 != 0;
                    c.use_cx = mask & 2 != 0;
                    c.use_cmb = mask & 4 != 0;
                    assert_same_rhs(
                        midpoint_gas::rhs(&s, &c),
                        rhs_with_rates(&s, &c, actual_t, &r),
                    );
                }
            }
        }
    }
}

#[test]
fn direct_midpoint_step_bitwise_parity_and_transactional_failures() {
    for t in [100.0, 3000.0, 5500.0, 9284.0, 10000.0, 60000.0] {
        let (s, mut c) = fixture(t, 1.0, true);
        for use_cx in [false, true] {
            c.use_cx = use_cx;
            for h in [0.0, 1.0, 1e4, 1e7, 1e20] {
                let before = state_bits(&s);
                assert_same_result(
                    midpoint_gas::step(&s, &c, h),
                    step_with_evaluator(&s, &c, h, &mut igm_rates),
                );
                assert_eq!(before, state_bits(&s));
            }
        }
    }
}

#[test]
fn direct_strang_half_flows_and_accumulated_history_are_bitwise_identical() {
    for t in [100.0, 3000.0, 10000.0, 60000.0] {
        let (mut original, mut c) = fixture(t, 1.0, true);
        c.owner = CxOwnership::ThermalSubstep;
        let mut adapted = original.clone();
        for _ in 0..8 {
            let a = midpoint_gas::step_strang(&original, &c, 1e8).unwrap();
            let b = step_strang_with_evaluator(&adapted, &c, 1e8, &mut igm_rates).unwrap();
            assert_eq!(result_bits(&a), result_bits(&b));
            original = a.state;
            adapted = b.state;
        }
    }
}

#[test]
fn evaluator_is_called_once_per_rhs_stage_and_zero_step_calls_none() {
    let (s, mut c) = fixture(10000.0, 1.0, false);
    c.use_cx = false;
    let mut calls = 0;
    rhs_with_evaluator(&s, &c, &mut |t| {
        calls += 1;
        igm_rates(t)
    })
    .unwrap();
    assert_eq!(calls, 1);
    calls = 0;
    step_with_evaluator(&s, &c, 1e7, &mut |t| {
        calls += 1;
        igm_rates(t)
    })
    .unwrap();
    assert_eq!(calls, 2);
    let zero = step_with_evaluator(&s, &c, 0.0, &mut |_| {
        panic!("zero exposure must not evaluate a rate")
    })
    .unwrap();
    assert_eq!(state_bits(&zero.state), state_bits(&s));
}

#[test]
fn prepared_temperature_requires_exact_eos_bits() {
    let (s, c) = fixture(10000.0, 1.0, false);
    let t = s.gas.eos().unwrap().temperature_k;
    let r = igm_rates(t).unwrap();
    for wrong_t in [t.next_up(), t.next_down(), f64::NAN, f64::INFINITY, -t] {
        assert_eq!(
            rhs_with_rates(&s, &c, wrong_t, &r).unwrap_err(),
            NetworkError::SourceMismatch
        );
    }
}

#[test]
fn invalid_coefficients_fail_closed_before_population_updates() {
    let (s, c) = fixture(10000.0, 1.0, false);
    let before = state_bits(&s);
    let t = s.gas.eos().unwrap().temperature_k;
    let r = igm_rates(t).unwrap();
    for bad_value in [-1.0, f64::NAN, f64::INFINITY] {
        let expected = if bad_value.is_finite() {
            NetworkError::InvalidInput
        } else {
            NetworkError::NonFinite
        };
        let mut bad = r;
        bad.ci_cm3_s[0] = bad_value;
        assert_eq!(rhs_with_rates(&s, &c, t, &bad).unwrap_err(), expected);
        bad = r;
        bad.diagnostics.ce_cap_erg[2] = bad_value;
        assert_eq!(rhs_with_rates(&s, &c, t, &bad).unwrap_err(), expected);
    }
    assert_eq!(before, state_bits(&s));
    let mut negative = [0.0; 13];
    negative[S::DNeutral as usize] = -1.0;
    assert!(IsotopeNumberState::new(negative).is_err());
}

#[test]
fn original_source_photo_owner_and_temperature_rejections_are_preserved() {
    let (s, c) = fixture(10000.0, 1.0, false);
    let mut cases = Vec::new();
    let mut cc = c;
    cc.photon_source = "";
    cases.push((s.clone(), cc));
    cc = c;
    cc.use_photo = true;
    cases.push((s.clone(), cc));
    cc = c;
    cc.owner = CxOwnership::ThermalSubstep;
    cases.push((s.clone(), cc));
    let mut ss = s.clone();
    ss.photon_bins.push(parent::full_network::PhotonBin {
        energy_ev: 30.0,
        number_m3: 1.0,
    });
    cases.push((ss, c));
    for t in [2.0, 200001.0] {
        cases.push(fixture(t, 1.0, false));
    }
    for (s, c) in cases {
        assert_same_rhs(
            midpoint_gas::rhs(&s, &c),
            rhs_with_evaluator(&s, &c, &mut igm_rates),
        );
    }
    for h in [-1.0, f64::NAN, f64::INFINITY] {
        assert_same_result(
            midpoint_gas::step(&s, &c, h),
            step_with_evaluator(&s, &c, h, &mut igm_rates),
        );
    }
    assert_eq!(
        rhs_with_evaluator(&s, &c, &mut |_| {
            Err(ForwardError::InvalidInput("TEST_BACKEND_UNAVAILABLE"))
        })
        .unwrap_err(),
        NetworkError::TemperatureOutsideSource
    );
}

#[test]
fn cx_work_limit_remains_a_work_limit_and_does_not_mutate_state() {
    let (s, mut c) = fixture(10000.0, 1.0, false);
    c.owner = CxOwnership::ThermalSubstep;
    c.cx_controls.max_rate_calls = 1;
    let before = state_bits(&s);
    let original = midpoint_gas::step_strang(&s, &c, 1e8).unwrap_err();
    let adapted = step_strang_with_evaluator(&s, &c, 1e8, &mut igm_rates).unwrap_err();
    assert_eq!(original, NetworkError::Cx(CoupleError::WorkLimit));
    assert_eq!(adapted, original);
    assert_eq!(before, state_bits(&s));
}

#[test]
fn noncx_arithmetic_underflow_rejection_matches_original() {
    let (s, mut c) = fixture(10000.0, 1e-155, false);
    c.use_cx = false;
    assert_eq!(
        midpoint_gas::rhs(&s, &c).unwrap_err(),
        rhs_with_evaluator(&s, &c, &mut igm_rates).unwrap_err()
    );
}
