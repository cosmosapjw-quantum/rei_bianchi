use rei_iso_couple_reference::deuterium_atomic::DAtomicProvider;
use rei_iso_couple_reference::deuterium_charge_exchange::{DhState, Savin2002};
use rei_iso_couple_reference::deuterium_thermal_charge_exchange::{
    ThermalCxControls, ThermalCxStatus, integrate_si, savin_provider,
};
use rei_iso_couple_reference::deuterium_thermal_coupling::{CxOwnership, ThermalCxComponent};
use rei_iso_couple_reference::isotope_state::{IsotopeNumberState, IsotopeSpecies as Sp};
use rei_iso_couple_reference::mixture_coupling::{CoupleError, MixtureCxComponent, StepControls};
use rei_iso_couple_reference::mixture_eos::{CxOwner, KB_J_K, MixtureCxReference, MixtureState};

const SOURCE: &str = "MANUFACTURED_0_0037_EV_TEST_NOT_PHYSICAL_ADMISSION";
fn provider() -> DAtomicProvider {
    DAtomicProvider::new(13.598_434_599_702, 13.602_134_599_702, SOURCE).unwrap()
}
fn state(he: f64) -> MixtureState {
    let mut n = [0.0; 13];
    n[Sp::H1Neutral as usize] = 1000.0;
    n[Sp::H1Ionized as usize] = 900.0;
    n[Sp::DNeutral as usize] = 25.0;
    n[Sp::DIonized as usize] = 5.0;
    n[Sp::He4Neutral as usize] = he;
    n[Sp::He4SinglyIonized as usize] = he / 5.0;
    n[Sp::He4DoublyIonized as usize] = he / 7.0;
    let nuclei = IsotopeNumberState::new(n).unwrap();
    let nth = nuclei.thermal_particle_density_all_thermal_m3().unwrap();
    MixtureState {
        nuclei,
        thermal_j_m3: 1.5 * KB_J_K * nth * 10000.0,
    }
}
fn component(owner: CxOwnership) -> MixtureCxComponent {
    MixtureCxComponent::new(provider(), owner)
}
fn approx(a: f64, b: f64, tol: f64) {
    assert!(
        (a - b).abs() <= tol * (1.0 + a.abs().max(b.abs())),
        "a={a:.17e} b={b:.17e} tol={tol}"
    );
}

