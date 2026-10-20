mod common;
use common::fixture;
use rei_iso_couple_reference::{HHeModel, midpoint_gas, positive_spectral::SpectralMode};
#[test]
fn cmb_exact_relaxation_is_second_order_not_euler() {
    let (_, _, mut cfg, start) = fixture(0., false, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    cfg.use_photo = false;
    cfg.use_cmb = true;
    cfg.cmb_temperature_k = 1000.;
    let hc = HHeModel::controlled_fixture();
    let arad = 8. * std::f64::consts::PI.powi(5) * hc.kb_erg_k.powi(4)
        / (15. * 6.626_070_15e-27_f64.powi(3) * hc.c_cm_s.powi(3));
    let coeff = 4. * 6.652_458_705_1e-25 * arad * hc.kb_erg_k / (9.109_383_713_9e-28 * hc.c_cm_s);
    let eos = start.gas.eos().unwrap();
    let cv = start.gas.thermal_j_m3 / eos.temperature_k;
    let lambda = coeff * (eos.free_electrons_m3 * 1e-6) * cfg.cmb_temperature_k.powi(4) * 0.1 / cv;
    let total = 0.4 / lambda;
    let exact =
        cfg.cmb_temperature_k + (eos.temperature_k - cfg.cmb_temperature_k) * (-0.4_f64).exp();
    let mut errs = Vec::new();
    for n in [8, 16, 32] {
        let mut s = start.clone();
        for _ in 0..n {
            s = midpoint_gas::step(&s, &cfg, total / n as f64)
                .unwrap()
                .state;
        }
        errs.push((s.gas.eos().unwrap().temperature_k - exact).abs());
    }
    let order = (errs[1] / errs[2]).log2();
    assert!(
        order > 1.9 && order < 2.15,
        "expected second-order CMB relaxation, measured {order}, errors={errs:?}"
    );
}
#[test]
fn collision_euler_map_matches_original_rate_owner() {
    use rei_iso_couple_reference::{
        deuterium_thermal_coupling::CxOwnership, full_network, isotope_state::IsotopeSpecies as S,
        midpoint_gas,
    };
    let (_, _, mut cfg, start) = fixture(0., true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    cfg.use_photo = false;
    cfg.use_cx = false;
    cfg.owner = CxOwnership::AtomicRhs;
    for t in [100., 3000., 10000., 60000.] {
        let mut s = start.clone();
        s.gas.thermal_j_m3 *= t / 10000.;
        let a = full_network::step(&s, &cfg, 1e7).unwrap();
        let k = midpoint_gas::rhs(&s, &cfg).unwrap();
        let b = midpoint_gas::apply(&s, &cfg, &k, 1e7).unwrap();
        for sp in S::ALL {
            let x = a.state.gas.nuclei.density_m3(sp);
            let y = b.state.gas.nuclei.density_m3(sp);
            assert!((x - y).abs() < 2e-13 * x.abs().max(1.));
        }
        for (x, y) in [
            (a.state.gas.thermal_j_m3, b.state.gas.thermal_j_m3),
            (a.state.escaped_j_m3, b.state.escaped_j_m3),
            (a.state.cmb_reservoir_j_m3, b.state.cmb_reservoir_j_m3),
        ] {
            assert!((x - y).abs() < 3e-13 * x.abs().max(1e-40));
        }
        for (x, y) in a
            .budget
            .ci_events_m3
            .iter()
            .chain(a.budget.rr_events_m3.iter())
            .zip(
                b.budget
                    .ci_events_m3
                    .iter()
                    .chain(b.budget.rr_events_m3.iter()),
            )
        {
            assert!((x - y).abs() < 3e-13 * x.abs().max(1e-40));
        }
    }
}
#[test]
fn cx_uses_original_forward_reverse_ledger_once() {
    use rei_iso_couple_reference::{
        deuterium_atomic::{DChargeExchange, d_atomic_rhs},
        deuterium_thermal_coupling::CxOwnership,
        isotope_state::IsotopeSpecies as S,
    };
    let (_, _, mut c, s) = fixture(0., false, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    c.use_photo = false;
    c.use_cx = true;
    c.owner = CxOwnership::AtomicRhs;
    let p = c
        .deuterium
        .photo_input_from_bound_rates(0., 0., c.photon_source)
        .unwrap();
    let d = d_atomic_rhs(
        c.deuterium,
        &s.gas.nuclei,
        1e4,
        &p,
        DChargeExchange::Savin2002,
    )
    .unwrap();
    let rhs = midpoint_gas::rhs(&s, &c).unwrap();
    let x = d.cx_forward_events_m3_s - d.cx_reverse_events_m3_s;
    assert_eq!(rhs.budget_per_s.cx_signed_m3.to_bits(), x.to_bits());
    assert_eq!(rhs.nuclei_per_s[S::DIonized as usize], x);
    assert_eq!(rhs.nuclei_per_s[S::H1Ionized as usize], -x);
    assert_eq!(
        rhs.budget_per_s.thermal_change_j_m3,
        d.channel_energy[4].thermal + d.channel_energy[5].thermal
    );
    assert_eq!(rhs.budget_per_s.freefree_integrated_j_m3, 0.);
    c.owner = CxOwnership::ThermalSubstep;
    assert!(midpoint_gas::rhs(&s, &c).is_err());
}
#[test]
fn gas_rhs_conserves_nuclei_and_augmented_energy() {
    use rei_iso_couple_reference::{
        deuterium_thermal_coupling::CxOwnership, isotope_state::IsotopeSpecies as S,
    };
    let (_, _, mut c, s) = fixture(0., true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    c.use_photo = false;
    c.owner = CxOwnership::AtomicRhs;
    let k = midpoint_gas::rhs(&s, &c).unwrap();
    let dn = k.nuclei_per_s;
    let scale = dn.iter().map(|x| x.abs()).fold(1e-50, f64::max);
    for family in [
        vec![S::H1Neutral, S::H1Ionized],
        vec![S::DNeutral, S::DIonized],
        vec![S::He4Neutral, S::He4SinglyIonized, S::He4DoublyIonized],
    ] {
        assert!(family.iter().map(|i| dn[*i as usize]).sum::<f64>().abs() < 1e-13 * scale);
    }
    let b = k.budget_per_s;
    let scale = b
        .thermal_change_j_m3
        .abs()
        .max(b.chemical_change_j_m3.abs())
        .max(1e-80);
    assert!(
        (b.thermal_change_j_m3 + b.chemical_change_j_m3 + b.escape_change_j_m3 + b.cmb_change_j_m3)
            .abs()
            < 2e-12 * scale
    );
    assert!(b.rr_events_m3.iter().sum::<f64>() > 0.);
    assert!(b.freefree_integrated_j_m3 > 0.);
}
#[test]
fn gas_invalid_steps_and_source_ownership_fail_transactionally() {
    use rei_iso_couple_reference::deuterium_thermal_coupling::CxOwnership;
    let (_, _, mut c, s) = fixture(0., true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    let before = format!("{s:?}");
    assert!(midpoint_gas::step(&s, &c, 1.).is_err());
    c.use_photo = false;
    c.owner = CxOwnership::AtomicRhs;
    for h in [f64::NAN, f64::INFINITY, -1., 1e20] {
        assert!(midpoint_gas::step(&s, &c, h).is_err());
    }
    assert_eq!(before, format!("{s:?}"));
    let r = midpoint_gas::step(&s, &c, 0.).unwrap();
    assert_eq!(before, format!("{:?}", r.state));
}
#[test]
fn all_gas_channels_off_changes_only_elapsed_time() {
    let (_, _, mut c, s) = fixture(0., false, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    c.use_photo = false;
    let mut out = midpoint_gas::step(&s, &c, 1e10).unwrap().state;
    assert_eq!(out.elapsed_s, 1e10);
    out.elapsed_s = s.elapsed_s;
    assert_eq!(format!("{s:?}"), format!("{out:?}"));
}

#[test]
fn native_cx_flow_preserved_at_coarse_grid_matches_independent_reference() {
    let (_, _, mut c, mut state) = fixture(0., true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    c.use_photo = false;
    c.cx_controls.rtol = 1e-12;
    c.cx_controls.atol_normalized = 1e-15;
    for _ in 0..8 {
        state = midpoint_gas::step_strang(&state, &c, 1e10).unwrap().state;
    }
    // Independent DOP853 over source-native instantaneous RHS, tolerance-refined.
    let reference_dii = 11.486186477801967;
    let error = (state
        .gas
        .nuclei
        .density_m3(rei_iso_couple_reference::IsotopeSpecies::DIonized)
        - reference_dii)
        .abs();
    assert!(error < 1e-6, "CX stiffness accuracy target: error {error}");
}
