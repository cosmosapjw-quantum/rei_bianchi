use rei_iso_couple_reference::{
    HHeModel,
    deuterium_atomic::DAtomicProvider,
    full_network::{self, FullState, NetworkConfig},
    gas_reference_rhs::gas_rates,
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
};
fn fixture() -> (FullState, NetworkConfig) {
    let mut n = [0.; 13];
    for (s, v) in [
        (S::H1Neutral, 180.),
        (S::H1Ionized, 20.),
        (S::DNeutral, 0.0045),
        (S::DIonized, 0.0005),
        (S::He4Neutral, 12.),
        (S::He4SinglyIonized, 3.),
        (S::He4DoublyIonized, 1.),
    ] {
        n[s as usize] = v;
    }
    let nuclei = IsotopeNumberState::new(n).unwrap();
    let u = 1.5 * KB_J_K * nuclei.thermal_particle_density_all_thermal_m3().unwrap() * 1.0e4;
    let h = HHeModel::controlled_fixture().threshold_ev[0];
    let mut c = NetworkConfig::source_bound(
        DAtomicProvider::new(h, h + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        "TEST_SOURCE",
    );
    c.use_photo = false;
    c.use_cx = false;
    c.cmb_temperature_k = 29.;
    (
        FullState {
            gas: MixtureState {
                nuclei,
                thermal_j_m3: u,
            },
            photon_bins: vec![],
            escaped_j_m3: 0.,
            cmb_reservoir_j_m3: 0.,
            elapsed_s: 0.,
        },
        c,
    )
}
#[test]
fn instantaneous_events_match_original_collision_step() {
    let (s, c) = fixture();
    let dt = 1.0e6;
    let out = full_network::step(&s, &c, dt).unwrap();
    let r = gas_rates(&s, &c, 5).unwrap();
    for j in 0..4 {
        let v = r.rr[j] * dt;
        let w = out.budget.rr_events_m3[j];
        assert!(
            (v - w).abs() < 1e-11 * w.abs().max(1e-40),
            "rr channel {j}: {v} vs {w}"
        );
    }
    assert!(
        (r.heat * dt - out.budget.thermal_change_j_m3).abs()
            < 1e-11 * out.budget.thermal_change_j_m3.abs()
    );
}
#[test]
fn rate_energy_baryon_charge_identities_on_temperature_grid() {
    for t in [10., 100., 1000., 10000., 50000., 190000.] {
        let (mut s, c) = fixture();
        s.gas.thermal_j_m3 *= t / 1e4;
        for mask in 0..8 {
            let q = gas_rates(&s, &c, mask).unwrap();
            let b = S::ALL
                .into_iter()
                .map(|sp| f64::from(sp.baryon_number()) * q.species[sp as usize])
                .sum::<f64>();
            let scale = q.species.iter().map(|x| x.abs()).sum::<f64>().max(1e-100);
            assert!(b.abs() < 1e-12 * scale);
            let qdot = S::ALL
                .into_iter()
                .map(|sp| f64::from(sp.charge()) * q.species[sp as usize])
                .sum::<f64>();
            let expected = q.ci.iter().sum::<f64>() - q.rr.iter().sum::<f64>() - q.dr;
            assert!((qdot - expected).abs() < 1e-12 * scale);
            let en = q.heat.abs() + q.chemical.abs() + q.escape.abs() + q.cmb.abs();
            assert!(q.residual().abs() <= 1e-12 * en);
        }
    }
}
#[test]
fn all_collision_budget_channels_and_state_agree_with_native() {
    let (mut s, c) = fixture();
    for t in [100., 1e4, 5e4] {
        s.gas.thermal_j_m3 = 1.5
            * KB_J_K
            * s.gas
                .nuclei
                .thermal_particle_density_all_thermal_m3()
                .unwrap()
            * t;
        let h = 1e5;
        let out = full_network::step(&s, &c, h).unwrap();
        let q = gas_rates(&s, &c, 5).unwrap();
        for sp in S::ALL {
            let expected = s.gas.nuclei.density_m3(sp) + h * q.species[sp as usize];
            assert!(
                (expected - out.state.gas.nuclei.density_m3(sp)).abs() <= 2e-14 * expected.abs()
            );
        }
        for (a, b) in
            q.ci.into_iter()
                .zip(out.budget.ci_events_m3)
                .chain(q.rr.into_iter().zip(out.budget.rr_events_m3))
        {
            assert!((a * h - b).abs() <= 1e-12 * b.abs());
        }
        for (a, b) in [
            (q.dr, out.budget.dr_hei_m3),
            (q.ff, out.budget.freefree_integrated_j_m3),
            (q.escape, out.budget.escape_change_j_m3),
            (q.cmb, out.budget.cmb_change_j_m3),
        ] {
            assert!((a * h - b).abs() <= 1e-12 * b.abs());
        }
    }
}
#[test]
fn masks_are_additive_and_zero_is_zero() {
    let (s, c) = fixture();
    let total = gas_rates(&s, &c, 7).unwrap().vector();
    let mut sum = [0.; 27];
    for m in [1, 2, 4] {
        for (a, b) in sum.iter_mut().zip(gas_rates(&s, &c, m).unwrap().vector()) {
            *a += b;
        }
    }
    for (a, b) in sum.into_iter().zip(total) {
        assert!((a - b).abs() <= 3e-14 * a.abs().max(b.abs()).max(1e-100));
    }
    assert_eq!(gas_rates(&s, &c, 0).unwrap().vector(), [0.; 27]);
}
#[test]
fn cx_alone_has_no_electron_source_or_radiative_loss() {
    let (s, c) = fixture();
    let q = gas_rates(&s, &c, 2).unwrap();
    assert_eq!(q.escape, 0.);
    assert_eq!(q.cmb, 0.);
    assert_eq!(q.ff, 0.);
    assert_eq!(q.ci, [0.; 4]);
    assert_eq!(q.rr, [0.; 4]);
    assert_eq!(
        q.species[S::H1Ionized as usize] + q.species[S::DIonized as usize],
        0.
    );
}
#[test]
fn cmb_direction_and_zero_at_common_temperature() {
    let (s, mut c) = fixture();
    let t = s.gas.eos().unwrap().temperature_k;
    c.cmb_temperature_k = t;
    assert_eq!(gas_rates(&s, &c, 4).unwrap().heat, 0.);
    c.cmb_temperature_k = 2. * t;
    let r = gas_rates(&s, &c, 4).unwrap();
    assert!(r.heat > 0.);
    assert_eq!(r.heat, -r.cmb);
}
#[test]
fn photon_owner_and_source_domain_fail_closed() {
    let (mut s, mut c) = fixture();
    c.use_photo = true;
    assert!(gas_rates(&s, &c, 7).is_err());
    c.use_photo = false;
    s.gas.thermal_j_m3 *= 30.;
    assert!(gas_rates(&s, &c, 7).is_err());
}
#[test]
fn native_gas_result_satisfies_external_contract() {
    let (s, mut c) = fixture();
    c.use_cx = true;
    let out = full_network::step(&s, &c, 1e8).unwrap();
    rei_iso_couple_reference::gas_solver_contract::validate_result(&s, &c, 1e8, &out).unwrap();
}
#[test]
fn wrong_event_budget_and_photo_ownership_are_rejected() {
    let (s, c) = fixture();
    let mut out = full_network::step(&s, &c, 1e8).unwrap();
    out.budget.rr_events_m3[0] += 1.;
    assert!(
        rei_iso_couple_reference::gas_solver_contract::validate_result(&s, &c, 1e8, &out).is_err()
    );
    let mut out = full_network::step(&s, &c, 1e8).unwrap();
    out.budget.photo_events_m3[0] = 1.;
    assert!(
        rei_iso_couple_reference::gas_solver_contract::validate_result(&s, &c, 1e8, &out).is_err()
    );
}

#[test]
fn unowned_spectator_change_is_rejected() {
    let (s, c) = fixture();
    let mut out = full_network::step(&s, &c, 1e8).unwrap();
    let mut n = [0.; 13];
    for sp in S::ALL {
        n[sp as usize] = out.state.gas.nuclei.density_m3(sp);
    }
    n[S::He3Neutral as usize] = 1.;
    out.state.gas.nuclei = IsotopeNumberState::new(n).unwrap();
    assert!(
        rei_iso_couple_reference::gas_solver_contract::validate_result(&s, &c, 1e8, &out).is_err()
    );
}
