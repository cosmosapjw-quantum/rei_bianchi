use rei_iso_couple_reference::{
    HHeModel,
    axbi_sources::{AxbiSource, SOURCE_ID},
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground, GeometryBackground},
    deuterium_atomic::DAtomicProvider,
    full_network::{FullState, NetworkConfig},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
    positive_spectral::SpectralMode,
    retarded_transport::{PositiveRetardedBridge, RetardedControls},
    retarded_transport_threshold::PositiveThresholdBridge,
    source_age::{Cohort, SourceAgeBridge},
    threshold_roots::{split_by_thresholds, turning_time},
};
fn bg(h: f64, s: f64, tmax: f64) -> ConstantAxisymmetricBackground {
    ConstantAxisymmetricBackground::new(
        0.,
        AxisymmetricPoint::new(1. / 21., 0., h, s).unwrap(),
        [0., tmax],
    )
    .unwrap()
}
fn cohort(g: &ConstantAxisymmetricBackground, e: f64, mu: f64) -> Cohort {
    Cohort {
        birth_time_s: 0.,
        birth_geometry: g.snapshot(0.).unwrap(),
        energy_at_birth_ev: e,
        direction_at_birth: [(1. - mu * mu).sqrt(), 0., mu],
        n_comoving_m3: 1.,
        spectral_index: 0,
        angular_index: 0,
    }
}
fn roots(g: &ConstantAxisymmetricBackground, c: &Cohort, t: f64, d: f64) -> Vec<f64> {
    split_by_thresholds(
        g,
        c,
        0.,
        t,
        &g.snapshot(0.).unwrap(),
        &g.snapshot(t).unwrap(),
        d,
    )
    .unwrap()
}
fn rel(a: f64, b: f64) -> f64 {
    (a - b).abs() / a.abs().max(b.abs()).max(1e-30)
}
#[test]
fn flrw_exact_crossing_all_four_edges_sorted() {
    let g = bg(1e-15, 0., 2e15);
    let co = cohort(&g, 80., 0.5);
    let d = HHeModel::controlled_fixture().threshold_ev[0] + 0.0037;
    let r = roots(&g, &co, 2e15, d);
    assert_eq!(r.len(), 6, "{r:?}");
    for (t, edge) in r[1..5].iter().zip([54.42, 24.59, d, 13.6]) {
        assert!(rel(*t, (80. / edge).ln() / 1e-15) < 2e-13, "{t} vs {edge}");
        assert!(rel(co.ray_at(&g.snapshot(*t).unwrap()).unwrap().energy_ev, edge) < 1e-13);
    }
    assert!(turning_time(&co, &g).unwrap().is_none());
}
#[test]
fn signed_mixed_directional_hubble_two_he1_crossings() {
    let g = bg(1e-15, 2e-15, 8e14);
    let c = cohort(&g, 36., 0.9);
    let turn = turning_time(&c, &g).unwrap().unwrap();
    assert!(turn > 0. && turn < 8e14);
    let r = roots(&g, &c, 8e14, 13.602134599702);
    assert_eq!(r.len(), 4, "expected two HeI threshold crossings, {r:?}");
    assert!(r[1] < turn && r[2] > turn);
    for t in &r[1..3] {
        assert!(rel(c.ray_at(&g.snapshot(*t).unwrap()).unwrap().energy_ev, 24.59) < 2e-13);
    }
}
#[test]
fn endpoint_touch_no_zero_width_cell_and_fail_closed() {
    let g = bg(1e-15, 0., 1e15);
    let c = cohort(&g, 24.59, 0.2);
    let r = roots(&g, &c, 1e14, 13.602134599702);
    assert_eq!(r, [0., 1e14]);
    let mut wrong = cohort(&g, 30., 0.2);
    wrong.birth_geometry.scale_factors[0] = 0.0;
    assert!(
        split_by_thresholds(
            &g,
            &wrong,
            0.,
            1e13,
            &g.snapshot(0.).unwrap(),
            &g.snapshot(1e13).unwrap(),
            13.6
        )
        .is_err()
    );
}
fn native_pair(
    h: f64,
    s: f64,
) -> (
    PositiveRetardedBridge,
    PositiveThresholdBridge,
    NetworkConfig,
    FullState,
) {
    let src = AxbiSource::new(1900. / (21.0f64.powi(3) * 1e6), 0.2, 16, 8).unwrap();
    let gg = bg(h, s, 1.5e14);
    let bridge = SourceAgeBridge::new(src, gg).unwrap();
    let controls = RetardedControls::new(2, 4, SpectralMode::OriginalCellMean).unwrap();
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let conf = NetworkConfig::source_bound(
        DAtomicProvider::new(chi, chi + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        SOURCE_ID,
    );
    let mut values = [0.; 13];
    values[S::H1Neutral as usize] = 1000.;
    values[S::H1Ionized as usize] = 900.;
    values[S::He4Neutral as usize] = 300.;
    values[S::He4SinglyIonized as usize] = 100.;
    values[S::He4DoublyIonized as usize] = 60.;
    values[S::DNeutral as usize] = 25.;
    values[S::DIonized as usize] = 5.;
    let nuclei = IsotopeNumberState::new(values).unwrap();
    let thermal = nuclei.thermal_particle_density_all_thermal_m3().unwrap() * 1.5 * KB_J_K * 10000.;
    let full = FullState {
        gas: MixtureState {
            nuclei,
            thermal_j_m3: thermal,
        },
        photon_bins: vec![],
        escaped_j_m3: 0.,
        cmb_reservoir_j_m3: 0.,
        elapsed_s: 0.,
    };
    (
        PositiveRetardedBridge(bridge.clone(), controls),
        PositiveThresholdBridge(bridge, controls),
        conf,
        full,
    )
}
#[test]
fn immutable_p4s3_parity_non_crossing_and_cache_plan_count() {
    for s in [0., -0.06 * 1.2e-16, 0.06 * 1.2e-16] {
        let (a, b, c, f) = native_pair(1.2e-16, s);
        let mut old = a.initial(f.clone(), &c, 0.).unwrap();
        let mut new = b.initial(f, &c, 0.).unwrap();
        for step in 0..3 {
            let prev = a.advance(&old, &c, 2e10).unwrap();
            let (next, diag) = b.advance_with_diagnostics(&new, &c, 2e10).unwrap();
            assert_eq!(diag.threshold_crossings, 0);
            assert_eq!(diag.unique_geometry_plans, if step == 0 { 2 } else { 3 });
            assert!(
                rel(
                    prev.state.source_injected_count_com3,
                    next.state.source_injected_count_com3
                ) < 3e-13
            );
            assert!(
                rel(
                    prev.state.photon_absorbed_count_com3,
                    next.state.photon_absorbed_count_com3
                ) < 3e-13
            );
            assert!(
                rel(
                    prev.state.cohorts.iter().map(|x| x.n_comoving_m3).sum(),
                    next.state.cohorts.iter().map(|x| x.n_comoving_m3).sum()
                ) < 3e-13
            );
            assert!(
                rel(
                    prev.state.full.gas.eos().unwrap().temperature_k,
                    next.state.full.gas.eos().unwrap().temperature_k
                ) < 3e-13
            );
            assert!(next.global_energy_relative_error < 3e-10);
            old = prev.state;
            new = next.state;
        }
    }
}
#[test]
fn manufactured_discontinuous_opacity_root_split_improves_quadrature() {
    // Source-native HI/D Verner threshold gates, but a prescribed static number
    // density and expanding Killing energy: tests the quadrature discontinuity only.
    let h = 1.2e-16;
    let tmax = 5e12;
    let g = bg(h, 0., tmax);
    let d = 13.602134599702;
    let co = cohort(&g, 13.605, 0.4);
    let p = rei_iso_couple_reference::AtomicProvider::reference();
    let dp = DAtomicProvider::new(13.598434599702, d, "MANUFACTURED_D_H_DELTA_CHI").unwrap();
    let k = |tm: f64| {
        let e = co.ray_at(&g.snapshot(tm).unwrap()).unwrap().energy_ev;
        let kh = p
            .cross_section(rei_iso_couple_reference::Absorber::HI, e)
            .unwrap()
            * 1e-4
            * 0.03;
        let kd = dp.cross_section_m2(e).unwrap() * 0.03;
        (kh + kd) * 299_792_458.0
    };
    let trap = |n: usize, use_edges: bool| {
        let mut integral = 0.;
        for j in 0..n {
            let a = tmax * (j as f64) / n as f64;
            let b = tmax * ((j + 1) as f64) / n as f64;
            let bb = if use_edges {
                roots(&g, &co, b, d)
                    .into_iter()
                    .filter(|x| *x >= a && *x <= b)
                    .collect::<Vec<_>>()
            } else {
                vec![]
            };
            let mut v = vec![a];
            v.extend(bb);
            v.push(b);
            v.sort_by(f64::total_cmp);
            v.dedup_by(|x, y| (*x - *y).abs() < 1e-3);
            for w in v.windows(2) {
                integral += k(0.5 * (w[0] + w[1])) * (w[1] - w[0]);
            }
        }
        integral
    };
    // One independent very finely sampled source-original reference.
    let exact = trap(32768, true);
    let unsplit = trap(4, false);
    let split = trap(4, true);
    assert!(exact > 0.);
    assert!(
        rel(split, exact) < rel(unsplit, exact) * 0.02,
        "no edge benefit: {unsplit} {split} {exact}"
    );
}
#[test]
fn real_native_source_flrw_edge_crossing_with_transactional_ledger() {
    let h = 2e-15;
    let src = AxbiSource::new(0.04 / (21.0f64.powi(3) * 1e6), 0.0001, 16, 8).unwrap();
    let bg = bg(h, 0.02 * h, 1.5e14);
    let base = SourceAgeBridge::new(src, bg).unwrap();
    let ctl = RetardedControls::new(2, 4, SpectralMode::SplitPositiveGauss3).unwrap();
    let bridge = PositiveThresholdBridge(base, ctl);
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let mut conf = NetworkConfig::source_bound(
        DAtomicProvider::new(chi, chi + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        SOURCE_ID,
    );
    conf.use_collisions = false;
    conf.use_cx = false;
    conf.use_cmb = false;
    let mut n = [0.; 13];
    n[S::H1Neutral as usize] = 0.03;
    n[S::H1Ionized as usize] = 0.01;
    n[S::He4Neutral as usize] = 0.02;
    n[S::He4SinglyIonized as usize] = 0.001;
    n[S::DNeutral as usize] = 0.002;
    n[S::DIonized as usize] = 0.001;
    let nuclei = IsotopeNumberState::new(n).unwrap();
    let full = FullState {
        gas: MixtureState {
            nuclei,
            thermal_j_m3: 1.5
                * KB_J_K
                * nuclei.thermal_particle_density_all_thermal_m3().unwrap()
                * 1e4,
        },
        photon_bins: vec![],
        escaped_j_m3: 0.,
        cmb_reservoir_j_m3: 0.,
        elapsed_s: 0.,
    };
    let initial = bridge.initial(full, &conf, 0.).unwrap();
    let (out, diag) = bridge
        .advance_with_diagnostics(&initial, &conf, 1e13)
        .unwrap();
    assert!(
        diag.threshold_crossings > 0,
        "real source GL3 must cross a D or H threshold"
    );
    assert_eq!(diag.unique_geometry_plans, 2);
    assert!(out.global_energy_relative_error < 3e-10);
    assert!(
        rel(
            out.state.source_injected_count_com3,
            out.state
                .cohorts
                .iter()
                .map(|x| x.n_comoving_m3)
                .sum::<f64>()
                + out.state.photon_absorbed_count_com3
        ) < 2e-12
    );
    assert!(out.chemistry_budget.photo_events_m3.iter().sum::<f64>() > 0.);
}
#[test]
fn high_opacity_exact_zero_age_compaction_has_no_photon_energy_loss() {
    let (_, bridge, mut cfg, full) = native_pair(1.2e-16, 0.);
    cfg.use_collisions = false;
    cfg.use_cx = false;
    cfg.use_cmb = false;
    let state = bridge.initial(full, &cfg, 0.).unwrap();
    let (compact, diag) = bridge
        .advance_compact_exact_zeros(&state, &cfg, 1e13)
        .unwrap();
    let raw = bridge.advance(&state, &cfg, 1e13).unwrap();
    assert!(
        diag.retired_exact_zero_cohorts > 0,
        "expected some optically opaque rays underflow to exactly zero"
    );
    assert_eq!(
        compact.state.cohorts.len() + diag.retired_exact_zero_cohorts,
        raw.state.cohorts.len()
    );
    assert!(
        rel(
            compact.state.cohorts.iter().map(|c| c.n_comoving_m3).sum(),
            raw.state.cohorts.iter().map(|c| c.n_comoving_m3).sum()
        ) < 2e-13
    );
    assert_eq!(
        compact.state.photon_absorbed_count_com3,
        raw.state.photon_absorbed_count_com3
    );
    assert!(
        rel(
            compact.state.full.gas.eos().unwrap().temperature_k,
            raw.state.full.gas.eos().unwrap().temperature_k
        ) < 1e-14
    );
    let (next_compact, _) = bridge
        .advance_compact_exact_zeros(&compact.state, &cfg, 1e13)
        .unwrap();
    let next_raw = bridge.advance(&raw.state, &cfg, 1e13).unwrap();
    assert!(
        rel(
            next_compact.state.photon_absorbed_count_com3,
            next_raw.state.photon_absorbed_count_com3
        ) < 2e-13
    );
    assert!(next_compact.global_energy_relative_error < 3e-10);
    assert!(
        rel(
            next_compact.state.source_injected_count_com3,
            next_compact.state.photon_absorbed_count_com3
                + next_compact
                    .state
                    .cohorts
                    .iter()
                    .map(|c| c.n_comoving_m3)
                    .sum::<f64>()
        ) < 4e-13
    );
}
