use rei_iso_couple_reference::deuterium_charge_exchange::{DhEnergyDefect, Savin2002};
use rei_iso_couple_reference::deuterium_thermal_charge_exchange::{
    KB_EV_K, ThermalCxDefect, ThermalCxState, ThermalCxSystem, savin_provider,
};
use rei_iso_couple_reference::mixture_eos::{
    CxOwner, KB_J_K, MixtureCxReference, MixtureError, MixtureState, temperature_derivative,
};
use rei_iso_couple_reference::{IsotopeNumberState, IsotopeSpecies};

const EV_J: f64 = 1.602_176_634e-19;
const DCHI_EV: f64 = 0.0037; // explicitly manufactured, not source-admitted
const T0_K: f64 = 10_000.0;

fn close(a: f64, b: f64, rel: f64) {
    assert!(a.is_finite() && b.is_finite());
    assert!(
        (a - b).abs() <= rel * a.abs().max(b.abs()).max(1e-300),
        "{a:e} != {b:e}, rel={rel}"
    );
}
fn sample(helium: bool) -> MixtureState {
    let mut n = [0.0; 13];
    n[IsotopeSpecies::H1Neutral as usize] = 1000.0;
    n[IsotopeSpecies::H1Ionized as usize] = 500.0;
    n[IsotopeSpecies::DNeutral as usize] = 50.0;
    n[IsotopeSpecies::DIonized as usize] = 50.0;
    if helium {
        n[IsotopeSpecies::He4Neutral as usize] = 200.0;
        n[IsotopeSpecies::He4SinglyIonized as usize] = 200.0;
        n[IsotopeSpecies::He4DoublyIonized as usize] = 100.0;
    }
    let nt = if helium { 3050.0 } else { 2150.0 };
    MixtureState {
        nuclei: IsotopeNumberState::new(n).unwrap(),
        thermal_j_m3: 1.5 * KB_J_K * nt * T0_K,
    }
}
fn cx(owner: CxOwner) -> MixtureCxReference<'static> {
    MixtureCxReference {
        defect: DhEnergyDefect {
            delta_chi_j: DCHI_EV * EV_J,
            source: "MANUFACTURED_CHI_D_MINUS_CHI_H",
        },
        owner,
        rate_source: Savin2002::SOURCE,
    }
}

