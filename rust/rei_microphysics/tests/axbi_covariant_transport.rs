use rei_microphysics::axbi_covariant_transport::{
    CovariantTransport, PhotonState, MAX_NODES_PER_CELL,
};
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::{Absorber, AtomicProvider, AxisymmetricPoint, GeometrySnapshot, HHeModel};

fn geometry(a: f64, b: f64) -> GeometrySnapshot {
    AxisymmetricPoint::new(a, b, 1e-16, 0.0)
        .unwrap()
        .snapshot()
        .unwrap()
}
fn component(cells: usize) -> (CovariantTransport, AxbiSource) {
    let source = AxbiSource::new(1.898198450714027e-7, 0.2, 16, 8).unwrap();
    (
        CovariantTransport::new(&source, geometry(0.05, 0.0), cells, 13.6, 512.0).unwrap(),
        source,
    )
}
fn broad_state(core: &CovariantTransport, lo: f64, hi: f64, mean: f64) -> PhotonState {
    let mut state = core.empty_state();
    state.number[0] = 1.0;
    state.energy_ref[0] = mean;
    state.support_lo[0] = lo;
    state.support_hi[0] = hi;
    core.validate_state(&state).unwrap();
    state
}
fn close(a: f64, b: f64, relative: f64) {
    assert!(
        (a - b).abs() <= relative * a.abs().max(b.abs()).max(1e-300),
        "{a} != {b}"
    );
}

#[test]
fn exact_fit_threshold_delta_redshifts_without_false_heii_ionization() {
    let (core, _) = component(128);
    let mut state = core.empty_state();
    core.add_delta(&mut state, 0, 54.42, 0.7).unwrap();
    let before = core.prepare(&state, &geometry(0.05, 0.0)).unwrap();
    let initial = before.evaluate([0.0, 0.0, 1e-5], 1e-4, 1e10).unwrap();
    assert!(initial.photo.gamma_s[2] > 0.0);
    let frozen = state.clone();
    let late = geometry(0.05005, 0.0);
    let after = core.prepare(&state, &late).unwrap();
    let result = after.evaluate([0.0, 0.0, 1e-5], 1e-4, 1e10).unwrap();
    assert_eq!(result.photo.gamma_s[2], 0.0);
    assert_eq!(result.photo.heat_erg_per_absorber_s[2], 0.0);
    assert_eq!(result.absorbed_per_h[2], 0.0);
    assert_eq!(state, frozen);
    assert_eq!(result.state.number, state.number);
    assert_eq!(result.state.energy_ref, state.energy_ref);
    let (n0, u0) = core.inventory(&state, &geometry(0.05, 0.0)).unwrap();
    let (n1, u1) = core.inventory(&state, &late).unwrap();
    assert_eq!(n0, n1);
    close(u1 / u0, 0.05 / 0.05005, 2e-15);
}

#[test]
fn backward_euler_node_survival_number_energy_gamma_and_heat_share_one_owner() {
    let (core, _) = component(128);
    let mut state = core.empty_state();
    core.add_delta(&mut state, 2, 60.0, 0.7).unwrap();
    let gas = [1e-4, 1e-5, 3e-6];
    let nh = 1e-3;
    let dt = 1e10;
    let prepared = core.prepare(&state, &geometry(0.05, 0.0)).unwrap();
    let out = core.evaluate(&prepared, gas, nh, dt).unwrap();
    let c = HHeModel::controlled_fixture();
    let provider = AtomicProvider::reference();
    let sigma = [Absorber::HI, Absorber::HeI, Absorber::HeII]
        .map(|a| provider.cross_section(a, 60.0).unwrap());
    let expected = 0.7 / (1.0 + dt * c.c_cm_s * (0..3).map(|i| gas[i] * sigma[i]).sum::<f64>());
    let (n, u) = core.inventory(&out.state, &geometry(0.05, 0.0)).unwrap();
    close(n, expected, 2e-15);
    close(u, 60.0 * expected, 2e-15);
    close(0.7 - n, out.absorbed_per_h.iter().sum(), 4e-14);
    close(42.0 - u, out.binding_ev_per_h + out.heat_ev_per_h, 4e-14);
    for i in 0..3 {
        close(out.photo.gamma_s[i], c.c_cm_s * nh * sigma[i] * n, 2e-15);
        close(
            out.absorbed_per_h[i],
            dt * gas[i] / nh * out.photo.gamma_s[i],
            3e-15,
        );
        close(
            out.photo.heat_erg_per_absorber_s[i],
            out.photo.gamma_s[i] * (60.0 - c.threshold_ev[i]) * c.ev_erg,
            3e-15,
        );
    }
    core.validate_state(&out.state).unwrap();
}

