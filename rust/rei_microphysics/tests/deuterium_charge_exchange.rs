use rei_microphysics::deuterium_charge_exchange::{
    step_frozen_rates, DhEnergyDefect, DhError, DhMethodScope, DhRates, DhState, DhStep, Savin2002,
};

fn rates(forward: f64, reverse: f64) -> DhRates {
    DhRates {
        forward_m3_s: forward,
        reverse_m3_s: reverse,
        temperature_k: 1.0,
        minimum_k: 1.0,
        maximum_k: 1.0,
        source: "manufactured dimensionless kinetics, not atomic rate data",
    }
}

fn defect(delta_chi_j: f64) -> DhEnergyDefect {
    DhEnergyDefect {
        delta_chi_j,
        source: "explicit manufactured chi_D - chi_H, independent of fit exponents",
    }
}

fn state() -> DhState {
    DhState {
        h0_m3: 5.0,
        hp_m3: 5.0,
        d0_m3: 2.0,
        dp_m3: 1.0,
        thermal_j_m3: 100.0,
    }
}

fn close(actual: f64, expected: f64, relative: f64) {
    assert!(
        (actual - expected).abs() <= relative * actual.abs().max(expected.abs()).max(1e-300),
        "actual={actual:.17e}, expected={expected:.17e}, relative={relative}"
    );
}

fn conserved(step: DhStep) {
    let a = step.totals_before;
    let b = step.totals_after;
    for (x, y) in [
        (a.hydrogen_m3, b.hydrogen_m3),
        (a.deuterium_m3, b.deuterium_m3),
        (a.positive_charge_m3, b.positive_charge_m3),
        (a.baryons_m3, b.baryons_m3),
        (a.electrons_m3, b.electrons_m3),
        (a.thermal_particles_m3, b.thermal_particles_m3),
    ] {
        close(x, y, 1e-13);
    }
    for x in [
        step.state.h0_m3,
        step.state.hp_m3,
        step.state.d0_m3,
        step.state.dp_m3,
        step.state.thermal_j_m3,
    ] {
        assert!(x.is_finite() && x >= 0.0);
    }
    let lower = (b.positive_charge_m3 - b.hydrogen_m3).max(0.0);
    let upper = b.deuterium_m3.min(b.positive_charge_m3);
    assert!(step.state.dp_m3 >= lower && step.state.dp_m3 <= upper);
}

#[test]
fn integer_stoichiometry_and_missing_electron_negative_control() {
    // Rows H0,H+,D0,D+,e; columns Hion,Hrec,Dion,Drec,CTf,CTr.
    let s = [
        [-1, 1, 0, 0, 1, -1],
        [1, -1, 0, 0, -1, 1],
        [0, 0, -1, 1, -1, 1],
        [0, 0, 1, -1, 1, -1],
        [1, -1, 1, -1, 0, 0],
    ];
    let rows = [
        [1, 1, 0, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 1, 0, 1, -1],
        [1, 1, 2, 2, 0],
    ];
    for row in rows {
        for j in 0..6 {
            assert_eq!((0..5).map(|i| row[i] * s[i][j]).sum::<i32>(), 0);
        }
    }
    let mut broken = s;
    broken[4][0] = 0;
    let charge = rows[2];
    let residual: Vec<i32> = (0..6)
        .map(|j| (0..5).map(|i| charge[i] * broken[i][j]).sum())
        .collect();
    assert_eq!(residual, [1, 0, 0, 0, 0, 0]);
    let particle_changes: Vec<i32> = (0..6).map(|j| (0..5).map(|i| s[i][j]).sum()).collect();
    assert_eq!(particle_changes, [1, -1, 1, -1, 0, 0]);
}

