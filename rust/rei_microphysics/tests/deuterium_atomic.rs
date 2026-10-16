use rei_microphysics::deuterium_atomic::*;
use rei_microphysics::deuterium_charge_exchange::{DhError, DhState, Savin2002};
use rei_microphysics::igm_rates::igm_rates;
use rei_microphysics::{Absorber, AtomicProvider, HHeModel, IsotopeNumberState, IsotopeSpecies};

fn provider() -> DAtomicProvider {
    let h = HHeModel::controlled_fixture().threshold_ev[0];
    DAtomicProvider::new(h, h + 0.0037,
        "Savin2002 approximate 3.7meV defect added explicitly to existing H binding owner; not precision chi_D").unwrap()
}

fn state(h0: f64, hp: f64, d0: f64, dp: f64) -> IsotopeNumberState {
    let mut ns = [0.0; 13];
    use IsotopeSpecies::*;
    for (i, value) in [
        (H1Neutral, h0),
        (H1Ionized, hp),
        (DNeutral, d0),
        (DIonized, dp),
    ] {
        ns[i as usize] = value;
    }
    IsotopeNumberState::new(ns).unwrap()
}

fn close(x: f64, y: f64) {
    assert!(
        (x - y).abs() <= 2e-13 * x.abs().max(y.abs()).max(1e-300),
        "{x:.17e} != {y:.17e}"
    );
}

fn energy_closes(ledger: DEnergyLedger) {
    let scale = ledger.thermal.abs()
        + ledger.chemical.abs()
        + ledger.escape.abs()
        + ledger.photon_input.abs();
    assert!(
        ledger.residual().abs() <= 2e-13 * scale,
        "ledger {ledger:?}"
    );
}

fn no_light(p: DAtomicProvider) -> DPhotoInput {
    p.photo_input(&[], "explicit empty photon field").unwrap()
}

#[test]
fn source_wrapper_si_units_floors_caps_and_operational_domain() {
    let p = provider();
    for t in [1.0, 3.0, 10.0, 100.0, 1e4, 1e5, 1e6] {
        let d = p.rates(t).unwrap();
        let h = igm_rates(t).unwrap();
        assert_eq!(d.ci_m3_s, h.ci_cm3_s[0] * 1e-6);
        assert_eq!(d.rr_case_a_m3_s, h.rr_cm3_s[0] * 1e-6);
        assert_eq!(d.rr_kinetic_j_m3_s, h.rr_cooling_erg_cm3_s[0] * 1e-13);
        assert_eq!(d.ce_j_m3_s, h.ce_erg[0] * 1e-13);
        assert_eq!(d.ci_floor_m3_s, h.diagnostics.ci_floor_cm3_s[0] * 1e-6);
        assert_eq!(d.ce_cap_j_m3_s, h.diagnostics.ce_cap_erg[0] * 1e-13);
        assert_eq!(d.model_id, "GRACKLE_3_4_1_H_EQUALITY_D_ATOMIC_V1");
        assert_eq!(d.source_commit, "af7939494ce65007887ada7b98d1813df6843346");
        println!("actual D H-equality coefficients T={t}K ci={}m3/s rr={}m3/s rr_kinetic={}Jm3/s ce={}Jm3/s floor={} cap={}",
            d.ci_m3_s,d.rr_case_a_m3_s,d.rr_kinetic_j_m3_s,d.ce_j_m3_s,d.ci_floor_m3_s,d.ce_cap_j_m3_s);
    }
    assert!(p.rates(1.0).unwrap().ci_floor_m3_s > 0.0);
    assert!(p.rates(1.0).unwrap().ce_cap_j_m3_s > 0.0);
    for t in [0.0, -1.0, 0.999999, 1_000_000.01] {
        assert_eq!(p.rates(t), Err(DAtomicError::TemperatureDomain));
    }
    assert_eq!(p.rates(f64::NAN), Err(DAtomicError::NonFiniteInput));
}