#[test]
fn eos_pure_h_d_exact_counts() {
    let e = sample(false).eos().unwrap();
    close(e.baryons_m3, 1700.0, 0.0);
    close(e.heavy_m3, 1600.0, 0.0);
    close(e.free_electrons_m3, 550.0, 0.0);
    close(e.thermal_particles_m3, 2150.0, 0.0);
    close(e.temperature_k, T0_K, 1e-15);
    close(
        e.pressure_j_m3,
        2.0 / 3.0 * sample(false).thermal_j_m3,
        1e-15,
    );
}
#[test]
fn helium_spectator_adds_heat_capacity_and_charge_once() {
    let p = sample(false).eos().unwrap();
    let h = sample(true).eos().unwrap();
    close(h.heavy_m3, 2100.0, 0.0);
    close(h.baryons_m3, 3700.0, 0.0);
    close(h.free_electrons_m3, 950.0, 0.0);
    close(h.thermal_particles_m3, 3050.0, 0.0);
    close(
        h.heat_capacity_j_m3_k / p.heat_capacity_j_m3_k,
        3050.0 / 2150.0,
        1e-14,
    );
}
#[test]
fn cx_forward_preserves_species_invariants_and_ledger() {
    let a = sample(true);
    let e = cx(CxOwner::ThermalSubstep).apply_extent(a, 10.0).unwrap();
    let b = e.state_after.nuclei;
    close(b.density_m3(IsotopeSpecies::H1Neutral), 1010.0, 0.0);
    close(b.density_m3(IsotopeSpecies::H1Ionized), 490.0, 0.0);
    close(b.density_m3(IsotopeSpecies::DNeutral), 40.0, 0.0);
    close(b.density_m3(IsotopeSpecies::DIonized), 60.0, 0.0);
    close(b.density_m3(IsotopeSpecies::He4DoublyIonized), 100.0, 0.0);
    close(e.before.baryons_m3, e.after.baryons_m3, 0.0);
    close(e.before.free_electrons_m3, e.after.free_electrons_m3, 0.0);
    close(
        e.before.thermal_particles_m3,
        e.after.thermal_particles_m3,
        0.0,
    );
    close(e.chemical_delta_j_m3, -e.thermal_delta_j_m3, 0.0);
    assert_eq!(e.photon_delta_j_m3, 0.0);
    assert_eq!(e.cmb_delta_j_m3, 0.0);
    assert_eq!(e.freefree_delta_j_m3, 0.0);
}
#[test]
fn cx_reverse_preserves_invariants() {
    let e = cx(CxOwner::ThermalSubstep)
        .apply_extent(sample(true), -20.0)
        .unwrap();
    close(e.before.baryons_m3, e.after.baryons_m3, 0.0);
    close(e.before.free_electrons_m3, e.after.free_electrons_m3, 0.0);
    assert!(e.thermal_delta_j_m3 > 0.0);
    close(e.chemical_delta_j_m3 + e.thermal_delta_j_m3, 0.0, 1e-14);
}
#[test]
fn helium_reduces_signed_temperature_jump_at_same_t() {
    let a = cx(CxOwner::ThermalSubstep)
        .apply_extent(sample(false), 10.0)
        .unwrap();
    let b = cx(CxOwner::ThermalSubstep)
        .apply_extent(sample(true), 10.0)
        .unwrap();
    let dt0 = a.after.temperature_k - a.before.temperature_k;
    let dth = b.after.temperature_k - b.before.temperature_k;
    assert!(dt0 < 0.0 && dth < 0.0);
    close(dth / dt0, 2150.0 / 3050.0, 3e-8); // subtraction of nearly equal 10k T
}
#[test]
fn pure_hd_reconstruct_parity_original_unmodified_system() {
    let s = sample(false);
    let initial = ThermalCxState {
        h0: 0.001,
        hp: 0.0005,
        d0: 0.00005,
        dp: 0.00005,
        thermal_ev_cm3: s.thermal_j_m3 / (EV_J * 1e6),
    };
    let delta = ThermalCxDefect {
        delta_chi_ev: DCHI_EV,
        source: "MANUFACTURED_CHI",
    };
    let provider = savin_provider();
    let original = ThermalCxSystem::new(initial, delta, &provider).unwrap();
    let z = 10.0 / 1000.0; // original scale = max(H0,..)=0.001 cm-3; xi_m3 = 10
    let (state, xi, t, chemical) = original.reconstruct(z);
    let ev = cx(CxOwner::ThermalSubstep).apply_extent(s, 10.0).unwrap();
    close(xi * 1e6, 10.0, 1e-14);
    close(
        state.h0 * 1e6,
        ev.state_after.nuclei.density_m3(IsotopeSpecies::H1Neutral),
        1e-14,
    );
    close(
        state.dp * 1e6,
        ev.state_after.nuclei.density_m3(IsotopeSpecies::DIonized),
        1e-14,
    );
    close(t.unwrap(), ev.after.temperature_k, 3e-15);
    close(chemical * EV_J * 1e6, ev.chemical_delta_j_m3, 2e-14);
    close(KB_EV_K * EV_J, KB_J_K, 1e-15);
}
#[test]
fn savin_rhs_independent_spectator_same_extent_rate() {
    let r0 = cx(CxOwner::ThermalSubstep)
        .savin_rhs(sample(false))
        .unwrap();
    let r1 = cx(CxOwner::ThermalSubstep).savin_rhs(sample(true)).unwrap();
    close(r0.extent_rate_m3_s, r1.extent_rate_m3_s, 1e-14);
    close(
        r1.temperature_rate_k_s / r0.temperature_rate_k_s,
        2150.0 / 3050.0,
        1e-13,
    );
    close(r1.chemical_power_j_m3_s, -r1.thermal_power_j_m3_s, 0.0);
    assert_eq!(r1.conserved_electron_rate_m3_s, 0.0);
}
#[test]
fn exact_savin_rhs_parity_original_thermal_system_at_zero_extent() {
    let s = sample(false);
    let initial = ThermalCxState {
        h0: 0.001,
        hp: 0.0005,
        d0: 0.00005,
        dp: 0.00005,
        thermal_ev_cm3: s.thermal_j_m3 / (EV_J * 1e6),
    };
    let provider = savin_provider();
    let sys = ThermalCxSystem::new(
        initial,
        ThermalCxDefect {
            delta_chi_ev: DCHI_EV,
            source: "MANUFACTURED",
        },
        &provider,
    )
    .unwrap();
    let original_cm3_s = sys.field(0.0).unwrap() * 0.001;
    let ours = cx(CxOwner::ThermalSubstep).savin_rhs(s).unwrap();
    close(original_cm3_s * 1e6, ours.extent_rate_m3_s, 2e-14);
}
#[test]
fn original_temperature_bounds_fail_closed() {
    assert!(Savin2002::rates(2.7).is_ok());
    assert!(Savin2002::rates(200_000.0).is_ok());
    assert!(Savin2002::rates(2.69).is_err());
    assert!(Savin2002::rates(200_000.1).is_err());
    let s = MixtureState {
        nuclei: sample(false).nuclei,
        thermal_j_m3: 1.5 * KB_J_K * 2150.0 * 200_001.0,
    };
    assert_eq!(
        cx(CxOwner::ThermalSubstep).savin_rhs(s).unwrap_err(),
        MixtureError::UnsupportedTemperature
    );
}
#[test]
fn cx_requires_one_owner_and_bound_source() {
    assert_eq!(
        cx(CxOwner::AtomicRhs)
            .signed_extent_bounds(sample(true))
            .unwrap_err(),
        MixtureError::UnsupportedOwner
    );
    let c = MixtureCxReference {
        rate_source: "",
        ..cx(CxOwner::ThermalSubstep)
    };
    assert_eq!(
        c.signed_extent_bounds(sample(true)).unwrap_err(),
        MixtureError::MissingSource
    );
    let c = MixtureCxReference {
        rate_source: "UNBOUND_FAKE_RATE",
        ..cx(CxOwner::ThermalSubstep)
    };
    assert_eq!(
        c.signed_extent_bounds(sample(true)).unwrap_err(),
        MixtureError::RateSourceMismatch
    );
    let c = MixtureCxReference {
        defect: DhEnergyDefect {
            delta_chi_j: f64::NAN,
            source: "synthetic",
        },
        ..cx(CxOwner::ThermalSubstep)
    };
    assert_eq!(
        c.signed_extent_bounds(sample(true)).unwrap_err(),
        MixtureError::InvalidDefect
    );
}
#[test]
fn event_extent_strict_without_clipping_and_input_immutable() {
    let s = sample(true);
    let c = cx(CxOwner::ThermalSubstep);
    let [min, max] = c.signed_extent_bounds(s).unwrap();
    assert_eq!([min, max], [-50.0, 50.0]);
    assert_eq!(
        c.apply_extent(s, 50.001).unwrap_err(),
        MixtureError::ExtentOutsideDomain
    );
    assert_eq!(
        c.apply_extent(s, -50.001).unwrap_err(),
        MixtureError::ExtentOutsideDomain
    );
    assert_eq!(s.nuclei.density_m3(IsotopeSpecies::DNeutral), 50.0);
    assert!(c.apply_extent(s, 50.0).is_ok());
}
#[test]
fn rejects_negative_thermal_energy_instead_of_projecting() {
    let s = sample(false);
    let bad = MixtureCxReference {
        defect: DhEnergyDefect {
            delta_chi_j: 2.0 * s.thermal_j_m3,
            source: "MANUFACTURED_LARGE_ENERGY",
        },
        ..cx(CxOwner::ThermalSubstep)
    };
    assert_eq!(
        bad.apply_extent(s, 1.0).unwrap_err(),
        MixtureError::NegativeThermal
    );
}
#[test]
fn electron_closure_one_owner_and_stale_value_rejected() {
    let s = sample(true);
    let ne = s.eos().unwrap().free_electrons_m3;
    s.validate_reported_electrons(ne).unwrap();
    assert_eq!(
        s.validate_reported_electrons(ne + 1.0).unwrap_err(),
        MixtureError::InvalidElectronOwner
    );
}
#[test]
fn all_13_isotope_nuclear_and_charge_weights_included() {
    let mut n = [1.0; 13];
    n[IsotopeSpecies::He4DoublyIonized as usize] = 2.0;
    let state = MixtureState {
        nuclei: IsotopeNumberState::new(n).unwrap(),
        thermal_j_m3: 1e-16,
    };
    let m = state.eos().unwrap();
    assert_eq!(m.baryons_m3, 38.0);
    assert_eq!(m.free_electrons_m3, 11.0);
    assert_eq!(m.heavy_m3, 14.0);
    assert_eq!(m.thermal_particles_m3, 25.0);
}
#[test]
fn expanding_gas_temperature_equation_has_correct_adiabatic_and_particle_term() {
    let e = sample(true).eos().unwrap();
    let theta = 0.0001;
    let td = temperature_derivative(&e, theta, 0.0, 0.0, 0.0, DCHI_EV * EV_J).unwrap();
    close(td, -(2.0 / 3.0) * theta * e.temperature_k, 1e-14);
    let extra = 30.0;
    let td2 = temperature_derivative(&e, 0.0, 0.0, extra, 0.0, DCHI_EV * EV_J).unwrap();
    close(
        td2,
        -e.temperature_k * extra / e.thermal_particles_m3,
        1e-14,
    );
}
#[test]
fn pure_cx_temperature_rhs_matches_fixed_volume_formula() {
    let e = sample(true).eos().unwrap();
    let rate = 10.0;
    let td = temperature_derivative(&e, 0.0, 0.0, 0.0, rate, DCHI_EV * EV_J).unwrap();
    close(td, -(DCHI_EV * EV_J) * rate / e.heat_capacity_j_m3_k, 1e-14);
}
#[test]
fn helium_only_gas_zero_cx_with_valid_eos() {
    let mut n = [0.0; 13];
    n[IsotopeSpecies::He4DoublyIonized as usize] = 100.0;
    let s = MixtureState {
        nuclei: IsotopeNumberState::new(n).unwrap(),
        thermal_j_m3: 1.5 * KB_J_K * 300.0 * T0_K,
    };
    assert_eq!(s.eos().unwrap().free_electrons_m3, 200.0);
    let e = cx(CxOwner::ThermalSubstep).apply_extent(s, 0.0).unwrap();
    close(e.after.temperature_k, T0_K, 1e-14);
    assert_eq!(
        cx(CxOwner::ThermalSubstep)
            .savin_rhs(s)
            .unwrap()
            .extent_rate_m3_s,
        0.0
    );
}
#[test]
fn zero_energy_defect_preserves_thermal_energy() {
    let c = MixtureCxReference {
        defect: DhEnergyDefect {
            delta_chi_j: 0.0,
            source: "ZERO_DEFECT_TEST",
        },
        ..cx(CxOwner::ThermalSubstep)
    };
    let s = sample(true);
    let e = c.apply_extent(s, 10.0).unwrap();
    assert_eq!(e.chemical_delta_j_m3, 0.0);
    assert_eq!(e.state_after.thermal_j_m3, s.thermal_j_m3);
}