#[test]
fn source_identity_from_real_provider() {
    let p = provider();
    assert_eq!(p.threshold_source(), SOURCE);
    assert_eq!(p.defect().source, SOURCE);
    let diff = (p.chi_d_ev() - p.chi_h_ev()) * 1.602_176_634e-19;
    approx(p.defect().delta_chi_j, diff, 1e-16);
}
#[test]
fn atomic_rhs_owner_exclusive() {
    let s = state(300.0);
    let p = provider();
    let photo = p.photo_input(&[], "SOURCE_OFF").unwrap();
    let a = component(CxOwnership::AtomicRhs)
        .atomic_rhs(&s, &photo)
        .unwrap()
        .instantaneous_atomic_rhs;
    let b = component(CxOwnership::ThermalSubstep)
        .atomic_rhs(&s, &photo)
        .unwrap()
        .instantaneous_atomic_rhs;
    assert!(a.cx_forward_events_m3_s > 0.0);
    assert!(a.cx_reverse_events_m3_s > 0.0);
    assert_eq!(b.cx_forward_events_m3_s, 0.0);
    assert_eq!(b.cx_reverse_events_m3_s, 0.0);
    // Non-CX source term and each other event ledger are identical.
    for j in 0..4 {
        assert_eq!(
            a.channel_energy[j].thermal.to_bits(),
            b.channel_energy[j].thermal.to_bits()
        );
    }
    approx(a.energy.residual(), 0.0, 1e-16);
    approx(b.energy.residual(), 0.0, 1e-16);
    assert_eq!(
        a.electron_density_m3.to_bits(),
        b.electron_density_m3.to_bits()
    );
    assert_eq!(
        a.thermal_particle_density_m3.to_bits(),
        b.thermal_particle_density_m3.to_bits()
    );
}
#[test]
fn owned_atomic_mode_denies_second_cx_integrator() {
    let s = state(230.0);
    let q = component(CxOwnership::AtomicRhs).advance_cx_only(s, 1e9, StepControls::default());
    assert!(matches!(q, Err(CoupleError::OwnershipConflict)));
}
#[test]
fn mixture_positive_conservative_time_evolution() {
    let before = state(400.0);
    let q = component(CxOwnership::ThermalSubstep)
        .advance_cx_only(before, 3e10, StepControls::default())
        .unwrap();
    assert!(q.counts.accepted_steps >= 1);
    let after = q.final_state.eos().unwrap();
    let init = before.eos().unwrap();
    approx(after.baryons_m3, init.baryons_m3, 1e-12);
    approx(after.free_electrons_m3, init.free_electrons_m3, 1e-12);
    approx(after.thermal_particles_m3, init.thermal_particles_m3, 1e-12);
    approx(q.delta_chemical_j_m3 + q.delta_thermal_j_m3, 0.0, 1e-30);
    approx(
        q.delta_thermal_j_m3,
        q.final_state.thermal_j_m3 - before.thermal_j_m3,
        1e-16,
    );
    assert_eq!(q.photon_j_m3, 0.0);
    assert_eq!(q.cmb_j_m3, 0.0);
    assert_eq!(q.freefree_j_m3, 0.0);
    assert!(q.accepted_s == q.requested_s);
    assert!(q.defect_source == SOURCE && q.rate_source == Savin2002::SOURCE);
    for sp in Sp::ALL {
        assert!(q.final_state.nuclei.density_m3(sp) >= 0.0);
    }
    assert!((Savin2002::MINIMUM_K..=Savin2002::MAXIMUM_K).contains(&after.temperature_k));
}
#[test]
fn helium_changes_cv_but_not_initial_rxn_rate() {
    let a = state(0.0);
    let b = state(600.0);
    let refmap = MixtureCxReference {
        defect: provider().defect(),
        owner: CxOwner::ThermalSubstep,
        rate_source: Savin2002::SOURCE,
    };
    let ra = refmap.savin_rhs(a).unwrap();
    let rb = refmap.savin_rhs(b).unwrap();
    approx(ra.extent_rate_m3_s, rb.extent_rate_m3_s, 1e-14);
    let aa = component(CxOwnership::ThermalSubstep)
        .advance_cx_only(a, 1e10, StepControls::default())
        .unwrap();
    let bb = component(CxOwnership::ThermalSubstep)
        .advance_cx_only(b, 1e10, StepControls::default())
        .unwrap();
    let dt_a = aa.final_state.eos().unwrap().temperature_k - 1e4;
    let dt_b = bb.final_state.eos().unwrap().temperature_k - 1e4;
    assert!(dt_b.abs() < dt_a.abs());
}
#[test]
fn direct_small_time_matches_savin_source_rhs() {
    let s = state(270.0);
    let refmap = MixtureCxReference {
        defect: provider().defect(),
        owner: CxOwner::ThermalSubstep,
        rate_source: Savin2002::SOURCE,
    };
    let rhs = refmap.savin_rhs(s).unwrap();
    let out = component(CxOwnership::ThermalSubstep)
        .advance_cx_only(s, 1e5, StepControls::default())
        .unwrap();
    let derivative = out.extent_m3 / 1e5;
    let relative =
        (derivative - rhs.extent_rate_m3_s).abs() / rhs.extent_rate_m3_s.abs().max(1e-30);
    assert!(
        relative < 2e-4,
        "relative={relative} derivative={derivative} rhs={}",
        rhs.extent_rate_m3_s
    );
}
#[test]
fn pure_hd_limit_agrees_with_original_native_time_integrator() {
    let initial = state(0.0);
    let n = initial.nuclei;
    let dh = DhState {
        h0_m3: n.density_m3(Sp::H1Neutral),
        hp_m3: n.density_m3(Sp::H1Ionized),
        d0_m3: n.density_m3(Sp::DNeutral),
        dp_m3: n.density_m3(Sp::DIonized),
        thermal_j_m3: initial.thermal_j_m3,
    };
    let old = integrate_si(
        dh,
        provider().defect(),
        &savin_provider(),
        2e10,
        ThermalCxControls::default(),
    );
    assert!(matches!(
        old.core.status,
        ThermalCxStatus::Complete | ThermalCxStatus::CompleteEquilibrium
    ));
    let new = component(CxOwnership::ThermalSubstep)
        .advance_cx_only(
            initial,
            2e10,
            StepControls {
                rtol: 1e-10,
                ..Default::default()
            },
        )
        .unwrap();
    let a = old.extent_m3.unwrap();
    let b = new.extent_m3;
    let rel = (a - b).abs() / a.abs().max(1e-30);
    assert!(rel < 1e-3, "native={a} mixed={b} relative={rel}");
}
#[test]
fn zero_duration_exact_identity() {
    let s = state(100.0);
    let r = component(CxOwnership::ThermalSubstep)
        .advance_cx_only(s, 0.0, StepControls::default())
        .unwrap();
    assert_eq!(r.extent_m3, 0.0);
    assert_eq!(
        r.final_state.thermal_j_m3.to_bits(),
        s.thermal_j_m3.to_bits()
    );
    for sp in Sp::ALL {
        assert_eq!(
            r.final_state.nuclei.density_m3(sp).to_bits(),
            s.nuclei.density_m3(sp).to_bits()
        );
    }
}
#[test]
fn photo_input_binding_keeps_owner_single() {
    let p = provider();
    let photo = p.photo_input(&[], "SOURCE_OFF").unwrap();
    let bad = DAtomicProvider::new(13.598, 13.604, "DIFFERENT_THRESHOLD_OWNER").unwrap();
    let s = state(200.0);
    assert!(
        component(CxOwnership::ThermalSubstep)
            .atomic_rhs(&s, &photo)
            .is_ok()
    );
    let fail = ThermalCxComponent::new(bad, CxOwnership::ThermalSubstep).rhs(
        &s.nuclei,
        s.eos().unwrap().temperature_k,
        &photo,
    );
    assert!(matches!(
        fail,
        Err(rei_iso_couple_reference::deuterium_atomic::DAtomicError::PhotoThresholdMismatch)
    ));
}
#[test]
fn overdomain_temperature_rejected_without_clipping() {
    let mut s = state(1.0);
    s.thermal_j_m3 *= 35.0;
    assert!(matches!(
        component(CxOwnership::ThermalSubstep).advance_cx_only(s, 1e10, StepControls::default()),
        Err(CoupleError::ProviderBoundary)
    ));
}
#[test]
fn negative_duration_and_invalid_controls() {
    let c = component(CxOwnership::ThermalSubstep);
    let s = state(100.0);
    assert!(matches!(
        c.advance_cx_only(s, -1.0, StepControls::default()),
        Err(CoupleError::InvalidTimeOrControls)
    ));
    assert!(matches!(
        c.advance_cx_only(
            s,
            1.0,
            StepControls {
                max_attempts: 0,
                ..Default::default()
            }
        ),
        Err(CoupleError::InvalidTimeOrControls)
    ));
    assert!(matches!(
        c.advance_cx_only(
            s,
            1.0,
            StepControls {
                rtol: f64::NAN,
                ..Default::default()
            }
        ),
        Err(CoupleError::InvalidTimeOrControls)
    ));
}
#[test]
fn tiny_rhs_cap_is_a_typed_failure_not_a_success() {
    let c = component(CxOwnership::ThermalSubstep);
    let ans = c.advance_cx_only(
        state(100.0),
        1e9,
        StepControls {
            max_rate_calls: 1,
            ..Default::default()
        },
    );
    assert!(matches!(ans, Err(CoupleError::WorkLimit)));
}
#[test]
fn random_manufactured_spectators_preserve_invariants() {
    let c = component(CxOwnership::ThermalSubstep);
    let mut seed = 0x29ed_u64;
    for _ in 0..96 {
        seed = seed
            .wrapping_mul(2862933555777941757)
            .wrapping_add(3037000493);
        let he = (seed % 400) as f64;
        let s = state(he);
        let q = c.advance_cx_only(s, 2e9, StepControls::default()).unwrap();
        let a = s.eos().unwrap();
        let b = q.final_state.eos().unwrap();
        approx(a.baryons_m3, b.baryons_m3, 1e-12);
        approx(a.free_electrons_m3, b.free_electrons_m3, 1e-12);
        approx(a.thermal_particles_m3, b.thermal_particles_m3, 1e-12);
        approx(q.delta_thermal_j_m3 + q.delta_chemical_j_m3, 0.0, 1e-20);
    }
}
#[test]
fn source_native_coefficients_not_manufactured() {
    let p = provider();
    let r = p.rates(10000.0).unwrap();
    assert_eq!(r.model_id, "GRACKLE_3_4_1_H_EQUALITY_D_ATOMIC_V1");
    assert_eq!(r.source_commit, "af7939494ce65007887ada7b98d1813df6843346");
    assert!(r.rr_case_a_m3_s > 0.0);
}
#[test]
fn imported_photo_cross_section_real_verner_but_not_integrated() {
    let p = provider();
    let s = p.cross_section_m2(20.0).unwrap();
    assert!(s > 0.0);
    let ph = p
        .photo_input(
            &[rei_iso_couple_reference::deuterium_atomic::DPhotoBin {
                energy_ev: 20.0,
                photon_flux_m2_s: 1e9,
            }],
            "MANUFACTURED_GAS_REST_FLUX",
        )
        .unwrap();
    assert!(ph.gamma_s() > 0.0 && ph.heat_j_per_absorber_s() > 0.0);
    assert!(
        component(CxOwnership::ThermalSubstep)
            .atomic_rhs(&state(20.0), &ph)
            .unwrap()
            .instantaneous_atomic_rhs
            .photo_events_m3_s
            > 0.0
    );
}

#[test]
fn savin_independent_fits_are_not_detailed_balance_surrogate() {
    let r = Savin2002::rates(10000.0).unwrap();
    let ratio = r.forward_m3_s / r.reverse_m3_s;
    let expected = (-42.915_f64 / 10000.0).exp();
    assert!(ratio > 1.0 && expected < 1.0);
    assert!((ratio - 1.00989376).abs() < 1e-7);
    assert!((expected - 0.995717695).abs() < 1e-7);
}