#[test]
fn photo_threshold_actual_cross_section_and_common_absorption_heat() {
    let p = provider();
    let chi = p.chi_d_ev();
    close(chi, 13.602134599702);
    assert_eq!(p.cross_section_m2(chi - 1e-9).unwrap(), 0.0);
    for e in [chi, chi + 1e-9, 20.0, 50_000.0] {
        assert_eq!(
            p.cross_section_m2(e).unwrap(),
            AtomicProvider::reference()
                .cross_section(Absorber::HI, e)
                .unwrap()
                * 1e-4
        );
    }
    assert!(p.cross_section_m2(chi).unwrap() > 0.0);
    let edge = p
        .photo_input(
            &[DPhotoBin {
                energy_ev: chi,
                photon_flux_m2_s: 1e9,
            }],
            "threshold monochromatic flux",
        )
        .unwrap();
    assert!(edge.gamma_s() > 0.0);
    assert_eq!(edge.heat_j_per_absorber_s(), 0.0);
    let ev_j = HHeModel::controlled_fixture().ev_erg * 1e-7;
    close(edge.energy_j_per_absorber_s(), chi * ev_j * edge.gamma_s());
    let photo = p
        .photo_input(
            &[
                DPhotoBin {
                    energy_ev: 20.0,
                    photon_flux_m2_s: 1e9,
                },
                DPhotoBin {
                    energy_ev: chi - 1e-9,
                    photon_flux_m2_s: 1e30,
                },
            ],
            "explicit mono20eV plus sub-D-edge spectrum",
        )
        .unwrap();
    close(photo.gamma_s(), p.cross_section_m2(20.0).unwrap() * 1e9);
    close(
        photo.heat_j_per_absorber_s(),
        photo.gamma_s() * (20.0 - chi) * ev_j,
    );
    close(
        photo.energy_j_per_absorber_s(),
        photo.heat_j_per_absorber_s() + chi * ev_j * photo.gamma_s(),
    );
    assert!(PHOTO_APPROXIMATION.contains("not exact"));
    assert_eq!(
        p.cross_section_m2(50_000.01),
        Err(DAtomicError::PhotonEnergyDomain)
    );
    assert_eq!(p.cross_section_m2(-1.0), Err(DAtomicError::InvalidInput));
    assert_eq!(
        p.cross_section_m2(f64::INFINITY),
        Err(DAtomicError::NonFiniteInput)
    );
}

#[test]
fn pure_photoionization_counts_energy_and_particle_temperature_term() {
    let p = provider();
    let s = state(5.0, 0.0, 2.0, 0.0);
    let photo = p
        .photo_input(
            &[DPhotoBin {
                energy_ev: 20.0,
                photon_flux_m2_s: 1e9,
            }],
            "explicit test monochromatic flux",
        )
        .unwrap();
    let rhs = d_atomic_rhs(p, &s, 100.0, &photo, DChargeExchange::Disabled).unwrap();
    close(rhs.photo_events_m3_s, 2.0 * photo.gamma_s());
    assert_eq!(rhs.ci_events_m3_s, 0.0);
    assert_eq!(rhs.rr_events_m3_s, 0.0);
    close(rhs.electron_m3_s, rhs.photo_events_m3_s);
    close(
        rhs.species_m3_s[IsotopeSpecies::DIonized as usize],
        rhs.photo_events_m3_s,
    );
    close(rhs.energy.thermal, 2.0 * photo.heat_j_per_absorber_s());
    assert_eq!(rhs.energy.escape, 0.0);
    energy_closes(rhs.energy);
    let kb = HHeModel::controlled_fixture().kb_erg_k * 1e-7;
    close(
        rhs.temperature_k_s,
        2.0 * rhs.energy.thermal / (3.0 * kb * 7.0) - 100.0 * rhs.electron_m3_s / 7.0,
    );
}