#[test]
fn source_domain_crossing_is_rejected_without_clipping() {
    let s = sample(false);
    let bad = MixtureCxReference {
        defect: DhEnergyDefect {
            delta_chi_j: s.thermal_j_m3,
            source: "MANUFACTURED_DOMAIN_EVENT",
        },
        ..cx(CxOwner::ThermalSubstep)
    };
    assert_eq!(
        bad.apply_extent(s, 1.0).unwrap_err(),
        MixtureError::UnsupportedTemperature
    );
}

#[test]
fn deterministic_256_state_extents_stoichiometry_and_energy() {
    let c = cx(CxOwner::ThermalSubstep);
    let mut tested = 0;
    for i in 0..16 {
        for j in 0..16 {
            let mut n = [0.0; 13];
            n[IsotopeSpecies::H1Neutral as usize] = 400.0 + i as f64;
            n[IsotopeSpecies::H1Ionized as usize] = 700.0 + j as f64;
            n[IsotopeSpecies::DNeutral as usize] = 40.0 + i as f64;
            n[IsotopeSpecies::DIonized as usize] = 30.0 + j as f64;
            n[IsotopeSpecies::He4Neutral as usize] = i as f64 * 6.0;
            n[IsotopeSpecies::He4SinglyIonized as usize] = j as f64 * 6.0;
            n[IsotopeSpecies::He4DoublyIonized as usize] = 30.0;
            n[IsotopeSpecies::He3Neutral as usize] = 2.0;
            n[IsotopeSpecies::TNeutral as usize] = 1.0;
            let state = IsotopeNumberState::new(n).unwrap();
            let n_th = state.thermal_particle_density_all_thermal_m3().unwrap();
            let s = MixtureState {
                nuclei: state,
                thermal_j_m3: 1.5 * KB_J_K * n_th * T0_K,
            };
            let extent = (i as f64 - 7.5) / 4.0;
            let after = c.apply_extent(s, extent).unwrap();
            close(after.before.baryons_m3, after.after.baryons_m3, 2e-15);
            close(
                after.before.free_electrons_m3,
                after.after.free_electrons_m3,
                2e-15,
            );
            close(
                after.before.thermal_particles_m3,
                after.after.thermal_particles_m3,
                2e-15,
            );
            close(after.chemical_delta_j_m3, -after.thermal_delta_j_m3, 0.0);
            tested += 1;
        }
    }
    assert_eq!(tested, 256);
}