#[test]
fn broad_positive_spectrum_uses_threshold_cut_nodes_instead_of_centroid() {
    let (core, _) = component(1);
    // Centroid below HeII, while a physically populated tail is above it.
    let state = broad_state(&core, 40.0, 56.0, 48.0);
    let prepared = core.prepare(&state, &geometry(0.05, 0.0)).unwrap();
    assert!(prepared.node_count() > 8);
    assert!(prepared.diagnostics.max_count_relative_defect <= 64.0 * f64::EPSILON);
    assert!(prepared.diagnostics.max_energy_relative_defect <= 128.0 * f64::EPSILON);
    let no_loss = prepared.evaluate([0.0; 3], 1e-4, 1e10).unwrap();
    close(no_loss.state.number[0], 1.0, 64.0 * f64::EPSILON);
    close(no_loss.state.energy_ref[0], 48.0, 128.0 * f64::EPSILON);
    let out = prepared.evaluate([0.0, 0.0, 1e-5], 1e-4, 1e10).unwrap();
    assert!(out.absorbed_per_h[2] > 0.0);
    close(1.0 - out.state.number[0], out.absorbed_per_h[2], 1e-12);
    close(
        48.0 - out.state.energy_ref[0],
        out.binding_ev_per_h + out.heat_ev_per_h,
        1e-12,
    );
    assert_eq!(out.state.support_lo[0], 40.0);
    assert_eq!(out.state.support_hi[0], 56.0);
    let below = broad_state(&core, 40.0, 54.41, 47.0);
    let result = core
        .prepare(&below, &geometry(0.05, 0.0))
        .unwrap()
        .evaluate([0.0, 0.0, 1e-5], 1e-4, 1e10)
        .unwrap();
    assert_eq!(result.absorbed_per_h[2], 0.0);
}

#[test]
fn near_endpoint_broad_support_stays_positive_and_records_tail_control() {
    let (core, _) = component(1);
    let lo = 13.6_f64;
    let mean = f64::from_bits(lo.to_bits() + 1);
    let state = broad_state(&core, lo, 100.0, mean);
    let prepared = core.prepare(&state, &geometry(0.05, 0.0)).unwrap();
    assert!(prepared.node_count() > 1);
    assert!(prepared.diagnostics.omitted_tail_number_bound_per_h > 0.0);
    assert!(prepared.diagnostics.omitted_tail_number_bound_per_h < 1.426e-21);
    let out = prepared.evaluate([1e-5, 0.0, 0.0], 1e-4, 1e10).unwrap();
    core.validate_state(&out.state).unwrap();
    assert_eq!(out.state.support_lo[0], lo);
    assert_eq!(out.state.support_hi[0], 100.0);
    close(1.0 - out.state.number[0], out.absorbed_per_h[0], 1e-12);
    core.prepare(&out.state, &geometry(0.05, 0.0)).unwrap();
    let high_mean = f64::from_bits(100.0_f64.to_bits() - 1);
    let high = broad_state(&core, lo, 100.0, high_mean);
    let cache = core.prepare(&high, &geometry(0.05, 0.0)).unwrap();
    assert!(cache.node_count() > 1);
    let high_after = cache.evaluate([1e-5; 3], 1e-4, 1e10).unwrap();
    core.validate_state(&high_after.state).unwrap();
    core.prepare(&high_after.state, &geometry(0.05, 0.0))
        .unwrap();
}