#[test]
fn ci_rr_ce_have_one_energy_owner_and_no_guessed_rr_kinetic_moment() {
    let p = provider();
    let ev_j = HHeModel::controlled_fixture().ev_erg * 1e-7;
    let chi = p.chi_d_ev() * ev_j;
    let ci_state = state(5.0, 1.0, 2.0, 0.0);
    let ci = d_atomic_rhs(p, &ci_state, 1e5, &no_light(p), DChargeExchange::Disabled).unwrap();
    assert!(ci.ci_events_m3_s > 0.0);
    assert_eq!(ci.rr_events_m3_s, 0.0);
    close(ci.channel_energy[1].thermal, -chi * ci.ci_events_m3_s);
    close(ci.channel_energy[1].chemical, chi * ci.ci_events_m3_s);
    assert_eq!(ci.channel_energy[1].escape, 0.0);
    let ce = ci.channel_energy[3];
    assert!(ce.escape > 0.0);
    assert_eq!(ce.chemical, 0.0);
    assert_eq!(ce.thermal, -ce.escape);
    close(
        ci.species_m3_s[IsotopeSpecies::DIonized as usize],
        ci.ci_events_m3_s,
    );
    for row in ci.channel_energy {
        energy_closes(row);
    }
    energy_closes(ci.energy);
    let rr_state = state(5.0, 0.0, 0.0, 2.0);
    let rr = d_atomic_rhs(p, &rr_state, 1e4, &no_light(p), DChargeExchange::Disabled).unwrap();
    assert_eq!(rr.ci_events_m3_s, 0.0);
    assert_eq!(rr.channel_energy[3], DEnergyLedger::default());
    let kinetic = 4.0 * p.rates(1e4).unwrap().rr_kinetic_j_m3_s;
    close(rr.energy.thermal, -kinetic);
    close(rr.energy.chemical, -chi * rr.rr_events_m3_s);
    close(rr.energy.escape, kinetic + chi * rr.rr_events_m3_s);
    close(rr.electron_m3_s, -rr.rr_events_m3_s);
    energy_closes(rr.energy);
    let naive = 1.5 * HHeModel::controlled_fixture().kb_erg_k * 1e-7 * 1e4;
    assert!((kinetic / rr.rr_events_m3_s / naive - 1.0).abs() > 0.01);
}

#[test]
fn combined_native_rhs_cx_stoichiometry_same_defect_and_plasma_contributions() {
    let p = provider();
    let mut ns = [0.0; 13];
    use IsotopeSpecies::*;
    for (i, v) in [
        (H1Neutral, 5.0),
        (H1Ionized, 3.0),
        (DNeutral, 2.0),
        (DIonized, 1.0),
        (He3SinglyIonized, 0.25),
        (He4DoublyIonized, 0.5),
        (Neutron, 0.1),
    ] {
        ns[i as usize] = v;
    }
    let s = IsotopeNumberState::new(ns).unwrap();
    let photo = p
        .photo_input(
            &[DPhotoBin {
                energy_ev: 30.0,
                photon_flux_m2_s: 2e9,
            }],
            "explicit test common field",
        )
        .unwrap();
    let rhs = d_atomic_rhs(p, &s, 1e4, &photo, DChargeExchange::Savin2002).unwrap();
    let r = Savin2002::rates(1e4).unwrap();
    close(rhs.cx_forward_events_m3_s, r.forward_m3_s * 2.0 * 3.0);
    close(rhs.cx_reverse_events_m3_s, r.reverse_m3_s * 1.0 * 5.0);
    let x = rhs.cx_forward_events_m3_s - rhs.cx_reverse_events_m3_s;
    close(rhs.species_m3_s[H1Neutral as usize], x);
    close(rhs.electron_density_m3, 3.0 + 1.0 + 0.25 + 2.0 * 0.5);
    close(
        rhs.electron_m3_s,
        rhs.photo_events_m3_s + rhs.ci_events_m3_s - rhs.rr_events_m3_s,
    );
    assert_eq!(
        rhs.species_m3_s[H1Neutral as usize] + rhs.species_m3_s[H1Ionized as usize],
        0.0
    );
    assert_eq!(
        rhs.species_m3_s[DNeutral as usize] + rhs.species_m3_s[DIonized as usize],
        0.0
    );
    let baryons: f64 = IsotopeSpecies::ALL
        .iter()
        .map(|&i| f64::from(i.baryon_number()) * rhs.species_m3_s[i as usize])
        .sum();
    assert_eq!(baryons, 0.0);
    let charge: f64 = IsotopeSpecies::ALL
        .iter()
        .map(|&i| f64::from(i.charge()) * rhs.species_m3_s[i as usize])
        .sum();
    close(charge, rhs.electron_m3_s);
    for i in [He3SinglyIonized, He4DoublyIonized, Neutron] {
        assert_eq!(rhs.species_m3_s[i as usize], 0.0);
    }
    for row in rhs.channel_energy {
        energy_closes(row);
    }
    energy_closes(rhs.energy);
    close(
        rhs.channel_energy[4].thermal,
        -p.defect().delta_chi_j * rhs.cx_forward_events_m3_s,
    );
    close(
        rhs.channel_energy[5].thermal,
        p.defect().delta_chi_j * rhs.cx_reverse_events_m3_s,
    );
    assert_eq!(
        rhs.plasma,
        DPlasmaContributions {
            electrons_m3: 1.0,
            ions_m3: 1.0,
            freefree_z2_ions_m3: 1.0
        }
    );
    let split = p
        .step_charge_exchange(
            DhState {
                h0_m3: 5.0,
                hp_m3: 3.0,
                d0_m3: 2.0,
                dp_m3: 1.0,
                thermal_j_m3: 1.0,
            },
            1e4,
            1e12,
        )
        .unwrap();
    assert_eq!(split.defect, p.defect());
    close(
        split.chemical_delta_j_m3,
        p.defect().delta_chi_j * split.extent_m3,
    );
    println!(
        "actual combined RHS ne={} electron_dt={} CXf={} CXr={} energy_residual={}J/m3/s",
        rhs.electron_density_m3,
        rhs.electron_m3_s,
        rhs.cx_forward_events_m3_s,
        rhs.cx_reverse_events_m3_s,
        rhs.energy.residual()
    );
}

