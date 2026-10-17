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
    let h = 0.0;
    let s = 0.0;
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
fn newborns_use_phi_and_old_cohorts_use_exp() {
    let (b, mut c, initial) = data();
    c.use_collisions = false;
    c.use_cx = false;
    c.use_cmb = false;
    let state = b.initial(initial, &c, 0.).unwrap();
    let dt = 1e8;
    let born = b.0.source_births(dt / 2., dt).unwrap();
    let first = b.advance_fixed_geometry_phi(&state, &c, dt).unwrap();
    let g = b.0.geometry.snapshot(0.).unwrap();
    for (before, after) in born.iter().zip(&first.state.cohorts) {
        let e = before.ray_at(&g).unwrap().energy_ev;
        let lam = lambda(e, &state.full.gas, &c);
        let t = lam * dt;
        let phi = if t == 0. { 1. } else { -(-t).exp_m1() / t };
        assert!(rel(after.n_comoving_m3, before.n_comoving_m3 * phi) < 2e-12);
    }
    let second = b.advance_fixed_geometry_phi(&first.state, &c, dt).unwrap();
    for (before, after) in first.state.cohorts.iter().zip(&second.state.cohorts) {
        let e = before.ray_at(&g).unwrap().energy_ev;
        let lam = lambda(e, &first.state.full.gas, &c);
        assert!(
            rel(
                after.n_comoving_m3,
                before.n_comoving_m3 * (-lam * dt).exp()
            ) < 2e-12
        );
    }
    assert!(second.global_energy_relative_error < 3e-10);
    let n = second
        .state
        .cohorts
        .iter()
        .map(|x| x.n_comoving_m3)
        .sum::<f64>();
    assert!(
        rel(
            second.state.source_injected_count_com3,
            n + second.state.photon_absorbed_count_com3
        ) < 1e-11
    );
}
#[test]
fn variable_geometry_rejected() {
    for (h, s) in [(1e-16, 0.), (0., 1e-17)] {
        let (mut b, c, initial) = data();
        b.0.geometry.reference_point.mean_hubble_per_s = h;
        b.0.geometry.reference_point.shear_per_s = s;
        let state = b.initial(initial, &c, 0.).unwrap();
        assert!(b.advance_fixed_geometry_phi(&state, &c, 1e8).is_err());
    }
}
#[test]
fn malformed_history_rejected_transactionally() {
    let (b, c, initial) = data();
    let state = b.initial(initial, &c, 0.).unwrap();
    let mut bad = state.clone();
    bad.full.elapsed_s = 1.;
    assert!(b.advance_fixed_geometry_phi(&bad, &c, 1e8).is_err());
    let mut bad = state.clone();
    bad.full
        .photon_bins
        .push(rei_iso_couple_reference::full_network::PhotonBin {
            energy_ev: 30.,
            number_m3: 1.,
        });
    assert!(b.advance_fixed_geometry_phi(&bad, &c, 1e8).is_err());
    let mut bad = state.clone();
    bad.source_injected_count_com3 = f64::INFINITY;
    assert!(b.advance_fixed_geometry_phi(&bad, &c, 1e8).is_err());
    assert_eq!(state.time_s, 0.);
}
#[test]
fn incompatible_cohort_or_future_birth_rejected() {
    let (b, c, initial) = data();
    let mut state = b.initial(initial, &c, 0.).unwrap();
    state.cohorts = b.0.source_births(0., 1e6).unwrap();
    state.cohorts[0].birth_time_s = 1.;
    assert!(b.advance_fixed_geometry_phi(&state, &c, 1e8).is_err());
    state.cohorts[0].birth_time_s = f64::NAN;
    assert!(b.advance_fixed_geometry_phi(&state, &c, 1e8).is_err());
    state.cohorts[0].birth_time_s = 0.;
    state.cohorts[0].birth_geometry.scale_factors[0] *= 2.;
    assert!(b.advance_fixed_geometry_phi(&state, &c, 1e8).is_err());
}
#[test]
fn legacy_and_phi_are_distinct() {
    let (b, mut c, initial) = data();
    c.use_collisions = false;
    c.use_cx = false;
    c.use_cmb = false;
    let s = b.initial(initial, &c, 0.).unwrap();
    let a = b.advance(&s, &c, 1e8).unwrap();
    let p = b.advance_fixed_geometry_phi(&s, &c, 1e8).unwrap();
    assert!(p.state.photon_absorbed_count_com3 < a.state.photon_absorbed_count_com3);
}
#[test]
fn all_channels_fixed_geometry_close() {
    let (b, c, initial) = data();
    let s = b.initial(initial, &c, 0.).unwrap();
    let r = b.advance_fixed_geometry_phi(&s, &c, 1e8).unwrap();
    assert!(r.global_energy_relative_error < 3e-10);
    assert_eq!(r.radiation_redshift_work_j_com3, 0.);
    assert_eq!(r.adiabatic_gas_work_j_com3, 0.);
}

fn lambda(e: f64, gas: &MixtureState, c: &NetworkConfig) -> f64 {
    use rei_iso_couple_reference::{Absorber, AtomicProvider};
    let n = &gas.nuclei;
    let p = AtomicProvider::reference();
    let mut op = 0.;
    for (sp, a) in [
        (S::H1Neutral, Absorber::HI),
        (S::He4Neutral, Absorber::HeI),
        (S::He4SinglyIonized, Absorber::HeII),
    ] {
        op += n.density_m3(sp) * p.cross_section(a, e).unwrap() * 1e-4;
    }
    op += n.density_m3(S::DNeutral) * c.deuterium.cross_section_m2(e).unwrap();
    op * rei_iso_couple_reference::full_network::SPEED_OF_LIGHT_M_S
}
#[test]
fn cohort_cap_is_checked_before_new_birth_allocation() {
    let (b, c, initial) = data();
    let mut s = b.initial(initial, &c, 0.).unwrap();
    let co = b.0.source_births(0., 1.).unwrap()[0].clone();
    s.cohorts = vec![co; 65_536];
    let n = s.cohorts.len();
    assert!(b.advance_fixed_geometry_phi(&s, &c, 1.).is_err());
    assert_eq!(s.cohorts.len(), n);
}
#[test]
fn time_roundoff_cannot_hide_newborn_classification() {
    let (b, c, mut initial) = data();
    initial.elapsed_s = 1e12;
    let s = b.initial(initial, &c, 1e12).unwrap();
    assert!(b.advance_fixed_geometry_phi(&s, &c, 1e-10).is_err());
}
#[test]
fn signed_geometry_ledger_and_counter_guards() {
    let (b, c, initial) = data();
    let s = b.initial(initial, &c, 0.).unwrap();
    for x in [f64::NAN, f64::INFINITY, f64::NEG_INFINITY] {
        let mut bad = s.clone();
        bad.geometry_work_j_com3 = x;
        assert!(b.advance_fixed_geometry_phi(&bad, &c, 1e8).is_err());
    }
    let mut bad = s.clone();
    bad.chemistry_accepted = usize::MAX;
    assert!(b.advance_fixed_geometry_phi(&bad, &c, 1e8).is_err());
    let mut good = s;
    good.geometry_work_j_com3 = -1e-30;
    assert!(b.advance_fixed_geometry_phi(&good, &c, 1e8).is_ok());
}