#[test]
fn source_subcells_close_number_energy_and_anisotropic_reflection() {
    let (core, source) = component(128);
    let mut state = core.empty_state();
    let now = geometry(0.1, 0.004);
    let dt = 1e10;
    let ledger = core.inject(&mut state, &now, 9.0, dt).unwrap();
    let expected = source.at_redshift(9.0).unwrap().per_h_s
        * dt
        * source
            .spectral_cells
            .iter()
            .map(|s| s.photon_fraction)
            .sum::<f64>();
    close(ledger.added_photons_per_h, expected, 2e-13);
    let (n, u) = core.inventory(&state, &now).unwrap();
    close(n, ledger.added_photons_per_h, 2e-14);
    close(u, ledger.added_energy_ev_per_h, 2e-14);
    let rays = core.ray_geometry(&now).unwrap();
    close(
        rays.iter().map(|r| r.angular_weight).sum::<f64>(),
        1.0,
        2e-15,
    );
    for j in 0..rays.len() / 2 {
        let mirror = rays.len() - 1 - j;
        assert_eq!(rays[j].scale, rays[mirror].scale);
        assert_eq!(rays[j].mu, -rays[mirror].mu);
        assert_eq!(rays[j].angular_weight, rays[mirror].angular_weight);
        for i in 0..core.n_energy() {
            assert_eq!(
                state.number[j * core.n_energy() + i],
                state.number[mirror * core.n_energy() + i]
            );
            assert_eq!(
                state.energy_ref[j * core.n_energy() + i],
                state.energy_ref[mirror * core.n_energy() + i]
            );
        }
    }
    let prepared = core.prepare(&state, &now).unwrap();
    let after = prepared.evaluate([1e-4, 1e-5, 2e-6], 1e-4, 1e9).unwrap();
    let (na, ua) = core.inventory(&after.state, &now).unwrap();
    close(n - na, after.absorbed_per_h.iter().sum(), 2e-12);
    close(u - ua, after.binding_ev_per_h + after.heat_ev_per_h, 2e-12);
    // Every selected shear case retains the full physical source at z4.
    use rei_microphysics::axbi_background::{AxbiBackground, BackgroundFamily, Cosmology};
    for q in [0.0, 0.005, -0.005, 0.01, -0.01] {
        let bg = AxbiBackground::new(
            Cosmology {
                h0_per_s: 67.4e5 / 3.0856775814913673e24,
                omega_m: 0.315,
                omega_r: 9.2e-5,
                omega_lambda: 1.0 - 0.315 - 9.2e-5,
            },
            1.0 / 21.0,
            0.2,
            0.0,
            q,
            BackgroundFamily::PhysicalDensityFixed,
            64,
        )
        .unwrap();
        let reference = bg.point_at_scale(1.0 / 21.0).unwrap().geometry().unwrap();
        let end = bg.point_at_scale(0.2).unwrap().geometry().unwrap();
        let selected = CovariantTransport::new(&source, reference, 128, 13.6, 512.0).unwrap();
        let mut photons = selected.empty_state();
        let injected = selected.inject(&mut photons, &end, 4.0, dt).unwrap();
        let (ns, us) = selected.inventory(&photons, &end).unwrap();
        close(ns, injected.added_photons_per_h, 2e-14);
        close(us, injected.added_energy_ev_per_h, 2e-14);
    }
}

#[test]
fn redshifted_inert_photons_are_retained_and_history_memory_is_fixed() {
    let (core, _) = component(128);
    let mut state = core.empty_state();
    core.add_delta(&mut state, 0, 13.6, 1.0).unwrap();
    let late = geometry(0.2, 0.0);
    let prepared = core.prepare(&state, &late).unwrap();
    let after = prepared.evaluate([1.0; 3], 1.0, 1e15).unwrap();
    assert_eq!(after.state.number, state.number);
    assert_eq!(after.state.energy_ref, state.energy_ref);
    assert_eq!(after.absorbed_per_h, [0.0; 3]);
    let capacity = state.buffer_capacity_bytes();
    for i in 0..24 {
        let a = 0.05 + 0.15 * i as f64 / 23.0;
        core.inject(&mut state, &geometry(a, 0.0), 1.0 / a - 1.0, 1e8)
            .unwrap();
        assert_eq!(state.buffer_capacity_bytes(), capacity);
        let cache = core.prepare(&state, &geometry(a, 0.0)).unwrap();
        assert!(cache.node_count() <= core.cell_count() * MAX_NODES_PER_CELL);
    }
}

#[test]
fn unsupported_source_and_malformed_support_reject_transactionally() {
    let source = AxbiSource::new(1.9e-7, 0.2, 16, 8).unwrap();
    let core = CovariantTransport::new(&source, geometry(0.05, 0.0), 32, 13.6, 100.0).unwrap();
    let mut state = core.empty_state();
    let initial = state.clone();
    assert!(core
        .inject(&mut state, &geometry(0.1, 0.0), 9.0, 1e10)
        .is_err());
    assert_eq!(state, initial);
    state.number[0] = 1.0;
    assert!(core.prepare(&state, &geometry(0.05, 0.0)).is_err());
}
