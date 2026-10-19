//! P2 bounded model: original PR150 Grackle/Verner/Savin rate modules, H/He/D
//! shared photons, fixed proper volume; not a native universe history.
use rei_iso_couple_reference::deuterium_atomic::{DAtomicProvider, DChargeExchange, d_atomic_rhs};
use rei_iso_couple_reference::deuterium_thermal_coupling::CxOwnership;
use rei_iso_couple_reference::full_network::{
    FullState, NetworkConfig, NetworkError, PhotonBin, run_substeps, step,
};
use rei_iso_couple_reference::isotope_state::{IsotopeNumberState, IsotopeSpecies as Sp};
use rei_iso_couple_reference::mixture_eos::{KB_J_K, MixtureState};
use rei_iso_couple_reference::{
    HHeModel,
    atomic_provider::{Absorber, AtomicProvider},
};
const SOURCE: &str = "MANUFACTURED_INITIAL_PHOTON_BINS_NOT_MD14";
const THRESHOLD_SOURCE: &str = "P2_MANUFACTURED_D_BOUND_THRESHOLD";
fn provider() -> DAtomicProvider {
    let h = HHeModel::controlled_fixture().threshold_ev[0];
    DAtomicProvider::new(h, h + 0.0037, THRESHOLD_SOURCE).unwrap()
}
fn state(he4: f64, other: f64) -> FullState {
    let mut n = [0.0; 13];
    n[Sp::H1Neutral as usize] = 1000.0;
    n[Sp::H1Ionized as usize] = 900.0;
    n[Sp::He4Neutral as usize] = he4;
    n[Sp::He4SinglyIonized as usize] = he4 / 3.0;
    n[Sp::He4DoublyIonized as usize] = he4 / 5.0;
    n[Sp::DNeutral as usize] = 25.0;
    n[Sp::DIonized as usize] = 5.0;
    n[Sp::He3SinglyIonized as usize] = other;
    let nuclei = IsotopeNumberState::new(n).unwrap();
    let nth = nuclei.thermal_particle_density_all_thermal_m3().unwrap();
    FullState {
        gas: MixtureState {
            nuclei,
            thermal_j_m3: 1.5 * KB_J_K * nth * 10_000.0,
        },
        photon_bins: vec![
            PhotonBin {
                energy_ev: 70.0,
                number_m3: 120.0,
            },
            PhotonBin {
                energy_ev: 30.0,
                number_m3: 70.0,
            },
        ],
        escaped_j_m3: 0.0,
        cmb_reservoir_j_m3: 0.0,
        elapsed_s: 0.0,
    }
}
fn cfg() -> NetworkConfig {
    NetworkConfig::source_bound(provider(), SOURCE)
}
fn approx(a: f64, b: f64, rtol: f64) {
    let den = a.abs().max(b.abs()).max(1e-36);
    assert!(
        (a - b).abs() <= rtol * den,
        "{a:e} != {b:e}; relative={:e}",
        (a - b).abs() / den
    );
}
fn energy_check(s: &FullState, q: &FullState, c: &NetworkConfig) {
    approx(s.energy_j_m3(c), q.energy_j_m3(c), 1e-11);
    let e0 = s.gas.eos().unwrap();
    let e1 = q.gas.eos().unwrap();
    approx(e0.baryons_m3, e1.baryons_m3, 1e-12);
    assert!((q.gas.nuclei.density_m3(Sp::H1Neutral) >= 0.0) && q.elapsed_s >= 0.0);
}
#[test]
fn imported_source_thresholds_are_true_owner_constants() {
    let h = HHeModel::controlled_fixture();
    assert_eq!(h.threshold_ev[0], provider().chi_h_ev());
    assert!(h.threshold_ev[1] > 24.58 && h.threshold_ev[2] > 54.41);
    assert_eq!(
        AtomicProvider::reference()
            .cross_section(Absorber::HI, 13.0)
            .unwrap(),
        0.0
    );
}
#[test]
fn manufactured_two_bin_photon_pool_one_absorber_per_photon() {
    let s = state(110.0, 0.0);
    let mut c = cfg();
    c.use_collisions = false;
    c.use_cx = false;
    c.use_cmb = false;
    let r = step(&s, &c, 1e8).unwrap();
    let dn = s.photon_number() - r.state.photon_number();
    let sum = r.budget.photo_events_m3.iter().sum::<f64>();
    approx(dn, sum, 1e-12);
    assert!(sum > 0.0 && sum < s.photon_number());
    assert!(r.budget.photo_events_m3.iter().all(|&x| x > 0.0));
    energy_check(&s, &r.state, &c);
    approx(
        r.budget.thermal_change_j_m3 + r.budget.chemical_change_j_m3,
        r.budget.photo_energy_j_m3,
        1e-12,
    );
}
#[test]
fn lower_energy_has_no_heii_or_d_if_subthreshold() {
    let mut s = state(110.0, 0.0);
    s.photon_bins = vec![PhotonBin {
        energy_ev: 13.601,
        number_m3: 100.0,
    }];
    let mut c = cfg();
    c.use_collisions = false;
    c.use_cx = false;
    c.use_cmb = false;
    let r = step(&s, &c, 1e8).unwrap();
    assert!(r.budget.photo_events_m3[0] > 0.0);
    assert_eq!(r.budget.photo_events_m3[1], 0.0);
    assert_eq!(r.budget.photo_events_m3[2], 0.0);
    assert_eq!(r.budget.photo_events_m3[3], 0.0);
    energy_check(&s, &r.state, &c);
}
#[test]
fn collisional_grackle_and_native_d_ledger_share_electrons() {
    let mut s = state(135.0, 8.0);
    s.photon_bins.clear();
    let mut c = cfg();
    c.use_photo = false;
    c.use_cx = false;
    c.use_cmb = false;
    let t = s.gas.eos().unwrap().temperature_k;
    let p = c
        .deuterium
        .photo_input_from_bound_rates(0.0, 0.0, SOURCE)
        .unwrap();
    let d = d_atomic_rhs(c.deuterium, &s.gas.nuclei, t, &p, DChargeExchange::Disabled).unwrap();
    approx(
        d.electron_density_m3,
        s.gas.eos().unwrap().free_electrons_m3,
        1e-15,
    );
    let r = step(&s, &c, 1e8).unwrap();
    assert_eq!(r.budget.photo_energy_j_m3, 0.0);
    assert!(r.budget.ci_events_m3[0] >= 0.0 && r.budget.rr_events_m3[3] > 0.0);
    approx(r.budget.ci_events_m3[3] / 1e8, d.ci_events_m3_s, 3e-12);
    approx(r.budget.rr_events_m3[3] / 1e8, d.rr_events_m3_s, 3e-12);
    energy_check(&s, &r.state, &c);
}
#[test]
fn finite_time_cx_owner_exact_original_p1_limit() {
    let mut s = state(200.0, 0.0);
    s.photon_bins.clear();
    let mut c = cfg();
    c.use_photo = false;
    c.use_collisions = false;
    c.use_cmb = false;
    let direct = rei_iso_couple_reference::mixture_coupling::MixtureCxComponent::new(
        c.deuterium,
        CxOwnership::ThermalSubstep,
    )
    .advance_cx_only(s.gas, 1e8, c.cx_controls)
    .unwrap();
    let r = step(&s, &c, 1e8).unwrap();
    approx(r.budget.cx_signed_m3, direct.extent_m3, 1e-12);
    approx(
        r.state.gas.thermal_j_m3,
        direct.final_state.thermal_j_m3,
        1e-13,
    );
    energy_check(&s, &r.state, &c);
}
#[test]
fn atomic_rhs_owner_rejects_double_cx() {
    let s = state(200.0, 0.0);
    let mut c = cfg();
    c.owner = CxOwnership::AtomicRhs;
    assert_eq!(
        step(&s, &c, 1e8).unwrap_err(),
        NetworkError::OwnershipConflict
    );
}
#[test]
fn cmb_reservoir_and_freefree_are_global_single_owners() {
    let mut s = state(155.0, 12.0);
    s.photon_bins.clear();
    let mut c = cfg();
    c.use_cx = false;
    c.use_photo = false;
    c.use_cmb = true;
    c.cmb_temperature_k = 2000.0;
    let r = step(&s, &c, 1e8).unwrap();
    assert!(r.state.cmb_reservoir_j_m3 > 0.0);
    assert!(r.budget.freefree_integrated_j_m3 > 0.0);
    assert!(r.state.escaped_j_m3 > 0.0);
    energy_check(&s, &r.state, &c);
}
#[test]
fn no_photon_emission_in_case_a_is_reported_as_escape() {
    let mut s = state(155.0, 0.0);
    s.photon_bins.clear();
    let mut c = cfg();
    c.use_photo = false;
    c.use_cx = false;
    c.use_cmb = false;
    let r = step(&s, &c, 1e8).unwrap();
    assert_eq!(r.state.photon_number(), 0.0);
    assert!(r.state.escaped_j_m3 > 0.0);
    energy_check(&s, &r.state, &c);
}
#[test]
fn full_hhe_d_savin_photo_and_collisional_step_conserves() {
    let s = state(150.0, 13.0);
    let c = cfg();
    let r = step(&s, &c, 1e7).unwrap();
    assert!(r.budget.photo_events_m3.iter().sum::<f64>() > 0.0);
    assert!(r.budget.cx_signed_m3 != 0.0);
    assert!(r.budget.rr_events_m3.iter().sum::<f64>() > 0.0);
    energy_check(&s, &r.state, &c);
}
#[test]
fn source_labels_and_rate_domains_fail_closed() {
    let s = state(0.0, 0.0);
    let mut c = cfg();
    c.photon_source = "";
    assert_eq!(step(&s, &c, 1e8).unwrap_err(), NetworkError::SourceMismatch);
    let c = cfg();
    assert_eq!(step(&s, &c, -1.0).unwrap_err(), NetworkError::InvalidInput);
    let mut wrong = s.clone();
    wrong.photon_bins[0].energy_ev = 100_000.0;
    assert_eq!(
        step(&wrong, &c, 1e8).unwrap_err(),
        NetworkError::InputOutsideDomain
    );
}
#[test]
fn no_clipping_overdrawn_photon_step_is_rejected() {
    let mut s = state(0.0, 0.0);
    s.photon_bins = vec![PhotonBin {
        energy_ev: 70.0,
        number_m3: 1e9,
    }];
    let mut c = cfg();
    c.use_collisions = false;
    c.use_cx = false;
    c.use_cmb = false;
    assert_eq!(
        step(&s, &c, 1e13).unwrap_err(),
        NetworkError::NegativePopulation
    );
    // Caller data is by-reference immutable despite the rejected trial.
    assert_eq!(s.photon_bins[0].number_m3, 1e9);
}
#[test]
fn helium_spectators_affect_cv_and_charge_once() {
    let a = state(0.0, 0.0);
    let b = state(300.0, 10.0);
    let ea = a.gas.eos().unwrap();
    let eb = b.gas.eos().unwrap();
    assert!(eb.thermal_particles_m3 > ea.thermal_particles_m3);
    assert!(eb.free_electrons_m3 > ea.free_electrons_m3);
    assert!(eb.heat_capacity_j_m3_k > ea.heat_capacity_j_m3_k);
}
#[test]
fn source_off_zero_photons_does_not_produce_photon_budget() {
    let mut s = state(150.0, 0.0);
    s.photon_bins.clear();
    let c = cfg();
    let r = step(&s, &c, 1e7).unwrap();
    assert_eq!(r.budget.photo_events_m3, [0.0; 4]);
    assert_eq!(r.state.photon_number(), 0.0);
    energy_check(&s, &r.state, &c);
}
#[test]
fn finite_time_refinement_and_energy_are_bounded() {
    let s = state(120.0, 0.0);
    let c = cfg();
    let coarse = run_substeps(&s, &c, 4e7, 1).unwrap();
    let medium = run_substeps(&s, &c, 4e7, 4).unwrap();
    let fine = run_substeps(&s, &c, 4e7, 16).unwrap();
    let reference = run_substeps(&s, &c, 4e7, 128).unwrap();
    let species = Sp::H1Ionized;
    let d = |x: &rei_iso_couple_reference::full_network::NetworkResult| {
        x.state.gas.nuclei.density_m3(species)
    };
    assert!((d(&fine) - d(&reference)).abs() < (d(&coarse) - d(&reference)).abs());
    assert!((d(&medium) - d(&reference)).abs() < (d(&coarse) - d(&reference)).abs());
    energy_check(&s, &reference.state, &c);
}
#[test]
fn exact_zero_step_is_identity() {
    let s = state(100.0, 0.0);
    let c = cfg();
    let r = step(&s, &c, 0.0).unwrap();
    assert_eq!(s.photon_bins, r.state.photon_bins);
    assert_eq!(s.gas.thermal_j_m3, r.state.gas.thermal_j_m3);
}
#[test]
fn pure_hhe_point_rates_match_original_igm_thermal_source() {
    use rei_iso_couple_reference::igm_state::IgmGasState;
    use rei_iso_couple_reference::igm_thermal::{IgmPhotoInput, igm_point_rhs};
    let mut s = state(180.0, 0.0);
    let mut n = [0.0; 13];
    for sp in [
        Sp::H1Neutral,
        Sp::H1Ionized,
        Sp::He4Neutral,
        Sp::He4SinglyIonized,
        Sp::He4DoublyIonized,
    ] {
        n[sp as usize] = s.gas.nuclei.density_m3(sp);
    }
    let nh = n[Sp::H1Neutral as usize] + n[Sp::H1Ionized as usize];
    let nhe = n[Sp::He4Neutral as usize]
        + n[Sp::He4SinglyIonized as usize]
        + n[Sp::He4DoublyIonized as usize];
    let frac = [
        n[Sp::H1Ionized as usize] / nh,
        n[Sp::He4SinglyIonized as usize] / nhe,
        n[Sp::He4DoublyIonized as usize] / nhe,
    ];
    let nuclei = IsotopeNumberState::new(n).unwrap();
    s.gas = MixtureState {
        nuclei,
        thermal_j_m3: 1.5
            * KB_J_K
            * (nh + nhe + nuclei.moments().unwrap().neutral_free_electron_density_m3)
            * 10000.0,
    };
    s.photon_bins.clear();
    let eig = IgmGasState {
        fractions: frac,
        w_erg_per_h: s.gas.thermal_j_m3 * 10.0 / (nh * 1e-6),
    };
    let orig = igm_point_rhs(
        &eig,
        nh * 1e-6,
        nhe * 1e-6,
        0.0,
        20.0,
        IgmPhotoInput::default(),
    )
    .unwrap();
    let mut c = cfg();
    c.use_photo = false;
    c.use_cx = false;
    c.use_cmb = true;
    c.cmb_temperature_k = 20.0;
    let dt = 1e7;
    let stepper = step(&s, &c, dt).unwrap();
    // Compare source-integrated transaction, not a tiny finite difference of
    // the much larger initial thermal inventory (which loses digits).
    approx(
        stepper.budget.thermal_change_j_m3 / dt,
        orig.thermal_micro_erg_cm3_s * 0.1,
        2e-13,
    );
    approx(
        stepper.budget.escape_change_j_m3 / dt,
        orig.escape_erg_cm3_s * 0.1,
        1e-11,
    );
    approx(
        stepper.budget.ci_events_m3[0] / dt,
        orig.ci_events_cm3_s[0] * 1e6,
        1e-11,
    );
    approx(
        stepper.budget.rr_events_m3[2] / dt,
        orig.rr_events_cm3_s[2] * 1e6,
        1e-11,
    );
    approx(
        stepper.budget.freefree_integrated_j_m3 / dt,
        orig.freefree_thermal_sink_erg_cm3_s * 0.1,
        1e-11,
    );
    energy_check(&s, &stepper.state, &c);
}
#[test]
fn all_external_reservoir_events_cancel_per_step() {
    for (on_photo, on_collisions, on_cx, on_cmb) in [
        (true, true, true, true),
        (true, false, false, false),
        (false, true, false, true),
        (false, false, true, false),
        (false, false, false, true),
    ] {
        let s = state(250.0, 4.0);
        let mut c = cfg();
        c.use_photo = on_photo;
        c.use_collisions = on_collisions;
        c.use_cx = on_cx;
        c.use_cmb = on_cmb;
        let r = step(&s, &c, 1e7).unwrap();
        let q = r.budget;
        let defect = q.thermal_change_j_m3
            + q.chemical_change_j_m3
            + q.escape_change_j_m3
            + q.cmb_change_j_m3
            - q.photo_energy_j_m3;
        let mag = q.thermal_change_j_m3.abs()
            + q.chemical_change_j_m3.abs()
            + q.escape_change_j_m3.abs()
            + q.cmb_change_j_m3.abs()
            + q.photo_energy_j_m3.abs();
        assert!(
            defect.abs() <= 2e-11 * mag.max(1e-40),
            "owner defect={defect:e} mag={mag:e}"
        );
        energy_check(&s, &r.state, &c);
    }
}
#[test]
fn photon_bounded_capacity_guard_no_unlimited_allocations() {
    let mut s = state(0.0, 0.0);
    s.photon_bins = vec![
        PhotonBin {
            energy_ev: 70.0,
            number_m3: 1.0
        };
        65
    ];
    assert_eq!(
        step(&s, &cfg(), 1e7).unwrap_err(),
        NetworkError::InputOutsideDomain
    );
}
#[test]
fn source_fit_temperature_guard_never_extrapolates() {
    let mut s = state(0.0, 0.0);
    s.gas.thermal_j_m3 *= 23.0;
    assert_eq!(
        step(&s, &cfg(), 1e7).unwrap_err(),
        NetworkError::TemperatureOutsideSource
    );
}
#[test]
fn passive_he3_electrons_are_not_evolved_by_active_atomic_channels() {
    let s = state(200.0, 71.0);
    let r = step(&s, &cfg(), 1e7).unwrap();
    for i in [
        Sp::He3Neutral,
        Sp::He3SinglyIonized,
        Sp::He3DoublyIonized,
        Sp::TNeutral,
        Sp::TIonized,
    ] {
        assert_eq!(
            s.gas.nuclei.density_m3(i).to_bits(),
            r.state.gas.nuclei.density_m3(i).to_bits()
        );
    }
    energy_check(&s, &r.state, &cfg());
}
