use rei_iso_couple_reference::birth_clock::{BirthPartition, uniform_partition};
use rei_iso_couple_reference::deuterium_atomic::DAtomicProvider;
use rei_iso_couple_reference::full_network::{
    EV_J, FullState, NetworkConfig, PhotonBin, step, step_fixed_volume_uniform_births,
};
use rei_iso_couple_reference::mixture_eos::{KB_J_K, MixtureState};
use rei_iso_couple_reference::{HHeModel, IsotopeNumberState, IsotopeSpecies as S};
fn close(a: f64, b: f64, t: f64) {
    assert!(
        (a - b).abs() <= t * a.abs().max(b.abs()).max(1e-300),
        "{a:e} {b:e}"
    );
}
fn fixture() -> (FullState, NetworkConfig) {
    let mut n = [0.; 13];
    n[S::H1Neutral as usize] = 1000.;
    n[S::H1Ionized as usize] = 900.;
    n[S::DNeutral as usize] = 25.;
    n[S::DIonized as usize] = 5.;
    n[S::He4Neutral as usize] = 300.;
    n[S::He4SinglyIonized as usize] = 100.;
    let nuclei = IsotopeNumberState::new(n).unwrap();
    let nth = nuclei.thermal_particle_density_all_thermal_m3().unwrap();
    let h = HHeModel::controlled_fixture().threshold_ev[0];
    let mut c = NetworkConfig::source_bound(
        DAtomicProvider::new(h, h + 0.0037, "MANUFACTURED_OFFSET").unwrap(),
        "MANUFACTURED_CONSTANT_BIRTHS",
    );
    c.use_collisions = false;
    c.use_cx = false;
    c.use_cmb = false;
    (
        FullState {
            gas: MixtureState {
                nuclei,
                thermal_j_m3: 1.5 * KB_J_K * nth * 1e4,
            },
            photon_bins: vec![
                PhotonBin {
                    energy_ev: 70.,
                    number_m3: 2.,
                },
                PhotonBin {
                    energy_ev: 30.,
                    number_m3: 1.,
                },
            ],
            escaped_j_m3: 0.,
            cmb_reservoir_j_m3: 0.,
            elapsed_s: 0.,
        },
        c,
    )
}
#[test]
fn kernel_zero() {
    let p = uniform_partition(3., 5., 0.).unwrap();
    assert_eq!(
        p,
        BirthPartition {
            surviving: 8.,
            absorbed: 0.
        }
    );
}
#[test]
fn tiny_birth_absorption_is_not_cancelled() {
    let p = uniform_partition(0., 1., 1e-20).unwrap();
    close(p.absorbed, 5e-21, 1e-15);
    assert!(p.absorbed > 0.);
}
#[test]
fn analytic_tau_one() {
    let p = uniform_partition(0., 1., 1.).unwrap();
    close(p.surviving, 1. - (-1f64).exp(), 2e-15);
    close(p.absorbed, (-1f64).exp(), 2e-15);
}
#[test]
fn thick_limit_survival_retained() {
    let p = uniform_partition(0., 1., 1e20).unwrap();
    close(p.surviving, 1e-20, 1e-15);
    assert_eq!(p.absorbed, 1.);
}
#[test]
fn frozen_semigroup() {
    for t in [1e-12, 0.1, 1., 100.] {
        let p = uniform_partition(2., 3., t).unwrap();
        let h = uniform_partition(2., 1.5, t / 2.).unwrap();
        let q = uniform_partition(h.surviving, 1.5, t / 2.).unwrap();
        close(p.surviving, q.surviving, 3e-14);
        close(p.absorbed, h.absorbed + q.absorbed, 3e-14);
    }
}
#[test]
fn invalid_kernel_inputs() {
    for x in [-1., f64::NAN, f64::INFINITY] {
        assert!(uniform_partition(x, 1., 1.).is_err());
        assert!(uniform_partition(1., x, 1.).is_err());
        assert!(uniform_partition(1., 1., x).is_err());
    }
    assert!(uniform_partition(f64::MAX, f64::MAX, 0.).is_err());
}
#[test]
fn zero_birth_matches_legacy() {
    let (s, c) = fixture();
    let a = step(&s, &c, 1e6).unwrap();
    let b = step_fixed_volume_uniform_births(&s, &c, 1e6, &[0., 0.]).unwrap();
    assert_eq!(format!("{:?}", a), format!("{:?}", b.network));
    assert_eq!(b.injected_energy_j_m3, 0.);
}
#[test]
fn shared_photo_energy_and_nuclei_close() {
    let (s, c) = fixture();
    let r = step_fixed_volume_uniform_births(&s, &c, 1e6, &[0.5, 0.3]).unwrap();
    let n = &r.network;
    close(
        r.injected_energy_j_m3,
        (0.5 * 70. + 0.3 * 30.) * EV_J,
        1e-15,
    );
    close(
        n.state.energy_j_m3(&c),
        s.energy_j_m3(&c) + r.injected_energy_j_m3,
        3e-14,
    );
    close(
        s.photon_number() + 0.8,
        n.state.photon_number() + n.budget.photo_events_m3.iter().sum::<f64>(),
        3e-14,
    );
    close(
        s.gas.eos().unwrap().baryons_m3,
        n.state.gas.eos().unwrap().baryons_m3,
        2e-15,
    );
    assert!(n.budget.photo_events_m3.iter().all(|x| *x > 0.));
}
#[test]
fn births_without_photo_survive() {
    let (s, mut c) = fixture();
    c.use_photo = false;
    let r = step_fixed_volume_uniform_births(&s, &c, 1., &[2., 3.]).unwrap();
    assert_eq!(r.network.state.photon_bins[0].number_m3, 4.);
    assert_eq!(r.network.state.photon_bins[1].number_m3, 4.);
    assert_eq!(r.network.budget.photo_events_m3, [0.; 4]);
}
#[test]
fn zero_duration_rejects_nonzero_integrated_births() {
    let (s, c) = fixture();
    assert!(step_fixed_volume_uniform_births(&s, &c, 0., &[1., 0.]).is_err());
    let r = step_fixed_volume_uniform_births(&s, &c, 0., &[0., 0.]).unwrap();
    assert_eq!(format!("{:?}", s), format!("{:?}", r.network.state));
}
#[test]
fn failure_is_transactional() {
    let (s, c) = fixture();
    let before = format!("{:?}", s);
    assert!(step_fixed_volume_uniform_births(&s, &c, 1e12, &[1e12, 1e12]).is_err());
    assert_eq!(before, format!("{:?}", s));
    for b in [
        vec![1.],
        vec![-1., 0.],
        vec![f64::NAN, 0.],
        vec![f64::INFINITY, 0.],
    ] {
        assert!(step_fixed_volume_uniform_births(&s, &c, 1., &b).is_err());
    }
    assert_eq!(before, format!("{:?}", s));
}
#[test]
fn actual_network_birth_exposure_matches_four_absorber_formula() {
    use rei_iso_couple_reference::full_network::SPEED_OF_LIGHT_M_S;
    use rei_iso_couple_reference::{Absorber, AtomicProvider};
    let (mut s, c) = fixture();
    s.photon_bins = vec![PhotonBin {
        energy_ev: 70.,
        number_m3: 0.,
    }];
    let dt = 1e8;
    let born = 0.1;
    let n = &s.gas.nuclei;
    let op = [
        n.density_m3(S::H1Neutral)
            * AtomicProvider::reference()
                .cross_section(Absorber::HI, 70.)
                .unwrap()
            * 1e-4,
        n.density_m3(S::He4Neutral)
            * AtomicProvider::reference()
                .cross_section(Absorber::HeI, 70.)
                .unwrap()
            * 1e-4,
        n.density_m3(S::He4SinglyIonized)
            * AtomicProvider::reference()
                .cross_section(Absorber::HeII, 70.)
                .unwrap()
            * 1e-4,
        n.density_m3(S::DNeutral) * c.deuterium.cross_section_m2(70.).unwrap(),
    ];
    let total = op.iter().sum::<f64>();
    let tau = total * SPEED_OF_LIGHT_M_S * dt;
    assert!(tau > 1e-3);
    let phi = -(-tau).exp_m1() / tau;
    let r = step_fixed_volume_uniform_births(&s, &c, dt, &[born]).unwrap();
    close(r.network.state.photon_number(), born * phi, 3e-14);
    for (i, x) in op.iter().enumerate() {
        close(
            r.network.budget.photo_events_m3[i],
            born * (1. - phi) * x / total,
            3e-13,
        );
    }
    let wrong = born * (-tau).exp();
    assert!((wrong - r.network.state.photon_number()).abs() > born * 1e-4);
}
#[test]
fn d_only_shared_owner() {
    let (mut s, c) = fixture();
    let mut ns = [0.; 13];
    ns[S::DNeutral as usize] = 1000.;
    ns[S::DIonized as usize] = 10.;
    let n = IsotopeNumberState::new(ns).unwrap();
    let p = n.thermal_particle_density_all_thermal_m3().unwrap();
    s.gas = MixtureState {
        nuclei: n,
        thermal_j_m3: 1.5 * KB_J_K * p * 1e4,
    };
    s.photon_bins = vec![PhotonBin {
        energy_ev: 30.,
        number_m3: 0.,
    }];
    let r = step_fixed_volume_uniform_births(&s, &c, 1e6, &[1.]).unwrap();
    let events = r.network.budget.photo_events_m3;
    assert_eq!(&events[..3], &[0.; 3]);
    assert!(events[3] > 0.);
    close(
        r.network.budget.thermal_change_j_m3 + r.network.budget.chemical_change_j_m3,
        r.network.budget.photo_energy_j_m3,
        3e-14,
    );
}
#[test]
fn retry_recomputes_births_once() {
    let (s, c) = fixture();
    let failed = step_fixed_volume_uniform_births(&s, &c, 1e12, &[1e12, 1e12]);
    assert!(failed.is_err());
    let r = step_fixed_volume_uniform_births(&s, &c, 1e6, &[0.5, 0.3]).unwrap();
    assert_eq!(r.injected_number_m3, 0.8);
}
#[test]
fn binding_below_fit_edge_keeps_photons() {
    let (mut s, c) = fixture();
    s.photon_bins = vec![PhotonBin {
        energy_ev: 13.599,
        number_m3: 0.,
    }];
    let r = step_fixed_volume_uniform_births(&s, &c, 1e6, &[1.]).unwrap();
    assert_eq!(r.network.budget.photo_events_m3, [0.; 4]);
    assert_eq!(r.network.state.photon_number(), 1.);
}
#[test]
fn subnormal_tau_scaled_birth_absorption() {
    let t = f64::from_bits(1);
    let p = uniform_partition(0., 1e300, t).unwrap();
    assert!(p.absorbed > 0.);
    close(p.absorbed, (1e300 * t) * 0.5, 1e-15);
}
#[test]
fn very_thick_large_old_does_not_prematurely_underflow() {
    let p = uniform_partition(1e300, 0., 800.).unwrap();
    assert!(p.surviving > 0.);
    close(p.surviving, 3.667874584177687e-48, 2e-13);
}
#[test]
fn old_inventory_survives_birth_dynamic_range() {
    let p = uniform_partition(1., 1e20, 0.1).unwrap();
    let q = uniform_partition(0., 1e20, 0.1).unwrap();
    assert!(p.absorbed >= q.absorbed);
    let p = uniform_partition(1e20, 1., 100.).unwrap();
    close(p.surviving, 1e20 * (-100f64).exp() + 0.01, 2e-15);
}
#[test]
fn nonzero_births_with_all_channels_close() {
    let (s, mut c) = fixture();
    c.use_collisions = true;
    c.use_cx = true;
    c.use_cmb = true;
    let r = step_fixed_volume_uniform_births(&s, &c, 1e5, &[0.01, 0.02]).unwrap();
    close(
        r.network.state.energy_j_m3(&c),
        s.energy_j_m3(&c) + r.injected_energy_j_m3,
        3e-13,
    );
}
#[test]
fn nonzero_births_reject_duplicate_cx() {
    use rei_iso_couple_reference::deuterium_thermal_coupling::CxOwnership;
    let (s, mut c) = fixture();
    c.use_cx = true;
    c.owner = CxOwnership::AtomicRhs;
    assert!(step_fixed_volume_uniform_births(&s, &c, 1., &[1., 1.]).is_err());
}
#[test]
fn downstream_nonfinite_reservoir_failure_is_transactional() {
    let (s, mut c) = fixture();
    c.use_collisions = true;
    c.use_cmb = true;
    c.cmb_temperature_k = 1e300;
    let before = format!("{:?}", s);
    assert!(step_fixed_volume_uniform_births(&s, &c, 1e6, &[0.5, 0.3]).is_err());
    assert_eq!(before, format!("{:?}", s));
}