#[test]
fn savin_domain_table_and_si_transcription() {
    for t in [2.7, 200_000.0] {
        let r = Savin2002::rates(t).unwrap();
        assert_eq!(r.minimum_k, 2.7);
        assert_eq!(r.maximum_k, 200_000.0);
        assert!(r.source.contains("10.1086/324218"));
    }
    for t in [2.699999, 200_000.0001, 1.0, 0.0, -1.0] {
        assert_eq!(Savin2002::rates(t), Err(DhError::OutsideTemperatureDomain));
    }
    for t in [f64::NAN, f64::INFINITY, f64::NEG_INFINITY] {
        assert_eq!(Savin2002::rates(t), Err(DhError::NonFiniteInput));
    }
    // Savin Table 1; Table 2's fit deviations, not physical uncertainty bounds.
    for (t, forward_cm3, reverse_cm3) in [
        (20.0, 1.04e-10, 8.90e-10),
        (100.0, 8.63e-10, 1.32e-9),
        (10_000.0, 8.04e-9, 8.07e-9),
    ] {
        let r = Savin2002::rates(t).unwrap();
        assert!((r.forward_m3_s / (forward_cm3 * 1e-6) - 1.0).abs() < 0.06);
        assert!((r.reverse_m3_s / (reverse_cm3 * 1e-6) - 1.0).abs() < 0.04);
        let direct_f = 2.00e-10 * t.powf(0.402) * (-37.1 / t).exp() - 3.31e-17 * t.powf(1.48);
        let direct_r = 2.06e-10 * t.powf(0.396) * (-33.0 / t).exp() + 2.03e-9 * t.powf(-0.332);
        close(r.forward_m3_s / direct_f, 1e-6, 1e-15);
        close(r.reverse_m3_s / direct_r, 1e-6, 1e-15);
    }
}

#[test]
fn manufactured_wolfram_oracle() {
    // A=10,B=3,C=6,x=1,kf=2/5,kr=1/7,h=7/3. Not a physical run.
    let step = step_frozen_rates(
        state(),
        rates(2.0 / 5.0, 1.0 / 7.0),
        7.0 / 3.0,
        defect(0.01),
    )
    .unwrap();
    close(step.state.dp_m3, 1.96318481884852365308088403099, 1e-13);
    assert_eq!(step.scope, DhMethodScope::ExactFrozenRatesFixedProperVolume);
    conserved(step);
}

#[test]
fn frozen_semigroup_and_identity_cases() {
    let r = rates(0.4, 1.0 / 7.0);
    let first = step_frozen_rates(state(), r, 0.37, defect(0.01)).unwrap();
    let split = step_frozen_rates(first.state, r, 1.63, defect(0.01)).unwrap();
    let one = step_frozen_rates(state(), r, 2.0, defect(0.01)).unwrap();
    for (x, y) in [
        (split.state.h0_m3, one.state.h0_m3),
        (split.state.hp_m3, one.state.hp_m3),
        (split.state.d0_m3, one.state.d0_m3),
        (split.state.dp_m3, one.state.dp_m3),
        (split.state.thermal_j_m3, one.state.thermal_j_m3),
    ] {
        close(x, y, 1e-13);
    }
    for (s, rr, dt) in [
        (state(), r, 0.0),
        (state(), rates(0.0, 0.0), 100.0),
        (
            DhState {
                h0_m3: 0.0,
                hp_m3: 0.0,
                ..state()
            },
            r,
            100.0,
        ),
        (
            DhState {
                h0_m3: 0.0,
                hp_m3: 0.0,
                d0_m3: 0.0,
                dp_m3: 0.0,
                thermal_j_m3: 0.0,
            },
            r,
            100.0,
        ),
    ] {
        let step = step_frozen_rates(s, rr, dt, defect(0.01)).unwrap();
        assert_eq!(step.state, s);
        assert_eq!(step.extent_m3, 0.0);
    }
    // Equal forward/reverse flux at x=1 with all four densities unity.
    let equilibrium = DhState {
        h0_m3: 1.0,
        hp_m3: 1.0,
        d0_m3: 1.0,
        dp_m3: 1.0,
        ..state()
    };
    let eq = step_frozen_rates(equilibrium, rates(0.25, 0.25), 1e300, defect(0.01)).unwrap();
    assert_eq!(eq.state, equilibrium);
}