#[test]
fn invalid_inputs_domains_and_threshold_binding_reject_transactionally() {
    let p = provider();
    let s = state(5.0, 1.0, 2.0, 1.0);
    let original = s;
    assert_eq!(
        p.photo_input_from_bound_rates(0.0, 1.0, "inconsistent external moments"),
        Err(DAtomicError::InvalidInput)
    );
    assert_eq!(
        p.photo_input_from_bound_rates(-1.0, 0.0, "negative"),
        Err(DAtomicError::InvalidInput)
    );
    assert_eq!(
        p.photo_input_from_bound_rates(1.0, f64::NAN, "nonfinite"),
        Err(DAtomicError::NonFiniteInput)
    );
    assert_eq!(
        p.photo_input(
            &[DPhotoBin {
                energy_ev: 20.0,
                photon_flux_m2_s: -1.0
            }],
            "invalid flux"
        ),
        Err(DAtomicError::InvalidInput)
    );
    assert!(DAtomicProvider::new(13.6, 13.6, "no defect").is_err());
    assert!(DAtomicProvider::new(13.6, 13.7, "").is_err());
    assert!(DAtomicProvider::new(f64::NAN, 13.7, "bad H").is_err());
    let other = DAtomicProvider::new(
        p.chi_h_ev(),
        p.chi_d_ev() + 0.001,
        "other threshold approximation",
    )
    .unwrap();
    assert_eq!(
        d_atomic_rhs(other, &s, 100.0, &no_light(p), DChargeExchange::Disabled),
        Err(DAtomicError::PhotoThresholdMismatch)
    );
    for t in [1.0, 1e6] {
        assert!(d_atomic_rhs(p, &s, t, &no_light(p), DChargeExchange::Disabled).is_ok());
        assert_eq!(
            d_atomic_rhs(p, &s, t, &no_light(p), DChargeExchange::Savin2002),
            Err(DAtomicError::ChargeExchange(
                DhError::OutsideTemperatureDomain
            ))
        );
    }
    for t in [2.7, 2e5] {
        assert!(d_atomic_rhs(p, &s, t, &no_light(p), DChargeExchange::Savin2002).is_ok());
    }
    assert_eq!(
        d_atomic_rhs(
            p,
            &s,
            f64::INFINITY,
            &no_light(p),
            DChargeExchange::Disabled
        ),
        Err(DAtomicError::NonFiniteInput)
    );
    assert_eq!(s, original);
    let external = p
        .photo_input_from_bound_rates(1e-12, 2e-30, "explicit matched absorption moments fixture")
        .unwrap();
    close(
        external.energy_j_per_absorber_s(),
        external.heat_j_per_absorber_s()
            + p.chi_d_ev() * HHeModel::controlled_fixture().ev_erg * 1e-7 * external.gamma_s(),
    );
}

