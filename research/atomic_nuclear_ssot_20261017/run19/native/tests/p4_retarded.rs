use rei_iso_couple_reference::{
    Absorber, AtomicProvider, HHeModel,
    axbi_sources::{AxbiSource, SOURCE_ID},
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground, GeometryBackground},
    deuterium_atomic::DAtomicProvider,
    full_network::{FullState, NetworkConfig, NetworkError},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
    positive_spectral::{SpectralMode, owner_cell_nodes},
    retarded_transport::{PositiveRetardedBridge, RetardedControls, gauss_birth_nodes},
    source_age::SourceAgeBridge,
};
fn setup(
    h: f64,
    shear: f64,
    fe: f64,
    all_ions: bool,
    t_end: f64,
    c: RetardedControls,
) -> (PositiveRetardedBridge, NetworkConfig, FullState) {
    let src = AxbiSource::new(1900.0 / (21.0f64.powi(3) * 1e6), fe, 16, 8).unwrap();
    let bg = ConstantAxisymmetricBackground::new(
        0.,
        AxisymmetricPoint::new(1.0 / 21.0, 0., h, shear).unwrap(),
        [0., t_end],
    )
    .unwrap();
    let bridge = PositiveRetardedBridge(SourceAgeBridge::new(src, bg).unwrap(), c);
    let ch = HHeModel::controlled_fixture().threshold_ev[0];
    let mut conf = NetworkConfig::source_bound(
        DAtomicProvider::new(ch, ch + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        SOURCE_ID,
    );
    let mut n = [0.; 13];
    if all_ions {
        n[S::H1Ionized as usize] = 1900.;
        n[S::He4DoublyIonized as usize] = 460.;
        n[S::DIonized as usize] = 30.;
        conf.use_cx = false;
        conf.use_collisions = false;
        conf.use_cmb = false;
    } else {
        n[S::H1Neutral as usize] = 1000.;
        n[S::H1Ionized as usize] = 900.;
        n[S::He4Neutral as usize] = 300.;
        n[S::He4SinglyIonized as usize] = 100.;
        n[S::He4DoublyIonized as usize] = 60.;
        n[S::DNeutral as usize] = 25.;
        n[S::DIonized as usize] = 5.;
    }
    let nuclei = IsotopeNumberState::new(n).unwrap();
    let thermal = nuclei.thermal_particle_density_all_thermal_m3().unwrap() * 1.5 * KB_J_K * 1e4;
    (
        bridge,
        conf,
        FullState {
            gas: MixtureState {
                nuclei,
                thermal_j_m3: thermal,
            },
            photon_bins: vec![],
            escaped_j_m3: 0.,
            cmb_reservoir_j_m3: 0.,
            elapsed_s: 0.,
        },
    )
}
fn rel(a: f64, b: f64) -> f64 {
    (a - b).abs() / a.abs().max(b.abs()).max(1e-45)
}
#[test]
fn birth_quadrature_weights_are_positive_and_reject_wrong_order() {
    for n in [2, 4] {
        let nodes = gauss_birth_nodes(n).unwrap();
        assert_eq!(nodes.len(), n);
        assert!(nodes.windows(2).all(|w| w[0].0 < w[1].0));
        assert!(nodes.iter().all(|(x, w)| *x > 0. && *x < 1. && *w > 0.));
        assert!((nodes.iter().map(|(_, w)| w).sum::<f64>() - 1.).abs() < 3e-16);
        assert!((nodes.iter().map(|(x, w)| w * x).sum::<f64>() - 0.5).abs() < 3e-16);
    }
    assert!(gauss_birth_nodes(3).is_err());
    assert!(RetardedControls::new(4, 3, SpectralMode::OriginalCellMean).is_err());
}
#[test]
fn source_spectral_refinement_preserves_per_cell_photon_number_and_resolves_d_edge() {
    let src = AxbiSource::new(1900.0 / (21.0f64.powi(3) * 1e6), 0.2, 16, 8).unwrap();
    let d = HHeModel::controlled_fixture().threshold_ev[0] + 0.0037;
    let first = owner_cell_nodes(&src, 0, d, SpectralMode::SplitPositiveGauss3).unwrap();
    assert_eq!(first.len(), 6);
    assert!(first.iter().any(|c| c.energy_ev < d));
    assert!(first.iter().any(|c| c.energy_ev > d));
    assert!((first.iter().map(|c| c.fraction).sum::<f64>() - 1.).abs() < 5e-16);
    let un = owner_cell_nodes(&src, 0, d, SpectralMode::OriginalCellMean).unwrap();
    assert_eq!(un.len(), 1);
    assert_eq!(un[0].energy_ev, src.spectral_cells[0].energy_ev);
    for i in 0..src.spectral_cells.len() {
        let nodes = owner_cell_nodes(&src, i, d, SpectralMode::SplitPositiveGauss3).unwrap();
        assert!(nodes.iter().all(|x| x.fraction > 0.
            && x.energy_ev > src.spectral_cells[i].lower_ev
            && x.energy_ev < src.spectral_cells[i].upper_ev));
        assert!(rel(nodes.iter().map(|x| x.fraction).sum(), 1.) < 8e-16);
        let centroid = nodes.iter().map(|x| x.energy_ev * x.fraction).sum::<f64>();
        assert!(
            rel(centroid, src.spectral_cells[i].energy_ev) < 3e-7,
            "cell {i}: centroid {centroid} owner {}",
            src.spectral_cells[i].energy_ev
        );
    }
    assert!(owner_cell_nodes(&src, 0, f64::NAN, SpectralMode::OriginalCellMean).is_err());
}
#[test]
fn static_no_absorption_exact_birth_inventory_and_killing_photon_energy() {
    let ctl = RetardedControls::new(4, 8, SpectralMode::SplitPositiveGauss3).unwrap();
    let (b, conf, full) = setup(1.2e-16, 0.06 * 1.2e-16, 0.2, true, 1.5e14, ctl);
    let s = b.initial(full, &conf, 0.).unwrap();
    let one = b.advance(&s, &conf, 1e10).unwrap();
    assert!(
        one.chemistry_budget
            .photo_events_m3
            .iter()
            .all(|x| *x == 0.)
    );
    assert!(one.source_birth_com3 > 0.);
    assert!(
        rel(
            one.state.cohorts.iter().map(|c| c.n_comoving_m3).sum(),
            one.source_birth_com3
        ) < 2e-14
    );
    assert!(one.global_energy_relative_error < 3e-10);
    let two = b.advance(&one.state, &conf, 1e10).unwrap();
    assert!(
        rel(
            two.state.cohorts.iter().map(|c| c.n_comoving_m3).sum(),
            two.state.source_injected_count_com3
        ) < 2e-14
    );
    assert!(
        two.chemistry_budget
            .photo_events_m3
            .iter()
            .all(|x| *x == 0.)
    );
}
#[test]
fn constant_opacity_dynamics_photon_oracle_vs_gauss_birth() {
    let ctl = RetardedControls::new(4, 1, SpectralMode::OriginalCellMean).unwrap();
    let (b, mut conf, full) = setup(0., 0., 0.2, false, 1.5e14, ctl);
    conf.use_collisions = false;
    conf.use_cx = false;
    conf.use_cmb = false;
    let s = b.initial(full, &conf, 0.).unwrap();
    let dt = 1e9;
    let born = b.emit_births(0., dt, &conf).unwrap();
    let g = b.0.geometry.snapshot(0.).unwrap();
    let mut exact_survivor = 0.;
    for co in &born {
        let en = co.ray_at(&g).unwrap().energy_ev;
        // Independent original provider-based opacity assembly (does not expose a
        // private native bridge method or mutate the source owner).
        let gas = &s.full.gas.nuclei;
        let p = AtomicProvider::reference();
        let k0 = gas.density_m3(S::H1Neutral) * p.cross_section(Absorber::HI, en).unwrap() * 1e-4;
        let k1 = gas.density_m3(S::He4Neutral) * p.cross_section(Absorber::HeI, en).unwrap() * 1e-4;
        let k2 = gas.density_m3(S::He4SinglyIonized)
            * p.cross_section(Absorber::HeII, en).unwrap()
            * 1e-4;
        let k3 = gas.density_m3(S::DNeutral) * conf.deuterium.cross_section_m2(en).unwrap();
        let tau = (k0 + k1 + k2 + k3) * 299_792_458.0 * dt;
        let remaining = dt - co.birth_time_s;
        // exact individual point birth at gauss time, frozen original rate
        exact_survivor += co.n_comoving_m3 * (-tau * remaining / dt).exp();
    }
    let one = b.advance(&s, &conf, dt).unwrap();
    let total = one
        .state
        .cohorts
        .iter()
        .map(|c| c.n_comoving_m3)
        .sum::<f64>();
    assert!(rel(total, exact_survivor) < 4e-14);
    assert!(
        rel(
            one.state.source_injected_count_com3,
            total + one.state.photon_absorbed_count_com3
        ) < 3e-14
    );
    assert!(one.global_energy_relative_error < 3e-10);
}
#[test]
fn actual_native_photo_and_gas_signed_shear_physics_ledgers() {
    for shear in [-0.06 * 1.2e-16, 0., 0.06 * 1.2e-16] {
        let ctl = RetardedControls::new(2, 4, SpectralMode::OriginalCellMean).unwrap();
        let (b, conf, full) = setup(1.2e-16, shear, 0.2, false, 1.5e14, ctl);
        let initial = b.initial(full, &conf, 0.).unwrap();
        let (step, diag) = b.advance_with_diagnostics(&initial, &conf, 1e10).unwrap();
        assert_eq!(step.state.chemistry_accepted, 1);
        assert_eq!(step.state.cohorts.len(), 768);
        assert!(step.global_energy_relative_error < 3e-10);
        assert!(diag.photon_events_com3.iter().sum::<f64>() > 0.);
        assert!(
            rel(
                step.state.source_injected_count_com3,
                step.state
                    .cohorts
                    .iter()
                    .map(|c| c.n_comoving_m3)
                    .sum::<f64>()
                    + step.state.photon_absorbed_count_com3
            ) < 5e-13
        );
        assert!(diag.photon_work_ledger_j_com3.is_finite());
        assert!(diag.photon_work_independent_j_com3.is_finite());
        let second = b.advance(&step.state, &conf, 1e10).unwrap();
        assert_eq!(second.state.chemistry_accepted, 2);
        assert!(second.global_energy_relative_error < 3e-10);
    }
}
#[test]
fn retarded_rejects_domain_and_preserves_input() {
    let ctl = RetardedControls::new(2, 1, SpectralMode::OriginalCellMean).unwrap();
    let (b, mut conf, full) = setup(1.2e-16, 0., 0.2, false, 1.5e14, ctl);
    let state = b.initial(full, &conf, 0.).unwrap();
    let t = state.time_s;
    let photons = state.cohorts.len();
    for bad in [-1., 0., f64::NAN, 1e16] {
        assert!(b.advance(&state, &conf, bad).is_err());
    }
    conf.photon_source = "BAD_SOURCE";
    assert_eq!(
        b.advance(&state, &conf, 1e10).unwrap_err(),
        NetworkError::SourceMismatch
    );
    assert_eq!(state.time_s, t);
    assert_eq!(state.cohorts.len(), photons);
}
#[test]
fn scalar_linear_varying_opacity_positive_conservative() {
    use rei_iso_couple_reference::retarded_transport::scalar_duhamel;
    for q in [2, 4] {
        for m in [1, 4, 8, 16] {
            let out = scalar_duhamel(
                0.,
                1.,
                2.3,
                q,
                m,
                |t| 1.7 * (1. + t / 4.),
                |t| 0.3 + 1.1 * t,
            )
            .unwrap();
            assert!(out.emitted > 0. && out.absorbed > 0. && out.survivors > 0.);
            assert!((out.survivors + out.absorbed - 2.3 - out.emitted).abs() < 5e-15);
        }
    }
    for bad in [-1., f64::NAN, f64::INFINITY] {
        assert!(scalar_duhamel(0., 1., 2.3, 4, 8, |_| 1., move |_| bad).is_err());
    }
}

#[test]
fn md14_source_age_gauss_reproduces_independent_simpson_emissivity() {
    let ctl = RetardedControls::new(4, 2, SpectralMode::OriginalCellMean).unwrap();
    let h = 1.2e-16;
    let (b, conf, full) = setup(h, 0.06 * h, 0.2, false, 1.5e14, ctl);
    let _initial = b.initial(full, &conf, 0.).unwrap();
    let end = 1e13;
    let emitted = b
        .emit_births(0., end, &conf)
        .unwrap()
        .iter()
        .map(|x| x.n_comoving_m3)
        .sum::<f64>();
    let n = 512usize;
    let mut s = 0.;
    for j in 0..=n {
        let t = end * j as f64 / n as f64;
        let z = 1.
            / b.0
                .geometry
                .snapshot(t)
                .unwrap()
                .volume_factor()
                .unwrap()
                .cbrt()
            - 1.;
        let q =
            b.0.source
                .at_redshift(z)
                .unwrap()
                .comoving_photons_per_s_cmpc3;
        let weight = if j == 0 || j == n {
            1.
        } else if j % 2 == 0 {
            2.
        } else {
            4.
        };
        s += weight * q;
    }
    let integrated = s * end / (3. * n as f64) * 1e6 / rei_iso_couple_reference::MPC_CM.powi(3);
    assert!(
        rel(integrated, emitted) < 5e-12,
        "Gauss source {emitted:e} vs source-native Simpson {integrated:e}"
    );
}
#[test]
fn exact_killing_work_independently_reconstructed_when_ionization_opacity_zero() {
    let h = 1.2e-16;
    let ctl = RetardedControls::new(4, 4, SpectralMode::SplitPositiveGauss3).unwrap();
    let (b, conf, full) = setup(h, 0.06 * h, 0.2, true, 1.5e14, ctl);
    let state = b.initial(full, &conf, 0.).unwrap();
    let dt = 1e10;
    let (step, diag) = b.advance_with_diagnostics(&state, &conf, dt).unwrap();
    let g1 = b.0.geometry.snapshot(dt).unwrap();
    let expected = step
        .state
        .cohorts
        .iter()
        .map(|x| {
            x.n_comoving_m3
                * (x.ray_at(&g1).unwrap().energy_ev - x.energy_at_birth_ev)
                * rei_iso_couple_reference::full_network::EV_J
        })
        .sum::<f64>();
    assert!(rel(diag.photon_work_ledger_j_com3, expected) < 3e-10);
    assert!(rel(diag.photon_work_independent_j_com3, expected) < 8e-8);
}

#[test]
fn p4s4_optin_is_default_off_and_preserves_small_step_native_ledgers() {
    use rei_iso_couple_reference::retarded_transport::OpacityEventMode;
    let original = RetardedControls::new(2, 4, SpectralMode::OriginalCellMean).unwrap();
    assert_eq!(
        original.opacity_event_mode,
        OpacityEventMode::FrozenMidpoint
    );
    let event_aware = original.with_threshold_events();
    assert_eq!(
        event_aware.opacity_event_mode,
        OpacityEventMode::SplitProviderThresholds
    );
    let (base, conf, full) = setup(1.2e-16, 0., 0.2, false, 1.5e14, original);
    let (split, conf2, full2) = setup(1.2e-16, 0., 0.2, false, 1.5e14, event_aware);
    let input = base.initial(full, &conf, 0.).unwrap();
    let input2 = split.initial(full2, &conf2, 0.).unwrap();
    let (a, da) = base.advance_with_diagnostics(&input, &conf, 1e10).unwrap();
    let (b, db) = split
        .advance_with_diagnostics(&input2, &conf2, 1e10)
        .unwrap();
    assert_eq!(
        a.chemistry_budget.photo_events_m3,
        b.chemistry_budget.photo_events_m3
    );
    assert_eq!(da.photon_events_com3, db.photon_events_com3);
    assert_eq!(a.state.cohorts.len(), b.state.cohorts.len());
    assert_eq!(db.provider_threshold_cuts, 0);
    assert!(b.global_energy_relative_error < 3e-10);
}