#[test]
fn degenerate_depletion_reverse_and_stiff_limits() {
    // Pure forward, equal reactants: d=0, y_new = y/(1+k*y*h).
    let initial = DhState {
        h0_m3: 0.0,
        hp_m3: 2.0,
        d0_m3: 2.0,
        dp_m3: 0.0,
        ..state()
    };
    let step = step_frozen_rates(initial, rates(0.5, 0.0), 3.0, defect(0.01)).unwrap();
    close(step.state.d0_m3, 2.0 / (1.0 + 0.5 * 2.0 * 3.0), 1e-13);
    conserved(step);
    let reverse = DhState {
        h0_m3: 2.0,
        hp_m3: 0.0,
        d0_m3: 0.0,
        dp_m3: 2.0,
        ..state()
    };
    let rev = step_frozen_rates(reverse, rates(0.0, 0.5), 3.0, defect(0.01)).unwrap();
    close(rev.state.dp_m3, 0.5, 1e-13);
    assert!(rev.extent_m3 < 0.0);
    conserved(rev);
    for (s, r) in [
        (initial, rates(1e200, 0.0)),
        (reverse, rates(0.0, 1e200)),
        (state(), rates(1e200, 1e200)),
    ] {
        let stiff = step_frozen_rates(s, r, 1e200, defect(0.01)).unwrap();
        conserved(stiff);
        if r.forward_m3_s == r.reverse_m3_s {
            close(
                stiff.state.d0_m3 * stiff.state.hp_m3,
                stiff.state.dp_m3 * stiff.state.h0_m3,
                1e-13,
            );
        }
    }
}

#[test]
fn energy_exchange_transaction_and_diagnostics() {
    let input = state();
    let forward = step_frozen_rates(input, rates(0.4, 0.0), 1.0, defect(0.02)).unwrap();
    assert!(forward.extent_m3 > 0.0);
    assert!(forward.chemical_delta_j_m3 > 0.0 && forward.thermal_delta_j_m3 < 0.0);
    assert_eq!(
        forward.chemical_delta_j_m3 + forward.thermal_delta_j_m3,
        0.0
    );
    close(
        forward.state.thermal_j_m3 - input.thermal_j_m3,
        forward.thermal_delta_j_m3,
        1e-12,
    );
    assert_eq!(forward.electron_delta_m3, 0.0);
    conserved(forward);
    let reverse = step_frozen_rates(input, rates(0.0, 0.4), 1.0, defect(0.02)).unwrap();
    assert!(
        reverse.extent_m3 < 0.0
            && reverse.chemical_delta_j_m3 < 0.0
            && reverse.thermal_delta_j_m3 > 0.0
    );
    assert_eq!(
        reverse.chemical_delta_j_m3 + reverse.thermal_delta_j_m3,
        0.0
    );
    let cold = DhState {
        thermal_j_m3: 0.0,
        ..input
    };
    let saved = cold;
    assert_eq!(
        step_frozen_rates(cold, rates(0.4, 0.0), 1.0, defect(0.02)),
        Err(DhError::NegativeFinalThermalEnergy)
    );
    assert_eq!(cold, saved);
    assert_eq!(input, state());
    assert_eq!(
        step_frozen_rates(input, rates(0.4, 0.0), -1.0, defect(0.02)),
        Err(DhError::InvalidInput)
    );
    assert_eq!(
        step_frozen_rates(input, rates(0.4, 0.0), f64::NAN, defect(0.02)),
        Err(DhError::NonFiniteInput)
    );
    assert_eq!(
        step_frozen_rates(
            DhState {
                hp_m3: -1.0,
                ..input
            },
            rates(1.0, 0.0),
            1.0,
            defect(0.02)
        ),
        Err(DhError::InvalidInput)
    );
    assert_eq!(
        step_frozen_rates(input, rates(1.0, 0.0), 1.0, defect(f64::INFINITY)),
        Err(DhError::NonFiniteInput)
    );
    assert_eq!(
        step_frozen_rates(
            DhState {
                h0_m3: f64::MAX,
                hp_m3: f64::MAX,
                ..input
            },
            rates(1.0, 0.0),
            1.0,
            defect(0.02)
        ),
        Err(DhError::ArithmeticOverflow)
    );
}

#[test]
fn absent_deuterium_is_hhe_noop() {
    let hhe = DhState {
        d0_m3: 0.0,
        dp_m3: 0.0,
        ..state()
    };
    let step =
        step_frozen_rates(hhe, Savin2002::rates(100.0).unwrap(), 1e30, defect(6e-22)).unwrap();
    assert_eq!(step.state, hhe);
    assert_eq!(step.extent_m3, 0.0);
    assert_eq!(step.chemical_delta_j_m3, 0.0);
    conserved(step);
}