#[test]
fn conditional_inventory_preserves_nb_and_is_not_matched_rec_donor() {
    let inventory = DInventory {
        ratio_d_to_h1: 2.527e-5,
        uncertainty: Some(0.030e-5),
        uncertainty_definition:
            "68 percent confidence interval; observational inference, not new BBN run",
        kind: DInventoryKind::ObservationConditionedPrimordialRatio,
        source: "Cooke Pettini Steidel2018 ApJ855102 DOI10.3847/1538-4357/aaab53 Eq10",
    };
    let initial = conditional_h1_d_he4_state(
        100.0,
        0.08,
        1e-4,
        [0.0, 0.0],
        inventory,
        DInitialIonization::FrozenChargeExchangeBalance {
            temperature_k: 100.0,
        },
    )
    .unwrap();
    assert_eq!(initial.inventory, inventory);
    assert!(initial.inventory_scope.contains("NO_MATCHED_REC_DONOR"));
    let s = initial.state;
    use IsotopeSpecies::*;
    let nh = s.density_m3(H1Neutral) + s.density_m3(H1Ionized);
    let nd = s.density_m3(DNeutral) + s.density_m3(DIonized);
    close(nd / nh, inventory.ratio_d_to_h1);
    close(s.moments().unwrap().baryon_density_m3, 100.0);
    close(
        nh,
        100.0 / (1.0 + 2.0 * inventory.ratio_d_to_h1 + 4.0 * 0.08),
    );
    let r = Savin2002::rates(100.0).unwrap();
    close(
        r.forward_m3_s * s.density_m3(DNeutral) * s.density_m3(H1Ionized),
        r.reverse_m3_s * s.density_m3(DIonized) * s.density_m3(H1Neutral),
    );
    for i in [
        Neutron,
        TNeutral,
        TIonized,
        He3Neutral,
        He3SinglyIonized,
        He3DoublyIonized,
    ] {
        assert_eq!(s.density_m3(i), 0.0);
    }
    let explicit = conditional_h1_d_he4_state(
        100.0,
        0.08,
        1e-4,
        [0.1, 0.2],
        inventory,
        DInitialIonization::Explicit {
            fraction: 0.25,
            source: "explicit conditional ionic IC",
        },
    )
    .unwrap();
    assert_eq!(explicit.dplus_fraction, 0.25);
    assert!(conditional_h1_d_he4_state(
        100.0,
        0.08,
        1e-4,
        [0.9, 0.2],
        inventory,
        DInitialIonization::Explicit {
            fraction: 0.25,
            source: "invalid He fractions"
        }
    )
    .is_err());
    println!(
        "actual conditional Cooke inventory nb={} nH1={} nD={} xDplus={} scope={}",
        s.moments().unwrap().baryon_density_m3,
        nh,
        nd,
        initial.dplus_fraction,
        initial.inventory_scope
    );
}

#[test]
fn absent_deuterium_is_native_noop_and_legacy_guard_is_preserved() {
    let p = provider();
    let hhe = state(5.0, 1.0, 0.0, 0.0);
    let light = p
        .photo_input(
            &[DPhotoBin {
                energy_ev: 30.0,
                photon_flux_m2_s: 1e9,
            }],
            "explicit no-D fixture flux",
        )
        .unwrap();
    let rhs = d_atomic_rhs(p, &hhe, 100.0, &light, DChargeExchange::Savin2002).unwrap();
    assert_eq!(rhs.species_m3_s, [0.0; 13]);
    assert_eq!(rhs.electron_m3_s, 0.0);
    assert_eq!(rhs.energy, DEnergyLedger::default());
    assert_eq!(rhs.temperature_k_s, 0.0);
    assert!(hhe.try_legacy_hhe_projection().is_ok());
    assert!(state(5.0, 1.0, 2.0, 1.0)
        .try_legacy_hhe_projection()
        .is_err());
}
