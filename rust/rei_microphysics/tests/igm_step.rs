use rei_microphysics::{
    coupled_primary::PrimaryPacket, igm_state::IgmGasState, igm_step::*, HHeModel,
};
fn bg() -> StepBackground {
    StepBackground {
        n_h: 4e-4,
        n_he: 3.16e-5,
        hubble: 6e-17,
        tcmb: 35.0,
    }
}
fn gas(t: f64) -> IgmGasState {
    IgmGasState::from_temperature([2e-4, 0.0, 0.0], bg().n_h, bg().n_he, t).unwrap()
}
fn binding(g: &IgmGasState, b: StepBackground) -> f64 {
    let c = HHeModel::controlled_fixture();
    c.ev_erg
        * (c.threshold_ev[0] * g.fractions[0]
            + b.n_he / b.n_h
                * (c.threshold_ev[1] * g.fractions[1]
                    + (c.threshold_ev[1] + c.threshold_ev[2]) * g.fractions[2]))
}
#[test]
fn neutral_helium_growth_and_complete_energy_number_ownership() {
    let old = gas(30.0);
    let p = vec![PrimaryPacket {
        energy_ev: 80.0,
        per_h: 0.01,
    }];
    let dt = 1e11;
    let b = bg();
    let r = implicit_step(&old, &p, b, dt, StepControl::default()).unwrap();
    assert!(r.gas.fractions[1] > 0.0 && r.gas.fractions[2] > 0.0);
    assert!(r.packets[0].per_h > 0.0 && r.packets[0].per_h < p[0].per_h);
    let absorbed = r.absorbed_per_h.iter().sum::<f64>();
    assert!((p[0].per_h - r.packets[0].per_h - absorbed).abs() < 1e-10 * p[0].per_h);
    let c = HHeModel::controlled_fixture();
    let material = r.gas.w_erg_per_h + binding(&r.gas, b) - old.w_erg_per_h - binding(&old, b);
    let radiation = (r.packets[0].per_h - p[0].per_h) * 80.0 * c.ev_erg;
    let reservoirs = dt / b.n_h
        * (r.endpoint.escape_erg_cm3_s - r.endpoint.cmb_to_gas_erg_cm3_s
            + r.endpoint.expansion_work_erg_cm3_s);
    assert!((material + radiation + reservoirs).abs() < 1e-10 * (p[0].per_h * 80.0 * c.ev_erg));
    assert!(r.residual <= 1e-13);
}
#[test]
fn zero_photons_and_zero_electrons_stay_zero() {
    let b = bg();
    let old = IgmGasState::from_temperature([0.0; 3], b.n_h, b.n_he, 30.0).unwrap();
    let r = implicit_step(&old, &[], b, 1e12, StepControl::default()).unwrap();
    assert_eq!(r.gas.fractions, [0.0; 3]);
    assert!(r.packets.is_empty());
    assert!(r.gas.w_erg_per_h < old.w_erg_per_h);
}
#[test]
fn failure_is_nonmutating_and_eos_domain_is_strict() {
    let old = gas(30.0);
    let copy = old;
    assert!(implicit_step(
        &old,
        &[],
        bg(),
        1e12,
        StepControl {
            max_iterations: 0,
            ..StepControl::default()
        }
    )
    .is_err());
    assert_eq!(old.fractions, copy.fractions);
    assert_eq!(old.w_erg_per_h, copy.w_erg_per_h);
    let bad = gas(0.9);
    assert!(implicit_step(&bad, &[], bg(), 1.0, StepControl::default()).is_err());
}
#[test]
fn high_opacity_and_stiff_recombination_remain_admissible() {
    let b = StepBackground {
        n_h: 1.0,
        n_he: 0.08,
        ..bg()
    };
    let old = IgmGasState::from_temperature([0.9, 0.2, 0.7], b.n_h, b.n_he, 1e4).unwrap();
    let r = implicit_step(
        &old,
        &[PrimaryPacket {
            energy_ev: 20.0,
            per_h: 1e-3,
        }],
        b,
        1e11,
        StepControl::default(),
    )
    .unwrap();
    r.gas.eos(b.n_h, b.n_he).unwrap();
    assert!(r.packets[0].per_h > 0.0);
    assert!(r.gas.fractions[0] < old.fractions[0]);
}
#[test]
fn admitted_static_eos_roots_are_exact_fixed_points_including_endpoints() {
    let b = StepBackground {
        hubble: 0.0,
        ..bg()
    };
    for t in [1.0, 1.0 + 1e-13, 30.0, 1e6 - 1e-7, 1e6] {
        let old = IgmGasState::from_temperature([0.0; 3], b.n_h, b.n_he, t).unwrap();
        if rei_microphysics::igm_thermal::igm_point_rhs(
            &old,
            b.n_h,
            b.n_he,
            0.0,
            b.tcmb,
            Default::default(),
        )
        .is_err()
        {
            continue;
        }
        let r = implicit_step(&old, &[], b, 1.0, StepControl::default()).unwrap();
        assert_eq!(r.gas.w_erg_per_h, old.w_erg_per_h);
        assert_eq!(r.gas.fractions, old.fractions);
    }
}
#[test]
fn tiny_adiabatic_steps_keep_representable_budget_roots() {
    let b = bg();
    let old = IgmGasState::from_temperature([0.0; 3], b.n_h, b.n_he, 30.0).unwrap();
    for dt in [3.0, 10.0, 1e3, 1e6] {
        let r = implicit_step(&old, &[], b, dt, StepControl::default()).unwrap();
        let expected = old.w_erg_per_h / (1.0 + 2.0 * b.hubble * dt);
        assert!((r.gas.w_erg_per_h - expected).abs() <= 2e-30);
    }
}
